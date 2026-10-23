"""The Email buffer: logging in or loading the saved account, composing and
sending mail (over a stand-in for the SMTP server), attachments, and the
spellcheck."""

import email
from types import SimpleNamespace

import canvastk as ctk
import pytest

import dialogs
import pynotesemail
import state
import window
from encrypter import encryptdecrypt
from test_editor import editor, put, wait_for, wait_for_message
from test_utils import console_messages  # noqa: F401  (a fixture)

pytestmark = pytest.mark.display


def descendants(widget):
    for child in widget.winfo_children():
        yield child
        yield from descendants(child)


def buttons_of(widget):
    return {w.cget("text"): w for w in descendants(widget) if isinstance(w, ctk.Button)}


def entries_of(widget):
    return [w for w in descendants(widget) if isinstance(w, ctk.Entry)]


class FakeSMTP:
    """The SMTP server: remembers what was sent."""

    sessions = []
    fail_on = None

    def __init__(self, server, port):
        self.server, self.port = server, port
        self.logins = []
        self.sent = []
        FakeSMTP.sessions.append(self)

    def __enter__(self):
        return self

    def __exit__(self, *arguments):
        return False

    def login(self, user, password):
        if FakeSMTP.fail_on == "login":
            raise RuntimeError("bad login")
        self.logins.append((user, password))

    def sendmail(self, sender, recipient, text):
        if FakeSMTP.fail_on == recipient:
            raise RuntimeError(f"cannot send to {recipient}")
        self.sent.append((sender, recipient, text))


@pytest.fixture
def mail(app, tk_root, editor, tmp_path, monkeypatch, console_messages):
    """A clean email state: no session, no saved account, SMTP faked."""
    for name in ("e", "p", "s", "po"):
        monkeypatch.delattr(pynotesemail, name, raising=False)
    FakeSMTP.sessions = []
    FakeSMTP.fail_on = None
    monkeypatch.setattr(pynotesemail.smtplib, "SMTP_SSL", FakeSMTP)
    state.emailwordlist = []
    config = app.home / ".pynotesemailconfig"
    return SimpleNamespace(config=config, root=tk_root, app=app)


def open_mail():
    return pynotesemail.openemailbuf()


def log_in(
    buffer,
    address="me@example.com",
    password="secret",
    server="smtp.example.com",
    port="465",
):
    fields = entries_of(buffer.loginframe)
    for field, value in zip(fields, (address, password, server, port)):
        field.delete(0, "end")
        field.insert(0, value)
    buttons_of(buffer.loginframe)["Let's Go!"].invoke()


def write_account(config, lines="me@example.com\nsecret\nsmtp.example.com\n465"):
    config.write_text(lines)
    encryptdecrypt(str(config))


# ---------------------------------------------------------------------------
# Opening the buffer
# ---------------------------------------------------------------------------


def test_opening_the_email_buffer_makes_a_new_active_buffer(mail):
    buffer = open_mail()

    assert isinstance(buffer, pynotesemail.EmailBuffer)
    assert state.active is buffer
    assert buffer.wanttitle == "*PyNotes Email*"
    assert buffer.close() is True


def test_opening_it_again_switches_to_the_open_one(mail):
    first = open_mail()
    window.neweditor()
    assert state.active is not first

    second = open_mail()

    assert second is first
    assert state.active is first
    assert sum(isinstance(b, pynotesemail.EmailBuffer) for b in state.all_buffers) == 1


def test_finding_the_open_email_buffer(mail):
    assert pynotesemail.find_open_emailbuf() is None

    buffer = open_mail()

    assert pynotesemail.find_open_emailbuf() is buffer


def test_opening_runs_the_hooks(mail):
    seen = []
    state.pcbeforehooks["open-email-buffer"] = [lambda value: seen.append("before")]
    state.pcafterhooks["open-email-buffer"] = [lambda value: seen.append("after")]

    open_mail()

    assert seen == ["before", "after"]


# ---------------------------------------------------------------------------
# Logging in
# ---------------------------------------------------------------------------


def test_without_a_saved_account_the_buffer_shows_a_login_form(mail):
    buffer = open_mail()

    labels = [
        w.cget("text")
        for w in descendants(buffer.loginframe)
        if isinstance(w, ctk.Label)
    ]
    assert labels == ["Email:", "Password:", "Smtp Server:", "Smtp Port:"]
    assert set(buttons_of(buffer.loginframe)) == {"Let's Go!"}
    assert buffer._email_logged_in is False
    assert buffer.password.cget("show") == "*"


