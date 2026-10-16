"""Shared helper functions used throughout PyNotes."""

import os
import sys
import platform
import subprocess
import threading
import webbrowser
import state
import tkinter as tk
import time
import weakref
import canvastk as ctk
import textbox
from init import homedir, rootdir, monospace


def bindrecur(widget, event, func, break_=True, *args, **kwargs):
    """Bind an event handler to widget and all of its descendants.

    If break_ is True, the handler's return value is ignored and "break"
    is returned instead, stopping tkinter's normal event propagation.
    """
    if break_:
        f = lambda *args, **kwargs: func(*args, **kwargs) or "break"
    else:
        f = func
    widget.bind(event, lambda event, f=f: f(event), *args, **kwargs)
    for child in widget.winfo_children():
        bindrecur(child, event, func, break_, *args, **kwargs)


def unbindrecur(widget, *args, **kwargs):
    """Unbind an event from widget and all of its descendants."""
    widget.unbind(*args, **kwargs)
    for child in widget.winfo_children():
        unbindrecur(child, *args, **kwargs)


def bindtype_(buffer, event, func, break_=True, *args, **kwargs):
    """Bind an event on an Editor buffer's underlying text widget only.

    No-op for non-Editor buffers (e.g. terminals), since they have no
    `_own_type` text widget to bind to.
    """
    import editor

    if break_:
        f = lambda *args, **kwargs: func(*args, **kwargs) or "break"
    else:
        f = func
    if isinstance(buffer, editor.Editor):
        buffer._own_type.bind(event, lambda event, f=f: f(event), *args, **kwargs)


def unbindtype_(buffer, *args, **kwargs):
    """Unbind an event from an Editor buffer's underlying text widget."""
    if isinstance(buffer, editor.Editor):
        buffer._own_type.unbind(*args, **kwargs)


def load_user_themes():
    """Refresh the themes list."""

    def _valid_color(color):
        try:
            state.root.winfo_rgb(color)
        except Exception:
            return False
        else:
            return True

    def _check_valid_themes(*themes_to_check):
        for themes_list in themes_to_check:
            assert type(themes_list) == dict, "Invalid user themes"
            for name, theme in themes_list.items():
                assert type(name) == str, "Theme name not a string."
                assert type(theme) == dict, f"Invalid theme {name!r}"
                for theme_key, theme_value in theme.items():
                    assert theme_key in tuple(
                        ctk.CANVAS_WIDGET_THEME
                    ), "Invalid theme key."

    import json
    import themes
    import copy

    themes_path = f"{homedir}/.local/share/PyNotes/user_themes.json"
    if not os.path.exists(themes_path):
        return
    try:
        with open(themes_path) as file:
            light_themes, dark_themes = json.load(file)
        _check_valid_themes(light_themes, dark_themes)
        themes.THEMES[0].update(light_themes)
        themes.THEMES[1].update(dark_themes)
    except Exception as e:
        state.root.error("Error", f"Error while trying to load user themes:\n{e}")
        themes.THEMES = copy.deepcopy(themes.ORIGINAL_THEMES)


def save_theme_and_reload(theme):
    """Save a user-made theme and refresh the themes list."""
    import json
    import themes

    name, dark, colors = theme
    user_themes = [
        {
            k: v
            for k, v in lightordark.items()
            if k not in lightordarkorg or v != lightordarkorg[k]
        }
        for lightordark, lightordarkorg in zip(themes.THEMES, themes.ORIGINAL_THEMES)
    ]
    if dark:
        user_themes[1][name] = colors
    else:
        user_themes[0][name] = colors
    themes_path = f"{homedir}/.local/share/PyNotes/user_themes.json"
    with open(themes_path, "w") as file:
        json.dump(user_themes, file, indent=4)
    load_user_themes()


class EnabledLookTextbox(ctk.Textbox):
    """A canvastk Textbox that is disabled only to prevent editing, so
    it isn't drawn greyed out: its disabled colors are the normal ones.
    These colors are recomputed by refresh_enabled_look_textboxes()
    whenever the theme changes."""

    _ALL_ENABLED_LOOK_TEXTBOXES = weakref.WeakSet()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._ALL_ENABLED_LOOK_TEXTBOXES.add(self)
        self.refresh_enabled_look()

    def refresh_enabled_look(self):
        """Recompute the disabled colors from the current theme."""
        theme = ctk.get_theme()
        self.set_theme(
            {"surface_disabled": theme["surface"], "text_disabled": theme["text"]}
        )

    @classmethod
    def refresh_all(cls):
        """Recompute the disabled colors of every live instance."""
        for textbox in list(cls._ALL_ENABLED_LOOK_TEXTBOXES):
            try:
                textbox.refresh_enabled_look()
            except tk.TclError:
                pass


class EnabledLookCursorTextbox(EnabledLookTextbox, textbox.CustomTextbox):
    """An enabled look textbox which is also a custom cursor textbox."""


def lock_window_size(window):
    """Lock window to its current size (fixes both min and max size to
    the current geometry), preventing manual resizing."""
    try:
        window.update()
        width, height = window.winfo_width(), window.winfo_height()
        window.minsize(width=width, height=height)
        window.maxsize(width=width, height=height)
    except Exception:
        pass


