import importlib
import os
import sys
import tkinter as tk
from unittest.mock import MagicMock

import pytest

# Optional third-party packages that are only used by features the tests do
# not exercise (PDF reading, file watching, speech). Where one is not
# installed, an empty stand-in lets the PyNotes modules that import it load.
# Setting PYNOTES_REQUIRE_OPTIONAL_PACKAGES (as the CI does) makes a missing
# package an error instead.
_OPTIONAL_PACKAGE_STAND_INS = {
    "tika": ("parser",),
    "pdfplumber": (),
    "pyttsx3": (),
    "sounddevice": (),
    "speech_recognition": (),
    "watchdog": ("observers", "events"),
}


def _install_optional_package_stand_ins():
    for package, submodules in _OPTIONAL_PACKAGE_STAND_INS.items():
        try:
            importlib.import_module(package)
            continue
        except ImportError:
            if os.environ.get("PYNOTES_REQUIRE_OPTIONAL_PACKAGES"):
                raise
        stand_in = MagicMock(name=package)
        stand_in.__path__ = []
        sys.modules[package] = stand_in
        for submodule in submodules:
            sys.modules[f"{package}.{submodule}"] = MagicMock(
                name=f"{package}.{submodule}"
            )
    if isinstance(sys.modules.get("watchdog.events"), MagicMock):
        sys.modules["watchdog.events"].FileSystemEventHandler = type(
            "FileSystemEventHandler", (), {}
        )


_install_optional_package_stand_ins()

import state


def pytest_configure(config):
    # Normally set by init.load_plugins() before buffer.py is imported.
    for name, value in (
        ("plgncmds", {}),
        ("plgnhmodes", {}),
        ("plgnpccmds", {}),
        ("plgnsprf", []),
        ("plgnscmdhelp", ""),
        ("plgnspccmdhelp", ""),
    ):
        if not hasattr(state, name):
            setattr(state, name, value)
    for name in (
        "buffer_init_code",
        "buffer_init_functions",
        "editor_init_code",
        "editor_init_functions",
    ):
        if not hasattr(state, name):
            setattr(state, name, [])


@pytest.fixture(scope="session")
def tk_root():
    """One withdrawn PyNotes window for the whole run: it never maps a window,
    so nothing appears on screen."""
    import window

    try:
        root = window.pynoteswindow()
    except tk.TclError as error:
        pytest.skip(f"no display available: {error}")
    root.withdraw()
    state.root = root
    yield root
    del state.root
    root.destroy()


@pytest.fixture(autouse=True)
def fresh_application_state(monkeypatch):
    """The defaults main.py and init.py give the shared state module at startup."""
    monkeypatch.setattr(state, "_open_terminal_closers", [], raising=False)
    monkeypatch.setattr(state, "prompting", False, raising=False)


@pytest.fixture
def app(tk_root, tmp_path, monkeypatch):
    """The application state of a started PyNotes on the withdrawn root."""
    import application

    application_ = application.boot_application(tk_root, tmp_path / "home", monkeypatch)
    yield application_
    application_.cleanup()