def test_logging_in_shows_the_compose_form(mail):
    buffer = open_mail()
    mail.app.dialogs.answer("ask", False)

    log_in(buffer)

    assert buffer._email_logged_in is True
    assert pynotesemail.e == "me@example.com"
    assert (pynotesemail.p, pynotesemail.s, pynotesemail.po) == (
        "secret",
        "smtp.example.com",
        "465",
    )
    assert set(buttons_of(buffer.buttonframe)) == {
        "Send (Ctrl + Enter)",
        "Attach",
        "Change Info",
        "Remove Attachment",
    }
    assert not mail.config.exists()


def test_logging_in_can_save_the_account_encrypted(mail):
    buffer = open_mail()
    mail.app.dialogs.answer("ask", True)

    log_in(buffer)

    assert mail.config.exists()
    assert "secret" not in mail.config.read_text(errors="replace")
    encryptdecrypt(str(mail.config))
    assert mail.config.read_text() == "me@example.com\nsecret\nsmtp.example.com\n465"
    assert "save your email and password" in mail.app.dialogs.messages("ask")[0]


def test_a_saved_account_opens_the_compose_form_at_once(mail):
    write_account(mail.config)

    buffer = open_mail()

    assert buffer._email_logged_in is True
    assert (pynotesemail.e, pynotesemail.p) == ("me@example.com", "secret")
    assert (pynotesemail.s, pynotesemail.po) == ("smtp.example.com", "465")
    assert hasattr(buffer, "emailtextbox")


def test_reading_the_saved_account_leaves_the_file_encrypted(mail):
    write_account(mail.config)
    before = mail.config.read_bytes()

    open_mail()

    assert mail.config.read_bytes() == before


def test_a_saved_account_also_offers_a_form_for_another_account(mail):
    write_account(mail.config)

    buffer = open_mail()

    assert "Let's Go!" in buttons_of(buffer.loginframe)


def test_a_corrupted_saved_account_is_reported_and_removed(mail):
    mail.config.write_text("only one line")
    encryptdecrypt(str(mail.config))

    buffer = open_mail()

    assert "saved email details are corrupted" in mail.app.dialogs.messages("error")[0]
    assert not mail.config.exists()
    assert "Let's Go!" in buttons_of(buffer.loginframe)


def test_a_second_buffer_uses_the_account_already_logged_into(mail):
    first = open_mail()
    mail.app.dialogs.answer("ask", False)
    log_in(first)
    second = pynotesemail.newbuffer(pynotesemail.EmailBuffer, "horizontal")

    assert second._email_logged_in is True
    assert hasattr(second, "emailtextbox")


def test_a_logged_out_buffer_follows_another_that_logs_in(mail):
    first = open_mail()
    second = pynotesemail.newbuffer(pynotesemail.EmailBuffer, "horizontal")
    assert second._email_logged_in is False
    mail.app.dialogs.answer("ask", False)
    log_in(first)

    second._email_login_poll()

    assert second._email_logged_in is True
    assert hasattr(second, "emailtextbox")
    first._cancel_all_after_ids()
    second._cancel_all_after_ids()


def test_the_login_poll_stops_with_the_buffer(mail):
    buffer = open_mail()
    assert buffer._email_login_poll_after_id is not None

    buffer._cancel_all_after_ids()

    assert buffer._email_login_poll_after_id is None
    buffer._cancel_all_after_ids()


def test_change_info_shows_a_form_and_saves_the_new_account(mail):
    write_account(mail.config)
    buffer = open_mail()

    buttons_of(buffer.buttonframe)["Change Info"].invoke()
    for field, value in zip(
        (buffer.email, buffer.password, buffer.server, buffer.port),
        ("new@example.com", "newpass", "smtp.new.com", "587"),
    ):
        field.insert(0, value)
    buttons_of(buffer.loginframe)["Done"].invoke()

    assert (pynotesemail.e, pynotesemail.p) == ("new@example.com", "newpass")
    assert (pynotesemail.s, pynotesemail.po) == ("smtp.new.com", "587")
    encryptdecrypt(str(mail.config))
    assert mail.config.read_text() == "new@example.com\nnewpass\nsmtp.new.com\n587"


# ---------------------------------------------------------------------------
# Sending
# ---------------------------------------------------------------------------


@pytest.fixture
def composing(mail):
    write_account(mail.config)
    buffer = open_mail()
    mail.buffer = buffer
    mail.send = buttons_of(buffer.buttonframe)["Send (Ctrl + Enter)"]
    return mail


