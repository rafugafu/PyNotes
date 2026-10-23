"""The Preferences window and the saving of the preferences file."""

import copy

import canvastk as ctk
import pytest

import dialogs
import init
import preferences
import state
import themes
import utils
from test_editor import editor, put, wait_for_message
from test_utils import console_messages  # noqa: F401  (a fixture)

pytestmark = pytest.mark.display


def descendants(widget):
    for child in widget.winfo_children():
        yield child
        yield from descendants(child)


class Window:
    def __init__(self, top):
        self.top = top
        self.widgets = list(descendants(top))

    def button(self, text):
        return next(
            w
            for w in self.widgets
            if isinstance(w, ctk.Button) and w.cget("text") == text
        )

    def check(self, text):
        return next(
            w
            for w in self.widgets
            if isinstance(w, ctk.Checkbutton) and w.cget("text").startswith(text)
        )

    def label(self, text):
        return next(
            w
            for w in self.widgets
            if isinstance(w, ctk.Label) and w.cget("text").startswith(text)
        )

    def options(self):
        return [w for w in self.widgets if isinstance(w, ctk.OptionMenu)]

    @property
    def colours(self):
        return preferences.colours


@pytest.fixture
def prefs(app, tk_root, editor, monkeypatch, console_messages):
    """The Preferences window, opened but hidden."""
    saved_themes = copy.deepcopy(themes.THEMES)
    windows = []
    original = type(tk_root).subwin

    def subwin(*arguments, **keywords):
        top = original(tk_root, *arguments, **keywords)
        top.withdraw()
        windows.append(top)
        return top

    monkeypatch.setattr(tk_root, "subwin", subwin, raising=False)
    preferences.prf()
    yield Window(windows[0])
    for top in windows:
        if top.winfo_exists():
            top.destroy()
    themes.THEMES = saved_themes


def saved_lines(app):
    return (app.home / ".local/share/PyNotes/defs").read_text().split("\n")


def test_the_window_opens_with_the_current_settings(prefs):
    assert prefs.top.title() == "Preferences"
    assert not prefs.check("Backup").variable.get()
    assert not prefs.check("Use spaces").variable.get()
    assert not prefs.check("Use Emacs").variable.get()
    assert not prefs.check("File prompts").variable.get()
    assert prefs.label("Python interpreter").cget("text") == (
        f"Python interpreter: '{state.pythonexecutable}'"
    )


def test_opening_runs_the_hooks(app, tk_root, editor, monkeypatch, console_messages):
    seen = []
    state.pcbeforehooks["open-preferences"] = [lambda value: seen.append("before")]
    state.pcafterhooks["open-preferences"] = [lambda value: seen.append("after")]
    monkeypatch.setattr(
        tk_root, "subwin", lambda *a, **k: _hidden(tk_root), raising=False
    )

    preferences.prf()

    assert seen == ["before", "after"]


def _hidden(root):
    top = ctk.Toplevel(root)
    top.withdraw()
    return top


@pytest.mark.parametrize(
    ("text", "name"),
    [
        ("Backup", "bfr"),
        ("Use spaces", "taborspace"),
        ("Use Emacs", "emacskeysforsearch"),
        ("File prompts", "nographicalfiledialogs"),
    ],
)
def test_the_checkboxes_change_the_settings(prefs, text, name):
    check = prefs.check(text)

    check.invoke()
    assert getattr(state, name) is True
    check.invoke()
    assert getattr(state, name) is False


def test_the_python_interpreter_can_be_changed(prefs, monkeypatch, tmp_path):
    chosen = tmp_path / "python"
    monkeypatch.setattr(dialogs, "openfileget", lambda *a, **k: str(chosen))

    prefs.button("Change").invoke()

    assert state.pythonexecutable == str(chosen)
    assert prefs.label("Python interpreter").cget("text") == (
        f"Python interpreter: '{chosen}'"
    )


