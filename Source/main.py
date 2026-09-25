"""PyNotes' entry point. This is a top-to-bottom startup script rather
than a library of functions: parse command-line arguments (handling any
CLI-only mode that exits before the GUI, e.g. --version/--plugin-*),
bootstrap the Python environment and optional dependencies, start the
terminal console, build the root window/menus, load preferences, and
finally run any startup PyCode/commands and open the requested files
before handing control to the tkinter main loop at the very end."""

import os
import sys
import platform
import getpass
import subprocess
import shutil
import copy
import codecs
import base64
import keyword
import wave
import re
import threading
import queue
import ast
import warnings
import io
import time
import state
import urllib.request
import zipfile
import init
import utils
import dialogs
from cli import claht, clcht

# Pull init/utils/dialogs' top-level names straight into this module's
# namespace (so e.g. init.homedir can be used here as plain homedir),
# mirroring what's later done for the rest of PyNotes' own modules.
for _m in (init, utils, dialogs):
    globals().update({_k: _v for _k, _v in vars(_m).items() if not _k.startswith("__")})
del _m
from cli import argparse, start_console
from tkinter import messagebox as mb

state.options, state.files_to_open = argparse(
    {
        "version": False,
        "changes": False,
        "plugin-list-github": False,
        "plugin-list-installed": False,
        "no-load-pycode": False,
        "no-load-plugins": False,
        "pycode-exec": True,
        "command-exec": True,
        "help": False,
        "plugin-install": True,
        "plugin-remove": True,
        "plugin-describe": True,
        "wait-start": False,
    },
    sys.argv[1:],
)

# The changelog shown by --changes / the "What's new" menu item.
changelist = [
    "Added a live cli console inside the starting terminal which can interact with and control PyNotes while it runs! (See pynotes --help)\nNow PyNotes will run with Terminal=true even on linux.",
    "Removed tabs in the editor and made the Python shell and Email separate buffers.\nRemoved the Email HMode.\nCommands now make these new buffers or switch to already existing ones.",
    "Added reverse search and separated forward search from search from beginning.",
    "Added setattr and getattr commands to PyCode.",
    "Added a PyCode evaluator Alt-X command.",
    "Made a custom terminal cursor which lets it change shape and not move on mouse click, drag, etc.",
    "Fixed many bugs and implemented new ANSI codes and features in the terminal.",
    "Fixed upgrading ttkbootstrap from 1.x failing.",
    "Made the editor line number widget thinner.",
    "Made the LaTeX environment highlighting include the \\begin{env} line.",
    "Fixed a bug where the HMode would not change from PDF/PNG/Epub when opening a file or new file.",
    "Fixed some bugs.",
]
state.changestr = ""
for i in range(len(changelist) - 1):
    state.changestr += f"{i + 1}. {changelist[i]}\n\n"
state.changestr += f"{len(changelist)}. {changelist[-1]}"

# CLI-only modes below (--version, --changes, --plugin-*, --help) each
# print and exit(0/1) before anything GUI-related is touched, so at
# most one of them may be given.
if (
    sum(
        [
            bool(state.options[op])
            for op in (
                "version",
                "changes",
                "help",
                "plugin-list-github",
                "plugin-list-installed",
                "plugin-install",
                "plugin-describe",
                "wait-start",
            )
        ]
    )
    > 1
):
    print(
        f"error: cannot combine --version, --changes, --help, --plugin-list-github, --plugin-list-installed, --plugin-install, --plugin-describe, --wait-start arguments"
    )
    exit(1)
if state.options["version"]:
    print(f"This is PyNotes v{v}.")
    exit()
if state.options["changes"]:
    print(f"Changes in v{v}:\n" + state.changestr.replace("\n\n", "\n"))
    exit()
