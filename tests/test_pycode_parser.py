"""The PyCode parser: string, comment and bracket scanning, and the
translation of PyCode to Python. It is pure text processing, so no display
is needed."""

import pytest

import pycode
import state
from pycode import (
    PyCodeError,
    PyCodeFunction,
    pycode_bracket_match,
    pycode_remove_comments,
    pycode_string_ranges,
    pycodeparse,
)

# ---------------------------------------------------------------------------
# pycode_string_ranges
# ---------------------------------------------------------------------------


def test_string_ranges_maps_opening_quote_to_closing_quote():
    assert pycode_string_ranges("a \"b\" 'cd'") == {2: 4, 6: 9}


def test_string_ranges_skips_escaped_quotes():
    assert pycode_string_ranges(r'"a\"b"') == {0: 5}


def test_string_ranges_ignores_quotes_inside_comments():
    assert pycode_string_ranges("a # \"b\n'c'") == {7: 9}


def test_string_ranges_of_text_without_strings_is_empty():
    assert pycode_string_ranges("a = 1") == {}


@pytest.mark.parametrize("text", ['"abc', "'abc", 'a = "b\\"'])
def test_string_ranges_rejects_unterminated_strings(text):
    with pytest.raises(PyCodeError, match="unmatched"):
        pycode_string_ranges(text)


def test_string_error_reports_line_and_column_and_context():
    with pytest.raises(PyCodeError) as info:
        pycode_string_ranges('a = 1\n  "oops', inwhat="of the test")
    assert str(info.value).startswith("line 2 of the test, column 3,")


# ---------------------------------------------------------------------------
# pycode_remove_comments
# ---------------------------------------------------------------------------


def test_remove_comments_blanks_comments_and_keeps_indices():
    text = "a # b\nc"
    result = pycode_remove_comments(text)
    assert result == "a    \nc"
    assert len(result) == len(text)


def test_remove_comments_keeps_hashes_inside_strings():
    assert pycode_remove_comments('"#" # c') == '"#"    '


def test_remove_comments_handles_a_comment_on_the_last_line():
    assert pycode_remove_comments("x # end") == "x      "


def test_remove_comments_leaves_text_without_comments_alone():
    assert pycode_remove_comments("x = 1\ny = 2") == "x = 1\ny = 2"


# ---------------------------------------------------------------------------
# pycode_bracket_match
# ---------------------------------------------------------------------------


def test_bracket_match_returns_opening_to_closing_indices():
    assert pycode_bracket_match("f([1], {2})") == {1: 10, 2: 4, 7: 9}


def test_bracket_match_ignores_brackets_in_strings():
    assert pycode_bracket_match('"(" []') == {4: 5}


def test_bracket_match_of_text_without_brackets_is_empty():
    assert pycode_bracket_match("a = 1") == {}


def test_bracket_match_rejects_mismatched_brackets():
    with pytest.raises(PyCodeError, match="does not match opening bracket '\\('"):
        pycode_bracket_match("(]")


def test_bracket_match_rejects_an_unmatched_closing_bracket():
    with pytest.raises(PyCodeError, match="unmatched '\\)'"):
        pycode_bracket_match("a)")


def test_bracket_match_rejects_an_unclosed_bracket():
    with pytest.raises(PyCodeError, match="'\\{' was never closed"):
        pycode_bracket_match("a {")


# ---------------------------------------------------------------------------
# pycodeparse
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("code", "expected"),
    [
        ("a = 2; b = 3;", ["a = 2", "b = 3"]),
        ("x = 1", ["x = 1"]),
        ("x = 1 # comment", ["x = 1"]),
        ("break; continue; pass", ["break", "continue", "pass"]),
        ("return 5", ["return 5"]),
        ("del x", ["del x"]),
        ("global g; nonlocal h", ["global g", "nonlocal h"]),
        ("f(1, k=2)", ["f(1, k=2)"]),
        ("l = [i for i in range(5)]", ["l = [i for i in range(5)]"]),
        ("x = (True if 2 + 3 < 5 else False)", ["x = True if 2 + 3 < 5 else False"]),
    ],
)
def test_simple_statements_translate_to_python(code, expected):
    assert pycodeparse(code, {}) == expected


