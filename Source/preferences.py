"""The Preferences window and saving preferences to the defs file."""

import os
import sys
import subprocess
import state
import canvastk as ctk
import themes
import tkinter as tk
from init import v, homedir, monospace
import cursortextbox
import utils


def svprf():
    """Save the current preferences (including the Theme & Font tab's
    colours textbox) to the defs file, apply the new theme to every open
    buffer, and re-run syntax highlighting so the change takes effect
    immediately. Relies on `colours`, set by prf() while its window is
    open.
    """
    global colours
    import editor
    import pythonshell

    file = open(f"{homedir}/.local/share/PyNotes/defs", "w+", encoding="utf-8")
    font = state.defs[2]
    state.theme = (
        colours.get("1.0", "end-1c")
        .replace("\n", "")
        .replace("orgfont", "state.defs[2]")
    )
    file.write(
        f'{v}\n{str(state.bfr)}\n{font}\n{state.root.gettheme()}\n{",".join(state.dicts)}\n{state.emacskeysforsearch}\n{state.taborspace}\n{state.nographicalfiledialogs}\n{state.pythonexecutable}\n{state.curcurtype}\n{state.theme}'
    )
    file.close()
    exec("theme = {" + state.theme + "}", vars(state))
    editor._init_hl_tags()
    pythonshell._init_pythonshell_hl_tags()
    editor._init_plugin_tags()
    for buffer in state.all_buffers:
        if hasattr(buffer, "keypress"):
            buffer.keypress()