def test_cancelling_the_interpreter_change_keeps_it(prefs, monkeypatch):
    before = state.pythonexecutable
    monkeypatch.setattr(dialogs, "openfileget", lambda *a, **k: "")

    prefs.button("Change").invoke()

    assert state.pythonexecutable == before


def test_the_cursor_shape_is_changed_in_every_editor_and_the_command_box(prefs, editor):
    shape_menu = next(o for o in prefs.options() if "Block" in o.values)

    shape_menu.pick("Underline")

    assert editor.type_.cursor_shape == "underline"
    assert state.cmdentry.cursor_shape == "underline"
    assert state.curcurtype == 2


def test_the_cursor_shape_menu_offers_the_three_shapes(prefs):
    shape_menu = next(o for o in prefs.options() if "Block" in o.values)

    assert list(shape_menu.values) == ["Line", "Block", "Underline"]
    assert shape_menu.variable.get() == "Line"


def test_the_ui_theme_menu_switches_the_theme(prefs, tk_root):
    theme_menu = next(o for o in prefs.options() if "Dark" in o.values)

    theme_menu.pick("Dark")

    assert tk_root.gettheme() == "Dark"


def test_the_font_menu_changes_the_editor_font_and_the_sample(prefs, editor):
    font_menu = next(o for o in prefs.options() if init.monospace in o.values)
    sample = next(
        w
        for w in prefs.widgets
        if isinstance(w, ctk.Textbox) and w.get("1.0", "1.9") == "The quick"
    )

    font_menu.pick("courier")

    assert state.defs[2] == "courier"
    assert editor.type_.cget("font").startswith("courier") or "courier" in str(
        editor.type_.cget("font")
    )
    assert "courier" in str(sample.cget("font"))


def test_the_colours_box_shows_the_theme_keys(prefs):
    text = prefs.colours.get("1.0", "end-1c")

    assert "'python:keywords'" in text
    assert "orgfont" in text
    assert "state.defs[2]" not in text


def test_the_email_dictionaries_are_listed(prefs):
    listbox = next(w for w in prefs.widgets if isinstance(w, ctk.Listbox))

    assert list(listbox.get(0, "end")) == state.dicts


def test_adding_a_dictionary_rebuilds_the_word_list(prefs, monkeypatch, tmp_path):
    words = tmp_path / "words.txt"
    words.write_text("alpha\nbeta")
    monkeypatch.setattr(dialogs, "openfileget", lambda *a, **k: str(words))
    state.dicts = []
    state.emailwordlist = ["stale"]

    prefs.button("Add").invoke()

    assert state.dicts == [str(words)]
    assert state.emailwordlist == ["alpha", "beta"]


def test_adding_an_unreadable_dictionary_is_reported(prefs, monkeypatch, tmp_path, app):
    monkeypatch.setattr(
        dialogs, "openfileget", lambda *a, **k: str(tmp_path / "missing.txt")
    )
    state.dicts = []

    prefs.button("Add").invoke()

    assert app.dialogs.of_kind("error")


def test_cancelling_a_dictionary_adds_nothing(prefs, monkeypatch):
    monkeypatch.setattr(dialogs, "openfileget", lambda *a, **k: "")
    before = list(state.dicts)

    prefs.button("Add").invoke()

    assert state.dicts == before


def test_removing_the_selected_dictionary(prefs, tmp_path):
    words = tmp_path / "words.txt"
    words.write_text("gamma")
    listbox = next(w for w in prefs.widgets if isinstance(w, ctk.Listbox))
    state.dicts = [str(words)]
    state.emailwordlist = ["stale"]
    listbox.delete(0, "end")
    listbox.insert("end", str(words))
    listbox.selection_set(0)

    prefs.button("Remove").invoke()

    assert state.dicts == []
    assert state.emailwordlist == []


def test_removing_without_a_selection_changes_nothing(prefs):
    before = list(state.dicts)

    prefs.button("Remove").invoke()

    assert state.dicts == before


