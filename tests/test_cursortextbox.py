"""CustomTextbox: a text box whose cursor is a label laid over the text, so
that it can have any shape and color and show the character under it."""

import pytest

import cursortextbox
from cursortextbox import CustomTextbox
from terminal_helpers import relayout

pytestmark = pytest.mark.display


@pytest.fixture
def box(app, tk_root):
    textbox = CustomTextbox(
        tk_root, cursor_shape="block", font=("monospace", 12), width=20, height=5
    )
    textbox.place(x=0, y=0, width=300, height=200)
    relayout(tk_root, textbox)
    textbox._cursor_focus_in(None)  # the text has the focus
    yield textbox
    textbox.destroy()


def label_box(box):
    box.redraw_cursor()
    info = box._cursor_label.place_info()
    return tuple(int(info[key]) for key in ("x", "y", "width", "height"))


def cell(box):
    font = str(box.inner.cget("font"))
    width = box._font_measure(font, " ")
    height = box._font_metric(font, "-ascent") + box._font_metric(font, "-descent")
    return width, height


def is_shown(box):
    return box._cursor_label.winfo_manager() == "place"


# ---------------------------------------------------------------------------
# Options
# ---------------------------------------------------------------------------


def test_the_defaults(app, tk_root):
    textbox = CustomTextbox(tk_root)
    try:
        assert textbox.cursor_shape == "line"
        assert textbox.cursor_blink is True
        assert textbox.cursor_thickness == 2
        assert textbox.cursor_visible is True
        assert textbox.cursor_follows_text_colors is False
    finally:
        textbox.destroy()


def test_the_shapes():
    assert cursortextbox.CURSOR_SHAPES == ("line", "block", "underline")


def test_an_invalid_shape_is_refused(app, tk_root):
    with pytest.raises(ValueError, match="cursor_shape must be one of"):
        CustomTextbox(tk_root, cursor_shape="triangle")


def test_the_shape_can_be_changed_later(box):
    box.set_cursor_shape("underline")
    assert box.cursor_shape == "underline"
    with pytest.raises(ValueError):
        box.set_cursor_shape("triangle")
    assert box.cursor_shape == "underline"


def test_options_can_be_changed_with_configure(box):
    box.configure(cursor_shape="line", cursor_thickness=4, cursor_blink=False)

    assert (box.cursor_shape, box.cursor_thickness, box.cursor_blink) == (
        "line",
        4,
        False,
    )
    with pytest.raises(ValueError):
        box.configure(cursor_shape="triangle")


# ---------------------------------------------------------------------------
# Where and how big the cursor is
# ---------------------------------------------------------------------------


def test_the_block_cursor_covers_the_character_it_is_on(box):
    box.insert("1.0", "abc")
    box.mark_set("insert", "1.1")

    x, y, width, height = label_box(box)
    bbox = box.inner.bbox("1.1")

    assert (x, width) == (bbox[0], bbox[2])
    assert height == cell(box)[1]
    assert box._cursor_label.cget("text") == "b"


def test_the_cursor_moves_with_the_insert_mark(box):
    box.insert("1.0", "abc")
    box.mark_set("insert", "1.0")
    first = label_box(box)
    box.mark_set("insert", "1.2")
    second = label_box(box)

    assert second[0] > first[0] and second[1] == first[1]


def test_the_cursor_follows_the_line(box):
    box.insert("1.0", "abc\ndef")
    box.mark_set("insert", "1.0")
    first = label_box(box)
    box.mark_set("insert", "2.0")
    second = label_box(box)

    assert second[0] == first[0] and second[1] > first[1]


def test_the_line_cursor_is_a_thin_bar(box):
    box.insert("1.0", "abc")
    box.set_cursor_shape("line")

    _, _, width, height = label_box(box)

    assert width == box.cursor_thickness
    assert height == cell(box)[1]
    assert box._cursor_label.cget("text") == ""


def test_the_line_thickness_is_used(box):
    box.set_cursor_shape("line")
    box.configure(cursor_thickness=5)

    assert label_box(box)[2] == 5


def test_the_underline_cursor_is_a_bar_at_the_bottom_of_the_cell(box):
    box.insert("1.0", "abc")
    block = label_box(box)
    box.set_cursor_shape("underline")

    x, y, width, height = label_box(box)

    assert (x, width) == (block[0], block[2])
    assert height == box.cursor_thickness
    assert y + height == block[1] + block[3]


def test_a_thin_cursor_is_at_least_one_pixel(box):
    box.set_cursor_shape("line")
    box.configure(cursor_thickness=0)

    assert label_box(box)[2] == 1


def test_a_tab_is_covered_by_one_ordinary_cell(box):
    box.insert("1.0", "\tx")
    box.mark_set("insert", "1.0")

    _, _, width, _ = label_box(box)

    assert width == cell(box)[0]
    assert box._cursor_label.cget("text") == " "


def test_at_the_end_of_the_text_the_cursor_is_an_empty_cell(box):
    box.insert("1.0", "abc")
    box.mark_set("insert", "1.3")

    _, _, width, _ = label_box(box)

    assert width == cell(box)[0]
    assert box._cursor_label.cget("text") == " "


