"""PyNotes' file dialogs, which a graphical dialog or the terminal console
can answer, whichever answers first, and the other helpers around them."""

import re
import threading
import time
from types import SimpleNamespace

import canvastk as ctk
import pytest

import dialogs
import state
from box_driver import drive
import utils
from test_editor import editor
from test_utils import run_binding
from test_window_dialogs import ConsoleAnswers, descendants

pytestmark = pytest.mark.display


@pytest.fixture(autouse=True)
def the_real_file_dialogs(app, monkeypatch):
    """The tests of the file dialogs need the real ones, which the
    application fixture replaces with cancelled ones."""
    for name, function in app.real_file_dialogs.items():
        monkeypatch.setattr(dialogs, name, function)


# ---------------------------------------------------------------------------
# Path completion and the dialog's starting place
# ---------------------------------------------------------------------------


def test_completing_a_path_lists_the_directory(tmp_path):
    tmp_path = tmp_path / "listed"
    tmp_path.mkdir()
    (tmp_path / "alpha.txt").write_text("")
    (tmp_path / "beta").mkdir()

    candidates = dialogs.fileautocompletefunc(str(tmp_path) + "/")

    assert set(candidates) == {
        "../",
        f"{tmp_path}/alpha.txt",
        f"{tmp_path}/beta/",
    }


def test_hidden_files_are_only_listed_when_a_dot_is_typed(tmp_path):
    (tmp_path / ".hidden").write_text("")
    (tmp_path / "shown").write_text("")

    without_dot = dialogs.fileautocompletefunc(str(tmp_path) + "/")
    with_dot = dialogs.fileautocompletefunc(str(tmp_path) + "/.h")

    assert f"{tmp_path}/.hidden" not in without_dot
    assert f"{tmp_path}/.hidden" in with_dot


def test_a_missing_directory_has_no_completions(tmp_path):
    assert dialogs.fileautocompletefunc(str(tmp_path / "missing") + "/x") == ()


