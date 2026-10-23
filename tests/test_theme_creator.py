"""The theme creator: a window with a control for every theme key and a live
preview, that returns the theme designed (or nothing if it is cancelled)."""

import time

import canvastk as ctk
import pytest

import state
import themes
from test_editor import editor  # noqa: F401  (a fixture)

pytestmark = pytest.mark.display


def descendants(widget):
    for child in widget.winfo_children():
        yield child
        yield from descendants(child)


class Creator:
    """The creator's window, found while it waits for the user."""

    def __init__(self, top):
        self.top = top
        self.widgets = list(descendants(top))

    def buttons(self, text):
        return [
            w
            for w in self.widgets
            if isinstance(w, ctk.Button) and w.cget("text") == text
        ]

    def button(self, text):
        return self.buttons(text)[0]

    @property
    def name_entry(self):
        return next(w for w in self.widgets if isinstance(w, ctk.Entry))

    @property
    def dark_toggle(self):
        return next(w for w in self.widgets if isinstance(w, ctk.Toggle))

    def finish(self):
        self.button("Done").invoke()


@pytest.fixture
def run_creator(app, tk_root, editor, monkeypatch):
    """Run themes.creator() while the actions work its window; returns what
    the creator returns."""
    windows = []
    original = type(tk_root).subwin

    def subwin(*arguments, **keywords):
        top = original(tk_root, *arguments, **keywords)
        top.withdraw()
        windows.append(top)
        return top

    monkeypatch.setattr(tk_root, "subwin", subwin, raising=False)

    def run(*actions, color=None):
        monkeypatch.setattr(
            themes, "askcolor", lambda *a, **k: (None, color), raising=False
        )
        pending = list(actions)
        deadline = time.monotonic() + 15

        def step():
            if not windows or not windows[-1].winfo_exists():
                if time.monotonic() < deadline:
                    tk_root.after(20, step)
                return
            top = windows[-1]
            if time.monotonic() > deadline:
                top.destroy()
                return
            if pending:
                pending.pop(0)(Creator(top))
                tk_root.after(20, step)

        tk_root.after(50, step)
        return themes.creator()

    run.windows = windows
    run.app = app
    return run


def name_it(name):
    return lambda creator: (
        creator.name_entry.delete(0, "end"),
        creator.name_entry.insert(0, name),
    )


def test_a_named_theme_is_returned_with_what_was_changed(run_creator):
    result = run_creator(
        name_it("Sunset"),
        lambda creator: creator.button("Change").invoke(),
        lambda creator: creator.finish(),
        color="#112233",
    )

    name, dark, theme = result
    assert name == "Sunset"
    assert dark is False
    assert theme == {"accent": "#112233"}


def test_the_theme_can_be_dark(run_creator):
    result = run_creator(
        name_it("Night"),
        lambda creator: creator.dark_toggle.invoke(),
        lambda creator: creator.finish(),
    )

    assert result[:2] == ("Night", True)
    assert result[2] == {}


def test_a_theme_without_changes_is_empty(run_creator):
    result = run_creator(name_it("Plain"), lambda creator: creator.finish())

    assert result == ("Plain", False, {})


def test_the_name_is_trimmed(run_creator):
    result = run_creator(name_it("  Spaced  "), lambda creator: creator.finish())

    assert result[0] == "Spaced"


def test_done_needs_a_name(run_creator):
    result = run_creator(
        lambda creator: creator.finish(),
        name_it("Late"),
        lambda creator: creator.finish(),
    )

    assert result[0] == "Late"
    assert ("info", "Theme Creator", "Theme name not provided.") in (
        run_creator.app.dialogs.calls
    )


def test_a_colour_can_be_reset(run_creator):
    result = run_creator(
        name_it("Reset"),
        lambda creator: creator.button("Change").invoke(),
        lambda creator: creator.buttons("Reset")[0].invoke(),
        lambda creator: creator.finish(),
        color="#112233",
    )

    assert result[2] == {}


def test_resetting_a_colour_that_was_not_changed_does_nothing(run_creator):
    result = run_creator(
        name_it("Same"),
        lambda creator: creator.buttons("Reset")[3].invoke(),
        lambda creator: creator.finish(),
    )

    assert result[2] == {}


def test_a_cancelled_colour_chooser_changes_nothing(run_creator):
    result = run_creator(
        name_it("None"),
        lambda creator: creator.button("Change").invoke(),
        lambda creator: creator.finish(),
        color=None,
    )

    assert result[2] == {}


def test_several_colours_can_be_changed(run_creator):
    result = run_creator(
        name_it("Many"),
        lambda creator: creator.buttons("Change")[0].invoke(),
        lambda creator: creator.buttons("Change")[1].invoke(),
        lambda creator: creator.finish(),
        color="#abcdef",
    )

    assert list(result[2].values()) == ["#abcdef", "#abcdef"]
    assert len(result[2]) == 2


def test_cancel_asks_and_discards_the_theme(run_creator):
    run_creator.app.dialogs.answer("ask", True)

    result = run_creator(
        name_it("Gone"), lambda creator: creator.button("Cancel").invoke()
    )

    assert result is None
    assert run_creator.app.dialogs.messages("ask") == ["Discard theme and exit?"]


def test_cancel_can_be_declined(run_creator):
    run_creator.app.dialogs.answer("ask", False)

    result = run_creator(
        name_it("Kept"),
        lambda creator: creator.button("Cancel").invoke(),
        lambda creator: creator.finish(),
    )

    assert result[0] == "Kept"


def test_closing_the_window_cancels(run_creator):
    run_creator.app.dialogs.answer("ask", True)

    result = run_creator(
        lambda creator: creator.top.tk.call(creator.top.protocol("WM_DELETE_WINDOW"))
    )

    assert result is None


def test_the_creator_has_a_control_for_every_theme_key_it_offers(run_creator):
    seen = {}

    def look(creator):
        seen["changes"] = len(creator.buttons("Change"))
        seen["resets"] = len(creator.buttons("Reset"))

    run_creator(look, name_it("x"), lambda creator: creator.finish())

    assert seen["changes"] >= 8
    assert seen["resets"] > seen["changes"]


def test_the_preview_follows_the_dark_toggle(run_creator):
    seen = []

    def look(creator):
        preview = next(w for w in creator.widgets if isinstance(w, ctk.LabelFrame))
        seen.append(preview.get_appearance_mode())

    run_creator(
        look,
        lambda creator: creator.dark_toggle.invoke(),
        look,
        name_it("x"),
        lambda creator: creator.finish(),
    )

    assert seen == ["light", "dark"]


def test_the_creator_starts_dark_when_the_application_is_dark(run_creator, tk_root):
    tk_root.settheme("Dark")
    toggled = []

    run_creator(
        lambda creator: toggled.append(creator.dark_toggle.variable.get()),
        name_it("x"),
        lambda creator: creator.finish(),
    )

    assert toggled == [True]


def test_the_creators_result_can_be_saved_and_used(run_creator, app, tk_root):
    import utils

    result = run_creator(
        name_it("Saved"),
        lambda creator: creator.button("Change").invoke(),
        lambda creator: creator.finish(),
        color="#445566",
    )
    utils.save_theme_and_reload(result)

    assert themes.THEMES[0]["Saved"] == {"accent": "#445566"}
    tk_root.settheme("Saved")
    assert tk_root.gettheme() == "Saved"
    themes.THEMES[0].pop("Saved", None)