def test_empty_code_has_no_blocks():
    assert pycodeparse("", {}) == []
    assert pycodeparse("# only a comment", {}) == []


def test_whitespace_between_tokens_is_ignored():
    assert pycodeparse("a\n=\n  2", {}) == ["a = 2"]


def test_strings_are_normalised_and_newlines_in_them_are_escaped():
    assert pycodeparse('x = "hi"', {}) == ["x = 'hi'"]
    assert pycodeparse('x = "a\nb"', {}) == ["x = 'a\\nb'"]


def test_function_definition_becomes_def():
    assert pycodeparse("add (a, b) {\n return a + b;\n};", {}) == [
        "def add(a, b):\n return a + b"
    ]


def test_nested_function_definitions_nest():
    assert pycodeparse("g () { h () { return 1; }; };", {}) == [
        "def g():\n def h():\n  return 1"
    ]


def test_if_elif_else_chain():
    code = "if (a) {x=1} elif (b) {x=2} else {x=3};"
    assert pycodeparse(code, {}) == ["if a:\n x = 1\nelif b:\n x = 2\nelse:\n x = 3"]


def test_while_loop():
    assert pycodeparse("while (i < 3) { i = i + 1; };", {}) == [
        "while i < 3:\n i = i + 1"
    ]


def test_commands_are_replaced_by_their_python_expressions():
    assert pycodeparse("save_file()", {}) == ["pcsavefile()"]
    assert pycodeparse('open_file("x")', {}) == ["pcopenfile('x')"]
    assert pycodeparse("show_popup('a\\nb')", {}) == ["say('a\\nb')"]


def test_commands_are_replaced_inside_conditions_and_lambdas():
    assert pycodeparse("if (save_file()) {pass};", {}) == ["if pcsavefile():\n pass"]
    assert pycodeparse("k = lambda q: save_file()", {}) == [
        "k = lambda q: pcsavefile()"
    ]


def test_every_command_is_translated_to_its_table_entry():
    for command, python in pycode.pycode_commands.items():
        assert pycodeparse(f"{command}()", {}) == [f"{python}()"]


def test_pycode_functions_in_defined_are_replaced_by_their_python_name():
    defined = {"mine": PyCodeFunction("user_mine")}
    assert pycodeparse("mine(1)", defined) == ["user_mine(1)"]


def test_names_bound_inside_an_expression_shadow_pycode_functions():
    defined = {"q": PyCodeFunction("user_q")}
    assert pycodeparse("k = lambda q: q", defined) == ["k = lambda q: q"]
    assert pycodeparse("k = [q for q in y]", defined) == ["k = [q for q in y]"]


@pytest.mark.parametrize(
    ("code", "message"),
    [
        ("a b", "invalid syntax"),
        ("x = ", "invalid syntax"),
        ("f(1,,2)", "invalid syntax"),
        ("if a {}", "invalid syntax"),
        ("else {}", "invalid syntax"),
        ("elif (a) {}", "invalid syntax"),
        ("if (a) {} else {} else {}", "invalid syntax"),
        ("while (a) {}; else {}", "invalid syntax"),
        ("x = 1 y = 2", "invalid syntax"),
        ("f (a b) {}", "invalid parameter 'a b'"),
        ("say(", "'\\(' was never closed"),
        ('x = "abc', "unmatched"),
    ],
)
def test_invalid_pycode_is_rejected(code, message):
    with pytest.raises(PyCodeError, match=message):
        pycodeparse(code, {})


def test_parse_error_names_line_and_column():
    with pytest.raises(PyCodeError) as info:
        pycodeparse("a = 1;\nb b", {}, inwhat="of the test")
    assert str(info.value).startswith("line 2 of the test, column")


# ---------------------------------------------------------------------------
# Parsing in depth
# ---------------------------------------------------------------------------


def translate(code, defined=None):
    return pycodeparse(code, defined or {})


