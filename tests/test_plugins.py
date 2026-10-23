"""The plugin archives in Plugins/, the lists that describe them, and the
loader that reads an installed plugin."""

import ast
import zipfile
from pathlib import Path

import pytest

import init
import state

PLUGINS_DIRECTORY = Path(__file__).resolve().parent.parent / "Plugins"
PLUGIN_NAMES = (PLUGINS_DIRECTORY / "list").read_text(encoding="utf-8").split("\n")
PLUGIN_PYTHON_FILES = ("init", "first", "last")
PLUGIN_ENTRY_FILES = ("commands", "hmodes", "pycodecommands")
PLUGIN_FULL_DESCRIPTION_SEPARATOR = "=========="


def _plugin_members(files):
    """(plugin name, file name) pairs for the given files the plugins have."""
    pairs = []
    for name in PLUGIN_NAMES:
        with zipfile.ZipFile(PLUGINS_DIRECTORY / f"{name}.zip") as archive:
            members = set(archive.namelist())
        pairs.extend((name, file) for file in files if f"{name}/{file}" in members)
    return pairs


def _plugin_archive(name):
    return zipfile.ZipFile(PLUGINS_DIRECTORY / f"{name}.zip")


def _plugin_text(name, member):
    with _plugin_archive(name) as archive:
        try:
            return archive.read(f"{name}/{member}").decode("utf-8")
        except KeyError:
            return None


def test_plugin_list_has_no_blank_or_duplicate_entries():
    assert all(name.strip() == name and name for name in PLUGIN_NAMES)
    assert len(set(PLUGIN_NAMES)) == len(PLUGIN_NAMES)


def test_every_archive_is_in_the_plugin_list():
    archives = {path.stem for path in PLUGINS_DIRECTORY.glob("*.zip")}
    assert archives == set(PLUGIN_NAMES)


def test_one_line_descriptions_match_the_plugin_list():
    descriptions = (
        (PLUGINS_DIRECTORY / "onelinedescriptions")
        .read_text(encoding="utf-8")
        .split("\n")
    )
    assert len(descriptions) == len(PLUGIN_NAMES)
    for name, description in zip(PLUGIN_NAMES, descriptions):
        assert description == _plugin_text(name, "onelinedescription"), name


def test_full_descriptions_match_the_plugin_list():
    text = (PLUGINS_DIRECTORY / "fulldescriptions").read_text(encoding="utf-8")
    sections = text.split(f"\n{PLUGIN_FULL_DESCRIPTION_SEPARATOR}\n")
    assert len(sections) == len(PLUGIN_NAMES)
    for name, section in zip(PLUGIN_NAMES, sections):
        assert section == _plugin_text(name, "fulldescription"), name


@pytest.mark.parametrize("name", PLUGIN_NAMES)
def test_archive_is_valid_and_holds_only_its_own_directory(name):
    with _plugin_archive(name) as archive:
        assert archive.testzip() is None
        members = archive.namelist()
    assert f"{name}/" in members
    for member in members:
        assert member.startswith(f"{name}/"), member
        assert ".." not in Path(member).parts
        assert not member.startswith("/")


@pytest.mark.parametrize("name", PLUGIN_NAMES)
def test_archive_has_both_descriptions(name):
    assert _plugin_text(name, "onelinedescription")
    assert _plugin_text(name, "fulldescription")


@pytest.mark.parametrize(("name", "member"), _plugin_members(PLUGIN_PYTHON_FILES))
def test_plugin_python_files_are_valid_python(name, member):
    code = _plugin_text(name, member)
    ast.parse(code, filename=f"{name}/{member}")


@pytest.mark.parametrize(("name", "member"), _plugin_members(PLUGIN_ENTRY_FILES))
def test_plugin_entry_files_have_one_quoted_name_then_code_per_line(name, member):
    text = _plugin_text(name, member)
    for line in text.split("\n"):
        assert line.startswith('"') and line.count('"') >= 2, line


@pytest.fixture(autouse=True)
def restored_state():
    """load_plugins() assigns the plugin tables of the shared state module."""
    saved = dict(vars(state))
    yield
    vars(state).clear()
    vars(state).update(saved)


def _install_plugins(add_ons_directory):
    add_ons_directory.mkdir(parents=True)
    for name in PLUGIN_NAMES:
        with _plugin_archive(name) as archive:
            archive.extractall(add_ons_directory)


@pytest.fixture
def installed_plugins(tmp_path, monkeypatch):
    add_ons = tmp_path / ".local" / "share" / "PyNotes" / "add-ons"
    _install_plugins(add_ons)
    monkeypatch.setattr(init, "homedir", str(tmp_path))
    return add_ons


def test_loader_reads_every_installed_plugin(installed_plugins):
    init_code, first_code, last_code = init.load_plugins(False)
    directories = {str(installed_plugins / name) for name in PLUGIN_NAMES}
    for loaded in (init_code, first_code, last_code):
        assert {directory for directory, _ in loaded} <= directories
    assert {d for d, _ in init_code + first_code + last_code} == directories
    assert state.plgncmds
    assert isinstance(state.plgnhmodes, dict)
    assert state.plgnpccmds


def test_loader_loads_nothing_when_plugins_are_disabled(installed_plugins):
    assert init.load_plugins(True) == ([], [], [])
    assert state.plgncmds == {}
    assert state.plgnpccmds == {}
    assert state.plgnhmodes == {}
    assert state.buffer_init_functions == []


def test_loader_ignores_files_that_are_not_plugin_directories(installed_plugins):
    (installed_plugins / "stray.txt").write_text("not a plugin")
    init_code, first_code, last_code = init.load_plugins(False)
    assert not any(
        directory.endswith("stray.txt")
        for directory, _ in init_code + first_code + last_code
    )


def test_loader_registers_commands_by_their_quoted_name(tmp_path, monkeypatch):
    add_ons = tmp_path / ".local" / "share" / "PyNotes" / "add-ons"
    plugin = add_ons / "Example"
    plugin.mkdir(parents=True)
    (plugin / "commands").write_text('"hello"print("hi")\\nprint("again")')
    (plugin / "pycodecommands").write_text('"greet"say("hi")')
    (plugin / "hmodes").write_text('"Mode"state.mode = 1')
    (plugin / "helpcommands").write_text("hello: says hi\n")
    (plugin / "first").write_text("x = 1")
    monkeypatch.setattr(init, "homedir", str(tmp_path))
    _, first_code, _ = init.load_plugins(False)
    assert state.plgncmds == {"hello": (str(plugin), 'print("hi")\nprint("again")')}
    assert state.plgnpccmds == {"greet": (str(plugin), 'say("hi")')}
    assert state.plgnhmodes == {"Mode": (str(plugin), "state.mode = 1")}
    assert state.plgnscmdhelp == "\n\nhello: says hi"
    assert first_code == [(str(plugin), "x = 1")]
