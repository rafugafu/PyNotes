"""The window functions (opening, switching and closing buffers, titles,
menus, themes, exiting) and editors that share a file as peer views.

The application runs in the withdrawn window of application.py, so nothing is
ever shown, and its dialogs are scripted.
"""

import os

import pytest

import buffer as buffer_module
import editor as editor_module
import state
import window
from test_editor import FakeObserver, put, text_of, wait_for

pytestmark = pytest.mark.display


class ExitCalled(Exception):
    """Raised instead of ending the test process."""


@pytest.fixture
def work(app, tk_root, tmp_path, monkeypatch):
    """A working directory of its own, with no file watching."""
    directory = tmp_path / "work"
    directory.mkdir()
    monkeypatch.chdir(directory)
    monkeypatch.setattr(editor_module, "Observer", FakeObserver)
    FakeObserver.instances = []
    yield directory


@pytest.fixture
def startup(work):
    """The blank editor PyNotes opens first, which loading files into other
    buffers relies on (the menu bar is rebuilt from the active buffer)."""
    return window.neweditor()


def file_with(work, name, text="content"):
    path = work / name
    path.write_text(text)
    return str(path)


# ---------------------------------------------------------------------------
# Opening editors
# ---------------------------------------------------------------------------


def test_opening_an_editor_makes_it_active_and_titles_the_window(work, tk_root):
    first = window.neweditor()
    second = window.neweditor()

    assert state.all_buffers == [first, second]
    assert state.active is second
    assert state.buffindex == 1
    assert first.active is False and second.active is True
    assert tk_root.title() == "PyNotes - Untitled"


def test_opening_a_file_loads_it_in_a_new_editor(work, startup):
    path = file_with(work, "a.txt", "hello")

    opened = window.neweditor(path)

    assert text_of(opened) == "hello"
    assert opened.title == path


def test_opening_a_file_that_is_already_open_makes_a_peer_view(work, startup):
    path = file_with(work, "a.txt", "shared")
    master = window.neweditor(path)

    view = window.neweditor(path)

    assert view.view_master is master
    assert master.view_children == [view]
    assert text_of(view) == "shared"
    assert view.title == path


def test_opening_a_directory_is_an_error(work, app, tmp_path):
    assert window.neweditor(str(tmp_path)) is None

    assert app.dialogs.messages("error") == [f'"{tmp_path.name}" is a directory.']
    assert state.all_buffers == []


def test_opening_with_true_asks_for_the_file(work, startup, monkeypatch):
    path = file_with(work, "picked.txt", "picked")
    monkeypatch.setattr(window.dialogs, "openfileget", lambda *a, **k: path)

    assert window.neweditor(True) is None

    assert state.all_buffers[-1].title == path


def test_asking_for_a_file_and_cancelling_opens_nothing(work, monkeypatch):
    monkeypatch.setattr(window.dialogs, "openfileget", lambda *a, **k: "")

    window.neweditor(True)

    assert state.all_buffers == []


def test_opening_runs_the_pycode_hooks(work):
    seen = []
    state.pcbeforehooks["new-file-new-editor"] = [lambda value: seen.append("before")]
    state.pcafterhooks["new-file-new-editor"] = [lambda value: seen.append("after")]

    window.neweditor()

    assert seen == ["before", "after"]


def test_find_open_editor_ignores_views_and_viewers(work, startup):
    path = file_with(work, "a.txt")
    master = window.neweditor(path)
    window.neweditor(path)

    assert window.find_open_editor(path) is master
    assert window.find_open_editor(path + "x") is None


def test_find_open_editor_ignores_images(work):
    master = window.neweditor()
    master.title = "/some/picture.png"
    master.hmode = "png"

    assert window.find_open_editor("/some/picture.png") is None


# ---------------------------------------------------------------------------
# Switching buffers
# ---------------------------------------------------------------------------


def test_setactive_goes_to_the_next_buffer_and_wraps(work):
    first = window.neweditor()
    second = window.neweditor()
    third = window.neweditor()

    window.setactive()
    assert state.active is first
    window.setactive()
    assert state.active is second
    window.setactive(-1)
    assert state.active is third


def test_setactive_to_a_given_index(work):
    first = window.neweditor()
    window.neweditor()

    window.setactive(0)

    assert state.active is first
    assert state.buffindex == 0


def test_setactive_of_the_active_buffer_does_nothing_unless_forced(work):
    window.neweditor()
    seen = []
    state.pcbeforehooks["switch-buffer"] = [lambda value: seen.append(value)]

    window.setactive(0)
    assert seen == []
    window.setactive(0, force=True)
    assert seen == [0]


