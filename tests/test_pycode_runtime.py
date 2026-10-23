"""Running PyCode: parsing and running source, the commands, hooks, key
bindings and the chord state machine they compile to, window commands, and
the PyCode editor window."""

import re
from types import SimpleNamespace

import pytest

import canvastk as ctk
import pycode
import state
import utils
from test_editor import cursor_at, editor, put, text_of, wait_for, wait_for_message
from test_pycode_editing import not_an_editor

pytestmark = pytest.mark.display


# ---------------------------------------------------------------------------
# Running translated code
# ---------------------------------------------------------------------------


def test_run_executes_blocks_in_the_state_namespace(app):
    pycode.pcrun(["state.ran = 1", "state.ran += 1"])

    assert state.ran == 2


def test_run_reports_a_failing_block_and_goes_on(app):
    pycode.pcrun(["1 / 0", "state.after = True"])

    assert state.after is True
    (message,) = app.dialogs.messages("error")
    assert 'Error in running the translated PyCode block\n"1 / 0":' in message
    assert "division by zero" in message


def test_run_ignores_tcl_errors(app):
    import tkinter

    state.raise_tcl = lambda: (_ for _ in ()).throw(tkinter.TclError("gone"))

    pycode.pcrun(["raise_tcl()"])

    assert app.dialogs.of_kind("error") == []


def test_parse_returns_blocks(app):
    assert pycode.pcparse("x = 1; y = 2") == ["x = 1", "y = 2"]


def test_parse_reports_an_error_and_returns_none(app):
    assert pycode.pcparse("x = ") is None

    (message,) = app.dialogs.messages("error")
    assert "line 1 of code, column 4" in message


def test_evaluate_runs_the_expression(app, tk_root):
    pycode.pcevaluate("set_variable('evaluated', 5)")

    assert state.evaluated == 5
    wait_for_message(tk_root, "evaluated pycode expression")


def test_evaluate_an_invalid_expression(app, tk_root):
    pycode.pcevaluate("x = ")

    wait_for_message(tk_root, "invalid pycode expression")
    assert "PyCode expression" in app.dialogs.messages("error")[0]


def test_commands_translate_to_working_python(app):
    pycode.pcevaluate("set_variable('fromcommand', 7)")

    assert state.fromcommand == 7


def test_set_variable_sets_a_name_in_the_state(app):
    pycode.pcsetvar("variable_name", [1])

    assert state.variable_name == [1]


def test_a_pycode_program_runs_end_to_end(app):
    pycode.pcread("""
        add (a, b) { return a + b };
        total = 0;
        i = 0;
        while (i < 4) { total = add(total, i); i = i + 1 };
        set_variable('result', total)
        """.replace("\n", " "))

    assert state.result == 6


# ---------------------------------------------------------------------------
# Reading PyCode, commands and hooks
# ---------------------------------------------------------------------------


def test_reading_forgets_what_the_previous_source_registered(app):
    state.pcwrittencommands["old"] = lambda: None
    state.pcbeforehooks["save-file"] = [lambda: None]
    state.pcafterhooks["save-file"] = [lambda: None]
    state.pckeybindings.append(("<Control-j>", lambda: None, None))

    pycode.pcread("")

    assert state.pcwrittencommands == {}
    assert state.pcbeforehooks == {}
    assert state.pcafterhooks == {}
    assert state.pckeybindings == []


def test_reading_registers_commands(app):
    pycode.pcread("add_command('greet', lambda: set_variable('greeted', True))")

    assert list(state.pcwrittencommands) == ["greet"]
    state.pcwrittencommands["greet"]()
    assert state.greeted is True


def test_reading_registers_hooks(app):
    pycode.pcread("add_event_hook('before:save-file', lambda: None)")

    assert list(state.pcbeforehooks) == ["save-file"]


def test_reading_invalid_source_shows_the_error_and_still_binds_keys(app):
    pycode.pcread("x = ")

    assert "line 1" in app.dialogs.messages("error")[0]
    assert state.pcdeferkeybindings is False