def error_message(code, defined=None):
    """The message of the PyCodeError for code, without its position."""
    with pytest.raises(PyCodeError) as info:
        pycodeparse(code, defined or {})
    return str(info.value).split("\n", 1)[1]


@pytest.mark.parametrize(
    ("code", "expected"),
    [
        ("x.y = 1", ["x.y = 1"]),
        ("x[0] = 1", ["x[0] = 1"]),
        ("x, y = 1, 2", ["(x, y) = (1, 2)"]),
        ("(x, y) = (1, 2)", ["(x, y) = (1, 2)"]),
        ("a.b.c = d.e(f)", ["a.b.c = d.e(f)"]),
        ("x = (y == 2)", ["x = y == 2"]),
        ("x == 1", ["x == 1"]),
        ("x = y if z else w", ["x = y if z else w"]),
        ("x = a if b else c if d else e", ["x = a if b else c if d else e"]),
    ],
)
def test_assignments(code, expected):
    assert translate(code) == expected


@pytest.mark.parametrize(
    ("code", "message"),
    [
        ("1 = x", "invalid assignment target"),
        ("f() = 1", "invalid assignment target"),
        ("x += 1", "invalid syntax"),
        ("x = y = 3", "invalid syntax"),
        ("x = ", "invalid syntax"),
        (" = 1", "invalid syntax"),
        ("x: int = 1", "invalid syntax"),
    ],
)
def test_invalid_assignments(code, message):
    assert message in error_message(code)


@pytest.mark.parametrize(
    ("code", "expected"),
    [
        ("x = [i*2 for i in range(3) if i]", ["x = [i * 2 for i in range(3) if i]"]),
        ("x = {k: v for k, v in d}", ["x = {k: v for k, v in d}"]),
        ("x = lambda a, b=1: a + b", ["x = lambda a, b=1: a + b"]),
        ("x = not a", ["x = not a"]),
        ("x = a and b or c", ["x = a and b or c"]),
        ("x = a < b < c", ["x = a < b < c"]),
        ("x = a is not b", ["x = a is not b"]),
        ("x = a not in b", ["x = a not in b"]),
        ("x = *a, b", ["x = (*a, b)"]),
        ("x = [*a, *b]", ["x = [*a, *b]"]),
        ("x = {**a}", ["x = {**a}"]),
        ("x = a[1:2, ::3]", ["x = a[1:2, ::3]"]),
        ("x = ...", ["x = ..."]),
        ("x = -1", ["x = -1"]),
        ("x = await y", ["x = await y"]),
        ("x = (save_file := 1)", ["x = (save_file := 1)"]),
    ],
)
def test_python_expressions_are_accepted(code, expected):
    assert translate(code) == expected


@pytest.mark.parametrize(
    ("code", "expected"),
    [
        ('x = "a;b"', ["x = 'a;b'"]),
        ("x = 'a(b'", ["x = 'a(b'"]),
        ('x = "a # b" # c', ["x = 'a # b'"]),
        ('x = "a" "b"', ["x = 'ab'"]),
        ('x = """abc"""', ["x = 'abc'"]),
        ("x = ''", ["x = ''"]),
        ('x = f"{a}"', ["x = f'{a}'"]),
        ('x = r"\\d"', ["x = '\\\\d'"]),
        ('x = b"a"', ["x = b'a'"]),
        ("x = 1_000", ["x = 1000"]),
        ("x = 0x1F", ["x = 31"]),
        ("x = 1.5e3", ["x = 1500.0"]),
        ('x = "a\\nb"', ["x = 'a\\nb'"]),
        ('x = "line1\nline2"', ["x = 'line1\\nline2'"]),
    ],
)
def test_literals(code, expected):
    assert translate(code) == expected


