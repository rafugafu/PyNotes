"""The built-in themes: the data is plain dicts, so no display is needed."""

import re

import pytest

import canvastk as ctk
import themes

HEX_COLOR = re.compile(r"#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})")
LIGHT_THEMES, DARK_THEMES = themes.ORIGINAL_THEMES
EVERY_THEME = [
    (kind, name, theme)
    for kind, group in (("light", LIGHT_THEMES), ("dark", DARK_THEMES))
    for name, theme in group.items()
]


def test_there_is_a_light_and_a_dark_group():
    assert len(themes.ORIGINAL_THEMES) == 2
    assert LIGHT_THEMES and DARK_THEMES


def test_theme_names_are_unique_across_light_and_dark():
    assert not set(LIGHT_THEMES) & set(DARK_THEMES)


@pytest.mark.parametrize(("kind", "name", "theme"), EVERY_THEME)
def test_theme_keys_are_canvastk_theme_keys(kind, name, theme):
    assert set(theme) <= set(ctk.CANVAS_WIDGET_THEME)


@pytest.mark.parametrize(("kind", "name", "theme"), EVERY_THEME)
def test_theme_values_are_hex_colors(kind, name, theme):
    for key, value in theme.items():
        assert HEX_COLOR.fullmatch(value), (key, value)


@pytest.mark.parametrize(
    ("kind", "name", "theme"),
    [entry for entry in EVERY_THEME if entry[1] not in ("Default", "Dark", "Light")],
)
def test_other_themes_set_the_same_keys_as_the_base_theme(kind, name, theme):
    reference = LIGHT_THEMES["Light"] if kind == "light" else DARK_THEMES["Dark"]
    assert set(theme) == set(reference)


def test_default_theme_changes_nothing():
    assert LIGHT_THEMES["Default"] == {}


def test_working_themes_start_as_an_independent_copy_of_the_originals():
    assert themes.THEMES == themes.ORIGINAL_THEMES
    assert themes.THEMES is not themes.ORIGINAL_THEMES
    assert themes.THEMES[0] is not themes.ORIGINAL_THEMES[0]