def prf():
    """Open the Preferences window (General / Theme & Font / Email tabs).

    Preferences are only written to disk by svprf(), which runs when the
    window is closed (OK, Escape, or the window's close button).
    """
    global colours
    import editor
    import pycode
    import dialogs

    pycode.pcrunhook("before", "open-preferences")
    utils.show("open preferences")

    def removedict():
        """Remove the selected dictionary from the list and rebuild the
        combined email spellcheck word list from what remains.
        """
        try:
            state.dicts.remove(dictlist.selection_get())
        except Exception:
            pass
        else:
            dictlist.delete(dictlist.curselection())
        state.emailwordlist.clear()
        try:
            for dictionary in state.dicts:
                if dictionary:
                    state.emailwordlist.extend(
                        open(dictionary, "r", encoding="utf-8").read().split("\n")
                    )
        except Exception as error:
            error = str(error)
            state.root.error("Error", error, parent=pr)

    def setts(val):
        state.taborspace = val

    def setffre(val):
        state.emacskeysforsearch = val

    def setnoguifd(val):
        state.nographicalfiledialogs = val

    def bf(opt):
        state.bfr = opt

    def adddict():
        """Prompt for a dictionary file, add it to the list, and rebuild
        the combined email spellcheck word list.
        """
        dicttoadd = dialogs.openfileget(
            prompttext="Email Dictionary File: ",
            filetypes=(("Text Files", "*.txt"),),
            parent=pr,
        )
        if dicttoadd:
            state.dicts.append(dicttoadd)
            dictlist.insert("end", dicttoadd)
            state.emailwordlist.clear()
            try:
                for dictionary in state.dicts:
                    if dictionary:
                        state.emailwordlist.extend(
                            open(dictionary, "r", encoding="utf-8").read().split("\n")
                        )
            except Exception as error:
                error = str(error)
                state.root.error("Error", error, parent=pr)

    def changepyexec():
        """Prompt for a new Python executable and update the shown path."""
        nonlocal pyexecshowtext
        fn = dialogs.openfileget(
            prompttext="New Python Executable: ",
            filetypes=(("All Files", "*"),),
            parent=pr,
        )
        if fn:
            state.pythonexecutable = fn
            pyexecshowtext.config(
                text=f"Python interpreter: '{state.pythonexecutable}'"
            )

    def changecurtype(newtype):
        """Change the cursor shape of all editors."""
        for buf in state.all_buffers:
            if hasattr(buf, "setcursortype"):
                buf.setcursortype(newtype.lower())
        state.cmdentry.set_cursor_shape(newtype.lower())
        state.curcurtype = [t.capitalize() for t in cursortextbox.CURSOR_SHAPES].index(
            newtype
        )

    def makeowntheme():
        """Launch custom canvastk creator so the user can design a
        custom canvastk theme, then apply the theme to canvastk.
        """
        newtheme = themes.creator()
        if newtheme is None:
            return
        utils.save_theme_and_reload(newtheme)
        uithemes = state.root.themes()
        state.root.settheme(newtheme[0])
        sts.configure(values=uithemes)
        sts.variable.set(newtheme[0])

    pr = state.root.subwin()
    pr.title("Preferences")
    tabs = ctk.Notebook(pr)
    gt = ctk.Frame(tabs)
    tft = ctk.Frame(tabs)
    et = ctk.Frame(tabs)
    tabs.add(gt, text="General")
    bfc = tk.BooleanVar(pr, value=state.bfr)
    ctk.Checkbutton(
        gt, text="Backup file regularly", command=lambda: bf(bfc.get()), variable=bfc
    ).grid(column=0, row=0, sticky="w")
    varts = tk.BooleanVar(pr, value=state.taborspace)
    ctk.Checkbutton(
        gt,
        text="Use spaces instead of tabs for indentation commands",
        command=lambda: setts(varts.get()),
        variable=varts,
    ).grid(column=0, row=1, sticky="w")
    varffre = tk.BooleanVar(pr, value=state.emacskeysforsearch)
    ctk.Checkbutton(
        gt,
        text="Use Emacs-like keybindings for the Find and Find & Replace",
        command=lambda: setffre(varffre.get()),
        variable=varffre,
    ).grid(column=0, row=2, sticky="w")
    ctk.Label(
        gt,
        text="""Emacs-like keys:
Find keys:
Control-R for previous match
Control-S for next match
Enter to close search
Find & Replace keys:
^ for previous
Alt-Enter for next
Control-T for replace and next
Enter to close search""",
    ).grid(column=0, row=3, sticky="w")
    varnoguifd = tk.BooleanVar(pr, value=state.nographicalfiledialogs)
    ctk.Checkbutton(
        gt,
        text="File prompts in the Alt-X command box (minibuffer) instead of a graphical file dialogue",
        command=lambda: setnoguifd(varnoguifd.get()),
        variable=varnoguifd,
    ).grid(column=0, row=4, sticky="w")
    ctk.Separator(gt).grid(column=0, row=5, sticky="ew")
    pyexecshowtext = ctk.Label(
        gt, text=f"Python interpreter: '{state.pythonexecutable}'"
    )
    pyexecshowtext.grid(column=0, row=6, sticky="w")
    ctk.Label(
        gt,
        text="Python executable to use for running Python code and the Python shell.\nNote: restart Python shell for this to take effect.",
    ).grid(column=0, row=7, sticky="w")
    ctk.Button(gt, text="Change", command=changepyexec).grid(
        column=0, row=8, sticky="ew"
    )
    ctk.Label(gt, text="Cursor shape:").grid(
        column=1, row=0, padx=10, pady=10, sticky="w"
    )
    current_cursor = [t.capitalize() for t in cursortextbox.CURSOR_SHAPES][
        state.curcurtype
    ]
    ctk.OptionMenu(
        gt,
        default=current_cursor,
        values=[t.capitalize() for t in cursortextbox.CURSOR_SHAPES],
        command=changecurtype,
    ).grid(column=2, row=0, padx=10, pady=10, sticky="ew")
    tabs.add(tft, text="Theme & Font")
    tabs.select(tft)
    tabs.pack(side="top", fill="both", expand=True, padx=10, pady=10)
    mf = ctk.Frame(tft)
    mf.grid(column=0, row=0)
    ctk.Label(mf, text="UI Theme").grid(column=0, row=0, padx=10, pady=10)
    sts = ctk.OptionMenu(
        mf,
        None,
        state.root.gettheme(),
        *state.root.themes(),
        command=lambda value: state.root.settheme(value),
    )
    sts.grid(column=1, row=0, padx=10, pady=10, sticky="ew")
    ctk.Button(mf, text="Make your own!", command=makeowntheme).grid(
        column=2, row=0, padx=10, pady=10, sticky="w"
    )
    ctk.Label(mf, text="Editor Font").grid(column=0, row=1, padx=10, pady=10)
    showfont = ctk.Textbox(tft, font=(state.defs[2], 12), wrap="word", height=5)
    showfont.insert(
        "end",
        "The quick brown fox jumped over the lazy dogs\nAaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz\n1234567890\n?.,<>;:'\"{}[]\\|\n!@#$%^&*()-_+=",
    )
    showfont.grid(column=0, row=1, sticky="nsew", padx=10, pady=10)
    f = ctk.OptionMenu(
        mf,
        None,
        state.defs[2],
        monospace,
        *sorted(state.root.getfonts()),
        command=lambda value: [
            [
                buffer.type_.config(font=(value, 12))
                for buffer in state.all_buffers
                if isinstance(buffer, editor.Editor)
            ],
            showfont.config(font=(value, 12)),
            state.defs.__setitem__(2, value),
        ],
    )
    f.grid(column=1, row=1, padx=10, pady=10, sticky="ew")
    ctk.Label(tft, text="Colours:").grid(column=0, row=2, padx=10, pady=10)
    colours = ctk.Textbox(tft, font=monospace, wrap="word", height=5)
    colours.insert(
        "end",
        str(state.theme)[:-1][1:].replace("state.defs[2]", "orgfont"),
    )
    colours.grid(column=0, row=3, sticky="nsew", padx=10, pady=10)
    pr.bind(
        "<Escape>",
        lambda event: [svprf(), utils.show("change / view preferences"), pr.destroy()],
    )
    tabs.add(et, text="Email")
    ctk.Label(et, text="Dictionaries:").pack(padx=10, pady=10, side="top", anchor="n")
    dictlist = ctk.Listbox(et)
    for dictionary in state.dicts:
        dictlist.insert("end", dictionary)
    dictlist.pack(fill="both", expand=True, padx=10, pady=10, anchor="center")
    ctk.Button(et, text="Remove", command=removedict).pack(
        fill="x", expand=True, padx=10, pady=10, side="left", anchor="sw"
    )
    ctk.Button(et, text="Add", command=adddict).pack(
        fill="x", expand=True, padx=10, pady=10, side="right", anchor="se"
    )
    ctk.Button(
        pr,
        text="OK",
        command=lambda: [
            svprf(),
            utils.show("change / view preferences"),
            pr.destroy(),
        ],
    ).pack(side="bottom", fill="x", padx=10, pady=10)
    pr.protocol(
        "WM_DELETE_WINDOW",
        lambda: [svprf(), utils.show("change / view preferences"), pr.destroy()],
    )
    for code in state.plgnsprf:
        try:
            exec(code[1], vars(state))
        except Exception as error:
            error = str(error)
            state.root.error(
                "Error!",
                f'There was an error in setting up the preferences of the plugin "{os.path.basename(os.path.normpath(code[0]))}":\n{error}',
                parent=pr,
            )
    utils.lock_window_size(pr)
    pr.focus()
    pycode.pcrunhook("after", "open-preferences")
