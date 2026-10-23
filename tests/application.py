"""Starts PyNotes' shared application state the way main.py does, minus what
needs a user or the outside world: the command line, the terminal console,
the dependency check, the plugins, the menu entries, and the main loop.

The root window is the real pynoteswindow, withdrawn, so nothing is shown.
Its dialogs (ask, info, error, warning, askstring) are replaced by scripted
ones that record what was asked, so a test decides the answers and nothing
ever blocks on a dialog. The home directory is a temporary one, so nothing
of the user's is read or written.
"""

import queue
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import state

SOURCE_DIRECTORY = Path(__file__).resolve().parent.parent / "Source"
MODULES_WITH_A_HOME_DIRECTORY = (
    "init",
    "utils",
    "dialogs",
    "preferences",
    "pynotesemail",
    "window",
    "help",
    "pycode",
    "editor",
)
# The modules whose names main.py puts in the state module, in its order,
# so PyCode and the plugins can reach them as plain names.
MODULES_SHARED_THROUGH_STATE = (
    "init",
    "utils",
    "dialogs",
    "buffer",
    "speech",
    "editor",
    "terminal",
    "pythonshell",
    "pynotesemail",
    "command",
    "pycode",
    "window",
    "help",
    "preferences",
)
UNANSWERED = object()


class ScriptedDialogs:
    """Stands in for the root window's dialogs. Every call is recorded in
    calls as (kind, title, message); the answers come from answers[kind], a
    queue filled with answer(kind, value), or are `default` when it is empty.
    """

    KINDS = ("ask", "askstring", "info", "error", "warning")

    def __init__(self, root):
        self.calls = []
        self.answers = {kind: queue.Queue() for kind in self.KINDS}
        self.defaults = {
            "ask": None,
            "askstring": "",
            "info": None,
            "error": None,
            "warning": None,
        }
        for kind in self.KINDS:
            setattr(root, kind, self._make(kind))

    def _make(self, kind):
        def dialog(title, message, *arguments, **keywords):
            self.calls.append((kind, title, message))
            try:
                return self.answers[kind].get_nowait()
            except queue.Empty:
                return self.defaults[kind]

        return dialog

    def answer(self, kind, *values):
        for value in values:
            self.answers[kind].put(value)

    def of_kind(self, kind):
        return [call for call in self.calls if call[0] == kind]

    def messages(self, kind):
        return [message for _, _, message in self.of_kind(kind)]


class ConsoleStandIn:
    """The terminal console, which is not running."""

    def __getattr__(self, name):
        return lambda *arguments, **keywords: None


def boot_application(root, home, monkeypatch):
    """Set up the shared state on root with home as the home directory.
    Returns the object the tests drive: its dialogs, and a cleanup function.
    """
    import canvastk as ctk
    import init
    import utils

    config_directory = home / ".local" / "share" / "PyNotes"
    (config_directory / "add-ons").mkdir(parents=True)
    (config_directory / "themes").mkdir(parents=True)
    for name in MODULES_WITH_A_HOME_DIRECTORY:
        module = sys.modules.get(name) or __import__(name)
        monkeypatch.setattr(module, "homedir", str(home), raising=False)
    # The installed PyNotes directory (where the icon and the images are) is the
    # Source directory here. Every module that copied it from init is changed,
    # as a copy keeps the old value.
    for name in ("init", "utils", "help"):
        module = sys.modules.get(name) or __import__(name)
        monkeypatch.setattr(module, "rootdir", str(SOURCE_DIRECTORY))
    monkeypatch.setattr(sys, "stderr", sys.stderr)
    saved_state = dict(vars(state))
    children_before = set(root.winfo_children())

    dialogs = ScriptedDialogs(root)
    import dialogs as dialogs_module

    # The file dialogs are real windows; unless a test chooses a file, they
    # are cancelled.
    real_file_dialogs = {
        name: getattr(dialogs_module, name) for name in ("openfileget", "saveasfileget")
    }
    for name in real_file_dialogs:
        monkeypatch.setattr(dialogs_module, name, lambda *arguments, **keywords: "")
    init.load_plugins(True)
    import window

    monkeypatch.setattr(window, "pynoteswindow", lambda: root)
    with monkeypatch.context() as welcome:
        welcome.setattr(init, "info", lambda *arguments, **keywords: None)
        file, new, default_defs = init.load_or_create_defs()
    init.setup_app()
    init.load_config(file, default_defs)
    state.console = ConsoleStandIn()

    import python_scope_build

    for name in MODULES_SHARED_THROUGH_STATE:
        module = __import__(name)
        vars(state).update(
            {
                key: value
                for key, value in vars(module).items()
                if not key.startswith("__")
            }
        )
    vars(state).update(
        {
            key: value
            for key, value in vars(python_scope_build).items()
            if key.startswith("_PYTHON") or key.startswith("_python")
        }
    )
    state.state = state
    import cursortextbox

    state._EDITOR_HL_SKIP_REMOVE_TAGS = {
        "sel",
        "marked",
        "found",
        "foundhighlight",
        "overscroll",
        "bracket_matched",
        "bracket_unmatched",
    }
    state._PYTHON_SHELL_HL_SKIP_REMOVE_TAGS = {"sel", "prompt", "wrapcont"}
    state.skiptags = {}
    state.skiptagspythonshell = {}
    state.plugin_hl = {}
    state.engine = MagicMock()
    state.pcwrittencommands = {}
    state.pcbeforehooks = {}
    state.pcafterhooks = {}
    state.cmdentry = utils.EnabledLookCursorTextbox(
        root,
        state="disabled",
        height=1,
        font=(init.monospace, 12),
        cursor_shape=cursortextbox.CURSOR_SHAPES[state.curcurtype],
    )
    state.cmdentry.pack(padx=10, pady=10, fill="x", anchor="n")
    state.cmdautocomplete = utils.EnabledLookCursorTextbox(
        root, state="disabled", font=(init.monospace, 10), wrap="word"
    )
    state.emailwordlist = []
    state.wholenewwords = []
    state.pycode_keybindings_cdt = []
    state.pckeybindings = []
    state.pckeyactions = []
    state.pcdeferkeybindings = False
    state._open_terminal_closers = []
    state.all_buffers = []
    state.buffindex = -1
    state.panes = ctk.GridPanedwindow(root, draggable=True)
    state.panes.pack(side="bottom", fill="both", expand=True)
    state.active = None
    state._resize_after_id = None
    state._last_root_size = (root.winfo_width(), root.winfo_height())
    state.options = {}
    state.files_to_open = []

    def cleanup():
        for buffer in list(state.all_buffers):
            try:
                buffer.destroy()
            except Exception:
                pass
        for child in set(root.winfo_children()) - children_before:
            try:
                child.destroy()
            except Exception:
                pass
        for name in (
            "deiconify",
            "ask",
            "askstring",
            "info",
            "error",
            "warning",
        ):
            root.__dict__.pop(name, None)
        if root.theme not in (None, "Default"):
            try:
                root.settheme("Default")
            except Exception:
                pass
        vars(state).clear()
        vars(state).update(saved_state)

    return SimpleNamespace(
        dialogs=dialogs,
        cleanup=cleanup,
        home=home,
        new=new,
        real_file_dialogs=real_file_dialogs,
    )