def test_done_saves_the_source_and_runs_it(app):
    pycode.pcdone("set_variable('from_done', 1)")

    assert (app.home / ".pynotes").read_text() == "set_variable('from_done', 1)"
    assert state.from_done == 1


def test_add_command_needs_a_function(app):
    with pytest.raises(TypeError, match="needs a function"):
        pycode.pcaddcommand("name", "not callable")


@pytest.mark.parametrize(
    ("event", "message"),
    [
        ("during:save-file", "must start with before: or after:"),
        ("save-file", "must start with before: or after:"),
        ("before:no-such-event", "invalid event 'no-such-event'"),
    ],
)
def test_add_event_hook_checks_the_event(app, event, message):
    with pytest.raises(ValueError, match=message):
        pycode.pcaddeventhook(event, lambda: None)


def test_add_event_hook_needs_a_function(app):
    with pytest.raises(TypeError, match="needs a function"):
        pycode.pcaddeventhook("before:save-file", None)


def test_event_hooks_are_stored_by_time_and_event(app):
    first, second = (lambda: None), (lambda: None)

    pycode.pcaddeventhook("before:alt-x-command:save", first)
    pycode.pcaddeventhook("before:alt-x-command:save", second)
    pycode.pcaddeventhook("after:undo", first)

    assert state.pcbeforehooks == {"alt-x-command:save": [first, second]}
    assert state.pcafterhooks == {"undo": [first]}


def test_every_hook_event_is_one_the_application_runs(app):
    import pathlib

    sources = "".join(
        path.read_text()
        for path in pathlib.Path(pycode.__file__).parent.glob("*.py")
        if path.name != "help.py"
    )
    for event in pycode.pchookevents:
        assert f'"{event}"' in sources.replace("pchookevents", ""), event


def test_hooks_run_in_order_with_the_input(app):
    seen = []
    state.pcbeforehooks["save-file"] = [
        lambda value: seen.append(("one", value)),
        lambda value: seen.append(("two", value)),
    ]

    pycode.pcrunhook("before", "save-file", "input")

    assert seen == [("one", "input"), ("two", "input")]


def test_hooks_for_a_whole_kind_run_for_every_detail(app):
    seen = []
    state.pcafterhooks["alt-x-command"] = [lambda value: seen.append(("kind", value))]
    state.pcafterhooks["alt-x-command:save"] = [
        lambda value: seen.append(("detail", value))
    ]

    pycode.pcrunhook("after", "alt-x-command:save", "v")
    pycode.pcrunhook("after", "alt-x-command:other", "w")

    assert seen == [("detail", "v"), ("kind", "v"), ("kind", "w")]


def test_hooks_before_and_after_are_separate(app):
    seen = []
    state.pcbeforehooks["undo"] = [lambda: seen.append("before")]
    state.pcafterhooks["undo"] = [lambda: seen.append("after")]

    pycode.pcrunhook("before", "undo")
    pycode.pcrunhook("after", "undo")

    assert seen == ["before", "after"]


def test_a_failing_hook_is_reported_and_does_not_stop_the_others(app):
    seen = []
    state.pcbeforehooks["undo"] = [
        lambda: 1 / 0,
        lambda: seen.append("second"),
    ]

    pycode.pcrunhook("before", "undo")

    assert seen == ["second"]
    assert "error in running the 'before:undo' hook" in app.dialogs.messages("error")[0]


def test_a_function_gets_the_input_as_an_argument_or_as_a_variable(app):
    received = []

    pycode.pccallwithinput(lambda value: received.append(("argument", value)), "a")
    pycode.pccallwithinput(
        lambda: received.append(("variable", state.commandinput)), "b"
    )
    pycode.pccallwithinput(lambda *args: received.append(("args", args)), "c")

    assert received == [("argument", "a"), ("variable", "b"), ("args", ())]


# ---------------------------------------------------------------------------
# Commands that talk to the application
# ---------------------------------------------------------------------------


def test_say_shows_an_info_dialog(app):
    pycode.say("hello")

    assert app.dialogs.calls == [("info", "Print PyCode", "hello")]


def test_ask_returns_the_answer(app):
    app.dialogs.answer("askstring", "typed")

    assert pycode.pcask("question?") == "typed"
    assert app.dialogs.calls[-1] == ("askstring", "PyCode Input", "question?")


