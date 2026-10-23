"""PyNotes' startup helpers: the small standalone dialogs, the virtual
environment switch, the dependency check, and the preferences file."""

import io
import sys
from types import SimpleNamespace

import canvastk as ctk
import pytest

import cli
import dialogs
import init
import state

pytestmark = pytest.mark.display


class Exited(Exception):
    pass


# ---------------------------------------------------------------------------
# Exiting and the standalone dialogs
# ---------------------------------------------------------------------------


def test_exit_closes_the_console_and_ends_the_process(monkeypatch):
    closed = []
    monkeypatch.setattr(cli, "close", lambda: closed.append(True))

    with pytest.raises(SystemExit) as info:
        init.exit(3)

    assert info.value.code == 3
    assert closed == [True]


def test_exit_still_ends_the_process_if_the_console_fails(monkeypatch):
    def broken():
        raise RuntimeError

    monkeypatch.setattr(cli, "close", broken)

    with pytest.raises(SystemExit):
        init.exit()


class DialogWindow(ctk.Toplevel):
    """A standalone dialog's window, which is a hidden subwindow whose main
    loop presses a button instead of waiting for the user."""

    press = None
    labels = []
    title_text = None
    delete_protocol = None

    def __init__(self, *arguments, **keywords):
        super().__init__(state.root)
        self.withdraw()
        DialogWindow.last = self

    def mainloop(self, *arguments):
        buttons = {
            widget.cget("text"): widget
            for widget in descendants(self)
            if isinstance(widget, ctk.Button)
        }
        DialogWindow.labels = list(buttons)
        DialogWindow.title_text = self.title()
        DialogWindow.delete_protocol = self.protocol("WM_DELETE_WINDOW")
        if DialogWindow.press:
            buttons[DialogWindow.press].invoke()


def descendants(widget):
    for child in widget.winfo_children():
        yield child
        yield from descendants(child)


@pytest.fixture
def dialog_window(app, monkeypatch):
    monkeypatch.setattr(ctk, "Window", DialogWindow)
    DialogWindow.press = None
    DialogWindow.labels = []
    yield DialogWindow
    try:
        DialogWindow.last.destroy()
    except Exception:
        pass


def test_info_shows_a_message_with_a_close_button(dialog_window):
    dialog_window.press = "Close"

    init.info("Title", "Some information")

    assert dialog_window.labels == ["Close"]
    assert dialog_window.title_text == "Title"
    assert not dialog_window.last.winfo_exists()


@pytest.mark.parametrize(("button", "answer"), [("Yes", True), ("No", False)])
def test_ask_returns_the_button_pressed(dialog_window, button, answer):
    dialog_window.press = button

    assert init.ask("Question", "Sure?") is answer
    assert sorted(dialog_window.labels) == ["No", "Yes"]


def test_the_ask_window_cannot_be_closed_without_answering(dialog_window):
    dialog_window.press = "Yes"

    init.ask("Question", "Sure?")

    assert dialog_window.delete_protocol != ""


# ---------------------------------------------------------------------------
# The virtual environment
# ---------------------------------------------------------------------------


@pytest.fixture
def venv(app, monkeypatch):
    calls = SimpleNamespace(shown=[], runs=[], execs=[])
    monkeypatch.setattr(init.mb, "showinfo", lambda *a, **k: calls.shown.append(a))
    monkeypatch.setattr(
        init.subprocess, "run", lambda *a, **k: calls.runs.append((a, k))
    )
    monkeypatch.setattr(init.os, "execv", lambda *a: calls.execs.append(a))
    monkeypatch.setattr(init.platform, "system", lambda: "Linux")
    calls.directory = f"{app.home}/.local/share/PyNotes/venv"
    return calls


def test_a_missing_venv_is_created_and_then_used(venv, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["pynotes", "file.txt"])

    init.switchvenv()

    assert venv.shown[0][0] == "Making Python virtual environment"
    assert venv.runs == [
        (([sys.executable, "-m", "venv", venv.directory],), {"check": True})
    ]
    assert venv.execs == [
        (
            f"{venv.directory}/bin/python",
            [f"{venv.directory}/bin/python", "pynotes", "file.txt"],
        )
    ]


def test_an_existing_venv_is_not_created_again(venv, monkeypatch, app):
    import os

    os.makedirs(f"{venv.directory}/bin")
    open(f"{venv.directory}/bin/python", "w").close()
    monkeypatch.setattr(sys, "argv", ["pynotes"])

    init.switchvenv()

    assert venv.shown == [] and venv.runs == []
    assert len(venv.execs) == 1


