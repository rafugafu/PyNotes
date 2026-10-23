"""The Editor buffer: file loading/saving, external-change watching,
find/find-replace, undo/redo, and syntax highlighting for every HMode
(Python, LaTeX, HTML, Markdown, plus PDF/PNG/ePub viewing). Python
highlighting/autocomplete is scope-aware, backed by python_scope_build.
An Editor can also be a "view" (a synced peer of another Editor already
showing the same file - see _make_peer_type()/view_master/
view_children) so the same file can be open in more than one pane.
"""

import os
import platform
import subprocess
import shutil
import codecs
import re
import threading
import queue
import ast
import warnings
import io
import canvastk as ctk
import tkinter as tk
import state
from init import homedir, monospace, DEBOUNCE_TIME
from buffer import Buffer
from python_scope_build import _python_highlight_ops
import python_scope_build
import dialogs
import pycode
import speech
import terminal
import cursortextbox
import utils
import window
import tika
from tika import parser
import pdfplumber
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class Editor(Buffer):
    """The text-editor buffer. Also doubles as a "view" onto another
    Editor already showing the same file (see _make_peer_type()): a
    view's view_master points at the original Editor, and setting one
    of _SHARED_STATE_ATTRS on a view (via __setattr__) is redirected to
    the master instead, so every peer view of a file shares one copy of
    its unsaved-state, title, HMode, and Python-scan caches, while each
    keeps its own widgets/UI state (_PER_PANE_ATTRS).
    """

    for code in state.editor_init_functions:
        try:
            exec(code, vars(state), locals())
        except Exception as error:
            error = str(error)
            state.root.error("Error", f"Error in editor init functions:\n{error}")

    class FileChangeHandler(FileSystemEventHandler):
        """watchdog event handler that flags outer's file as externally
        changed (queuing _file_watch_prompt() onto the GUI thread) when
        the file on disk is modified/created/moved into place by
        something other than outer's own save.
        """

        def __init__(self, outer):
            self.outer = outer
            super().__init__()

        def _handle(self, path):
            """Flag a file-watch prompt as pending, unless path isn't
            outer's file, outer is the one currently writing it
            (file_editing_own), or a prompt is already pending.
            """
            if os.path.abspath(path) != self.outer.title:
                return
            if self.outer.file_editing_own:
                return
            if self.outer._file_watch_prompt_pending:
                return
            self.outer._file_watch_prompt_pending = True
            self.outer._main_queue.put(self.outer._file_watch_prompt)

        def on_modified(self, event):
            if event.is_directory:
                return
            self._handle(event.src_path)

        def on_created(self, event):
            if event.is_directory:
                return
            self._handle(event.src_path)

        def on_moved(self, event):
            if event.is_directory:
                return
            self._handle(event.dest_path)

    # Attributes shared by every peer view of a file (redirected to
    # view_master by __setattr__/__getattr__ below).
    _SHARED_STATE_ATTRS = frozenset(
        (
            "unsaved",
            "unsavedtext",
            "hmode",
            "title",
            "wanttitle",
            "file_editing_own",
            "_file_watch_prompt_pending",
            "imageloaded",
            "observer",
            "_python_scopes",
            "_python_call_kwargs",
            "_python_module_literals",
            "_python_literal_attrs",
            "_python_name_positions",
            "_python_def_names",
            "_python_typed_attrs",
            "_python_param_default_tags",
            "_python_kwarg_positions",
            "_python_import_dotted_lines",
            "_python_import_orig_name_tags",
            "_python_instance_name_positions",
            "_python_global_stmt_kind_positions",
            "_python_names_scan_thread",
            "_python_scan_after_id",
            "_python_edit_generation",
            "_python_module_spec_cache",
            "_python_module_members_cache",
            "_python_module_class_members_cache",
            "_python_module_func_params_cache",
            "_ha_running",
            "_ha_pending",
        )
    )
    # Plain tkinter/Tcl internals, excluded (alongside _PER_PANE_ATTRS)
    # when _promote_new_master() carries a closed master's attributes
    # over to the view being promoted to replace it.
    _TK_INTERNAL_ATTRS = frozenset(
        (
            "_w",
            "_name",
            "children",
            "master",
            "tk",
            "_tclCommands",
            "widgetName",
            "_last_child_ids",
        )
    )
    # Attributes each view keeps its own copy of (widgets and per-pane
    # UI state), never shared or carried over from another view.
    _PER_PANE_ATTRS = frozenset(
        (
            "root",
            "fileinfo",
            "infos",
            "fileinfocolumn",
            "fileinforelief",
            "fileinfoconfig",
            "_own_fileinfoconfig",
            "filename",
            "filetype",
            "filesize",
            "mf",
            "lf",
            "latexbold",
            "latexitalic",
            "latexunderline",
            "latexsubscript",
            "latexsuperscript",
            "latexnumberlist",
            "latexbulletlist",
            "latexsectionvar",
            "latexsection",
            "latexparagraph",
            "latexequation",
            "latexcharvar",
            "latexmath",
            "_own_type",
            "active",
            "imageload",
            "m",
            "view_master",
            "view_children",
            "_selectionpoint",
            "type_top",
            "type_bottom",
            "_prev_visible_region",
            "_ha_after_id",
            "_filesize_after_id",
            "_unsaved_after_id",
            "_main_queue",
        )
    )

    def __setattr__(self, name, value):
        """Redirect setting a _SHARED_STATE_ATTRS attribute to
        view_master, if this is a view of one, so every peer view
        stays in sync automatically.
        """
        if (
            name in Editor._SHARED_STATE_ATTRS
            and self.__dict__.get("view_master") is not None
        ):
            setattr(self.__dict__["view_master"], name, value)
        else:
            object.__setattr__(self, name, value)

    def __getattr__(self, name):
        """Fall back to reading a _SHARED_STATE_ATTRS attribute from
        view_master (only reached when name isn't set on this instance
        itself, which - given __setattr__ above - is always true for a
        view's own shared attributes).
        """
        if name in Editor._SHARED_STATE_ATTRS:
            master = self.__dict__.get("view_master")
            if master is not None:
                return getattr(master, name)
        raise AttributeError(name)

    @property
    def mainwidget(self):
        """The active pane's own Text widget: on the master (view_master
        is None), whichever view (including itself) currently has focus;
        on a view, always its own widget.
        """
        if self.view_master is None:
            for child in self.view_children:
                if child.active:
                    return child._own_type
        return self._own_type

    @mainwidget.setter
    def mainwidget(self, value):
        pass

    @property
    def type_(self):
        """Same resolution as mainwidget; the name used throughout the
        rest of this file to mean "the Text widget to act on".
        """
        if self.view_master is None:
            for child in self.view_children:
                if child.active:
                    return child._own_type
        return self._own_type

    @type_.setter
    def type_(self, value):
        self._own_type = value

    def _group_members(self):
        """This Editor's view_master (or self, if it is the master)
        plus every peer view of it.
        """
        resolved = self.view_master if self.view_master else self
        return [resolved] + list(resolved.view_children)

    def _focused_pane(self):
        """Whichever pane in this Editor's view group currently has
        focus, or self if none does.
        """
        for member in self._group_members():
            if member.active:
                return member
        return self

    @property
    def selectionpoint(self):
        """The selection-point index (see setselpoint()), tracked per
        focused pane rather than shared, since each view can have its
        own cursor position/selection into the same file.
        """
        return self._focused_pane()._selectionpoint

    @selectionpoint.setter
    def selectionpoint(self, value):
        self._focused_pane()._selectionpoint = value

    def _make_peer_type(self, master):
        """Create a CustomTextbox whose Text widget is a tkinter "peer" (Tk's
        own peer_create, a second view onto the same underlying text
        content as master's) for this Editor to use as its own Text
        widget, copied from master's configuration.
        """
        name = "peertype%d" % id(self)
        peer_box = cursortextbox.CustomTextbox(
            self.mf,
            scrolled=True,
            cursor_shape=cursortextbox.CURSOR_SHAPES[state.curcurtype],
            font=(state.defs[2], 12),
            wrap="word",
            undo=True,
            autoseparators=True,
        )
        peer_box.inner.destroy()
        master._own_type.inner.peer_create(str(peer_box) + "." + name)
        peer = tk.Text.__new__(tk.Text)
        peer.widgetName = "text"
        peer._tclCommands = None
        peer._setup(peer_box, {"name": name})
        for option in master._own_type.inner.configure():
            if option in ("xscrollcommand", "yscrollcommand"):
                continue
            try:
                peer.configure(**{option: master._own_type.inner.cget(option)})
            except Exception:
                pass
        peer_box.install_inner(
            peer, side="left", fill="both", expand=True, padx=(7, 2), pady=5
        )
        peer_box.scrollbar.config(command=peer.yview)
        peer.bind("<Control-a>", peer_box._select_all, add="+")
        self._attach_peer_cursor(peer_box)
        peer_box.restyle_inner()
        peer_box.configure(line_numbers=True)
        return peer_box

    def _attach_peer_cursor(self, peer_box):
        """Move the cursor of peer_box (a cursortextbox.CustomTextbox) over to the peer Text that
        replaced its own, as its cursor label, bindings and change event belonged to
        the Text that was destroyed.
        """
        peer = peer_box.inner
        peer_box.stop_cursor_timers()
        peer_box._cursor_appearance = None
        peer_box._cursor_placement = None
        peer_box._cursor_xview_command = None
        peer.configure(insertwidth=0, insertontime=0)
        peer_box._cursor_label = peer_box._make_cursor_label()
        peer.bind("<FocusIn>", peer_box._cursor_focus_in, add="+")
        peer.bind("<FocusOut>", peer_box._cursor_focus_out, add="+")
        peer.bind("<Configure>", lambda _: peer_box.schedule_cursor_redraw(), add="+")
        peer.bind("<Map>", lambda _: peer_box.schedule_cursor_redraw(), add="+")
        peer.bind("<Destroy>", peer_box._cursor_text_destroyed, add="+")
        peer_box._change_event_installed = False  # the new Text has none yet
        peer_box._install_change_event()
        peer.bind("<<TextboxChanged>>", peer_box._cursor_changed, add="+")
        peer_box._cursor_follow_xview()
        peer_box.schedule_cursor_redraw()

    def _wire_type(self):
        """Pack this pane's own CustomTextbox and bind its events."""
        own_box = self._own_type
        own_box.focus_set()
        own_box.pack(side="right", fill="both", expand=True)
        self._bind_type_events()
        self._bind_focus_recursive(own_box)
        self._wrap_text_command(own_box)

    def _wrap_text_command(self, box):
        """Let the view of box scroll on past the last line until it is a quarter
        of the way down the box.

        The room is spacing below the last line of the text, which is always an
        empty line of its own: the real text is the text that everything else sees
        plus one newline, and the spacing is on the line after that newline. The
        spacing is on that line alone, as a selected character paints its selection
        color over the whole height of its line, spacing included.

        That last line is hidden by wrapping the Tcl command of the text, which is
        what every call on the text ends up in, whoever makes it (the editor,
        PyCode, plugins, the bindings of Tk): "end" means the end of the text
        without that newline (so index, get, compare, count and the rest do not know
        about the last line; see() of the end scrolls to the spacing, which is how
        the room is shown), nothing can be inserted, deleted, replaced, or
        marked at the cursor past that end, no tag (the selection included) is
        put on it, the cursor is moved off the last line when something else (a click
        below the text) puts it there, and the newline is put back if the text has none.

        The same wrapper also highlights the bracket at the cursor whenever the cursor
        is moved (see bracket_match()).
        """
        text = box.inner
        box._overscroll_gap = None
        box._install_change_event()
        name = text._w
        wrapped = name + "_overscroll"
        text.tk.call("rename", name, wrapped)
        past_end = re.compile(r"^\s*end(?![A-Za-z0-9_.])")

        def real(*arguments):
            """Run a command of the text without these rules."""
            return text.tk.call(wrapped, *arguments)

        def last_line():
            """The index of the last line, which is empty, and its line number and
            column (the column is 0 as long as the text ends with a newline).
            """
            index = str(real("index", "end-1c"))
            line, column = index.split(".")
            return index, int(line), int(column)

        def hiding_last_line(index):
            """`index` with "end" as the end of the text that is not the last line."""
            return past_end.sub("end-1c", index, count=1)

        def before_last_line(index, limit="end-2c"):
            """The real index of `index` (which is as the text is seen from outside),
            or `limit` if it is further: the last place where something can be put
            before the last line, by default.
            """
            index = str(real("index", index))
            limit = str(real("index", limit))
            return (
                limit
                if text.tk.getboolean(real("compare", index, ">", limit))
                else index
            )

        bracket_match_pending = [False]  # whether a bracket_match() is scheduled
        reached_end_by_delete = [False]  # whether the delete under way goes to the end

        def real_arguments(*arguments):
            """The arguments of a command of the text as it is seen from outside,
            made into those of the real text, as a Tcl list. This is an empty string
            when there is nothing for the command to do.
            """
            arguments = [str(argument) for argument in arguments]
            kind = arguments[0]
            second = arguments[1] if len(arguments) > 1 else ""

            def hide(position):
                if position < len(arguments):
                    arguments[position] = hiding_last_line(arguments[position])

            if kind in ("index", "see", "bbox", "dlineinfo"):
                hide(1)
            elif kind == "get":
                for position in range(1, len(arguments)):
                    if not arguments[position].startswith("-"):
                        hide(position)
            elif kind == "insert":
                hide(1)
                arguments[1] = before_last_line(arguments[1])
            elif kind == "delete":
                if len(arguments) == 3:
                    reached_end_by_delete[0] = text.tk.getboolean(
                        real(
                            "compare",
                            hiding_last_line(arguments[2]),
                            ">=",
                            "end-1c",
                        )
                    )
                for position in range(1, len(arguments)):
                    arguments[position] = before_last_line(
                        hiding_last_line(arguments[position])
                    )
                if len(arguments) == 2:
                    first = arguments[1]
                    last = before_last_line(f"{first} +1c")
                    if first == last:
                        return ""
                    arguments.append(last)
                elif len(arguments) == 3 and arguments[1] == arguments[2]:
                    return ""
            elif kind == "replace":
                for position in (1, 2):
                    if position < len(arguments):
                        arguments[position] = before_last_line(
                            hiding_last_line(arguments[position])
                        )
            elif kind == "compare":
                hide(1)
                hide(3)
            elif kind == "mark":
                if second == "set":
                    hide(3)
                    if len(arguments) > 3 and arguments[2] == "insert":
                        arguments[3] = before_last_line(arguments[3])
                elif second in ("next", "previous"):
                    hide(2)
            elif kind == "tag":
                if second in ("add", "remove"):
                    # a tag, the selection included, ends where the last line starts
                    for position in range(3, len(arguments)):
                        arguments[position] = before_last_line(
                            hiding_last_line(arguments[position]), "end-1c"
                        )
                    if len(arguments) == 4 and arguments[3] == str(
                        real("index", "end-1c")
                    ):
                        return ""
                elif second in ("nextrange", "prevrange"):
                    hide(3)
                    hide(4)
            elif kind == "search" and "--" in arguments:
                separator = arguments.index("--")
                hide(separator + 2)
                hide(separator + 3)
            elif kind == "count":
                indices = [
                    position
                    for position in range(1, len(arguments))
                    if not arguments[position].startswith("-")
                ]
                for position in indices[-2:]:
                    hide(position)
            elif kind in ("image", "window") and second == "create":
                hide(2)
                arguments[2] = before_last_line(arguments[2])
            return tk._join(tuple(arguments))

        def real_arguments_for_tcl(*arguments):
            """real_arguments() for the Tcl procedure below."""
            try:
                return real_arguments(*arguments)
            except tk.TclError:  # the text is being destroyed
                return tk._join(tuple(str(argument) for argument in arguments))

        def keep_ending_newline():
            """End the real text with the newline that makes the last line."""
            _, line, column = last_line()
            if column or line == 1:
                cursor = str(real("index", "insert"))
                real("insert", "end-1c", "\n")
                real("mark", "set", "insert", cursor)

        def keep_cursor_off_last_line():
            """Move the cursor to the end of the text without the last line."""
            _, line, column = last_line()
            if not column and int(str(real("index", "insert")).split(".")[0]) == line:
                real("mark", "set", "insert", "end-2c")

        def spaced_last_line(_=None):
            """Give the last line its spacing, a quarter of the way down the box."""
            gap = text.winfo_height() * 3 // 4
            if box._overscroll_gap != gap:
                box._overscroll_gap = gap
                real("tag", "configure", "overscroll", "-spacing3", gap)
            real("tag", "add", "overscroll", "end-1c", "end")

        def match_bracket_when_idle():
            """Highlight the bracket at the cursor once idle, however many times
            the cursor moved meanwhile.
            """
            if not bracket_match_pending[0]:
                bracket_match_pending[0] = True

                def match_bracket():
                    bracket_match_pending[0] = False
                    if self.winfo_exists():
                        self.bracket_match()

                text.after_idle(match_bracket)

        def after(kind):
            """The text did `kind` of something that the rules are about."""
            try:
                if kind == "mark":
                    keep_cursor_off_last_line()
                    match_bracket_when_idle()
                else:
                    if reached_end_by_delete[0]:
                        # the newline that ends the text seen from outside can not be
                        # deleted, but loses its tags (the selection) like Tk's does
                        reached_end_by_delete[0] = False
                        for tag in real("tag", "names", "end-2c"):
                            real("tag", "remove", str(tag), "end-2c", "end-1c")
                    keep_ending_newline()
                    keep_cursor_off_last_line()
                    spaced_last_line()
            except tk.TclError:  # the text is being destroyed
                pass

        text.tk.eval(
            """
            proc {name} args {{
                set kind [lindex $args 0]
                set routed [expr {{[string first end $args] >= 0
                    || $kind in {{insert delete replace}}
                    || ($kind eq "mark" && [lindex $args 1] eq "set"
                        && [lindex $args 2] eq "insert")}}]
                if {{!$routed && $kind eq "tag" && [lindex $args 1] in {{add remove}}}} {{
                    set limit [{wrapped} index end-1c]
                    foreach index [lrange $args 3 end] {{
                        if {{[{wrapped} compare $index >= $limit]}} {{
                            set routed 1
                            break
                        }}
                    }}
                }}
                if {{$routed}} {{
                    set args [{real_arguments} {{*}}$args]
                    if {{$args eq ""}} {{
                        return
                    }}
                }}
                set result [{wrapped} {{*}}$args]
                if {{$kind in {{insert delete replace}}
                    || ($kind eq "edit" && [lindex $args 1] in {{undo redo}})}} {{
                    {after} edit
                }} elseif {{$kind eq "mark" && [lindex $args 1] eq "set"
                    && [lindex $args 2] eq "insert"}} {{
                    {after} mark
                }}
                return $result
            }}
            """.format(
                name=name,
                wrapped=wrapped,
                real_arguments=text.register(real_arguments_for_tcl),
                after=text.register(after),
            )
        )
        draw_line_numbers = box._draw_line_numbers

        def draw_line_numbers_without_last_line():
            """Draw the line numbers, but not the number of the last line, which is
            not a line of the text as far as the user is concerned.
            """
            draw_line_numbers()
            gutter = box._gutter
            if gutter is None:
                return
            _, line, column = last_line()
            if not column:
                for item in gutter.find_all():
                    if gutter.type(item) == "text" and gutter.itemcget(
                        item, "text"
                    ) == str(line):
                        gutter.delete(item)

        box._draw_line_numbers = draw_line_numbers_without_last_line
        text.bind("<Configure>", spaced_last_line, add="+")
        _, line, column = last_line()
        if column or line == 1:
            keep_ending_newline()
            text.edit_reset()
            text.edit_modified(False)
        after("edit")

    def _bind_focus_recursive(self, widget, skip_widgets=()):
        """Bind <FocusIn> (to make this buffer active) on widget and
        every descendant, except any in skip_widgets.
        """
        if widget in skip_widgets:
            return
        widget.bind(
            "<FocusIn>",
            lambda event, buffer=self: window.setactive(
                state.all_buffers.index(buffer)
            ),
            add="+",
        )
        for child in widget.winfo_children():
            self._bind_focus_recursive(child, skip_widgets)

    def _bind_type_events(self):
        """Bind this pane's Text widget's keyboard shortcuts."""
        self.type_.bind("<Control-a>", lambda event: self.selall() or "break")
        self.type_.bind("<Control-n>", lambda event: self.nw() or "break")
        self.type_.bind("<Control-o>", lambda event: self.llld() or "break")
        self.type_.bind("<Control-c>", lambda event: self.cp() or "break")
        self.type_.bind("<Control-v>", lambda event: self.pst() or "break")
        self.type_.bind("<Control-x>", lambda event: self.cut() or "break")
        self.type_.bind("<KeyRelease>", lambda event: self.keypress())
        self.type_.bind("<Return>", lambda event: self.indent())
        self.type_.bind("<Tab>", lambda event: self.tab() or "break")
        self.type_.bind("<BackSpace>", lambda event: self.backspace() or "break")
        self.type_.bind("<Left>", lambda event: self.left() or "break")
        self.type_.bind("<Right>", lambda event: self.right() or "break")
        self.type_.bind("<Delete>", lambda event: self.delete_key() or "break")
        self.type_.bind("<Shift-Left>", lambda event: self.select_left())
        self.type_.bind("<Shift-Right>", lambda event: self.select_right())
        self.type_.bind("<Control-Left>", lambda event: self.word_left())
        self.type_.bind("<Control-Right>", lambda event: self.word_right())
        self.type_.bind("<Control-Shift-Left>", lambda event: self.select_word_left())
        self.type_.bind("<Control-Shift-Right>", lambda event: self.select_word_right())
        self.type_.bind("<Control-BackSpace>", lambda event: self.delete_word_back())
        self.type_.bind("<Control-Delete>", lambda event: self.delete_word_forward())
        self.type_.bind("<Alt-l>", lambda event: self.gl() or "break")
        self.type_.bind("<Control-p>", lambda event: self.ptf() or "break")
        self.type_.bind("<Control-P>", lambda event: self.ptb() or "break")
        self.type_.bind("<Control-f>", lambda event: self.f() or "break")
        self.type_.bind("<Control-F>", lambda event: self.fr() or "break")
        self.type_.bind("<Control-h>", lambda event: self.fr() or "break")
        self.type_.bind("<Control-z>", lambda event: self.undo() or "break")
        self.type_.bind("<Control-Z>", lambda event: self.redo() or "break")
        self.type_.bind("<Control-s>", lambda event: self.sssv() or "break")
        self.type_.bind("<Control-S>", lambda event: self.ssv() or "break")
        self.type_.bind("<F5>", lambda event: self.f5() or "break")
        self.type_.bind(
            "<Control-space>", lambda event: self.toggleselpoint() or "break"
        )
        self.type_.bind("<KeyPress>", self.selkeypress)
        self.type_.bind("<Destroy>", lambda event: self._cancel_type_after_ids())

    def selkeypress(self, event):
        """<KeyPress> handler while a selection point is set (see
        setselpoint()): typing/editing keys clear it (since the
        selection they'd have extended is about to change), other keys
        (e.g. arrows) extend the selection to the new cursor position.
        """
        if not self.selectionpoint:
            return
        if event.keysym in ("BackSpace", "Delete", "Return", "Tab") or (
            event.char and ord(event.char[0]) >= 32
        ):
            self.removeselpoint()
        else:
            self.type_.after_idle(self.selupdate)

    def _sync_group_chrome(self):
        """Run _sync_chrome() on every pane in this view group."""
        for member in self._group_members():
            member._sync_chrome()

    def _sync_chrome(self):
        """Copy the master's file-info bar text and LaTeX-toolbar/
        PNG-view visibility onto this view (chrome that mirrors
        shared state but, being actual widgets, isn't itself shared).
        """
        master = self.view_master or self
        if master is not self:
            self._own_fileinfoconfig(
                **{info: label.cget("text") for info, label in master.infos.items()}
            )
        if master.hmode == "latex":
            self.lfouter.pack(
                padx=10, pady=10, side="top", fill="x", before=self.fileinfo
            )
        else:
            self.lfouter.pack_forget()
        if master.imageloaded:
            self.type_.pack_forget()
            self.mf.pack_forget()
        else:
            self.type_.pack(fill="both", expand=True, anchor="n")
            self.mf.pack(fill="both", expand=True)

    def _cancel_type_after_ids(self):
        """Cancel every pending .after() callback tracked for this pane
        - both the ones scheduled on this pane's Text widget and
        self._ha_apply_after_id, scheduled on state.root - before
        replacing/destroying the widget, e.g. in
        _connect_to()/_disconnect().
        """
        for name in (
            "_main_poll_after_id",
            "_ha_after_id",
            "_filesize_after_id",
            "_setundo_after_id",
            "_unsaved_after_id",
            "_python_scan_after_id",
            "_find_apply_after_id",
        ):
            after_id = getattr(self, name, None)
            if after_id is not None:
                try:
                    self._own_type.after_cancel(after_id)
                except Exception:
                    pass
                setattr(self, name, None)
        if self._ha_apply_after_id is not None:
            try:
                state.root.after_cancel(self._ha_apply_after_id)
            except Exception:
                pass
            self._ha_apply_after_id = None

    def _cancel_all_after_ids(self):
        """_cancel_type_after_ids() plus the pane-frame-level .after()
        callbacks (type_setview, do_backup); called when this pane is
        actually closing for good.
        """
        self._cancel_type_after_ids()
        for name, widget in (
            ("_type_setview_after_id", self.mf),
            ("_do_backup_after_id", self.mf),
        ):
            after_id = getattr(self, name, None)
            if after_id is not None:
                try:
                    widget.after_cancel(after_id)
                except Exception:
                    pass
                setattr(self, name, None)

    def _drop_own_shared_state(self):
        """Drop this instance's own copies of the shared-state
        attributes (whatever Buffer/Editor init stored before it was
        a view), so they read through to view_master via __getattr__.
        """
        for name in Editor._SHARED_STATE_ATTRS:
            self.__dict__.pop(name, None)

    def _connect_to(self, master):
        """Turn this (currently standalone) Editor into a peer view of
        master: swap in a Text peer widget onto master's content, drop
        this instance's own copies of the shared-state attributes (so
        they read through to master via __getattr__), and register
        self in master.view_children.
        """
        old_type = self.type_
        self._cancel_type_after_ids()
        self.type_ = self._make_peer_type(master)
        self.mainwidget = self.type_
        self._wire_type()
        old_type.destroy()
        try:
            self.__dict__["observer"].stop()
            self.__dict__["observer"].join()
        except Exception:
            pass
        self._drop_own_shared_state()
        self.view_master = master
        master.view_children.append(self)
        self.m = master.m
        self._sync_chrome()
        window.settitle()
        self._main_poll()
        pycode.pcrun(state.pycode_keybindings_cdt)

    def _disconnect(self):
        """Detach this Editor from view-sharing and reset it to a
        blank, standalone editor (its own plain Text widget and fresh
        state) in place, without closing the pane. If it currently has
        peer views (self.view_children), one is first promoted to take
        over as their new master (see _promote_new_master()).
        """
        if self.view_children:
            _promote_new_master(self)
            self.view_children = []
            old_type = self.type_
            self._cancel_type_after_ids()
            self.type_ = cursortextbox.CustomTextbox(
                self.mf,
                scrolled=True,
                cursor_shape=cursortextbox.CURSOR_SHAPES[state.curcurtype],
                font=(state.defs[2], 12),
                wrap="word",
                undo=True,
                autoseparators=True,
                line_numbers=True,
            )
            self.mainwidget = self.type_
            self._wire_type()
            old_type.destroy()
            self._reset_shared_state()
            self.init_hl_tags()
            self.init_plugin_tags()
            self.type_.edit_reset()
            python_scope_build._python_reset_scan_state(self)
            self.resetfileinfo()
            self.lfouter.pack_forget()
            self._main_poll()
            pycode.pcrun(state.pycode_keybindings_cdt)
        if self.view_master is not None:
            master = self.view_master
            if self in master.view_children:
                master.view_children.remove(self)
            old_type = self.type_
            self._cancel_type_after_ids()
            self.type_ = cursortextbox.CustomTextbox(
                self.mf,
                scrolled=True,
                cursor_shape=cursortextbox.CURSOR_SHAPES[state.curcurtype],
                font=(state.defs[2], 12),
                wrap="word",
                undo=True,
                autoseparators=True,
                line_numbers=True,
            )
            self.mainwidget = self.type_
            self._wire_type()
            old_type.destroy()
            self._main_poll()
            self.view_master = None
            self._reset_shared_state()
            self.m = ctk.Menu(state.root)
            for label, menu in state.all_editor_menus.items():
                self.m.add_cascade(label=label, menu=menu)
            self.init_hl_tags()
            self.init_plugin_tags()
            self.type_.edit_reset()
            python_scope_build._python_reset_scan_state(self)
            self.resetfileinfo()
            self.lfouter.pack_forget()
            pycode.pcrun(state.pycode_keybindings_cdt)

    def _reset_shared_state(self):
        """Give this (now standalone) Editor its own fresh blank
        shared state, so nothing is still shared by reference with the
        view group it left.
        """
        self.unsaved = False
        self.unsavedtext = ""
        self.hmode = "normal"
        self.title = ""
        self._sync_wanttitle()
        self.imageloaded = False
        self.file_editing_own = False
        self._file_watch_prompt_pending = False
        self.observer = None
        self._python_scopes = [{"start": 1, "end": 1, "parent": None, "names": {}}]
        self._python_call_kwargs = {}
        self._python_module_literals = []
        self._python_literal_attrs = []
        self._python_name_positions = []
        self._python_def_names = []
        self._python_typed_attrs = []
        self._python_param_default_tags = []
        self._python_kwarg_positions = []
        self._python_import_dotted_lines = []
        self._python_import_orig_name_tags = []
        self._python_instance_name_positions = set()
        self._python_global_stmt_kind_positions = {}
        self._python_names_scan_thread = None
        self._python_scan_after_id = None
        self._python_edit_generation = [0]
        self._python_module_spec_cache = {}
        self._python_module_members_cache = {}
        self._python_module_class_members_cache = {}
        self._python_module_func_params_cache = {}
        self._ha_running = [False]
        self._ha_pending = [None]

    def _group_fileinfoconfig(self, **infoconfigs):
        """Show infoconfigs in the file-info bar of every pane in this
        view group, so the bars never differ.
        """
        for member in self._group_members():
            member._own_fileinfoconfig(**infoconfigs)

    def resetfileinfo(self):
        """Reset the file-info bar to the "no file open" defaults."""
        self.fileinfoconfig(
            filename="Untitled",
            filetype="Plain Text (*.*)",
            filesize="0 bytes",
            filesaved="Untitled File",
        )

    def _detach_before_close(self):
        """Untangle this pane from view-sharing before it's actually
        destroyed (unlike _disconnect(), doesn't reset it into a blank
        editor - there's no point, since it's closing anyway):
        promote a peer to take over as master if this was one, or just
        remove self from its master's view_children if this was a
        view.
        """
        if self.view_children:
            new_master = _promote_new_master(self)
            if state.active is self:
                state.active = new_master
            self.view_children = []
        if self.view_master is not None:
            master = self.view_master
            if self in master.view_children:
                master.view_children.remove(self)

    def _smart_open(self, path):
        """Load path into this pane: no-op if it's already showing it,
        otherwise become a view of the already-open Editor for it if
        there is one, or load it fresh (ld()) if not.
        """
        abspath = os.path.abspath(path)
        resolved = self.view_master if self.view_master else self
        if resolved.title == abspath:
            return
        match = window.find_open_editor(abspath)
        self._disconnect()
        if match is not None and match is not self:
            self._connect_to(match)
        else:
            self.ld(path)

    def __init__(self, master, file=None, view_master=None, *args, **kwargs):
        """Build this pane's chrome (file-info bar, LaTeX toolbar,
        Text widget/line numbers). If view_master is given, this pane
        is created as a peer view of it (a peer Text widget, joining
        its view_children, sharing its state) instead of getting its
        own blank document; otherwise, if file (a path) is given, it's
        loaded via ld().
        """
        super().__init__(master, *args, **kwargs)
        self.view_master = view_master
        self._drop_own_shared_state()
        self.view_children = []
        self._own_fileinfoconfig = self.fileinfoconfig
        self.fileinfoconfig = self._group_fileinfoconfig
        if view_master is None:
            self.resetfileinfo()
        self.mf = ctk.Frame(self)
        self.lfouter = ctk.ScrolledFrame(self, orient="horizontal")
        self.lf = ctk.Frame(self.lfouter)
        self.lf.pack(side="left", anchor="nw")
        self.lf.bind(
            "<Configure>",
            lambda event: self.lfouter.viewport.configure(
                height=self.lf.winfo_reqheight()
            ),
        )
        ctk.Label(self.lf, text="LaTeX:").grid(column=0, row=0, padx=10, pady=10)
        self.latexbold = ctk.Button(self.lf, text="Bold", command=self.boldlatex)
        self.latexbold.grid(column=1, row=0, padx=10, pady=10)
        self.latexitalic = ctk.Button(self.lf, text="Italic", command=self.italiclatex)
        self.latexitalic.grid(column=2, row=0, padx=10, pady=10)
        self.latexunderline = ctk.Button(
            self.lf, text="Underline", command=self.underlinelatex
        )
        self.latexunderline.grid(column=3, row=0, padx=10, pady=10)
        self.latexsubscript = ctk.Button(
            self.lf, text="Subscript", command=self.subscriptlatex
        )
        self.latexsubscript.grid(column=4, row=0, padx=10, pady=10)
        self.latexsuperscript = ctk.Button(
            self.lf, text="Superscript", command=self.superscriptlatex
        )
        self.latexsuperscript.grid(column=5, row=0, padx=10, pady=10)
        self.latexnumberlist = ctk.Button(
            self.lf, text="Numbered List", command=self.numberlistlatex
        )
        self.latexnumberlist.grid(column=6, row=0, padx=10, pady=10)
        self.latexbulletlist = ctk.Button(
            self.lf, text="Bullet List", command=self.bulletlistlatex
        )
        self.latexbulletlist.grid(column=7, row=0, padx=10, pady=10)
        self.latexsectionvar = tk.StringVar(self.lf)
        self.latexsection = ctk.OptionMenu(
            self.lf,
            self.latexsectionvar,
            "Section",
            "Subsection",
            "Subsubsection",
            command=self.sectionlatex,
            solid=True,
        )
        self.latexsection.grid(column=8, row=0, padx=10, pady=10)
        self.latexparagraph = ctk.Button(
            self.lf, text="Paragraph", command=self.paragraphlatex
        )
        self.latexparagraph.grid(column=9, row=0, padx=10, pady=10)
        self.latexequation = ctk.Button(
            self.lf, text="Equation", command=self.equationlatex
        )
        self.latexequation.grid(column=10, row=0, padx=10, pady=10)
        self.latexcharvar = tk.StringVar(state.root)
        self.latexmath = ctk.OptionMenu(
            self.lf,
            self.latexcharvar,
            "Multiplication",
            "Division",
            "Less or equal",
            "More or equal",
            "Not equal",
            "Infinity",
            "Summation",
            "Integral",
            "Pi",
            "Theta",
            "Alpha Lower",
            "Alpha Upper",
            "Inline Math",
            command=self.mathlatex,
            solid=True,
        )
        self.latexmath.grid(column=11, row=0, padx=10, pady=10)
        self.mf.pack(fill="both", expand=True)
        if view_master is None:
            self.type_ = cursortextbox.CustomTextbox(
                self.mf,
                scrolled=True,
                cursor_shape=cursortextbox.CURSOR_SHAPES[state.curcurtype],
                font=(state.defs[2], 12),
                wrap="word",
                undo=True,
                autoseparators=True,
                line_numbers=True,
            )
        else:
            self.type_ = self._make_peer_type(view_master)
        self.undoset = False
        self.type_.bind(
            "<<Modified>>",
            lambda event: [
                setattr(self, "undoset", False),
                self.type_.edit_modified(False),
            ],
        )
        self.mainwidget = self.type_
        self._wire_type()
        self.type_top = "1.0"
        self.type_bottom = "end"
        self._ha_after_id = None
        self._ha_apply_after_id = None
        self._find_apply_after_id = None
        self._filesize_after_id = None
        self._setundo_after_id = None
        self._unsaved_after_id = None
        self._prev_visible_region = None
        self._main_poll_after_id = None
        self._type_setview_after_id = None
        self._do_backup_after_id = None
        self._main_queue = queue.Queue()
        self._selectionpoint = None
        if view_master is None:
            self.unsaved = False
            self.unsavedtext = ""
            self.hmode = "normal"
            self.title = ""
            self.setwanttitle("Untitled")
            self.imageloaded = False
            self.file_editing_own = False
            self._file_watch_prompt_pending = False
            self._python_scopes = [{"start": 1, "end": 1, "parent": None, "names": {}}]
            self._python_call_kwargs = {}
            self._python_module_literals = []
            self._python_literal_attrs = []
            self._python_name_positions = []
            self._python_def_names = []
            self._python_typed_attrs = []
            self._python_param_default_tags = []
            self._python_kwarg_positions = []
            self._python_import_dotted_lines = []
            self._python_import_orig_name_tags = []
            self._python_instance_name_positions = set()
            self._python_global_stmt_kind_positions = {}
            self._python_names_scan_thread = None
            self._python_scan_after_id = None
            self._python_edit_generation = [0]
            self._python_module_spec_cache = {}
            self._python_module_members_cache = {}
            self._python_module_class_members_cache = {}
            self._python_module_func_params_cache = {}
            self._ha_running = [False]
            self._ha_pending = [None]
            self.m = ctk.Menu(state.root)
            for label, menu in state.all_editor_menus.items():
                self.m.add_cascade(label=label, menu=menu)
        else:
            self.m = view_master.m
            view_master.view_children.append(self)
        if view_master is None:
            self.init_hl_tags()
            self.init_plugin_tags()
            self.type_.edit_reset()
            python_scope_build._python_reset_scan_state(self)
        self.type_setview()
        self._main_poll()
        if view_master is None:
            self.do_backup()
        if view_master is None:
            if file:
                self.ld(file)
        else:
            self._sync_chrome()
        self._bind_focus_recursive(
            self,
            (self._own_type,)
            + ((self.imageload,) if getattr(self, "imageload", None) else ()),
        )
        for code in state.editor_init_code:
            try:
                exec(code, vars(state), locals())
            except Exception as error:
                error = str(error)
                state.root.error("Error", f"Error in editor init code:\n{error}")

    def setcursortype(self, new):
        self._own_type.set_cursor_shape(new)

    def close(self):
        """Confirm/save before closing this pane. Only actually asks
        to save if this is the last reference to the file (not a view
        with other peers still open on it, and not itself a master
        that peers are viewing).
        """
        if self._file_watch_prompt_pending:
            utils.show(
                "select 'Discard Changes & Reload' or 'Ignore' external changes before closing the editor"
            )
            return False
        is_last_reference = self.view_master is None and not self.view_children
        answer = (
            state.root.ask(
                "Warning",
                "Do you want to save file before closing?",
                options=("yes", "no", "cancel"),
            )
            if (self.unsaved and is_last_reference)
            else False
        )
        if answer != None:
            if answer:
                if not self.saveforclose():
                    return False
            self._detach_before_close()
            return True
        return False

    def _file_watch_prompt(self):
        """Ask whether to reload the file (discarding unsaved changes)
        or keep editing and overwrite it on next save, after
        FileChangeHandler detected an external change.
        """
        answer = state.root.warning(
            "Warning",
            f'The file "{self.title}" has changed on disk. Should PyNotes discard unsaved changes and reload the file, or overwrite the file on next save?',
            buttons=["Ignore", "Discard Changes & Reload"],
        )
        self._file_watch_prompt_pending = False
        if answer == "Discard Changes & Reload":
            self.ld(self.title)

    def setselpoint(self, index=None):
        """Set the selection point at index (the cursor if not given):
        an anchor that subsequent cursor movement (selkeypress()) then
        extends into a selection from, an Emacs-style alternative to
        drag-selecting.
        """
        if index is None:
            index = self.type_.index("insert")
        self.selectionpoint = index
        utils.show(f"selection point set at {self.selectionpoint}")

    def removeselpoint(self):
        if self.selectionpoint:
            self.selectionpoint = None
            utils.show("removed selection point")
        else:
            utils.show("no selection point set")

    def toggleselpoint(self):
        if self.selectionpoint:
            self.removeselpoint()
        else:
            self.setselpoint()

    def lld(self):
        """PyCode's/Alt-X's `openfile` command: prompt for a file and
        load it into this pane (via _smart_open()).
        """
        if self._file_watch_prompt_pending:
            utils.show(
                "select 'Discard Changes & Reload' or 'Ignore' external changes before loading another file"
            )
            return
        fn = dialogs.openfileget(
            (
                ("All Files", "*"),
                ("Python Files", "*.py"),
                ("Text Files", "*.txt"),
                ("LaTeX Files", "*.tex"),
                ("PNG Images", "*.png"),
                ("PDF Files", "*.pdf"),
                ("ePub Files", "*.epub"),
            )
        )
        pycode.pcrunhook("before", "open-file-current-editor", fn if fn else None)
        if fn:
            utils.show("open file")
            self._smart_open(fn)
            pycode.pcrunhook("after", "open-file-current-editor", fn)

    def ssssv(self, nm):
        """Save to nm if given, otherwise just clear the title (via
        clt()) - the shared save-to-known-path logic behind sssv()
        (Save) and saveforclose(); redirects to view_master if this is
        a view, since only the master actually owns the file state.
        """
        if self.view_master:
            return self.view_master.ssssv(nm)
        if self._file_watch_prompt_pending:
            utils.show("select 'Ignore' external changes before saving file")
            return False
        if not nm == "":
            return self.sv(nm)
        self.clt(nm)
        return True

    def _sync_wanttitle(self):
        """Update the buffer/window title from the current filename and
        unsaved state.
        """
        self.setwanttitle(
            os.path.basename(self.title) + (" *" if self.unsaved else "")
            if self.title
            else "Untitled"
        )

    def clt(self, nt):
        """Set the title to nt (or clear it, if nt == "") without
        writing any file content: updates the file-info bar/window
        title, marks unsaved False, and (re)starts the file-watcher for
        the new path. Used both after an actual save (sv()) and to
        just rename/detitle without touching disk.
        """
        if self.view_master:
            return self.view_master.clt(nt)
        if state.active in self._group_members():
            state.pcsettitle = False
        try:
            self.observer.stop()
            self.observer.join()
        except Exception:
            pass
        try:
            if not nt == "":
                self.fileinfoconfig(
                    filename=os.path.basename(nt), filesaved="Saved File"
                )
                self.title = os.path.abspath(nt)
            else:
                self.fileinfoconfig(filename="Untitled", filesaved="Untitled File")
                self.title = ""
            self.unsaved = False
            self._sync_wanttitle()
        except Exception:
            pass
        else:
            self.file_editing_own = False
            if nt == "":
                return
            self.observer = Observer()
            self.observer.schedule(
                self.FileChangeHandler(self),
                os.path.dirname(self.title),
                recursive=False,
            )
            self.observer.start()

    def sssv(self):
        """PyCode's/Alt-X's `savefile` command (Save): save to the
        current title, or prompt for one (ssv()) if there isn't one
        yet.
        """
        if self.view_master:
            return self.view_master.sssv()
        if self._file_watch_prompt_pending:
            utils.show("select 'Ignore' external changes before saving file")
            return
        if not self.title == "":
            pycode.pcrunhook("before", "save-file")
            self.ssssv(self.title)
            pycode.pcrunhook("after", "save-file")
        else:
            self.ssv()

    def saveforclose(self):
        """Save before closing (see Buffer/window.saveforclose()):
        same logic as sssv(), but returning whether it actually
        succeeded so the caller can abort the close on failure/cancel.
        """
        if self.view_master:
            return self.view_master.saveforclose()
        if not self.title == "":
            return self.ssssv(self.title)
        else:
            if self.ssv() == False:
                return False
            else:
                return True

    def ld(self, nm):
        """Load file nm into this pane, replacing whatever it
        currently shows (see _disconnect(), called first to detach
        from any existing view-sharing). Tries to read it as plain
        text; if that fails, tries it as a PNG, then a PDF, then an
        ePub (extracting each to text/a PNG view as appropriate),
        setting the matching HMode/file-info for whichever succeeds.
        """
        if os.path.isdir(nm):
            state.root.error("Error", f'"{nm}" is a directory.')
            return
        if self._file_watch_prompt_pending:
            utils.show(
                "select 'Discard Changes & Reload' or 'Ignore' external changes before loading another file"
            )
            return
        if not nm == "":
            self._disconnect()
            self.hmode = "normal"
            try:
                self.imageload.pack_forget()
                self.imageloaded = False
                self.mainwidget = self.type_
            except Exception:
                pass
            else:
                self.type_.pack(fill="both", expand=True, anchor="n")
                self.mf.pack(fill="both", expand=True)
            self.type_.delete("1.0", "end")
            if os.path.dirname(nm):
                try:
                    os.chdir(os.path.dirname(nm))
                except Exception:
                    state.root.error(
                        "Error",
                        f"The directory '{os.path.dirname(nm)}' does not exist.",
                    )
                    return
                else:
                    nm = os.path.basename(nm)
                    self.type_.edit_reset()
                    python_scope_build._python_reset_scan_state(self)
            if not os.path.exists(nm):
                open(nm, "w", encoding="utf-8")
            try:
                file = open(nm, "r", encoding="utf-8")
                content = file.read()
                self.type_.delete("1.0", "end")
                self.type_.insert("end", content)
                file.close()
            except Exception as error:
                error = str(error)
                try:
                    self.imageload = ctk.Label(self, image=ctk.load_canvas_image(nm))
                    self._bind_focus_recursive(self.imageload)
                    self.imageloaded = True
                    self.mainwidget = self.imageload
                except Exception:
                    try:
                        pdf = pdfplumber.open(nm)
                        self.type_.delete("1.0", "end")
                        for page in pdf.pages:
                            self.type_.insert("end", page.extract_text())
                    except Exception:
                        try:
                            parsed = parser.from_file(nm, service="text")
                            content = parsed["content"]
                            self.type_.delete("1.0", "end")
                            self.type_.insert("end", content)
                        except Exception:
                            state.root.error("Error", error)
                        else:
                            self.clt(nm)
                            self.fileinfoconfig(
                                filesize=str(os.path.getsize(nm)) + " bytes",
                                filetype="EPUB File (*.epub)",
                            )
                            self.sethmenu(None)
                            self.lfouter.pack_forget()
                            self.hmode = "epub"
                            self.keypress()
                    else:
                        self.clt(nm)
                        self.fileinfoconfig(
                            filesize=str(os.path.getsize(nm)) + " bytes",
                            filetype="PDF File (*.pdf)",
                        )
                        self.sethmenu(None)
                        self.lfouter.pack_forget()
                        self.hmode = "pdf"
                        self.keypress()
                else:
                    self.type_.pack_forget()
                    self.mf.pack_forget()
                    self.imageload.pack(fill="both", expand=True)
                    self.imageloaded = True
                    self.mainwidget = self.imageload
                    self.clt(nm)
                    self.fileinfoconfig(
                        filesize=str(os.path.getsize(nm)) + " bytes",
                        filetype="PNG Image (*.png)",
                    )
                    self.hmode = "png"
                    self.imageload.focus_set()
                    self.sethmenu(None)
                    self.lfouter.pack_forget()
                    self.keypress()
            else:
                self.unsavedtext = self.type_.get("1.0", "end-1c")
                self.clt(nm)
                self.fileinfoconfig(filesize=str(os.path.getsize(nm)) + " bytes")
                if os.path.splitext(nm)[1] == ".py":
                    self.pchmode("python")
                elif os.path.splitext(nm)[1] == ".tex":
                    self.pchmode("latex")
                elif os.path.splitext(nm)[1] == ".html":
                    self.pchmode("html")
                elif os.path.splitext(nm)[1] == ".md":
                    self.pchmode("markdown")
                else:
                    self.pchmode("normal")
                self.keypress()
            self.type_.edit_reset()
            python_scope_build._python_reset_scan_state(self)
            self._sync_group_chrome()

    def llld(self):
        """PyCode's/Alt-X's `open` command: confirm discarding unsaved
        changes (offering to save first) if needed, then prompt for and
        load a file (lld()).
        """
        if self._file_watch_prompt_pending:
            utils.show(
                "select 'Discard Changes & Reload' or 'Ignore' external changes before loading another file"
            )
            return
        is_last_reference = self.view_master is None and not self.view_children
        answer = (
            state.root.ask(
                "Warning",
                "Do you want to save file before closing?",
                options=("yes", "no", "cancel"),
            )
            if (self.unsaved and is_last_reference)
            else False
        )
        if answer != None:
            if answer:
                if not self.saveforclose():
                    return
            self.lld()

    def sv(self, nm):
        """Write the editor's content to file nm (which may be
        relative to a changed cwd - a directory component is chdir'd
        into and stripped, creating it if needed), skipping the write
        entirely (and returning True) if the content hasn't actually
        changed. Refuses for png/pdf/epub HModes, which have no
        editable text to write back.
        """
        if self.view_master:
            return self.view_master.sv(nm)
        if self._file_watch_prompt_pending:
            utils.show("select 'Ignore' external changes before saving file")
            return False
        if not nm == "":
            if self.hmode not in ["png", "pdf", "epub"]:
                try:
                    content = self.type_.get("1.0", "end-1c")
                    if os.path.isdir(nm):
                        state.root.error(
                            "Error",
                            f'"{os.path.basename(nm)}" is an already existing directory.',
                        )
                        return False
                    if os.path.dirname(nm):
                        if not os.path.exists(os.path.dirname(nm)):
                            os.makedirs(os.path.dirname(nm), exist_ok=True)
                        os.chdir(os.path.dirname(nm))
                        nm = os.path.basename(nm)
                    if content == self.unsavedtext:
                        utils.show("no changes to save")
                        return True
                    self.file_editing_own = True
                    try:
                        file = open(nm, "w", encoding="utf-8")
                        file.write(content)
                        file.close()
                        self.unsavedtext = content
                        utils.show("save file")
                        self.clt(nm)
                    except Exception as error:
                        error = str(error)
                        state.root.error("Error", error)
                        self.file_editing_own = False
                        return False
                    else:
                        self.file_editing_own = False
                        return True
                except Exception as error:
                    error = str(error)
                    state.root.error("Error", error)
                    return False
            else:
                state.root.error("Error!", "Cannot save files of this type.")
                return False

    def ssv(self):
        """PyCode's/Alt-X's `saveasfile` command (Save As): prompt for
        a filename and save to it. Temporarily highlight the active
        editor to let the user know which file is being saved instead
        of making the first line of the editor the initial filename.
        """
        if self.view_master:
            return self.view_master.ssv()
        if self._file_watch_prompt_pending:
            utils.show("select 'Ignore' external changes before saving file")
            return False
        self.type_.config(fill_color="green")
        fn = dialogs.saveasfileget()
        self.type_.config(fill_color=None)
        pycode.pcrunhook("before", "save-as-file", fn if fn else None)
        if fn:
            utils.show("save as file")
            if not self.sv(fn):
                return False
            self.clt(fn)
            pycode.pcrunhook("after", "save-as-file", fn)
            return True
        else:
            return False

    def nw(self):
        """PyCode's/Alt-X's `newfile` command: confirm discarding
        unsaved changes (offering to save first) if needed, then reset
        this pane to a blank, untitled document.
        """
        is_last_reference = self.view_master is None and not self.view_children
        answer = (
            state.root.ask(
                "Warning",
                "Do you want to save file before closing?",
                options=("yes", "no", "cancel"),
            )
            if (self.unsaved and is_last_reference)
            else False
        )
        if answer != None:
            if answer:
                if not self.saveforclose():
                    return
            pycode.pcrunhook("before", "new-file-current-editor")
            self._disconnect()
            self.hmode = "normal"
            try:
                self.imageload.pack_forget()
                self.imageloaded = False
                self.mainwidget = self.type_
            except Exception:
                pass
            else:
                self.type_.pack(fill="both", expand=True, anchor="n")
                self.mf.pack(fill="both", expand=True)
            self.type_.delete("1.0", "end")
            self.unsavedtext = ""
            self.clt("")
            self.type_.edit_reset()
            python_scope_build._python_reset_scan_state(self)
            self.pchmode("normal")
            self.fileinfoconfig(filesize="0 bytes")
            utils.show("new file")
            pycode.pcrunhook("after", "new-file-current-editor")

    def fr(self, dir="forward"):
        """Open the Find & Replace panel: search-as-you-type finds
        every match of the typed pattern (regex or plain text) in the
        background (updatef()/do_search(), applied to the widget in
        small batches so a large file doesn't freeze the UI),
        highlighting all matches ("found") and the current one
        ("foundhighlight"); Enter/Shift-Enter step to the next/previous
        match (fnext()/fback()), each optionally replacing the current
        match with the typed replacement text first. dir picks where
        the initial search position/direction starts from ("forward"/
        "backward" from the cursor, or "beginning" of the file).
        """
        if dir == "forward":
            utils.show("find & replace text forward")
        elif dir == "backward":
            utils.show("find & replace text backward")
        elif dir == "beginning":
            utils.show("find & replace text from beginning")
        search_anchor = [self.type_.index("insert")]

        def fback(replacetext=None):
            """Step to the previous match, or (replacetext given)
            replace the current match then step to the previous one
            relative to the replacement.
            """
            nonlocal i
            if searching[0]:
                return
            self.type_.tag_remove("foundhighlight", "1.0", "end")
            if not foundlist:
                return
            if replacetext is not None:
                replace_start = foundlist[i][0]
                programmatic_edit[0] = True
                self.type_.delete(foundlist[i][0], foundlist[i][1])
                self.type_.insert(foundlist[i][0], replacetext)
                self.type_.after_idle(clear_programmatic_edit)

                def after_search():
                    nonlocal i
                    for j in range(len(foundlist) - 1, -1, -1):
                        if self.type_.compare(foundlist[j][0], "<", replace_start):
                            i = j
                            self.type_.tag_add(
                                "foundhighlight", foundlist[i][0], foundlist[i][1]
                            )
                            exec(
                                "self.type_.tag_config('foundhighlight',"
                                + state.theme["pynotes:foundhighlight"]
                                + ")"
                            )
                            self.type_.see(foundlist[i][1])
                            self.type_.mark_set("insert", foundlist[i][1])
                            return
                    close_find()

                pending_action[0] = after_search
                updatef()
            else:
                if i != 0:
                    i -= 1
                else:
                    i = len(foundlist) - 1
                self.type_.tag_add("foundhighlight", foundlist[i][0], foundlist[i][1])
                exec(
                    "self.type_.tag_config('foundhighlight',"
                    + state.theme["pynotes:foundhighlight"]
                    + ")"
                )
                self.type_.see(foundlist[i][1])
                self.type_.mark_set("insert", foundlist[i][1])
            self.keypress()

        def fnext(replacetext=None):
            """Step to the next match, or (replacetext given) replace
            the current match then step to the next one relative to
            the replacement.
            """
            nonlocal i
            if searching[0]:
                return
            self.type_.tag_remove("foundhighlight", "1.0", "end")
            if not foundlist:
                return
            if replacetext is not None:
                replace_start = foundlist[i][0]
                programmatic_edit[0] = True
                self.type_.delete(foundlist[i][0], foundlist[i][1])
                self.type_.insert(foundlist[i][0], replacetext)
                self.type_.after_idle(clear_programmatic_edit)
                after_replace = "%s+%dc" % (replace_start, len(replacetext))

                def after_search():
                    nonlocal i
                    for j in range(len(foundlist)):
                        if self.type_.compare(foundlist[j][0], ">=", after_replace):
                            i = j
                            self.type_.tag_add(
                                "foundhighlight", foundlist[i][0], foundlist[i][1]
                            )
                            exec(
                                "self.type_.tag_config('foundhighlight',"
                                + state.theme["pynotes:foundhighlight"]
                                + ")"
                            )
                            self.type_.see(foundlist[i][1])
                            self.type_.mark_set("insert", foundlist[i][1])
                            return
                    close_find()

                pending_action[0] = after_search
                updatef()
            else:
                if i != len(foundlist) - 1:
                    i += 1
                else:
                    i = 0
                self.type_.tag_add("foundhighlight", foundlist[i][0], foundlist[i][1])
                exec(
                    "self.type_.tag_config('foundhighlight',"
                    + state.theme["pynotes:foundhighlight"]
                    + ")"
                )
                self.type_.see(foundlist[i][1])
                self.type_.mark_set("insert", foundlist[i][1])
            self.keypress()

        def replaceall(replacetext):
            """Replace every match from the current one (i) through the
            end of the file - not matches before it - with
            replacetext, then close the panel.
            """
            nonlocal i
            if searching[0]:
                return
            self.type_.tag_remove("foundhighlight", "1.0", "end")
            if not foundlist:
                return
            programmatic_edit[0] = True
            for j in range(len(foundlist) - 1, i - 1, -1):
                self.type_.delete(foundlist[j][0], foundlist[j][1])
                self.type_.insert(foundlist[j][0], replacetext)
            self.type_.after_idle(clear_programmatic_edit)
            close_find()
            self.keypress()

        search_cancel = [None]
        searching = [False]
        pending_action = [None]
        programmatic_edit = [False]

        def clear_programmatic_edit():
            """Clear the flag that tells on_type_modified() to ignore
            an edit made by this search/replace itself, rather than by
            the user, once tkinter's <<Modified>> event for it fires.
            """
            programmatic_edit[0] = False

        def updatef():
            """(Re-)run the search for the current pattern/options in a
            background thread (do_search(), handing its result back to
            the GUI thread via self._main_queue), cancelling any search
            already in progress first; applies the (possibly huge)
            result to the widget's tags in small batches
            (_apply_batch(), scheduled via .after) so highlighting a
            large file's worth of matches doesn't freeze the UI.
            """
            nonlocal i
            nonlocal foundlist
            find = findbox.get()
            useregx = regx.get()
            case = cs.get()
            wholeword = ww.get()
            if search_cancel[0]:
                search_cancel[0].set()
            if self._find_apply_after_id is not None:
                self._own_type.after_cancel(self._find_apply_after_id)
                self._find_apply_after_id = None
            if not find:
                self.type_.tag_remove("found", "1.0", "end")
                self.type_.tag_remove("foundhighlight", "1.0", "end")
                foundlist.clear()
                searching[0] = False
                return
            self.type_.tag_remove("found", "1.0", "end")
            self.type_.tag_remove("foundhighlight", "1.0", "end")
            text_content = self.type_.get("1.0", "end")
            cancel = threading.Event()
            search_cancel[0] = cancel
            searching[0] = True

            def do_search():
                try:
                    pat = find if useregx else re.escape(find)
                    if wholeword:
                        pat = r"\b" + pat + r"\b"
                    flags = 0 if case else re.IGNORECASE
                    compiled = re.compile(pat, flags)
                except Exception:
                    self._main_queue.put(lambda: _start_apply([]))
                    return
                line_starts = [0]
                pos = 0
                while True:
                    pos = text_content.find("\n", pos)
                    if pos == -1:
                        break
                    line_starts.append(pos + 1)
                    pos += 1

                def to_tk(offset):
                    lo, hi = 0, len(line_starts) - 1
                    while lo < hi:
                        mid = (lo + hi + 1) // 2
                        if line_starts[mid] <= offset:
                            lo = mid
                        else:
                            hi = mid - 1
                    return f"{lo + 1}.{offset - line_starts[lo]}"

                tk_results = []
                for m in compiled.finditer(text_content):
                    if cancel.is_set():
                        return
                    if m.start() == m.end():
                        continue
                    tk_results.append((to_tk(m.start()), to_tk(m.end())))
                if not cancel.is_set():
                    self._main_queue.put(lambda: _start_apply(tk_results))

            def _start_apply(tk_results):
                nonlocal i, foundlist
                if cancel.is_set():
                    searching[0] = False
                    return
                foundlist = []
                i = 0
                if tk_results:
                    if dir == "forward":
                        cursor = search_anchor[0]
                        for idx in range(len(tk_results)):
                            if self.type_.compare(tk_results[idx][0], ">=", cursor):
                                i = idx
                                break
                        else:
                            i = 0
                    elif dir == "backward":
                        cursor = search_anchor[0]
                        for idx in range(len(tk_results) - 1, -1, -1):
                            if self.type_.compare(tk_results[idx][0], "<", cursor):
                                i = idx
                                break
                        else:
                            i = len(tk_results) - 1
                _apply_batch(tk_results, len(tk_results), 0)

            def _apply_batch(tk_results, n, idx):
                nonlocal i, foundlist
                if cancel.is_set():
                    self._find_apply_after_id = None
                    searching[0] = False
                    return
                end = idx + 500
                if end > n:
                    end = n
                for k in range(idx, end):
                    st, et = tk_results[k]
                    self._own_type.tag_add("found", st, et)
                    foundlist.append((st, et))
                if end < n:
                    self._find_apply_after_id = self._own_type.after(
                        1, lambda: _apply_batch(tk_results, n, end)
                    )
                else:
                    self._find_apply_after_id = None
                    searching[0] = False
                    if foundlist:
                        exec(
                            "self.type_.tag_config('found',"
                            + state.theme["pynotes:found"]
                            + ")"
                        )
                    action = pending_action[0]
                    pending_action[0] = None
                    if action:
                        action()
                    elif foundlist:
                        self.type_.tag_add(
                            "foundhighlight", foundlist[i][0], foundlist[i][1]
                        )
                        exec(
                            "self.type_.tag_config('foundhighlight',"
                            + state.theme["pynotes:foundhighlight"]
                            + ")"
                        )
                        self.type_.see(foundlist[i][1])
                        self.type_.mark_set("insert", foundlist[i][1])

            threading.Thread(target=do_search, daemon=True).start()

        def updateff(event=None):
            """The Find field's <KeyRelease> handler (also used as the
            option checkboxes' command): re-run the search on any
            change, except a bare Return (no Control held) - that's
            handled by the findbox's own <Return>/<Shift-Return>
            bindings below to step to the next/previous match instead,
            so this just re-highlights the already-current match.
            """
            if (
                not event
                or event
                and not event.keysym == "Return"
                and not (event.state & 4)
            ):
                updatef()
                return
            if not foundlist:
                return
            self.type_.tag_add("foundhighlight", foundlist[i][0], foundlist[i][1])
            exec(
                "self.type_.tag_config('foundhighlight',"
                + state.theme["pynotes:foundhighlight"]
                + ")"
            )
            self.type_.see(foundlist[i][1])
            self.type_.mark_set("insert", foundlist[i][1])

        ok = state.root.subwin()
        if dir == "beginning":
            i = 0
        foundlist = []
        ok.title("Find & Replace")
        ctk.Label(ok, text="Find:").grid(column=0, row=0, padx=10, pady=10)
        findbox = ctk.Entry(ok)
        findbox.focus()
        findbox.bind("<KeyRelease>", updateff)
        if not state.emacskeysforsearch:
            findbox.bind(
                ("<Return>" if dir != "backward" else "<Shift-Return>"),
                lambda event: fnext(),
            )
            findbox.bind(
                ("<Return>" if dir == "backward" else "<Shift-Return>"),
                lambda event: fback(),
            )
        findbox.grid(column=1, row=0, padx=10, pady=10, sticky="ew")
        ctk.Label(ok, text="Replace:").grid(column=0, row=1, padx=10, pady=10)
        replacebox = ctk.Entry(ok)
        if not state.emacskeysforsearch:
            replacebox.bind(
                "<Return>",
                lambda event: (
                    fback(replacebox.get())
                    if dir == "backward"
                    else fnext(replacebox.get())
                ),
            )
        replacebox.grid(column=1, row=1, padx=10, pady=10, sticky="ew")
        cs = tk.BooleanVar(ok)
        ctk.Checkbutton(ok, text="Case Sensitive", variable=cs, command=updateff).grid(
            column=0, row=2, padx=10, pady=10, sticky="ew"
        )
        regx = tk.BooleanVar(ok)
        ctk.Checkbutton(ok, text="Use regexp", variable=regx, command=updateff).grid(
            column=1, row=2, padx=10, pady=10, sticky="ew"
        )
        ww = tk.BooleanVar(ok)
        ctk.Checkbutton(
            ok, text="Match Whole Word Only", variable=ww, command=updateff
        ).grid(column=0, row=3, columnspan=2, padx=10, pady=10, sticky="ew")
        ctk.Button(ok, text="Previous", command=fback).grid(
            column=0, row=4, padx=10, pady=10, sticky="ew"
        )
        ctk.Button(ok, text="Next", command=fnext).grid(
            column=1, row=4, padx=10, pady=10, sticky="ew"
        )

        def replace_current():
            """Replace just the current match with the replacement
            text, staying on (the now-shifted) same match index.
            """
            nonlocal i
            if searching[0] or not foundlist:
                return
            programmatic_edit[0] = True
            self.type_.delete(foundlist[i][0], foundlist[i][1])
            self.type_.insert(foundlist[i][0], replacebox.get())
            self.type_.after_idle(clear_programmatic_edit)
            saved_i = i

            def after_search():
                nonlocal i
                if not foundlist:
                    return
                i = saved_i if saved_i < len(foundlist) else len(foundlist) - 1
                self.type_.tag_add("foundhighlight", foundlist[i][0], foundlist[i][1])
                exec(
                    "self.type_.tag_config('foundhighlight',"
                    + state.theme["pynotes:foundhighlight"]
                    + ")"
                )
                self.type_.see(foundlist[i][1])
                self.type_.mark_set("insert", foundlist[i][1])

            pending_action[0] = after_search
            updatef()

        ctk.Button(ok, text="Replace", command=replace_current).grid(
            column=0, row=5, padx=10, pady=10, sticky="ew"
        )
        ctk.Button(
            ok, text="Replace and next", command=lambda: fnext(replacebox.get())
        ).grid(column=1, row=5, padx=10, pady=10, sticky="ew")
        ctk.Button(
            ok, text="Replace all", command=lambda: replaceall(replacebox.get())
        ).grid(column=0, row=6, padx=10, pady=10, sticky="ew")

        def close_find():
            """Cancel any in-flight search, clear the found/
            foundhighlight tags, and close the panel.
            """
            if search_cancel[0]:
                search_cancel[0].set()
            if self._find_apply_after_id is not None:
                self.type_.after_cancel(self._find_apply_after_id)
                self._find_apply_after_id = None
            self.type_.tag_remove("found", "1.0", "end")
            self.type_.tag_remove("foundhighlight", "1.0", "end")
            self.type_.unbind("<<Modified>>", findmodbindid)
            ok.destroy()

        def on_type_modified(event):
            """Auto-close the panel if the user edits the text some
            other way while it's open (a search/replace's own edits
            set programmatic_edit first to be excluded from this).
            """
            event.widget.edit_modified(False)
            if programmatic_edit[0]:
                return
            close_find()

        self.type_.edit_modified(False)
        state.root.update()
        findmodbindid = self.type_.bind("<<Modified>>", on_type_modified, "+")
        ctk.Button(ok, text="Close", command=close_find).grid(
            column=1, row=6, padx=10, pady=10, sticky="ew"
        )
        if state.emacskeysforsearch:
            ok.bind("<Alt-Return>", lambda event: fnext())
            ok.bind("^", lambda event: fback())
            ok.bind(
                "<Control-t>",
                lambda event: (
                    fback(replacebox.get())
                    if dir == "backward"
                    else fnext(replacebox.get())
                ),
            )
            ok.bind("!", lambda event: replaceall(replacebox.get()))
            ok.bind("<Return>", lambda event: close_find())
            for w in (findbox, replacebox):
                w.bind("^", lambda event: fback() or "break")
                w.bind("!", lambda event: replaceall(replacebox.get()) or "break")
        ok.update()
        utils.lock_window_size(ok)
        ok.bind("<Escape>", lambda event: close_find())
        ok.protocol("WM_DELETE_WINDOW", close_find)

    def f(self, dir="forward"):
        """Open the Find panel: the find-only counterpart of fr()
        (search-as-you-type, batched background search, Enter/
        Shift-Enter to step to the next/previous match) with no
        replace field.
        """
        if dir == "forward":
            utils.show("find text forward")
        elif dir == "backward":
            utils.show("find text backward")
        elif dir == "beginning":
            utils.show("find text from beginning")
        search_anchor = [self.type_.index("insert")]

        def fback():
            """Step to the previous match."""
            nonlocal i
            self.type_.tag_remove("foundhighlight", "1.0", "end")
            if not foundlist:
                return
            if i != 0:
                i -= 1
            else:
                i = len(foundlist) - 1
            self.type_.tag_add("foundhighlight", foundlist[i][0], foundlist[i][1])
            exec(
                "self.type_.tag_config('foundhighlight',"
                + state.theme["pynotes:foundhighlight"]
                + ")"
            )
            self.type_.see(foundlist[i][1])
            self.type_.mark_set("insert", foundlist[i][1])
            self.keypress()

        def fnext():
            """Step to the next match."""
            nonlocal i
            self.type_.tag_remove("foundhighlight", "1.0", "end")
            if not foundlist:
                return
            if i != len(foundlist) - 1:
                i += 1
            else:
                i = 0
            self.type_.tag_add("foundhighlight", foundlist[i][0], foundlist[i][1])
            exec(
                "self.type_.tag_config('foundhighlight',"
                + state.theme["pynotes:foundhighlight"]
                + ")"
            )
            self.type_.see(foundlist[i][1])
            self.type_.mark_set("insert", foundlist[i][1])
            self.keypress()

        search_cancel = [None]

        def updatef():
            """(Re-)run the search for the current pattern/options in a
            background thread, batching the (possibly huge) result's
            application to the widget's tags so it doesn't freeze the
            UI; see fr()'s updatef() for the same logic in more
            detail.
            """
            nonlocal i
            nonlocal foundlist
            find = findbox.get()
            useregx = regx.get()
            case = cs.get()
            wholeword = ww.get()
            if search_cancel[0]:
                search_cancel[0].set()
            if self._find_apply_after_id is not None:
                self._own_type.after_cancel(self._find_apply_after_id)
                self._find_apply_after_id = None
            if not find:
                self.type_.tag_remove("found", "1.0", "end")
                self.type_.tag_remove("foundhighlight", "1.0", "end")
                foundlist.clear()
                return
            self.type_.tag_remove("found", "1.0", "end")
            self.type_.tag_remove("foundhighlight", "1.0", "end")
            text_content = self.type_.get("1.0", "end")
            cancel = threading.Event()
            search_cancel[0] = cancel

            def do_search():
                try:
                    pat = find if useregx else re.escape(find)
                    if wholeword:
                        pat = r"\b" + pat + r"\b"
                    flags = 0 if case else re.IGNORECASE
                    compiled = re.compile(pat, flags)
                except Exception:
                    self._main_queue.put(lambda: _start_apply([]))
                    return
                line_starts = [0]
                pos = 0
                while True:
                    pos = text_content.find("\n", pos)
                    if pos == -1:
                        break
                    line_starts.append(pos + 1)
                    pos += 1

                def to_tk(offset):
                    lo, hi = 0, len(line_starts) - 1
                    while lo < hi:
                        mid = (lo + hi + 1) // 2
                        if line_starts[mid] <= offset:
                            lo = mid
                        else:
                            hi = mid - 1
                    return f"{lo + 1}.{offset - line_starts[lo]}"

                tk_results = []
                for m in compiled.finditer(text_content):
                    if cancel.is_set():
                        return
                    if m.start() == m.end():
                        continue
                    tk_results.append((to_tk(m.start()), to_tk(m.end())))
                if not cancel.is_set():
                    self._main_queue.put(lambda: _start_apply(tk_results))

            def _start_apply(tk_results):
                nonlocal i, foundlist
                if cancel.is_set():
                    return
                foundlist = []
                i = 0
                if tk_results:
                    if dir == "forward":
                        cursor = search_anchor[0]
                        for idx in range(len(tk_results)):
                            if self.type_.compare(tk_results[idx][0], ">=", cursor):
                                i = idx
                                break
                        else:
                            i = 0
                    elif dir == "backward":
                        cursor = search_anchor[0]
                        for idx in range(len(tk_results) - 1, -1, -1):
                            if self.type_.compare(tk_results[idx][0], "<", cursor):
                                i = idx
                                break
                        else:
                            i = len(tk_results) - 1
                _apply_batch(tk_results, len(tk_results), 0)

            def _apply_batch(tk_results, n, idx):
                nonlocal i, foundlist
                if cancel.is_set():
                    self._find_apply_after_id = None
                    return
                end = idx + 500
                if end > n:
                    end = n
                for k in range(idx, end):
                    st, et = tk_results[k]
                    self._own_type.tag_add("found", st, et)
                    foundlist.append((st, et))
                if end < n:
                    self._find_apply_after_id = self._own_type.after(
                        1, lambda: _apply_batch(tk_results, n, end)
                    )
                else:
                    self._find_apply_after_id = None
                    if foundlist:
                        exec(
                            "self.type_.tag_config('found',"
                            + state.theme["pynotes:found"]
                            + ")"
                        )
                        self.type_.tag_add(
                            "foundhighlight", foundlist[i][0], foundlist[i][1]
                        )
                        exec(
                            "self.type_.tag_config('foundhighlight',"
                            + state.theme["pynotes:foundhighlight"]
                            + ")"
                        )
                        self.type_.see(foundlist[i][1])
                        self.type_.mark_set("insert", foundlist[i][1])

            threading.Thread(target=do_search, daemon=True).start()

        def updateff(event=None):
            if (
                not event
                or event
                and not event.keysym == "Return"
                and not (event.state & 4)
            ):
                updatef()
                return
            if not foundlist:
                return
            self.type_.tag_add("foundhighlight", foundlist[i][0], foundlist[i][1])
            exec(
                "self.type_.tag_config('foundhighlight',"
                + state.theme["pynotes:foundhighlight"]
                + ")"
            )
            self.type_.see(foundlist[i][1])
            self.type_.mark_set("insert", foundlist[i][1])

        ok = state.root.subwin()
        if dir == "beginning":
            i = 0
        foundlist = []
        ok.title("Find")
        ctk.Label(ok, text="Find:").grid(column=0, row=0, padx=10, pady=10)
        findbox = ctk.Entry(ok)
        findbox.focus()
        findbox.bind("<KeyRelease>", updateff)
        if not state.emacskeysforsearch:
            findbox.bind(
                ("<Return>" if dir != "backward" else "<Shift-Return>"),
                lambda event: fnext(),
            )
            findbox.bind(
                ("<Return>" if dir == "backward" else "<Shift-Return>"),
                lambda event: fback(),
            )
        findbox.grid(column=1, row=0, padx=10, pady=10, sticky="ew")
        cs = tk.BooleanVar(ok)
        ctk.Checkbutton(ok, text="Case Sensitive", variable=cs, command=updateff).grid(
            column=0, row=1, padx=10, pady=10, sticky="ew"
        )
        regx = tk.BooleanVar(ok)
        ctk.Checkbutton(ok, text="Use regexp", variable=regx, command=updateff).grid(
            column=1, row=1, padx=10, pady=10, sticky="ew"
        )
        ww = tk.BooleanVar(ok)
        ctk.Checkbutton(
            ok, text="Match Whole Word Only", variable=ww, command=updateff
        ).grid(column=0, row=2, columnspan=2, padx=10, pady=10, sticky="ew")
        ctk.Button(ok, text="Previous", command=fback).grid(
            column=0, row=3, padx=10, pady=10, sticky="ew"
        )
        ctk.Button(ok, text="Next", command=fnext).grid(
            column=1, row=3, padx=10, pady=10, sticky="ew"
        )

        def close_find():
            if search_cancel[0]:
                search_cancel[0].set()
            if self._find_apply_after_id is not None:
                self.type_.after_cancel(self._find_apply_after_id)
                self._find_apply_after_id = None
            self.type_.tag_remove("found", "1.0", "end")
            self.type_.tag_remove("foundhighlight", "1.0", "end")
            self.type_.unbind("<<Modified>>", findmodbindid)
            ok.destroy()

        def on_type_modified(event):
            event.widget.edit_modified(False)
            close_find()

        self.type_.edit_modified(False)
        state.root.update()
        findmodbindid = self.type_.bind("<<Modified>>", on_type_modified)
        ctk.Button(ok, text="Close", command=close_find).grid(
            column=1, row=4, padx=10, pady=10, sticky="ew"
        )
        if state.emacskeysforsearch:
            ok.bind("<Control-s>", lambda event: fnext())
            ok.bind("<Control-r>", lambda event: fback())
            ok.bind("<Return>", lambda event: close_find())
        ok.update()
        utils.lock_window_size(ok)
        ok.bind("<Escape>", lambda event: close_find())
        ok.protocol("WM_DELETE_WINDOW", close_find)

    def type_getvisible(self):
        """The (top, bottom) tkinter indices of the currently visible
        text, padded by 2 lines on each side.
        """
        self._own_type.update()
        top = self._own_type.index("@0,0-2l")
        bottom = self._own_type.index(f"@0,{self._own_type.winfo_height()}+2l")
        return (top, bottom)

    def _update_filesize(self):
        """Recompute and show the file size in every pane's info bar."""
        size = len(io.StringIO(self.type_.get("1.0", "end")).read()) - 1
        self.fileinfoconfig(filesize=str(size) + " bytes")

    def trigger_filesize(self):
        """Debounce _update_filesize() after an edit."""
        if self._filesize_after_id is not None:
            self._own_type.after_cancel(self._filesize_after_id)
        self._filesize_after_id = self._own_type.after(
            DEBOUNCE_TIME, self._update_filesize
        )

    def _set_undo_mark(self):
        """Insert an undo separator so the edits since the last one
        are grouped as a single undo step, if one hasn't already been
        placed for this burst of typing.
        """
        if not self.undoset:
            self.type_.edit_separator()
            self.undoset = True

    def trigger_undo_set(self):
        """Debounce _set_undo_mark() after an edit, so a steady burst
        of typing becomes one undo step instead of one per keystroke
        (the <<Modified>> handler in __init__ resets self.undoset as
        soon as any edit happens, so the next debounced call places a
        fresh separator once typing pauses).
        """
        if self._setundo_after_id is not None:
            self._own_type.after_cancel(self._setundo_after_id)
        self._setundo_after_id = self._own_type.after(
            DEBOUNCE_TIME, self._set_undo_mark
        )

    def _update_unsaved(self):
        """Recompute whether the buffer differs from what's on disk
        and update the title/every pane's info bar to match.
        """
        if self.title and self.hmode not in ["png", "pdf", "epub"]:
            if self.type_.get("1.0", "end-1c") != self.unsavedtext:
                self.unsaved = True
                self._sync_wanttitle()
                self.fileinfoconfig(filesaved="Unsaved File")
            else:
                self.unsaved = False
                self._sync_wanttitle()
                self.fileinfoconfig(filesaved="Saved File")

    def trigger_unsaved(self):
        """Debounce _update_unsaved() after an edit."""
        if self._unsaved_after_id is not None:
            self._own_type.after_cancel(self._unsaved_after_id)
        self._unsaved_after_id = self._own_type.after(
            DEBOUNCE_TIME, self._update_unsaved
        )

    def trigger_ha(self, ft):
        """Debounce a re-highlight (ha(ft)) after an edit; redirects to
        view_master since highlighting only needs to run once for a
        file, regardless of which peer view was actually edited.
        """
        if self.view_master is not None:
            return self.view_master.trigger_ha(ft)
        if self._ha_after_id is not None:
            self._own_type.after_cancel(self._ha_after_id)
        self._ha_after_id = self._own_type.after(DEBOUNCE_TIME, lambda: self.ha(ft))

    def python_trigger_name_scan(self):
        """Debounce a Python scope re-scan after an edit (same
        view_master redirect as trigger_ha()).
        """
        if self.view_master is not None:
            return self.view_master.python_trigger_name_scan()
        if self._python_scan_after_id is not None:
            self._own_type.after_cancel(self._python_scan_after_id)
        self._python_scan_after_id = self._own_type.after(
            DEBOUNCE_TIME, lambda: python_scope_build._python_scan_start(self)
        )

    def ha(self, ft):
        """Re-run syntax highlighting for HMode ft over each pane's
        currently visible region (type_top/type_bottom; see
        type_setview()) and apply it to every peer view sharing this
        file.

        _build_ops() computes a plain list of tag operations
        (("remove_all",) / ("add", tag, start, end) / ("remove", ...) /
        ("config", ...) / ("clear_other", ...)) for the given text
        rather than touching the widget directly, so the same work can
        be applied identically to every pane. Python highlighting is
        semantic, driven by the scope analysis python_scope_build
        already computed (self._python_scopes etc., kept up to date by
        python_trigger_name_scan()); LaTeX/HTML/Markdown are regex-
        pattern based. _apply_plugin_ops() then layers on any
        plugin-defined highlighting (or PyCode `color` tags) registered
        for this HMode. The resulting ops are applied to each pane in
        small batches (_apply_chunk(), scheduled via .after) so
        highlighting a large visible region doesn't freeze the UI.
        Re-entrant calls (e.g. from rapid edits) are coalesced via
        self._ha_running/self._ha_pending rather than running
        concurrently; redirects to view_master since highlighting only
        needs to run once for a file.
        """
        if self.view_master is not None:
            return self.view_master.ha(ft)
        if self._ha_running[0]:
            self._ha_pending[0] = ft
            return
        self._ha_running[0] = True
        try:
            snapshots = []
            for member in self._group_members():
                own_type = member._own_type
                top = member.type_top
                bottom = member.type_bottom
                text = own_type.get(top, bottom)
                pre_text = own_type.get("1.0", top)
                snapshots.append((member, own_type, top, bottom, text, pre_text))
            python_scopes = self._python_scopes
            python_call_kwargs = self._python_call_kwargs
            python_module_literals = self._python_module_literals
            python_name_positions = self._python_name_positions
            python_def_names = self._python_def_names
            python_typed_attrs = self._python_typed_attrs
            python_param_default_tags = self._python_param_default_tags
            python_kwarg_positions = self._python_kwarg_positions
            python_import_dotted_lines = self._python_import_dotted_lines
            python_instance_name_positions = self._python_instance_name_positions
            python_global_stmt_kind_positions = self._python_global_stmt_kind_positions
            python_import_orig_name_tags = self._python_import_orig_name_tags
        except Exception:
            self._ha_running[0] = False
            pending = self._ha_pending[0]
            if pending is not None:
                self._ha_pending[0] = None
                self.ha(pending)
            return

        def _build_ops(own_type, top, bottom, text, pre_text):
            """Compute the highlight tag operations for text (the
            visible region from top to bottom in own_type), per the
            HMode ft; pre_text (everything before top) is used where a
            highlight rule needs to know context carried in from above
            the visible region (e.g. whether it starts already inside
            a triple-quoted string or LaTeX environment).
            """
            ops = []
            try:
                ops.append(("remove_all",))
                if ft == "python":
                    ops.extend(
                        _python_highlight_ops(
                            text,
                            top,
                            pre_text,
                            python_scopes,
                            python_call_kwargs,
                            python_module_literals,
                            self._python_literal_attrs,
                            python_name_positions,
                            python_def_names,
                            python_typed_attrs,
                            python_param_default_tags,
                            python_kwarg_positions,
                            python_import_dotted_lines,
                            python_instance_name_positions,
                            python_global_stmt_kind_positions,
                            python_import_orig_name_tags,
                        )
                    )
                elif ft == "latex":
                    pre_n = len(pre_text)
                    pre_i = 0
                    in_math = False
                    math_close = ""
                    while pre_i < pre_n:
                        pc = pre_text[pre_i]
                        if pc == "\\" and pre_i + 1 < pre_n:
                            nc = pre_text[pre_i + 1]
                            if not in_math and nc == "[":
                                in_math = True
                                math_close = "\\]"
                                pre_i += 2
                                continue
                            if not in_math and nc == "(":
                                in_math = True
                                math_close = "\\)"
                                pre_i += 2
                                continue
                            if in_math and math_close == "\\]" and nc == "]":
                                in_math = False
                                pre_i += 2
                                continue
                            if in_math and math_close == "\\)" and nc == ")":
                                in_math = False
                                pre_i += 2
                                continue
                            pre_i += 2
                            continue
                        if pc == "%":
                            while pre_i < pre_n and pre_text[pre_i] != "\n":
                                pre_i += 1
                            continue
                        if pc == "$":
                            if pre_i + 1 < pre_n and pre_text[pre_i + 1] == "$":
                                if in_math and math_close == "$$":
                                    in_math = False
                                elif not in_math:
                                    in_math = True
                                    math_close = "$$"
                                pre_i += 2
                                continue
                            else:
                                if in_math and math_close == "$":
                                    in_math = False
                                elif not in_math:
                                    in_math = True
                                    math_close = "$"
                        pre_i += 1
                    if in_math:
                        j = text.find(math_close)
                        if j == -1:
                            j = len(text)
                        else:
                            j += len(math_close)
                        ops.append(("add", "hla", f"{top}+0c", f"{top}+{j}c"))
                    for m in _LATEX_MATH_PAT.finditer(text):
                        ops.append(
                            ("add", "hla", f"{top}+{m.start()}c", f"{top}+{m.end()}c")
                        )
                    pre_n = len(pre_text)
                    env_stack = []
                    for em in re.finditer(r"\\(begin|end){\s*(\w+\*?)\s*}", pre_text):
                        ename = em.group(2)
                        if ename == "document":
                            continue
                        if em.group(1) == "begin":
                            env_stack.append((ename, em.start()))
                        elif env_stack and env_stack[-1][0] == ename:
                            env_stack.pop()
                    scan_from = 0
                    if env_stack:
                        outer_name, outer_start = env_stack[0]
                        region = own_type.get(f"1.0+{outer_start}c", bottom)
                        env_pat = re.compile(
                            r"\\(begin|end){\s*" + re.escape(outer_name) + r"\s*}"
                        )
                        m0 = env_pat.match(region)
                        depth = 1
                        search_from = m0.end() if m0 else len(region)
                        while depth > 0:
                            em2 = env_pat.search(region, search_from)
                            if not em2:
                                search_from = len(region)
                                break
                            if em2.group(1) == "begin":
                                depth += 1
                            else:
                                depth -= 1
                            search_from = em2.end()
                        end_abs = outer_start + search_from
                        ops.append(
                            ("add", "hlb", f"1.0+{outer_start}c", f"1.0+{end_abs}c")
                        )
                        scan_from = max(0, end_abs - pre_n)
                    tn = len(text)
                    for begin_m in re.finditer(
                        r"\\begin{\s*(\w+\*?)\s*}", text[scan_from:]
                    ):
                        if begin_m.group(1) == "document":
                            continue
                        env_name = re.escape(begin_m.group(1))
                        search_from2 = scan_from + begin_m.end()
                        bstart = scan_from + begin_m.start()
                        depth2 = 1
                        env_pat2 = re.compile(r"\\(begin|end){\s*" + env_name + r"\s*}")
                        bend = tn
                        while depth2 > 0:
                            em3 = env_pat2.search(text, search_from2)
                            if not em3:
                                break
                            if em3.group(1) == "begin":
                                depth2 += 1
                            else:
                                depth2 -= 1
                            search_from2 = em3.end()
                            if depth2 == 0:
                                bend = em3.end()
                        ops.append(("add", "hlb", f"{top}+{bstart}c", f"{top}+{bend}c"))
                    for m in re.finditer(r"\\[a-zA-Z@]+\*?", text):
                        ops.append(
                            ("add", "hld", f"{top}+{m.start()}c", f"{top}+{m.end()}c")
                        )
                    for i in range(len(text)):
                        if text[i] == "{" and (i == 0 or text[i - 1] != "\\"):
                            j = _find_closing_brace(text, i)
                            ops.append(("add", "hle", f"{top}+{i}c", f"{top}+{j}c"))
                    for m in re.finditer(r"\\\\|&|\|", text):
                        ops.append(
                            ("add", "hlf", f"{top}+{m.start()}c", f"{top}+{m.end()}c")
                        )
                    for i in range(len(text)):
                        if text[i] == "[" and (i == 0 or text[i - 1] != "\\"):
                            j = _find_closing_bracket(text, i)
                            ops.append(("add", "hlg", f"{top}+{i}c", f"{top}+{j}c"))
                    for m in _LH_PAT.finditer(text):
                        s = f"{top}+{m.start()}c"
                        e = f"{top}+{m.end()}c"
                        ops.append(("add", "hlh", s, e))
                elif ft == "html":
                    last_open = pre_text.rfind("<!--")
                    last_close = pre_text.rfind("-->")
                    if last_open != -1 and last_close < last_open:
                        close_pos = text.find("-->")
                        j = (close_pos + 3) if close_pos != -1 else len(text)
                        ops.append(("add", "hcmt", f"{top}+0c", f"{top}+{j}c"))
                    for m in _HC_PAT.finditer(text):
                        s = f"{top}+{m.start()}c"
                        e = f"{top}+{m.end()}c"
                        ops.append(("add", "hcmt", s, e))
                    hi = 0
                    htlen = len(text)
                    while hi < htlen:
                        if text[hi] != "<" or hi >= htlen - 1:
                            hi += 1
                            continue
                        hj = _find_closing_tag(text, hi)
                        htag_inner = text[hi:hj]
                        if text[hi + 1] == "!":
                            if re.match(r"<!DOCTYPE\b", htag_inner, re.IGNORECASE):
                                ops.append(
                                    ("add", "hstuff", f"{top}+{hi}c", f"{top}+{hj}c")
                                )
                            hi = hj
                            continue
                        if hj > hi + 1 and (
                            text[hi + 1].isalpha() or text[hi + 1] == "/"
                        ):
                            ops.append(
                                ("add", "hstuff", f"{top}+{hi}c", f"{top}+{hj}c")
                            )
                            htn_m = re.match(
                                r"</?([a-zA-Z][a-zA-Z0-9:-]*)",
                                htag_inner,
                                re.IGNORECASE,
                            )
                            hattrs_off = htn_m.end() if htn_m else 1
                            for ham in _HTML_ATTR_PAT.finditer(htag_inner, hattrs_off):
                                ops.append(
                                    (
                                        "add",
                                        "hattr",
                                        f"{top}+{hi + ham.start(1)}c",
                                        f"{top}+{hi + ham.end(1)}c",
                                    )
                                )
                                ops.append(
                                    (
                                        "add",
                                        "hstr",
                                        f"{top}+{hi + ham.start(2)}c",
                                        f"{top}+{hi + ham.end(2)}c",
                                    )
                                )
                            for hbm in _HTML_BOOL_ATTR_PAT.finditer(
                                htag_inner, hattrs_off
                            ):
                                ops.append(
                                    (
                                        "add",
                                        "hattr",
                                        f"{top}+{hi + hbm.start()}c",
                                        f"{top}+{hi + hbm.end()}c",
                                    )
                                )
                        hi = hj
                elif ft == "markdown":
                    last_open = pre_text.rfind("<!--")
                    last_close = pre_text.rfind("-->")
                    if last_open != -1 and last_close < last_open:
                        close_pos = text.find("-->")
                        j = (close_pos + 3) if close_pos != -1 else len(text)
                        ops.append(("add", "hcmt", f"{top}+0c", f"{top}+{j}c"))
                    for m in _HC_PAT.finditer(text):
                        s = f"{top}+{m.start()}c"
                        e = f"{top}+{m.end()}c"
                        ops.append(("add", "hcmt", s, e))
                    mhi = 0
                    mhtlen = len(text)
                    while mhi < mhtlen:
                        if text[mhi] != "<" or mhi >= mhtlen - 1:
                            mhi += 1
                            continue
                        mhj = _find_closing_tag(text, mhi)
                        mhtag_inner = text[mhi:mhj]
                        if text[mhi + 1] == "!":
                            if re.match(r"<!DOCTYPE\b", mhtag_inner, re.IGNORECASE):
                                ops.append(
                                    ("add", "hstuff", f"{top}+{mhi}c", f"{top}+{mhj}c")
                                )
                            mhi = mhj
                            continue
                        if mhj > mhi + 1 and (
                            text[mhi + 1].isalpha() or text[mhi + 1] == "/"
                        ):
                            ops.append(
                                ("add", "hstuff", f"{top}+{mhi}c", f"{top}+{mhj}c")
                            )
                            mhtn_m = re.match(
                                r"</?([a-zA-Z][a-zA-Z0-9:-]*)",
                                mhtag_inner,
                                re.IGNORECASE,
                            )
                            mhattrs_off = mhtn_m.end() if mhtn_m else 1
                            for mham in _HTML_ATTR_PAT.finditer(
                                mhtag_inner, mhattrs_off
                            ):
                                ops.append(
                                    (
                                        "add",
                                        "hattr",
                                        f"{top}+{mhi + mham.start(1)}c",
                                        f"{top}+{mhi + mham.end(1)}c",
                                    )
                                )
                                ops.append(
                                    (
                                        "add",
                                        "hstr",
                                        f"{top}+{mhi + mham.start(2)}c",
                                        f"{top}+{mhi + mham.end(2)}c",
                                    )
                                )
                            for mhbm in _HTML_BOOL_ATTR_PAT.finditer(
                                mhtag_inner, mhattrs_off
                            ):
                                ops.append(
                                    (
                                        "add",
                                        "hattr",
                                        f"{top}+{mhi + mhbm.start()}c",
                                        f"{top}+{mhi + mhbm.end()}c",
                                    )
                                )
                        mhi = mhj
                    for m in _MDH_PAT.finditer(text):
                        level = len(m.group(1))
                        s = f"{top}+{m.start()}c"
                        e = f"{top}+{m.end()}c"
                        for htag in _MD_HTML_TAGS:
                            ops.append(("remove", htag, s, e))
                        ops.append(("add", f"hmh{level}", s, e))
                    for m in _MDB_PAT.finditer(text):
                        s = f"{top}+{m.start()}c"
                        e = f"{top}+{m.end()}c"
                        for htag in _MD_HTML_TAGS:
                            ops.append(("remove", htag, s, e))
                        ops.append(("add", "hmb", s, e))
                    for m in _MDI_PAT.finditer(text):
                        s = f"{top}+{m.start()}c"
                        e = f"{top}+{m.end()}c"
                        for htag in _MD_HTML_TAGS:
                            ops.append(("remove", htag, s, e))
                        ops.append(("add", "hmi", s, e))
                    for m in _MDBI_PAT.finditer(text):
                        s = f"{top}+{m.start()}c"
                        e = f"{top}+{m.end()}c"
                        ops.append(("add", "hmbi", s, e))
                    for m in _MDS_PAT.finditer(text):
                        s = f"{top}+{m.start()}c"
                        e = f"{top}+{m.end()}c"
                        for htag in _MD_HTML_TAGS:
                            ops.append(("remove", htag, s, e))
                        ops.append(("add", "hms", s, e))
                    for m in _MDC_PAT.finditer(text):
                        s = f"{top}+{m.start()}c"
                        e = f"{top}+{m.end()}c"
                        ops.append(("add", "hmc", s, e))
                    for m in _MDL_PAT.finditer(text):
                        s = f"{top}+{m.start()}c"
                        e = f"{top}+{m.end()}c"
                        ops.append(("add", "hml", s, e))
                    for m in _MDQ_PAT.finditer(text):
                        s = f"{top}+{m.start()}c"
                        e = f"{top}+{m.end()}c"
                        for htag in _MD_HTML_TAGS:
                            ops.append(("remove", htag, s, e))
                        ops.append(("add", "hmq", s, e))
                    pre_n = len(pre_text)
                    pre_i = 0
                    in_fence = False
                    while pre_i < pre_n:
                        if (pre_i == 0 or pre_text[pre_i - 1] == "\n") and pre_text[
                            pre_i : pre_i + 3
                        ] == "```":
                            j = pre_i + 3
                            while j < pre_n and pre_text[j] != "\n":
                                j += 1
                            if j < pre_n:
                                j += 1
                            k = j
                            found_close = False
                            while k < pre_n:
                                if (k == 0 or pre_text[k - 1] == "\n") and pre_text[
                                    k : k + 3
                                ] == "```":
                                    k += 3
                                    while k < pre_n and pre_text[k] != "\n":
                                        k += 1
                                    if k < pre_n:
                                        k += 1
                                    found_close = True
                                    break
                                k += 1
                            if found_close:
                                pre_i = k
                            else:
                                in_fence = True
                                break
                        else:
                            pre_i += 1
                    n = len(text)
                    i = 0
                    if in_fence:
                        j = 0
                        found_close = False
                        while j < n:
                            if (j == 0 or text[j - 1] == "\n") and text[
                                j : j + 3
                            ] == "```":
                                j += 3
                                while j < n and text[j] != "\n":
                                    j += 1
                                if j < n:
                                    j += 1
                                found_close = True
                                break
                            j += 1
                        if not found_close:
                            j = n
                        ops.append(("add", "hmf", f"{top}+0c", f"{top}+{j}c"))
                        i = j
                    while i < n:
                        if (i == 0 or text[i - 1] == "\n") and text[i : i + 3] == "```":
                            j = i + 3
                            while j < n and text[j] != "\n":
                                j += 1
                            if j < n:
                                j += 1
                            k = j
                            found_close = False
                            while k < n:
                                if (k == 0 or text[k - 1] == "\n") and text[
                                    k : k + 3
                                ] == "```":
                                    k += 3
                                    while k < n and text[k] != "\n":
                                        k += 1
                                    if k < n:
                                        k += 1
                                    found_close = True
                                    break
                                k += 1
                            if not found_close:
                                k = n
                            ops.append(("add", "hmf", f"{top}+{i}c", f"{top}+{k}c"))
                            i = k
                        else:
                            i += 1
            except Exception:
                pass
            return ops

        def _apply_plugin_ops(text, top, ops):
            """Append tag operations for any plugin-defined highlighting
            registered for HMode ft in state.plugin_hl: either a
            {func, if, hl, else} dict (func optionally run first, hl
            evaluated - and its operations appended - only if the if
            condition, default True, evaluates truthy, else else_fn is
            run if given), or a callable given (text, top, ops) to
            append its own operations to. (PyCode `color` tags, see
            pycode.pccolor(), also live in state.plugin_hl as a plain
            {tag: (pattern, theme_key)} mapping, but under a synthetic
            key that never equals a real ft, so they're invisible here
            - they're only consumed by init_plugin_tags(), to
            pre-build the tag_config for later manual use via PyCode's
            `tag` command.)
            """
            if ft in state.plugin_hl:
                entry = state.plugin_hl[ft]
                plugin_name = entry.get("plugin", "") if isinstance(entry, dict) else ""
                if isinstance(entry, dict):
                    func = entry.get("func", None)
                    cond = entry.get("if", True)
                    hl = entry.get("hl", "{}")
                    else_fn = entry.get("else", None)
                    if func is not None:
                        try:
                            exec(func, vars(state))
                        except Exception as error:
                            error = str(error)
                            msg = f'There was an error in running the function "{func}" before syntax highlighting by the plugin "{plugin_name}":\n{error}'
                            state.root.error("Error", msg)
                    try:
                        cond_result = bool(eval(cond, vars(state)))
                    except Exception as error:
                        msg = f'There was an error in evaluating the condition "{cond}" for syntax highlighting by the plugin "{plugin_name}":\n{error}'
                        state.root.error("Error", msg)
                        cond_result = False
                    if cond_result:
                        try:
                            hl_value = eval(hl, vars(state))
                        except Exception as error:
                            error = str(error)
                            msg = f'There was an error in syntax highlighting of the plugin "{plugin_name}":\n{error}'
                            state.root.error("Error", msg)
                            hl_value = {}
                        if callable(hl_value):
                            try:
                                hl_value(text, top, ops)
                            except Exception as error:
                                error = str(error)
                                msg = f'There was an error in syntax highlighting of the plugin "{plugin_name}":\n{error}'
                                state.root.error("Error", msg)
                        else:
                            for tag, (pat, theme_key) in hl_value.items():
                                try:
                                    for m in pat.finditer(text):
                                        ops.append(
                                            (
                                                "add",
                                                tag,
                                                f"{top}+{m.start()}c",
                                                f"{top}+{m.end()}c",
                                            )
                                        )
                                    ops.append(("config", tag, state.theme[theme_key]))
                                except Exception as error:
                                    error = str(error)
                                    msg = f'There was an error in syntax highlighting of the plugin "{plugin_name}":\n{error}'
                                    state.root.error("Error", msg)
                    elif else_fn is not None:
                        try:
                            exec(else_fn, vars(state))
                        except Exception as error:
                            error = str(error)
                            msg = f'There was an error in running the else block in the syntax highlighting of the plugin "{plugin_name}":\n{error}'
                            state.root.error("Error", msg)
                elif callable(entry):
                    try:
                        entry(text, top, ops)
                    except Exception as error:
                        error = str(error)
                        msg = f'There was an error in syntax highlighting of the plugin "{plugin_name}":\n{error}'
                        state.root.error("Error", msg)
                else:
                    for tag, (pat, theme_key) in entry.items():
                        try:
                            for m in pat.finditer(text):
                                ops.append(
                                    (
                                        "add",
                                        tag,
                                        f"{top}+{m.start()}c",
                                        f"{top}+{m.end()}c",
                                    )
                                )
                        except Exception as error:
                            error = str(error)
                            msg = f'There was an error in syntax highlighting of the plugin "{plugin_name}":\n{error}'
                            state.root.error("Error", msg)

        def do_hl():
            results = [
                (
                    member,
                    own_type,
                    top,
                    bottom,
                    text,
                    _build_ops(own_type, top, bottom, text, pre_text),
                )
                for member, own_type, top, bottom, text, pre_text in snapshots
            ]
            self._main_queue.put(lambda: _finish_all(results))

        def _done():
            self._ha_running[0] = False
            pending = self._ha_pending[0]
            if pending is not None:
                self._ha_pending[0] = None
                self.ha(pending)

        def _finish_all(results):
            def _process(i):
                if i >= len(results):
                    _done()
                    return
                member, own_type, top, bottom, text, ops = results[i]
                _apply_plugin_ops(text, top, ops)
                _finish_one(
                    member, own_type, top, bottom, text, ops, lambda: _process(i + 1)
                )

            _process(0)

        def _finish_one(member, own_type, top, bottom, text, ops, on_done):
            try:
                if not own_type.winfo_exists():
                    on_done()
                    return
                if own_type.get(top, bottom) != text:
                    on_done()
                    return
                all_tags = set(own_type.tag_names())
                removable_tags = [
                    tag
                    for tag in all_tags
                    if tag not in state._EDITOR_HL_SKIP_REMOVE_TAGS
                    and (
                        tag not in state.skiptags
                        or member.hmode not in state.skiptags[tag]
                    )
                ]
                _HA_CHUNK_SIZE = 4000

                def _apply_chunk(start):
                    """Apply ops[start : start + _HA_CHUNK_SIZE] to
                    own_type, then reschedule itself for the next chunk
                    (via .after(0, ...)) if there's more, so a large
                    ops list doesn't freeze the UI applying it all in
                    one go.
                    """
                    try:
                        end = min(start + _HA_CHUNK_SIZE, len(ops))
                        for op in ops[start:end]:
                            if op[0] == "remove_all":
                                for tag in removable_tags:
                                    own_type.tag_remove(tag, top, bottom)
                            elif op[0] == "add":
                                for tag in removable_tags:
                                    if tag != op[1] and not (
                                        ft == "latex"
                                        and tag == "hlb"
                                        and op[1] != "hlb"
                                    ):
                                        own_type.tag_remove(tag, op[2], op[3])
                                own_type.tag_add(op[1], op[2], op[3])
                                if ft == "latex" and op[1] != "hlb":
                                    own_type.tag_raise(op[1], "hlb")
                            elif op[0] == "remove":
                                own_type.tag_remove(op[1], op[2], op[3])
                            elif op[0] == "config":
                                exec(
                                    "own_type.tag_config('" + op[1] + "'," + op[2] + ")"
                                )
                            elif op[0] == "clear_other":
                                for tag in removable_tags:
                                    own_type.tag_remove(tag, op[1], op[2])
                        own_type.tag_raise("sel")
                        if end < len(ops):
                            member._ha_apply_after_id = state.root.after(
                                0, lambda: _apply_chunk(end)
                            )
                        else:
                            member._ha_apply_after_id = None
                            on_done()
                    except Exception as error:
                        member._ha_apply_after_id = None
                        error = str(error)
                        state.root.error(
                            "Error!",
                            f"Error:{error}\nInvalid colour settings.\nQuitting syntax highlighting.",
                        )
                        on_done()

                _apply_chunk(0)
            except Exception as error:
                error = str(error)
                state.root.error(
                    "Error!",
                    f"Error:{error}\nInvalid colour settings.\nQuitting syntax highlighting.",
                )
                on_done()

        threading.Thread(target=do_hl, daemon=True).start()

    def init_hl_tags(self):
        """(Re-)create every built-in syntax-highlight tag (Python,
        LaTeX, HTML, Markdown) from the current theme (state.theme),
        the same "exec a Python attribute-config expression written in
        terms of `type_`" pattern as
        pythonshell.PythonShellBuffer.init_pythonshell_hl_tags(). Called
        on init and after a theme change.
        """
        [
            self._own_type.tag_delete(tag)
            for tag in (
                "hpa",
                "hpb",
                "hpv",
                "hpi",
                "hpf",
                "hpx",
                "hpfa",
                "hpm",
                "hpo",
                "hpd",
                "hpc",
                "hla",
                "hlb",
                "hld",
                "hle",
                "hlf",
                "hlg",
                "hlh",
                "hstuff",
                "hattr",
                "hstr",
                "hcmt",
                "hmh1",
                "hmh2",
                "hmh3",
                "hmh4",
                "hmh5",
                "hmh6",
                "hmb",
                "hmi",
                "hmbi",
            )
        ]
        exec(
            "self._own_type.tag_config('hpa',"
            + state.theme["python:keywords"].replace("type_", "self._own_type")
            + ")"
        )
        exec(
            "self._own_type.tag_config('hpb',"
            + state.theme["python:inbuilt"].replace("type_", "self._own_type")
            + ")"
        )
        exec(
            "self._own_type.tag_config('hpv',"
            + state.theme["python:variable_names"].replace("type_", "self._own_type")
            + ")"
        )
        exec(
            "self._own_type.tag_config('hpi',"
            + state.theme["python:class_instances"].replace("type_", "self._own_type")
            + ")"
        )
        exec(
            "self._own_type.tag_config('hpf',"
            + state.theme["python:function_names"].replace("type_", "self._own_type")
            + ")"
        )
        exec(
            "self._own_type.tag_config('hpx',"
            + state.theme["python:class_names"].replace("type_", "self._own_type")
            + ")"
        )
        exec(
            "self._own_type.tag_config('hpfa',"
            + state.theme["python:function_arguments"].replace(
                "type_", "self._own_type"
            )
            + ")"
        )
        exec(
            "self._own_type.tag_config('hpm',"
            + state.theme["python:module_names"].replace("type_", "self._own_type")
            + ")"
        )
        exec(
            "self._own_type.tag_config('hpo',"
            + state.theme["python:operators"].replace("type_", "self._own_type")
            + ")"
        )
        exec(
            "self._own_type.tag_config('hpd',"
            + state.theme["python:strings"].replace("type_", "self._own_type")
            + ")"
        )
        exec(
            "self._own_type.tag_config('hpc',"
            + state.theme["python:comments"].replace("type_", "self._own_type")
            + ")"
        )
        exec(
            "self._own_type.tag_config('hla',"
            + state.theme["latex:inlinemath"].replace("type_", "self._own_type")
            + ")"
        )
        exec(
            "self._own_type.tag_config('hlb',"
            + state.theme["latex:environment"].replace("type_", "self._own_type")
            + ")"
        )
        exec(
            "self._own_type.tag_config('hld',"
            + state.theme["latex:commands"].replace("type_", "self._own_type")
            + ")"
        )
        exec(
            "self._own_type.tag_config('hle',"
            + state.theme["latex:arguments"].replace("type_", "self._own_type")
            + ")"
        )
        exec(
            "self._own_type.tag_config('hlf',"
            + state.theme["latex:operators"].replace("type_", "self._own_type")
            + ")"
        )
        exec(
            "self._own_type.tag_config('hlg',"
            + state.theme["latex:square_brackets"].replace("type_", "self._own_type")
            + ")"
        )
        exec(
            "self._own_type.tag_config('hlh',"
            + state.theme["latex:comments"].replace("type_", "self._own_type")
            + ")"
        )
        exec(
            "self._own_type.tag_config('hstuff',"
            + state.theme["html:tags"].replace("type_", "self._own_type")
            + ")"
        )
        exec(
            "self._own_type.tag_config('hattr',"
            + state.theme["html:attributes"].replace("type_", "self._own_type")
            + ")"
        )
        exec(
            "self._own_type.tag_config('hstr',"
            + state.theme["html:quotes"].replace("type_", "self._own_type")
            + ")"
        )
        exec(
            "self._own_type.tag_config('hcmt',"
            + state.theme["html:comments"].replace("type_", "self._own_type")
            + ")"
        )
        exec(
            "self._own_type.tag_config('hmh1',"
            + state.theme["markdown:headers1"].replace("type_", "self._own_type")
            + ")"
        )
        exec(
            "self._own_type.tag_config('hmh2',"
            + state.theme["markdown:headers2"].replace("type_", "self._own_type")
            + ")"
        )
        exec(
            "self._own_type.tag_config('hmh3',"
            + state.theme["markdown:headers3"].replace("type_", "self._own_type")
            + ")"
        )
        exec(
            "self._own_type.tag_config('hmh4',"
            + state.theme["markdown:headers4"].replace("type_", "self._own_type")
            + ")"
        )
        exec(
            "self._own_type.tag_config('hmh5',"
            + state.theme["markdown:headers5"].replace("type_", "self._own_type")
            + ")"
        )
        exec(
            "self._own_type.tag_config('hmh6',"
            + state.theme["markdown:headers6"].replace("type_", "self._own_type")
            + ")"
        )
        exec(
            "self._own_type.tag_config('hmb',"
            + state.theme["markdown:bold"].replace("type_", "self._own_type")
            + ")"
        )
        exec(
            "self._own_type.tag_config('hmi',"
            + state.theme["markdown:italic"].replace("type_", "self._own_type")
            + ")"
        )
        exec(
            "self._own_type.tag_config('hmbi',"
            + state.theme["markdown:bold_italic"].replace("type_", "self._own_type")
            + ")"
        )
        exec(
            "self._own_type.tag_config('hms',"
            + state.theme["markdown:strike"].replace("type_", "self._own_type")
            + ")"
        )
        exec(
            "self._own_type.tag_config('hmc',"
            + state.theme["markdown:inlinecode"].replace("type_", "self._own_type")
            + ")"
        )
        exec(
            "self._own_type.tag_config('hml',"
            + state.theme["markdown:links"].replace("type_", "self._own_type")
            + ")"
        )
        exec(
            "self._own_type.tag_config('hmq',"
            + state.theme["markdown:blockquotes"].replace("type_", "self._own_type")
            + ")"
        )
        exec(
            "self._own_type.tag_config('hmf',"
            + state.theme["markdown:codeblocks"].replace("type_", "self._own_type")
            + ")"
        )
        exec(
            "self._own_type.tag_config('marked',"
            + state.theme["pynotes:marked"].replace("type_", "self._own_type")
            + ")"
        )
        exec(
            "self._own_type.tag_config('bracket_matched',"
            + state.theme["pynotes:bracket_matched"].replace("type_", "self._own_type")
            + ")"
        )
        exec(
            "self._own_type.tag_config('bracket_unmatched',"
            + state.theme["pynotes:bracket_unmatched"].replace(
                "type_", "self._own_type"
            )
            + ")"
        )

    def init_plugin_tags(self):
        """(Re-)create the tags for every plugin-defined HMode's
        (or PyCode `color` command's) fixed pattern-to-tag mapping from
        the current theme; skipped for entries that are instead a
        custom highlighting callable ("hl" a function), since those
        configure their own tags themselves.
        """
        for ft, entry in state.plugin_hl.items():
            mapping = None
            if isinstance(entry, dict):
                if "hl" not in entry:
                    mapping = entry
            elif not callable(entry):
                mapping = entry
            if mapping is None:
                continue
            for tag, (pat, theme_key) in mapping.items():
                try:
                    self._own_type.tag_delete(tag)
                    exec(
                        "self._own_type.tag_config('"
                        + tag
                        + "',"
                        + state.theme[theme_key].replace("type_", "self._own_type")
                        + ")"
                    )
                except Exception:
                    pass

    def selupdate(self):
        """Refresh the visual selection to span from the selection
        point (see setselpoint()) to the cursor.
        """
        if self.selectionpoint:
            self.type_.tag_remove("sel", "1.0", "end")
            if self.type_.compare(self.selectionpoint, "<=", "insert"):
                self.type_.tag_add("sel", self.selectionpoint, "insert")
            else:
                self.type_.tag_add("sel", "insert", self.selectionpoint)

    def bracket_match(self):
        """Highlight the bracket behind the cursor (else the one after
        it) together with its matching bracket, or only that bracket if
        it has no match.
        """
        text = self.type_
        text.tag_remove("bracket_matched", "1.0", "end")
        text.tag_remove("bracket_unmatched", "1.0", "end")
        for start in ("insert-1c", "insert"):
            bracket = text.get(start)
            if bracket in _BRACKET_MATCH_PAIRS:
                break
        else:
            return
        opener, closer, forward = _BRACKET_MATCH_PAIRS[bracket]
        pattern = _BRACKET_MATCH_PATTERNS[opener]
        start = text.index(start)
        line, col = (int(part) for part in start.split("."))
        last_line = int(text.index("end-1c").split(".")[0])
        depth = 0
        match = None
        if forward:
            chunk_start = f"{line}.{col}"
            while line <= last_line:
                end_line = min(line + _BRACKET_MATCH_CHUNK_LINES, last_line + 1)
                chunk_end = f"{end_line}.0" if end_line <= last_line else "end-1c"
                chunk = text.get(chunk_start, chunk_end)
                for found in pattern.finditer(chunk):
                    depth += 1 if found.group() == opener else -1
                    if depth == 0:
                        match = f"{chunk_start}+{found.start()}c"
                        break
                if match:
                    break
                line = end_line
                chunk_start = f"{line}.0"
        else:
            chunk_end = f"{start}+1c"
            while line >= 1:
                begin_line = max(line - _BRACKET_MATCH_CHUNK_LINES, 1)
                chunk_begin = f"{begin_line}.0"
                chunk = text.get(chunk_begin, chunk_end)
                for found in reversed(list(pattern.finditer(chunk))):
                    depth += 1 if found.group() == closer else -1
                    if depth == 0:
                        match = f"{chunk_begin}+{found.start()}c"
                        break
                if match:
                    break
                line = begin_line - 1
                chunk_end = chunk_begin
        if match:
            text.tag_add("bracket_matched", start, f"{start}+1c")
            text.tag_add("bracket_matched", match, f"{match}+1c")
        else:
            text.tag_add("bracket_unmatched", start, f"{start}+1c")

    def keypress(self):
        """Run after (essentially) every edit/keystroke: update the
        selection, highlight bracket matches, and debounced filesize/undo-mark/
        highlight/unsaved-state triggers, and refresh the file-info
        bar's filename/saved-state display.
        """
        if not self.winfo_exists():
            return
        self.selupdate()
        self.bracket_match()
        self._python_edit_generation[0] += 1
        # An edit made through one view never passes through the other
        # views' Tk commands, so their line numbers have to be told.
        for member in self._group_members():
            member._own_type._schedule_line_numbers()
        self.trigger_filesize()
        self.trigger_undo_set()
        if self.hmode == "python":
            self.python_trigger_name_scan()
        else:
            self.trigger_ha(self.hmode)
        self._sync_wanttitle()
        if self.title:
            if self.hmode in ["png", "pdf", "epub"]:
                self.fileinfoconfig(
                    filename=os.path.basename(self.title),
                    filesaved="Read Only File",
                )
            else:
                self.fileinfoconfig(filename=os.path.basename(self.title))
        else:
            if state.active in self._group_members() and not state.pcsettitle:
                self.fileinfoconfig(filename="Untitled", filesaved="Untitled File")
            else:
                self.fileinfoconfig(filename="Untitled")
        self.trigger_unsaved()
        if not self.title:
            if self.type_.get("1.0", "end-1c"):
                self.unsaved = True
            else:
                self.unsaved = False

    def sethmenu(self, mode):
        """Show the HMode-specific menu (Python or LaTeX) matching
        mode, removing whichever one was there before.
        """
        try:
            self.m.delete("Python")
        except Exception:
            pass
        try:
            self.m.delete("LaTeX")
        except Exception:
            pass
        if mode == "python":
            self.m.insert_cascade(
                self.m.index("Options") + 1, label="Python", menu=state.pm
            )
        elif mode == "latex":
            self.m.insert_cascade(
                self.m.index("Options") + 1, label="LaTeX", menu=state.lm
            )
        window.update_menus()

    def pchmode(self, mode):
        """PyCode's/Alt-X's `hmode` command: switch this editor's
        HMode (python/latex/normal/html/markdown, or a plugin-provided
        one), updating its menu, LaTeX toolbar visibility, and
        file-type label, and re-highlighting. No-op for the read-only
        png/pdf/epub HModes.
        """
        if self.view_master:
            return self.view_master.pchmode(mode)
        if self.hmode in ["png", "pdf", "epub"]:
            return
        pycode.pcrunhook("before", "change-hmode", mode)
        [
            self.type_.tag_remove(tag, "1.0", "end")
            for tag in self.type_.tag_names()
            if tag not in state._EDITOR_HL_SKIP_REMOVE_TAGS
        ]
        if mode == "python" or mode == "py":
            self.sethmenu("python")
            self.lfouter.pack_forget()
            self.hmode = "python"
            self.fileinfoconfig(filetype="Python File (*.py)")
            self.python_trigger_name_scan()
        elif mode == "latex" or mode == "la":
            self.sethmenu("latex")
            self.lfouter.pack(
                padx=10, pady=10, side="top", fill="x", before=self.fileinfo
            )
            self.hmode = "latex"
            self.fileinfoconfig(filetype="LaTeX / TeX File (*.tex)")
        elif mode == "normal" or mode == "norm":
            self.sethmenu(None)
            self.lfouter.pack_forget()
            self.hmode = "normal"
            self.fileinfoconfig(filetype="Plain Text (*.*)")
        elif mode == "html":
            self.sethmenu(None)
            self.hmode = "html"
            self.fileinfoconfig(filetype="HTML File (*.html)")
            self.lfouter.pack_forget()
        elif mode == "markdown" or mode == "md":
            self.sethmenu(None)
            self.lfouter.pack_forget()
            self.hmode = "markdown"
            self.fileinfoconfig(filetype="Markdown File (*.md)")
        elif mode in state.plgnhmodes:
            try:
                self.hmode = mode
                exec(state.plgnhmodes[mode][1], vars(state))
            except Exception as error:
                error = str(error)
                state.root.error(
                    "Error!",
                    f'There was an error in switching to the HMode {mode} from the plugin "{os.path.basename(os.path.normpath(state.plgnhmodes[mode][0]))}":\n{error}',
                )
        utils.show(f"{self.hmode} hmode")
        self.keypress()
        self._sync_group_chrome()
        pycode.pcrunhook("after", "change-hmode", mode)

    def rp(self):
        """Run this editor's Python code (F5, Python HMode): save it
        (to a temp file if untitled, otherwise saving/using its own
        file) and run it with state.pythonexecutable in a terminal.
        """
        if not self.title:
            f = open(
                f"{homedir}/.local/share/PyNotes/tempcode",
                "w",
                encoding="utf-8",
            )
            f.write(self.type_.get("1.0", "end-1c"))
            f.close()
            file = f"{homedir}/.local/share/PyNotes/tempcode"
        else:
            file = self.title
            self.sv(file)
        terminal.term(
            [state.pythonexecutable, file],
            title=f"*{file} Running*",
            endmessage="--- Python code finished, press any key to continue ---",
        )

    def hp(self):
        """Run this editor's HTML code (F5, HTML HMode): save it (to a
        temp file if untitled, otherwise saving its own file) and open
        it with the system's default handler for it (a browser).
        """
        if not self.title:
            f = open(
                f"{homedir}/.local/share/PyNotes/tempcode",
                "w",
                encoding="utf-8",
            )
            f.write(self.type_.get("1.0", "end-1c"))
            f.close()
            file = f"{homedir}/.local/share/PyNotes/tempcode"
        else:
            file = self.title
            self.sv(file)
        if platform.system() == "Linux":
            subprocess.run(["xdg-open", file], cwd=os.path.dirname(file))
        else:
            subprocess.run(["start", file], cwd=os.path.dirname(file))

    def runtex(self, compiler):
        """Compile this editor's LaTeX code with compiler ("lua" or
        "pdf", i.e. lualatex/pdflatex) and open the resulting PDF (see
        dialogs.pdf()), or offer to show the compile log if it failed.
        """
        if not self.title:
            f = open(
                f"{homedir}/.local/share/PyNotes/tempcode",
                "w",
                encoding="utf-8",
            )
            f.write(self.type_.get("1.0", "end-1c"))
            f.close()
            file = f"{homedir}/.local/share/PyNotes/tempcode"
        else:
            file = self.title
            self.sv(file)
        compiler += "latex"
        if not shutil.which(compiler):
            state.root.error(
                "Error", f"Error in running LaTeX - {compiler} is not installed"
            )
            return
        if os.path.splitext(file)[1] == ".tex":
            pdf_ = os.path.splitext(file)[0]
        else:
            pdf_ = file
        pdf_ += ".pdf"
        try:
            os.remove(pdf_)
        except Exception:
            pass
        terminal.term(
            [compiler, file, f"--output-directory={os.path.dirname(file)}"],
            title=f"*{file} Compiling*",
            endmessage="--- LaTeX compiling finished, press any key to continue ---",
            blocking=True,
        )
        dialogs.pdf(file)

    def f5(self):
        """PyCode's/Alt-X's `runcode` command (F5): run this editor's
        code with whichever runner matches its HMode (rp() for Python,
        runtex() for LaTeX, hp() for HTML).
        """
        if self._file_watch_prompt_pending:
            utils.show(
                "select 'Discard Changes & Reload' or 'Ignore' external changes before loading another file"
            )
            return
        pycode.pcrunhook("before", "run-code")
        if self.hmode == "python":
            self.rp()
        elif self.hmode == "latex":
            self.runtex("lua")
        elif self.hmode == "html":
            self.hp()
        else:
            utils.show("hmode not in python / latex / html")
            return
        utils.show(f"run {self.hmode} code")
        pycode.pcrunhook("after", "run-code")

    def tab(self):
        """<Tab> handler for all HModes; indent one level with tabs
        or spaces depending on the user's preferences if on start
        of stripped line. Otherwise, insert a literal tab. If there is
        a selection, indent the selected lines instead.
        """
        if self.type_.tag_ranges("sel"):
            pycode.pcindentselection()
            return
        il = self.type_.index("insert").split(".")[0]
        onstart = not self.type_.get(il + ".0", "insert").strip()
        if not onstart or not state.taborspace:
            indent = "	"
        else:
            indent = "    "
        self._set_undo_mark()
        self.type_.insert(f"insert", indent)
        self._set_undo_mark()

    def _indent_chars_before_cursor(self):
        """How many characters back the previous indent stop is (a tab,
        or the spaces back to the previous multiple of 4 columns), or 0
        if anything but whitespace is before the cursor on its line.
        """
        before = self.type_.get("insert linestart", "insert")
        if not before or before.strip():
            return 0
        trailing_spaces = len(before) - len(before.rstrip(" "))
        if not trailing_spaces:
            return 1
        column = len(before.expandtabs(8))
        return min(trailing_spaces, column % 4 or 4)

    def _indent_chars_after_cursor(self):
        """How many characters forward the next indent stop is, or 0 if
        anything but whitespace is before the cursor on its line or a
        non-whitespace character follows it.
        """
        before = self.type_.get("insert linestart", "insert")
        after = self.type_.get("insert", "insert lineend")
        if before.strip() or not after or after[0] not in " \t":
            return 0
        if after[0] == "\t":
            return 1
        spaces = len(after) - len(after.lstrip(" "))
        column = len(before.expandtabs(8))
        return min(spaces, 4 - column % 4)

    def _collapse_selection(self, edge):
        """If a selection exists without a selection point, move the
        cursor to its sel.first/sel.last `edge`, close the selection
        and return True; otherwise return False.
        """
        if self.selectionpoint or not self.type_.tag_ranges("sel"):
            return False
        self.type_.mark_set("insert", f"sel.{edge}")
        self.type_.tag_remove("sel", "1.0", "end")
        self.type_.see("insert")
        return True

    def left(self):
        """<Left> handler for all HModes: with a selection (and no
        selection point), jump to its start and close it. Otherwise,
        if only whitespace is before the cursor, move back one
        indentation level (see backspace()); otherwise move back one
        character. A selection point extends the selection instead.
        """
        if self._collapse_selection("first"):
            return "break"
        if self.selectionpoint:
            self.type_.after_idle(self.selupdate)
        move = self._indent_chars_before_cursor()
        if move:
            self.type_.mark_set("insert", f"insert-{move}c")
        else:
            self.type_.mark_set("insert", "insert-1displayindices")
        self.type_.see("insert")
        return "break"

    def right(self):
        """<Right> handler for all HModes, the opposite of left():
        with a selection (and no selection point), jump to its end and
        close it. Otherwise, if only whitespace is before the cursor
        and whitespace follows it, move forward one indentation level;
        otherwise move forward one character. A selection point
        extends the selection instead.
        """
        if self._collapse_selection("last"):
            return "break"
        if self.selectionpoint:
            self.type_.after_idle(self.selupdate)
        move = self._indent_chars_after_cursor()
        if move:
            self.type_.mark_set("insert", f"insert+{move}c")
        else:
            self.type_.mark_set("insert", "insert+1displayindices")
        self.type_.see("insert")
        return "break"

    def _word_boundary(self, forward):
        """The index of the word boundary before (or after, if
        forward) the cursor: past any whitespace, then past one run of
        word characters or of punctuation. At a line edge, the
        boundary is the end of the previous line / start of the next.
        """
        if forward:
            rest = self.type_.get("insert", "insert lineend")
            if not rest:
                return self.type_.index("insert+1c")
            rest_stripped = rest.lstrip()
            run = re.match(r"\w+|[^\w\s]+", rest_stripped)
            consumed = len(rest) - len(rest_stripped) + (run.end() if run else 0)
            return self.type_.index(f"insert+{consumed}c")
        before = self.type_.get("insert linestart", "insert")
        if not before:
            return self.type_.index("insert-1c")
        before_stripped = before.rstrip()
        run = re.search(r"\w+$|[^\w\s]+$", before_stripped)
        kept = run.start() if run else len(before_stripped)
        return self.type_.index(f"insert-{len(before) - kept}c")

    def word_left(self):
        """<Control-Left> handler: move back one word (extending the
        selection if a selection point is set).
        """
        if self.selectionpoint:
            self.type_.after_idle(self.selupdate)
        else:
            self.type_.tag_remove("sel", "1.0", "end")
        self.type_.mark_set("insert", self._word_boundary(False))
        self.type_.see("insert")
        return "break"

    def word_right(self):
        """<Control-Right> handler, the opposite of word_left()."""
        if self.selectionpoint:
            self.type_.after_idle(self.selupdate)
        else:
            self.type_.tag_remove("sel", "1.0", "end")
        self.type_.mark_set("insert", self._word_boundary(True))
        self.type_.see("insert")
        return "break"

    def _extend_selection_to(self, index):
        """Move the cursor to `index`, extending the selection from
        its far end (or from where the cursor was, if there is no
        selection), like a normal editor's Shift-arrow.
        """
        text = self.type_
        if self.selectionpoint:
            anchor = None
        elif text.tag_ranges("sel"):
            first, last = text.index("sel.first"), text.index("sel.last")
            anchor = last if text.compare("insert", "==", first) else first
        else:
            anchor = text.index("insert")
        text.mark_set("insert", index)
        if anchor is None:
            self.selupdate()
        else:
            text.tag_remove("sel", "1.0", "end")
            if text.compare(anchor, "<=", "insert"):
                text.tag_add("sel", anchor, "insert")
            else:
                text.tag_add("sel", "insert", anchor)
        text.see("insert")
        return "break"

    def select_left(self):
        """<Shift-Left> handler: extend the selection one character back."""
        return self._extend_selection_to("insert-1displayindices")

    def select_right(self):
        """<Shift-Right> handler: extend the selection one character forward."""
        return self._extend_selection_to("insert+1displayindices")

    def select_word_left(self):
        """<Control-Shift-Left> handler: extend the selection one word back."""
        return self._extend_selection_to(self._word_boundary(False))

    def select_word_right(self):
        """<Control-Shift-Right> handler: extend the selection one word forward."""
        return self._extend_selection_to(self._word_boundary(True))

    def delete_word_forward(self):
        """<Control-Delete> handler: delete the selection if the cursor
        is in it; otherwise delete to the next word boundary.
        """
        return self._delete_word(True)

    def delete_word_back(self):
        """<Control-BackSpace> handler: delete the selection if the
        cursor is in it; otherwise delete back to the previous word
        boundary.
        """
        return self._delete_word(False)

    def _delete_word(self, forward):
        if self.selectionpoint:
            self.removeselpoint()
        self._set_undo_mark()
        if (
            self.type_.tag_ranges("sel")
            and self.type_.compare("sel.first", "<=", "insert")
            and self.type_.compare("insert", "<=", "sel.last")
        ):
            self.type_.delete("sel.first", "sel.last")
        elif forward:
            self.type_.delete("insert", self._word_boundary(True))
        else:
            self.type_.delete(self._word_boundary(False), "insert")
        self._set_undo_mark()
        self.type_.see("insert")
        return "break"

    def delete_key(self):
        """<Delete> handler for all HModes, the forward version of
        backspace(): delete the selection if the cursor is in it;
        otherwise, if only whitespace is before the cursor and
        whitespace follows it, delete forward to the next indentation
        level; otherwise delete the next character.
        """
        if self.selectionpoint:
            self.removeselpoint()
        if (
            self.type_.tag_ranges("sel")
            and self.type_.compare("sel.first", "<=", "insert")
            and self.type_.compare("insert", "<=", "sel.last")
        ):
            self._set_undo_mark()
            self.type_.delete("sel.first", "sel.last")
            self._set_undo_mark()
            return "break"
        remove = self._indent_chars_after_cursor()
        if remove:
            self._set_undo_mark()
            self.type_.delete("insert", f"insert+{remove}c")
            self._set_undo_mark()
        else:
            self.type_.delete("insert")
        self.type_.see("insert")
        return "break"

    def backspace(self):
        """<BackSpace> handler for all HModes, the opposite of tab():
        delete the selection if the cursor is in it; otherwise, if only
        whitespace is before the cursor, delete one indentation level
        (a tab, or the spaces back to the previous multiple of 4
        columns); otherwise delete the previous character.
        """
        if (
            self.type_.tag_ranges("sel")
            and self.type_.compare("sel.first", "<=", "insert")
            and self.type_.compare("insert", "<=", "sel.last")
        ):
            self._set_undo_mark()
            self.type_.delete("sel.first", "sel.last")
            self._set_undo_mark()
            return "break"
        remove = self._indent_chars_before_cursor()
        if remove:
            self._set_undo_mark()
            self.type_.delete(f"insert-{remove}c", "insert")
            self._set_undo_mark()
        elif self.type_.compare("insert", ">", "1.0"):
            self.type_.delete("insert-1c", "insert")
        self.type_.see("insert")
        return "break"

    def indent(self):
        """<Return> handler for Python HMode: insert a newline and
        auto-indent the new line to match the previous one, adding one
        more indent level if the previous line (ignoring string/
        comment content) ends with ':'.
        """
        self._set_undo_mark()
        if not self.hmode == "python":
            return
        l = int(self.type_.index("insert").split(".")[0])
        self.type_.insert(f"insert", "\n")
        line = self.type_.get(f"{l}.0", f"{l}.end")
        whitespace = re.match(r"\s*", line).group()
        self.type_.insert(f"{l + 1}.0", whitespace)
        line = re.sub(
            r'\'[^\'\\]*(?:\\.[^\'\\]*)*\'|"[^"\\]*(?:\\.[^"\\]*)*"', "", line
        )
        line = re.sub(r"#.*", "", line).strip()
        if state.taborspace:
            indentthing = "    "
        else:
            indentthing = "	"
        if not line:
            return "break"
        if line[-1] == ":":
            self.type_.insert(f"{l + 1}.0", indentthing)
        self._set_undo_mark()
        return "break"

    def gl(self, l=None):
        """PyCode's/Alt-X's `gotoline` command: jump to and select line
        l (prompting for it if not given).
        """
        if l is None:
            l = utils.prompt("Go to line: ")
        if type(l) == str:
            l = l.strip()
        if not l:
            return
        try:
            l = int(l)
        except Exception:
            utils.show(f"cannot go to line number '{l}'")
            return
        else:
            utils.show(f"go to line no. {l}")
            self.type_.see(f"{l}.0")
            self.type_.mark_set("insert", f"{l}.0")
            self.type_.tag_add("sel", f"{l}.0", f"{l}.end")

    def selall(self):
        """PyCode's/Alt-X's `selall` command."""
        utils.show("select all text")
        self.type_.tag_add("sel", "1.0", "end")
        return "break"

    def cp(self):
        """PyCode's/Alt-X's `copy` command."""
        try:
            select = self.type_.get("sel.first", "sel.last")
        except Exception:
            utils.show("no text is selected")
            return
        else:
            pycode.pcrunhook("before", "copy-text", select)
            utils.show("copy text")
        state.root.clipboard_clear()
        state.root.clipboard_append(select)
        pycode.pcrunhook("after", "copy-text", select)

    def cut(self):
        """PyCode's/Alt-X's `cut` command."""
        try:
            select = self.type_.get("sel.first", "sel.last")
        except Exception:
            utils.show("no text is selected")
            return
        else:
            pycode.pcrunhook("before", "cut-text", select)
            utils.show("cut text")
        self._set_undo_mark()
        self.type_.delete("sel.first", "sel.last")
        state.root.clipboard_clear()
        state.root.clipboard_append(select)
        self._set_undo_mark()
        utils.show("cut text")
        pycode.pcrunhook("after", "cut-text", select)

    def spk(self):
        """PyCode's/Alt-X's `speaktext` command: speak the selected
        text aloud on a background thread.
        """
        try:
            select = self.type_.get("sel.first", "sel.last")
        except Exception:
            utils.show("no text is selected")
            return
        else:
            utils.show("speak selected text")
            speakthread = threading.Thread(
                target=speech.actualspk, args=(select,), daemon=True
            )
            speakthread.start()

    def pst(self):
        """PyCode's/Alt-X's `paste` command."""
        try:
            text = state.root.clipboard_get()
        except Exception:
            utils.show("no text is on clipboard")
            return
        else:
            pycode.pcrunhook("before", "paste-text", text)
            utils.show("paste text")
        self._set_undo_mark()
        self.type_.insert("insert", text)
        self._set_undo_mark()
        pycode.pcrunhook("after", "paste-text", text)
        return "break"

    def ptb(self):
        """PyCode's/Alt-X's `pageback` command."""
        if self.type_.yview()[0] == 0.0:
            utils.show("already at beginning")
            return
        pycode.pcrunhook("before", "previous-page")
        self.type_.yview_scroll(-1, "pages")
        utils.show("go to previous page")
        pycode.pcrunhook("after", "previous-page")

    def ptf(self):
        """PyCode's/Alt-X's `pageforw` command."""
        if self.type_.yview()[1] == 1.0:
            utils.show("already at end")
            return
        pycode.pcrunhook("before", "next-page")
        self.type_.yview_scroll(1, "pages")
        utils.show("go to next page")
        pycode.pcrunhook("after", "next-page")

    def undo(self):
        """PyCode's/Alt-X's `undo` command."""
        pycode.pcrunhook("before", "undo")
        try:
            self.type_.edit_undo()
            utils.show("undoed edit")
            pycode.pcrunhook("after", "undo")
        except Exception:
            utils.show("nothing to undo")

    def redo(self):
        """PyCode's/Alt-X's `redo` command."""
        pycode.pcrunhook("before", "redo")
        try:
            self.type_.edit_redo()
            utils.show("redoed edit")
            pycode.pcrunhook("after", "redo")
        except Exception:
            utils.show("nothing to redo")

    def _main_poll(self):
        """Every 10ms, run every callback queued on self._main_queue -
        the way background threads (the file watcher, find/replace's
        and highlighting's search threads) hand results back to the GUI
        thread, since they can't touch widgets directly.
        """
        if not self.winfo_exists():
            return
        try:
            while True:
                task = self._main_queue.get_nowait()
                task()
        except Exception:
            pass
        self._main_poll_after_id = self._own_type.after(10, self._main_poll)

    def type_setview(self):
        """Every 10ms, check whether the visible region has changed
        (scrolling) and, if so, trigger a re-highlight of the new
        region (see ha()).
        """
        if not self.winfo_exists():
            return
        new_region = self.type_getvisible()
        if new_region != self._prev_visible_region:
            self._prev_visible_region = new_region
            self.type_top, self.type_bottom = new_region
            self.trigger_ha(self.hmode)
        else:
            self.type_top, self.type_bottom = new_region
        self._type_setview_after_id = self.mf.after(10, self.type_setview)

    def do_backup(self):
        """Every 10 seconds, write a ".<name>backpynotes<ext>" backup
        of the current content next to the file, if backups are
        enabled (state.bfr, see preferences), the file has a title,
        and it isn't a read-only png/pdf/epub HMode.
        """
        if not self.winfo_exists():
            return
        if all((self.hmode not in ["png", "pdf", "epub"], state.bfr, self.title)):
            open(
                os.path.join(
                    os.path.dirname(os.path.splitext(self.title)[0]),
                    "."
                    + os.path.basename(os.path.splitext(self.title)[0])
                    + "backpynotes"
                    + os.path.splitext(self.title)[1],
                ),
                "w+",
                encoding="utf-8",
            ).write(self.type_.get("1.0", "end"))
            utils.show("saved backup")
        self._do_backup_after_id = self.mf.after(10000, self.do_backup)

    # The LaTeX toolbar button handlers below each wrap the current
    # selection in the matching LaTeX markup (no-op if nothing is
    # selected, except where noted).
    def boldlatex(self):
        try:
            select = self.type_.get("sel.first", "sel.last")
        except Exception:
            return
        self._set_undo_mark()
        self.type_.delete("sel.first", "sel.last")
        self.type_.insert("insert", "{\\bf " + select + "}")
        self._set_undo_mark()
        utils.show("bold text latex")
        self.keypress()

    def italiclatex(self):
        try:
            select = self.type_.get("sel.first", "sel.last")
        except Exception:
            return
        self._set_undo_mark()
        self.type_.delete("sel.first", "sel.last")
        self.type_.insert("insert", "\\textit{" + select + "}")
        self._set_undo_mark()
        utils.show("italic text latex")
        self.keypress()

    def underlinelatex(self):
        try:
            select = self.type_.get("sel.first", "sel.last")
        except Exception:
            return
        self._set_undo_mark()
        self.type_.delete("sel.first", "sel.last")
        self.type_.insert("insert", "\\underline{" + select + "}")
        self._set_undo_mark()
        utils.show("underline text latex")
        self.keypress()

    def subscriptlatex(self):
        try:
            select = self.type_.get("sel.first", "sel.last")
        except Exception:
            return
        self._set_undo_mark()
        self.type_.delete("sel.first", "sel.last")
        self.type_.insert("insert", "_{" + select + "}")
        self._set_undo_mark()
        utils.show("subscript text latex")
        self.keypress()

    def superscriptlatex(self):
        try:
            select = self.type_.get("sel.first", "sel.last")
        except Exception:
            return
        self._set_undo_mark()
        self.type_.delete("sel.first", "sel.last")
        self.type_.insert("insert", "^{" + select + "}")
        self._set_undo_mark()
        utils.show("superscript text latex")
        self.keypress()

    def numberlistlatex(self):
        """Wrap the selection as an enumerate (numbered) list, one
        \\item per line; if the selection is already a whole such list,
        unwrap it back to plain lines instead. Inserts an empty list if
        nothing is selected.
        """
        self._set_undo_mark()
        try:
            select = self.type_.get("sel.first", "sel.last")
        except Exception:
            self.type_.insert("insert", "\n\\begin{enumerate}\n\n\\end{enumerate}\n")
        else:
            tryfind = re.findall(
                r"\\begin{enumerate}.+\\end{enumerate}", select, re.DOTALL
            )
            if not tryfind:
                select = "\\item " + select.replace("\n", "\n\\item ").replace(
                    "\\item \\item ", "\\item "
                )
                self.type_.delete("sel.first", "sel.last")
                self.type_.insert(
                    "insert", "\n\\begin{enumerate}\n" + select + "\n\\end{enumerate}\n"
                )
            else:
                keeptext = tryfind[0][len("\\begin{enumerate}") :][
                    : -len("\\end{enumerate}")
                ].replace("\\item ", "")
                self.type_.delete("sel.first", "sel.last")
                self.type_.insert("insert", keeptext)
        self._set_undo_mark()
        utils.show("numbered list latex")
        self.keypress()

    def bulletlistlatex(self):
        """Same as numberlistlatex(), but an itemize (bulleted) list."""
        self._set_undo_mark()
        try:
            select = self.type_.get("sel.first", "sel.last")
        except Exception:
            self.type_.insert("insert", "\n\\begin{itemize}\n\n\\end{itemize}\n")
        else:
            tryfind = re.findall(r"\\begin{itemize}.+\\end{itemize}", select, re.DOTALL)
            if not tryfind:
                select = "\\item " + select.replace("\n", "\n\\item ").replace(
                    "\\item \\item ", "\\item "
                )
                self.type_.delete("sel.first", "sel.last")
                self.type_.insert(
                    "insert", "\n\\begin{itemize}\n" + select + "\n\\end{itemize}\n"
                )
            else:
                keeptext = tryfind[0][len("\\begin{itemize}") :][
                    : -len("\\end{itemize}")
                ].replace("\\item ", "")
                self.type_.delete("sel.first", "sel.last")
                self.type_.insert("insert", keeptext)
        self._set_undo_mark()
        utils.show("bulleted list latex")
        self.keypress()

    def paragraphlatex(self):
        """Insert a \\par (new paragraph)."""
        self._set_undo_mark()
        self.type_.insert("insert", "\\par\n")
        utils.show("new paragraph latex")
        self.keypress()

    def equationlatex(self):
        """Wrap the selection as an equation/split environment (each
        line ended with '\\\\' for a line break); if the selection is
        already a whole such environment, unwrap it back to plain lines
        instead. Inserts an empty equation if nothing is selected.
        """
        self._set_undo_mark()
        try:
            select = self.type_.get("sel.first", "sel.last")
        except Exception:
            self.type_.insert(
                "insert",
                "\n\\begin{equation}\n\\begin{split}\n\n\\end{split}\n\\end{equation}\n",
            )
        else:
            tryfind = re.findall(
                r"\\begin{equation}.+\\end{equation}", select, re.DOTALL
            )
            if not tryfind:
                select = select.replace("\n", "\\\\\n").replace("\\\\\\\\", "\\\\")
                self.type_.delete("sel.first", "sel.last")
                self.type_.insert(
                    "insert", "\n\\begin{equation}\n" + select + "\n\\end{equation}\n"
                )
            else:
                keeptext = tryfind[0][len("\\begin{equation}") :][
                    : -len("\\end{equation}")
                ].replace("\\", "")
                self.type_.delete("sel.first", "sel.last")
                self.type_.insert("insert", keeptext)
        self._set_undo_mark()
        utils.show("equation latex")
        self.keypress()

    def sectionlatex(self, typeofsection):
        """Insert a '\\{typeofsection}{Section}' heading command (e.g.
        typeofsection "section"/"subsection"/"subsubsection", matching
        the LaTeX toolbar's Section dropdown), with the placeholder
        title text "Section" left for the user to edit.
        """
        self._set_undo_mark()
        typeofsection = typeofsection.lower()
        secname = "Section"
        if secname:
            self.type_.insert("insert", f"\n\\{typeofsection}" + "{" + secname + "}\n")
        self._set_undo_mark()
        utils.show(f"new {typeofsection} latex")
        self.keypress()

    def mathlatex(self, whichchar):
        """Insert the LaTeX code for the math symbol/construct named
        whichchar (matching the LaTeX toolbar's math-symbol dropdown,
        e.g. "Multiplication" -> '\\times').
        """
        self._set_undo_mark()
        original = [
            "Multiplication",
            "Division",
            "Less or equal",
            "More or equal",
            "Not equal",
            "Infinity",
            "Summation",
            "Integral",
            "Pi",
            "Theta",
            "Alpha Lower",
            "Alpha Upper",
            "Inline Math",
        ]
        replaces = [
            "\\times",
            "\\div",
            "\\leq",
            "\\meq",
            "\\neq",
            "\\infty",
            "\\sum",
            "\\int",
            "\\pi",
            "\\theta",
            "\\alpha",
            "\\Alpha",
            "$$",
        ]
        whichchar = replaces[original.index(whichchar)]
        self.type_.insert("insert", whichchar)
        self._set_undo_mark()
        utils.show("insert math latex")
        self.keypress()