def test_copying_text_to_the_clipboard(app, tk_root):
    pycode.pccopytext("copied text")

    assert tk_root.clipboard_get() == "copied text"
    wait_for_message(tk_root, "copied 'copied text'")


def test_run_shell_shows_the_output(app, tk_root):
    pycode.pctermexec("echo from shell")

    wait_for_message(tk_root, "output: from shell\n".replace("\n", "\\n"))


def test_repeat_runs_an_altx_command_several_times(app, monkeypatch):
    import command

    seen = []
    monkeypatch.setattr(command, "cmdrun", lambda text: seen.append(text))

    pycode.pcrepeatx("sw", 3)

    assert seen == ["sw", "sw", "sw"]


@pytest.mark.parametrize(
    ("thing", "function", "message"),
    [
        ("commands", "hx", "open alt-x commands help"),
        ("email", "hemail", "open email help"),
        ("pycode", "helppycode", "open pycode help"),
        ("mathgod", "helpmathgod", "open mathgod help"),
        ("plugins", "ap", "open plugin help"),
    ],
)
def test_opening_help_topics(app, tk_root, monkeypatch, thing, function, message):
    opened = []
    monkeypatch.setattr(pycode.help, function, lambda: opened.append(function))

    pycode.pcopenhelp(thing)

    assert opened == [function]
    wait_for_message(tk_root, message)


def test_opening_an_unknown_help_topic_does_nothing(app, monkeypatch):
    monkeypatch.setattr(pycode.help, "hx", lambda: pytest.fail("opened"))

    pycode.pcopenhelp("nothing")


def test_opening_the_email_buffer(app, monkeypatch):
    opened = []
    monkeypatch.setattr(pycode.pynotesemail, "openemailbuf", lambda: opened.append(1))

    pycode.pcopenemailbuf()

    assert opened == [1]


def test_split_editor_opens_a_view_of_the_file(app, tk_root, tmp_path, monkeypatch):
    import window

    monkeypatch.chdir(tmp_path)
    window.neweditor()
    path = tmp_path / "split.txt"
    path.write_text("text")
    window.neweditor(str(path))

    pycode.pcsplitedit()

    views = state.all_buffers[-1]
    assert views.view_master is state.all_buffers[1]


def test_split_editor_without_a_file(app, tk_root, monkeypatch, tmp_path):
    import window

    monkeypatch.chdir(tmp_path)
    window.neweditor()

    pycode.pcsplitedit()

    wait_for_message(tk_root, "no file open to split editor")


def test_split_editor_of_another_buffer_says_so(app, tk_root):
    state.all_buffers.append(SimpleNamespace())
    state.buffindex = 0

    pycode.pcsplitedit()

    wait_for_message(tk_root, "not an editor")


# ---------------------------------------------------------------------------
# Window commands
# ---------------------------------------------------------------------------


@pytest.fixture
def window_calls(tk_root, monkeypatch):
    """The window commands, recorded instead of changing the real window."""
    calls = []
    monkeypatch.setattr(
        tk_root,
        "attributes",
        lambda *args: calls.append(("attributes", args)),
        raising=False,
    )
    monkeypatch.setattr(
        tk_root, "state", lambda *args: calls.append(("state", args)), raising=False
    )
    monkeypatch.setattr(
        tk_root, "iconify", lambda: calls.append(("iconify", ())), raising=False
    )
    return calls


def test_fullscreen_and_back(app, window_calls, tk_root):
    pycode.pcfullscreen()
    pycode.pcunfullscreen()

    assert window_calls == [
        ("attributes", ("-fullscreen", True)),
        ("attributes", ("-fullscreen", False)),
    ]


def test_maximize_and_back(app, window_calls):
    pycode.pcmax()
    pycode.pcunmax()

    assert window_calls == [
        ("attributes", ("-zoomed", True)),
        ("attributes", ("-zoomed", False)),
    ]


def test_minimize(app, window_calls):
    pycode.pcmin()

    assert window_calls == [("iconify", ())]


