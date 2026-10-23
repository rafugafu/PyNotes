"""The Help windows: that each opens, shows what it should, and that the
help lists every command PyNotes has. The PyCode help also has a testing tab
that translates PyCode to Python live."""

import re

import canvastk as ctk
import pytest

import command
import help
import init
import pycode
import state
import utils
from test_editor import editor, wait_for_message
from test_utils import console_messages, run_binding  # noqa: F401

pytestmark = pytest.mark.display


def descendants(widget):
    for child in widget.winfo_children():
        yield child
        yield from descendants(child)


def all_text(top):
    pieces = []
    for widget in descendants(top):
        if isinstance(widget, ctk.Label):
            pieces.append(widget.cget("text"))
        elif isinstance(widget, ctk.Textbox):
            pieces.append(widget.get("1.0", "end-1c"))
        elif isinstance(widget, ctk.Button):
            pieces.append(widget.cget("text"))
    return "\n".join(str(piece) for piece in pieces)


@pytest.fixture
def helping(app, tk_root, editor, monkeypatch, console_messages):
    """The Help windows, opened but hidden."""
    windows = []
    original = type(tk_root).subwin

    def subwin(*arguments, **keywords):
        top = original(tk_root, *arguments, **keywords)
        top.withdraw()
        windows.append(top)
        return top

    monkeypatch.setattr(tk_root, "subwin", subwin, raising=False)
    helping_ = type("Helping", (), {})()
    helping_.windows = windows
    helping_.last = lambda: windows[-1]
    yield helping_
    for top in windows:
        if top.winfo_exists():
            top.destroy()


# ---------------------------------------------------------------------------
# About, changes, email, plugins
# ---------------------------------------------------------------------------


def test_about_shows_the_version_and_a_close_button(helping, tk_root):
    help.abt()

    top = helping.last()
    text = all_text(top)
    assert top.title() == "About PyNotes"
    assert f"PyNotes v{init.v}" in text
    assert "Emacs-like text editor" in text
    wait_for_message(tk_root, "open about pynotes")


def test_about_closes_with_its_button_and_keys(helping):
    help.abt()
    top = helping.last()
    next(
        w
        for w in descendants(top)
        if isinstance(w, ctk.Button) and w.cget("text") == "Close"
    ).invoke()
    assert not top.winfo_exists()

    help.abt()
    top = helping.last()
    run_binding(top, "<Escape>")
    assert not top.winfo_exists()
    help.abt()
    top = helping.last()
    run_binding(top, "<Return>")
    assert not top.winfo_exists()


def test_changes_shows_the_changelog(helping, tk_root):
    state.changestr = "1. First change\n\n2. Second change"

    help.changes()

    top = helping.last()
    assert top.title() == f"Changes in v{init.v}"
    box = next(w for w in descendants(top) if isinstance(w, ctk.Textbox))
    assert box.get("1.0", "end-1c") == state.changestr
    assert str(box.cget("state")) == "disabled"
    wait_for_message(tk_root, "show pynotes changes")


def test_changes_closes_with_escape(helping):
    state.changestr = "x"
    help.changes()
    top = helping.last()

    run_binding(top, "<Escape>")

    assert not top.winfo_exists()


def test_email_help_has_setup_and_dictionary_tabs(helping, tk_root):
    help.hemail()

    text = all_text(helping.last())
    assert helping.last().title() == "Help with Email"
    assert "sendemail" in text and "sendmail" in text
    assert "one word in each line" in text
    wait_for_message(tk_root, "open email help")


def test_plugin_help_gives_the_steps_and_the_directory(helping, app, monkeypatch):
    opened = []
    monkeypatch.setattr(utils, "dp", lambda: opened.append("dp"))
    monkeypatch.setattr(utils, "op", lambda: opened.append("op"))

    help.ap()

    top = helping.last()
    text = all_text(top)
    assert top.title() == "Add Plugins"
    assert f"{app.home}/.local/share/PyNotes/add-ons" in text
    assert "Warning: Plugins have full access" in text
    for button in ("Download From PyNotes' GitHub", "Open Plugins Directory"):
        next(
            w
            for w in descendants(top)
            if isinstance(w, ctk.Button) and w.cget("text") == button
        ).invoke()
    assert opened == ["dp", "op"]


def test_recovering_a_backup_shows_the_steps(app):
    help.rb()

    assert app.dialogs.of_kind("info")[0][1] == "Recover Backup"
    assert ".filebackpynotes.txt" in app.dialogs.messages("info")[0]