def test_on_an_empty_line_the_cursor_is_a_cell(box):
    box.insert("1.0", "\n\nx")
    box.mark_set("insert", "2.0")

    assert label_box(box)[2:] == cell(box)


def test_a_larger_font_on_the_character_makes_a_larger_cursor(box):
    box.insert("1.0", "abc")
    box.tag_configure("big", font=("monospace", 24))
    box.tag_add("big", "1.1", "1.2")
    box.mark_set("insert", "1.1")

    _, _, width, height = label_box(box)

    assert width > cell(box)[0]
    assert height > cell(box)[1]


def test_the_cursor_at_the_end_of_big_text_takes_its_font(box):
    box.insert("1.0", "abc")
    box.tag_configure("big", font=("monospace", 24))
    box.tag_add("big", "1.0", "1.3")
    box.mark_set("insert", "1.3")

    _, _, width, height = label_box(box)

    assert width > cell(box)[0]


def test_wide_characters_are_covered_whole(box):
    box.insert("1.0", "世x")
    box.mark_set("insert", "1.0")

    _, _, width, _ = label_box(box)

    assert width >= box.inner.bbox("1.0")[2] > 0


def test_half_of_an_emoji_shows_the_whole_character(box):
    box.insert("1.0", "😀")
    box.mark_set("insert", "1.0")

    box.redraw_cursor()

    assert box._cursor_label.cget("text") == "😀"


# ---------------------------------------------------------------------------
# Colors
# ---------------------------------------------------------------------------


def test_the_cursor_uses_the_theme_colors_by_default(box):
    box.insert("1.0", "abc")
    box.redraw_cursor()
    label = box._cursor_label

    assert label.cget("bg") != label.cget("fg")
    assert label.cget("fg").lower() == box.rc(box.inner.cget("background")).lower()


def test_a_cursor_color_of_its_own(box):
    box.insert("1.0", "abc")
    box.configure(cursor_color="#ff0000")
    box.redraw_cursor()

    assert box._cursor_label.cget("bg").lower() == "#ff0000"


def test_the_cursor_can_take_the_colors_of_the_character(box):
    box.configure(cursor_follows_text_colors=True)
    box.insert("1.0", "abc")
    box.tag_configure("red", foreground="#cd0000", background="#101010")
    box.tag_add("red", "1.0", "1.1")
    box.mark_set("insert", "1.0")
    box.redraw_cursor()
    label = box._cursor_label

    assert label.cget("bg").lower() == "#cd0000"
    assert label.cget("fg").lower() == "#101010"


def test_the_selection_tag_does_not_color_the_cursor(box):
    box.configure(cursor_follows_text_colors=True)
    box.insert("1.0", "abc")
    box.tag_add("sel", "1.0", "1.2")
    box.mark_set("insert", "1.0")

    assert "sel" not in box.cursor_text_tags("1.0")


def test_a_color_of_its_own_wins_over_the_text_colors(box):
    box.configure(cursor_follows_text_colors=True, cursor_color="#00ff00")
    box.insert("1.0", "abc")
    box.tag_configure("red", foreground="#cd0000")
    box.tag_add("red", "1.0", "1.1")
    box.mark_set("insert", "1.0")
    box.redraw_cursor()

    assert box._cursor_label.cget("bg").lower() == "#00ff00"


# ---------------------------------------------------------------------------
# When the cursor shows
# ---------------------------------------------------------------------------


def test_the_cursor_shows_while_the_text_has_the_focus(box):
    box.redraw_cursor()

    assert is_shown(box)


def test_the_cursor_hides_when_the_focus_is_lost(box):
    box.redraw_cursor()

    box._cursor_focus_out(None)
    box.redraw_cursor()

    assert not is_shown(box)


def test_the_cursor_can_be_hidden(box):
    box.set_cursor_visible(False)
    box.redraw_cursor()

    assert not is_shown(box)
    box.set_cursor_visible(True)
    box.redraw_cursor()
    assert is_shown(box)


def test_a_disabled_text_has_no_cursor(box):
    box.configure(state="disabled")
    box.redraw_cursor()

    assert not is_shown(box)


def test_the_cursor_is_hidden_when_its_character_is_not_on_screen(box):
    box.insert("1.0", "\n".join(str(n) for n in range(100)))
    box.mark_set("insert", "100.0")
    box.yview_moveto(0)
    box.redraw_cursor()

    assert not is_shown(box)


def test_the_cursor_is_hidden_while_in_the_hidden_half_of_the_blink(box):
    box._cursor_blink_phase = False
    box.redraw_cursor()

    assert not is_shown(box)


# ---------------------------------------------------------------------------
# Blinking and redrawing
# ---------------------------------------------------------------------------


def test_the_blink_timer_runs_only_for_a_visible_focused_blinking_cursor(box):
    assert box._cursor_blink_call is not None
    box.set_cursor_blink(False)
    assert box._cursor_blink_call is None
    box.set_cursor_blink(True)
    assert box._cursor_blink_call is not None
    box._cursor_focus_out(None)
    assert box._cursor_blink_call is None
    box._cursor_focus_in(None)
    box.set_cursor_visible(False)
    assert box._cursor_blink_call is None