def test_setactive_to_a_missing_buffer_does_nothing(work):
    window.neweditor()

    window.setactive(7)

    assert state.buffindex == 0


def test_switching_updates_the_window_title(work, startup, tk_root, tmp_path):
    named = window.neweditor(file_with(work, "named.txt"))
    window.neweditor()

    window.setactive(1)

    assert tk_root.title() == "PyNotes - named.txt"
    assert state.active is named


def test_a_title_set_by_pycode_is_kept(work, tk_root):
    window.neweditor()
    tk_root.title("custom")
    state.pcsettitle = True

    window.settitle()

    assert tk_root.title() == "custom"


def test_the_menu_bar_follows_the_active_buffer(work):
    window.neweditor()

    labels = [entry["label"] for entry in state.mainmenu.entries]

    assert labels == list(state.all_editor_menus)


# ---------------------------------------------------------------------------
# Closing buffers
# ---------------------------------------------------------------------------


def test_the_only_buffer_cannot_be_closed(work, tk_root):
    window.neweditor()

    assert buffer_module.pcclosebuff() is False

    assert len(state.all_buffers) == 1


def test_closing_the_active_buffer(work):
    first = window.neweditor()
    second = window.neweditor()

    buffer_module.pcclosebuff()

    assert state.all_buffers == [first]
    assert state.active is first
    assert not second.winfo_exists()


def test_closing_a_buffer_by_number(work):
    first = window.neweditor()
    second = window.neweditor()
    window.neweditor()

    buffer_module.pcclosebuff(1)

    assert second not in state.all_buffers
    assert first in state.all_buffers


def test_closing_a_buffer_with_unsaved_text_can_be_cancelled(work, app):
    window.neweditor()
    second = window.neweditor()
    put(second, "unsaved")
    second.keypress()
    app.dialogs.answer("ask", None)

    assert buffer_module.pcclosebuff() is False

    assert second in state.all_buffers


def test_save_before_closing_asks_every_buffer_to_save(work, startup):
    startup.clt(str(work / "startup.txt"))
    path = file_with(work, "a.txt", "old")
    editor = window.neweditor(path)
    put(editor, " new", "end-1c")

    assert window.saveforclose() is True

    assert (work / "a.txt").read_text() == "old new"


def test_save_before_closing_stops_if_a_save_fails(work, monkeypatch):
    editor = window.neweditor()
    monkeypatch.setattr(editor, "saveforclose", lambda: False)

    assert window.saveforclose() is False


# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------


def test_balancing_gives_every_pane_an_equal_share(work, tk_root):
    window.neweditor()
    window.neweditor()
    window.neweditor()
    split = state.panes._splits()[0]
    split.fractions = [0.7, 0.2, 0.1]

    window.balance()

    assert split.fractions == pytest.approx([1 / 3] * 3)


def test_vertical_splits_are_balanced_separately(work, tk_root):
    window.neweditor()
    window.neweditor(orient="vertical")
    splits = {split.orient: split for split in state.panes._splits()}

    splits["vertical"].fractions = [0.9, 0.1]
    window.balance("horizontal")
    assert splits["vertical"].fractions == [0.9, 0.1]
    window.balance("vertical")
    assert splits["vertical"].fractions == pytest.approx([0.5, 0.5])


def test_resizing_the_window_rebalances_after_a_pause(work, tk_root, monkeypatch):
    window.neweditor()
    balanced = []
    monkeypatch.setattr(window, "balance", lambda *a: balanced.append(True))
    event = type("Event", (), {"widget": tk_root, "width": 1234, "height": 987})()

    window._on_root_resize(event)
    window._on_root_resize(event)

    assert state._last_root_size == (1234, 987)
    wait_for(tk_root, lambda: balanced, "the rebalance", seconds=5)
    assert balanced == [True]


def test_resize_events_of_other_widgets_are_ignored(work, tk_root):
    window.neweditor()
    before = state._last_root_size
    event = type("Event", (), {"widget": object(), "width": 5, "height": 5})()

    window._on_root_resize(event)

    assert state._last_root_size == before


# ---------------------------------------------------------------------------
# Themes and dialogs
# ---------------------------------------------------------------------------


def test_the_window_lists_all_theme_names_sorted(work, tk_root):
    names = tk_root.themes()

    assert names == sorted(names)
    assert "Default" in names and "Dark" in names and "Light" in names


