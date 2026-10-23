"""The main PyNotes window, its dialogs, and buffer/window management
(switching, splitting, balancing, resizing, closing PyNotes).
"""

import os
import sys
import shutil
import queue
import threading
import tkinter.font as tkfont
import canvastk as ctk
import themes
import state
from init import homedir, DEBOUNCE_TIME
import buffer
import editor
import dialogs
import pycode
import utils
import importlib.util

_ASK_PRESETS = {
    ("yes", "no"): {"Yes": True, "No": False, None: None},
    ("ok", "cancel"): {"OK": True, "Cancel": False, None: None},
    ("yes", "no", "cancel"): {"Yes": True, "No": False, "Cancel": None, None: None},
    ("retry", "cancel"): {"Retry": True, "Cancel": False, None: None},
}
_ASK_PRESET_LABELS = {
    ("yes", "no"): ["No", "Yes"],
    ("ok", "cancel"): ["Cancel", "OK"],
    ("yes", "no", "cancel"): ["Cancel", "No", "Yes"],
    ("retry", "cancel"): ["Cancel", "Retry"],
}


class pynoteswindow(ctk.Window):
    """The root PyNotes window; adds sub-windows,
    and ask/info/error/warning dialogs that can be answered
    from either the GUI or the terminal console.
    """

    def __init__(self, *args, **kwargs):
        """Create the window; no theme is applied until one is set."""
        super().__init__(*args, **kwargs)
        self.theme = None

    def subwin(self, *args, parent=None, **kwargs):
        """Create a themed Toplevel sub-window of this window, or of
        `parent` (another window of PyNotes) if given (kept above it,
        and minimized/restored together with it).
        """
        return ctk.Toplevel(parent or self, *args, **kwargs)

    def themes(self):
        """The sorted names of every available theme."""
        return sorted(list(themes.THEMES[0].keys() | themes.THEMES[1].keys()))

    def gettheme(self):
        """The name of the current theme."""
        return self.theme or "Default"

    def settheme(self, name):
        """Switch to the given theme name, and make the canvastk
        widgets follow it (light/dark appearance and colors).
        """
        if name is None:
            self.settheme("Default")
            return
        if name in themes.THEMES[0]:
            ctk.reset_theme()
            ctk.set_appearance_mode("light")
            ctk.set_theme(themes.THEMES[0][name])
        elif name in themes.THEMES[1]:
            ctk.reset_theme()
            ctk.set_appearance_mode("dark")
            ctk.set_theme(themes.THEMES[1][name])
        else:
            return
        self.theme = name
        utils.EnabledLookTextbox.refresh_all()
        for buffer in state.all_buffers:
            buffer.refresh_fileinfo_contrast_colors()

    def getfonts(self):
        """The names of every font family available."""
        return tkfont.families(self)

    def _build_message_dialog(
        self,
        kind,
        title,
        message,
        button_labels,
        default_label=None,
        alert=False,
        parent=None,
    ):
        """Build (but don't yet show/grab) a message dialog laid out
        exactly like canvastk's own message boxes, with the given
        buttons (button_labels is in console order, so it's shown
        reversed); return it and a dict that press() fills in with the
        clicked button's label. It belongs to `parent` (default: this
        window).
        """
        top = self.subwin(parent=parent)
        top.withdraw()
        top.title(title or "")
        top.resizable(False, False)
        state_ = {"result": None}

        def press(label):
            """Record the clicked button's label and close the dialog."""
            state_["result"] = label
            top.after_idle(lambda: top.destroy() if top.winfo_exists() else None)

        def close_dialog():
            """Close the dialog without an answer."""
            if top.winfo_exists():
                top.destroy()

        default_label = default_label or button_labels[-1]
        body = ctk.Frame(top)
        body.pack(fill="both", expand=True, padx=18, pady=(16, 10))
        ctk.messagebox._MessageBoxIcon(body, kind or ctk.messagebox.QUESTION).pack(
            side="left", anchor="n", padx=(0, 14)
        )
        text = ctk.Frame(body)
        text.pack(side="left", fill="both", expand=True)
        ctk.Label(text, str(message or ""), wraplength=380, justify="left").pack(
            anchor="w"
        )
        row = ctk.Frame(top)
        row.pack(fill="x", padx=18, pady=(0, 16))
        for label in button_labels:
            ctk.Button(row, label, command=lambda l=label: press(l)).pack(
                side="right", padx=(8, 0)
            )
        top.bind("<Return>", lambda e: press(default_label))
        top.bind("<Escape>", lambda e: close_dialog())
        top.protocol("WM_DELETE_WINDOW", close_dialog)
        ctk.messagebox._center_on(top, parent or self)
        top.deiconify()
        top.lift()
        if alert:
            top.bell()
        top.focus_force()
        return top, state_

    def _build_query_dialog(self, title, prompt, parent=None):
        """Build (but don't yet show/grab) a text-entry dialog styled
        like canvastk's own message boxes; return it and a dict that
        submit() fills in with the entered text. It belongs to `parent`
        (default: this window).
        """
        top = self.subwin(parent=parent)
        top.withdraw()
        top.title(title or "")
        top.resizable(False, False)
        state_ = {"result": None}

        def submit(*_):
            """Record the entered text and close the dialog."""
            state_["result"] = entry.get()
            if top.winfo_exists():
                top.destroy()

        def cancel(*_):
            """Close the dialog without an answer."""
            if top.winfo_exists():
                top.destroy()

        body = ctk.Frame(top)
        body.pack(fill="both", expand=True, padx=18, pady=(16, 10))
        ctk.messagebox._MessageBoxIcon(body, ctk.messagebox.QUESTION).pack(
            side="left", anchor="n", padx=(0, 14)
        )
        text = ctk.Frame(body)
        text.pack(side="left", fill="both", expand=True)
        ctk.Label(text, str(prompt or ""), wraplength=380, justify="left").pack(
            anchor="w"
        )
        entry = ctk.Entry(text)
        entry.pack(fill="x", pady=(8, 0))
        row = ctk.Frame(top)
        row.pack(fill="x", padx=18, pady=(0, 16))
        ctk.Button(row, "Cancel", command=cancel).pack(side="right", padx=(8, 0))
        ctk.Button(row, "Submit", command=submit).pack(side="right", padx=(8, 0))
        entry.bind("<Return>", submit)
        entry.bind("<KP_Enter>", submit)
        top.bind("<Escape>", cancel)
        top.protocol("WM_DELETE_WINDOW", cancel)
        ctk.messagebox._center_on(top, parent or self)
        top.deiconify()
        top.lift()
        entry.focus_force()
        return top, state_

    def _race_console(self, console_call, top, state_):
        """Show a built graphical dialog (top) while also running
        console_call (an equivalent console prompt/ask) in a background
        thread; return whichever answers first, closing the graphical
        dialog if the console wins or cancelling the console prompt if
        the graphical dialog wins.
        """
        cancel_event = threading.Event()
        resultq = queue.Queue()

        def worker():
            """Run the console prompt and queue its answer."""
            resultq.put(console_call(cancel_event))

        threading.Thread(target=worker, daemon=True).start()
        top.grab_set()

        def poll():
            """Close the dialog if the console has answered, else check again soon."""
            try:
                value = resultq.get_nowait()
            except queue.Empty:
                if top.winfo_exists():
                    top.after(50, poll)
                return
            state_["console_result"] = ("console", value)
            if top.winfo_exists():
                top.destroy()

        top.after(50, poll)
        top.wait_window()
        if "console_result" in state_:
            return state_["console_result"][1]
        cancel_event.set()
        return state_["result"]

    def _resolve_clicked(self, clicked, button_labels):
        """Normalize a console answer (a 1-based button index) or a
        graphical answer (already the button's label) to a label.
        """
        if isinstance(clicked, int):
            return (
                button_labels[clicked - 1]
                if 1 <= clicked <= len(button_labels)
                else None
            )
        return clicked

    def ask(self, title, question, options, parent=None):
        """Ask a yes/no(/cancel)-style question and return the mapped
        boolean/None answer (or, for an options tuple with no preset,
        the clicked label itself). `parent` is the window it belongs to
        (default: the main window).
        """
        options_tuple = tuple(options)
        button_labels = _ASK_PRESET_LABELS.get(options_tuple, list(options))
        top, state_ = self._build_message_dialog(
            None, title, question, button_labels, parent=parent
        )
        console_call = lambda cancel_event: state.console.ask(
            title, question, button_labels, cancel_event=cancel_event
        )
        clicked = self._resolve_clicked(
            self._race_console(console_call, top, state_), button_labels
        )
        return (
            _ASK_PRESETS[options_tuple].get(clicked, None)
            if options_tuple in _ASK_PRESETS
            else clicked
        )

    def askstring(self, title, prompt, parent=None):
        """Prompt for a line of text and return it (or "" if cancelled).
        `parent` is the window it belongs to (default: the main window).
        """
        top, state_ = self._build_query_dialog(title, prompt, parent=parent)
        console_call = lambda cancel_event: state.console.prompt(
            title, prompt, cancel_event=cancel_event
        )
        return self._race_console(console_call, top, state_)

    def _notice_with_buttons(self, kind, title, message, buttons, alert, parent=None):
        """Show an info/error/warning dialog with custom buttons and
        return the clicked label (used when info/error/warning are given
        a `buttons` argument instead of the plain OK-only default).
        """
        color = "43m" if kind == "warning" else ("41m" if kind == "error" else "100m")
        button_labels = list(buttons)
        top, state_ = self._build_message_dialog(
            kind, title, message, button_labels, alert=alert, parent=parent
        )
        console_call = lambda cancel_event: state.console.ask(
            title, message, button_labels, color=color, cancel_event=cancel_event
        )
        return self._resolve_clicked(
            self._race_console(console_call, top, state_), button_labels
        )

    def info(self, title, message, buttons=None, parent=None, **kwargs):
        """Show an info dialog. With buttons, it's answerable from the
        console like ask(); without, it's shown in the console only as a
        non-blocking mirror (via a background thread) while the
        graphical OK-only dialog is what actually blocks.
        """
        if buttons:
            return self._notice_with_buttons(
                "info", title, message, buttons, alert=False, parent=parent
            )
        threading.Thread(
            target=state.console.dialog, args=(title, message), daemon=True
        ).start()
        return ctk.messagebox.showinfo(title, message, parent=parent, **kwargs)

    def error(self, title, message, buttons=None, parent=None, **kwargs):
        """Show an error dialog; see info() for the buttons/console
        behavior.
        """
        if buttons:
            return self._notice_with_buttons(
                "error", title, message, buttons, alert=True, parent=parent
            )
        threading.Thread(
            target=state.console.dialog, args=(title, message, "41m"), daemon=True
        ).start()
        return ctk.messagebox.showerror(title, message, parent=parent, **kwargs)

    def warning(self, title, message, buttons=None, parent=None, **kwargs):
        """Show a warning dialog; see info() for the buttons/console
        behavior.
        """
        if buttons:
            return self._notice_with_buttons(
                "warning", title, message, buttons, alert=True, parent=parent
            )
        threading.Thread(
            target=state.console.dialog, args=(title, message, "43m"), daemon=True
        ).start()
        return ctk.messagebox.showwarning(title, message, parent=parent, **kwargs)


