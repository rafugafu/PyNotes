"""The command-line option parser and the live terminal console.

The console is driven without a terminal: it believes it is on one, its
output goes to a string, its keys come from a queue, and its width is set
with the COLUMNS variable.
"""

import io
import os
import queue
import threading
import time

import pytest

import cli
import state

SPEC = {
    "version": False,
    "changes": False,
    "plugin-list-github": False,
    "plugin-list-installed": False,
    "no-load-pycode": False,
    "no-load-plugins": False,
    "pycode-exec": True,
    "command-exec": True,
    "help": False,
    "plugin-install": True,
    "plugin-remove": True,
    "plugin-describe": True,
    "wait-start": False,
}


def parse(*arguments, spec=SPEC):
    return cli.argparse(dict(spec), list(arguments))


def parse_fails(*arguments, spec=SPEC):
    with pytest.raises(SystemExit) as info:
        cli.argparse(dict(spec), list(arguments))
    assert info.value.code == 1


# ---------------------------------------------------------------------------
# Command-line options
# ---------------------------------------------------------------------------


def test_no_arguments_gives_every_option_off(capsys):
    options, files = parse()

    assert files == []
    assert options == {
        "version": False,
        "changes": False,
        "plugin-list-github": False,
        "plugin-list-installed": False,
        "no-load-pycode": False,
        "no-load-plugins": False,
        "pycode-exec": None,
        "command-exec": None,
        "help": False,
        "plugin-install": None,
        "plugin-remove": None,
        "plugin-describe": None,
        "wait-start": False,
    }


def test_plain_arguments_are_files_to_open():
    assert parse("a.txt", "b.txt")[1] == ["a.txt", "b.txt"]


def test_a_flag_turns_an_option_on():
    options, files = parse("--version")

    assert options["version"] is True and files == []


def test_flags_and_files_can_be_mixed_in_any_order():
    assert parse("a.txt", "--version")[1] == ["a.txt"]
    assert parse("--version", "a.txt")[1] == ["a.txt"]
    options, files = parse("a", "--wait-start", "b", "--no-load-plugins", "c")
    assert files == ["a", "b", "c"]
    assert options["wait-start"] and options["no-load-plugins"]


def test_an_option_with_a_value_takes_the_next_argument():
    options, files = parse("--pycode-exec", "x = 1", "file.txt")

    assert options["pycode-exec"] == "x = 1"
    assert files == ["file.txt"]


def test_an_option_value_can_be_given_with_an_equals_sign():
    assert parse("--pycode-exec=x = 1")[0]["pycode-exec"] == "x = 1"
    assert parse("--command-exec=a=b")[0]["command-exec"] == "a=b"


def test_an_empty_value_is_still_a_value():
    assert parse("--pycode-exec=")[0]["pycode-exec"] == ""


def test_plugin_names_with_spaces():
    assert parse("--plugin-install", "My Plugin")[0]["plugin-install"] == "My Plugin"


def test_a_repeatable_option_collects_every_value(capsys):
    spec = {"include": [True], "flag": False}

    options, files = parse("--include", "a", "--include=b", "--flag", spec=spec)

    assert options == {"include": ["a", "b"], "flag": True}
    assert files == []


def test_a_repeatable_option_is_an_empty_list_when_not_given():
    assert parse(spec={"include": [True]})[0] == {"include": []}


def test_a_repeatable_option_takes_one_value_per_use():
    options, files = parse("--include", "a", "b", spec={"include": [True]})

    assert options["include"] == ["a"] and files == ["b"]


