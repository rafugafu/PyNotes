"""Running Alt-X command lines with cmdrun()."""

import os
from types import SimpleNamespace

import pytest

import buffer as buffer_module
import command
import editor as editor_module
import state
import window
from test_editor import (
    FakeObserver,
    cursor_at,
    editor,
    put,
    select,
    selected,
    shown,
    text_of,
    wait_for,
    wait_for_message,
)
from test_pycode_editing import not_an_editor, python_editor

pytestmark = pytest.mark.display

# What opens windows or leaves the application, recorded instead of run.
OPENERS = {
    "help": ("hx", "hemail", "helppycode", "helpmathgod", "ap", "changes", "abt"),
    "utils": ("op", "dp", "mathgod", "ss"),
    "speech": ("st",),
    "preferences": ("prf",),
    "pycode": (
        "pc",
        "pcfullscreen",
        "pcunfullscreen",
        "pcmax",
        "pcunmax",
        "pcmin",
        "pcopenemailbuf",
    ),
    "pythonshell": ("openpythonshell",),
    "terminal": ("term",),
}


@pytest.fixture
def opened(monkeypatch):
    """The windows and actions a command opens, recorded."""
    calls = []
    for module_name, names in OPENERS.items():
        module = __import__(module_name)
        for name in names:
            monkeypatch.setattr(
                module,
                name,
                lambda *arguments, _id=f"{module_name}.{name}", **keywords: calls.append(
                    (_id, arguments, keywords)
                ),
            )
    monkeypatch.setattr(window, "ext", lambda: calls.append(("window.ext", (), {})))
    return calls


@pytest.fixture
def started(editor, opened, monkeypatch):
    """An editor as the active buffer, with file watching faked and the
    openers recorded."""
    monkeypatch.setattr(editor_module, "Observer", FakeObserver)
    return editor


def message_is(root, text):
    wait_for_message(root, text)


# ---------------------------------------------------------------------------
# Commands that take no input
# ---------------------------------------------------------------------------

COMMANDS_WITHOUT_INPUT = [
    "exit",
    "e",
    "sh",
    "splithoriz",
    "sv",
    "splitvert",
    "sw",
    "switch",
    "sol",
    "startofline",
    "eol",
    "endofline",
    "neh",
    "nev",
    "onh",
    "onv",
    "changes",
    "ch",
    "run",
    "ms",
    "mark",
    "unms",
    "unmark",
    "sendemail",
    "unma",
    "comment",
    "cr",
    "uncomment",
    "uncr",
    "fullup",
    "fulldown",
    "st",
    "opd",
    "dp",
    "indent-region",
    "ir",
    "unindent-region",
    "unir",
    "mathgod",
    "mg",
    "u",
    "undo",
    "r",
    "redo",
    "save",
    "s",
    "saveas",
    "sa",
    "show-source",
    "new",
    "n",
    "open",
    "o",
    "prf",
    "cancel",
    "z",
    "a",
    "selall",
    "copy",
    "c",
    "cut",
    "pf",
    "pb",
    "paste",
    "p",
    "sp",
    "full",
    "unfull",
    "max",
    "unmax",
    "min",
    "clear",
    "pycode",
    "pc",
    "about",
    "ab",
]


@pytest.mark.parametrize("name", COMMANDS_WITHOUT_INPUT)
def test_commands_that_take_no_input_refuse_it(started, opened, tk_root, name):
    command.cmdrun(f"{name}:junk")

    wait_for_message(tk_root, f"error: command '{name}' does not take input")
    assert opened == []
    assert text_of(started) == ""


def test_an_unknown_command_is_an_error(started, tk_root):
    command.cmdrun("nonsense")

    wait_for_message(tk_root, "error: invalid command 'nonsense'")


def test_an_empty_command_does_nothing(started, tk_root):
    command.cmdrun("")
    command.cmdrun("   ")
    command.cmdrun(":")

    assert shown() == ""


def test_the_cancel_command_does_nothing(started, opened):
    command.cmdrun("cancel")
    command.cmdrun("z")

    assert opened == []


def test_unmatched_brackets_are_refused(started, tk_root):
    command.cmdrun("write:(abc")

    wait_for_message(tk_root, "error: unmatched opening and closing brackets")
    assert text_of(started) == ""


def test_chained_commands_run_one_after_another(started, tk_root):
    command.cmdrun("write:a*2;write:b*3")

    assert text_of(started) == "aabbb"