def test_ok_saves_the_preferences_and_closes_the_window(prefs, app):
    prefs.check("Backup").invoke()
    prefs.check("Use spaces").invoke()

    prefs.button("OK").invoke()

    lines = saved_lines(app)
    assert lines[0] == init.v
    assert lines[1] == "True"
    assert lines[2] == state.defs[2]
    assert lines[3] == "Default"
    assert lines[4] == ",".join(state.dicts)
    assert lines[5] == "False"
    assert lines[6] == "True"
    assert lines[7] == "False"
    assert lines[8] == state.pythonexecutable
    assert lines[9] == "0"
    assert not prefs.top.winfo_exists()


def test_the_saved_file_loads_back(prefs, app):
    prefs.check("Backup").invoke()
    prefs.button("OK").invoke()
    before = dict(state.theme)

    file = open(app.home / ".local/share/PyNotes/defs")
    init.load_config(file, "unused")

    assert state.bfr is True
    assert state.theme == before


def test_saving_keeps_the_chosen_ui_theme(prefs, app, tk_root):
    next(o for o in prefs.options() if "Dark" in o.values).pick("Dark")

    prefs.button("OK").invoke()

    assert saved_lines(app)[3] == "Dark"


def test_saving_applies_an_edited_colour_at_once(prefs, editor):
    prefs.colours.delete("1.0", "end")
    text = str(
        {
            **state.theme,
            "python:keywords": "foreground = '#112233'",
        }
    )[
        1:-1
    ].replace("state.defs[2]", "orgfont")
    prefs.colours.insert("1.0", text)

    prefs.button("OK").invoke()

    assert state.theme["python:keywords"] == "foreground = '#112233'"
    assert editor.type_.tag_cget("hpa", "foreground") == "#112233"


def test_saving_refreshes_the_open_editors(prefs, editor, monkeypatch):
    refreshed = []
    monkeypatch.setattr(editor, "keypress", lambda: refreshed.append(True))

    prefs.button("OK").invoke()

    assert refreshed == [True]


def test_escape_saves_too(prefs, app):
    from test_utils import run_binding

    prefs.check("Backup").invoke()

    run_binding(prefs.top, "<Escape>")

    assert saved_lines(app)[1] == "True"
    assert not prefs.top.winfo_exists()


def test_closing_the_window_saves_too(prefs, app):
    prefs.check("Backup").invoke()

    prefs.top.tk.call(prefs.top.protocol("WM_DELETE_WINDOW"))

    assert saved_lines(app)[1] == "True"


def test_designing_a_theme_adds_and_selects_it(prefs, monkeypatch, tk_root):
    monkeypatch.setattr(
        themes, "creator", lambda: ("Mine", False, {"surface": "#123456"})
    )
    theme_menu = next(o for o in prefs.options() if "Dark" in o.values)

    prefs.button("Make your own!").invoke()

    assert "Mine" in tk_root.themes()
    assert tk_root.gettheme() == "Mine"
    assert "Mine" in theme_menu.values
    assert theme_menu.variable.get() == "Mine"


def test_cancelling_the_theme_designer_changes_nothing(prefs, monkeypatch, tk_root):
    monkeypatch.setattr(themes, "creator", lambda: None)
    before = tk_root.gettheme()

    prefs.button("Make your own!").invoke()

    assert tk_root.gettheme() == before


def test_a_plugins_preference_code_runs_when_the_window_opens(
    app, tk_root, editor, monkeypatch, console_messages
):
    state.plgnsprf = [("/plugins/Demo", "state.plugin_prefs_ran = True")]
    monkeypatch.setattr(
        tk_root, "subwin", lambda *a, **k: _hidden(tk_root), raising=False
    )

    preferences.prf()

    assert state.plugin_prefs_ran is True


def test_a_plugins_failing_preference_code_is_reported(
    app, tk_root, editor, monkeypatch, console_messages
):
    state.plgnsprf = [("/plugins/Demo", "1 / 0")]
    monkeypatch.setattr(
        tk_root, "subwin", lambda *a, **k: _hidden(tk_root), raising=False
    )

    preferences.prf()

    message = app.dialogs.messages("error")[0]
    assert 'preferences of the plugin "Demo"' in message
