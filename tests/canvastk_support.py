"""Helpers shared by the canvastk tests."""


def settle(widget, rounds=3):
    """Run the pending idle callbacks (redraws, measurements) a few times."""
    for _ in range(rounds):
        widget.update_idletasks()
        widget.update()
