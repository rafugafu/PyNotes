"""The Python semantic-analysis engine behind editor.py's and
pythonshell.py's Python-HMode syntax highlighting: python_scope_build.py's
AST-based scope/type analysis. It is pure text processing (buf is a tiny
stand-in with just the handful of attributes _python_build_scopes() and
the module-resolution helpers it calls actually touch), so no display is
needed.

Most of these scenarios are regression tests for real bugs found while
stress-testing the highlighter against hand-written files - each test's
docstring says what broke and why, not just what it asserts."""

import sys
import textwrap

import pytest

import state
from python_scope_build import _python_build_scopes, _PYTHON_TARGET_SYS_PATH_CACHE

# ---------------------------------------------------------------------------
# Harness
# ---------------------------------------------------------------------------


class StubBuffer:
    """A minimal stand-in for an Editor/PythonShellBuffer: just the
    per-buffer caches and edit-generation counter _python_build_scopes()
    and the module-resolution helpers it calls need. title is left unset
    by default - PythonShellBuffer (the Python shell's own buffer class)
    has no file and so no title attribute at all, which is itself a
    scenario this module needs to tolerate (see test_module_resolution
    below)."""

    def __init__(self, title=None):
        self._python_edit_generation = [0]
        self._python_module_spec_cache = {}
        self._python_module_members_cache = {}
        self._python_module_class_members_cache = {}
        self._python_module_func_params_cache = {}
        if title is not None:
            self.title = title


FIELD_NAMES = (
    "scopes",
    "call_kwargs",
    "module_aliases",
    "local_classes",
    "module_literals",
    "scope_var_types",
    "literal_attrs",
    "def_names",
    "typed_attrs",
    "param_default_tags",
    "kwarg_positions",
    "import_dotted_lines",
    "import_orig_name_tags",
    "class_module_origin",
    "local_class_method_params",
    "local_class_accepts_any",
    "name_positions",
    "local_class_module_origins",
    "from_func_module",
    "class_type_maps",
    "class_attr_types",
    "func_params",
    "func_accepts_any",
    "class_bases",
    "inherited",
    "module_scope_class_keys",
    "instance_only",
    "instance_name_positions",
    "global_stmt_kind_positions",
)


class ScopeResult(dict):
    """_python_build_scopes()'s return tuple, unpacked into a dict keyed
    by FIELD_NAMES so tests can read result.scope_var_types instead of a
    bare, easy-to-miscount tuple index - and still support result[0] etc.
    for anything not worth naming."""

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)


def build(text, buf=None, **seeds):
    """_python_build_scopes(), dedented and run against a fresh
    StubBuffer by default, with its 29-tuple result unpacked into a
    ScopeResult. text's own leading/trailing blank lines (from writing
    it as an indented triple-quoted string) are stripped first, so line
    1 in every assertion below means the first line actually written in
    the test, not an invisible one contributed by the string literal's
    own opening newline. Asserts the parse actually succeeded (a None
    result means _python_build_scopes() gave up, which every scenario
    here should avoid - a genuinely-unparseable snippet belongs in its
    own explicit test instead)."""
    if buf is None:
        buf = StubBuffer()
    result = _python_build_scopes(buf, textwrap.dedent(text).strip("\n"), **seeds)
    assert result is not None, "the snippet failed to parse at all"
    assert len(result) == len(FIELD_NAMES)
    return ScopeResult(zip(FIELD_NAMES, result))


def instance_kind(result, name, line):
    """Whichever of result.name_positions' entries matches (name, line)
    is treated as an instance (a custom-class-typed variable/attribute,
    colored differently from a plain var) - i.e. the same check
    editor.py's ha() makes against instance_name_positions. Only ever
    true for a custom class's instances - a builtin-typed name (a dict,
    a list, ...) gets a separate 'builtin' kind instead (see
    attr_kind() below for checking those)."""
    matches = [
        (l, c) for (l, c, n, _store) in result.name_positions if n == name and l == line
    ]
    assert matches, f"no name_positions entry for {name!r} on line {line}"
    return any(pos in result.instance_name_positions for pos in matches)


def attr_kind(result, attr, line):
    """The kind ('func'/'var'/'instance'/'module'/'class') typed_attrs
    resolved a given attribute access (obj.attr) to on line, or None if
    it was never resolved into anything at all (so it would be left
    unhighlighted, plain text) - the right check for "does .update/
    .append/... highlight as a real method", for both builtin- and
    custom-class-typed objects alike."""
    matches = [k for (l, _c, a, k) in result.typed_attrs if l == line and a == attr]
    return matches[0] if matches else None


