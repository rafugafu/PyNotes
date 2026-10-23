"""The application window's own dialogs (ask, askstring, info, error,
warning), which can be answered in a window or from the terminal console,
whichever answers first.

The dialog windows are kept hidden and their buttons pressed by the tests;
the terminal console is a stand-in that answers, or waits to be cancelled.
"""

import threading
import time
from types import SimpleNamespace

import canvastk as ctk
import pytest

import state
import window

pytestmark = pytest.mark.display


def descendants(widget):
    for child in widget.winfo_children():
        yield child
        yield from descendants(child)


@pytest.fixture
def hidden_dialogs(app, tk_root, monkeypatch):
    """Dialog windows stay hidden and silent; the plain message boxes are
    recorded instead of shown. The window's real dialog methods are used."""
    monkeypatch.setattr(ctk.Toplevel, "deiconify", lambda self: None)
    monkeypatch.setattr(ctk.Toplevel, "bell", lambda self: None, raising=False)
    boxes = []
    for name in ("showinfo", "showerror", "showwarning"):
        monkeypatch.setattr(
            ctk.messagebox,
            name,
            lambda title, message, _name=name, **keywords: boxes.append(
                (_name, title, message)
            ),
        )
    for name in ("ask", "askstring", "info", "error", "warning"):
        tk_root.__dict__.pop(name, None)
    return SimpleNamespace(root=tk_root, boxes=boxes)


class ConsoleAnswers:
    """The terminal console: answers right away, or waits until cancelled."""

    def __init__(self, answer=None, wait=False):
        self.answer = answer
        self.wait = wait
        self.calls = []

    def _respond(self, kind, arguments, cancel_event):
        self.calls.append((kind, arguments))
        if self.wait:
            cancel_event.wait(5)
            return None
        return self.answer

    def ask(self, title, question, labels, color=None, cancel_event=None):
        return self._respond("ask", (title, question, labels, color), cancel_event)

    def prompt(self, title, prompt, cancel_event=None):
        return self._respond("prompt", (title, prompt), cancel_event)

    def dialog(self, *arguments):
        self.calls.append(("dialog", arguments))

    def show(self, text):
        pass


def click_when_open(root, label=None, entry_text=None, deadline=5):
    """Press a button of the dialog window as soon as there is one."""
    end = time.monotonic() + deadline

    def look():
        for top in root.winfo_children():
            if not isinstance(top, ctk.Toplevel):
                continue
            widgets = list(descendants(top))
            buttons = {w.cget("text"): w for w in widgets if isinstance(w, ctk.Button)}
            entries = [w for w in widgets if isinstance(w, ctk.Entry)]
            if label in buttons:
                if entry_text is not None and entries:
                    entries[0].insert(0, entry_text)
                buttons[label].invoke()
                return
        if time.monotonic() < end:
            root.after(10, look)

    root.after(10, look)


# ---------------------------------------------------------------------------
# Questions
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("options", "button", "answer"),
    [
        (("yes", "no"), "Yes", True),
        (("yes", "no"), "No", False),
        (("ok", "cancel"), "OK", True),
        (("ok", "cancel"), "Cancel", False),
        (("yes", "no", "cancel"), "Yes", True),
        (("yes", "no", "cancel"), "No", False),
        (("yes", "no", "cancel"), "Cancel", None),
        (("retry", "cancel"), "Retry", True),
        (("retry", "cancel"), "Cancel", False),
    ],
)
def test_a_question_answered_in_the_window(hidden_dialogs, options, button, answer):
    root = hidden_dialogs.root
    state.console = ConsoleAnswers(wait=True)
    click_when_open(root, button)

    assert root.ask("Title", "Question?", options) is answer
    assert state.console.calls[0][0] == "ask"


def test_a_question_with_other_options_returns_the_clicked_label(hidden_dialogs):
    root = hidden_dialogs.root
    state.console = ConsoleAnswers(wait=True)
    click_when_open(root, "Maybe")

    assert root.ask("Title", "Question?", ("Never", "Maybe")) == "Maybe"


def test_a_question_answered_in_the_console(hidden_dialogs):
    root = hidden_dialogs.root
    state.console = ConsoleAnswers(answer=2)

    assert root.ask("Title", "Question?", ("yes", "no")) is True
    # The console numbers the buttons in the order they were given to it.
    assert state.console.calls[0][1][2] == ["No", "Yes"]