def saveforclose():
    """Ask every buffer that supports it to save before closing; return
    False (aborting the close) if any buffer's save is cancelled.
    """
    for buffer in state.all_buffers:
        if hasattr(buffer, "saveforclose") and not buffer.saveforclose():
            return False
    return True


def find_open_editor(abspath):
    """Return the already-open, non-view Editor buffer for abspath, if
    any, so opening it again can create a synced peer view of it (see
    Editor._make_peer_type) instead of loading a second, separate copy.
    """
    for buffer in state.all_buffers:
        if not isinstance(buffer, editor.Editor):
            continue
        if (
            buffer.view_master is None
            and buffer.title == abspath
            and buffer.hmode not in ("png", "pdf", "epub")
        ):
            return buffer


def setactive(newindex=None, force=False):
    """Switch the active buffer to newindex (default: the next buffer,
    wrapping around), or re-activate the current one if force is True.
    """
    if newindex is None:
        newindex = state.buffindex + 1
    if newindex == -1:
        newindex = len(state.all_buffers) - 1
    if newindex == len(state.all_buffers):
        newindex = 0
    if newindex == state.buffindex and not force:
        return
    if 0 <= state.buffindex < len(state.all_buffers):
        state.all_buffers[state.buffindex].active = False
    try:
        buffer = state.all_buffers[newindex]
    except Exception:
        return
    pycode.pcrunhook("before", "switch-buffer", newindex)
    state.buffindex = newindex
    buffer.active = True
    state.active = buffer
    update_menus()
    state.root.update()
    buffer.mainwidget.focus_set()
    settitle()
    pycode.pcrunhook("after", "switch-buffer", state.buffindex)