def test_a_group_may_contain_semicolons(started):
    command.cmdrun("write:(a;b)*2;write:!*1")

    assert text_of(started) == "a;ba;b!"


def test_surrounding_spaces_are_ignored(started):
    command.cmdrun("   write :  x*2  ")

    assert text_of(started) == "xx"


# ---------------------------------------------------------------------------
# Commands with their own behavior
# ---------------------------------------------------------------------------


def test_exit_calls_the_exit_function(started, opened):
    command.cmdrun("exit")
    command.cmdrun("e")

    assert opened == [("window.ext", (), {})] * 2


def test_write_inserts_text_repeated(started, tk_root):
    command.cmdrun("write:ab*3")

    assert text_of(started) == "ababab"
    wait_for_message(tk_root, "wrote 'ab' 3 times")


def test_write_with_a_group_and_escapes(started):
    command.cmdrun("w:(a\\nb)*2")

    assert text_of(started) == "a\nba\nb"


@pytest.mark.parametrize(
    ("text", "reported"),
    [("abc", "abc"), ("abc*x", "abc*x"), ("(abc)", "abc"), ("abc*", "abc*")],
)
def test_write_with_invalid_input(started, tk_root, text, reported):
    command.cmdrun(f"write:{text}")

    wait_for_message(tk_root, f"error: invalid input '{reported}'")
    assert text_of(started) == ""


def test_write_needs_input_and_an_editor(started, tk_root, not_an_editor):
    command.cmdrun("write")
    wait_for_message(tk_root, "error: no input given to command 'write'")
    command.cmdrun("write:a*1")
    wait_for_message(tk_root, "not an editor")


def test_write_can_be_undone_in_one_step(started):
    started.type_.edit_reset()

    command.cmdrun("write:abc*2")
    started.undo()

    assert text_of(started) == ""


def test_repeat_runs_a_command_several_times(started):
    command.cmdrun("repeat:(write:ab*1)*3")
    command.cmdrun("re:(write:x*1)*4")

    assert text_of(started) == "abababxxxx"


def test_repeat_of_a_group(started):
    command.cmdrun("repeat:(write:x*1)*4")

    assert text_of(started) == "xxxx"


def test_repeat_with_invalid_input(started, tk_root):
    command.cmdrun("repeat:abc")

    wait_for_message(tk_root, "error: invalid input 'abc'")


def test_repeat_without_input(started, tk_root):
    command.cmdrun("repeat")

    wait_for_message(tk_root, "error: invalid input 'None'")


def test_goto_line(started):
    put(started, "one\ntwo\nthree")

    command.cmdrun("gl:2")

    assert selected(started) == "two"


def test_goto_line_with_the_other_names(started):
    put(started, "one\ntwo")

    command.cmdrun("l:1")
    assert selected(started) == "one"
    started.type_.tag_remove("sel", "1.0", "end")
    command.cmdrun("gotoline:2")
    assert selected(started) == "two"


def test_goto_line_in_another_buffer(not_an_editor, tk_root, opened):
    command.cmdrun("gl:2")

    wait_for_message(tk_root, "not an editor")


def test_start_and_end_of_line(started, tk_root):
    put(started, "  one two\nsecond")
    cursor_at(started, "1.5")

    command.cmdrun("sol")
    assert started.type_.index("insert") == "1.0"
    wait_for_message(tk_root, "moved to start of line 1")
    command.cmdrun("eol")
    assert started.type_.index("insert") == started.type_.index("1.end")
    wait_for_message(tk_root, "moved to end of line 1")


@pytest.mark.parametrize("name", ["sol", "eol", "fullup", "fulldown", "ms", "unms"])
def test_editor_only_commands_in_another_buffer(not_an_editor, tk_root, name):
    command.cmdrun(name)

    wait_for_message(tk_root, "not an editor")


def test_full_up_and_down(started):
    put(started, "one\ntwo\nthree")
    cursor_at(started, "2.1")

    command.cmdrun("fulldown")
    assert started.type_.index("insert") == started.type_.index("end-1c")
    command.cmdrun("fullup")
    assert started.type_.index("insert") == "1.0"


def test_selection_point_commands(started):
    put(started, "abc")
    cursor_at(started, "1.1")

    command.cmdrun("setsel")
    assert started.selectionpoint == "1.1"
    command.cmdrun("unsetsel")
    assert started.selectionpoint is None


def test_selection_point_commands_in_another_buffer(not_an_editor, tk_root):
    command.cmdrun("setsel")
    wait_for_message(tk_root, "not an editor")
    command.cmdrun("unsetsel")
    wait_for_message(tk_root, "not an editor")


