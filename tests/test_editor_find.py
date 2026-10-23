"""The Find and Find & Replace panels of the editor.

The panels are windows of the application; here they are made but never
shown, and driven through their widgets: the text is typed into the entry,
the entry's key-release binding runs, and the buttons are invoked.
"""

import re
import time

import canvastk as ctk
import pytest

import state
import window
from test_editor import (
    FakeObserver,
    cursor_at,
    editor,
    put,
    tagged,
    text_of,
    wait_for,
)

pytestmark = pytest.mark.display


class Panel:
    """A find panel's widgets."""

    def __init__(self, top):
        self.top = top

    def descendants(self, widget=None):
        for child in (widget or self.top).winfo_children():
            yield child
            yield from self.descendants(child)

    @property
    def entries(self):
        return [w for w in self.descendants() if isinstance(w, ctk.Entry)]

    @property
    def find_entry(self):
        return self.entries[0]

    @property
    def replace_entry(self):
        return self.entries[1]

    def widget(self, kind, text):
        for candidate in self.descendants():
            if isinstance(candidate, kind) and candidate.cget("text") == text:
                return candidate
        raise AssertionError(f"no {kind.__name__} {text!r}")

    def button(self, text):
        return self.widget(ctk.Button, text)

    def option(self, text):
        return self.widget(ctk.Checkbutton, text)

    def alive(self):
        return self.top.winfo_exists()


def run_binding(widget, sequence):
    """Run the Tcl script bound to sequence with dummy event values (key
    events cannot be delivered to a window that is never shown)."""
    script = re.sub(r"%.", "0", widget.inner.bind(sequence))
    widget.tk.eval("while 1 {" + script + "\nbreak}")


@pytest.fixture
def opened_panels(monkeypatch, tk_root):
    """Make the panels' windows withdrawn, and collect them."""
    panels = []
    original = type(state.root).subwin

    def subwin(*arguments, **keywords):
        top = original(state.root, *arguments, **keywords)
        top.withdraw()
        panels.append(Panel(top))
        return top

    monkeypatch.setattr(state.root, "subwin", subwin, raising=False)
    yield panels
    for panel in panels:
        if panel.alive():
            panel.top.destroy()


def settle(root, seconds=0.25):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        root.update()
        time.sleep(0.005)


def open_panel(editor, panels, method="f", direction="forward"):
    getattr(editor, method)(direction)
    return panels[-1]


def search(root, panel, text):
    panel.find_entry.delete(0, "end")
    panel.find_entry.insert(0, text)
    run_binding(panel.find_entry, "<KeyRelease>")
    settle(root)


def current(editor):
    return tagged(editor, "foundhighlight")


def current_at(editor):
    ranges = editor.type_.tag_ranges("foundhighlight")
    return str(ranges[0]) if ranges else None


# ---------------------------------------------------------------------------
# Find
# ---------------------------------------------------------------------------


def test_find_highlights_every_match_and_the_first_one_after_the_cursor(
    editor, opened_panels, tk_root
):
    put(editor, "cat dog cat bird cat")
    cursor_at(editor, "1.5")
    panel = open_panel(editor, opened_panels)

    search(tk_root, panel, "cat")

    assert tagged(editor, "found") == ["cat", "cat", "cat"]
    assert current_at(editor) == "1.8"


def test_find_ignores_case_by_default(editor, opened_panels, tk_root):
    put(editor, "Cat cat CAT")
    panel = open_panel(editor, opened_panels)

    search(tk_root, panel, "cat")

    assert tagged(editor, "found") == ["Cat", "cat", "CAT"]


def test_find_can_match_case(editor, opened_panels, tk_root):
    put(editor, "Cat cat CAT")
    panel = open_panel(editor, opened_panels)
    panel.option("Case Sensitive").invoke()

    search(tk_root, panel, "cat")

    assert tagged(editor, "found") == ["cat"]


def test_find_can_use_regular_expressions(editor, opened_panels, tk_root):
    put(editor, "a1 b22 c333")
    panel = open_panel(editor, opened_panels)
    panel.option("Use regexp").invoke()

    search(tk_root, panel, r"\d+")

    assert tagged(editor, "found") == ["1", "22", "333"]


