import pytest

from encrypter import encryptdecrypt


def test_encrypting_changes_the_file(tmp_path):
    path = tmp_path / "config"
    path.write_bytes(b"password=hunter2")
    encryptdecrypt(str(path))
    assert path.read_bytes() != b"password=hunter2"
    assert len(path.read_bytes()) == len(b"password=hunter2")


def test_decrypting_restores_the_original_bytes(tmp_path):
    path = tmp_path / "config"
    original = bytes(range(256)) * 3
    path.write_bytes(original)
    encryptdecrypt(str(path))
    encryptdecrypt(str(path))
    assert path.read_bytes() == original


def test_text_longer_than_the_key_round_trips(tmp_path):
    path = tmp_path / "config"
    original = ("long line of text\n" * 100).encode()
    path.write_bytes(original)
    encryptdecrypt(str(path))
    encryptdecrypt(str(path))
    assert path.read_bytes() == original


def test_empty_file_stays_empty(tmp_path):
    path = tmp_path / "config"
    path.write_bytes(b"")
    encryptdecrypt(str(path))
    assert path.read_bytes() == b""


def test_missing_file_exits_without_creating_it(tmp_path):
    path = tmp_path / "missing"
    with pytest.raises(SystemExit) as info:
        encryptdecrypt(str(path))
    assert info.value.code == 0
    assert not path.exists()