os.makedirs(f"{homedir}/.local/share/PyNotes/add-ons", exist_ok=True)
os.makedirs(f"{homedir}/.local/share/PyNotes/themes", exist_ok=True)
if state.options["plugin-list-github"]:
    try:
        plgns = (
            urllib.request.urlopen(
                "https://raw.githubusercontent.com/rafugafu/PyNotes/main/Plugins/list"
            )
            .read()
            .decode()
            .split("\n")
        )
        onelinedescplgns = (
            urllib.request.urlopen(
                "https://raw.githubusercontent.com/rafugafu/PyNotes/main/Plugins/onelinedescriptions"
            )
            .read()
            .decode()
            .split("\n")
        )
    except Exception as error:
        error = str(error)
        print(f"error in downloading plugin list: {error}")
        exit(1)
    installed = os.listdir(f"{homedir}/.local/share/PyNotes/add-ons")
    printstr = "Plugins currently on PyNotes GitHub:\n"
    for i in range(len(plgns) - 1):
        if plgns[i] in installed:
            printstr += "(Installed) "
        else:
            printstr += "(Not Installed) "
        printstr += plgns[i] + " - " + onelinedescplgns[i] + ".\n"
    if plgns[-1] in installed:
        printstr += "(Installed) "
    else:
        printstr += "(Not Installed) "
    printstr += plgns[-1] + " - " + onelinedescplgns[-1] + "."
    print(printstr)
    exit()
if state.options["plugin-list-installed"]:
    installed = os.listdir(f"{homedir}/.local/share/PyNotes/add-ons")
    if not installed:
        print("No plugins are installed.")
        exit()
    printstr = ""
    for i in range(len(installed) - 1):
        printstr += installed[i] + " - "
        if "onelinedescription" in os.listdir(
            f"{homedir}/.local/share/PyNotes/add-ons/{installed[i]}"
        ):
            printstr += (
                open(
                    f"{homedir}/.local/share/PyNotes/add-ons/{installed[i]}/onelinedescription",
                    "r",
                ).read()
                + ".\n"
            )
        else:
            printstr += "[description not provided]\n"
    printstr += installed[-1] + " - "
    if "onelinedescription" in os.listdir(
        f"{homedir}/.local/share/PyNotes/add-ons/{installed[-1]}"
    ):
        printstr += (
            open(
                f"{homedir}/.local/share/PyNotes/add-ons/{installed[-1]}/onelinedescription",
                "r",
            ).read()
            + "."
        )
    else:
        printstr += "[description not provided]"
    print(printstr)
    exit()
if state.options["plugin-describe"]:
    installed = os.listdir(f"{homedir}/.local/share/PyNotes/add-ons")
    printstr = f'Description of plugin \'{state.options["plugin-describe"]}\' '
    if state.options["plugin-describe"] in installed:
        printstr += "(installed):\n"
        if "fulldescription" not in os.listdir(
            f'{homedir}/.local/share/PyNotes/add-ons/{state.options["plugin-describe"]}'
        ):
            printstr += "[Not provided]"
        else:
            printstr += open(
                f'{homedir}/.local/share/PyNotes/add-ons/{state.options["plugin-describe"]}/fulldescription',
                "r",
            ).read()
    else:
        printstr += "(not installed):\n"
        try:
            plgns = (
                urllib.request.urlopen(
                    "https://raw.githubusercontent.com/rafugafu/PyNotes/main/Plugins/list"
                )
                .read()
                .decode()
                .split("\n")
            )
            fulldescplgns = (
                urllib.request.urlopen(
                    "https://raw.githubusercontent.com/rafugafu/PyNotes/main/Plugins/fulldescriptions"
                )
                .read()
                .decode()
                .split("\n==========\n")
            )
        except Exception as error:
            error = str(error)
            print(f"error in downloading plugin list: {error}")
            exit(1)
        if state.options["plugin-describe"] not in plgns:
            print(
                f'error: plugin \'{state.options["plugin-describe"]}\' is not installed and does not exist on the PyNotes GitHub.'
            )
            exit(1)
        printstr += fulldescplgns[plgns.index(state.options["plugin-describe"])]
    print(printstr)
    exit()
if state.options["plugin-install"]:
    try:
        plgns = (
            urllib.request.urlopen(
                "https://raw.githubusercontent.com/rafugafu/PyNotes/main/Plugins/list"
            )
            .read()
            .decode()
            .split("\n")
        )
    except Exception as error:
        error = str(error)
        print(f"error in downloading plugin list: {error}")
        exit(1)
    if state.options["plugin-install"] not in plgns:
        print(f'error: cannot find plugin \'{state.options["plugin-install"]}\'')
        exit(1)
    print("downloading plugin...", end="")
    try:
        plgn = urllib.request.urlopen(
            f'https://raw.githubusercontent.com/rafugafu/PyNotes/main/Plugins/{state.options["plugin-install"].replace(" ", "%20")}.zip'
        ).read()
    except Exception as error:
        error = str(error)
        print(f"\nerror in downloading plugin: {error}")
        exit(1)
    print(" done")
    print("extracting plugin...", end="")
    try:
        archive = io.BytesIO(plgn)
        zipfile.ZipFile(archive, "r").extractall(
            path=f"{homedir}/.local/share/PyNotes/add-ons/"
        )
    except Exception as error:
        error = str(error)
        print(f"\nerror in extracting plugin: {error}")
        exit(1)
    print(" done\n")
    print(f'Installed plugin \'{state.options["plugin-install"]}\'.')
    exit()
