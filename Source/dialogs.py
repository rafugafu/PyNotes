"""File dialogs and other prompts that PyNotes can answer either from its
graphical window or from its terminal console (whichever the user
responds to first "wins the race" and cancels the other).
"""

import os
import sys
import platform
import getpass
import subprocess
import time
import queue
import threading
import state
from init import homedir, monospace
import utils


def faketerm(command):
    """Run a shell command in a small popup window, streaming its output
    live, then close the window after a short pause. Used to show the
    progress of a pip install.
    """
    import canvastk as ctk

    def error(title, message):
        """Show an error dialog in both the console and the graphical window."""
        threading.Thread(
            target=state.console.dialog, args=(title, message, "41m"), daemon=True
        ).start()
        ctk.messagebox.showerror(title, message)

    termwin = ctk.Window()
    termwin.title("Terminal")
    term = ctk.Textbox(termwin, font=(monospace, 12))
    term.insert("end", f"{getpass.getuser()}@PyNotes:~$ {command}\n")
    term.pack(fill="both")
    termwin.update()
    utils.lock_window_size(termwin)
    try:
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        for line in process.stdout:
            term.insert("end", line)
            term.see("end")
            termwin.update()
        process.wait()
    except Exception as e:
        error(
            "Error",
            f'An error occured while installing the module {command.split("pip install ")[1]}:\n{e}',
        )
    time.sleep(2)
    termwin.destroy()


def fileautocompletefunc(typed):
    """Return filesystem-path completions for typed, for use as the
    autocompletefunc of utils.prompt() in console-mode file dialogs.
    """
    typed = typed.strip()
    dir_ = os.path.abspath(os.path.expanduser(os.path.dirname(typed)))
    if not os.path.exists(dir_):
        return []
    elif not os.path.isdir(dir_):
        return []
    else:
        autocompletelist = ["../"]
        for file in os.listdir(dir_):
            if (
                platform.system() == "Linux"
                and file.startswith(".")
                and not os.path.basename(typed)
            ):
                continue
            completion = os.path.join(os.path.dirname(typed), file)
            fullpath = os.path.abspath(os.path.expanduser(completion))
            if os.path.isdir(fullpath):
                completion += "/"
            autocompletelist.append(completion)
        return autocompletelist


def _console_prompt_worker(title, prompttext, cancel_event, resultq):
    """Background-thread target: block on the console prompt and put its
    result (or "" if cancel_event caused it to give up) into resultq.
    """
    resultq.put(state.console.prompt(title, prompttext, cancel_event=cancel_event))


def _race_console_box(title, prompttext, defaultinput, *args, **kwargs):
    """Prompt for a filename via the Alt-X minibuffer, while also polling
    a console prompt running in a background thread; return whichever
    answers first and cancel the other.
    """
    cancel_event = threading.Event()
    resultq = queue.Queue()
    threading.Thread(
        target=_console_prompt_worker,
        args=(title, prompttext, cancel_event, resultq),
        daemon=True,
    ).start()
    winner = {}

    def poll():
        """Take the console's answer if one has arrived, else check again soon."""
        if "result" in winner:
            return
        try:
            value = resultq.get_nowait()
        except queue.Empty:
            state.root.after(50, poll)
            return
        winner["result"] = value or ""
        # End the minibuffer prompt's blocking event loop early since the
        # console already answered.
        state.prompting = False

    state.root.after(50, poll)
    fn = utils.prompt(prompttext, fileautocompletefunc, defaultinput, *args, **kwargs)
    if "result" not in winner:
        winner["result"] = fn
        cancel_event.set()
    return winner["result"]


def _file_dialog_initial_dir_and_name(initialfile):
    """Split initialfile (a file path, a directory, or None for the
    current directory) into the (initialdir, initialfile) options of
    a canvastk file dialog.
    """
    if not initialfile:
        return os.getcwd(), ""
    if os.path.isdir(initialfile):
        return initialfile, ""
    return os.path.dirname(initialfile), os.path.basename(initialfile)


def _race_console_graphical(title, prompttext, native_dialog_call):
    """Show a graphical file dialog (native_dialog_call, a blocking
    canvastk file dialog call) while also polling a console prompt
    running in a background thread; return whichever answers first and
    cancel/close the other. If the console wins, the dialog's
    top-level windows (the ones created while it was open) are
    destroyed to end it.
    """
    cancel_event = threading.Event()
    resultq = queue.Queue()
    threading.Thread(
        target=_console_prompt_worker,
        args=(title, prompttext, cancel_event, resultq),
        daemon=True,
    ).start()
    winner = {}
    before = set(state.root.winfo_children())

    def poll():
        """Take the console's answer and close the dialog, else check again soon."""
        if "result" in winner:
            return
        try:
            value = resultq.get_nowait()
        except queue.Empty:
            state.root.after(50, poll)
            return
        winner["result"] = value or ""
        for w in set(state.root.winfo_children()) - before:
            try:
                w.destroy()
            except Exception:
                pass

    state.root.after(50, poll)
    fn = native_dialog_call()
    if "result" not in winner:
        winner["result"] = fn or ""
        cancel_event.set()
    return winner["result"]


