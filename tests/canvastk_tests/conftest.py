"""Shared fixtures for the canvastk tests.

Most of these tests create real, shown windows (the ones that measure sizes
need a mapped window), so they are skipped unless they run on a virtual
display, which keeps them off the screen of whoever runs the tests:

    xvfb-run -a python -m pytest tests/canvastk_tests

or PYNOTES_ALLOW_VISIBLE_WINDOWS=1 says that showing windows is fine.
Without a display at all, the tests that need one are skipped, so the
pure-logic tests (colors, file dialog helpers, theme dictionaries) also run on
their own.
"""

import os
import tkinter as tk

import pytest

import canvastk as ctk

ALLOWED = bool(os.environ.get("PYNOTES_ALLOW_VISIBLE_WINDOWS"))


def _display_works():
    """Whether a Tk window can be created at all."""
    try:
        probe = tk.Tk()
    except tk.TclError:
        return False
    probe.destroy()
    return True


_HAS_DISPLAY = ALLOWED and _display_works()


def pytest_collection_modifyitems(config, items):
    """Skip the tests that use the `root` fixture unless windows may be shown
    and there is a display."""
    if _HAS_DISPLAY:
        return
    reason = (
        "needs a Tk display"
        if ALLOWED
        else "shows windows: run under xvfb-run or set "
        "PYNOTES_ALLOW_VISIBLE_WINDOWS=1"
    )
    skip = pytest.mark.skip(reason=reason)
    for item in items:
        if "root" in item.fixturenames and "canvastk_tests" in str(item.fspath):
            item.add_marker(skip)


@pytest.fixture(autouse=True)
def clean_application_theme():
    """Every test starts and ends with the default application theme and mode."""
    ctk.reset_theme()
    ctk.set_appearance_mode("light")
    yield
    ctk.reset_theme()
    ctk.set_appearance_mode("light")


@pytest.fixture
def root():
    """A shown window (the tests that measure sizes need a mapped window)."""
    window = ctk.Window()
    window.geometry("700x500+0+0")
    window.update()
    yield window
    for child in list(window.winfo_children()):
        try:
            child.destroy()
        except tk.TclError:
            pass
    window.destroy()