@pytest.mark.parametrize(
    ("arguments", "message"),
    [
        (["--bogus"], 'error: unknown option "--bogus"'),
        (["--bogus=1"], 'error: unknown option "--bogus"'),
        (["--"], 'error: unknown option "--"'),
        (["--version=1"], 'error: option "--version" does not take any argument'),
        (["--version", "--version"], 'error: repeated argument "--version"'),
        (
            ["--pycode-exec", "a", "--pycode-exec", "b"],
            'error: repeated argument "--pycode-exec"',
        ),
        (["--command-exec"], 'error: unspecified option "command-exec"'),
        (
            ["--command-exec", "--version"],
            'unexpected "--version" after option "--command-exec"',
        ),
    ],
)
def test_invalid_usage_prints_an_error_and_exits(capsys, arguments, message):
    parse_fails(*arguments)

    assert message in capsys.readouterr().out


def test_a_single_dash_is_a_file_not_an_option():
    assert parse("-v")[1] == ["-v"]


def test_help_texts_describe_every_option():
    for option in SPEC:
        if option not in ("help",):
            assert f"--{option}" in cli.claht, option


def test_console_help_lists_the_console_commands():
    for name in (
        "start",
        "command-exec",
        "pycode-eval",
        "extra-pycode",
        "open-file",
        "exit",
        "kill",
        "run",
        "clear",
        "help",
    ):
        assert name in cli.clcht, name


# ---------------------------------------------------------------------------
# The console
# ---------------------------------------------------------------------------


class Keys:
    def __init__(self):
        self.queue = queue.Queue()

    def type(self, text):
        for character in text:
            self.queue.put(character)

    def get(self):
        key = self.queue.get()
        if key is None:
            threading.Event().wait()  # the console is finished with: sleep for good
        return key


@pytest.fixture
def terminal_output(monkeypatch):
    """The console on a pretend terminal 40 columns wide."""
    keys = Keys()
    output = io.StringIO()
    monkeypatch.setattr(cli, "CONSOLE_IS_TTY", True)
    monkeypatch.setattr(cli, "get_key", keys.get)
    monkeypatch.setenv("COLUMNS", "40")
    monkeypatch.setattr(state, "stdout", output, raising=False)
    monkeypatch.setattr(state, "stderr", output, raising=False)
    monkeypatch.setattr(state, "options", {"pycode-exec": None}, raising=False)
    monkeypatch.setattr(state, "files_to_open", [], raising=False)
    monkeypatch.setattr(state, "started", threading.Event(), raising=False)
    yield SimpleKeys(keys, output)
    keys.queue.put(None)


class SimpleKeys:
    def __init__(self, keys, output):
        self.keys = keys
        self.output = output

    def type(self, text):
        self.keys.type(text)

    def text(self):
        return self.output.getvalue()


def new_console():
    consoleq = queue.Queue()
    return cli.Console(consoleq), consoleq


def test_the_console_starts_with_a_banner(terminal_output):
    new_console()

    assert "PyNotes terminal console. PyNotes v" in terminal_output.text()
    assert terminal_output.text().startswith("\x1b[H\x1b[2J")


def test_the_banner_lists_files_and_options(terminal_output):
    state.files_to_open.append("a.txt")
    state.options.update(
        {"wait-start": True, "pycode-exec": "x" * 40, "command-exec": "short\nline"}
    )

    new_console()

    text = terminal_output.text()
    assert "Opening Files" in text and "a.txt" in text
    assert "--wait-start" in text
    assert "--pycode-exec \x1b[0m" not in text
    assert "x" * 15 + "\x1b[1m..." in text
    assert "--command-exec shortline" in text


def test_without_a_terminal_the_console_prints_nothing(monkeypatch):
    output = io.StringIO()
    monkeypatch.setattr(cli, "CONSOLE_IS_TTY", False)
    monkeypatch.setattr(state, "stdout", output, raising=False)
    monkeypatch.setattr(state, "options", {}, raising=False)
    monkeypatch.setattr(state, "files_to_open", [], raising=False)

    console = cli.Console(queue.Queue())
    console.outpt("hello")

    assert output.getvalue() == ""


def test_output_returns_the_cursor_after_each_line(terminal_output):
    console, _ = new_console()
    terminal_output.output.truncate(0)
    terminal_output.output.seek(0)

    console.outpt("one\ntwo")

    assert terminal_output.text() == "one\n\rtwo\n\r"


