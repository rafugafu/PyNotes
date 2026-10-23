"""The Editor buffer: loading and saving, the editing commands behind the
keys and the Alt-X commands, selection, the clipboard, undo and redo, HMode
switching, bracket matching, the LaTeX toolbar, and the file watcher.

The editor lives in the withdrawn application window (see application.py),
so nothing is ever shown; its dialogs are scripted.
"""

import os
import time
from types import SimpleNamespace

import pytest

import dialogs
import editor as editor_module
import state
import utils
import window

pytestmark = pytest.mark.display


def wait_for(root, condition, what, seconds=5):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        root.update()
        if condition():
            return
        time.sleep(0.005)
    raise AssertionError(f"timed out waiting for {what}")


class FakeObserver:
    """The file watcher, which only records what it is asked to watch, so the
    tests do not depend on the operating system's file notifications."""

    instances = []

    def __init__(self):
        self.scheduled = []
        self.started = False
        self.stopped = False
        FakeObserver.instances.append(self)

    def schedule(self, handler, path, recursive=False):
        self.scheduled.append((handler, path, recursive))

    def start(self):
        self.started = True

    def stop(self):
        self.stopped = True

    def join(self):
        pass


@pytest.fixture
def editor(app, tk_root, tmp_path, monkeypatch):
    """A blank editor, the active buffer, in a working directory of its own."""
    work = tmp_path / "work"
    work.mkdir()
    monkeypatch.chdir(work)
    FakeObserver.instances = []
    monkeypatch.setattr(editor_module, "Observer", FakeObserver)
    buffer = window.neweditor()
    tk_root.update()
    yield buffer
    for open_editor in list(state.all_buffers):
        observer = getattr(open_editor, "observer", None)
        if observer is not None:
            try:
                observer.stop()
                observer.join()
            except Exception:
                pass


def text_of(editor):
    return editor.type_.get("1.0", "end-1c")


def put(editor, text, at="1.0"):
    editor.type_.insert(at, text)


def cursor_at(editor, index):
    editor.type_.mark_set("insert", index)


def select(editor, first, last):
    editor.type_.tag_remove("sel", "1.0", "end")
    editor.type_.tag_add("sel", first, last)
    editor.type_.mark_set("insert", last)


def selected(editor):
    ranges = editor.type_.tag_ranges("sel")
    if not ranges:
        return ""
    return editor.type_.get(ranges[0], ranges[1])


def shown():
    """The status message last shown in the command box."""
    return state.cmdentry.get("1.0", "end-1c")


def wait_for_message(root, message):
    wait_for(root, lambda: shown() == message, f"{message!r} to be shown")


# ---------------------------------------------------------------------------
# A new editor
# ---------------------------------------------------------------------------


def test_a_new_editor_is_blank_untitled_and_active(editor):
    assert text_of(editor) == ""
    assert editor.title == ""
    assert editor.unsaved is False
    assert editor.hmode == "normal"
    assert editor.view_master is None
    assert editor.view_children == []
    assert state.active is editor
    assert editor in state.all_buffers


# ---------------------------------------------------------------------------
# Loading files
# ---------------------------------------------------------------------------


def test_loading_a_file_shows_its_text_and_title(editor, tmp_path):
    path = tmp_path / "work" / "note.txt"
    path.write_text("hello\nworld")

    editor.ld(str(path))

    assert text_of(editor) == "hello\nworld"
    assert editor.title == str(path)
    assert editor.unsaved is False
    assert editor.unsavedtext == "hello\nworld"
    assert os.getcwd() == str(path.parent)


@pytest.mark.parametrize(
    ("name", "mode"),
    [
        ("a.py", "python"),
        ("a.tex", "latex"),
        ("a.html", "html"),
        ("a.md", "markdown"),
        ("a.txt", "normal"),
        ("a", "normal"),
    ],
)
def test_the_file_extension_picks_the_hmode(editor, tmp_path, name, mode):
    path = tmp_path / "work" / name
    path.write_text("x")

    editor.ld(str(path))

    assert editor.hmode == mode


def test_loading_a_missing_file_creates_it_empty(editor, tmp_path):
    path = tmp_path / "work" / "new.txt"

    editor.ld(str(path))

    assert path.read_text() == ""
    assert editor.title == str(path)


def test_loading_a_directory_is_an_error(editor, app, tmp_path):
    editor.ld(str(tmp_path))

    assert app.dialogs.messages("error") == [f'"{tmp_path}" is a directory.']
    assert editor.title == ""


def test_loading_a_file_in_a_missing_directory_is_an_error(editor, app, tmp_path):
    editor.ld(str(tmp_path / "missing" / "file.txt"))

    assert "does not exist" in app.dialogs.messages("error")[0]


def test_loading_a_file_replaces_the_text_and_resets_undo(editor, tmp_path):
    put(editor, "old text")
    path = tmp_path / "work" / "other.txt"
    path.write_text("new text")

    editor.ld(str(path))
    editor.undo()

    assert text_of(editor) == "new text"


def test_loading_a_png_shows_the_image_read_only(editor, tmp_path):
    from PIL import Image

    path = tmp_path / "work" / "pixel.png"
    Image.new("RGB", (4, 4), "red").save(path)

    editor.ld(str(path))

    assert editor.hmode == "png"
    assert editor.imageloaded is True
    assert editor.title == str(path)
    assert editor.infos["filetype"].cget("text") == "PNG Image (*.png)"
    assert editor.infos["filesaved"].cget("text") == "Read Only File"


def test_loading_a_text_file_after_a_png_shows_the_text_again(editor, tmp_path):
    from PIL import Image

    image = tmp_path / "work" / "pixel.png"
    Image.new("RGB", (4, 4), "red").save(image)
    note = tmp_path / "work" / "note.txt"
    note.write_text("back to text")
    editor.ld(str(image))

    editor.ld(str(note))

    assert editor.imageloaded is False
    assert editor.hmode == "normal"
    assert text_of(editor) == "back to text"


def test_loading_while_an_external_change_is_pending_is_refused(
    editor, tk_root, tmp_path
):
    path = tmp_path / "work" / "a.txt"
    path.write_text("a")
    editor._file_watch_prompt_pending = True

    editor.ld(str(path))

    assert editor.title == ""
    wait_for_message(
        tk_root,
        "select 'Discard Changes & Reload' or 'Ignore' external changes before loading another file",
    )


# ---------------------------------------------------------------------------
# Saving files
# ---------------------------------------------------------------------------


def test_saving_writes_the_text_and_marks_it_saved(editor, tmp_path):
    path = tmp_path / "work" / "out.txt"
    put(editor, "saved text")

    assert editor.sv(str(path)) is True

    assert path.read_text() == "saved text"
    assert editor.title == str(path)
    assert editor.unsaved is False
    assert editor.unsavedtext == "saved text"


