"""The Alt-X command line's parsing and autocomplete, which are pure text
and registry logic and need no display."""

import pytest

import command
import editor
import state
from command import (
    cmdactivesegment,
    cmdautocompletefunc,
    cmdcheckbrackets,
    cmdfindgroupclose,
    cmdinputvariants,
    cmdparsegroup,
    cmdsplit,
    cmdstripgroup,
)


@pytest.fixture
def no_active_buffer(monkeypatch):
    """Autocomplete with no plugin or PyCode commands and no active buffer."""
    monkeypatch.setattr(state, "active", None, raising=False)
    monkeypatch.setattr(state, "plgncmds", {}, raising=False)
    monkeypatch.setattr(state, "pcwrittencommands", {}, raising=False)
    monkeypatch.setattr(state, "plgnhmodes", {}, raising=False)


# ---------------------------------------------------------------------------
# Groups
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("text", "open_index", "expected"),
    [
        ("(abc)", 0, 4),
        ("(a(b)c)", 0, 6),
        ("(a(b)c)", 2, 4),
        ("x(a)y", 1, 3),
        ("(a\\)b)", 0, 5),
        ("(abc", 0, None),
        ("((a)", 0, None),
        ("()", 0, 1),
    ],
)
def test_finding_the_closing_parenthesis(text, open_index, expected):
    assert cmdfindgroupclose(text, open_index) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("w:(abc)", True),
        ("w:(a(b)c)", True),
        ("w: (abc)", True),
        ("w:(abc", False),
        ("w:(a(b)", False),
        ("w:abc", True),
        ("w", True),
        ("w:\\(abc", True),
        ("re:(w:(a;b)*2)*3", True),
        ("re:(w:(a;b*2)*3", False),
        ("", True),
    ],
)
def test_checking_that_groups_are_closed(text, expected):
    assert cmdcheckbrackets(text) is expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("(abc)", "abc"),
        ("(a(b)c)", "a(b)c"),
        ("(a)(b)", "(a)(b)"),
        ("abc", "abc"),
        ("(abc", "(abc"),
        ("()", ""),
        ("", ""),
    ],
)
def test_stripping_a_group_that_wraps_the_whole_input(text, expected):
    assert cmdstripgroup(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("a;b;c", ["a", "b", "c"]),
        ("a", ["a"]),
        ("", [""]),
        ("a;", ["a", ""]),
        (";a", ["", "a"]),
        ("w:(a;b);c", ["w:(a;b)", "c"]),
        ("w:(a;b)*2;c", ["w:(a;b)*2", "c"]),
        (r"w:a\;b;c", [r"w:a\;b", "c"]),
        ("w: (a;b);c", ["w: (a;b)", "c"]),
        ("re:(w:(x;y)*2);z", ["re:(w:(x;y)*2)", "z"]),
        ("w:(a;b", ["w:(a;b"]),
        ("a\\", ["a\\"]),
    ],
)
def test_splitting_chained_commands(text, expected):
    assert cmdsplit(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("abc*3", ("abc", 3)),
        ("(abc)*3", ("abc", 3)),
        ("  abc*3  ", ("abc", 3)),
        ("(a*b)*2", ("a*b", 2)),
        ("a*b*2", ("a", None)),
        ("(a(b)c)*4", ("a(b)c", 4)),
        ("x*0", ("x", 0)),
    ],
)
def test_parsing_repeat_syntax(text, expected):
    if expected[1] is None:
        with pytest.raises(ValueError):
            cmdparsegroup(text)
    else:
        assert cmdparsegroup(text) == expected


@pytest.mark.parametrize(
    "text", ["abc", "abc*x", "(abc)", "(abc)3", "(abc", "(abc)x*3"]
)
def test_invalid_repeat_syntax(text):
    with pytest.raises(Exception):
        cmdparsegroup(text)


# ---------------------------------------------------------------------------
# Autocomplete
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("typed", "prefix", "segment"),
    [
        ("sav", "", "sav"),
        ("  sav", "  ", "sav"),
        ("a;sav", "a;", "sav"),
        ("a; b;sav", "a; b;", "sav"),
        ("a;  sav", "a;  ", "sav"),
        ("w:(a;b);sa", "w:(a;b);", "sa"),
        ("", "", ""),
        ("a;", "a;", ""),
    ],
)
def test_the_part_being_typed(typed, prefix, segment):
    assert cmdactivesegment(typed) == (prefix, segment)


@pytest.mark.parametrize(
    ("inputs", "expected"),
    [
        (None, (True, False)),
        ([None], (True, False)),
        ([None, "a"], (True, True)),
        (["a", "b"], (False, True)),
        ([], (False, True)),
        (lambda text: [], (False, True)),
    ],
)
def test_how_a_command_is_offered(inputs, expected):
    assert cmdinputvariants(inputs) == expected


def test_commands_without_input_are_offered_bare(no_active_buffer):
    assert "exit" in command.cmdbasecommandnames()
    assert "exit:" not in command.cmdbasecommandnames()


def test_commands_with_input_are_offered_with_a_colon(no_active_buffer):
    names = command.cmdbasecommandnames()

    assert "write:" in names and "write" not in names
    assert "help:" in names


def test_commands_with_optional_input_are_offered_both_ways(no_active_buffer):
    names = command.cmdbasecommandnames()

    assert "balance" in names and "balance:" in names