def test_already_running_in_the_venv_changes_nothing(venv, monkeypatch):
    import os

    os.makedirs(f"{venv.directory}/bin")
    open(f"{venv.directory}/bin/python", "w").close()
    monkeypatch.setattr(sys, "prefix", venv.directory)

    init.switchvenv()

    assert venv.execs == []


def test_other_systems_do_not_use_a_venv(venv, monkeypatch):
    monkeypatch.setattr(init.platform, "system", lambda: "Windows")

    init.switchvenv()

    assert venv.shown == [] and venv.execs == []


# ---------------------------------------------------------------------------
# The dependency check
# ---------------------------------------------------------------------------

DEPENDENCIES = [
    ("tika", "tika"),
    ("pdfplumber", "pdfplumber"),
    ("pyttsx3", "pyttsx3"),
    ("matplotlib", "matplotlib"),
    ("sympy", "sympy"),
    ("sounddevice", "sounddevice"),
    ("speech_recognition", "SpeechRecognition"),
    ("numpy", "numpy"),
    ("ziamath", "ziamath"),
    ("cairosvg", "cairosvg"),
    ("watchdog", "watchdog"),
]


def blocked_names(module):
    """The names to make unimportable so that importing module fails, however
    it is imported."""
    return {
        "tika": ["tika", "tika.parser"],
        "watchdog": ["watchdog", "watchdog.observers", "watchdog.events"],
    }.get(module, [module])


@pytest.fixture
def dependency_dialogs(app, monkeypatch):
    calls = SimpleNamespace(asked=[], installed=[], answer=True, infos=[])
    monkeypatch.setattr(
        init,
        "ask",
        lambda title, text: calls.asked.append((title, text)) or calls.answer,
    )
    monkeypatch.setattr(init, "info", lambda *a: calls.infos.append(a))
    monkeypatch.setattr(
        dialogs, "faketerm", lambda command: calls.installed.append(command)
    )
    monkeypatch.setattr(init, "exit", lambda *a: (_ for _ in ()).throw(Exited(a)))
    return calls


def test_nothing_is_asked_when_everything_is_installed(dependency_dialogs):
    init.ensure_dependencies()

    assert dependency_dialogs.asked == []
    assert dependency_dialogs.installed == []


@pytest.mark.parametrize(("module", "package"), DEPENDENCIES)
def test_a_missing_module_is_offered_for_installation(
    dependency_dialogs, monkeypatch, module, package
):
    installed_modules = dict(sys.modules)
    for name in blocked_names(module):
        monkeypatch.setitem(sys.modules, name, None)

    # Installing "works": the module is importable again afterwards.
    def install(command):
        dependency_dialogs.installed.append(command)
        for name in blocked_names(module):
            sys.modules[name] = installed_modules.get(name) or SimpleNamespace()

    monkeypatch.setattr(dialogs, "faketerm", install)

    init.ensure_dependencies()

    assert dependency_dialogs.asked[0][1].startswith(f"The module '{module}'")
    assert dependency_dialogs.installed == [f"pip3 install {package}"]


@pytest.mark.parametrize(("module", "package"), DEPENDENCIES)
def test_declining_to_install_a_module_quits(
    dependency_dialogs, monkeypatch, module, package
):
    for name in blocked_names(module):
        monkeypatch.setitem(sys.modules, name, None)
    dependency_dialogs.answer = False

    with pytest.raises(Exited):
        init.ensure_dependencies()

    assert dependency_dialogs.installed == []


def test_a_module_that_still_cannot_be_imported_after_installing_quits(
    dependency_dialogs, monkeypatch
):
    monkeypatch.setitem(sys.modules, "numpy", None)

    with pytest.raises(Exited):
        init.ensure_dependencies()

    assert dependency_dialogs.installed == ["pip3 install numpy"]
    assert dependency_dialogs.infos[-1][1] == (
        "The modules were not installed properly. Quitting PyNotes."
    )


# ---------------------------------------------------------------------------
# The preferences file
# ---------------------------------------------------------------------------


def test_the_preferences_are_created_on_first_run(app, monkeypatch):
    welcomed = []
    monkeypatch.setattr(init, "info", lambda *a: welcomed.append(a))
    defs = app.home / ".local" / "share" / "PyNotes" / "defs"
    defs.unlink()

    file, new, default_defs = init.load_or_create_defs()

    assert new is True
    assert welcomed == [("", "Welcome to PyNotes!")]
    assert file.read() == default_defs
    assert defs.read_text() == default_defs
    file.close()


