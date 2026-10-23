"""Every source file and installer script of the repository must at least
parse."""

import ast
import shutil
import subprocess
from pathlib import Path

import pytest

REPOSITORY = Path(__file__).resolve().parent.parent
PYTHON_FILES = sorted(
    [*REPOSITORY.glob("Source/**/*.py"), *REPOSITORY.glob("*.py")],
)
SHELL_FILES = sorted(REPOSITORY.glob("*.sh"))


@pytest.mark.parametrize(
    "path", PYTHON_FILES, ids=lambda p: str(p.relative_to(REPOSITORY))
)
def test_python_file_parses(path):
    ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


@pytest.mark.skipif(shutil.which("bash") is None, reason="bash is not installed")
@pytest.mark.parametrize("path", SHELL_FILES, ids=lambda p: p.name)
def test_shell_script_parses(path):
    result = subprocess.run(["bash", "-n", str(path)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


def test_source_files_were_found():
    assert PYTHON_FILES and SHELL_FILES