@pytest.mark.parametrize(
    ("code", "expected"),
    [
        ("a.b(c)", ["a.b(c)"]),
        ("f(1)(2)", ["f(1)(2)"]),
        ("f(a)[0]", ["f(a)[0]"]),
        ("f(*a, **k)", ["f(*a, **k)"]),
        ("f(**o, x=1)", ["f(**o, x=1)"]),
        ("f(*a, x=1)", ["f(*a, x=1)"]),
        ('print(*a, sep="")', ["print(*a, sep='')"]),
        ("f(a,)", ["f(a)"]),
        ("f(f(1), g(h(2)))", ["f(f(1), g(h(2)))"]),
        ("f(x=(1, 2))", ["f(x=(1, 2))"]),
        ("f()", ["f()"]),
        ('f("a)")', ["f('a)')"]),
    ],
)
def test_calls(code, expected):
    assert translate(code) == expected


@pytest.mark.parametrize(
    ("code", "message"),
    [
        ("f(a=1, a=2)", "The argument 'a' is given more than once"),
        ("f(if=1)", "'if' cannot be used as an argument name"),
        ("f(a=)", "The argument 'a' has no value"),
        ("f(a, b=1, c)", "A plain argument must come before the named arguments"),
        ("f(,)", "invalid syntax"),
        ("f(a b)", "invalid syntax"),
        ("f(1 2)", "invalid syntax"),
    ],
)
def test_invalid_calls(code, message):
    assert message in error_message(code)


@pytest.mark.parametrize("code", ["f(x=1, **opts)", "f(x=1, *rest)"])
def test_unpacking_after_a_keyword_argument(code):
    assert translate(code) == [code]


@pytest.mark.parametrize(
    "code",
    [
        "f(*a, **b, c=1)",
        "f(a, *b, c)",
        "f(**a, **b)",
        "f(*a, *b)",
        "f(**a, c=1)",
        "f(x=1, *a, y=2)",
    ],
)
def test_unpacked_arguments_may_be_mixed_with_the_others(code):
    assert translate(code) == [code]


def test_a_space_after_the_stars_is_allowed():
    assert translate("f(* a, ** b)") == ["f(*a, **b)"]


def test_unpacked_arguments_are_translated_too():
    assert translate("f(*save_file, **open_file)") == ["f(*pcsavefile, **pcopenfile)"]


@pytest.mark.parametrize(
    ("code", "message"),
    [
        ("f(***a)", "There can be at most two * before an argument"),
        ("f(**a, *b)", "A * argument cannot come after a ** argument"),
        ("f(*)", "Nothing follows the *"),
        ("f(**)", "Nothing follows the *"),
        ("f(**a, b)", "A plain argument must come before the named arguments"),
    ],
)
def test_invalid_unpacked_arguments(code, message):
    assert message in error_message(code)


@pytest.mark.parametrize("name", ["for", "lambda", "import", "class", "try", "with"])
def test_a_function_cannot_be_named_like_a_python_keyword(name):
    assert f"invalid function name '{name}'" in error_message(f"{name} (a) {{}}")


@pytest.mark.parametrize(
    ("code", "expected"),
    [
        ("foo(a) {}", ["def foo(a):\n pass"]),
        ("foo() {}", ["def foo():\n pass"]),
        (
            "foo(a, b=2, *args, **kw) { return a }",
            ["def foo(a, b=2, *args, **kw):\n return a"],
        ),
        ("foo(*a, b) {}", ["def foo(*a, b):\n pass"]),
        ("foo(a=save_file) {}", ["def foo(a=pcsavefile):\n pass"]),
        ("foo(a=[1,2]) {}", ["def foo(a=[1, 2]):\n pass"]),
        ("foo(a=g()) {}", ["def foo(a=g()):\n pass"]),
        ("foo(a,) {}", ["def foo(a):\n pass"]),
        (
            "foo(a) { global g; g = a }",
            ["def foo(a):\n global g\n g = a"],
        ),
        ("foo() { nonlocal q }", ["def foo():\n nonlocal q"]),
        ("foo() {\n}\n", ["def foo():\n pass"]),
    ],
)
def test_function_definitions(code, expected):
    assert translate(code) == expected