def update_menus():
    """Rebuild the main menu bar from the active buffer's own menu (`.m`),
    since different buffer types (editor, terminal, ...) expose different
    menus.
    """
    state.mainmenu.delete(0, "end")
    for entry in state.active.m.entries:
        if entry["kind"] == "cascade":
            state.mainmenu.add_cascade(label=entry["label"], menu=entry["menu"])


def settitle():
    """Set the window title from the active buffer's wanttitle, unless a
    PyCode command has taken over the title (state.pcsettitle).
    """
    if state.active and not state.pcsettitle:
        state.root.title("PyNotes - " + state.active.wanttitle)


def balance(orient="all"):
    """Resize the panes of the horizontal and/or vertical splits to be
    equal-sized.
    """
    if orient == "all":
        orients = ("horizontal", "vertical")
    else:
        orients = (orient,)
    for split in state.panes._splits():
        if split.orient in orients:
            share = 1 / len(split.children)
            split.fractions = [share] * len(split.children)
    state.panes._layout()


def neweditor(file=None, orient="horizontal"):
    """Open a new Editor buffer. If file is True, prompt for a file to
    open; if file is a path, load it (or open a peer view of it if
    already open elsewhere); if file is None, open a blank editor.
    """
    if file == True:
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
        if fn:
            utils.show("open file")
            neweditor(fn, orient=orient)
        return
    if file and os.path.isdir(file):
        state.root.error("Error", f'"{os.path.basename(file)}" is a directory.')
        return
    hookevent = "open-file-new-editor" if file else "new-file-new-editor"
    pycode.pcrunhook("before", hookevent, file)
    match = find_open_editor(os.path.abspath(file)) if file else None
    newedit = buffer.newbuffer(
        editor.Editor, orient, file=None if match else file, view_master=match
    )
    pycode.pcrunhook("after", hookevent, file)
    return newedit