def _promote_new_master(old_master):
    """Promote one of old_master's peer views to take over as the new
    master for the rest, carrying over old_master's shared state
    (everything except _PER_PANE_ATTRS/_TK_INTERNAL_ATTRS) and its menu.
    Called when old_master is about to stop being usable as a master
    (see Editor._disconnect()/_detach_before_close()) but its peers
    need to keep sharing state with each other.
    """
    children = list(old_master.view_children)
    if not children:
        return
    new_master, rest = children[0], children[1:]
    carried_values = dict(
        (name, value)
        for name, value in old_master.__dict__.items()
        if name not in Editor._PER_PANE_ATTRS and name not in Editor._TK_INTERNAL_ATTRS
    )
    new_master.view_master = None
    for name, value in carried_values.items():
        setattr(new_master, name, value)
    new_master._file_watch_prompt_pending = False
    new_master.view_children = rest
    for child in rest:
        child.view_master = new_master
    new_master.m = ctk.Menu(state.root)
    for label, menu in state.all_editor_menus.items():
        new_master.m.add_cascade(label=label, menu=menu)
    for child in rest:
        child.m = new_master.m
    if new_master.hmode == "python":
        new_master.sethmenu("python")
    elif new_master.hmode == "latex":
        new_master.sethmenu("latex")
    if new_master.title:
        new_master.clt(new_master.title)
    return new_master