def test_window_commands_run_their_hooks(app, window_calls):
    seen = []
    for event in ("fullscreen", "un-fullscreen", "maximize-window", "minimize-window"):
        state.pcbeforehooks[event] = [lambda value, event=event: seen.append(event)]

    pycode.pcfullscreen()
    pycode.pcunfullscreen()
    pycode.pcmax()
    pycode.pcmin()

    assert seen == ["fullscreen", "un-fullscreen", "maximize-window", "minimize-window"]


def test_setting_the_window_title(app, tk_root):
    pycode.pcgosettitle("My Title")

    assert tk_root.title() == "My Title"
    assert state.pcsettitle is True


def test_unsetting_the_window_title_goes_back_to_the_buffer_title(
    app, tk_root, tmp_path, monkeypatch
):
    import window

    monkeypatch.chdir(tmp_path)
    window.neweditor()
    path = tmp_path / "named.txt"
    path.write_text("x")
    window.neweditor(str(path))
    pycode.pcgosettitle("My Title")

    pycode.pcgosettitle()

    assert state.pcsettitle is False
    assert tk_root.title() == "PyNotes - named.txt"


def test_unsetting_the_title_of_an_untitled_buffer(app, tk_root, monkeypatch, tmp_path):
    import window

    monkeypatch.chdir(tmp_path)
    window.neweditor()
    pycode.pcgosettitle("My Title")

    pycode.pcunsettitle()

    assert tk_root.title() == "PyNotes - Untitled"


def test_unsetting_the_title_shows_unsaved_changes(app, tk_root, tmp_path, monkeypatch):
    import window

    monkeypatch.chdir(tmp_path)
    path = tmp_path / "named.txt"
    path.write_text("x")
    window.neweditor()
    opened = window.neweditor(str(path))
    opened.unsaved = True

    pycode.pcunsettitle()

    assert tk_root.title() == "PyNotes - named.txt *"


def test_defining_a_color_makes_a_reusable_tag(app, tk_root, tmp_path, monkeypatch):
    import window

    monkeypatch.chdir(tmp_path)
    opened = window.neweditor()

    pycode.pccolor("shiny", foreground="red")

    assert opened.type_.tag_cget("shiny", "foreground") == "red"
    assert state.theme["pccolor:shiny"] == "foreground = 'red'"
    assert "shiny" in state._EDITOR_HL_SKIP_REMOVE_TAGS
    assert state.plugin_hl["pccolor:shiny"] == {"shiny": (None, "pccolor:shiny")}


def test_killing_pynotes_ends_the_process(app, monkeypatch):
    exits = []
    monkeypatch.setattr(pycode.os, "_exit", lambda code: exits.append(code))

    pycode.pckillexit()

    assert exits == [0]


# ---------------------------------------------------------------------------
# Key bindings
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("key", "message"),
    [
        ("Control-x", "invalid key"),
        ("<>", "invalid key"),
        (5, "invalid key"),
    ],
)
def test_key_bind_checks_the_key(app, key, message):
    with pytest.raises(ValueError, match=message):
        pycode.pckeybind(key, lambda: None)


def test_key_bind_checks_the_function_and_place(app):
    with pytest.raises(TypeError, match="needs a function"):
        pycode.pckeybind("<Control-j>", "no")
    with pytest.raises(ValueError, match="invalid binding place"):
        pycode.pckeybind("<Control-j>", lambda: None, "everywhere")


def test_key_bind_registers_and_applies_the_binding(app):
    function = lambda: None

    pycode.pckeybind("<Control-j>", function)

    assert state.pckeybindings == [("<Control-j>", function, None)]
    assert state.pckeyactions == [function]
    assert "<Control-j>" in state.wholenewwords


def test_key_binding_is_deferred_while_reading(app):
    state.pcdeferkeybindings = True
    pycode.pckeybind("<Control-j>", lambda: None)

    assert state.pckeyactions == []
    assert "<Control-j>" not in state.wholenewwords


def test_applying_key_bindings_removes_the_previous_ones(app):
    pycode.pckeybind("<Control-j>", lambda: None)
    assert "<Control-j>" in state.wholenewwords

    state.pckeybindings.clear()
    pycode.pcapplykeybindings()

    assert "<Control-j>" not in state.wholenewwords


