"""Python syntax highlighting: python_scope_build._python_highlight_ops(), which
turns the scope analysis of _python_build_scopes() into the tag operations
that editor.py's ha() and the Python shell apply to the text. Both run on the
text alone, so no display is needed.

The tags: hpa keyword, hpo operator, hpd string, hpc comment, hpv variable,
hpi instance of a class, hpf function, hpfa function argument, hpx class,
hpm module, hpb builtin or first parameter.
"""

import re
import sys
import textwrap

import pytest

import state
from python_scope_build import (
    _PYTHON_KW_PAT,
    _PYTHON_OP_PAT,
    _PythonStandaloneScanHost,
    _python_build_scopes,
    _python_bytecol_to_charcol,
    _python_highlight_ops,
)

OFFSET = re.compile(r"\+(\d+)c")


@pytest.fixture(autouse=True)
def target_interpreter(monkeypatch):
    """Module resolution asks the interpreter the edited code would run on."""
    monkeypatch.setattr(state, "pythonexecutable", sys.executable, raising=False)


def analyse(text, title=None):
    host = _PythonStandaloneScanHost()
    host.title = title
    result = _python_build_scopes(host, text)
    assert result is not None, "the snippet failed to parse at all"
    return result


def highlight_ops(text, pre_text="", title=None, top="1.0"):
    """_python_highlight_ops() on the analysis of text, the way the editor
    calls it."""
    result = analyse(pre_text + text, title) if pre_text else analyse(text, title)
    (
        scopes,
        call_kwargs,
        _module_aliases,
        _local_classes,
        module_literals,
        _scope_var_types,
        literal_attrs,
        def_names,
        typed_attrs,
        param_default_tags,
        kwarg_positions,
        import_dotted_lines,
        import_orig_name_tags,
        *_,
    ) = result
    name_positions = result[16]
    instance_name_positions = result[27]
    global_stmt_kind_positions = result[28]
    return _python_highlight_ops(
        text,
        top,
        pre_text,
        scopes,
        call_kwargs,
        module_literals,
        literal_attrs,
        name_positions,
        def_names,
        typed_attrs,
        param_default_tags,
        kwarg_positions,
        import_dotted_lines,
        instance_name_positions,
        global_stmt_kind_positions,
        import_orig_name_tags,
    )


def highlight(code, **kwargs):
    """The (tag, text) pairs the highlighter applies to dedented code."""
    text = textwrap.dedent(code).strip("\n")
    pre_text = kwargs.get("pre_text", "")
    pairs = []
    for operation in highlight_ops(text, **kwargs):
        if operation[0] != "add":
            continue
        start, end = (int(OFFSET.search(index).group(1)) for index in operation[2:4])
        pairs.append((operation[1], text[start:end]))
    return pairs


def words(pairs, tag):
    return [text for pair_tag, text in pairs if pair_tag == tag]


# ---------------------------------------------------------------------------
# Keywords and operators
# ---------------------------------------------------------------------------


def test_keywords_are_highlighted():
    pairs = highlight("if x and not y:\n    pass")

    assert words(pairs, "hpa") == ["if", "and", "not", "pass"]


def test_none_true_and_false_are_keywords():
    assert words(highlight("a = None\nb = True\nc = False"), "hpa") == [
        "None",
        "True",
        "False",
    ]


def test_a_word_after_a_dot_is_not_a_keyword():
    assert _PYTHON_KW_PAT.findall("obj.import and import") == ["and", "import"]


def test_a_keyword_inside_a_longer_word_is_not_a_keyword():
    assert _PYTHON_KW_PAT.findall("important iffy classy") == []


@pytest.mark.parametrize(
    "operator",
    [
        "**=",
        "//=",
        "<<=",
        ">>=",
        ":=",
        "==",
        "!=",
        "<=",
        ">=",
        "+=",
        "-=",
        "*=",
        "/=",
        "%=",
        "&=",
        "|=",
        "^=",
        "@=",
        "->",
        "**",
        "//",
        "<<",
        ">>",
        "+",
        "-",
        "*",
        "/",
        "%",
        "@",
        "&",
        "|",
        "^",
        "~",
        "=",
        "<",
        ">",
    ],
)
def test_every_operator_is_one_token(operator):
    assert _PYTHON_OP_PAT.findall(f"a {operator} b") == [operator]


def test_operators_are_highlighted_in_code():
    pairs = highlight("x = 1\nx += 2\nx //= 3\ny = x ** 2")

    assert words(pairs, "hpo") == ["=", "+=", "//=", "=", "**"]


# ---------------------------------------------------------------------------
# Strings and comments
# ---------------------------------------------------------------------------


def test_strings_are_highlighted_with_their_quotes():
    pairs = highlight("a = 'single'\nb = \"double\"")

    assert words(pairs, "hpd") == ["'single'", '"double"']


def test_a_string_ends_at_its_closing_quote_despite_an_escaped_one():
    assert words(highlight(r"s = 'it\'s'"), "hpd") == [r"'it\'s'"]