def run_session(statements, buf=None):
    """Simulates a Python shell session where everything before the
    current statement has scrolled out of the transcript entirely (the
    scrollback was cleared, or trimmed) - the opposite of the shell's
    normal case, where _python_build_scopes() simply re-analyzes the
    *entire* cumulative transcript as one text blob on every keystroke
    (see pythonshell.py's _hapyshell_body(), which always re-strips and
    re-passes the whole shellcmd widget's text), so ordinary continuity
    needs no seed_* at all - the full text already has everything.
    seed_*/result carry-over (threaded here exactly the way
    PythonShellBuffer's own session dicts are updated) exists
    specifically for this harder case: each statement after the first
    is analyzed with *only its own text*, relying entirely on what the
    previous statement's result seeded forward. Returns the final
    statement's ScopeResult."""
    if buf is None:
        buf = StubBuffer()
    seeds = dict(
        seed_names={},
        seed_types={},
        seed_classes={},
        seed_aliases={},
        seed_origins={},
        seed_method_params={},
        seed_accepts_any=set(),
        seed_module_bases={},
        seed_func_origins={},
        seed_attr_types={},
        seed_class_attr_types={},
        seed_func_params={},
        seed_func_accepts_any={},
        seed_class_bases={},
        seed_inherited={"members": set(), "attr_types": set(), "method_params": set()},
        seed_instance_only={},
    )
    result = None
    for statement in statements:
        text = textwrap.dedent(statement).strip("\n")
        lines = text.split("\n")
        line_blocks = [1] * len(lines)
        exec_boundary = len(lines) + 1
        raw = _python_build_scopes(
            buf,
            text,
            line_blocks=line_blocks,
            **{k: dict(v) if isinstance(v, dict) else set(v) for k, v in seeds.items()},
        )
        assert raw is not None, f"statement failed to parse: {statement!r}"
        result = ScopeResult(zip(FIELD_NAMES, raw))
        for name, defs in result.scopes[0]["names"].items():
            exec_defs = [d for d in defs if d[0] < exec_boundary]
            if (
                exec_defs
                and name not in result.scopes[0].get("globals", {})
                and name not in result.scopes[0].get("nonlocals", {})
            ):
                seeds["seed_names"][name] = max(exec_defs, key=lambda d: d[0])[1]
        for name, type_list in result.scope_var_types.get(0, {}).items():
            exec_types = [t for t in type_list if t[0] < exec_boundary]
            if exec_types:
                seeds["seed_types"][name] = max(exec_types, key=lambda t: t[0])[1]
        for class_name, members in result.local_classes.items():
            seeds["seed_classes"][class_name] = members
        for alias_name, defs in result.module_aliases.items():
            best = [d for d in defs if d[0] < exec_boundary]
            if best:
                seeds["seed_aliases"][alias_name] = max(best, key=lambda d: d[0])[1]
        for class_key, type_map in result.class_type_maps.items():
            seeds["seed_attr_types"][class_key] = dict(type_map)
        for class_key, type_map in result.class_attr_types.items():
            seeds["seed_class_attr_types"][class_key] = dict(type_map)
        for key in result.local_class_accepts_any:
            seeds["seed_accepts_any"].add(key)
        seeds["seed_method_params"].update(result.local_class_method_params)
        seeds["seed_func_params"].update(result.func_params)
        seeds["seed_func_accepts_any"].update(result.func_accepts_any)
        seeds["seed_class_bases"].update(result.class_bases)
        for key in ("members", "attr_types", "method_params"):
            seeds["seed_inherited"][key].update(result.inherited.get(key, ()))
        for class_key, attrs in result.instance_only.items():
            seeds["seed_instance_only"].setdefault(class_key, set()).update(attrs)
    return result


# ---------------------------------------------------------------------------
# Builtin-literal attribute types (plain variables)
#
# self.properties is a builtin dict: self.properties.update(...) should
# highlight .update as a real method, the same as if self.properties had
# held a custom-class instance. Originally this only worked for
# constructor calls (x = dict()), not literals (x = {}); fixed by
# _value_type()/_infer_type() treating a recognized literal the same as
# a ('builtin', typename) type tuple.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "literal,method",
    [
        ("{}", "update"),
        ("[]", "append"),
        ("()", "count"),
        ("set()", "add"),
        ("''", "join"),
    ],
)
def test_builtin_literal_propagates_to_a_plain_variable(literal, method):
    result = build(f"""
        a = {literal}
        a.{method}()
        """)
    assert attr_kind(result, method, 2) == "func"


def test_builtin_literal_propagates_through_a_constructor_call_too():
    result = build("""
        a = dict()
        a.update()
        """)
    assert attr_kind(result, "update", 2) == "func"


def test_builtin_literal_propagates_to_a_self_attribute():
    """self.properties = {} inside __init__, then self.properties.update(...)
    inside another method - the original bug report: self.properties is
    a builtin dict and .update should highlight, but didn't."""
    result = build("""
        class K:
        \tdef __init__(self):
        \t\tself.properties = {}
        \tdef go(self):
        \t\tself.properties.update({'a': 1})
        """)
    assert attr_kind(result, "update", 5) == "func"


def test_builtin_literal_propagates_across_inheritance():
    result = build("""
        class Big:
        \tdef __init__(self):
        \t\tself.properties = {}
        class Small(Big):
        \tpass
        small = Small()
        small.properties.update({})
        """)
    assert attr_kind(result, "update", 7) == "func"


# ---------------------------------------------------------------------------
# Invalidation on reassignment
#
# Reassigning a variable/attribute to something untyped (None, an
# unresolvable call, ...) must stop the old highlighting from sticking
# around - found as three separate bugs, one per tracking mechanism
# (scope_var_types for plain vars; class_attr_types/
# dynamic_class_attr_types and the older class_type_maps scan, both for
# self.attr), each needing its own explicit invalidation entry.
# ---------------------------------------------------------------------------


def test_reassigning_a_plain_variable_to_none_stops_the_old_highlight():
    result = build("""
        a = {}
        a = None
        a.update({})
        """)
    assert attr_kind(result, "update", 3) is None


def test_reassigning_a_self_attribute_to_none_stops_the_old_highlight():
    result = build("""
        class K:
        \tdef __init__(self):
        \t\tself.properties = {}
        \tdef go(self):
        \t\tself.properties = None
        \t\tself.properties.update({})
        """)
    assert attr_kind(result, "update", 6) is None


def test_reassigning_then_reassigning_back_to_a_real_type_resolves_again():
    result = build("""
        class K:
        \tdef __init__(self):
        \t\tself.properties = {}
        k = K()
        k.properties = None
        k.properties = {'x': 1}
        k.properties.update({})
        """)
    assert attr_kind(result, "update", 7) == "func"


