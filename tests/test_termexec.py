"""terminal.termexec(), the one-off command runner behind Alt-X termexec."""

import os

import pytest

import state
import terminal


@pytest.fixture(autouse=True)
def no_pycode_hooks(monkeypatch):
    monkeypatch.setattr(state, "pcbeforehooks", {}, raising=False)
    monkeypatch.setattr(state, "pcafterhooks", {}, raising=False)
    monkeypatch.setattr(state, "root", None, raising=False)


def test_returns_standard_output():
    assert terminal.termexec("echo hello") == "hello\n"


def test_returns_standard_error_after_standard_output():
    assert terminal.termexec("echo out; echo err >&2") == "out\nerr\n"


def test_failing_command_returns_its_error_output():
    assert "not found" in terminal.termexec("definitely_not_a_command_xyz")


def test_command_running_too_long_returns_the_timeout_message(monkeypatch):
    run = terminal.subprocess.run
    monkeypatch.setattr(
        terminal.subprocess, "run", lambda *a, **kw: run(*a, **{**kw, "timeout": 0.2})
    )
    assert "timed out" in terminal.termexec("sleep 30")


def test_cd_changes_the_working_directory(tmp_path, monkeypatch):
    monkeypatch.chdir(os.getcwd())
    assert terminal.termexec(f"cd {tmp_path}") == ""
    assert os.getcwd() == str(tmp_path)


def test_cd_to_a_missing_directory_returns_the_error(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = terminal.termexec(f"cd {tmp_path / 'missing'}")
    assert "No such file or directory" in result
    assert os.getcwd() == str(tmp_path)


def test_hooks_run_before_and_after(monkeypatch):
    calls = []
    monkeypatch.setattr(
        terminal.pycode,
        "pcrunhook",
        lambda when, event, command=None: calls.append((when, event, command)),
    )
    terminal.termexec("true")
    assert calls == [("before", "term-exec", "true"), ("after", "term-exec", "true")]