def test_saving_unchanged_text_does_not_write_again(editor, tk_root, tmp_path):
    path = tmp_path / "work" / "same.txt"
    path.write_text("same")
    editor.ld(str(path))
    modified = path.stat().st_mtime_ns

    assert editor.sv(str(path)) is True

    assert path.stat().st_mtime_ns == modified
    wait_for_message(tk_root, "no changes to save")


def test_saving_into_a_missing_directory_creates_it(editor, tmp_path):
    path = tmp_path / "made" / "deep" / "out.txt"
    put(editor, "text")

    assert editor.sv(str(path)) is True

    assert path.read_text() == "text"


def test_saving_over_a_directory_is_an_error(editor, app, tmp_path):
    put(editor, "text")

    assert editor.sv(str(tmp_path)) is False

    assert "already existing directory" in app.dialogs.messages("error")[0]


@pytest.mark.parametrize("mode", ["png", "pdf", "epub"])
def test_files_that_are_only_viewed_cannot_be_saved(editor, app, mode):
    editor.hmode = mode

    assert editor.sv("out") is False

    assert app.dialogs.messages("error") == ["Cannot save files of this type."]


def test_saving_an_unwritable_path_is_an_error(editor, app, tmp_path):
    (tmp_path / "work" / "readonly").mkdir()
    put(editor, "text")

    assert editor.sv(str(tmp_path / "work" / "readonly")) is False

    assert app.dialogs.of_kind("error")


def test_save_uses_the_current_title(editor, tmp_path):
    path = tmp_path / "work" / "a.txt"
    path.write_text("one")
    editor.ld(str(path))
    put(editor, " two", "end-1c")

    editor.sssv()

    assert path.read_text() == "one two"


def test_save_of_an_untitled_editor_asks_for_a_name(editor, tmp_path, monkeypatch):
    path = tmp_path / "work" / "named.txt"
    monkeypatch.setattr(dialogs, "saveasfileget", lambda *a, **k: str(path))
    put(editor, "content")

    editor.sssv()

    assert path.read_text() == "content"
    assert editor.title == str(path)


def test_save_as_that_is_cancelled_saves_nothing(editor, monkeypatch):
    monkeypatch.setattr(dialogs, "saveasfileget", lambda *a, **k: "")
    put(editor, "content")

    assert editor.ssv() is False

    assert editor.title == ""


def test_save_as_resets_the_highlight_it_set(editor, monkeypatch):
    monkeypatch.setattr(dialogs, "saveasfileget", lambda *a, **k: "")

    editor.ssv()

    assert editor.type_.cget("fill_color") is None


def test_set_title_names_the_buffer_and_marks_it_saved(editor, tmp_path):
    path = tmp_path / "work" / "t.txt"
    path.write_text("x")

    editor.clt(str(path))

    assert editor.title == str(path)
    assert editor.unsaved is False
    assert editor.wanttitle == "t.txt"


def test_clearing_the_title_makes_the_buffer_untitled(editor, tmp_path):
    path = tmp_path / "work" / "t.txt"
    path.write_text("x")
    editor.ld(str(path))

    editor.clt("")

    assert editor.title == ""
    assert editor.wanttitle == "Untitled"


def test_the_title_shows_when_there_are_unsaved_changes(editor, tk_root, tmp_path):
    path = tmp_path / "work" / "t.txt"
    path.write_text("x")
    editor.ld(str(path))
    put(editor, "y", "end-1c")
    editor.keypress()

    wait_for(tk_root, lambda: editor.unsaved, "the change to be noticed")

    assert editor.wanttitle == "t.txt *"
    put(editor, "", "end-1c")
    editor.type_.delete("1.0", "end")
    editor.type_.insert("1.0", "x")
    editor.keypress()
    wait_for(tk_root, lambda: not editor.unsaved, "the change to be undone")
    assert editor.wanttitle == "t.txt"


def test_an_untitled_editor_with_text_is_unsaved(editor):
    put(editor, "text")

    editor.keypress()

    assert editor.unsaved is True
    editor.type_.delete("1.0", "end")
    editor.keypress()
    assert editor.unsaved is False


def test_the_file_size_follows_the_text(editor, tk_root):
    put(editor, "twelve chars")
    editor.keypress()

    wait_for(
        tk_root,
        lambda: editor.infos["filesize"].cget("text") == "12 bytes",
        "the file size",
    )


# ---------------------------------------------------------------------------
# New file, open and close
# ---------------------------------------------------------------------------


def test_new_file_blanks_a_saved_editor(editor, tmp_path):
    path = tmp_path / "work" / "a.txt"
    path.write_text("content")
    editor.ld(str(path))

    editor.nw()

    assert text_of(editor) == ""
    assert editor.title == ""
    assert editor.hmode == "normal"


def test_new_file_asks_before_discarding_unsaved_text(editor, app):
    put(editor, "unsaved")
    editor.keypress()
    app.dialogs.answer("ask", False)

    editor.nw()

    assert text_of(editor) == ""
    assert app.dialogs.messages("ask") == ["Do you want to save file before closing?"]


def test_new_file_that_is_cancelled_keeps_the_text(editor, app):
    put(editor, "unsaved")
    editor.keypress()
    app.dialogs.answer("ask", None)

    editor.nw()

    assert text_of(editor) == "unsaved"


def test_new_file_can_save_first(editor, app, tmp_path):
    path = tmp_path / "work" / "keep.txt"
    path.write_text("")
    editor.ld(str(path))
    put(editor, "changed")
    editor._update_unsaved()
    app.dialogs.answer("ask", True)

    editor.nw()

    assert path.read_text() == "changed"
    assert text_of(editor) == ""


def test_closing_a_saved_editor_does_not_ask(editor, app):
    assert editor.close() is True

    assert app.dialogs.of_kind("ask") == []


def test_closing_with_unsaved_text_asks(editor, app):
    put(editor, "unsaved")
    editor.keypress()
    app.dialogs.answer("ask", False)

    assert editor.close() is True

    assert app.dialogs.of_kind("ask")


def test_closing_can_be_cancelled(editor, app):
    put(editor, "unsaved")
    editor.keypress()
    app.dialogs.answer("ask", None)

    assert editor.close() is False


def test_closing_can_save_first(editor, app, tmp_path):
    path = tmp_path / "work" / "closed.txt"
    path.write_text("")
    editor.ld(str(path))
    put(editor, "changed")
    editor._update_unsaved()
    app.dialogs.answer("ask", True)

    assert editor.close() is True

    assert path.read_text() == "changed"


def test_closing_is_refused_while_an_external_change_is_pending(editor, app):
    editor._file_watch_prompt_pending = True

    assert editor.close() is False


def test_open_asks_for_a_file_and_loads_it(editor, tmp_path, monkeypatch):
    path = tmp_path / "work" / "picked.txt"
    path.write_text("picked")
    monkeypatch.setattr(dialogs, "openfileget", lambda *a, **k: str(path))

    editor.lld()

    assert text_of(editor) == "picked"


def test_open_that_is_cancelled_loads_nothing(editor, monkeypatch):
    monkeypatch.setattr(dialogs, "openfileget", lambda *a, **k: "")

    editor.lld()

    assert editor.title == ""