if state.options["plugin-remove"]:
    installed = os.listdir(f"{homedir}/.local/share/PyNotes/add-ons")
    if state.options["plugin-remove"] not in installed:
        print(f'error: plugin \'{state.options["plugin-remove"]}\' is not installed')
        exit(1)
    shutil.rmtree(
        f'{homedir}/.local/share/PyNotes/add-ons/{state.options["plugin-remove"]}'
    )
    print(f'Removed plugin \'{state.options["plugin-remove"]}\'.')
    exit()
if state.options["help"]:
    print(
        "\x1b[33mThis is help only for the command line interface of PyNotes. For help on PyNotes functions and features, open Help from within PyNotes itself.\x1b[0m\n"
        + claht
        + "\n"
        + clcht
    )
    exit()

# GUI startup begins here: make sure PyNotes' own venv is used (Linux),
# ensure ttkbootstrap itself is installed (needed even to show the
# "install this?" dialogs for every other optional dependency), then
# redirect stdout/stderr so the terminal is free for the console below.
import subprocess
from tkinter import messagebox as mb

if platform.system() == "Linux":
    if rootdir not in sys.path:
        sys.path.insert(0, rootdir)
if platform.system() == "Linux":
    os.environ["PATH"] = (
        f"{homedir}/.local/share/PyNotes/venv/bin:" + os.environ["PATH"]
    )
switchvenv()
try:
    import easytk

    assert tuple(map(int, easytk.ttk.__version__.split("."))) >= (2, 0, 0)
except Exception:
    if mb.askyesno(
        "Info",
        "The module 'ttkbootstrap' is not installed. PyNotes will not be able to run without this module. Should PyNotes install it locally?",
    ):
        subprocess.run([sys.executable, "-m", "pip", "install", "-U", "ttkbootstrap"])
    else:
        mb.showerror("Error!", "Quitting PyNotes.")
        exit(1)
    mb.showinfo("Info", "Restarting PyNotes.")
    os.execv(sys.executable, [sys.executable] + sys.argv)

# Save the real stdout/stderr fds, then redirect the process' own
# stdout/stderr to /dev/null: from here on, state.stdout/state.stderr
# (not print()/sys.stderr) are what actually reach the terminal, so
# they can be shared with the console below instead of colliding with
# whatever else PyNotes or its dependencies print.
state.stdout = os.fdopen(os.dup(1), "w")
state.stderr = os.fdopen(os.dup(2), "w")
devnullfd = os.open(os.devnull, os.O_WRONLY)
os.dup2(devnullfd, 1)
os.dup2(devnullfd, 2)
os.close(devnullfd)
state.consoleq = queue.Queue()
# state.started gates the rest of GUI startup below; with --wait-start
# it's only set once the console's own "start" command is typed, letting
# the user queue up command-exec/pycode-eval/open-file/extra-pycode
# console commands before anything actually launches.
state.started = threading.Event()
if not state.options["wait-start"]:
    state.started.set()
threading.Thread(target=start_console, args=(state.consoleq,), daemon=True).start()
if not state.options["wait-start"]:
    time.sleep(0.05)
    # Fake-echo "start" and its usual response, matching what the
    # console would print if the user had actually typed it themselves.
    print("start\n\r\x1b[32mstarting pynotes.\x1b[0m\n\r> ", end="", file=state.stdout)
state.started.wait()
if platform.system() != "Linux":
    fd = easytk.fd