@pytest.mark.parametrize(
    ("code", "message"),
    [
        ("foo(a, a) {}", "duplicate parameter 'a'"),
        ("foo(if) {}", "invalid parameter name 'if'"),
        (
            "foo(a=1, b) {}",
            "parameter without a default follows parameter with a default",
        ),
        ("foo(*a, *b) {}", "more than one * parameter"),
        ("foo(**k, a) {}", "parameter follows ** parameter"),
        ("foo(***a) {}", "invalid parameter '***a'"),
        ("foo(a b) {}", "invalid parameter 'a b'"),
        ("foo(a:int) {}", "invalid parameter 'a:int'"),
        ("foo(a, /) {}", "invalid parameter '/'"),
        ("foo(*) {}", "invalid parameter '*'"),
        ("foo(a=1 +) {}", "invalid syntax"),
        ("foo(a=) {}", "invalid syntax"),
        ("foo(a) {} x", "invalid syntax"),
        ("foo(a) {} {}", "invalid syntax"),
        ("foo(a) {}(b)", "invalid syntax"),
        ("if () {}", "invalid syntax"),
    ],
)
def test_invalid_function_definitions(code, message):
    assert message in error_message(code)


def test_a_function_definition_nested_in_an_argument_is_rejected():
    assert "function definition inside function argument" in error_message(
        "async f() { }"
    )


def test_a_function_can_call_itself():
    assert translate("f(a) { f(a) }") == ["def f(a):\n f(a)"]


def test_a_function_can_be_called_after_it_is_defined():
    assert translate("f(a) { return a }; f(1)") == [
        "def f(a):\n return a",
        "f(1)",
    ]


def test_a_nested_function_is_not_visible_outside():
    assert translate("f() { g() { return 1 }; return g() }; g()") == [
        "def f():\n def g():\n  return 1\n return g()",
        "g()",
    ]


def test_a_function_can_be_assigned_and_called_through_a_variable():
    assert translate("f() { }; x = f; x()") == [
        "def f():\n pass",
        "x = f",
        "x()",
    ]


# ---------------------------------------------------------------------------
# Commands, variables and shadowing
# ---------------------------------------------------------------------------


def test_a_command_used_without_calling_it_is_still_translated():
    assert translate("x = [save_file, open_file]") == ["x = [pcsavefile, pcopenfile]"]
    assert translate("x = {save_file: 1}") == ["x = {pcsavefile: 1}"]
    assert translate("x = save_file if y else open_file") == [
        "x = pcsavefile if y else pcopenfile"
    ]


def test_commands_inside_comprehensions_and_arguments():
    assert translate("x = [save_file() for i in y]") == [
        "x = [pcsavefile() for i in y]"
    ]
    assert translate('x = "{}".format(save_file)') == ["x = '{}'.format(pcsavefile)"]


def test_a_comprehension_variable_shadows_a_command():
    assert translate("x = [i for save_file in y]") == ["x = [i for save_file in y]"]


def test_a_lambda_parameter_shadows_a_command():
    assert translate("x = lambda save_file: save_file") == [
        "x = lambda save_file: save_file"
    ]


def test_a_variable_with_a_commands_name_shadows_it():
    assert translate("save_file = 1; save_file()") == ["save_file = 1", "save_file()"]


def test_a_function_with_a_commands_name_shadows_it():
    assert translate("save_file () { }; save_file()") == [
        "def save_file():\n pass",
        "save_file()",
    ]


def test_a_parameter_with_a_commands_name_shadows_it_only_inside():
    assert translate("f(save_file) { save_file() }; save_file()") == [
        "def f(save_file):\n save_file()",
        "pcsavefile()",
    ]


def test_a_local_variable_shadows_a_command_only_inside():
    assert translate("f() { save_file = 1; save_file() }; save_file()") == [
        "def f():\n save_file = 1\n save_file()",
        "pcsavefile()",
    ]


def test_deleting_a_name_makes_it_undefined_even_if_it_is_a_commands_name():
    assert translate("save_file = 1; del save_file; save_file()") == [
        "save_file = 1",
        "del save_file",
        "save_file()",
    ]


def test_deleting_a_function_removes_its_definition():
    assert translate("f() { }; del f; f()") == [
        "def f():\n pass",
        "del f",
        "f()",
    ]