def test_open_offers_to_save_unsaved_text_first(editor, app, tmp_path, monkeypatch):
    path = tmp_path / "work" / "picked.txt"
    path.write_text("picked")
    monkeypatch.setattr(dialogs, "openfileget", lambda *a, **k: str(path))
    put(editor, "unsaved")
    editor.keypress()
    app.dialogs.answer("ask", None)

    editor.llld()

    assert text_of(editor) == "unsaved"


# ---------------------------------------------------------------------------
# Watching the file for outside changes
# ---------------------------------------------------------------------------


def test_a_loaded_file_has_its_directory_watched(editor, tmp_path):
    path = tmp_path / "work" / "w.txt"
    path.write_text("x")

    editor.ld(str(path))

    (watcher,) = FakeObserver.instances
    assert watcher.started
    handler, directory, recursive = watcher.scheduled[0]
    assert isinstance(handler, editor.FileChangeHandler)
    assert (directory, recursive) == (str(path.parent), False)


def test_loading_another_file_stops_watching_the_first(editor, tmp_path):
    first = tmp_path / "work" / "one.txt"
    second = tmp_path / "work" / "two.txt"
    first.write_text("1")
    second.write_text("2")
    editor.ld(str(first))

    editor.ld(str(second))

    assert [watcher.stopped for watcher in FakeObserver.instances] == [True, False]


def test_an_untitled_editor_watches_nothing(editor):
    editor.clt("")

    assert FakeObserver.instances == []


@pytest.fixture
def watched(editor, tmp_path):
    path = tmp_path / "work" / "watched.txt"
    path.write_text("original")
    editor.ld(str(path))
    return editor, str(path)


def test_a_change_to_the_file_from_outside_asks_what_to_do(watched, app, tk_root):
    editor, path = watched
    handler = editor.FileChangeHandler(editor)
    app.dialogs.answer("warning", "Ignore")

    handler.on_modified(SimpleNamespace(is_directory=False, src_path=path))

    assert editor._file_watch_prompt_pending is True
    wait_for(tk_root, lambda: app.dialogs.of_kind("warning"), "the question")
    assert "has changed on disk" in app.dialogs.messages("warning")[0]
    assert editor._file_watch_prompt_pending is False
    assert text_of(editor) == "original"


def test_discarding_changes_reloads_the_file(watched, app, tk_root):
    editor, path = watched
    put(editor, " edited", "end-1c")
    with open(path, "w") as file:
        file.write("changed outside")
    app.dialogs.answer("warning", "Discard Changes & Reload")

    editor.FileChangeHandler(editor).on_modified(
        SimpleNamespace(is_directory=False, src_path=path)
    )

    wait_for(tk_root, lambda: text_of(editor) == "changed outside", "the reload")


@pytest.mark.parametrize(
    ("method", "event"),
    [
        ("on_created", {"src_path": "{path}"}),
        ("on_moved", {"src_path": "elsewhere", "dest_path": "{path}"}),
    ],
)
def test_other_ways_of_replacing_the_file_are_noticed_too(watched, method, event):
    editor, path = watched
    event = {key: value.format(path=path) for key, value in event.items()}

    getattr(editor.FileChangeHandler(editor), method)(
        SimpleNamespace(is_directory=False, **event)
    )

    assert editor._file_watch_prompt_pending is True


def test_changes_to_other_files_and_directories_are_ignored(watched):
    editor, path = watched
    handler = editor.FileChangeHandler(editor)

    handler.on_modified(SimpleNamespace(is_directory=False, src_path=path + ".other"))
    handler.on_modified(SimpleNamespace(is_directory=True, src_path=path))
    handler.on_created(SimpleNamespace(is_directory=True, src_path=path))
    handler.on_moved(SimpleNamespace(is_directory=True, dest_path=path))

    assert editor._file_watch_prompt_pending is False


def test_the_editors_own_save_is_not_an_outside_change(watched):
    editor, path = watched
    editor.file_editing_own = True

    editor.FileChangeHandler(editor).on_modified(
        SimpleNamespace(is_directory=False, src_path=path)
    )

    assert editor._file_watch_prompt_pending is False


def test_a_second_change_while_the_question_is_pending_does_not_ask_again(watched):
    editor, path = watched
    handler = editor.FileChangeHandler(editor)
    event = SimpleNamespace(is_directory=False, src_path=path)

    handler.on_modified(event)
    handler.on_modified(event)

    assert editor._main_queue.qsize() == 1


def test_saving_is_refused_while_an_outside_change_is_pending(watched, tk_root):
    editor, path = watched
    editor._file_watch_prompt_pending = True
    put(editor, "x")

    assert editor.sv(path) is False
    assert editor.ssssv(path) is False
    editor.sssv()

    wait_for_message(tk_root, "select 'Ignore' external changes before saving file")


# ---------------------------------------------------------------------------
# Tab, indentation and the movement keys
# ---------------------------------------------------------------------------


def test_tab_inserts_a_tab_character_by_default(editor, monkeypatch):
    monkeypatch.setattr(state, "taborspace", False)

    editor.tab()

    assert text_of(editor) == "\t"


def test_tab_at_the_start_of_a_line_inserts_spaces_when_chosen(editor, monkeypatch):
    monkeypatch.setattr(state, "taborspace", True)

    editor.tab()

    assert text_of(editor) == "    "


def test_tab_after_text_is_always_a_tab(editor, monkeypatch):
    monkeypatch.setattr(state, "taborspace", True)
    put(editor, "x")
    cursor_at(editor, "end-1c")

    editor.tab()

    assert text_of(editor) == "x\t"


def test_tab_with_a_selection_indents_the_selected_lines(editor, monkeypatch):
    monkeypatch.setattr(state, "taborspace", False)
    put(editor, "a\nb")
    select(editor, "1.0", "2.1")

    editor.tab()

    assert text_of(editor) == "\ta\n\tb"


def test_enter_in_python_keeps_the_indent_of_the_line(editor):
    editor.hmode = "python"
    put(editor, "    x = 1")
    cursor_at(editor, "end-1c")

    assert editor.indent() == "break"

    assert text_of(editor) == "    x = 1\n    "


def test_enter_after_a_colon_in_python_indents_one_more_level(editor, monkeypatch):
    monkeypatch.setattr(state, "taborspace", True)
    editor.hmode = "python"
    put(editor, "if x:")
    cursor_at(editor, "end-1c")

    editor.indent()

    assert text_of(editor) == "if x:\n    "


def test_a_colon_in_a_string_or_comment_does_not_indent(editor, monkeypatch):
    monkeypatch.setattr(state, "taborspace", True)
    editor.hmode = "python"
    put(editor, 'x = ":"  # if y:')
    cursor_at(editor, "end-1c")

    editor.indent()

    assert text_of(editor) == 'x = ":"  # if y:\n'


def test_enter_outside_python_is_left_to_the_text_widget(editor):
    put(editor, "x")
    cursor_at(editor, "end-1c")

    assert editor.indent() is None

    assert text_of(editor) == "x"