# ---------------------------------------------------------------------------
# Alt-X commands
# ---------------------------------------------------------------------------


def test_the_commands_help_names_every_command_and_alias(helping, tk_root):
    help.hx()

    text = all_text(helping.last())
    missing = [
        name
        for name in command.cmdregistry
        if not re.search(rf"'{re.escape(name)}['\s:]", text)
    ]
    assert missing == []
    wait_for_message(tk_root, "open alt-x commands help")


def test_the_commands_help_includes_the_plugin_commands_help(helping):
    state.plgnscmdhelp = "\n\n'plugcommand': Does the plugin thing"

    help.hx()

    assert "'plugcommand': Does the plugin thing" in all_text(helping.last())


def test_the_commands_help_explains_the_syntax(helping):
    help.hx()

    text = all_text(helping.last())
    assert "Alt-X" in text
    assert ";" in text


# ---------------------------------------------------------------------------
# MathGod
# ---------------------------------------------------------------------------


def test_mathgod_help_shows_examples(helping):
    help.helpmathgod()

    text = all_text(helping.last())
    assert "Integral(x^2, x)" in text


# ---------------------------------------------------------------------------
# PyCode
# ---------------------------------------------------------------------------


@pytest.fixture
def pycode_help(helping):
    help.helppycode()
    top = helping.last()
    widgets = list(descendants(top))
    translator = next(
        w
        for w in widgets
        if isinstance(w, ctk.Frame)
        and getattr(w, "t", None) is not None
        and getattr(getattr(w, "t", None), "placeholder", "").startswith("Type PyCode")
    )
    translated = [w for w in widgets if isinstance(w, utils.EnabledLookTextbox)][-1]
    return type(
        "PyCodeHelp",
        (),
        {
            "top": top,
            "input": translator.t,
            "output": translated,
            "text": all_text(top),
        },
    )()


def translate_live(pycode_help, code):
    pycode_help.input.delete("1.0", "end")
    pycode_help.input.insert("1.0", code)
    run_binding(pycode_help.input.inner, "<<Modified>>")
    return pycode_help.output.get("1.0", "end-1c")


def test_the_pycode_help_documents_every_command(pycode_help):
    missing = [
        name for name in pycode.pycode_commands if f"{name}(" not in pycode_help.text
    ]

    assert missing == []


def test_the_testing_tab_translates_pycode_as_it_is_typed(pycode_help):
    assert translate_live(pycode_help, "x = 1; save_file()") == "x = 1\npcsavefile()"


def test_the_testing_tab_follows_every_edit(pycode_help):
    translate_live(pycode_help, "a = 1")

    assert translate_live(pycode_help, "b = 2") == "b = 2"


def test_the_testing_tab_clears_when_all_the_pycode_is_deleted(pycode_help):
    translate_live(pycode_help, "a = 1")

    assert translate_live(pycode_help, "") == ""


def test_the_testing_tab_clears_when_only_spaces_remain(pycode_help):
    translate_live(pycode_help, "a = 1")

    assert translate_live(pycode_help, "   \n  ") == ""


def test_the_testing_tab_shows_errors_in_red(pycode_help):
    shown = translate_live(pycode_help, "x = ")

    assert shown.startswith("line 1 of code, column 4")
    assert pycode_help.output.tag_ranges("error")


def test_the_testing_tab_removes_an_old_error_when_the_code_is_fixed(pycode_help):
    translate_live(pycode_help, "x = ")

    shown = translate_live(pycode_help, "x = 1")

    assert shown == "x = 1"
    assert not pycode_help.output.tag_ranges("error")


def test_the_testing_tab_highlights_the_python(pycode_help):
    translate_live(pycode_help, "f (a) { return a }")

    def tagged(tag):
        ranges = [str(i) for i in pycode_help.output.tag_ranges(tag)]
        return [
            pycode_help.output.get(a, b) for a, b in zip(ranges[0::2], ranges[1::2])
        ]

    assert tagged("hpa") == ["def", "return"]
    assert tagged("hpf") == ["f"]


def test_the_testing_tab_translates_multi_line_pycode(pycode_help):
    shown = translate_live(pycode_help, "if (a) {\n  x = 1;\n} else {\n  x = 2;\n}")

    assert shown == "if a:\n x = 1\nelse:\n x = 2"


def test_the_testing_output_cannot_be_edited(pycode_help):
    assert str(pycode_help.output.cget("state")) == "disabled"