def test_setting_a_theme_remembers_its_name(work, tk_root):
    window.neweditor()

    tk_root.settheme("Dark")
    assert tk_root.gettheme() == "Dark"
    tk_root.settheme("Light")
    assert tk_root.gettheme() == "Light"


def test_setting_a_missing_theme_changes_nothing(work, tk_root):
    window.neweditor()
    tk_root.settheme("Dark")

    tk_root.settheme("No Such Theme")

    assert tk_root.gettheme() == "Dark"


def test_setting_no_theme_goes_back_to_the_default(work, tk_root):
    window.neweditor()
    tk_root.settheme("Dark")

    tk_root.settheme(None)

    assert tk_root.gettheme() == "Default"


def test_the_window_lists_the_font_families(work, tk_root):
    assert tk_root.getfonts()


@pytest.mark.parametrize(
    ("clicked", "labels", "expected"),
    [
        (1, ["No", "Yes"], "No"),
        (2, ["No", "Yes"], "Yes"),
        (3, ["No", "Yes"], None),
        (0, ["No", "Yes"], None),
        ("Yes", ["No", "Yes"], "Yes"),
        (None, ["No", "Yes"], None),
    ],
)
def test_console_answers_are_turned_into_button_labels(
    tk_root, clicked, labels, expected
):
    assert tk_root._resolve_clicked(clicked, labels) == expected


def test_ask_presets_map_buttons_to_answers():
    assert window._ASK_PRESETS[("yes", "no")] == {"Yes": True, "No": False, None: None}
    assert window._ASK_PRESETS[("yes", "no", "cancel")]["Cancel"] is None
    for options, labels in window._ASK_PRESET_LABELS.items():
        assert len(labels) == len(options)


# ---------------------------------------------------------------------------
# Exiting
# ---------------------------------------------------------------------------


@pytest.fixture
def exits(work, monkeypatch, app):
    """Make ext() raise instead of ending the process or destroying the
    window."""
    monkeypatch.setattr(
        window.os, "_exit", lambda code: (_ for _ in ()).throw(ExitCalled(code))
    )
    monkeypatch.setattr(state.root, "destroy", lambda: None)
    import cli

    monkeypatch.setattr(cli, "close", lambda: None)
    state.consoleqafter = None
    return app


def test_exiting_a_clean_application(exits):
    window.neweditor()

    with pytest.raises(ExitCalled):
        window.ext()

    assert exits.dialogs.of_kind("ask") == []


def test_exiting_asks_before_killing_a_running_process(exits):
    editor = window.neweditor()
    editor.running = True
    exits.dialogs.answer("ask", False)

    window.ext()

    assert exits.dialogs.messages("ask") == ["Kill active process(es) and close?"]


def test_exiting_is_refused_while_an_outside_change_is_pending(exits, tk_root):
    editor = window.neweditor()
    editor._file_watch_prompt_pending = True

    window.ext()

    wait_for(
        tk_root,
        lambda: state.cmdentry.get("1.0", "end-1c").startswith("select 'Discard"),
        "the message",
    )
    assert exits.dialogs.of_kind("ask") == []


def test_exiting_with_unsaved_text_asks_and_can_be_cancelled(exits):
    editor = window.neweditor()
    put(editor, "unsaved")
    editor.keypress()
    exits.dialogs.answer("ask", None)

    window.ext()

    assert exits.dialogs.messages("ask") == [
        "Do you want to save files before closing?"
    ]


def test_exiting_can_discard_unsaved_text(exits):
    editor = window.neweditor()
    put(editor, "unsaved")
    editor.keypress()
    exits.dialogs.answer("ask", False)

    with pytest.raises(ExitCalled):
        window.ext()


def test_exiting_can_save_first(exits, work, startup):
    startup.clt(str(work / "startup.txt"))
    path = file_with(work, "a.txt", "old")
    editor = window.neweditor(path)
    put(editor, " new", "end-1c")
    editor._update_unsaved()
    exits.dialogs.answer("ask", True)

    with pytest.raises(ExitCalled):
        window.ext()

    assert (work / "a.txt").read_text() == "old new"


def test_exiting_removes_the_temporary_run_file_and_runs_the_hooks(exits, app):
    window.neweditor()
    temporary = app.home / ".local" / "share" / "PyNotes" / "tempcode"
    temporary.write_text("print(1)")
    seen = []
    state.pcbeforehooks["exit-pynotes"] = [lambda value: seen.append("before")]
    state.pcafterhooks["exit-pynotes"] = [lambda value: seen.append("after")]

    with pytest.raises(ExitCalled):
        window.ext()

    assert not temporary.exists()
    assert seen == ["before", "after"]