# python_scope_build implements editor.py's Python-scope analysis
# (autocomplete, go-to-definition); these names are imported here too so
# they end up in vars(state) below, reachable from PyCode/plugin code
# the same way every other PyNotes module's globals are.
from python_scope_build import (
    _PYTHON_BUILTIN_MEMBERS,
    _PYTHON_BUILTIN_CALLABLE_PARAMS,
    _PYTHON_BUILTIN_CALLABLE_NAMES,
    _PYTHON_BUILTIN_NAMES,
    _PYTHON_BUILTIN_METHOD_RETURNS,
    _PythonScanCancelled,
    _PythonScopeBuilder,
    _python_method_has_implicit_first_param,
    _python_c3_linearize,
    _python_partial_target,
    _python_unwrap_descriptor,
    _python_import_fromlist_is_nonempty,
    _python_static_value_kind,
    _python_inspect_ast_members,
    _PythonModuleSpec,
    _python_resolve_toplevel_fs,
    _python_module_src_path,
    _python_relative_import_target,
)

init.ensure_dependencies()
file, new, defaultdefs = init.load_or_create_defs()
init_plugin, first_plugin, last_plugin = init.load_plugins(
    state.options["no-load-plugins"]
)
vars(state).update(globals())
# Run each plugin's "init" code now, before buffer/editor/etc. are even
# imported below, so it can populate state.buffer_init_functions and
# friends for those classes' bodies to pick up as they're defined.
for code in init_plugin:
    try:
        exec(code[1], vars(state))
    except Exception as error:
        error = str(error)
        info(
            "Error!",
            f'There was an error in initializing the plugin "{os.path.basename(os.path.normpath(code[0]))}":\n{error}',
        )
# Every optional dependency ensure_dependencies() just confirmed/installed.
import tika
from tika import parser
import pdfplumber
import pyttsx3 as stt
import matplotlib.pyplot as plt
import sympy
import sounddevice as sd
import speech_recognition as sr
import numpy as np
from tklinenums import TkLineNumbers
import ziamath
import cairosvg
from PIL import Image
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

if platform.system() != "Linux":
    from winpty import PtyProcess
# PyNotes' own modules, imported only now since several of them (e.g.
# buffer.py's Buffer class body) rely on state set up above, such as
# the just-run plugin "init" code's state.buffer_init_functions.
import buffer
import speech
import editor
import terminal
import pythonshell
import pynotesemail
import command
import pycode
import window
import help
import preferences

for _m in (
    buffer,
    speech,
    editor,
    terminal,
    pythonshell,
    pynotesemail,
    command,
    pycode,
    window,
    help,
    preferences,
):
    globals().update({_k: _v for _k, _v in vars(_m).items() if not _k.startswith("__")})
del _m
init.create_root_and_menus()
init.load_config(file, defaultdefs)
vars(state).update(globals())
# Plugin "first" code runs now that the root window/menus/preferences
# exist, so it can add its own menu entries, HModes, etc.
for code in first_plugin:
    try:
        exec(code[1], vars(state))
    except Exception as error:
        error = str(error)
        state.root.error(
            "Error!",
            f'There was an error in the first part of the plugin "{os.path.basename(os.path.normpath(code[0]))}":\n{error}',
        )
# Remaining core state PyNotes needs before any buffer can be created.
state._EDITOR_HL_SKIP_REMOVE_TAGS = {"sel", "marked", "found", "foundhighlight"}
state._PYTHON_SHELL_HL_SKIP_REMOVE_TAGS = {"sel", "prompt", "wrapcont"}
state.skiptags = {}
state.skiptagspythonshell = {}
state.plugin_hl = {}
state.engine = stt.init()
state.pcwrittencommands = {}
state.pcbeforehooks = {}
state.pcafterhooks = {}
state.cmdentry = state.root.textbox(
    state="disabled", height=1, bd=1, font=(monospace, 12)
)
state.cmdentry.pack(padx=10, pady=10, fill="x", anchor="n")
state.cmdautocomplete = state.root.textbox(
    state="disabled", bd=1, font=(monospace, 10), wrap="word"
)