def test_mark_and_unmark_the_selection(started, tk_root):
    put(started, "hello world")
    select(started, "1.0", "1.5")

    command.cmdrun("mark")
    assert [str(i) for i in started.type_.tag_ranges("marked")] == ["1.0", "1.5"]
    command.cmdrun("unmark")
    assert not started.type_.tag_ranges("marked")


def test_mark_without_a_selection(started, tk_root):
    command.cmdrun("ms")

    wait_for_message(tk_root, "nothing is selected")
    command.cmdrun("unms")
    wait_for_message(tk_root, "nothing is selected")


def test_unmark_all(started):
    put(started, "hello")
    started.type_.tag_add("marked", "1.0", "1.5")

    command.cmdrun("unmarkall")

    assert not started.type_.tag_ranges("marked")


def test_comment_and_uncomment(started):
    python_editor(started, "a = 1\nb = 2")
    select(started, "1.0", "2.5")

    command.cmdrun("comment")
    assert text_of(started) == "# a = 1\n# b = 2"
    select(started, "1.0", "2.7")
    command.cmdrun("uncomment")
    assert text_of(started) == "a = 1\nb = 2"


def test_comment_outside_the_supported_hmodes(started, tk_root):
    command.cmdrun("comment")

    wait_for_message(tk_root, "hmode is not python / latex / html / markdown")
    command.cmdrun("uncomment")
    wait_for_message(tk_root, "hmode is not python / latex / html / markdown")


def test_indent_and_unindent_the_selection(started, monkeypatch):
    monkeypatch.setattr(state, "taborspace", False)
    put(started, "a\nb")
    select(started, "1.0", "2.1")

    command.cmdrun("indent-region")
    assert text_of(started) == "\ta\n\tb"
    select(started, "1.0", "2.2")
    command.cmdrun("unindent-region")
    assert text_of(started) == "a\nb"


def test_hmode_switches_the_hmode(started, tk_root):
    command.cmdrun("hmode:python")
    assert started.hmode == "python"
    command.cmdrun("hmode:la")
    assert started.hmode == "latex"
    command.cmdrun("hmode:norm")
    assert started.hmode == "normal"


def test_hmode_with_a_plugin_hmode(started):
    state.plgnhmodes["Shouting"] = ("/plugins/Loud", "state.shouted = True")

    command.cmdrun("hmode:Shouting")

    assert started.hmode == "Shouting"


def test_hmode_errors(started, tk_root):
    command.cmdrun("hmode")
    wait_for_message(tk_root, "error: no input given to command 'hmode'")
    command.cmdrun("hmode:cobol")
    wait_for_message(tk_root, "hmode 'cobol' does not exist")


def test_hmode_in_another_buffer(not_an_editor, tk_root):
    command.cmdrun("hmode:python")

    wait_for_message(tk_root, "not an editor")


def test_undo_and_redo(started):
    started.type_.edit_reset()
    started.type_.edit_separator()
    put(started, "typed")
    started.type_.edit_separator()

    command.cmdrun("undo")
    assert text_of(started) == ""
    command.cmdrun("redo")
    assert text_of(started) == "typed"


def test_copy_cut_paste_and_select_all(started, tk_root):
    put(started, "hello")

    command.cmdrun("selall")
    assert selected(started) == "hello\n"
    select(started, "1.0", "1.5")
    command.cmdrun("copy")
    assert tk_root.clipboard_get() == "hello"
    command.cmdrun("cut")
    assert text_of(started) == ""
    command.cmdrun("paste")
    assert text_of(started) == "hello"


def test_buffers_without_an_action_say_so(not_an_editor, tk_root):
    for name, message in (
        ("save", "cannot save file in current buffer"),
        ("saveas", "cannot save file in current buffer"),
        ("new", "cannot open new file in current buffer"),
        ("open", "cannot open file in current buffer"),
        ("selall", "cannot select all in current buffer"),
        ("copy", "cannot copy in current buffer"),
        ("paste", "cannot paste in current buffer"),
    ):
        command.cmdrun(name)
        wait_for_message(tk_root, message)


def test_save_writes_the_file(started, tmp_path):
    path = tmp_path / "work" / "saved.txt"
    path.write_text("")
    started.ld(str(path))
    put(started, "saved text")

    command.cmdrun("save")

    assert path.read_text() == "saved text"