# ---------------------------------------------------------------------------
# Per-instance isolation
#
# All instances of one class originally shared a single class-level
# type record for a given attribute, so invalidating one instance's
# attribute (k1.properties = None) wrongly suppressed highlighting on a
# completely different, untouched instance (k2.properties.update(...)).
# Fixed with a separate per-variable tracking structure (var_attr_types)
# for *external* (not self.) attribute assignments, consulted before the
# shared class-level default.
# ---------------------------------------------------------------------------


def test_invalidating_one_instance_does_not_affect_a_different_instance():
    result = build("""
        class K:
        \tdef __init__(self):
        \t\tself.properties = {}
        k1 = K()
        k2 = K()
        k1.properties = None
        k2.properties.update({})
        """)
    assert attr_kind(result, "update", 7) == "func"


def test_external_reassignment_does_not_corrupt_the_class_s_own_internal_use():
    """Reassigning k.properties externally must never change how
    self.properties.update resolves inside K's own methods - the two are
    tracked completely separately (var_attr_types for the external
    write, class_attr_types for self.'s own)."""
    result = build("""
        class K:
        \tdef __init__(self):
        \t\tself.properties = {}
        \tdef go(self):
        \t\tself.properties.update({})
        k = K()
        k.properties = None
        """)
    assert attr_kind(result, "update", 5) == "func"


def test_external_reassignment_on_a_subclass_with_no_init_of_its_own():
    """Small has no self.attr assignments anywhere in its own body, so
    the earlier _self_assigned_attrs-based merge-skip (added for the
    case above) couldn't catch this one - a broader _direct_attr_assigns
    set (every (class, attr) pair touched at all, self or external) was
    needed so the inheritance merge doesn't resurrect Big's stale type
    into Small right after small.properties was invalidated."""
    result = build("""
        class Big:
        \tdef __init__(self):
        \t\tself.properties = {}
        class Small(Big):
        \tpass
        small = Small()
        small.properties = None
        small.properties.update({})
        """)
    assert attr_kind(result, "update", 8) is None


def test_ast_walk_is_breadth_first_but_resolution_follows_textual_order():
    """ast.walk() visits every module-level statement before descending
    into any class method, regardless of line number - so a flat
    last-write-wins loop over tree_assigns in raw ast.walk() order was
    processing the module-level k.properties = None below (line 5)
    *before* the nested self.properties = {} (line 3), even though line
    3 is textually/execution-order earlier, wrongly letting the later
    None assignment get silently overwritten back to dict. Fixed by
    sorting tree_assigns by (lineno, col_offset) before that loop, so
    line 5 - truly the latest assignment - correctly wins."""
    result = build("""
        class K:
        \tdef __init__(self):
        \t\tself.properties = {}
        k = K()
        k.properties = None
        k.properties.update({})
        """)
    assert attr_kind(result, "update", 6) is None


# ---------------------------------------------------------------------------
# Self-referential and shadowed assignments (a = a)
#
# a = a (or any x = x) on the line that *introduces* a local inside a
# function must not resolve the right-hand a's type from an outer-scope
# variable of the same name: Python's own scoping rule is that assigning
# to a name anywhere in a function makes it local for the entire
# function body, so a read of it before any real value is assigned is
# unbound, not a fallback to an enclosing scope. The alias-assignment
# resolution pass (for plain x = y aliasing) was climbing to the parent
# scope whenever it had no type recorded yet for the name in the current
# scope, without first checking whether the name was already locally
# bound there at all - which it always is, for a self-assignment.
# ---------------------------------------------------------------------------


def test_self_assignment_inside_a_function_does_not_inherit_the_outer_type():
    result = build("""
        class K:
        \tpass
        a = K()
        def f():
        \ta = a
        \ta.anything()
        """)
    assert not instance_kind(result, "a", 6)


def test_self_assignment_at_module_scope_keeps_its_existing_type():
    """The same a = a pattern, but with nothing shadowing anything (one
    scope, one a throughout) - should keep resolving correctly, since
    this is simply re-confirming the same variable's own prior type."""
    result = build("""
        class K:
        \tpass
        a = K()
        a = a
        a.anything()
        """)
    assert instance_kind(result, "a", 5)


def test_reading_a_truly_unshadowed_outer_variable_from_inside_a_function_still_works():
    """The fix above must not stop a function from reading an outer
    variable it never assigns to anywhere in its own body - that's a
    completely ordinary closure-style read, with no local of the same
    name to shadow it."""
    result = build("""
        class K:
        \tpass
        a = K()
        def f():
        \tb = a
        \tb.anything()
        """)
    assert instance_kind(result, "b", 6)


def test_a_name_assigned_anywhere_in_a_function_is_local_for_the_whole_function():
    """Matches real Python's scoping rule directly: once a is assigned
    anywhere in f, every a inside f is that local - even a read on a
    line textually before the assignment (print(a), line 5) - so it
    must not pick up K's type from the outer scope."""
    result = build("""
        class K:
        \tpass
        a = K()
        def f():
        \tprint(a)
        \ta = 5
        """)
    assert not instance_kind(result, "a", 5)
    assert not instance_kind(result, "a", 6)


# ---------------------------------------------------------------------------
# Deliberately unimplemented (scope boundary, not a bug)
#
# "Fix every bug" does not mean "implement every feature that was never
# built": these lock in documented, deliberate non-goals so a future
# change doesn't quietly start supporting them (which would then need
# its own correctness pass) without anyone deciding to.
# ---------------------------------------------------------------------------