def test_existing_preferences_are_reopened_as_they_are(app, monkeypatch):
    welcomed = []
    monkeypatch.setattr(init, "info", lambda *a: welcomed.append(a))
    defs = app.home / ".local" / "share" / "PyNotes" / "defs"
    defs.write_text("custom")

    file, new, default_defs = init.load_or_create_defs()

    assert new is False
    assert welcomed == []
    assert file.read() == "custom"
    file.close()


def test_the_default_preferences_have_every_theme_key(app):
    file, _, default_defs = init.load_or_create_defs()
    file.close()
    lines = default_defs.split("\n")

    assert lines[0] == init.v
    assert lines[1] in ("True", "False")
    assert len(lines) == 11


def test_loaded_preferences_fill_the_state(app):
    assert state.bfr is False
    assert state.emacskeysforsearch is False
    assert state.taborspace is False
    assert state.nographicalfiledialogs is False
    assert state.curcurtype == 0
    assert state.defs[2] == init.monospace
    assert state.dicts == [f"{init.rootdir}/english.txt"]
    assert "python:keywords" in state.theme


@pytest.fixture
def preferences_file(app, monkeypatch):
    """Load other preferences than the default ones."""
    monkeypatch.setattr(app.dialogs, "defaults", app.dialogs.defaults)
    defs_path = app.home / ".local" / "share" / "PyNotes" / "defs"
    _, _, default_defs = init.load_or_create_defs()

    def load(text):
        defs_path.write_text(text)
        return init.load_config(open(defs_path), default_defs)

    load.default = default_defs
    load.path = defs_path
    return load


def test_changed_preferences_are_loaded(app, preferences_file):
    lines = preferences_file.default.split("\n")
    lines[1] = "True"
    lines[5] = "True"
    lines[6] = "True"
    lines[7] = "True"
    lines[9] = "2"
    lines[4] = "a.txt,b.txt"

    preferences_file("\n".join(lines))

    assert state.bfr is True
    assert state.emacskeysforsearch is True
    assert state.taborspace is True
    assert state.nographicalfiledialogs is True
    assert state.curcurtype == 2
    assert state.dicts == ["a.txt", "b.txt"]


def test_preferences_from_an_older_version_are_updated_and_announced(
    app, preferences_file
):
    lines = preferences_file.default.split("\n")
    lines[0] = "0.0.1"

    preferences_file("\n".join(lines))

    assert ("info", "Info", "PyNotes has been updated!") in app.dialogs.calls
    assert preferences_file.path.read_text().split("\n")[0] == init.v
    assert state.defs[0] == init.v


def test_same_version_preferences_are_not_announced(app, preferences_file):
    preferences_file(preferences_file.default)

    assert app.dialogs.of_kind("info") == []


def test_preferences_missing_settings_can_be_reset(app, preferences_file):
    app.dialogs.answer("ask", True)

    preferences_file(
        "0.0.1\nFalse\nmonospace\nDefault\nenglish.txt\nFalse\nFalse\nFalse\n/usr/bin/python3\n'a': \"b\""
    )

    assert "older version of PyNotes" in app.dialogs.messages("ask")[0]
    assert preferences_file.path.read_text() == preferences_file.default or (
        preferences_file.path.read_text().startswith(init.v)
    )
    assert state.defs[2] == init.monospace


def test_declining_to_reset_old_preferences_quits(app, preferences_file, monkeypatch):
    app.dialogs.answer("ask", False)
    destroyed = []
    monkeypatch.setattr(state.root, "destroy", lambda: destroyed.append(True))
    monkeypatch.setattr(init, "exit", lambda *a: (_ for _ in ()).throw(Exited(a)))

    with pytest.raises(Exited):
        preferences_file("broken preferences")

    assert ("info", "Info", "Quitting PyNotes") in app.dialogs.calls
    assert destroyed == [True]


def test_a_missing_icon_quits(app, preferences_file, monkeypatch, tmp_path):
    monkeypatch.setattr(init, "rootdir", str(tmp_path))
    destroyed = []
    monkeypatch.setattr(state.root, "destroy", lambda: destroyed.append(True))
    monkeypatch.setattr(init, "exit", lambda *a: (_ for _ in ()).throw(Exited(a)))

    with pytest.raises(Exited):
        preferences_file(preferences_file.default)

    assert "Could not find the icon" in app.dialogs.messages("error")[0]
    assert destroyed == [True]


def test_the_window_gets_its_starting_size(app, preferences_file, monkeypatch):
    sizes = []
    monkeypatch.setattr(state.root, "geometry", lambda size: sizes.append(size))

    preferences_file(preferences_file.default)

    assert sizes == ["820x800"]