def test_output_without_a_line_end(terminal_output):
    console, _ = new_console()
    terminal_output.output.truncate(0)
    terminal_output.output.seek(0)

    console.outpt("x", end="")

    assert terminal_output.text() == "x"


@pytest.mark.parametrize(
    ("rows", "expected"),
    [(0, ""), (3, "\x1b[3B"), (-2, "\x1b[2A")],
)
def test_moving_rows(rows, expected):
    assert cli.Console._move_rows(rows) == expected


def test_moving_to_a_row_and_column(terminal_output):
    console, _ = new_console()

    assert console._move_to(0, 0) == "\r"
    assert console._move_to(2, 5) == "\r\x1b[2B\x1b[5C"
    assert console._move_to(-1, 0) == "\r\x1b[1A"


def test_the_terminal_width_comes_from_the_environment(terminal_output):
    console, _ = new_console()

    assert console._get_terminal_width() == 40


def test_input_rows_count_the_prompt_and_wrapping(terminal_output):
    console, _ = new_console()
    console.curpromptlens["command"] = 2

    assert console._input_rows("command", 0) == 1
    assert console._input_rows("command", 37) == 1
    assert console._input_rows("command", 38) == 2
    assert console._input_rows("command", 78) == 3


def test_input_positions_wrap_at_the_width(terminal_output):
    console, _ = new_console()
    console.curpromptlens["command"] = 2

    assert console._input_position("command", 0) == (0, 2)
    assert console._input_position("command", 38) == (1, 0)
    assert console._input_position("command", 45) == (1, 7)


def test_rows_below_an_input(terminal_output):
    console, _ = new_console()
    console.curpromptlens["command"] = 2

    assert console._rows_below_input("command") == 0
    console.n = 2
    assert console._rows_below_input("dialog") == 2 + 1


def test_erasing_the_last_entered_line(terminal_output):
    console, _ = new_console()
    console.curlastrows["command"] = 2

    assert console._erase_last_input_string("command") == "\r\x1b[A\x1b[K\x1b[A\x1b[K"


def test_moving_back_to_the_first_row_of_the_prompt(terminal_output):
    console, _ = new_console()
    console.n = 2
    console.curn["command"] = 1

    assert console._moveback_string() == "\x1b[3A"


def test_scrolling_ahead_makes_room_for_a_dialog(terminal_output):
    console, _ = new_console()

    assert console._scroll_ahead_string(2) == "\x1bD\x1bD\x1b[A\x1b[A"


def test_restoring_after_a_dialog(terminal_output):
    console, _ = new_console()
    console.cursors["command"] = 3
    console.curpromptlens["command"] = 2

    assert console._dialog_restore_string(4) == "\r\x1b[5C"
    console.helping = True
    console.curlastrows["dialog"] = 2
    assert console._dialog_restore_string(4) == "\x1b8\x1b[5B"


def wait_until(condition, what, seconds=5):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        if condition():
            return
        time.sleep(0.005)
    raise AssertionError(f"timed out waiting for {what}")


def read_line(console, keys, typed, prompt="> ", **keywords):
    """Ask the console for a line while the keys are typed."""
    results = []
    thread = threading.Thread(
        target=lambda: results.append(console.inpt(prompt, **keywords)), daemon=True
    )
    thread.start()
    wait_until(lambda: console.curdoneevents, "the prompt")
    keys.type(typed)
    thread.join(5)
    assert not thread.is_alive(), "no line was entered"
    return results[0]


def test_reading_a_line(terminal_output):
    console, _ = new_console()

    assert read_line(console, terminal_output, "hello\r") == "hello"
    assert "hello" in terminal_output.text()


def test_backspace_deletes_the_character_before_the_cursor(terminal_output):
    console, _ = new_console()

    assert read_line(console, terminal_output, "abc\x7f\x7fx\r") == "ax"
    assert read_line(console, terminal_output, "\x7fq\x08\r") == ""


