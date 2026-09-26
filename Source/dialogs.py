"""File dialogs and other prompts that PyNotes can answer either from its
graphical window or from its terminal console (whichever the user
responds to first "wins the race" and cancels the other)."""

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
    progress of a pip install."""
    import easytk

    termwin = easytk.win()
    termwin.title("Terminal")
    term = termwin.textbox(font=(monospace, 12))
    term.insert("end", f"{getpass.getuser()}@PyNotes:~$ {command}\n")
    term.pack(fill="both")
    termwin.update()
    termwin.sizablefalse()
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
        termwin.error(
            "Error",
            f'An error occured while installing the module {command.split("pip install ")[1]}:\n{e}',
        )
    time.sleep(2)
    termwin.destroy()


def fileautocompletefunc(typed):
    """Return filesystem-path completions for typed, for use as the
    autocompletefunc of utils.prompt() in console-mode file dialogs."""
    typed = typed.strip()
    dir_ = os.path.abspath(os.path.expanduser(os.path.dirname(typed)))
    if not os.path.exists(dir_):
        return ()
    else:
        autocompletelist = ("../",)
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
            autocompletelist += (completion,)
        return autocompletelist


def _console_prompt_worker(title, prompttext, cancel_event, resultq):
    """Background-thread target: block on the console prompt and put its
    result (or "" if cancel_event caused it to give up) into resultq."""
    resultq.put(state.console.prompt(title, prompttext, cancel_event=cancel_event))


def _race_console_box(title, prompttext, defaultinput):
    """Prompt for a filename via the Alt-X minibuffer, while also polling
    a console prompt running in a background thread; return whichever
    answers first and cancel the other."""
    cancel_event = threading.Event()
    resultq = queue.Queue()
    threading.Thread(
        target=_console_prompt_worker,
        args=(title, prompttext, cancel_event, resultq),
        daemon=True,
    ).start()
    winner = {}

    def poll():
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
    fn = utils.prompt(prompttext, fileautocompletefunc, defaultinput)
    if "result" not in winner:
        winner["result"] = fn
        cancel_event.set()
    return winner["result"]


def _race_console_graphical(title, prompttext, zenity_args, native_dialog_call):
    """Show a graphical file dialog (zenity on Linux, otherwise
    native_dialog_call) while also polling a console prompt running in a
    background thread; return whichever answers first and cancel/close
    the other."""
    cancel_event = threading.Event()
    resultq = queue.Queue()
    threading.Thread(
        target=_console_prompt_worker,
        args=(title, prompttext, cancel_event, resultq),
        daemon=True,
    ).start()
    winner = {}
    if platform.system() == "Linux":
        proc = subprocess.Popen(
            zenity_args, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True
        )
        while "result" not in winner:
            try:
                value = resultq.get(timeout=0.1)
            except queue.Empty:
                value = None
            else:
                # Console answered first; kill the still-open zenity dialog.
                winner["result"] = value or ""
                if proc.poll() is None:
                    proc.terminate()
                    proc.wait()
                break
            if proc.poll() is not None:
                # zenity closed first; take its output as the answer.
                out, _ = proc.communicate()
                winner["result"] = out.strip()
                cancel_event.set()
                break
    else:
        # No zenity on non-Linux platforms, so native_dialog_call (a
        # blocking tkinter filedialog call) is used instead; track which
        # top-level windows it creates so they can be torn down if the
        # console answers first.
        before = set(state.root.winfo_children())

        def poll():
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
    filetypes=(("All Files", "*"),), prompttext="Open File: ", initialfile=None
):
    """Prompt for an existing file to open and return its absolute path,
    "" if cancelled, or None (after showing an error) if the chosen path
    doesn't exist or is a directory. Uses a graphical file dialog unless
    state.nographicalfiledialogs is set, in which case it prompts for a
    path in the Alt-X minibuffer instead.
    """
    if not state.nographicalfiledialogs:
        if platform.system() == "Linux":
            zenity_args = [
                "zenity",
                "--file-selection",
                f'--filename={initialfile or "./"}',
                "--title=Open File",
            ] + [f"--file-filter={ft[0]} | {ft[1]}" for ft in filetypes]
            fn = _race_console_graphical("Open", prompttext, zenity_args, None)
        else:
            import easytk

            initialdir = os.path.dirname(initialfile)
            initialfilename = os.path.basename(initialfile)
            native_dialog_call = lambda: easytk.fd.askopenfilename(
                title="Open File",
                filetypes=filetypes,
                initialfile=initialfilename or "",
                initialdir=initialdir or "",
            )
            fn = _race_console_graphical("Open", prompttext, None, native_dialog_call)
    else:
        if initialfile is None:
            initialfile = os.getcwd()
        if platform.system() == "Linux":
            initialfile = initialfile.replace(homedir, "~") + "/"
        else:
            initialfile = initialfile + "\\"
        fn = _race_console_box("Open", prompttext, initialfile)
    if not fn.strip():
        return ""
    fn = os.path.abspath(os.path.expanduser(fn))
    if not os.path.exists(fn):
        utils.show(f"error: '{fn}' does not exist")
        return None
    if os.path.isdir(fn):
        utils.show(f"error: '{fn}' is a directory")
        return None
    return fn


def saveasfileget(prompttext="Save File: ", initialfile=None):
    """Prompt for a filename to save to and return its absolute path, or
    "" if cancelled. Uses a graphical file dialog unless
    state.nographicalfiledialogs is set, in which case it prompts for a
    path in the Alt-X minibuffer instead, giving up if the path is a
    directory or looping to re-prompt if asking to confirm overwrite is
    declined (the graphical dialogs handle both of these themselves).
    """
    if not state.nographicalfiledialogs:
        if platform.system() == "Linux":
            zenity_args = [
                "zenity",
                "--file-selection",
                f'--filename={initialfile or "./"}',
                "--save",
                "--confirm-overwrite",
                "--title=Save As",
                "--file-filter=All Files | *",
            ]
            fn = _race_console_graphical("Save As", prompttext, zenity_args, None)
        else:
            import easytk

            initialdir = os.path.dirname(initialfile)
            initialfilename = os.path.basename(initialfile)
            native_dialog_call = lambda: easytk.fd.asksaveasfilename(
                initialfile=initialfilename or "", initialdir=initialdir or ""
            )
            fn = _race_console_graphical(
                "Save As", prompttext, None, native_dialog_call
            )
        if not fn.strip():
            return ""
    else:
        if initialfile is None:
            initialfile = os.getcwd()
        if platform.system() == "Linux":
            initialfile = initialfile.replace(homedir, "~") + "/"
        else:
            initialfile = initialfile + "\\"
        while True:
            fn = _race_console_box("Save As", prompttext, initialfile)
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
    it wasn't produced (compile failed), offer to show the LaTeX log."""
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
            logwin = state.root.subwin()
            logwin.title(f"LaTeX log for {os.path.basename(title)}")
            logtextboxscroll = logwin.scroll()
            logtextbox = logwin.textbox(
                yscrollcommand=logtextboxscroll.set, font=(monospace, 12)
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
                )
                logtextbox.insert("1.0", "log not found")
            logtextbox.config(state="disabled")
            logtextboxscroll.config(command=logtextbox.yview)
            logtextboxscroll.pack(fill="y", side="right")
            logtextbox.pack(fill="both", expand=True, side="left")
            logwin.style(state.root.gettheme())
    elif platform.system() == "Linux":
        subprocess.run(["xdg-open", pdf_], cwd=os.path.dirname(title))
    else:
        subprocess.run(["start", pdf_], cwd=os.path.dirname(title))
