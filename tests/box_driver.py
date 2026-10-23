"""Drives the Alt-X box's prompts from a test, without ever hanging."""

import time

import state


def drive(root, function, actions, delay=20, timeout=10, **keywords):
    """Call function(**keywords), which prompts in the box, while the actions
    (functions of the box) run one at a time, each while a prompt is waiting.
    When the actions are used up the waiting prompt is ended. After timeout
    seconds every prompt is ended, so a test that does not get the prompt it
    expects fails instead of hanging."""
    pending = list(actions)
    deadline = time.monotonic() + timeout
    finished = []

    def step():
        if finished:
            return
        if time.monotonic() > deadline:
            state.prompting = False
        elif state.prompting:
            if pending:
                pending.pop(0)(state.cmdentry)
            else:
                state.prompting = False
        root.after(5, step)

    root.after(delay, step)
    try:
        return function(**keywords)
    finally:
        finished.append(True)