def test_the_cursor_keys_edit_in_the_middle(terminal_output):
    console, _ = new_console()

    typed = "ac\x1b[Db\r"
    assert read_line(console, terminal_output, typed) == "abc"
    typed = "bc\x1b[Aa\r"
    assert read_line(console, terminal_output, typed) == "abc"
    typed = "ab\x1b[A\x1b[B!\r"
    assert read_line(console, terminal_output, typed) == "ab!"
    typed = "a\x1b[C\x1b[Db\x1b[Cc\r"
    assert read_line(console, terminal_output, typed) == "bac"


def test_delete_removes_the_character_under_the_cursor(terminal_output):
    console, _ = new_console()

    typed = "abc\x1b[A\x1b[3~\x1b[3~\r"
    assert read_line(console, terminal_output, typed) == "c"


def test_tab_is_ignored(terminal_output):
    console, _ = new_console()

    assert read_line(console, terminal_output, "a\tb\r") == "ab"


def test_a_line_longer_than_the_terminal_wraps(terminal_output):
    console, _ = new_console()
    line = "x" * 100

    assert read_line(console, terminal_output, line + "\r") == line


def test_editing_a_wrapped_line(terminal_output):
    console, _ = new_console()
    line = "y" * 60

    typed = line + "\x1b[A" + "z" + "\x7f" + "\x1b[B" + "w\r"
    assert read_line(console, terminal_output, typed) == line + "w"


def test_input_without_echo_does_not_show_the_text(terminal_output):
    console, _ = new_console()
    terminal_output.output.truncate(0)
    terminal_output.output.seek(0)

    assert read_line(console, terminal_output, "secret\r", echo=False) == "secret"
    assert "secret" not in terminal_output.text()


def test_a_cancelled_prompt_returns_nothing(terminal_output):
    console, _ = new_console()
    cancel = threading.Event()
    results = []
    thread = threading.Thread(
        target=lambda: results.append(console.inpt("> ", cancel_event=cancel)),
        daemon=True,
    )
    thread.start()
    wait_until(lambda: console.curdoneevents, "the prompt")
    terminal_output.type("half")
    wait_until(lambda: console.curinput["command"] == "half", "the typed text")

    cancel.set()
    thread.join(5)

    assert results == [None]
    assert console.curinput["command"] == ""


def test_the_dialog_input_is_separate_from_the_command_input(terminal_output):
    console, _ = new_console()

    assert read_line(console, terminal_output, "7\r", forinput="dialog") == "7"
    assert console.curactiveinput == "command"


def test_a_status_message_is_shown_above_the_prompt(terminal_output):
    console, _ = new_console()
    terminal_output.output.truncate(0)
    terminal_output.output.seek(0)

    console.show("  saved the file  ")
    console.show("   ")

    text = terminal_output.text()
    assert "message: \x1b[3msaved the file" in text
    assert text.count("message:") == 1


def test_a_long_status_message_wraps(terminal_output):
    console, _ = new_console()
    terminal_output.output.truncate(0)
    terminal_output.output.seek(0)

    console.show("word " * 30)

    assert terminal_output.text().count("\x1b[L") >= 4


def test_status_messages_while_help_is_shown_go_to_the_top(terminal_output):
    console, _ = new_console()
    console.helping = True
    terminal_output.output.truncate(0)
    terminal_output.output.seek(0)

    console.show("hello")

    assert "\x1b[H" in terminal_output.text()


@pytest.mark.parametrize("color", ["41m", "43m", "100m"])
def test_a_dialog_is_drawn_with_its_title_and_text(terminal_output, color):
    console, _ = new_console()
    terminal_output.output.truncate(0)
    terminal_output.output.seek(0)

    console.dialog("Title", "Some message text", color)

    text = terminal_output.text()
    assert "Title" in text and "Some message text" in text
    assert f"\x1b[{color}" in text


