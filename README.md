# About  
![Icon](images/Icon.png)  
PyNotes is an advanced cross-platform text editor and IDE made in Python.  
Links: [GitHub](https://github.com/rafugafu/pynotes), [Codeberg](codeberg.org/rafugafu/pynotes), [Sourceforge](https://sourceforge.net/projects/pynotespython/), [Launchpad PPA](https://launchpad.net/~rafugafu/+archive/ubuntu/pynotes)  
## Important Features  
* **Programming** - Syntax highlighting and running code with outputs and errors for Python, LaTeX, and HTML! Graphical buttons for formatting LaTeX!  
* **Alt-X Commands** - Powerful Emacs-like commands and options inside PyNotes!  
* **Plugins** - Powerful extensions that seamlessly integrate with PyNotes! Very easy to make and install! Currently made by me are: Letter Invaders Game (A fun typing game), Typing (A typing test that also gives feedback and suggestions), 3D Maze Game (A 3D Maze Game with a simple AI as an opponent), Simple Spellcheck (Spellcheck for the editor with the option to change or add dictionaries), ChessPy (A Chess Program where you can play 2 player or with any engine you provide)  
* **PyCode** - Programming language inside PyNotes to customize it even beyond plugins! You can fully make and change your own keyboard shortcuts, functions, Alt-X commands, startup code, etc!  
* **MathGod** - Notebook for symbolic math inside PyNotes!  
* **Email** - Send emails from within PyNotes! Also has a spellcheck and option to change or add new dictionaries for the spellcheck.  
* **HModes** - Modes like Emacs for different purposes! Changes syntax highlighting, running code, tabs, etc.  
* **Text to speech** - Make PyNotes speak your selection inside the editor!  
* **Speech to text** - Dictate to write text in the editor!  
* **Terminal** - Full Terminal or Powershell inside PyNotes!  
* **Python Shell / REPL** - Full Python shell / REPL inside PyNotes!  
* **Preferences** - Fully customize your syntax highlighting and options easily in the preferences!  
* **Search** - Incremental search for Find and Find & Replace - Find strings without fully typing them!  
* **Regexp Search** - Find and Find & Replace using regexp!  
* **Emacs-like keybindings in search** - Option to use Emacs-like keybindings for Find and Find & Replace!  
* **Backup** - Auto backup option to save your files!  
* **Quick Installation** - Fast installation with an installer script for Linux and a graphical installer for Windows!  
* **And much more!**  
## Screenshots  
![Typing Test](images/Typing_Test.png)  
![3D Maze Game](images/3D_Maze_Game.png)  
![Letter Invaders Game](images/Letter_Invaders_Game.png)  
![Startup](images/Start.png)  
![Preferences](images/Preferences.png)  
![Python Shell](images/Python_Shell.png)  
![PyCode](images/PyCode.png)  
![MathGod](images/MathGod.png)  
![Terminal](images/Terminal.png)  
![ChessPy](images/ChessPy.png)  
![Opening Images in PyNotes](images/Image_in_PyNotes.png)  
![Write Command Example](images/Write_Command_Example.png)  
# Installation  
For Windows, download Python from [here](https://www.python.org/downloads/windows/).  
Click [here](pynotes_debian_installer.sh) to download the Debian installer script, [here](pynotes_rpm_installer.sh) for the RPM installer script, and [here](pynotes_windows_installer.py) for the Windows Installer.  
For PyNotes version v1.8 and above, you might also have to manually download the Cairo C library. For Linux, install these packages: `python3-tk, python3-venv, zenity, libcairo2-dev, python3-dev, libffi-dev, pkg-config` (names may vary for your distribution). The `.deb` and `.rpm` packages also contain all the dependencies. For Windows, follow [this](https://www.gtk.org/docs/installations/windows).  
System: Linux or Windows with Python 3.10 or above.  
**Easytk needs ttkthemes to work. It is automatically installed with other packages from version 1.4.2. For older versions, install with:**  
`pip3 install ttkthemes`  
## Sourceforge  
Download from [Sourceforge](https://sourceforge.net/projects/pynotespython/).  
## Linux  
**Note:** In some distros or versions of Linux, tkinter or pip may not come installed. You will then have to manually install tkinter and pip. Example: `sudo apt install python3-tk` and `sudo apt install python3-pip` for Ubuntu. You can also run PyNotes inside a virtual environment.  
**Note:** In older versions of PyNotes, if you are using Ubuntu 23 or later, you may get an error like this when PyNotes tries to install the dependencies using pip:  
```
error: externally-managed-environment  
  
× This environment is externally managed  
╰─> To install Python packages system-wide, try apt install  
    python3-xyz, where xyz is the package you are trying to  
    install.  
      
    If you wish to install a non-Debian-packaged Python package,  
    create a virtual environment using python3 -m venv path/to/venv.  
    Then use path/to/venv/bin/python and path/to/venv/bin/pip. Make  
    sure you have python3-full installed.  
      
    If you wish to install a non-Debian packaged Python application,  
    it may be easiest to use pipx install xyz, which will manage a  
    virtual environment for you. Make sure you have pipx installed.  
      
    See /usr/share/doc/python3.12/README.venv for more information.  
  
note: If you believe this is a mistake, please contact your Python installation or OS distribution provider. You can override this, at the risk of breaking your Python installation or OS, by passing --break-system-packages.  
hint: See PEP 668 for the detailed specification.  
```
If this happens, you should upgrade your PyNotes version to 1.6 or later, which avoids this problem entirely. Otherwise (Not recommended), you can install the required modules manually with `--break-system-packages` (the modules PyNotes and it's add-ons need do not break system packages, this warning is because some other modules might break system packages), run PyNotes inside a Virtual Machine, or remove or move the file `/usr/lib/python3.*/EXTERNALLY-MANAGED` to stop this warning forever.  
### PPA for Ubuntu  
Add the PyNotes Launchpad PPA with the command: `sudo add-apt-repository ppa:rafugafu/pynotes`  
Then, run `sudo apt update`  
Now PyNotes should be installable through apt like any other package. Run `sudo apt install pynotes` to install it. You will also be able to upgrade PyNotes through `sudo apt upgrade`.  
### Debian Package  
There is a `.deb` package inside every `tar.gz` inside every version folder. You can install this manually with:  
`sudo dpkg -i PyNotes.deb`  
### Debian Package Installer Script  
Run the [pynotes_debian_installer.sh](pynotes_debian_installer.sh) script with root. You can give a specific version as an argument, or it will install the latest version.  
Command: `sudo pynotes_debian_installer.sh {version no. or blank}`  
### RPM Package  
There is a `.rpm` package inside every `tar.gz` inside every version folder. You can install this manually with:  
`sudo rpm -i --replacefiles *.rpm`  
### RPM Package Installer Script  
Run the [pynotes_rpm_installer.sh](pynotes_rpm_installer.sh) script with root. You can give a specific version as an argument, or it will install the latest version.  
Command: `sudo pynotes_rpm_installer.sh {version no. or blank}`  
## Windows  
1. Download Python from [here](https://www.python.org/downloads/windows/).  
2. Run the installer to install Python. Make sure to check add Python to PATH.  
3. Run the [pynotes_windows_installer.py](pynotes_windows_installer.py) script with Python, or using the command-line command `python pynotes_windows_installer.py`.  
4. It will then open a graphical installer, where you can select the version and install it. This script can also upgrade or downgrade your PyNotes version.  
# Plugins  
**Note:** If PyNotes is open when you install a new plugin, you will have to restart it for the plugin to work, as plugins are loaded only on startup.  
## Script  
This script works on both Linux and Windows. Run the `pynotes_plugin_installer.py` with Python and it will open a window where you can select the plugin(s) from PyNotes' GitHub to install. Once you are done, it will automatically download and install the plugins you have selected.  
## Manual  
Download the plugins from the `Plugins/` folder. You can also make your own or get them from somewhere else. Then extract them if they are compressed, and move the folder to `~/.local/share/PyNotes/add-ons/` on Linux, and `C:/Users/{Your Username}/.local/share/PyNotes/add-ons` on Windows.  
**Note:** Be careful in downloading plugins from other sources, as they will have full access to your system and be able to run any commands.  
# PyNotes Emacs Config  
**Note:** This config only works on PyNotes versions 1.8 and above, as it uses chord keybindings, which did not exist before PyNotes v1.8.  
## What it does  
This PyNotes Emacs config copies the following Emacs `M-x` commands and keybindings:  
### Emacs M-x Commands  
* `transpose-chars` - Transpose (swap) the two characters behind the cursor in the editor.  
* `query-replace` - Find & Replace.  
* `kill-ring-save` - Copy selected text.  
* `isearch-forward` - Find.  
* `kill-region` - Cut (kill) the selected text.  
* `yank` - Paste previously copied or cut text.  
* `move-beginning-of-line` - Move the cursor to the start of the current line.  
* `move-end-of-line` - Move the cursor to the end of the current line.  
* `next-line` - Move the cursor down one line.  
* `previous-line` - Move the cursor up one line.  
* `forward-char` - Move the cursor forward one character.  
* `backward-char` - Move the cursor backward one character.  
* `find-file` - Open a file.  
* `mark-whole-buffer` - Select all text in the buffer.  
* `save-buffers-kill-terminal` - Close PyNotes normally, after asking to save unsaved changes.  
* `save-buffer` - Save the current file.  
* `write-file` - Save As.  
* `undo` - Undo.  
* `python-mode` - Switch the HMode to Python.  
* `latex-mode` - Switch the HMode to LaTeX.  
* `html-mode` - Switch the HMode to HTML.  
* `text-mode` - Switch the HMode to Normal.  
* `kill-line` - Cut (kill) text from the cursor to the end of the line.  
* `kill-whole-line` - Cut (kill) the entire current line.  
### Emacs Keybindings  
* `Alt-semicolon` - Comment the current selection.  
* `Alt-percent` - Find & Replace.  
* `Alt-w` - Copy selected text.  
* `Control-slash` - Undo.  
* `Control-underscore` - Undo.  
* `Control-t` - Transpose (swap) the two characters behind the cursor in the editor.  
* `Control-s` - Find.  
* `Control-w` - Cut (kill) selected text.  
* `Control-y` - Paste previously copied or cut text.  
* `Control-a` - Move cursor to start of line.  
* `Control-e` - Move cursor to end of line.  
* `Control-n` - Move cursor to next line.  
* `Control-p` - Move cursor to previous line.  
* `Control-f` - Move cursor forward one character.  
* `Control-b` - Move cursor backward one character.  
* `Control-k` - Kill (cut) from cursor to end of line.  
* `Control-Alt-backslash` - Indent selected text.  
* `Alt-v` - Scroll/page backward.  
* `Control-v` - Scroll/page forward.  
* `Alt-less` - Move cursor to start of buffer.  
* `Alt-greater` - Move cursor to end of buffer.  
* `Control-Shift-BackSpace` - Kill (cut) the entire current line.  
* `Control-x & h` - Select the entire buffer.  
* `Control-x & Control-c` - Close the editor/application.  
* `Control-c & less` - Unindent selected text.  
* `Control-c & greater` - Indent selected text.  
* `Control-x & Control-s` - Save file.  
* `Control-x & Control-w` - Save As.  
* `Control-x & u` - Undo last change.  
## To Use  
For Emacs users, there is a readymade PyCode config in [pynotesemacsconfig.txt](pynotesemacsconfig.txt) that copies a lot of standard Emacs keybindings and `M-x` commands. To use it, open PyCode with `Alt-X pc`, and paste the contents of the file in the window that appears. Then, click the 'Done' button on the bottom. This automatically saves and applies the config to the instance of PyNotes you opened it in. For other already open PyNotes windows, just open PyCode and click 'Done' in them to apply the config. Alternatively, directly copy the file to `~/pynotes` on Linux, and `C:\Users\{yourusername}\.pynotes on Windows. This will only apply to PyNotes opened after this, or if you open PyCode and close it in already open PyNotes windows.  
**Note:** Make sure to close PyCode with the 'Done' button only, and not close the window in any other way, as this will cancel the changes to your PyCode config.  