def test_commands_for_editors_need_an_editor_in_the_right_hmode(
    no_active_buffer, monkeypatch
):
    assert "run" not in command.cmdbasecommandnames()

    class FakeEditor(editor.Editor):
        def __init__(self, hmode):
            self.hmode = hmode

    for hmode, offered in (("python", True), ("normal", False)):
        monkeypatch.setattr(state, "active", FakeEditor(hmode))
        assert ("run" in command.cmdbasecommandnames()) is offered
    monkeypatch.setattr(state, "active", FakeEditor("python"))
    assert "pynavstart:" in command.cmdbasecommandnames()
    assert "lanavstart:" not in command.cmdbasecommandnames()


def test_plugin_and_pycode_commands_are_offered(no_active_buffer, monkeypatch):
    monkeypatch.setattr(state, "plgncmds", {"plug": ("dir", "code")})
    monkeypatch.setattr(state, "pcwrittencommands", {"mine": lambda: None})

    names = command.cmdbasecommandnames()

    assert "plug" in names and "mine" in names


def test_completing_a_command_name(no_active_buffer):
    assert cmdautocompletefunc("sav") == ["save", "saveas"]
    assert cmdautocompletefunc("exi") == ["exit"]
    assert cmdautocompletefunc("zzz") == []


def test_completing_keeps_the_text_typed_before(no_active_buffer):
    assert cmdautocompletefunc("sw; exi") == ["sw; exit"]
    assert cmdautocompletefunc("  exi") == ["  exit"]


def test_completing_a_commands_input(no_active_buffer):
    assert cmdautocompletefunc("balance:") == [
        "balance:h",
        "balance:horiz",
        "balance:horizontal",
        "balance:v",
        "balance:vert",
        "balance:vertical",
    ]
    assert cmdautocompletefunc("balance: ho") == [
        "balance: horiz",
        "balance: horizontal",
    ]
    assert cmdautocompletefunc("help:p") == [
        "help:pc",
        "help:pl",
        "help:plugins",
        "help:pycode",
    ]


def test_completing_after_a_chained_command(no_active_buffer):
    assert cmdautocompletefunc("sw;balance:v") == [
        "sw;balance:v",
        "sw;balance:vert",
        "sw;balance:vertical",
    ]


def test_a_command_with_free_input_has_nothing_to_complete(no_active_buffer):
    assert cmdautocompletefunc("write:a") == []
    assert cmdautocompletefunc("unknown:a") == []


def test_completing_pycode_commands_for_pccmd(no_active_buffer):
    candidates = cmdautocompletefunc("pccmd:save_f")

    assert candidates == ["pccmd:save_file", "pccmd:save_file_as"]


def test_completing_inside_a_repeat_group(no_active_buffer):
    assert cmdautocompletefunc("repeat:(exi") == ["repeat:(exit"]
    assert cmdautocompletefunc("repeat:(exit)*2") == []


def test_python_navigation_values_only_in_python_editors(no_active_buffer):
    assert command.cmdpynavvalues("") == []
    assert command.cmdpygodefvalues("") == []
    assert command.cmdlanavvalues("") == []
    assert command.cmdmdnavvalues("") == []


def test_hmode_names_include_plugin_hmodes(no_active_buffer, monkeypatch):
    monkeypatch.setattr(state, "plgnhmodes", {"Shouting": ("dir", "code")})

    assert command.cmdallhmodenames() == [
        "python",
        "latex",
        "normal",
        "html",
        "markdown",
        "Shouting",
    ]


# ---------------------------------------------------------------------------
# The registry matches the commands cmdrun() runs
# ---------------------------------------------------------------------------


def test_every_command_cmdrun_handles_is_registered_for_autocomplete():
    import ast
    import pathlib

    tree = ast.parse(pathlib.Path(command.__file__).read_text())
    run = next(
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "cmdrun"
    )
    handled = {
        comparator.value
        for node in ast.walk(run)
        if isinstance(node, ast.Compare)
        and isinstance(node.left, ast.Name)
        and node.left.id == "command"
        for comparator in node.comparators
        if isinstance(comparator, ast.Constant) and isinstance(comparator.value, str)
    }

    assert handled - {""} == set(command.cmdregistry)


def test_registry_entries_have_valid_restrictions():
    for name, entry in command.cmdregistry.items():
        assert set(entry) == {"hmodes", "inputs", "buffertypes"}, name
        assert entry["buffertypes"] is None or all(
            isinstance(kind, type) for kind in entry["buffertypes"]
        ), name
        assert (
            entry["inputs"] is None
            or callable(entry["inputs"])
            or isinstance(entry["inputs"], list)
        ), name


def test_unregistered_commands_are_unrestricted():
    assert command.cmdregistryentry("not-registered") == {
        "hmodes": None,
        "inputs": None,
        "buffertypes": None,
    }


def test_registering_aliases_shares_one_entry_shape():
    command.cmdregister(("zz-one", "zz-two"), inputs=["a"])
    try:
        assert command.cmdregistry["zz-one"] == command.cmdregistry["zz-two"]
        assert command.cmdregistry["zz-one"]["inputs"] == ["a"]
    finally:
        del command.cmdregistry["zz-one"], command.cmdregistry["zz-two"]
