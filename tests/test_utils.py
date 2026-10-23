"""PyNotes' shared helpers: recursive key bindings, window size locking,
status messages and the Alt-X prompt, the user theme files, the error
window, and the helpers that open outside things."""

import copy
import json
import re
import threading
import time
from types import SimpleNamespace

import canvastk as ctk
import pytest

import dialogs
import editor as editor_module
import state
import themes
import utils
import window
from box_driver import drive
from test_editor import FakeObserver, editor, put, wait_for, wait_for_message


def run_binding(widget, sequence, **substitutions):
    """Run the Tcl script bound to sequence with event values made up: every
    % substitution is 0 unless given, e.g. K="Return" for the key name."""
    # The result is Tcl's code for the script: 3 when it said "break".
    script = widget.bind(sequence)
    script = re.sub(r"%(.)", lambda m: str(substitutions.get(m.group(1), 0)), script)
    return int(widget.tk.eval("catch {" + script + "} message"))


# ---------------------------------------------------------------------------
# Binding to a widget and everything in it
# ---------------------------------------------------------------------------


class FakeWidget:
    def __init__(self, *children):
        self.children = list(children)
        self.bound = []
        self.unbound = []

    def winfo_children(self):
        return self.children

    def bind(self, event, handler, *arguments, **keywords):
        self.bound.append((event, handler, arguments, keywords))

    def unbind(self, *arguments, **keywords):
        self.unbound.append((arguments, keywords))


def test_bindrecur_binds_the_widget_and_all_its_descendants():
    leaf = FakeWidget()
    middle = FakeWidget(leaf)
    top = FakeWidget(middle, FakeWidget())

    utils.bindrecur(top, "<Key>", lambda event: None)

    for widget in (top, middle, leaf, top.children[1]):
        assert [binding[0] for binding in widget.bound] == ["<Key>"]


def test_bound_handlers_stop_the_event_by_default():
    widget = FakeWidget()
    seen = []

    utils.bindrecur(widget, "<Key>", lambda event: seen.append(event))
    handler = widget.bound[0][1]

    assert handler("EVENT") == "break"
    assert seen == ["EVENT"]


def test_a_handler_may_choose_the_result():
    widget = FakeWidget()
    utils.bindrecur(widget, "<Key>", lambda event: "custom")

    assert widget.bound[0][1]("e") == "custom"


def test_without_break_the_handlers_result_is_kept():
    widget = FakeWidget()
    utils.bindrecur(widget, "<Key>", lambda event: None, False)

    assert widget.bound[0][1]("e") is None


def test_extra_bind_arguments_are_passed_on():
    widget = FakeWidget()

    utils.bindrecur(widget, "<Key>", lambda event: None, True, "+")

    assert widget.bound[0][2] == ("+",)


def test_unbindrecur_unbinds_everywhere():
    leaf = FakeWidget()
    top = FakeWidget(FakeWidget(leaf))

    utils.unbindrecur(top, "<Key>")

    assert top.unbound == [(("<Key>",), {})]
    assert leaf.unbound == [(("<Key>",), {})]


def test_bindtype_binds_only_the_text_of_an_editor(editor, monkeypatch):
    bound = []
    monkeypatch.setattr(
        editor._own_type, "bind", lambda *arguments, **keywords: bound.append(arguments)
    )

    utils.bindtype_(editor, "<F9>", lambda event: None)

    assert [arguments[0] for arguments in bound] == ["<F9>"]
    assert bound[0][1]("event") == "break"


def test_bindtype_does_nothing_for_other_buffers():
    other = SimpleNamespace(_own_type=FakeWidget())

    utils.bindtype_(other, "<F9>", lambda event: None)

    assert other._own_type.bound == []


# ---------------------------------------------------------------------------
# Window size
# ---------------------------------------------------------------------------