def test_commands_translate_inside_blocks():
    assert translate('if (save_file()) { open_file("a") } else { new_file() }') == [
        "if pcsavefile():\n pcopenfile('a')\nelse:\n pcnewfile()"
    ]
    assert translate("while (True) { save_file() }") == ["while True:\n pcsavefile()"]
    assert translate("f(a) { return save_file() }") == [
        "def f(a):\n return pcsavefile()"
    ]


def test_commands_with_dotted_python_expressions():
    assert translate("sleep(1)") == ["time.sleep(1)"]
    assert translate('set_window_geometry("10x10")') == ["root.geometry('10x10')"]
    assert translate('prompt("x")') == ["utils.prompt('x')"]


def test_names_given_as_defined_variables_are_not_commands():
    assert translate("save_file()", {"save_file": "save_file"}) == ["save_file()"]


def test_pycode_functions_given_as_defined_are_called_by_their_python_name():
    defined = {"mine": PyCodeFunction("user_mine")}
    assert translate("mine(); x = mine", defined) == ["user_mine()", "x = user_mine"]


def test_the_given_definitions_are_not_changed_by_parsing():
    defined = {"keep": "keep"}

    translate("x = 1; f() { }", defined)

    assert defined == {"keep": "keep"}


# ---------------------------------------------------------------------------
# Control flow
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("code", "expected"),
    [
        ("if (a) { } else { } ", ["if a:\n pass\nelse:\n pass"]),
        (
            "if (a) { x = 1 } elif (b) { x = 2 }",
            ["if a:\n x = 1\nelif b:\n x = 2"],
        ),
        (
            "if (a) { x = 1 } elif (b) { x = 2 } elif (c) { x = 3 } else { x = 4 }",
            ["if a:\n x = 1\nelif b:\n x = 2\nelif c:\n x = 3\nelse:\n x = 4"],
        ),
        (
            "if (a) { if (b) { x = 1 } else { x = 2 } }",
            ["if a:\n if b:\n  x = 1\n else:\n  x = 2"],
        ),
        (
            "while (a) { while (b) { pass } }",
            ["while a:\n while b:\n  pass"],
        ),
        ("while (a) { break; continue }", ["while a:\n break\n continue"]),
        ("while (a) { }", ["while a:\n pass"]),
        ("if (a and\n b) { pass }", ["if a and b:\n pass"]),
        ("if ((a)) { pass }", ["if a:\n pass"]),
        ("if (x == 1) { y = 2 }", ["if x == 1:\n y = 2"]),
        (
            "if (a) { f() { return 1 } }",
            ["if a:\n def f():\n  return 1"],
        ),
    ],
)
def test_conditions_and_loops(code, expected):
    assert translate(code) == expected


@pytest.mark.parametrize(
    "code",
    [
        "if { }",
        "if () { }",
        "if (a) else { }",
        "if (a) { } elif { }",
        "else { }",
        "elif (a) { }",
        "while (a) { } else { }",
        "if (a) { } else { } else { }",
        "if (a) { x } y",
        "if a { }",
        "while a { }",
        "if (a) { } elif (b) { } else { } elif (c) { }",
    ],
)
def test_invalid_conditions_and_loops(code):
    assert "invalid syntax" in error_message(code)


def test_a_function_defined_in_a_branch_stays_inside_it():
    assert translate("if (a) { f() { } }; f()") == [
        "if a:\n def f():\n  pass",
        "f()",
    ]


# ---------------------------------------------------------------------------
# global, nonlocal, return, pass, break, continue, del
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("code", "expected"),
    [
        ("global a, b", ["global a, b"]),
        ("global a", ["global a"]),
        ("nonlocal x", ["nonlocal x"]),
        ("return", ["return"]),
        ("return;", ["return"]),
        ("return x, y", ["return (x, y)"]),
        ("return x + 1", ["return x + 1"]),
        ("pass", ["pass"]),
        ("break", ["break"]),
        ("continue", ["continue"]),
        ("del x", ["del x"]),
        ("del x, y", ["del x, y"]),
        ("del x.y", ["del x.y"]),
        ("del x[0]", ["del x[0]"]),
    ],
)
def test_keyword_statements(code, expected):
    assert translate(code) == expected


