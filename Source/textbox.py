"""A text box whose cursor is drawn by PyNotes itself instead of by tkinter, so
that it can have several shapes and any color, and so that its block shape shows
the character under it. Meant for everything in PyNotes that needs more than
tkinter's thin insertion cursor, such as the editors."""

import tkinter as tk

import canvastk as ctk

CURSOR_SHAPES = ("line", "block", "underline")


class CustomTextbox(ctk.Textbox):
    """A canvastk Textbox with a cursor drawn using a Label placed over the text.

    The cursor follows the character it is on, whatever its font: its position and
    size come from the box the text widget reports for that character, so it fits any
    font, any size, and fonts that tags apply to part of the text, and it moves with
    every change of the text, the view, the size, and the fonts.

    Options, all of which can also be changed later with configure():
    cursor_shape: "line" (a thin vertical line, the default), "block" (covers the
    character and shows it in inverted colors), or "underline". cursor_blink: whether
    it blinks. cursor_thickness: the width in px of the line, the height of the
    underline. cursor_visible: whether it is shown at all (it is only ever shown
    while the text has the keyboard focus and is not disabled). cursor_color: its
    color (the text color of the theme by default); insertbackground is the same.
    cursor_follows_text_colors: with no color of its own, the cursor takes the color
    of the character under it, and the block takes the background of it for the
    character it shows.

    follow_insert (a constructor option only): whether the cursor is drawn at the
    insert mark and follows it by itself. Pass False for a text that keeps its cursor
    somewhere else; it then overrides cursor_index() and calls schedule_cursor_redraw()
    whenever the cursor moves or the text under it changes.
    """

    _OWN_OPTIONS = ctk.Textbox._OWN_OPTIONS + (
        "cursor_shape",
        "cursor_blink",
        "cursor_thickness",
        "cursor_visible",
        "cursor_follows_text_colors",
    )
    CURSOR_BLINK_ON_MS = 600  # how long the cursor is shown in each blink cycle
    CURSOR_BLINK_OFF_MS = 300  # and how long it is hidden
    # The mouse events that happen on the cursor itself, which are handed on to the
    # text under it.
    _CURSOR_PASSED_EVENTS = (
        "<ButtonPress-1>",
        "<ButtonPress-2>",
        "<ButtonPress-3>",
        "<ButtonRelease-1>",
        "<ButtonRelease-2>",
        "<ButtonRelease-3>",
        "<B1-Motion>",
        "<B2-Motion>",
        "<B3-Motion>",
        "<Motion>",
        "<MouseWheel>",
        "<Button-4>",
        "<Button-5>",
    )
    _cursor_label = None  # made at the end of __init__

    def __init__(
        self,
        master,
        *args,
        cursor_shape="line",
        cursor_blink=True,
        cursor_thickness=2,
        cursor_follows_text_colors=False,
        follow_insert=True,
        **kwargs,
    ):
        """Create the text box. See the class for the cursor options; everything else
        is for canvastk's Textbox.
        """
        self._check_cursor_shape(cursor_shape)
        super().__init__(master, *args, **kwargs)
        self.cursor_shape = cursor_shape
        self.cursor_blink = bool(cursor_blink)
        self.cursor_thickness = cursor_thickness
        self.cursor_visible = True
        self.cursor_follows_text_colors = bool(cursor_follows_text_colors)
        self._cursor_focused = False
        self._cursor_focus_seen = False  # whether a focus event has told us yet
        self._cursor_blink_phase = True  # in the shown half of the blink
        self._cursor_blink_call = None
        self._cursor_redraw_call = None
        self._cursor_appearance = None  # what the label shows right now
        self._cursor_placement = None  # where the label is placed right now
        self._cursor_xview_command = None
        text = self.inner
        text.configure(insertwidth=0, insertontime=0)  # hide tkinter's own cursor
        self._cursor_label = self._make_cursor_label()
        text.bind("<FocusIn>", self._cursor_focus_in, add="+")
        text.bind("<FocusOut>", self._cursor_focus_out, add="+")
        text.bind("<Configure>", lambda _: self.schedule_cursor_redraw(), add="+")
        text.bind("<Map>", lambda _: self.schedule_cursor_redraw(), add="+")
        text.bind("<Destroy>", self._cursor_text_destroyed, add="+")
        if follow_insert:
            # Every change of the text, the insert mark, and the view raises this
            # event (see canvastk's Textbox); the view scrolling sideways is followed
            # separately.
            self._install_change_event()
            text.bind("<<TextboxChanged>>", self._cursor_changed, add="+")
            self._cursor_follow_xview()
        self.schedule_cursor_redraw()

    # ---- the cursor's label -------------------------------------------------------
    def _make_cursor_label(self):
        """The Label that is the cursor, laid over the text when it is shown."""
        label = tk.Label(
            self.inner,
            text="",
            bd=0,
            highlightthickness=0,
            padx=0,
            pady=0,
            anchor="nw",
            takefocus=0,
            cursor=self.inner.cget("cursor"),
        )
        # Showing and hiding it all the time must not look like the window being
        # shown and hidden to anything that listens for that.
        label.bind("<Map>", lambda _: "break")
        label.bind("<Unmap>", lambda _: "break")
        for sequence in self._CURSOR_PASSED_EVENTS:
            label.bind(
                sequence, lambda event, s=sequence: self._cursor_pass_on(s, event)
            )
        return label

    def _cursor_pass_on(self, sequence, event):
        """Hand a mouse event that happened on the cursor on to the text under it, as if
        the cursor were not there.
        """
        label = self._cursor_label
        options = {
            "x": event.x + label.winfo_x(),
            "y": event.y + label.winfo_y(),
            "state": event.state & 0xFF,  # the keys; the pattern has the buttons
            "time": event.time,
        }
        if sequence == "<MouseWheel>":
            options["delta"] = event.delta
        self.inner.event_generate(sequence, **options)
        return "break"

    # ---- options ------------------------------------------------------------------
    @staticmethod
    def _check_cursor_shape(shape):
        """Raise ValueError unless `shape` is one of the cursor shapes."""
        if shape not in CURSOR_SHAPES:
            names = ", ".join(repr(name) for name in CURSOR_SHAPES)
            raise ValueError(f"cursor_shape must be one of {names}")

    def set_cursor_shape(self, shape):
        """Change the shape of the cursor: "line", "block", or "underline"."""
        self._check_cursor_shape(shape)
        self.cursor_shape = shape
        self.schedule_cursor_redraw()

    def set_cursor_blink(self, enabled):
        """Make the cursor blink, or stay on."""
        self.cursor_blink = bool(enabled)
        self.reset_cursor_blink()
        self.schedule_cursor_redraw()

    def set_cursor_visible(self, visible):
        """Show or hide the cursor (it is shown only while the text has the focus)."""
        self.cursor_visible = bool(visible)
        self.reset_cursor_blink()
        self.schedule_cursor_redraw()

    def apply_own_options(self, options):
        """Store changed options, and draw the cursor again if one of its options
        changed (colors are among them).
        """
        if "cursor_shape" in options:
            self._check_cursor_shape(options["cursor_shape"])
        super().apply_own_options(options)
        if self._cursor_label is None:
            return
        if "xscrollcommand" in options:
            self._cursor_follow_xview()
        if "cursor_blink" in options or "cursor_visible" in options:
            self.reset_cursor_blink()
        self.schedule_cursor_redraw()

    def restyle_inner(self):
        """Also draw the cursor again: the colors and the fonts may have changed."""
        super().restyle_inner()
        if self._cursor_label is not None:
            self.schedule_cursor_redraw()

    def on_theme_changed(self):
        """Also draw the cursor again, in the colors of the new theme."""
        super().on_theme_changed()
        if self._cursor_label is not None:
            self.schedule_cursor_redraw()

    # ---- tags: they can change the fonts and colors under the cursor -----------------
    def tag_configure(self, *arguments, **options):
        """Forwarded tag_configure() that also draws the cursor again."""
        result = self.inner.tag_configure(*arguments, **options)
        self.schedule_cursor_redraw()
        return result

    tag_config = tag_configure

    def tag_add(self, *arguments):
        """Forwarded tag_add() that also draws the cursor again."""
        result = self.inner.tag_add(*arguments)
        self.schedule_cursor_redraw()
        return result

    def tag_remove(self, *arguments):
        """Forwarded tag_remove() that also draws the cursor again."""
        result = self.inner.tag_remove(*arguments)
        self.schedule_cursor_redraw()
        return result

    def tag_delete(self, *arguments):
        """Forwarded tag_delete() that also draws the cursor again."""
        result = self.inner.tag_delete(*arguments)
        self.schedule_cursor_redraw()
        return result

    def tag_raise(self, *arguments):
        """Forwarded tag_raise() that also draws the cursor again."""
        result = self.inner.tag_raise(*arguments)
        self.schedule_cursor_redraw()
        return result

    def tag_lower(self, *arguments):
        """Forwarded tag_lower() that also draws the cursor again."""
        result = self.inner.tag_lower(*arguments)
        self.schedule_cursor_redraw()
        return result

    # ---- events that move or change the cursor ------------------------------------
    def _text_has_focus(self):
        """Whether the text has the keyboard focus right now."""
        try:
            return self.inner.focus_get() is self.inner
        except (KeyError, tk.TclError):
            return False

    def _cursor_focus_in(self, _):
        """The text got the focus: show the cursor (it starts out solid)."""
        self._cursor_focus_seen = True
        self._cursor_focused = True
        self.reset_cursor_blink()
        self.schedule_cursor_redraw()

    def _cursor_focus_out(self, _):
        """The text lost the focus: hide the cursor."""
        self._cursor_focus_seen = True
        self._cursor_focused = False
        self._cursor_update_blink()
        self.schedule_cursor_redraw()

    def _cursor_changed(self, _):
        """The text, the insert mark, or the view changed: the cursor moved (it is solid
        while it moves).
        """
        self.reset_cursor_blink()
        self.schedule_cursor_redraw()

    def _cursor_follow_xview(self):
        """Draw the cursor again whenever the view scrolls sideways. The text reports
        that to its xscrollcommand, which may be one that is already set, or be set
        again later; ours calls that one too.
        """
        text = self.inner
        current = str(text.cget("xscrollcommand"))
        if current and current == self._cursor_xview_command:
            return  # ours is still the one that is set

        def scrolled(first, last):
            """The view scrolled sideways."""
            if current:
                text.tk.call(current, first, last)
            self.schedule_cursor_redraw()

        text.configure(xscrollcommand=scrolled)
        self._cursor_xview_command = str(text.cget("xscrollcommand"))

    def _cursor_text_destroyed(self, event):
        """The text is being destroyed: stop the timers of the cursor."""
        if event.widget is self.inner:
            self.stop_cursor_timers()

    # ---- blinking and scheduling -----------------------------------------------------
    def reset_cursor_blink(self):
        """Start the blink cycle again with the cursor shown (call it whenever the
        cursor moves, so that it is solid while it does).
        """
        self._cursor_blink_phase = True
        if self._cursor_blink_call is not None:
            self.cancel_call(self._cursor_blink_call)
            self._cursor_blink_call = None
        self._cursor_update_blink()

    def _cursor_update_blink(self):
        """Run the blink timer exactly while there is a blinking cursor to show."""
        wanted = self.cursor_blink and self._cursor_focused and self.cursor_visible
        if wanted and self._cursor_blink_call is None:
            delay = (
                self.CURSOR_BLINK_ON_MS
                if self._cursor_blink_phase
                else self.CURSOR_BLINK_OFF_MS
            )
            self._cursor_blink_call = self.call_later(delay, self._cursor_blink_tick)
        elif not wanted and self._cursor_blink_call is not None:
            self.cancel_call(self._cursor_blink_call)
            self._cursor_blink_call = None
            self._cursor_blink_phase = True

    def _cursor_blink_tick(self):
        """The timer of the blink: show or hide the cursor, and wait again."""
        self._cursor_blink_call = None
        self._cursor_blink_phase = not self._cursor_blink_phase
        self.redraw_cursor()
        self._cursor_update_blink()

    def schedule_cursor_redraw(self):
        """Draw the cursor again once the program is idle (any number of requests before
        that cost one redraw).
        """
        if self._cursor_label is not None and self._cursor_redraw_call is None:
            self._cursor_redraw_call = self.call_later(None, self._cursor_redraw_now)

    def _cursor_redraw_now(self):
        """The idle callback of schedule_cursor_redraw()."""
        self._cursor_redraw_call = None
        self.redraw_cursor()

    def stop_cursor_timers(self):
        """Cancel the blink timer and a redraw that is waiting. Anything that cancels
        every timer of the text by itself has to call this too, so that the cursor does
        not think that they are still going to run.
        """
        for name in ("_cursor_blink_call", "_cursor_redraw_call"):
            identifier = getattr(self, name)
            setattr(self, name, None)
            try:
                self.cancel_call(identifier)
            except tk.TclError:
                pass
        self._cursor_blink_phase = True

    # ---- drawing ------------------------------------------------------------------
    def cursor_index(self):
        """The index of the character the cursor is drawn on: the insert mark. A text
        that keeps its cursor somewhere else overrides this.
        """
        return "insert"

    def cursor_text_tags(self, index):
        """The tags whose colors the cursor takes when it follows the colors of the
        text, from the lowest priority to the highest: every tag on the character at
        `index` but the selection.
        """
        return [tag for tag in self.inner.tag_names(index) if tag != "sel"]

    def redraw_cursor(self):
        """Draw the cursor now: placed over the character it is on, in its shape, font
        and colors; or hidden while it should not show.
        """
        label = self._cursor_label
        if label is None:
            return
        if not self._cursor_focus_seen:
            # No focus event yet: the text may have been given the focus before
            # it could tell us.
            self._cursor_focused = self._text_has_focus()
            self._cursor_update_blink()
        try:
            look = self._cursor_look() if self._cursor_is_shown() else None
        except tk.TclError:
            look = None  # destroyed meanwhile, or an index that is not valid (yet)
        if look is None:
            self._cursor_hide()
            return
        x, y, width, height, char, font, glyph_top, color, glyph_color = look
        thickness = max(1, int(self.cursor_thickness))
        if self.cursor_shape == "line":
            box = (x, y, thickness, height)
            appearance = ("", color, color, "", 0)
        elif self.cursor_shape == "underline":
            thickness = min(thickness, height)
            box = (x, y + height - thickness, width, thickness)
            appearance = ("", color, color, "", 0)
        else:
            box = (x, y, width, height)
            appearance = (char, color, glyph_color, font, glyph_top)
        if appearance != self._cursor_appearance:
            self._cursor_appearance = appearance
            text, background, foreground, label_font, top = appearance
            options = {"text": text, "bg": background, "fg": foreground, "pady": top}
            if label_font:
                options["font"] = label_font
            label.configure(**options)
        if box != self._cursor_placement:
            self._cursor_placement = box
            # bordermode "outside": the coordinates are the ones the text reports,
            # measured from the corner of the text widget itself.
            label.place(
                in_=self.inner,
                bordermode="outside",
                x=box[0],
                y=box[1],
                width=max(1, box[2]),
                height=max(1, box[3]),
            )

    def _cursor_hide(self):
        """Take the cursor away until it is drawn again."""
        if self._cursor_placement is not None:
            self._cursor_placement = None
            self._cursor_label.place_forget()

    def _cursor_is_shown(self):
        """Whether the cursor should be on screen: it is visible, in the shown half of
        its blink, and on a text that has the focus and is not disabled.
        """
        return (
            self.winfo_exists()
            and self.cursor_visible
            and self._cursor_focused
            and self._cursor_blink_phase
            and str(self.inner.cget("state")) != "disabled"
        )

    def _cursor_look(self):
        """What is needed to draw the cursor now: (x, y, width, height) of the cell it
        covers in the text widget, the character in it, the font that character has,
        how far below the top of the cell that font has to draw it to share the baseline
        of the line, and the colors of the cursor and of the character on it. None when
        the character is not on screen.
        """
        text = self.inner
        index = self.cursor_index()
        box = text.bbox(index)
        if not box:
            return None
        x, y, width, height = box
        char = self._cursor_character(index)
        font = self._cursor_font(index)
        if char in ("", "\n") or width < 1:
            # Nothing there to measure: the cell of a space in the font that applies.
            width = self._font_measure(font, " ")
        glyph_top = 0
        if char not in ("", "\n"):
            ascent = self._font_metric(font, "-ascent")
            line = text.dlineinfo(index)
            baseline = line[1] + line[4] if line else y + ascent
            glyph_top = max(0, baseline - y - ascent)
        color, glyph_color = self._cursor_colors(index)
        shown = char if char and char.isprintable() and not char.isspace() else " "
        return x, y, width, height, shown, font, glyph_top, color, glyph_color

    def _cursor_character(self, index):
        """The character at `index` ("" at the end of the text, "\\n" at the end of a
        line).
        """
        text = self.inner
        char = text.get(index)
        if "\ud800" <= char <= "\udfff":
            # Half of a character beyond the Basic Multilingual Plane (most emoji):
            # tk keeps those as two characters, and the next one is the other half.
            char = text.get(index, f"{index}+2c")
        return char

    def _cursor_font(self, index):
        """The font description that applies to the character at `index`: the one of the
        highest-priority tag on it that has one, else the one of the text.
        """
        text = self.inner
        font = str(text.cget("font"))
        for tag in text.tag_names(index):
            tag_font = str(text.tag_cget(tag, "font"))
            if tag_font:
                font = tag_font
        return font

    def _font_measure(self, font, string):
        """The width in px of `string` in `font` (a description or a font name)."""
        return int(self.inner.tk.call("font", "measure", font, string))

    def _font_metric(self, font, option):
        """One metric of `font` in px, such as "-ascent"."""
        return int(self.inner.tk.call("font", "metrics", font, option))

    def _cursor_colors(self, index):
        """(the color of the cursor, the color of the character it shows) as #rrggbb.
        With a color of its own the cursor has it; with cursor_follows_text_colors it
        has the colors of the character, swapped; else the theme's.
        """
        text = self.inner
        background = text.cget("background")
        if self.cget("cursor_color") is None and self.cursor_follows_text_colors:
            foreground = text.cget("foreground")
            for tag in self.cursor_text_tags(index):
                tag_foreground = text.tag_cget(tag, "foreground")
                tag_background = text.tag_cget(tag, "background")
                if tag_foreground:
                    foreground = tag_foreground
                if tag_background:
                    background = tag_background
            return self.rc(foreground), self.rc(background)
        return self.part("cursor_color", "text"), self.rc(background)