_BRACKET_MATCH_PAIRS = {
    "(": ("(", ")", True),
    "[": ("[", "]", True),
    "{": ("{", "}", True),
    ")": ("(", ")", False),
    "]": ("[", "]", False),
    "}": ("{", "}", False),
}
_BRACKET_MATCH_PATTERNS = {
    opener: re.compile("[" + re.escape(opener + closer) + "]")
    for opener, closer in (("(", ")"), ("[", "]"), ("{", "}"))
}
_BRACKET_MATCH_CHUNK_LINES = 200


def _init_hl_tags():
    """Reconfigure every open Editor's built-in highlight tags (after a
    theme change).
    """
    for buffer in state.all_buffers:
        if isinstance(buffer, Editor):
            buffer.init_hl_tags()


def _init_plugin_tags():
    """Reconfigure every open Editor's plugin-defined highlight tags
    (after a theme change).
    """
    for buffer in state.all_buffers:
        if isinstance(buffer, Editor):
            buffer.init_plugin_tags()


def _find_closing_brace(text, start):
    """The index just past the '}' in text that matches the '{' at
    start (honoring nesting and backslash-escaped characters), or
    len(text) if unmatched. Used by the LaTeX highlighter.
    """
    depth = 1
    i = start + 1
    while i < len(text) and depth > 0:
        if text[i] == "\\" and i + 1 < len(text):
            i += 2
            continue
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
        i += 1
    return i if depth == 0 else len(text)