def test_left_and_right_move_one_character(editor):
    put(editor, "abc")
    cursor_at(editor, "1.1")

    assert editor.right() == "break"
    assert editor.type_.index("insert") == "1.2"
    assert editor.left() == "break"
    assert editor.type_.index("insert") == "1.1"


def test_left_in_the_indent_moves_back_a_whole_level(editor):
    put(editor, "        x")
    cursor_at(editor, "1.8")

    editor.left()

    assert editor.type_.index("insert") == "1.4"


def test_left_after_a_tab_moves_back_over_the_tab(editor):
    put(editor, "\t\tx")
    cursor_at(editor, "1.2")

    editor.left()

    assert editor.type_.index("insert") == "1.1"


def test_right_in_the_indent_moves_forward_a_whole_level(editor):
    put(editor, "        x")
    cursor_at(editor, "1.0")

    editor.right()

    assert editor.type_.index("insert") == "1.4"


def test_left_with_a_selection_jumps_to_its_start_and_closes_it(editor):
    put(editor, "abcdef")
    select(editor, "1.1", "1.4")

    editor.left()

    assert editor.type_.index("insert") == "1.1"
    assert selected(editor) == ""


def test_right_with_a_selection_jumps_to_its_end_and_closes_it(editor):
    put(editor, "abcdef")
    select(editor, "1.1", "1.4")
    cursor_at(editor, "1.1")

    editor.right()

    assert editor.type_.index("insert") == "1.4"
    assert selected(editor) == ""


def test_backspace_deletes_the_previous_character(editor):
    put(editor, "abc")
    cursor_at(editor, "1.2")

    assert editor.backspace() == "break"

    assert text_of(editor) == "ac"


def test_backspace_at_the_start_of_the_text_does_nothing(editor):
    put(editor, "abc")
    cursor_at(editor, "1.0")

    editor.backspace()

    assert text_of(editor) == "abc"


def test_backspace_in_the_indent_deletes_a_whole_level(editor):
    put(editor, "      x")
    cursor_at(editor, "1.6")

    editor.backspace()

    assert text_of(editor) == "    x"


def test_backspace_deletes_a_selection_the_cursor_is_in(editor):
    put(editor, "abcdef")
    select(editor, "1.1", "1.4")

    editor.backspace()

    assert text_of(editor) == "aef"


def test_delete_deletes_the_next_character(editor):
    put(editor, "abc")
    cursor_at(editor, "1.1")

    assert editor.delete_key() == "break"

    assert text_of(editor) == "ac"


def test_delete_in_the_indent_deletes_a_whole_level(editor):
    put(editor, "        x")
    cursor_at(editor, "1.0")

    editor.delete_key()

    assert text_of(editor) == "    x"


def test_delete_deletes_a_selection_the_cursor_is_in(editor):
    put(editor, "abcdef")
    select(editor, "1.1", "1.4")

    editor.delete_key()

    assert text_of(editor) == "aef"


@pytest.mark.parametrize(
    ("text", "start", "forward", "expected"),
    [
        ("one two", "1.7", False, "1.4"),
        ("one two", "1.4", False, "1.0"),
        ("one  two", "1.5", False, "1.0"),
        ("foo.bar", "1.7", False, "1.4"),
        ("foo.bar", "1.4", False, "1.3"),
        ("one two", "1.0", True, "1.3"),
        ("one two", "1.3", True, "1.7"),
        ("foo.bar", "1.3", True, "1.4"),
        ("one\ntwo", "1.3", True, "2.0"),
        ("one\ntwo", "2.0", False, "1.3"),
    ],
)
def test_word_boundaries(editor, text, start, forward, expected):
    put(editor, text)
    cursor_at(editor, start)

    assert editor.type_.index(editor._word_boundary(forward)) == expected


def test_control_arrows_move_by_word(editor):
    put(editor, "one two three")
    cursor_at(editor, "1.0")

    editor.word_right()
    assert editor.type_.index("insert") == "1.3"
    editor.word_right()
    assert editor.type_.index("insert") == "1.7"
    editor.word_left()
    assert editor.type_.index("insert") == "1.4"


def test_control_delete_and_backspace_delete_by_word(editor):
    put(editor, "one two three")
    cursor_at(editor, "1.7")

    editor.delete_word_back()
    assert text_of(editor) == "one  three"
    editor.delete_word_forward()
    assert text_of(editor) == "one "


def test_deleting_by_word_deletes_a_selection_the_cursor_is_in(editor):
    put(editor, "one two three")
    select(editor, "1.4", "1.7")

    editor.delete_word_back()

    assert text_of(editor) == "one  three"


def test_shift_arrows_extend_the_selection(editor):
    put(editor, "abcdef")
    cursor_at(editor, "1.2")

    editor.select_right()
    editor.select_right()
    assert selected(editor) == "cd"
    editor.select_left()
    assert selected(editor) == "c"


def test_control_shift_arrows_extend_the_selection_by_word(editor):
    put(editor, "one two three")
    cursor_at(editor, "1.0")

    editor.select_word_right()
    editor.select_word_right()
    assert selected(editor) == "one two"
    editor.select_word_left()
    assert selected(editor) == "one "


# ---------------------------------------------------------------------------
# The selection point
# ---------------------------------------------------------------------------


def test_the_selection_point_anchors_a_selection(editor, tk_root):
    put(editor, "abcdef")
    cursor_at(editor, "1.1")

    editor.setselpoint()
    cursor_at(editor, "1.4")
    editor.selupdate()

    assert editor.selectionpoint == "1.1"
    assert selected(editor) == "bcd"
    wait_for_message(tk_root, "selection point set at 1.1")


def test_the_selection_can_extend_backwards_from_the_point(editor):
    put(editor, "abcdef")
    editor.setselpoint("1.4")
    cursor_at(editor, "1.1")

    editor.selupdate()

    assert selected(editor) == "bcd"


def test_removing_the_selection_point(editor, tk_root):
    editor.setselpoint("1.0")

    editor.removeselpoint()

    assert editor.selectionpoint is None
    wait_for_message(tk_root, "removed selection point")
    editor.removeselpoint()
    wait_for_message(tk_root, "no selection point set")


def test_toggling_the_selection_point(editor):
    editor.toggleselpoint()
    assert editor.selectionpoint is not None
    editor.toggleselpoint()
    assert editor.selectionpoint is None


# ---------------------------------------------------------------------------
# Go to line, select all, clipboard, undo
# ---------------------------------------------------------------------------


def test_go_to_line_selects_the_line(editor):
    put(editor, "one\ntwo\nthree")

    editor.gl(2)

    assert editor.type_.index("insert") == "2.0"
    assert selected(editor) == "two"


def test_go_to_line_accepts_text(editor):
    put(editor, "one\ntwo")

    editor.gl(" 2 ")

    assert selected(editor) == "two"


