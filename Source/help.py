"""All of PyNotes' Help windows (About, Changes, and the various
Help-with-X topics), each a self-contained window builder."""

import easytk
import state
from init import v, rootdir, homedir, monospace
import pycode
import utils


def abt():
    """Show the About PyNotes window."""
    utils.show("open about pynotes")
    abw = state.root.subwin()
    abw.title("About PyNotes")
    abw.focus()
    abw_ = abw.frame()
    abw_.pack(fill="both", padx=10, pady=10)
    abw.imgs = []
    abw.image(master=abw_, image=f"{rootdir}/Icon.png", imsize=(2, 2)).grid(
        column=0, row=0, sticky="w"
    )
    abw.text(master=abw_, text=f"PyNotes v{v}", font=("TkDefaultFont", 20)).grid(
        column=0, row=1, sticky="w"
    )
    abw.text(
        master=abw_,
        text="Rafey <https://github.com/rafugafu>",
        font=("TkDefaultFont", 15),
    ).grid(column=0, row=2, sticky="w")
    abw.text(
        master=abw_,
        text="PyNotes is an advanced, extensible, cross-platform\nEmacs-like text editor and IDE made in Python.",
        font=("TkDefaultFont", 12),
    ).grid(column=0, row=3, sticky="w")
    abw.button(text="Close", command=abw.destroy).pack(
        side="bottom", fill="x", padx=10, pady=10
    )
    abw.bind("<Escape>", lambda event: abw.destroy())
    abw.bind("<Return>", lambda event: abw.destroy())
    abw.sizablefalse()


def changes():
    """Show the current version's changelog (state.changestr)."""
    utils.show("show pynotes changes")
    cw = state.root.subwin()
    cw.title(f"Changes in v{v}")
    chtextbox = cw.textbox(scrolled=True, font=("TkDefaultFont", 13), wrap="word")
    chtextbox.insert("end", state.changestr)
    chtextbox.text.config(state="disabled")
    chtextbox.yview_moveto(1)
    chtextbox.pack(fill="both", expand=True)
    cw.bind("<Escape>", lambda event: cw.destroy())
    cw.bind("<Return>", lambda event: cw.destroy())
    cw.sizablefalse()
    cw.style(state.root.gettheme())
    cw.focus()


def hemail():
    """Show the Help with Email window (setup and spellcheck dictionaries)."""
    utils.show("open email help")
    hew = state.root.subwin()
    hew.title("Help with Email")
    tabs = hew.tabs()
    mf = hew.frame()
    tabs.add(mf, text="Setup")
    tabs.pack(fill="both", expand=True, padx=10, pady=10)
    hew.text(
        master=mf,
        text="""Open the Email buffer with Alt-X and 'sendemail' or 'sendmail'.
Give the username and password of your email in that buffer.
Then you can type and send any email from PyNotes!""",
    ).grid(padx=10, pady=10)
    dt = hew.frame()
    tabs.add(dt, text="Dictionaries")
    hew.text(
        master=dt,
        text="""The email textbox has a spellcheck. The default dictionary for spellchecking is English,
but you can add or remove extra dictionaries to this.
To add another language or dictionary, you need to find or make a text file that has
one word in each line, without any spaces. (It can be any language)
Then go to Preferences → Email to upload that dictionary.

Once you have added a dictionary, don't move or remove the
dictionary before removing it in the settings.""",
    ).grid(padx=10, pady=10)
    hew.sizablefalse()
    hew.style(state.root.gettheme())
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
    hxs = hxw.scroll()
    hxs.pack(side="right", fill="y", padx=10, pady=10)
    hxh = hxw.textbox(wrap="word", yscrollcommand=hxs.set)
    hxs.config(command=hxh.yview)
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
'show-source' or 'source-code': Show any PyNotes source code file selected by you in /usr/share/PyNotes/ on Linux and C:/Program Files/PyNotes on Windows
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
'pynavstart:{f/fun/func/function/c/class/name}' or 'pyjumpstart:{f/fun/func/function/c/class/name}' or 'python-jump-startof:{f/fun/func/function/c/class/name}': If the HMode is Python, jump to the start of the current function/class the cursor is in if given f/fun/func/function/c/class, or jump to the start of the given function/class name
'pynavend:{f/fun/func/function/c/class/name}' or 'pyjumpend:{f/fun/func/function/c/class/name}' or 'python-jump-endof:{f/fun/func/function/c/class/name}': If the HMode is Python, jump to the end of the current function/class the cursor is in if given f/fun/func/function/c/class, or jump to the end of the given function/class name
'pygodef:{name}' or 'python-go-definition:{name}': If the HMode is Python, jump to the definition of the given name in the active editor
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
    hxw.sizablefalse()
    hxw.style(state.root.gettheme())
    hxh.bind("<Escape>", lambda event: hxh.destroy())
    hxh.bind("<Return>", lambda event: hxh.destroy())
    hxh.focus()