# Populate every shared menu (state.fm, state.em, ...) each buffer type
# assembles its own menu bar from; see init.create_root_and_menus() and
# window.update_menus().
state.plgnm.add_command(label="Download From PyNotes' GitHub", command=dp)
state.plgnm.add_command(label="Open Plugins Directory", command=op)
state.plgnm.add_separator()
state.plgnm.add_command(label="Help with Adding Plugins", command=ap)
state.pm.add_command(label="Run → F5", command=lambda: state.active.rp())
state.lm.add_command(
    label="Run LuaLaTeX → F5", command=lambda: state.active.runtex("lua")
)
state.lm.add_command(label="Run PdfLaTeX", command=lambda: state.active.runtex("pdf"))
state.em.add_command(
    label="Undo → Ctrl + Z / Alt + X - u", command=lambda: state.active.undo()
)
state.em.add_command(
    label="Redo → Ctrl + Shift + Z / Alt + X - r", command=lambda: state.active.redo()
)
state.em.add_separator()
state.em.add_command(
    label="Copy selection → Ctrl + C / Alt + X - c",
    command=lambda: (
        state.active.cp()
        if hasattr(state.active, "cp")
        else show("cannot copy in current buffer")
    ),
)
state.em.add_command(
    label="Paste clipboard → Ctrl + V / Alt + X - p",
    command=lambda: (
        state.active.pst()
        if hasattr(state.active, "pst")
        else show("cannot paste in current buffer")
    ),
)
state.em.add_command(
    label="Cut selection → Ctrl + X / Alt + X - cut", command=lambda: state.active.cut()
)
state.em.add_separator()
state.em.add_command(
    label="Select all → Ctrl + A / Alt + X - a",
    command=lambda: (
        state.active.selall()
        if hasattr(state.active, "selall")
        else show("cannot select all in current buffer")
    ),
)
state.hm.add_command(label="About", command=abt)
state.hm.add_command(label=f"What's new in {v}?", command=changes)
state.hm.add_command(label="Help with commands → Alt + X - h", command=hx)
state.hm.add_command(label="Help with Email", command=hemail)
state.hm.add_command(label="Help with PyCode", command=helppycode)
state.hm.add_command(label="Help with MathGod", command=helpmathgod)
state.hm.add_command(label="Help with Adding Plugins", command=ap)
state.hm.add_separator()
state.hm.add_command(label="Recover backup", command=rb)
state.hmm.add_command(
    label="Normal → Alt + X - hmode:norm", command=lambda: pchmode("normal")
)
state.hmm.add_command(
    label="Python → Alt + X - hmode:py", command=lambda: pchmode("python")
)
state.hmm.add_command(
    label="LaTeX → Alt + X - hmode:la", command=lambda: pchmode("latex")
)
state.hmm.add_command(
    label="Markdown → Alt + X - hmode:md", command=lambda: pchmode("markdown")
)
state.hmm.add_command(
    label="HTML → Alt + X - hmode:html", command=lambda: pchmode("html")
)
state.hmm.add_separator()
for hmode in state.plgnhmodes:
    state.hmm.add_command(
        label=hmode + " → Alt + X - hmode:" + hmode, command=lambda: pchmode(hmode)
    )