def test_a_very_long_dialog_title_is_shortened(terminal_output):
    console, _ = new_console()
    terminal_output.output.truncate(0)
    terminal_output.output.seek(0)

    console.dialog("T" * 100, "message")

    assert "T" * 100 not in terminal_output.text()
    assert "..." in terminal_output.text()


def run_ask(console, keys, typed, options=("Yes", "No"), **keywords):
    results = []
    thread = threading.Thread(
        target=lambda: results.append(
            console.ask("Question", "Are you sure?", list(options), **keywords)
        ),
        daemon=True,
    )
    thread.start()
    wait_until(lambda: console.curdoneevents, "the dialog prompt")
    keys.type(typed)
    thread.join(5)
    assert not thread.is_alive()
    return results[0]


def test_ask_returns_the_number_chosen(terminal_output):
    console, _ = new_console()

    assert run_ask(console, terminal_output, "2\r") == 2
    assert "1. Yes" in terminal_output.text() and "2. No" in terminal_output.text()
    assert "select (1/2):" in terminal_output.text()


def test_ask_asks_again_after_an_invalid_answer(terminal_output):
    console, _ = new_console()
    results = []
    thread = threading.Thread(
        target=lambda: results.append(console.ask("Q", "Sure?", ["Yes", "No"])),
        daemon=True,
    )
    thread.start()
    wait_until(lambda: console.curdoneevents, "the first prompt")

    terminal_output.type("x\r")
    wait_until(lambda: terminal_output.text().count("[invalid input]") == 1, "a re-ask")
    terminal_output.type("9\r")
    wait_until(lambda: terminal_output.text().count("[invalid input]") == 2, "a re-ask")
    terminal_output.type("1\r")
    thread.join(5)

    assert results == [1]


def test_ask_with_many_options_wraps_them(terminal_output):
    console, _ = new_console()
    options = [f"option number {n}" for n in range(1, 7)]

    assert run_ask(console, terminal_output, "6\r", options=options) == 6
    assert "6. option number 6" in terminal_output.text()


def test_ask_can_be_cancelled(terminal_output):
    console, _ = new_console()
    cancel = threading.Event()
    results = []
    thread = threading.Thread(
        target=lambda: results.append(
            console.ask("Q", "Sure?", ["Yes", "No"], cancel_event=cancel)
        ),
        daemon=True,
    )
    thread.start()
    wait_until(lambda: console.curdoneevents, "the prompt")

    cancel.set()
    thread.join(5)

    assert results == [None]


def test_prompt_returns_the_line_typed(terminal_output):
    console, _ = new_console()
    results = []
    thread = threading.Thread(
        target=lambda: results.append(console.prompt("Name", "Your name?")),
        daemon=True,
    )
    thread.start()
    wait_until(lambda: console.curdoneevents, "the prompt")

    terminal_output.type("Ada\r")
    thread.join(5)

    assert results == ["Ada"]
    assert "Your name?" in terminal_output.text()


def test_prompt_can_be_cancelled(terminal_output):
    console, _ = new_console()
    cancel = threading.Event()
    results = []
    thread = threading.Thread(
        target=lambda: results.append(
            console.prompt("Name", "Your name?", cancel_event=cancel)
        ),
        daemon=True,
    )
    thread.start()
    wait_until(lambda: console.curdoneevents, "the prompt")

    cancel.set()
    thread.join(5)

    assert results == [None]


# ---------------------------------------------------------------------------
# The console's commands
# ---------------------------------------------------------------------------


class EndOfScript(Exception):
    pass


@pytest.fixture
def scripted(terminal_output, monkeypatch):
    """A console whose prompt answers come from a list, and which stops
    when the list is used up."""
    console, consoleq = new_console()
    answers = []
    prompts = []

    def inpt(prompt, echo=True, cancel_event=None, forinput=None):
        prompts.append(prompt)
        if not answers:
            raise EndOfScript
        return answers.pop(0)

    monkeypatch.setattr(console, "inpt", inpt)
    monkeypatch.setattr(cli, "set_raw_mode", lambda: None)
    monkeypatch.setattr(cli, "unset_raw_mode", lambda: None)

    def run(*lines):
        answers.extend(lines)
        with pytest.raises(EndOfScript):
            console.loop()
        return terminal_output.text()

    console.run = run
    console.prompts = prompts
    console.queue = consoleq
    console.answers = answers
    return console