def _on_root_resize(event):
    """<Configure> handler for the root window: debounce resize events
    (which fire continuously while dragging) so _do_resize_balance only
    runs once, DEBOUNCE_TIME after resizing stops.
    """
    if event.widget is not state.root:
        return
    size = (event.width, event.height)
    if size == state._last_root_size:
        return
    state._last_root_size = size
    if state._resize_after_id is not None:
        state.root.after_cancel(state._resize_after_id)
    state._resize_after_id = state.root.after(DEBOUNCE_TIME, _do_resize_balance)


def _do_resize_balance():
    """Rebalance all panes after the debounce delay in _on_root_resize."""
    state._resize_after_id = None
    if not state.root.winfo_exists():
        return
    pycode.pcrunhook("before", "resize-window")
    balance()
    pycode.pcrunhook("after", "resize-window")


def ext():
    """Cleanly exit PyNotes: confirm killing any running processes and
    saving unsaved files, then tear down buffers, the console, and the
    window before exiting the process.
    """
    if any(getattr(buffer, "running", False) for buffer in state.all_buffers):
        answer = state.root.ask(
            "Warning", "Kill active process(es) and close?", options=("ok", "cancel")
        )
        if answer != True:
            return
    if any(
        isinstance(buffer, editor.Editor) and buffer._file_watch_prompt_pending
        for buffer in state.all_buffers
    ):
        utils.show(
            "select 'Discard Changes & Reload' or 'Ignore' external changes before closing the editor"
        )
        return
    answer = (
        state.root.ask(
            "Warning",
            "Do you want to save files before closing?",
            options=("yes", "no", "cancel"),
        )
        if any(getattr(buffer, "unsaved", False) for buffer in state.all_buffers)
        else False
    )
    if answer != None:
        if answer:
            if not saveforclose():
                return
        try:
            pycode.pcrunhook("before", "exit-pynotes")
        except Exception:
            pass
        try:
            if os.path.exists(f"{homedir}/.local/share/PyNotes/tempcode"):
                os.remove(f"{homedir}/.local/share/PyNotes/tempcode")
        except Exception:
            pass
        sys.stderr = open(os.devnull, "w")
        try:
            state.root.after_cancel(state.consoleqafter)
        except Exception:
            pass
        for buffer in state.all_buffers:
            try:
                if hasattr(buffer, "_cancel_all_after_ids"):
                    buffer._cancel_all_after_ids()
            except Exception:
                pass
        for closer in list(state._open_terminal_closers):
            try:
                closer()
            except Exception:
                pass
        try:
            state.root.destroy()
        except Exception:
            pass
        for buffer in state.all_buffers:
            try:
                buffer.observer.stop()
            except Exception:
                pass
        try:
            pycode.pcrunhook("after", "exit-pynotes")
        except Exception:
            pass
        try:
            import cli

            cli.close()
        except Exception:
            pass
        os._exit(0)