state.tem.add_command(
    label="Copy → Ctrl + Shift + C / Alt + X - c",
    command=lambda: (
        state.active.cp()
        if hasattr(state.active, "cp")
        else show("cannot copy in current buffer")
    ),
)
state.tem.add_command(
    label="Paste → Ctrl + Shift + V / Alt + X - p",
    command=lambda: (
        state.active.pst()
        if hasattr(state.active, "pst")
        else show("cannot paste in current buffer")
    ),
)
state.tem.add_separator()
state.tem.add_command(
    label="Select All → Ctrl + Shift + A / Alt + X - a",
    command=lambda: (
        state.active.selall()
        if hasattr(state.active, "selall")
        else show("cannot select all in current buffer")
    ),
)
state.fm.add_command(
    label="New → Ctrl + N / Alt + X - n",
    command=lambda: (
        state.active.nw()
        if hasattr(state.active, "nw")
        else show("cannot open new file in current buffer")
    ),
)
state.fm.add_command(
    label="New Editor Horizontal → Ctrl + Shift + N / Alt + X - neh",
    command=lambda: neweditor(orient="horizontal"),
)
state.fm.add_command(
    label="New Editor Vertical → Alt + X - nev",
    command=lambda: neweditor(orient="vertical"),
)
state.fm.add_command(
    label="Open → Ctrl + O / Alt + X - o",
    command=lambda: (
        state.active.llld()
        if hasattr(state.active, "llld")
        else show("cannot open file in current buffer")
    ),
)
state.fm.add_command(
    label="Open in New Editor Horizontal → Ctrl + Shift + O / Alt + X - onh",
    command=lambda: neweditor(True),
)
state.fm.add_command(
    label="Open in New Editor Vertical → Alt + X - onv",
    command=lambda: neweditor(True, "vertical"),
)
state.fm.add_separator()
state.fm.add_command(
    label="Save → Ctrl + S / Alt + X - s",
    command=lambda: (
        state.active.sssv()
        if hasattr(state.active, "sssv")
        else show("cannot save file in current buffer")
    ),
)
state.fm.add_command(
    label="Save As → Ctrl + Shift + S / Alt + X - sa",
    command=lambda: (
        state.active.ssv()
        if hasattr(state.active, "ssv")
        else show("cannot save file in current buffer")
    ),
)
state.fm.add_separator()
state.fm.add_command(label="Switch Buffer → Alt + X - sw", command=setactive)
state.fm.add_command(
    label="Close Current Buffer → Ctrl + W / Alt + X - cb", command=pcclosebuff
)
state.fm.add_separator()
state.fm.add_command(label="Quit PyNotes → Ctrl + Q / Alt + X - e", command=ext)
state.pcm.add_command(label="Start", command=pc)
state.pcm.add_separator()
state.pcm.add_command(label="Help", command=helppycode)
state.om.add_command(label="Preferences → Alt + X - prf", command=prf)
state.om.add_command(
    label="Open PyNotes Source Code → Alt + X - source-code", command=ss
)
state.om.add_separator()
state.om.add_command(
    label="Go to line → Alt + L / Alt + X - gl",
    command=lambda: (
        state.active.gl() if isinstance(state.active, Editor) else show("not an editor")
    ),
)
state.om.add_command(
    label="Page turn forward → Ctrl + P / Alt + X - pf",
    command=lambda: state.active.ptf(),
)
state.om.add_command(
    label="Page turn backward → Ctrl + Shift + P / Alt + X - pb",
    command=lambda: state.active.ptb(),
)
state.om.add_separator()
state.om.add_command(label="Command → Alt + X", command=cmd)
state.om.add_command(label="PyCode → Alt + X - pc", command=pc)
state.om.add_separator()
state.em.add_command(
    label="Find → Ctrl + F / Alt + X - f", command=lambda: state.active.f()
)
state.em.add_command(
    label="Find & Replace → Ctrl + Shift + F / Alt + X - fr",
    command=lambda: state.active.fr(),
)
# Build the combined email spellcheck word list from every configured
# dictionary file (see preferences.py's Email tab).
state.emailwordlist = []
try:
    for dictionary in state.dicts:
        if dictionary:
            state.emailwordlist.extend(
                open(dictionary, "r", encoding="utf-8").read().split("\n")
            )
except Exception as error:
    error = str(error)
    state.root.error("Error", error)
state.om.add_command(label="Terminal → Alt + X - t", command=term)
state.om.add_command(label="Python Shell → Alt + X - pyshell", command=openpythonshell)
state.om.add_separator()
state.om.add_command(label="Email → Alt + X - sendemail", command=openemailbuf)
state.om.add_separator()
state.om.add_command(label="Speech to Text → Alt + X - st", command=st)
state.om.add_command(
    label="Speak Text → Alt + X - sp", command=lambda: state.active.spk()
)
state.root.protocol("WM_DELETE_WINDOW", ext)
state.mg.add_command(label="Start", command=mathgod)
state.mg.add_separator()
state.mg.add_command(label="Help", command=helpmathgod)
# state.wholenewwords tracks PyCode `bind` keybindings so they can be
# cleared/rebuilt on every (re)compile of PyCode source, in pcread()
# (see pycode.py); merge each plugin's own PyCode commands into the
# same translation table as PyCode's built-in ones so they're parsed
# identically.
state.wholenewwords = []
for command in state.plgnpccmds:
    pycodetopythoncommands[command] = state.plgnpccmds[command][1]
