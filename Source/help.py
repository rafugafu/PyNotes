"""All of PyNotes' Help windows (About, Changes, and the various
Help-with-X topics), each a self-contained window builder.
"""

import inspect
import re
import canvastk as ctk
import state
from init import v, rootdir, homedir, monospace
import pycode
import python_scope_build
import utils


def _help_code_label(master, text):
    """A Label showing example code (monospaced, black on a white
    background).
    """
    return ctk.Label(
        master,
        text=text,
        bg="white",
        fg="black",
        padx=7,
        pady=7,
        bd=2,
        relief="sunken",
        font=(monospace, 11),
    )


def _help_image_label(master, path, shrink):
    """A Label showing the image at path, shrunk by a factor of shrink."""
    from PIL import Image

    with Image.open(path) as source:
        width, height = source.size
    return ctk.Label(
        master,
        image=ctk.load_canvas_image(path, size=(width // shrink, height // shrink)),
    )


def abt():
    """Show the About PyNotes window."""
    utils.show("open about pynotes")
    abw = state.root.subwin()
    abw.title("About PyNotes")
    abw.focus()
    abw_ = ctk.Frame(abw)
    abw_.pack(fill="both", padx=10, pady=10)
    _help_image_label(abw_, f"{rootdir}/Icon.png", 2).grid(column=0, row=0, sticky="w")
    ctk.Label(abw_, text=f"PyNotes v{v}", font=("TkDefaultFont", 20)).grid(
        column=0, row=1, sticky="w"
    )
    ctk.Label(
        abw_, text="Rafey <https://github.com/rafugafu>", font=("TkDefaultFont", 15)
    ).grid(column=0, row=2, sticky="w")
    ctk.Label(
        abw_,
        text="PyNotes is an advanced, extensible, cross-platform\nEmacs-like text editor and IDE made in Python.",
        font=("TkDefaultFont", 12),
    ).grid(column=0, row=3, sticky="w")
    ctk.Button(abw, text="Close", command=abw.destroy).pack(
        side="bottom", fill="x", padx=10, pady=10
    )
    abw.bind("<Escape>", lambda event: abw.destroy())
    abw.bind("<Return>", lambda event: abw.destroy())
    utils.lock_window_size(abw)


def changes():
    """Show the current version's changelog (state.changestr)."""
    utils.show("show pynotes changes")
    cw = state.root.subwin()
    cw.title(f"Changes in v{v}")
    chtextbox = utils.EnabledLookTextbox(
        cw, scrolled=True, font=("TkDefaultFont", 13), wrap="word"
    )
    chtextbox.insert("end", state.changestr)
    chtextbox.config(state="disabled")
    chtextbox.yview_moveto(1)
    chtextbox.pack(fill="both", expand=True)
    cw.bind("<Escape>", lambda event: cw.destroy())
    cw.bind("<Return>", lambda event: cw.destroy())
    utils.lock_window_size(cw)
    cw.focus()


def hemail():
    """Show the Help with Email window (setup and spellcheck dictionaries)."""
    utils.show("open email help")
    hew = state.root.subwin()
    hew.title("Help with Email")
    tabs = ctk.Notebook(hew)
    mf = ctk.Frame(hew)
    tabs.add(mf, text="Setup")
    tabs.pack(fill="both", expand=True, padx=10, pady=10)
    ctk.Label(
        mf,
        text="""Open the Email buffer with Alt-X and 'sendemail' or 'sendmail'.
Give the username and password of your email in that buffer.
Then you can type and send any email from PyNotes!""",
    ).grid(padx=10, pady=10)
    dt = ctk.Frame(hew)
    tabs.add(dt, text="Dictionaries")
    ctk.Label(
        dt,
        text="""The email textbox has a spellcheck. The default dictionary for spellchecking is English,
but you can add or remove extra dictionaries to this.
To add another language or dictionary, you need to find or make a text file that has
one word in each line, without any spaces. (It can be any language)
Then go to Preferences → Email to upload that dictionary.

Once you have added a dictionary, don't move or remove the
dictionary before removing it in the settings.""",
    ).grid(padx=10, pady=10)
    utils.lock_window_size(hew)
    hew.focus()


def hx():
    """Show the Help with Alt-X commands window: the command syntax,
    then every built-in command (one line each), then any plugin
    commands' help text. Section headings are bolded ("bigstuff") by
    recording the text range's start/end index (l*/r*) around each
    insert() call and tagging it afterwards.
    """
    utils.show("open alt-x commands help")
    hxw = state.root.subwin()
    hxw.title("Help with commands")
    hxh = utils.EnabledLookTextbox(hxw, wrap="word", scrolled=True)
    l1 = hxh.index("end-1c")
    hxh.insert("end", "General\n\n")
    r1 = hxh.index("end-1c")
    hxh.tag_add("bigstuff", l1, r1)
    hxh.insert(
        "end",
        """Pressing Alt-X will open a box where you can type commands to do things in PyNotes.
Many commands have many different aliases; for example, 'sh', 'splithoriz', and 'split-editor-horizontal' all split the currently open editor horizontally.
':' separates commands from their input.
To include semicolons in the input to a command, put the input in brackets.
To include unmatched literal brackets in the input, escape them with a backslash.
Example:
re:(hmode:py;w:print('hello')*1;sw)*3;w:\\n'back'*1""",
    )
    l2 = hxh.index("end-1c")
    hxh.insert("end", "\n\nPyNotes' Commands\n\n")
    r2 = hxh.index("end-1c")
    hxh.tag_add("bigstuff", l2, r2)
    hxh.insert(
        "end",
        (
            """'mathgod' or 'mg': Open MathGod
'exit' or 'e': Cleanly exit PyNotes
'pccmd:{command}' or 'pycodecommand:{command}': Directly takes and evaluates a single PyCode expression
'save' or 's': Save the current file
'saveas' or 'sa': Copy the current file to another filename
'u' or 'undo': Undo the last edit
'r' or 'redo': Redo the last undoed edit
'termexec:{string}' or 'te:{string}': Run the given string as a terminal command
'write:{string}*{n}' or 'w:{string}*{n}': Copy the given text {n} times after the cursor position
'search' or 'f' (optional ':b' or ':back' to find reverse): Find a string in the current editor
'fr' or 'find-replace' or 'findreplace' (optional ':b' or ':back' to find & replace reverse): Find and replace a string in the current editor
'show-source' or 'source-code': Show any PyNotes source code file selected by you in /usr/share/PyNotes/ on Linux and C:/Program Files/PyNotes/ on Windows
'new' or 'n': Open a new file in the same editor
'gotoline:n' or 'gl:n' or 'l:n': Go to the nth line in the active editor if n is given, otherwise prompts for a line number and goes to it
'pyshell' or 'ps' (optional ':h' or ':horiz' or ':horizontal'): Opens a Python REPL buffer, vertical by default, horizontal if given
'o' or or 'load' or 'find' or 'open': Load a new file into the currently active editor
't:{optional command}' or 'term:{optional command}' or 'terminal:{optional command}' or 'cmd:{optional command}': Open a full terminal running command if given, otherwise /bin/bash or powershell.exe
'prf' or 'preferences': Change the preferences
'cancel' or 'z': Cancel the command
'a' or 'selall' or 'all': Select all the text in the active editor
'c' or 'copy': Copy the selected text
'cut': Cut the selected text
'p' or 'paste': Paste the last copied text
'h:{(x/em/pc/mg/pl)}' or 'help:{(x/em/pc/mg/pl)}': Open the Help of Alt-X commands (this), Email, PyCode, MathGod, Plugins
'hmode:{(py/la/norm/html/md)}': Change the HMode to Python / LaTeX / Normal / HTML / Markdown (PyNotes mode)
'pf' or 'pagenext': Scroll down a page in the active editor
'pb' or 'pageback': Scroll up a page in the active editor
'clear': Clear the active editor completely
'full': Make the window fullscreen
'unfull': Make PyNotes windowed mode from fullscreen
'max' or 'maximize': Maximize the window
'unmax' or 'unmaximize': Unmaximize the main window
'min': Minimize the window
'pycode' or 'pc': Open PyCode
'<Esc>': 'cancel'
'sp' or 'speak': Speak the text selected out loud
'ir' or 'indent-region': Indent the selected region with tabs or spaces
'unir' or 'unindent-region': Unindent the selected region (handles tabs, spaces, and mixed)
'st' or 'speech-to-text': Use speech-to-text
'opd' or 'openplugindir': Open the Plugin's Directory
'dp' or 'downloadplugins': Download plugins from the PyNotes' GitHub
'ch' or 'changes': Open a list of the changes made in PyNotes v{v}
'ab' or 'abt' or 'about' or 'pynotes': Open the PyNotes About
're:{command}*{n}' or 'repeat:{command}*{n}': Repeat the given command {n} times
'run': Run the code in the active editor if the HMode is Python / LaTeX / HTML
'cr' or 'comment' or 'comment-region': Comment the selected code if the HMode is Python / LaTeX / HTML / Markdown
'uncr' or 'uncomment' or 'uncomment-region': Uncomment the selected code if the HMode is Python / LaTeX / HTML / Markdown
'fullup': Moves the cursor to the beginning of the file
'fulldown': Moves the cursor to the end of the file
'ms' or 'mark' or 'markset' or 'mark-selection': Visually marks the selected text in the active editor
'unms' or 'unmark' or 'unmark-selection': Unmarks the visually marked text inside the selection in the active editor
'unma' or 'unmarkall': Unmarks all the visually marked text in the active editor
'sol' or 'startofline': Move the cursor to the start of the line
'eol' or 'endofline': Move the cursor to the end of the line
'sendemail' or 'sendmail': Opens (or switches to) the standalone Email buffer
'sh' or 'splithoriz' or 'split-editor-horizontal': Split the currently active editor horizontally
'sv' or 'splitvert' or 'split-editor-vertical': Split the currently active editor vertically
'bb' or 'balance' or 'balance-buffers': Make all the open buffers equal size
'neh' or 'newedithoriz' or 'new-editor-horizontal': Opens a new horizontal editor
'nev' or 'neweditvert' or 'new-editor-vertical': Opens a new vertical editor
'onh' or 'opennewhoriz' or 'open-file-horizontal': Opens a file in a new horizontal editor
'onv' or 'opennewvert' or 'open-file-vertical': Opens a file in a new vertical editor
'cb' or 'close' or 'closecurbuf' or 'close-current-buffer': Close the currently active buffer
'sw' or 'switch' or 'switchbuf' or 'switch-buffer': Cycle between open buffers
'pynavstart:{f/fun/func/function/c/class/b/block/name}' or 'pyjumpstart:{f/fun/func/function/c/class/b/block/name}' or 'python-jump-startof:{f/fun/func/function/c/class/b/block/name}': If the HMode is Python, jump to the start of the current function/class/block the cursor is in if given f/fun/func/function/c/class/b/block, or jump to the start of the given function/class name (an attribute chain like Outer.Inner.name from the module level for nested ones)
'pynavend:{f/fun/func/function/c/class/b/block/name}' or 'pyjumpend:{f/fun/func/function/c/class/b/block/name}' or 'python-jump-endof:{f/fun/func/function/c/class/b/block/name}': If the HMode is Python, jump to the end of the current function/class/block the cursor is in if given f/fun/func/function/c/class/b/block, or jump to the end of the given function/class name (an attribute chain like Outer.Inner.name from the module level for nested ones)
'pygodef:{name}' or 'python-go-definition:{name}': If the HMode is Python, jump to the definition of the given name in the active editor (an attribute chain like Outer.Inner.name from the module level for names inside classes/functions)
'lanavstart:{c/chapter/s/sec/section/ss/subsec/subsection/sss/subsubsec/subsubsection/title}' or 'lajumpstart:{c/chapter/s/sec/section/ss/subsec/subsection/sss/subsubsec/subsubsection/title}' or 'latex-jump-startof:{c/chapter/s/sec/section/ss/subsec/subsection/sss/subsubsec/subsubsection/title}': If the HMode is LaTeX, jump to the start of the current chapter/section/subsection/subsubsection the cursor is in if given the respective keyword, or jump to the start of the section with the given title
'lanavend:{c/chapter/s/sec/section/ss/subsec/subsection/sss/subsubsec/subsubsection/title}' or 'lajumpend:{c/chapter/s/sec/section/ss/subsec/subsection/sss/subsubsec/subsubsection/title}' or 'latex-jump-endof:{c/chapter/s/sec/section/ss/subsec/subsection/sss/subsubsec/subsubsection/title}': If the HMode is LaTeX, jump to the end of the current chapter/section/subsection/subsubsection the cursor is in if given the respective keyword, or jump to the end of the section with the given title
'mdnavstart:{h1/h2/h3/h4/h5/h6/s/sec/section/title}' or 'mdjumpstart:{h1/h2/h3/h4/h5/h6/s/sec/section/title}' or 'markdown-jump-startof:{h1/h2/h3/h4/h5/h6/s/sec/section/title}': If the HMode is Markdown, jump to the start of the current section of the given level (h1-h6) the cursor is in if given h1/h2/h3/h4/h5/h6, or of any level if given s/sec/section, or jump to the start of the section with the given title
'mdnavend:{h1/h2/h3/h4/h5/h6/s/sec/section/title}' or 'mdjumpend:{h1/h2/h3/h4/h5/h6/s/sec/section/title}' or 'markdown-jump-endof:{h1/h2/h3/h4/h5/h6/s/sec/section/title}': If the HMode is Markdown, jump to the end of the current section of the given level (h1-h6) the cursor is in if given h1/h2/h3/h4/h5/h6, or of any level if given s/sec/section, or jump to the end of the section with the given title
'setsel' or 'selpointset' or 'selection-point-set': Set the selection point at the cursor
'unsetsel' or 'selpointunset' or 'selection-point-remove': Remove the selection point if set"""
            # Blank line between each command for readability.
        ).replace("\n", "\n\n"),
    )
    l3 = hxh.index("end-1c")
    if state.plgnscmdhelp:
        hxh.insert("end", "\n\nPlugin Commands")
    r3 = hxh.index("end-1c") + "+2c"
    hxh.insert("end", state.plgnscmdhelp)
    hxh.tag_add("bigstuff", l3, r3)
    hxh.tag_config("bigstuff", font=(monospace, 15, "bold"))
    hxh.pack(fill="both", padx=10, pady=10)
    hxh.config(state="disabled")
    utils.lock_window_size(hxw)
    hxh.bind("<Escape>", lambda event: hxh.destroy())
    hxh.bind("<Return>", lambda event: hxh.destroy())
    hxh.focus()


def helppycode():
    """Show the Help with PyCode window: syntax, commands, graphical
    coding, keyboard shortcuts, variables, functions, loops and conditions,
    each as its own tab.
    """

    def make_code_box(master, code, disabled=True, *args, **kwargs):
        """Make and return a textbox showing the code, with basic syntax highlighting,
        with a copy button in the top right corner.
        """

        def match(key, expr):
            """Find and tag all exprs found in the code with key for syntax highlighting."""
            code = f.t.get("1.0", "end")
            for m in re.finditer(expr, code, re.DOTALL):
                for tag in f.t.tag_names():
                    if tag == "sel":
                        continue
                    f.t.tag_remove(tag, f"1.0+{m.start()}c", f"1.0+{m.end()}c")
                f.t.tag_add(key, f"1.0+{m.start()}c", f"1.0+{m.end()}c")

        def ha():
            """Syntax highlight the PyCode code. Converts numbers, variables,
            function calls and definitions, keywords, strings, and
            comments.
            """

            import keyword

            for tag in f.t.tag_names():
                if tag == "sel":
                    continue
                f.t.tag_remove(tag, "1.0", "end")
            match("number", r"\b\d+\b")
            match("variable", r"(?<![\w.])[^\W\d]\w*(?=\s*\=)")
            match("function_call", r"(?<![\w.])[^\W\d]\w*(?=\s*\()")
            match("function_definition", r"(?<![\w.])[^\W\d]\w*(?=\s*\([^)]*\)\s*\{)")
            match(
                "keyword",
                rf"\b({'|'.join(keyword.kwlist)})\b",
            )
            match("string", r"'.+?'")
            match("string", r'".+?"')
            match("comment", r"#.+?(?=\n)")
            f.t.edit_modified(False)

        f = ctk.Frame(master)
        kwargs.setdefault("scrolled", True)
        kwargs.setdefault("font", (monospace, 12))
        kwargs.setdefault("wrap", "word")
        if disabled:
            f.t = utils.EnabledLookTextbox(f, *args, **kwargs)
        else:
            f.t = ctk.Textbox(f, *args, **kwargs)
        f.t.pack(fill="both", expand=True)
        if code is not None:
            f.t.insert("end", code)
        f.t.tag_config("function_call", foreground="blue")
        f.t.tag_config("function_definition", foreground="brown")
        f.t.tag_config("string", foreground="green")
        f.t.tag_config("comment", foreground="grey", font=(monospace, 12, "italic"))
        f.t.tag_config("variable", foreground="red")
        f.t.tag_config("keyword", foreground="purple", font=(monospace, 12, "bold"))
        f.t.tag_config("number", foreground="orange")
        ha()
        if disabled:
            f.t.config(state="disabled")
        f.t.bind("<<Modified>>", lambda _: ha())
        ctk.Button(
            f.t,
            text="⮺",
            radius=99,
            command=lambda: [
                state.root.clipboard_clear(),
                state.root.clipboard_append(f.t.get("1.0", "end-1c")),
            ],
        ).place(relx=1.0, x=-30, y=10, anchor="ne")
        return f

    def make_text(master, text):
        """Make and return a label showing the help text, which automatically adjusts
        its wrap on width change.
        """
        f = ctk.Frame(master)
        t = ctk.Label(f, text=text)
        t.pack(fill="both", expand=True)
        hpwin.update()
        t.config(wraplength=f.winfo_width())
        f.bind("<Configure>", lambda _: t.config(wraplength=f.winfo_width()))
        return f

    utils.show("open pycode help")
    hpwin = state.root.subwin()
    hpwin.title("Help with PyCode")
    hpwin.geometry("1200x800")
    hptabs = ctk.Notebook(hpwin)
    hptabs.pack(fill="both", expand=True, padx=10, pady=10)

    # =========================================================================
    # SYNTAX
    # =========================================================================

    st = ctk.Frame(hptabs)
    hptabs.add(st, text="Syntax")
    st.grid_columnconfigure(0, weight=1)
    st.grid_rowconfigure(1, weight=1)

    make_text(
        st,
        """The syntax of PyCode is similar to C and Python. \
Statements are separated by semicolons, and all whitespace between tokens \
is ignored. There does not need to be a semicolon at the end of a code block. \
All names must be valid syntax in Python. The syntax of calling functions is the \
same as Python, including the arguments, but the syntax of defining functions is: \
name (python-args) {code}; . The syntax of defining variables is simply name = val. \
The syntax of conditions is if (cond) {code} elif (cond) {code} else {code}; , and \
the syntax of loops is while (cond) {code}; . Keywords are global, nonlocal, return, \
del, pass, break, and continue. They can be used normally as in Python. You can always \
include a plain Python expression anywhere. The syntax for comments is also the same \
as Python (# this is a comment). All PyCode is translated to plain Python before being \
executed. You can test how PyCode translates in the 'Testing' tab in this help window.
Example:""",
    ).grid(column=0, row=0, padx=10, pady=10, sticky="ew")
    make_code_box(
        st,
        """\
# This is a comment.

func_1 (*args, **kwargs) {}; # Do nothing

func_1(None, arg1=None); # Function call with positional and keyword arguments

func_2 (a, b) {
    local_func () {
        # This is a local function, not visible outside
    };
    return a + b; # Add and return a and b
};

a = 2;
b = 3;

if (True) {
    show_message(f"{a}+{b}={func_2(a, b)}");
}
else {
    show_message("This is not possible");
};

i = 0;
while (i <= 2) {
    show_message(func_2(i, i + 2));
    i = i + 1;
};\
""",
    ).grid(column=0, row=1, padx=10, pady=10, sticky="nsew")

    # =========================================================================
    # COMMANDS
    # =========================================================================

    ct = ctk.Frame(hptabs)
    hptabs.add(ct, text="Commands")
    ct.grid_columnconfigure(0, weight=1)
    ct.grid_rowconfigure(1, weight=1)

    make_text(
        ct,
        """Commands are built-in PyCode functions used to control the PyNotes editor.
All the commands are:""",
    ).grid(column=0, row=0, padx=10, pady=10, sticky="ew")
    ctt = utils.EnabledLookTextbox(ct, scrolled=True, font=(monospace, 12))
    ctt.grid(column=0, row=1, padx=10, pady=10, sticky="nsew")
    l1 = ctt.index("end-1c")
    ctt.insert("end", "PyNotes' Commands Help\n\n")
    r1 = ctt.index("end-1c")
    ctt.tag_add("bigstuff", l1, r1)
    ctt.insert(
        "end",
        """\
about_pynotes() - Opens the PyNotes About.

add_command(name, function) - Makes the given function the Alt-X command name. If the function takes a parameter, it gets the command's input.

add_event_hook(event, function) - Runs the given function before or after an event, where event is 'before:event' or 'after:event'. If the function takes a parameter, it gets the event's input.

ask_dialog(prompt) - Asks an input from the user in a dialog and returns the answer.

backspace() - Presses BackSpace in the active editor: deletes the selection, or one indentation level if only whitespace is before the cursor, or the previous character.

balance_buffers(orient = 'all') - Balance the horizontal/vertical/both ('horizontal', 'vertical', 'all') buffers to make them equal size.

clear_editor() - Clears the active editor.

close_buffer(n = None) - Closes the nth buffer if n is given, defaults to the currently active buffer.

close_pynotes() - Cleanly closes PyNotes.

comment_region(start, end) - Comments the text from a given line number start to a given line number end in the active editor if the HMode is Python / LaTeX / HTML / Markdown.

comment_selection() - Comments the selected code if the HMode is Python / LaTeX / HTML / Markdown.

configure_fileinfo(name_1 = val_1, name_2 = val_2, ...) - Configs or reconfigs if already existent the names in the file info bar to the values in the active buffer. Editors have filename, filetype, filesize, and filesaved inbuilt, Terminals use buffertype, title, and command, the Python Shell uses buffertype and interpreter, and Email uses buffertype.

copy_clipboard(text) - Copies the given text to the clipboard.

copy_selection() - Copies the selected text in the active editor.

cut_selection() - Cuts the selected text in the active editor.

delete_key() - Presses Delete in the active editor: deletes the selection, or one indentation level if only whitespace is before the cursor and whitespace follows it, or the next character.

delete_text(index_1, index_2 = None) - Deletes the text from a given tkinter-style index_1 to a given tkinter-style index_2 in the active editor (only the character at index_1 if index_2 is not given).

dictate_text() - Opens the speech-to-text, lets you dictate text to the active editor.

download_plugins() - Automatically opens a link to the PyNotes GitHub Plugin page to let you download plugins in your default browser.

find_replace(dir = 'forward') - Opens Find & Replace with optional dir ('forward', 'backward', 'beginning').

find_text(dir = 'forward') - Opens Find with optional dir ('forward', 'backward', 'beginning').

fullscreen_window() - Makes the PyNotes window fullscreen.

get_selection() - Gets the range of the selected text in the active editor and returns it as a tuple (start, end), or an empty tuple if nothing is selected.

get_text(index_1, index_2 = None) - Gets the text in the active editor from a given tkinter-style index_1 to a given tkinter-style index_2 and returns it.

go_to_line(n = None) - Moves the cursor to the given line number n if given, otherwise prompts the user for a line number and goes to it.

indent_region(start, end) - Indents the text from a given line number start to a given line number end in the active editor.

indent_selection() - Indents the selected region in the active editor.

insert_text(index, text) - Inserts the text at a given tkinter-style index in the active editor.

key_bind(key, function, where = None) - Runs the function when the tkinter-style key (like '<Control-x>', or a chord like '<Control-x & Control-s>') is pressed. where can be None to work in every buffer or 'editor' to work only in editors.

kill_pynotes() - Forcibly kills PyNotes without saving files or cleaning up.

latex_go_to_end_of(target) - If the HMode is LaTeX, jumps to the end of the current chapter/section/subsection/subsubsection the cursor is in if target is 'c/chapter/s/sec/section/ss/subsec/subsection/sss/subsubsec/subsubsection', otherwise jumps to the end of the section with the title target if it exists in the active editor.

latex_go_to_start_of(target) - If the HMode is LaTeX, jumps to the start of the current chapter/section/subsection/subsubsection the cursor is in if target is 'c/chapter/s/sec/section/ss/subsec/subsection/sss/subsubsec/subsubsection', otherwise jumps to the start of the section with the title target if it exists in the active editor.

left() - Presses Left in the active editor: moves the cursor back one indentation level if only whitespace is before it, otherwise one character.

mark_region(start, end) - Visually marks the text between a tkinter-style index start and a tkinter-style index end in the active editor.

mark_selection() - Visually marks the selected text in the active editor.

markdown_go_to_end_of(target) - If the HMode is Markdown, jumps to the end of the current section of the given level the cursor is in if target is 'h1-h6', or of any level if target is 's/sec/section', otherwise jumps to the end of the section with the title target if it exists in the active editor.

markdown_go_to_start_of(target) - If the HMode is Markdown, jumps to the start of the current section of the given level the cursor is in if target is 'h1-h6', or of any level if target is 's/sec/section', otherwise jumps to the start of the section with the title target if it exists in the active editor.

maximize_window() - Maximizes the PyNotes window.

minimize_window() - Minimizes the PyNotes window.

move_cursor(index) - Moves the cursor to a given tkinter-style index in the active editor.

new_editor(file = None, orient = 'horizontal') - Opens a new editor loading file if given and being horizontal or vertical depending on orient (default 'horizontal').

new_file() - Opens a new file in the currently active editor.

open_email_buffer() - Opens (or switches to) the standalone Email buffer.

open_file() - Opens a file picker to open a file in the currently active editor.

open_file_new_editor(orient = 'horizontal') - Opens a new editor with orientation orient (default 'horizontal') loading the file from a filedialog that is shown.

open_help(topic) - Opens the Help about the given feature, topic can be 'commands/email/pycode/mathgod/plugins'.

open_mathgod() - Opens MathGod.

open_plugin_directory() - Opens the plugins directory in your file manager.

open_preferences() - Opens the PyNotes preferences.

open_pycode() - Opens PyCode.

open_python_shell(orient = 'vertical') - Opens a Python REPL buffer in the given orientation.

open_terminal(command = None, title = 'Terminal', endmessage = None, blocking = False, orient = 'vertical') - Opens the PyNotes terminal in a buffer with orientation orient running a given command list (example [command, input1, input2]), /bin/bash or powershell.exe if not specified. Set optional title (the title of the terminal buffer) and endmessage (the message shown at the end after the process stops, terminal buffer closes immediately if no endmessage is set). If blocking is set to True (default False), it doesn't return till the process finishes.

page_back() - Goes to the previous page in the active editor.

page_forward() - Goes to the next page in the active editor.

paste_clipboard() - Pastes your clipboard in the active editor.

prompt(text, autocompletefunc = None, defaultinput = None) - Prompts the user with text in the Alt-X command box and returns input. Calls autocompletefunc with the currently typed text if it is a function, otherwise uses the fixed list/tuple if given in it when Tab is pressed. If defaultinput is given, starts the prompt with it.

python_go_to_definition(name) - If the HMode is Python, jumps to the definition of the given name in the active editor (an attribute chain like 'Outer.Inner.name' from the module level for names inside classes/functions).

python_go_to_end_of(target) - If the HMode is Python, jumps to the end of the current function/class/block the cursor is in if target is 'f/fun/func/function/c/class/b/block', otherwise jumps to the end of the given function/class name (an attribute chain like 'Outer.Inner.name' from the module level for nested ones) if it exists in the active editor.

python_go_to_start_of(target) - If the HMode is Python, jumps to the start of the current function/class/block the cursor is in if target is 'f/fun/func/function/c/class/b/block', otherwise jumps to the start of the given function/class name (an attribute chain like 'Outer.Inner.name' from the module level for nested ones) if it exists in the active editor.

redo_editor() - Redos the last undo in the active editor.

remove_selection_point() - Removes the selection point if set.

repeat_command(command, n) - Repeats the given Alt-X command n times.

right() - Presses Right in the active editor: moves the cursor forward one indentation level if only whitespace is before it and whitespace follows it, otherwise one character.

run_code() - Runs the code in the active editor if the HMode is Python / LaTeX / HTML.

run_command(command) - Runs the given Alt-X command.

run_shell(command) - Executes the given command in a terminal and shows the output in the Alt-X command box.

save_file() - Saves the file in the active editor.

save_file_as() - Save the text in the active editor to another filename.

select_all() - Selects all the text in the active editor.

select_text(start, end) - Selects the text from a given tkinter-style index start to a given tkinter-style index end in the active editor.

set_hmode(mode) - Switches the HMode (PyNotes mode) to Python / LaTeX / HTML / Markdown / Normal, mode can be 'py/la/html/md/norm'.

set_selection_point(index = None) - Sets the selection point at the index if given, otherwise cursor position.

set_variable(var, val) - Makes a variable with a given name var and a given value val.

set_window_geometry(geo) - Calls the tkinter root.geometry(geo).

set_window_title(title = None) - Sets the title of the PyNotes window to a given string, or sets it back to normal if title is not given.

show_message(text) - Shows the given text in the Alt-X command box.

show_popup(text) - Opens a graphical messagebox showing the given text. You can also use a variable here.

show_pynotes_source_code() - Show any PyNotes source code file selected by you in /usr/share/PyNotes/ on Linux and C:/Program Files/PyNotes/ on Windows in a new editor.

sleep(n) - Freezes PyNotes for n seconds.

speak_selection() - Speaks the selected text in the active editor.

split_editor(n = None, orient = 'horizontal') - Splits the nth editor (default active) horizontally or vertically depending on orient (default 'horizontal').

switch_buffer(n = None) - Switches focus to the nth buffer if given n, otherwise cycle buffers.

tag_add(tag, index_1, index_2) - Uses a tag previously set with tag_config. Same options as tkinter textbox.tag_add.

tag_config(name, **options) - Makes a tag named name with the given options. Same options as tkinter textbox.tag_config. Can be used later with tag_add.

tag_remove(tag, index_1, index_2) - Untags a tag previously set with tag_add. Same options as tkinter textbox.tag_remove.

tk_index(index, line = False) - Indexes the given tkinter-style input in the active editor and returns the output. If line is 'line', it returns only the linenumber as a string.

toggle_selection_point() - Sets the selection point at the cursor if not set, otherwise removes it.

type_command() - Lets you type an Alt-X command.

uncomment_region(start, end) - Uncomments the text from a given line number start to another given line number end in the active editor if the HMode is Python / LaTeX / HTML / Markdown.

uncomment_selection() - Uncomments the selected text in the active editor if the HMode is Python / LaTeX / HTML / Markdown.

undo_editor() - Undoes the last edit in the active editor.

unfullscreen_window() - Makes PyNotes windowed mode from fullscreen.

unindent_region(start, end) - Unindents the text from a given line number start to another given line number end in the active editor if the HMode is Python / LaTeX / HTML / Markdown.

unindent_selection() - Unindents the selected text in the active editor.

unmark_all() - Unmarks all the visually marked text in the active editor.

unmark_region(start, end) - Unmark the visually marked text in the active editor from a tkinter-style index start to a tkinter-style index end.

unmaximize_window() - Unmaximizes the main window.

write_editor(text, n) - Writes the given text repeated n times in the active editor.\
""",
    )
    l2 = ctt.index("end-1c")
    if state.plgnspccmdhelp:
        ctt.insert("end", "\n\nPlugins' Commands Help")
    r2 = ctt.index("end-1c") + "+2c"
    ctt.insert("end-1c", state.plgnspccmdhelp)
    ctt.tag_add("bigstuff", l2, r2)
    ctt.tag_config("bigstuff", font=(monospace, 15, "bold"))
    ctt.config(state="disabled")

    # =========================================================================
    # FUNCTIONS
    # =========================================================================

    ft = ctk.Frame(hptabs)
    hptabs.add(ft, text="Functions")
    ft.grid_columnconfigure(0, weight=1)
    ft.grid_rowconfigure(1, weight=1)

    make_text(
        ft,
        """Make functions using the syntax: \
name (python_args) {code}; . Function names which are invalid in Python cannot \
be used. Use the return keyword to return values.
Example:""",
    ).grid(column=0, row=0, padx=10, pady=10, sticky="ew")
    make_code_box(
        ft,
        """\
add (a, b) { # A function which adds and returns a and b.
    return a + b;
};

# Usage:
show_message("2 + 3 is " + add(2, 3) + ".") # Result: 2 + 3 is 5.\
""",
    ).grid(column=0, row=1, padx=10, pady=10, sticky="nsew")

    # =========================================================================
    # VARIABLES
    # =========================================================================

    vt = ctk.Frame(hptabs)
    hptabs.add(vt, text="Variables")
    vt.grid_columnconfigure(0, weight=1)
    vt.grid_rowconfigure(1, weight=1)

    make_text(
        vt,
        """Make variables using the syntax: var = val. Variable names which \
are invalid in Python cannot be used. val can be any valid PyCode or Python \
expression.
Example:""",
    ).grid(column=0, row=0, padx=10, pady=10, sticky="ew")
    make_code_box(
        vt,
        """\
a = 2;
b = 3;
sum_a_b = a + b;\
""",
    ).grid(column=0, row=1, padx=10, pady=10, sticky="nsew")

    # =========================================================================
    # LOOPS AND CONDITIONS
    # =========================================================================

    lct = ctk.Frame(hptabs)
    hptabs.add(lct, text="Loops and Conditions")
    lct.grid_columnconfigure(0, weight=1)
    lct.grid_rowconfigure(1, weight=1)

    make_text(
        lct,
        """The syntax of loops and conditions is similar to functions. The \
syntax of conditions is: if (cond) {code} elif (cond) {code} else {code}; . \
while is the only loop in PyCode. The syntax is: while (cond) {code}; . \
Additionally, you can always use inline Python loops and conditions.
Example:""",
    ).grid(column=0, row=0, padx=10, pady=10, sticky="ew")
    make_code_box(
        lct,
        """\
# =======================
# LOOPS
# =======================

score = 85;
if (score >= 90) {
    show_popup("Grade: A");
}
elif (score >= 80) {
    show_popup("Grade: B");
}
elif (score >= 70) {
    show_popup("Grade: C");
}
else {
    show_popup("Grade: F");
};

less_than_5 = (True if 2 + 3 < 5 else False); # Inline condition

# =======================
# CONDITIONS
# =======================

i = 0;
l1 = [];
while (i < 5) { # Loop 5 times
    l1.append(i);
    i = i + 1;
};

l2 = [i for i in range(5)]; # Same as l1: [0, 1, 2, 3, 4]
""",
    ).grid(column=0, row=1, padx=10, pady=10, sticky="nsew")

    # =========================================================================
    # KEYBOARD SHORTCUTS
    # =========================================================================

    kst = ctk.Frame(hptabs)
    hptabs.add(kst, text="Keyboard Shortcuts")
    kst.grid_columnconfigure(0, weight=1)
    kst.grid_rowconfigure(1, weight=1)

    make_text(
        kst,
        """Make keyboard shortcuts using the command key_bind(key, function, what=None).
key is a tkinter-style key string like '<Control-a>'. For chord bindings, separate tkinter-style \
keys with an &. For example, to bind Control-a Control-b, use the string \
'<Control-a & Control-b>'. Whitespace between the <, key, &, key, > does not matter. \
Chords can be of infinite length.
function is any callable (function or lambda) object.
what can be None or the string 'editor'. If it is None, the key works everywhere. \
If it is 'editor', it is bound only on editors.
Example:""",
    ).grid(column=0, row=0, padx=10, pady=10, sticky="ew")
    make_code_box(
        kst,
        """\
# Bind Control-Alt-x to type an Alt-X command.
key_bind("<Control-Alt-x>", type_command);
# The same as above, using a lambda instead of directly giving the function.
key_bind("<Control-Alt-x>", lambda: type_command());

end_of_line () { # Move the cursor to the end of the current line.
    cur_line = tk_index("insert", "line");
    move_cursor(cur_line + ".end");
};

# Bind Control-e to move the cursor to the end of the line in editors.
key_bind("<Control-e>", end_of_line, "editor");
""",
    ).grid(column=0, row=1, padx=10, pady=10, sticky="nsew")

    # =========================================================================
    # TESTING
    # =========================================================================

    def ha():
        """Highlight the translated Python in ttpyt the same way the editor
        highlights Python.
        """
        for tag in PYTHON_HIGHLIGHT_TAGS:
            ttpyt.tag_remove(tag, "1.0", "end")
        text = ttpyt.get("1.0", "end")
        # The translated code calls the commands' Python names, which exist in vars(state) at runtime
        command_names = {}
        for expression in pycode.pycode_commands.values():
            name = re.match(r"[^\W\d]\w*", expression)
            if name is None:
                continue
            name = name.group()
            if "." in expression:
                command_names[name] = (
                    "module" if inspect.ismodule(vars(state).get(name)) else "var"
                )
            else:
                command_names[name] = "func"
        result = python_scope_build._python_build_scopes(
            ttpyt_scan_host, text, seed_names=command_names
        )
        if result is None:
            return
        (
            scopes,
            call_kwargs,
            _module_aliases,
            _local_classes,
            module_literals,
            _scope_var_types,
            literal_attrs,
            def_names,
            typed_attrs,
            param_default_tags,
            kwarg_positions,
            import_dotted_lines,
            import_orig_name_tags,
            _class_module_origin,
            _local_class_method_params,
            _local_class_accepts_any,
            name_positions,
            _local_class_module_origins,
            _from_func_module,
            _class_type_maps,
            _class_attr_types,
            _func_params,
            _func_accepts_any,
            _class_bases,
            _inherited,
            _module_scope_class_keys,
            _instance_only,
            instance_name_positions,
            global_stmt_kind_positions,
        ) = result
        ops = python_scope_build._python_highlight_ops(
            text,
            "1.0",
            "",
            scopes,
            call_kwargs,
            module_literals,
            literal_attrs,
            name_positions,
            def_names,
            typed_attrs,
            param_default_tags,
            kwarg_positions,
            import_dotted_lines,
            instance_name_positions,
            global_stmt_kind_positions,
            import_orig_name_tags,
        )
        for op in ops:
            if op[0] == "add":
                for tag in PYTHON_HIGHLIGHT_TAGS:
                    ttpyt.tag_remove(tag, op[2], op[3])
                ttpyt.tag_add(op[1], op[2], op[3])
            elif op[0] == "clear_other":
                for tag in PYTHON_HIGHLIGHT_TAGS:
                    ttpyt.tag_remove(tag, op[1], op[2])
        ttpyt.tag_raise("sel")

    def parse():
        """Translate the PyCode in the input box and show the result or the error."""
        code = ttpct.t.get("1.0", "end-1c").strip()
        ttpyt.config(state="normal")
        ttpyt.delete("1.0", "end")  # This also removes the error tag if present
        try:
            translated = "\n".join(pycode.pycodeparse(code, {}))
        except pycode.PyCodeError as e:
            translated = e
            ttpyt.insert("end", translated)
            ttpyt.tag_add("error", "1.0", "end")
        else:
            ttpyt.insert("end", translated)
            ha()
        ttpyt.config(state="disabled")

    PYTHON_HIGHLIGHT_TAGS = (
        "hpa",
        "hpb",
        "hpv",
        "hpi",
        "hpf",
        "hpx",
        "hpfa",
        "hpm",
        "hpo",
        "hpd",
        "hpc",
    )
    ttpyt_scan_host = python_scope_build._PythonStandaloneScanHost()

    tt = ctk.Panedwindow(hptabs)
    hptabs.add(tt, text="Testing")

    ttpct = make_code_box(
        tt,
        None,
        disabled=False,
        placeholder="Type PyCode here to see how it translates!",
        undo=True,
    )
    ttpct.t.bind("<<Modified>>", lambda _: parse(), "+")
    tt.add(ttpct, weight=1)
    ttpyt = utils.EnabledLookTextbox(
        tt, scrolled=True, wrap="word", font=(monospace, 12)
    )
    ctk.Button(
        ttpyt,
        text="⮺",
        radius=99,
        command=lambda: [
            state.root.clipboard_clear(),
            state.root.clipboard_append(ttpyt.get("1.0", "end-1c")),
        ],
    ).place(relx=1.0, x=-30, y=10, anchor="ne")
    ttpyt.tag_config("error", foreground="red")
    ttpyt.tag_config("hpa", foreground="#7C3AED", font=(monospace, 12, "bold"))
    ttpyt.tag_config("hpb", foreground="#D97706")
    ttpyt.tag_config("hpv", foreground="#DC2626")
    ttpyt.tag_config("hpi", foreground="#155E75")
    ttpyt.tag_config("hpf", foreground="#2563EB")
    ttpyt.tag_config("hpx", foreground="#0891B2")
    ttpyt.tag_config("hpfa", foreground="#0F766E")
    ttpyt.tag_config("hpm", foreground="#0369A1")
    ttpyt.tag_config("hpo", foreground="white", background="light grey")
    ttpyt.tag_config("hpd", foreground="#15803D")
    ttpyt.tag_config("hpc", foreground="#6B7280", font=(monospace, 12, "italic"))
    ttpyt.config(state="disabled")
    tt.add(ttpyt, weight=1)

    hpwin.focus()


def ap():
    """Show the Add Plugins window: install steps plus shortcuts to
    download plugins or open the add-ons directory.
    """
    utils.show("open plugin help")
    apw = state.root.subwin()
    apw.title("Add Plugins")
    ctk.Label(
        apw,
        text=f"1. Download a plugin\n2. Extract the plugin if it is a zip\n3. Move the folder to {homedir}/.local/share/PyNotes/add-ons\n4. Restart PyNotes",
    ).grid(column=0, row=0, padx=10, pady=10, sticky="w")
    ctk.Button(apw, text="Download From PyNotes' GitHub", command=utils.dp).grid(
        column=0, row=1, padx=10, pady=10, sticky="w"
    )
    ctk.Button(apw, text="Open Plugins Directory", command=utils.op).grid(
        column=0, row=2, padx=10, pady=10, sticky="w"
    )
    ctk.Label(
        apw,
        text="Warning: Plugins have full access to PyNotes and your system\nand can run any commands. Be careful in downloading and using\nplugins from other websites.",
        font=(monospace, 12, "bold"),
    ).grid(column=0, row=3, padx=10, pady=10, sticky="w")
    apw.focus()


def helpmathgod():
    """Show the Help with MathGod window: variables, functions,
    equations, calculus, plotting (2D/3D/pie/bar), summation/products,
    interpolation, conditions, and other (raw sympy/Python) functions,
    each as its own tab.
    """
    utils.show("open mathgod help")
    hmgwin = state.root.subwin()
    hmgwin.title("Help with MathGod")
    tabs = ctk.Notebook(hmgwin)
    vars = ctk.Frame(hmgwin)
    tabs.add(vars, text="Variables")
    ctk.Label(
        vars, text="You can define variables using the standard python syntax:"
    ).grid(column=0, row=0, padx=10, pady=10)
    _help_code_label(vars, "{varname} = {varval}").grid(
        column=0, row=1, padx=10, pady=10
    )
    ctk.Label(vars, text="Here is an example:").grid(column=0, row=2, padx=10, pady=10)
    _help_code_label(vars, "v = 5\nv\nv + 1").grid(column=0, row=3, padx=10, pady=10)
    ctk.Label(vars, text="This will return 5 and 6.").grid(
        column=0, row=4, padx=10, pady=10
    )
    func = ctk.Frame(hmgwin)
    tabs.add(func, text="Functions")
    ctk.Label(
        func,
        text="You can define functions of any number of variables to be used later.\nHere is how to define a function 'f' of a variable 'x' which will return x^2:",
    ).grid(column=0, row=0, padx=10, pady=10)
    _help_code_label(func, "{func f, x, x^2}").grid(column=0, row=1, padx=10, pady=10)
    ctk.Label(func, text="You can now use it like this:").grid(
        column=0, row=2, padx=10, pady=10
    )
    _help_code_label(func, "f(5)").grid(column=0, row=3, padx=10, pady=10)
    ctk.Label(
        func,
        text="This will return 25.\nYou can also now use this function in things which take a function as an input. Eg:",
    ).grid(column=0, row=4, padx=10, pady=10)
    _help_code_label(func, "{plot f(x), x, -10, 10}").grid(
        column=0, row=5, padx=10, pady=10
    )
    ctk.Label(
        func,
        text="You can use this function in other things as well, for example integrals, derivatives, limits, etc...\nYou can also define a function of two or more variables.\nThis is the syntax:",
    ).grid(column=0, row=6, padx=10, pady=10)
    _help_code_label(
        func, "{func {function name}, {vars separated by spaces}, {return value}}"
    ).grid(column=0, row=7, padx=10, pady=10)
    ctk.Label(func, text="Here is an example of a function of two variables:").grid(
        column=0, row=8, padx=10, pady=10
    )
    _help_code_label(func, "{func f, x y, x^2+y^2}").grid(
        column=0, row=9, padx=10, pady=10
    )
    ctk.Label(func, text="You can now even plot this function using").grid(
        column=0, row=10, padx=10, pady=10
    )
    _help_code_label(func, "{plot3 f(x, y), x, y, -10, 10}").grid(
        column=0, row=11, padx=10, pady=10
    )
    ctk.Label(func, text="Images:").grid(column=1, row=0, padx=10, pady=10)
    _help_image_label(func, f"{rootdir}/Images/plotim.png", 3).grid(
        column=1, row=1, padx=10, pady=10
    )
    _help_image_label(func, f"{rootdir}/Images/plotim2.png", 3).grid(
        column=1, row=2, padx=10, pady=10
    )
    eq = ctk.Frame(hmgwin)
    tabs.add(eq, text="Defining Equations")
    ctk.Label(
        eq,
        text="If you have a long equation and want to solve it, you can define it first.\nHere is how to define an equation named 'something' which is 5x^2=25:",
    ).grid(column=0, row=0, padx=10, pady=10)
    _help_code_label(eq, "{eq something, 5x^2=25}").grid(
        column=0, row=1, padx=10, pady=10
    )
    ctk.Label(eq, text="You can now solve this using").grid(
        column=0, row=2, padx=10, pady=10
    )
    _help_code_label(eq, "{solve something, x}").grid(column=0, row=3, padx=10, pady=10)
    ctk.Label(eq, text="to get '[-sqrt(5), sqrt(5)]'.").grid(
        column=0, row=4, padx=10, pady=10
    )
    int = ctk.Frame(hmgwin)
    tabs.add(int, text="Integrals")
    ctk.Label(
        int,
        text="You can use defined functions as variables here.\nHere is how to find the indefinite integral of a function 'x^2':",
    ).grid(column=0, row=0, padx=10, pady=10)
    _help_code_label(int, "{integrate x^2, x}").grid(column=0, row=1, padx=10, pady=10)
    ctk.Label(
        int,
        text="This will return 'x^3/3'.\nIf you want to calculate a definite integral, just put the bounds at the end, separated by commas.\nFor example,",
    ).grid(column=0, row=2, padx=10, pady=10)
    _help_code_label(int, "{integrate x^2, x, 0, 1}").grid(
        column=0, row=3, padx=10, pady=10
    )
    ctk.Label(
        int,
        text="""This will return '0.333333333333333'.
If you have defined a function as a variable, you can integrate that too.
You can also put another command which returns a function like integral and derivative inside.
For example,""",
    ).grid(column=0, row=4, padx=10, pady=10)
    _help_code_label(int, "{func f, x, x^2}\n{integrate f(x), x}").grid(
        column=0, row=5, padx=10, pady=10
    )
    ctk.Label(int, text="This will also return 'x^3/3'.").grid(
        column=0, row=6, padx=10, pady=10
    )
    der = ctk.Frame(hmgwin)
    tabs.add(der, text="Derivatives")
    ctk.Label(
        der,
        text="The syntax of finding derivatives is very similar to finding integrals.\nJust type 'derivative' instead of 'integrate'.\nFor example, here is how to find the derivative of x^2:",
    ).grid(column=0, row=0, padx=10, pady=10)
    _help_code_label(der, "{derivative x^2, x}").grid(column=0, row=1, padx=10, pady=10)
    ctk.Label(
        der,
        text="In this too, like integrals (see Functions), you can put a named function inside.\nYou can also put another command which returns a function like integral and derivative inside.",
    ).grid(column=0, row=2, padx=10, pady=10)
    lim = ctk.Frame(hmgwin)
    tabs.add(lim, text="Limits")
    ctk.Label(
        lim,
        text="The syntax of finding limits is very similar to finding integrals and derivatives.\nYou can also specify the direction from which the limit is calculated.\nThe default is +. For example,",
    ).grid(column=0, row=0, padx=10, pady=10)
    _help_code_label(lim, "{limit abs(x)/x, x, 0}").grid(
        column=0, row=1, padx=10, pady=10
    )
    ctk.Label(lim, text="will give you '1', and").grid(
        column=0, row=2, padx=10, pady=10
    )
    _help_code_label(lim, "{limit abs(x)/x, x, 0, dir='-'}").grid(
        column=0, row=3, padx=10, pady=10
    )
    ctk.Label(
        lim,
        text="will give you '-1'.\nIn this too, like integrals and derivatives (see Functions), you can put a named function inside.\nYou can also put another command which returns a function like integral and derivative inside.",
    ).grid(column=0, row=4, padx=10, pady=10)
    sol = ctk.Frame(hmgwin)
    tabs.add(sol, text="Solving Equations")
    ctk.Label(
        sol,
        text="You can solve an equation that has been defined (See Defining Equations).\nYou can either have an equation with one variable, or many equations with many variables.\nLet us first look at how to solve an equation with one variable:",
    ).grid(column=0, row=0, padx=10, pady=10)
    _help_code_label(sol, "{solve {equation_name}, {equation_var}}").grid(
        column=0, row=1, padx=10, pady=10
    )
    ctk.Label(sol, text="is the general syntax. Fox example,").grid(
        column=0, row=2, padx=10, pady=10
    )
    _help_code_label(sol, "{eq something, x+3=5}\n{solve something, x}").grid(
        column=0, row=3, padx=10, pady=10
    )
    ctk.Label(
        sol,
        text="will give you '[2]'.\nThis can solve things of any order.\nIf there are multiple answers, you will get a list of the format '[a, b, c, ...]'.",
    ).grid(column=0, row=4, padx=10, pady=10)
    ctk.Label(
        sol,
        text="""The next is multiple equations with multiple variables.
This is also very easy.
Instead of one equation, you put a list of all your equations,
and instead of one variable, you put a list of all the variables.
For example, here is how to solve two simultaneous linear equations""",
    ).grid(column=0, row=5, padx=10, pady=10)
    _help_code_label(sol, "5x+6y=15\n2x+8y=9").grid(column=0, row=6, padx=10, pady=10)
    ctk.Label(sol, text=":").grid(column=0, row=7, padx=10, pady=10)
    _help_code_label(
        sol, "{eq one, 5x+6y=15}\n{eq two 2x+8y=9}\n{solve [one, two], [x, y]}"
    ).grid(column=0, row=8, padx=10, pady=10)
    ctk.Label(
        sol, text="This will give you an answer like '{x: 33/14, y: 15/28}'."
    ).grid(column=0, row=9, padx=10, pady=10)
    plt2 = ctk.Frame(hmgwin)
    tabs.add(plt2, text="Plotting 2D")
    ctk.Label(
        plt2,
        text="You can either plot a function of one variable, or a list of coordinates.\nBy default, if you close the plot and plot something else, that will get added to this plot,\nnot make a new graph. If you want to clear the plot, just type:",
    ).grid(column=0, row=0, padx=10, pady=10)
    _help_code_label(plt2, "clearplot").grid(column=0, row=1, padx=10, pady=10)
    ctk.Label(
        plt2, text="First, let's look at how to plot a function. The general syntax is:"
    ).grid(column=0, row=2, padx=10, pady=10)
    _help_code_label(
        plt2, "{plot {function}, {variable}, {start}, {end}, {options}}"
    ).grid(column=0, row=3, padx=10, pady=10)
    ctk.Label(
        plt2,
        text="In this too, you can put a named function (see Functions) inside.\nYou can also put another command which returns a function like an indefinite integral or derivative inside.\nHere is an example of a plot of x^2:",
    ).grid(column=0, row=4, padx=10, pady=10)
    _help_code_label(plt2, "{plot x^2, x, 0, 10}").grid(
        column=0, row=5, padx=10, pady=10
    )
    _help_image_label(plt2, f"{rootdir}/Images/plotim.png", 3).grid(
        column=2, row=1, padx=10, pady=10
    )
    ctk.Label(
        plt2, text="Here is an example of a plot of x^3 using a named function:"
    ).grid(column=0, row=6, padx=10, pady=10)
    _help_code_label(plt2, "{func f, x, x^3}\n{plot f(x), x, -10, 10}").grid(
        column=0, row=7, padx=10, pady=10
    )
    _help_image_label(plt2, f"{rootdir}/Images/plotim3.png", 3).grid(
        column=2, row=2, padx=10, pady=10
    )
    ctk.Label(
        plt2,
        text="You can also specify various 'options'. The basic ones for plotting a function are:",
    ).grid(column=1, row=0, padx=10, pady=10)
    ops = [
        "label: Makes a legend with the label",
        "xticks: Sets the xticks of the plot",
        "yticks: Sets the yticks of the plot",
        "x_label: Sets the label of the x axis",
        "y_label: Sets the label of the y axis",
        "title: Sets the title of the plot (by default just 'Plot')",
        "linspace: Sets the smoothness of the plot",
        "grid: Sets grid to 'True' or 'False'",
    ]
    opl = ctk.Listbox(plt2, width=50)
    for op in ops:
        opl.insert("end", op)
    opl.grid(column=1, row=1, padx=10, pady=10)
    ctk.Label(
        plt2,
        text="The xticks and yticks options take an input in the format of a list made with square brackets, and separated by commas.\nYou will have to use the option followed by an '=' and the value, separated by commas at the end of the plot command.\nHere is an example of a plot with a title:",
    ).grid(column=1, row=2, padx=10, pady=10)
    _help_code_label(plt2, "{plot x^2, x, 0, 10, title='Title'}").grid(
        column=1, row=3, padx=10, pady=10
    )
    ctk.Label(
        plt2,
        text="The syntax of plotting a list of coordinates is also very easy.\nHere is the general syntax:",
    ).grid(column=1, row=4, padx=10, pady=10)
    _help_code_label(plt2, "{plotlist {xs}, {ys}, {options}}").grid(
        column=1, row=5, padx=10, pady=10
    )
    ctk.Label(plt2, text="For example,").grid(column=1, row=6, padx=10, pady=10)
    _help_code_label(plt2, "{plotlist [1, 2, 3], [1, 2, 3]}").grid(
        column=1, row=7, padx=10, pady=10
    )
    _help_image_label(plt2, f"{rootdir}/Images/plotim4.png", 3).grid(
        column=2, row=3, padx=10, pady=10
    )
    _help_image_label(plt2, f"{rootdir}/Images/plotim5.png", 3).grid(
        column=2, row=3, padx=10, pady=10
    )
    ctk.Label(plt2, text="Images:").grid(column=2, row=0, padx=10, pady=10)
    pltpie = ctk.Frame(hmgwin)
    tabs.add(pltpie, text="Pie Charts")
    ctk.Label(
        pltpie,
        text="Making Pie Charts with MathGod is very easy.\nYou do not have to make the values add up to 1 or 100.\nHere is an example of a simple pie chart of 40% and 60%:",
    ).grid(column=0, row=0, padx=10, pady=10)
    _help_code_label(pltpie, "{pie [40, 60]}").grid(column=0, row=1, padx=10, pady=10)
    ctk.Label(
        pltpie, text="There are various options for a pie chart. The basic ones are:"
    ).grid(column=0, row=2, padx=10, pady=10)
    opspie = [
        "labels: Sets the labels of the sectors",
        "colors: Sets the colors of the sectors",
        "explode: Sets the distance each sector comes out by",
        "startangle: Sets the starting point of the first sector",
    ]
    oplpie = ctk.Listbox(pltpie, width=50)
    for op in opspie:
        oplpie.insert("end", op)
    oplpie.grid(column=0, row=3, padx=10, pady=10)
    ctk.Label(
        pltpie,
        text="""The labels, colors, and explode options get a list of the same size as the list of input values.
The startangle option is in degrees.
Here is an example of a pie chart of 3 sectors of the same size,
with labels 'a', 'b', 'c', the first one ('a') set to explode '0.1', and colors red, blue, and green:""",
    ).grid(column=0, row=4, padx=10, pady=10)
    _help_code_label(
        pltpie,
        "{pie [1, 1, 1], labels=['a', 'b', 'c'], colors=['red', 'blue', 'green'], explode=[0.1, 0, 0]}",
    ).grid(column=0, row=5, padx=10, pady=10)
    ctk.Label(pltpie, text="Images:").grid(column=1, row=0, padx=10, pady=10)
    _help_image_label(pltpie, f"{rootdir}/Images/plotim6.png", 3).grid(
        column=1, row=1, padx=10, pady=10
    )
    _help_image_label(pltpie, f"{rootdir}/Images/plotim7.png", 3).grid(
        column=1, row=2, padx=10, pady=10
    )
    pltbar = ctk.Frame(hmgwin)
    tabs.add(pltbar, text="Bar Charts")
    ctk.Label(
        pltbar,
        text="Making Bar Charts with MathGod is very simple. This is the general syntax:",
    ).grid(column=0, row=0, padx=10, pady=10)
    _help_code_label(pltbar, "{bar {xs}, {ys}, {options}}").grid(
        column=0, row=1, padx=10, pady=10
    )
    ctk.Label(pltbar, text="The basic options are:").grid(
        column=0, row=2, padx=10, pady=10
    )
    oplbar = ctk.Listbox(pltbar, width=50)
    opbar = [
        "color: Sets the color of the bars",
        "tick_label: Sets the label of each bar",
        "width: Sets the width of the bars",
    ]
    for op in opbar:
        oplbar.insert("end", op)
    oplbar.grid(column=0, row=3, padx=10, pady=10)
    ctk.Label(pltbar, text="Here is an example of a basic bar chart:").grid(
        column=0, row=4, padx=10, pady=10
    )
    _help_code_label(pltbar, "{bar [1, 2, 3], [1, 5, 3]}").grid(
        column=0, row=5, padx=10, pady=10
    )
    ctk.Label(pltbar, text="Images:").grid(column=1, row=0, padx=10, pady=10)
    _help_image_label(pltbar, f"{rootdir}/Images/plotim8.png", 3).grid(
        column=1, row=1, padx=10, pady=10
    )
    ctk.Label(
        pltbar,
        text="Here is an example of a bar chart labeled 'a', 'b', and 'c' with the color green with the width '0.1' of each bar:",
    ).grid(column=0, row=6, padx=10, pady=10)
    _help_code_label(
        pltbar,
        "{bar [1, 2, 3], [1, 5, 3], tick_label=['a', 'b', 'c'], color='green', width=0.1}",
    ).grid(column=0, row=7, padx=10, pady=10)
    _help_image_label(pltbar, f"{rootdir}/Images/plotim9.png", 3).grid(
        column=1, row=2, padx=10, pady=10
    )
    plt3 = ctk.Frame(hmgwin)
    tabs.add(plt3, text="Plotting 3D")
    ctk.Label(
        plt3,
        text="You can only 3D plot a function of two variables.\nThe general syntax is:",
    ).grid(column=0, row=0, padx=10, pady=10)
    _help_code_label(
        plt3,
        "{plot3  {func}, {var1}, {var2}, [{var1 start}, {var1 end}], [{var2 start}, {var2 end}], options}",
    ).grid(column=0, row=1, padx=10, pady=10)
    ctk.Label(plt3, text="The options are").grid(column=0, row=2, padx=10, pady=10)
    oplpl3 = ctk.Listbox(plt3, width=50)
    opspl3 = [
        "title: Sets the title of the plot",
        "grid: Sets the grid to True or False",
        "x_label: Sets the label of the x-axis",
        "y_label: Sets the label of the y-axis",
        "z_label: Sets the label of the z-axis",
        "linspace: Sets the smoothness of the plot",
    ]
    for op in opspl3:
        oplpl3.insert("end", op)
    oplpl3.grid(column=0, row=3, padx=10, pady=10)
    ctk.Label(
        plt3,
        text="You have to use the options followed by an '=' and then the value.\nHere is an example of a plot of x^2+y^2:",
    ).grid(column=0, row=4, padx=10, pady=10)
    _help_code_label(plt3, "{plot3 x^2+y^2, x, y, [-10, 10], [-10, 10]}").grid(
        column=0, row=5, padx=10, pady=10
    )
    ctk.Label(
        plt3,
        text="Here is an example of a plot of the same function but using a named function:",
    ).grid(column=0, row=6, padx=10, pady=10)
    _help_code_label(
        plt3, "{func f, x y, x^2+y^2}\n{plot3 f(x, y), x, y, [-10, 10], [-10, 10]}"
    ).grid(column=0, row=7, padx=10, pady=10)
    ctk.Label(plt3, text="Images:").grid(column=1, row=0, padx=10, pady=10)
    _help_image_label(plt3, f"{rootdir}/Images/plotim10.png", 3).grid(
        column=1, row=1, padx=10, pady=10
    )
    sum = ctk.Frame(hmgwin)
    tabs.add(sum, text="Summation and Products")
    ctk.Label(
        sum,
        text="Summation with MathGod is very easy.\nYou can either put an named function inside, or an unnamed one.\nHere is the general syntax:",
    ).grid(column=0, row=0, padx=10, pady=10)
    _help_code_label(sum, "{sum {func}, {var}, {start}, {end}}").grid(
        column=0, row=1, padx=10, pady=10
    )
    ctk.Label(sum, text="Here is an example of a sum of i from 1 to 10:").grid(
        column=0, row=2, padx=10, pady=10
    )
    _help_code_label(sum, "{sum i, i, 1, 10}").grid(column=0, row=3, padx=10, pady=10)
    ctk.Label(
        sum,
        text="This will return '55'. You can also put in named functions.\nHere is an example:",
    ).grid(column=0, row=4, padx=10, pady=10)
    _help_code_label(sum, "{func f, x, x}\n{sum f(i), i, 1, 10}").grid(
        column=0, row=5, padx=10, pady=10
    )
    ctk.Label(
        sum,
        text="This will also return the same output.\nYou can also put another variable inside the bounds.\nHere is an example:",
    ).grid(column=0, row=6, padx=10, pady=10)
    _help_code_label(sum, "{sum i, i, 1, n}").grid(column=0, row=7, padx=10, pady=10)
    ctk.Label(
        sum,
        text="This will return 'n^2/2 + n/2'.\nFinding products is exactly the same, except just 'prod' instead of 'sum'.\nHere is an example:",
    ).grid(column=0, row=8, padx=10, pady=10)
    _help_code_label(sum, "{prod i, i, 1, 10}").grid(column=0, row=9, padx=10, pady=10)
    ctk.Label(sum, text="This will return '3628800'.").grid(
        column=0, row=10, padx=10, pady=10
    )
    intp = ctk.Frame(hmgwin)
    tabs.add(intp, text="Interpolation")
    ctk.Label(
        intp,
        text="Interpolation returns a function that is the given value for all the given points. The general syntax is:",
    ).grid(column=0, row=0, padx=10, pady=10)
    _help_code_label(intp, "{interpolate [(x_1, y_1), (x_2, y_2), ...], {var}}").grid(
        column=0, row=1, padx=10, pady=10
    )
    ctk.Label(intp, text="Here is an example:").grid(column=0, row=2, padx=10, pady=10)
    _help_code_label(intp, "{interpolate [(0, 10), (1, 5), (2, -3)], x}").grid(
        column=0, row=3, padx=10, pady=10
    )
    ctk.Label(
        intp,
        text="This will return '-3x^2/2 - 7x/2 + 10'.\nIf you plot it, you can see that it actually passes through all the exact points:",
    ).grid(column=0, row=4, padx=10, pady=10)
    _help_code_label(
        intp,
        "{func f, x, {interpolate [(0, 10), (1, 5), (2, -3)], x}}\n{plot f(x), x, -5, 5, xticks=[0, 1, 2], yticks=[10, 5, -3], grid=True}",
    ).grid(column=0, row=5, padx=10, pady=10)
    ctk.Label(intp, text="Images:").grid(column=1, row=0, padx=10, pady=10)
    _help_image_label(intp, f"{rootdir}/Images/plotim11.png", 3).grid(
        column=1, row=1, padx=10, pady=10
    )
    cnd = ctk.Frame(hmgwin)
    tabs.add(cnd, text="Conditions")
    ctk.Label(
        cnd,
        text="There are two ways to create a function with a condition.\nThe first is using 'Piecewise', and the second is just using 'if'.\nLet's first look at the first method:",
    ).grid(column=0, row=0, padx=10, pady=10)
    _help_code_label(cnd, "{func f, x, Piecewise((x-1, x<0), (x+1, x>=0))}").grid(
        column=0, row=1, padx=10, pady=10
    )
    ctk.Label(
        cnd,
        text="This creates a function 'f', which is x-1 for x<0, and x+1 for x>=0.\nNow, the other way to create the same function is this:",
    ).grid(column=0, row=2, padx=10, pady=10)
    _help_code_label(cnd, "{func f, x, (x-1 if x<0 else x+1)}").grid(
        column=0, row=3, padx=10, pady=10
    )
    ctk.Label(
        cnd,
        text="With this method, to make multiple 'elif' conditions, you can stack the 'if's up.",
    ).grid(column=0, row=4, padx=10, pady=10)
    tabs.pack(fill="both", expand=True)
    ot = ctk.Frame(hmgwin)
    tabs.add(ot, text="Other")
    ctk.Label(
        ot,
        text="""Additionally, you can use any function from sympy, or any basic function from python.
For example, you can use range, map, min, max, subs, sin, cos, etc...
The functions from sympy like sin, cos, log, etc... will work with both symbols, and numbers.
Multiline python things like 'while', 'for', 'if', etc... will not work.
For example, if you want to just output the integral back without calculating it, you can type:""",
    ).grid(column=0, row=0, padx=10, pady=10)
    _help_code_label(ot, "Integral(x^2, x)").grid(column=0, row=1, padx=10, pady=10)
    ctk.Label(ot, text="OR").grid(column=0, row=2, padx=10, pady=10)
    _help_code_label(ot, "Integral(y^2, (y, 0, x))").grid(
        column=0, row=3, padx=10, pady=10
    )
    hmgwin.focus()


def rb():
    """Show instructions for recovering a file from its autosave backup."""
    state.root.info(
        "Recover Backup",
        """1. Go to the directory of the lost file
2. Press Ctrl+h to show hidden files if on Linux
3. You will see something like .filebackpynotes.txt
4. Copy it into the original lost file.
(This may not be an exact copy)""",
    )