def helppycode():
    """Show the Help with PyCode window: syntax, commands, graphical
    coding, keyboard shortcuts, variables, functions, startup code,
    Alt-X command definitions, event hooks, and loops/conditions, each
    as its own tab."""
    utils.show("open pycode help")
    hpwin = state.root.subwin()
    hpwin.title("Help with PyCode")
    hptabs = hpwin.tabs()
    hptabs.pack(side="top", fill="both", padx=10, pady=10)
    bt = hpwin.frame()
    hptabs.add(bt, text="Basics")
    ct = hpwin.frame()
    hptabs.add(ct, text="Commands")
    gt = hpwin.frame()
    hptabs.add(gt, text="Graphical Coding")
    kst = hpwin.frame()
    hptabs.add(kst, text="Keyboard Shortcuts")
    vt = hpwin.frame()
    hptabs.add(vt, text="Variables")
    ft = hpwin.frame()
    hptabs.add(ft, text="Functions")
    st = hpwin.frame()
    hptabs.add(st, text="Startup Code")
    act = hpwin.frame()
    hptabs.add(act, text="Alt-X Command Definition")
    ht = hpwin.frame()
    hptabs.add(ht, text="Event Hooks")
    lct = hpwin.frame()
    hptabs.add(lct, text="Loops and Conditions")
    code = hpwin.style()
    code.configure(
        "CodeStyle.TLabel", background="white", padding=(7, 7, 7, 7), relief="sunken"
    )
    hpwin.text(
        master=bt,
        text="""Syntax -
All Keyboard Shortcuts, Event Hooks, Functions, and Startup Code should end with a semicolon ';'.
Inputs to a command must be given with one and only one space between
the command and the input.
If the input to a command is a string, it can only be inside single quotes 'input'.
Spaces do not matter between full commands and between brackets.
Newlines do not matter between full commands and between brackets.
For example, the code""",
    ).grid(column=0, row=0, padx=10, pady=10, sticky="w")
    hpwin.text(
        master=bt,
        text="(something) →: (say 'hello' ↩ say 'this is a test');",
        style="CodeStyle.TLabel",
    ).grid(column=0, row=1, padx=10, pady=10, sticky="w")
    hpwin.text(master=bt, text="is the same as").grid(
        column=0, row=2, padx=10, pady=10, sticky="w"
    )
    hpwin.text(
        master=bt,
        text="(\nsomething\n)\n→:\n(\nsay 'hello'\n↩\nsay 'this is a test'\n);",
        style="CodeStyle.TLabel",
    ).grid(column=0, row=3, padx=10, pady=10, sticky="w")
    hpwin.text(
        master=bt,
        text="""PyCode uses some symbols which are not on the keyboard.
To type '→', press 'Control + =' on your keyboard.
To type '↩', press 'Control + Enter'.
To type '↓', press 'Control + Down Arrow'.
To type '⌊', press 'Control + ['.
To type '⌋', press 'Control + ]'.
The functions and uses of these symbols are explained later in the Help.
PyCode also has a simple autocomplete to help you type code faster.
Typing any of these characters will make PyCode automatically close them with the opposite,
and put your cursor in the middle: '|/|', '</>', '(/)', '[/]', \"'/'\", '\"/\"'.
Pressing ';' will automatically put your cursor on a new line after the semicolon.
PyCode runs in the same global space as the rest of PyNotes.
So, you can access PyNotes variables directly, like 'active' for the currently active buffer.""",
    ).grid(column=0, row=4, padx=10, pady=10, sticky="w")
    hpwin.text(
        master=ct,
        text="These are all the commands in PyCode which you can use to make or change Functions, Keyboard Shortcuts,\nStartup Code, and Alt-X commands:",
    ).grid(column=0, row=0, padx=10, pady=10, sticky="w")
    pccmdlistcontainer = hpwin.textbox(master=ct, scrolled=True)
    pccmdlist = pccmdlistcontainer.text
    l1 = pccmdlist.index("end-1c")
    pccmdlist.insert("end", "PyNotes' Commands Help\n\n")
    r1 = pccmdlist.index("end-1c")
    pccmdlist.tag_add("bigstuff", l1, r1)
    pccmdlist.insert(
        "end",
        """aboutpynotes - Opens the PyNotes About.

ask 'prompt' - Asks an input from the user and returns the answer.

backspace - Presses BackSpace in the active editor: deletes the selection, or one indentation level if only whitespace is before the cursor, or the previous character.

balancebuffers 'all/horizontal/vertical' - Balance the horizontal/vertical/both buffers to make them equal size.`

cleareditor - Clears the active editor.

closebuffer n = current - Closes the nth buffer if n is given, defaults to the currently active buffer.

cmdrun 'command' - Runs the given Alt-X command.

color name, ... - Makes a tag named 'name' with the options .... Same options as tkinter textbox.tag_config. Can be used later with tag name, a, b.

commentregion 'a', 'b' - Coments the text from a given line number 'a' to a given line number 'b' in the active editor if the HMode is Python / LaTeX / HTML / Markdown.

commentselection - Comments the selected code if the HMode is Python / LaTeX / HTML / Markdown.

copy - Copies the selected text in the active editor.

copytext 'text' - Copies the given input to the clipboard

cut - Cuts the selected text in the active editor.

delete 'a', 'b' - Deletes the text from a given tkinter-style index 'a' to a given tkinter-style index 'b' in the active editor.

dictate - Opens the speech-to-text, lets you dictate text to the active editor.

downloadplugins - Automatically opens a link to the PyNotes GitHub Plugin page to let you download plugins in your default browser.

fileinfoconfig name_1 = val_1, name_2 = val_2, ... - Configs or reconfigs if already existent the names in the file info bar to the values in the active buffer. Editors have filename, filetype, filesize, and filesaved inbuilt, Terminals use buffertype, title, and command, the Python Shell uses buffertype and interpreter, and Email uses buffertype.

findreplace dir = 'forward' | 'backward' | 'beginning' - Opens Find & Replace with optional dir. Default dir = 'forward'.

findtext dir = 'forward' | 'backward' | 'beginning' - Opens Find with optional dir. Default dir = 'forward'.

fullscreen - Makes the PyNotes window fullscreen.

get 'a', 'b' - Gets the text in the active editor from a given tkinter style index 'a' to a given tkinter-style index 'b'.

getattr *args, **kwargs - Python getattr(*args, **kwargs).

getselection - Gets the range of the selected text in the active editor and returns it.

gotoline n = None - Moves the cursor to the given line number n if given, otherwise prompts the user for a line number and goes to it.

hmode 'py/la/html/md/norm' - Switches the HMode (PyNotes mode) to Python / LaTeX / HTML / Markdown / Normal.

indentregion 'a', 'b' - Indents the text from a given line number 'a' to a given line number 'b' in the active editor.

indentselection - Indents the selected region in the active editor.

insert 'index', 'text' - Inserts the text at a given tkinter-style index in the active editor.

killquit - Forcibly kills PyNotes without saving files or cleaning up.

mark 'a', 'b' - Visually marks the text between a tkinter-style index 'a' and a tkinter-style index 'b' in the active editor.

markselection - Visually marks the selected text in the active editor.

mathgod - Opens MathGod.

maximize - Maximizes the PyNotes window.

minimize - Minimizes the PyNotes window.

movecursor 'index' - Moves the cursor to a given tkinter-style index in the active editor.

neweditor file = None, orient = 'horizontal' - Opens a new editor loading file if given and being horizontal or vertical depending on orient (default 'horizontal').

newfile - Opens a new file in the currently active editor.

openemailbuf - Opens (or switches to) the standalone Email buffer.

openfile - Opens a file picker to open a file in the currently active editor.

openfilenewedit orient = 'horizontal' - Opens a new editor with orientation orient (default horizontal) loading the file from a filedialog that is shown.

openhelp 'commands/email/pycode/mathgod/plugins' - Opens the Help about the given feature.

openplugindir - Opens the plugins directory in your file manager.

openpycode - Opens PyCode.

openterm command = None, title = 'Terminal', endmessage = None, blocking = False, orient = 'vertical' - Opens the PyNotes terminal in a buffer with orientation orient running a given command list (example [command, input1, input2]), /bin/bash or powershell.exe if not specified. Set optional title (the title of the terminal buffer) and endmessage (the message shown at the end after the process stops, terminal buffer closes immediately if no endmessage is set). If blocking is set to True (default False), it doesn't return till the process finishes.

pageback - Goes to the previous page in the active editor.

pageforw - Goes to the next page in the active editor.

pass - Do nothing.

paste - Pastes your clipboard in the active editor.

preferences - Opens the PyNotes preferences.

prompt text, autocompletefunc = None, defaultinput = None - Prompts the user with text in the Alt-X command box and returns input. Calls the function inside the string autocomplete with the currently typed text if it is a string, otherwise uses the fixed list/tuple if given in it when Tab is pressed. If defaultinput is given, starts the prompt with it.

pynotessourcecode - Show any PyNotes source code file selected by you in /usr/share/PyNotes/ on Linux and C:/Program Files/PyNotes on Windows in a new editor.

pyshell orient = 'vertical' - Opens a Python REPL buffer in the given orientation.

pythongoendof 'f/fun/func/function/c/class/name' - If the HMode is Python, jumps to the end of the current function/class the cursor is in if given 'f/fun/func/function/c/class', otherwise jumps to the end of the given function/class name if it exists in the active editor.

pythongostartof 'f/fun/func/function/c/class/name' - If the HMode is Python, jumps to the start of the current function/class the cursor is in if given 'f/fun/func/function/c/class', otherwise jumps to the start of the given function/class name if it exists in the active editor.

pythongodef 'name' - If the HMode is Python, jumps to the definition of the given name in the active editor.

quit - Cleanly closes PyNotes.

redo - Redos the last undo in the active editor.

repeatxcommand 'command', n - Repeats the given Alt-X command n times.

removeselectionpoint - Removes the selection point if set.

return value - Returns the given value from a function.

runcode - Runs the code in the active editor if the HMode is Python / LaTeX / HTML.

saveasfile - Save the text in the active editor to another filename.

savefile - Saves the file in the active editor.

say 'input' - Opens a graphical messagebox showing the given input. You can also use a variable here.

selall - Selects all the text in the active editor.

select 'a', 'b' - Selects the text from a given tkinter-style index 'a' to a given tkinter-style index 'b' in the active editor.

setattr *args, **kwargs - Python setattr(*args, **kwargs).

setselectionpoint index = None - Sets the selection point at the index if given, otherwise cursor position.

setvar 'var', 'val' - Makes a variable with a given name 'var' and a given value 'val'.

setwingeometry geo - Calls the tkinter root.geometry(geo).

setwintitle 'title' - Sets the title of the PyNotes window to a given string.

show 'text' - Shows the given text in the Alt-X command box.

speaktext - Speaks the selected text in the active editor.

spliteditor n = active, orient = 'horizontal' - Splits the nth editor (default active) horizontally or vertically depending on orient (default horizontal).

switchbuffer n = current + 1 - Switches focus to the nth buffer if given n, otherwise cycle buffers.

tag ... - Uses a tag previously set with color name, ... . Same options as tkinter textbox.tag_add.

termexec 'command' - Executes the given command in a terminal and shows the output in the Alt-X command box.

tkindex 'toindex', (optional: 'line') - Indexes the given tkinter-style input in the active editor and returns the output. If the optional 'line' input is also given, it returns only the linenumber as a string.

toggleselectionpoint - Sets the selection point at the cursor if not set, otherwise removes it.

typecommand - Lets you type an Alt-X command.

uncommentregion a, b - Uncomments the text from a given line number a to another given line number b in the active editor if the HMode is Python / LaTeX / HTML / Markdown.

uncommentselection - Uncomments the selected text in the active editor if the HMode is Python / LaTeX / HTML / Markdown.

undo - Undoes the last edit in the active editor.

unfullscreen - Makes PyNotes windowed mode from fullscreen.

unindentregion a, b - Unindents the text from a given line number a to another given line number b in the active editor if the HMode is Python / LaTeX / HTML / Markdown.

unindentselection - Unindents the selected text in the active editor.

unmark 'a', 'b' - Unmark the visually marked text in the active editor from a tkinter-style index 'a' to a tkinter-style index 'b'.

unmarkall - Unmarks all the visually marked text in the active editor.

unmaximize - Unmaximizes the main window.

unsetwintitle - Sets the window title back to normal after the command 'setwintitle'

untag ... - Untags a tag previouslyl set with tag .... Same options as tkinter textbox.tag_remove.

wait n - Freezes PyNotes for n seconds.

write 'text', n - Writes the given text repeated n times in the active editor.""",
    )
    l2 = pccmdlist.index("end-1c")
    if state.plgnspccmdhelp:
        pccmdlist.insert("end", "\n\nPlugins' Commands Help")
    r2 = pccmdlist.index("end-1c") + "+2c"
    pccmdlist.insert("end-1c", state.plgnspccmdhelp)
    pccmdlist.tag_add("bigstuff", l2, r2)
    pccmdlist.tag_config("bigstuff", font=(monospace, 15, "bold"))
    pccmdlist.config(state="disabled")
    pccmdlistcontainer.grid(column=0, row=1, padx=10, pady=10, sticky="nsew")
    hpwin.text(
        master=ct,
        text="By default, a command will take all the text that comes after it after a space as it's input.\nTo avoid that, you can give the input inside () brackets.\nThen, the command will only take the text after itself which is inside the brackets as input.",
    ).grid(column=0, row=2, padx=10, pady=10, sticky="w")
    ct.grid_columnconfigure(0, weight=1)
    hpwin.text(
        master=gt,
        text="""There is a dropdown menu in the top left corner, using which you can code graphically.
Whenever you click something in it, it will ask for inputs.
It will also show a list of all the commands on the side if it needs it.
Then, you can click any commands you want, and it will put them in the
Function / Keyboard Shortcut / Startup Code in order.
It will not ask for the inputs of commands that take inputs,
you will have to put those in the code yourself.""",
    ).grid(column=0, row=0, padx=10, pady=10, sticky="w")
    state.root.image(
        master=gt, image=f"{rootdir}/Images/PYCODE1.png", imsize=(2, 2)
    ).grid(column=0, row=1, padx=10, pady=10, sticky="w")
    state.root.image(
        master=gt, image=f"{rootdir}/Images/PYCODE2.png", imsize=(2, 2)
    ).grid(column=1, row=1, padx=10, pady=10, sticky="e")
    hpwin.text(
        master=kst,
        text="""You can bind or rebind Keyboard Shortcuts to any of the PyCode commands.
To put more than one command in a Keyboard Shortcut, separate them with '↩'.
If you want to make a keyboard shortcut where you have to press and hold 2 keys,
(eg. Control or Alt + something else), you will have to put a dash between them.
Control and Alt keys, when used, can never be after a normal letter.
You can never repeat Control or Alt keys in the same keyboard shortcut.
You can bind keys to any commands, or a function made by you.
This uses the same syntax as tkinter's bindings.
If you do not know how to bind a key to something, you can use the graphical coding.
There, PyCode will automatically detect which keys you press and put them in the code.
You can also bind chord keys like Control-x Control-s by separating the keys inside the first '<>' with '&'.
You cannot bind chord keys using the graphical programming till now.
Examples:""",
    ).grid(column=0, row=0, padx=10, pady=10, sticky="w")
    hpwin.text(
        master=kst, text="<Control-q> → <close>;", style="CodeStyle.TLabel"
    ).grid(column=0, row=1, padx=10, pady=10, sticky="w")
    hpwin.text(
        master=kst,
        text="<Control-x & Control-s> → <savefile>;",
        style="CodeStyle.TLabel",
    ).grid(column=0, row=2, padx=10, pady=10, sticky="w")
    hpwin.text(
        master=kst,
        text="<Control-t> → <say 'Hello!' ↩ say 'PyNotes is the best!'>;",
        style="CodeStyle.TLabel",
    ).grid(column=0, row=3, padx=10, pady=10, sticky="w")
    hpwin.text(
        master=vt,
        text="""Variables can be defined using the PyCode command 'setvar'.
This can be used like a normal PyCode command.
The syntax is: setvar 'varname', value.
For example, here is how to make a variable named 'something' with the value 'something else' on startup:""",
    ).grid(column=0, row=0, padx=10, pady=10, sticky="w")
    hpwin.text(
        master=vt,
        text="|setvar 'something', 'something else'|;",
        style="CodeStyle.TLabel",
    ).grid(column=0, row=1, padx=10, pady=10, sticky="w")
    hpwin.text(
        master=vt,
        text="This can then be used in Keyboard Shortcuts and Functions like this:",
    ).grid(column=0, row=2, padx=10, pady=10, sticky="w")
    hpwin.text(
        master=vt, text="<Control-q> → <say something>;", style="CodeStyle.TLabel"
    ).grid(column=0, row=3, padx=10, pady=10, sticky="w")
    hpwin.text(master=ft, text="The syntax to define a function is:").grid(
        column=0, row=0, padx=10, pady=10, sticky="w"
    )
    hpwin.text(
        master=ft, text="(funcname:args) →: (commands);", style="CodeStyle.TLabel"
    ).grid(column=0, row=1, padx=10, pady=10, sticky="w")
    hpwin.text(
        master=ft,
        text="""The input definition syntax is exactly like Python's function inputs.
The commands inside the function are separated by a '↩'. For example, here is how to make a function named 'something'
which clears the editor and writes any given text 5 times
with a default value of 'text':""",
    ).grid(column=0, row=2, padx=10, pady=10, sticky="w")
    hpwin.text(
        master=ft,
        text="(something:text = 'text') →: (cleareditor ↩ write text, 5);",
        style="CodeStyle.TLabel",
    ).grid(column=0, row=3, padx=10, pady=10, sticky="w")
    hpwin.text(
        master=ft,
        text="This can then be used in other Functions, Keyboard Shortcuts, Startup Code, and Alt-X commands like a normal PyCode command.",
    ).grid(column=0, row=4, padx=10, pady=10, sticky="w")
    hpwin.text(
        master=ft,
        text="If you want to make a more complex function that cannot be made with normal PyCode commands,\nyou can make a Python Function in PyCode.\nThe syntax is:",
    ).grid(column=0, row=5, padx=10, pady=10, sticky="w")
    hpwin.text(
        master=ft,
        text="(python:funcname:args) → (python code);",
        style="CodeStyle.TLabel",
    ).grid(column=0, row=6, padx=10, pady=10, sticky="w")
    hpwin.text(
        master=ft,
        text="""The input definition syntax is exactly the same as normal PyCode functions,
and the inputs also work exactly the same way.
The lines of the Python code are separated by a '↩', not newlines.
Also remember to put the 'python:' prefix before the name of the function.
To use PyCode commands in a Python function, use the prefix 'pycode:' before the command, and put the command in curly brackets.
There cannot be any spaces between the 'pycode' and the semicolon.
PyCode commands used in a Python function should maintain proper indentation in the Python code.
For example, here is how to make a Python function named 'something' that asks for 1+1 and shows 'correct' or 'wrong' for the answer in the Alt-X command box:""",
    ).grid(column=0, row=7, padx=10, pady=10, sticky="w")
    hpwin.text(
        master=ft,
        text="""(python:something) →: (
useranswer = int(root.askstring('Question', 'What is 1+1?')) ↩
if useranswer == 2: ↩
    pycode:{show 'correct'} ↩
else: ↩
    pycode:{show 'wrong'}
);""",
        style="CodeStyle.TLabel",
    ).grid(column=0, row=8, padx=10, pady=10, sticky="w")
    hpwin.text(
        master=st,
        text="""Startup Code runs automatically every time PyNotes starts.
This can be used to execute some commands everytime on startup or configure PyNotes in some way.
Everything that is inside a '| |' is executed as startup code.
To run multiple commands on startup, you can use a Function,
have multiple '| |'s, or separate the commands inside one
'| |' with '↩'.
For example, these are all the ways you can make PyNotes start with an empty editor instead of the Zen of Python in Python HMode:""",
    ).grid(column=0, row=0, padx=10, pady=10, sticky="w")
    hpwin.text(
        master=st,
        text="(startup) →: (newfile ↩ hmode 'py');\n|startup|;",
        style="CodeStyle.TLabel",
    ).grid(column=0, row=1, padx=10, pady=10, sticky="w")
    hpwin.text(
        master=st, text="|newfile|;\n|hmode 'py'|;", style="CodeStyle.TLabel"
    ).grid(column=0, row=2, padx=10, pady=10, sticky="w")
    hpwin.text(
        master=st, text="|newfile ↩ hmode 'py'|;", style="CodeStyle.TLabel"
    ).grid(column=0, row=3, padx=10, pady=10, sticky="w")
    hpwin.text(
        master=act,
        text="You can make or change Alt-X commands in PyCode.\nPyCode commands inside the Alt-X command definition are separated by a '↩'. The syntax is:",
    ).grid(column=0, row=0, padx=10, pady=10, sticky="w")
    hpwin.text(
        master=act, text="⌊cmdname⌋ → ⌊commands⌋;", style="CodeStyle.TLabel"
    ).grid(column=0, row=1, padx=10, pady=10, sticky="w")
    hpwin.text(
        master=act,
        text="Any input given from the Alt-X command will be saved to the variable 'commandinput'.\nYou can then use it in PyCode commands. For example, here is how to make an Alt-X command named 'tktemplate' which writes code in the editor that\nopens a window using easytk with the title and text 'PyCode Easytk Window Template':",
    ).grid(column=0, row=2, padx=10, pady=10, sticky="w")
    hpwin.text(
        master=act,
        text=r"""
⌊tktemplate⌋
→
⌊
newfile ↩
hmode 'py' ↩
write '
import easytk\n
root = easytk.win()\n
root.title("PyCode Easytk Window Template")\n
root.text(text = "PyCode Easytk Window Template").grid()\n
root.show()',
1
⌋;
""",
        style="CodeStyle.TLabel",
    ).grid(column=0, row=3, padx=10, pady=10, sticky="w")
    hpwin.text(
        master=ht,
        text="You can make event hooks to execute some code before or after the event runs.\nThe syntax is:",
    ).grid(column=0, row=0, padx=10, pady=10, sticky="w")
    hpwin.text(
        master=ht, text="[before/after:event] :→ [pycode];", style="CodeStyle.TLabel"
    ).grid(column=0, row=1, padx=10, pady=10, sticky="w")
    hpwin.text(
        master=ht,
        text="Commands should be separated with a '↩'.\nThese are all the events you can hook into:",
    ).grid(column=0, row=2, padx=10, pady=10, sticky="w")
    pceventhooklistcontainer = hpwin.textbox(master=ht, scrolled=True)
    pceventhooklist = pceventhooklistcontainer.text
    pceventhooklist.insert(
        "end",
        """new-file-current-editor

new-file-new-editor

open-file-current-editor

open-file-new-editor

save-file

save-as-file

exit-pynotes

close-buffer

switch-buffer

run-code

mark-region

unmark-region

comment-region

uncomment-region

indent-region

unindent-region

open-mathgod

term-exec

alt-x-command:{command}

pycode-command:{command}

undo

redo

show-pynotes-source-code

open-terminal

open-preferences

next-page

previous-page

copy-text

paste-text

cut-text

fullscreen

un-fullscreen

maximize-window

unmaximize-window

minimize-window

clear-editor

open-pycode

change-hmode

open-python-shell

open-email-buffer

resize-window""",
    )
    pceventhooklist.config(state="disabled")
    pceventhooklistcontainer.grid(column=0, row=3, padx=10, pady=10, sticky="nsew")
    hpwin.text(
        master=ht,
        text="""The events 'open-file-current-editor' (filename, or None if cancelled), 'open-file-new-editor' (filename, or None if cancelled),
'save-as-file' (filename, or None if cancelled), 'switch-buffer' (new editor number),'*-region' (tuple (a, b) containing the incides of the region), 'term-exec' (command), 'open-terminal' (command),
alt-x-command (command input),pycode-command (command input), 'change-hmode' (new HMode), 'copy-text' (selected text),
'cut-text' (selected text), 'paste-text' (pasted text) will all set a variable 'commandinput' for the code to run which contains
the previously shown possible inputs. For events involving a file dialog, the 'before' hook runs after the dialog closes (with commandinput
set to None if the dialog was cancelled), but the 'after' hook only runs if the dialog was not cancelled.""",
    ).grid(column=0, row=4, padx=10, pady=10, sticky="w")
    hpwin.text(master=ht, text="Example:").grid(
        column=0, row=5, padx=10, pady=10, sticky="w"
    )
    hpwin.text(
        master=ht,
        text="[after:new-file-current-editor] :→ [hmode 'py'];\n[after:new-file-new-editor] :→ [hmode 'py'];",
        style="CodeStyle.TLabel",
    ).grid(column=0, row=6, padx=10, pady=10, sticky="w")
    hpwin.text(master=lct, text="The syntax to make conditions in PyCode is:").grid(
        column=0, row=0, padx=10, pady=10, sticky="w"
    )
    hpwin.text(
        master=lct,
        text="if (condition) {code} elif (condition) {code} else (condition) {code}",
        style="CodeStyle.TLabel",
    ).grid(column=0, row=1, padx=10, pady=10, sticky="w")
    hpwin.text(
        master=lct,
        text="""These can be put anywhere where normal PyCode commands can be used, in Keyboard Shortcuts, Functions, Python Functions pycode:{} wrappers, etc.
You can have any number of 'elif's in the condition.
The code inside these conditions is separated by '↓'s.
Make sure to not put any '↩'s, semicolons, etc between the 'if's, 'elif's, and 'else's, because they are all part of the same statement.
Example:""",
    ).grid(column=0, row=2, padx=10, pady=10, sticky="w")
    hpwin.text(
        master=lct,
        text="(sayhellofunc) →:\n(\nif (ask ('Say hello.') == 'hello') {\nsay 'Good job!'\n}\nelse {\nsay 'You did not say hello'\n}\n);",
        style="CodeStyle.TLabel",
    ).grid(column=0, row=3, padx=10, pady=10, sticky="w")
    hpwin.text(
        master=lct, text="The syntax of making loops in PyCode is very similar:"
    ).grid(column=0, row=4, padx=10, pady=10, sticky="w")
    hpwin.text(
        master=lct, text="while (condition) {code}", style="CodeStyle.TLabel"
    ).grid(column=0, row=5, padx=10, pady=10, sticky="w")
    hpwin.text(
        master=lct, text="The code inside the loop is also separated by '↓'s.\nExample:"
    ).grid(column=0, row=6, padx=10, pady=10, sticky="w")
    hpwin.text(
        master=lct, text="while (True) {say 'Spam'}", style="CodeStyle.TLabel"
    ).grid(column=0, row=7, padx=10, pady=10, sticky="w")
    hpwin.sizablefalse()
    hpwin.style(state.root.gettheme())
    hpwin.focus()


