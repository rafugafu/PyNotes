"""Command-line argument parsing and the live terminal console that runs
alongside the PyNotes GUI (see main.py's start_console thread), letting
the launching terminal show status messages, mirror dialogs, and accept
commands (including answering dialogs/prompts before the GUI does)."""

from init import exit
import state
import os
import sys
import select
import subprocess
import shutil
import threading
import platform

if platform.system() == "Linux":
    import termios
    import tty

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)

    def set_raw_mode():
        """Put stdin into raw mode so keys can be read one at a time."""
        tty.setraw(fd)

    def unset_raw_mode():
        """Restore stdin's original terminal settings."""
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    def get_key():
        """Block for and return the next single character from stdin."""
        return sys.stdin.read(1)

else:
    import msvcrt

    def set_raw_mode():
        # msvcrt.getch() already reads unbuffered/unechoed, no raw-mode
        # setup needed on Windows.
        pass

    def unset_raw_mode():
        pass

    def get_key():
        """Block for and return the next single character from stdin."""
        return msvcrt.getch().decode("utf-8", errors="ignore")


# Help text for --help (claht) and the console's "help" command (clcht).
claht = """\
\x1b[1mCommand line arguments:\x1b[0m
\x1b[3m--version\x1b[0m: Print the current PyNotes version number.
\x1b[3m--changes\x1b[0m: Print the current PyNotes version's changelog.
\x1b[3m--wait-start\x1b[0m: Does not launch the PyNotes window till 'start' is typed into the console.
\x1b[3m--plugin-list-github\x1b[0m: List the plugins on the PyNotes GitHub with a one line description for each.
\x1b[3m--plugin-list-installed\x1b[0m: List the currently installed plugins with a one line description for each if provided.
\x1b[3m--plugin-install "name"\x1b[0m: Installs the given plugin from the PyNotes GitHub if present.
\x1b[3m--plugin-remove "name"\x1b[0m: Uninstalls the given plugin if installed.
\x1b[3m--plugin-describe "name"\x1b[0m: Give a full description of the given plugin if installed and provided, fallback to checking in the PyNotes GitHub if not.
\x1b[3m--no-load-pycode\x1b[0m: Start PyNotes without loading your PyCode configuration until you open and close PyCode yourself.
\x1b[3m--no-load-plugins\x1b[0m: Start PyNotes without loading any plugins.
\x1b[3m--pycode-exec "string"\x1b[0m: Execute the given string as PyCode after loading your normal configuration.
\x1b[3m--command-exec "string"\x1b[0m: Execute the given string as Alt-X commands.\
"""
clcht = """\
\x1b[1mConsole:\x1b[0m
PyNotes has a live cli console in the launching terminal which can interact with and control PyNotes while it runs. Commands:
'\x1b[3mstart\x1b[0m' - Finally shows the PyNotes window if the \x1b[3m--wait-start\x1b[0m option was used.
'\x1b[3mcommand-exec {command}\x1b[0m' - Runs the given command as an Alt-X command after 'start' is done.
'\x1b[3mpycode-eval {command}\x1b[0m' - Directly takes and evaluates a single PyCode expression after 'start' is done.
'\x1b[3mextra-pycode\x1b[0m' - If the \x1b[3m--wait-start\x1b[0m option was used, take normal PyCode code as if it was passed to --pycode-exec at the start until exactly 'DONE' or 'CANCEL' is typed on a new line before 'start' is done. If 'CANCEL' is typed, it cancels the whole command.
'\x1b[3mopen-file {optional filename}\x1b[0m' - Prompts for a filename if not given directly and opens it in a new editor after 'start' is done.
'\x1b[3mexit\x1b[0m' / '\x1b[3mclose\x1b[0m' - Cleanly exits PyNotes after prompting to save files and close running processes.
'\x1b[31m\x1b[3mkill\x1b[0m' - Forcefully kills PyNotes without saving any files or cleaning up.
'\x1b[3mrun {optional command}\x1b[0m' - Prompts for a shell command to run in the same terminal if not given directly and runs it.
'\x1b[3mclear\x1b[0m' - Clears the terminal screen.
'\x1b[3mhelp\x1b[0m' - Shows help on the PyNotes terminal console (this screen).\
"""