def test_for_loop_over_literal_elements_does_not_infer_a_type():
    """for x in [{}, {}]: ... was explicitly tried and reverted - looping
    over a list of literals (as opposed to a list of constructor calls,
    container_elem_types' actual job) was ruled out as unwanted scope
    creep, not a bug."""
    result = build("""
        for x in [{}, {}]:
        \tx.update({})
        """)
    assert attr_kind(result, "update", 2) is None


def test_except_as_binds_a_name_but_its_members_are_not_resolved():
    """except Exception as e binds e (it appears as a Store in
    name_positions, so it is at least highlighted as a variable), but
    e's own members (e.args, ...) are never introspected - exception
    types aren't one of the builtins _PYTHON_BUILTIN_MEMBERS covers,
    and there's no local class to look them up in either."""
    result = build("""
        try:
        \tpass
        except Exception as e:
        \te.args
        """)
    assert attr_kind(result, "args", 4) is None


def test_with_as_binds_a_name_but_its_members_are_not_resolved():
    """with K() as k: ... never resolves k's own type at all - unlike a
    plain k = K() assignment, the with/as binding form was never wired
    into the same value-type inference, so k.frob() stays unhighlighted
    even though frob is a real method of K."""
    result = build("""
        class K:
        \tdef frob(self):
        \t\tpass
        with K() as k:
        \tk.frob()
        """)
    assert attr_kind(result, "frob", 5) is None


def test_a_ternary_expression_does_not_infer_a_type():
    """a = {} if True else [] - picking a type out of a conditional
    expression's two branches (even when, as here, they'd actually
    agree) was never implemented."""
    result = build("""
        a = {} if True else []
        a.update({})
        """)
    assert attr_kind(result, "update", 2) is None


# ---------------------------------------------------------------------------
# Broader scope-build coverage
#
# Scenarios beyond the specific historical bugs above: other kinds of
# assignment (annotated, augmented, tuple-unpacking), other binding
# forms (lambda, comprehensions, global), and other type-tracking
# mechanisms (call-site keyword-argument validation, multiple
# inheritance's MRO, class-level - not instance-level - attribute
# access) that the engine also has to get right.
# ---------------------------------------------------------------------------


def test_a_call_s_keyword_arguments_are_matched_against_the_callee_s_real_parameters():
    result = build("""
        def f(a, b):
        \tpass
        f(a=1, b=2)
        """)
    assert result.call_kwargs.get(3) == {"a", "b"}


def test_a_keyword_argument_not_in_the_callee_s_signature_is_not_recognized():
    result = build("""
        def f(a, b):
        \tpass
        f(a=1, c=2)
        """)
    assert result.call_kwargs.get(3) == {"a"}


def test_a_catch_all_kwargs_parameter_accepts_any_keyword_name():
    result = build("""
        def f(a, **kw):
        \tpass
        f(a=1, whatever=2)
        """)
    assert result.call_kwargs.get(3) == {"a", "whatever"}


def test_a_class_s_init_parameters_are_matched_the_same_way_as_a_function_s():
    result = build("""
        class K:
        \tdef __init__(self, x, y):
        \t\tpass
        K(x=1, y=2)
        """)
    assert result.call_kwargs.get(4) == {"x", "y"}


def test_a_lambda_assigned_to_a_variable_is_treated_as_a_callable_with_real_parameters():
    result = build("""
        f = lambda a, b: a + b
        f(a=1, b=2)
        """)
    assert result.call_kwargs.get(2) == {"a", "b"}


def test_diamond_inheritance_resolves_a_member_from_the_correct_branch():
    """D(B, C), both of which derive from A, with C (not A or B) the one
    that actually defines "other" - a plain single-base merge wouldn't
    get this right without real C3-linearization-ordered resolution."""
    result = build("""
        class A:
        \tdef __init__(self):
        \t\tself.val = 1
        class B(A):
        \tpass
        class C(A):
        \tdef __init__(self):
        \t\tself.other = 2
        class D(B, C):
        \tpass
        d = D()
        d.other
        """)
    assert attr_kind(result, "other", 12) == "var"


def test_a_loop_variable_inside_a_comprehension_does_not_leak_its_type_outward():
    """The i in [i for i in range(10)] lives in the comprehension's own
    scope (Python 3's comprehensions always get one); a same-named i
    used afterwards at module scope is a completely different, unrelated
    name and must not inherit int from the loop variable."""
    result = build("""
        x = [i for i in range(10)]
        i.bit_length()
        """)
    assert attr_kind(result, "bit_length", 2) is None


def test_global_inside_a_function_redirects_an_assignment_to_module_scope():
    result = build("""
        g = {}
        def f():
        \tglobal g
        \tg = []
        \tg.append(1)
        f()
        g.append(2)
        """)
    assert attr_kind(result, "append", 5) == "func"
    assert attr_kind(result, "append", 7) == "func"


def test_a_walrus_assignment_is_typed_the_same_as_a_plain_one():
    result = build("""
        class K:
        \tpass
        if (a := K()):
        \ta.anything
        """)
    assert instance_kind(result, "a", 4)


def test_an_fstring_is_typed_as_str():
    result = build("""
        a = f"hi {1}"
        a.upper()
        """)
    assert attr_kind(result, "upper", 2) == "func"


def test_an_annotated_assignment_is_typed_from_its_value():
    result = build("""
        a: dict = {}
        a.update({})
        """)
    assert attr_kind(result, "update", 2) == "func"


def test_an_augmented_assignment_keeps_the_variable_s_existing_type():
    result = build("""
        a = []
        a += [1]
        a.append(2)
        """)
    assert attr_kind(result, "append", 3) == "func"


def test_tuple_unpacking_assigns_each_target_its_own_element_s_type():
    result = build("""
        a, b = {}, []
        a.update({})
        b.append(1)
        """)
    assert attr_kind(result, "update", 2) == "func"
    assert attr_kind(result, "append", 3) == "func"