def test_find_treats_the_text_literally_without_regexp(editor, opened_panels, tk_root):
    put(editor, "a.c abc")
    panel = open_panel(editor, opened_panels)

    search(tk_root, panel, "a.c")

    assert tagged(editor, "found") == ["a.c"]


def test_find_can_match_whole_words_only(editor, opened_panels, tk_root):
    put(editor, "cat concat cat.")
    panel = open_panel(editor, opened_panels)
    panel.option("Match Whole Word Only").invoke()

    search(tk_root, panel, "cat")

    assert tagged(editor, "found") == ["cat", "cat"]


def test_an_invalid_regular_expression_finds_nothing(editor, opened_panels, tk_root):
    put(editor, "text")
    panel = open_panel(editor, opened_panels)
    panel.option("Use regexp").invoke()

    search(tk_root, panel, "(")

    assert tagged(editor, "found") == []


def test_clearing_the_search_text_removes_the_highlights(
    editor, opened_panels, tk_root
):
    put(editor, "cat cat")
    panel = open_panel(editor, opened_panels)
    search(tk_root, panel, "cat")

    search(tk_root, panel, "")

    assert tagged(editor, "found") == []
    assert current(editor) == []


def test_matches_across_lines_are_found_with_their_positions(
    editor, opened_panels, tk_root
):
    put(editor, "ab\ncab\nabc")
    panel = open_panel(editor, opened_panels)

    search(tk_root, panel, "ab")

    ranges = [str(index) for index in editor.type_.tag_ranges("found")]
    assert ranges == ["1.0", "1.2", "2.1", "2.3", "3.0", "3.2"]


def test_next_and_previous_step_through_the_matches_and_wrap(
    editor, opened_panels, tk_root
):
    put(editor, "x one x two x")
    panel = open_panel(editor, opened_panels)
    search(tk_root, panel, "x")
    assert current_at(editor) == "1.0"

    panel.button("Next").invoke()
    assert current_at(editor) == "1.6"
    panel.button("Next").invoke()
    assert current_at(editor) == "1.12"
    panel.button("Next").invoke()
    assert current_at(editor) == "1.0"
    panel.button("Previous").invoke()
    assert current_at(editor) == "1.12"


def test_stepping_moves_the_cursor_after_the_match(editor, opened_panels, tk_root):
    put(editor, "x one x")
    panel = open_panel(editor, opened_panels)
    search(tk_root, panel, "x")

    panel.button("Next").invoke()

    assert editor.type_.index("insert") == "1.7"


def test_stepping_without_matches_does_nothing(editor, opened_panels, tk_root):
    put(editor, "text")
    panel = open_panel(editor, opened_panels)
    search(tk_root, panel, "zzz")

    panel.button("Next").invoke()
    panel.button("Previous").invoke()

    assert current(editor) == []


def test_find_backward_starts_at_the_match_before_the_cursor(
    editor, opened_panels, tk_root
):
    put(editor, "x one x two x")
    cursor_at(editor, "1.8")
    panel = open_panel(editor, opened_panels, direction="backward")

    search(tk_root, panel, "x")

    assert current_at(editor) == "1.6"


def test_find_backward_wraps_to_the_last_match(editor, opened_panels, tk_root):
    put(editor, "x one x")
    cursor_at(editor, "1.0")
    panel = open_panel(editor, opened_panels, direction="backward")

    search(tk_root, panel, "x")

    assert current_at(editor) == "1.6"


def test_find_from_the_beginning_starts_at_the_first_match(
    editor, opened_panels, tk_root
):
    put(editor, "x one x")
    cursor_at(editor, "1.5")
    panel = open_panel(editor, opened_panels, direction="beginning")

    search(tk_root, panel, "x")

    assert current_at(editor) == "1.0"


def test_find_forward_wraps_to_the_first_match_after_the_last(
    editor, opened_panels, tk_root
):
    put(editor, "x one x")
    cursor_at(editor, "1.7")
    panel = open_panel(editor, opened_panels)

    search(tk_root, panel, "x")

    assert current_at(editor) == "1.0"


@pytest.mark.parametrize(
    ("direction", "message"),
    [
        ("forward", "find text forward"),
        ("backward", "find text backward"),
        ("beginning", "find text from beginning"),
    ],
)
def test_opening_find_says_which_way_it_searches(
    editor, opened_panels, tk_root, direction, message
):
    open_panel(editor, opened_panels, direction=direction)

    wait_for(tk_root, lambda: state.cmdentry.get("1.0", "end-1c") == message, message)


