"""Color themes and a custom theme creator for PyNotes
using canvastk.
"""

import canvastk as ctk
from canvastk.colorchooser import askcolor
import tkinter as tk
import copy

# Built-in themes. Restored on error in loading user themes
ORIGINAL_THEMES = [
    # Light themes
    {
        "Default": {},
        "Light": {
            "accent": "#007AFF",
            "text": "#000000",
            "window": "#FFFFFF",
            "neutral": "#F2F2F7",
            "surface": "#F9F9F9",
            "surface_disabled": "#E5E5EA",
            "border": "#D1D1D6",
            "track": "#E5E5EA",
            "thumb": "#C7C7CC",
            "accent_hover": "#0063CC",
            "accent_press": "#0051A8",
            "accent_text": "#FFFFFF",
            "selection": "#B3D7FF",
            "selection_text": "#000000",
            "row_current": "#E5F1FF",
            "text_muted": "#8E8E93",
            "text_disabled": "#AEAEB2",
            "surface_hover": "#EFEFEF",
            "neutral_hover": "#E5E5EA",
            "thumb_hover": "#A1A1A6",
            "tooltip": "#F2F2F7",
            "button_border": "#C7C7CC",
            "focus_ring": "#007AFF",
            "separator": "#E5E5EA",
            "danger": "#FF3B30",
        },
        "Catppuccin Latte": {
            "accent": "#1E66F5",
            "text": "#4C4F69",
            "window": "#EFF1F5",
            "neutral": "#E6E9EF",
            "surface": "#CCD0DA",
            "surface_disabled": "#BCC0CC",
            "border": "#BCC0CC",
            "track": "#E6E9EF",
            "thumb": "#9CA0B0",
            "accent_hover": "#1752D7",
            "accent_press": "#123FB2",
            "accent_text": "#EFF1F5",
            "selection": "#DC8A78",
            "selection_text": "#4C4F69",
            "row_current": "#DCE0E8",
            "text_muted": "#7C7F93",
            "text_disabled": "#9CA0B0",
            "surface_hover": "#BCC0CC",
            "neutral_hover": "#DCE0E8",
            "thumb_hover": "#8C90A0",
            "tooltip": "#E6E9EF",
            "button_border": "#BCC0CC",
            "focus_ring": "#1E66F5",
            "separator": "#BCC0CC",
            "danger": "#D20F39",
        },
        "GitHub Light": {
            "accent": "#0969DA",
            "text": "#24292F",
            "window": "#F6F8FA",
            "neutral": "#F3F4F6",
            "surface": "#FFFFFF",
            "surface_disabled": "#F6F8FA",
            "border": "#D0D7DE",
            "track": "#EAEEF2",
            "thumb": "#D0D7DE",
            "accent_hover": "#0550AE",
            "accent_press": "#033D83",
            "accent_text": "#FFFFFF",
            "selection": "#ADD6FF",
            "selection_text": "#24292F",
            "row_current": "#F2F7FE",
            "text_muted": "#57606A",
            "text_disabled": "#8C95A0",
            "surface_hover": "#F6F8FA",
            "neutral_hover": "#EAEEF2",
            "thumb_hover": "#AFB8C1",
            "tooltip": "#F3F4F6",
            "button_border": "#D0D7DE",
            "focus_ring": "#0969DA",
            "separator": "#D0D7DE",
            "danger": "#CF222E",
        },
        "One Light": {
            "accent": "#4078F2",
            "text": "#383A42",
            "window": "#FAFAFA",
            "neutral": "#EAEAEB",
            "surface": "#FFFFFF",
            "surface_disabled": "#F0F0F1",
            "border": "#D3D3D4",
            "track": "#EAEAEB",
            "thumb": "#C8C8C9",
            "accent_hover": "#275EC8",
            "accent_press": "#1B449C",
            "accent_text": "#FFFFFF",
            "selection": "#E5E5E6",
            "selection_text": "#383A42",
            "row_current": "#E0E8F9",
            "text_muted": "#A0A1A7",
            "text_disabled": "#C8C8C9",
            "surface_hover": "#F0F0F1",
            "neutral_hover": "#E5E5E6",
            "thumb_hover": "#B6B6B7",
            "tooltip": "#EAEAEB",
            "button_border": "#D3D3D4",
            "focus_ring": "#4078F2",
            "separator": "#E0E0E2",
            "danger": "#E45649",
        },
        "Ayu Light": {
            "accent": "#F29718",
            "text": "#5C6773",
            "window": "#FAFAFA",
            "neutral": "#F3F4F5",
            "surface": "#FFFFFF",
            "surface_disabled": "#F0F1F2",
            "border": "#E6E8EA",
            "track": "#F3F4F5",
            "thumb": "#CDD0D3",
            "accent_hover": "#D9800F",
            "accent_press": "#B36605",
            "accent_text": "#FFFFFF",
            "selection": "#E2E4E7",
            "selection_text": "#5C6773",
            "row_current": "#FEF4E6",
            "text_muted": "#ABB2BF",
            "text_disabled": "#CDD0D3",
            "surface_hover": "#F0F1F2",
            "neutral_hover": "#E6E8EA",
            "thumb_hover": "#B8BCBF",
            "tooltip": "#F3F4F5",
            "button_border": "#E6E8EA",
            "focus_ring": "#F29718",
            "separator": "#E6E8EA",
            "danger": "#FF3333",
        },
        "Tokyo Night Day": {
            "accent": "#385EAE",
            "text": "#3760BF",
            "window": "#E1E2E7",
            "neutral": "#D5D6DB",
            "surface": "#F2F3F5",
            "surface_disabled": "#E9EAEF",
            "border": "#B4B5BC",
            "track": "#D5D6DB",
            "thumb": "#B4B5BC",
            "accent_hover": "#2B4C91",
            "accent_press": "#203A70",
            "accent_text": "#E1E2E7",
            "selection": "#CCD1E4",
            "selection_text": "#3760BF",
            "row_current": "#E9EDFA",
            "text_muted": "#8A91A5",
            "text_disabled": "#B4B5BC",
            "surface_hover": "#E9EAEF",
            "neutral_hover": "#CCD1E4",
            "thumb_hover": "#9EA0A9",
            "tooltip": "#D5D6DB",
            "button_border": "#B4B5BC",
            "focus_ring": "#385EAE",
            "separator": "#B4B5BC",
            "danger": "#F52A65",
        },
        "Solarized Light": {
            "accent": "#268BD2",
            "text": "#586E75",
            "window": "#FDF6E3",
            "neutral": "#EEE8D5",
            "surface": "#FDF6E3",
            "surface_disabled": "#EAE3CE",
            "border": "#93A1A1",
            "track": "#EEE8D5",
            "thumb": "#93A1A1",
            "accent_hover": "#1A6FAA",
            "accent_press": "#135482",
            "accent_text": "#FDF6E3",
            "selection": "#EEE8D5",
            "selection_text": "#073642",
            "row_current": "#E7E4D3",
            "text_muted": "#93A1A1",
            "text_disabled": "#A8B5B5",
            "surface_hover": "#EEE8D5",
            "neutral_hover": "#E4DDCA",
            "thumb_hover": "#586E75",
            "tooltip": "#EEE8D5",
            "button_border": "#93A1A1",
            "focus_ring": "#268BD2",
            "separator": "#93A1A1",
            "danger": "#DC322F",
        },
        "Gruvbox Light": {
            "accent": "#AF3A03",
            "text": "#3C3836",
            "window": "#FBF1C7",
            "neutral": "#EBDBB2",
            "surface": "#FBF1C7",
            "surface_disabled": "#EADBB2",
            "border": "#A89984",
            "track": "#EBDBB2",
            "thumb": "#A89984",
            "accent_hover": "#8F2F02",
            "accent_press": "#6F2401",
            "accent_text": "#FBF1C7",
            "selection": "#EBDBB2",
            "selection_text": "#282828",
            "row_current": "#F4E7BF",
            "text_muted": "#7C6F64",
            "text_disabled": "#A89984",
            "surface_hover": "#EBDBB2",
            "neutral_hover": "#DFD0A6",
            "thumb_hover": "#7C6F64",
            "tooltip": "#EBDBB2",
            "button_border": "#A89984",
            "focus_ring": "#AF3A03",
            "separator": "#A89984",
            "danger": "#9D0006",
        },
        "Material Light": {
            "accent": "#00BCD4",
            "text": "#212121",
            "window": "#FAFAFA",
            "neutral": "#F5F5F5",
            "surface": "#FFFFFF",
            "surface_disabled": "#EEEEEE",
            "border": "#E0E0E0",
            "track": "#F5F5F5",
            "thumb": "#BDBDBD",
            "accent_hover": "#00ACC1",
            "accent_press": "#0097A7",
            "accent_text": "#FFFFFF",
            "selection": "#E0F7FA",
            "selection_text": "#006064",
            "row_current": "#E0F7FA",
            "text_muted": "#757575",
            "text_disabled": "#BDBDBD",
            "surface_hover": "#F5F5F5",
            "neutral_hover": "#EEEEEE",
            "thumb_hover": "#9E9E9E",
            "tooltip": "#F5F5F5",
            "button_border": "#E0E0E0",
            "focus_ring": "#00BCD4",
            "separator": "#E0E0E0",
            "danger": "#F44336",
        },
        "Sepia": {
            "accent": "#8B5A2B",
            "text": "#433422",
            "window": "#F4ECD8",
            "neutral": "#E6DAB8",
            "surface": "#FAF4E8",
            "surface_disabled": "#DFD3B0",
            "border": "#C2B28F",
            "track": "#E6DAB8",
            "thumb": "#C2B28F",
            "accent_hover": "#704822",
            "accent_press": "#56371A",
            "accent_text": "#F4ECD8",
            "selection": "#E6DAB8",
            "selection_text": "#2B1D0C",
            "row_current": "#EEDFB8",
            "text_muted": "#8A7960",
            "text_disabled": "#C2B28F",
            "surface_hover": "#E6DAB8",
            "neutral_hover": "#DCCFAD",
            "thumb_hover": "#A89977",
            "tooltip": "#E6DAB8",
            "button_border": "#C2B28F",
            "focus_ring": "#8B5A2B",
            "separator": "#C2B28F",
            "danger": "#A52A2A",
        },
    },
    # Dark themes
    {
        "Dark": {
            "accent": "#0A84FF",
            "text": "#FFFFFF",
            "window": "#121212",
            "neutral": "#1C1C1E",
            "surface": "#2C2C2E",
            "surface_disabled": "#1C1C1E",
            "border": "#3A3A3C",
            "track": "#1C1C1E",
            "thumb": "#48484A",
            "accent_hover": "#2693FF",
            "accent_press": "#0073E6",
            "accent_text": "#FFFFFF",
            "selection": "#264F78",
            "selection_text": "#FFFFFF",
            "row_current": "#1A334D",
            "text_muted": "#8E8E93",
            "text_disabled": "#48484A",
            "surface_hover": "#3A3A3C",
            "neutral_hover": "#2C2C2E",
            "thumb_hover": "#636366",
            "tooltip": "#1C1C1E",
            "button_border": "#3A3A3C",
            "focus_ring": "#0A84FF",
            "separator": "#2C2C2E",
            "danger": "#FF453A",
        },
        "Catppuccin Macchiato": {
            "accent": "#8AADF4",
            "text": "#CAD3F5",
            "window": "#24273A",
            "neutral": "#1E2030",
            "surface": "#363A4F",
            "surface_disabled": "#1E2030",
            "border": "#494D64",
            "track": "#1E2030",
            "thumb": "#5B6078",
            "accent_hover": "#9BB9F6",
            "accent_press": "#79A1F2",
            "accent_text": "#24273A",
            "selection": "#5B6078",
            "selection_text": "#CAD3F5",
            "row_current": "#2E3B5B",
            "text_muted": "#939AB7",
            "text_disabled": "#5B6078",
            "surface_hover": "#494D64",
            "neutral_hover": "#25283D",
            "thumb_hover": "#6E738D",
            "tooltip": "#1E2030",
            "button_border": "#494D64",
            "focus_ring": "#8AADF4",
            "separator": "#494D64",
            "danger": "#ED8796",
        },
        "Tokyo Night": {
            "accent": "#7AA2F7",
            "text": "#A9B1D6",
            "window": "#1A1B26",
            "neutral": "#16161E",
            "surface": "#24283B",
            "surface_disabled": "#16161E",
            "border": "#383E5A",
            "track": "#16161E",
            "thumb": "#4E5579",
            "accent_hover": "#8FB3F9",
            "accent_press": "#6591F5",
            "accent_text": "#1A1B26",
            "selection": "#33467C",
            "selection_text": "#A9B1D6",
            "row_current": "#22325A",
            "text_muted": "#565F89",
            "text_disabled": "#4E5579",
            "surface_hover": "#2E344E",
            "neutral_hover": "#1F2335",
            "thumb_hover": "#5C638A",
            "tooltip": "#16161E",
            "button_border": "#383E5A",
            "focus_ring": "#7AA2F7",
            "separator": "#383E5A",
            "danger": "#F7768E",
        },
        "GitHub Dark": {
            "accent": "#58A6FF",
            "text": "#C9D1D9",
            "window": "#0D1117",
            "neutral": "#161B22",
            "surface": "#21262D",
            "surface_disabled": "#161B22",
            "border": "#30363D",
            "track": "#161B22",
            "thumb": "#30363D",
            "accent_hover": "#79B8FF",
            "accent_press": "#388BFD",
            "accent_text": "#0D1117",
            "selection": "#1F6FEB",
            "selection_text": "#C9D1D9",
            "row_current": "#172E54",
            "text_muted": "#8B949E",
            "text_disabled": "#484F58",
            "surface_hover": "#30363D",
            "neutral_hover": "#21262D",
            "thumb_hover": "#8B949E",
            "tooltip": "#161B22",
            "button_border": "#30363D",
            "focus_ring": "#58A6FF",
            "separator": "#30363D",
            "danger": "#F85149",
        },
        "One Dark Pro": {
            "accent": "#61AFEF",
            "text": "#ABB2BF",
            "window": "#282C34",
            "neutral": "#21252B",
            "surface": "#2C313C",
            "surface_disabled": "#21252B",
            "border": "#3E4451",
            "track": "#21252B",
            "thumb": "#4B5263",
            "accent_hover": "#74BAF2",
            "accent_press": "#4E94D4",
            "accent_text": "#282C34",
            "selection": "#3E4451",
            "selection_text": "#ABB2BF",
            "row_current": "#2C384E",
            "text_muted": "#5C6370",
            "text_disabled": "#4B5263",
            "surface_hover": "#353B45",
            "neutral_hover": "#282C34",
            "thumb_hover": "#5C6370",
            "tooltip": "#21252B",
            "button_border": "#3E4451",
            "focus_ring": "#61AFEF",
            "separator": "#3E4451",
            "danger": "#E06C75",
        },
        "Monokai Pro": {
            "accent": "#FFD866",
            "text": "#FCE5CD",
            "window": "#2D2A2E",
            "neutral": "#221F22",
            "surface": "#403E41",
            "surface_disabled": "#221F22",
            "border": "#49474A",
            "track": "#221F22",
            "thumb": "#5B595C",
            "accent_hover": "#FFE085",
            "accent_press": "#E6C25C",
            "accent_text": "#2D2A2E",
            "selection": "#5B595C",
            "selection_text": "#FCE5CD",
            "row_current": "#4A4335",
            "text_muted": "#726E75",
            "text_disabled": "#5B595C",
            "surface_hover": "#49474A",
            "neutral_hover": "#2D2A2E",
            "thumb_hover": "#726E75",
            "tooltip": "#221F22",
            "button_border": "#49474A",
            "focus_ring": "#FFD866",
            "separator": "#49474A",
            "danger": "#FF6188",
        },
        "Nord": {
            "accent": "#88C0D0",
            "text": "#D8DEE9",
            "window": "#2E3440",
            "neutral": "#242933",
            "surface": "#3B4252",
            "surface_disabled": "#242933",
            "border": "#434C5E",
            "track": "#242933",
            "thumb": "#4C566A",
            "accent_hover": "#98C9D7",
            "accent_press": "#78B2C2",
            "accent_text": "#2E3440",
            "selection": "#434C5E",
            "selection_text": "#ECEFF4",
            "row_current": "#394850",
            "text_muted": "#4C566A",
            "text_disabled": "#4C566A",
            "surface_hover": "#434C5E",
            "neutral_hover": "#2E3440",
            "thumb_hover": "#616E88",
            "tooltip": "#242933",
            "button_border": "#434C5E",
            "focus_ring": "#88C0D0",
            "separator": "#434C5E",
            "danger": "#BF616A",
        },
        "Dracula": {
            "accent": "#FF79C6",
            "text": "#F8F8F2",
            "window": "#282A36",
            "neutral": "#191A21",
            "surface": "#44475A",
            "surface_disabled": "#191A21",
            "border": "#44475A",
            "track": "#191A21",
            "thumb": "#6272A4",
            "accent_hover": "#FF92DF",
            "accent_press": "#E066AE",
            "accent_text": "#282A36",
            "selection": "#44475A",
            "selection_text": "#F8F8F2",
            "row_current": "#44354A",
            "text_muted": "#6272A4",
            "text_disabled": "#44475A",
            "surface_hover": "#44475A",
            "neutral_hover": "#21222C",
            "thumb_hover": "#7887B6",
            "tooltip": "#191A21",
            "button_border": "#44475A",
            "focus_ring": "#FF79C6",
            "separator": "#44475A",
            "danger": "#FF5555",
        },
        "Solarized Dark": {
            "accent": "#2AA198",
            "text": "#839496",
            "window": "#002B36",
            "neutral": "#073642",
            "surface": "#002B36",
            "surface_disabled": "#04232C",
            "border": "#586E75",
            "track": "#073642",
            "thumb": "#586E75",
            "accent_hover": "#35B2A9",
            "accent_press": "#208C84",
            "accent_text": "#002B36",
            "selection": "#073642",
            "selection_text": "#93A1A1",
            "row_current": "#063A3B",
            "text_muted": "#586E75",
            "text_disabled": "#475B62",
            "surface_hover": "#073642",
            "neutral_hover": "#0A414F",
            "thumb_hover": "#839496",
            "tooltip": "#073642",
            "button_border": "#586E75",
            "focus_ring": "#2AA198",
            "separator": "#586E75",
            "danger": "#DC322F",
        },
        "Gruvbox": {
            "accent": "#FE8019",
            "text": "#EBDBB2",
            "window": "#282828",
            "neutral": "#1D2021",
            "surface": "#3C3836",
            "surface_disabled": "#1D2021",
            "border": "#504945",
            "track": "#1D2021",
            "thumb": "#665C54",
            "accent_hover": "#FFA254",
            "accent_press": "#D66B10",
            "accent_text": "#282828",
            "selection": "#504945",
            "selection_text": "#FBF1C7",
            "row_current": "#4E3E2F",
            "text_muted": "#928374",
            "text_disabled": "#665C54",
            "surface_hover": "#504945",
            "neutral_hover": "#282828",
            "thumb_hover": "#7C6F64",
            "tooltip": "#1D2021",
            "button_border": "#504945",
            "focus_ring": "#FE8019",
            "separator": "#504945",
            "danger": "#FB4934",
        },
        "Cyberpunk": {
            "accent": "#00FF66",
            "text": "#00FFFF",
            "window": "#000000",
            "neutral": "#0F0F14",
            "surface": "#14141F",
            "surface_disabled": "#0F0F14",
            "border": "#FF0055",
            "track": "#0F0F14",
            "thumb": "#FF0055",
            "accent_hover": "#33FF85",
            "accent_press": "#00CC52",
            "accent_text": "#000000",
            "selection": "#FF0055",
            "selection_text": "#FFFFFF",
            "row_current": "#003314",
            "text_muted": "#7A7A99",
            "text_disabled": "#3A3A4D",
            "surface_hover": "#1F1F2E",
            "neutral_hover": "#14141F",
            "thumb_hover": "#FF3377",
            "tooltip": "#0F0F14",
            "button_border": "#FF0055",
            "focus_ring": "#00FF66",
            "separator": "#FF0055",
            "danger": "#FF0000",
        },
    },
]