def test_new_blanks_the_editor(started, tmp_path):
    path = tmp_path / "work" / "a.txt"
    path.write_text("content")
    started.ld(str(path))

    command.cmdrun("new")

    assert text_of(started) == ""
    assert started.title == ""


def test_find_opens_the_find_panel(started, monkeypatch):
    opened_panels = []
    monkeypatch.setattr(
        started, "f", lambda *direction: opened_panels.append(("f", direction))
    )
    monkeypatch.setattr(
        started, "fr", lambda *direction: opened_panels.append(("fr", direction))
    )

    command.cmdrun("search")
    command.cmdrun("f:b")
    command.cmdrun("find-replace")
    command.cmdrun("fr:back")

    assert opened_panels == [
        ("f", ()),
        ("f", ("backward",)),
        ("fr", ()),
        ("fr", ("backward",)),
    ]


@pytest.mark.parametrize("name", ["search", "find-replace"])
def test_find_with_invalid_input(started, tk_root, name):
    command.cmdrun(f"{name}:sideways")

    wait_for_message(
        tk_root,
        f"error: invalid input 'sideways' for "
        + ("find command" if name == "search" else "find & replace command"),
    )


def test_run_runs_the_code(started, monkeypatch):
    calls = []
    monkeypatch.setattr(started, "f5", lambda: calls.append(True))

    command.cmdrun("run")

    assert calls == [True]


# ---------------------------------------------------------------------------
# Buffers and windows
# ---------------------------------------------------------------------------


def test_new_editors(started):
    command.cmdrun("neh")
    command.cmdrun("nev")

    assert len(state.all_buffers) == 3


def test_split_the_editor_of_a_file(started, tmp_path, tk_root):
    path = tmp_path / "work" / "split.txt"
    path.write_text("text")
    started.ld(str(path))

    command.cmdrun("sh")
    assert state.all_buffers[-1].view_master is started
    command.cmdrun("splitvert")
    assert len(state.all_buffers) == 3


def test_split_without_a_file(started, tk_root):
    command.cmdrun("sh")
    wait_for_message(tk_root, "no file open to split editor")
    command.cmdrun("sv")
    wait_for_message(tk_root, "no file open to split editor")


def test_split_in_another_buffer(not_an_editor, tk_root):
    command.cmdrun("sh")
    wait_for_message(tk_root, "not an editor")
    command.cmdrun("sv")
    wait_for_message(tk_root, "not an editor")


def test_switch_buffers(started):
    window.neweditor()
    assert state.buffindex == 1

    command.cmdrun("switch")

    assert state.buffindex == 0


def test_close_buffers(started):
    window.neweditor()
    window.neweditor()

    command.cmdrun("close:0")
    assert len(state.all_buffers) == 2
    command.cmdrun("cb")
    assert len(state.all_buffers) == 1


def test_close_with_invalid_input(started, tk_root):
    window.neweditor()

    command.cmdrun("close:abc")
    wait_for_message(tk_root, "error: invalid input 'abc' to close editor command")
    command.cmdrun("close:9")
    wait_for_message(tk_root, "error: editor 9 does not exist")
    command.cmdrun("close:-1")
    wait_for_message(tk_root, "error: editor -1 does not exist")
    assert len(state.all_buffers) == 2


@pytest.mark.parametrize(
    ("text", "message"),
    [
        ("", "balanced buffers"),
        ("h", "balanced horizontal buffers"),
        ("horiz", "balanced horizontal buffers"),
        ("v", "balanced vertical buffers"),
        ("vertical", "balanced vertical buffers"),
    ],
)
def test_balance(started, tk_root, text, message):
    command.cmdrun(f"balance:{text}" if text else "balance")

    wait_for_message(tk_root, message)


def test_balance_with_invalid_input(started, tk_root):
    command.cmdrun("bb:diagonal")

    wait_for_message(tk_root, "error: invalid direction 'diagonal' for balance command")


def test_open_new_editors_ask_for_a_file(started, monkeypatch, tmp_path):
    path = tmp_path / "work" / "picked.txt"
    path.write_text("picked")
    monkeypatch.setattr(window.dialogs, "openfileget", lambda *a, **k: str(path))

    command.cmdrun("onh")
    command.cmdrun("onv")

    assert len(state.all_buffers) == 3