def test_a_path_with_surrounding_spaces_and_a_home_directory(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    (tmp_path / "doc.txt").write_text("")

    candidates = dialogs.fileautocompletefunc("  ~/d  ")

    assert "~/doc.txt" in candidates


@pytest.mark.parametrize("initial", [None, ""])
def test_the_dialog_starts_in_the_current_directory(initial, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    assert dialogs._file_dialog_initial_dir_and_name(initial) == (str(tmp_path), "")


def test_the_dialog_starts_in_a_given_directory(tmp_path):
    assert dialogs._file_dialog_initial_dir_and_name(str(tmp_path)) == (
        str(tmp_path),
        "",
    )


def test_the_dialog_starts_with_a_given_file(tmp_path):
    path = tmp_path / "name.txt"

    assert dialogs._file_dialog_initial_dir_and_name(str(path)) == (
        str(tmp_path),
        "name.txt",
    )


# ---------------------------------------------------------------------------
# Graphical dialogs against the console
# ---------------------------------------------------------------------------


@pytest.fixture
def graphical(app, tk_root, monkeypatch):
    state.nographicalfiledialogs = False
    state.console = ConsoleAnswers(wait=True)
    calls = SimpleNamespace(open=[], save=[])
    from canvastk import filedialog

    def answering(kind, answer):
        def dialog(**keywords):
            calls.__dict__[kind].append(keywords)
            return answer() if callable(answer) else answer

        return dialog

    calls.answer_open = lambda answer: monkeypatch.setattr(
        filedialog, "askopenfilename", answering("open", answer)
    )
    calls.answer_save = lambda answer: monkeypatch.setattr(
        filedialog, "asksaveasfilename", answering("save", answer)
    )
    return calls


def test_open_returns_the_file_chosen_in_the_dialog(graphical, tmp_path):
    path = tmp_path / "a.txt"
    path.write_text("x")
    graphical.answer_open(str(path))

    assert dialogs.openfileget() == str(path)
    assert state.fileopenhistory == [str(path)]
    assert graphical.open[0]["title"] == "Open File"


def test_open_passes_the_file_types_and_starting_place(graphical, tmp_path):
    graphical.answer_open("")
    types = (("Python", "*.py"),)

    dialogs.openfileget(types, initialfile=str(tmp_path / "start.py"))

    assert graphical.open[0]["filetypes"] == types
    assert graphical.open[0]["initialdir"] == str(tmp_path)
    assert graphical.open[0]["initialfile"] == "start.py"


def test_open_that_is_cancelled_returns_nothing(graphical):
    graphical.answer_open("")

    assert dialogs.openfileget() == ""
    assert state.fileopenhistory == []


def test_open_of_a_file_that_does_not_exist_is_an_error(graphical, tmp_path, tk_root):
    graphical.answer_open(str(tmp_path / "missing.txt"))

    assert dialogs.openfileget() is None
    assert utils_message(tk_root) == f"error: '{tmp_path}/missing.txt' does not exist"


def test_open_of_a_directory_is_an_error(graphical, tmp_path, tk_root):
    graphical.answer_open(str(tmp_path))

    assert dialogs.openfileget() is None
    assert utils_message(tk_root) == f"error: '{tmp_path}' is a directory"


def utils_message(root):
    deadline = time.monotonic() + 2
    while time.monotonic() < deadline:
        root.update()
        text = state.cmdentry.get("1.0", "end-1c")
        if text:
            return text
        time.sleep(0.005)
    return ""


def test_save_returns_the_name_chosen_in_the_dialog(graphical, tmp_path):
    graphical.answer_save(str(tmp_path / "new.txt"))

    assert dialogs.saveasfileget() == str(tmp_path / "new.txt")
    assert state.filesavehistory == [str(tmp_path / "new.txt")]


def test_save_that_is_cancelled_returns_nothing(graphical):
    graphical.answer_save("")

    assert dialogs.saveasfileget() == ""
    assert state.filesavehistory == []


def test_the_console_may_answer_first(graphical, tk_root, tmp_path):
    path = tmp_path / "console.txt"
    path.write_text("x")
    state.console = ConsoleAnswers(answer=str(path))

    def blocking_dialog(**keywords):
        top = state.root.subwin()
        top.withdraw()
        while top.winfo_exists():
            state.root.update()
            time.sleep(0.005)
        return ""

    from canvastk import filedialog

    filedialog.askopenfilename = blocking_dialog
    try:
        assert dialogs.openfileget() == str(path)
    finally:
        pass


def test_the_dialog_may_answer_first_and_the_console_is_cancelled(graphical, tmp_path):
    path = tmp_path / "a.txt"
    path.write_text("x")
    graphical.answer_open(str(path))
    cancelled = threading.Event()

    class Console(ConsoleAnswers):
        def prompt(self, title, prompt, cancel_event=None):
            cancel_event.wait(5)
            cancelled.set()

    state.console = Console()

    assert dialogs.openfileget() == str(path)
    assert cancelled.wait(5)


# ---------------------------------------------------------------------------
# The same dialogs in the Alt-X box
# ---------------------------------------------------------------------------


@pytest.fixture
def in_the_box(app, tk_root, monkeypatch, editor):
    """File dialogs asked in the Alt-X box, answered by scripted actions."""
    state.nographicalfiledialogs = True
    state.console = ConsoleAnswers(wait=True)

    def run(function, *actions, **keywords):
        return drive(tk_root, lambda: function(**keywords), actions, delay=40)

    return run


def typing(text, prompt=None):
    """Type text; with a prompt, first clear the path the box starts with."""

    def action(box):
        if prompt is not None:
            box.delete(f"1.{len(prompt)}", "end")
        box.insert("end", text)

    return action


def press(sequence):
    return lambda box: run_binding(box.inner, sequence)


def test_open_in_the_box_returns_the_typed_path(in_the_box, tmp_path):
    path = tmp_path / "typed.txt"
    path.write_text("x")

    result = in_the_box(
        dialogs.openfileget, typing(str(path), "Open File: "), press("<Return>")
    )

    assert result.startswith("/") and result.endswith("typed.txt")
    assert state.fileopenhistory[-1] == result


def test_open_in_the_box_starts_with_the_working_directory(
    in_the_box, tmp_path, monkeypatch
):
    monkeypatch.chdir(tmp_path)
    seen = []

    result = in_the_box(
        dialogs.openfileget,
        lambda box: seen.append(box.get("1.0", "end-1c")),
        press("<Escape>"),
    )

    assert seen[0].startswith("Open File: ")
    assert seen[0].endswith(str(tmp_path).replace(dialogs.homedir, "~") + "/")
    assert result == ""


def test_open_in_the_box_with_nothing_typed(in_the_box):
    assert in_the_box(dialogs.openfileget, press("<Escape>")) == ""


def test_open_in_the_box_of_a_missing_file(in_the_box, tmp_path, tk_root):
    result = in_the_box(
        dialogs.openfileget,
        typing(str(tmp_path / "missing.txt"), "Open File: "),
        press("<Return>"),
    )

    assert result is None
    assert "does not exist" in utils_message(tk_root)


def test_open_in_the_box_of_a_directory(in_the_box, tmp_path, tk_root):
    result = in_the_box(
        dialogs.openfileget, typing(str(tmp_path), "Open File: "), press("<Return>")
    )

    assert result is None
    assert "is a directory" in utils_message(tk_root)


def test_save_in_the_box_returns_a_new_path(in_the_box, tmp_path):
    result = in_the_box(
        dialogs.saveasfileget,
        typing(str(tmp_path / "new.txt"), "Save File: "),
        press("<Return>"),
    )

    assert result == str(tmp_path / "new.txt")
    assert state.filesavehistory[-1] == str(tmp_path / "new.txt")


def test_save_in_the_box_with_nothing_typed(in_the_box):
    assert in_the_box(dialogs.saveasfileget, press("<Escape>")) == ""


def test_save_in_the_box_over_a_directory(in_the_box, tmp_path, tk_root):
    result = in_the_box(
        dialogs.saveasfileget, typing(str(tmp_path), "Save File: "), press("<Return>")
    )

    assert result is None
    assert "already existing directory" in utils_message(tk_root)


def test_save_in_the_box_over_a_file_overwrites_when_confirmed(in_the_box, tmp_path):
    path = tmp_path / "exists.txt"
    path.write_text("x")

    result = in_the_box(
        dialogs.saveasfileget,
        typing(str(path), "Save File: "),
        press("<Return>"),
        typing("yes"),
        press("<Return>"),
    )

    assert result == str(path)


def test_save_in_the_box_over_a_file_asks_again_when_declined(in_the_box, tmp_path):
    path = tmp_path / "exists.txt"
    path.write_text("x")
    other = tmp_path / "other.txt"

    result = in_the_box(
        dialogs.saveasfileget,
        typing(str(path), "Save File: "),
        press("<Return>"),
        typing("n"),
        press("<Return>"),
        typing(str(other), "Save File: "),
        press("<Return>"),
    )

    assert result == str(other)


def test_the_console_may_answer_a_box_prompt(app, tk_root, tmp_path, editor):
    path = tmp_path / "console.txt"
    path.write_text("x")
    state.nographicalfiledialogs = True
    state.console = ConsoleAnswers(answer=str(path))

    assert dialogs.openfileget() == str(path)


# ---------------------------------------------------------------------------
# Showing a LaTeX PDF
# ---------------------------------------------------------------------------


@pytest.fixture
def hidden_subwindows(app, tk_root, monkeypatch):
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


def test_an_existing_pdf_is_opened_with_the_system(app, monkeypatch, tmp_path):
    runs = []
    monkeypatch.setattr(dialogs.subprocess, "run", lambda *a, **k: runs.append((a, k)))
    (tmp_path / "doc.pdf").write_text("pdf")

    dialogs.pdf(str(tmp_path / "doc.tex"))

    assert runs == [
        ((["xdg-open", str(tmp_path / "doc.pdf")],), {"cwd": str(tmp_path)})
    ]


def test_a_missing_pdf_offers_the_log(app, hidden_subwindows, tmp_path):
    (tmp_path / "doc.log").write_text("! LaTeX Error: bad")
    app.dialogs.answer("ask", True)

    dialogs.pdf(str(tmp_path / "doc.tex"))

    (window_,) = hidden_subwindows
    assert window_.title() == "LaTeX log for doc.tex"
    box = next(w for w in descendants(window_) if isinstance(w, ctk.Textbox))
    assert box.get("1.0", "end-1c") == "! LaTeX Error: bad"
    assert app.dialogs.messages("ask")[0].startswith("The pdf could not be shown")


def test_a_missing_pdf_and_log(app, hidden_subwindows, tmp_path):
    app.dialogs.answer("ask", True)

    dialogs.pdf(str(tmp_path / "doc.tex"))

    (window_,) = hidden_subwindows
    box = next(w for w in descendants(window_) if isinstance(w, ctk.Textbox))
    assert box.get("1.0", "end-1c") == "log not found"
    assert "was not found at" in app.dialogs.messages("error")[0]


def test_a_missing_pdf_can_be_left_alone(app, hidden_subwindows, tmp_path):
    app.dialogs.answer("ask", False)

    dialogs.pdf(str(tmp_path / "doc.tex"))

    assert hidden_subwindows == []


def test_a_file_that_is_not_tex_is_taken_as_it_is(app, monkeypatch, tmp_path):
    runs = []
    monkeypatch.setattr(dialogs.subprocess, "run", lambda *a, **k: runs.append(a))
    (tmp_path / "notes.pdf").write_text("pdf")

    dialogs.pdf(str(tmp_path / "notes"))

    assert runs == [(["xdg-open", str(tmp_path / "notes.pdf")],)]


# ---------------------------------------------------------------------------
# The install window
# ---------------------------------------------------------------------------


class FakeTerminalWindow(ctk.Toplevel):
    """The install window, hidden, remembering what it showed."""

    shown = None

    def __init__(self, *arguments, **keywords):
        super().__init__(state.root)
        self.withdraw()
        FakeTerminalWindow.last = self

    def destroy(self):
        for widget in descendants(self):
            if isinstance(widget, ctk.Textbox):
                FakeTerminalWindow.shown = widget.get("1.0", "end-1c")
        super().destroy()


@pytest.fixture
def install_window(app, monkeypatch):
    monkeypatch.setattr(ctk, "Window", FakeTerminalWindow)
    monkeypatch.setattr(dialogs.time, "sleep", lambda seconds: None)
    FakeTerminalWindow.shown = None


def test_the_install_window_shows_the_command_and_its_output(install_window):
    dialogs.faketerm("echo hello from pip")

    assert FakeTerminalWindow.shown.endswith("$ echo hello from pip\nhello from pip\n")
    assert "@PyNotes:~$" in FakeTerminalWindow.shown
    assert not FakeTerminalWindow.last.winfo_exists()


def test_the_install_window_shows_error_output_too(install_window):
    dialogs.faketerm("echo to-stderr >&2")

    assert "to-stderr" in FakeTerminalWindow.shown