def test_a_class_level_attribute_is_typed_the_same_way_as_a_self_attribute():
    """K.x (accessed on the class itself, not an instance) should
    resolve the same way self.x/instance.x does - it is still, in the
    end, one literal dict value."""
    result = build("""
        class K:
        \tx = {}
        K.x.update({})
        """)
    assert attr_kind(result, "update", 3) == "func"


def test_a_bytes_literal_is_typed_as_bytes():
    result = build("""
        a = b"hi"
        a.decode()
        """)
    assert attr_kind(result, "decode", 2) == "func"


def test_a_method_awaited_on_an_instance_still_resolves_correctly():
    result = build("""
        import asyncio
        class K:
        \tasync def frob(self):
        \t\tpass
        async def main():
        \tk = K()
        \tawait k.frob()
        asyncio.run(main())
        """)
    assert attr_kind(result, "frob", 7) == "func"


# ---------------------------------------------------------------------------
# Historical regressions (git history)
#
# Dug out of old commits that fixed real Python-highlighting bugs, well
# before this file existed, to make sure none of them have crept back in
# under the current (since-rewritten) engine.
# ---------------------------------------------------------------------------


def test_a_builtin_name_shadowed_later_in_the_file_does_not_corrupt_earlier_uses_of_it():
    """list() called on line 1 is the real builtin, even though list
    gets reassigned to something else on line 2 - a name with no
    definition *yet in effect* at a given line used to fall back to
    whatever its *eventual* (later) definition in the file was, rather
    than correctly recognizing it as still the builtin at that point."""
    result = build("""
        x = list((1, 2))
        list = 5
        x.append(1)
        """)
    assert attr_kind(result, "append", 3) == "func"


def test_import_dunder_without_fromlist_binds_only_the_top_level_package(
    tmp_path, no_target_interpreter
):
    """__import__('pkg.sub') - with no fromlist - returns pkg, the
    top-level package, exactly like Python's own __import__() does;
    this used to be conflated with importlib.import_module(), which
    always returns the full leaf module regardless of fromlist."""
    package = tmp_path / "pkg_no_fromlist"
    package.mkdir()
    (package / "__init__.py").write_text("def root_func():\n\tpass\n")
    (package / "sub.py").write_text("def sub_func():\n\tpass\n")
    buf = StubBuffer(title=str(tmp_path / "main.py"))
    result = build(
        """
        x = __import__('pkg_no_fromlist.sub')
        x.root_func()
        """,
        buf=buf,
    )
    assert attr_kind(result, "root_func", 2) == "func"


def test_import_dunder_with_a_nonempty_fromlist_binds_the_full_dotted_module(
    tmp_path, no_target_interpreter
):
    package = tmp_path / "pkg_with_fromlist"
    package.mkdir()
    (package / "__init__.py").write_text("def root_func():\n\tpass\n")
    (package / "sub.py").write_text("def sub_func():\n\tpass\n")
    buf = StubBuffer(title=str(tmp_path / "main.py"))
    result = build(
        """
        x = __import__('pkg_with_fromlist.sub', fromlist=['sub'])
        x.sub_func()
        """,
        buf=buf,
    )
    assert attr_kind(result, "sub_func", 2) == "func"


def test_staticmethod_decorated_methods_first_parameter_is_not_treated_as_self():
    """A @staticmethod has no implicit self/cls at all - its first
    parameter used to be unconditionally highlighted the same as a
    real method's self, regardless of the decorator."""
    result = build("""
        class K:
        \t@staticmethod
        \tdef frob(x):
        \t\tpass
        \tdef normal(self):
        \t\tpass
        """)
    param_kinds = {
        name: kind
        for sc in result.scopes
        if sc.get("kind") == "function"
        for name, defs in sc["names"].items()
        for (_l, kind) in defs
    }
    assert param_kinds.get("x") == "func_arg"
    assert param_kinds.get("self") == "first_param"


def test_staticmethod_wrapped_class_body_lambda_keeps_its_real_first_parameter():
    """frob = staticmethod(lambda a, b: ...) at class scope has the
    same "no implicit self" property as a @staticmethod def, but
    the class-body-lambda-as-method scan dropped its first real
    parameter (a) unconditionally, the same bug as the decorator case
    above but for this different, lambda-based spelling of it."""
    result = build("""
        class K:
        \tfrob = staticmethod(lambda a, b: a + b)
        K.frob(a=1, b=2)
        """)
    assert result.call_kwargs.get(3) == {"a", "b"}


def test_classmethod_wrapped_class_body_lambda_still_drops_its_implicit_first_parameter():
    """The contrasting case: classmethod(lambda cls, a, b: ...) does
    have an implicit first parameter (cls), so it should still be
    dropped - only staticmethod's wrapped lambda should keep it."""
    result = build("""
        class K:
        \tfrob = classmethod(lambda cls, a, b: a + b)
        K.frob(a=1, b=2)
        """)
    assert result.call_kwargs.get(3) == {"a", "b"}


def test_a_super_call_s_keyword_arguments_are_validated_against_the_base_class_s_method():
    result = build("""
        class Base:
        \tdef __init__(self, a, b):
        \t\tpass
        class Sub(Base):
        \tdef __init__(self, a, b):
        \t\tsuper().__init__(a=a, b=b)
        """)
    assert result.call_kwargs.get(6) == {"a", "b"}


def test_a_catch_all_kwargs_method_on_an_instance_accepts_any_keyword_name():
    result = build("""
        class K:
        \tdef greet(self, **kw):
        \t\tpass
        k = K()
        k.greet(anything=1)
        """)
    assert result.call_kwargs.get(5) == {"anything"}