def test_go_to_line_with_something_that_is_not_a_number(editor, tk_root):
    editor.gl("abc")

    wait_for_message(tk_root, "cannot go to line number 'abc'")


def test_go_to_line_with_nothing_does_nothing(editor):
    put(editor, "one")

    editor.gl("")

    assert selected(editor) == ""


def test_go_to_line_prompts_when_not_given_a_line(editor, monkeypatch):
    monkeypatch.setattr(utils, "prompt", lambda text, **keywords: "2")
    put(editor, "one\ntwo")

    editor.gl()

    assert selected(editor) == "two"


def test_select_all(editor):
    put(editor, "one\ntwo")

    assert editor.selall() == "break"

    assert selected(editor) == "one\ntwo\n"


def test_copy_puts_the_selection_on_the_clipboard(editor, tk_root):
    put(editor, "copy me")
    select(editor, "1.0", "1.4")

    editor.cp()

    assert tk_root.clipboard_get() == "copy"
    assert text_of(editor) == "copy me"


def test_copy_without_a_selection_says_so(editor, tk_root):
    editor.cp()

    wait_for_message(tk_root, "no text is selected")


def test_cut_removes_the_selection_and_copies_it(editor, tk_root):
    put(editor, "cut me")
    select(editor, "1.0", "1.3")

    editor.cut()

    assert text_of(editor) == " me"
    assert tk_root.clipboard_get() == "cut"


def test_cut_without_a_selection_says_so(editor, tk_root):
    put(editor, "text")

    editor.cut()

    assert text_of(editor) == "text"
    wait_for_message(tk_root, "no text is selected")


def test_paste_inserts_the_clipboard_at_the_cursor(editor, tk_root):
    tk_root.clipboard_clear()
    tk_root.clipboard_append("pasted")
    put(editor, "ab")
    cursor_at(editor, "1.1")

    assert editor.pst() == "break"

    assert text_of(editor) == "apastedb"


def test_paste_with_an_empty_clipboard_says_so(editor, tk_root):
    tk_root.clipboard_clear()

    editor.pst()

    assert text_of(editor) == ""
    wait_for_message(tk_root, "no text is on clipboard")


def test_undo_and_redo(editor, tk_root):
    editor.type_.edit_reset()
    editor.type_.edit_separator()
    put(editor, "typed")
    editor.type_.edit_separator()

    editor.undo()
    assert text_of(editor) == ""
    wait_for_message(tk_root, "undoed edit")
    editor.redo()
    assert text_of(editor) == "typed"
    wait_for_message(tk_root, "redoed edit")


def test_undo_with_nothing_to_undo_says_so(editor, tk_root):
    editor.undo()

    wait_for_message(tk_root, "nothing to undo")


def test_redo_with_nothing_to_redo_says_so(editor, tk_root):
    editor.redo()

    wait_for_message(tk_root, "nothing to redo")


def test_an_undo_mark_is_set_once_per_burst_of_typing(editor):
    editor.undoset = False

    editor._set_undo_mark()
    assert editor.undoset is True
    editor._set_undo_mark()
    assert editor.undoset is True


def test_editing_the_text_allows_a_new_undo_mark(editor, tk_root):
    editor.undoset = True

    put(editor, "x")
    tk_root.update()

    assert editor.undoset is False


# ---------------------------------------------------------------------------
# Bracket matching
# ---------------------------------------------------------------------------


def bracket_tags(editor, tag):
    ranges = [str(index) for index in editor.type_.tag_ranges(tag)]
    return [editor.type_.index(start) for start in ranges[0::2]]


def test_the_bracket_before_the_cursor_is_matched_with_its_partner(editor):
    put(editor, "f(a(b)c)")
    cursor_at(editor, "1.8")

    editor.bracket_match()

    assert bracket_tags(editor, "bracket_matched") == ["1.1", "1.7"]


def test_the_bracket_after_the_cursor_is_used_when_none_is_before_it(editor):
    put(editor, "[x]")
    cursor_at(editor, "1.0")

    editor.bracket_match()

    assert bracket_tags(editor, "bracket_matched") == ["1.0", "1.2"]


def test_matching_works_across_lines_and_for_every_kind(editor):
    put(editor, "{\n  [1,\n  2]\n}")
    cursor_at(editor, "1.1")

    editor.bracket_match()

    assert bracket_tags(editor, "bracket_matched") == ["1.0", "4.0"]


def test_a_bracket_without_a_partner_is_unmatched(editor):
    put(editor, "(abc")
    cursor_at(editor, "1.1")

    editor.bracket_match()

    assert bracket_tags(editor, "bracket_unmatched") == ["1.0"]
    assert bracket_tags(editor, "bracket_matched") == []


def test_moving_away_from_a_bracket_clears_the_highlight(editor):
    put(editor, "(a) b")
    cursor_at(editor, "1.1")
    editor.bracket_match()

    cursor_at(editor, "1.4")
    editor.bracket_match()

    assert bracket_tags(editor, "bracket_matched") == []


# ---------------------------------------------------------------------------
# HModes
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("mode", "expected", "filetype"),
    [
        ("python", "python", "Python File (*.py)"),
        ("py", "python", "Python File (*.py)"),
        ("latex", "latex", "LaTeX / TeX File (*.tex)"),
        ("la", "latex", "LaTeX / TeX File (*.tex)"),
        ("normal", "normal", "Plain Text (*.*)"),
        ("norm", "normal", "Plain Text (*.*)"),
        ("html", "html", "HTML File (*.html)"),
        ("markdown", "markdown", "Markdown File (*.md)"),
        ("md", "markdown", "Markdown File (*.md)"),
    ],
)
def test_switching_the_hmode(editor, mode, expected, filetype):
    editor.pchmode(mode)

    assert editor.hmode == expected
    assert editor.infos["filetype"].cget("text") == filetype


def test_the_latex_toolbar_only_shows_in_latex(editor):
    def toolbar_is_packed():
        outermost = editor.lfouter
        while outermost.master is not editor:
            outermost = outermost.master
        return outermost in editor.pack_slaves()

    editor.pchmode("latex")
    assert toolbar_is_packed()

    editor.pchmode("python")
    assert not toolbar_is_packed()


def test_the_python_and_latex_menus_follow_the_hmode(editor):
    def has(label):
        try:
            editor.m.index(label)
        except Exception:
            return False
        return True

    editor.pchmode("python")
    assert has("Python") and not has("LaTeX")
    editor.pchmode("latex")
    assert has("LaTeX") and not has("Python")
    editor.pchmode("normal")
    assert not has("Python") and not has("LaTeX")


def test_a_plugin_hmode_runs_its_code(editor):
    state.plgnhmodes["Shouting"] = ("/plugins/Loud", "state.shouted = True")

    editor.pchmode("Shouting")

    assert editor.hmode == "Shouting"
    assert state.shouted is True


def test_a_plugin_hmode_with_broken_code_reports_the_error(editor, app):
    state.plgnhmodes["Broken"] = ("/plugins/Broken", "1 / 0")

    editor.pchmode("Broken")

    message = app.dialogs.messages("error")[0]
    assert 'HMode Broken from the plugin "Broken"' in message
    assert "division by zero" in message