# ---------------------------------------------------------------------------
# Opening other windows
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("line", "expected"),
    [
        ("changes", "help.changes"),
        ("pycode", "pycode.pc"),
        ("pc", "pycode.pc"),
        ("prf", "preferences.prf"),
        ("preferences", "preferences.prf"),
        ("about", "help.abt"),
        ("pynotes", "help.abt"),
        ("st", "speech.st"),
        ("opd", "utils.op"),
        ("dp", "utils.dp"),
        ("mathgod", "utils.mathgod"),
        ("show-source", "utils.ss"),
        ("sendemail", "pycode.pcopenemailbuf"),
        ("full", "pycode.pcfullscreen"),
        ("unfull", "pycode.pcunfullscreen"),
        ("max", "pycode.pcmax"),
        ("unmax", "pycode.pcunmax"),
        ("min", "pycode.pcmin"),
    ],
)
def test_commands_that_open_windows(started, opened, line, expected):
    command.cmdrun(line)

    assert [call[0] for call in opened] == [expected]


@pytest.mark.parametrize(
    ("topic", "expected"),
    [
        ("x", "help.hx"),
        ("commands", "help.hx"),
        ("em", "help.hemail"),
        ("email", "help.hemail"),
        ("pc", "help.helppycode"),
        ("pycode", "help.helppycode"),
        ("mg", "help.helpmathgod"),
        ("mathgod", "help.helpmathgod"),
        ("pl", "help.ap"),
        ("plugins", "help.ap"),
    ],
)
def test_help_topics(started, opened, topic, expected):
    command.cmdrun(f"help:{topic}")

    assert [call[0] for call in opened] == [expected]


def test_help_errors(started, tk_root):
    command.cmdrun("help")
    wait_for_message(tk_root, "error: no input given to command 'help'")
    command.cmdrun("h:cookery")
    wait_for_message(tk_root, "error: invalid input 'cookery'")


def test_python_shell_command(started, opened, tk_root):
    command.cmdrun("pyshell")
    command.cmdrun("ps:h")

    assert [(call[0], call[1]) for call in opened] == [
        ("pythonshell.openpythonshell", ()),
        ("pythonshell.openpythonshell", ("horizontal",)),
    ]
    command.cmdrun("ps:diagonal")
    wait_for_message(tk_root, "error: invalid input 'diagonal' to python shell command")


def test_terminal_command_with_and_without_a_program(started, opened, tk_root):
    command.cmdrun("terminal")
    command.cmdrun("t:ls -l")

    assert opened[0][:2] == ("terminal.term", ())
    assert opened[1][0] == "terminal.term"
    assert opened[1][2] == {
        "command": ["ls", "-l"],
        "endmessage": "--- Command finished, press any key to continue ---",
    }


def test_terminal_command_with_a_missing_program(started, opened, tk_root):
    command.cmdrun("term:definitely_not_a_program_xyz")

    wait_for_message(
        tk_root, "error: 'definitely_not_a_program_xyz' not found or not executable"
    )
    assert opened == []


def test_termexec_shows_the_output(started, tk_root):
    command.cmdrun("termexec:echo hello")

    wait_for_message(tk_root, "output: hello\\n")


def test_termexec_without_input(started, tk_root):
    command.cmdrun("te")

    wait_for_message(tk_root, "error: no input given to command 'te'")


# ---------------------------------------------------------------------------
# PyCode and plugin commands
# ---------------------------------------------------------------------------


def test_pccmd_runs_pycode(started):
    command.cmdrun("pccmd:set_variable('from_pccmd', 3)")

    assert state.from_pccmd == 3


def test_pccmd_without_input(started, tk_root):
    command.cmdrun("pycodecommand")

    wait_for_message(tk_root, "error: no input given")


def test_commands_written_in_pycode_are_run(started):
    state.pcwrittencommands["greet"] = lambda value: setattr(state, "greeted", value)

    command.cmdrun("greet:world")

    assert state.greeted == "world"


def test_a_pycode_command_that_fails_is_reported(started, app):
    state.pcwrittencommands["broken"] = lambda: 1 / 0

    command.cmdrun("broken")

    assert "error in running the command 'broken' defined in PyCode" in (
        app.dialogs.messages("error")[0]
    )


def test_plugin_commands_run_their_code(started):
    state.plgncmds["plug"] = ("/plugins/Demo", "state.plugged = commandinput")

    command.cmdrun("plug:arg")

    assert state.plugged == "arg"


def test_a_plugin_command_sees_its_own_file(started):
    state.plgncmds["plug"] = ("/plugins/Demo", "state.where = __file__")

    command.cmdrun("plug")

    assert state.where == os.path.join("/plugins/Demo", "commands")