def openfileget(
    filetypes=(("All Files", "*"),),
    prompttext="Open File: ",
    initialfile=None,
    parent=None,
):
    """Prompt for an existing file to open and return its absolute path,
    "" if cancelled, or None (after showing an error) if the chosen path
    doesn't exist or is a directory. Uses a graphical file dialog unless
    state.nographicalfiledialogs is set, in which case it prompts for a
    path in the Alt-X minibuffer instead. `parent` is the window the
    graphical dialog belongs to (default: the main window).
    """
    if not state.nographicalfiledialogs:
        from canvastk import filedialog

        initialdir, initialfilename = _file_dialog_initial_dir_and_name(initialfile)
        native_dialog_call = lambda: filedialog.askopenfilename(
            title="Open File",
            filetypes=filetypes,
            initialfile=initialfilename,
            initialdir=initialdir,
            parent=parent,
        )
        fn = _race_console_graphical("Open", prompttext, native_dialog_call)
    else:
        if initialfile is None:
            initialfile = os.getcwd()
        if platform.system() == "Linux":
            initialfile = initialfile.replace(homedir, "~") + "/"
        else:
            initialfile = initialfile + "\\"
        fn = _race_console_box(
            "Open", prompttext, initialfile, history=state.fileopenhistory
        )
    if not fn.strip():
        return ""
    fn = os.path.abspath(os.path.expanduser(fn))
    state.fileopenhistory.append(fn.strip())
    if not os.path.exists(fn):
        utils.show(f"error: '{fn}' does not exist")
        return None
    if os.path.isdir(fn):
        utils.show(f"error: '{fn}' is a directory")
        return None
    return fn


def saveasfileget(prompttext="Save File: ", initialfile=None, parent=None):
    """Prompt for a filename to save to and return its absolute path, or
    "" if cancelled. Uses a graphical file dialog unless
    state.nographicalfiledialogs is set, in which case it prompts for a
    path in the Alt-X minibuffer instead, giving up if the path is a
    directory or looping to re-prompt if asking to confirm overwrite is
    declined (the graphical dialogs handle both of these themselves).
    """
    if not state.nographicalfiledialogs:
        from canvastk import filedialog

        initialdir, initialfilename = _file_dialog_initial_dir_and_name(initialfile)
        native_dialog_call = lambda: filedialog.asksaveasfilename(
            initialfile=initialfilename, initialdir=initialdir, parent=parent
        )
        fn = _race_console_graphical("Save As", prompttext, native_dialog_call)
        if not fn.strip():
            return ""
        state.filesavehistory.append(fn.strip())
    else:
        if initialfile is None:
            initialfile = os.getcwd()
        if platform.system() == "Linux":
            initialfile = initialfile.replace(homedir, "~") + "/"
        else:
            initialfile = initialfile + "\\"
        while True:
            fn = _race_console_box(
                "Save As", prompttext, initialfile, history=state.filesavehistory
            )
            state.filesavehistory.append(fn.strip())
            if not fn.strip():
                return ""
            fn = os.path.abspath(os.path.expanduser(fn))
            if os.path.isdir(fn):
                utils.show(f"error: '{fn}' is an already existing directory")
                return None
            if os.path.exists(fn):
                overwrite = utils.prompt(
                    "File already exists. Overwrite (y/yes) or no (other): ",
                    ("y", "yes", "n", "no"),
                )
                if overwrite.strip().lower() in ("y", "yes"):
                    break
                initialfile = fn
            else:
                break
    return fn


def pdf(title):
    """Open the PDF for LaTeX file title in the system PDF viewer, or, if
    it wasn't produced (compile failed), offer to show the LaTeX log.
    """
    if os.path.splitext(title)[1] == ".tex":
        pdf_ = os.path.splitext(title)[0]
    else:
        pdf_ = title
    pdf_ += ".pdf"
    if not os.path.exists(pdf_):
        if state.root.ask(
            "Error",
            "The pdf could not be shown, there might have been an error in your code.\nDo you want to see the log?",
            ("yes", "no"),
        ):
            import canvastk as ctk

            logwin = state.root.subwin()
            logwin.title(f"LaTeX log for {os.path.basename(title)}")
            logtextbox = utils.EnabledLookTextbox(
                logwin,
                scrolled=True,
                font=(monospace, 12),
            )
            try:
                logtextbox.insert(
                    "1.0",
                    open(
                        f"{os.path.splitext(title)[0]}.log", "r", encoding="utf-8"
                    ).read(),
                )
            except:
                state.root.error(
                    "Error!",
                    f'The log was not found at "{os.path.splitext(title)[0]}.log".',
                    parent=logwin,
                )
                logtextbox.insert("1.0", "log not found")
            logtextbox.config(state="disabled")
            logtextbox.pack(fill="both", expand=True)
    elif platform.system() == "Linux":
        subprocess.run(["xdg-open", pdf_], cwd=os.path.dirname(title))
    else:
        subprocess.run(["start", pdf_], cwd=os.path.dirname(title))