def test_files_that_are_only_viewed_keep_their_hmode(editor):
    editor.hmode = "png"

    editor.pchmode("python")

    assert editor.hmode == "png"


def test_switching_the_hmode_runs_the_pycode_hooks(editor):
    seen = []
    state.pcbeforehooks["change-hmode"] = [lambda value: seen.append(("before", value))]
    state.pcafterhooks["change-hmode"] = [lambda value: seen.append(("after", value))]

    editor.pchmode("latex")

    assert seen == [("before", "latex"), ("after", "latex")]


# ---------------------------------------------------------------------------
# The LaTeX toolbar
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("method", "expected"),
    [
        ("boldlatex", "{\\bf word}"),
        ("italiclatex", "\\textit{word}"),
        ("underlinelatex", "\\underline{word}"),
        ("subscriptlatex", "_{word}"),
        ("superscriptlatex", "^{word}"),
    ],
)
def test_text_style_buttons_wrap_the_selection(editor, method, expected):
    put(editor, "word")
    select(editor, "1.0", "1.4")
    cursor_at(editor, "1.0")

    getattr(editor, method)()

    assert text_of(editor) == expected


@pytest.mark.parametrize(
    "method",
    [
        "boldlatex",
        "italiclatex",
        "underlinelatex",
        "subscriptlatex",
        "superscriptlatex",
    ],
)
def test_text_style_buttons_do_nothing_without_a_selection(editor, method):
    put(editor, "word")

    getattr(editor, method)()

    assert text_of(editor) == "word"


def test_numbered_list_wraps_the_selected_lines(editor):
    put(editor, "one\ntwo")
    select(editor, "1.0", "2.3")
    cursor_at(editor, "1.0")

    editor.numberlistlatex()

    assert text_of(editor) == (
        "\n\\begin{enumerate}\n\\item one\n\\item two\n\\end{enumerate}\n"
    )


def test_numbered_list_unwraps_a_selected_list(editor):
    put(editor, "\\begin{enumerate}\n\\item one\n\\item two\n\\end{enumerate}")
    select(editor, "1.0", "end-1c")
    cursor_at(editor, "1.0")

    editor.numberlistlatex()

    assert text_of(editor) == "\none\ntwo\n"


def test_numbered_list_without_a_selection_inserts_an_empty_one(editor):
    editor.numberlistlatex()

    assert text_of(editor) == "\n\\begin{enumerate}\n\n\\end{enumerate}\n"


def test_bullet_list_wraps_the_selected_lines(editor):
    put(editor, "one\ntwo")
    select(editor, "1.0", "2.3")
    cursor_at(editor, "1.0")

    editor.bulletlistlatex()

    assert text_of(editor) == (
        "\n\\begin{itemize}\n\\item one\n\\item two\n\\end{itemize}\n"
    )


def test_bullet_list_unwraps_a_selected_list(editor):
    put(editor, "\\begin{itemize}\n\\item one\n\\end{itemize}")
    select(editor, "1.0", "end-1c")
    cursor_at(editor, "1.0")

    editor.bulletlistlatex()

    assert text_of(editor) == "\none\n"


def test_bullet_list_without_a_selection_inserts_an_empty_one(editor):
    editor.bulletlistlatex()

    assert text_of(editor) == "\n\\begin{itemize}\n\n\\end{itemize}\n"


def test_paragraph_inserts_par(editor):
    editor.paragraphlatex()

    assert text_of(editor) == "\\par\n"


def test_equation_wraps_the_selection_with_line_breaks(editor):
    put(editor, "a=1\nb=2")
    select(editor, "1.0", "2.3")
    cursor_at(editor, "1.0")

    editor.equationlatex()

    assert text_of(editor) == "\n\\begin{equation}\na=1\\\\\nb=2\n\\end{equation}\n"


def test_equation_without_a_selection_inserts_an_empty_one(editor):
    editor.equationlatex()

    assert text_of(editor) == (
        "\n\\begin{equation}\n\\begin{split}\n\n\\end{split}\n\\end{equation}\n"
    )


@pytest.mark.parametrize(
    ("kind", "expected"),
    [
        ("Section", "\n\\section{Section}\n"),
        ("Subsection", "\n\\subsection{Section}\n"),
        ("Subsubsection", "\n\\subsubsection{Section}\n"),
    ],
)
def test_section_inserts_a_heading(editor, kind, expected):
    editor.sectionlatex(kind)

    assert text_of(editor) == expected


@pytest.mark.parametrize(
    ("name", "latex"),
    [
        ("Multiplication", "\\times"),
        ("Division", "\\div"),
        ("Less or equal", "\\leq"),
        ("Not equal", "\\neq"),
        ("Infinity", "\\infty"),
        ("Summation", "\\sum"),
        ("Integral", "\\int"),
        ("Pi", "\\pi"),
        ("Theta", "\\theta"),
        ("Alpha Lower", "\\alpha"),
        ("Inline Math", "$$"),
    ],
)
def test_math_symbols(editor, name, latex):
    editor.mathlatex(name)

    assert text_of(editor) == latex


# ---------------------------------------------------------------------------
# Helpers for the LaTeX, HTML and Markdown highlighters
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("function", "text", "start", "expected"),
    [
        (editor_module._find_closing_brace, "{a}b", 0, 3),
        (editor_module._find_closing_brace, "{a{b}c}d", 0, 7),
        (editor_module._find_closing_brace, "{a\\}b}", 0, 6),
        (editor_module._find_closing_brace, "{abc", 0, 4),
        (editor_module._find_closing_bracket, "[a]b", 0, 3),
        (editor_module._find_closing_bracket, "[a[b]c]d", 0, 7),
        (editor_module._find_closing_bracket, "[a\\]b]", 0, 6),
        (editor_module._find_closing_bracket, "[abc", 0, 4),
        (editor_module._find_closing_tag, '<a href="x">t', 0, 12),
        (editor_module._find_closing_tag, '<a title=">">t', 0, 13),
        (editor_module._find_closing_tag, "<a title='>'>t", 0, 13),
        (editor_module._find_closing_tag, "<a", 0, 2),
    ],
)
def test_closing_delimiter_search(function, text, start, expected):
    assert function(text, start) == expected


# ---------------------------------------------------------------------------
# Syntax highlighting applied to the text
# ---------------------------------------------------------------------------


def tagged(editor, tag):
    """The texts the tag covers in the editor."""
    ranges = [str(index) for index in editor.type_.tag_ranges(tag)]
    return [editor.type_.get(a, b) for a, b in zip(ranges[0::2], ranges[1::2])]


def highlight_all(editor, root, mode, text):
    """Switch to mode, type text, and wait until the whole text was
    highlighted."""
    editor.pchmode(mode)
    put(editor, text)
    editor.type_top, editor.type_bottom = "1.0", "end"
    editor.ha(mode)
    wait_for(root, lambda: not editor._ha_running[0], "the highlighting")
    root.update()