def fill(buffer, recipients="you@example.com", subject="Hello", body="Body text"):
    buffer.recipiententry.insert(0, recipients)
    buffer.subjectentry.insert(0, subject)
    buffer.emailtextbox.insert("1.0", body)


def sent_message(index=0):
    (session,) = FakeSMTP.sessions[index : index + 1]
    return session, email.message_from_string(session.sent[0][2])


def test_sending_a_message(composing):
    fill(composing.buffer)

    composing.send.invoke()

    session, message = sent_message()
    assert (session.server, session.port) == ("smtp.example.com", "465")
    assert session.logins == [("me@example.com", "secret")]
    assert session.sent[0][:2] == ("me@example.com", "you@example.com")
    assert message["From"] == "me@example.com"
    assert message["To"] == "you@example.com"
    assert message["Subject"] == "Hello"
    assert message.get_payload()[0].get_payload() == "Body text"


def test_every_recipient_gets_the_message(composing):
    fill(composing.buffer, recipients="a@example.com,b@example.com,,c@example.com")

    composing.send.invoke()

    recipients = [session.sent[0][1] for session in FakeSMTP.sessions]
    assert recipients == ["a@example.com", "b@example.com", "c@example.com"]


def test_a_message_without_a_subject_gets_a_placeholder(composing):
    fill(composing.buffer, subject="")

    composing.send.invoke()

    assert sent_message()[1]["Subject"] == "(No Subject)"


def test_sending_clears_the_form_and_says_so(composing, tk_root):
    fill(composing.buffer)

    composing.send.invoke()

    buffer = composing.buffer
    assert buffer.recipiententry.get() == ""
    assert buffer.subjectentry.get() == ""
    assert buffer.emailtextbox.get("1.0", "end-1c") == ""
    assert buffer.attachmentslistwidget.cget("text") == "Attachments:"
    assert ("info", "Info", "Email Sent Successfully!") in composing.app.dialogs.calls
    wait_for_message(tk_root, "email sent")


def test_a_failed_send_keeps_the_form_and_reports_the_error(composing, tk_root):
    fill(composing.buffer)
    FakeSMTP.fail_on = "you@example.com"

    composing.send.invoke()

    buffer = composing.buffer
    assert buffer.emailtextbox.get("1.0", "end-1c") == "Body text"
    assert buffer.recipiententry.get() == "you@example.com"
    assert composing.app.dialogs.messages("error") == ["cannot send to you@example.com"]
    wait_for_message(tk_root, "email failed")


def test_a_failed_login_is_reported(composing, tk_root):
    fill(composing.buffer)
    FakeSMTP.fail_on = "login"

    composing.send.invoke()

    assert composing.app.dialogs.messages("error") == ["bad login"]
    assert composing.buffer.subjectentry.get() == "Hello"


def test_sending_stops_at_the_first_recipient_that_fails(composing):
    fill(composing.buffer, recipients="a@example.com,bad@example.com,c@example.com")
    FakeSMTP.fail_on = "bad@example.com"

    composing.send.invoke()

    sent_to = [s.sent[0][1] for s in FakeSMTP.sessions if s.sent]
    assert sent_to == ["a@example.com"]


def test_control_return_sends_too(composing):
    from test_utils import run_binding

    fill(composing.buffer)

    run_binding(composing.buffer.emailtextbox.inner, "<Control-Return>")

    assert FakeSMTP.sessions and FakeSMTP.sessions[0].sent


# ---------------------------------------------------------------------------
# Attachments
# ---------------------------------------------------------------------------


@pytest.fixture
def attaching(composing, tmp_path, monkeypatch):
    chosen = []
    calls = []

    def openfileget(*arguments, **keywords):
        calls.append(keywords)
        return chosen[-1] if chosen else ""

    monkeypatch.setattr(dialogs, "openfileget", openfileget)
    composing.chosen = chosen
    composing.calls = calls
    composing.directory = tmp_path
    return composing


def attach_file(attaching, name, content=b"data"):
    path = attaching.directory / name
    path.write_bytes(content)
    attaching.chosen.append(str(path))
    buttons_of(attaching.buffer.buttonframe)["Attach"].invoke()
    return path