def test_a_blink_tick_toggles_the_cursor(box):
    assert box._cursor_blink_phase is True

    box._cursor_blink_tick()
    assert box._cursor_blink_phase is False
    assert not is_shown(box)
    box._cursor_blink_tick()
    assert box._cursor_blink_phase is True
    assert is_shown(box)


def test_the_hidden_half_of_the_blink_is_shorter(box):
    assert box.CURSOR_BLINK_ON_MS > box.CURSOR_BLINK_OFF_MS


def test_the_cursor_is_solid_while_it_moves(box):
    box._cursor_blink_phase = False

    box.reset_cursor_blink()

    assert box._cursor_blink_phase is True


def test_redraws_are_collected_until_idle(box, tk_root, monkeypatch):
    tk_root.update()
    redraws = []
    monkeypatch.setattr(box, "redraw_cursor", lambda: redraws.append(True))

    box.schedule_cursor_redraw()
    box.schedule_cursor_redraw()
    box.schedule_cursor_redraw()
    assert redraws == []
    tk_root.update()

    assert redraws == [True]


def test_changing_text_tags_redraws_the_cursor(box, tk_root, monkeypatch):
    box.insert("1.0", "abc")
    tk_root.update()
    redraws = []
    monkeypatch.setattr(box, "redraw_cursor", lambda: redraws.append(True))

    box.tag_configure("t", foreground="red")
    box.tag_add("t", "1.0", "1.1")
    box.tag_remove("t", "1.0", "1.1")
    box.tag_raise("t")
    box.tag_lower("t")
    box.tag_delete("t")
    tk_root.update()

    assert redraws == [True]


def test_stopping_the_timers_cancels_the_blink_and_the_redraw(box):
    box.schedule_cursor_redraw()
    box._cursor_blink_phase = False

    box.stop_cursor_timers()

    assert box._cursor_blink_call is None
    assert box._cursor_redraw_call is None
    assert box._cursor_blink_phase is True


def test_a_theme_change_redraws_the_cursor(box, tk_root, monkeypatch):
    tk_root.update()
    redraws = []
    monkeypatch.setattr(box, "redraw_cursor", lambda: redraws.append(True))

    box.on_theme_changed()
    tk_root.update()

    assert redraws


def test_a_text_that_keeps_its_cursor_elsewhere(app, tk_root):
    class Elsewhere(CustomTextbox):
        def cursor_index(self):
            return "1.2"

    textbox = Elsewhere(
        tk_root, follow_insert=False, cursor_shape="block", font=("monospace", 12)
    )
    textbox.place(x=0, y=0, width=300, height=100)
    relayout(tk_root, textbox)
    textbox.insert("1.0", "abcdef")
    textbox._cursor_focus_in(None)
    textbox.mark_set("insert", "1.0")
    try:
        textbox.redraw_cursor()

        assert textbox._cursor_label.cget("text") == "c"
    finally:
        textbox.destroy()


# ---------------------------------------------------------------------------
# Mouse clicks on the cursor
# ---------------------------------------------------------------------------


def test_presses_are_remembered_to_count_multiple_clicks(box):
    event = lambda t, x=5, y=5: type("E", (), {"time": t, "x": x, "y": y})()

    for t in (100, 200, 300, 400):
        box._cursor_press_seen(event(t))

    assert [press[0] for press in box._cursor_presses] == [200, 300, 400]


def test_clicks_close_together_make_a_multiple_click(box):
    box._cursor_presses = [(100, 5, 5), (300, 5, 5), (400, 5, 5)]

    earlier = box._cursor_earlier_clicks(500, 5, 5)

    assert earlier == [(100, 5, 5), (300, 5, 5), (400, 5, 5)]


def test_clicks_too_far_apart_in_time_or_space_do_not(box):
    box._cursor_presses = [(0, 5, 5), (700, 5, 5), (800, 50, 5)]

    assert box._cursor_earlier_clicks(900, 5, 5) == []
    assert box._cursor_earlier_clicks(900, 50, 5) == [(800, 50, 5)]


def test_the_pointer_crossing_between_the_text_and_its_cursor_is_hidden(
    box, tk_root, monkeypatch
):
    box.insert("1.0", "abc")
    box.mark_set("insert", "1.0")
    box.redraw_cursor()
    tk_root.update()
    label = box._cursor_label
    monkeypatch.setattr(label, "winfo_ismapped", lambda: True)
    onto = type(
        "E",
        (),
        {"x": label.winfo_x() + 1, "y": label.winfo_y() + 1, "widget": box.inner},
    )()
    away = type("E", (), {"x": 250, "y": 150, "widget": box.inner})()

    assert box._cursor_text_left(onto) == "break"
    assert box._cursor_text_entered(away) == "break"
    assert box._cursor_text_entered(away) is None
    assert box._cursor_text_left(away) is None