def test_a_plugin_command_that_fails_is_reported(started, app):
    state.plgncmds["plug"] = ("/plugins/Demo", "1 / 0")

    command.cmdrun("plug")

    message = app.dialogs.messages("error")[0]
    assert "running the command 'plug' from the plugin \"Demo\"" in message


def test_plugin_commands_win_over_pycode_commands(started):
    state.plgncmds["both"] = ("/p", "state.who = 'plugin'")
    state.pcwrittencommands["both"] = lambda: setattr(state, "who", "pycode")

    command.cmdrun("both")

    assert state.who == "plugin"


def test_hooks_run_around_commands(started):
    seen = []
    state.pcbeforehooks["alt-x-command:cancel"] = [
        lambda value: seen.append(("before", value))
    ]
    state.pcafterhooks["alt-x-command"] = [lambda value: seen.append(("after", value))]

    command.cmdrun("cancel")

    assert seen == [("before", None), ("after", None)]


def test_hooks_get_the_commands_input(started):
    seen = []
    state.pcbeforehooks["alt-x-command"] = [lambda value: seen.append(value)]

    command.cmdrun("write:(a b)*1")

    assert seen == ["(a b)*1"]


def test_the_after_hook_is_skipped_when_a_command_stops_early(started):
    seen = []
    state.pcafterhooks["alt-x-command"] = [lambda value: seen.append(value)]

    command.cmdrun("exit:junk")

    assert seen == []


def test_a_pycode_command_runs_its_own_hooks(started):
    seen = []
    state.pcwrittencommands["mine"] = lambda: None
    state.pcbeforehooks["pycode-command:mine"] = [lambda value: seen.append("before")]
    state.pcafterhooks["pycode-command:mine"] = [lambda value: seen.append("after")]

    command.cmdrun("mine")

    assert seen == ["before", "after"]


# ---------------------------------------------------------------------------
# Python, LaTeX and Markdown navigation commands
# ---------------------------------------------------------------------------


def test_python_navigation_commands(started):
    python_editor(started, "def alpha():\n    pass\n\nclass K:\n    x = 1\n")

    command.cmdrun("pynavstart:alpha")
    assert started.type_.index("insert") == started.type_.index("1.end")
    command.cmdrun("pyjumpend:K")
    assert started.type_.index("insert") == started.type_.index("5.end")
    command.cmdrun("python-jump-startof:K")
    assert started.type_.index("insert") == started.type_.index("4.end")
    command.cmdrun("pygodef:K.x")
    assert started.type_.index("insert") == started.type_.index("5.end")


def test_latex_and_markdown_navigation_commands(started):
    started.pchmode("latex")
    put(started, "\\section{One}\ntext\n\\section{Two}\nmore\n")

    command.cmdrun("lanavstart:Two")
    assert started.type_.index("insert") == started.type_.index("3.end")
    command.cmdrun("latex-jump-endof:One")
    assert started.type_.index("insert") == started.type_.index("2.end")

    started.pchmode("markdown")
    started.type_.delete("1.0", "end")
    put(started, "# One\ntext\n# Two\nmore\n")
    command.cmdrun("mdnavstart:Two")
    assert started.type_.index("insert") == started.type_.index("3.end")
    command.cmdrun("markdown-jump-endof:One")
    assert started.type_.index("insert") == started.type_.index("2.end")


@pytest.mark.parametrize(
    "name",
    [
        "pynavstart",
        "pynavend",
        "pygodef",
        "lanavstart",
        "lanavend",
        "mdnavstart",
        "mdnavend",
    ],
)
def test_navigation_commands_need_input(started, tk_root, name):
    command.cmdrun(name)

    wait_for_message(tk_root, f"error: no input given to command '{name}'")


# ---------------------------------------------------------------------------
# Running the prompt
# ---------------------------------------------------------------------------


def test_the_prompt_runs_what_is_typed_and_remembers_it(started, monkeypatch):
    prompts = []

    def prompt(text, completer, history=None):
        prompts.append((text, completer, history))
        return "write:z*2"

    monkeypatch.setattr(command.utils, "prompt", prompt)
    state.cmdhistory = []

    command.cmd()

    assert text_of(started) == "zz"
    assert state.cmdhistory == ["write:z*2"]
    assert prompts[0][0] == "Alt-X- "
    assert prompts[0][1] is command.cmdautocompletefunc


# ---------------------------------------------------------------------------
# Commands in a buffer that is not an editor (a terminal, the Python shell)
# ---------------------------------------------------------------------------