def ap():
    """Show the Add Plugins window: install steps plus shortcuts to
    download plugins or open the add-ons directory."""
    utils.show("open plugin help")
    apw = state.root.subwin()
    apw.title("Add Plugins")
    apw.text(
        text=f"1. Download a plugin\n2. Extract the plugin if it is a zip\n3. Move the folder to {homedir}/.local/share/PyNotes/add-ons\n4. Restart PyNotes"
    ).grid(column=0, row=0, padx=10, pady=10, sticky="w")
    apw.button(text="Download From PyNotes' GitHub", command=utils.dp).grid(
        column=0, row=1, padx=10, pady=10, sticky="w"
    )
    apw.button(text="Open Plugins Directory", command=utils.op).grid(
        column=0, row=2, padx=10, pady=10, sticky="w"
    )
    apw.text(
        text="Warning: Plugins have full access to PyNotes and your system\nand can run any commands. Be careful in downloading and using\nplugins from other websites.",
        font=(monospace, 12, "bold"),
    ).grid(column=0, row=3, padx=10, pady=10, sticky="w")
    apw.style(state.root.gettheme())
    apw.focus()


def helpmathgod():
    """Show the Help with MathGod window: variables, functions,
    equations, calculus, plotting (2D/3D/pie/bar), summation/products,
    interpolation, conditions, and other (raw sympy/Python) functions,
    each as its own tab."""
    utils.show("open mathgod help")
    hmgwin = state.root.subwin()
    hmgwin.title("Help with MathGod")
    code = hmgwin.style()
    code.configure(
        "CodeStyle.TLabel", background="white", padding=(7, 7, 7, 7), relief="sunken"
    )
    tabs = hmgwin.tabs()
    vars = hmgwin.frame()
    tabs.add(vars, text="Variables")
    hmgwin.text(
        master=vars, text="You can define variables using the standard python syntax:"
    ).grid(column=0, row=0, padx=10, pady=10)
    hmgwin.text(
        master=vars, text="{varname} = {varval}", style="CodeStyle.TLabel"
    ).grid(column=0, row=1, padx=10, pady=10)
    hmgwin.text(master=vars, text="Here is an example:").grid(
        column=0, row=2, padx=10, pady=10
    )
    hmgwin.text(master=vars, text="v = 5\nv\nv + 1", style="CodeStyle.TLabel").grid(
        column=0, row=3, padx=10, pady=10
    )
    hmgwin.text(master=vars, text="This will return 5 and 6.").grid(
        column=0, row=4, padx=10, pady=10
    )
    func = hmgwin.frame()
    tabs.add(func, text="Functions")
    hmgwin.text(
        master=func,
        text="You can define functions of any number of variables to be used later.\nHere is how to define a function 'f' of a variable 'x' which will return x^2:",
    ).grid(column=0, row=0, padx=10, pady=10)
    hmgwin.text(master=func, text="{func f, x, x^2}", style="CodeStyle.TLabel").grid(
        column=0, row=1, padx=10, pady=10
    )
    hmgwin.text(master=func, text="You can now use it like this:").grid(
        column=0, row=2, padx=10, pady=10
    )
    hmgwin.text(master=func, text="f(5)", style="CodeStyle.TLabel").grid(
        column=0, row=3, padx=10, pady=10
    )
    hmgwin.text(
        master=func,
        text="This will return 25.\nYou can also now use this function in things which take a function as an input. Eg:",
    ).grid(column=0, row=4, padx=10, pady=10)
    hmgwin.text(
        master=func, text="{plot f(x), x, -10, 10}", style="CodeStyle.TLabel"
    ).grid(column=0, row=5, padx=10, pady=10)
    hmgwin.text(
        master=func,
        text="You can use this function in other things as well, for example integrals, derivatives, limits, etc...\nYou can also define a function of two or more variables.\nThis is the syntax:",
    ).grid(column=0, row=6, padx=10, pady=10)
    hmgwin.text(
        master=func,
        text="{func {function name}, {vars separated by spaces}, {return value}}",
        style="CodeStyle.TLabel",
    ).grid(column=0, row=7, padx=10, pady=10)
    hmgwin.text(
        master=func, text="Here is an example of a function of two variables:"
    ).grid(column=0, row=8, padx=10, pady=10)
    hmgwin.text(
        master=func, text="{func f, x y, x^2+y^2}", style="CodeStyle.TLabel"
    ).grid(column=0, row=9, padx=10, pady=10)
    hmgwin.text(master=func, text="You can now even plot this function using").grid(
        column=0, row=10, padx=10, pady=10
    )
    hmgwin.text(
        master=func, text="{plot3 f(x, y), x, y, -10, 10}", style="CodeStyle.TLabel"
    ).grid(column=0, row=11, padx=10, pady=10)
    hmgwin.text(master=func, text="Images:").grid(column=1, row=0, padx=10, pady=10)
    state.root.image(
        master=func, image=f"{rootdir}/Images/plotim.png", imsize=(3, 3)
    ).grid(column=1, row=1, padx=10, pady=10)
    state.root.image(
        master=func, image=f"{rootdir}/Images/plotim2.png", imsize=(3, 3)
    ).grid(column=1, row=2, padx=10, pady=10)
    eq = hmgwin.frame()
    tabs.add(eq, text="Defining Equations")
    hmgwin.text(
        master=eq,
        text="If you have a long equation and want to solve it, you can define it first.\nHere is how to define an equation named 'something' which is 5x^2=25:",
    ).grid(column=0, row=0, padx=10, pady=10)
    hmgwin.text(
        master=eq, text="{eq something, 5x^2=25}", style="CodeStyle.TLabel"
    ).grid(column=0, row=1, padx=10, pady=10)
    hmgwin.text(master=eq, text="You can now solve this using").grid(
        column=0, row=2, padx=10, pady=10
    )
    hmgwin.text(master=eq, text="{solve something, x}", style="CodeStyle.TLabel").grid(
        column=0, row=3, padx=10, pady=10
    )
    hmgwin.text(master=eq, text="to get '[-sqrt(5), sqrt(5)]'.").grid(
        column=0, row=4, padx=10, pady=10
    )
    int = hmgwin.frame()
    tabs.add(int, text="Integrals")
    hmgwin.text(
        master=int,
        text="You can use defined functions as variables here.\nHere is how to find the indefinite integral of a function 'x^2':",
    ).grid(column=0, row=0, padx=10, pady=10)
    hmgwin.text(master=int, text="{integrate x^2, x}", style="CodeStyle.TLabel").grid(
        column=0, row=1, padx=10, pady=10
    )
    hmgwin.text(
        master=int,
        text="This will return 'x^3/3'.\nIf you want to calculate a definite integral, just put the bounds at the end, separated by commas.\nFor example,",
    ).grid(column=0, row=2, padx=10, pady=10)
    hmgwin.text(
        master=int, text="{integrate x^2, x, 0, 1}", style="CodeStyle.TLabel"
    ).grid(column=0, row=3, padx=10, pady=10)
    hmgwin.text(
        master=int,
        text="""This will return '0.333333333333333'.
If you have defined a function as a variable, you can integrate that too.
You can also put another command which returns a function like integral and derivative inside.
For example,""",
    ).grid(column=0, row=4, padx=10, pady=10)
    hmgwin.text(
        master=int,
        text="{func f, x, x^2}\n{integrate f(x), x}",
        style="CodeStyle.TLabel",
    ).grid(column=0, row=5, padx=10, pady=10)
    hmgwin.text(master=int, text="This will also return 'x^3/3'.").grid(
        column=0, row=6, padx=10, pady=10
    )
    der = hmgwin.frame()
    tabs.add(der, text="Derivatives")
    hmgwin.text(
        master=der,
        text="The syntax of finding derivatives is very similar to finding integrals.\nJust type 'derivative' instead of 'integrate'.\nFor example, here is how to find the derivative of x^2:",
    ).grid(column=0, row=0, padx=10, pady=10)
    hmgwin.text(master=der, text="{derivative x^2, x}", style="CodeStyle.TLabel").grid(
        column=0, row=1, padx=10, pady=10
    )
    hmgwin.text(
        master=der,
        text="In this too, like integrals (see Functions), you can put a named function inside.\nYou can also put another command which returns a function like integral and derivative inside.",
    ).grid(column=0, row=2, padx=10, pady=10)
    lim = hmgwin.frame()
    tabs.add(lim, text="Limits")
    hmgwin.text(
        master=lim,
        text="The syntax of finding limits is very similar to finding integrals and derivatives.\nYou can also specify the direction from which the limit is calculated.\nThe default is +. For example,",
    ).grid(column=0, row=0, padx=10, pady=10)
    hmgwin.text(
        master=lim, text="{limit abs(x)/x, x, 0}", style="CodeStyle.TLabel"
    ).grid(column=0, row=1, padx=10, pady=10)
    hmgwin.text(master=lim, text="will give you '1', and").grid(
        column=0, row=2, padx=10, pady=10
    )
    hmgwin.text(
        master=lim, text="{limit abs(x)/x, x, 0, dir='-'}", style="CodeStyle.TLabel"
    ).grid(column=0, row=3, padx=10, pady=10)
    hmgwin.text(
        master=lim,
        text="will give you '-1'.\nIn this too, like integrals and derivatives (see Functions), you can put a named function inside.\nYou can also put another command which returns a function like integral and derivative inside.",
    ).grid(column=0, row=4, padx=10, pady=10)
    sol = hmgwin.frame()
    tabs.add(sol, text="Solving Equations")
    hmgwin.text(
        master=sol,
        text="You can solve an equation that has been defined (See Defining Equations).\nYou can either have an equation with one variable, or many equations with many variables.\nLet us first look at how to solve an equation with one variable:",
    ).grid(column=0, row=0, padx=10, pady=10)
    hmgwin.text(
        master=sol,
        text="{solve {equation_name}, {equation_var}}",
        style="CodeStyle.TLabel",
    ).grid(column=0, row=1, padx=10, pady=10)
    hmgwin.text(master=sol, text="is the general syntax. Fox example,").grid(
        column=0, row=2, padx=10, pady=10
    )
    hmgwin.text(
        master=sol,
        text="{eq something, x+3=5}\n{solve something, x}",
        style="CodeStyle.TLabel",
    ).grid(column=0, row=3, padx=10, pady=10)
    hmgwin.text(
        master=sol,
        text="will give you '[2]'.\nThis can solve things of any order.\nIf there are multiple answers, you will get a list of the format '[a, b, c, ...]'.",
    ).grid(column=0, row=4, padx=10, pady=10)
    hmgwin.text(
        master=sol,
        text="""The next is multiple equations with multiple variables.
This is also very easy.
Instead of one equation, you put a list of all your equations,
and instead of one variable, you put a list of all the variables.
For example, here is how to solve two simultaneous linear equations""",
    ).grid(column=0, row=5, padx=10, pady=10)
    hmgwin.text(master=sol, text="5x+6y=15\n2x+8y=9", style="CodeStyle.TLabel").grid(
        column=0, row=6, padx=10, pady=10
    )
    hmgwin.text(master=sol, text=":").grid(column=0, row=7, padx=10, pady=10)
    hmgwin.text(
        master=sol,
        text="{eq one, 5x+6y=15}\n{eq two 2x+8y=9}\n{solve [one, two], [x, y]}",
        style="CodeStyle.TLabel",
    ).grid(column=0, row=8, padx=10, pady=10)
    hmgwin.text(
        master=sol, text="This will give you an answer like '{x: 33/14, y: 15/28}'."
    ).grid(column=0, row=9, padx=10, pady=10)
    plt2 = hmgwin.frame()
    tabs.add(plt2, text="Plotting 2D")
    hmgwin.text(
        master=plt2,
        text="You can either plot a function of one variable, or a list of coordinates.\nBy default, if you close the plot and plot something else, that will get added to this plot,\nnot make a new graph. If you want to clear the plot, just type:",
    ).grid(column=0, row=0, padx=10, pady=10)
    hmgwin.text(master=plt2, text="clearplot", style="CodeStyle.TLabel").grid(
        column=0, row=1, padx=10, pady=10
    )
    hmgwin.text(
        master=plt2,
        text="First, let's look at how to plot a function. The general syntax is:",
    ).grid(column=0, row=2, padx=10, pady=10)
    hmgwin.text(
        master=plt2,
        text="{plot {function}, {variable}, {start}, {end}, {options}}",
        style="CodeStyle.TLabel",
    ).grid(column=0, row=3, padx=10, pady=10)
    hmgwin.text(
        master=plt2,
        text="In this too, you can put a named function (see Functions) inside.\nYou can also put another command which returns a function like an indefinite integral or derivative inside.\nHere is an example of a plot of x^2:",
    ).grid(column=0, row=4, padx=10, pady=10)
    hmgwin.text(
        master=plt2, text="{plot x^2, x, 0, 10}", style="CodeStyle.TLabel"
    ).grid(column=0, row=5, padx=10, pady=10)
    state.root.image(
        master=plt2, image=f"{rootdir}/Images/plotim.png", imsize=(3, 3)
    ).grid(column=2, row=1, padx=10, pady=10)
    hmgwin.text(
        master=plt2, text="Here is an example of a plot of x^3 using a named function:"
    ).grid(column=0, row=6, padx=10, pady=10)
    hmgwin.text(
        master=plt2,
        text="{func f, x, x^3}\n{plot f(x), x, -10, 10}",
        style="CodeStyle.TLabel",
    ).grid(column=0, row=7, padx=10, pady=10)
    state.root.image(
        master=plt2, image=f"{rootdir}/Images/plotim3.png", imsize=(3, 3)
    ).grid(column=2, row=2, padx=10, pady=10)
    hmgwin.text(
        master=plt2,
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
    opl = hmgwin.listbox(master=plt2, width=50)
    for op in ops:
        opl.insert("end", op)
    opl.grid(column=1, row=1, padx=10, pady=10)
    hmgwin.text(
        master=plt2,
        text="The xticks and yticks options take an input in the format of a list made with square brackets, and separated by commas.\nYou will have to use the option followed by an '=' and the value, separated by commas at the end of the plot command.\nHere is an example of a plot with a title:",
    ).grid(column=1, row=2, padx=10, pady=10)
    hmgwin.text(
        master=plt2,
        text="{plot x^2, x, 0, 10, title='Title'}",
        style="CodeStyle.TLabel",
    ).grid(column=1, row=3, padx=10, pady=10)
    hmgwin.text(
        master=plt2,
        text="The syntax of plotting a list of coordinates is also very easy.\nHere is the general syntax:",
    ).grid(column=1, row=4, padx=10, pady=10)
    hmgwin.text(
        master=plt2, text="{plotlist {xs}, {ys}, {options}}", style="CodeStyle.TLabel"
    ).grid(column=1, row=5, padx=10, pady=10)
    hmgwin.text(master=plt2, text="For example,").grid(
        column=1, row=6, padx=10, pady=10
    )
    hmgwin.text(
        master=plt2, text="{plotlist [1, 2, 3], [1, 2, 3]}", style="CodeStyle.TLabel"
    ).grid(column=1, row=7, padx=10, pady=10)
    state.root.image(
        master=plt2, image=f"{rootdir}/Images/plotim4.png", imsize=(3, 3)
    ).grid(column=2, row=3, padx=10, pady=10)
    state.root.image(
        master=plt2, image=f"{rootdir}/Images/plotim5.png", imsize=(3, 3)
    ).grid(column=2, row=3, padx=10, pady=10)
    hmgwin.text(master=plt2, text="Images:").grid(column=2, row=0, padx=10, pady=10)
    pltpie = hmgwin.frame()
    tabs.add(pltpie, text="Pie Charts")
    hmgwin.text(
        master=pltpie,
        text="Making Pie Charts with MathGod is very easy.\nYou do not have to make the values add up to 1 or 100.\nHere is an example of a simple pie chart of 40% and 60%:",
    ).grid(column=0, row=0, padx=10, pady=10)
    hmgwin.text(master=pltpie, text="{pie [40, 60]}", style="CodeStyle.TLabel").grid(
        column=0, row=1, padx=10, pady=10
    )
    hmgwin.text(
        master=pltpie,
        text="There are various options for a pie chart. The basic ones are:",
    ).grid(column=0, row=2, padx=10, pady=10)
    opspie = [
        "labels: Sets the labels of the sectors",
        "colors: Sets the colors of the sectors",
        "explode: Sets the distance each sector comes out by",
        "startangle: Sets the starting point of the first sector",
    ]
    oplpie = hmgwin.listbox(master=pltpie, width=50)
    for op in opspie:
        oplpie.insert("end", op)
    oplpie.grid(column=0, row=3, padx=10, pady=10)
    hmgwin.text(
        master=pltpie,
        text="""The labels, colors, and explode options get a list of the same size as the list of input values.
The startangle option is in degrees.
Here is an example of a pie chart of 3 sectors of the same size,
with labels 'a', 'b', 'c', the first one ('a') set to explode '0.1', and colors red, blue, and green:""",
    ).grid(column=0, row=4, padx=10, pady=10)
    hmgwin.text(
        master=pltpie,
        text="{pie [1, 1, 1], labels=['a', 'b', 'c'], colors=['red', 'blue', 'green'], explode=[0.1, 0, 0]}",
        style="CodeStyle.TLabel",
    ).grid(column=0, row=5, padx=10, pady=10)
    hmgwin.text(master=pltpie, text="Images:").grid(column=1, row=0, padx=10, pady=10)
    state.root.image(
        master=pltpie, image=f"{rootdir}/Images/plotim6.png", imsize=(3, 3)
    ).grid(column=1, row=1, padx=10, pady=10)
    state.root.image(
        master=pltpie, image=f"{rootdir}/Images/plotim7.png", imsize=(3, 3)
    ).grid(column=1, row=2, padx=10, pady=10)
    pltbar = hmgwin.frame()
    tabs.add(pltbar, text="Bar Charts")
    hmgwin.text(
        master=pltbar,
        text="Making Bar Charts with MathGod is very simple. This is the general syntax:",
    ).grid(column=0, row=0, padx=10, pady=10)
    hmgwin.text(
        master=pltbar, text="{bar {xs}, {ys}, {options}}", style="CodeStyle.TLabel"
    ).grid(column=0, row=1, padx=10, pady=10)
    hmgwin.text(master=pltbar, text="The basic options are:").grid(
        column=0, row=2, padx=10, pady=10
    )
    oplbar = hmgwin.listbox(master=pltbar, width=50)
    opbar = [
        "color: Sets the color of the bars",
        "tick_label: Sets the label of each bar",
        "width: Sets the width of the bars",
    ]
    for op in opbar:
        oplbar.insert("end", op)
    oplbar.grid(column=0, row=3, padx=10, pady=10)
    hmgwin.text(master=pltbar, text="Here is an example of a basic bar chart:").grid(
        column=0, row=4, padx=10, pady=10
    )
    hmgwin.text(
        master=pltbar, text="{bar [1, 2, 3], [1, 5, 3]}", style="CodeStyle.TLabel"
    ).grid(column=0, row=5, padx=10, pady=10)
    hmgwin.text(master=pltbar, text="Images:").grid(column=1, row=0, padx=10, pady=10)
    state.root.image(
        master=pltbar, image=f"{rootdir}/Images/plotim8.png", imsize=(3, 3)
    ).grid(column=1, row=1, padx=10, pady=10)
    hmgwin.text(
        master=pltbar,
        text="Here is an example of a bar chart labeled 'a', 'b', and 'c' with the color green with the width '0.1' of each bar:",
    ).grid(column=0, row=6, padx=10, pady=10)
    hmgwin.text(
        master=pltbar,
        text="{bar [1, 2, 3], [1, 5, 3], tick_label=['a', 'b', 'c'], color='green', width=0.1}",
        style="CodeStyle.TLabel",
    ).grid(column=0, row=7, padx=10, pady=10)
    state.root.image(
        master=pltbar, image=f"{rootdir}/Images/plotim9.png", imsize=(3, 3)
    ).grid(column=1, row=2, padx=10, pady=10)
    plt3 = hmgwin.frame()
    tabs.add(plt3, text="Plotting 3D")
    hmgwin.text(
        master=plt3,
        text="You can only 3D plot a function of two variables.\nThe general syntax is:",
    ).grid(column=0, row=0, padx=10, pady=10)
    hmgwin.text(
        master=plt3,
        text="{plot3  {func}, {var1}, {var2}, [{var1 start}, {var1 end}], [{var2 start}, {var2 end}], options}",
        style="CodeStyle.TLabel",
    ).grid(column=0, row=1, padx=10, pady=10)
    hmgwin.text(master=plt3, text="The options are").grid(
        column=0, row=2, padx=10, pady=10
    )
    oplpl3 = hmgwin.listbox(master=plt3, width=50)
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
    hmgwin.text(
        master=plt3,
        text="You have to use the options followed by an '=' and then the value.\nHere is an example of a plot of x^2+y^2:",
    ).grid(column=0, row=4, padx=10, pady=10)
    hmgwin.text(
        master=plt3,
        text="{plot3 x^2+y^2, x, y, [-10, 10], [-10, 10]}",
        style="CodeStyle.TLabel",
    ).grid(column=0, row=5, padx=10, pady=10)
    hmgwin.text(
        master=plt3,
        text="Here is an example of a plot of the same function but using a named function:",
    ).grid(column=0, row=6, padx=10, pady=10)
    hmgwin.text(
        master=plt3,
        text="{func f, x y, x^2+y^2}\n{plot3 f(x, y), x, y, [-10, 10], [-10, 10]}",
        style="CodeStyle.TLabel",
    ).grid(column=0, row=7, padx=10, pady=10)
    hmgwin.text(master=plt3, text="Images:").grid(column=1, row=0, padx=10, pady=10)
    state.root.image(
        master=plt3, image=f"{rootdir}/Images/plotim10.png", imsize=(3, 3)
    ).grid(column=1, row=1, padx=10, pady=10)
    sum = hmgwin.frame()
    tabs.add(sum, text="Summation and Products")
    hmgwin.text(
        master=sum,
        text="Summation with MathGod is very easy.\nYou can either put an named function inside, or an unnamed one.\nHere is the general syntax:",
    ).grid(column=0, row=0, padx=10, pady=10)
    hmgwin.text(
        master=sum, text="{sum {func}, {var}, {start}, {end}}", style="CodeStyle.TLabel"
    ).grid(column=0, row=1, padx=10, pady=10)
    hmgwin.text(master=sum, text="Here is an example of a sum of i from 1 to 10:").grid(
        column=0, row=2, padx=10, pady=10
    )
    hmgwin.text(master=sum, text="{sum i, i, 1, 10}", style="CodeStyle.TLabel").grid(
        column=0, row=3, padx=10, pady=10
    )
    hmgwin.text(
        master=sum,
        text="This will return '55'. You can also put in named functions.\nHere is an example:",
    ).grid(column=0, row=4, padx=10, pady=10)
    hmgwin.text(
        master=sum,
        text="{func f, x, x}\n{sum f(i), i, 1, 10}",
        style="CodeStyle.TLabel",
    ).grid(column=0, row=5, padx=10, pady=10)
    hmgwin.text(
        master=sum,
        text="This will also return the same output.\nYou can also put another variable inside the bounds.\nHere is an example:",
    ).grid(column=0, row=6, padx=10, pady=10)
    hmgwin.text(master=sum, text="{sum i, i, 1, n}", style="CodeStyle.TLabel").grid(
        column=0, row=7, padx=10, pady=10
    )
    hmgwin.text(
        master=sum,
        text="This will return 'n^2/2 + n/2'.\nFinding products is exactly the same, except just 'prod' instead of 'sum'.\nHere is an example:",
    ).grid(column=0, row=8, padx=10, pady=10)
    hmgwin.text(master=sum, text="{prod i, i, 1, 10}", style="CodeStyle.TLabel").grid(
        column=0, row=9, padx=10, pady=10
    )
    hmgwin.text(master=sum, text="This will return '3628800'.").grid(
        column=0, row=10, padx=10, pady=10
    )
    intp = hmgwin.frame()
    tabs.add(intp, text="Interpolation")
    hmgwin.text(
        master=intp,
        text="Interpolation returns a function that is the given value for all the given points. The general syntax is:",
    ).grid(column=0, row=0, padx=10, pady=10)
    hmgwin.text(
        master=intp,
        text="{interpolate [(x_1, y_1), (x_2, y_2), ...], {var}}",
        style="CodeStyle.TLabel",
    ).grid(column=0, row=1, padx=10, pady=10)
    hmgwin.text(master=intp, text="Here is an example:").grid(
        column=0, row=2, padx=10, pady=10
    )
    hmgwin.text(
        master=intp,
        text="{interpolate [(0, 10), (1, 5), (2, -3)], x}",
        style="CodeStyle.TLabel",
    ).grid(column=0, row=3, padx=10, pady=10)
    hmgwin.text(
        master=intp,
        text="This will return '-3x^2/2 - 7x/2 + 10'.\nIf you plot it, you can see that it actually passes through all the exact points:",
    ).grid(column=0, row=4, padx=10, pady=10)
    hmgwin.text(
        master=intp,
        text="{func f, x, {interpolate [(0, 10), (1, 5), (2, -3)], x}}\n{plot f(x), x, -5, 5, xticks=[0, 1, 2], yticks=[10, 5, -3], grid=True}",
        style="CodeStyle.TLabel",
    ).grid(column=0, row=5, padx=10, pady=10)
    hmgwin.text(master=intp, text="Images:").grid(column=1, row=0, padx=10, pady=10)
    state.root.image(
        master=intp, image=f"{rootdir}/Images/plotim11.png", imsize=(3, 3)
    ).grid(column=1, row=1, padx=10, pady=10)
    cnd = hmgwin.frame()
    tabs.add(cnd, text="Conditions")
    hmgwin.text(
        master=cnd,
        text="There are two ways to create a function with a condition.\nThe first is using 'Piecewise', and the second is just using 'if'.\nLet's first look at the first method:",
    ).grid(column=0, row=0, padx=10, pady=10)
    hmgwin.text(
        master=cnd,
        text="{func f, x, Piecewise((x-1, x<0), (x+1, x>=0))}",
        style="CodeStyle.TLabel",
    ).grid(column=0, row=1, padx=10, pady=10)
    hmgwin.text(
        master=cnd,
        text="This creates a function 'f', which is x-1 for x<0, and x+1 for x>=0.\nNow, the other way to create the same function is this:",
    ).grid(column=0, row=2, padx=10, pady=10)
    hmgwin.text(
        master=cnd, text="{func f, x, (x-1 if x<0 else x+1)}", style="CodeStyle.TLabel"
    ).grid(column=0, row=3, padx=10, pady=10)
    hmgwin.text(
        master=cnd,
        text="With this method, to make multiple 'elif' conditions, you can stack the 'if's up.",
    ).grid(column=0, row=4, padx=10, pady=10)
    tabs.pack(fill="both", expand=True)
    ot = hmgwin.frame()
    tabs.add(ot, text="Other")
    hmgwin.text(
        master=ot,
        text="""Additionally, you can use any function from sympy, or any basic function from python.
For example, you can use range, map, min, max, subs, sin, cos, etc...
The functions from sympy like sin, cos, log, etc... will work with both symbols, and numbers.
Multiline python things like 'while', 'for', 'if', etc... will not work.
For example, if you want to just output the integral back without calculating it, you can type:""",
    ).grid(column=0, row=0, padx=10, pady=10)
    hmgwin.text(master=ot, text="Integral(x^2, x)", style="CodeStyle.TLabel").grid(
        column=0, row=1, padx=10, pady=10
    )
    hmgwin.text(master=ot, text="OR").grid(column=0, row=2, padx=10, pady=10)
    hmgwin.text(
        master=ot, text="Integral(y^2, (y, 0, x))", style="CodeStyle.TLabel"
    ).grid(column=0, row=3, padx=10, pady=10)
    hmgwin.style(state.root.gettheme())
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