def test_locking_and_unlocking_the_window_size(app, tk_root):
    top = tk_root.subwin()
    top.withdraw()
    try:
        top.geometry("300x200")
        utils.lock_window_size(top)
        locked = (top.minsize(), top.maxsize())
        assert locked[0] == locked[1]
        utils.unlock_window_size(top)
        assert top.minsize() == (0, 0)
        assert top.maxsize() == (99999, 99999)
    finally:
        top.destroy()


def test_locking_a_destroyed_window_does_not_fail(app, tk_root):
    top = tk_root.subwin()
    top.destroy()

    utils.lock_window_size(top)
    utils.unlock_window_size(top)


# ---------------------------------------------------------------------------
# Status messages
# ---------------------------------------------------------------------------


@pytest.fixture
def console_messages(app):
    messages = []
    state.console = SimpleNamespace(show=lambda text: messages.append(text))
    return messages


def test_show_writes_the_message_in_the_command_box(app, console_messages):
    utils.show("hello")

    assert state.cmdentry.get("1.0", "end-1c") == "hello"
    assert str(state.cmdentry.cget("state")) == "disabled"
    wait_for(state.root, lambda: console_messages == ["hello"], "the console copy")


def test_show_replaces_the_previous_message(app, console_messages):
    utils.show("first")
    utils.show("second")

    assert state.cmdentry.get("1.0", "end-1c") == "second"


def test_show_escapes_newlines(app, console_messages):
    utils.show("a\nb")

    assert state.cmdentry.get("1.0", "end-1c") == "a\\nb"


def test_show_hides_the_autocomplete_list(app, console_messages):
    state.cmdautocomplete.pack(side="top")

    utils.show("x")

    assert state.cmdautocomplete.winfo_manager() == ""


# ---------------------------------------------------------------------------
# The Alt-X prompt
# ---------------------------------------------------------------------------


@pytest.fixture
def prompting(app, tk_root, editor, console_messages):
    """Run utils.prompt() with scripted actions at the box. Each action is a
    function of the box that runs while the prompt waits."""

    def run(*actions, **keywords):
        text = keywords.pop("text", "Prompt: ")
        delay = keywords.pop("delay", 20)
        return drive(
            tk_root,
            lambda: utils.prompt(text, **keywords),
            actions,
            delay=delay,
        )

    return run


def type_text(text):
    return lambda box: box.insert("end", text)


def press(sequence, **substitutions):
    return lambda box: run_binding(box.inner, sequence, **substitutions)


def test_prompt_returns_what_was_typed_after_the_prompt(prompting):
    assert prompting(type_text("hello"), press("<Return>")) == "hello"


def test_prompt_returns_nothing_when_escaped(prompting):
    assert prompting(type_text("hello"), press("<Escape>")) == ""


def test_prompt_shows_the_prompt_text_and_clears_the_box_after(prompting):
    seen = []

    def look(box):
        seen.append(box.get("1.0", "end-1c"))
        assert "prompt" in box.tag_names("1.0")

    prompting(look, press("<Return>"), text="Alt-X- ")

    assert seen == ["Alt-X- "]
    assert state.cmdentry.get("1.0", "end-1c") == ""
    assert str(state.cmdentry.cget("state")) == "disabled"


def test_prompt_starts_with_a_default_input(prompting):
    assert prompting(press("<Return>"), defaultinput="default") == "default"


def test_prompt_keeps_the_prompt_text_in_place(prompting):
    def damage(box):
        box.delete("1.0", "1.3")
        run_binding(box.inner, "<KeyPress>", K="x")

    assert prompting(damage, type_text("ok"), press("<Return>"), text="Go: ") == "ok"


def test_prompt_blocks_backspace_into_the_prompt_text(prompting):
    results = []

    def backspace(box):
        results.append(run_binding(box.inner, "<KeyPress>", K="BackSpace"))

    prompting(backspace, press("<Return>"), text="Go: ")

    assert results == [3]