def test_an_action_runs_the_function_of_its_binding(app):
    ran = []
    pycode.pckeybind("<Control-j>", lambda: ran.append(1))

    pycode.pcexecaction(0)

    assert ran == [1]


def test_an_action_that_fails_is_reported(app):
    pycode.pckeybind("<Control-j>", lambda: 1 / 0)

    pycode.pcexecaction(0)

    assert "Error in running the PyCode key binding" in app.dialogs.messages("error")[0]


class KeyRecorder:
    """Collects the handlers the key binding code installs, so a test can
    press keys by calling them with a made-up event."""

    def __init__(self, monkeypatch, tk_root):
        self.root = {}
        self.buffers = {}
        self.editors = {}
        monkeypatch.setattr(
            tk_root,
            "bind",
            lambda key, handler, *rest: self.root.__setitem__(key, handler),
            raising=False,
        )
        monkeypatch.setattr(tk_root, "unbind", lambda *args: None, raising=False)
        state.bindrecur = (
            lambda buffer, key, handler, *rest, **keywords: self.buffers.__setitem__(
                (key, id(buffer)), handler
            )
        )
        state.bindtype_ = (
            lambda buffer, key, handler, *rest, **keywords: self.editors.__setitem__(
                (key, id(buffer)), handler
            )
        )

    def press(self, key, keysym=None, modifiers=0):
        """Send the root a press of key ('<Control-x>' style). Tk runs only
        the most specific binding there is for a key."""
        event = SimpleNamespace(
            keysym=keysym or key.strip("<>").split("-")[-1], state=modifiers
        )
        handler = self.root.get(key) or self.root.get("<KeyPress>")
        return handler(event) if handler else None


@pytest.fixture
def keys(app, tk_root, monkeypatch):
    return KeyRecorder(monkeypatch, tk_root)


def test_a_simple_binding_runs_on_the_root(keys):
    ran = []
    pycode.pckeybind("<Control-j>", lambda: ran.append("j"))

    result = keys.press("<Control-j>")

    assert ran == ["j"]
    assert result == "break"


def test_a_two_key_chord_runs_after_both_keys(keys):
    ran = []
    pycode.pckeybind("<Control-x & Control-j>", lambda: ran.append("chord"))

    keys.press("<Control-x>")
    assert ran == []
    keys.press("<Control-j>")

    assert ran == ["chord"]


def test_a_chord_does_not_run_after_the_wrong_second_key(keys):
    ran = []
    pycode.pckeybind("<Control-x & Control-j>", lambda: ran.append("chord"))

    keys.press("<Control-x>")
    keys.press("<Control-k>")
    keys.press("<Control-j>")

    assert ran == []


def test_a_chord_can_be_repeated(keys):
    ran = []
    pycode.pckeybind("<Control-x & Control-j>", lambda: ran.append("chord"))

    for _ in range(2):
        keys.press("<Control-x>")
        keys.press("<Control-j>")

    assert ran == ["chord", "chord"]


def test_a_three_key_chord(keys):
    ran = []
    pycode.pckeybind("<Control-x & Control-c & Control-j>", lambda: ran.append("three"))

    keys.press("<Control-x>")
    keys.press("<Control-c>")
    assert ran == []
    keys.press("<Control-j>")

    assert ran == ["three"]


def test_a_plain_key_chord_is_handled_by_the_key_press(keys):
    ran = []
    pycode.pckeybind("<Control-x & a>", lambda: ran.append("a"))

    keys.press("<Control-x>")
    keys.press("<a>", keysym="a")

    assert ran == ["a"]


def test_a_chord_is_reset_by_any_other_key(keys):
    ran = []
    pycode.pckeybind("<Control-x & a>", lambda: ran.append("a"))

    keys.press("<Control-x>")
    keys.press("<b>", keysym="b")
    keys.press("<a>", keysym="a")

    assert ran == []


def test_a_chords_first_key_keeps_its_own_binding(keys):
    ran = []
    pycode.pckeybind("<Control-x>", lambda: ran.append("alone"))
    pycode.pckeybind("<Control-x & Control-j>", lambda: ran.append("chord"))

    keys.press("<Control-x>")
    keys.press("<Control-j>")

    assert ran == ["alone", "chord"]


