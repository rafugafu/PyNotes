"""The Python Shell buffer: a real Python REPL running in a Terminal over a
PTY, with the highlighting of what is typed at its prompt, the carry-over of
what earlier statements defined, and its Clear and Restart buttons.

The buffer lives in the withdrawn root and is laid out with place(), so
nothing is ever shown. The REPL is the basic (non-curses) one, so the
transcript looks the same on every Python version.
"""

import sys
import time

import pytest

import pythonshell
import state
import terminal as terminal_module
import window
from terminal_helpers import relayout

pytestmark = pytest.mark.display

PYTHON_HIGHLIGHT_THEME = {
    "python:keywords": "foreground = '#7C3AED'",
    "python:inbuilt": "foreground = '#D97706'",
    "python:comments": "foreground = '#6B7280'",
    "python:strings": "foreground = '#15803D'",
    "python:variable_names": "foreground = '#DC2626'",
    "python:function_names": "foreground = '#2563EB'",
    "python:class_names": "foreground = '#0891B2'",
    "python:class_instances": "foreground = '#155E75'",
    "python:function_arguments": "foreground = '#0F766E'",
    "python:operators": "foreground = '#111111'",
    "python:module_names": "foreground = '#0369A1'",
}
WAIT_SECONDS = 10


def wait_for(root, condition, what):
    """Run the event loop until condition() holds."""
    deadline = time.monotonic() + WAIT_SECONDS
    while time.monotonic() < deadline:
        root.update()
        if condition():
            return
        time.sleep(0.01)
    raise AssertionError(f"timed out waiting for {what}")


def transcript(shell):
    return shell.shellcmd.get("1.0", "end")


def tagged_text(shell, tag):
    """The texts the tag covers in the transcript."""
    ranges = [str(index) for index in shell.shellcmd.tag_ranges(tag)]
    return [
        shell.shellcmd.get(start, end) for start, end in zip(ranges[0::2], ranges[1::2])
    ]


def at_prompt(shell):
    return transcript(shell).rstrip().endswith(">>>")


@pytest.fixture
def shell(tk_root, monkeypatch):
    """A running Python Shell buffer, waiting at its first prompt."""
    monkeypatch.setenv("PYTHON_BASIC_REPL", "1")
    monkeypatch.setenv("PYTHON_COLORS", "0")
    monkeypatch.setenv("NO_COLOR", "1")
    monkeypatch.setattr(state, "theme", dict(PYTHON_HIGHLIGHT_THEME), raising=False)
    monkeypatch.setattr(state, "defs", [None, None, "monospace"], raising=False)
    monkeypatch.setattr(state, "pythonexecutable", sys.executable, raising=False)
    monkeypatch.setattr(state, "all_pythonshell_menus", {}, raising=False)
    monkeypatch.setattr(state, "all_buffers", [], raising=False)
    monkeypatch.setattr(state, "pcbeforehooks", {}, raising=False)
    monkeypatch.setattr(state, "pcafterhooks", {}, raising=False)
    monkeypatch.setattr(
        state,
        "_PYTHON_SHELL_HL_SKIP_REMOVE_TAGS",
        {"sel", "prompt", "wrapcont"},
        raising=False,
    )
    monkeypatch.setattr(state, "skiptagspythonshell", {}, raising=False)
    monkeypatch.setattr(window, "settitle", lambda *args, **kwargs: None)
    buffer = pythonshell.PythonShellBuffer(tk_root)
    state.all_buffers.append(buffer)
    buffer.place(x=0, y=0, width=700, height=400)
    relayout(tk_root, buffer)
    buffer.shellcmd._term_on_map(None)
    wait_for(tk_root, lambda: at_prompt(buffer), "the first prompt")
    yield buffer
    buffer.shellcmd._terminate_process()
    buffer.destroy()


def type_text(shell, tk_root, text):
    """Type text at the prompt as the terminal would send it, and wait until
    the REPL has echoed all of it."""
    before = transcript(shell)
    shell.shellcmd._write(text.encode())
    wait_for(
        tk_root,
        lambda: transcript(shell) != before
        and text.replace("\r", "") in transcript(shell).replace("\n", "")
        or "\r" in text,
        f"{text!r} to be echoed",
    )