def test_prompt_autocompletes_a_unique_match(prompting):
    result = prompting(
        type_text("sa"),
        press("<Tab>"),
        press("<Return>"),
        autocompletefunc=["save", "open"],
    )

    assert result == "save"


def test_prompt_autocompletes_the_common_prefix(prompting):
    result = prompting(
        type_text("s"),
        press("<Tab>"),
        press("<Return>"),
        autocompletefunc=["save", "saveas", "search"],
    )

    assert result == "s"


def test_prompt_autocompletes_the_common_prefix_of_several_matches(prompting):
    result = prompting(
        type_text("sa"),
        press("<Tab>"),
        press("<Return>"),
        autocompletefunc=["save", "saveas"],
    )

    assert result == "save"


def test_prompt_lists_the_matches_when_there_is_nothing_to_complete(prompting):
    shown = []

    def look(box):
        shown.append(state.cmdautocomplete.get("1.0", "end-1c"))

    prompting(
        type_text("s"),
        press("<Tab>"),
        look,
        press("<Return>"),
        autocompletefunc=["save", "search"],
    )

    assert shown == ["save    search"]


def test_prompt_says_when_nothing_matches(prompting):
    shown = []

    prompting(
        type_text("zzz"),
        press("<Tab>"),
        lambda box: shown.append(state.cmdautocomplete.get("1.0", "end-1c")),
        press("<Return>"),
        autocompletefunc=lambda typed: ["save"],
    )

    assert shown == ["[no match]"]


def test_prompt_autocompletion_may_use_a_function_of_the_typed_text(prompting):
    result = prompting(
        type_text("ab"),
        press("<Tab>"),
        press("<Return>"),
        autocompletefunc=lambda typed: [typed + "cdef", typed + "cdxx"],
    )

    assert result == "abcd"


def test_prompt_history_goes_back_and_forth(prompting):
    history = ["first", "second"]
    seen = []

    def current(box):
        seen.append(box.get("1.6", "1.end"))

    result = prompting(
        type_text("typed"),
        press("<Up>"),
        current,
        press("<Up>"),
        current,
        press("<Up>"),
        current,
        press("<Down>"),
        current,
        press("<Down>"),
        current,
        press("<Return>"),
        history=history,
        text="Alt-X-",
    )

    assert [value.strip() for value in seen] == [
        "second",
        "first",
        "first",
        "second",
        "typed",
    ]
    assert result.strip() == "typed"


def test_prompt_history_with_no_history_does_nothing(prompting):
    result = prompting(
        type_text("x"), press("<Up>"), press("<Down>"), press("<Return>"), history=[]
    )

    assert result == "x"


def test_prompt_waits_for_an_earlier_prompt_to_end(prompting, tk_root):
    state.prompting = True
    tk_root.after(60, lambda: setattr(state, "prompting", False))

    assert prompting(type_text("late"), press("<Return>"), delay=150) == "late"


# ---------------------------------------------------------------------------
# User themes
# ---------------------------------------------------------------------------


@pytest.fixture
def theme_files(app, monkeypatch):
    saved = copy.deepcopy(themes.THEMES)
    saved_original = copy.deepcopy(themes.ORIGINAL_THEMES)
    yield app.home / ".local" / "share" / "PyNotes" / "user_themes.json"
    themes.THEMES = saved
    themes.ORIGINAL_THEMES = saved_original


def test_saving_a_theme_writes_only_what_differs_from_the_built_in_themes(theme_files):
    utils.save_theme_and_reload(("Mine", False, {"surface": "#123456"}))

    light, dark = json.loads(theme_files.read_text())
    assert light == {"Mine": {"surface": "#123456"}}
    assert dark == {}


def test_saving_a_dark_theme(theme_files):
    utils.save_theme_and_reload(("Night", True, {"surface": "#000001"}))

    light, dark = json.loads(theme_files.read_text())
    assert light == {} and dark == {"Night": {"surface": "#000001"}}