def test_functools_partial_aliases_through_to_the_wrapped_callable_s_parameters():
    result = build("""
        from functools import partial
        def f(a, b):
        \tpass
        p = partial(f)
        p(a=1, b=2)
        """)
    assert result.call_kwargs.get(5) == {"a", "b"}


# ---------------------------------------------------------------------------
# Module-boundary resolution
#
# Everything above resolves within one file; a function/method/class
# defined in a *different*, separately-imported local module needs the
# same resolution - its real source gets opened and AST-inspected too
# (see _python_resolve_module_func_params()/_python_resolve_module_method()),
# not just stdlib modules.
# ---------------------------------------------------------------------------


@pytest.fixture
def helper_module(tmp_path, no_target_interpreter):
    """A sibling module, next to the file under test, with one real
    function and one real class to resolve things against."""
    (tmp_path / "helper_module.py").write_text(
        "def func(a, b):\n\tpass\nclass MyClass:\n\tdef method(self, a, b):\n\t\tpass\n"
    )
    return StubBuffer(title=str(tmp_path / "main.py"))


def test_a_function_defined_in_a_separately_imported_module_gets_its_kwargs_validated(
    helper_module,
):
    result = build(
        """
        import helper_module
        helper_module.func(a=1, b=2)
        """,
        buf=helper_module,
    )
    assert result.call_kwargs.get(2) == {"a", "b"}


def test_an_unrecognized_kwarg_is_rejected_even_for_a_module_defined_class_s_method(
    helper_module,
):
    result = build(
        """
        import helper_module
        x = helper_module.MyClass()
        x.method(a=3, c=4)
        """,
        buf=helper_module,
    )
    assert result.call_kwargs.get(3) == {"a"}


def test_a_from_import_of_a_module_function_still_gets_its_kwargs_validated(
    helper_module,
):
    result = build(
        """
        from helper_module import func
        func(a=1, c=2)
        """,
        buf=helper_module,
    )
    assert result.call_kwargs.get(2) == {"a"}


def test_a_subclass_of_a_module_defined_class_inherits_its_method_s_real_parameters(
    helper_module,
):
    result = build(
        """
        from helper_module import MyClass
        class Sub(MyClass):
        \tpass
        s = Sub()
        s.method(a=1, b=2)
        """,
        buf=helper_module,
    )
    assert result.call_kwargs.get(5) == {"a", "b"}


def test_a_dotted_import_as_alias_still_resolves_the_submodule_s_function(
    tmp_path, no_target_interpreter
):
    package = tmp_path / "dotted_pkg"
    package.mkdir()
    (package / "__init__.py").write_text("")
    (package / "sub.py").write_text("def func(a, b):\n\tpass\n")
    buf = StubBuffer(title=str(tmp_path / "main.py"))
    result = build(
        """
        import dotted_pkg.sub as s
        s.func(a=1, b=2)
        """,
        buf=buf,
    )
    assert result.call_kwargs.get(2) == {"a", "b"}


def test_a_class_in_one_module_inherits_a_method_from_a_base_defined_in_the_same_module(
    tmp_path, no_target_interpreter
):
    (tmp_path / "helper_module3.py").write_text(
        "class Base:\n\tdef base_method(self):\n\t\tpass\n"
        "class Derived(Base):\n\tdef derived_method(self):\n\t\tpass\n"
    )
    buf = StubBuffer(title=str(tmp_path / "main.py"))
    result = build(
        """
        from helper_module3 import Derived
        d = Derived()
        d.base_method()
        d.derived_method()
        """,
        buf=buf,
    )
    assert attr_kind(result, "base_method", 3) == "func"
    assert attr_kind(result, "derived_method", 4) == "func"


def test_a_class_inherits_through_a_base_defined_in_a_second_separate_module(
    tmp_path, no_target_interpreter
):
    """Derived (in mid_module) inherits from base_module.Base - a
    *different* module than the one Derived itself lives in - and the
    file under test only ever imports Derived, two hops removed from
    where base_method is actually defined."""
    (tmp_path / "base_module.py").write_text(
        "class Base:\n\tdef base_method(self):\n\t\tpass\n"
    )
    (tmp_path / "mid_module.py").write_text(
        "import base_module\n"
        "class Derived(base_module.Base):\n\tdef derived_method(self):\n\t\tpass\n"
    )
    buf = StubBuffer(title=str(tmp_path / "main.py"))
    result = build(
        """
        from mid_module import Derived
        d = Derived()
        d.base_method()
        """,
        buf=buf,
    )
    assert attr_kind(result, "base_method", 3) == "func"


def test_a_base_class_imported_under_an_alias_is_still_chased_correctly(
    tmp_path, no_target_interpreter
):
    """mid_module does `from base_module import Base as RenamedBase` and
    inherits from RenamedBase - the base-class chasing has to follow
    that import-time rename, not just a same-name reference."""
    (tmp_path / "base_module4.py").write_text(
        "class Base:\n\tdef base_method(self, a, b):\n\t\tpass\n"
    )
    (tmp_path / "mid_module4.py").write_text(
        "from base_module4 import Base as RenamedBase\n"
        "class Derived(RenamedBase):\n\tpass\n"
    )
    buf = StubBuffer(title=str(tmp_path / "main.py"))
    result = build(
        """
        from mid_module4 import Derived
        d = Derived()
        d.base_method(a=1, b=2)
        """,
        buf=buf,
    )
    assert result.call_kwargs.get(3) == {"a", "b"}