def queued(console):
    items = []
    while not console.queue.empty():
        items.append(console.queue.get())
    return items


def test_start_starts_pynotes_once(scripted):
    text = scripted.run("start", "start")

    assert state.started.is_set()
    assert "starting pynotes." in text
    assert "pynotes has already started" in text


def test_command_exec_before_and_after_start(scripted):
    text = scripted.run("command-exec save", "start", "command-exec undo")

    assert queued(scripted) == [("command-exec", "save"), ("command-exec", "undo")]
    assert "will execute alt-x command" in text
    assert "executing alt-x command" in text


def test_pycode_eval_before_and_after_start(scripted):
    text = scripted.run("pycode-eval x = 1", "start", "pycode-eval y = 2")

    assert queued(scripted) == [("pycode-eval", "x = 1"), ("pycode-eval", "y = 2")]
    assert "will evaluate pycode" in text
    assert "evaluating pycode expression" in text


@pytest.mark.parametrize("name", ["command-exec", "pycode-eval", "open-file"])
def test_commands_without_what_they_need_are_cancelled(scripted, name):
    text = scripted.run(name, "") if name == "open-file" else scripted.run(name)

    assert "cancelled." in text
    assert queued(scripted) == []


def test_extra_pycode_is_collected_until_done(scripted):
    state.options["pycode-exec"] = None

    text = scripted.run("extra-pycode", "x = 1", "y = 2", "DONE")

    assert state.options["pycode-exec"] == "\nx = 1\ny = 2"
    assert "added extra pycode" in text


def test_extra_pycode_is_appended_to_existing_pycode(scripted):
    state.options["pycode-exec"] = "a = 0"

    scripted.run("extra-pycode", "b = 1", "DONE")

    assert state.options["pycode-exec"] == "a = 0\n;\nb = 1"


def test_extra_pycode_can_be_cancelled(scripted):
    state.options["pycode-exec"] = None

    text = scripted.run("extra-pycode", "x = 1", "CANCEL")

    assert state.options["pycode-exec"] is None
    assert "cancelled." in text


def test_extra_pycode_takes_no_input_and_only_before_start(scripted):
    text = scripted.run("extra-pycode junk", "start", "extra-pycode")

    assert "input given to" in text
    assert "pynotes has already started" in text


def test_open_file_before_start_remembers_the_file(scripted, tmp_path):
    path = tmp_path / "wanted.txt"

    text = scripted.run(f"open-file {path}")

    assert state.files_to_open == [str(path)]
    assert "does not exist, creating file" in text
    assert "will be opened on pynotes start" in text


def test_open_file_after_start_queues_it(scripted, tmp_path):
    path = tmp_path / "wanted.txt"
    path.write_text("x")

    text = scripted.run("start", f"open-file {path}")

    assert queued(scripted) == [("open-file", str(path))]
    assert "opening file" in text
    assert "does not exist" not in text


def test_open_file_asks_for_a_name(scripted, tmp_path):
    path = tmp_path / "asked.txt"
    path.write_text("x")

    scripted.run("start", "open-file", str(path))

    assert queued(scripted) == [("open-file", str(path))]
    assert "file to open: " in scripted.prompts


def test_open_file_expands_the_home_directory(scripted):
    scripted.run("start", "open-file ~/some-file-that-is-not-there.txt")

    ((_, path),) = queued(scripted)
    assert path == os.path.expanduser("~/some-file-that-is-not-there.txt")


def test_exit_after_start_queues_a_close(scripted):
    text = scripted.run("start", "exit", "close")

    assert queued(scripted) == [("close",), ("close",)]
    assert text.count("closing pynotes.") == 2