def argparse(options, args):
    """Parse args (PyNotes' own --option/--option=value command-line
    syntax) against the given options spec and return (parsed_options,
    files_to_open).

    options maps each recognized option name to a sentinel describing
    its shape:
      - False: a boolean flag taking no value; ends up True if given,
        False otherwise.
      - True: a flag taking one string value (--opt value or
        --opt=value); ends up as that string if given, None otherwise.
      - [True]: a repeatable flag taking one value per occurrence
        (--opt a --opt b -> ['a', 'b']); ends up as a list, empty if
        never given. Only one value is consumed per occurrence; extra
        bare arguments after it are treated as files to open, not
        additional values.
    Any argument that isn't consumed as an option/value is collected
    into files_to_open. Unknown options or malformed usage print an
    error and exit(1).
    """
    options = {
        key: (item if item != [True] else []) for key, item in options.copy().items()
    }
    exitwith = lambda message: [print(message), exit(1)]
    curarg = None
    files_to_open = []
    for arg in args:
        if not curarg and not arg.startswith("--"):
            files_to_open.append(arg)
            continue
        if curarg and options[curarg] in (False, None) and not arg.startswith("--"):
            files_to_open.append(arg)
            continue
        if arg.startswith("--"):
            if curarg and options[curarg] not in (False, None):
                exitwith(f'unexpected "{arg}" after option "--{curarg}"')
            arg = arg[2:]
        if curarg and options[curarg] in (False, None):
            curarg = None
        if not curarg:
            if "=" in arg:
                opn, opv = arg.split("=", 1)
                if opn not in options:
                    exitwith(f'error: unknown option "--{opn}"')
                if options[opn] == True:
                    options[opn] = opv
                elif type(options[opn]) == list:
                    options[opn].append(opv)
                elif options[opn] in (False, None):
                    exitwith(f'error: option "--{opn}" does not take any argument')
                else:
                    exitwith(f'error: repeated argument "--{arg}"')
            else:
                if arg not in options:
                    exitwith(f'error: unknown option "--{arg}"')
                if options[arg] == True or type(options[arg]) == list:
                    curarg = arg
                elif options[arg] == False:
                    curarg = arg
                    options[arg] = None
                else:
                    exitwith(f'error: repeated argument "--{arg}"')
        elif curarg:
            if type(options[curarg]) == list:
                options[curarg].append(arg)
            else:
                options[curarg] = arg
            curarg = None
    if curarg and options[curarg] not in (False, None):
        exitwith(f'error: unspecified option "{curarg}"')
    for option in options:
        if options[option] is None:
            options[option] = True
        elif options[option] == True:
            options[option] = None
    return options, files_to_open