def test_a_nested_class_accessed_through_its_outer_class_resolves_its_own_methods():
    result = build("""
        class Outer:
        \tclass Inner:
        \t\tdef m(self):
        \t\t\tpass
        x = Outer.Inner()
        x.m()
        """)
    assert attr_kind(result, "m", 6) == "func"


def test_a_doubly_nested_class_accessed_through_two_outer_classes_resolves_its_methods():
    result = build("""
        class A:
        \tclass B:
        \t\tclass C:
        \t\t\tdef m(self):
        \t\t\t\tpass
        x = A.B.C()
        x.m()
        """)
    assert attr_kind(result, "m", 7) == "func"


def test_a_class_through_a_submodule_hop_resolves_its_init_kwargs_and_methods(
    tmp_path, no_target_interpreter
):
    """import pkg3; pkg3.sub.Thing() - the dotted chain passes through
    one module (pkg3), then its submodule (sub), before finally
    reaching the class (Thing) - each hop has to be resolved in turn."""
    package = tmp_path / "pkg3"
    package.mkdir()
    (package / "__init__.py").write_text("")
    (package / "sub.py").write_text("class Thing:\n\tdef m(self, a):\n\t\tpass\n")
    buf = StubBuffer(title=str(tmp_path / "main.py"))
    result = build(
        """
        import pkg3
        x = pkg3.sub.Thing()
        x.m(a=1)
        """,
        buf=buf,
    )
    assert result.call_kwargs.get(3) == {"a"}


def test_instantiating_a_nested_class_through_self_validates_its_init_s_kwargs():
    result = build("""
        class Outer:
        \tclass Inner:
        \t\tdef __init__(self, a, b):
        \t\t\tpass
        \tdef make(self):
        \t\treturn self.Inner(a=1, b=2)
        """)
    assert result.call_kwargs.get(6) == {"a", "b"}


def test_a_metaclass_keyword_argument_in_a_class_statement_is_always_recognized():
    result = build("""
        class Foo(metaclass=type):
        \tpass
        """)
    assert result.call_kwargs.get(1) == {"metaclass"}


def test_a_class_definition_keyword_argument_is_validated_against_init_subclass():
    result = build("""
        class Base:
        \tdef __init_subclass__(cls, custom_kw=None, **kw):
        \t\tpass
        class Sub(Base, custom_kw=1):
        \tpass
        """)
    assert result.call_kwargs.get(4) == {"custom_kw"}


def test_a_class_attribute_aliased_to_a_builtin_type_is_itself_colored_as_a_class():
    """K.helper = list makes K.helper (and so k.helper) a class-like
    name, the same as if it had been a real nested class - calling it
    is instantiating something, not an ordinary method call."""
    result = build("""
        class K:
        \tpass
        K.helper = list
        k = K()
        k.helper
        """)
    assert attr_kind(result, "helper", 5) == "class"


def test_a_self_attribute_aliased_to_a_builtin_type_is_itself_colored_as_a_class():
    result = build("""
        class K:
        \tdef __init__(self):
        \t\tself.Alias = list
        k = K()
        k.Alias
        """)
    assert attr_kind(result, "Alias", 5) == "class"


# ---------------------------------------------------------------------------
# Python-shell session continuity
#
# Ordinarily the shell needs no seed_* at all: _hapyshell_body() always
# re-analyzes the *entire* cumulative transcript as one text blob, so a
# later statement referencing an earlier one's bindings is just ordinary
# same-text resolution (already covered above). seed_* exists
# specifically for when that assumption breaks - text that scrolled out
# of the transcript (or was explicitly cleared) but whose bindings
# should still be known. These test that narrower, real guarantee:
# resolution purely from a previous result's seed_*, with none of the
# original defining text available to re-derive it from.
# ---------------------------------------------------------------------------


def test_session_seeding_carries_a_self_attribute_s_type_once_its_defining_text_is_gone():
    result = run_session(
        [
            """
            class K:
            \tdef __init__(self):
            \t\tself.properties = {}
            k = K()
            """,
            """
            k.properties.update({})
            """,
        ]
    )
    assert attr_kind(result, "update", 1) == "func"


def test_session_seeding_carries_inherited_attribute_types_through_a_subclass_too():
    result = run_session(
        [
            """
            class Big:
            \tdef __init__(self):
            \t\tself.properties = {}
            class Small(Big):
            \tpass
            small = Small()
            """,
            """
            small.properties.update({})
            """,
        ]
    )
    assert attr_kind(result, "update", 1) == "func"


def test_an_invalidation_in_the_current_statement_overrides_seeded_history():
    """A reassignment in the statement actually being analyzed must win
    over whatever an earlier (now gone) statement seeded forward - the
    seed is only ever a fallback default, never a fact that overrides
    what the current text itself says."""
    result = run_session(
        [
            """
            class K:
            \tdef __init__(self):
            \t\tself.properties = {}
            k = K()
            """,
            """
            k.properties = None
            k.properties.update({})
            """,
        ]
    )
    assert attr_kind(result, "update", 2) is None


def test_per_instance_invalidation_is_not_part_of_what_a_session_seeds_forward():
    """var_attr_types - the per-variable tracking that keeps one
    instance's invalidated attribute from affecting a different
    instance of the same class (see the per-instance isolation section
    above) - has no seed_var_attr_types counterpart at all: it is local
    to one _python_build_scopes() call. In the real shell this never
    matters, since the whole transcript (including the reassignment) is
    always right there to re-derive it from on every call; it only
    shows up in this artificial seed-only-continuity scenario, where an
    external reassignment and the text that reads it afterwards end up
    in two separate calls with nothing but seed_class_attr_types
    between them - so the class-level (not per-instance) type is all
    that is left to resolve from, same as if the reassignment had never
    happened. Documented here as a known boundary, not something to
    "fix" by inventing a seed for a structure the real caller never
    actually needs seeded."""
    result = run_session(
        [
            """
            class K:
            \tdef __init__(self):
            \t\tself.properties = {}
            k = K()
            """,
            """
            k.properties = None
            """,
            """
            k.properties.update({})
            """,
        ]
    )
    assert attr_kind(result, "update", 1) == "func"