def test_python_code_is_highlighted_as_it_is_typed(editor, tk_root):
    editor.pchmode("python")
    put(editor, "def f(a):\n    return a + 1\n")
    editor.type_top, editor.type_bottom = "1.0", "end"
    editor.keypress()

    wait_for(tk_root, lambda: tagged(editor, "hpf"), "the Python highlighting")
    wait_for(tk_root, lambda: not editor._ha_running[0], "the highlighting to end")

    assert tagged(editor, "hpa") == ["def", "return"]
    assert tagged(editor, "hpf") == ["f"]
    assert tagged(editor, "hpfa") == ["a", "a"]
    assert tagged(editor, "hpo") == ["+"]


def test_highlighting_follows_an_edit(editor, tk_root):
    editor.pchmode("python")
    put(editor, "x = 1\n")
    editor.type_top, editor.type_bottom = "1.0", "end"
    editor.keypress()
    wait_for(tk_root, lambda: tagged(editor, "hpv"), "the first highlighting")

    put(editor, "y = 2\n", "end-1c")
    editor.type_top, editor.type_bottom = "1.0", "end"
    editor.keypress()

    wait_for(tk_root, lambda: tagged(editor, "hpv") == ["x", "y"], "the new variable")


def test_latex_is_highlighted(editor, tk_root):
    highlight_all(
        editor,
        tk_root,
        "latex",
        "% note\n\\section{Title}\nText $x^2$ \\textbf{bold}[opt] \\\\\n",
    )

    assert tagged(editor, "hlh") == ["% note\n"]
    assert tagged(editor, "hld") == ["\\section", "\\textbf"]
    assert tagged(editor, "hle") == ["{Title}", "{bold}"]
    assert tagged(editor, "hlg") == ["[opt]"]
    assert tagged(editor, "hlf") == ["\\\\"]
    assert tagged(editor, "hla") == ["$x^2$"]


def test_html_is_highlighted(editor, tk_root):
    highlight_all(
        editor,
        tk_root,
        "html",
        '<!-- c --><div class="a b" id=x disabled>text</div>\n',
    )

    assert tagged(editor, "hcmt") == ["<!-- c -->"]
    assert tagged(editor, "hattr") == ["class", "id", "disabled"]
    assert tagged(editor, "hstr") == ['"a b"', "x"]
    assert "</div>" in tagged(editor, "hstuff")


def test_markdown_is_highlighted(editor, tk_root):
    highlight_all(
        editor,
        tk_root,
        "markdown",
        "# H1\n## H2\n**bold** *it* ***both*** ~~s~~ `code` [l](u)\n> quote\n",
    )

    assert tagged(editor, "hmh1") == ["# H1"]
    assert tagged(editor, "hmh2") == ["## H2"]
    assert tagged(editor, "hmb") == ["**bold**"]
    assert tagged(editor, "hmi") == ["*it*"]
    assert tagged(editor, "hmbi") == ["***both***"]
    assert tagged(editor, "hms") == ["~~s~~"]
    assert tagged(editor, "hmc") == ["`code`"]
    assert tagged(editor, "hml") == ["[l](u)"]
    assert tagged(editor, "hmq") == ["> quote"]


def test_markdown_fenced_code_is_highlighted(editor, tk_root):
    highlight_all(
        editor, tk_root, "markdown", "text\n```\n# not a header\n```\nafter\n"
    )

    assert tagged(editor, "hmf") == ["```\n# not a header\n```\n"]
    assert tagged(editor, "hmh1") == []


def test_normal_text_has_no_highlighting(editor, tk_root):
    highlight_all(editor, tk_root, "normal", "if x: 'string' # note\n")

    assert tagged(editor, "hpa") == []
    assert tagged(editor, "hpd") == []


def test_switching_the_hmode_removes_the_old_highlighting(editor, tk_root):
    highlight_all(editor, tk_root, "latex", "\\section{Title}\n")
    assert tagged(editor, "hld")

    editor.pchmode("normal")

    assert tagged(editor, "hld") == []


def test_a_plugin_can_highlight_with_patterns(editor, tk_root):
    state.plugin_hl["normal"] = {
        "plugin": "Demo",
        "if": "True",
        "hl": "{'shout': (__import__('re').compile(r'[A-Z]{3,}'), 'python:strings')}",
    }
    editor.type_.tag_configure("shout")

    highlight_all(editor, tk_root, "normal", "a LOUD word and QUIET one\n")

    assert tagged(editor, "shout") == ["LOUD", "QUIET"]
    assert editor.type_.tag_cget("shout", "foreground") == "#15803D"


def test_a_plugin_can_highlight_with_a_function(editor, tk_root):
    def mark_first_character(text, top, ops):
        ops.append(("add", "firsttag", f"{top}+0c", f"{top}+1c"))

    state.plugin_hl["normal"] = mark_first_character
    editor.type_.tag_configure("firsttag")

    highlight_all(editor, tk_root, "normal", "hello")

    assert tagged(editor, "firsttag") == ["h"]


def test_a_plugin_function_that_fails_reports_the_error(editor, tk_root, app):
    def broken(text, top, ops):
        raise RuntimeError("plugin broke")

    state.plugin_hl["normal"] = broken

    highlight_all(editor, tk_root, "normal", "hello")

    assert "plugin broke" in app.dialogs.messages("error")[0]


def test_a_plugin_dict_runs_its_function_and_condition(editor, tk_root):
    state.plugin_hl["normal"] = {
        "plugin": "Demo",
        "func": "state.ran_function = True",
        "if": "state.ran_function",
        "hl": "{'demotag': (__import__('re').compile('e'), 'python:strings')}",
    }
    editor.type_.tag_configure("demotag")

    highlight_all(editor, tk_root, "normal", "e e")

    assert state.ran_function is True
    assert tagged(editor, "demotag") == ["e", "e"]


def test_a_plugin_dict_runs_its_else_block_when_the_condition_is_false(editor, tk_root):
    state.plugin_hl["normal"] = {
        "plugin": "Demo",
        "if": "False",
        "else": "state.took_else = True",
    }

    highlight_all(editor, tk_root, "normal", "x")

    assert state.took_else is True


def test_a_plugin_condition_that_fails_reports_the_error(editor, tk_root, app):
    state.plugin_hl["normal"] = {"plugin": "Demo", "if": "1 / 0"}

    highlight_all(editor, tk_root, "normal", "x")

    assert 'condition "1 / 0"' in app.dialogs.messages("error")[0]


def test_highlighting_requested_while_it_runs_is_run_afterwards(editor, tk_root):
    editor.pchmode("normal")
    put(editor, "text")
    editor.type_top, editor.type_bottom = "1.0", "end"
    editor._ha_running[0] = True

    editor.ha("normal")

    assert editor._ha_pending[0] == "normal"
    editor._ha_running[0] = False
    editor._ha_pending[0] = None