def test_close_removes_the_highlights_and_the_panel(editor, opened_panels, tk_root):
    put(editor, "cat cat")
    panel = open_panel(editor, opened_panels)
    search(tk_root, panel, "cat")

    panel.button("Close").invoke()

    assert not panel.alive()
    assert tagged(editor, "found") == []
    assert current(editor) == []


def test_editing_the_text_closes_the_panel(editor, opened_panels, tk_root):
    put(editor, "cat")
    panel = open_panel(editor, opened_panels)
    search(tk_root, panel, "cat")

    editor.type_.insert("end", "s")
    settle(tk_root, 0.1)

    assert not panel.alive()
    assert tagged(editor, "found") == []


def test_the_return_key_in_the_find_field_steps_to_the_next_match(
    editor, opened_panels, tk_root
):
    put(editor, "x x x")
    panel = open_panel(editor, opened_panels)
    search(tk_root, panel, "x")

    run_binding(panel.find_entry, "<Return>")

    assert current_at(editor) == "1.2"
    run_binding(panel.find_entry, "<Shift-Return>")
    assert current_at(editor) == "1.0"


def test_a_new_search_replaces_the_old_results(editor, opened_panels, tk_root):
    put(editor, "cat dog")
    panel = open_panel(editor, opened_panels)
    search(tk_root, panel, "cat")

    search(tk_root, panel, "dog")

    assert tagged(editor, "found") == ["dog"]


def test_many_matches_are_all_applied(editor, opened_panels, tk_root):
    put(editor, "a " * 1200)
    panel = open_panel(editor, opened_panels)

    search(tk_root, panel, "a")
    wait_for(tk_root, lambda: len(tagged(editor, "found")) == 1200, "all matches")

    assert len(tagged(editor, "found")) == 1200


def test_the_emacs_style_find_keys(editor, opened_panels, tk_root, monkeypatch):
    monkeypatch.setattr(state, "emacskeysforsearch", True)
    put(editor, "x x")
    panel = open_panel(editor, opened_panels)
    search(tk_root, panel, "x")

    run_binding_toplevel = lambda sequence: panel.top.tk.eval(
        "while 1 {" + re.sub(r"%.", "0", panel.top.bind(sequence)) + "\nbreak}"
    )
    run_binding_toplevel("<Control-s>")
    assert current_at(editor) == "1.2"
    run_binding_toplevel("<Control-r>")
    assert current_at(editor) == "1.0"
    run_binding_toplevel("<Return>")
    assert not panel.alive()


# ---------------------------------------------------------------------------
# Find & Replace
# ---------------------------------------------------------------------------


def replacing(editor, panels, root, text="a b a b a", find="a", replacement="X"):
    put(editor, text)
    cursor_at(editor, "1.0")
    panel = open_panel(editor, panels, method="fr")
    panel.replace_entry.delete(0, "end")
    panel.replace_entry.insert(0, replacement)
    search(root, panel, find)
    return panel


def test_replace_and_find_share_the_search(editor, opened_panels, tk_root):
    panel = replacing(editor, opened_panels, tk_root)

    assert tagged(editor, "found") == ["a", "a", "a"]
    assert current_at(editor) == "1.0"
    assert len(panel.entries) == 2


def test_replace_swaps_the_current_match_only(editor, opened_panels, tk_root):
    panel = replacing(editor, opened_panels, tk_root)

    panel.button("Replace").invoke()
    settle(tk_root)

    assert text_of(editor) == "X b a b a"
    assert panel.alive()


def test_replace_and_next_swaps_the_match_and_goes_to_the_next(
    editor, opened_panels, tk_root
):
    panel = replacing(editor, opened_panels, tk_root)

    panel.button("Replace and next").invoke()
    settle(tk_root)

    assert text_of(editor) == "X b a b a"
    assert current_at(editor) == "1.4"