THEMES = copy.deepcopy(ORIGINAL_THEMES)


def creator():
    """A custom theme creator for PyNotes."""

    def refresh_preview():
        """Apply the dark/light mode and the changes so far to the preview,
        and update the display of every color that hasn't been changed, since
        its default can depend on the mode and on other colors.
        """
        previewframe.reset_theme()
        previewframe.set_appearance_mode("dark" if return_dark.get() else "light")
        previewframe.set_theme(return_theme)
        preview_theme = previewframe.get_theme()
        for theme_key, display in displays.items():
            if theme_key not in return_theme:
                display.set(preview_theme[theme_key])

    def theme_change(what, new=None, reset=False):
        """Open the color chooser and change the color in the theme to return
        if not cancelled.
        """
        if not reset and new is None:
            return
        if reset:
            if what not in return_theme:
                return
            del return_theme[what]
        else:
            displays[what].set(new)
            return_theme[what] = new
        refresh_preview()

    def done():
        """Check if the theme name is given. If it is, return the theme."""
        nonlocal is_done
        nonlocal return_theme_name
        if not (return_theme_name := themenameentry.get().strip()):
            state.root.info("Theme Creator", "Theme name not provided.", parent=cwin)
            return
        is_done = True
        cwin.destroy()

    def cancel():
        """Prompt to cancel the changes and exit."""
        if state.root.ask(
            "Theme Creator", "Discard theme and exit?", ("yes", "no"), parent=cwin
        ):
            cwin.destroy()

    def make_change_row(
        master,
        key,
        text,
        tooltip,
        type_="color",
        last=None,
        options=None,
        theme_options=None,
    ):
        """Make and return a frame which controls the given theme key. If the
        type_ is "color", show a color display with a change button. If the type_
        is "number", show a slider with a label showing its value. If the type_
        is "option", show a dropdown.
        """
        frame = ctk.Frame(master)
        ctk.Label(frame, text=text).grid(
            column=0,
            row=0,
            padx=10,
            pady=10,
            sticky="w",
        )
        frame.grid_columnconfigure(0, weight=1)
        if type_ == "color":
            displays[key] = ctk.ColorDisplay(
                frame, color=previewframe.get_theme()[key], size=32
            )
            displays[key].set = lambda c: displays[key].config(color=c)
            displays[key].grid(
                column=1,
                row=0,
                padx=10,
                pady=10,
                sticky="e",
            )
            cb = ctk.Button(
                frame,
                text="Change",
                command=lambda: theme_change(
                    key,
                    askcolor(ctk.get_theme()[key], title="Theme Creator", parent=cwin)[
                        1
                    ],
                ),
            )
            cb.grid(
                column=2,
                row=0,
                padx=10,
                pady=10,
                sticky="e",
            )
            ctk.Tooltip(cb, tooltip)
        elif type_ == "number":
            starting_radius = previewframe.get_theme()[key]

            class numberdisplay:
                def __init__(self, l):
                    self.l = l

            displays[key] = numberdisplay(
                [
                    ctk.Label(frame, text=round(starting_radius)),
                    ctk.Scale(
                        frame,
                        from_=0,
                        to=last,
                        length=300,
                        value=starting_radius,
                        command=lambda v: theme_change(key, v),
                    ),
                ]
            )
            displays[key].set = lambda n: [
                displays[key].l[0].config(text=round(n)),
                displays[key].l[1].set(n),
            ]
            displays[key].l[0].grid(
                column=1,
                row=0,
                padx=10,
                pady=10,
                sticky="e",
            )
            displays[key].l[1].grid(
                column=2,
                row=0,
                padx=10,
                pady=10,
                sticky="e",
            )
            ctk.Tooltip(displays[key].l[1], tooltip)
        elif type_ == "option":
            frame.grid_columnconfigure(2, weight=1)
            displays[key] = ctk.OptionMenu(
                frame,
                values=options,
                command=lambda new: theme_change(
                    key, theme_options[options.index(new)]
                ),
            )
            displays[key].set = lambda new: displays[key].variable.set(
                options[theme_options.index(new)]
            )
            displays[key].set(previewframe.get_theme()[key])
            displays[key].grid(column=2, row=0, padx=10, pady=10, sticky="ew")
            ctk.Tooltip(displays[key], tooltip)
        ctk.Button(
            frame,
            text="Reset",
            command=lambda: theme_change(key, reset=True),
        ).grid(column=3, row=0, padx=10, pady=10, sticky="e")
        return frame

    import state

    return_theme = {}
    return_dark = tk.BooleanVar()
    if ctk.get_appearance_mode() == "dark":
        return_dark.set(True)
    return_theme_name = ""
    is_done = False
    cwin = state.root.subwin(appearance_mode="light", theme={})
    cwin.title("Theme Creator")
    cwin.geometry("1600x800")
    displays = {}
    panes = ctk.Panedwindow(cwin)
    changeframe = ctk.Frame(cwin)
    previewframe = ctk.LabelFrame(
        cwin,
        "Preview",
        font=("TkDefaultFont", 20),
        scrolled=True,
    )
    panes.add(changeframe, weight=1)
    panes.add(previewframe, weight=1)
    # Preview
    previewframe.grid_columnconfigure(0, weight=1)
    st = ctk.Notebook(previewframe)
    st.grid_columnconfigure(0, weight=1)
    stt1 = ctk.Frame(st)
    st.add(stt1, text="Tab 1")
    ctk.Label(stt1, text="Tab 1").grid()
    stt2 = ctk.Frame(st)
    st.add(stt2, text="Tab 2")
    ctk.Label(stt2, text="Tab 2").grid()
    stt3 = ctk.Frame(st)
    st.add(stt3, text="Tab 3")
    ctk.Label(stt3, text="Tab 3").grid()
    stct = ctk.Frame(st)
    st.add(stct, text="Closeable Tab", closable=True)
    ctk.Label(stct, text="This is a closeable tab").grid()
    st.grid(column=0, row=0, sticky="ew")
    ctk.Separator(previewframe).grid(column=0, row=1, padx=10, pady=10, sticky="ew")
    previewtabs = ctk.Notebook(previewframe)
    previewtabs.grid(column=0, row=2, sticky="nsew")
    s1f = ctk.Frame(previewtabs)
    s2f = ctk.Frame(previewtabs)
    previewtabs.add(s1f, text="Section 1")
    previewtabs.add(s2f, text="Section 2")
    # Section 1 of the preview
    s1mf = ctk.Frame(s1f)
    s1mf.grid(column=0, row=0, sticky="nsew")
    hb = ctk.Button(s1mf, text="Hover me")
    hb.grid(column=0, row=0, padx=10, pady=10, sticky="w")
    ctk.Tooltip(hb, "This is a tooltip.")
    ctk.Entry(s1mf, placeholder="This is an entry.").grid(
        column=0, row=1, padx=10, pady=10, sticky="ew"
    )
    ctk.Entry(s1mf, placeholder="This is a disabled entry.", state="disabled").grid(
        column=1, row=1, padx=10, pady=10, sticky="ew"
    )
    ctk.OptionMenu(
        s1mf,
        values=["Option 1", "Option 2", "Option 3"],
        placeholder="This is an optionmenu.",
    ).grid(column=0, row=2, padx=10, pady=10, sticky="ew")
    ctk.OptionMenu(
        s1mf, default="This is a disabled optionmenu.", state="disabled"
    ).grid(column=1, row=2, padx=10, pady=10, sticky="ew")
    ctk.OptionMenu(
        s1mf,
        values=["Option 1", "Option 2", "Option 3"],
        placeholder="This is a solid optionmenu.",
        solid=True,
    ).grid(column=0, row=3, padx=10, pady=10, sticky="ew")
    ctk.OptionMenu(
        s1mf,
        default="This is a disabled solid optionmenu.",
        state="disabled",
        solid=True,
    ).grid(column=1, row=3, padx=10, pady=10, sticky="ew")
    ctk.Combobox(
        s1mf,
        values=["Option 1", "Option 2", "Option 3"],
        placeholder="This is a combobox.",
    ).grid(column=0, row=4, padx=10, pady=10, sticky="ew")
    ctk.Combobox(s1mf, default="This is a disabled combobox.", state="disabled").grid(
        column=1, row=4, padx=10, pady=10, sticky="ew"
    )
    ctk.Textbox(
        s1f,
        placeholder="This is a scrolled textbox.",
        scrolled=True,
        orient="both",
        height=5,
    ).grid(column=0, row=1, padx=10, pady=10, sticky="ew")
    ctk.Textbox(
        s1f,
        placeholder="This is a disabled textbox.",
        scrolled=True,
        orient="both",
        state="disabled",
        height=5,
    ).grid(column=0, row=2, padx=10, pady=10, sticky="ew")
    # Section 2 of the preview
    fp = ctk.Foldable(s2f, "Foldable", expanded=True)
    ctk.Label(fp, text="This text is inside a foldable (try hiding it).").grid()
    ctk.Tooltip(fp.header, "This is a foldable.")
    s2f.grid_columnconfigure(0, weight=1)
    fp.grid(column=0, row=0, padx=10, pady=10, sticky="ew")
    ctk.Scale(s2f, from_=0, to=100, width=300, value=35).grid(
        column=0, row=1, padx=10, pady=10, sticky="w"
    )
    ctk.Scale(s2f, from_=0, to=100, width=300, value=35, state="disabled").grid(
        column=1, row=1, padx=10, pady=10, sticky="w"
    )
    ctk.Progressbar(s2f, value=35, length=300).grid(
        column=0, row=2, padx=10, pady=10, sticky="w"
    )
    ctk.Meter(s2f, value=35).grid(column=0, row=3, padx=10, pady=10, sticky="w")
    ctk.Listbox(
        s2f, ["Item " + str(i + 1) for i in range(100)], height=5, scrolled=True
    ).grid(column=0, row=4, padx=10, pady=10, sticky="ew")
    ctk.Listbox(
        s2f,
        ["Disabled Item " + str(i + 1) for i in range(100)],
        height=5,
        scrolled=True,
        state="disabled",
    ).grid(column=0, row=5, padx=10, pady=10, sticky="ew")
    # Creator
    changeframe.grid_columnconfigure(0, weight=1)
    topframe = ctk.Frame(changeframe)
    topframe.grid(
        column=0,
        row=0,
        sticky="ew",
    )
    topframe.grid_columnconfigure(0, weight=1)
    ctk.Label(topframe, text="Name (can overwrite existing custom themes):").grid(
        column=0,
        row=0,
        padx=10,
        pady=10,
        sticky="w",
    )
    themenameentry = ctk.Entry(topframe, placeholder="Custom Theme")
    themenameentry.grid(
        column=1,
        row=0,
        padx=10,
        pady=10,
        sticky="ew",
    )
    changepanes = ctk.Panedwindow(changeframe, orient="vertical")
    changeframe.grid_rowconfigure(1, weight=1)
    changepanes.grid(column=0, row=1, padx=10, pady=10, sticky="nsew")
    mainframe = ctk.ScrolledFrame(changepanes)
    changepanes.add(mainframe, weight=1)
    mainframe.grid_columnconfigure(0, weight=1)
    dt = ctk.Toggle(topframe, "Dark theme", return_dark, command=refresh_preview)
    dt.grid(
        column=0,
        row=1,
        padx=10,
        pady=10,
        sticky="w",
    )
    ctk.Tooltip(dt, "The theme is light or dark.")
    options = [
        (
            "accent",
            "Accent color:",
            "The color of selection, buttons, tabs, toggles, etc.",
        ),
        ("text", "Text color:", "The color of default text."),
        (
            "window",
            "Window background:\n(can override light or dark mode)",
            "The background of the main window and all frames.",
        ),
        (
            "neutral",
            "Neutral color:",
            "Quiet fill for foldable headers, notebook tab strips, etc.",
        ),
        ("surface", "Input widget color:", "Color of entry widgets."),
        (
            "surface_disabled",
            "Disabled input widget color:",
            "Color of disabled entry widgets.",
        ),
        ("border", "Border color:", "Normal widget border color."),
        (
            "track",
            "Track color:",
            "Trough behind numbers, scrollbars, progress bars, etc.",
        ),
        ("thumb", "Thumb color:", "The color of scrollbars, numbers, etc."),
        (
            "radius",
            "Widget radius:",
            "The radius of all input widgets, lists, labeled frames, and headers.",
            "number",
            20,
        ),
        (
            "button_radius",
            "Button radius:",
            "The radius of all buttons.",
            "number",
            20,
        ),
        (
            "tab_radius",
            "Tab radius:",
            "The radius of all tabs.",
            "number",
            20,
        ),
        (
            "small_radius",
            "Small radius:",
            "Radius of menu items, highlights, notebook arrow hovers, etc.",
            "number",
            20,
        ),
        (
            "row_radius",
            "Selection radius:",
            "Radius of selected and hovered items in lists.",
            "number",
            15,
        ),
        ("checkbox_radius", "Checkbox radius:", "Radius of checkboxes.", "number", 10),
        (
            "track_radius",
            "Track radius:",
            "Radius of slider and progressbar tracks.",
            "number",
            7,
        ),
        (
            "scrollbar_radius",
            "Scrollbar radius:",
            "Radius of scrollbars and their tracks.",
            "number",
            7,
        ),
        (
            "tab_style",
            "Tab style:",
            "Style of tabs (segmented/classic/underline).",
            "option",
            None,
            ("Segmented", "Classic", "Underline"),
            ("segmented", "classic", "underline"),
        ),
    ]
    row = 0
    for option in options:
        make_change_row(mainframe, *option).grid(
            column=0,
            row=row,
            sticky="ew",
        )
        row += 1
    advanced = ctk.Foldable(changepanes, "Advanced", expanded=False, scrolled=True)
    changepanes.add(advanced, weight=1)
    advanced.grid_columnconfigure(0, weight=1)
    advanced_options = [
        (
            "accent_hover",
            "Hover accent:",
            "Accent of widgets on hover; normally derived from accent.",
        ),
        ("accent_press", "Pressed color:", "Color of pressed buttons."),
        ("accent_text", "Accent text:", "Text color on accented widget or part."),
        ("selection", "Selection color:\n(normally accent)", "Color of selection."),
        (
            "selection_text",
            "Selection foreground:",
            "Foreground of selected text; normally derived from accent.",
        ),
        (
            "row_current",
            "Current row:",
            "Color of inactive selected row in lists; normally derived from accent.",
        ),
        ("text_muted", "Secondary text:", "Color of secondary/muted text."),
        ("text_disabled", "Disabled text:", "Color of text in disabled widgets."),
        (
            "surface_hover",
            "Surface hover:",
            "Hover fill of check boxes, radio buttons, list rows, and option menus.",
        ),
        (
            "neutral_hover",
            "Neutral hover:",
            "Hover fill of foldable headers and notebook tabs.",
        ),
        (
            "thumb_hover",
            "Thumb hover:",
            "Color of scrollbars and sliders when hovering or dragged.",
        ),
        ("tooltip", "Tooltip background:", "Color of the background of tooltips."),
        (
            "button_border",
            "Button border color:",
            "Color of button and solid optionmenu borders.",
        ),
        (
            "focus_ring",
            "Focus border color:",
            "Color of the border of focused widgets.",
        ),
        ("separator", "Separator color:", "Color of separator lines."),
        ("danger", "Danger color:", "Color of errors and tab close buttons."),
    ]
    row = 0
    for option in advanced_options:
        make_change_row(advanced, *option).grid(
            column=0,
            row=row,
            sticky="ew",
        )
        row += 1
    buttonframe = ctk.Frame(cwin)
    buttonframe.pack(side="bottom", fill="x")
    ctk.Separator(cwin).pack(side="bottom", fill="x")
    panes.pack(side="top", fill="both", expand=True)
    ctk.Button(buttonframe, text="Cancel", command=cancel).grid(
        column=0,
        row=0,
        padx=10,
        pady=10,
        sticky="e",
    )
    ctk.Button(buttonframe, text="Done", command=done).grid(
        column=1,
        row=0,
        padx=10,
        pady=10,
        sticky="e",
    )
    cwin.protocol("WM_DELETE_WINDOW", cancel)
    cwin.focus()
    cwin.wait_window()
    if is_done:
        return return_theme_name, return_dark.get(), return_theme
    else:
        return None