def unlock_window_size(window):
    """Undo lock_window_size(), letting window resize freely again."""
    try:
        window.update()
        window.minsize(width=0, height=0)
        window.maxsize(width=99999, height=99999)
    except Exception:
        pass


def show(text):
    """Display text as a status message in the Alt-X command box, and
    mirror it to the console (the terminal PyNotes was launched
    from)."""
    while state.prompting:
        state.root.update()
        time.sleep(0.01)
    state.cmdentry.config(state="normal")
    state.cmdentry.delete("1.0", "end")
    state.cmdentry.insert("end", text.replace("\n", "\\n"))
    state.cmdentry.unbind("<KeyPress>")
    state.cmdentry.unbind("<Return>")
    state.cmdentry.unbind("<Escape>")
    state.cmdentry.unbind("<Up>")
    state.cmdentry.unbind("<Down>")
    state.cmdentry.config(state="disabled")
    state.cmdautocomplete.pack_forget()
    threading.Thread(target=state.console.show, args=(text,), daemon=True).start()


def prompt(text, autocompletefunc=None, defaultinput=None, history=[]):
    """Prompt the user for input in the Alt-X command box and return it.

    text is shown as the fixed, non-editable prompt prefix. If
    autocompletefunc is given, Tab either completes the common prefix of
    the matches or shows the match list; it may be a callable that takes
    the currently typed text and returns candidates, or a fixed
    list/tuple of candidates. If defaultinput is given, the input starts
    pre-filled with it. Blocks (pumping the tkinter event loop) until the
    user presses Return.
    """

    def check_edit(event, text, promptend):
        nonlocal i
        nonlocal current_history
        """Re-pin the prompt prefix after each keypress and hide the
        autocomplete list; block BackSpace from eating into the prompt.
        Move the current typed text to the bottom of the history if it
        is not already."""
        state.cmdentry.delete("1.0", promptend)
        state.cmdentry.insert("1.0", text)
        state.cmdentry.tag_add("prompt", "1.0", promptend)
        state.cmdautocomplete.pack_forget()
        i = None
        current_history = None
        if event.keysym in ("BackSpace", "Left") and state.cmdentry.compare(
            "insert", "==", promptend
        ):
            return "break"

    def setreturninput(promptend):
        """Capture the typed input (everything after the prompt) and end
        the prompt loop."""
        nonlocal inputtext
        inputtext = state.cmdentry.get(promptend, "1.end")
        state.prompting = False

    def autocomplete(cmdentry, promptend, autocompletefunc):
        """Complete the typed text's common prefix among the candidates,
        or, if there's nothing more to complete, show the match list."""
        completes = []
        typedtext = cmdentry.get(promptend, "1.end")
        if callable(autocompletefunc):
            autocompletelist = sorted(autocompletefunc(typedtext))
        else:
            autocompletelist = sorted(autocompletefunc)
        for option in autocompletelist:
            if option.startswith(typedtext):
                completes.append(option)
        if newcomplete := os.path.commonprefix(completes)[len(typedtext) :]:
            cmdentry.insert("1.end", newcomplete)
        else:
            if not completes:
                completes.append("[no match]")
            state.cmdautocomplete.config(state="normal")
            state.cmdautocomplete.delete("1.0", "end")
            state.cmdautocomplete.insert("1.0", "    ".join(completes))
            state.cmdautocomplete.pack(
                padx=10, pady=10, fill="x", anchor="n", after=cmdentry
            )
            state.cmdautocomplete.update_idletasks()
            displaylines = state.cmdautocomplete.count("1.0", "end-1c", "displaylines")
            state.cmdautocomplete.config(
                height=min(displaylines[0], 5) if displaylines else 1
            )
            state.cmdautocomplete.config(state="disabled")

    def history_up():
        """Move up in the given history to the prompt."""
        nonlocal i
        nonlocal current_history
        if i == 0:
            return
        if not history:
            return
        if i is None:
            i = len(history)
            current_history = state.cmdentry.get(promptend, "1.end")
        i -= 1
        state.cmdentry.delete(promptend, "end")
        state.cmdentry.insert(promptend, history[i])
        state.cmdentry.mark_set("insert", "end")

    def history_down():
        """Move down in the given history to the prompt."""
        nonlocal i
        nonlocal current_history
        if i is None:
            return
        if not history:
            return
        len_his = len(history)
        if i == len_his:
            return
        i += 1
        if i == len_his:
            state.cmdentry.delete(promptend, "end")
            state.cmdentry.insert(promptend, current_history)
            state.cmdentry.mark_set("insert", "end")
            i = None
            current_history = None
            return
        state.cmdentry.delete(promptend, "end")
        state.cmdentry.insert(promptend, history[i])
        state.cmdentry.mark_set("insert", "end")

    while state.prompting:
        state.root.update()
        time.sleep(0.01)
    state.prompting = True
    inputtext = ""
    i = None
    current_history = None
    state.cmdentry.config(state="normal")
    state.cmdentry.delete("1.0", "end")
    state.cmdentry.insert("1.0", text)
    promptend = state.cmdentry.index("1.end")
    state.cmdentry.tag_add("prompt", "1.0", promptend)
    state.cmdentry.tag_config("prompt", font=(monospace, 12, "bold"))
    if defaultinput:
        state.cmdentry.insert("end", defaultinput)
        state.cmdentry.mark_set("insert", "end")
    state.cmdentry.bind(
        "<KeyPress>",
        lambda event, text=text, promptend=promptend: check_edit(
            event, text, promptend
        ),
    )
    state.cmdentry.bind(
        "<Return>", lambda event, promptend=promptend: setreturninput(promptend)
    )
    state.cmdentry.bind("<Escape>", lambda event: setattr(state, "prompting", False))
    state.cmdentry.bind("<Up>", lambda event: history_up() or "break")
    state.cmdentry.bind("<Down>", lambda event: history_down() or "break")
    if autocompletefunc:
        state.cmdentry.bind(
            "<Tab>",
            lambda event, cmdentry=state.cmdentry, promptend=promptend, autocompletefunc=autocompletefunc: autocomplete(
                cmdentry, promptend, autocompletefunc
            )
            or "break",
        )
    state.root.update()
    state.cmdentry.focus_set()
    while state.prompting:
        state.root.update()
        time.sleep(0.01)
    state.cmdentry.delete("1.0", "end")
    state.cmdentry.unbind("<KeyPress>")
    state.cmdentry.unbind("<Return>")
    state.cmdentry.unbind("<Escape>")
    state.cmdentry.unbind("<Up>")
    state.cmdentry.unbind("<Down>")
    state.cmdentry.config(state="disabled")
    state.cmdautocomplete.pack_forget()
    state.active.mainwidget.focus_set()
    state.root.update()
    return inputtext