def test_a_theme_change_reconfigures_the_highlight_tags(editor):
    assert editor.type_.tag_cget("hpa", "foreground") == "#7C3AED"
    state.theme["python:keywords"] = "foreground = '#112233'"

    editor_module._init_hl_tags()

    assert editor.type_.tag_cget("hpa", "foreground") == "#112233"


def test_bracket_highlight_colors_come_from_the_theme(editor):
    assert editor.type_.tag_cget("bracket_matched", "background") == "#40e0d0"
    assert editor.type_.tag_cget("bracket_unmatched", "background") == "#FF0000"


# ---------------------------------------------------------------------------
# Running code
# ---------------------------------------------------------------------------


@pytest.fixture
def terminals(monkeypatch):
    """The terminal buffers a run would open, recorded instead of opened."""
    opened = []

    def term(command, **keywords):
        opened.append((command, keywords))

    monkeypatch.setattr(editor_module.terminal, "term", term)
    return opened


def test_running_python_saves_the_file_and_runs_it(editor, terminals, tmp_path):
    path = tmp_path / "work" / "run.py"
    path.write_text("")
    editor.ld(str(path))
    put(editor, "print(1)")

    editor.rp()

    assert path.read_text() == "print(1)"
    ((command, keywords),) = terminals
    assert command == [state.pythonexecutable, str(path)]
    assert keywords["title"] == f"*{path} Running*"
    assert keywords["endmessage"].startswith("--- Python code finished")


def test_running_untitled_python_uses_a_temporary_file(editor, terminals, app):
    put(editor, "print(2)")

    editor.rp()

    temporary = app.home / ".local" / "share" / "PyNotes" / "tempcode"
    assert temporary.read_text() == "print(2)"
    assert terminals[0][0] == [state.pythonexecutable, str(temporary)]


def test_running_html_opens_it_with_the_system(editor, monkeypatch, app, tmp_path):
    runs = []
    monkeypatch.setattr(
        editor_module.subprocess, "run", lambda *a, **k: runs.append((a, k))
    )
    path = tmp_path / "work" / "page.html"
    path.write_text("")
    editor.ld(str(path))
    put(editor, "<p>hi</p>")

    editor.hp()

    assert path.read_text() == "<p>hi</p>"
    assert runs == [((["xdg-open", str(path)],), {"cwd": str(path.parent)})]


def test_running_untitled_html_uses_a_temporary_file(editor, monkeypatch, app):
    runs = []
    monkeypatch.setattr(editor_module.subprocess, "run", lambda *a, **k: runs.append(a))
    put(editor, "<p>hi</p>")

    editor.hp()

    temporary = app.home / ".local" / "share" / "PyNotes" / "tempcode"
    assert temporary.read_text() == "<p>hi</p>"
    assert runs == [(["xdg-open", str(temporary)],)]


def test_latex_without_a_compiler_is_an_error(editor, monkeypatch, app):
    monkeypatch.setattr(editor_module.shutil, "which", lambda name: None)

    editor.runtex("lua")

    assert app.dialogs.messages("error") == [
        "Error in running LaTeX - lualatex is not installed"
    ]


def test_latex_is_compiled_and_the_pdf_shown(editor, terminals, monkeypatch, tmp_path):
    shown = []
    monkeypatch.setattr(editor_module.shutil, "which", lambda name: "/bin/" + name)
    monkeypatch.setattr(editor_module.dialogs, "pdf", lambda file: shown.append(file))
    path = tmp_path / "work" / "doc.tex"
    path.write_text("")
    editor.ld(str(path))
    (tmp_path / "work" / "doc.pdf").write_text("old pdf")
    put(editor, "\\documentclass{article}")

    editor.runtex("pdf")

    assert not (tmp_path / "work" / "doc.pdf").exists()
    ((command, keywords),) = terminals
    assert command == [
        "pdflatex",
        str(path),
        f"--output-directory={path.parent}",
    ]
    assert keywords["blocking"] is True
    assert shown == [str(path)]


def test_run_code_picks_the_runner_by_hmode(editor, monkeypatch):
    calls = []
    monkeypatch.setattr(editor, "rp", lambda: calls.append("python"))
    monkeypatch.setattr(editor, "runtex", lambda compiler: calls.append(compiler))
    monkeypatch.setattr(editor, "hp", lambda: calls.append("html"))

    for mode in ("python", "latex", "html"):
        editor.hmode = mode
        editor.f5()

    assert calls == ["python", "lua", "html"]


def test_run_code_in_another_hmode_says_so(editor, tk_root):
    editor.hmode = "normal"

    editor.f5()

    wait_for_message(tk_root, "hmode not in python / latex / html")


def test_run_code_is_refused_while_an_outside_change_is_pending(editor, tk_root):
    editor._file_watch_prompt_pending = True

    editor.f5()

    wait_for(
        tk_root,
        lambda: shown().startswith("select 'Discard Changes & Reload'"),
        "the message",
    )


# ---------------------------------------------------------------------------
# Backups
# ---------------------------------------------------------------------------


def test_a_backup_is_written_next_to_the_file(editor, monkeypatch, tmp_path):
    monkeypatch.setattr(state, "bfr", True)
    path = tmp_path / "work" / "notes.txt"
    path.write_text("")
    editor.ld(str(path))
    put(editor, "backed up")

    editor.do_backup()

    backup = tmp_path / "work" / ".notesbackpynotes.txt"
    assert backup.read_text() == "backed up\n"


def test_no_backup_is_written_when_backups_are_off(editor, monkeypatch, tmp_path):
    monkeypatch.setattr(state, "bfr", False)
    path = tmp_path / "work" / "notes.txt"
    path.write_text("")
    editor.ld(str(path))

    editor.do_backup()

    assert not (tmp_path / "work" / ".notesbackpynotes.txt").exists()


def test_no_backup_is_written_for_an_untitled_editor(editor, monkeypatch, tmp_path):
    monkeypatch.setattr(state, "bfr", True)
    put(editor, "text")

    editor.do_backup()

    assert [path.name for path in (tmp_path / "work").iterdir()] == []


# ---------------------------------------------------------------------------
# The room below the last line
# ---------------------------------------------------------------------------


def test_the_end_of_the_text_is_where_a_plain_text_widget_puts_it(editor):
    put(editor, "one\ntwo")

    assert editor.type_.index("end") == "3.0"
    assert editor.type_.get("1.0", "end") == "one\ntwo\n"
    assert editor.type_.index("end-1c") == "2.3"


def test_nothing_can_be_inserted_past_the_end(editor):
    put(editor, "one")

    editor.type_.insert("end", "two")
    editor.type_.insert("end + 5 lines", "three")

    assert text_of(editor) == "onetwothree"


def test_deleting_to_the_end_keeps_the_text_valid(editor):
    put(editor, "one\ntwo")

    editor.type_.delete("1.2", "end")

    assert text_of(editor) == "on"


def test_the_text_always_ends_with_the_hidden_newline(editor):
    put(editor, "one")

    assert editor._own_type.inner.get("1.0", "end").endswith("\n")
