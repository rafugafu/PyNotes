"""Text to speech and the speech-to-text window. The speech engine, the
microphone and Google's recognizer are replaced by stand-ins."""

import time
from types import SimpleNamespace

import canvastk as ctk
import numpy as np
import pytest

import speech
import state
from test_editor import editor, put, text_of, wait_for, wait_for_message
from test_utils import console_messages  # noqa: F401  (a fixture)

pytestmark = pytest.mark.display


def descendants(widget):
    for child in widget.winfo_children():
        yield child
        yield from descendants(child)


# ---------------------------------------------------------------------------
# Speaking
# ---------------------------------------------------------------------------


def test_text_is_spoken_with_the_engine(app):
    spoken = []
    state.engine = SimpleNamespace(
        say=lambda text: spoken.append(text), runAndWait=lambda: spoken.append("done")
    )

    speech.actualspk("hello")

    assert spoken == ["hello", "done"]


def test_a_failing_engine_is_reported(app):
    def broken(text):
        raise RuntimeError("no voice")

    state.engine = SimpleNamespace(say=broken, runAndWait=lambda: None)

    speech.actualspk("hello")

    assert app.dialogs.messages("error") == ["An error occured:no voice"]


# ---------------------------------------------------------------------------
# The speech-to-text window
# ---------------------------------------------------------------------------


class FakeRecognizer:
    """Google's recognizer, answering with a fixed text."""

    answer = ""
    heard = []

    def record(self, source):
        FakeRecognizer.heard.append(source)
        return "audio"

    def recognize_google(self, audio):
        if isinstance(FakeRecognizer.answer, Exception):
            raise FakeRecognizer.answer
        return FakeRecognizer.answer


class FakeAudioFile:
    def __init__(self, file):
        self.file = file

    def __enter__(self):
        return self.file

    def __exit__(self, *arguments):
        return False


class FakeInputStream:
    """The microphone: delivers one block of silence when it opens."""

    opened = []

    def __init__(self, callback, channels, dtype, samplerate):
        FakeInputStream.opened.append((channels, dtype, samplerate))
        self.callback = callback

    def __enter__(self):
        self.callback(np.zeros((1600, 1), dtype=np.int16), 1600, None, None)
        return self

    def __exit__(self, *arguments):
        return False


@pytest.fixture
def speech_window(app, tk_root, editor, monkeypatch, console_messages):
    FakeRecognizer.answer = ""
    FakeRecognizer.heard = []
    FakeInputStream.opened = []
    monkeypatch.setattr(
        speech,
        "sr",
        SimpleNamespace(Recognizer=FakeRecognizer, AudioFile=FakeAudioFile),
    )
    monkeypatch.setattr(
        speech,
        "sd",
        SimpleNamespace(
            InputStream=FakeInputStream, sleep=lambda ms: time.sleep(0.001)
        ),
    )
    windows = []
    original = type(tk_root).subwin

    def subwin(*arguments, **keywords):
        top = original(tk_root, *arguments, **keywords)
        top.withdraw()
        windows.append(top)
        return top

    monkeypatch.setattr(tk_root, "subwin", subwin, raising=False)
    speech.st()
    (window_,) = windows
    widgets = list(descendants(window_))
    buttons = {w.cget("text"): w for w in widgets if isinstance(w, ctk.Button)}
    output = next(w for w in widgets if isinstance(w, ctk.Textbox))
    yield SimpleNamespace(window=window_, buttons=buttons, output=output, editor=editor)
    speech.recording = False
    if window_.winfo_exists():
        window_.destroy()


def record_and_stop(speech_window, tk_root, said):
    FakeRecognizer.answer = said
    speech_window.buttons["Start Recording"].invoke()
    wait_for(tk_root, lambda: speech.recording is True, "the recording to start")
    speech_window.buttons["Stop Recording"].invoke()
    return speech_window.output.get("1.0", "end-1c")


def test_the_window_has_recording_buttons_and_a_write_button(speech_window):
    assert set(speech_window.buttons) == {
        "Start Recording",
        "Stop Recording",
        "Write to Active Editor",
    }
    assert speech_window.window.title() == "Control"


def test_recording_uses_16_kilohertz_mono(speech_window, tk_root):
    speech_window.buttons["Start Recording"].invoke()
    wait_for(tk_root, lambda: speech.recording is True, "the recording to start")

    assert FakeInputStream.opened == [(1, np.int16, 16000)]
    speech_window.buttons["Stop Recording"].invoke()


def test_the_recognized_text_is_shown(speech_window, tk_root):
    assert record_and_stop(speech_window, tk_root, "hello world") == "hello world"


def test_a_recognition_error_is_shown_as_text(speech_window, tk_root):
    shown = record_and_stop(speech_window, tk_root, RuntimeError("no network"))

    assert shown == "Error:\nno network"


def test_stopping_ends_the_recording(speech_window, tk_root):
    record_and_stop(speech_window, tk_root, "x")

    assert speech.recording is False
    assert speech.audio == []


@pytest.mark.parametrize(
    ("said", "written"),
    [
        ("hello full stop", "hello ."),
        ("hello Full Stop", "hello ."),
        ("hello full Stop", "hello ."),
        ("hello Full stop", "hello ."),
        ("a comma b", "a , b"),
        ("a Comma b", "a , b"),
        ("a colon b", "a : b"),
        ("a Colon b", "a : b"),
        ("a semi colon b", "a ; b"),
        ("a Semi Colon b", "a ; b"),
        ("a semi Colon b", "a ; b"),
        ("a Semi colon b", "a ; b"),
        ("a semicolon b", "a ; b"),
        ("a Semicolon b", "a ; b"),
        ("wow exclamation mark", "wow !"),
        ("wow Exclamation Mark", "wow !"),
        ("wow Exclamation mark", "wow !"),
        ("wow exclamation Mark", "wow !"),
        ("one new line two", "one \n two"),
        ("one New Line two", "one \n two"),
        ("one New line two", "one \n two"),
        ("one new Line two", "one \n two"),
        ("one newline two", "one \n two"),
        ("one Newline two", "one \n two"),
        ("commas are not comma-separated", "commas are not ,-separated"),
        ("no punctuation words", "no punctuation words"),
    ],
)
def test_spoken_punctuation_becomes_symbols(speech_window, tk_root, said, written):
    assert record_and_stop(speech_window, tk_root, said) == written


def test_several_spoken_symbols_in_one_text(speech_window, tk_root):
    said = "dear sir comma new line thank you full stop"

    assert record_and_stop(speech_window, tk_root, said) == "dear sir , \n thank you ."


def test_writing_inserts_the_text_in_the_editor_and_closes_the_window(
    speech_window, tk_root
):
    put(speech_window.editor, "ab")
    speech_window.editor.type_.mark_set("insert", "1.1")
    speech_window.output.insert("end", "XYZ")

    speech_window.buttons["Write to Active Editor"].invoke()

    assert text_of(speech_window.editor) == "aXYZb"
    assert not speech_window.window.winfo_exists()


def test_writing_in_another_buffer_says_so(speech_window, tk_root):
    state.active = SimpleNamespace(hmode="normal")
    speech_window.output.insert("end", "XYZ")

    speech_window.buttons["Write to Active Editor"].invoke()

    wait_for_message(tk_root, "cannot write to current buffer")
    assert speech_window.window.winfo_exists()