def dp():
    """Open the PyNotes GitHub plugins page in the default browser."""
    show("open download plugins url")
    webbrowser.open("https://github.com/rafugafu/PyNotes/tree/main/Plugins")


def op():
    """Open the plugin add-ons directory in the system file manager."""
    show("open plugin directory")
    pp = f"{homedir}/.local/share/PyNotes/add-ons"
    if platform.system() == "Linux":
        subprocess.run(["xdg-open", pp])
    else:
        os.startfile(pp)


def mathgod():
    """Launch MathGod.py as a separate process, running its open-mathgod
    PyCode hooks before and after."""
    import pycode

    pycode.pcrunhook("before", "open-mathgod")
    show("open mathgod")
    subprocess.Popen([sys.executable, f"{rootdir}/MathGod.py"])
    pycode.pcrunhook("after", "open-mathgod")


def ss():
    """Open a PyNotes source code file chosen by the user, from the
    installed PyNotes source directory, in a new editor."""
    import dialogs
    import pycode
    import window

    pycode.pcrunhook("before", "show-pynotes-source-code")
    show("open pynotes source code")
    fn = dialogs.openfileget(
        (("Python Files", "*.py"),), "Open PyNotes Source Code File: ", rootdir
    )
    if not fn:
        return
    window.neweditor(fn)
    pycode.pcrunhook("after", "show-pynotes-source-code")


class ErrorHandler:
    """A file-like object (assigned to sys.stderr) that shows uncaught
    errors/tracebacks in a popup window instead of only printing them."""

    def __init__(self):
        self.win = None
        self.textbox = None

    def write(self, error):
        """Show error in the error window, creating it if needed, or
        appending to it if it's already open. Runs on the main thread via
        state.root.after since write() may be called from any thread."""
        if error.strip():

            def _do_write(error=error):
                threading.Thread(
                    target=state.console.dialog,
                    args=("Error", error, "41m"),
                    daemon=True,
                ).start()
                if self.win == None or not self.win.winfo_exists():
                    self.win = state.root.subwin()
                    self.win.lift()
                    self.win.title("Error")
                    self.win.bind("<Escape>", lambda event: self.win.destroy())
                    self.win.bind("<Return>", lambda event: self.win.destroy())

                    self.textbox = EnabledLookTextbox(
                        self.win,
                        scrolled=True,
                        font=(monospace, 12),
                        width=60,
                        height=15,
                    )
                    self.textbox.pack(fill="both", expand=True)
                    self.textbox.insert("end", error)
                    self.textbox.see("end")
                    self.textbox.config(state="disabled")
                    self.win.update()
                    lock_window_size(self.win)
                else:
                    self.textbox.config(state="normal")
                    self.textbox.insert("end", f"\n{error}")
                    self.textbox.see("end")
                    self.textbox.config(state="disabled")

            state.root.after(0, _do_write)

    def flush(self):
        pass


def _report_callback_exception(exc, val, tb):
    """tkinter callback-exception hook (installed in init.py): report
    errors as usual, except TclErrors, which are suppressed since they
    tend to be harmless Tcl/tk-level issues (e.g. a widget already
    destroyed) rather than real bugs."""
    if issubclass(exc, tk.TclError):
        return
    tk.Tk.report_callback_exception(state.root, exc, val, tb)