state.pycode_keybindings_cdt = ""
state._open_terminal_closers = []
state.all_buffers = []
state.buffindex = -1
# The pane layout every buffer is added into: an outer vertical
# splitter (state.vertical) whose panes stack top to bottom, containing
# one inner horizontal splitter (state.horizontal, itself one of
# state.vertical's panes) whose panes sit side by side. A buffer opened
# with orient="vertical" becomes another top-level pane of state.vertical
# directly; orient="horizontal" adds it into state.horizontal instead.
state.vertical = easytk.ttk.Panedwindow(state.root, orient="vertical")
state.vertical.pack(side="bottom", fill="both", expand=True)
state.horizontal = easytk.ttk.Panedwindow(state.vertical, orient="horizontal")
state.vertical.add(state.horizontal)
# Widening the pane divider (sash) is a ttk style setting, which a
# theme switch resets, so it's reapplied via <<ThemeChanged>> too.
state.sashconfig = lambda: [
    state.root.style().configure("Sash", sashthickness=15, relief="raised")
]
state.active = None
state.sashconfig()
state.root.bind("<<ThemeChanged>>", lambda event: state.sashconfig())
state._resize_after_id = None
state._last_root_size = (state.root.winfo_width(), state.root.winfo_height())
# Global keybindings, active regardless of which buffer has focus.
bindrecur(state.root, "<Alt-x>", lambda event: cmd())
bindrecur(state.root, "<Control-N>", lambda event: neweditor())
bindrecur(state.root, "<Control-O>", lambda event: neweditor(True))
bindrecur(state.root, "<Control-q>", lambda event: ext())
state.root.bind("<Configure>", _on_root_resize)
neweditor()
if state.defs[3] in state.root.themes():
    state.root.style(state.defs[3])
else:
    state.root.style("bootstrap-light")
vars(state).update(globals())
# Load the user's ~/.pynotes PyCode config (unless --no-load-pycode),
# append --pycode-exec if given, and run the result, one statement per
# line so one bad line doesn't stop the rest from running.
pycodecode = ""
if not state.options["no-load-pycode"]:
    pycodecode += open(f"{homedir}/.pynotes", "r", encoding="utf-8").read()
if state.options["pycode-exec"]:
    if pycodecode:
        pycodecode += ";"
    pycodecode += state.options["pycode-exec"]
try:
    pycodestartupcdt = pcread(pycodecode)
except Exception:
    pass
else:
    for line in pycodestartupcdt.split("\n"):
        try:
            exec(line, vars(state))
        except Exception as error:
            error = str(error)
            state.root.error("Error", f"Error in PyCode: {error}")
if state.options["command-exec"]:
    cmdrun(state.options["command-exec"])
# Plugin "last" code runs once startup is otherwise complete.
for code in last_plugin:
    try:
        exec(code[1], vars(state))
    except Exception as error:
        error = str(error)
        state.root.error(
            "Error!",
            f'There was an error in the last part of the plugin "{os.path.basename(os.path.normpath(code[0]))}":\n{error}',
        )
# Load the first requested file into the already-open blank editor
# from neweditor() above, and open the rest each in their own editor.
if state.files_to_open:
    state.all_buffers[0].ld(state.files_to_open.pop(0))
for file in state.files_to_open:
    neweditor(file)
if new:
    prf()


def consoleexec(task):
    """Run a task queued by the console thread (see cli.py's Console)
    on the GUI thread; task is one of the (name, ...) tuples the console
    commands put on state.consoleq."""
    if task[0] == "command-exec":
        cmdrun(task[1])
    elif task[0] == "pycode-eval":
        try:
            translated = pycode.pycodeindex(task[1])
            if translated:
                exec(translated, vars(state))
            else:
                utils.show("invalid pycode expression")
                return
        except Exception as error:
            error = str(error)
            state.root.error("Error", f"Error in PyCode: {error}")
        utils.show("evaluated pycode expression")
    elif task[0] == "open-file":
        neweditor(task[1])
    elif task[0] == "close":
        ext()
    state.root.update()
    if hasattr(state.active, "keypress"):
        state.active.keypress()


def consoleqempty():
    """Drain and run every task currently queued on state.consoleq, then
    reschedule itself 200ms later. Runs on the GUI thread (via
    state.root.after) so it's safe for consoleexec() to touch widgets,
    even though tasks are queued from the console's own thread."""
    while True:
        try:
            task = state.consoleq.get_nowait()
            consoleexec(task)
            state.consoleq.task_done()
        except Exception:
            break
    state.consoleqafter = state.root.after(200, consoleqempty)


state.consoleqafter = state.root.after(200, consoleqempty)
# Hand off to tkinter; everything from here on runs from GUI callbacks.
state.root.show()