def test_exiting_closes_the_running_terminals(exits):
    window.neweditor()
    closed = []
    state._open_terminal_closers.append(lambda: closed.append(True))

    with pytest.raises(ExitCalled):
        window.ext()

    assert closed == [True]


# ---------------------------------------------------------------------------
# Views of one file
# ---------------------------------------------------------------------------


@pytest.fixture
def views(work, startup):
    path = file_with(work, "shared.txt", "one\ntwo")
    master = window.neweditor(path)
    view = window.neweditor(path)
    return master, view


def test_views_show_the_same_text(views):
    master, view = views

    put(master, "zero\n")

    assert text_of(view) == "zero\none\ntwo"


def test_an_edit_in_a_view_shows_in_the_master(views):
    master, view = views

    view.type_.insert("end", "\nthree")

    assert text_of(master) == "one\ntwo\nthree"


def test_views_have_their_own_cursor(views):
    master, view = views

    master._own_type.mark_set("insert", "1.1")
    view._own_type.mark_set("insert", "2.2")

    assert master._own_type.index("insert") == "1.1"
    assert view._own_type.index("insert") == "2.2"


def test_views_share_the_state_of_the_file(views):
    master, view = views

    master.hmode = "latex"
    assert view.hmode == "latex"
    view.unsaved = True
    assert master.unsaved is True
    assert view.title == master.title
    assert view.unsavedtext == master.unsavedtext


def test_saving_in_a_view_saves_the_master(views):
    master, view = views
    view.type_.insert("end", "\nthree")

    view.sssv()

    assert open(master.title).read() == "one\ntwo\nthree"
    assert master.unsaved is False


def test_the_hmode_of_a_view_is_set_on_the_master(views):
    master, view = views

    view.pchmode("python")

    assert master.hmode == "python"


def test_a_view_asks_nothing_when_it_closes(views, app):
    master, view = views
    put(view, "unsaved")
    view.keypress()

    assert view.close() is True

    assert app.dialogs.of_kind("ask") == []
    assert view not in master.view_children


def test_the_master_asks_nothing_when_a_view_remains(views, app):
    master, view = views
    put(master, "unsaved")
    master.keypress()

    assert master.close() is True

    assert app.dialogs.of_kind("ask") == []
    assert view.view_master is None
    assert text_of(view) == "unsaved" + "one\ntwo"


def test_closing_the_master_hands_the_file_to_a_view(views):
    master, view = views
    title = master.title

    master.close()

    assert view.view_master is None
    assert view.title == title
    assert state.active is not master or state.active is view


def test_loading_another_file_in_a_view_detaches_it(views, work):
    master, view = views
    other = file_with(work, "other.txt", "other text")

    view.ld(other)

    assert view.view_master is None
    assert view not in master.view_children
    assert text_of(view) == "other text"
    assert text_of(master) == "one\ntwo"


def test_new_file_in_a_view_detaches_it(views):
    master, view = views

    view.nw()

    assert view.view_master is None
    assert text_of(view) == ""
    assert text_of(master) == "one\ntwo"


def test_a_buffer_can_become_a_view_of_an_open_file(work, startup):
    path = file_with(work, "shared.txt", "text")
    master = window.neweditor(path)
    other = window.neweditor()

    other._smart_open(path)

    assert other.view_master is master
    assert text_of(other) == "text"


def test_opening_the_file_a_buffer_already_shows_does_nothing(work, startup):
    path = file_with(work, "shared.txt", "text")
    editor = window.neweditor(path)

    editor._smart_open(path)

    assert editor.view_master is None
    assert editor.title == path


def test_a_free_file_is_loaded_into_the_buffer(work):
    path = file_with(work, "free.txt", "free")
    editor = window.neweditor()

    editor._smart_open(path)

    assert editor.view_master is None
    assert text_of(editor) == "free"


def test_all_views_are_highlighted_together(views, tk_root):
    master, view = views
    master.pchmode("markdown")
    put(master, "# Title\n")
    for member in (master, view):
        member.type_top, member.type_bottom = "1.0", "end"
    master.ha("markdown")
    wait_for(tk_root, lambda: not master._ha_running[0], "the highlighting")

    for member in (master, view):
        ranges = [str(i) for i in member._own_type.tag_ranges("hmh1")]
        assert ranges, member


def test_group_members_list_the_master_first(views):
    master, view = views

    assert master._group_members() == [master, view]
    assert view._group_members() == [master, view]