def run_statement(shell, tk_root, statement):
    """Run one single-line statement and wait for the next prompt."""
    count = transcript(shell).count(">>>")
    shell.shellcmd._write(statement.encode() + b"\r")
    wait_for(
        tk_root,
        lambda: at_prompt(shell) and transcript(shell).count(">>>") > count,
        f"the prompt after {statement!r}",
    )


def highlighted(shell, tk_root):
    shell.hapyshell()
    tk_root.update()


# ---------------------------------------------------------------------------
# The REPL
# ---------------------------------------------------------------------------


def test_the_shell_runs_a_python_repl(shell):
    assert shell.shellcmd.running
    assert transcript(shell).startswith("Python 3")
    assert shell.hmode == "python"


def test_a_statement_is_run_and_its_output_shown(shell, tk_root):
    run_statement(shell, tk_root, "print(6 * 7)")

    assert "\n42\n" in transcript(shell)


def test_the_session_remembers_earlier_statements(shell, tk_root):
    run_statement(shell, tk_root, "answer = 6 * 7")
    run_statement(shell, tk_root, "print(answer)")

    assert "\n42\n" in transcript(shell)


def test_errors_are_shown_and_the_prompt_comes_back(shell, tk_root):
    run_statement(shell, tk_root, "1 / 0")

    assert "ZeroDivisionError" in transcript(shell)
    assert at_prompt(shell)


def test_the_shell_is_not_in_color_mode(shell):
    assert shell.shellcmd.nocolor is True


def test_prompts_are_tagged(shell, tk_root):
    run_statement(shell, tk_root, "x = 1")

    assert tagged_text(shell, "prompt") == [">>> ", ">>> "]


def test_a_multi_line_statement_has_continuation_prompts(shell, tk_root):
    shell.shellcmd._write(b"def f(a):\r")
    wait_for(tk_root, lambda: "..." in transcript(shell), "a continuation prompt")

    assert "... " in tagged_text(shell, "prompt")


# ---------------------------------------------------------------------------
# Highlighting of what is typed
# ---------------------------------------------------------------------------


def test_keywords_at_the_prompt_are_highlighted(shell, tk_root):
    type_text(shell, tk_root, "def f(a): return a")
    highlighted(shell, tk_root)

    assert tagged_text(shell, "hpa") == ["def", "return"]
    assert tagged_text(shell, "hpf") == ["f"]
    assert tagged_text(shell, "hpfa") == ["a", "a"]


def test_strings_comments_and_operators_at_the_prompt_are_highlighted(shell, tk_root):
    type_text(shell, tk_root, 'x = "s" + t  # c')
    highlighted(shell, tk_root)

    assert tagged_text(shell, "hpd") == ['"s"']
    assert tagged_text(shell, "hpc") == ["# c"]
    assert tagged_text(shell, "hpo") == ["=", "+"]
    assert tagged_text(shell, "hpv") == ["x"]


def test_builtins_at_the_prompt_are_highlighted(shell, tk_root):
    type_text(shell, tk_root, "print(len([]))")
    highlighted(shell, tk_root)

    assert tagged_text(shell, "hpb") == ["print", "len"]


def test_the_output_of_a_statement_is_not_highlighted(shell, tk_root):
    run_statement(shell, tk_root, "print('if else def')")
    highlighted(shell, tk_root)

    assert "if" not in tagged_text(shell, "hpa")
    assert "else" not in tagged_text(shell, "hpa")


def test_a_name_defined_by_an_earlier_statement_is_highlighted_when_used(
    shell, tk_root
):
    run_statement(shell, tk_root, "items = []")
    type_text(shell, tk_root, "items.append(1)")
    highlighted(shell, tk_root)

    assert tagged_text(shell, "hpv") == ["items"]
    assert tagged_text(shell, "hpf") == ["append"]


def test_a_class_defined_earlier_makes_its_instances_instances(shell, tk_root):
    shell.shellcmd._write(b"class K:\r")
    wait_for(tk_root, lambda: "..." in transcript(shell), "a continuation prompt")
    shell.shellcmd._write(b"    def m(self): pass\r\r")
    wait_for(tk_root, lambda: at_prompt(shell), "the prompt after the class")
    run_statement(shell, tk_root, "k = K()")
    type_text(shell, tk_root, "k.m()")
    highlighted(shell, tk_root)

    assert tagged_text(shell, "hpi") == ["k"]
    assert tagged_text(shell, "hpf") == ["m"]


