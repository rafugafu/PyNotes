"""The standalone Email buffer: login/account setup, composing and
sending mail via SMTP, attachments, and a simple dictionary-based
spellcheck."""

import os
import math as mathmod
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import state
from init import homedir, monospace
from encrypter import encryptdecrypt
from buffer import Buffer
from utils import bindrecur
import dialogs
import pycode
import utils
import window


class EmailBuffer(Buffer):
    """A buffer for logging into an email account and sending mail.
    Login credentials (e, p, s, po: email/password/smtp server/smtp
    port), once entered, are kept as module-level globals so other
    EmailBuffer instances/tabs can reuse the same session."""

    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.m = state.root.menu()
        for label, menu in state.all_buffer_menus.items():
            self.m.add_cascade(label=label, menu=menu)
        self.setwanttitle("*PyNotes Email*")
        self.fileinfoconfig(buffertype="*PyNotes Email*")
        self.mainwidget = self
        self._email_logged_in = False
        self._email_login_poll_after_id = None
        pycode.pcrunhook("before", "open-email-buffer")
        self._email_login_setup()
        self._email_login_poll()
        bindrecur(
            self,
            "<FocusIn>",
            lambda event, buffer=self: window.setactive(
                state.all_buffers.index(buffer)
            ),
        )
        pycode.pcrunhook("after", "open-email-buffer")

    def emailsetup(self, saved=None):
        """Build the email compose UI. saved controls where the login
        credentials come from: None reads them from the just-submitted
        login form (and optionally saves them, encrypted, to
        ~/.pynotesemailconfig); "file" loads and decrypts them from that
        config file; "memory" reuses the e/p/s/po globals already set by
        a previous call (e.g. reloading this tab or switching accounts).
        """
        global e
        global p
        global s
        global po
        attachments = []

        def removeattach():
            """Show a window of buttons, one per attachment, that each
            remove that attachment when clicked."""

            def actualremoveattachment(attachment):
                del self.attachmentslist[attachment]
                del attachments[attachment]
                self.attachmentslistwidget.config(
                    text="Attachments: " + " , ".join(self.attachmentslist)
                )
                raw.destroy()

            if self.attachmentslist:
                raw = state.root.subwin()
                for i in range(len(self.attachmentslist)):
                    attachment = self.attachmentslist[i]
                    raw.button(
                        text=attachment, command=lambda i=i: actualremoveattachment(i)
                    ).grid(column=i % 5, row=mathmod.floor(i / 5), sticky="ew")

        def attach():
            """Prompt for a file and add it as a pending email
            attachment (MIME part), unless already attached."""
            fn = dialogs.openfileget(
                prompttext="Email Attachment File: ", filetypes=(("All Files", "*"))
            )
            if fn:
                try:
                    with open(fn, "rb") as attachment:
                        part = MIMEBase("application", "octet-stream")
                        part.set_payload(attachment.read())
                        encoders.encode_base64(part)
                        part.add_header(
                            "Content-Disposition",
                            f"attachment; filename={os.path.basename(fn)}",
                        )
                        if os.path.basename(fn) not in self.attachmentslist:
                            attachments.append(part)
                            self.attachmentslist.append(os.path.basename(fn))
                            self.attachmentslistwidget.config(
                                text="Attachments: " + " , ".join(self.attachmentslist)
                            )
                except Exception as error:
                    error = str(error)
                    state.root.error("Error", error)

        def changeinfo():
            """Replace the compose UI with a login form pre-populated
            for re-entering account details ("Change Info" button)."""

            def emailsetupother():
                """Save the edited login details and restore the compose
                UI (the "Done" button of changeinfo()'s login form)."""
                global e
                global p
                global s
                global po
                self.entryframe.pack(
                    padx=10, pady=10, fill="x", anchor="n", expand=True
                )
                self.buttonframe.pack(
                    padx=10, pady=10, fill="x", anchor="n", expand=True
                )
                self.mainwidget = self.emailtextbox.text
                self.emailtextbox.pack(fill="both", expand=True, padx=10, pady=10)
                e = self.email.get()
                p = self.password.get()
                s = self.server.get()
                po = self.port.get()
                file = open(f"{homedir}/.pynotesemailconfig", "w+", encoding="utf-8")
                file.write(f"{e}\n{p}\n{s}\n{po}")
                file.close()
                encryptdecrypt(f"{homedir}/.pynotesemailconfig")
                self.loginframe.pack_forget()

            self.entryframe.pack_forget()
            self.buttonframe.pack_forget()
            self.emailtextbox.pack_forget()
            self.loginframe = state.root.frame(master=self)
            self.loginframe.pack(expand=True)
            state.root.text(master=self.loginframe, text="Email:").grid(
                column=0, row=0, padx=10, pady=10
            )
            self.email = state.root.entry(master=self.loginframe)
            self.email.grid(column=1, row=0, padx=10, pady=10)
            self.mainwidget = self.email
            state.root.text(master=self.loginframe, text="Password:").grid(
                column=0, row=1, padx=10, pady=10
            )
            self.password = state.root.entry(master=self.loginframe, show="*")
            self.password.grid(column=1, row=1, padx=10, pady=10)
            state.root.text(master=self.loginframe, text="Smtp Server:").grid(
                column=0, row=2, padx=10, pady=10
            )
            self.server = state.root.entry(master=self.loginframe)
            self.server.grid(column=1, row=2, padx=10, pady=10)
            state.root.text(master=self.loginframe, text="Smtp Port:").grid(
                column=0, row=3, padx=10, pady=10
            )
            self.port = state.root.entry(master=self.loginframe)
            self.port.grid(column=1, row=3, padx=10, pady=10)
            state.root.button(
                master=self.loginframe, text="Done", command=emailsetupother
            ).grid(column=1, row=4, padx=10, pady=10, sticky="e")
            bindrecur(
                self.loginframe,
                "<FocusIn>",
                lambda event, buffer=self: window.setactive(
                    state.all_buffers.index(buffer)
                ),
            )

        def sendemail():
            """Send the composed email (with attachments) to every
            comma-separated recipient over SMTP, then clear the compose
            form - unless a send fails, in which case an error is shown
            and the form is left as-is (recipients already sent to are
            not re-sent to on retry). Bound to the Send button and
            Control-Return."""
            global e
            global p
            global s
            global po
            recipients = self.recipiententry.get().split(",")
            subject = self.subjectentry.get()
            if not subject:
                subject = "(No Subject)"
            body = self.emailtextbox.get("1.0", "end-1c")
            for recipient in recipients:
                if recipient:
                    message = MIMEMultipart()
                    message["From"] = e
                    message["To"] = recipient
                    message["Subject"] = subject
                    message.attach(MIMEText(body, "plain"))
                    try:
                        for attachment in attachments:
                            message.attach(attachment)
                        with smtplib.SMTP_SSL(s, po) as server:
                            server.login(e, p)
                            server.sendmail(e, recipient, message.as_string())
                    except Exception as error:
                        error = str(error)
                        state.root.error("Error", error)
                        utils.show("email failed")
                        return
            self.emailtextbox.delete("1.0", "end")
            self.recipiententry.delete(0, "end")
            attachments.clear()
            self.attachmentslist.clear()
            self.attachmentslistwidget.config(text="Attachments:")
            self.subjectentry.delete(0, "end")
            utils.show("email sent")
            state.root.info("Info", "Email Sent Successfully!")
            return "break"

        def spellcheck():
            """Re-tag every word in the email body not found in
            state.emailwordlist (excluding purely numeric words and
            single-character words) as misspelled. Bound to run on
            every keystroke in the body."""
            if not state.emailwordlist:
                return
            self.emailtextbox.tag_remove("wrong", "1.0", "end")
            n = "1.0"
            search = r"\w+"
            while True:
                count = state.root.intvar()
                n = self.emailtextbox.search(
                    search, n, nocase=1, count=count, stopindex="end", regexp=True
                )
                if not n:
                    break
                nn = "%s+%dc" % (n, count.get())
                if (
                    self.emailtextbox.get(n, nn).lower() not in state.emailwordlist
                    and len(self.emailtextbox.get(n, nn)) > 1
                ):
                    try:
                        int(self.emailtextbox.get(n, nn))
                    except Exception:
                        self.emailtextbox.tag_add("wrong", n, nn)
                n = nn
            n = "1.0"

        if not saved:
            e = self.email.get()
            p = self.password.get()
            s = self.server.get()
            po = self.port.get()
            self.loginframe.pack_forget()
            self._email_logged_in = True
            ans = state.root.ask(
                "",
                "Do you want PyNotes to save your email and password?",
                ["yes", "no"],
            )
            if ans:
                file = open(f"{homedir}/.pynotesemailconfig", "w+", encoding="utf-8")
                file.write(f"{e}\n{p}\n{s}\n{po}")
                file.close()
                encryptdecrypt(f"{homedir}/.pynotesemailconfig")
        elif saved == "file":
            encryptdecrypt(f"{homedir}/.pynotesemailconfig")
            file = (
                open(f"{homedir}/.pynotesemailconfig", "r", encoding="utf-8")
                .read()
                .split("\n")
            )
            encryptdecrypt(f"{homedir}/.pynotesemailconfig")
            e = file[0]
            p = file[1]
            s = file[2]
            po = file[3]
        self._email_logged_in = True
        self.entryframe = state.root.frame(master=self)
        self.recipiententry = state.root.entry(master=self.entryframe)
        state.root.text(
            master=self.entryframe, text="Recipients (separate by commas):"
        ).grid(column=0, row=0, padx=10, pady=10, sticky="e")
        self.recipiententry.grid(column=1, row=0, padx=10, pady=10, sticky="ew")
        state.root.text(master=self.entryframe, text="Subject:").grid(
            column=0, row=1, padx=10, pady=10, sticky="e"
        )
        self.subjectentry = state.root.entry(master=self.entryframe)
        self.subjectentry.grid(column=1, row=1, padx=10, pady=10, sticky="ew")
        self.entryframe.pack(padx=10, pady=10, fill="both", anchor="n", expand=True)
        self.entryframe.columnconfigure(1, weight=1)
        self.buttonframe = state.root.frame(master=self)
        self.buttonframe.pack(padx=10, pady=10, fill="both", anchor="n", expand=True)
        state.root.button(
            master=self.buttonframe, text="Send (Ctrl + Enter)", command=sendemail
        ).pack(fill="x", expand=True, padx=10, pady=10, side="left", anchor="n")
        state.root.button(master=self.buttonframe, text="Attach", command=attach).pack(
            fill="x", expand=True, padx=10, pady=10, side="right", anchor="n"
        )
        state.root.button(
            master=self.buttonframe, text="Change Info", command=changeinfo
        ).pack(fill="x", expand=True, padx=10, pady=10, side="left", anchor="n")
        state.root.button(
            master=self.buttonframe, text="Remove Attachment", command=removeattach
        ).pack(fill="x", expand=True, padx=10, pady=10, side="right", anchor="n")
        self.attachmentslist = []
        self.attachmentslistwidget = state.root.text(
            master=self.buttonframe, text="Attachments:"
        )
        self.attachmentslistwidget.pack(fill="x", expand=True, padx=10, pady=10)
        self.emailtextbox = state.root.textbox(
            master=self, scrolled=True, font=(monospace, 15)
        )
        self.emailtextbox.tag_config("wrong", underline=True, underlinefg="red")
        self.mainwidget = self.emailtextbox.text
        self.emailtextbox.pack(fill="both", expand=True, padx=10, pady=10)
        self.emailtextbox.bind("<Control-Return>", lambda event: sendemail())
        self.emailtextbox.bind("<KeyRelease>", lambda event: spellcheck())
        bindrecur(
            self,
            "<FocusIn>",
            lambda event, buffer=self: window.setactive(
                state.all_buffers.index(buffer)
            ),
        )

    def _email_session_active(self):
        """Whether the e/p/s/po login-credential globals are currently
        set (an email session is already logged in, in this tab or
        another)."""
        try:
            e, p, s, po
        except Exception:
            return False
        return bool(e and p and s and po)

    def _add_switch_account_loginframe(self):
        """Add a login form (to switch to a different account) below
        the already-built compose UI."""
        self.loginframe = state.root.frame(master=self)
        self.loginframe.pack(expand=True)
        state.root.text(master=self.loginframe, text="Email:").grid(
            column=0, row=0, padx=10, pady=10
        )
        self.email = state.root.entry(master=self.loginframe)
        self.email.grid(column=1, row=0, padx=10, pady=10)
        state.root.text(master=self.loginframe, text="Password:").grid(
            column=0, row=1, padx=10, pady=10
        )
        self.password = state.root.entry(master=self.loginframe, show="*")
        self.password.grid(column=1, row=1, padx=10, pady=10)
        state.root.text(master=self.loginframe, text="Smtp Server:").grid(
            column=0, row=2, padx=10, pady=10
        )
        self.server = state.root.entry(master=self.loginframe)
        self.server.grid(column=1, row=2, padx=10, pady=10)
        state.root.text(master=self.loginframe, text="Smtp Port:").grid(
            column=0, row=3, padx=10, pady=10
        )
        self.port = state.root.entry(master=self.loginframe)
        self.port.grid(column=1, row=3, padx=10, pady=10)
        state.root.button(
            master=self.loginframe, text="Let's Go!", command=self.emailsetup
        ).grid(column=1, row=4, padx=10, pady=10, sticky="e")
        bindrecur(
            self.loginframe,
            "<FocusIn>",
            lambda event, buffer=self: window.setactive(
                state.all_buffers.index(buffer)
            ),
        )

    def _email_tab_reload(self):
        """Rebuild this buffer's UI from scratch as the compose UI for
        the now-active (memory) session, once _email_login_poll() sees
        another tab has logged in."""
        for child in self.winfo_children():
            if child is self.fileinfo:
                continue
            child.destroy()
        self.emailsetup("memory")
        self._add_switch_account_loginframe()

    def _email_login_poll(self):
        """Every 2 seconds, check whether this still-logged-out buffer
        should switch to the compose UI because another EmailBuffer
        logged in (or loaded a saved session) in the meantime."""
        if not self.winfo_exists():
            return
        if not self._email_logged_in and self._email_session_active():
            self._email_tab_reload()
        self._email_login_poll_after_id = self.after(2000, self._email_login_poll)

    def _email_login_setup(self):
        """Build this buffer's initial UI: the compose UI directly if a
        session is already active or a saved config file exists (and
        loads successfully), otherwise a login form."""
        if self._email_session_active():
            self.emailsetup("memory")
            self._add_switch_account_loginframe()
            return
        try:
            open(f"{homedir}/.pynotesemailconfig", "r", encoding="utf-8")
        except Exception:
            self.loginframe = state.root.frame(master=self)
            self.loginframe.pack(expand=True)
            state.root.text(master=self.loginframe, text="Email:").grid(
                column=0, row=0, padx=10, pady=10
            )
            self.email = state.root.entry(master=self.loginframe)
            self.email.grid(column=1, row=0, padx=10, pady=10)
            state.root.text(master=self.loginframe, text="Password:").grid(
                column=0, row=1, padx=10, pady=10
            )
            self.password = state.root.entry(master=self.loginframe, show="*")
            self.password.grid(column=1, row=1, padx=10, pady=10)
            state.root.text(master=self.loginframe, text="Smtp Server:").grid(
                column=0, row=2, padx=10, pady=10
            )
            self.server = state.root.entry(master=self.loginframe)
            self.server.grid(column=1, row=2, padx=10, pady=10)
            state.root.text(master=self.loginframe, text="Smtp Port:").grid(
                column=0, row=3, padx=10, pady=10
            )
            self.port = state.root.entry(master=self.loginframe)
            self.port.grid(column=1, row=3, padx=10, pady=10)
            state.root.button(
                master=self.loginframe, text="Let's Go!", command=self.emailsetup
            ).grid(column=1, row=4, padx=10, pady=10, sticky="e")
            self.mainwidget = self.email
            bindrecur(
                self.loginframe,
                "<FocusIn>",
                lambda event, buffer=self: window.setactive(
                    state.all_buffers.index(buffer)
                ),
            )
        else:
            try:
                self.emailsetup("file")
            except Exception:
                state.root.error(
                    "Error", "The saved email details are corrupted. Remaking file."
                )
                os.remove(f"{homedir}/.pynotesemailconfig")
            self._add_switch_account_loginframe()

    def close(self):
        """Always allow this buffer to close without a save prompt (an
        email buffer has nothing unsaved to lose)."""
        return True

    def _cancel_all_after_ids(self):
        """Cancel the pending _email_login_poll() callback, if any."""
        if self._email_login_poll_after_id is not None:
            try:
                self.after_cancel(self._email_login_poll_after_id)
            except Exception:
                pass
            self._email_login_poll_after_id = None


def find_open_emailbuf():
    """Return the already-open EmailBuffer, if any."""
    for buffer in state.all_buffers:
        if isinstance(buffer, EmailBuffer):
            return buffer


def openemailbuf(orient="horizontal"):
    """Switch to the Email buffer if one is already open, otherwise
    open a new one."""
    existing = find_open_emailbuf()
    if existing is not None:
        window.setactive(state.all_buffers.index(existing))
        utils.show("switched to email buffer")
        return existing
    newbuff = window.newbuffer(EmailBuffer, orient)
    utils.show("opened email buffer")
    return newbuff