class Console:
    """The live terminal console: renders a `> ` command prompt and
    ANSI-drawn dialogs/messages in the launching terminal, and answers
    PyNotes' own commands (start, command-exec, exit, ...). Runs its own
    raw-mode key-reading loop on a background thread (inputloop) so
    dialog methods (show/dialog/ask/prompt) can be called from any
    thread while a separate "dialog" input channel is multiplexed with
    the main "command" prompt (see curactiveinput)."""

    def __init__(self, consoleq):
        """consoleq: the queue.Queue that commands (e.g. ("command-exec",
        text)) are put on, which main.py's consoleqempty() polls and
        runs on the GUI thread."""
        import init

        self.dialoglock = threading.Lock()
        self.q = consoleq
        self.curinput = {"command": "", "dialog": ""}
        self.cursors = {"command": 0, "dialog": 0}
        self.curecho = {"command": True, "dialog": True}
        self.curdoneevents = {}
        self.curresults = {}
        self.curactiveinput = "command"
        threading.Thread(target=self.inputloop, daemon=True).start()
        self.outpt("\x1b[H\x1b[2J", end="")
        self.outpt(f"\x1b[1mPyNotes terminal console. PyNotes v{init.v}.\x1b[0m")
        thefiles = []
        for file in state.files_to_open:
            thefiles.append(f"\x1b[3m{file}\x1b[0m")
        if thefiles:
            self.outpt(f"\x1b[1mOpening Files:\x1b[0m {', '.join(thefiles)}")
        theargs = []
        for arg, val in state.options.items():
            if val == True:
                theargs.append(f"\x1b[3m--{arg}\x1b[0m")
            elif val:
                val = val.replace("\n", "")
                if len(val) > 18:
                    val = val[:15] + "\x1b[1m..."
                theargs.append(f"\x1b[3m--{arg} {val}\x1b[0m")
        if theargs:
            self.outpt(f"\x1b[1mStarting with Arguments:\x1b[0m {', '.join(theargs)}")

    def outpt(self, string, end="\n", *args, **kwargs):
        """Write string (with every \\n also carriage-returned, since
        the terminal is in raw mode) to the real stdout PyNotes saved
        before redirecting sys.stdout to /dev/null."""
        string += end
        string = string.replace("\n", "\n\r")
        return print(string, end="", file=state.stdout, flush=True, *args, **kwargs)

    def inputloop(self):
        """Background-thread loop: read raw keys and maintain the
        current line buffer/cursor for whichever input is active
        (curactiveinput: "command" or "dialog"), handling backspace,
        arrow keys, and delete via their ANSI escape sequences, and
        signalling inpt()'s waiting caller via curdoneevents on Enter."""
        while True:
            key = get_key()
            user = self.curactiveinput
            buf = self.curinput[user]
            cursor = self.cursors[user]
            echo = self.curecho[user]
            if key == "\r":
                doneevent = self.curdoneevents.get(user)
                self.curresults[user] = buf
                self.curinput[user] = ""
                self.cursors[user] = 0
                self.outpt("")
                if doneevent:
                    doneevent.set()
            elif key in ("\x7f", "\x08"):
                if cursor == 0:
                    continue
                if echo:
                    self.outpt("\x1b[D\x1b[P", end="")
                self.curinput[user] = buf[: cursor - 1] + buf[cursor:]
                self.cursors[user] = cursor - 1
            elif key == "\x1b":
                second = None
                third = None
                while not second:
                    second = get_key()
                while not third:
                    third = get_key()
                if second + third == "[D":
                    if cursor == 0:
                        continue
                    self.cursors[user] = cursor - 1
                    if echo:
                        self.outpt("\x1b[D", end="")
                elif second + third == "[C":
                    if cursor == len(buf):
                        continue
                    self.cursors[user] = cursor + 1
                    if echo:
                        self.outpt("\x1b[C", end="")
                elif second + third == "[A":
                    self.cursors[user] = 0
                    if echo:
                        self.outpt(f"\x1b[{cursor}D", end="")
                elif second + third == "[B":
                    self.cursors[user] = len(self.curinput[user])
                    if echo:
                        self.outpt(f"\x1b[{len(self.curinput[user]) - cursor}C", end="")
                elif second + third == "[3":
                    fourth = None
                    while not fourth:
                        fourth = get_key()
                    if cursor == len(buf):
                        continue
                    if echo:
                        self.outpt("\x1b[P", end="")
                    self.curinput[user] = buf[:cursor] + buf[cursor + 1 :]
            elif key == "\t":
                continue
            else:
                if echo:
                    self.outpt("\x1b[@" + key, end="")
                self.curinput[user] = buf[:cursor] + key + buf[cursor:]
                self.cursors[user] = cursor + 1

    def inpt(self, prompt, echo=True, cancel_event=None):
        """Print prompt, then block until inputloop() records an Enter
        for the current input channel and return the entered line (with
        echo controlling whether typed characters are shown), or None if
        cancel_event is set first (e.g. because a graphical dialog
        answered instead)."""
        self.outpt(prompt, end="")
        user = self.curactiveinput
        self.curecho[user] = echo
        doneevent = threading.Event()
        self.curdoneevents[user] = doneevent
        while not doneevent.wait(timeout=0.1):
            if cancel_event and cancel_event.is_set():
                self.curdoneevents.pop(user, None)
                self.outpt("")
                return
        self.curdoneevents.pop(user, None)
        return self.curresults.pop(user, "")

    def show(self, text):
        """Mirror a utils.show() status message above the command
        prompt line (mirrors PyNotes' Alt-X command box)."""
        with self.dialoglock:
            if not (text := text.strip()):
                return
            # self.n (set by loop()) is how many extra lines the current
            # command prompt has printed below it (e.g. from a nested
            # sub-prompt); moveback re-descends past them so the message
            # is drawn just above the prompt line, using cursor Home
            # instead while the full-screen help text (self.helping) is
            # showing, since its layout doesn't follow the prompt line.
            if self.n:
                moveback = f"\x1b[{self.n}B"
            else:
                moveback = ""
            if self.helping:
                moveback = "\x1b[H"
            self.outpt(
                f"\x1b7{moveback}\x1b[L\r\x1b[7mmessage: \x1b[3m{text}\x1b[0m\x1b8\x1b[B",
                end="",
            )

    def dialog(self, title, message, color="100m"):
        """Draw a non-interactive titled message box (mirrors
        info/error/warning) above the command prompt. color is an ANSI
        SGR background-color code fragment, e.g. "41m" for error (red),
        "43m" for warning (yellow)."""
        with self.dialoglock:
            import textwrap

            width = min(shutil.get_terminal_size()[0], 80)
            if len(title) > width:
                title = title[: width - 3] + "..."
            text = textwrap.fill(message, width=width) + "\n"
            spacing = " " * ((width - len(title)) // 2)
            if self.n:
                moveback = f"\x1b[{self.n}B"
            else:
                moveback = ""
            if self.helping:
                moveback = "\x1b[H"
            text = "\n".join(line.ljust(width) for line in text.split("\n"))
            self.outpt(
                f'\x1b7{moveback}\x1b[L\r\x1b[{color}\x1b[7m{spacing}\x1b[1m{title}\x1b[22m{spacing}{" " * ((width - len(title)) % 2)}\x1b[27m\n{text}\x1b[0m\x1b8\x1b[{text.count("\n") + 2}B'.replace(
                    "\n", f"\x1b[49m\n\x1b[L\x1b[{color}"
                ),
                end="",
            )

    def ask(self, title, question, options, color="100m", cancel_event=None):
        """Draw a titled question with numbered options and block for a
        valid choice (re-prompting on invalid input); return the chosen
        option's 1-based index, or None if cancelled via cancel_event
        (e.g. a graphical dialog answered first)."""
        with self.dialoglock:
            import textwrap

            width = min(shutil.get_terminal_size()[0], 80)
            if len(title) > width:
                title = title[: width - 3] + "..."
            text = textwrap.fill(question, width=width) + "\n"
            spacing = " " * ((width - len(title)) // 2)
            if self.n:
                moveback = f"\x1b[{self.n}B"
            else:
                moveback = ""
            if self.helping:
                moveback = "\x1b[H"
            text = "\n".join(line.ljust(width) for line in text.split("\n"))
            optionstext = ""
            optiontotalwidth = 0
            row = []
            for optioni in range(len(options)):
                option = textwrap.fill(
                    f"{optioni + 1}. {options[optioni]}", width=width
                )
                if optiontotalwidth + len(option) > width:
                    optionspacing = " " * (
                        (width - optiontotalwidth) // ((len(row) - 1) or 1)
                    )
                    current = optionspacing.join(row)
                    optionstext += (
                        current
                        + " "
                        * max(
                            0,
                            width
                            - len(
                                current.split("\n")[-1]
                                .replace("\x1b[7m", "")
                                .replace("\x1b[1m", "")
                                .replace("\x1b[22m", "")
                                .replace("\x1b[27m", "")
                            ),
                        )
                        + "\n"
                        + " " * width
                        + "\n"
                    )
                    optiontotalwidth = 0
                    row = []
                optiontotalwidth += len(option)
                row.append(f"\x1b[7m\x1b[1m{option}\x1b[22m\x1b[27m")
            optionspacing = " " * ((width - optiontotalwidth) // ((len(row) - 1) or 1))
            current = optionspacing.join(row)
            optionstext += (
                current
                + " "
                * max(
                    0,
                    width
                    - len(
                        current.split("\n")[-1]
                        .replace("\x1b[7m", "")
                        .replace("\x1b[1m", "")
                        .replace("\x1b[22m", "")
                        .replace("\x1b[27m", "")
                    ),
                )
                + "\n"
            )
            self.outpt(
                f'\x1b7{moveback}\x1b[L\r\x1b[{color}\x1b[7m{spacing}\x1b[1m{title}\x1b[22m{spacing}{" " * ((width - len(title)) % 2)}\x1b[27m\n{text}\n{optionstext}\x1b[0m'.replace(
                    "\n", f"\x1b[49m\n\x1b[L\x1b[{color}"
                ),
                end="",
            )
            options = range(1, optioni + 2)
            optionpromptslash = "/".join(map(str, options))
            previnput = self.curactiveinput
            restore = lambda: [
                self.outpt(
                    f'\x1b8\x1b[{optionstext.count("\n") + text.count("\n") + 3}B',
                    end="",
                ),
                setattr(self, "curactiveinput", previnput),
            ]
            self.curactiveinput = "dialog"
            gotinput = self.inpt(
                f"\x1b[7m\x1b[1mselect ({optionpromptslash}):\x1b[0m ",
                cancel_event=cancel_event,
            )
            if gotinput is None:
                restore()
                return
            gotinput = gotinput.strip().lower()
            try:
                gotinput = int(gotinput)
            except Exception:
                pass
            if gotinput not in options:
                while gotinput not in options:
                    self.curactiveinput = "dialog"
                    gotinput = self.inpt(
                        f"\x1b[A\r\x1b[K\x1b[7m\x1b[1m\x1b[31m[invalid input]\x1b[39m select ({optionpromptslash}):\x1b[0m ",
                        cancel_event=cancel_event,
                    )
                    if gotinput is None:
                        restore()
                        return
                    gotinput = gotinput.strip().lower()
                    try:
                        gotinput = int(gotinput)
                    except Exception:
                        pass
            restore()
            return gotinput

    def prompt(self, title, text, color="100m", cancel_event=None):
        """Draw a titled text prompt and block for a line of input;
        return it, or None if cancelled via cancel_event (e.g. a
        graphical dialog answered first)."""
        with self.dialoglock:
            import textwrap

            width = min(shutil.get_terminal_size()[0], 80)
            if len(title) > width:
                title = title[: width - 3] + "..."
            text = textwrap.fill(text, width=width) + "\n"
            spacing = " " * ((width - len(title)) // 2)
            if self.n:
                moveback = f"\x1b[{self.n}B"
            else:
                moveback = ""
            if self.helping:
                moveback = "\x1b[H"
            text = "\n".join(line.ljust(width) for line in text.split("\n"))
            self.outpt(
                f'\x1b7{moveback}\x1b[L\r\x1b[{color}\x1b[7m{spacing}\x1b[1m{title}\x1b[22m{spacing}{" " * ((width - len(title)) % 2)}\x1b[27m\n{text}\n\x1b[0m'.replace(
                    "\n", f"\x1b[49m\n\x1b[L\x1b[{color}"
                ),
                end="",
            )
            previnput = self.curactiveinput
            self.curactiveinput = "dialog"
            restore = lambda: [
                self.outpt(f'\x1b8\x1b[{text.count("\n") + 3}B', end=""),
                setattr(self, "curactiveinput", previnput),
            ]
            gotinput = self.inpt(
                f"\x1b[7m\x1b[1mprompt:\x1b[0m ", cancel_event=cancel_event
            )
            if gotinput is None:
                restore()
                return
            restore()
            return gotinput

    def loop(self):
        """The console's main command loop: repeatedly prompt for and
        handle one of the console's own commands (start, command-exec,
        pycode-eval, extra-pycode, open-file, exit/close, kill, run,
        clear, help), queuing GUI-affecting ones via self.q. Runs for
        the lifetime of the process; kill always os._exit()s out of it
        directly, and so does exit/close before PyNotes has started
        (state.started unset) — otherwise exit/close queues a close
        for the GUI thread and returns to the loop."""
        try:
            set_raw_mode()
            while True:
                self.n = 0
                self.helping = False
                commandline = self.inpt("> ")
                command, commandinput = (commandline.strip() + " ").split(" ", 1)
                command = command.strip()
                commandinput = commandinput.strip()
                if not command:
                    continue
                if command == "start":
                    if not state.started.is_set():
                        self.outpt("\x1b[32mstarting pynotes.\x1b[0m")
                        state.started.set()
                    else:
                        self.outpt("\x1b[31merror: pynotes has already started.\x1b[0m")
                elif command == "command-exec":
                    if not commandinput:
                        self.outpt("\x1b[33mcancelled.\x1b[0m")
                        continue
                    if not state.started.is_set():
                        self.outpt(
                            f"\x1b[33mwill execute alt-x command '\x1b[3m{commandinput}\x1b[23m' on pynotes start.\x1b[0m"
                        )
                    else:
                        self.outpt(
                            f"\x1b[32mexecuting alt-x command '\x1b[3m{commandinput}\x1b[23m'.\x1b[0m"
                        )
                    self.q.put(("command-exec", commandinput))
                elif command == "pycode-eval":
                    if not commandinput:
                        self.outpt("\x1b[33mcancelled.\x1b[0m")
                        continue
                    if not state.started.is_set():
                        self.outpt(
                            f"\x1b[33mwill evaluate pycode '\x1b[3m{commandinput}\x1b[23m' on pynotes start.\x1b[0m"
                        )
                    else:
                        self.outpt(
                            f"\x1b[32mevaluating pycode expression '\x1b[3m{commandinput}\x1b[32m'.\x1b[0m"
                        )
                    self.q.put(("pycode-eval", commandinput))
                elif command == "extra-pycode":
                    if commandinput:
                        self.outpt(
                            "\x1b[31merror: input given to \x1b[3mextra-pycode\x1b[23m command.\x1b[0m"
                        )
                        continue
                    if state.started.is_set():
                        self.outpt("\x1b[31merror: pynotes has already started.\x1b[3m")
                        continue
                    expc = ""
                    while True:
                        self.n += 1
                        self.curactiveinput = "command"
                        nl = self.inpt("extra-pycode> ").strip()
                        if nl == "DONE":
                            break
                        elif nl == "CANCEL":
                            expc = ""
                            break
                        expc += nl
                    if not expc:
                        self.outpt("\x1b[33mcancelled.\x1b[0m")
                        continue
                    if state.options["pycode-exec"]:
                        state.options["pycode-exec"] += ";" + expc
                    else:
                        state.options["pycode-exec"] = expc
                    self.n += 1
                    self.outpt(
                        "\x1b[32madded extra pycode to run on pynotes start.\x1b[0m"
                    )
                elif command == "open-file":
                    if commandinput:
                        filetoopen = commandinput
                    else:
                        self.n = 1
                        self.curactiveinput = "command"
                        filetoopen = self.inpt("file to open: ").strip()
                        self.outpt("\r\x1b[A\x1b[K", end="")
                    if not filetoopen:
                        self.outpt("\x1b[33mcancelled.\x1b[0m")
                        continue
                    self.outpt(f"\x1b[A\x1b[K> open-file {filetoopen}")
                    self.n = 0
                    filetoopen = os.path.abspath(os.path.expanduser(filetoopen))
                    if not os.path.exists(filetoopen):
                        self.outpt(
                            f"\x1b[33mfile '\x1b[3m{filetoopen}\x1b[23m' does not exist, creating file.\x1b[0m"
                        )
                    if state.started.is_set():
                        self.outpt(
                            f"\x1b[32mopening file '\x1b[3m{filetoopen}\x1b[23m'.\x1b[0m"
                        )
                        self.q.put(("open-file", filetoopen))
                    else:
                        self.outpt(
                            f"\x1b[33mfile '\x1b[3m{filetoopen}\x1b[23m' will be opened on pynotes start.\x1b[0m"
                        )
                        state.files_to_open.append(filetoopen)
                elif command in ("exit", "close"):
                    if commandinput:
                        self.outpt(
                            f"\x1b[31merror: input given to \x1b[3mclose\x1b[23m command.\x1b[0m"
                        )
                        continue
                    self.outpt(f"\x1b[32mclosing pynotes.\x1b[0m")
                    if state.started.is_set():
                        self.q.put(("close",))
                    else:
                        unset_raw_mode()
                        self.outpt("\n\x1b[H\x1b[2J", end="")
                        os._exit(0)
                elif command == "kill":
                    if commandinput:
                        self.outpt(
                            f"\x1b[31merror: input given to \x1b[3mkill\x1b[23m command.\x1b[0m"
                        )
                        continue
                    self.n = 1
                    self.curactiveinput = "command"
                    userinput = (
                        self.inpt("\x1b[33mkill pynotes? (y/n): \x1b[0m").strip() + "g"
                    )[0].lower()
                    if userinput not in ("y", "n"):
                        for i in range(2):
                            self.outpt("\r\x1b[A\x1b[K", end="")
                            self.curactiveinput = "command"
                            userinput = (
                                self.inpt(
                                    f"\x1b[31m[invalid input ({i + 2}/3)]\x1b[0m \x1b[33mkill pynotes? (y/n): \x1b[0m"
                                ).strip()
                                + "g"
                            )[0].lower()
                            if userinput in ("y", "n"):
                                break
                            else:
                                userinput = "n"
                    if userinput != "y":
                        self.outpt("\r\x1b[A\x1b[K\x1b[32mcancelled.\x1b[0m")
                        continue
                    else:
                        self.outpt("\x1b[31mkilling pynotes.\x1b[0m")
                        unset_raw_mode()
                        self.outpt("\n\x1b[H\x1b[2J", end="")
                        os._exit(0)
                elif command == "run":
                    if commandinput:
                        torun = commandinput
                    else:
                        self.n = 1
                        self.curactiveinput = "command"
                        torun = self.inpt("command to run: ").strip()
                    if not torun:
                        self.outpt("\r\x1b[A\x1b[K\x1b[33mcancelled.\x1b[0m")
                        continue
                    subprocess.run(
                        torun, shell=True, stdout=state.stdout, stderr=state.stderr
                    )
                elif command == "clear":
                    if commandinput:
                        self.outpt(
                            "\x1b[31merror: input given to \x1b[3mclear\x1b[23m command.\x1b[0m"
                        )
                        continue
                    self.outpt("\x1b[H\x1b[2J\x1b[3J", end="")
                elif command == "help":
                    if commandinput:
                        self.outpt(
                            "\x1b[31merror: input given to \x1b[3mhelp\x1b[23m command.\x1b[0m"
                        )
                        continue
                    self.helping = True
                    self.outpt("\x1b[?1049h", end="")
                    self.outpt(clcht)
                    self.curactiveinput = "command"
                    self.inpt(
                        "\x1b[33m\x1b[1m[PRESS ENTER TO CONTINUE]\x1b[0m", echo=False
                    )
                    self.outpt("\x1b[?1049l", end="")
                    self.helping = False
                    self.outpt("\x1b[32m\x1b[3mhelp text shown\x1b[0m")
                else:
                    self.outpt(
                        f"\x1b[31merror: invalid command '\x1b[3m{command}\x1b[23m'.\x1b[0m"
                    )
        finally:
            unset_raw_mode()
            self.outpt("\n\x1b[H\x1b[2J", end="")


def start_console(consoleq):
    """Create the Console and run its command loop; the thread target
    main.py starts alongside the GUI."""
    state.console = Console(consoleq)
    state.console.loop()
    return state.console
