"""Shared helper functions used throughout PyNotes."""

import os
import sys
import platform
import subprocess
import threading
import webbrowser
import state
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


def load_themes():
    """Import every theme file in the user's themes directory."""
    themesdir = f"{homedir}/.local/share/PyNotes/themes"
    for file in os.listdir(themesdir):
        try:
            state.root.import_theme(f"{themesdir}/{file}")
        except Exception:
            pass


def show(text):
    """Display text as a status message in the Alt-X command box, and
    mirror it to the console (the terminal PyNotes was launched
    from)."""
    state.prompting = False
    state.cmdentry.config(state="normal")
    state.cmdentry.delete("1.0", "end")
    state.cmdentry.insert("end", text.replace("\n", "\\n"))
    state.cmdentry.unbind("<KeyPress>")
    state.cmdentry.unbind("<Return>")
    state.cmdentry.unbind("<Escape>")
    state.cmdentry.config(state="disabled")
    state.cmdautocomplete.pack_forget()
    threading.Thread(target=state.console.show, args=(text,), daemon=True).start()


def prompt(text, autocompletefunc=None, defaultinput=None):
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
        """Re-pin the prompt prefix after each keypress and hide the
        autocomplete list; block BackSpace from eating into the prompt."""
        state.cmdentry.delete("1.0", promptend)
        state.cmdentry.insert("1.0", text)
        state.cmdentry.tag_add("prompt", "1.0", promptend)
        state.cmdentry.mark_set("insert", "1.end")
        state.cmdautocomplete.pack_forget()
        if event.keysym == "BackSpace" and state.cmdentry.compare(
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

    state.prompting = True
    inputtext = ""
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
    state.cmdentry.bind("<Escape>", lambda event: show(""))
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
    state.cmdentry.delete("1.0", "end")
    state.cmdentry.unbind("<KeyPress>")
    state.cmdentry.unbind("<Return>")
    state.cmdentry.unbind("<Escape>")
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
                if self.win == None or not self.win.exists:
                    self.win = state.root.subwin()
                    self.win.title("Error")
                    self.win.bind("<Escape>", lambda event: self.win.destroy())
                    self.win.bind("<Return>", lambda event: self.win.destroy())
                    scrollbar = self.win.scroll()
                    self.textbox = self.win.textbox(
                        yscrollcommand=scrollbar.set,
                        font=(monospace, 12),
                        width=60,
                        height=15,
                    )
                    scrollbar.config(command=self.textbox.yview)
                    scrollbar.pack(fill="y", side="right")
                    self.textbox.pack(fill="both", expand=True, side="left")
                    self.textbox.insert("end", error)
                    self.textbox.see("end")
                    self.textbox.config(state="disabled")
                    self.win.style(state.root.gettheme())
                    self.win.update()
                    self.win.sizablefalse()
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
    import easytk

    if issubclass(exc, easytk.tk.TclError):
        return
    easytk.tk.Tk.report_callback_exception(state.root, exc, val, tb)