def _find_closing_bracket(text, start):
    """Same as _find_closing_brace() but for '['/']'. Used by the
    LaTeX highlighter (e.g. optional-argument brackets).
    """
    depth = 1
    i = start + 1
    while i < len(text) and depth > 0:
        if text[i] == "\\" and i + 1 < len(text):
            i += 2
            continue
        if text[i] == "[":
            depth += 1
        elif text[i] == "]":
            depth -= 1
        i += 1
    return i if depth == 0 else len(text)


def _find_closing_tag(text, start):
    """The index just past the '>' that closes the tag opening at
    start, skipping any '>' found inside a quoted attribute value. Used
    by the HTML and Markdown highlighters.
    """
    i = start + 1
    in_quote = None
    while i < len(text):
        if text[i] == "\\" and i + 1 < len(text) and in_quote:
            i += 2
            continue
        if in_quote:
            if text[i] == in_quote:
                in_quote = None
        else:
            if text[i] in ('"', "'"):
                in_quote = text[i]
            elif text[i] == ">":
                return i + 1
        i += 1
    return len(text)


# Precompiled patterns used by ha()'s LaTeX/HTML/Markdown highlighting:
# _LH_PAT = LaTeX line comments; _LATEX_MATH_PAT = LaTeX inline/display
# math; _HC_PAT = HTML comments; _HTML_ATTR_PAT/_HTML_BOOL_ATTR_PAT =
# HTML attributes (name=value, and bare boolean attributes); _MDH/_MDBI/
# _MDB/_MDI/_MDS/_MDC/_MDL/_MDQ_PAT = Markdown headers, bold+italic,
# bold, italic, strikethrough, inline code, links, and blockquotes.
_LH_PAT = re.compile(r"(?<!\\)%[^\n]*(?:\n|$)")
_LATEX_MATH_PAT = re.compile(
    r"\$\$[\s\S]*?\$\$|\\\[[\s\S]*?\\\]|\\\([\s\S]*?\\\)|\$(?!\$)(?:[^$\\]|\\.)*?\$(?!\$)"
)
_HC_PAT = re.compile(r"<!--.*?-->", re.DOTALL)
_HTML_ATTR_PAT = re.compile(
    r'\s([\w:-]+)\s*=\s*("(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\'|[^\s"\'=<>]+)',
    re.IGNORECASE,
)
_HTML_BOOL_ATTR_PAT = re.compile(
    r"\b(?:async|autofocus|autoplay|checked|controls|default|defer|disabled|formnovalidate|hidden|ismap|loop|multiple|muted|nomodule|novalidate|open|readonly|required|reversed|selected)\b",
    re.IGNORECASE,
)
_MDH_PAT = re.compile(r"(?m)^(#{1,6})(?:[ \t].*)?$")
_MDBI_PAT = re.compile(
    r"(?<!\\)\*\*\*(?:\\.|[^*\n])+?\*\*\*|(?<!\\)___(?:\\.|[^_\n])+?___|(?<!\\)\*\*_(?:\\.|[^_\n])+?_\*\*|(?<!\\)__\*(?:\\.|[^*\n])+?\*__|(?<!\\)\*__(?:\\.|[^_\n])+?__\*|(?<!\\)_\*\*(?:\\.|[^*\n])+?\*\*_"
)
_MDB_PAT = re.compile(r"(?<!\\)\*\*(?:\\.|[^*\n])+?\*\*|(?<!\\)__(?:\\.|[^_\n])+?__")
_MDI_PAT = re.compile(
    r"(?<!\\)(?<!\*)\*(?:\\.|[^*\n])+?\*(?!\*)|(?<!\\)(?<!_)_(?:\\.|[^_\n])+?_(?!_)"
)
_MDS_PAT = re.compile(r"(?<!\\)~~(?:\\.|[^~\n])+?~~")
_MDC_PAT = re.compile(r"(?<!\\)`(?:\\.|[^`\n])+?`")
_MDL_PAT = re.compile(r"(?<!\\)\[(?:\\.|[^\]\n])*\]\((?:\\.|[^)\n])*\)")
_MDQ_PAT = re.compile(r"(?m)^>.*$")
# The HTML highlight tags Markdown's highlighter also applies for any
# raw HTML embedded in a Markdown file.
_MD_HTML_TAGS = ("hstuff", "hattr", "hstr", "hcmt")