def test_editor_bindings_are_bound_on_the_editors_not_the_root(keys):
    pycode.pckeybind("<Control-j>", lambda: None, "editor")

    assert "<Control-j>" not in keys.root


def test_bindings_for_the_editor_replace_nothing_for_other_buffers(keys):
    pycode.pckeybind("<Control-j>", lambda: None)

    assert "<Control-j>" in keys.root


def test_the_chord_state_is_cleared_when_bindings_are_applied(app):
    state._pychord_state = ["leftover"]

    pycode.pcapplykeybindings()

    assert state._pychord_state == [None]


# ---------------------------------------------------------------------------
# The PyCode editor window
# ---------------------------------------------------------------------------


def test_the_graphical_helpers_write_pycode():
    assert pycode.pcgraphicalstatements(["save_file", "new_file"]) == (
        "save_file();\nnew_file();\n"
    )
    assert pycode.pcgraphicalstatements(["undo"], "    ") == "    undo();\n"
    assert pycode.pcgraphicallambda([]) == "lambda: None"
    assert pycode.pcgraphicallambda(["save_file", "undo_editor"]) == (
        "lambda: [\n    save_file(),\n    undo_editor(),\n]"
    )


def test_the_graphical_helpers_write_valid_pycode(app):
    code = (
        "add_command('x', "
        + pycode.pcgraphicallambda(["save_file", "undo_editor"])
        + ");"
        + pycode.pcgraphicalstatements(["balance_buffers"])
    )

    assert pycode.pcparse(code) is not None


def test_the_editor_adds_the_closing_bracket_or_quote_after_the_cursor():
    class Box:
        def __init__(self):
            self.text, self.cursor = "", 0

        def insert(self, index, chars):
            self.text = self.text[: self.cursor] + chars + self.text[self.cursor :]
            self.cursor += len(chars)

        def mark_set(self, mark, index):
            self.cursor -= 1

    for opening, closing in (
        ("(", ")"),
        ("[", "]"),
        ("{", "}"),
        ('"', '"'),
        ("'", "'"),
    ):
        box = Box()
        assert pycode.edit(box, opening) is None
        assert (box.text, box.cursor) == (closing, 0)


def test_the_editor_starts_a_new_line_after_a_semicolon():
    class Box:
        text = ""

        def insert(self, index, chars):
            self.text += chars

    box = Box()

    assert pycode.edit(box, ";") == "break"
    assert box.text == ";\n"


@pytest.fixture
def pycode_window(app, tk_root, monkeypatch):
    windows = []
    original = type(tk_root).subwin

    def subwin(*arguments, **keywords):
        top = original(tk_root, *arguments, **keywords)
        top.withdraw()
        windows.append(top)
        return top

    monkeypatch.setattr(tk_root, "subwin", subwin, raising=False)
    yield windows
    for top in windows:
        if top.winfo_exists():
            top.destroy()


def descendants(widget):
    for child in widget.winfo_children():
        yield child
        yield from descendants(child)


def test_the_pycode_window_opens_with_the_saved_source_and_saves_on_done(
    app, tk_root, pycode_window
):
    pycode.pc()
    (window_,) = pycode_window
    buttons = {
        widget.cget("text"): widget
        for widget in descendants(window_)
        if isinstance(widget, ctk.Button)
    }
    box = next(w for w in descendants(window_) if isinstance(w, ctk.Textbox))
    box.insert("1.0", "set_variable('written_in_window', 3)")

    buttons["Done"].invoke()

    assert (app.home / ".pynotes").read_text() == "set_variable('written_in_window', 3)"
    assert state.written_in_window == 3
    assert not window_.winfo_exists()


def test_the_pycode_window_lists_every_command(app, pycode_window):
    pycode.pc()
    (window_,) = pycode_window

    labels = {
        widget.cget("text")
        for widget in descendants(window_)
        if isinstance(widget, ctk.Button)
    }

    assert set(pycode.pycode_commands) <= labels
