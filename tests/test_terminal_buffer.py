"""The terminal buffer, which wraps a Terminal in the application's buffer
layout, and terminal.term(), which opens one. The shell itself is not
started: the terminal starts its process when it is first shown."""

import re

import pytest

import state
import terminal
import window
from test_editor import editor, wait_for_message
from test_utils import console_messages  # noqa: F401

pytestmark = pytest.mark.display


@pytest.fixture
def term_window(app, tk_root, editor, console_messages):
    return tk_root


def fire(terminal_widget, sequence):
    """Run the Tcl script bound to a virtual event on the terminal (events
    cannot be delivered to a window that is never shown)."""
    script = re.sub(r"%.", "0", terminal_widget.realbind(sequence))
    terminal_widget.tk.eval("while 1 {" + script + "\nbreak}")


def open_term(*arguments, **keywords):
    terminal.term(*arguments, **keywords)
    return state.all_buffers[-1]


def test_a_terminal_buffer_is_active_and_runs_the_default_shell_command(term_window):
    buffer = open_term()

    assert isinstance(buffer, terminal.TerminalBuffer)
    assert state.active is buffer
    assert buffer.term._term_command == ["/bin/bash"]
    assert buffer.wanttitle == "*PyNotes Terminal* - /bin/bash"
    assert buffer.running is True
    assert buffer.mainwidget is buffer.term


def test_a_terminal_for_a_command(term_window):
    buffer = open_term(["echo", "hello world"], title="Echo", endmessage="done")

    assert buffer.term._term_command == ["echo", "hello world"]
    assert buffer.wanttitle == "*PyNotes Terminal* - echo hello world"
    assert buffer.term.endmessage == "done"
    assert buffer.infos["title"].cget("text") == "Echo"
    assert buffer.infos["command"].cget("text") == "echo hello world"
    assert buffer.infos["buffertype"].cget("text") == "*PyNotes Terminal*"


def test_opening_the_plain_terminal_says_so(term_window):
    open_term()

    wait_for_message(term_window, "open pynotes terminal")


def test_a_command_terminal_does_not_say_so(term_window):
    open_term(["true"])

    assert state.cmdentry.get("1.0", "end-1c") != "open pynotes terminal"


def test_the_buffers_menu_is_the_terminal_menu(term_window):
    buffer = open_term()

    labels = [entry["label"] for entry in buffer.m.entries]

    assert labels == list(state.all_terminal_menus)


def test_copy_paste_and_select_all_are_the_terminals(term_window):
    buffer = open_term()

    assert buffer.cp == buffer.term._copy_selection
    assert buffer.pst == buffer.term._paste_clipboard
    assert buffer.selall == buffer.term._select_all


def test_opening_runs_the_hooks(term_window):
    seen = []
    state.pcbeforehooks["open-terminal"] = [
        lambda value: seen.append(("before", value))
    ]
    state.pcafterhooks["open-terminal"] = [lambda value: seen.append(("after", value))]

    open_term(["ls", "-l"])

    assert seen == [("before", ["ls", "-l"]), ("after", "ls -l")]


def test_a_terminal_opens_below_by_default_and_beside_on_request(term_window):
    open_term()
    open_term(orient="horizontal")

    splits = {split.orient for split in state.panes._splits()}
    assert splits == {"horizontal", "vertical"}


def test_closing_a_finished_terminal_does_not_ask(term_window, app):
    buffer = open_term()
    buffer.term.running = False

    assert buffer.close() is True

    assert app.dialogs.of_kind("ask") == []


@pytest.mark.parametrize(
    ("answer", "closed"), [(True, True), (False, False), (None, False)]
)
def test_closing_a_running_terminal_asks_first(term_window, app, answer, closed):
    buffer = open_term()
    app.dialogs.answer("ask", answer)

    assert buffer.close() is closed

    assert app.dialogs.messages("ask") == ["Kill active process and close?"]


def test_the_title_says_when_the_process_ended(term_window):
    buffer = open_term(["echo", "x"])

    fire(buffer.term, "<<TerminalProcessEnded>>")

    assert buffer.wanttitle == "*PyNotes Terminal* - echo x - finished"


def test_a_stopped_terminal_closes_its_buffer(term_window):
    keep = state.all_buffers[0]
    buffer = open_term(["echo", "x"])

    buffer.term.running = False
    fire(buffer.term, "<<TerminalStopped>>")

    assert buffer not in state.all_buffers
    assert keep in state.all_buffers


def test_a_blocking_terminal_waits_until_it_is_closed(term_window, monkeypatch):
    waited = []
    monkeypatch.setattr(
        terminal.TerminalBuffer, "wait_window", lambda self: waited.append(self)
    )

    buffer = open_term(["true"], blocking=True)

    assert waited == [buffer]


def test_the_terminals_process_is_started_when_it_is_shown(term_window, monkeypatch):
    started = []
    buffer = open_term(["true"])
    monkeypatch.setattr(buffer.term, "_term_start_process", lambda: started.append(1))

    buffer.term._term_on_map(None)

    assert started == [1]