def test_exit_before_start_ends_the_process(scripted, monkeypatch):
    class Exited(Exception):
        pass

    def exit_now(code):
        raise Exited(code)

    monkeypatch.setattr(cli.os, "_exit", exit_now)
    scripted.answers.append("exit")

    with pytest.raises(Exited):
        scripted.loop()


def test_exit_takes_no_input(scripted):
    text = scripted.run("start", "exit now")

    assert "input given to" in text
    assert queued(scripted) == []


def test_kill_asks_for_confirmation(scripted, monkeypatch):
    class Exited(Exception):
        pass

    monkeypatch.setattr(cli.os, "_exit", lambda code: (_ for _ in ()).throw(Exited))
    scripted.answers.extend(["kill", "n"])
    with pytest.raises(EndOfScript):
        scripted.loop()

    scripted.answers.extend(["kill", "y"])
    with pytest.raises(Exited):
        scripted.loop()


def test_kill_asks_again_after_invalid_answers(scripted):
    text = scripted.run("kill", "maybe", "perhaps", "n")

    assert any("invalid input (2/3)" in prompt for prompt in scripted.prompts)
    assert any("invalid input (3/3)" in prompt for prompt in scripted.prompts)
    assert "cancelled." in text


def test_kill_gives_up_after_three_invalid_answers(scripted):
    text = scripted.run("kill", "maybe", "perhaps", "what")

    assert "cancelled." in text


def test_kill_takes_no_input(scripted):
    assert "input given to" in scripted.run("kill now")


def test_run_runs_a_shell_command(scripted, tmp_path, monkeypatch):
    out = open(tmp_path / "out", "w+")
    monkeypatch.setattr(state, "stdout", out)
    monkeypatch.setattr(state, "stderr", out)

    scripted.run("run echo from the console")
    out.flush()

    assert "from the console" in (tmp_path / "out").read_text()


def test_run_asks_for_a_command_and_can_be_cancelled(scripted):
    text = scripted.run("run", "")

    assert "command to run: " in scripted.prompts
    assert "cancelled." in text


def test_clear_clears_the_screen(scripted):
    text = scripted.run("clear")

    assert "\x1b[H\x1b[2J\x1b[3J" in text


def test_help_shows_the_console_help(scripted):
    text = scripted.run("help", "")

    assert "Console:" in text
    assert "\x1b[?1049h" in text and "\x1b[?1049l" in text
    assert "help text shown" in text


@pytest.mark.parametrize("name", ["clear", "help"])
def test_clear_and_help_take_no_input(scripted, name):
    assert "input given to" in scripted.run(f"{name} junk")


def test_an_unknown_console_command(scripted):
    assert "invalid command" in scripted.run("frobnicate")


def test_blank_lines_are_ignored(scripted):
    text = scripted.run("", "   ", "start")

    assert "invalid command" not in text
    assert state.started.is_set()


def test_closing_the_console_clears_the_screen(terminal_output):
    cli.close()

    assert "\x1b[H\x1b[2J" in terminal_output.text()


def test_closing_without_a_terminal_does_nothing(monkeypatch):
    output = io.StringIO()
    monkeypatch.setattr(cli, "CONSOLE_IS_TTY", False)
    monkeypatch.setattr(state, "stdout", output, raising=False)

    cli.close()

    assert output.getvalue() == ""


def test_starting_the_console_runs_its_loop_only_on_a_terminal(monkeypatch):
    ran = []
    monkeypatch.setattr(cli.Console, "loop", lambda self: ran.append(self))
    monkeypatch.setattr(state, "options", {}, raising=False)
    monkeypatch.setattr(state, "files_to_open", [], raising=False)

    monkeypatch.setattr(cli, "CONSOLE_IS_TTY", False)
    cli.start_console(queue.Queue())
    assert ran == []
    assert isinstance(state.console, cli.Console)