def test_a_saved_theme_is_available_at_once(theme_files):
    utils.save_theme_and_reload(("Mine", False, {"surface": "#123456"}))

    assert themes.THEMES[0]["Mine"] == {"surface": "#123456"}
    assert "Mine" in state.root.themes()


def test_loading_without_a_theme_file_changes_nothing(theme_files):
    before = copy.deepcopy(themes.THEMES)

    utils.load_user_themes()

    assert themes.THEMES == before


def test_loading_a_theme_file_adds_its_themes(theme_files):
    theme_files.write_text(json.dumps([{"A": {"surface": "#111111"}}, {"B": {}}]))

    utils.load_user_themes()

    assert themes.THEMES[0]["A"] == {"surface": "#111111"}
    assert themes.THEMES[1]["B"] == {}


@pytest.mark.parametrize(
    "content",
    [
        "not json",
        json.dumps([{"A": {"no_such_key": "#111111"}}, {}]),
        json.dumps([{"A": "not a dict"}, {}]),
        json.dumps([[], {}]),
        json.dumps({"A": 1}),
    ],
)
def test_an_invalid_theme_file_is_reported_and_the_built_in_themes_kept(
    theme_files, app, content
):
    theme_files.write_text(content)
    original = copy.deepcopy(themes.ORIGINAL_THEMES)

    utils.load_user_themes()

    assert "Error while trying to load user themes" in app.dialogs.messages("error")[0]
    assert themes.THEMES == original


def test_saved_themes_survive_a_restart(theme_files):
    utils.save_theme_and_reload(("Mine", False, {"surface": "#123456"}))
    themes.THEMES = copy.deepcopy(themes.ORIGINAL_THEMES)
    assert "Mine" not in themes.THEMES[0]

    utils.load_user_themes()

    assert themes.THEMES[0]["Mine"] == {"surface": "#123456"}


# ---------------------------------------------------------------------------
# Text boxes that look enabled
# ---------------------------------------------------------------------------


def test_a_disabled_enabled_look_box_keeps_the_normal_colors(app, tk_root):
    box = utils.EnabledLookTextbox(tk_root, state="disabled")
    try:
        theme = ctk.get_theme()

        assert box.colors["surface_disabled"] == theme["surface"]
        assert box.colors["text_disabled"] == theme["text"]
    finally:
        box.destroy()


def test_refreshing_all_boxes_follows_a_theme_change(app, tk_root):
    box = utils.EnabledLookTextbox(tk_root, state="disabled")
    try:
        state.root.settheme("Dark")
        assert box.colors["surface_disabled"] == ctk.get_theme()["surface"]
        state.root.settheme("Light")
        assert box.colors["surface_disabled"] == ctk.get_theme()["surface"]
    finally:
        box.destroy()


def test_refreshing_skips_boxes_that_are_gone(app, tk_root):
    box = utils.EnabledLookTextbox(tk_root)
    box.destroy()

    utils.EnabledLookTextbox.refresh_all()


# ---------------------------------------------------------------------------
# The error window
# ---------------------------------------------------------------------------


@pytest.fixture
def errors(app, tk_root, monkeypatch):
    windows = []
    original = type(tk_root).subwin

    def subwin(*arguments, **keywords):
        top = original(tk_root, *arguments, **keywords)
        top.withdraw()
        windows.append(top)
        return top

    monkeypatch.setattr(tk_root, "subwin", subwin, raising=False)
    state.console = SimpleNamespace(dialog=lambda *arguments: None)
    handler = utils.ErrorHandler()
    yield handler, windows
    for top in windows:
        if top.winfo_exists():
            top.destroy()


def test_errors_open_a_window_with_the_text(errors, tk_root):
    handler, windows = errors

    handler.write("Traceback...\nValueError: bad")
    wait_for(tk_root, lambda: handler.win is not None, "the error window")

    assert handler.win.title() == "Error"
    assert handler.textbox.get("1.0", "end-1c") == "Traceback...\nValueError: bad"
    assert str(handler.textbox.cget("state")) == "disabled"