def test_a_console_answer_out_of_range_is_no_answer(hidden_dialogs):
    root = hidden_dialogs.root
    state.console = ConsoleAnswers(answer=9)

    assert root.ask("Title", "Question?", ("yes", "no")) is None


def test_the_question_window_closes_when_the_console_answers(hidden_dialogs):
    root = hidden_dialogs.root
    state.console = ConsoleAnswers(answer=1)

    root.ask("Title", "Question?", ("yes", "no"))
    root.update()

    assert not [w for w in root.winfo_children() if isinstance(w, ctk.Toplevel)]


# ---------------------------------------------------------------------------
# Text questions
# ---------------------------------------------------------------------------


def test_a_text_question_answered_in_the_window(hidden_dialogs):
    root = hidden_dialogs.root
    state.console = ConsoleAnswers(wait=True)
    click_when_open(root, "Submit", entry_text="typed answer")

    assert root.askstring("Name", "Your name?") == "typed answer"
    assert state.console.calls == [("prompt", ("Name", "Your name?"))]


def test_a_cancelled_text_question_has_no_answer(hidden_dialogs):
    root = hidden_dialogs.root
    state.console = ConsoleAnswers(wait=True)
    click_when_open(root, "Cancel")

    assert root.askstring("Name", "Your name?") is None


def test_a_text_question_answered_in_the_console(hidden_dialogs):
    root = hidden_dialogs.root
    state.console = ConsoleAnswers(answer="from console")

    assert root.askstring("Name", "Your name?") == "from console"


# ---------------------------------------------------------------------------
# Notices
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("method", "box", "color"),
    [
        ("info", "showinfo", None),
        ("error", "showerror", "41m"),
        ("warning", "showwarning", "43m"),
    ],
)
def test_a_notice_is_shown_and_mirrored_to_the_console(
    hidden_dialogs, method, box, color
):
    root = hidden_dialogs.root
    state.console = ConsoleAnswers()

    getattr(root, method)("Title", "Message")

    assert hidden_dialogs.boxes == [(box, "Title", "Message")]
    deadline = time.monotonic() + 5
    while not state.console.calls and time.monotonic() < deadline:
        time.sleep(0.005)
    expected = ("Title", "Message") + ((color,) if color else ())
    assert state.console.calls == [("dialog", expected)]


@pytest.mark.parametrize(
    ("method", "color"), [("info", "100m"), ("error", "41m"), ("warning", "43m")]
)
def test_a_notice_with_buttons_returns_the_button_pressed(
    hidden_dialogs, method, color
):
    root = hidden_dialogs.root
    state.console = ConsoleAnswers(wait=True)
    click_when_open(root, "Reload")

    answer = getattr(root, method)("Title", "Message", buttons=["Ignore", "Reload"])

    assert answer == "Reload"
    kind, arguments = state.console.calls[0]
    assert kind == "ask" and arguments[3] == color
    assert hidden_dialogs.boxes == []


def test_a_notice_with_buttons_can_be_answered_in_the_console(hidden_dialogs):
    root = hidden_dialogs.root
    state.console = ConsoleAnswers(answer=1)

    assert root.warning("Title", "Message", buttons=["Ignore", "Reload"]) == "Ignore"


def test_a_notice_window_has_the_message_and_the_buttons(hidden_dialogs):
    root = hidden_dialogs.root
    state.console = ConsoleAnswers(wait=True)
    seen = {}

    def look():
        for top in root.winfo_children():
            if isinstance(top, ctk.Toplevel):
                widgets = list(descendants(top))
                seen["title"] = top.title()
                seen["labels"] = [
                    w.cget("text") for w in widgets if isinstance(w, ctk.Label)
                ]
                seen["buttons"] = [
                    w.cget("text") for w in widgets if isinstance(w, ctk.Button)
                ]
                for w in widgets:
                    if isinstance(w, ctk.Button) and w.cget("text") == "B":
                        w.invoke()
                return
        root.after(10, look)

    root.after(10, look)

    root.info("The Title", "The message", buttons=["A", "B"])

    assert seen["title"] == "The Title"
    assert "The message" in seen["labels"]
    assert seen["buttons"] == ["A", "B"]


# ---------------------------------------------------------------------------
# Sub-windows
# ---------------------------------------------------------------------------


def test_a_subwindow_belongs_to_the_window_or_to_a_given_parent(hidden_dialogs):
    root = hidden_dialogs.root
    first = root.subwin()
    second = root.subwin(parent=first)
    try:
        assert first.master is root
        assert second.master is first
    finally:
        first.destroy()