def test_an_attachment_is_listed_and_sent(attaching):
    attach_file(attaching, "notes.txt", b"hello attachment")
    fill(attaching.buffer)

    assert (
        attaching.buffer.attachmentslistwidget.cget("text") == "Attachments: notes.txt"
    )
    attaching.send.invoke()

    _, message = sent_message()
    parts = message.get_payload()
    assert len(parts) == 2
    assert parts[1].get_filename() == "notes.txt"
    assert parts[1].get_payload(decode=True) == b"hello attachment"


def test_several_attachments_are_listed_together(attaching):
    attach_file(attaching, "a.txt")
    attach_file(attaching, "b.txt")

    assert (
        attaching.buffer.attachmentslistwidget.cget("text")
        == "Attachments: a.txt , b.txt"
    )


def test_the_same_file_is_not_attached_twice(attaching):
    attach_file(attaching, "a.txt")
    attaching.chosen.append(str(attaching.directory / "a.txt"))
    buttons_of(attaching.buffer.buttonframe)["Attach"].invoke()

    assert attaching.buffer.attachmentslist == ["a.txt"]


def test_choosing_no_file_attaches_nothing(attaching):
    buttons_of(attaching.buffer.buttonframe)["Attach"].invoke()

    assert attaching.buffer.attachmentslist == []


def test_an_unreadable_attachment_is_reported(attaching):
    attaching.chosen.append(str(attaching.directory / "missing.txt"))

    buttons_of(attaching.buffer.buttonframe)["Attach"].invoke()

    assert attaching.app.dialogs.of_kind("error")
    assert attaching.buffer.attachmentslist == []


def test_removing_an_attachment(attaching, tk_root, monkeypatch):
    windows = []
    original = type(tk_root).subwin

    def subwin(*arguments, **keywords):
        top = original(tk_root, *arguments, **keywords)
        top.withdraw()
        windows.append(top)
        return top

    monkeypatch.setattr(tk_root, "subwin", subwin, raising=False)
    attach_file(attaching, "a.txt")
    attach_file(attaching, "b.txt")

    buttons_of(attaching.buffer.buttonframe)["Remove Attachment"].invoke()
    (window_,) = windows
    buttons_of(window_)["a.txt"].invoke()

    assert attaching.buffer.attachmentslist == ["b.txt"]
    assert attaching.buffer.attachmentslistwidget.cget("text") == "Attachments: b.txt"
    assert not window_.winfo_exists()
    fill(attaching.buffer)
    attaching.send.invoke()
    assert len(sent_message()[1].get_payload()) == 2


def test_removing_with_no_attachments_opens_nothing(attaching, tk_root, monkeypatch):
    windows = []
    monkeypatch.setattr(
        tk_root, "subwin", lambda *a, **k: windows.append(1), raising=False
    )

    buttons_of(attaching.buffer.buttonframe)["Remove Attachment"].invoke()

    assert windows == []


def test_sending_clears_the_attachments(attaching):
    attach_file(attaching, "a.txt")
    fill(attaching.buffer)

    attaching.send.invoke()

    assert attaching.buffer.attachmentslist == []


# ---------------------------------------------------------------------------
# The spellcheck
# ---------------------------------------------------------------------------


def misspelled(buffer):
    ranges = [str(i) for i in buffer.emailtextbox.tag_ranges("wrong")]
    return [buffer.emailtextbox.get(a, b) for a, b in zip(ranges[0::2], ranges[1::2])]


def type_and_release(buffer, text):
    from test_utils import run_binding

    buffer.emailtextbox.insert("1.0", text)
    run_binding(buffer.emailtextbox.inner, "<KeyRelease>")


def test_unknown_words_are_underlined(composing):
    state.emailwordlist = ["hello", "world"]

    type_and_release(composing.buffer, "Hello wrold World")

    assert misspelled(composing.buffer) == ["wrold"]


def test_numbers_and_single_letters_are_not_misspelled(composing):
    state.emailwordlist = ["hello"]

    type_and_release(composing.buffer, "hello 123 a b2c")

    assert misspelled(composing.buffer) == ["b2c"]


def test_the_spellcheck_forgets_old_marks(composing):
    state.emailwordlist = ["hello"]
    type_and_release(composing.buffer, "hello wrold")
    assert misspelled(composing.buffer) == ["wrold"]

    composing.buffer.emailtextbox.delete("1.0", "end")
    type_and_release(composing.buffer, "hello")

    assert misspelled(composing.buffer) == []


def test_without_a_word_list_nothing_is_marked(composing):
    state.emailwordlist = []

    type_and_release(composing.buffer, "zxqv")

    assert misspelled(composing.buffer) == []