def test_the_session_remembers_what_executed_statements_defined(shell, tk_root):
    run_statement(shell, tk_root, "number = 1")
    highlighted(shell, tk_root)

    assert "number" in shell._pyshell_session_names


def test_highlighting_does_not_run_again_while_it_is_running(
    shell, tk_root, monkeypatch
):
    calls = []
    monkeypatch.setattr(shell, "_hapyshell_body", lambda: calls.append(True))

    shell._hapyshell_running[0] = True
    shell.hapyshell()
    assert calls == []

    shell._hapyshell_running[0] = False
    shell.hapyshell()
    assert calls == [True]
    assert shell._hapyshell_running[0] is False


def test_the_scope_analysis_is_reused_while_the_text_does_not_change(
    shell, tk_root, monkeypatch
):
    type_text(shell, tk_root, "x = 1")
    highlighted(shell, tk_root)
    first = shell._pyshell_cached_scope_result
    scans = []
    real_build = pythonshell.python_scope_build._python_build_scopes
    monkeypatch.setattr(
        pythonshell.python_scope_build,
        "_python_build_scopes",
        lambda *args, **kwargs: scans.append(True) or real_build(*args, **kwargs),
    )

    highlighted(shell, tk_root)
    assert scans == []
    assert shell._pyshell_cached_scope_result is first

    type_text(shell, tk_root, "0")
    highlighted(shell, tk_root)
    assert scans == [True]


def test_a_theme_change_recolors_the_highlight_tags(shell, tk_root):
    assert shell.shellcmd.tag_cget("hpa", "foreground") == "#7C3AED"
    state.theme["python:keywords"] = "foreground = '#112233'"

    pythonshell._init_pythonshell_hl_tags()

    assert shell.shellcmd.tag_cget("hpa", "foreground") == "#112233"


# ---------------------------------------------------------------------------
# Clear and Restart
# ---------------------------------------------------------------------------


def buttons(shell):
    return {
        button.cget("text"): button
        for button in shell._shellbuttons.winfo_children()
        if hasattr(button, "invoke")
    }


def test_the_toolbar_has_clear_and_restart_buttons(shell):
    assert set(buttons(shell)) == {"Clear Shell", "Restart Shell"}


def test_clear_shell_wipes_the_transcript_but_keeps_the_session(shell, tk_root):
    run_statement(shell, tk_root, "kept = 5")

    buttons(shell)["Clear Shell"].invoke()
    wait_for(
        tk_root, lambda: "kept = 5" not in transcript(shell), "the transcript to clear"
    )
    wait_for(tk_root, lambda: at_prompt(shell), "a fresh prompt")
    run_statement(shell, tk_root, "print(kept)")

    assert "\n5\n" in transcript(shell)


def test_restart_shell_starts_a_fresh_interpreter_and_forgets_the_session(
    shell, tk_root
):
    run_statement(shell, tk_root, "gone = 5")
    highlighted(shell, tk_root)
    assert "gone" in shell._pyshell_session_names

    buttons(shell)["Restart Shell"].invoke()
    wait_for(
        tk_root, lambda: "gone = 5" not in transcript(shell), "the transcript to clear"
    )
    wait_for(tk_root, lambda: at_prompt(shell), "the new prompt")

    assert shell._pyshell_session_names == {}
    assert shell._pyshell_session_types == {}
    assert "gone" not in shell._pyshell_last_scan_key[0]
    run_statement(shell, tk_root, "print(gone)")
    assert "NameError" in transcript(shell)


def test_leaving_the_interpreter_restarts_the_shell(shell, tk_root):
    run_statement(shell, tk_root, "left = 1")
    shell.shellcmd._write(b"exit()\r")

    wait_for(
        tk_root, lambda: "left = 1" not in transcript(shell), "the shell to restart"
    )
    wait_for(tk_root, lambda: at_prompt(shell), "the new prompt")

    assert shell.shellcmd.running