# ---------------------------------------------------------------------------
# Module/import resolution
#
# _python_resolve_toplevel_fs() locates a top-level import by looking in
# the edited file's own directory (so a sibling, not-yet-installed
# module resolves the same way Python's own sys.path[0] convention
# would for the directly-run script), then by asking the configured
# target interpreter (state.pythonexecutable) for its own sys.path via a
# real subprocess - never PyNotes' own sys.path, which belongs to a
# different interpreter/venv entirely and has no bearing on what the
# edited file could actually import.
# ---------------------------------------------------------------------------


@pytest.fixture
def no_target_interpreter(monkeypatch):
    """state.pythonexecutable unset (or pointing nowhere) - the
    subprocess-query fallback must degrade to "nothing found" rather
    than raising."""
    monkeypatch.setattr(state, "pythonexecutable", None, raising=False)
    yield


def test_sibling_package_in_the_edited_file_s_own_directory_resolves(
    tmp_path, no_target_interpreter
):
    """A package living right next to the edited file (e.g. a
    not-yet-installed in-development module) must resolve even though
    it is nowhere on any interpreter's sys.path - this is what lets
    `import canvastk` work when editing a sibling file inside the same
    project directory."""
    package = tmp_path / "sibling_package"
    package.mkdir()
    (package / "__init__.py").write_text("class Widget:\n\tdef frob(self):\n\t\tpass\n")
    buf = StubBuffer(title=str(tmp_path / "main.py"))
    result = build(
        """
        import sibling_package
        w = sibling_package.Widget()
        w.frob()
        """,
        buf=buf,
    )
    assert attr_kind(result, "frob", 3) == "func"


def test_a_buffer_with_no_title_does_not_crash_resolution(no_target_interpreter):
    """PythonShellBuffer (the Python shell's own buffer class) has no
    file and so no title attribute at all - _python_resolve_toplevel_fs()
    used to assume buf.title always exists and crashed every shell
    highlight pass with AttributeError the moment any import appeared in
    the session. Resolution should just fall through to the next
    fallback (here, nothing at all) instead of raising."""
    buf = StubBuffer()
    assert not hasattr(buf, "title")
    result = build(
        """
        import some_module_that_does_not_exist_anywhere
        """,
        buf=buf,
    )
    assert result.local_classes is not None


def test_a_name_not_found_anywhere_simply_does_not_resolve(
    tmp_path, no_target_interpreter
):
    buf = StubBuffer(title=str(tmp_path / "main.py"))
    result = build(
        """
        import some_module_that_does_not_exist_anywhere
        x = some_module_that_does_not_exist_anywhere.Thing()
        x.whatever()
        """,
        buf=buf,
    )
    assert attr_kind(result, "whatever", 3) is None


def test_target_interpreter_s_own_sys_path_is_queried_not_pynotes_own(
    tmp_path, monkeypatch
):
    """Querying state.pythonexecutable's sys.path happens via a real
    subprocess (so it reflects that interpreter/venv, not whatever
    PyNotes itself happens to be running under) with cwd set to the
    edited file's directory - exercised here with sys.executable (this
    test process's own interpreter) standing in for the configured one,
    which is guaranteed to exist and makes the test deterministic."""
    monkeypatch.setattr(state, "pythonexecutable", sys.executable, raising=False)
    _PYTHON_TARGET_SYS_PATH_CACHE.clear()
    buf = StubBuffer(title=str(tmp_path / "main.py"))
    result = build(
        """
        import json
        x = json.JSONDecoder()
        x.decode('{}')
        """,
        buf=buf,
    )
    assert attr_kind(result, "decode", 3) == "func"


def test_target_interpreter_sys_path_query_is_cached_per_interpreter_and_cwd(
    tmp_path, monkeypatch
):
    """Spawning a subprocess on every single scan would make typing in
    the shell or editor noticeably laggy, so the result is cached by
    (interpreter, cwd) - changing either one (here, the cwd, by editing
    a file in a different directory) must still produce a fresh,
    independent cache entry rather than reusing a stale one from an
    unrelated directory."""
    monkeypatch.setattr(state, "pythonexecutable", sys.executable, raising=False)
    _PYTHON_TARGET_SYS_PATH_CACHE.clear()
    first_dir = tmp_path / "first"
    second_dir = tmp_path / "second"
    first_dir.mkdir()
    second_dir.mkdir()
    build("import json\n", buf=StubBuffer(title=str(first_dir / "a.py")))
    build("import json\n", buf=StubBuffer(title=str(second_dir / "b.py")))
    assert len(_PYTHON_TARGET_SYS_PATH_CACHE) == 2


def test_an_interpreter_that_is_not_actually_python_does_not_crash_resolution(
    tmp_path, monkeypatch
):
    """A misconfigured state.pythonexecutable (not Python at all, or
    missing) must degrade to "nothing found" rather than raising, since
    this runs as part of ordinary, non-blocking highlighting."""
    monkeypatch.setattr(
        state, "pythonexecutable", "/definitely/not/a/real/interpreter", raising=False
    )
    _PYTHON_TARGET_SYS_PATH_CACHE.clear()
    buf = StubBuffer(title=str(tmp_path / "main.py"))
    result = build(
        """
        import some_module_that_does_not_exist_anywhere
        """,
        buf=buf,
    )
    assert result.local_classes is not None