def test_more_errors_are_added_to_the_open_window(errors, tk_root):
    handler, windows = errors
    handler.write("first")
    wait_for(tk_root, lambda: handler.win is not None, "the window")

    handler.write("second")
    wait_for(
        tk_root, lambda: "second" in handler.textbox.get("1.0", "end"), "the second"
    )

    assert handler.textbox.get("1.0", "end-1c") == "first\nsecond"
    assert len(windows) == 1


def test_a_closed_error_window_is_opened_again(errors, tk_root):
    handler, windows = errors
    handler.write("first")
    wait_for(tk_root, lambda: handler.win is not None, "the window")
    handler.win.destroy()

    handler.write("second")
    wait_for(tk_root, lambda: len(windows) == 2, "a new window")

    assert handler.textbox.get("1.0", "end-1c") == "second"


def test_blank_errors_are_ignored(errors, tk_root):
    handler, windows = errors

    handler.write("   \n")
    tk_root.update()

    assert handler.win is None and windows == []


def test_errors_are_also_sent_to_the_console(errors, tk_root):
    handler, windows = errors
    seen = []
    state.console = SimpleNamespace(dialog=lambda *arguments: seen.append(arguments))

    handler.write("oops")
    wait_for(tk_root, lambda: seen, "the console copy")

    assert seen == [("Error", "oops", "41m")]


def test_the_error_window_closes_on_escape(errors, tk_root):
    handler, windows = errors
    handler.write("first")
    wait_for(tk_root, lambda: handler.win is not None, "the window")

    run_binding(handler.win, "<Escape>")

    assert not handler.win.winfo_exists()


def test_flush_does_nothing():
    assert utils.ErrorHandler().flush() is None


def test_tcl_errors_in_callbacks_are_ignored(app, monkeypatch):
    reported = []
    monkeypatch.setattr(
        utils.tk.Tk,
        "report_callback_exception",
        lambda root, *info: reported.append(info),
    )
    import tkinter

    utils._report_callback_exception(tkinter.TclError, tkinter.TclError("x"), None)
    utils._report_callback_exception(ValueError, ValueError("y"), None)

    assert [info[0] for info in reported] == [ValueError]


# ---------------------------------------------------------------------------
# Opening outside things
# ---------------------------------------------------------------------------


def test_download_plugins_opens_the_plugin_page(app, monkeypatch, console_messages):
    opened = []
    monkeypatch.setattr(utils.webbrowser, "open", opened.append)

    utils.dp()

    assert opened == ["https://github.com/rafugafu/PyNotes/tree/main/Plugins"]


def test_open_plugin_directory(app, monkeypatch, console_messages):
    runs = []
    monkeypatch.setattr(utils.subprocess, "run", lambda *a, **k: runs.append(a))

    utils.op()

    assert runs == [(["xdg-open", f"{app.home}/.local/share/PyNotes/add-ons"],)]


def test_open_mathgod_runs_it_as_a_separate_process(app, monkeypatch, console_messages):
    started = []
    monkeypatch.setattr(utils.subprocess, "Popen", lambda *a, **k: started.append(a))

    utils.mathgod()

    assert started == [([utils.sys.executable, f"{utils.rootdir}/MathGod.py"],)]


def test_show_source_opens_the_chosen_file_in_an_editor(
    app, editor, monkeypatch, tmp_path, console_messages
):
    path = tmp_path / "work" / "source.py"
    path.write_text("x = 1")
    monkeypatch.setattr(dialogs, "openfileget", lambda *a, **k: str(path))

    utils.ss()

    assert state.active.title == str(path)


def test_show_source_with_no_file_chosen(app, editor, monkeypatch, console_messages):
    monkeypatch.setattr(dialogs, "openfileget", lambda *a, **k: "")
    before = len(state.all_buffers)

    utils.ss()

    assert len(state.all_buffers) == before