def test_triple_quoted_strings_span_lines():
    pairs = highlight('doc = """first\nsecond"""\nx = 1')

    assert words(pairs, "hpd") == ['"""first\nsecond"""']


def test_an_unterminated_string_runs_to_the_end_of_its_line():
    assert words(highlight('u = "open'), "hpd") == ['"open']


def test_comments_are_highlighted_up_to_and_with_the_newline():
    pairs = highlight("# first\nx = 1  # second\ny = 2")

    assert words(pairs, "hpc") == ["# first\n", "# second\n"]


def test_a_comment_at_the_end_of_the_text_has_no_newline():
    assert words(highlight("# only"), "hpc") == ["# only"]


def test_a_hash_inside_a_string_is_not_a_comment():
    pairs = highlight('x = "#no"')

    assert words(pairs, "hpc") == []
    assert words(pairs, "hpd") == ['"#no"']


def test_quotes_inside_a_comment_do_not_start_a_string():
    pairs = highlight('x = 1  # it\'s "quoted"\ny = 2')

    assert words(pairs, "hpd") == []
    assert words(pairs, "hpc") == ['# it\'s "quoted"\n']


def test_text_that_starts_inside_a_triple_quoted_string_is_a_string_until_it_closes():
    pre_text = 'x = """start\n'

    pairs = highlight('abc"""\ny = 2', pre_text=pre_text)

    assert words(pairs, "hpd") == ['abc"""']


def test_text_after_a_closed_triple_quoted_string_is_not_a_string():
    pre_text = 'x = """one\ntwo"""\n'

    pairs = highlight("y = 2", pre_text=pre_text)

    assert words(pairs, "hpd") == []


def test_a_comment_in_the_text_before_does_not_hide_a_following_string_start():
    pre_text = '# """ not a string\n'

    pairs = highlight('z = "real"', pre_text=pre_text)

    assert words(pairs, "hpd") == ['"real"']


# ---------------------------------------------------------------------------
# Names
# ---------------------------------------------------------------------------


def test_functions_classes_and_their_calls():
    pairs = highlight("""
        class Box:
            def open(self):
                return self
        def make():
            return Box()
        make()
        """)

    assert words(pairs, "hpx").count("Box") == 2
    assert words(pairs, "hpf").count("make") == 2
    assert "open" in words(pairs, "hpf")


def test_parameters_are_function_arguments_and_self_is_a_builtin_colour():
    pairs = highlight("""
        def f(a, b=2):
            return a + b
        class K:
            def m(self):
                return self
        """)

    assert words(pairs, "hpfa") == ["a", "b", "a", "b"]
    assert words(pairs, "hpb") == ["self", "self"]


def test_builtins_are_highlighted():
    pairs = highlight("print(len([1]))")

    assert words(pairs, "hpb") == ["print", "len"]


def test_unknown_names_are_not_highlighted():
    pairs = highlight("print(undefined_name)")

    assert "undefined_name" not in [text for _, text in pairs]


def test_a_keyword_argument_that_the_function_takes_is_a_function_argument():
    pairs = highlight("""
        def f(a, b=2): pass
        f(1, b=3)
        f(1, c=4)
        """)

    assert words(pairs, "hpfa") == ["a", "b", "b"]


def test_an_instance_of_a_local_class_is_an_instance():
    pairs = highlight("""
        class D:
            pass
        d = D()
        """)

    assert words(pairs, "hpi") == ["d"]


def test_a_plain_variable_is_a_variable():
    assert words(highlight("x = 1\ny = x"), "hpv") == ["x", "y", "x"]


def test_methods_of_builtin_values_are_functions():
    pairs = highlight('x = "a"\nx.upper()')

    assert "upper" in words(pairs, "hpf")


def test_a_name_assigned_inside_a_function_is_not_highlighted_outside_it():
    pairs = highlight("""
        def f():
            loc = 1
            return loc
        print(loc)
        """)

    assert words(pairs, "hpv") == ["loc", "loc"]


def test_a_module_level_name_is_visible_inside_a_function():
    pairs = highlight("x = 1\ndef f():\n    return x")

    assert words(pairs, "hpv") == ["x", "x"]


def test_a_name_from_an_enclosing_function_is_visible_in_the_inner_one():
    pairs = highlight("""
        def f(a):
            def g(b):
                return a + b
            return g
        """)

    assert words(pairs, "hpfa").count("a") == 2


def test_a_class_attribute_is_not_visible_inside_its_methods():
    pairs = highlight("""
        class C:
            attr = 1
            def m(self):
                return attr
        """)

    assert words(pairs, "hpv") == ["attr"]


def test_a_global_name_assigned_in_a_function_is_visible_outside():
    pairs = highlight("""
        def f():
            global G
            G = 1
        print(G)
        """)

    assert words(pairs, "hpv") == ["G", "G", "G"]