@pytest.mark.parametrize(
    ("code", "message"),
    [
        ("global", "invalid syntax"),
        ("global 1", "invalid syntax"),
        ("global if", "invalid syntax"),
        ("return x y", "invalid syntax"),
        ("pass x", "invalid syntax"),
        ("break 1", "invalid syntax"),
        ("del", "invalid syntax"),
        ("del 1", "invalid delete target"),
    ],
)
def test_invalid_keyword_statements(code, message):
    assert message in error_message(code)


def test_a_name_declared_global_is_a_variable_afterwards():
    assert translate("f() { global save_file; save_file() }") == [
        "def f():\n global save_file\n save_file()"
    ]


# ---------------------------------------------------------------------------
# Separators, comments and whitespace
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("code", "expected"),
    [
        ("x = 1;; y = 2", ["x = 1", "y = 2"]),
        ("; x = 1", ["x = 1"]),
        ("x = 1;", ["x = 1"]),
        (";", []),
        ("", []),
        ("   \n  ", []),
        ("x = 1 # c ; y = 2", ["x = 1"]),
        ("# a\nx = 1 # b\n# c", ["x = 1"]),
        ("x = (1\n+ 2)", ["x = 1 + 2"]),
        ("f(a,\n  b)", ["f(a, b)"]),
        ("x\t=\t1", ["x = 1"]),
        ("a;\n\nb", ["a", "b"]),
        ("(a)", ["a"]),
        ("1", ["1"]),
        ('"str"', ["'str'"]),
        ("{}", ["{}"]),
        ("[]", ["[]"]),
        ("()", ["()"]),
    ],
)
def test_separators_comments_and_whitespace(code, expected):
    assert translate(code) == expected


@pytest.mark.parametrize(
    "code",
    ["x = 1\ny = 2", "x y", "x = 1 y", "x = 1 2", "f(a) b", "a b", "f(a)\ng(b)"],
)
def test_statements_need_a_semicolon_between_them(code):
    assert "invalid syntax" in error_message(code)


@pytest.mark.parametrize(
    "code",
    ["for i in x: pass", "import os", "class A: pass", "@dec", "x = y if", "x = ("],
)
def test_python_statements_are_not_pycode(code):
    assert error_message(code)


# ---------------------------------------------------------------------------
# Error positions
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("code", "line", "column"),
    [
        ("a b", 1, 3),
        ("x = 1;\ny = ;", 2, 4),
        ("f(a, a) {}", 1, 6),
        ("x = (", 1, 5),
        ("x = )", 1, 5),
        ("\n\n  1 = x", 3, 3),
        ('x = "abc', 1, 5),
        ("x = 1;\n\nif (a) {\n  b c\n}", 4, 5),
    ],
)
def test_errors_point_at_the_offending_character(code, line, column):
    with pytest.raises(PyCodeError) as info:
        pycodeparse(code, {})
    assert str(info.value).startswith(f"line {line} of code, column {column},")


def test_the_description_of_the_code_is_in_the_error():
    with pytest.raises(PyCodeError) as info:
        pycodeparse("a b", {}, inwhat="of the startup file")

    assert str(info.value).startswith("line 1 of the startup file, column 3,")


# ---------------------------------------------------------------------------
# The commands table
# ---------------------------------------------------------------------------


def test_command_names_are_valid_python_names_and_not_keywords():
    import keyword

    for name in pycode.pycode_commands:
        assert name.isidentifier() and not keyword.iskeyword(name), name


def test_command_translations_are_valid_python_expressions():
    import ast

    for name, python in pycode.pycode_commands.items():
        ast.parse(python, mode="eval")


def test_each_command_translation_is_reachable_through_the_state_namespace(app):
    """PyCode runs its output with the names of the state module, so every
    command must resolve to something there."""
    missing = []
    for name, python in pycode.pycode_commands.items():
        root = python.split(".")[0]
        if root not in vars(state) and root not in vars(__builtins__):
            missing.append((name, python))
    assert missing == []