def test_replace_and_next_on_the_last_match_closes_the_panel(
    editor, opened_panels, tk_root
):
    panel = replacing(editor, opened_panels, tk_root, text="a b a")
    panel.button("Replace and next").invoke()
    settle(tk_root)
    panel.button("Replace and next").invoke()
    settle(tk_root)

    assert text_of(editor) == "X b X"
    assert not panel.alive()


def test_replace_all_swaps_every_match_from_the_current_one(
    editor, opened_panels, tk_root
):
    panel = replacing(editor, opened_panels, tk_root)

    panel.button("Replace all").invoke()
    settle(tk_root)

    assert text_of(editor) == "X b X b X"
    assert not panel.alive()


def test_replace_all_starts_at_the_current_match(editor, opened_panels, tk_root):
    put(editor, "a b a b a")
    cursor_at(editor, "1.3")
    panel = open_panel(editor, opened_panels, method="fr")
    panel.replace_entry.insert(0, "X")
    search(tk_root, panel, "a")

    panel.button("Replace all").invoke()
    settle(tk_root)

    assert text_of(editor) == "a b X b X"


def test_replace_all_with_a_longer_text(editor, opened_panels, tk_root):
    panel = replacing(editor, opened_panels, tk_root, replacement="long text")

    panel.button("Replace all").invoke()
    settle(tk_root)

    assert text_of(editor) == "long text b long text b long text"


def test_replace_with_nothing_deletes_the_matches(editor, opened_panels, tk_root):
    panel = replacing(editor, opened_panels, tk_root, replacement="")

    panel.button("Replace all").invoke()
    settle(tk_root)

    assert text_of(editor) == " b  b "


def test_replace_without_matches_does_nothing(editor, opened_panels, tk_root):
    panel = replacing(editor, opened_panels, tk_root, find="zzz")

    panel.button("Replace").invoke()
    panel.button("Replace and next").invoke()
    panel.button("Replace all").invoke()

    assert text_of(editor) == "a b a b a"
    assert panel.alive()


def test_replacing_does_not_close_the_panel_like_other_edits_do(
    editor, opened_panels, tk_root
):
    panel = replacing(editor, opened_panels, tk_root)

    panel.button("Replace").invoke()
    settle(tk_root, 0.3)

    assert panel.alive()


def test_replace_backward_goes_to_the_previous_match(editor, opened_panels, tk_root):
    put(editor, "a b a b a")
    cursor_at(editor, "1.8")
    panel = open_panel(editor, opened_panels, method="fr", direction="backward")
    panel.replace_entry.insert(0, "X")
    search(tk_root, panel, "a")
    assert current_at(editor) == "1.4"

    run_binding(panel.replace_entry, "<Return>")
    settle(tk_root)

    assert text_of(editor) == "a b X b a"
    assert current_at(editor) == "1.0"


def test_the_return_key_in_the_replace_field_replaces_and_goes_on(
    editor, opened_panels, tk_root
):
    panel = replacing(editor, opened_panels, tk_root)

    run_binding(panel.replace_entry, "<Return>")
    settle(tk_root)

    assert text_of(editor) == "X b a b a"
    assert current_at(editor) == "1.4"


def test_replace_next_and_previous_step_like_find(editor, opened_panels, tk_root):
    panel = replacing(editor, opened_panels, tk_root)

    panel.button("Next").invoke()
    assert current_at(editor) == "1.4"
    panel.button("Previous").invoke()
    assert current_at(editor) == "1.0"


def test_replace_close_removes_the_highlights(editor, opened_panels, tk_root):
    panel = replacing(editor, opened_panels, tk_root)

    panel.button("Close").invoke()

    assert not panel.alive()
    assert tagged(editor, "found") == []


def test_the_emacs_style_replace_keys(editor, opened_panels, tk_root, monkeypatch):
    monkeypatch.setattr(state, "emacskeysforsearch", True)
    panel = replacing(editor, opened_panels, tk_root)
    run = lambda sequence: panel.top.tk.eval(
        "while 1 {" + re.sub(r"%.", "0", panel.top.bind(sequence)) + "\nbreak}"
    )

    run("<Alt-Return>")
    assert current_at(editor) == "1.4"
    run("^")
    assert current_at(editor) == "1.0"
    run("<Control-t>")
    settle(tk_root)
    assert text_of(editor) == "X b a b a"
    run("!")
    settle(tk_root)
    assert text_of(editor) == "X b X b X"