def test_the_loop_variable_is_visible_after_the_loop():
    pairs = highlight("for i in range(3): print(i)\nprint(i)")

    assert words(pairs, "hpv") == ["i", "i", "i"]


def test_names_in_exceptions_and_with_blocks():
    pairs = highlight("""
        try:
            pass
        except Exception as e:
            print(e)
        with open("f") as fh:
            fh.read()
        """)

    assert words(pairs, "hpv") == ["e", "e", "fh", "fh"]
    assert "Exception" in words(pairs, "hpb")


def test_names_in_comprehensions_and_lambdas():
    pairs = highlight("x = [i for i in range(3)]\nlambda q: q")

    assert words(pairs, "hpv").count("i") == 2
    assert words(pairs, "hpfa") == ["q", "q"]


def test_unpacking_and_chained_assignment_highlight_every_target():
    pairs = highlight("x = y = 0\nx, y = 1, 2")

    assert words(pairs, "hpv") == ["x", "y", "x", "y"]


def test_a_walrus_target_is_a_variable():
    assert words(highlight("a = (b := 3)"), "hpv") == ["a", "b"]


# ---------------------------------------------------------------------------
# Imports and modules
# ---------------------------------------------------------------------------


@pytest.fixture
def sibling_package(tmp_path):
    package = tmp_path / "highlightpkg"
    package.mkdir()
    (package / "__init__.py").write_text(
        "class Widget:\n\tdef frob(self):\n\t\tpass\n"
        "constant = 1\n"
        "def helper(a, b):\n\tpass\n"
    )
    return str(tmp_path / "main.py")


def test_an_imported_module_and_its_members(sibling_package):
    pairs = highlight(
        """
        import highlightpkg
        w = highlightpkg.Widget()
        w.frob()
        highlightpkg.helper(1, 2)
        highlightpkg.constant
        """,
        title=sibling_package,
    )

    assert words(pairs, "hpm") == ["highlightpkg"] * 4
    assert "Widget" in words(pairs, "hpx")
    assert words(pairs, "hpf").count("helper") == 1
    assert "frob" in words(pairs, "hpf")
    assert "constant" in words(pairs, "hpv")
    assert words(pairs, "hpi") == ["w", "w"]


def test_an_import_alias_is_a_module(sibling_package):
    pairs = highlight("import highlightpkg as hp\nhp.Widget()", title=sibling_package)

    assert words(pairs, "hpm") == ["hp", "highlightpkg", "hp"]
    assert "Widget" in words(pairs, "hpx")


def test_names_imported_from_a_module_take_their_kind(sibling_package):
    pairs = highlight(
        "from highlightpkg import Widget, helper as h\nWidget()\nh(1, 2)",
        title=sibling_package,
    )

    assert words(pairs, "hpm") == ["highlightpkg"]
    assert words(pairs, "hpx") == ["Widget", "Widget"]
    assert words(pairs, "hpf") == ["h", "helper", "h"]


def test_every_part_of_a_dotted_import_is_a_module():
    pairs = highlight('import os.path\nos.path.join("a")')

    assert words(pairs, "hpm") == ["os", "path", "os", "path"]
    assert "join" in words(pairs, "hpf")


def test_a_module_that_does_not_exist_is_not_highlighted():
    pairs = highlight("import no_such_module_anywhere_xyz")

    assert words(pairs, "hpm") == []


# ---------------------------------------------------------------------------
# Positions
# ---------------------------------------------------------------------------


def test_columns_after_non_ascii_text_are_character_columns():
    pairs = highlight('s = "é"; t = 1\néé = 2')

    assert words(pairs, "hpv") == ["s", "t", "éé"]
    assert words(pairs, "hpd") == ['"é"']


@pytest.mark.parametrize(
    ("line", "byte_column", "character_column"),
    [
        ("abc", 2, 2),
        ("éa", 2, 1),
        ("éa", 3, 2),
        ("a€b", 4, 2),
        ("abc", 99, 3),
        ("abc", 0, 0),
        ("abc", -1, -1),
    ],
)
def test_byte_columns_become_character_columns(line, byte_column, character_column):
    assert _python_bytecol_to_charcol(line, byte_column) == character_column


def test_operations_are_relative_to_the_top_index_given():
    operations = _python_highlight_ops(
        "if x:\n    pass", "7.0", "", [], {}, [], [], [], [], [], [], [], [], {}, {}, []
    )

    assert ("add", "hpa", "7.0+0c", "7.0+2c") in operations
    assert ("add", "hpa", "7.0+10c", "7.0+14c") in operations


def test_text_without_any_analysis_still_gets_keywords_strings_and_comments():
    operations = _python_highlight_ops(
        'return "a"  # b', "1.0", "", [], {}, [], [], [], [], [], [], [], [], {}, {}, []
    )

    assert ("add", "hpa", "1.0+0c", "1.0+6c") in operations
    assert ("add", "hpd", "1.0+7c", "1.0+10c") in operations
    assert ("add", "hpc", "1.0+12c", "1.0+15c") in operations
