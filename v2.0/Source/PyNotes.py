import sys
import urllib.request
import os
import io
import zipfile
import platform
import getpass
exit = sys.exit
v = '2.0'
if platform.system() == 'Linux':
	rootdir = '/usr/share/PyNotes'
	homedir = f'/home/{getpass.getuser()}'
	monospace = 'monospace'
else:
	rootdir = 'C:/Program Files/PyNotes'
	homedir = f'C:/Users/{getpass.getuser()}'
	monospace = 'Courier'
def argparse(options, args):
	exitwith = lambda message: [print(message), exit(1)]
	curarg = None
	files_to_open = []
	for arg in args:
		if not curarg and not arg.startswith('--'):
			files_to_open.append(arg)
			continue
		if curarg and options[curarg] in (False, None) and not arg.startswith('--'):
			files_to_open.append(arg)
			continue
		if arg.startswith('--'):
			if curarg and options[curarg] not in (False, None):
				exitwith(f'unexpected "{arg}" after option "--{curarg}"')
			arg = arg[2:]
		if curarg and options[curarg] in (False, None):
			curarg = None
		if not curarg:
			if '=' in arg:
				opn, opv = arg.split('=', 1)
				if opn not in options:
					exitwith(f'error: unknown option "--{opn}"')
				if options[opn] == True:
					options[opn] = opv
				elif options[opn] in (False, None):
					exitwith(f'error: option "--{opn}" does not take any argument')
				else:
					exitwith(f'error: repeated argument "--{arg}"')
			else:
				if arg not in options:
					exitwith(f'error: unknown option "--{arg}"')
				if options[arg] == True:
					curarg = arg
				elif options[arg] == False:
					curarg = arg
					options[arg] = None
				else:
					exitwith(f'error: repeated argument "--{arg}"')
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
options, files_to_open = argparse({'version': False, 'changes': False, 'plugin-list-github': False, 'plugin-list-installed': False, 'no-load-pycode': False, 'no-load-plugins': False, 'pycode-exec': True, 'command-exec': True, 'help': False, 'plugin-install': True, 'plugin-remove': True, 'plugin-describe': True}, sys.argv[1:])
changelist = ['Added Emacs-like buffers to PyNotes!', 'Added event hooks to PyCode!', 'Made the Alt-X command prompt better and added smart Emacs-like autocomplete to it!', 'Added an option to use Emacs-like file pickers with autocomplete in the Alt-X command box (minibuffer)!', 'Added loops and conditions to PyCode!', 'PyNotes now accepts proper command-line arguments instead of just --version! (pynotes --help for details)\nPlugins are now manageable directly through PyNotes!', 'Added chaining of Alt-X commands using \';\'!', 'Added Emacs-like selection points (mark sets) with Ctrl-Space!', 'Made nesting of Alt-X commands much better by handling brackets.', 'Added some Python code navigation Alt-X and PyCode commands.', 'Made PyNotes detect external changes and ask instead of silently overwriting the file on the next save.', 'Fixed some bugs in the PyNotes terminal and added some more ANSI codes support.', 'Made MathGod cells scrollable.', 'Fixed a bug where undefined commands in pycode:{} blocks inside Python functions in PyCode would not show a proper error message.', 'Added some more Alt-X commands.', 'Added some more PyCode commands.', 'The Alt-X command terminal and the PyCode command openterm now accept a command to run instead of the default /bin/bash or powershell.exe.', 'Removed the Zen of Python on startup.', 'Fixed some Python syntax highlighting bugs.', 'Made the Alt-X and PyCode commands go to line accept input and use the new better prompt in Alt-X command box.', 'Fixed a bug where an error on saving file would not show a proper error message.']
changestr = ''
for i in range(len(changelist) - 1):
	changestr += f'{i + 1}. {changelist[i]}\n\n'
changestr += f'{len(changelist)}. {changelist[-1]}'
if sum([bool(options[op]) for op in ('version', 'changes', 'help', 'plugin-list-github', 'plugin-list-installed', 'plugin-install', 'plugin-describe')]) > 1:
	print(options)
	print(f'error: cannot combine --version, --changes, --help, --plugin-list-github, --plugin-list-installed, --plugin-install, --plugin-describe arguments')
	exit(1)
if options['version']:
	print(f'This is PyNotes v{v}.')
	exit()
if options['changes']:
	print(f'Changes in v{v}:\n' + changestr.replace('\n\n', '\n'))
	exit()
os.makedirs(f'{homedir}/.local/share/PyNotes/add-ons', exist_ok = True)
if options['plugin-list-github']:
	try:
		plgns = urllib.request.urlopen('https://raw.githubusercontent.com/rafugafu/PyNotes/main/Plugins/list').read().decode().split('\n')
		onelinedescplgns = urllib.request.urlopen('https://raw.githubusercontent.com/rafugafu/PyNotes/main/Plugins/onelinedescriptions').read().decode().split('\n')
	except Exception as error:
		error = str(error)
		print(f'error in downloading plugin list: {error}')
		exit(1)
	installed = os.listdir(f'{homedir}/.local/share/PyNotes/add-ons')
	printstr = 'Plugins currently on PyNotes GitHub:\n'
	for i in range(len(plgns) - 1):
		if plgns[i] in installed:
			printstr += '(Installed) '
		else:
			printstr += '(Not Installed) '
		printstr += plgns[i] + ' - ' + onelinedescplgns[i] + '.\n'
	if plgns[-1] in installed:
		printstr += '(Installed) '
	else:
		printstr += '(Not Installed) '
	printstr += plgns[-1] + ' - ' + onelinedescplgns[-1] + '.'
	print(printstr)
	exit()
if options['plugin-list-installed']:
	installed = os.listdir(f'{homedir}/.local/share/PyNotes/add-ons')
	if not installed:
		print('No plugins are installed.')
		exit()
	printstr = ''
	for i in range(len(installed) - 1):
		printstr += installed[i] + ' - '
		if 'onelinedescription' in os.listdir(f'{homedir}/.local/share/PyNotes/add-ons/{installed[i]}'):
			printstr += open(f'{homedir}/.local/share/PyNotes/add-ons/{installed[i]}/onelinedescription', 'r').read() + '.\n'
		else:
			printstr += '[description not provided]\n'
	printstr += installed[-1] + ' - '
	if 'onelinedescription' in os.listdir(f'{homedir}/.local/share/PyNotes/add-ons/{installed[-1]}'):
		printstr += open(f'{homedir}/.local/share/PyNotes/add-ons/{installed[-1]}/onelinedescription', 'r').read() + '.'
	else:
		printstr += '[description not provided]'
	print(printstr)
	exit()
if options['plugin-describe']:
	installed = os.listdir(f'{homedir}/.local/share/PyNotes/add-ons')
	printstr = f'Description of plugin \'{options["plugin-describe"]}\' '
	if options['plugin-describe'] in installed:
		printstr += '(installed):\n'
		if not 'fulldescription' in os.listdir(f'{homedir}/.local/share/PyNotes/add-ons/{options["plugin-describe"]}'):
			printstr += '[Not provided]'
		else:
			printstr += open(f'{homedir}/.local/share/PyNotes/add-ons/{options["plugin-describe"]}/fulldescription', 'r').read()
	else:
		printstr += '(not installed):\n'
		try:
			plgns = urllib.request.urlopen('https://raw.githubusercontent.com/rafugafu/PyNotes/main/Plugins/list').read().decode().split('\n')
			fulldescplgns = urllib.request.urlopen('https://raw.githubusercontent.com/rafugafu/PyNotes/main/Plugins/fulldescriptions').read().decode().split('\n==========\n')
		except Exception as error:
			error = str(error)
			print(f'error in downloading plugin list: {error}')
			exit(1)
		if not options['plugin-describe'] in plgns:
			print(f'error: plugin \'{options["plugin-describe"]}\' is not installed and does not exist on the PyNotes GitHub.')
			exit(1)
		printstr += fulldescplgns[plgns.index(options['plugin-describe'])]
	print(printstr)
	exit()
if options['plugin-install']:
	try:
		plgns = urllib.request.urlopen('https://raw.githubusercontent.com/rafugafu/PyNotes/main/Plugins/list').read().decode().split('\n')
	except Exception as error:
		error = str(error)
		print(f'error in downloading plugin list: {error}')
		exit(1)
	if not options['plugin-install'] in plgns:
		print(f'error: cannot find plugin \'{options["plugin-install"]}\'')
		exit(1)
	print('downloading plugin...', end = '')
	try:
		plgn = urllib.request.urlopen(f'https://raw.githubusercontent.com/rafugafu/PyNotes/main/Plugins/{options["plugin-install"]}.zip').read()
	except Exception as error:
		error = str(error)
		print(f'\nerror in downloading plugin: {error}')
		exit(1)
	print(' done')
	print('extracting plugin...', end = '')
	try:
		archive = io.BytesIO(plgn)
		zipfile.ZipFile(archive, 'r').extractall(path = f'{homedir}/.local/share/PyNotes/add-ons/')
	except Exception as error:
		error = str(error)
		print(f'\nerror in extracting plugin: {error}')
		exit(1)
	print(' done\n')
	print(f'Installed plugin \'{options["plugin-install"]}\'.')
	exit()
if options['plugin-remove']:
	installed = os.listdir(f'{homedir}/.local/share/PyNotes/add-ons')
	if not options['plugin-remove'] in installed:
		print(f'error: plugin \'{options["plugin-remove"]}\' is not installed')
		exit(1)
	shutil.rmtree(f'{homedir}/.local/share/PyNotes/add-ons/{options["plugin-remove"]}')
	print(f'Removed plugin \'{options["plugin-remove"]}\'.')
	exit()
if options['help']:
	print('''\
This is help only for the command line arguments given to PyNotes. For help on PyNotes functions and features, open Help from within PyNotes itself.
--version: Print the current PyNotes version number.
--changes: Print the current PyNotes version's changelog.
--plugin-list-github: List the plugins on the PyNotes GitHub with a one line description for each.
--plugin-list-installed: List the currently installed plugins with a one line description for each if provided.
--plugin-install "name": Installs the given plugin from the PyNotes GitHub if present.
--plugin-remove "name": Uninstalls the given plugin if installed.
--plugin-describe "name": Give a full description of the given plugin if installed and provided, fallback to checking in the PyNotes GitHub if not.
--no-load-pycode: Start PyNotes without loading your PyCode configuration until you open and close PyCode yourself.
--no-load-plugins: Start PyNotes without loading any plugins.
--pycode-exec "string": Execute the given string as PyCode after loading your normal configuration.
--command-exec "string": Execute the given string as Alt-X commands.\
''')
	exit()
import subprocess
from tkinter import messagebox as mb
if platform.system() == 'Linux':
	if rootdir not in sys.path:
		sys.path.insert(0, rootdir)
def info(title, inf):
	infowin = easytk.win()
	infowin.title(title)
	infowin.text(text = inf).pack(side = 'top', anchor = 'n', padx = 10, pady = 10)
	infowin.button(text = 'Close', command = infowin.destroy).pack(side = 'right', anchor = 'se', padx = 10, pady = 10)
	infowin.show()
def ask(title, askinput):
	def yes():
		global returnval
		askwin.destroy()
		returnval = True
	def no():
		global returnval
		askwin.destroy()
		returnval = False
	askwin = easytk.win()
	askwin.title(title)
	askwin.text(text = askinput).pack(side = 'top', anchor = 'n', padx = 10, pady = 10)
	askwin.button(text = 'Yes', command = yes).pack(side = 'left', anchor = 'nw', padx = 10, pady = 10)
	askwin.button(text = 'No', command = no).pack(side = 'right', anchor = 'ne', padx = 10, pady = 10)
	askwin.protocol('WM_DELETE_WINDOW', lambda: None)
	askwin.show()
	return returnval
def switchvenv():
	if platform.system() != 'Linux':
		return
	venvdir = f'{homedir}/.local/share/PyNotes/venv'
	if not os.path.exists(f'{venvdir}/bin/python'):
		mb.showinfo('Making Python virtual environment', 'Making the Python virtual environment for PyNotes. This only happens on the first startup of a new\ninstallation of PyNotes.')
		subprocess.run([sys.executable, '-m', 'venv', venvdir], check = True)
	if sys.prefix != venvdir:
		os.execv(f'{venvdir}/bin/python', [f'{venvdir}/bin/python'] + sys.argv)
if platform.system() == 'Linux':
	os.environ['PATH'] = f'{homedir}/.local/share/PyNotes/venv/bin:' + os.environ['PATH']
switchvenv()
try:
	import easytk
except Exception:
	if mb.askyesno('Info', 'The module \'ttkbootstrap\' is not installed. PyNotes will not be able to run without this module. Should PyNotes install it locally?'):
		pipdir = os.path.dirname(sys.executable)
		subprocess.run([os.path.join(pipdir, 'pip'), 'install', 'ttkbootstrap'])
	try:
		import easytk
	except Exception:
		mb.showerror('Error', 'ttkbootstrap was not installed successfully. Quitting PyNotes.')
		exit(1)
if platform.system() != 'Linux':
	fd = easytk.fd
from encrypter import encryptdecrypt
import io
import time
import shutil
import copy
import codecs
import base64
import smtplib
import webbrowser
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import keyword
import wave
import re
import threading
import queue
import ast
import warnings
_PYTHON_BUILTIN_MEMBERS = {}
for _bt in (str, int, float, list, dict, tuple, set, frozenset, bool, bytes, bytearray):
	_ms = {}
	for _nm in dir(_bt):
		if not _nm.startswith('_'):
			_ms[_nm] = 'func' if callable(getattr(_bt, _nm, None)) else 'var'
	_PYTHON_BUILTIN_MEMBERS[_bt.__name__] = _ms
del _bt, _ms, _nm
def _python_build_builtin_callable_params():
	import builtins
	import inspect
	out = {}
	for name in dir(builtins):
		obj = getattr(builtins, name, None)
		if not callable(obj):
			continue
		try:
			sig = inspect.signature(obj)
		except (ValueError, TypeError):
			continue
		kw = {pn for pn, pp in sig.parameters.items() if pp.kind in (pp.POSITIONAL_OR_KEYWORD, pp.KEYWORD_ONLY)}
		if kw:
			out[name] = kw
	return out
try:
	_PYTHON_BUILTIN_CALLABLE_PARAMS = _python_build_builtin_callable_params()
except Exception:
	_PYTHON_BUILTIN_CALLABLE_PARAMS = {}
del _python_build_builtin_callable_params
for _bn, _bkw in {'min': {'key', 'default'}, 'max': {'key', 'default'}, 'int': {'base'}, 'str': {'encoding', 'errors'}, 'bytes': {'encoding', 'errors'}, 'bytearray': {'encoding', 'errors'}}.items():
	_PYTHON_BUILTIN_CALLABLE_PARAMS.setdefault(_bn, _bkw)
del _bn, _bkw
import builtins as _bmod
_PYTHON_BUILTIN_CALLABLE_NAMES = {n for n in dir(_bmod) if callable(getattr(_bmod, n, None))}
_PYTHON_BUILTIN_NAMES = set(dir(_bmod))
del _bmod
_PYTHON_BUILTIN_METHOD_RETURNS = {'str': {'capitalize': 'str', 'casefold': 'str', 'center': 'str', 'expandtabs': 'str', 'format': 'str', 'format_map': 'str', 'join': 'str', 'ljust': 'str', 'lower': 'str', 'lstrip': 'str', 'removeprefix': 'str', 'removesuffix': 'str', 'replace': 'str', 'rjust': 'str', 'rstrip': 'str', 'strip': 'str', 'swapcase': 'str', 'title': 'str', 'translate': 'str', 'upper': 'str', 'zfill': 'str', 'split': 'list', 'rsplit': 'list', 'splitlines': 'list', 'partition': 'tuple', 'rpartition': 'tuple', 'encode': 'bytes', 'count': 'int', 'find': 'int', 'index': 'int', 'rfind': 'int', 'rindex': 'int', 'maketrans': 'dict', 'isalnum': 'bool', 'isalpha': 'bool', 'isascii': 'bool', 'isdecimal': 'bool', 'isdigit': 'bool', 'isidentifier': 'bool', 'islower': 'bool', 'isnumeric': 'bool', 'isprintable': 'bool', 'isspace': 'bool', 'istitle': 'bool', 'isupper': 'bool', 'startswith': 'bool', 'endswith': 'bool'}, 'bytes': {'capitalize': 'bytes', 'center': 'bytes', 'expandtabs': 'bytes', 'hex': 'str', 'join': 'bytes', 'ljust': 'bytes', 'lower': 'bytes', 'lstrip': 'bytes', 'removeprefix': 'bytes', 'removesuffix': 'bytes', 'replace': 'bytes', 'rjust': 'bytes', 'rstrip': 'bytes', 'strip': 'bytes', 'swapcase': 'bytes', 'title': 'bytes', 'translate': 'bytes', 'upper': 'bytes', 'zfill': 'bytes', 'decode': 'str', 'split': 'list', 'rsplit': 'list', 'splitlines': 'list', 'partition': 'tuple', 'rpartition': 'tuple', 'count': 'int', 'find': 'int', 'index': 'int', 'rfind': 'int', 'rindex': 'int', 'maketrans': 'dict', 'isalnum': 'bool', 'isalpha': 'bool', 'isascii': 'bool', 'isdigit': 'bool', 'islower': 'bool', 'isspace': 'bool', 'istitle': 'bool', 'isupper': 'bool', 'startswith': 'bool', 'endswith': 'bool'}, 'bytearray': {'capitalize': 'bytearray', 'center': 'bytearray', 'expandtabs': 'bytearray', 'hex': 'str', 'join': 'bytearray', 'ljust': 'bytearray', 'lower': 'bytearray', 'lstrip': 'bytearray', 'removeprefix': 'bytearray', 'removesuffix': 'bytearray', 'replace': 'bytearray', 'rjust': 'bytearray', 'rstrip': 'bytearray', 'strip': 'bytearray', 'swapcase': 'bytearray', 'title': 'bytearray', 'translate': 'bytearray', 'upper': 'bytearray', 'zfill': 'bytearray', 'decode': 'str', 'split': 'list', 'rsplit': 'list', 'splitlines': 'list', 'partition': 'tuple', 'rpartition': 'tuple', 'count': 'int', 'find': 'int', 'index': 'int', 'rfind': 'int', 'rindex': 'int', 'maketrans': 'dict', 'isalnum': 'bool', 'isalpha': 'bool', 'isascii': 'bool', 'isdigit': 'bool', 'islower': 'bool', 'isspace': 'bool', 'istitle': 'bool', 'isupper': 'bool', 'startswith': 'bool', 'endswith': 'bool'}, 'list': {'copy': 'list', 'count': 'int', 'index': 'int'}, 'dict': {'copy': 'dict', 'keys': 'list', 'values': 'list', 'items': 'list', 'fromkeys': 'dict'}, 'set': {'copy': 'set', 'union': 'set', 'intersection': 'set', 'difference': 'set', 'symmetric_difference': 'set', 'isdisjoint': 'bool', 'issubset': 'bool', 'issuperset': 'bool'}, 'frozenset': {'copy': 'frozenset', 'union': 'frozenset', 'intersection': 'frozenset', 'difference': 'frozenset', 'symmetric_difference': 'frozenset', 'isdisjoint': 'bool', 'issubset': 'bool', 'issuperset': 'bool'}, 'int': {'bit_length': 'int', 'bit_count': 'int', 'conjugate': 'int', 'as_integer_ratio': 'tuple', 'to_bytes': 'bytes'}, 'float': {'conjugate': 'float', 'as_integer_ratio': 'tuple', 'hex': 'str', 'is_integer': 'bool'}}
def faketerm(command):
	termwin = easytk.win()
	termwin.title('Terminal')
	term = termwin.textbox(font = (monospace, 12))
	term.insert('end', f'{getpass.getuser()}@PyNotes:~$ {command}\n')
	term.pack(fill = 'both')
	termwin.update()
	termwin.sizablefalse()
	try:
		process = subprocess.Popen(command, shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT, text = True, bufsize = 1)
		for line in process.stdout:
			term.insert('end', line)
			term.see('end')
			termwin.update()
		process.wait()
	except Exception as e:
		termwin.error('Error', f'An error occured while installing the module {command.split("pip install ")[1]}:\n{e}')
	time.sleep(2)
	termwin.destroy()
try:
	import tika
	from tika import parser
except Exception:
	ans = ask('Error!', 'The module \'tika\' is not installed. Should PyNotes install it locally?')
	if not ans:
		exit()
	else:
		faketerm('pip3 install tika')
try:
	import pdfplumber
except Exception:
	ans = ask('Error!', 'The module \'pdfplumber\' is not installed. Should PyNotes install it locally?')
	if not ans:
		exit()
	else:
		faketerm('pip3 install pdfplumber')
try:
	import pyttsx3 as stt
except Exception:
	ans = ask('Error!', 'The module \'pyttsx3\' is not installed. Should PyNotes install it locally?')
	if not ans:
		exit()
	else:
		faketerm('pip3 install pyttsx3')
try:
	import matplotlib.pyplot as plt
except Exception:
	ans = ask('Error!', 'The module \'matplotlib\' is not installed. Should PyNotes install it locally?')
	if not ans:
		exit()
	else:
		faketerm('pip3 install matplotlib')
try:
	import sympy
except Exception:
	ans = ask('Error!', 'The module \'sympy\' is not installed. Should PyNotes install it locally?')
	if not ans:
		exit()
	else:
		faketerm('pip3 install sympy')
try:
	import sounddevice as sd
except Exception:
	ans = ask('Error!', 'The module \'sounddevice\' is not installed. Should PyNotes install it locally?')
	if not ans:
		exit()
	else:
		faketerm('pip3 install sounddevice')
try:
	import speech_recognition as sr
except Exception:
	ans = ask('Error!', 'The module \'speech_recognition\' is not installed. Should PyNotes install it locally?')
	if not ans:
		exit()
	else:
		faketerm('pip3 install SpeechRecognition')
try:
	import numpy as np
except Exception:
	ans = ask('Error!', 'The module \'numpy\' is not installed. Should PyNotes install it locally?')
	if not ans:
		exit()
	else:
		faketerm(7)
try:
	from tklinenums import TkLineNumbers
except Exception:
	ans = ask('Error!', 'The module \'tklinenums\' is not installed. Should PyNotes install it locally?')
	if not ans:
		exit()
	else:
		faketerm('pip3 install tklinenums')
try:
	import ziamath
except Exception:
	ans = ask('Error!', 'The module \'ziamath\' is not installed. Should PyNotes install it locally?')
	if not ans:
		exit()
	else:
		faketerm('pip3 install ziamath')
try:
	import cairosvg
except Exception:
	ans = ask('Error!', 'The module \'cairosvg\' is not installed. Should PyNotes install it locally?')
	if not ans:
		exit()
	else:
		faketerm('pip3 install cairosvg')
try:
	from PIL import Image
except Exception:
	ans = ask('Error!', 'The module \'Pillow\' is not installed. Should PyNotes install it locally?')
	if not ans:
		exit()
	else:
		faketerm('pip3 install Pillow')
try:
	from watchdog.observers import Observer
	from watchdog.events import FileSystemEventHandler
except Exception:
	ans = ask('Error!', 'The module \'watchdog\' is not installed. Should PyNotes install it locally?')
	if not ans:
		exit()
	else:
		faketerm('pip3 install watchdog')
if platform.system() != 'Linux':
	try:
		from winpty import PtyProcess
	except Exception:
		ans = ask('Error!', 'The module \'pywinpty\' is not installed. Should PyNotes install it locally?')
		if not ans:
			exit()
		else:
			faketerm('pip3 install pywinpty')
new = False
try:
	import tika
	from tika import parser
	import pdfplumber
	import pyttsx3 as stt
	import matplotlib.pyplot as plt
	import sympy
	import sounddevice as sd
	import speech_recognition as sr
	import numpy as np
	from tklinenums import TkLineNumbers
	import ziamath
	import cairosvg
	from PIL import Image
	from watchdog.observers import Observer
	from watchdog.events import FileSystemEventHandler
	if platform.system() != 'Linux':
		from winpty import PtyProcess
except Exception:
	info('Error!', 'The modules were not installed properly. Quitting PyNotes.')
	exit()
defaultpythonexec = '/usr/bin/python3' if platform.system() == 'Linux' else 'python'
defaultdefs = f"{v}\nFalse\n{monospace}\npulse\n{rootdir}/english.txt\nFalse\nFalse\nFalse\n{defaultpythonexec}\n'pynotes:found': \"foreground = '#FFFFFF', background = '#16A34A'\", 'pynotes:foundhighlight': \"foreground = '#FFFFFF', background = '#1F2937'\", 'pynotes:marked': \"background = 'yellow'\", 'python:keywords': \"foreground = '#7C3AED', font = (type_.cget('font')[:-3].strip('{{}}'), 12, 'bold')\", 'python:inbuilt': \"foreground = '#D97706'\", 'python:comments': \"foreground = '#6B7280', font = (type_.cget('font')[:-3].strip('{{}}'), 12, 'italic')\", 'python:strings': \"foreground = '#15803D'\", 'python:variable_names': \"foreground = '#DC2626'\", 'python:function_names': \"foreground = '#2563EB'\", 'python:class_names': \"foreground = '#0891B2'\", 'python:class_instances': \"foreground = '#155E75'\", 'python:function_arguments': \"foreground = '#0F766E'\", 'python:operators': \"foreground = 'white', background = 'light grey'\", 'python:module_names': \"foreground = '#0369A1'\", 'latex:inlinemath': \"foreground = '#15803D'\", 'latex:environment': \"background = '#DCFCE7'\", 'latex:comments': \"foreground = '#6B7280', font = (type_.cget('font')[:-3].strip('{{}}'), 12, 'italic')\", 'latex:commands': \"foreground = '#C026D3'\", 'latex:arguments': \"foreground = '#2563EB'\", 'latex:operators': \"foreground = 'white', background = 'light grey'\", 'latex:square_brackets': \"foreground = '#92400E'\", 'html:attributes': \"foreground = '#DC2626'\", 'html:tags': \"foreground = '#047857'\", 'html:comments': \"foreground = '#6B7280', font = (type_.cget('font')[:-3].strip('{{}}'), 12, 'italic')\", 'html:quotes': \"foreground = '#2563EB'\", 'markdown:headers1': \"foreground = '#111827', font = (type_.cget('font')[:-3].strip('{{}}'), 29, 'bold')\", 'markdown:headers2': \"foreground = '#1F2937', font = (type_.cget('font')[:-3].strip('{{}}'), 26, 'bold')\", 'markdown:headers3': \"foreground = '#374151', font = (type_.cget('font')[:-3].strip('{{}}'), 23, 'bold')\", 'markdown:headers4': \"foreground = '#4B5563', font = (type_.cget('font')[:-3].strip('{{}}'), 20, 'bold')\", 'markdown:headers5': \"foreground = '#6B7280', font = (type_.cget('font')[:-3].strip('{{}}'), 17, 'bold')\", 'markdown:headers6': \"foreground = '#9CA3AF', font = (type_.cget('font')[:-3].strip('{{}}'), 14, 'bold')\", 'markdown:bold': \"font = (type_.cget('font')[:-3].strip('{{}}'), 12, 'bold')\", 'markdown:italic': \"font = (type_.cget('font')[:-3].strip('{{}}'), 12, 'italic')\", 'markdown:bold_italic': \"font = (type_.cget('font')[:-3].strip('{{}}'), 12, 'bold italic')\", 'markdown:strike': 'overstrike = True', 'markdown:inlinecode': \"foreground = '#BE123C', background = '#F3F4F6'\", 'markdown:links': \"foreground = '#2563EB', underline = True, underlinefg = '#2563EB'\", 'markdown:blockquotes': \"foreground = '#374151', background = '#F3F4F6'\", 'markdown:codeblocks': \"background = '#F3F4F6'\""
try:
	file = open(f'{homedir}/.local/share/PyNotes/defs', 'r', encoding = 'utf-8')
except Exception:
	file = open(f'{homedir}/.local/share/PyNotes/defs', 'w+', encoding = 'utf-8')
	file.write(defaultdefs)
	file.close()
	file = open(f'{homedir}/.local/share/PyNotes/defs', 'r', encoding = 'utf-8')
	info('', 'Welcome to PyNotes!')
	new = True
if not options['no-load-plugins']:
	plgns = os.listdir(f'{homedir}/.local/share/PyNotes/add-ons')
else:
	plgns = []
editor_init_code = []
editor_init_functions = []
plgns = [os.path.join(f'{homedir}/.local/share/PyNotes/add-ons', plgn) for plgn in plgns if os.path.isdir(os.path.join(f'{homedir}/.local/share/PyNotes/add-ons', plgn))]
plgncmds = dict()
init = []
first = []
last = []
plgnsprf = []
plgnhmodes = dict()
plgnpccmds = dict()
plgnscmdhelp = ''
plgnspccmdhelp = ''
for plgn in plgns:
	inf = os.path.join(plgn, 'init')
	ff = os.path.join(plgn, 'first')
	lf = os.path.join(plgn, 'last')
	pchf = os.path.join(plgn, 'helpcommands')
	plgncmdf = os.path.join(plgn, 'commands')
	plgnhmodesf = os.path.join(plgn, 'hmodes')
	plgnpccmdf = os.path.join(plgn, 'pycodecommands')
	plgnpccmdhf = os.path.join(plgn, 'helppycodecommands')
	plgnprff = os.path.join(plgn, 'preferences')
	try:
		init.append((plgn, open(inf, 'r', encoding = 'utf-8').read()))
	except Exception:
		pass
	try:
		first.append((plgn, open(ff, 'r', encoding = 'utf-8').read()))
	except Exception:
		pass
	try:
		last.append((plgn, open(lf, 'r', encoding = 'utf-8').read()))
	except Exception:
		pass
	try:
		plgnsprf.append((plgn, open(plgnprff, 'r', encoding = 'utf-8').read()))
	except Exception:
		pass
	try:
		pchfr = open(pchf, 'r', encoding = 'utf-8').read()
	except Exception:
		pass
	else:
		if pchfr.strip():
			plgnscmdhelp += '\n\n' + pchfr.strip()
	try:
		plgnhmoder = open(plgnhmodesf, 'r', encoding = 'utf-8').read().split('\n')
	except Exception:
		pass
	else:
		try:
			for p in plgnhmoder:
				ps = p[1:].split('"', 1)
				plgnhmodes[ps[0]] = (plgn, ps[1].replace('\\n', '\n'))
		except Exception as error:
			error = str(error)
			info('Error!', f'There was an error in loading the HModes of the plugin "{os.path.basename(os.path.normpath(plgn))}":\n{error}')
			exit()
	try:
		plgnpcr = open(plgnpccmdf, 'r', encoding = 'utf-8').read().split('\n')
	except Exception:
		pass
	else:
		try:
			for p in plgnpcr:
				ps = p[1:].split('"', 1)
				plgnpccmds[ps[0]] = (plgn, ps[1])
		except Exception as error:
			error = str(error)
			info('Error!', f'There was an error in loading the PyCode commands of the plugin "{os.path.basename(os.path.normpath(plgn))}":\n{error}')
			exit()
	try:
		plgnpchr = open(plgnpccmdhf, 'r', encoding = 'utf-8').read()
	except Exception:
		pass
	else:
		plgnspccmdhelp += '\n\n' + plgnpchr.strip()
	try:
		plgncmdfr = open(plgncmdf, 'r', encoding = 'utf-8').read().split('\n')
	except Exception:
		pass
	else:
		try:
			for p in plgncmdfr:
				ps = p[1:].split('"', 1)
				plgncmds[ps[0]] = (plgn, ps[1].replace('\\n', '\n'))
		except Exception as error:
			error = str(error)
			info('Error!', f'There was an error in loading the Alt-X commands of the plugin "{os.path.basename(os.path.normpath(plgn))}":\n{error}')
			exit()
for code in init:
	try:
		exec(code[1])
	except Exception as error:
		error = str(error)
		info('Error!', f'There was an error in initializing the plugin "{os.path.basename(os.path.normpath(code[0]))}":\n{error}')
class ErrorHandler:
	def __init__(self):
		self.win = None
		self.textbox = None
	def write(self, error):
		try:
			if error.strip():
				def _do_write(error = error):
					if self.win == None or not self.win.exists:
						self.win = root.subwin()
						self.win.title('Error')
						self.win.bind('<Escape>', lambda event: self.win.destroy())
						self.win.bind('<Return>', lambda event: self.win.destroy())
						scrollbar = self.win.scroll()
						self.textbox = self.win.textbox(yscrollcommand = scrollbar.set, font = (monospace, 12), width = 60, height = 15)
						scrollbar.config(command = self.textbox.yview)
						scrollbar.pack(fill = 'y', side = 'right')
						self.textbox.pack(fill = 'both', expand = True, side = 'left')
						self.textbox.insert('end', error)
						self.textbox.see('end')
						self.textbox.config(state = 'disabled')
						self.win.style(root.gettheme())
						self.win.update()
						self.win.sizablefalse()
					else:
						self.textbox.config(state = 'normal')
						self.textbox.insert('end', f'\n{error}')
						self.textbox.see('end')
						self.textbox.config(state = 'disabled')
				root.after(0, _do_write)
		except Exception:
			print(error)
	def flush(self):
		pass
root = easytk.win()
def _report_callback_exception(exc, val, tb):
	if issubclass(exc, easytk.tk.TclError):
		return
	easytk.tk.Tk.report_callback_exception(root, exc, val, tb)
root.report_callback_exception = _report_callback_exception
fm = root.menu()
em = root.menu()
om = root.menu()
pm = root.menu()
lm = root.menu()
pcm = root.menu()
hm = root.menu()
mg = root.menu()
plgnm = root.menu()
all_editor_menus = {'File': fm, 'Edit': em, 'Options': om, 'PyCode': pcm, 'MathGod': mg, 'Plugins': plgnm, 'Help': hm}
os.makedirs(f'{homedir}/.local/share/PyNotes/tempfiles', exist_ok = True)
sys.stderr = ErrorHandler()
pcsettitle = False
import math as mathmod
try:
	defs = file.read().split('\n')
	file.close()
	dicts = defs[4].split(',')
	if defs[1] == 'False':
		bfr = False
	elif defs[1] == 'True':
		bfr = True
	else:
		raise Exception
	if defs[5] == 'True':
		emacskeysforsearch = True
	elif defs[5] == 'False':
		emacskeysforsearch = False
	else:
		raise Exception
	if defs[6] == 'True':
		taborspace = True
	elif defs[6] == 'False':
		taborspace = False
	else:
		raise Exception
	if defs[7] == 'True':
		nographicalfiledialogs = True
	elif defs[7] == 'False':
		nographicalfiledialogs = False
	pythonexecutable = defs[8]
	exec('theme = ' + '{' + defs[9] + '}')
	theme['python:variable_names']
	theme['python:function_names']
	theme['python:class_names']
	theme['python:class_instances']
	theme['python:function_arguments']
	theme['python:operators']
	theme['python:module_names']
	theme['pynotes:found']
	theme['pynotes:foundhighlight']
	theme['pynotes:marked']
	theme['latex:commands']
	theme['latex:arguments']
	theme['latex:operators']
	theme['latex:square_brackets']
	theme['python:strings']
	theme['python:keywords']
	theme['python:inbuilt']
	theme['python:comments']
	theme['latex:inlinemath']
	theme['latex:environment']
	theme['latex:comments']
	theme['html:attributes']
	theme['html:tags']
	theme['html:comments']
	theme['html:quotes']
	theme['markdown:headers1']
	theme['markdown:headers2']
	theme['markdown:headers3']
	theme['markdown:headers4']
	theme['markdown:headers5']
	theme['markdown:headers6']
	theme['markdown:bold']
	theme['markdown:italic']
	theme['markdown:bold_italic']
	theme['markdown:strike']
	theme['markdown:inlinecode']
	theme['markdown:links']
	theme['markdown:blockquotes']
	theme['markdown:codeblocks']
except Exception:
	truncate = root.ask('Warning', f'You are using preferences from an older version of PyNotes which do not have all the settings of this one.\nDo you want to reset the preferences and continue?\n(File: {homedir}/.local/share/PyNotes/defs)', ('yes', 'no'))
	if not truncate:
		root.info('Info', 'Quitting PyNotes')
		root.destroy()
		exit()
	os.remove(f'{homedir}/.local/share/PyNotes/defs')
	file = open(f'{homedir}/.local/share/PyNotes/defs', 'w+', encoding = 'utf-8')
	file.write(defaultdefs)
	file.close()
	file = open(f'{homedir}/.local/share/PyNotes/defs', 'r', encoding = 'utf-8')
	defs = file.read().split('\n')
	file.close()
	dicts = defs[4].split(',')
	if defs[1] == 'False':
		bfr = False
	elif defs[1] == 'True':
		bfr = True
	if defs[5] == 'True':
		emacskeysforsearch = True
	elif defs[5] == 'False':
		emacskeysforsearch = False
	if defs[6] == 'True':
		taborspace = True
	elif defs[6] == 'False':
		taborspace = False
	if defs[7] == 'True':
		nographicalfiledialogs = True
	elif defs[7] == 'False':
		nographicalfiledialogs = False
	pythonexecutable = defs[8]
	exec('theme = ' + '{' + defs[9] + '}')
if not v == defs[0]:
	root.info('Info', 'PyNotes has been updated!')
	defs[0] = v
	file = open(f'{homedir}/.local/share/PyNotes/defs', 'w+', encoding = 'utf-8')
	for d in defs:
		file.write(d + '\n')
	file.close()
try:
	icon = f'{rootdir}/Icon.png'
	root.seticon(icon)
except Exception:
	root.error('Error', f'Could not find the icon at {rootdir}/Icon.png.\nQuitting PyNotes.')
	root.destroy()
	exit()
root.geometry('820x800')
def fileautocompletefunc(typed):
	typed = typed.strip()
	dir_ = os.path.abspath(os.path.expanduser(os.path.dirname(typed)))
	if not os.path.exists(dir_):
		return ()
	else:
		autocompletelist = ('../',)
		for file in os.listdir(dir_):
			if platform.system() == 'Linux' and file.startswith('.') and not os.path.basename(typed):
				continue
			completion = os.path.join(os.path.dirname(typed), file)
			fullpath = os.path.abspath(os.path.expanduser(completion))
			if os.path.isdir(fullpath):
				completion += '/'
			autocompletelist += (completion,)
		return autocompletelist
def openfileget(filetypes = (('All Files', '*'),), prompttext = 'Open File: '):
	if not nographicalfiledialogs:
		if platform.system() == 'Linux':
			fn = subprocess.run(['zenity', '--file-selection', '--filename=./', '--title=Open File'] + [f'--file-filter={ft[0]} | {ft[1]}' for ft in filetypes], capture_output = True, text = True).stdout.strip()
		else:
			fn = fd.askopenfilename(title = 'Open File', filetypes = filetypes)
	else:
		fn = prompt(prompttext, fileautocompletefunc)
	if not fn.strip():
		return ''
	fn = os.path.abspath(os.path.expanduser(fn))
	if not os.path.exists(fn):
		show(f'error: \'{fn}\' does not exist')
		return None
	if os.path.isdir(fn):
		show(f'error: \'{fn}\' is a directory')
		return None
	return fn
def saveasfileget(initialfile = '', prompttext = 'Save File: '):
	if not nographicalfiledialogs:
		if platform.system() == 'Linux':
			fn = subprocess.run(['zenity', '--file-selection', f'--filename={initialfile}', '--save', '--confirm-overwrite', '--title=Save As', '--file-filter=All Files | *'], capture_output = True, text = True).stdout.strip()
		else:
			fn = fd.asksaveasfilename(initialfile = initialfile)
		if not fn.strip():
			return ''
	else:
		while True:
			fn = prompt(prompttext, fileautocompletefunc, initialfile)
			if not fn.strip():
				return ''
			fn = os.path.abspath(os.path.expanduser(fn))
			if os.path.isdir(fn):
				show(f'error: \'{fn}\' is an already existing directory')
				return None
			if os.path.exists(fn):
				overwrite = prompt('File already exists. Overwrite (y/yes) or no (other): ', ('y', 'yes', 'n', 'no'))
				if overwrite.strip().lower() in ('y', 'yes'):
					break
				initialfile = fn
			else:
				break
	return fn
class Editor(easytk.ttk.Frame):
	for code in editor_init_functions:
		try:
			exec(code, globals(), locals())
		except Exception as error:
			error = str(error)
			root.error('Error', f'Error in editor init functions:\n{error}')
	class FileChangeHandler(FileSystemEventHandler):
		def __init__(self, outer):
			self.outer = outer
			super().__init__()
		def _handle(self, path):
			if os.path.abspath(path) != self.outer.title:
				return
			if self.outer.file_editing_own:
				return
			if self.outer._file_watch_prompt_pending:
				return
			self.outer._file_watch_prompt_pending = True
			self.outer._main_queue.put(self.outer._file_watch_prompt)
		def on_modified(self, event):
			if event.is_directory:
				return
			self._handle(event.src_path)
		def on_created(self, event):
			if event.is_directory:
				return
			self._handle(event.src_path)
		def on_moved(self, event):
			if event.is_directory:
				return
			self._handle(event.dest_path)
	_SHARED_STATE_ATTRS = frozenset(('unsaved', 'unsavedtext', 'hmode', 'title', 'file_editing_own', '_file_watch_prompt_pending', 'imageloaded', 'observer', '_python_scopes', '_python_call_kwargs', '_python_module_literals', '_python_literal_attrs', '_python_name_positions', '_python_def_names', '_python_typed_attrs', '_python_param_default_tags', '_python_kwarg_positions', '_python_import_dotted_lines', '_python_import_orig_name_tags', '_python_instance_name_positions', '_python_global_stmt_kind_positions', '_python_names_scan_thread', '_python_scan_after_id', '_python_edit_generation', '_python_module_spec_cache', '_python_module_members_cache', '_python_module_class_members_cache', '_python_module_func_params_cache', '_ha_running', '_ha_pending'))
	_TK_INTERNAL_ATTRS = frozenset(('_w', '_name', 'children', 'master', 'tk', '_tclCommands', 'widgetName', '_last_child_ids'))
	_PER_PANE_ATTRS = frozenset(('root', 'fileinfo', 'filename', 'filetype', 'filesize', 'mf', 'sf', 'lf', 'latexbold', 'latexitalic', 'latexunderline', 'latexsubscript', 'latexsuperscript', 'latexnumberlist', 'latexbulletlist', 'latexsectionvar', 'latexsection', 'latexparagraph', 'latexequation', 'latexcharvar', 'latexmath', 'ef', 'tabs', 'scrlbr', '_own_type', 'ln', 'active', 'imageload', 'm', 'view_master', 'view_children', '_selectionpoint', 'type_top', 'type_bottom', '_prev_visible_region', '_ha_after_id', '_filesize_after_id', '_unsaved_after_id', '_main_queue', '_hapyshell_running', '_pyshell_last_scan_key', '_pyshell_cached_scope_result', '_pyshell_session_names', '_pyshell_session_types', '_pyshell_session_classes', '_pyshell_session_aliases', '_pyshell_session_origins', '_pyshell_session_method_params', '_pyshell_session_accepts_any', '_pyshell_session_module_bases', '_pyshell_session_func_origins', '_pyshell_session_attr_types', '_pyshell_session_class_attr_types', '_pyshell_session_func_params', '_pyshell_session_func_accepts_any', '_pyshell_session_class_bases', '_pyshell_session_inherited', '_pyshell_session_instance_only', 'shellcmd', 'loginframe', 'email', 'password', 'server', 'port', 'entryframe', 'recipiententry', 'subjectentry', 'buttonframe', 'attachmentslist', 'attachmentslistwidget', 'emailtextbox', '_email_logged_in'))
	def __setattr__(self, name, value):
		if name in Editor._SHARED_STATE_ATTRS and self.__dict__.get('view_master') is not None:
			setattr(self.__dict__['view_master'], name, value)
		else:
			object.__setattr__(self, name, value)
	def __getattr__(self, name):
		if name in Editor._SHARED_STATE_ATTRS:
			master = self.__dict__.get('view_master')
			if master is not None:
				return getattr(master, name)
		raise AttributeError(name)
	@property
	def type_(self):
		if self.view_master is None:
			for child in self.view_children:
				if child.active:
					return child._own_type
		return self._own_type
	@type_.setter
	def type_(self, value):
		self._own_type = value
	def _group_members(self):
		resolved = self.view_master if self.view_master else self
		return [resolved] + list(resolved.view_children)
	def _focused_pane(self):
		for member in self._group_members():
			if member.active:
				return member
		return self
	@property
	def selectionpoint(self):
		return self._focused_pane()._selectionpoint
	@selectionpoint.setter
	def selectionpoint(self, value):
		self._focused_pane()._selectionpoint = value
	def _make_peer_type(self, master):
		name = 'peertype%d' % id(self)
		master._own_type.peer_create(str(self.mf) + '.' + name)
		peer = easytk.tk.Text.__new__(easytk.tk.Text)
		peer.widgetName = 'text'
		peer._tclCommands = None
		peer._setup(self.mf, {'name': name})
		for option in master._own_type.configure():
			if option in ('xscrollcommand', 'yscrollcommand'):
				continue
			try:
				peer.configure(**{option: master._own_type.cget(option)})
			except Exception:
				pass
		return peer
	def _wire_type(self):
		self.scrlbr.config(command = self.type_.yview)
		self.type_.focus_set()
		self.ln = TkLineNumbers(self.mf, self.type_, justify = 'center')
		self.type_.config(yscrollcommand = lambda *args: [self.scrlbr.set(*args), self.ln.redraw()])
		self.ln.pack(side = 'left', fill = 'y')
		self.type_.pack(side = 'right', fill = 'both', expand = True)
		self._bind_type_events()
		self._bind_focus_recursive(self._own_type)
	def _bind_focus_recursive(self, widget, skip_widgets = ()):
		if widget in skip_widgets:
			return
		widget.bind('<FocusIn>', lambda event, editor = self: setactive(all_editors.index(editor)), add = True)
		for child in widget.winfo_children():
			self._bind_focus_recursive(child, skip_widgets)
	def _bind_type_events(self):
		self.type_.bind('<Control-a>', lambda event: self.selall())
		self.type_.bind('<Control-n>', lambda event: self.nw())
		self.type_.bind('<Control-o>', lambda event: self.llld())
		self.type_.bind('<Control-c>', lambda event: self.cp())
		self.type_.bind('<Control-v>', lambda event: self.pst())
		self.type_.bind('<Control-x>', lambda event: self.cut())
		self.type_.bind('<KeyRelease>', lambda event: self.keypress())
		self.type_.bind('<BackSpace>', lambda event: show('delete text'))
		self.type_.bind('<Delete>', lambda event: show('delete text'))
		self.type_.bind('<Return>', lambda event: self.indent())
		self.type_.bind('<Alt-l>', lambda event: self.gl())
		self.type_.bind('<Control-p>', lambda event: self.ptf())
		self.type_.bind('<Control-P>', lambda event: self.ptb())
		self.type_.bind('<Control-f>', lambda event: self.f())
		self.type_.bind('<Control-F>', lambda event: self.fr())
		self.type_.bind('<Control-z>', lambda event: self.undo())
		self.type_.bind('<Control-Z>', lambda event: self.redo())
		self.type_.bind('<Control-s>', lambda event: self.sssv())
		self.type_.bind('<Control-S>', lambda event: self.ssv())
		self.type_.bind('<F5>', lambda event: self.f5())
		self.type_.bind('<Control-space>', lambda event: self.toggleselpoint())
		self.type_.bind('<KeyPress>', self.selkeypress)
	def selkeypress(self, event):
		if not self.selectionpoint:
			return
		if event.keysym in ('BackSpace', 'Delete', 'Return', 'Tab') or (event.char and ord(event.char[0]) >= 32):
			self.removeselpoint()
		else:
			self.type_.after_idle(self.selupdate)
	def _sync_chrome(self):
		master = self.view_master
		if master is None:
			return
		self.filename.config(text = master.filename.cget('text'))
		self.filesaved.config(text = master.filesaved.cget('text'))
		self.filetype.config(text = master.filetype.cget('text'))
		self.filesize.config(text = master.filesize.cget('text'))
		self.tabs.tab(self.ef, state = master.tabs.tab(master.ef, option = 'state'))
		if master.hmode == 'latex':
			self.lfouter.pack(padx = 10, pady = 10, side = 'top', fill = 'x', before = self.fileinfo)
		else:
			self.lfouter.pack_forget()
		if master.imageloaded:
			self.type_.pack_forget()
			self.ln.pack_forget()
			self.tabs.pack_forget()
		else:
			self.ln.pack(side = 'left', fill = 'y', anchor = 'n')
			self.type_.pack(fill = 'both', expand = True, anchor = 'n')
			self.tabs.pack(padx = 10, pady = 10, fill = 'both', expand = True)
	def _cancel_type_after_ids(self):
		for name in ('_main_poll_after_id', '_ha_after_id', '_filesize_after_id', '_unsaved_after_id', '_python_scan_after_id', '_find_apply_after_id'):
			after_id = getattr(self, name, None)
			if after_id is not None:
				try:
					self._own_type.after_cancel(after_id)
				except Exception:
					pass
				setattr(self, name, None)
		if self._ha_apply_after_id is not None:
			try:
				root.after_cancel(self._ha_apply_after_id)
			except Exception:
				pass
			self._ha_apply_after_id = None
	def _cancel_all_after_ids(self):
		self._cancel_type_after_ids()
		for name, widget in (('_type_setview_after_id', self.mf), ('_do_backup_after_id', self.mf), ('_email_login_poll_after_id', self.ef), ('_shell_setview_after_id', self.sf)):
			after_id = getattr(self, name, None)
			if after_id is not None:
				try:
					widget.after_cancel(after_id)
				except Exception:
					pass
				setattr(self, name, None)
		if self._pyshell_stop_poller is not None:
			try:
				self._pyshell_stop_poller()
			except Exception:
				pass
	def _connect_to(self, master):
		old_type = self.type_
		old_ln = self.ln
		self._cancel_type_after_ids()
		self.type_ = self._make_peer_type(master)
		self.mainwidget = self.type_
		self._wire_type()
		old_ln.destroy()
		old_type.destroy()
		for name in Editor._SHARED_STATE_ATTRS:
			self.__dict__.pop(name, None)
		self.view_master = master
		master.view_children.append(self)
		self.m = master.m
		self._sync_chrome()
		self._main_poll()
		pcrun(pycode_keybindings_cdt)
	def _disconnect(self):
		if self.view_children:
			_promote_new_master(self)
			self.view_children = []
			old_type = self.type_
			old_ln = self.ln
			self._cancel_type_after_ids()
			self.type_ = root.textbox(master = self.mf, undo = True, font = (defs[2], 12), wrap = 'word')
			self.mainwidget = self.type_
			self._wire_type()
			old_ln.destroy()
			old_type.destroy()
			self.init_hl_tags()
			self.init_plugin_tags()
			self.type_.edit_reset()
			self._python_reset_scan_state()
			self._main_poll()
			pcrun(pycode_keybindings_cdt)
		if self.view_master is not None:
			master = self.view_master
			if self in master.view_children:
				master.view_children.remove(self)
			old_type = self.type_
			old_ln = self.ln
			self._cancel_type_after_ids()
			self.type_ = root.textbox(master = self.mf, undo = True, font = (defs[2], 12), wrap = 'word')
			self.mainwidget = self.type_
			self._wire_type()
			old_ln.destroy()
			old_type.destroy()
			self._main_poll()
			self.view_master = None
			self.unsaved = False
			self.unsavedtext = ''
			self.hmode = 'normal'
			self.title = ''
			self.imageloaded = False
			self.file_editing_own = False
			self._file_watch_prompt_pending = False
			self.observer = None
			self._python_scopes = [{'start': 1, 'end': 1, 'parent': None, 'names': {}}]
			self._python_call_kwargs = {}
			self._python_module_literals = []
			self._python_literal_attrs = []
			self._python_name_positions = []
			self._python_def_names = []
			self._python_typed_attrs = []
			self._python_param_default_tags = []
			self._python_kwarg_positions = []
			self._python_import_dotted_lines = []
			self._python_import_orig_name_tags = []
			self._python_instance_name_positions = set()
			self._python_global_stmt_kind_positions = {}
			self._python_names_scan_thread = None
			self._python_scan_after_id = None
			self._python_edit_generation = [0]
			self._python_module_spec_cache = {}
			self._python_module_members_cache = {}
			self._python_module_class_members_cache = {}
			self._python_module_func_params_cache = {}
			self._ha_running = [False]
			self._ha_pending = [None]
			self.m = root.menu()
			for label, menu in all_editor_menus.items():
				self.m.add_cascade(label = label, menu = menu)
			self.init_hl_tags()
			self.init_plugin_tags()
			self.type_.edit_reset()
			self._python_reset_scan_state()
			self.filename.config(text = 'Untitled')
			self.filetype.config(text = 'Plain Text (*.*)')
			self.filesize.config(text = '0 bytes')
			self.tabs.tab(self.ef, state = 'hidden')
			self.lfouter.pack_forget()
			pcrun(pycode_keybindings_cdt)
	def _detach_before_close(self):
		if self.view_children:
			_promote_new_master(self)
			self.view_children = []
		if self.view_master is not None:
			master = self.view_master
			if self in master.view_children:
				master.view_children.remove(self)
	def _smart_open(self, path):
		abspath = os.path.abspath(path)
		resolved = self.view_master if self.view_master else self
		if resolved.title == abspath:
			return
		match = find_open_editor(abspath)
		self._disconnect()
		if match is not None and match is not self:
			self._connect_to(match)
		else:
			self.ld(path)
	def __init__(self, master, file = None, view_master = None, *args, **kwargs):
		super().__init__(master, *args, **kwargs)
		self.view_master = view_master
		self.view_children = []
		self.fileinfo = root.frame(master = self)
		self.fileinfo.pack(padx = 10, pady = 10, fill = 'x')
		self.filename = root.text(master = self.fileinfo, text = 'Untitled', padding = (5, 5, 5, 5), relief = 'raised')
		self.filename.grid(column = 0, row = 0)
		self.filesaved = root.text(master = self.fileinfo, text = 'Untitled File', padding = (5, 5, 5, 5), relief = 'raised')
		self.filesaved.grid(column = 1, row = 0)
		self.filetype = root.text(master = self.fileinfo, text = 'Plain Text (*.*)', padding = (5, 5, 5, 5), relief = 'sunken')
		self.filetype.grid(column = 2, row = 0)
		self.filesize = root.text(master = self.fileinfo, text = '0 bytes', padding = (5, 5, 5, 5), relief = 'raised')
		self.filesize.grid(column = 3, row = 0)
		self.tabs = root.tabs(master = self)
		self.mf = root.frame(master = self.tabs)
		self.sf = root.frame(master = self.tabs)
		self.ef = root.frame(master = self.tabs)
		self.lfouter = root.frame(master = self)
		self.lfcanvas = easytk.ttk.Canvas(self.lfouter, highlightthickness = 0)
		self.lfscroll = root.scroll(master = self.lfouter, orient = 'horizontal', command = self.lfcanvas.xview)
		self.lfcanvas.configure(xscrollcommand = self.lfscroll.set)
		self.lfcanvas.pack(side = 'top', fill = 'x')
		self.lfscroll.pack(side = 'top', fill = 'x')
		self.lf = root.frame(master = self.lfcanvas)
		self.lfcanvaswindow = self.lfcanvas.create_window((0, 0), window = self.lf, anchor = 'nw')
		self.lf.bind('<Configure>', lambda event: self.lfcanvas.configure(scrollregion = self.lfcanvas.bbox('all'), height = self.lf.winfo_reqheight()))
		root.text(master = self.lf, text = 'LaTeX:').grid(column = 0, row = 0, padx = 10, pady = 10)
		self.latexbold = root.button(master = self.lf, text = 'Bold', command = self.boldlatex)
		self.latexbold.grid(column = 1, row = 0, padx = 10, pady = 10)
		self.latexitalic = root.button(master = self.lf, text = 'Italic', command = self.italiclatex)
		self.latexitalic.grid(column = 2, row = 0, padx = 10, pady = 10)
		self.latexunderline = root.button(master = self.lf, text = 'Underline', command = self.underlinelatex)
		self.latexunderline.grid(column = 3, row = 0, padx = 10, pady = 10)
		self.latexsubscript = root.button(master = self.lf, text = 'Subscript', command = self.subscriptlatex)
		self.latexsubscript.grid(column = 4, row = 0, padx = 10, pady = 10)
		self.latexsuperscript = root.button(master = self.lf, text = 'Superscript', command = self.superscriptlatex)
		self.latexsuperscript.grid(column = 5, row = 0, padx = 10, pady = 10)
		self.latexnumberlist = root.button(master = self.lf, text = 'Numbered List', command = self.numberlistlatex)
		self.latexnumberlist.grid(column = 6, row = 0, padx = 10, pady = 10)
		self.latexbulletlist = root.button(master = self.lf, text = 'Bullet List', command = self.bulletlistlatex)
		self.latexbulletlist.grid(column = 7, row = 0, padx = 10, pady = 10)
		self.latexsectionvar = root.stringvar(master = self.lf)
		self.latexsection = root.dropdown(stringvar = self.latexsectionvar, showdefault = 'Section', options = ['Section', 'Subsection', 'Subsubsection'], master = self.lf, command = self.sectionlatex)
		self.latexsection.grid(column = 8, row = 0, padx = 10, pady = 10)
		self.latexparagraph = root.button(master = self.lf, text = 'Paragraph', command = self.paragraphlatex)
		self.latexparagraph.grid(column = 9, row = 0, padx = 10, pady = 10)
		self.latexequation = root.button(master = self.lf, text = 'Equation', command = self.equationlatex)
		self.latexequation.grid(column = 10, row = 0, padx = 10, pady = 10)
		self.latexcharvar = root.stringvar()
		self.latexmath = root.dropdown(master = self.lf, stringvar = self.latexcharvar, showdefault = 'Multiplication', options = ['Multiplication', 'Division', 'Less or equal', 'More or equal', 'Not equal', 'Infinity', 'Summation', 'Integral', 'Pi', 'Theta', 'Alpha Lower', 'Alpha Upper', 'Inline Math'], command = self.mathlatex)
		self.latexmath.grid(column = 11, row = 0, padx = 10, pady = 10)
		self.tabs.add(self.mf, text = 'Editor')
		self.tabs.add(self.sf, text = 'Python Shell', state = 'hidden')
		self.tabs.add(self.ef, text = 'Email', state = 'hidden')
		self.tabs.pack(fill = 'both', expand = True)
		self.scrlbr = root.scroll(master = self.mf)
		self.scrlbr.pack(side = 'right', fill = 'y')
		if view_master is None:
			self.type_ = root.textbox(master = self.mf, undo = True, font = (defs[2], 12), wrap = 'word')
		else:
			self.type_ = self._make_peer_type(view_master)
		self.mainwidget = self.type_
		self._wire_type()
		self.type_top = '1.0'
		self.type_bottom = 'end'
		self._ha_after_id = None
		self._ha_apply_after_id = None
		self._find_apply_after_id = None
		self._filesize_after_id = None
		self._unsaved_after_id = None
		self._prev_visible_region = None
		self._main_poll_after_id = None
		self._type_setview_after_id = None
		self._email_login_poll_after_id = None
		self._shell_setview_after_id = None
		self._do_backup_after_id = None
		self._pyshell_stop_poller = None
		self._main_queue = queue.Queue()
		self._hapyshell_running = [False]
		self._pyshell_last_scan_key = None
		self._pyshell_cached_scope_result = None
		self._pyshell_session_names = {}
		self._pyshell_session_types = {}
		self._pyshell_session_classes = {}
		self._pyshell_session_aliases = {}
		self._pyshell_session_origins = {}
		self._pyshell_session_method_params = {}
		self._pyshell_session_accepts_any = set()
		self._pyshell_session_module_bases = {}
		self._pyshell_session_func_origins = {}
		self._pyshell_session_attr_types = {}
		self._pyshell_session_class_attr_types = {}
		self._pyshell_session_func_params = {}
		self._pyshell_session_func_accepts_any = {}
		self._pyshell_session_class_bases = {}
		self._pyshell_session_inherited = {'members': set(), 'attr_types': set(), 'method_params': set()}
		self._pyshell_session_instance_only = {}
		self._selectionpoint = None
		if view_master is None:
			self.unsaved = False
			self.unsavedtext = ''
			self.hmode = 'normal'
			self.title = ''
			self.imageloaded = False
			self.file_editing_own = False
			self._file_watch_prompt_pending = False
			self._python_scopes = [{'start': 1, 'end': 1, 'parent': None, 'names': {}}]
			self._python_call_kwargs = {}
			self._python_module_literals = []
			self._python_literal_attrs = []
			self._python_name_positions = []
			self._python_def_names = []
			self._python_typed_attrs = []
			self._python_param_default_tags = []
			self._python_kwarg_positions = []
			self._python_import_dotted_lines = []
			self._python_import_orig_name_tags = []
			self._python_instance_name_positions = set()
			self._python_global_stmt_kind_positions = {}
			self._python_names_scan_thread = None
			self._python_scan_after_id = None
			self._python_edit_generation = [0]
			self._python_module_spec_cache = {}
			self._python_module_members_cache = {}
			self._python_module_class_members_cache = {}
			self._python_module_func_params_cache = {}
			self._ha_running = [False]
			self._ha_pending = [None]
			self.m = root.menu()
			for label, menu in all_editor_menus.items():
				self.m.add_cascade(label = label, menu = menu)
		else:
			self.m = view_master.m
			view_master.view_children.append(self)
		self.active = False
		self.shellpy()
		self.init_pythonshell_hl_tags()
		if view_master is None:
			self.init_hl_tags()
			self.init_plugin_tags()
			self.type_.edit_reset()
			self._python_reset_scan_state()
		self.type_setview()
		self._main_poll()
		if view_master is None:
			self.do_backup()
		self._email_logged_in = False
		self._email_login_setup()
		self._email_login_poll()
		if view_master is None:
			if file:
				self.ld(file)
		else:
			self._sync_chrome()
		self._bind_focus_recursive(self, (self._own_type,) + tuple(self.ef.winfo_children()) + ((self.imageload,) if getattr(self, 'imageload', None) else ()))
		for code in editor_init_code:
			try:
				exec(code, globals(), locals())
			except Exception as error:
				error = str(error)
				root.error('Error', f'Error in editor init code:\n{error}')
	def close(self):
		is_last_reference = self.view_master is None and not self.view_children
		answer = root.ask('Warning', 'Do you want to save file before closing?', options = ('yes', 'no', 'cancel')) if (self.unsaved and is_last_reference) else False
		if answer != None:
			if answer:
				if not self.saveforclose():
					return False
			self._detach_before_close()
			return True
		return False
	def _file_watch_prompt(self):
		answer = root.warning('Warning', f'The file "{self.title}" has changed on disk. Should PyNotes discard unsaved changes and reload the file, or overwrite the file on next save?', buttons = ['Discard Changes & Reload', 'Ignore'])
		self._file_watch_prompt_pending = False
		if answer == 'Discard Changes & Reload':
			self.ld(self.title)
	def setselpoint(self, index = None):
		if index is None:
			index = self.type_.index('insert')
		self.selectionpoint = index
		show(f'selection point set at {self.selectionpoint}')
	def removeselpoint(self):
		if self.selectionpoint:
			self.selectionpoint = None
			show('removed selection point')
		else:
			show('no selection point set')
	def toggleselpoint(self):
		if self.selectionpoint:
			self.removeselpoint()
		else:
			self.setselpoint()
	def lld(self):
		if self._file_watch_prompt_pending:
			show('select \'Discard Changes & Reload\' or \'Ignore\' external changes before loading another file')
			return
		fn = openfileget((('All Files', '*'), ('Python Files', '*.py'), ('Text Files', '*.txt'), ('LaTeX Files', '*.tex'), ('PNG Images', '*.png'), ('PDF Files', '*.pdf'), ('ePub Files', '*.epub')))
		pcrunhook('before', 'open-file-current-editor', fn if fn else None)
		if fn:
			show('open file')
			self._smart_open(fn)
			pcrunhook('after', 'open-file-current-editor', fn)
	def ssssv(self, nm):
		if self.view_master:
			return self.view_master.ssssv(nm)
		if self._file_watch_prompt_pending:
			show('select \'Ignore\' external changes before saving file')
			return
		if not nm == '':
			self.sv(nm)
		self.clt(nm)
	def clt(self, nt):
		if self.view_master:
			return self.view_master.clt(nt)
		global pcsettitle
		if self is active:
			pcsettitle = False
		try:
			self.observer.stop()
			self.observer.join()
		except Exception:
			pass
		try:
			if not nt == '':
				if self is active:
					root.title('PyNotes' + ' - ' + os.path.basename(nt))
				self.filesaved.config(text = 'Saved File')
				self.filename.config(text = os.path.basename(nt))
				self.title = os.path.abspath(nt)
			else:
				if self is active:
					root.title('PyNotes - Untitled')
				self.filesaved.config(text = 'Untitled File')
				self.filename.config(text = 'Untitled')
				self.title = ''
			self.unsaved = False
			for child in self.view_children:
				child.filesaved.config(text = 'Saved File')
				child.filename.config(text = self.filename.cget('text'))
		except Exception:
			pass
		else:
			self.file_editing_own = False
			if nt == '':
				return
			self.observer = Observer()
			self.observer.schedule(self.FileChangeHandler(self), os.path.dirname(self.title), recursive = False)
			self.observer.start()
	def sssv(self):
		if self.view_master:
			return self.view_master.sssv()
		if self._file_watch_prompt_pending:
			show('select \'Ignore\' external changes before saving file')
			return
		if not self.title == '':
			pcrunhook('before', 'save-file')
			self.ssssv(self.title)
			pcrunhook('after', 'save-file')
		else:
			self.ssv()
	def saveforclose(self):
		if self.view_master:
			return self.view_master.saveforclose()
		if not self.title == '':
			self.ssssv(self.title)
		else:
			if self.ssv() == False:
				return False
			else:
				return True
	def ld(self, nm):
		if os.path.isdir(nm):
			root.error('Error', f'"{nm}" is a directory.')
			return
		if self._file_watch_prompt_pending:
			show('select \'Discard Changes & Reload\' or \'Ignore\' external changes before loading another file')
			return
		if not nm == '':
			self._disconnect()
			try:
				self.imageload.pack_forget()
				self.imageloaded = False
				self.mainwidget = self.type_
			except Exception:
				pass
			else:
				self.hmode = 'normal'
				self.ln.pack(side = 'left', fill = 'y', anchor = 'n')
				self.type_.pack(fill = 'both', expand = True, anchor = 'n')
				self.tabs.pack(padx = 10, pady = 10, fill = 'both', expand = True)
			self.type_.delete('1.0', 'end')
			if os.path.dirname(nm):
				try:
					os.chdir(os.path.dirname(nm))
				except Exception:
					root.error('Error', f'The directory \'{os.path.dirname(nm)}\' does not exist.')
					return
				else:
					nm = os.path.basename(nm)
					self.type_.edit_reset()
					self._python_reset_scan_state()
			if not os.path.exists(nm):
				open(nm, 'w', encoding = 'utf-8')
			try:
				file = open(nm, 'r', encoding = 'utf-8')
				content = file.read()
				self.type_.delete('1.0', 'end')
				self.type_.insert('end', content)
				file.close()
			except Exception as error:
				error = str(error)
				try:
					self.imageload = root.image(master = self, image = nm, imsize = (1, 1))
					self._bind_focus_recursive(self.imageload)
					self.imageloaded = True
					self.mainwidget = self.imageload
				except Exception:
					try:
						pdf = pdfplumber.open(nm)
						self.type_.delete('1.0', 'end')
						for page in pdf.pages:
							self.type_.insert('end', page.extract_text())
					except Exception:
						try:
							parsed = parser.from_file(nm, service = 'text')
							content = parsed['content']
							self.type_.delete('1.0', 'end')
							self.type_.insert('end', content)
						except Exception:
							root.error('Error', error)
						else:
							self.clt(nm)
							self.filesize.config(text = str(os.path.getsize(nm)) + ' bytes')
							self.sethmenu(None)
							self.tabs.tab(self.ef, state = 'hidden')
							self.lfouter.pack_forget()
							self.hmode = 'epub'
							self.filetype.config(text = 'EPUB File (*.epub)')
							self.keypress()
					else:
						self.clt(nm)
						self.filesize.config(text = str(os.path.getsize(nm)) + ' bytes')
						self.sethmenu(None)
						self.tabs.tab(self.ef, state = 'hidden')
						self.lfouter.pack_forget()
						self.hmode = 'pdf'
						self.filetype.config(text = 'PDF File (*.pdf)')
						self.keypress()
				else:
					self.type_.pack_forget()
					self.ln.pack_forget()
					self.tabs.pack_forget()
					self.imageload.pack(fill = 'both', expand = True)
					self.imageloaded = True
					self.mainwidget = self.imageload
					self.clt(nm)
					self.filesize.config(text = str(os.path.getsize(nm)) + ' bytes')
					self.hmode = 'png'
					self.filetype.config(text = 'PNG Image (*.png)')
					self.imageload.focus_set()
					self.sethmenu(None)
					self.tabs.tab(self.ef, state = 'hidden')
					self.lfouter.pack_forget()
					self.keypress()
			else:
				self.unsavedtext = self.type_.get('1.0', 'end-1c')
				self.clt(nm)
				self.filesize.config(text = str(os.path.getsize(nm)) + ' bytes')
				if os.path.splitext(nm)[1] == '.py':
					self.pchmode('python')
					self.filetype.config(text = 'Python File (*.py)')
				elif os.path.splitext(nm)[1] == '.tex':
					self.pchmode('latex')
					self.filetype.config(text = 'LaTeX / TeX File (*.tex)')
				elif os.path.splitext(nm)[1] == '.html':
					self.pchmode('html')
					self.filetype.config(text = 'HTML File (*.html)')
				elif os.path.splitext(nm)[1] == '.md':
					self.pchmode('markdown')
				else:
					self.pchmode('normal')
				self.keypress()
			self.type_.edit_reset()
			self._python_reset_scan_state()
			for child in self.view_children:
				child._sync_chrome()
	def llld(self):
		if self._file_watch_prompt_pending:
			show('select \'Discard Changes & Reload\' or \'Ignore\' external changes before loading another file')
			return
		is_last_reference = self.view_master is None and not self.view_children
		answer = root.ask('Warning', 'Do you want to save file before closing?', options = ('yes', 'no', 'cancel')) if (self.unsaved and is_last_reference) else False
		if answer != None:
			if answer:
				if not self.saveforclose():
					return
			self.lld()
	def sv(self, nm):
		if self.view_master:
			return self.view_master.sv(nm)
		if self._file_watch_prompt_pending:
			show('select \'Ignore\' external changes before saving file')
			return
		if not nm == '':
			if not self.hmode in ['png', 'pdf', 'epub']:
				try:
					content = self.type_.get('1.0', 'end-1c')
					if content == self.unsavedtext:
						show('no changes to save')
						return
					if os.path.isdir(nm):
						root.error('Error', f'"{os.path.basename(nm)}" is an already existing directory.')
						return True
					if os.path.dirname(nm):
						os.chdir(os.path.dirname(nm))
						nm = os.path.basename(nm)
					self.file_editing_own = True
					try:
						file = open(nm, 'w', encoding = 'utf-8')
						file.write(content)
						file.close()
						self.unsavedtext = content
						show('save file')
						self.clt(nm)
					except Exception as error:
						error = str(error)
						root.error('Error', error)
						self.file_editing_own = False
						return True
					else:
						self.file_editing_own = False
				except Exception:
					pass
			else:
				root.error('Error!', 'Cannot save files of this type.')
	def ssv(self):
		if self.view_master:
			return self.view_master.ssv()
		if self._file_watch_prompt_pending:
			show('select \'Ignore\' external changes before saving file')
			return
		fn = saveasfileget(self.type_.get('1.0', '1.end'))
		pcrunhook('before', 'save-as-file', fn if fn else None)
		if fn:
			show('save as file')
			if not self.sv(fn):
				return False
			self.clt(fn)
			pcrunhook('after', 'save-as-file', fn)
		else:
			return False
	def nw(self):
		is_last_reference = self.view_master is None and not self.view_children
		answer = root.ask('Warning', 'Do you want to save file before closing?', options = ('yes', 'no', 'cancel')) if (self.unsaved and is_last_reference) else False
		if answer != None:
			if answer:
				if not self.saveforclose():
					return
			pcrunhook('before', 'new-file-current-editor')
			self._disconnect()
			try:
				self.imageload.pack_forget()
				self.imageloaded = False
				self.mainwidget = self.type_
			except Exception:
				pass
			else:
				self.ln.pack(side = 'left', fill = 'y', anchor = 'n')
				self.type_.pack(fill = 'both', expand = True, anchor = 'n')
				self.tabs.pack(padx = 10, pady = 10, fill = 'both', expand = True)
			self.type_.delete('1.0', 'end')
			self.unsavedtext = ''
			self.clt('')
			self.type_.edit_reset()
			self._python_reset_scan_state()
			self.sethmenu(None)
			self.tabs.tab(self.ef, state = 'hidden')
			self.lfouter.pack_forget()
			self.hmode = 'normal'
			self.filetype.config(text = 'Plain Text (*.*)')
			show('open new file')
			self.filename.config(text = 'Untitled')
			self.filesize.config(text = '0 bytes')
			pcrunhook('after', 'new-file-current-editor')
	def fr(self):
		show('find & replace text')
		def fback():
			nonlocal i
			if searching[0]:
				return
			self.type_.tag_remove('foundhighlight', '1.0', 'end')
			if not foundlist:
				return
			if i != 0:
				i -= 1
			else:
				i = len(foundlist) - 1
			self.type_.tag_add('foundhighlight', foundlist[i][0], foundlist[i][1])
			exec("self.type_.tag_config('foundhighlight'," + theme['pynotes:foundhighlight'] + ')')
			self.type_.see(foundlist[i][1])
			self.type_.mark_set('insert', foundlist[i][1])
			self.keypress()
		def fnext(replacetext = None):
			nonlocal i
			if searching[0]:
				return
			self.type_.tag_remove('foundhighlight', '1.0', 'end')
			if not foundlist:
				return
			if replacetext is not None:
				replace_start = foundlist[i][0]
				programmatic_edit[0] = True
				self.type_.delete(foundlist[i][0], foundlist[i][1])
				self.type_.insert(foundlist[i][0], replacetext)
				programmatic_edit[0] = False
				after_replace = '%s+%dc' % (replace_start, len(replacetext))
				def after_search():
					nonlocal i
					for j in range(len(foundlist)):
						if self.type_.compare(foundlist[j][0], '>=', after_replace):
							i = j
							self.type_.tag_add('foundhighlight', foundlist[i][0], foundlist[i][1])
							exec("self.type_.tag_config('foundhighlight'," + theme['pynotes:foundhighlight'] + ')')
							self.type_.see(foundlist[i][1])
							self.type_.mark_set('insert', foundlist[i][1])
							return
					self.type_.tag_remove('found', '1.0', 'end')
					self.type_.tag_remove('foundhighlight', '1.0', 'end')
					ok.destroy()
				pending_action[0] = after_search
				updatef()
			else:
				if i != len(foundlist) - 1:
					i += 1
				else:
					self.type_.tag_remove('found', '1.0', 'end')
					self.type_.tag_remove('foundhighlight', '1.0', 'end')
					ok.destroy()
					return
				self.type_.tag_add('foundhighlight', foundlist[i][0], foundlist[i][1])
				exec("self.type_.tag_config('foundhighlight'," + theme['pynotes:foundhighlight'] + ')')
				self.type_.see(foundlist[i][1])
				self.type_.mark_set('insert', foundlist[i][1])
			self.keypress()
		def replaceall(replacetext):
			nonlocal i
			if searching[0]:
				return
			self.type_.tag_remove('foundhighlight', '1.0', 'end')
			if not foundlist:
				return
			programmatic_edit[0] = True
			for j in range(len(foundlist) - 1, i - 1, -1):
				self.type_.delete(foundlist[j][0], foundlist[j][1])
				self.type_.insert(foundlist[j][0], replacetext)
			programmatic_edit[0] = False
			self.type_.tag_remove('found', '1.0', 'end')
			ok.destroy()
			self.keypress()
		search_cancel = [None]
		searching = [False]
		pending_action = [None]
		programmatic_edit = [False]
		def updatef():
			nonlocal i
			nonlocal foundlist
			find = findbox.get()
			useregx = regx.get()
			case = cs.get()
			if search_cancel[0]:
				search_cancel[0].set()
			if not find:
				self.type_.tag_remove('found', '1.0', 'end')
				self.type_.tag_remove('foundhighlight', '1.0', 'end')
				foundlist.clear()
				searching[0] = False
				return
			self.type_.tag_remove('found', '1.0', 'end')
			self.type_.tag_remove('foundhighlight', '1.0', 'end')
			text_content = self.type_.get('1.0', 'end')
			cancel = threading.Event()
			search_cancel[0] = cancel
			searching[0] = True
			def do_search():
				try:
					pat = find if useregx else re.escape(find)
					flags = 0 if case else re.IGNORECASE
					compiled = re.compile(pat, flags)
				except Exception:
					self._main_queue.put(lambda: _start_apply([]))
					return
				line_starts = [0]
				pos = 0
				while True:
					pos = text_content.find('\n', pos)
					if pos == -1:
						break
					line_starts.append(pos + 1)
					pos += 1
				def to_tk(offset):
					lo, hi = 0, len(line_starts) - 1
					while lo < hi:
						mid = (lo + hi + 1) // 2
						if line_starts[mid] <= offset:
							lo = mid
						else:
							hi = mid - 1
					return f'{lo + 1}.{offset - line_starts[lo]}'
				tk_results = []
				for m in compiled.finditer(text_content):
					if cancel.is_set():
						return
					if m.start() == m.end():
						continue
					tk_results.append((to_tk(m.start()), to_tk(m.end())))
				if not cancel.is_set():
					self._main_queue.put(lambda: _start_apply(tk_results))
			def _start_apply(tk_results):
				nonlocal i, foundlist
				if cancel.is_set():
					searching[0] = False
					return
				foundlist = []
				i = 0
				_apply_batch(tk_results, len(tk_results), 0)
			def _apply_batch(tk_results, n, idx):
				nonlocal i, foundlist
				if cancel.is_set():
					self._own_type.tag_remove('found', '1.0', 'end')
					self._find_apply_after_id = None
					searching[0] = False
					return
				end = idx + 500
				if end > n:
					end = n
				for k in range(idx, end):
					st, et = tk_results[k]
					self._own_type.tag_add('found', st, et)
					foundlist.append((st, et))
				if end < n:
					self._find_apply_after_id = self._own_type.after(1, lambda: _apply_batch(tk_results, n, end))
				else:
					self._find_apply_after_id = None
					searching[0] = False
					if foundlist:
						exec("self.type_.tag_config('found'," + theme['pynotes:found'] + ')')
					action = pending_action[0]
					pending_action[0] = None
					if action:
						action()
					elif foundlist:
						self.type_.tag_add('foundhighlight', foundlist[i][0], foundlist[i][1])
						exec("self.type_.tag_config('foundhighlight'," + theme['pynotes:foundhighlight'] + ')')
						self.type_.see(foundlist[i][1])
						self.type_.mark_set('insert', foundlist[i][1])
			threading.Thread(target = do_search, daemon = True).start()
		def updateff(event = None):
			if not event or event and not event.keysym == 'Return' and not (event.state & 4):
				updatef()
				return
			if not foundlist:
				return
			self.type_.tag_add('foundhighlight', foundlist[i][0], foundlist[i][1])
			exec("self.type_.tag_config('foundhighlight'," + theme['pynotes:foundhighlight'] + ')')
			self.type_.see(foundlist[i][1])
			self.type_.mark_set('insert', foundlist[i][1])
		ok = root.subwin()
		i = 0
		foundlist = []
		ok.title('Find & Replace')
		ok.text(text = 'Find:').grid(column = 0, row = 0, padx = 10, pady = 10)
		findbox = ok.entry()
		findbox.focus()
		findbox.bind('<KeyRelease>', updateff)
		if not emacskeysforsearch:
			findbox.bind('<Shift-Return>', lambda event: fback())
			findbox.bind('<Return>', lambda event: fnext())
		findbox.grid(column = 1, row = 0, padx = 10, pady = 10, sticky = 'ew')
		ok.text(text = 'Replace:').grid(column = 0, row = 1, padx = 10, pady = 10)
		replacebox = ok.entry()
		if not emacskeysforsearch:
			replacebox.bind('<Return>', lambda event: fnext(replacebox.get()))
		replacebox.grid(column = 1, row = 1, padx = 10, pady = 10, sticky = 'ew')
		cs = ok.booleanvar()
		ok.check(text = 'Case Sensitive', variable = cs, command = updateff).grid(column = 0, row = 2, padx = 10, pady = 10, sticky = 'ew')
		regx = ok.booleanvar()
		ok.check(text = 'Use regexp', variable = regx, command = updateff).grid(column = 1, row = 2, padx = 10, pady = 10, sticky = 'ew')
		ok.button(text = 'Previous', command = fback).grid(column = 0, row = 3, padx = 10, pady = 10, sticky = 'ew')
		ok.button(text = 'Next', command = fnext).grid(column = 1, row = 3, padx = 10, pady = 10, sticky = 'ew')
		def replace_current():
			nonlocal i
			if searching[0] or not foundlist:
				return
			programmatic_edit[0] = True
			self.type_.delete(foundlist[i][0], foundlist[i][1])
			self.type_.insert(foundlist[i][0], replacebox.get())
			programmatic_edit[0] = False
			saved_i = i
			def after_search():
				nonlocal i
				if not foundlist:
					return
				i = saved_i if saved_i < len(foundlist) else len(foundlist) - 1
				self.type_.tag_add('foundhighlight', foundlist[i][0], foundlist[i][1])
				exec("self.type_.tag_config('foundhighlight'," + theme['pynotes:foundhighlight'] + ')')
				self.type_.see(foundlist[i][1])
				self.type_.mark_set('insert', foundlist[i][1])
			pending_action[0] = after_search
			updatef()
		ok.button(text = 'Replace', command = replace_current).grid(column = 0, row = 4, padx = 10, pady = 10, sticky = 'ew')
		ok.button(text = 'Replace and next', command = lambda: fnext(replacebox.get())).grid(column = 1, row = 4, padx = 10, pady = 10, sticky = 'ew')
		ok.button(text = 'Replace all', command = lambda: replaceall(replacebox.get())).grid(column = 0, row = 5, padx = 10, pady = 10, sticky = 'ew')
		def close_find():
			self.type_.tag_remove('found', '1.0', 'end')
			self.type_.tag_remove('foundhighlight', '1.0', 'end')
			for member in self._group_members():
				member._own_type.unbind('<<Modified>>')
			ok.destroy()
		def on_type_modified(event):
			event.widget.edit_modified(False)
			if programmatic_edit[0]:
				return
			close_find()
		for member in self._group_members():
			member._own_type.edit_modified(False)
		root.update()
		for member in self._group_members():
			member._own_type.bind('<<Modified>>', on_type_modified)
		ok.button(text = 'Close', command = close_find).grid(column = 1, row = 5, padx = 10, pady = 10, sticky = 'ew')
		if emacskeysforsearch:
			ok.bind('<Alt-Return>', lambda event: fnext())
			ok.bind('^', lambda event: fback())
			ok.bind('<Control-t>', lambda event: fnext(replacebox.get()))
			ok.bind('!', lambda event: replaceall(replacebox.get()))
			ok.bind('<Return>', lambda event: close_find())
			for w in (findbox, replacebox):
				w.bind('^', lambda event: fback() or 'break')
				w.bind('!', lambda event: replaceall(replacebox.get()) or 'break')
		ok.update()
		ok.sizablefalse()
		ok.style(root.gettheme())
		ok.bind('<Escape>', lambda event: close_find())
		ok.protocol('WM_DELETE_WINDOW', close_find)
	def f(self):
		show('find text')
		def fback():
			nonlocal i
			self.type_.tag_remove('foundhighlight', '1.0', 'end')
			if not foundlist:
				return
			if i != 0:
				i -= 1
			else:
				i = len(foundlist) - 1
			self.type_.tag_add('foundhighlight', foundlist[i][0], foundlist[i][1])
			exec("self.type_.tag_config('foundhighlight'," + theme['pynotes:foundhighlight'] + ')')
			self.type_.see(foundlist[i][1])
			self.type_.mark_set('insert', foundlist[i][1])
			self.keypress()
		def fnext():
			nonlocal i
			self.type_.tag_remove('foundhighlight', '1.0', 'end')
			if not foundlist:
				return
			if i != len(foundlist) - 1:
				i += 1
			else:
				i = 0
			self.type_.tag_add('foundhighlight', foundlist[i][0], foundlist[i][1])
			exec("self.type_.tag_config('foundhighlight'," + theme['pynotes:foundhighlight'] + ')')
			self.type_.see(foundlist[i][1])
			self.type_.mark_set('insert', foundlist[i][1])
			self.keypress()
		search_cancel = [None]
		def updatef():
			nonlocal i
			nonlocal foundlist
			find = findbox.get()
			useregx = regx.get()
			case = cs.get()
			if search_cancel[0]:
				search_cancel[0].set()
			if not find:
				self.type_.tag_remove('found', '1.0', 'end')
				self.type_.tag_remove('foundhighlight', '1.0', 'end')
				foundlist.clear()
				return
			self.type_.tag_remove('found', '1.0', 'end')
			self.type_.tag_remove('foundhighlight', '1.0', 'end')
			text_content = self.type_.get('1.0', 'end')
			cancel = threading.Event()
			search_cancel[0] = cancel
			def do_search():
				try:
					pat = find if useregx else re.escape(find)
					flags = 0 if case else re.IGNORECASE
					compiled = re.compile(pat, flags)
				except Exception:
					self._main_queue.put(lambda: _start_apply([]))
					return
				line_starts = [0]
				pos = 0
				while True:
					pos = text_content.find('\n', pos)
					if pos == -1:
						break
					line_starts.append(pos + 1)
					pos += 1
				def to_tk(offset):
					lo, hi = 0, len(line_starts) - 1
					while lo < hi:
						mid = (lo + hi + 1) // 2
						if line_starts[mid] <= offset:
							lo = mid
						else:
							hi = mid - 1
					return f'{lo + 1}.{offset - line_starts[lo]}'
				tk_results = []
				for m in compiled.finditer(text_content):
					if cancel.is_set():
						return
					if m.start() == m.end():
						continue
					tk_results.append((to_tk(m.start()), to_tk(m.end())))
				if not cancel.is_set():
					self._main_queue.put(lambda: _start_apply(tk_results))
			def _start_apply(tk_results):
				nonlocal i, foundlist
				if cancel.is_set():
					return
				foundlist = []
				i = 0
				_apply_batch(tk_results, len(tk_results), 0)
			def _apply_batch(tk_results, n, idx):
				nonlocal i, foundlist
				if cancel.is_set():
					self._own_type.tag_remove('found', '1.0', 'end')
					self._find_apply_after_id = None
					return
				end = idx + 500
				if end > n:
					end = n
				for k in range(idx, end):
					st, et = tk_results[k]
					self._own_type.tag_add('found', st, et)
					foundlist.append((st, et))
				if end < n:
					self._find_apply_after_id = self._own_type.after(1, lambda: _apply_batch(tk_results, n, end))
				else:
					self._find_apply_after_id = None
					if foundlist:
						exec("self.type_.tag_config('found'," + theme['pynotes:found'] + ')')
						self.type_.tag_add('foundhighlight', foundlist[i][0], foundlist[i][1])
						exec("self.type_.tag_config('foundhighlight'," + theme['pynotes:foundhighlight'] + ')')
						self.type_.see(foundlist[i][1])
						self.type_.mark_set('insert', foundlist[i][1])
			threading.Thread(target = do_search, daemon = True).start()
		def updateff(event = None):
			if not event or event and not event.keysym == 'Return' and not (event.state & 4):
				updatef()
				return
			if not foundlist:
				return
			self.type_.tag_add('foundhighlight', foundlist[i][0], foundlist[i][1])
			exec("self.type_.tag_config('foundhighlight'," + theme['pynotes:foundhighlight'] + ')')
			self.type_.see(foundlist[i][1])
			self.type_.mark_set('insert', foundlist[i][1])
		ok = root.subwin()
		i = 0
		foundlist = []
		ok.title('Find')
		ok.text(text = 'Find:').grid(column = 0, row = 0, padx = 10, pady = 10)
		findbox = ok.entry()
		findbox.focus()
		findbox.bind('<KeyRelease>', updateff)
		if not emacskeysforsearch:
			findbox.bind('<Return>', lambda event: fnext())
			findbox.bind('<Shift-Return>', lambda event: fback())
		findbox.grid(column = 1, row = 0, padx = 10, pady = 10, sticky = 'ew')
		cs = ok.booleanvar()
		ok.check(text = 'Case Sensitive', variable = cs, command = updateff).grid(column = 0, row = 1, padx = 10, pady = 10, sticky = 'ew')
		regx = ok.booleanvar()
		ok.check(text = 'Use regexp', variable = regx, command = updateff).grid(column = 1, row = 1, padx = 10, pady = 10, sticky = 'ew')
		ok.button(text = 'Previous', command = fback).grid(column = 0, row = 2, padx = 10, pady = 10, sticky = 'ew')
		ok.button(text = 'Next', command = fnext).grid(column = 1, row = 2, padx = 10, pady = 10, sticky = 'ew')
		def close_find():
			self.type_.tag_remove('found', '1.0', 'end')
			self.type_.tag_remove('foundhighlight', '1.0', 'end')
			for member in self._group_members():
				member._own_type.unbind('<<Modified>>')
			ok.destroy()
		def on_type_modified(event):
			event.widget.edit_modified(False)
			close_find()
		for member in self._group_members():
			member._own_type.edit_modified(False)
		root.update()
		for member in self._group_members():
			member._own_type.bind('<<Modified>>', on_type_modified)
		ok.button(text = 'Close', command = close_find).grid(column = 1, row = 3, padx = 10, pady = 10, sticky = 'ew')
		if emacskeysforsearch:
			ok.bind('<Control-s>', lambda event: fnext())
			ok.bind('<Control-r>', lambda event: fback())
			ok.bind('<Return>', lambda event: close_find())
		ok.update()
		ok.sizablefalse()
		ok.style(root.gettheme())
		ok.bind('<Escape>', lambda event: close_find())
		ok.protocol('WM_DELETE_WINDOW', close_find)
	def type_getvisible(self):
		self._own_type.update()
		top = self._own_type.index('@0,0-2l')
		bottom = self._own_type.index(f'@0,{self._own_type.winfo_height()}+2l')
		return (top, bottom)
	def _python_reset_scan_state(self):
		self._python_edit_generation[0] += 1
		self._python_scopes = [{'start': 1, 'end': 1, 'parent': None, 'names': {}}]
		self._python_call_kwargs = {}
		self._python_module_literals = []
		self._python_literal_attrs = []
		self._python_name_positions = []
		self._python_def_names = []
		self._python_typed_attrs = []
		self._python_param_default_tags = []
		self._python_kwarg_positions = []
		self._python_import_dotted_lines = []
		self._python_import_orig_name_tags = []
		self._python_instance_name_positions = set()
		self._python_global_stmt_kind_positions = {}
		if self.hmode == 'python':
			self.python_trigger_name_scan()
	def _python_find_spec_cached(self, name):
		if name in self._python_module_spec_cache:
			return self._python_module_spec_cache[name]
		spec = self._python_resolve_spec_fs(name)
		self._python_module_spec_cache[name] = spec
		return spec
	def _python_resolve_spec_fs(self, name):
		parts = name.split('.')
		if '' in parts or not parts:
			return None
		if len(parts) == 1:
			return _python_resolve_toplevel_fs(parts[0])
		parent = self._python_find_spec_cached('.'.join(parts[:-1]))
		if parent is None or not parent.submodule_search_locations:
			return None
		leaf = parts[-1]
		for _dir in parent.submodule_search_locations:
			_pkg = os.path.join(_dir, leaf, '__init__.py')
			if os.path.isfile(_pkg):
				return _PythonModuleSpec(name, _pkg, [os.path.dirname(_pkg)])
			_pdir = os.path.join(_dir, leaf)
			if os.path.isdir(_pdir):
				return _PythonModuleSpec(name, None, [_pdir])
			_mod = os.path.join(_dir, leaf + '.py')
			if os.path.isfile(_mod):
				return _PythonModuleSpec(name, _mod, None)
			for _ext in _PYTHON_EXTENSION_SUFFIXES:
				if os.path.isfile(os.path.join(_dir, leaf + _ext)):
					return _PythonModuleSpec(name, os.path.join(_dir, leaf + _ext), None)
		return None
	def _python_resolve_module_members(self, name, visited = None):
		if name in self._python_module_members_cache:
			return self._python_module_members_cache[name]
		if visited is None:
			visited = set()
		if name in visited:
			return {}
		visited.add(name)
		spec = self._python_find_spec_cached(name)
		src_path = _python_module_src_path(spec, name)
		if src_path is None:
			self._python_module_members_cache[name] = {}
			return {}
		try:
			with open(src_path, 'r', encoding = 'utf-8') as f:
				src = f.read()
			with warnings.catch_warnings():
				warnings.simplefilter('ignore')
				mod_ast = ast.parse(src)
		except Exception:
			self._python_module_members_cache[name] = {}
			return {}
		members = _python_inspect_ast_members(mod_ast.body)
		_import_nodes = []
		def _collect_scope_imports(_stmts, _globals):
			for _st in _stmts:
				if isinstance(_st, (ast.Import, ast.ImportFrom)):
					if _globals is None:
						_import_nodes.append(_st)
					else:
						for _al in _st.names:
							_bound = _al.asname if _al.asname else _al.name.split('.')[0]
							if _bound in _globals:
								_import_nodes.append(_st)
								break
				elif isinstance(_st, ast.Global):
					if _globals is not None:
						_globals.update(_st.names)
				elif isinstance(_st, ast.If):
					_collect_scope_imports(_st.body, _globals)
					_collect_scope_imports(_st.orelse, _globals)
				elif isinstance(_st, ast.Try):
					_collect_scope_imports(_st.body, _globals)
					for _h in _st.handlers:
						_collect_scope_imports(_h.body, _globals)
					_collect_scope_imports(_st.orelse, _globals)
					_collect_scope_imports(_st.finalbody, _globals)
				elif isinstance(_st, (ast.With, ast.AsyncWith)):
					_collect_scope_imports(_st.body, _globals)
				elif isinstance(_st, (ast.For, ast.AsyncFor, ast.While)):
					_collect_scope_imports(_st.body, _globals)
					_collect_scope_imports(_st.orelse, _globals)
				elif isinstance(_st, (ast.FunctionDef, ast.AsyncFunctionDef)):
					_fnglobals = set()
					for _sub in ast.walk(_st):
						if isinstance(_sub, ast.Global):
							_fnglobals.update(_sub.names)
					_collect_scope_imports(_st.body, _fnglobals)
				elif isinstance(_st, ast.ClassDef):
					_collect_scope_imports(_st.body, set())
		_collect_scope_imports(mod_ast.body, None)
		for node in _import_nodes:
			if isinstance(node, ast.ImportFrom):
				sub_name = _python_relative_import_target(name, node.level, node.module, bool(getattr(spec, 'submodule_search_locations', None))) if (node.module or node.level) else name
				sub_members = None
				for alias in node.names:
					if alias.name == '*':
						if sub_members is None:
							sub_members = self._python_resolve_module_members(sub_name, visited)
						for k, v in sub_members.items():
							members.setdefault(k, v)
					else:
						exported = alias.asname if alias.asname else alias.name
						if exported not in members:
							if sub_members is None:
								sub_members = self._python_resolve_module_members(sub_name, visited)
							if alias.name in sub_members:
								members[exported] = sub_members[alias.name]
								pfx = alias.name + '.'
								for k, v in sub_members.items():
									if k.startswith(pfx):
										members[exported + k[len(alias.name):]] = v
							elif self._python_find_spec_cached(f'{sub_name}.{alias.name}') is not None:
								members[exported] = 'module'
								members['@modtarget:' + exported] = f'{sub_name}.{alias.name}'
			elif isinstance(node, ast.Import):
				for alias in node.names:
					if alias.asname:
						members.setdefault(alias.asname, 'module')
						members.setdefault('@modtarget:' + alias.asname, alias.name)
					else:
						members.setdefault(alias.name.split('.')[0], 'module')
						members.setdefault('@modtarget:' + alias.name.split('.')[0], alias.name.split('.')[0])
		self._python_module_members_cache[name] = members
		return members
	def _python_resolve_module_member_kind(self, mod, class_name, member, seen = None):
		if seen is None:
			seen = set()
		key = (mod, class_name)
		if key in seen:
			return None
		seen.add(key)
		mems = self._python_resolve_module_members(mod)
		_dk = f'{class_name}.{member}'
		if _dk in mems:
			if _dk in self._python_resolve_module_func_params(mod):
				return 'func'
			return mems[_dk]
		fp = self._python_resolve_module_func_params(mod)
		imports = fp.get('@imports', {})
		if '@bases:' + class_name not in fp and class_name in imports and imports[class_name][1] is not None:
			return self._python_resolve_module_member_kind(imports[class_name][0], imports[class_name][1], member, seen)
		for base in fp.get('@bases:' + class_name, []):
			bparts = base.split('.')
			if len(bparts) == 1:
				if '@bases:' + base in fp:
					_r = self._python_resolve_module_member_kind(mod, base, member, seen)
					if _r is not None:
						return _r
				elif base in imports and imports[base][1] is not None:
					_r = self._python_resolve_module_member_kind(imports[base][0], imports[base][1], member, seen)
					if _r is not None:
						return _r
			else:
				broot = bparts[0]
				if broot in imports:
					bmod = imports[broot][0]
					full_mod = '.'.join([bmod] + bparts[1:-1]) if len(bparts) > 2 else bmod
					_r = self._python_resolve_module_member_kind(full_mod, bparts[-1], member, seen)
					if _r is not None:
						return _r
		return None
	def _python_resolve_module_class_members(self, mod, class_name, seen = None):
		_top_call = seen is None
		if _top_call and (mod, class_name) in self._python_module_class_members_cache:
			return self._python_module_class_members_cache[(mod, class_name)]
		if seen is None:
			seen = set()
		key = (mod, class_name)
		if key in seen:
			return {}
		seen.add(key)
		mems = self._python_resolve_module_members(mod)
		prefix = class_name + '.'
		out = {k[len(prefix):]: v for k, v in mems.items() if k.startswith(prefix) and '.' not in k[len(prefix):]}
		fp = self._python_resolve_module_func_params(mod)
		for _mk in out:
			if prefix + _mk in fp:
				out[_mk] = 'func'
		imports = fp.get('@imports', {})
		if '@bases:' + class_name not in fp and class_name in imports and imports[class_name][1] is not None:
			for k, v in self._python_resolve_module_class_members(imports[class_name][0], imports[class_name][1], seen).items():
				out.setdefault(k, v)
		for base in fp.get('@bases:' + class_name, []):
			bparts = base.split('.')
			if len(bparts) == 1:
				if '@bases:' + base in fp:
					for k, v in self._python_resolve_module_class_members(mod, base, seen).items():
						out.setdefault(k, v)
				elif base in imports and imports[base][1] is not None:
					for k, v in self._python_resolve_module_class_members(imports[base][0], imports[base][1], seen).items():
						out.setdefault(k, v)
			else:
				broot = bparts[0]
				if broot in imports:
					bmod = imports[broot][0]
					full_mod = '.'.join([bmod] + bparts[1:-1]) if len(bparts) > 2 else bmod
					for k, v in self._python_resolve_module_class_members(full_mod, bparts[-1], seen).items():
						out.setdefault(k, v)
		if _top_call:
			self._python_module_class_members_cache[(mod, class_name)] = out
		return out
	def _python_build_scopes(self, text, gen = None, line_blocks = None, seed_names = None, seed_types = None, seed_classes = None, seed_aliases = None, seed_origins = None, seed_method_params = None, seed_accepts_any = None, seed_module_bases = None, seed_func_origins = None, seed_attr_types = None, seed_class_attr_types = None, seed_func_params = None, seed_func_accepts_any = None, seed_class_bases = None, seed_inherited = None, seed_instance_only = None):
		def _ck():
			if gen is not None and self._python_edit_generation[0] != gen:
				raise _PythonScanCancelled()
		def _same_block(l1, l2):
			if line_blocks is None or l1 == l2:
				return True
			if not (0 < l1 <= len(line_blocks)) or not (0 < l2 <= len(line_blocks)):
				return False
			_b1 = line_blocks[l1 - 1]
			return _b1 != 0 and _b1 == line_blocks[l2 - 1]
		def _assign_pairs(targets, value):
			pairs = []
			def _pair(t, v):
				if isinstance(t, ast.Starred):
					_pair(t.value, None)
				elif isinstance(t, (ast.Tuple, ast.List)):
					if isinstance(v, (ast.Tuple, ast.List)) and len(v.elts) == len(t.elts):
						for _t2, _v2 in zip(t.elts, v.elts):
							_pair(_t2, _v2)
					else:
						_ev = v if isinstance(v, ast.JoinedStr) or (isinstance(v, ast.Constant) and isinstance(v.value, str)) else None
						for _t2 in t.elts:
							_pair(_t2, _ev)
				else:
					pairs.append((t, v))
			for t in targets:
				_pair(t, value)
			return pairs
		lines = text.split('\n')
		tree = None
		for _ in range(len(lines) + 2):
			_ck()
			try:
				with warnings.catch_warnings():
					warnings.simplefilter('ignore')
					tree = ast.parse('\n'.join(lines))
				break
			except (SyntaxError, SyntaxWarning) as error:
				ln = max(1, min(getattr(error, 'lineno', None) or 1, len(lines)))
				msg = getattr(error, 'msg', '') or ''
				target = ln - 1
				if 'unexpected indent' in msg and ln > 1:
					indent_n = len(lines[ln - 1]) - len(lines[ln - 1].lstrip())
					earlier_same = any(lines[i].strip() and (len(lines[i]) - len(lines[i].lstrip())) == indent_n for i in range(ln - 2, -1, -1))
					if earlier_same:
						for i in range(ln - 2, -1, -1):
							if lines[i].strip():
								if (len(lines[i]) - len(lines[i].lstrip())) < indent_n and not lines[i].rstrip().endswith(':'):
									target = i
								break
				if not lines[target].strip():
					target = ln - 1
				if not lines[target].strip():
					break
				lines[target] = ''
			except Exception:
				return None
		if tree is None:
			return None
		_ck()
		builder = _PythonScopeBuilder()
		builder.scopes[0]['end'] = len(lines)
		try:
			builder.visit(tree)
		except Exception:
			return None
		if seed_names:
			for _sn, _sk in seed_names.items():
				builder.scopes[0]['names'].setdefault(_sn, []).append((0, _sk))
		if seed_aliases:
			for _sa, _sm in seed_aliases.items():
				builder.module_aliases.setdefault(_sa, _sm)
				builder.module_alias_defs.setdefault(_sa, []).append((0, _sm))
		if seed_names:
			for _sn, _sk in seed_names.items():
				if _sk == 'module':
					builder.module_aliases.setdefault(_sn, _sn)
					builder.module_alias_defs.setdefault(_sn, []).append((0, _sn))
		if seed_func_params:
			for _sfp_n, _sfp_v in seed_func_params.items():
				builder.func_params.setdefault(_sfp_n, []).insert(0, (0, set(_sfp_v), 0))
		if seed_func_accepts_any:
			for _sfa_n, _sfa_v in seed_func_accepts_any.items():
				builder.func_accepts_any.setdefault(_sfa_n, []).insert(0, (0, _sfa_v, 0))
		_ck()
		line_to_scope = [None] * (len(lines) + 2)
		for ln in range(1, len(lines) + 1):
			if ln % 500 == 0:
				_ck()
			best_idx = None
			for idx, sc in enumerate(builder.scopes):
				if sc['start'] <= ln <= sc['end']:
					if best_idx is None or sc['start'] >= builder.scopes[best_idx]['start']:
						best_idx = idx
			line_to_scope[ln] = best_idx
		def _scope_for_line(ln):
			if 0 <= ln < len(line_to_scope):
				return line_to_scope[ln]
			return None
		def _scope_for_pos(ln, col):
			winner = None
			winner_start = None
			for idx, sc in enumerate(builder.scopes):
				if sc['start'] <= ln <= sc['end']:
					if sc['start'] == ln and col < sc.get('start_col', 0):
						continue
					_ec = sc.get('end_col')
					if sc['end'] == ln and _ec is not None and col >= _ec:
						continue
					if winner is None or sc['start'] >= winner_start:
						winner = idx
						winner_start = sc['start']
			return winner
		def _def_scope_chain(lineno):
			chain = []
			_si = _scope_for_line(lineno)
			_inner = _si
			while _si is not None:
				_sc = builder.scopes[_si]
				if _sc.get('kind') != 'class' or _si == _inner:
					chain.append(_si)
				_si = _sc['parent']
			if 0 not in chain:
				chain.append(0)
			return chain
		def _rebind_def_scopes(store):
			for _rn, _rdefs in store.items():
				for _ri, _rd in enumerate(_rdefs):
					if len(_rd) > 2:
						_rdefs[_ri] = (_rd[0], _rd[1], _binding_scope_for(_rn, _rd[2]))
		def _binding_scope_of_def(lineno):
			_si = _scope_for_line(lineno)
			if _si is None:
				return 0
			_par = builder.scopes[_si]['parent']
			return _par if _par is not None else 0
		def _binding_scope_for(name, sc_idx):
			if sc_idx is None:
				return sc_idx
			sc = builder.scopes[sc_idx]
			if name in sc.get('globals', {}):
				return 0
			if name in sc.get('nonlocals', {}):
				_p = sc['parent']
				while _p is not None:
					_ps = builder.scopes[_p]
					if _ps.get('kind') == 'function' and name in _ps['names'] and name not in _ps.get('globals', {}) and name not in _ps.get('nonlocals', {}):
						return _p
					_p = _ps['parent']
				return sc_idx
			return sc_idx
		_rebind_def_scopes(builder.func_params)
		_rebind_def_scopes(builder.func_accepts_any)
		_ck()
		def _call_name_kind(name, lineno):
			sidx = _scope_for_line(lineno)
			inner = sidx
			while sidx is not None:
				sc = builder.scopes[sidx]
				if sc.get('kind') == 'class' and sidx != inner:
					sidx = sc['parent']
					continue
				if name in sc['names']:
					best = None
					latest = None
					for dl, kind in sc['names'][name]:
						if latest is None or dl > latest[0]:
							latest = (dl, kind)
						if sidx == inner and dl > lineno:
							continue
						if best is None or dl > best[0]:
							best = (dl, kind)
					if best is None and latest is not None and name in _PYTHON_BUILTIN_NAMES:
						return None
					if best is None and latest is not None and _same_block(latest[0], lineno):
						best = latest
					return best[1] if best is not None else '_local'
				sidx = sc['parent']
			return None
		module_contents = {}
		local_classes = {}
		class_module_origin = {_so: [(0, _sv)] for _so, _sv in seed_origins.items()} if seed_origins else {}
		def _line_def_at(defs, lineno):
			if not defs:
				return None
			_best = None
			for _dl, _dv in defs:
				if _dl <= lineno and (_best is None or _dl >= _best[0]):
					_best = (_dl, _dv)
			if _best is None:
				for _dl, _dv in defs:
					if _same_block(_dl, lineno) and (_best is None or _dl > _best[0]):
						_best = (_dl, _dv)
			return _best[1] if _best is not None else None
		def _class_origin_at(name, lineno):
			return _line_def_at(class_module_origin.get(name), lineno)
		dynamic_class_attrs = {}
		dynamic_class_attr_types = {}
		dynamic_module_attrs = {}
		dynamic_module_attr_types = {}
		dynamic_modclass_attrs = {}
		dynamic_modclass_attr_types = {}
		tree_class_defs = []
		tree_func_defs = []
		tree_assigns = []
		tree_attributes = []
		tree_imports = []
		tree_importfroms = []
		name_positions = []
		global_stmt_positions = []
		def _skip_ws(enc, i):
			while i < len(enc) and enc[i:i + 1] in (b' ', b'\t'):
				i += 1
			return i
		_tw = 0
		for _tn in ast.walk(tree):
			_tw += 1
			if _tw % 2000 == 0:
				_ck()
			if isinstance(_tn, ast.Name):
				name_positions.append((_tn.lineno, _tn.col_offset, _tn.id, isinstance(_tn.ctx, ast.Store)))
			elif isinstance(_tn, ast.arg):
				name_positions.append((_tn.lineno, _tn.col_offset, _tn.arg, True))
			elif isinstance(_tn, ast.Attribute):
				tree_attributes.append(_tn)
			elif isinstance(_tn, ast.Assign):
				tree_assigns.append(_tn)
			elif isinstance(_tn, ast.NamedExpr) and isinstance(_tn.target, ast.Name):
				_tn.targets = [_tn.target]
				tree_assigns.append(_tn)
			elif isinstance(_tn, ast.AnnAssign) and _tn.value is not None and isinstance(_tn.target, ast.Name):
				_tn.targets = [_tn.target]
				tree_assigns.append(_tn)
			elif isinstance(_tn, ast.ClassDef):
				tree_class_defs.append(_tn)
			elif isinstance(_tn, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
				tree_func_defs.append(_tn)
			elif isinstance(_tn, ast.alias):
				if _tn.asname:
					name_positions.append((_tn.end_lineno, _tn.end_col_offset - len(_tn.asname.encode('utf-8')), _tn.asname, True))
				elif _tn.name != '*' and '.' not in _tn.name:
					name_positions.append((_tn.lineno, _tn.col_offset, _tn.name, True))
			elif isinstance(_tn, ast.Import):
				tree_imports.append(_tn)
			elif isinstance(_tn, ast.ImportFrom):
				tree_importfroms.append(_tn)
			elif isinstance(_tn, ast.ExceptHandler):
				if _tn.name and _tn.type is not None and 0 < _tn.type.end_lineno <= len(lines):
					_enc = lines[_tn.type.end_lineno - 1].encode('utf-8')
					_i = _skip_ws(_enc, _tn.type.end_col_offset)
					if _enc[_i:_i + 2] == b'as':
						_i = _skip_ws(_enc, _i + 2)
						_nb = _tn.name.encode('utf-8')
						if _enc[_i:_i + len(_nb)] == _nb:
							name_positions.append((_tn.type.end_lineno, _i, _tn.name, True))
			elif isinstance(_tn, (ast.Global, ast.Nonlocal)):
				if 0 < _tn.lineno <= len(lines):
					_enc = lines[_tn.lineno - 1].encode('utf-8')
					_i = _tn.col_offset + (6 if isinstance(_tn, ast.Global) else 8)
					for _gname in _tn.names:
						while _i < len(_enc) and _enc[_i:_i + 1] in (b' ', b'\t', b','):
							_i += 1
						_nb = _gname.encode('utf-8')
						if _enc[_i:_i + len(_nb)] != _nb:
							break
						name_positions.append((_tn.lineno, _i, _gname, False))
						global_stmt_positions.append((_tn.lineno, _i, _gname, _scope_for_line(_tn.lineno)))
						_i += len(_nb)
		def_name_positions = []
		for _tn in tree_class_defs + tree_func_defs:
			if isinstance(_tn, ast.Lambda) or not (0 < _tn.lineno <= len(lines)):
				continue
			_enc = lines[_tn.lineno - 1].encode('utf-8')
			_i = _tn.col_offset
			if isinstance(_tn, ast.ClassDef):
				_i += 5
			else:
				if _enc[_i:_i + 5] == b'async':
					_i = _skip_ws(_enc, _i + 5)
				_i += 3
			_i = _skip_ws(_enc, _i)
			_nb = _tn.name.encode('utf-8')
			if _enc[_i:_i + len(_nb)] == _nb:
				def_name_positions.append((_tn.lineno, _i, _tn.name, 'class' if isinstance(_tn, ast.ClassDef) else 'func'))
		_class_def_by_name = {}
		for _tn in tree_class_defs:
			if _tn.name not in _class_def_by_name:
				_class_def_by_name[_tn.name] = _tn
		def _flatten_class_body(body):
			out = []
			for _s in body:
				if isinstance(_s, (ast.Assign, ast.AnnAssign)):
					out.append(_s)
				elif isinstance(_s, (ast.For, ast.AsyncFor, ast.While)):
					out.extend(_flatten_class_body(_s.body))
					out.extend(_flatten_class_body(_s.orelse))
				elif isinstance(_s, ast.If):
					out.extend(_flatten_class_body(_s.body))
					out.extend(_flatten_class_body(_s.orelse))
				elif isinstance(_s, (ast.With, ast.AsyncWith)):
					out.extend(_flatten_class_body(_s.body))
				elif isinstance(_s, ast.Try):
					out.extend(_flatten_class_body(_s.body))
					for _h in _s.handlers:
						out.extend(_flatten_class_body(_h.body))
					out.extend(_flatten_class_body(_s.orelse))
					out.extend(_flatten_class_body(_s.finalbody))
			return out
		def _compute_class_members(node):
			members = _python_inspect_ast_members(node.body)
			for _bstmt in _flatten_class_body(node.body):
				_btgts = _bstmt.targets if isinstance(_bstmt, ast.Assign) else ([_bstmt.target] if isinstance(_bstmt, ast.AnnAssign) else [])
				_bval = _bstmt.value if isinstance(_bstmt, (ast.Assign, ast.AnnAssign)) else None
				if isinstance(_bval, ast.NamedExpr):
					_bval = _bval.value
				_bval = _python_unwrap_descriptor(_bval)
				if not isinstance(_bval, ast.Name):
					continue
				for _btgt in _btgts:
					if isinstance(_btgt, ast.Name) and members.get(_btgt.id) in ('var', None):
						_rk = _call_name_kind(_bval.id, _bstmt.lineno)
						if _rk in ('func', 'class', 'module'):
							members[_btgt.id] = _rk
			for meth in node.body:
				if isinstance(meth, (ast.FunctionDef, ast.AsyncFunctionDef)):
					_fp = meth.args.args[0].arg if (meth.args.args and _python_method_has_implicit_first_param(meth)) else None
					for stmt in ast.walk(meth):
						tgts = stmt.targets if isinstance(stmt, ast.Assign) else ([stmt.target] if isinstance(stmt, (ast.AnnAssign, ast.AugAssign)) else [])
						for tgt, _tval in _assign_pairs(tgts, stmt.value if isinstance(stmt, (ast.Assign, ast.AnnAssign)) else None):
							if _fp and isinstance(tgt, ast.Attribute) and isinstance(tgt.value, ast.Name) and tgt.value.id == _fp:
								_mvk = 'var'
								if isinstance(_tval, ast.Lambda):
									_mvk = 'func'
								elif isinstance(_tval, ast.Attribute) and isinstance(_tval.value, ast.Name) and _tval.value.id == _fp:
									_svk = members.get(_tval.attr)
									if _svk in ('func', 'class', 'module'):
										_mvk = _svk
								elif isinstance(_tval, ast.Name):
									_nvk = _call_name_kind(_tval.id, stmt.lineno)
									if _nvk in ('func', 'class', 'module'):
										_mvk = _nvk
								if _mvk == 'var' and members.get(tgt.attr) in ('func', 'class', 'module'):
									members[tgt.attr] = 'var'
								else:
									members.setdefault(tgt.attr, _mvk)
			return members
		class_def_lines = {}
		class_def_scopes = {}
		local_class_defs = {}
		_class_nested_lines = set()
		for _tn in tree_class_defs:
			for _tsub in _tn.body:
				if isinstance(_tsub, ast.ClassDef):
					_class_nested_lines.add((_tsub.name, _tsub.lineno))
		for _tn in tree_class_defs:
			if (_tn.name, _tn.lineno) in _class_nested_lines:
				continue
			class_def_lines.setdefault(_tn.name, []).append(_tn.lineno)
			class_def_scopes[(_tn.name, _tn.lineno)] = _binding_scope_for(_tn.name, _binding_scope_of_def(_tn.lineno))
		def _class_def_line_at(name, lineno):
			_lns = class_def_lines.get(name)
			if not _lns:
				return None
			for _sidx in _def_scope_chain(lineno):
				_cands = [_cl for _cl in _lns if class_def_scopes.get((name, _cl), 0) == _sidx]
				if not _cands:
					continue
				_best = None
				for _cl in _cands:
					if _cl <= lineno and (_best is None or _cl > _best):
						_best = _cl
				return _best if _best is not None else max(_cands)
			_best = None
			for _cl in _lns:
				if _cl <= lineno and (_best is None or _cl > _best):
					_best = _cl
			if _best is None:
				_best = max(_lns)
			return _best
		for scope in builder.scopes:
			for name, defs in scope['names'].items():
				for _, kind in defs:
					if kind == 'class' and name in _class_def_by_name and name not in local_classes:
						try:
							node = _class_def_by_name[name]
							local_classes[name] = _compute_class_members(node)
						except Exception:
							pass
		_class_first_line = {}
		for _tn in tree_class_defs:
			if _tn.name not in _class_first_line:
				_class_first_line[_tn.name] = _tn.lineno
		def _class_key_at(name, lineno):
			_dl = _class_def_line_at(name, lineno)
			if _dl is None or _dl == _class_first_line.get(name):
				return name
			return name + '\x00' + str(_dl)
		for _tn in tree_class_defs:
			if _tn.name in local_classes and _tn.lineno != _class_first_line.get(_tn.name):
				_rk = _tn.name + '\x00' + str(_tn.lineno)
				if _rk not in local_classes:
					try:
						local_classes[_rk] = _compute_class_members(_tn)
					except Exception:
						local_classes[_rk] = {}
		if seed_classes:
			for _scn, _scm in seed_classes.items():
				local_classes.setdefault(_scn, dict(_scm))
		_ck()
		def _node_class_key(node):
			if node.name in local_classes and node.lineno != _class_first_line.get(node.name):
				return node.name + '\x00' + str(node.lineno)
			return node.name
		class_bases = {}
		module_scope_class_keys = set()
		_nonmodule_scope_class_keys = set()
		_class_body_members = {}
		_self_assigned_attrs = {}
		if seed_instance_only:
			for _sio_c, _sio_v in seed_instance_only.items():
				_self_assigned_attrs.setdefault(_sio_c, set()).update(_sio_v)
		_module_class_bases = []
		for node in tree_class_defs:
			if node.name in local_classes:
				bases = []
				for base in node.bases:
					if isinstance(base, ast.Name):
						bases.append(_class_key_at(base.id, node.lineno))
					elif isinstance(base, ast.Attribute):
						bases.append(base.attr)
						_module_class_bases.append((_node_class_key(node), base))
				class_bases[_node_class_key(node)] = bases
				_class_body_members[_node_class_key(node)] = set(_bm for _bm in _python_inspect_ast_members(node.body) if '.' not in _bm)
				if _binding_scope_for(node.name, _binding_scope_of_def(node.lineno)) == 0:
					module_scope_class_keys.add(_node_class_key(node))
				else:
					_nonmodule_scope_class_keys.add(_node_class_key(node))
		if seed_class_bases:
			for _scb_c, _scb_b in seed_class_bases.items():
				module_scope_class_keys.add(_scb_c)
				if _scb_c not in class_bases:
					class_bases[_scb_c] = list(_scb_b)
		if seed_classes:
			module_scope_class_keys.update(seed_classes)
		module_scope_class_keys -= _nonmodule_scope_class_keys
		def _instance_only_attr(clskey, attr):
			for _ioc in _python_c3_linearize(clskey, class_bases, frozenset()):
				if attr in _class_body_members.get(_ioc, ()):
					return False
				if attr in _self_assigned_attrs.get(_ioc, ()):
					return True
			return False
		local_class_method_params = {}
		local_class_accepts_any = set()
		_class_attr_lambda_params = {}
		for node in tree_class_defs:
			if node.name in local_classes:
				_nk = _node_class_key(node)
				for sub in node.body:
					if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)):
						_mimp = _python_method_has_implicit_first_param(sub)
						_margs = list(sub.args.posonlyargs) + list(sub.args.args) + list(sub.args.kwonlyargs)
						_mp = (set(a.arg for a in (_margs[1:] if _mimp else _margs)) - set(a.arg for a in sub.args.posonlyargs)) | set(a.arg for a in sub.args.kwonlyargs)
						if sub.args.kwarg:
							local_class_accepts_any.add(_nk + '.' + sub.name)
						local_class_method_params[_nk + '.' + sub.name] = _mp
						_sfp = sub.args.args[0].arg if (sub.args.args and _mimp) else None
						if _sfp:
							for _astmt in ast.walk(sub):
								if not isinstance(_astmt, ast.Assign):
									continue
								for _atg in _astmt.targets:
									if isinstance(_atg, ast.Attribute) and isinstance(_atg.value, ast.Name) and _atg.value.id == _sfp:
										_av = _astmt.value
										if isinstance(_av, ast.Lambda):
											_lp = set(a.arg for a in list(_av.args.args) + list(_av.args.kwonlyargs))
											local_class_method_params[_nk + '.' + _atg.attr] = _lp
											if _av.args.kwarg:
												local_class_accepts_any.add(_nk + '.' + _atg.attr)
										elif isinstance(_av, ast.Attribute) and isinstance(_av.value, ast.Name) and _av.value.id == _sfp:
											_class_attr_lambda_params.setdefault(_nk, []).append((_atg.attr, _av.attr))
					for _clstmt in _flatten_class_body(node.body):
						_clval = _clstmt.value if isinstance(_clstmt, (ast.Assign, ast.AnnAssign)) else None
						if isinstance(_clval, ast.NamedExpr):
							_clval = _clval.value
						_clval = _python_unwrap_descriptor(_clval)
						if not isinstance(_clval, ast.Lambda):
							continue
						_cltgts = _clstmt.targets if isinstance(_clstmt, ast.Assign) else [_clstmt.target]
						_clargs = list(_clval.args.posonlyargs) + list(_clval.args.args) + list(_clval.args.kwonlyargs)
						_clp = (set(a.arg for a in (_clargs[1:] if _clargs else _clargs)) - set(a.arg for a in _clval.args.posonlyargs)) | set(a.arg for a in _clval.args.kwonlyargs)
						for _cltgt in _cltgts:
							if not isinstance(_cltgt, ast.Name):
								continue
							local_class_method_params[_nk + '.' + _cltgt.id] = _clp
							if _clval.args.kwarg:
								local_class_accepts_any.add(_nk + '.' + _cltgt.id)
					for _cmstmt in _flatten_class_body(node.body):
						_cmval = _cmstmt.value if isinstance(_cmstmt, (ast.Assign, ast.AnnAssign)) else None
						if isinstance(_cmval, ast.NamedExpr):
							_cmval = _cmval.value
						_cmval = _python_unwrap_descriptor(_cmval)
						if not isinstance(_cmval, ast.Name):
							continue
						_cmsrc = _nk + '.' + _cmval.id
						if _cmsrc not in local_class_method_params:
							continue
						_cmtgts = _cmstmt.targets if isinstance(_cmstmt, ast.Assign) else [_cmstmt.target]
						for _cmtgt in _cmtgts:
							if not isinstance(_cmtgt, ast.Name):
								continue
							local_class_method_params[_nk + '.' + _cmtgt.id] = local_class_method_params[_cmsrc]
							if _cmsrc in local_class_accepts_any:
								local_class_accepts_any.add(_nk + '.' + _cmtgt.id)
					for _cmstmt in _flatten_class_body(node.body):
						_cmval = _cmstmt.value if isinstance(_cmstmt, (ast.Assign, ast.AnnAssign)) else None
						if isinstance(_cmval, ast.NamedExpr):
							_cmval = _cmval.value
						_cmval = _python_unwrap_descriptor(_cmval)
						if not (isinstance(_cmval, ast.Attribute) and isinstance(_cmval.value, ast.Name)):
							continue
						_cmbase = _class_key_at(_cmval.value.id, _cmstmt.lineno)
						_cmsrc = _cmbase + '.' + _cmval.attr
						if _cmbase not in local_classes or _cmsrc not in local_class_method_params:
							continue
						_cmtgts = _cmstmt.targets if isinstance(_cmstmt, ast.Assign) else [_cmstmt.target]
						for _cmtgt in _cmtgts:
							if not isinstance(_cmtgt, ast.Name):
								continue
							local_class_method_params[_nk + '.' + _cmtgt.id] = local_class_method_params[_cmsrc]
							local_classes[_nk][_cmtgt.id] = 'func'
							if _cmsrc in local_class_accepts_any:
								local_class_accepts_any.add(_nk + '.' + _cmtgt.id)
		if seed_method_params:
			for _smk, _smv in seed_method_params.items():
				local_class_method_params.setdefault(_smk, _smv)
		if seed_accepts_any:
			local_class_accepts_any.update(seed_accepts_any)
		class_attr_types = {}
		if seed_class_attr_types:
			for _scat_c, _scat_m in seed_class_attr_types.items():
				class_attr_types.setdefault(_scat_c, {}).update(_scat_m)
		var_attr_types = {}
		def _var_attr_type_at(sc_idx, name, attr, lineno):
			sidx = sc_idx
			inner = sidx
			while sidx is not None:
				sc = builder.scopes[sidx]
				if sc.get('kind') == 'class' and sidx != inner:
					sidx = sc['parent']
					continue
				if name in sc['names']:
					_vat = var_attr_types.get((sidx, name), {}).get(attr)
					if _vat:
						best = None
						for dl, tp in _vat:
							if sidx == inner and dl > lineno:
								continue
							if best is None or dl > best[0]:
								best = (dl, tp)
						if best is not None:
							return True, best[1]
					return False, None
				sidx = sc['parent']
			return False, None
		for _ncnode in tree_class_defs:
			if _ncnode.name not in local_classes:
				continue
			_nckey = _node_class_key(_ncnode)
			for _ncsub in _ncnode.body:
				if isinstance(_ncsub, ast.ClassDef) and _ncsub.name in local_classes:
					class_attr_types.setdefault(_nckey, {})[_ncsub.name] = ('class', _node_class_key(_ncsub))
		_inherited_members = set()
		_inherited_attr_types = set()
		_inherited_method_params = set()
		_direct_attr_assigns = set()
		if seed_inherited:
			_inherited_members.update(seed_inherited.get('members', ()))
			_inherited_attr_types.update(seed_inherited.get('attr_types', ()))
			_inherited_method_params.update(seed_inherited.get('method_params', ()))
		def _python_merge_class_bases():
			for cls in list(class_bases):
				if cls not in local_classes:
					continue
				_filled = set()
				_filled_attrs = set()
				_filled_params = set()
				for base in _python_c3_linearize(cls, class_bases, frozenset())[1:]:
					if base not in local_classes:
						continue
					for k, v in local_classes[base].items():
						if (base, k) in _inherited_members or k in _filled:
							continue
						if k not in local_classes[cls] or (local_classes[cls][k] == 'var' and v != 'var'):
							local_classes[cls][k] = v
							_inherited_members.add((cls, k))
							_filled.add(k)
					for _ak, _av in class_attr_types.get(base, {}).items():
						if (base, _ak) in _inherited_attr_types or _ak in _filled_attrs:
							continue
						if _ak in _self_assigned_attrs.get(cls, ()) or (cls, _ak) in _direct_attr_assigns:
							continue
						if _ak not in class_attr_types.setdefault(cls, {}):
							class_attr_types[cls][_ak] = _av
							_inherited_attr_types.add((cls, _ak))
							_filled_attrs.add(_ak)
					for _mk in list(local_class_method_params):
						if not _mk.startswith(base + '.') or _mk in _inherited_method_params:
							continue
						_meth = _mk[len(base) + 1:]
						if _meth in _filled_params:
							continue
						_ck2 = cls + '.' + _meth
						if _ck2 not in local_class_method_params:
							local_class_method_params[_ck2] = local_class_method_params[_mk]
							if _mk in local_class_accepts_any:
								local_class_accepts_any.add(_ck2)
							_inherited_method_params.add(_ck2)
							_filled_params.add(_meth)
		_python_merge_class_bases()
		for _calp_nk, _calp_pairs in _class_attr_lambda_params.items():
			for _attr_name, _src_meth in _calp_pairs:
				_src_key = _calp_nk + '.' + _src_meth
				if _src_key in local_class_method_params and _calp_nk + '.' + _attr_name not in local_class_method_params:
					local_class_method_params[_calp_nk + '.' + _attr_name] = local_class_method_params[_src_key]
					if _src_key in local_class_accepts_any:
						local_class_accepts_any.add(_calp_nk + '.' + _attr_name)
		_ck()
		for _bname, _bmembers in _PYTHON_BUILTIN_MEMBERS.items():
			local_classes.setdefault(_bname, dict(_bmembers))
		def _name_is_class_at(name, lineno):
			if name not in local_classes:
				return False
			_k = _call_name_kind(name, lineno)
			return _k == 'class' or _k is None
		class_type_maps = {}
		if seed_attr_types:
			for _sat_c, _sat_m in seed_attr_types.items():
				class_type_maps.setdefault(_sat_c, {}).update(_sat_m)
		for node in tree_class_defs:
			if node.name in local_classes:
				class_type_maps[_node_class_key(node)] = {}
		_ck()
		candidate_modules = set()
		for _, imported_name, top_name, _, _ in builder.import_names:
			candidate_modules.add(top_name)
			candidate_modules.add(imported_name)
		for _, top_name in builder.module_literals:
			candidate_modules.add(top_name)
		for _, module_name, imported_name, _orig_name, _ in builder.from_imports:
			if module_name:
				candidate_modules.add(module_name.split('.')[0])
				candidate_modules.add(module_name)
				candidate_modules.add(f'{module_name}.{_orig_name}')
		for _adefs in builder.module_alias_defs.values():
			for _, _sm in _adefs:
				candidate_modules.add(_sm)
		for _sm in builder.module_aliases.values():
			candidate_modules.add(_sm)
		valid_modules = set()
		imported_modules = set()
		for name in candidate_modules:
			spec = self._python_find_spec_cached(name)
			if spec is not None:
				valid_modules.add(name)
				imported_modules.add(name)
				members = self._python_resolve_module_members(name)
				if members:
					module_contents[name] = members
		_dotted_module_targets = {}
		for name in candidate_modules:
			if name in valid_modules or '.' not in name:
				continue
			_dmt = self._python_resolve_dotted_module(name)
			if _dmt is None:
				continue
			_dotted_module_targets[name] = _dmt
			if _dmt not in valid_modules:
				valid_modules.add(_dmt)
				imported_modules.add(_dmt)
				_dmems = self._python_resolve_module_members(_dmt)
				if _dmems:
					module_contents[_dmt] = _dmems
		def _real_module_name(name):
			return _dotted_module_targets.get(name, name)
		_ck()
		for scope_idx, imported_name, top_name, used_name, lineno in builder.import_names:
			if used_name == top_name:
				if top_name in valid_modules:
					builder.scopes[scope_idx]['names'].setdefault(used_name, []).append((lineno, 'module'))
			elif imported_name in valid_modules or imported_name in _dotted_module_targets:
				builder.scopes[scope_idx]['names'].setdefault(used_name, []).append((lineno, 'module'))
		for _gsn in builder.global_seed_names:
			if not builder.scopes[0]['names'].get(_gsn):
				builder.scopes[0]['names'].setdefault(_gsn, []).append((1, 'var'))
		for _nlp, _nln in builder.nonlocal_seeds:
			_nlbound = False
			_nlcur = _nlp
			while _nlcur is not None:
				if builder.scopes[_nlcur].get('kind') == 'function' and builder.scopes[_nlcur]['names'].get(_nln):
					_nlbound = True
					break
				_nlcur = builder.scopes[_nlcur]['parent']
			if not _nlbound:
				builder.scopes[_nlp]['names'].setdefault(_nln, []).append((builder.scopes[_nlp]['start'], 'var'))
		for scope_idx, module_name, imported_name, _orig_name, lineno in builder.from_imports:
			module_name = _real_module_name(module_name)
			if not module_name or module_name not in valid_modules:
				continue
			contents = module_contents.get(module_name, {})
			if imported_name == '*':
				for _wname, _wkind in contents.items():
					if '.' not in _wname:
						builder.scopes[scope_idx]['names'].setdefault(_wname, []).append((lineno, _wkind))
			else:
				if _orig_name in contents:
					kind = contents[_orig_name]
					if kind == 'module':
						_fmtgt = contents.get('@modtarget:' + _orig_name)
						if _fmtgt is None:
							_fmtgt = f'{module_name}.{_orig_name}'
						if _fmtgt not in valid_modules and self._python_find_spec_cached(_fmtgt) is not None:
							valid_modules.add(_fmtgt)
							_fmmems = self._python_resolve_module_members(_fmtgt)
							if _fmmems:
								module_contents[_fmtgt] = _fmmems
						builder.module_alias_defs.setdefault(imported_name, []).append((lineno, _fmtgt))
						if lineno >= builder.module_alias_lines.get(imported_name, 0):
							builder.module_aliases[imported_name] = _fmtgt
							builder.module_alias_lines[imported_name] = lineno
				elif f'{module_name}.{_orig_name}' in valid_modules or self._python_find_spec_cached(f'{module_name}.{_orig_name}') is not None:
					kind = 'module'
					builder.module_alias_defs.setdefault(imported_name, []).append((lineno, f'{module_name}.{_orig_name}'))
					if lineno >= builder.module_alias_lines.get(imported_name, 0):
						builder.module_aliases[imported_name] = f'{module_name}.{_orig_name}'
						builder.module_alias_lines[imported_name] = lineno
				else:
					continue
				builder.scopes[scope_idx]['names'].setdefault(imported_name, []).append((lineno, kind))
		for _, module_name, imported_name, _orig_name, _fln0 in builder.from_imports:
			module_name = _real_module_name(module_name)
			if not module_name:
				continue
			mc = module_contents.get(module_name, {})
			if imported_name == '*':
				for _wname, _wkind in mc.items():
					if '.' not in _wname and _wkind == 'class':
						if _wname not in local_classes:
							_wmems = self._python_resolve_module_class_members(module_name, _wname)
							if _wmems:
								local_classes[_wname] = _wmems
						if _wname in local_classes:
							class_module_origin.setdefault(_wname, []).append((_fln0, (module_name, _wname)))
			elif mc.get(_orig_name) == 'class':
				if imported_name not in local_classes:
					_imp_mems = self._python_resolve_module_class_members(module_name, _orig_name)
					if _imp_mems:
						local_classes[imported_name] = _imp_mems
				if imported_name in local_classes:
					class_module_origin.setdefault(imported_name, []).append((_fln0, (module_name, _orig_name)))
		base_to_module = {}
		for _, imported_name, top_name, used_name, _iln in builder.import_names:
			if used_name == top_name:
				if top_name in valid_modules:
					base_to_module.setdefault(used_name, []).append((_iln, top_name))
			elif imported_name in valid_modules or imported_name in _dotted_module_targets:
				base_to_module.setdefault(used_name, []).append((_iln, _real_module_name(imported_name)))
			elif top_name in valid_modules:
				base_to_module.setdefault(used_name, []).append((_iln, top_name))
		for _alias, _adefs in builder.module_alias_defs.items():
			for _al, _afull in _adefs:
				if _afull in valid_modules or _afull in _dotted_module_targets:
					base_to_module.setdefault(_alias, []).append((_al, _real_module_name(_afull)))
		def _base_module_at(name, lineno):
			return _line_def_at(base_to_module.get(name), lineno)
		for _dsc, _dln, _dname, _dmod, _dbuiltin in builder.dynamic_imports:
			if _dbuiltin and _call_name_kind('__import__', _dln) is not None:
				continue
			if self._python_find_spec_cached(_dmod) is not None:
				valid_modules.add(_dmod)
				base_to_module.setdefault(_dname, []).append((_dln, _dmod))
				if _dln >= builder.module_alias_lines.get(_dname, 0):
					builder.module_aliases[_dname] = _dmod
					builder.module_alias_lines[_dname] = _dln
				if _dmod not in module_contents:
					_dmems = self._python_resolve_module_members(_dmod)
					if _dmems:
						module_contents[_dmod] = _dmems
						imported_modules.add(_dmod)
				_dnames = builder.scopes[_dsc]['names'].setdefault(_dname, [])
				_dnames[:] = [(_l, _k) for _l, _k in _dnames if not (_l == _dln and _k == 'var')]
				_dnames.append((_dln, 'module'))
		def _resolve_name_kind_scope(scope_idx, name, lineno):
			sidx = scope_idx
			inner = sidx
			while sidx is not None:
				sc = builder.scopes[sidx]
				if sc.get('kind') == 'class' and sidx != inner:
					sidx = sc['parent']
					continue
				if name in sc['names']:
					best = None
					latest = None
					for _dl, _k in sc['names'][name]:
						if latest is None or _dl > latest[0]:
							latest = (_dl, _k)
						if sidx == inner and _dl > lineno:
							continue
						if best is None or _dl > best[0]:
							best = (_dl, _k)
					if best is None and latest is not None and name in _PYTHON_BUILTIN_NAMES:
						return None
					if best is None and latest is not None and _same_block(latest[0], lineno):
						best = latest
					return best[1] if best is not None else None
				sidx = sc['parent']
			return None
		def _pick_scoped_def(defs, lineno, default):
			for _sidx in _def_scope_chain(lineno):
				best = None
				latest = None
				for _d in defs:
					if (_d[2] if len(_d) > 2 else 0) != _sidx:
						continue
					if latest is None or _d[0] > latest[0]:
						latest = _d
					if _d[0] > lineno:
						continue
					if best is None or _d[0] > best[0]:
						best = _d
				if best is None and latest is not None and _same_block(latest[0], lineno):
					best = latest
				if best is not None:
					return best[1]
			return default
		def _func_params_at(name, lineno):
			defs = builder.func_params.get(name)
			if not defs:
				return None
			return _pick_scoped_def(defs, lineno, None)
		def _func_accepts_any_at(name, lineno):
			defs = builder.func_accepts_any.get(name)
			if not defs:
				return False
			return _pick_scoped_def(defs, lineno, False)
		for _asc, _aln, _aname, _asrc in builder.alias_assigns:
			_srckind = _resolve_name_kind_scope(_asc, _asrc, _aln)
			if _srckind is None and _asrc in _PYTHON_BUILTIN_MEMBERS:
				_srckind = 'builtin'
			elif _srckind is None and _asrc in _PYTHON_BUILTIN_NAMES:
				_srckind = 'builtin'
				if _asrc in _PYTHON_BUILTIN_CALLABLE_PARAMS:
					builder.func_params.setdefault(_aname, []).append((_aln, _PYTHON_BUILTIN_CALLABLE_PARAMS[_asrc], _binding_scope_for(_aname, _asc)))
			if _srckind == 'module':
				_asrc_mod = _base_module_at(_asrc, _aln)
				if _asrc_mod is not None:
					_absc = _binding_scope_for(_aname, _asc)
					_anames = builder.scopes[_absc]['names'].setdefault(_aname, [])
					_anames[:] = [(_l, _k) for _l, _k in _anames if not (_l == _aln and _k == 'var')]
					_anames.append((_aln, 'module'))
					base_to_module.setdefault(_aname, []).append((_aln, _asrc_mod))
					builder.module_alias_defs.setdefault(_aname, []).append((_aln, _asrc_mod))
			if _srckind in ('class', 'func', 'builtin'):
				_absc = _binding_scope_for(_aname, _asc)
				_anames = builder.scopes[_absc]['names'].setdefault(_aname, [])
				_anames[:] = [(_l, _k) for _l, _k in _anames if not (_l == _aln and _k == 'var')]
				_anames.append((_aln, _srckind))
				if _srckind in ('func', 'builtin'):
					_src_params = _func_params_at(_asrc, _aln)
					if _src_params is not None:
						builder.func_params.setdefault(_aname, []).append((_aln, _src_params, _absc))
						builder.func_accepts_any.setdefault(_aname, []).append((_aln, _func_accepts_any_at(_asrc, _aln), _absc))
				if _srckind in ('class', 'builtin'):
					_asrc_key = _class_key_at(_asrc, _aln)
					if _asrc_key in local_classes:
						class_def_lines.setdefault(_aname, [])
						if _aln not in class_def_lines[_aname]:
							class_def_lines[_aname].append(_aln)
						class_def_scopes[(_aname, _aln)] = _absc
						_class_first_line.setdefault(_aname, _aln)
						_adst_key = _class_key_at(_aname, _aln)
						if _adst_key not in local_classes:
							local_classes[_adst_key] = local_classes[_asrc_key]
						class_type_maps[_adst_key] = class_type_maps.setdefault(_asrc_key, {})
						_sorig = _class_origin_at(_asrc, _aln)
						if _sorig is not None:
							class_module_origin.setdefault(_aname, []).append((_aln, _sorig))
						for _mk in list(local_class_method_params):
							if _mk.startswith(_asrc_key + '.'):
								_ameth = _mk[len(_asrc_key) + 1:]
								local_class_method_params[_adst_key + '.' + _ameth] = local_class_method_params[_mk]
								if _mk in local_class_accepts_any:
									local_class_accepts_any.add(_adst_key + '.' + _ameth)
		name_module_class = {}
		_attr_alias_func_origins = []
		def _dotted_chain_parts(node):
			attrs = []
			cur = node
			while isinstance(cur, ast.Attribute):
				attrs.append(cur.attr)
				cur = cur.value
			if isinstance(cur, ast.Name):
				attrs.reverse()
				return cur.id, attrs
			return None, None
		def _resolve_local_class_dotted(base, attrs, lineno):
			if not _name_is_class_at(base, lineno):
				return None
			_key = _class_key_at(base, lineno)
			for _i, _attr in enumerate(attrs):
				if local_classes.get(_key, {}).get(_attr) != 'class':
					return None
				_ct = class_attr_types.get(_key, {}).get(_attr)
				if _ct is not None and _ct[0] == 'modclass':
					if _i == len(attrs) - 1:
						return ('class', _ct[1], _ct[2])
					return None
				if _ct is not None and _ct[0] == 'class' and _ct[1] in local_classes:
					_key = _ct[1]
				elif _attr in local_classes:
					_key = _attr
				else:
					return None
				if _i == len(attrs) - 1:
					return ('localclass', _key)
			return None
		def _resolve_dotted_alias(base, attrs, lineno):
			mod = _base_module_at(base, lineno)
			if mod is None:
				return _resolve_local_class_dotted(base, attrs, lineno)
			for _i, _attr in enumerate(attrs):
				_mm = self._python_resolve_module_members(mod)
				_kind = _mm.get(_attr)
				_sub = f'{mod}.{_attr}'
				if _kind is None and (_sub in valid_modules or self._python_find_spec_cached(_sub) is not None):
					_kind = 'module'
				if _kind == 'module':
					_tgt = _mm.get('@modtarget:' + _attr)
					mod = _tgt if _tgt is not None else _sub
					continue
				if _i == len(attrs) - 1 and _kind in ('class', 'func'):
					return (_kind, mod, _attr)
				return None
			return ('module', mod)
		for _cbnode in tree_class_defs:
			if _cbnode.name not in local_classes:
				continue
			_cbkey = _node_class_key(_cbnode)
			for _cbstmt in _flatten_class_body(_cbnode.body):
				_cbtgts = _cbstmt.targets if isinstance(_cbstmt, ast.Assign) else ([_cbstmt.target] if isinstance(_cbstmt, ast.AnnAssign) else [])
				_cbval = _cbstmt.value if isinstance(_cbstmt, (ast.Assign, ast.AnnAssign)) else None
				if isinstance(_cbval, ast.NamedExpr):
					_cbval = _cbval.value
				_cbval = _python_unwrap_descriptor(_cbval)
				if not isinstance(_cbval, ast.Attribute):
					continue
				_cbbase, _cbattrs = _dotted_chain_parts(_cbval)
				if _cbbase is None or not _cbattrs:
					continue
				_cbr = _resolve_dotted_alias(_cbbase, _cbattrs, _cbstmt.lineno)
				if _cbr is None:
					continue
				for _cbtgt in _cbtgts:
					if not isinstance(_cbtgt, ast.Name):
						continue
					if _cbr[0] == 'localclass':
						local_classes[_cbkey][_cbtgt.id] = 'class'
						class_attr_types.setdefault(_cbkey, {})[_cbtgt.id] = ('class', _cbr[1])
					elif _cbr[0] == 'class':
						local_classes[_cbkey][_cbtgt.id] = 'class'
						class_attr_types.setdefault(_cbkey, {})[_cbtgt.id] = ('modclass', _cbr[1], _cbr[2])
					elif _cbr[0] == 'func':
						local_classes[_cbkey][_cbtgt.id] = 'func'
					elif _cbr[0] == 'module':
						local_classes[_cbkey][_cbtgt.id] = 'module'
		for _daa_sc, _daa_ln, _daa_name, _daa_val in builder.dotted_alias_assigns:
			_daa_base, _daa_attrs = _dotted_chain_parts(_daa_val)
			if _daa_base is None or not _daa_attrs:
				continue
			_dr = _resolve_dotted_alias(_daa_base, _daa_attrs, _daa_ln)
			if _dr is None:
				continue
			_akind = _dr[0]
			_absc = _binding_scope_for(_daa_name, _daa_sc)
			_anames = builder.scopes[_absc]['names'].setdefault(_daa_name, [])
			_anames[:] = [(_l, _k) for _l, _k in _anames if not (_l == _daa_ln and _k == 'var')]
			_anames.append((_daa_ln, 'class' if _akind == 'localclass' else _akind))
			if _akind == 'localclass':
				_asrckey = _dr[1]
				class_def_lines.setdefault(_daa_name, [])
				if _daa_ln not in class_def_lines[_daa_name]:
					class_def_lines[_daa_name].append(_daa_ln)
				class_def_scopes[(_daa_name, _daa_ln)] = _absc
				_class_first_line.setdefault(_daa_name, _daa_ln)
				_akey = _class_key_at(_daa_name, _daa_ln)
				if _akey not in local_classes:
					local_classes[_akey] = local_classes[_asrckey]
				for _mk in list(local_class_method_params):
					if _mk.startswith(_asrckey + '.'):
						_ameth = _mk[len(_asrckey) + 1:]
						if _akey + '.' + _ameth not in local_class_method_params:
							local_class_method_params[_akey + '.' + _ameth] = local_class_method_params[_mk]
							if _mk in local_class_accepts_any:
								local_class_accepts_any.add(_akey + '.' + _ameth)
				_sorig2 = _class_origin_at(_asrckey, _daa_ln)
				if _sorig2 is not None:
					class_module_origin.setdefault(_daa_name, []).append((_daa_ln, _sorig2))
			elif _akind == 'class':
				_amod, _aattr = _dr[1], _dr[2]
				name_module_class.setdefault(_daa_name, []).append((_daa_ln, (_amod, _aattr)))
				class_def_lines.setdefault(_daa_name, [])
				if _daa_ln not in class_def_lines[_daa_name]:
					class_def_lines[_daa_name].append(_daa_ln)
				class_def_scopes[(_daa_name, _daa_ln)] = _absc
				_class_first_line.setdefault(_daa_name, _daa_ln)
				_akey = _class_key_at(_daa_name, _daa_ln)
				if _akey not in local_classes:
					_amems = self._python_resolve_module_class_members(_amod, _aattr)
					if _amems:
						local_classes[_akey] = _amems
				class_module_origin.setdefault(_daa_name, []).append((_daa_ln, (_amod, _aattr)))
			elif _akind == 'module':
				_asub = _dr[1]
				valid_modules.add(_asub)
				base_to_module.setdefault(_daa_name, []).append((_daa_ln, _asub))
				builder.module_alias_defs.setdefault(_daa_name, []).append((_daa_ln, _asub))
			elif _akind == 'func':
				_amod, _aattr = _dr[1], _dr[2]
				_attr_alias_func_origins.append((_daa_name, _daa_ln, _amod, _aattr))
		from_func_module = {}
		if seed_func_origins:
			for _sfo_n, _sfo_v in seed_func_origins.items():
				from_func_module.setdefault(_sfo_n, []).append((0, _sfo_v))
		for _, module_name, imported_name, _orig_name, _fln in builder.from_imports:
			module_name = _real_module_name(module_name)
			if module_name and imported_name != '*' and module_name in valid_modules:
				from_func_module.setdefault(imported_name, []).append((_fln, (module_name, _orig_name)))
		for _afo_name, _afo_ln, _afo_mod, _afo_attr in _attr_alias_func_origins:
			from_func_module.setdefault(_afo_name, []).append((_afo_ln, (_afo_mod, _afo_attr)))
		local_def_lines = {}
		for _dln, _dnm, _dk in builder.def_names:
			local_def_lines.setdefault(_dnm, []).append(_dln)
		for _asc, _aln, _aname, _asrc in builder.alias_assigns:
			if _aname in local_classes or _asrc in local_classes:
				local_def_lines.setdefault(_aname, []).append(_aln)
		def _lookup_module_callable(mod_name, key, seen = None):
			if seen is None:
				seen = set()
			if (mod_name, key) in seen:
				return None, None
			seen.add((mod_name, key))
			if mod_name not in valid_modules and self._python_find_spec_cached(mod_name) is None:
				return None, None
			fp = self._python_resolve_module_func_params(mod_name)
			if key in fp:
				v = fp[key]
				if v is None:
					return True, None
				return True, v
			imports = fp.get('@imports', {})
			_head = key.split('.', 1)[0]
			_tail = key[len(_head) + 1:] if '.' in key else None
			if _head in imports and imports[_head][1] is not None:
				_rmod, _rname = imports[_head]
				return _lookup_module_callable(_rmod, _rname if _tail is None else f'{_rname}.{_tail}', seen)
			return None, None
		def _resolve_through_module(mod_name, rest):
			cur_mod = mod_name
			idx = 0
			while idx < len(rest):
				seg = rest[idx]
				sub_full = cur_mod + '.' + seg
				if sub_full in valid_modules or self._python_find_spec_cached(sub_full) is not None:
					cur_mod = sub_full
					idx += 1
					continue
				mems = self._python_resolve_module_members(cur_mod)
				_tgt = mems.get('@modtarget:' + seg)
				if _tgt is not None:
					cur_mod = _tgt
					idx += 1
					continue
				if mems.get(seg) == 'class':
					if idx + 1 < len(rest):
						return _lookup_module_callable(cur_mod, seg + '.' + rest[idx + 1])
					return _lookup_module_callable(cur_mod, seg)
				if idx == len(rest) - 1:
					return _lookup_module_callable(cur_mod, seg)
				return None, None
			return None, None
		def _params_for_dotted(dotted, lineno):
			if not dotted:
				return None, None
			root = dotted[0]
			rest = dotted[1:]
			if len(dotted) == 1:
				kind = _call_name_kind(root, lineno)
				_local_line = None
				for _dl in local_def_lines.get(root, []):
					if _dl <= lineno and (_local_line is None or _dl > _local_line):
						_local_line = _dl
				if _local_line is not None and kind not in ('func', 'class', None):
					_local_line = None
				_imp = None
				_imp_line = None
				for _fl, _fv in from_func_module.get(root, []):
					if _fl <= lineno and (_imp_line is None or _fl >= _imp_line):
						_imp_line = _fl
						_imp = _fv
				if _local_line is not None and (_imp_line is None or _local_line >= _imp_line):
					if kind == 'class' and root in local_classes and root in class_def_lines:
						_ckey = _class_key_at(root, lineno)
						if _ckey + '.__init__' in local_class_accepts_any:
							return True, None
						if _ckey + '.__init__' in local_class_method_params:
							return True, local_class_method_params[_ckey + '.__init__']
						for _lcmo_mod, _lcmo_cls in local_class_module_origins.get(_ckey, []):
							found, mp = self._python_resolve_module_method(_lcmo_mod, _lcmo_cls, '__init__')
							if found:
								return True, mp
						_corig = _class_origin_at(root, lineno)
						if _corig is not None:
							found, mp = self._python_resolve_module_method(_corig[0], _corig[1], '__init__')
							if found:
								return True, mp
						return True, set()
					if kind == 'class' and root in local_classes:
						_ckey = _class_key_at(root, lineno)
						if _ckey + '.__init__' in local_class_accepts_any:
							return True, None
						if _ckey + '.__init__' in local_class_method_params:
							return True, local_class_method_params[_ckey + '.__init__']
						for _lcmo_mod, _lcmo_cls in local_class_module_origins.get(_ckey, []):
							found, mp = self._python_resolve_module_method(_lcmo_mod, _lcmo_cls, '__init__')
							if found:
								return True, mp
						_corig = _class_origin_at(root, lineno)
						if _corig is not None:
							found, mp = self._python_resolve_module_method(_corig[0], _corig[1], '__init__')
							if found:
								return True, mp
					if _func_accepts_any_at(root, lineno):
						return True, None
					return True, _func_params_at(root, lineno) or set()
				if _imp_line is not None and kind in ('func', 'class', 'module', None):
					return _lookup_module_callable(_imp[0], _imp[1])
				if kind is None and root in _PYTHON_BUILTIN_CALLABLE_NAMES:
					return True, _PYTHON_BUILTIN_CALLABLE_PARAMS.get(root, set())
				if kind in ('func', 'builtin') and root in builder.func_params:
					if _func_accepts_any_at(root, lineno):
						return True, None
					return True, _func_params_at(root, lineno) or set()
				if kind == 'class' and root in local_classes:
					_ckey = _class_key_at(root, lineno)
					if _ckey + '.__init__' in local_class_accepts_any:
						return True, None
					if _ckey + '.__init__' in local_class_method_params:
						return True, local_class_method_params[_ckey + '.__init__']
					for _lcmo_mod, _lcmo_cls in local_class_module_origins.get(_ckey, []):
						found, mp = self._python_resolve_module_method(_lcmo_mod, _lcmo_cls, '__init__')
						if found:
							return True, mp
					_corig = _class_origin_at(root, lineno)
					if _corig is not None:
						found, mp = self._python_resolve_module_method(_corig[0], _corig[1], '__init__')
						if found:
							return True, mp
				return None, None
			if len(rest) == 1 and _name_is_class_at(root, lineno):
				_ckey = _class_key_at(root, lineno)
				if local_classes.get(_ckey, {}).get(rest[0]) == 'class':
					_cat = class_attr_types.get(_ckey, {}).get(rest[0])
					if _cat is None and rest[0] in local_classes:
						_cat = ('class', rest[0])
					if _cat is not None and _cat[0] == 'class' and _cat[1] in local_classes:
						_tkey = _cat[1]
						if _tkey + '.__init__' in local_class_accepts_any:
							return True, None
						if _tkey + '.__init__' in local_class_method_params:
							return True, local_class_method_params[_tkey + '.__init__']
						for _lcmo_mod, _lcmo_cls in local_class_module_origins.get(_tkey, []):
							found, mp = self._python_resolve_module_method(_lcmo_mod, _lcmo_cls, '__init__')
							if found:
								return True, mp
						_torig = _class_origin_at(_tkey, lineno)
						if _torig is not None:
							found, mp = self._python_resolve_module_method(_torig[0], _torig[1], '__init__')
							if found:
								return True, mp
						return True, set()
					if _cat is not None and _cat[0] == 'modclass':
						found, mp = self._python_resolve_module_method(_cat[1], _cat[2], '__init__')
						if found:
							return True, mp
				_mkey = _ckey + '.' + rest[0]
				if _instance_only_attr(_ckey, rest[0]):
					return None, None
				if _mkey in local_class_accepts_any:
					return True, None
				if _mkey in local_class_method_params:
					return True, local_class_method_params[_mkey]
				for _lcmo_mod, _lcmo_cls in local_class_module_origins.get(_ckey, []):
					found, mp = self._python_resolve_module_method(_lcmo_mod, _lcmo_cls, rest[0])
					if found:
						return True, mp
			if _call_name_kind(root, lineno) in ('module', None):
				_rmod = _base_module_at(root, lineno)
				if _rmod is not None:
					return _resolve_through_module(_rmod, rest)
			return None, None
		_ck()
		module_literals = []
		for _ifn in tree_importfroms:
			if _ifn.module and '.' not in _ifn.module and _ifn.module in valid_modules:
				module_literals.append((_ifn.lineno, _ifn.col_offset + 5 + _ifn.level, _ifn.module))
		for _imn in tree_imports:
			for _ial in _imn.names:
				if _ial.asname and '.' not in _ial.name and _ial.name in valid_modules:
					module_literals.append((_ial.lineno, _ial.col_offset, _ial.name))
		import_dotted_lines = [(lineno, col, dotted) for lineno, col, dotted in builder.import_dotted_lines if dotted in valid_modules or dotted in _dotted_module_targets or self._python_find_spec_cached(dotted) is not None]
		import_orig_name_tags = []
		_kind_to_tag = {'func': 'hpf', 'class': 'hpx', 'var': 'hpv', 'module': 'hpm'}
		for _oln, _ocol, _oname, _omod in builder.import_orig_names:
			_omod = _real_module_name(_omod)
			if not _omod or _omod not in valid_modules:
				continue
			_okind = None
			if f'{_omod}.{_oname}' in valid_modules or self._python_find_spec_cached(f'{_omod}.{_oname}') is not None:
				_okind = 'module'
			else:
				_ocontents = module_contents.get(_omod) or self._python_resolve_module_members(_omod)
				_okind = _ocontents.get(_oname)
			_otag = _kind_to_tag.get(_okind)
			if _otag is not None:
				import_orig_name_tags.append((_oln, _ocol, _oname, _otag))
		_from_import_map = {}
		for _, module_name, imported_name, _orig_name, _fln in builder.from_imports:
			module_name = _real_module_name(module_name)
			if module_name and imported_name != '*':
				_from_import_map.setdefault(imported_name, []).append((_fln, module_name))
		_ck()
		scope_var_types = {}
		if seed_types:
			for _stn, _stt in seed_types.items():
				if _stt in local_classes:
					scope_var_types.setdefault(0, {}).setdefault(_stn, []).append((0, _stt))
		_var_type_alias_assigns = []
		container_elem_types = {}
		def _elem_type_name(v, lineno):
			if isinstance(v, ast.Call) and isinstance(v.func, ast.Name):
				_en = v.func.id
				if _en in local_classes and _name_is_class_at(_en, lineno):
					return _class_key_at(_en, lineno)
				if _class_origin_at(_en, lineno) is not None:
					return _en
			if isinstance(v, ast.Call) and isinstance(v.func, ast.Attribute) and isinstance(v.func.value, ast.Name):
				_emod = _base_module_at(v.func.value.id, lineno)
				if _emod is not None and self._python_resolve_module_members(_emod).get(v.func.attr) == 'class':
					class_module_origin.setdefault(v.func.attr, []).append((lineno, (_emod, v.func.attr)))
					return v.func.attr
			return None
		for node in tree_assigns:
			for tgt, val in _assign_pairs(node.targets, node.value):
				if not isinstance(tgt, ast.Name) or val is None:
					continue
				type_name = None
				if isinstance(val, ast.Call):
					func = val.func
					mod_name = None
					if isinstance(func, ast.Name):
						type_name = func.id
						mod_name = _line_def_at(_from_import_map.get(type_name), node.lineno)
					elif isinstance(func, ast.Attribute):
						type_name = func.attr
						mod_name = _base_module_at(func.value.id, node.lineno) if isinstance(func.value, ast.Name) else None
					if type_name and type_name not in local_classes and mod_name:
						if self._python_resolve_module_members(mod_name).get(type_name) == 'class':
							class_module_origin.setdefault(type_name, []).append((node.lineno, (mod_name, type_name)))
				elif isinstance(val, ast.Constant):
					type_name = type(val.value).__name__
				elif isinstance(val, ast.List):
					type_name = 'list'
				elif isinstance(val, ast.Dict):
					type_name = 'dict'
				elif isinstance(val, ast.Tuple):
					type_name = 'tuple'
				elif isinstance(val, ast.Set):
					type_name = 'set'
				elif isinstance(val, ast.JoinedStr):
					type_name = 'str'
				elif isinstance(val, ast.Name):
					_var_type_alias_assigns.append((node.lineno, tgt.id, val.id))
				if isinstance(val, ast.Call) and isinstance(val.func, ast.Name) and type_name and type_name in local_classes and not _name_is_class_at(type_name, node.lineno):
					type_name = None
				if isinstance(val, ast.Call) and isinstance(val.func, ast.Name) and type_name and type_name in local_classes:
					type_name = _class_key_at(type_name, node.lineno)
				if type_name and (type_name in local_classes or _class_origin_at(type_name, node.lineno) is not None or (type_name in _PYTHON_BUILTIN_MEMBERS and type_name not in local_classes)):
					sc_idx = _binding_scope_for(tgt.id, _scope_for_line(node.lineno))
					if sc_idx is not None:
						scope_var_types.setdefault(sc_idx, {}).setdefault(tgt.id, []).append((node.lineno, type_name))
				elif not isinstance(val, ast.Name):
					sc_idx = _binding_scope_for(tgt.id, _scope_for_line(node.lineno))
					if sc_idx is not None:
						scope_var_types.setdefault(sc_idx, {}).setdefault(tgt.id, []).append((node.lineno, None))
				_cet_elts = None
				if isinstance(val, (ast.List, ast.Tuple, ast.Set)):
					_cet_elts = val.elts
				elif isinstance(val, ast.Dict):
					_cet_elts = [_dv for _dv in val.values if _dv is not None]
				if _cet_elts:
					_cet_name = None
					_cet_ok = True
					for _cet_el in _cet_elts:
						_cet_t = _elem_type_name(_cet_el, node.lineno)
						if _cet_t is None or (_cet_name is not None and _cet_t != _cet_name):
							_cet_ok = False
							break
						_cet_name = _cet_t
					if _cet_ok and _cet_name is not None and (_cet_name in local_classes or _class_origin_at(_cet_name, node.lineno) is not None):
						_cet_sc = _binding_scope_for(tgt.id, _scope_for_line(node.lineno))
						if _cet_sc is not None:
							container_elem_types.setdefault(_cet_sc, {}).setdefault(tgt.id, []).append((node.lineno, _cet_name))
		for _fn in ast.walk(tree):
			if not isinstance(_fn, (ast.For, ast.AsyncFor)) or not isinstance(_fn.target, ast.Name):
				continue
			_fit = None
			if isinstance(_fn.iter, ast.Name):
				_fsc0 = _binding_scope_for(_fn.iter.id, _scope_for_line(_fn.lineno))
				_fcands = container_elem_types.get(_fsc0, {}).get(_fn.iter.id) if _fsc0 is not None else None
				if _fcands:
					_fb = None
					for _fdl, _ftn in _fcands:
						if _fdl <= _fn.lineno and (_fb is None or _fdl > _fb[0]):
							_fb = (_fdl, _ftn)
					if _fb is not None:
						_fit = _fb[1]
			elif isinstance(_fn.iter, (ast.List, ast.Tuple, ast.Set)):
				_fname = None
				_fok = True
				for _fel in _fn.iter.elts:
					_ft = _elem_type_name(_fel, _fn.lineno)
					if _ft is None or (_fname is not None and _ft != _fname):
						_fok = False
						break
					_fname = _ft
				if _fok:
					_fit = _fname
			if _fit is not None and (_fit in local_classes or _class_origin_at(_fit, _fn.lineno) is not None):
				_ftsc = _binding_scope_for(_fn.target.id, _scope_for_line(_fn.lineno))
				if _ftsc is not None:
					scope_var_types.setdefault(_ftsc, {}).setdefault(_fn.target.id, []).append((_fn.lineno, _fit))
		for _valn, _vatgt, _vasrc in sorted(_var_type_alias_assigns):
			_vsc = _scope_for_line(_valn)
			_scur = _vsc
			_vtype = None
			_vfound = False
			while _scur is not None and not _vfound:
				_svt = scope_var_types.get(_scur, {}).get(_vasrc)
				if _svt:
					_vb = None
					for _vdl, _vtn in _svt:
						if _scur == _vsc and _vdl > _valn:
							continue
						if _vb is None or _vdl > _vb[0]:
							_vb = (_vdl, _vtn)
					if _vb is not None:
						_vtype = _vb[1]
						_vfound = True
				_scur = builder.scopes[_scur]['parent']
			_vtsc = _binding_scope_for(_vatgt, _vsc)
			if _vtsc is not None:
				scope_var_types.setdefault(_vtsc, {}).setdefault(_vatgt, []).append((_valn, _vtype))
		_ck()
		for cls_node in tree_class_defs:
			for meth in cls_node.body:
				if not isinstance(meth, (ast.FunctionDef, ast.AsyncFunctionDef)):
					continue
				_fp = meth.args.args[0].arg if (meth.args.args and _python_method_has_implicit_first_param(meth)) else None
				if not _fp:
					continue
				for stmt in ast.walk(meth):
					if not isinstance(stmt, ast.Assign):
						continue
					for tgt, val in _assign_pairs(stmt.targets, stmt.value):
						if not (isinstance(tgt, ast.Attribute) and isinstance(tgt.value, ast.Name) and tgt.value.id == _fp) or val is None:
							continue
						_self_assigned_attrs.setdefault(_node_class_key(cls_node), set()).add(tgt.attr)
						type_name = None
						if isinstance(val, ast.Call):
							func = val.func
							mod_name = None
							if isinstance(func, ast.Name):
								type_name = func.id
								mod_name = _line_def_at(_from_import_map.get(type_name), stmt.lineno)
								if mod_name is None and not _name_is_class_at(type_name, stmt.lineno):
									type_name = None
							elif isinstance(func, ast.Attribute):
								type_name = func.attr
								mod_name = _base_module_at(func.value.id, stmt.lineno) if isinstance(func.value, ast.Name) else None
							if type_name and type_name not in local_classes and mod_name:
								mems = self._python_resolve_module_class_members(mod_name, type_name)
								if mems:
									local_classes[type_name] = mems
									class_module_origin.setdefault(type_name, []).append((stmt.lineno, (mod_name, type_name)))
						elif isinstance(val, ast.Constant):
							type_name = type(val.value).__name__
						elif isinstance(val, ast.List):
							type_name = 'list'
						elif isinstance(val, ast.Dict):
							type_name = 'dict'
						elif isinstance(val, ast.Tuple):
							type_name = 'tuple'
						elif isinstance(val, ast.Set):
							type_name = 'set'
						elif isinstance(val, ast.JoinedStr):
							type_name = 'str'
						if type_name and type_name in local_classes:
							if isinstance(val, ast.Call) and isinstance(val.func, ast.Name):
								type_name = _class_key_at(type_name, stmt.lineno)
							class_type_maps.setdefault(_node_class_key(cls_node), {})[tgt.attr] = type_name
						else:
							class_type_maps.get(_node_class_key(cls_node), {}).pop(tgt.attr, None)
		for cls_node in tree_class_defs:
			if cls_node.name not in local_classes:
				continue
			for stmt in cls_node.body:
				if not isinstance(stmt, ast.Assign):
					continue
				val = stmt.value
				type_name = None
				if isinstance(val, ast.Call):
					func = val.func
					if isinstance(func, ast.Name):
						type_name = func.id
					elif isinstance(func, ast.Attribute):
						type_name = func.attr
				elif isinstance(val, ast.Constant):
					type_name = type(val.value).__name__
				elif isinstance(val, ast.List):
					type_name = 'list'
				elif isinstance(val, ast.Dict):
					type_name = 'dict'
				elif isinstance(val, ast.Tuple):
					type_name = 'tuple'
				elif isinstance(val, ast.Set):
					type_name = 'set'
				elif isinstance(val, ast.JoinedStr):
					type_name = 'str'
				if type_name and type_name in local_classes:
					if isinstance(val, ast.Call) and isinstance(val.func, ast.Name):
						type_name = _class_key_at(type_name, stmt.lineno)
					for tgt in stmt.targets:
						if isinstance(tgt, ast.Name) and tgt.id not in _self_assigned_attrs.get(_node_class_key(cls_node), ()):
							class_type_maps.setdefault(_node_class_key(cls_node), {})[tgt.id] = type_name
		for _saa_cls, _saa_names in _self_assigned_attrs.items():
			for _saa_name in _saa_names:
				if local_classes.get(_saa_cls, {}).get(_saa_name) != 'var':
					continue
				_saa_key = _saa_cls + '.' + _saa_name
				local_class_method_params.pop(_saa_key, None)
				local_class_accepts_any.discard(_saa_key)
		_ck()
		_ck()
		method_fp_ranges = []
		for _cnode in tree_class_defs:
			if _cnode.name in local_classes:
				_cnk = _node_class_key(_cnode)
				for _meth in _cnode.body:
					if isinstance(_meth, (ast.FunctionDef, ast.AsyncFunctionDef)) and _meth.args.args and _python_method_has_implicit_first_param(_meth):
						method_fp_ranges.append((_meth.lineno, getattr(_meth, 'end_lineno', _meth.lineno), _meth.args.args[0].arg, _cnk))
		def _fp_class_at(name, lineno):
			best = None
			for ms, me, fp, cn in method_fp_ranges:
				if ms <= lineno <= me and name == fp and (best is None or ms > best[0]):
					best = (ms, cn)
			return best[1] if best else None
		def _var_type_at(name, lineno, col = None):
			sidx = _scope_for_line(lineno) if col is None else _scope_for_pos(lineno, col)
			inner = sidx
			while sidx is not None:
				sc = builder.scopes[sidx]
				if sc.get('kind') == 'class' and sidx != inner:
					sidx = sc['parent']
					continue
				if name in sc['names']:
					svt = scope_var_types.get(sidx, {})
					if name in svt:
						best = None
						for dl, tn in svt[name]:
							if sidx == inner and dl > lineno:
								continue
							if best is None or dl > best[0]:
								best = (dl, tn)
						if best is not None:
							return best[1]
					return None
				sidx = sc['parent']
			return None
		def _assign_type_name(val, lineno):
			if isinstance(val, ast.Call):
				func = val.func
				if isinstance(func, ast.Name):
					return func.id if _name_is_class_at(func.id, lineno) else None
				if isinstance(func, ast.Attribute):
					return func.attr if func.attr in local_classes else None
				return None
			if isinstance(val, ast.Constant):
				return type(val.value).__name__
			if isinstance(val, ast.List):
				return 'list'
			if isinstance(val, ast.Dict):
				return 'dict'
			if isinstance(val, ast.Tuple):
				return 'tuple'
			if isinstance(val, ast.Set):
				return 'set'
			if isinstance(val, ast.JoinedStr):
				return 'str'
			if isinstance(val, ast.Name) and _name_is_class_at(val.id, lineno):
				return _class_key_at(val.id, lineno)
			return None
		def _literal_type(node):
			if isinstance(node, ast.Constant):
				return type(node.value).__name__
			if isinstance(node, ast.JoinedStr):
				return 'str'
			if isinstance(node, ast.List):
				return 'list'
			if isinstance(node, ast.Dict):
				return 'dict'
			if isinstance(node, ast.Tuple):
				return 'tuple'
			if isinstance(node, ast.Set):
				return 'set'
			return None
		def _module_attr_kind(mod, attr):
			_mm = self._python_resolve_module_members(mod)
			_k = _mm.get(attr)
			if _k is not None:
				return _k
			_dk = dynamic_module_attrs.get(mod, {}).get(attr)
			if _dk is not None:
				return _dk
			_sub = f'{mod}.{attr}'
			if _sub in valid_modules:
				return 'module'
			_spec = self._python_find_spec_cached(mod)
			if _spec is not None and getattr(_spec, 'submodule_search_locations', None) and self._python_find_spec_cached(_sub) is not None:
				return 'module'
			return None
		def _assign_value_kind(val, lineno):
			if val is None:
				return None
			val = _python_unwrap_descriptor(val)
			if isinstance(val, ast.Lambda):
				return 'func'
			if isinstance(val, ast.Call) and builder._dynamic_import_module(val) is not None:
				return 'module'
			if isinstance(val, ast.Name):
				_vk = _call_name_kind(val.id, lineno)
				if _vk in ('func', 'class', 'module'):
					return _vk
				if _vk is None and val.id in _PYTHON_BUILTIN_MEMBERS:
					return 'class'
				if _vk is None and val.id in _PYTHON_BUILTIN_CALLABLE_NAMES:
					return 'func'
				return None
			if isinstance(val, ast.Attribute) and isinstance(val.value, ast.Name):
				_vfpc = _fp_class_at(val.value.id, lineno)
				if _vfpc is not None:
					_vfk = local_classes.get(_vfpc, {}).get(val.attr)
					if _vfk in ('func', 'class', 'module'):
						return _vfk
				if _name_is_class_at(val.value.id, lineno):
					_vck = _class_key_at(val.value.id, lineno)
					_vckk = local_classes.get(_vck, {}).get(val.attr)
					if _vckk in ('func', 'class', 'module'):
						return _vckk
				if _call_name_kind(val.value.id, lineno) in ('module', None):
					_vmod = _base_module_at(val.value.id, lineno)
					if _vmod is not None:
						_vak = _module_attr_kind(_vmod, val.attr)
						if _vak in ('func', 'class', 'module'):
							return _vak
			return None
		def _value_type(val, lineno):
			val = _python_unwrap_descriptor(val)
			_blt = _literal_type(val)
			if _blt is not None and _blt in _PYTHON_BUILTIN_MEMBERS:
				return ('builtin', _blt)
			if isinstance(val, ast.Call):
				_dr = builder._dynamic_import_module(val)
				if _dr is not None:
					return ('module', _dr[0])
				_ft = _value_type(val.func, lineno)
				if _ft is not None:
					if _ft[0] == 'class':
						return ('instance', _ft[1])
					if _ft[0] == 'modclass':
						return ('minstance', _ft[1], _ft[2])
				return None
			if isinstance(val, ast.Name):
				_vo = _class_origin_at(val.id, lineno)
				if _vo is not None and _call_name_kind(val.id, lineno) in (None, 'class'):
					return ('modclass', _vo[0], _vo[1])
				if val.id in local_classes and _call_name_kind(val.id, lineno) in (None, 'class'):
					return ('class', _class_key_at(val.id, lineno))
				if _call_name_kind(val.id, lineno) == 'module':
					_vm = _base_module_at(val.id, lineno)
					if _vm is not None:
						return ('module', _vm)
				_vvt = _var_type_at(val.id, lineno)
				if _vvt is not None:
					if _vvt in _PYTHON_BUILTIN_MEMBERS and _vvt not in local_classes:
						return ('builtin', _vvt)
					_vvo = _class_origin_at(_vvt, lineno)
					if _vvo is not None and _vvt not in local_classes:
						return ('minstance', _vvo[0], _vvo[1])
					if _vvt in local_classes:
						return ('instance', _vvt)
				return None
			if isinstance(val, ast.Attribute) and isinstance(val.value, ast.Name):
				if _call_name_kind(val.value.id, lineno) in ('module', None):
					_vm = _base_module_at(val.value.id, lineno)
					if _vm is not None:
						_vmk = _module_attr_kind(_vm, val.attr)
						if _vmk == 'class':
							return ('modclass', _vm, val.attr)
						if _vmk == 'module':
							_vtgt = self._python_resolve_module_members(_vm).get('@modtarget:' + val.attr)
							return ('module', _vtgt if _vtgt is not None else f'{_vm}.{val.attr}')
				return None
			return None
		for _ccnode in tree_class_defs:
			if _ccnode.name not in local_classes:
				continue
			for _cstmt in _flatten_class_body(_ccnode.body):
				_ctgts = _cstmt.targets if isinstance(_cstmt, ast.Assign) else ([_cstmt.target] if isinstance(_cstmt, ast.AnnAssign) else [])
				for _ctgt, _cval in _assign_pairs(_ctgts, _cstmt.value if _ctgts else None):
					if isinstance(_cval, ast.NamedExpr):
						_cval = _cval.value
					_cval = _python_unwrap_descriptor(_cval)
					if not isinstance(_ctgt, ast.Name) or _cval is None:
						continue
					if _ctgt.id in _self_assigned_attrs.get(_node_class_key(_ccnode), ()):
						continue
					_cvt = _value_type(_cval, _cstmt.lineno)
					if _cvt is not None:
						class_attr_types.setdefault(_node_class_key(_ccnode), {})[_ctgt.id] = _cvt
						if _cvt[0] in ('modclass', 'class'):
							local_classes[_node_class_key(_ccnode)][_ctgt.id] = 'class'
		for _ucnode in tree_class_defs:
			if _ucnode.name not in local_classes:
				continue
			for _umeth in _ucnode.body:
				if not isinstance(_umeth, (ast.FunctionDef, ast.AsyncFunctionDef)) or not _umeth.args.args or not _python_method_has_implicit_first_param(_umeth):
					continue
				_ufp = _umeth.args.args[0].arg
				for _ustmt in ast.walk(_umeth):
					_utgts = _ustmt.targets if isinstance(_ustmt, ast.Assign) else ([_ustmt.target] if isinstance(_ustmt, ast.AnnAssign) else [])
					for _utgt, _uval in _assign_pairs(_utgts, _ustmt.value if _utgts else None):
						if not (isinstance(_utgt, ast.Attribute) and isinstance(_utgt.value, ast.Name) and _utgt.value.id == _ufp):
							continue
						_ukind = _assign_value_kind(_uval, _ustmt.lineno)
						_unk = _node_class_key(_ucnode)
						if _ukind is not None and local_classes[_unk].get(_utgt.attr) == 'var':
							local_classes[_unk][_utgt.attr] = _ukind
						_uvt = _value_type(_uval, _ustmt.lineno) if _uval is not None else None
						if _uvt is not None:
							class_attr_types.setdefault(_unk, {})[_utgt.attr] = _uvt
		def _elem_type_at(name, lineno):
			sidx = _scope_for_line(lineno)
			inner = sidx
			while sidx is not None:
				sc = builder.scopes[sidx]
				if sc.get('kind') == 'class' and sidx != inner:
					sidx = sc['parent']
					continue
				_cet = container_elem_types.get(sidx, {}).get(name)
				if _cet:
					_cb = None
					for _cdl, _ctn in _cet:
						if sidx == inner and _cdl > lineno:
							continue
						if _cb is None or _cdl > _cb[0]:
							_cb = (_cdl, _ctn)
					if _cb is not None:
						return _cb[1]
				sidx = sc['parent']
			return None
		def _infer_type(node):
			if isinstance(node, ast.NamedExpr):
				return _infer_type(node.value)
			if isinstance(node, ast.Subscript) and isinstance(node.value, ast.Name):
				_st = _elem_type_at(node.value.id, node.lineno)
				if _st is not None:
					_sorig3 = _class_origin_at(_st, node.lineno)
					if _sorig3 is not None and _st not in local_classes:
						return ('minstance', _sorig3[0], _sorig3[1])
					return ('instance', _st)
			if isinstance(node, ast.Name):
				vt = _var_type_at(node.id, node.lineno)
				if vt is not None:
					if vt in _PYTHON_BUILTIN_MEMBERS and vt not in local_classes:
						return ('builtin', vt)
					_vorig = _class_origin_at(vt, node.lineno)
					if _vorig is not None and vt not in local_classes:
						return ('minstance', _vorig[0], _vorig[1])
					return ('instance', vt)
				fpc = _fp_class_at(node.id, node.lineno)
				if fpc is not None:
					return ('instance', fpc)
				_norig = _class_origin_at(node.id, node.lineno)
				if _norig is not None and _call_name_kind(node.id, node.lineno) == 'class':
					return ('modclass', _norig[0], _norig[1])
				if _name_is_class_at(node.id, node.lineno):
					return ('class', _class_key_at(node.id, node.lineno))
				if _call_name_kind(node.id, node.lineno) == 'module':
					_nmod = _base_module_at(node.id, node.lineno)
					if _nmod is not None:
						return ('module', _nmod)
				return None
			_lt = _literal_type(node)
			if _lt is not None and _lt in local_classes:
				return ('instance', _lt)
			if isinstance(node, ast.Call):
				if isinstance(node.func, ast.Name) and node.func.id == '__import__' and _call_name_kind('__import__', node.lineno) is None and node.args and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
					if node.args[0].value in valid_modules or self._python_find_spec_cached(node.args[0].value) is not None:
						if _python_import_fromlist_is_nonempty(node):
							return ('module', node.args[0].value)
						return ('module', node.args[0].value.split('.')[0])
				if isinstance(node.func, ast.Attribute) and node.func.attr == 'import_module' and node.args and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
					if node.args[0].value in valid_modules or self._python_find_spec_cached(node.args[0].value) is not None:
						return ('module', node.args[0].value)
				if isinstance(node.func, ast.Name) and node.func.id == 'super' and _call_name_kind('super', node.lineno) is None:
					_sbest = None
					for _ms, _me, _mfp, _mcls in method_fp_ranges:
						if _ms <= node.lineno <= _me and (_sbest is None or _ms > _sbest[0]):
							_sbest = (_ms, _mcls)
					if _sbest is not None:
						return ('instance', _sbest[1])
				rf = _infer_type(node.func)
				if rf is not None and rf[0] == 'class':
					return ('instance', rf[1])
				if rf is not None and rf[0] == 'modclass':
					return ('minstance', rf[1], rf[2])
				if isinstance(node.func, ast.Attribute):
					br = _infer_type(node.func.value)
					if br is not None and br[0] in ('instance', 'class'):
						rt = class_type_maps.get(br[1], {}).get(node.func.attr)
						if rt is None:
							rt = _PYTHON_BUILTIN_METHOD_RETURNS.get(br[1], {}).get(node.func.attr)
						if rt is not None and rt in local_classes:
							return ('instance', rt)
				return None
			if isinstance(node, ast.Attribute):
				r = _infer_type(node.value)
				if r is None:
					return None
				if r[0] == 'instance' and isinstance(node.value, ast.Name) and _fp_class_at(node.value.id, node.lineno) != r[1]:
					_vasc = _binding_scope_for(node.value.id, _scope_for_line(node.lineno))
					if _vasc is not None:
						_vfound, _vtype = _var_attr_type_at(_vasc, node.value.id, node.attr, node.lineno)
						if _vfound:
							return _vtype
				if r[0] == 'module':
					_mk = _module_attr_kind(r[1], node.attr)
					if _mk == 'module':
						_tgt = self._python_resolve_module_members(r[1]).get('@modtarget:' + node.attr)
						return ('module', _tgt if _tgt is not None else f'{r[1]}.{node.attr}')
					if _mk == 'class':
						_dmc = dynamic_module_attr_types.get(r[1], {}).get(node.attr)
						if _dmc is not None and _dmc in local_classes:
							return ('class', _dmc)
						return ('modclass', r[1], node.attr)
					_dmt = dynamic_module_attr_types.get(r[1], {}).get(node.attr)
					if _dmt is not None and _dmt in local_classes:
						return ('instance', _dmt)
					return None
				if r[0] in ('modclass', 'minstance'):
					_cat = class_attr_types.get(r[2], {}).get(node.attr)
					if _cat is not None:
						return _cat
					_dt = dynamic_class_attr_types.get(r[2], {}).get(node.attr)
					if _dt is None and r[0] == 'modclass':
						_dt = dynamic_modclass_attr_types.get(r[2], {}).get(node.attr)
					if _dt is not None and _dt in local_classes:
						return ('instance', _dt)
					return None
				if r[0] == 'class' and _instance_only_attr(r[1], node.attr):
					return None
				members = local_classes.get(r[1], {})
				_cat = class_attr_types.get(r[1], {}).get(node.attr)
				if _cat is not None:
					return _cat
				if r[0] == 'instance':
					_dt = dynamic_class_attr_types.get(r[1], {}).get(node.attr)
					if _dt is not None and _dt in local_classes:
						return ('instance', _dt)
				if node.attr not in members:
					return None
				tt = class_type_maps.get(r[1], {}).get(node.attr)
				if tt is not None and tt in local_classes:
					return ('instance', tt)
				if members[node.attr] == 'class' and node.attr in local_classes:
					return ('class', node.attr)
				return None
			return None
		for _an in sorted(tree_assigns, key = lambda _n: (_n.lineno, _n.col_offset)):
			for _atgt, _aval in _assign_pairs(_an.targets, _an.value):
				if not isinstance(_atgt, ast.Attribute):
					continue
				_atn = _assign_type_name(_aval, _an.lineno) if _aval is not None else None
				_adkind = _assign_value_kind(_aval, _an.lineno) or 'var'
				if isinstance(_atgt.value, ast.Name) and _call_name_kind(_atgt.value.id, _an.lineno) == 'class' and _atgt.value.id in local_classes and _class_origin_at(_atgt.value.id, _an.lineno) is None:
					local_classes[_atgt.value.id][_atgt.attr] = _adkind
					if _adkind == 'class':
						_avr = _infer_type(_aval) if _aval is not None else None
						if _avr is not None and _avr[0] in ('class', 'modclass'):
							class_attr_types.setdefault(_atgt.value.id, {})[_atgt.attr] = _avr
					if _atn is not None and _atn in local_classes:
						class_type_maps.setdefault(_atgt.value.id, {})[_atgt.attr] = _atn
					continue
				_br = _infer_type(_atgt.value)
				if _br is None:
					continue
				if _br[0] == 'module':
					dynamic_module_attrs.setdefault(_br[1], {})[_atgt.attr] = _adkind
					if _atn is not None and _atn in local_classes:
						dynamic_module_attr_types.setdefault(_br[1], {})[_atgt.attr] = _atn
				elif _br[0] == 'modclass':
					dynamic_modclass_attrs.setdefault(_br[2], {})[_atgt.attr] = _adkind
					if _atn is not None and _atn in local_classes:
						dynamic_modclass_attr_types.setdefault(_br[2], {})[_atgt.attr] = _atn
				elif _br[0] == 'minstance':
					dynamic_class_attrs.setdefault(_br[2], {})[_atgt.attr] = _adkind
					if _atn is not None and _atn in local_classes:
						dynamic_class_attr_types.setdefault(_br[2], {})[_atgt.attr] = _atn
				elif _br[0] == 'class' and _class_origin_at(_br[1], _an.lineno) is not None:
					_ocls = _class_origin_at(_br[1], _an.lineno)[1]
					dynamic_modclass_attrs.setdefault(_ocls, {})[_atgt.attr] = _adkind
					if _atn is not None and _atn in local_classes:
						dynamic_modclass_attr_types.setdefault(_ocls, {})[_atgt.attr] = _atn
				elif _br[0] == 'class' and _br[1] in local_classes:
					local_classes[_br[1]][_atgt.attr] = _adkind
					_direct_attr_assigns.add((_br[1], _atgt.attr))
					_avt = _value_type(_aval, _an.lineno) if _aval is not None else None
					if _avt is not None:
						class_attr_types.setdefault(_br[1], {})[_atgt.attr] = _avt
						class_type_maps.get(_br[1], {}).pop(_atgt.attr, None)
					elif _atn is not None and _atn in local_classes:
						class_type_maps.setdefault(_br[1], {})[_atgt.attr] = _atn
						class_attr_types.get(_br[1], {}).pop(_atgt.attr, None)
					else:
						class_attr_types.get(_br[1], {}).pop(_atgt.attr, None)
						class_type_maps.get(_br[1], {}).pop(_atgt.attr, None)
				elif _br[0] == 'instance' and _br[1] in local_classes:
					dynamic_class_attrs.setdefault(_br[1], {})[_atgt.attr] = _adkind
					_avt = _value_type(_aval, _an.lineno) if _aval is not None else None
					_is_self_attr = not isinstance(_atgt.value, ast.Name) or _fp_class_at(_atgt.value.id, _an.lineno) == _br[1]
					if not _is_self_attr:
						_vasc = _binding_scope_for(_atgt.value.id, _scope_for_line(_an.lineno))
						if _vasc is not None:
							if _avt is not None:
								_vaval = _avt
							elif _atn is not None and _atn in local_classes:
								_vaval = ('instance', _atn)
							else:
								_vaval = None
							var_attr_types.setdefault((_vasc, _atgt.value.id), {}).setdefault(_atgt.attr, []).append((_an.lineno, _vaval))
					elif _avt is not None:
						class_attr_types.setdefault(_br[1], {})[_atgt.attr] = _avt
						dynamic_class_attr_types.get(_br[1], {}).pop(_atgt.attr, None)
						class_type_maps.get(_br[1], {}).pop(_atgt.attr, None)
						_direct_attr_assigns.add((_br[1], _atgt.attr))
					elif _atn is not None and _atn in local_classes:
						dynamic_class_attr_types.setdefault(_br[1], {})[_atgt.attr] = _atn
						class_attr_types.get(_br[1], {}).pop(_atgt.attr, None)
						class_type_maps.get(_br[1], {}).pop(_atgt.attr, None)
						_direct_attr_assigns.add((_br[1], _atgt.attr))
					else:
						class_attr_types.get(_br[1], {}).pop(_atgt.attr, None)
						dynamic_class_attr_types.get(_br[1], {}).pop(_atgt.attr, None)
						class_type_maps.get(_br[1], {}).pop(_atgt.attr, None)
						_direct_attr_assigns.add((_br[1], _atgt.attr))
		for node in tree_assigns:
			if not isinstance(node.value, ast.Call) or not isinstance(node.value.func, ast.Attribute):
				continue
			for tgt, _tv in _assign_pairs(node.targets, node.value):
				if not isinstance(tgt, ast.Name):
					continue
				_isc = _binding_scope_for(tgt.id, _scope_for_line(node.lineno))
				if _isc is None or scope_var_types.get(_isc, {}).get(tgt.id):
					continue
				_ir = _infer_type(node.value)
				if _ir is not None and _ir[0] == 'instance' and _ir[1] in local_classes:
					scope_var_types.setdefault(_isc, {}).setdefault(tgt.id, []).append((node.lineno, _ir[1]))
		_class_alias_seen = set()
		for _ in range(10):
			_alias_changed = False
			for _asc, _aln, _aname, _asrc in builder.alias_assigns:
				if (_aname, _aln) in _class_alias_seen:
					continue
				_asrc_key = _class_key_at(_asrc, _aln)
				if _asrc_key not in local_classes:
					continue
				_class_alias_seen.add((_aname, _aln))
				class_def_lines.setdefault(_aname, [])
				if _aln not in class_def_lines[_aname]:
					class_def_lines[_aname].append(_aln)
				_class_first_line.setdefault(_aname, _aln)
				_adst_key = _class_key_at(_aname, _aln)
				if _adst_key not in local_classes:
					local_classes[_adst_key] = local_classes[_asrc_key]
				_asrc_orig = _class_origin_at(_asrc, _aln)
				if _asrc_orig is not None:
					class_module_origin.setdefault(_aname, []).append((_aln, _asrc_orig))
				_aln_names = builder.scopes[_binding_scope_for(_aname, _asc)]['names'].setdefault(_aname, [])
				_aln_names[:] = [(_l, _k) for _l, _k in _aln_names if not (_l == _aln and _k == 'var')]
				_aln_names.append((_aln, 'class'))
				local_def_lines.setdefault(_aname, []).append(_aln)
				_alias_changed = True
			if not _alias_changed:
				break
		local_class_module_origins = {}
		for _nmc_name, _nmc_defs in name_module_class.items():
			for _nmc_ln, _nmc_origin in _nmc_defs:
				_nmc_key = _class_key_at(_nmc_name, _nmc_ln)
				local_class_module_origins.setdefault(_nmc_key, [])
				if _nmc_origin not in local_class_module_origins[_nmc_key]:
					local_class_module_origins[_nmc_key].append(_nmc_origin)
		if seed_module_bases:
			for _smb_k, _smb_v in seed_module_bases.items():
				local_class_module_origins.setdefault(_smb_k, [])
				for _smb_o in _smb_v:
					if _smb_o not in local_class_module_origins[_smb_k]:
						local_class_module_origins[_smb_k].append(_smb_o)
		for _mcb_key, _mcb_node in _module_class_bases:
			if _mcb_key not in local_classes:
				continue
			_mcb_r = _infer_type(_mcb_node)
			if _mcb_r is None or _mcb_r[0] != 'modclass':
				continue
			_mcb_mems = self._python_resolve_module_class_members(_mcb_r[1], _mcb_r[2])
			for _mcb_mk, _mcb_mv in _mcb_mems.items():
				local_classes[_mcb_key].setdefault(_mcb_mk, _mcb_mv)
			local_class_module_origins.setdefault(_mcb_key, []).append((_mcb_r[1], _mcb_r[2]))
		for _lcmo_node in tree_class_defs:
			if _lcmo_node.name not in local_classes:
				continue
			_lcmo_key = _node_class_key(_lcmo_node)
			for _lcmo_base in _lcmo_node.bases:
				if isinstance(_lcmo_base, ast.Name):
					_lcmo_orig = _class_origin_at(_lcmo_base.id, _lcmo_node.lineno)
					if _lcmo_orig is not None:
						local_class_module_origins.setdefault(_lcmo_key, []).append(_lcmo_orig)
		for _ in range(10):
			_lcmo_changed = False
			for _lcmo_cls, _lcmo_bases in class_bases.items():
				for _lcmo_b in _lcmo_bases:
					for _lcmo_o in local_class_module_origins.get(_lcmo_b, []):
						if _lcmo_o not in local_class_module_origins.get(_lcmo_cls, []):
							local_class_module_origins.setdefault(_lcmo_cls, []).append(_lcmo_o)
							_lcmo_changed = True
			if not _lcmo_changed:
				break
		for _ in range(10):
			_aomo_changed = False
			for _asc, _aln, _aname, _asrc in builder.alias_assigns:
				_asrc_key = _class_key_at(_asrc, _aln)
				_adst_key = _class_key_at(_aname, _aln)
				for _ao in local_class_module_origins.get(_asrc_key, []):
					if _ao not in local_class_module_origins.get(_adst_key, []):
						local_class_module_origins.setdefault(_adst_key, []).append(_ao)
						_aomo_changed = True
			if not _aomo_changed:
				break
		_python_merge_class_bases()
		typed_attrs = []
		_ti = 0
		for node in tree_attributes:
			_ti += 1
			if _ti % 400 == 0:
				_ck()
			r = _infer_type(node.value)
			if r is None:
				continue
			if r[0] == 'module':
				_k = _module_attr_kind(r[1], node.attr)
			elif r[0] in ('modclass', 'minstance'):
				_k = None
				if r[0] == 'minstance':
					_k = dynamic_class_attrs.get(r[2], {}).get(node.attr)
				if _k is None and r[0] == 'modclass':
					_k = dynamic_modclass_attrs.get(r[2], {}).get(node.attr)
				if _k is None:
					_k = self._python_resolve_module_member_kind(r[1], r[2], node.attr)
			elif r[0] == 'builtin':
				_k = _PYTHON_BUILTIN_MEMBERS.get(r[1], {}).get(node.attr)
			else:
				_k = None
				if r[0] == 'class' and _instance_only_attr(r[1], node.attr):
					continue
				if r[0] in ('instance', 'class'):
					_k = dynamic_class_attrs.get(r[1], {}).get(node.attr)
				if _k is None:
					_k = local_classes.get(r[1], {}).get(node.attr)
			if _k == 'var' and r[0] != 'builtin':
				_kir = _infer_type(node)
				if _kir is not None and (_kir[0] == 'minstance' or (_kir[0] == 'instance' and _kir[1] not in _PYTHON_BUILTIN_MEMBERS)):
					_k = 'instance'
			if _k is not None:
				typed_attrs.append((node.end_lineno, node.end_col_offset - len(node.attr), node.attr, _k))
		_ck()
		var_module_class = {}
		for _vn in tree_assigns:
			_val = _vn.value
			if not isinstance(_val, ast.Call):
				continue
			_fn = _val.func
			_cmod = None
			_ccls = None
			if isinstance(_fn, ast.Attribute) and isinstance(_fn.value, ast.Name):
				_bmod = _base_module_at(_fn.value.id, _vn.lineno)
				if _bmod is not None and self._python_resolve_module_members(_bmod).get(_fn.attr) == 'class':
					_cmod = _bmod
					_ccls = _fn.attr
			elif isinstance(_fn, ast.Name):
				_ffm = _line_def_at(from_func_module.get(_fn.id), _vn.lineno)
				if _ffm is not None and self._python_resolve_module_members(_ffm[0]).get(_ffm[1]) == 'class':
					_cmod, _ccls = _ffm
				else:
					_nmc = _line_def_at(name_module_class.get(_fn.id), _vn.lineno)
					if _nmc is not None:
						_cmod, _ccls = _nmc
			if _cmod is None:
				_vit = _infer_type(_val)
				if _vit is not None and _vit[0] == 'minstance':
					_cmod, _ccls = _vit[1], _vit[2]
			if _cmod is None:
				continue
			_vsc = _scope_for_line(_vn.lineno)
			for _t in _vn.targets:
				if isinstance(_t, ast.Name):
					var_module_class.setdefault((_binding_scope_for(_t.id, _vsc), _t.id), []).append((_vn.lineno, _cmod, _ccls))
		def _var_modclass_at(name, lineno, col = None):
			sidx = _scope_for_line(lineno) if col is None else _scope_for_pos(lineno, col)
			inner = sidx
			while sidx is not None:
				sc = builder.scopes[sidx]
				if sc.get('kind') == 'class' and sidx != inner:
					sidx = sc['parent']
					continue
				if name in sc['names']:
					best = None
					for _dl, _cm, _cc in var_module_class.get((sidx, name), []):
						if sidx == inner and _dl > lineno:
							continue
						if best is None or _dl > best[0]:
							best = (_dl, _cm, _cc)
					if best is not None:
						return best[1], best[2]
					return None
				sidx = sc['parent']
			return None
		call_kwargs = {}
		for lineno, func_name, kwarg_name, is_name, dotted, _cnode in builder.pending_calls:
			ok, params = _params_for_dotted(dotted, lineno)
			if not ok and dotted is not None and len(dotted) == 2:
				_mc = _var_modclass_at(dotted[0], lineno)
				if _mc is not None:
					found, mp = self._python_resolve_module_method(_mc[0], _mc[1], func_name)
					if found:
						ok, params = True, mp
				if not ok:
					_lcls = _var_type_at(dotted[0], lineno)
					if _lcls is not None:
						_lkey = _lcls + '.' + func_name
						if _lkey in local_class_accepts_any:
							ok, params = True, None
						elif _lkey in local_class_method_params:
							ok, params = True, local_class_method_params[_lkey]
						elif _class_origin_at(_lcls, lineno) is not None:
							_lorig = _class_origin_at(_lcls, lineno)
							found, mp = self._python_resolve_module_method(_lorig[0], _lorig[1], func_name)
							if found:
								ok, params = True, mp
						if not ok:
							for _lcmo_mod, _lcmo_cls in local_class_module_origins.get(_lcls, []):
								found, mp = self._python_resolve_module_method(_lcmo_mod, _lcmo_cls, func_name)
								if found:
									ok, params = True, mp
									break
			if not ok and isinstance(_cnode.func, ast.Attribute) and isinstance(_cnode.func.value, ast.Call) and isinstance(_cnode.func.value.func, ast.Name) and _cnode.func.value.func.id == 'super' and _call_name_kind('super', lineno) is None:
				_super_cls = None
				for _sms, _sme, _smfp, _smcls in method_fp_ranges:
					if _sms <= lineno <= _sme and (_super_cls is None or _sms > _super_cls[0]):
						_super_cls = (_sms, _smcls)
				if _super_cls is not None:
					for _sbase in class_bases.get(_super_cls[1], []):
						_sbkey = _sbase + '.' + func_name
						if _sbkey in local_class_accepts_any:
							ok, params = True, None
							break
						if _sbkey in local_class_method_params:
							ok, params = True, local_class_method_params[_sbkey]
							break
					if not ok:
						for _scmo_mod, _scmo_cls in local_class_module_origins.get(_super_cls[1], []):
							found, mp = self._python_resolve_module_method(_scmo_mod, _scmo_cls, func_name)
							if found:
								ok, params = True, mp
								break
			if not ok and isinstance(_cnode.func, ast.Attribute):
				_rcv = _infer_type(_cnode.func.value)
				if _rcv is not None:
					if _rcv[0] in ('modclass', 'minstance'):
						found, mp = self._python_resolve_module_method(_rcv[1], _rcv[2], func_name)
						if found:
							ok, params = True, mp
					elif _rcv[0] == 'module':
						_mok, _mp = _lookup_module_callable(_rcv[1], func_name)
						if _mok:
							ok, params = _mok, _mp
					elif _rcv[0] in ('instance', 'class') and not (_rcv[0] == 'class' and _instance_only_attr(_rcv[1], func_name)):
						if local_classes.get(_rcv[1], {}).get(func_name) == 'class':
							_cat = class_attr_types.get(_rcv[1], {}).get(func_name)
							if _cat is None and func_name in local_classes:
								_cat = ('class', func_name)
							if _cat is not None and _cat[0] == 'class' and _cat[1] in local_classes:
								_tkey = _cat[1]
								if _tkey + '.__init__' in local_class_accepts_any:
									ok, params = True, None
								elif _tkey + '.__init__' in local_class_method_params:
									ok, params = True, local_class_method_params[_tkey + '.__init__']
								else:
									ok, params = True, set()
									for _lcmo_mod, _lcmo_cls in local_class_module_origins.get(_tkey, []):
										found, mp = self._python_resolve_module_method(_lcmo_mod, _lcmo_cls, '__init__')
										if found:
											ok, params = True, mp
											break
									else:
										_torig = _class_origin_at(_tkey, lineno)
										if _torig is not None:
											found, mp = self._python_resolve_module_method(_torig[0], _torig[1], '__init__')
											if found:
												ok, params = True, mp
							elif _cat is not None and _cat[0] == 'modclass':
								found, mp = self._python_resolve_module_method(_cat[1], _cat[2], '__init__')
								if found:
									ok, params = True, mp
						_lkey = _rcv[1] + '.' + func_name
						if not ok and _lkey in local_class_accepts_any:
							ok, params = True, None
						elif not ok and _lkey in local_class_method_params:
							ok, params = True, local_class_method_params[_lkey]
						elif not ok and _class_origin_at(_rcv[1], lineno) is not None:
							_rorig = _class_origin_at(_rcv[1], lineno)
							found, mp = self._python_resolve_module_method(_rorig[0], _rorig[1], func_name)
							if found:
								ok, params = True, mp
						if not ok:
							for _lcmo_mod, _lcmo_cls in local_class_module_origins.get(_rcv[1], []):
								found, mp = self._python_resolve_module_method(_lcmo_mod, _lcmo_cls, func_name)
								if found:
									ok, params = True, mp
									break
			if ok and (params is None or kwarg_name in params):
				call_kwargs.setdefault(lineno, set()).add(kwarg_name)
		for _cdk_ln, _cdk_cls, _cdk_defln, _cdk_arg in builder.class_def_kwargs:
			if _cdk_arg == 'metaclass':
				call_kwargs.setdefault(_cdk_ln, set()).add(_cdk_arg)
				continue
			_cdk_key = _class_key_at(_cdk_cls, _cdk_defln)
			_cdk_ok = False
			_cdk_params = None
			for _cdk_base in class_bases.get(_cdk_key, []):
				_cdk_mk = _cdk_base + '.__init_subclass__'
				if _cdk_mk in local_class_accepts_any:
					_cdk_ok, _cdk_params = True, None
					break
				if _cdk_mk in local_class_method_params:
					_cdk_ok, _cdk_params = True, local_class_method_params[_cdk_mk]
					break
				for _cdk_mod, _cdk_mcls in local_class_module_origins.get(_cdk_base, []):
					found, mp = self._python_resolve_module_method(_cdk_mod, _cdk_mcls, '__init_subclass__')
					if found:
						_cdk_ok, _cdk_params = True, mp
						break
				if _cdk_ok:
					break
			if _cdk_ok and (_cdk_params is None or _cdk_arg in _cdk_params):
				call_kwargs.setdefault(_cdk_ln, set()).add(_cdk_arg)
		def _resolve_kind_in(start_idx, name, lineno):
			sidx = start_idx
			inner = sidx
			while sidx is not None:
				sc = builder.scopes[sidx]
				if sc.get('kind') == 'class' and sidx != inner:
					sidx = sc['parent']
					continue
				if name in sc['names']:
					best = None
					latest = None
					for dl, kind in sc['names'][name]:
						if latest is None or dl > latest[0]:
							latest = (dl, kind)
						if sidx == inner and dl > lineno:
							continue
						if best is None or dl > best[0]:
							best = (dl, kind)
					if best is None and latest is not None and _same_block(latest[0], lineno):
						best = latest
					return best[1] if best is not None else None
				sidx = sc['parent']
			return None
		param_default_tags = []
		for fnode in tree_func_defs:
			args = fnode.args
			param_names = set(a.arg for a in list(args.posonlyargs) + list(args.args) + list(args.kwonlyargs))
			if args.vararg:
				param_names.add(args.vararg.arg)
			if args.kwarg:
				param_names.add(args.kwarg.arg)
			defaults = list(args.defaults) + [d for d in args.kw_defaults if d is not None]
			if not param_names or not defaults:
				continue
			fscope = _scope_for_line(fnode.lineno)
			enclosing = builder.scopes[fscope]['parent'] if fscope is not None else None
			if enclosing is None:
				continue
			for dexpr in defaults:
				for nm in ast.walk(dexpr):
					if isinstance(nm, ast.Name) and nm.id in param_names:
						kind = _resolve_kind_in(enclosing, nm.id, fnode.lineno)
						if kind is not None:
							param_default_tags.append((nm.lineno, nm.col_offset, nm.id, kind))
		_ck()
		literal_attrs = []
		for node in tree_attributes:
			val = node.value
			_lat = None
			if isinstance(val, ast.Constant):
				_lat = type(val.value).__name__
			elif isinstance(val, ast.List):
				_lat = 'list'
			elif isinstance(val, ast.Dict):
				_lat = 'dict'
			elif isinstance(val, ast.Tuple):
				_lat = 'tuple'
			elif isinstance(val, ast.Set):
				_lat = 'set'
			elif isinstance(val, ast.JoinedStr):
				_lat = 'str'
			if _lat and node.attr in _PYTHON_BUILTIN_MEMBERS.get(_lat, {}):
				literal_attrs.append((node.end_lineno, node.end_col_offset - len(node.attr), node.attr, _lat))
		_ck()
		instance_name_positions = set()
		_instance_name_cache = {}
		for _inl, _incol, _inname, _instore in list(name_positions) + [(_pl, _pcol, _pname, False) for _pl, _pcol, _pname, _pkind in param_default_tags]:
			_inkey = (_inname, _inl, _incol)
			_inres = _instance_name_cache.get(_inkey)
			if _inres is None:
				_invt = _var_type_at(_inname, _inl, _incol)
				_inres = (_invt is not None and _invt in local_classes and _invt not in _PYTHON_BUILTIN_MEMBERS) or _var_modclass_at(_inname, _inl, _incol) is not None
				_instance_name_cache[_inkey] = _inres
			if _inres:
				instance_name_positions.add((_inl, _incol))
		_ck()
		global_stmt_kind_positions = {}
		def _gs_best(defs):
			best = None
			for _dl, _dv in defs:
				if _dl <= _gsend and (best is None or _dl > best[0]):
					best = (_dl, _dv)
			if best is None:
				for _dl, _dv in defs:
					if best is None or _dl > best[0]:
						best = (_dl, _dv)
			return best[1] if best is not None else None
		for _gsl, _gscol, _gsname, _gsscope in global_stmt_positions:
			if _gsscope is None:
				continue
			_gstgt = _binding_scope_for(_gsname, _gsscope)
			if _gstgt is None:
				continue
			_gsend = builder.scopes[_gsscope]['end']
			_gskind = _gs_best(builder.scopes[_gstgt]['names'].get(_gsname, ()))
			if _gskind is None:
				continue
			if _gskind == 'var':
				_gsvt = _gs_best(scope_var_types.get(_gstgt, {}).get(_gsname, ()))
				if _gsvt is not None and _gsvt in local_classes and _gsvt not in _PYTHON_BUILTIN_MEMBERS:
					_gskind = 'instance'
				elif _gs_best([(_d[0], (_d[1], _d[2])) for _d in var_module_class.get((_gstgt, _gsname), ())]) is not None:
					_gskind = 'instance'
			global_stmt_kind_positions[(_gsl, _gscol)] = _gskind
		_ck()
		_export_func_params = {}
		for _efp_n, _efp_defs in builder.func_params.items():
			_efp_mod = [_d for _d in _efp_defs if (_d[2] if len(_d) > 2 else 0) == 0]
			if _efp_mod:
				_export_func_params[_efp_n] = max(_efp_mod, key = lambda d: d[0])[1]
		_export_func_accepts_any = {}
		for _efa_n, _efa_defs in builder.func_accepts_any.items():
			_efa_mod = [_d for _d in _efa_defs if (_d[2] if len(_d) > 2 else 0) == 0]
			if _efa_mod:
				_export_func_accepts_any[_efa_n] = max(_efa_mod, key = lambda d: d[0])[1]
		_export_class_bases = {_k: _v for _k, _v in class_bases.items() if _k in module_scope_class_keys}
		_export_instance_only = {}
		for _eio_c, _eio_v in _self_assigned_attrs.items():
			if _eio_c not in module_scope_class_keys:
				continue
			_eio_only = set(_eio_v) - _class_body_members.get(_eio_c, set())
			if _eio_only:
				_export_instance_only[_eio_c] = _eio_only
		_export_inherited = {'members': _inherited_members, 'attr_types': _inherited_attr_types, 'method_params': _inherited_method_params}
		return builder.scopes, call_kwargs, builder.module_alias_defs, local_classes, module_literals, scope_var_types, literal_attrs, def_name_positions, typed_attrs, param_default_tags, builder.kwarg_positions, import_dotted_lines, import_orig_name_tags, class_module_origin, local_class_method_params, local_class_accepts_any, name_positions, local_class_module_origins, from_func_module, class_type_maps, class_attr_types, _export_func_params, _export_func_accepts_any, _export_class_bases, _export_inherited, module_scope_class_keys, _export_instance_only, instance_name_positions, global_stmt_kind_positions
	def _python_scan_names(self, text, gen = None):
		result = self._python_build_scopes(text, gen)
		if result is not None:
			scopes, call_kwargs, module_aliases, local_classes, module_literals, scope_var_types, literal_attrs, def_names, typed_attrs, param_default_tags, kwarg_positions, import_dotted_lines, import_orig_name_tags, class_module_origin, local_class_method_params, local_class_accepts_any, name_positions, _lcmo, _ffm, _ctm, _cat, _efp, _efa, _ecb, _ein, _emck, _eio, instance_name_positions, global_stmt_kind_positions = result
			self._python_scopes = scopes
			self._python_call_kwargs = call_kwargs
			self._python_module_literals = module_literals
			self._python_literal_attrs = literal_attrs
			self._python_name_positions = name_positions
			self._python_def_names = def_names
			self._python_typed_attrs = typed_attrs
			self._python_param_default_tags = param_default_tags
			self._python_kwarg_positions = kwarg_positions
			self._python_import_dotted_lines = import_dotted_lines
			self._python_import_orig_name_tags = import_orig_name_tags
			self._python_instance_name_positions = instance_name_positions
			self._python_global_stmt_kind_positions = global_stmt_kind_positions
			self._main_queue.put(lambda: self.ha('python') if self.hmode == 'python' else None)
	def _python_scan_start(self):
		self._python_scan_after_id = None
		if self._python_names_scan_thread is not None and self._python_names_scan_thread.is_alive():
			self._python_scan_after_id = self._own_type.after(10, self._python_scan_start)
			return
		gen = self._python_edit_generation[0]
		text = self.type_.get('1.0', 'end')
		def _get_and_scan():
			try:
				self._python_scan_names(text, gen)
			except _PythonScanCancelled:
				pass
			except Exception:
				pass
		self._python_names_scan_thread = threading.Thread(target = _get_and_scan, daemon = True)
		self._python_names_scan_thread.start()
	def _update_filesize(self):
		size = len(io.StringIO(self.type_.get('1.0', 'end')).read()) - 1
		self.filesize.config(text = str(size) + ' bytes')
	def trigger_filesize(self):
		if self._filesize_after_id is not None:
			self._own_type.after_cancel(self._filesize_after_id)
		self._filesize_after_id = self._own_type.after(DEBOUNCE_TIME, self._update_filesize)
	def _update_unsaved(self):
		if self.title and not self.hmode in ['png', 'pdf', 'epub']:
			if self.type_.get('1.0', 'end-1c') != self.unsavedtext:
				self.unsaved = True
				if (self.view_master or self) is active and not pcsettitle:
					root.title('PyNotes - ' + os.path.basename(self.title) + ' *')
				self.filesaved.config(text = 'Unsaved File')
			else:
				self.unsaved = False
				if (self.view_master or self) is active and not pcsettitle:
					root.title('PyNotes - ' + os.path.basename(self.title))
				self.filesaved.config(text = 'Saved File')
	def trigger_unsaved(self):
		if self._unsaved_after_id is not None:
			self._own_type.after_cancel(self._unsaved_after_id)
		self._unsaved_after_id = self._own_type.after(DEBOUNCE_TIME, self._update_unsaved)
	def trigger_ha(self, ft):
		if self.view_master is not None:
			return self.view_master.trigger_ha(ft)
		if self._ha_after_id is not None:
			self._own_type.after_cancel(self._ha_after_id)
		self._ha_after_id = self._own_type.after(DEBOUNCE_TIME, lambda: self.ha(ft))
	def python_trigger_name_scan(self):
		if self.view_master is not None:
			return self.view_master.python_trigger_name_scan()
		if self._python_scan_after_id is not None:
			self._own_type.after_cancel(self._python_scan_after_id)
		self._python_scan_after_id = self._own_type.after(DEBOUNCE_TIME, self._python_scan_start)
	def _python_resolve_module_func_params(self, name):
		if name in self._python_module_func_params_cache:
			return self._python_module_func_params_cache[name]
		spec = self._python_find_spec_cached(name)
		src_path = _python_module_src_path(spec, name)
		if src_path is None:
			self._python_module_func_params_cache[name] = {}
			return {}
		try:
			with open(src_path, 'r', encoding = 'utf-8') as f:
				src = f.read()
			with warnings.catch_warnings():
				warnings.simplefilter('ignore')
				mod_ast = ast.parse(src)
		except Exception:
			self._python_module_func_params_cache[name] = {}
			return {}
		out = {}
		_imp = {}
		_stars = []
		for node in mod_ast.body:
			if isinstance(node, ast.ImportFrom):
				_imod = _python_relative_import_target(name, node.level, node.module, bool(getattr(spec, 'submodule_search_locations', None))) if (node.module or node.level) else name
				if _imod:
					for alias in node.names:
						if alias.name != '*':
							_imp[alias.asname or alias.name] = (_imod, alias.name)
						elif _imod != name:
							_stars.append(_imod)
				continue
			if isinstance(node, ast.Import):
				for alias in node.names:
					_imp[alias.asname or alias.name.split('.')[0]] = (alias.name, None)
				continue
			if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
				params = set(a.arg for a in list(node.args.args) + list(node.args.kwonlyargs))
				if node.args.kwarg:
					params = None
				out[node.name] = params
			elif isinstance(node, ast.ClassDef):
				base_refs = []
				for b in node.bases:
					if isinstance(b, ast.Name):
						base_refs.append(b.id)
					elif isinstance(b, ast.Attribute):
						_parts = []
						_cur = b
						while isinstance(_cur, ast.Attribute):
							_parts.append(_cur.attr)
							_cur = _cur.value
						if isinstance(_cur, ast.Name):
							_parts.append(_cur.id)
							_parts.reverse()
							base_refs.append('.'.join(_parts))
				out['@bases:' + node.name] = base_refs
				for sub in node.body:
					if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)):
						margs = list(sub.args.posonlyargs) + list(sub.args.args) + list(sub.args.kwonlyargs)
						mparams = (set(a.arg for a in margs[1:]) - set(a.arg for a in sub.args.posonlyargs)) | set(a.arg for a in sub.args.kwonlyargs)
						if sub.args.kwarg:
							mparams = None
						out[node.name + '.' + sub.name] = mparams
						if sub.name == '__init__':
							out[node.name] = None if mparams is None else set(mparams)
				for sub in node.body:
					if isinstance(sub, ast.Assign) and isinstance(sub.value, ast.Name):
						_src_key = node.name + '.' + sub.value.id
						if _src_key in out:
							for _at in sub.targets:
								if isinstance(_at, ast.Name):
									out[node.name + '.' + _at.id] = out[_src_key]
		out['@imports'] = _imp
		self._python_module_func_params_cache[name] = out
		for _smod in _stars:
			for _sk, _sv in self._python_resolve_module_func_params(_smod).items():
				if _sk != '@imports' and _sk not in out:
					out[_sk] = _sv
		return out
	def _python_resolve_module_method(self, mod, class_name, method, seen = None):
		if seen is None:
			seen = set()
		key = (mod, class_name)
		if key in seen:
			return False, None
		seen.add(key)
		fp = self._python_resolve_module_func_params(mod)
		if f'{class_name}.{method}' in fp:
			return True, fp[f'{class_name}.{method}']
		imports = fp.get('@imports', {})
		if '@bases:' + class_name not in fp and class_name in imports and imports[class_name][1] is not None:
			return self._python_resolve_module_method(imports[class_name][0], imports[class_name][1], method, seen)
		for base in fp.get('@bases:' + class_name, []):
			bparts = base.split('.')
			if len(bparts) == 1:
				if '@bases:' + base in fp:
					ok, params = self._python_resolve_module_method(mod, base, method, seen)
					if ok:
						return True, params
				elif base in imports:
					bmod, bname = imports[base]
					if bname is not None:
						ok, params = self._python_resolve_module_method(bmod, bname, method, seen)
						if ok:
							return True, params
			else:
				broot = bparts[0]
				if broot in imports:
					bmod = imports[broot][0]
					full_mod = '.'.join([bmod] + bparts[1:-1]) if len(bparts) > 2 else bmod
					ok, params = self._python_resolve_module_method(full_mod, bparts[-1], method, seen)
					if ok:
						return True, params
		return False, None
	def _python_resolve_dotted_module(self, dotted):
		parts = dotted.split('.')
		cur = parts[0]
		if self._python_find_spec_cached(cur) is None:
			return None
		for _p in parts[1:]:
			_mm = self._python_resolve_module_members(cur)
			_tgt = _mm.get('@modtarget:' + _p)
			if _tgt is not None:
				cur = _tgt
				continue
			_sub = cur + '.' + _p
			if _mm.get(_p) == 'module' or self._python_find_spec_cached(_sub) is not None:
				cur = _sub
				continue
			return None
		return cur
	def ha(self, ft):
		if self.view_master is not None:
			return self.view_master.ha(ft)
		if self._ha_running[0]:
			self._ha_pending[0] = ft
			return
		self._ha_running[0] = True
		try:
			snapshots = []
			for member in self._group_members():
				own_type = member._own_type
				top = member.type_top
				bottom = member.type_bottom
				text = own_type.get(top, bottom)
				pre_text = own_type.get('1.0', top)
				snapshots.append((member, own_type, top, bottom, text, pre_text))
			python_scopes = self._python_scopes
			python_call_kwargs = self._python_call_kwargs
			python_module_literals = self._python_module_literals
			python_name_positions = self._python_name_positions
			python_def_names = self._python_def_names
			python_typed_attrs = self._python_typed_attrs
			python_param_default_tags = self._python_param_default_tags
			python_kwarg_positions = self._python_kwarg_positions
			python_import_dotted_lines = self._python_import_dotted_lines
			python_instance_name_positions = self._python_instance_name_positions
			python_global_stmt_kind_positions = self._python_global_stmt_kind_positions
			python_import_orig_name_tags = self._python_import_orig_name_tags
		except Exception:
			self._ha_running[0] = False
			pending = self._ha_pending[0]
			if pending is not None:
				self._ha_pending[0] = None
				self.ha(pending)
			return
		def _build_ops(own_type, top, bottom, text, pre_text):
			ops = []
			try:
				ops.append(('remove_all',))
				if ft == 'python':
					for m in _PYTHON_KW_PAT.finditer(text):
						ops.append(('add', 'hpa', f'{top}+{m.start()}c', f'{top}+{m.end()}c'))
					top_line = int(top.split('.')[0])
					line_scope_candidates = {}
					for line in range(top_line, top_line + len(text.split('\n'))):
						_cands = []
						for k, sc in enumerate(python_scopes):
							if sc['start'] <= line <= sc['end']:
								_cands.append((sc['start'], sc.get('start_col', 0), sc['end'], sc.get('end_col'), k))
						line_scope_candidates[line] = _cands
					def _resolve_scope_idx(line, col):
						winner = None
						winner_start = None
						for _cstart, _ccol, _cend, _ecol, _ck in line_scope_candidates.get(line, ()):
							if _cstart == line and col < _ccol:
								continue
							if _cend == line and _ecol is not None and col >= _ecol:
								continue
							if winner is None or _cstart >= winner_start:
								winner = _ck
								winner_start = _cstart
						return winner
					module_literal_lines = {}
					for lineno, _mcol, name in python_module_literals:
						module_literal_lines.setdefault(lineno, []).append((_mcol, name))
					import_dotted_by_line = {}
					for lineno, dcol, dotted in python_import_dotted_lines:
						import_dotted_by_line.setdefault(lineno, []).append((dcol, dotted))
					import_orig_by_line = {}
					for _oln, _ocol, _oname, _otag in python_import_orig_name_tags:
						import_orig_by_line.setdefault(_oln, []).append((_ocol, _oname, _otag))
					name_pos_by_line = {}
					for _nl, _ncol, _nname, _nstore in python_name_positions:
						name_pos_by_line.setdefault(_nl, []).append((_ncol, _nname, _nstore))
					def_names_by_line = {}
					for _dl, _dcol, _dname, _dkind in python_def_names:
						def_names_by_line.setdefault(_dl, []).append((_dcol, _dname, _dkind))
					python_kind_tags = {'var': 'hpv', 'instance': 'hpi', 'func': 'hpf', 'func_arg': 'hpfa', 'first_param': 'hpb', 'module': 'hpm', 'class': 'hpx', 'builtin': 'hpb'}
					python_literal_attrs = self._python_literal_attrs
					literal_attr_by_line = {}
					for _ln, _col, _attr, _tname in python_literal_attrs:
						literal_attr_by_line.setdefault(_ln, []).append((_col, _attr, _tname))
					typed_attr_by_line = {}
					for _tl, _tcol, _tattr, _tkind in python_typed_attrs:
						typed_attr_by_line.setdefault(_tl, []).append((_tcol, _tattr, _tkind))
					param_default_by_line = {}
					for _pl, _pcol, _pname, _pkind in python_param_default_tags:
						param_default_by_line.setdefault(_pl, []).append((_pcol, _pname, _pkind))
					kwarg_pos_by_line = {}
					for _kl, _kcol, _kname in python_kwarg_positions:
						kwarg_pos_by_line.setdefault(_kl, []).append((_kcol, _kname))
					_active_cache = {}
					def _active_for(abs_line, scope_idx):
						_ckey = (abs_line, scope_idx)
						if _ckey in _active_cache:
							return _active_cache[_ckey]
						active = {}
						prior_kinds = {}
						bound = set()
						innermost_scope = scope_idx
						innermost_parent = python_scopes[innermost_scope]['parent'] if innermost_scope is not None else None
						on_header = innermost_scope is not None and abs_line == python_scopes[innermost_scope]['start']
						_redir_names = set()
						_rsi = innermost_scope
						while _rsi is not None:
							_rsc = python_scopes[_rsi]
							_redir_names |= set(_rsc.get('globals', {}))
							_redir_names |= set(_rsc.get('nonlocals', {}))
							_rsi = _rsc['parent']
						_sidx = scope_idx
						while _sidx is not None:
							sc = python_scopes[_sidx]
							if sc.get('kind') == 'class' and _sidx != innermost_scope and not (on_header and _sidx == innermost_parent):
								_sidx = sc['parent']
								continue
							sc_globals = sc.get('globals', {})
							sc_nonlocals = sc.get('nonlocals', {})
							for name, defs in sc['names'].items():
								if name in active or name in bound:
									continue
								if name in sc_globals or name in sc_nonlocals:
									continue
								best = None
								second_best = None
								latest = None
								_guard = _sidx == innermost_scope or name in _redir_names
								for dl, kind in defs:
									if latest is None or dl > latest[0]:
										latest = (dl, kind)
									if _guard and dl > abs_line:
										continue
									if best is None or dl > best[0]:
										second_best = best
										best = (dl, kind)
									elif second_best is None or dl > second_best[0]:
										second_best = (dl, kind)
								if best is None and name not in _PYTHON_BUILTIN_NAMES:
									best = latest
								bound.add(name)
								if best is not None:
									active[name] = best[1]
									if best[0] == abs_line and second_best is not None and second_best[1] != best[1]:
										prior_kinds[name] = second_best[1]
							_sidx = sc['parent']
						_result = (active, prior_kinds)
						_active_cache[_ckey] = _result
						return _result
					offset = 0
					for li, line_str in enumerate(text.split('\n')):
						abs_line = top_line + li
						for _ncol, _nname, _nstore in name_pos_by_line.get(abs_line, []):
							_nkind = python_global_stmt_kind_positions.get((abs_line, _ncol))
							if _nkind is None:
								active, prior_kinds = _active_for(abs_line, _resolve_scope_idx(abs_line, _ncol))
								_nkind = active.get(_nname)
								if _nkind is None:
									if _nname not in _PYTHON_BUILTIN_NAMES:
										continue
									_nkind = 'builtin'
								elif not _nstore and _nname in prior_kinds:
									_nkind = prior_kinds[_nname]
							_ntag = python_kind_tags.get(_nkind)
							if _ntag is None:
								continue
							if _ntag == 'hpv' and (abs_line, _ncol) in python_instance_name_positions:
								_ntag = 'hpi'
							_nccol = _python_bytecol_to_charcol(line_str, _ncol)
							s = f'{top}+{offset + _nccol}c'
							e = f'{top}+{offset + _nccol + len(_nname)}c'
							ops.append(('add', _ntag, s, e))
						for _dcol, _dname, _dkind in def_names_by_line.get(abs_line, []):
							_dccol = _python_bytecol_to_charcol(line_str, _dcol)
							s = f'{top}+{offset + _dccol}c'
							e = f'{top}+{offset + _dccol + len(_dname)}c'
							ops.append(('add', 'hpf' if _dkind == 'func' else 'hpx', s, e))
						for _pcol, _pname, _pkind in param_default_by_line.get(abs_line, []):
							if _pkind == 'var' and (abs_line, _pcol) in python_instance_name_positions:
								_pkind = 'instance'
							_pcol = _python_bytecol_to_charcol(line_str, _pcol)
							_ptag = {'var': 'hpv', 'instance': 'hpi', 'func': 'hpf', 'func_arg': 'hpfa', 'first_param': 'hpb', 'module': 'hpm', 'class': 'hpx'}.get(_pkind)
							if _ptag is not None:
								s = f'{top}+{offset + _pcol}c'
								e = f'{top}+{offset + _pcol + len(_pname)}c'
								ops.append(('add', _ptag, s, e))
						for _mcol, name in module_literal_lines.get(abs_line, []):
							_mccol = _python_bytecol_to_charcol(line_str, _mcol)
							if line_str[_mccol:_mccol + len(name)] != name:
								continue
							ops.append(('add', 'hpm', f'{top}+{offset + _mccol}c', f'{top}+{offset + _mccol + len(name)}c'))
						for dcol, dotted in import_dotted_by_line.get(abs_line, []):
							dcol = _python_bytecol_to_charcol(line_str, dcol)
							if line_str[dcol:dcol + len(dotted)] != dotted:
								continue
							pos = dcol
							for part in dotted.split('.'):
								ops.append(('add', 'hpm', f'{top}+{offset + pos}c', f'{top}+{offset + pos + len(part)}c'))
								pos += len(part) + 1
						for _ocol, _oname, _otag in import_orig_by_line.get(abs_line, []):
							_ocol = _python_bytecol_to_charcol(line_str, _ocol)
							if line_str[_ocol:_ocol + len(_oname)] != _oname:
								continue
							ops.append(('add', _otag, f'{top}+{offset + _ocol}c', f'{top}+{offset + _ocol + len(_oname)}c'))
						for _col, _attr, _tname in literal_attr_by_line.get(abs_line, []):
							_col = _python_bytecol_to_charcol(line_str, _col)
							_kind = _PYTHON_BUILTIN_MEMBERS[_tname].get(_attr)
							if _kind is not None:
								ops.append(('add', 'hpf' if _kind == 'func' else 'hpv', f'{top}+{offset + _col}c', f'{top}+{offset + _col + len(_attr)}c'))
						for _tcol, _tattr, _tkind in typed_attr_by_line.get(abs_line, []):
							_tcol = _python_bytecol_to_charcol(line_str, _tcol)
							_ttag = {'func': 'hpf', 'var': 'hpv', 'instance': 'hpi', 'module': 'hpm', 'class': 'hpx'}.get(_tkind, 'hpx')
							ops.append(('add', _ttag, f'{top}+{offset + _tcol}c', f'{top}+{offset + _tcol + len(_tattr)}c'))
						for _kcol, _kname in kwarg_pos_by_line.get(abs_line, []):
							_kcol = _python_bytecol_to_charcol(line_str, _kcol)
							s = f'{top}+{offset + _kcol}c'
							e = f'{top}+{offset + _kcol + len(_kname)}c'
							ops.append(('clear_other', s, e))
							if _kname in python_call_kwargs.get(abs_line, set()):
								ops.append(('add', 'hpfa', s, e))
						offset += len(line_str) + 1
					for m in _PYTHON_OP_PAT.finditer(text):
						s = f'{top}+{m.start()}c'
						e = f'{top}+{m.end()}c'
						ops.append(('add', 'hpo', s, e))
					pre_n = len(pre_text)
					pre_i = 0
					in_triple = False
					triple_ch = None
					in_single = False
					single_ch = None
					while pre_i < pre_n:
						pch = pre_text[pre_i]
						if pch in ('"', "'") and pre_i + 2 < pre_n and pre_text[pre_i + 1] == pch and pre_text[pre_i + 2] == pch:
							pquote = pre_text[pre_i:pre_i + 3]
							j = pre_i + 3
							found_close = False
							while j < pre_n:
								if pre_text[j] == '\\':
									j += 2
									continue
								if pre_text[j:j + 3] == pquote:
									j += 3
									found_close = True
									break
								j += 1
							if not found_close:
								in_triple = True
								triple_ch = pch
								break
							pre_i = j
						elif pch in ('"', "'"):
							pquote = pch
							j = pre_i + 1
							closed = False
							while j < pre_n:
								if pre_text[j] == '\\':
									j += 2
									continue
								if pre_text[j] == pquote:
									j += 1
									closed = True
									break
								if pre_text[j] == '\n':
									closed = True
									break
								j += 1
							if not closed:
								in_single = True
								single_ch = pquote
								break
							pre_i = j
						elif pch == '#':
							j = pre_i + 1
							while j < pre_n and pre_text[j] != '\n':
								j += 1
							if j < pre_n:
								j += 1
							pre_i = j
						else:
							pre_i += 1
					n = len(text)
					i = 0
					if in_triple:
						quote = triple_ch * 3
						j = 0
						found_close = False
						while j < n:
							if text[j] == '\\':
								j += 2
								continue
							if text[j:j + 3] == quote:
								j += 3
								found_close = True
								break
							j += 1
						if not found_close:
							j = n
						ops.append(('add', 'hpd', f'{top}+0c', f'{top}+{j}c'))
						i = j
					elif in_single:
						quote = single_ch
						j = 0
						while j < n:
							if text[j] == '\\':
								j += 2
								continue
							if text[j] == quote:
								j += 1
								break
							if text[j] == '\n':
								break
							j += 1
						if j > n:
							j = n
						ops.append(('add', 'hpd', f'{top}+0c', f'{top}+{j}c'))
						i = j
					while i < n:
						ch = text[i]
						if ch in ('"', "'") and i + 2 < n and text[i + 1] == ch and text[i + 2] == ch:
							quote = text[i:i + 3]
							j = i + 3
							found_close = False
							while j < n:
								if text[j] == '\\':
									j += 2
									continue
								if text[j:j + 3] == quote:
									j += 3
									found_close = True
									break
								j += 1
							if not found_close:
								j = n
							ops.append(('add', 'hpd', f'{top}+{i}c', f'{top}+{j}c'))
							i = j
						elif ch in ('"', "'"):
							quote = ch
							j = i + 1
							while j < n:
								if text[j] == '\\':
									j += 2
									continue
								if text[j] == quote:
									j += 1
									break
								if text[j] == '\n':
									break
								j += 1
							ops.append(('add', 'hpd', f'{top}+{i}c', f'{top}+{j}c'))
							i = j
						elif ch == '#':
							j = i + 1
							while j < n and text[j] != '\n':
								j += 1
							if j < n:
								j += 1
							ops.append(('add', 'hpc', f'{top}+{i}c', f'{top}+{j}c'))
							i = j
						else:
							i += 1
				elif ft == 'latex':
					pre_n = len(pre_text)
					pre_i = 0
					in_math = False
					math_close = ''
					while pre_i < pre_n:
						pc = pre_text[pre_i]
						if pc == '\\' and pre_i + 1 < pre_n:
							nc = pre_text[pre_i + 1]
							if not in_math and nc == '[':
								in_math = True
								math_close = '\\]'
								pre_i += 2
								continue
							if not in_math and nc == '(':
								in_math = True
								math_close = '\\)'
								pre_i += 2
								continue
							if in_math and math_close == '\\]' and nc == ']':
								in_math = False
								pre_i += 2
								continue
							if in_math and math_close == '\\)' and nc == ')':
								in_math = False
								pre_i += 2
								continue
							pre_i += 2
							continue
						if pc == '%':
							while pre_i < pre_n and pre_text[pre_i] != '\n':
								pre_i += 1
							continue
						if pc == '$':
							if pre_i + 1 < pre_n and pre_text[pre_i + 1] == '$':
								if in_math and math_close == '$$':
									in_math = False
								elif not in_math:
									in_math = True
									math_close = '$$'
								pre_i += 2
								continue
							else:
								if in_math and math_close == '$':
									in_math = False
								elif not in_math:
									in_math = True
									math_close = '$'
						pre_i += 1
					if in_math:
						j = text.find(math_close)
						if j == -1:
							j = len(text)
						else:
							j += len(math_close)
						ops.append(('add', 'hla', f'{top}+0c', f'{top}+{j}c'))
					for m in _LATEX_MATH_PAT.finditer(text):
						ops.append(('add', 'hla', f'{top}+{m.start()}c', f'{top}+{m.end()}c'))
					pre_n = len(pre_text)
					env_stack = []
					for em in re.finditer(r'\\(begin|end)\{\s*(\w+\*?)\s*\}', pre_text):
						ename = em.group(2)
						if ename == 'document':
							continue
						if em.group(1) == 'begin':
							env_stack.append((ename, em.start()))
						elif env_stack and env_stack[-1][0] == ename:
							env_stack.pop()
					scan_from = 0
					if env_stack:
						outer_name, outer_start = env_stack[0]
						region = own_type.get(f'1.0+{outer_start}c', bottom)
						env_pat = re.compile(r'\\(begin|end)\{\s*' + re.escape(outer_name) + r'\s*\}')
						m0 = env_pat.match(region)
						depth = 1
						search_from = m0.end() if m0 else len(region)
						hl_start_rel = search_from
						nl0 = region.find('\n', hl_start_rel)
						if nl0 != -1:
							hl_start_rel = nl0 + 1
						while depth > 0:
							em2 = env_pat.search(region, search_from)
							if not em2:
								search_from = len(region)
								break
							if em2.group(1) == 'begin':
								depth += 1
							else:
								depth -= 1
							search_from = em2.end()
						end_abs = outer_start + search_from
						hl_start_abs = outer_start + hl_start_rel
						if hl_start_abs < end_abs:
							ops.append(('add', 'hlb', f'1.0+{hl_start_abs}c', f'1.0+{end_abs}c'))
						scan_from = max(0, end_abs - pre_n)
					tn = len(text)
					for begin_m in re.finditer(r'\\begin\{\s*(\w+\*?)\s*\}', text[scan_from:]):
						if begin_m.group(1) == 'document':
							continue
						env_name = re.escape(begin_m.group(1))
						search_from2 = scan_from + begin_m.end()
						bstart = search_from2
						nl1 = text.find('\n', bstart)
						if nl1 != -1:
							bstart = nl1 + 1
						depth2 = 1
						env_pat2 = re.compile(r'\\(begin|end)\{\s*' + env_name + r'\s*\}')
						bend = tn
						while depth2 > 0:
							em3 = env_pat2.search(text, search_from2)
							if not em3:
								break
							if em3.group(1) == 'begin':
								depth2 += 1
							else:
								depth2 -= 1
							search_from2 = em3.end()
							if depth2 == 0:
								bend = search_from2
						if bstart < bend:
							ops.append(('add', 'hlb', f'{top}+{bstart}c', f'{top}+{bend}c'))
					for m in re.finditer(r'\\[a-zA-Z@]+\*?', text):
						ops.append(('add', 'hld', f'{top}+{m.start()}c', f'{top}+{m.end()}c'))
					for i in range(len(text)):
						if text[i] == '{' and (i == 0 or text[i - 1] != '\\'):
							j = _find_closing_brace(text, i)
							ops.append(('add', 'hle', f'{top}+{i}c', f'{top}+{j}c'))
					for m in re.finditer(r'\\\\|&|\|', text):
						ops.append(('add', 'hlf', f'{top}+{m.start()}c', f'{top}+{m.end()}c'))
					for i in range(len(text)):
						if text[i] == '[' and (i == 0 or text[i - 1] != '\\'):
							j = _find_closing_bracket(text, i)
							ops.append(('add', 'hlg', f'{top}+{i}c', f'{top}+{j}c'))
					for m in _LH_PAT.finditer(text):
						s = f'{top}+{m.start()}c'
						e = f'{top}+{m.end()}c'
						ops.append(('add', 'hlh', s, e))
				elif ft == 'html':
					last_open = pre_text.rfind('<!--')
					last_close = pre_text.rfind('-->')
					if last_open != -1 and last_close < last_open:
						close_pos = text.find('-->')
						j = (close_pos + 3) if close_pos != -1 else len(text)
						ops.append(('add', 'hcmt', f'{top}+0c', f'{top}+{j}c'))
					for m in _HC_PAT.finditer(text):
						s = f'{top}+{m.start()}c'
						e = f'{top}+{m.end()}c'
						ops.append(('add', 'hcmt', s, e))
					hi = 0
					htlen = len(text)
					while hi < htlen:
						if text[hi] != '<' or hi >= htlen - 1:
							hi += 1
							continue
						hj = _find_closing_tag(text, hi)
						htag_inner = text[hi:hj]
						if text[hi + 1] == '!':
							if re.match(r'<!DOCTYPE\b', htag_inner, re.IGNORECASE):
								ops.append(('add', 'hstuff', f'{top}+{hi}c', f'{top}+{hj}c'))
							hi = hj
							continue
						if hj > hi + 1 and (text[hi + 1].isalpha() or text[hi + 1] == '/'):
							ops.append(('add', 'hstuff', f'{top}+{hi}c', f'{top}+{hj}c'))
							htn_m = re.match(r'</?([a-zA-Z][a-zA-Z0-9:-]*)', htag_inner, re.IGNORECASE)
							hattrs_off = htn_m.end() if htn_m else 1
							for ham in _HTML_ATTR_PAT.finditer(htag_inner, hattrs_off):
								ops.append(('add', 'hattr', f'{top}+{hi + ham.start(1)}c', f'{top}+{hi + ham.end(1)}c'))
								ops.append(('add', 'hstr', f'{top}+{hi + ham.start(2)}c', f'{top}+{hi + ham.end(2)}c'))
							for hbm in _HTML_BOOL_ATTR_PAT.finditer(htag_inner, hattrs_off):
								ops.append(('add', 'hattr', f'{top}+{hi + hbm.start()}c', f'{top}+{hi + hbm.end()}c'))
						hi = hj
				elif ft == 'markdown':
					last_open = pre_text.rfind('<!--')
					last_close = pre_text.rfind('-->')
					if last_open != -1 and last_close < last_open:
						close_pos = text.find('-->')
						j = (close_pos + 3) if close_pos != -1 else len(text)
						ops.append(('add', 'hcmt', f'{top}+0c', f'{top}+{j}c'))
					for m in _HC_PAT.finditer(text):
						s = f'{top}+{m.start()}c'
						e = f'{top}+{m.end()}c'
						ops.append(('add', 'hcmt', s, e))
					mhi = 0
					mhtlen = len(text)
					while mhi < mhtlen:
						if text[mhi] != '<' or mhi >= mhtlen - 1:
							mhi += 1
							continue
						mhj = _find_closing_tag(text, mhi)
						mhtag_inner = text[mhi:mhj]
						if text[mhi + 1] == '!':
							if re.match(r'<!DOCTYPE\b', mhtag_inner, re.IGNORECASE):
								ops.append(('add', 'hstuff', f'{top}+{mhi}c', f'{top}+{mhj}c'))
							mhi = mhj
							continue
						if mhj > mhi + 1 and (text[mhi + 1].isalpha() or text[mhi + 1] == '/'):
							ops.append(('add', 'hstuff', f'{top}+{mhi}c', f'{top}+{mhj}c'))
							mhtn_m = re.match(r'</?([a-zA-Z][a-zA-Z0-9:-]*)', mhtag_inner, re.IGNORECASE)
							mhattrs_off = mhtn_m.end() if mhtn_m else 1
							for mham in _HTML_ATTR_PAT.finditer(mhtag_inner, mhattrs_off):
								ops.append(('add', 'hattr', f'{top}+{mhi + mham.start(1)}c', f'{top}+{mhi + mham.end(1)}c'))
								ops.append(('add', 'hstr', f'{top}+{mhi + mham.start(2)}c', f'{top}+{mhi + mham.end(2)}c'))
							for mhbm in _HTML_BOOL_ATTR_PAT.finditer(mhtag_inner, mhattrs_off):
								ops.append(('add', 'hattr', f'{top}+{mhi + mhbm.start()}c', f'{top}+{mhi + mhbm.end()}c'))
						mhi = mhj
					for m in _MDH_PAT.finditer(text):
						level = len(m.group(1))
						s = f'{top}+{m.start()}c'
						e = f'{top}+{m.end()}c'
						for htag in _MD_HTML_TAGS:
							ops.append(('remove', htag, s, e))
						ops.append(('add', f'hmh{level}', s, e))
					for m in _MDB_PAT.finditer(text):
						s = f'{top}+{m.start()}c'
						e = f'{top}+{m.end()}c'
						for htag in _MD_HTML_TAGS:
							ops.append(('remove', htag, s, e))
						ops.append(('add', 'hmb', s, e))
					for m in _MDI_PAT.finditer(text):
						s = f'{top}+{m.start()}c'
						e = f'{top}+{m.end()}c'
						for htag in _MD_HTML_TAGS:
							ops.append(('remove', htag, s, e))
						ops.append(('add', 'hmi', s, e))
					for m in _MDBI_PAT.finditer(text):
						s = f'{top}+{m.start()}c'
						e = f'{top}+{m.end()}c'
						ops.append(('add', 'hmbi', s, e))
					for m in _MDS_PAT.finditer(text):
						s = f'{top}+{m.start()}c'
						e = f'{top}+{m.end()}c'
						for htag in _MD_HTML_TAGS:
							ops.append(('remove', htag, s, e))
						ops.append(('add', 'hms', s, e))
					for m in _MDC_PAT.finditer(text):
						s = f'{top}+{m.start()}c'
						e = f'{top}+{m.end()}c'
						ops.append(('add', 'hmc', s, e))
					for m in _MDL_PAT.finditer(text):
						s = f'{top}+{m.start()}c'
						e = f'{top}+{m.end()}c'
						ops.append(('add', 'hml', s, e))
					for m in _MDQ_PAT.finditer(text):
						s = f'{top}+{m.start()}c'
						e = f'{top}+{m.end()}c'
						for htag in _MD_HTML_TAGS:
							ops.append(('remove', htag, s, e))
						ops.append(('add', 'hmq', s, e))
					pre_n = len(pre_text)
					pre_i = 0
					in_fence = False
					while pre_i < pre_n:
						if (pre_i == 0 or pre_text[pre_i - 1] == '\n') and pre_text[pre_i:pre_i + 3] == '```':
							j = pre_i + 3
							while j < pre_n and pre_text[j] != '\n':
								j += 1
							if j < pre_n:
								j += 1
							k = j
							found_close = False
							while k < pre_n:
								if (k == 0 or pre_text[k - 1] == '\n') and pre_text[k:k + 3] == '```':
									k += 3
									while k < pre_n and pre_text[k] != '\n':
										k += 1
									if k < pre_n:
										k += 1
									found_close = True
									break
								k += 1
							if found_close:
								pre_i = k
							else:
								in_fence = True
								break
						else:
							pre_i += 1
					n = len(text)
					i = 0
					if in_fence:
						j = 0
						found_close = False
						while j < n:
							if (j == 0 or text[j - 1] == '\n') and text[j:j + 3] == '```':
								j += 3
								while j < n and text[j] != '\n':
									j += 1
								if j < n:
									j += 1
								found_close = True
								break
							j += 1
						if not found_close:
							j = n
						ops.append(('add', 'hmf', f'{top}+0c', f'{top}+{j}c'))
						i = j
					while i < n:
						if (i == 0 or text[i - 1] == '\n') and text[i:i + 3] == '```':
							j = i + 3
							while j < n and text[j] != '\n':
								j += 1
							if j < n:
								j += 1
							k = j
							found_close = False
							while k < n:
								if (k == 0 or text[k - 1] == '\n') and text[k:k + 3] == '```':
									k += 3
									while k < n and text[k] != '\n':
										k += 1
									if k < n:
										k += 1
									found_close = True
									break
								k += 1
							if not found_close:
								k = n
							ops.append(('add', 'hmf', f'{top}+{i}c', f'{top}+{k}c'))
							i = k
						else:
							i += 1
			except Exception:
				pass
			return ops
		def _apply_plugin_ops(text, top, ops):
			if ft in plugin_hl:
				entry = plugin_hl[ft]
				plugin_name = entry.get('plugin', '') if isinstance(entry, dict) else ''
				if isinstance(entry, dict):
					func = entry.get('func', None)
					cond = entry.get('if', True)
					hl = entry.get('hl', '{}')
					else_fn = entry.get('else', None)
					if func is not None:
						try:
							exec(func, globals())
						except Exception as error:
							error = str(error)
							msg = f'There was an error in running the function "{func}" before syntax highlighting by the plugin "{plugin_name}":\n{error}'
							root.error('Error', msg)
					try:
						cond_result = bool(eval(cond, globals()))
					except Exception as error:
						msg = f'There was an error in evaluating the condition "{cond}" for syntax highlighting by the plugin "{plugin_name}":\n{error}'
						root.error('Error', msg)
						cond_result = False
					if cond_result:
						try:
							hl_value = eval(hl, globals())
						except Exception as error:
							error = str(error)
							msg = f'There was an error in syntax highlighting of the plugin "{plugin_name}":\n{error}'
							root.error('Error', msg)
							hl_value = {}
						if callable(hl_value):
							try:
								hl_value(text, top, ops)
							except Exception as error:
								error = str(error)
								msg = f'There was an error in syntax highlighting of the plugin "{plugin_name}":\n{error}'
								root.error('Error', msg)
						else:
							for tag, (pat, theme_key) in hl_value.items():
								try:
									for m in pat.finditer(text):
										ops.append(('add', tag, f'{top}+{m.start()}c', f'{top}+{m.end()}c'))
									ops.append(('config', tag, theme[theme_key]))
								except Exception as error:
									error = str(error)
									msg = f'There was an error in syntax highlighting of the plugin "{plugin_name}":\n{error}'
									root.error('Error', msg)
					elif else_fn is not None:
						try:
							exec(else_fn, globals())
						except Exception as error:
							error = str(error)
							msg = f'There was an error in running the else block in the syntax highlighting of the plugin "{plugin_name}":\n{error}'
							root.error('Error', msg)
				elif callable(entry):
					try:
						entry(text, top, ops)
					except Exception as error:
						error = str(error)
						msg = f'There was an error in syntax highlighting of the plugin "{plugin_name}":\n{error}'
						root.error('Error', msg)
				else:
					for tag, (pat, theme_key) in entry.items():
						try:
							for m in pat.finditer(text):
								ops.append(('add', tag, f'{top}+{m.start()}c', f'{top}+{m.end()}c'))
						except Exception as error:
							error = str(error)
							msg = f'There was an error in syntax highlighting of the plugin "{plugin_name}":\n{error}'
							root.error('Error', msg)
		def do_hl():
			results = [(member, own_type, top, bottom, text, _build_ops(own_type, top, bottom, text, pre_text)) for member, own_type, top, bottom, text, pre_text in snapshots]
			self._main_queue.put(lambda: _finish_all(results))
		def _done():
			self._ha_running[0] = False
			pending = self._ha_pending[0]
			if pending is not None:
				self._ha_pending[0] = None
				self.ha(pending)
		def _finish_all(results):
			def _process(i):
				if i >= len(results):
					_done()
					return
				member, own_type, top, bottom, text, ops = results[i]
				_apply_plugin_ops(text, top, ops)
				_finish_one(member, own_type, top, bottom, text, ops, lambda: _process(i + 1))
			_process(0)
		def _finish_one(member, own_type, top, bottom, text, ops, on_done):
			try:
				if own_type.get(top, bottom) != text:
					on_done()
					return
				all_tags = set(own_type.tag_names())
				removable_tags = [tag for tag in all_tags if tag not in _PYTHON_EDITOR_HL_SKIP_REMOVE_TAGS and (tag not in skiptags or member.hmode not in skiptags[tag])]
				_HA_CHUNK_SIZE = 4000
				def _apply_chunk(start):
					try:
						end = min(start + _HA_CHUNK_SIZE, len(ops))
						for op in ops[start:end]:
							if op[0] == 'remove_all':
								for tag in removable_tags:
									own_type.tag_remove(tag, top, bottom)
							elif op[0] == 'add':
								for tag in removable_tags:
									if tag != op[1] and not (ft == 'latex' and tag == 'hlb' and op[1] != 'hlb'):
										own_type.tag_remove(tag, op[2], op[3])
								own_type.tag_add(op[1], op[2], op[3])
								if ft == 'latex' and op[1] != 'hlb':
									own_type.tag_raise(op[1], 'hlb')
							elif op[0] == 'remove':
								own_type.tag_remove(op[1], op[2], op[3])
							elif op[0] == 'config':
								exec("own_type.tag_config('" + op[1] + "'," + op[2] + ')')
							elif op[0] == 'clear_other':
								for tag in removable_tags:
									own_type.tag_remove(tag, op[1], op[2])
						own_type.tag_raise('sel')
						if end < len(ops):
							member._ha_apply_after_id = root.after(0, lambda: _apply_chunk(end))
						else:
							member._ha_apply_after_id = None
							on_done()
					except Exception as error:
						member._ha_apply_after_id = None
						error = str(error)
						root.error('Error!', f'Error:{error}\nInvalid colour settings.\nQuitting syntax highlighting.')
						on_done()
				_apply_chunk(0)
			except Exception as error:
				error = str(error)
				root.error('Error!', f'Error:{error}\nInvalid colour settings.\nQuitting syntax highlighting.')
				on_done()
		threading.Thread(target = do_hl, daemon = True).start()
	def init_hl_tags(self):
		[self._own_type.tag_delete(tag) for tag in ('hpa', 'hpb', 'hpv', 'hpi', 'hpf', 'hpx', 'hpfa', 'hpm', 'hpo', 'hpd', 'hpc', 'hla', 'hlb', 'hld', 'hle', 'hlf', 'hlg', 'hlh', 'hstuff', 'hattr', 'hstr', 'hcmt', 'hmh1', 'hmh2', 'hmh3', 'hmh4', 'hmh5', 'hmh6', 'hmb', 'hmi', 'hmbi')]
		exec("self._own_type.tag_config('hpa'," + theme['python:keywords'].replace('type_', 'self._own_type') + ')')
		exec("self._own_type.tag_config('hpb'," + theme['python:inbuilt'].replace('type_', 'self._own_type') + ')')
		exec("self._own_type.tag_config('hpv'," + theme['python:variable_names'].replace('type_', 'self._own_type') + ')')
		exec("self._own_type.tag_config('hpi'," + theme['python:class_instances'].replace('type_', 'self._own_type') + ')')
		exec("self._own_type.tag_config('hpf'," + theme['python:function_names'].replace('type_', 'self._own_type') + ')')
		exec("self._own_type.tag_config('hpx'," + theme['python:class_names'].replace('type_', 'self._own_type') + ')')
		exec("self._own_type.tag_config('hpfa'," + theme['python:function_arguments'].replace('type_', 'self._own_type') + ')')
		exec("self._own_type.tag_config('hpm'," + theme['python:module_names'].replace('type_', 'self._own_type') + ')')
		exec("self._own_type.tag_config('hpo'," + theme['python:operators'].replace('type_', 'self._own_type') + ')')
		exec("self._own_type.tag_config('hpd'," + theme['python:strings'].replace('type_', 'self._own_type') + ')')
		exec("self._own_type.tag_config('hpc'," + theme['python:comments'].replace('type_', 'self._own_type') + ')')
		exec("self._own_type.tag_config('hla'," + theme['latex:inlinemath'].replace('type_', 'self._own_type') + ')')
		exec("self._own_type.tag_config('hlb'," + theme['latex:environment'].replace('type_', 'self._own_type') + ')')
		exec("self._own_type.tag_config('hld'," + theme['latex:commands'].replace('type_', 'self._own_type') + ')')
		exec("self._own_type.tag_config('hle'," + theme['latex:arguments'].replace('type_', 'self._own_type') + ')')
		exec("self._own_type.tag_config('hlf'," + theme['latex:operators'].replace('type_', 'self._own_type') + ')')
		exec("self._own_type.tag_config('hlg'," + theme['latex:square_brackets'].replace('type_', 'self._own_type') + ')')
		exec("self._own_type.tag_config('hlh'," + theme['latex:comments'].replace('type_', 'self._own_type') + ')')
		exec("self._own_type.tag_config('hstuff'," + theme['html:tags'].replace('type_', 'self._own_type') + ')')
		exec("self._own_type.tag_config('hattr'," + theme['html:attributes'].replace('type_', 'self._own_type') + ')')
		exec("self._own_type.tag_config('hstr'," + theme['html:quotes'].replace('type_', 'self._own_type') + ')')
		exec("self._own_type.tag_config('hcmt'," + theme['html:comments'].replace('type_', 'self._own_type') + ')')
		exec("self._own_type.tag_config('hmh1'," + theme['markdown:headers1'].replace('type_', 'self._own_type') + ')')
		exec("self._own_type.tag_config('hmh2'," + theme['markdown:headers2'].replace('type_', 'self._own_type') + ')')
		exec("self._own_type.tag_config('hmh3'," + theme['markdown:headers3'].replace('type_', 'self._own_type') + ')')
		exec("self._own_type.tag_config('hmh4'," + theme['markdown:headers4'].replace('type_', 'self._own_type') + ')')
		exec("self._own_type.tag_config('hmh5'," + theme['markdown:headers5'].replace('type_', 'self._own_type') + ')')
		exec("self._own_type.tag_config('hmh6'," + theme['markdown:headers6'].replace('type_', 'self._own_type') + ')')
		exec("self._own_type.tag_config('hmb'," + theme['markdown:bold'].replace('type_', 'self._own_type') + ')')
		exec("self._own_type.tag_config('hmi'," + theme['markdown:italic'].replace('type_', 'self._own_type') + ')')
		exec("self._own_type.tag_config('hmbi'," + theme['markdown:bold_italic'].replace('type_', 'self._own_type') + ')')
		exec("self._own_type.tag_config('hms'," + theme['markdown:strike'].replace('type_', 'self._own_type') + ')')
		exec("self._own_type.tag_config('hmc'," + theme['markdown:inlinecode'].replace('type_', 'self._own_type') + ')')
		exec("self._own_type.tag_config('hml'," + theme['markdown:links'].replace('type_', 'self._own_type') + ')')
		exec("self._own_type.tag_config('hmq'," + theme['markdown:blockquotes'].replace('type_', 'self._own_type') + ')')
		exec("self._own_type.tag_config('hmf'," + theme['markdown:codeblocks'].replace('type_', 'self._own_type') + ')')
		exec("self._own_type.tag_config('marked'," + theme['pynotes:marked'].replace('type_', 'self._own_type') + ')')
	def init_pythonshell_hl_tags(self):
		exec("self.shellcmd.tag_config('hpa'," + theme['python:keywords'].replace('type_', 'self.shellcmd') + ')')
		exec("self.shellcmd.tag_config('hpb'," + theme['python:inbuilt'].replace('type_', 'self.shellcmd') + ')')
		exec("self.shellcmd.tag_config('hpv'," + theme['python:variable_names'].replace('type_', 'self.shellcmd') + ')')
		exec("self.shellcmd.tag_config('hpi'," + theme['python:class_instances'].replace('type_', 'self.shellcmd') + ')')
		exec("self.shellcmd.tag_config('hpf'," + theme['python:function_names'].replace('type_', 'self.shellcmd') + ')')
		exec("self.shellcmd.tag_config('hpx'," + theme['python:class_names'].replace('type_', 'self.shellcmd') + ')')
		exec("self.shellcmd.tag_config('hpfa'," + theme['python:function_arguments'].replace('type_', 'self.shellcmd') + ')')
		exec("self.shellcmd.tag_config('hpm'," + theme['python:module_names'].replace('type_', 'self.shellcmd') + ')')
		exec("self.shellcmd.tag_config('hpo'," + theme['python:operators'].replace('type_', 'self.shellcmd') + ')')
		exec("self.shellcmd.tag_config('hpd'," + theme['python:strings'].replace('type_', 'self.shellcmd') + ')')
		exec("self.shellcmd.tag_config('hpc'," + theme['python:comments'].replace('type_', 'self.shellcmd') + ')')
	def init_plugin_tags(self):
		for ft, entry in plugin_hl.items():
			mapping = None
			if isinstance(entry, dict):
				if 'hl' not in entry:
					mapping = entry
			elif not callable(entry):
				mapping = entry
			if mapping is None:
				continue
			for tag, (pat, theme_key) in mapping.items():
				try:
					exec("self._own_type.tag_config('" + tag + "'," + theme[theme_key].replace('type_', 'self._own_type') + ')')
				except Exception:
					pass
	def selupdate(self):
		if self.selectionpoint:
			self.type_.tag_remove('sel', '1.0', 'end')
			if self.type_.compare(self.selectionpoint, '<=', 'insert'):
				self.type_.tag_add('sel', self.selectionpoint, 'insert')
			else:
				self.type_.tag_add('sel', 'insert', self.selectionpoint)
	def keypress(self):
		if not self.winfo_exists():
			return
		self.selupdate()
		self._python_edit_generation[0] += 1
		self.ln.redraw()
		self.trigger_filesize()
		if self.hmode == 'python':
			self.tabs.tab(self.sf, state = 'normal')
			self.python_trigger_name_scan()
		else:
			self.tabs.tab(self.sf, state = 'hidden')
			self.trigger_ha(self.hmode)
		if self.title:
			self.filename.config(text = os.path.basename(self.title))
		else:
			if (self.view_master or self) is active and not pcsettitle:
				root.title('PyNotes - Untitled')
				self.filesaved.config(text = 'Untitled File')
			self.filename.config(text = 'Untitled')
		self.trigger_unsaved()
		if not self.title:
			if self.type_.get('1.0', 'end-1c'):
				self.unsaved = True
			else:
				self.unsaved = False
		if self.hmode in ['png', 'pdf', 'epub']:
			if (self.view_master or self) is active:
				root.title('PyNotes - ' + os.path.basename(self.title))
			self.filesaved.config(text = 'Read Only File')
		for member in self._group_members():
			if member is not self:
				member.filename.config(text = self.filename.cget('text'))
	def sethmenu(self, mode):
		try:
			self.m.delete('Python')
		except Exception:
			pass
		try:
			self.m.delete('LaTeX')
		except Exception:
			pass
		if mode == 'python':
			self.m.insert_cascade(self.m.index('Options') + 1, label = 'Python', menu = pm)
		elif mode == 'latex':
			self.m.insert_cascade(self.m.index('Options') + 1, label = 'LaTeX', menu = lm)
	def pchmode(self, mode):
		if self.view_master:
			return self.view_master.pchmode(mode)
		if self.hmode in ['png', 'pdf', 'epub']:
			return
		pcrunhook('before', 'change-hmode', mode)
		[self.type_.tag_remove(tag, '1.0', 'end') for tag in ('hpa', 'hpb', 'hpv', 'hpi', 'hpf', 'hpx', 'hpfa', 'hpm', 'hpo', 'hpd', 'hpc', 'hla', 'hlb', 'hld', 'hle', 'hlf', 'hlg', 'hlh', 'hstuff', 'hattr', 'hstr', 'hcmt', 'hmh1', 'hmh2', 'hmh3', 'hmh4', 'hmh5', 'hmh6', 'hmb', 'hmi', 'hmbi')]
		if mode == 'python' or mode == 'py':
			self.sethmenu('python')
			self.tabs.tab(self.ef, state = 'hidden')
			self.lfouter.pack_forget()
			self.hmode = 'python'
			self.filetype.config(text = 'Python File (*.py)')
			self.python_trigger_name_scan()
		elif mode == 'latex' or mode == 'la':
			self.sethmenu('latex')
			self.tabs.tab(self.ef, state = 'hidden')
			self.lfouter.pack(padx = 10, pady = 10, side = 'top', fill = 'x', before = self.fileinfo)
			self.hmode = 'latex'
			self.filetype.config(text = 'LaTeX / TeX File (*.tex)')
		elif mode == 'normal' or mode == 'norm':
			self.sethmenu(None)
			self.tabs.tab(self.ef, state = 'hidden')
			self.lfouter.pack_forget()
			self.hmode = 'normal'
			self.filetype.config(text = 'Plain Text (*.*)')
		elif mode == 'email' or mode == 'em':
			self.sethmenu(None)
			self.hmode = 'email'
			self.filetype.config(text = 'Plain Text (*.*) (Email)')
			self.tabs.tab(self.ef, state = 'normal')
		elif mode == 'html':
			self.sethmenu(None)
			self.hmode = 'html'
			self.filetype.config(text = 'HTML File (*.html)')
			self.tabs.tab(self.ef, state = 'hidden')
			self.lfouter.pack_forget()
		elif mode == 'markdown' or mode == 'md':
			self.sethmenu(None)
			self.tabs.tab(self.ef, state = 'hidden')
			self.lfouter.pack_forget()
			self.hmode = 'markdown'
			self.filetype.config(text = 'Markdown File (*.md)')
		elif mode in plgnhmodes:
			try:
				self.hmode = mode
				exec(plgnhmodes[mode][1])
			except Exception as error:
				error = str(error)
				root.error('Error!', f'There was an error in switching to the HMode {mode} from the plugin "{os.path.basename(os.path.normpath(plgnhmodes[mode][0]))}":\n{error}')
		show(f'{self.hmode} hmode')
		self.keypress()
		for child in self.view_children:
			child._sync_chrome()
		pcrunhook('after', 'change-hmode', mode)
	def pccommentregion(self, start, end):
		if not self.hmode in ('python', 'latex', 'html'):
			return
		pcrunhook('before', 'comment-region', (start, end))
		ender = ''
		if self.hmode == 'python':
			commentor = '#'
		elif self.hmode == 'latex':
			commentor = '%'
		elif self.hmode == 'html' or self.hmode == 'markdown':
			commentor = '<!--'
			ender = '-->'
		l = start
		self.type_.edit_separator()
		while not l > end:
			if not self.type_.get(f'{l}.0', f'{l}.end').strip():
				l += 1
				continue
			self.type_.insert(f'{l}.0', commentor)
			self.type_.insert(f'{l}.end', ender)
			l += 1
		self.type_.edit_separator()
		show('comment region')
		self.keypress()
		pcrunhook('after', 'comment-region', (start, end))
	def pccommentselection(self):
		if not self.hmode in ('python', 'latex', 'html', 'markdown'):
			return
		try:
			start = int(self.type_.index('sel.first').split('.')[0])
			end = int(self.type_.index('sel.last').split('.')[0])
		except Exception:
			show('nothing is selected')
			return
		else:
			pcrunhook('before', 'comment-region', (start, end))
			ender = ''
			if self.hmode == 'python':
				commentor = '#'
			elif self.hmode == 'latex':
				commentor = '%'
			elif self.hmode == 'html' or self.hmode == 'markdown':
				commentor = '<!--'
				ender = '-->'
			l = start
			self.type_.edit_separator()
			while not l > end:
				if not self.type_.get(f'{l}.0', f'{l}.end').strip():
					l += 1
					continue
				self.type_.insert(f'{l}.0', commentor)
				self.type_.insert(f'{l}.end', ender)
				l += 1
			self.type_.edit_separator()
		show('comment selection')
		self.keypress()
		pcrunhook('after', 'comment-region', (start, end))
	def pcuncommentregion(self, start, end):
		if not self.hmode in ('python', 'latex', 'html', 'markdown'):
			return
		pcrunhook('before', 'uncomment-region', (start, end))
		self.type_.edit_separator()
		ender = ''
		if self.hmode == 'python':
			commentor = '#'
		elif self.hmode == 'latex':
			commentor = '%'
		elif self.hmode == 'html' or self.hmode == 'markdown':
			commentor = '<!--'
			ender = '-->'
		l = start
		while not l > end:
			stripped = self.type_.get(f'{l}.0', f'{l}.end').lstrip()
			if stripped.startswith(commentor):
				a = len(self.type_.get(f'{l}.0', f'{l}.end')) - len(stripped)
				b = a + len(commentor)
				self.type_.delete(f'{l}.{a}', f'{l}.{b}')
			if ender:
				stripped = self.type_.get(f'{l}.0', f'{l}.end').rstrip()
				if stripped.endswith(ender):
					self.type_.delete(f'{l}.end-{len(ender)}c', f'{l}.end')
			l += 1
		self.type_.edit_separator()
		show('uncomment region')
		self.keypress()
		pcrunhook('after', 'uncomment-region', (start, end))
	def pcuncommentselection(self):
		if not self.hmode in ('python', 'latex', 'html', 'markdown'):
			return
		try:
			start = int(self.type_.index('sel.first').split('.')[0])
			end = int(self.type_.index('sel.last').split('.')[0])
		except Exception:
			show('nothing is selected')
			return
		else:
			pcrunhook('before', 'uncomment-region', (start, end))
			self.type_.edit_separator()
			ender = ''
			if self.hmode == 'python':
				commentor = '#'
			elif self.hmode == 'latex':
				commentor = '%'
			elif self.hmode == 'html' or self.hmode == 'markdown':
				commentor = '<!--'
				ender = '-->'
			l = start
			while not l > end:
				stripped = self.type_.get(f'{l}.0', f'{l}.end').lstrip()
				if stripped.startswith(commentor):
					a = len(self.type_.get(f'{l}.0', f'{l}.end')) - len(stripped)
					b = a + len(commentor)
					self.type_.delete(f'{l}.{a}', f'{l}.{b}')
				if ender:
					stripped = self.type_.get(f'{l}.0', f'{l}.end').rstrip()
					if stripped.endswith(ender):
						self.type_.delete(f'{l}.end-{len(ender)}c', f'{l}.end')
				l += 1
			self.type_.edit_separator()
			show('uncomment selection')
			self.keypress()
			pcrunhook('after', 'uncomment-region', (start, end))
	def pccleareditor(self):
		if root.ask('Warning', 'Clear the active editor?', options = ('ok', 'cancel')):
			pcrunhook('before', 'clear-editor')
			self.type_.edit_separator()
			self.type_.delete('1.0', 'end')
			self.type_.edit_separator()
			show('cleared editor')
			pcrunhook('after', 'clear-editor')
	def pcselecttext(self, a, b):
		self.type_.tag_remove('sel', '1.0', 'end')
		self.type_.tag_add('sel', a, b)
		show(f'selected text from {a} to {b}')
	def pcgetselection(self):
		try:
			start = self.type_.index('sel.first')
			end = self.type_.index('sel.last')
			ans = (str(start), str(end))
		except Exception:
			ans = tuple()
		return ans
	def pcmark(self, a, b = None):
		if not b:
			a, b = a[0], a[1]
		pcrunhook('before', 'mark-region', (a, b))
		self.type_.tag_add('marked', a, b)
		show(f'marked text from {a} to {b}')
		pcrunhook('after', 'mark-region', (a, b))
	def pcmarkselection(self):
		try:
			start = self.type_.index('sel.first')
			end = self.type_.index('sel.last')
		except Exception:
			return
		pcrunhook('before', 'mark-region', (start, end))
		self.type_.tag_add('marked', start, end)
		show(f'marked text from {start} to {end}')
		pcrunhook('after', 'mark-region', (start, end))
	def pcunmark(self, a, b = None):
		if not b:
			a, b = a[0], a[1]
		pcrunhook('before', 'unmark-region', (a, b))
		self.type_.tag_remove('marked', a, b)
		show(f'unmarked text from {a} to {b}')
		pcrunhook('after', 'unmark-region', (a, b))
	def pcunmarkall(self):
		self.type_.tag_remove('marked', '1.0', 'end')
		show(f'unmarked all text')
	def pctkindex(self, toindex, line = False):
		ans = self.type_.index(toindex)
		if line == 'line':
			ans = ans.split('.')[0]
		return ans
	def pcdelete(self, *args, **kwargs):
		show('delete text')
		self.type_.delete(*args, **kwargs)
	def pcmovecursor(self, index):
		self.type_.mark_set('insert', index)
		self.type_.see(index)
	def pcswitchemailtab(self):
		if self.hmode == 'email':
			pcrunhook('before', 'switch-to-email-tab')
			self.tabs.select(self.ef)
			show('switched to email tab')
			pcrunhook('after', 'switch-to-email-tab')
		else:
			show('not in email hmode')
	def pcpyshell(self):
		if self.hmode == 'python':
			pcrunhook('before', 'switch-to-python-shell-tab')
			self.tabs.select(self.sf)
			self.shellcmd.focus()
			show('switch to python shell')
			self.keypress()
			pcrunhook('after', 'switch-to-python-shell-tab')
		else:
			show('not in python hmode')
	def _pcpyresolve(self, commandinput):
		if self.hmode != 'python':
			show('not in python hmode')
			return None
		raw = commandinput.strip()
		word = raw.lower()
		if word in ('f', 'fun', 'func', 'function', 'c', 'class'):
			wantclass = word in ('c', 'class')
			want_scope_kind = 'class' if wantclass else 'function'
			want_def_kind = 'class' if wantclass else 'func'
			line = int(self.type_.index('insert').split('.')[0])
			defs_by_start = {}
			for dl, dc, dname, dkind in self._python_def_names:
				if dkind == want_def_kind:
					defs_by_start[dl] = dname
			best = None
			for sc in self._python_scopes:
				if sc.get('kind') != want_scope_kind:
					continue
				if not (sc['start'] <= line <= sc['end']):
					continue
				if sc['start'] not in defs_by_start:
					continue
				if best is None or sc['start'] > best[0]:
					best = (sc['start'], sc['end'], defs_by_start[sc['start']])
			if best is None:
				show('error: currently in no class' if wantclass else 'error: currently in no function')
				return None
			startline, endline, name = best
			return startline, endline, name, want_def_kind
		for dl, dc, dname, dkind in self._python_def_names:
			if dname == raw:
				want_scope_kind = 'class' if dkind == 'class' else 'function'
				endline = dl
				for sc in self._python_scopes:
					if sc.get('kind') == want_scope_kind and sc['start'] == dl:
						endline = sc['end']
						break
				return dl, endline, dname, dkind
		show(f'error: function or class \'{raw}\' does not exist in current editor')
		return None
	def pcpystartof(self, commandinput):
		result = self._pcpyresolve(commandinput)
		if result is None:
			return
		startline, endline, name, kind = result
		label = 'class' if kind == 'class' else 'function'
		self.pcmovecursor(f'{startline}.end')
		self.keypress()
		show(f'jumped to start of {label} \'{name}\'')
	def pcpyendof(self, commandinput):
		result = self._pcpyresolve(commandinput)
		if result is None:
			return
		startline, endline, name, kind = result
		label = 'class' if kind == 'class' else 'function'
		self.pcmovecursor(f'{endline}.end')
		self.keypress()
		show(f'jumped to end of {label} {name}')
	def pcgovardef(self, commandinput):
		if self.hmode != 'python':
			show('not in python hmode')
			return
		name = commandinput.strip()
		line = int(self.type_.index('insert').split('.')[0])
		scope_idx = None
		best_start = None
		for i, sc in enumerate(self._python_scopes):
			if sc['start'] <= line <= sc['end']:
				if best_start is None or sc['start'] > best_start:
					best_start = sc['start']
					scope_idx = i
		target_line = None
		idx = scope_idx
		while idx is not None:
			sc = self._python_scopes[idx]
			bindings = sc['names'].get(name)
			if bindings:
				candidates = [ln for ln, kd in bindings if ln <= line]
				target_line = max(candidates) if candidates else min(ln for ln, kd in bindings)
				break
			idx = sc['parent']
		if target_line is None:
			show(f'error: variable \'{name}\' does not exist in current editor')
			return
		self.pcmovecursor(f'{target_line}.end')
		self.keypress()
		show(f'jumped to definition of variable \'{name}\'')
	def pcswitchedittab(self):
		pcrunhook('before', 'switch-to-editor-tab')
		self.tabs.select(self.mf)
		self.type_.focus()
		show('switch to editor')
		self.keypress()
		pcrunhook('after', 'switch-to-editor-tab')
	def pccmdwrite(self, text, n):
		self.type_.edit_separator()
		self.type_.insert(self.type_.index('insert'), text * n)
		show(f'wrote \'{text.replace("\n", "\\n")}\' {n} times')
		self.type_.edit_separator()
		self.keypress()
	def pcindentregion(self, start, end):
		pcrunhook('before', 'indent-region', (start, end))
		if taborspace:
			whitespace = '    '
		else:
			whitespace = '	'
		l = start
		self.type_.edit_separator()
		while not l > end:
			if not self.type_.get(f'{l}.0', f'{l}.end').strip():
				l += 1
				continue
			self.type_.insert(f'{l}.0', whitespace)
			l += 1
		self.type_.edit_separator()
		show('indent region')
		self.keypress()
		pcrunhook('after', 'indent-region', (start, end))
	def pcindentselection(self):
		try:
			start = int(self.type_.index('sel.first').split('.')[0])
			end = int(self.type_.index('sel.last').split('.')[0])
		except Exception:
			show('nothing is selected')
			return
		else:
			pcrunhook('before', 'indent-region', (start, end))
			if taborspace:
				whitespace = '    '
			else:
				whitespace = '	'
			l = start
			self.type_.edit_separator()
			while not l == end:
				self.type_.insert(f'{l}.0', whitespace)
				l += 1
			self.type_.insert(f'{l}.0', whitespace)
			self.type_.edit_separator()
			show('indent selection')
			self.keypress()
			pcrunhook('after', 'indent-region', (start, end))
	def pcunindentregion(self, start, end):
		pcrunhook('before', 'unindent-region', (start, end))
		self.type_.edit_separator()
		lines = [self.type_.get(f'{l}.0', f'{l}.end') for l in range(start, end + 1)]
		min_spaces = None
		for line in lines:
			if not line.strip() or line.startswith('\t'):
				continue
			n = len(line) - len(line.lstrip(' '))
			if n > 0 and (min_spaces is None or n < min_spaces):
				min_spaces = n
		if min_spaces is None:
			min_spaces = 4
		for i, l in enumerate(range(start, end + 1)):
			line = lines[i]
			if not line.strip():
				continue
			if line.startswith('\t'):
				self.type_.delete(f'{l}.0', f'{l}.1')
			elif line.startswith(' '):
				remove = 0
				for ch in line:
					if ch == ' ' and remove < min_spaces:
						remove += 1
					else:
						break
				if remove:
					self.type_.delete(f'{l}.0', f'{l}.{remove}')
		self.type_.edit_separator()
		show('unindent region')
		self.keypress()
		pcrunhook('after', 'unindent-region', (start, end))
	def pcunindentselection(self):
		try:
			start = int(self.type_.index('sel.first').split('.')[0])
			end = int(self.type_.index('sel.last').split('.')[0])
		except Exception:
			show('nothing is selected')
			return
		else:
			pcrunhook('before', 'unindent-region', (start, end))
			self.type_.edit_separator()
			lines = [self.type_.get(f'{l}.0', f'{l}.end') for l in range(start, end + 1)]
			min_spaces = None
			for line in lines:
				if not line.strip() or line.startswith('\t'):
					continue
				n = len(line) - len(line.lstrip(' '))
				if n > 0 and (min_spaces is None or n < min_spaces):
					min_spaces = n
			if min_spaces is None:
				min_spaces = 4
			for i, l in enumerate(range(start, end + 1)):
				line = lines[i]
				if not line.strip():
					continue
				if line.startswith('\t'):
					self.type_.delete(f'{l}.0', f'{l}.1')
				elif line.startswith(' '):
					remove = 0
					for ch in line:
						if ch == ' ' and remove < min_spaces:
							remove += 1
						else:
							break
					if remove:
						self.type_.delete(f'{l}.0', f'{l}.{remove}')
			self.type_.edit_separator()
			show('unindent selection')
			self.keypress()
			pcrunhook('after', 'unindent-region', (start, end))
	def rp(self):
		if not self.title:
			f = open(f'{homedir}/.local/share/PyNotes/tempfiles/tempcode', 'w', encoding = 'utf-8')
			f.write(self.type_.get('1.0', 'end-1c'))
			f.close()
			file = f'{homedir}/.local/share/PyNotes/tempfiles/tempcode'
		else:
			file = self.title
			self.sv(file)
		term([pythonexecutable, file], title = file, endmessage = '--- Python code finished, press any key to continue ---', cwd = os.path.dirname(file))
	def hp(self):
		if not self.title:
			f = open(f'{homedir}/.local/share/PyNotes/tempfiles/tempcode', 'w', encoding = 'utf-8')
			f.write(self.type_.get('1.0', 'end-1c'))
			f.close()
			file = f'{homedir}/.local/share/PyNotes/tempfiles/tempcode'
		else:
			file = self.title
			self.sv(file)
		if platform.system() == 'Linux':
			subprocess.run(['xdg-open', file], cwd = os.path.dirname(file))
		else:
			subprocess.run(['start', file], cwd = os.path.dirname(file))
	def runtex(self, compiler):
		if not self.title:
			f = open(f'{homedir}/.local/share/PyNotes/tempfiles/tempcode', 'w', encoding = 'utf-8')
			f.write(self.type_.get('1.0', 'end-1c'))
			f.close()
			file = f'{homedir}/.local/share/PyNotes/tempfiles/tempcode'
		else:
			file = self.title
			self.sv(file)
		compiler += 'latex'
		if not shutil.which(compiler):
			root.error('Error', f'Error in running LaTeX - {compiler} is not installed')
			return
		if os.path.splitext(file)[1] == '.tex':
			pdf_ = os.path.splitext(file)[0]
		else:
			pdf_ = file
		pdf_ += '.pdf'
		try:
			os.remove(pdf_)
		except Exception:
			pass
		term([compiler, file], title = file, endmessage = '--- LaTeX compiling finished, press any key to continue ---', cwd = os.path.dirname(file), blocking = True)
		pdf(file)
	def f5(self):
		if self._file_watch_prompt_pending:
			show('select \'Discard Changes & Reload\' or \'Ignore\' external changes before loading another file')
			return
		pcrunhook('before', 'run-code')
		if self.hmode == 'python':
			self.rp()
		elif self.hmode == 'latex':
			self.runtex('lua')
		elif self.hmode == 'html':
			self.hp()
		else:
			show('hmode not in python / latex / html')
			return
		show(f'run {self.hmode} code')
		pcrunhook('after', 'run-code')
	def indent(self):
		self.type_.edit_separator()
		if not self.hmode == 'python':
			return
		l = int(self.type_.index('insert').split('.')[0])
		self.type_.insert(f'insert', '\n')
		line = self.type_.get(f'{l}.0', f'{l}.end')
		whitespace = re.match(r'\s*', line).group()
		self.type_.insert(f'{l + 1}.0', whitespace)
		line = re.sub(r'\'[^\'\\]*(?:\\.[^\'\\]*)*\'|"[^"\\]*(?:\\.[^"\\]*)*"', '', line)
		line = re.sub(r'#.*', '', line).strip()
		if taborspace:
			indentthing = '    '
		else:
			indentthing = '	'
		if not line:
			return 'break'
		if line[-1] == ':':
			self.type_.insert(f'{l + 1}.0', indentthing)
		self.type_.edit_separator()
		return 'break'
	def gl(self, l = None):
		if l is None:
			l = prompt('Go to line: ')
		if type(l) == str:
			l = l.strip()
		if not l:
			return
		try:
			l = int(l)
		except Exception:
			show(f'cannot go to line number \'{l}\'')
			return
		else:
			show(f'go to line no. {l}')
			self.type_.see(f'{l}.0')
			self.type_.mark_set('insert', f'{l}.0')
			self.type_.tag_add('sel', f'{l}.0', f'{l}.end')
	def selall(self):
		show('select all text')
		self.type_.tag_add('sel', '1.0', 'end')
		return 'break'
	def cp(self):
		try:
			select = self.type_.get('sel.first', 'sel.last')
		except Exception:
			show('no text is selected')
			return
		else:
			pcrunhook('before', 'copy-text', select)
			show('copy text')
		root.clipboard_clear()
		root.clipboard_append(select)
		pcrunhook('after', 'copy-text', select)
	def cut(self):
		try:
			select = self.type_.get('sel.first', 'sel.last')
		except Exception:
			show('no text is selected')
			return
		else:
			pcrunhook('before', 'cut-text', select)
			show('cut text')
		self.type_.delete('sel.first', 'sel.last')
		root.clipboard_clear()
		root.clipboard_append(select)
		show('cut text')
		pcrunhook('after', 'cut-text', select)
	def spk(self):
		try:
			select = self.type_.get('sel.first', 'sel.last')
		except Exception:
			show('no text is selected')
			return
		else:
			show('speak selected text')
			speakthread = threading.Thread(target = actualspk, args = (select,), daemon = True)
			speakthread.start()
	def pst(self):
		try:
			text = root.clipboard_get()
		except Exception:
			show('no text is on clipboard')
			return
		else:
			pcrunhook('before', 'paste-text', text)
			show('paste text')
		self.type_.edit_separator()
		self.type_.insert('insert', text)
		self.type_.edit_separator()
		pcrunhook('after', 'paste-text', text)
		return 'break'
	def ptb(self):
		if self.type_.yview()[0] == 0.0:
			show('already at beginning')
			return
		pcrunhook('before', 'previous-page')
		self.type_.yview_scroll(-1, 'pages')
		show('go to previous page')
		pcrunhook('after', 'previous-page')
	def ptf(self):
		if self.type_.yview()[1] == 1.0:
			show('already at end')
			return
		pcrunhook('before', 'next-page')
		self.type_.yview_scroll(1, 'pages')
		show('go to next page')
		pcrunhook('after', 'next-page')
	def undo(self):
		pcrunhook('before', 'undo')
		try:
			self.type_.edit_undo()
			show('undoed edit')
			pcrunhook('after', 'undo')
		except Exception:
			show('nothing to undo')
	def redo(self):
		pcrunhook('before', 'redo')
		try:
			self.type_.edit_redo()
			show('redoed edit')
			pcrunhook('after', 'redo')
		except Exception:
			show('nothing to redo')
	def _main_poll(self):
		try:
			while True:
				task = self._main_queue.get_nowait()
				task()
		except Exception:
			pass
		self._main_poll_after_id = self._own_type.after(10, self._main_poll)
	def type_setview(self):
		new_region = self.type_getvisible()
		if new_region != self._prev_visible_region:
			self._prev_visible_region = new_region
			self.type_top, self.type_bottom = new_region
			self.trigger_ha(self.hmode)
		else:
			self.type_top, self.type_bottom = new_region
		self._type_setview_after_id = self.mf.after(10, self.type_setview)
	def do_backup(self):
		if all((not self.hmode in ['png', 'pdf', 'epub'], bfr, self.title)):
			open(os.path.join(os.path.dirname(os.path.splitext(self.title)[0]), '.' + os.path.basename(os.path.splitext(self.title)[0]) + 'backpynotes' + os.path.splitext(self.title)[1]), 'w+', encoding = 'utf-8').write(self.type_.get('1.0', 'end'))
			show('saved backup')
		self._do_backup_after_id = self.mf.after(10000, self.do_backup)
	def emailsetup(self, saved = None):
		global e
		global p
		global s
		global po
		attachments = []
		def removeattach():
			def actualremoveattachment(attachment):
				del self.attachmentslist[attachment]
				del attachments[attachment]
				self.attachmentslistwidget.config(text = 'Attachments: ' + ' , '.join(self.attachmentslist))
				raw.destroy()
			if self.attachmentslist:
				raw = root.subwin()
				for i in range(len(self.attachmentslist)):
					attachment = self.attachmentslist[i]
					raw.button(text = attachment, command = lambda i = i: actualremoveattachment(i)).grid(column = i % 5, row = mathmod.floor(i / 5), sticky = 'ew')
		def attach():
			fn = openfileget(prompttext = 'Email Attachment File: ', filetypes = (('All Files', '*')))
			if fn:
				try:
					with open(fn, 'rb') as attachment:
						part = MIMEBase('application', 'octet-stream')
						part.set_payload(attachment.read())
						encoders.encode_base64(part)
						part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(fn)}')
						if not os.path.basename(fn) in self.attachmentslist:
							attachments.append(part)
							self.attachmentslist.append(os.path.basename(fn))
							self.attachmentslistwidget.config(text = 'Attachments: ' + ' , '.join(self.attachmentslist))
				except Exception as error:
					error = str(error)
					root.error('Error', error)
		def changeinfo():
			def emailsetupother():
				global e
				global p
				global s
				global po
				self.entryframe.pack(padx = 10, pady = 10, fill = 'x', anchor = 'n', expand = True)
				self.buttonframe.pack(padx = 10, pady = 10, fill = 'x', anchor = 'n', expand = True)
				self.emailtextbox.pack(fill = 'both', expand = True, padx = 10, pady = 10)
				e = self.email.get()
				p = self.password.get()
				s = self.server.get()
				po = self.port.get()
				file = open(f'{homedir}/.pynotesemailconfig', 'w+', encoding = 'utf-8')
				file.write(f'{e}\n{p}\n{s}\n{po}')
				file.close()
				encryptdecrypt(f'{homedir}/.pynotesemailconfig')
				self.loginframe.pack_forget()
			self.entryframe.pack_forget()
			self.buttonframe.pack_forget()
			self.emailtextbox.pack_forget()
			self.loginframe = root.frame(master = self.ef)
			self.loginframe.pack(expand = True)
			root.text(master = self.loginframe, text = 'Email:').grid(column = 0, row = 0, padx = 10, pady = 10)
			self.email = root.entry(master = self.loginframe)
			self.email.grid(column = 1, row = 0, padx = 10, pady = 10)
			root.text(master = self.loginframe, text = 'Password:').grid(column = 0, row = 1, padx = 10, pady = 10)
			self.password = root.entry(master = self.loginframe, show = '*')
			self.password.grid(column = 1, row = 1, padx = 10, pady = 10)
			root.text(master = self.loginframe, text = 'Smtp Server:').grid(column = 0, row = 2, padx = 10, pady = 10)
			self.server = root.entry(master = self.loginframe)
			self.server.grid(column = 1, row = 2, padx = 10, pady = 10)
			root.text(master = self.loginframe, text = 'Smtp Port:').grid(column = 0, row = 3, padx = 10, pady = 10)
			self.port = root.entry(master = self.loginframe)
			self.port.grid(column = 1, row = 3, padx = 10, pady = 10)
			root.button(master = self.loginframe, text = 'Done', command = emailsetupother).grid(column = 1, row = 4, padx = 10, pady = 10, sticky = 'e')
			self._bind_focus_recursive(self.loginframe)
		def sendemail():
			global e
			global p
			global s
			global po
			recipients = self.recipiententry.get().split(',')
			subject = self.subjectentry.get()
			if not subject:
				subject = '(No Subject)'
			body = self.emailtextbox.get('1.0', 'end-1c')
			for recipient in recipients:
				if recipient:
					message = MIMEMultipart()
					message['From'] = e
					message['To'] = recipient
					message['Subject'] = subject
					message.attach(MIMEText(body, 'plain'))
					try:
						for attachment in attachments:
							message.attach(attachment)
						with smtplib.SMTP_SSL(s, po) as server:
							server.login(e, p)
							server.sendmail(e, recipient, message.as_string())
					except Exception as error:
						error = str(error)
						root.error('Error', error)
						show('email failed')
						return
			self.emailtextbox.delete('1.0', 'end')
			self.recipiententry.delete(0, 'end')
			attachments.clear()
			self.attachmentslist.clear()
			self.attachmentslistwidget.config(text = 'Attachments:')
			self.subjectentry.delete(0, 'end')
			show('email sent')
			root.info('Info', 'Email Sent Successfully!')
			return 'break'
		def spellcheck():
			if not emailwordlist:
				return
			self.emailtextbox.tag_remove('wrong', '1.0', 'end')
			n = '1.0'
			search = r'\w+'
			while True:
				count = root.intvar()
				n = self.emailtextbox.search(search, n, nocase = 1, count = count, stopindex = 'end', regexp = True)
				if not n:
					break
				nn = '%s+%dc' % (n, count.get())
				if not self.emailtextbox.get(n, nn).lower() in emailwordlist and len(self.emailtextbox.get(n, nn)) > 1:
					try:
						int(self.emailtextbox.get(n, nn))
					except Exception:
						self.emailtextbox.tag_add('wrong', n, nn)
				n = nn
			n = '1.0'
		if not saved:
			e = self.email.get()
			p = self.password.get()
			s = self.server.get()
			po = self.port.get()
			self.loginframe.pack_forget()
			ans = root.ask('', 'Do you want PyNotes to save your email and password?', ['yes', 'no'])
			if ans:
				file = open(f'{homedir}/.pynotesemailconfig', 'w+', encoding = 'utf-8')
				file.write(f'{e}\n{p}\n{s}\n{po}')
				file.close()
				encryptdecrypt(f'{homedir}/.pynotesemailconfig')
		elif saved == 'file':
			encryptdecrypt(f'{homedir}/.pynotesemailconfig')
			file = open(f'{homedir}/.pynotesemailconfig', 'r', encoding = 'utf-8').read().split('\n')
			encryptdecrypt(f'{homedir}/.pynotesemailconfig')
			e = file[0]
			p = file[1]
			s = file[2]
			po = file[3]
		self._email_logged_in = True
		self.entryframe = root.frame(master = self.ef)
		self.recipiententry = root.entry(master = self.entryframe)
		root.text(master = self.entryframe, text = 'Recipients (separate by commas):').grid(column = 0, row = 0, padx = 10, pady = 10, sticky = 'e')
		self.recipiententry.grid(column = 1, row = 0, padx = 10, pady = 10, sticky = 'ew')
		root.text(master = self.entryframe, text = 'Subject:').grid(column = 0, row = 1, padx = 10, pady = 10, sticky = 'e')
		self.subjectentry = root.entry(master = self.entryframe)
		self.subjectentry.grid(column = 1, row = 1, padx = 10, pady = 10, sticky = 'ew')
		self.entryframe.pack(padx = 10, pady = 10, fill = 'both', anchor = 'n', expand = True)
		self.entryframe.columnconfigure(1, weight = 1)
		self.buttonframe = root.frame(master = self.ef)
		self.buttonframe.pack(padx = 10, pady = 10, fill = 'both', anchor = 'n', expand = True)
		root.button(master = self.buttonframe, text = 'Send (Ctrl + Enter)', command = sendemail).pack(fill = 'x', expand = True, padx = 10, pady = 10, side = 'left', anchor = 'n')
		root.button(master = self.buttonframe, text = 'Attach', command = attach).pack(fill = 'x', expand = True, padx = 10, pady = 10, side = 'right', anchor = 'n')
		root.button(master = self.buttonframe, text = 'Change Info', command = changeinfo).pack(fill = 'x', expand = True, padx = 10, pady = 10, side = 'left', anchor = 'n')
		root.button(master = self.buttonframe, text = 'Remove Attachment', command = removeattach).pack(fill = 'x', expand = True, padx = 10, pady = 10, side = 'right', anchor = 'n')
		self.attachmentslist = []
		self.attachmentslistwidget = root.text(master = self.buttonframe, text = 'Attachments:')
		self.attachmentslistwidget.pack(fill = 'x', expand = True, padx = 10, pady = 10)
		self.emailtextbox = root.textbox(master = self.ef, scrolled = True, font = (monospace, 15))
		self.emailtextbox.tag_config('wrong', underline = True, underlinefg = 'red')
		self.emailtextbox.pack(fill = 'both', expand = True, padx = 10, pady = 10)
		self.emailtextbox.bind('<Control-Return>', lambda event: sendemail())
		self.emailtextbox.bind('<KeyRelease>', lambda event: spellcheck())
		self._bind_focus_recursive(self.ef)
	def _email_session_active(self):
		try:
			e, p, s, po
		except Exception:
			return False
		return bool(e and p and s and po)
	def _add_switch_account_loginframe(self):
		self.loginframe = root.frame(master = self.ef)
		self.loginframe.pack(expand = True)
		root.text(master = self.loginframe, text = 'Email:').grid(column = 0, row = 0, padx = 10, pady = 10)
		self.email = root.entry(master = self.loginframe)
		self.email.grid(column = 1, row = 0, padx = 10, pady = 10)
		root.text(master = self.loginframe, text = 'Password:').grid(column = 0, row = 1, padx = 10, pady = 10)
		self.password = root.entry(master = self.loginframe, show = '*')
		self.password.grid(column = 1, row = 1, padx = 10, pady = 10)
		root.text(master = self.loginframe, text = 'Smtp Server:').grid(column = 0, row = 2, padx = 10, pady = 10)
		self.server = root.entry(master = self.loginframe)
		self.server.grid(column = 1, row = 2, padx = 10, pady = 10)
		root.text(master = self.loginframe, text = 'Smtp Port:').grid(column = 0, row = 3, padx = 10, pady = 10)
		self.port = root.entry(master = self.loginframe)
		self.port.grid(column = 1, row = 3, padx = 10, pady = 10)
		root.button(master = self.loginframe, text = 'Let\'s Go!', command = self.emailsetup).grid(column = 1, row = 4, padx = 10, pady = 10, sticky = 'e')
		self._bind_focus_recursive(self.loginframe)
	def _email_tab_reload(self):
		for child in self.ef.winfo_children():
			child.destroy()
		self.emailsetup('memory')
		self._add_switch_account_loginframe()
	def _email_login_poll(self):
		if not self._email_logged_in and self._email_session_active():
			self._email_tab_reload()
		self._email_login_poll_after_id = self.ef.after(2000, self._email_login_poll)
	def _email_login_setup(self):
		if self._email_session_active():
			self.emailsetup('memory')
			self._add_switch_account_loginframe()
			return
		try:
			open(f'{homedir}/.pynotesemailconfig', 'r', encoding = 'utf-8')
		except Exception:
			self.loginframe = root.frame(master = self.ef)
			self.loginframe.pack(expand = True)
			root.text(master = self.loginframe, text = 'Email:').grid(column = 0, row = 0, padx = 10, pady = 10)
			self.email = root.entry(master = self.loginframe)
			self.email.grid(column = 1, row = 0, padx = 10, pady = 10)
			root.text(master = self.loginframe, text = 'Password:').grid(column = 0, row = 1, padx = 10, pady = 10)
			self.password = root.entry(master = self.loginframe, show = '*')
			self.password.grid(column = 1, row = 1, padx = 10, pady = 10)
			root.text(master = self.loginframe, text = 'Smtp Server:').grid(column = 0, row = 2, padx = 10, pady = 10)
			self.server = root.entry(master = self.loginframe)
			self.server.grid(column = 1, row = 2, padx = 10, pady = 10)
			root.text(master = self.loginframe, text = 'Smtp Port:').grid(column = 0, row = 3, padx = 10, pady = 10)
			self.port = root.entry(master = self.loginframe)
			self.port.grid(column = 1, row = 3, padx = 10, pady = 10)
			root.button(master = self.loginframe, text = 'Let\'s Go!', command = self.emailsetup).grid(column = 1, row = 4, padx = 10, pady = 10, sticky = 'e')
			self._bind_focus_recursive(self.loginframe)
		else:
			try:
				self.emailsetup('file')
			except Exception:
				root.error('Error', 'The saved email details are corrupted. Remaking file.')
				os.remove(f'{homedir}/.pynotesemailconfig')
			self._add_switch_account_loginframe()
	def boldlatex(self):
		try:
			select = self.type_.get('sel.first', 'sel.last')
		except Exception:
			return
		self.type_.edit_separator()
		self.type_.delete('sel.first', 'sel.last')
		self.type_.insert('insert', '{\\bf ' + select + '}')
		self.type_.edit_separator()
		show('bold text latex')
		self.keypress()
	def italiclatex(self):
		try:
			select = self.type_.get('sel.first', 'sel.last')
		except Exception:
			return
		self.type_.edit_separator()
		self.type_.delete('sel.first', 'sel.last')
		self.type_.insert('insert', '\\textit{' + select + '}')
		self.type_.edit_separator()
		show('italic text latex')
		self.keypress()
	def underlinelatex(self):
		try:
			select = self.type_.get('sel.first', 'sel.last')
		except Exception:
			return
		self.type_.edit_separator()
		self.type_.delete('sel.first', 'sel.last')
		self.type_.insert('insert', '\\underline{' + select + '}')
		self.type_.edit_separator()
		show('underline text latex')
		self.keypress()
	def subscriptlatex(self):
		try:
			select = self.type_.get('sel.first', 'sel.last')
		except Exception:
			return
		self.type_.edit_separator()
		self.type_.delete('sel.first', 'sel.last')
		self.type_.insert('insert', '_{' + select + '}')
		self.type_.edit_separator()
		show('subscript text latex')
		self.keypress()
	def superscriptlatex(self):
		try:
			select = self.type_.get('sel.first', 'sel.last')
		except Exception:
			return
		self.type_.edit_separator()
		self.type_.delete('sel.first', 'sel.last')
		self.type_.insert('insert', '^{' + select + '}')
		self.type_.edit_separator()
		show('superscript text latex')
		self.keypress()
	def numberlistlatex(self):
		self.type_.edit_separator()
		try:
			select = self.type_.get('sel.first', 'sel.last')
		except Exception:
			self.type_.insert('insert', '\n\\begin{enumerate}\n\n\\end{enumerate}\n')
		else:
			tryfind = re.findall(r'\\begin{enumerate}.+\\end{enumerate}', select, re.DOTALL)
			if not tryfind:
				select = '\\item ' + select.replace('\n', '\n\\item ').replace('\\item \\item ', '\\item ')
				self.type_.delete('sel.first', 'sel.last')
				self.type_.insert('insert', '\n\\begin{enumerate}\n' + select + '\n\\end{enumerate}\n')
			else:
				keeptext = tryfind[0][len('\\begin{enumerate}'):][:-len('\\end{enumerate}')].replace('\\item ', '')
				self.type_.delete('sel.first', 'sel.last')
				self.type_.insert('insert', keeptext)
		self.type_.edit_separator()
		show('numbered list latex')
		self.keypress()
	def bulletlistlatex(self):
		self.type_.edit_separator()
		try:
			select = self.type_.get('sel.first', 'sel.last')
		except Exception:
			self.type_.insert('insert', '\n\\begin{itemize}\n\n\\end{itemize}\n').replace('\\item \\item ', '\\item ')
		else:
			tryfind = re.findall(r'\\begin{itemize}.+\\end{itemize}', select, re.DOTALL)
			if not tryfind:
				select = '\\item ' + select.replace('\n', '\n\\item ').replace('\\item \\item ', '\\item ')
				self.type_.delete('sel.first', 'sel.last')
				self.type_.insert('insert', '\n\\begin{itemize}\n' + select + '\n\\end{itemize}\n')
			else:
				keeptext = tryfind[0][len('\\begin{itemize}'):][:-len('\\end{itemize}')].replace('\\item ', '')
				self.type_.delete('sel.first', 'sel.last')
				self.type_.insert('insert', keeptext)
		self.type_.edit_separator()
		show('bulleted list latex')
		self.keypress()
	def paragraphlatex(self):
		self.type_.edit_separator()
		self.type_.insert('insert', '\\par\n')
		show('new paragraph latex')
		self.keypress()
	def equationlatex(self):
		self.type_.edit_separator()
		try:
			select = self.type_.get('sel.first', 'sel.last')
		except Exception:
			self.type_.insert('insert', '\n\\begin{equation}\n\\begin{split}\n\n\\end{split}\n\\end{equation}\n')
		else:
			tryfind = re.findall(r'\\begin{equation}.+\\end{equation}', select, re.DOTALL)
			if not tryfind:
				select = select.replace('\n', '\\\\\n').replace('\\\\\\\\', '\\\\')
				self.type_.delete('sel.first', 'sel.last')
				self.type_.insert('insert', '\n\\begin{equation}\n' + select + '\n\\end{equation}\n')
			else:
				keeptext = tryfind[0][len('\\begin{equation}'):][:-len('\\end{equation}')].replace('\\', '')
				self.type_.delete('sel.first', 'sel.last')
				self.type_.insert('insert', keeptext)
		self.type_.edit_separator()
		show('equation latex')
		self.keypress()
	def sectionlatex(self, typeofsection):
		self.type_.edit_separator()
		typeofsection = typeofsection.lower()
		secname = 'Section'
		if secname:
			self.type_.insert('insert', f'\n\\{typeofsection}' + '{' + secname + '}\n')
		self.type_.edit_separator()
		show(f'new {typeofsection} latex')
		self.keypress()
	def mathlatex(self, whichchar):
		self.type_.edit_separator()
		original = ['Multiplication', 'Division', 'Less or equal', 'More or equal', 'Not equal', 'Infinity', 'Summation', 'Integral', 'Pi', 'Theta', 'Alpha Lower', 'Alpha Upper', 'Inline Math']
		replaces = ['\\times', '\\div', '\\leq', '\\meq', '\\neq', '\\infty', '\\sum', '\\int', '\\pi', '\\theta', '\\alpha', '\\Alpha', '$$']
		whichchar = replaces[original.index(whichchar)]
		self.type_.insert('insert', whichchar)
		self.type_.edit_separator()
		show('insert math latex')
		self.keypress()
	def hapyshell(self):
		if self._hapyshell_running[0]:
			return
		self._hapyshell_running[0] = True
		lenprompt = len('>>> ')
		full_text = self.shellcmd.get('1.0', 'end')
		stripped_lines = []
		_shell_line_blocks = []
		_blk = 0
		_exec_boundary = 1
		for line in full_text.split('\n'):
			prefix = line[:lenprompt]
			if prefix in ('>>> ', '... '):
				stripped_lines.append(line[lenprompt:])
				if prefix == '>>> ':
					_blk += 1
					_exec_boundary = len(stripped_lines)
				_shell_line_blocks.append(_blk)
			else:
				stripped_lines.append('')
				_shell_line_blocks.append(0)
		stripped_text = '\n'.join(stripped_lines)
		_scan_key = (stripped_text, tuple(_shell_line_blocks))
		if _scan_key == self._pyshell_last_scan_key:
			shell_result = self._pyshell_cached_scope_result
		else:
			shell_result = self._python_build_scopes(stripped_text, line_blocks = _shell_line_blocks, seed_names = self._pyshell_session_names, seed_types = self._pyshell_session_types, seed_classes = self._pyshell_session_classes, seed_aliases = self._pyshell_session_aliases, seed_origins = self._pyshell_session_origins, seed_method_params = self._pyshell_session_method_params, seed_accepts_any = self._pyshell_session_accepts_any, seed_module_bases = self._pyshell_session_module_bases, seed_func_origins = self._pyshell_session_func_origins, seed_attr_types = self._pyshell_session_attr_types, seed_class_attr_types = self._pyshell_session_class_attr_types, seed_func_params = self._pyshell_session_func_params, seed_func_accepts_any = self._pyshell_session_func_accepts_any, seed_class_bases = self._pyshell_session_class_bases, seed_inherited = self._pyshell_session_inherited, seed_instance_only = self._pyshell_session_instance_only)
			self._pyshell_last_scan_key = _scan_key
			self._pyshell_cached_scope_result = shell_result
		if shell_result is None:
			shell_scopes = [{'start': 1, 'end': 1, 'parent': None, 'names': {}}]
			shell_call_kwargs = {}
			shell_module_aliases = {}
			shell_local_classes = {}
			shell_module_literals = []
			shell_scope_var_types = {}
			shell_literal_attrs = []
			shell_def_names = []
			shell_typed_attrs = []
			shell_param_default_tags = []
			shell_kwarg_positions = []
			shell_import_dotted_lines = []
			shell_import_orig_name_tags = []
			shell_name_positions = []
			shell_class_module_origin = {}
			shell_local_class_method_params = {}
			shell_local_class_accepts_any = set()
			shell_local_class_module_origins = {}
			shell_from_func_module = {}
			shell_class_type_maps = {}
			shell_class_attr_types = {}
			shell_func_params = {}
			shell_func_accepts_any = {}
			shell_class_bases = {}
			shell_inherited = {}
			shell_module_scope_class_keys = set()
			shell_instance_only = {}
			shell_instance_name_positions = set()
			shell_global_stmt_kind_positions = {}
		else:
			shell_scopes, shell_call_kwargs, shell_module_aliases, shell_local_classes, shell_module_literals, shell_scope_var_types, shell_literal_attrs, shell_def_names, shell_typed_attrs, shell_param_default_tags, shell_kwarg_positions, shell_import_dotted_lines, shell_import_orig_name_tags, shell_class_module_origin, shell_local_class_method_params, shell_local_class_accepts_any, shell_name_positions, shell_local_class_module_origins, shell_from_func_module, shell_class_type_maps, shell_class_attr_types, shell_func_params, shell_func_accepts_any, shell_class_bases, shell_inherited, shell_module_scope_class_keys, shell_instance_only, shell_instance_name_positions, shell_global_stmt_kind_positions = shell_result
		for _nm, _defs in shell_scopes[0]['names'].items():
			_exec_defs = [_d for _d in _defs if _d[0] < _exec_boundary]
			if _exec_defs and _nm not in shell_scopes[0].get('globals', {}) and _nm not in shell_scopes[0].get('nonlocals', {}):
				_best_def = _exec_defs[0]
				for _d in _exec_defs:
					if _d[0] >= _best_def[0]:
						_best_def = _d
				self._pyshell_session_names[_nm] = _best_def[1]
		for _nm, _tl in shell_scope_var_types.get(0, {}).items():
			_exec_tl = [_t for _t in _tl if _t[0] < _exec_boundary]
			if _exec_tl:
				_best_tl = _exec_tl[0]
				for _t in _exec_tl:
					if _t[0] >= _best_tl[0]:
						_best_tl = _t
				self._pyshell_session_types[_nm] = _best_tl[1]
		_text_class_lines = {}
		for _dl, _dcol, _dn, _dk in shell_def_names:
			if _dk == 'class':
				_text_class_lines.setdefault(_dn, []).append(_dl)
		for _cn, _mem in shell_local_classes.items():
			if _cn in _PYTHON_BUILTIN_MEMBERS:
				continue
			if _cn in _text_class_lines and _cn not in shell_module_scope_class_keys:
				continue
			_cls_lines = _text_class_lines.get(_cn)
			if _cls_lines is None or _cn in self._pyshell_session_classes or any(_l < _exec_boundary for _l in _cls_lines):
				self._pyshell_session_classes[_cn] = _mem
		for _an, _adefs in shell_module_aliases.items():
			_abest = None
			for _ad in _adefs:
				if _ad[0] < _exec_boundary and (_abest is None or _ad[0] >= _abest[0]):
					_abest = _ad
			if _abest is not None:
				self._pyshell_session_aliases[_an] = _abest[1]
		for _on, _odefs in shell_class_module_origin.items():
			_obest = None
			for _od in _odefs:
				if _od[0] < _exec_boundary and (_obest is None or _od[0] >= _obest[0]):
					_obest = _od
			if _obest is not None:
				self._pyshell_session_origins[_on] = _obest[1]
		for _mpk, _mpv in shell_local_class_method_params.items():
			if _mpk.split('.')[0] in shell_module_scope_class_keys:
				self._pyshell_session_method_params[_mpk] = _mpv
		for _mbk, _mbv in shell_local_class_module_origins.items():
			self._pyshell_session_module_bases.setdefault(_mbk, [])
			for _mbo in _mbv:
				if _mbo not in self._pyshell_session_module_bases[_mbk]:
					self._pyshell_session_module_bases[_mbk].append(_mbo)
		for _ffk, _ffv in shell_from_func_module.items():
			if _ffv and _ffk not in self._pyshell_session_func_origins:
				_ff_best = max(_ffv, key = lambda _x: _x[0])
				self._pyshell_session_func_origins[_ffk] = _ff_best[1]
		for _ctk, _ctv in shell_class_type_maps.items():
			self._pyshell_session_attr_types[_ctk] = dict(_ctv)
		for _catk, _catv in shell_class_attr_types.items():
			self._pyshell_session_class_attr_types[_catk] = dict(_catv)
		for _aak in shell_local_class_accepts_any:
			if _aak.split('.')[0] in shell_module_scope_class_keys:
				self._pyshell_session_accepts_any.add(_aak)
		self._pyshell_session_func_params.update(shell_func_params)
		self._pyshell_session_func_accepts_any.update(shell_func_accepts_any)
		self._pyshell_session_class_bases.update(shell_class_bases)
		for _inhk in ('members', 'attr_types', 'method_params'):
			self._pyshell_session_inherited[_inhk].update(shell_inherited.get(_inhk, ()))
		for _iok, _iov in shell_instance_only.items():
			self._pyshell_session_instance_only.setdefault(_iok, set()).update(_iov)
		try:
			shell_top = self.shellcmd.index('@0,0')
			shell_bottom = self.shellcmd.index(f'@0,{self.shellcmd.winfo_height()}')
		except Exception:
			shell_top = '1.0'
			shell_bottom = 'end'
		try:
			all_tags = set(self.shellcmd.tag_names())
			def _removable(tag):
				return tag not in _PYTHON_SHELL_HL_SKIP_REMOVE_TAGS and (tag not in skiptagspythonshell or self.hmode not in skiptagspythonshell[tag])
			shell_top_line = int(shell_top.split('.')[0])
			if shell_top_line < _exec_boundary:
				shell_top_line = _exec_boundary
				shell_top = f'{shell_top_line}.0'
			try:
				shell_bottom_line = int(self.shellcmd.index(shell_bottom).split('.')[0])
			except Exception:
				shell_bottom_line = shell_top_line + len(stripped_lines)
			vis_abs = list(range(shell_top_line, shell_bottom_line + 1))
			vis_code = [stripped_lines[L - 1] if 0 <= L - 1 < len(stripped_lines) else '' for L in vis_abs]
			visible_code = '\n'.join(vis_code)
			line_starts = []
			_acc = 0
			for _l in vis_code:
				line_starts.append(_acc)
				_acc += len(_l) + 1
			def widx(line, col):
				return f'{line}.{col + lenprompt}'
			def off2lc(off):
				lo = 0
				for _i in range(len(line_starts)):
					if line_starts[_i] <= off:
						lo = _i
					else:
						break
				return shell_top_line + lo, off - line_starts[lo]
			def clear_idx(a, b):
				for _t in all_tags:
					if _removable(_t):
						self.shellcmd.tag_remove(_t, a, b)
			def add_idx(tag, a, b):
				for _t in all_tags:
					if _t != tag and _removable(_t):
						self.shellcmd.tag_remove(_t, a, b)
				self.shellcmd.tag_add(tag, a, b)
			def add_span(tag, off_s, off_e):
				l1, c1 = off2lc(off_s)
				l2, c2 = off2lc(off_e)
				add_idx(tag, widx(l1, c1), widx(l2, c2))
			for tag in all_tags:
				if _removable(tag):
					self.shellcmd.tag_remove(tag, shell_top, shell_bottom)
			for m in _PYTHON_KW_PAT.finditer(visible_code):
				add_span('hpa', m.start(), m.end())
			line_scope_candidates = {}
			for line in vis_abs:
				_cands = []
				for k, sc in enumerate(shell_scopes):
					if sc['start'] <= line <= sc['end']:
						_cands.append((sc['start'], sc.get('start_col', 0), sc['end'], sc.get('end_col'), k))
				line_scope_candidates[line] = _cands
			def _resolve_scope_idx(line, col):
				winner = None
				winner_start = None
				for _cstart, _ccol, _cend, _ecol, _ck in line_scope_candidates.get(line, ()):
					if _cstart == line and col < _ccol:
						continue
					if _cend == line and _ecol is not None and col >= _ecol:
						continue
					if winner is None or _cstart >= winner_start:
						winner = _ck
						winner_start = _cstart
				return winner
			shell_module_literal_lines = {}
			for lineno, _mcol, name in shell_module_literals:
				shell_module_literal_lines.setdefault(lineno, []).append((_mcol, name))
			shell_import_dotted_by_line = {}
			for lineno, dcol, dotted in shell_import_dotted_lines:
				shell_import_dotted_by_line.setdefault(lineno, []).append((dcol, dotted))
			shell_import_orig_by_line = {}
			for _oln, _ocol, _oname, _otag in shell_import_orig_name_tags:
				shell_import_orig_by_line.setdefault(_oln, []).append((_ocol, _oname, _otag))
			def _shell_same_block(l1, l2):
				if l1 == l2:
					return True
				if not (0 < l1 <= len(_shell_line_blocks)) or not (0 < l2 <= len(_shell_line_blocks)):
					return False
				_b1 = _shell_line_blocks[l1 - 1]
				return _b1 != 0 and _b1 == _shell_line_blocks[l2 - 1]
			shell_name_pos_by_line = {}
			for _nl, _ncol, _nname, _nstore in shell_name_positions:
				shell_name_pos_by_line.setdefault(_nl, []).append((_ncol, _nname, _nstore))
			shell_def_names_by_line = {}
			for _dl, _dcol, _dname, _dkind in shell_def_names:
				shell_def_names_by_line.setdefault(_dl, []).append((_dcol, _dname, _dkind))
			shell_kind_tags = {'var': 'hpv', 'instance': 'hpi', 'func': 'hpf', 'func_arg': 'hpfa', 'first_param': 'hpb', 'module': 'hpm', 'class': 'hpx', 'builtin': 'hpb'}
			shell_literal_attr_by_line = {}
			for _ln, _col, _attr, _tname in shell_literal_attrs:
				shell_literal_attr_by_line.setdefault(_ln, []).append((_col, _attr, _tname))
			shell_typed_attr_by_line = {}
			for _tl, _tcol, _tattr, _tkind in shell_typed_attrs:
				shell_typed_attr_by_line.setdefault(_tl, []).append((_tcol, _tattr, _tkind))
			shell_param_default_by_line = {}
			for _pl, _pcol, _pname, _pkind in shell_param_default_tags:
				shell_param_default_by_line.setdefault(_pl, []).append((_pcol, _pname, _pkind))
			shell_kwarg_pos_by_line = {}
			for _kl, _kcol, _kname in shell_kwarg_positions:
				shell_kwarg_pos_by_line.setdefault(_kl, []).append((_kcol, _kname))
			_shell_active_cache = {}
			def _shell_active_for(abs_line, scope_idx):
				_ckey = (abs_line, scope_idx)
				if _ckey in _shell_active_cache:
					return _shell_active_cache[_ckey]
				active = {}
				prior_kinds = {}
				bound = set()
				innermost_scope = scope_idx
				innermost_parent = shell_scopes[innermost_scope]['parent'] if innermost_scope is not None else None
				on_header = innermost_scope is not None and abs_line == shell_scopes[innermost_scope]['start']
				_redir_names = set()
				_rsi = innermost_scope
				while _rsi is not None:
					_rsc = shell_scopes[_rsi]
					_redir_names |= set(_rsc.get('globals', {}))
					_redir_names |= set(_rsc.get('nonlocals', {}))
					_rsi = _rsc['parent']
				_sidx = scope_idx
				while _sidx is not None:
					sc = shell_scopes[_sidx]
					if sc.get('kind') == 'class' and _sidx != innermost_scope and not (on_header and _sidx == innermost_parent):
						_sidx = sc['parent']
						continue
					sc_globals = sc.get('globals', {})
					sc_nonlocals = sc.get('nonlocals', {})
					for name, defs in sc['names'].items():
						if name in active or name in bound:
							continue
						if name in sc_globals or name in sc_nonlocals:
							continue
						best = None
						second_best = None
						latest = None
						_guard = _sidx == innermost_scope or name in _redir_names
						for dl, kind in defs:
							if latest is None or dl > latest[0]:
								latest = (dl, kind)
							if _guard and dl > abs_line:
								continue
							if best is None or dl > best[0]:
								second_best = best
								best = (dl, kind)
							elif second_best is None or dl > second_best[0]:
								second_best = (dl, kind)
						if best is None and latest is not None and _shell_same_block(latest[0], abs_line) and name not in _PYTHON_BUILTIN_NAMES:
							best = latest
						bound.add(name)
						if best is not None:
							active[name] = best[1]
							if best[0] == abs_line and second_best is not None and second_best[1] != best[1]:
								prior_kinds[name] = second_best[1]
					_sidx = sc['parent']
				_result = (active, prior_kinds)
				_shell_active_cache[_ckey] = _result
				return _result
			for li, abs_line in enumerate(vis_abs):
				line_str = vis_code[li]
				for _ncol, _nname, _nstore in shell_name_pos_by_line.get(abs_line, []):
					_nkind = shell_global_stmt_kind_positions.get((abs_line, _ncol))
					if _nkind is None:
						active, prior_kinds = _shell_active_for(abs_line, _resolve_scope_idx(abs_line, _ncol))
						_nkind = active.get(_nname)
						if _nkind is None:
							if _nname not in _PYTHON_BUILTIN_NAMES:
								continue
							_nkind = 'builtin'
						elif not _nstore and _nname in prior_kinds:
							_nkind = prior_kinds[_nname]
					_ntag = shell_kind_tags.get(_nkind)
					if _ntag is None:
						continue
					if _ntag == 'hpv' and (abs_line, _ncol) in shell_instance_name_positions:
						_ntag = 'hpi'
					_nccol = _python_bytecol_to_charcol(line_str, _ncol)
					s = widx(abs_line, _nccol)
					e = widx(abs_line, _nccol + len(_nname))
					add_idx(_ntag, s, e)
				for _dcol, _dname, _dkind in shell_def_names_by_line.get(abs_line, []):
					_dccol = _python_bytecol_to_charcol(line_str, _dcol)
					s = widx(abs_line, _dccol)
					e = widx(abs_line, _dccol + len(_dname))
					add_idx('hpf' if _dkind == 'func' else 'hpx', s, e)
				for _pcol, _pname, _pkind in shell_param_default_by_line.get(abs_line, []):
					if _pkind == 'var' and (abs_line, _pcol) in shell_instance_name_positions:
						_pkind = 'instance'
					_pcol = _python_bytecol_to_charcol(line_str, _pcol)
					_ptag = {'var': 'hpv', 'instance': 'hpi', 'func': 'hpf', 'func_arg': 'hpfa', 'first_param': 'hpb', 'module': 'hpm', 'class': 'hpx'}.get(_pkind)
					if _ptag is not None:
						s = widx(abs_line, _pcol)
						e = widx(abs_line, _pcol + len(_pname))
						add_idx(_ptag, s, e)
				for _mcol, name in shell_module_literal_lines.get(abs_line, []):
					_mccol = _python_bytecol_to_charcol(line_str, _mcol)
					if line_str[_mccol:_mccol + len(name)] != name:
						continue
					add_idx('hpm', widx(abs_line, _mccol), widx(abs_line, _mccol + len(name)))
				for dcol, dotted in shell_import_dotted_by_line.get(abs_line, []):
					dcol = _python_bytecol_to_charcol(line_str, dcol)
					if line_str[dcol:dcol + len(dotted)] != dotted:
						continue
					pos = dcol
					for part in dotted.split('.'):
						add_idx('hpm', widx(abs_line, pos), widx(abs_line, pos + len(part)))
						pos += len(part) + 1
				for _ocol, _oname, _otag in shell_import_orig_by_line.get(abs_line, []):
					_ocol = _python_bytecol_to_charcol(line_str, _ocol)
					if line_str[_ocol:_ocol + len(_oname)] != _oname:
						continue
					add_idx(_otag, widx(abs_line, _ocol), widx(abs_line, _ocol + len(_oname)))
				for _col, _attr, _tname in shell_literal_attr_by_line.get(abs_line, []):
					_col = _python_bytecol_to_charcol(line_str, _col)
					_kind = _PYTHON_BUILTIN_MEMBERS[_tname].get(_attr)
					if _kind is not None:
						add_idx('hpf' if _kind == 'func' else 'hpv', widx(abs_line, _col), widx(abs_line, _col + len(_attr)))
				for _tcol, _tattr, _tkind in shell_typed_attr_by_line.get(abs_line, []):
					_tcol = _python_bytecol_to_charcol(line_str, _tcol)
					_ttag = {'func': 'hpf', 'var': 'hpv', 'instance': 'hpi', 'module': 'hpm', 'class': 'hpx'}.get(_tkind, 'hpx')
					add_idx(_ttag, widx(abs_line, _tcol), widx(abs_line, _tcol + len(_tattr)))
				for _kcol, _kname in shell_kwarg_pos_by_line.get(abs_line, []):
					_kcol = _python_bytecol_to_charcol(line_str, _kcol)
					s = widx(abs_line, _kcol)
					e = widx(abs_line, _kcol + len(_kname))
					clear_idx(s, e)
					if _kname in shell_call_kwargs.get(abs_line, set()):
						self.shellcmd.tag_add('hpfa', s, e)
			for m in _PYTHON_OP_PAT.finditer(visible_code):
				add_span('hpo', m.start(), m.end())
			shell_pre_text = '\n'.join(stripped_lines[:shell_top_line - 1])
			if shell_pre_text:
				shell_pre_text += '\n'
			pre_n = len(shell_pre_text)
			pre_i = 0
			in_triple = False
			triple_ch = None
			in_single = False
			single_ch = None
			while pre_i < pre_n:
				pch = shell_pre_text[pre_i]
				if pch in ('"', "'") and pre_i + 2 < pre_n and shell_pre_text[pre_i + 1] == pch and shell_pre_text[pre_i + 2] == pch:
					pquote = shell_pre_text[pre_i:pre_i + 3]
					j = pre_i + 3
					found_close = False
					while j < pre_n:
						if shell_pre_text[j] == '\\':
							j += 2
							continue
						if shell_pre_text[j:j + 3] == pquote:
							j += 3
							found_close = True
							break
						j += 1
					if not found_close:
						in_triple = True
						triple_ch = pch
						break
					pre_i = j
				elif pch in ('"', "'"):
					pquote = pch
					j = pre_i + 1
					closed = False
					while j < pre_n:
						if shell_pre_text[j] == '\\':
							j += 2
							continue
						if shell_pre_text[j] == pquote:
							j += 1
							closed = True
							break
						if shell_pre_text[j] == '\n':
							closed = True
							break
						j += 1
					if not closed:
						in_single = True
						single_ch = pquote
						break
					pre_i = j
				elif pch == '#':
					j = pre_i + 1
					while j < pre_n and shell_pre_text[j] != '\n':
						j += 1
					if j < pre_n:
						j += 1
					pre_i = j
				else:
					pre_i += 1
			n = len(visible_code)
			i = 0
			if in_triple:
				quote = triple_ch * 3
				j = 0
				found_close = False
				while j < n:
					if visible_code[j] == '\\':
						j += 2
						continue
					if visible_code[j:j + 3] == quote:
						j += 3
						found_close = True
						break
					j += 1
				if not found_close:
					j = n
				add_span('hpd', 0, j)
				i = j
			elif in_single:
				quote = single_ch
				j = 0
				while j < n:
					if visible_code[j] == '\\':
						j += 2
						continue
					if visible_code[j] == quote:
						j += 1
						break
					if visible_code[j] == '\n':
						break
					j += 1
				if j > n:
					j = n
				add_span('hpd', 0, j)
				i = j
			while i < n:
				ch = visible_code[i]
				if ch in ('"', "'") and i + 2 < n and visible_code[i + 1] == ch and visible_code[i + 2] == ch:
					quote = visible_code[i:i + 3]
					j = i + 3
					found_close = False
					while j < n:
						if visible_code[j] == '\\':
							j += 2
							continue
						if visible_code[j:j + 3] == quote:
							j += 3
							found_close = True
							break
						j += 1
					if not found_close:
						j = n
					add_span('hpd', i, j)
					i = j
				elif ch in ('"', "'"):
					quote = ch
					j = i + 1
					while j < n:
						if visible_code[j] == '\\':
							j += 2
							continue
						if visible_code[j] == quote:
							j += 1
							break
						if visible_code[j] == '\n':
							break
						j += 1
					add_span('hpd', i, j)
					i = j
				elif ch == '#':
					j = i + 1
					while j < n and visible_code[j] != '\n':
						j += 1
					add_span('hpc', i, j)
					i = j
				else:
					i += 1
		except Exception:
			pass
		self._hapyshell_running[0] = False
	def shellpy(self):
		import queue as _queue
		lenprompt = len('>>> ')
		running = [True]
		_poll_after_id = [None]
		out_q = _queue.Queue()
		cursor = ['1.0']
		screen_top = [1]
		prev_was_H1 = [False]
		_write_ref = [None]
		_proc_ref = [None]
		_mfd_ref = [None]
		_hl_pending = [False]
		generation = [0]
		_cursor_line = [1]
		_cursor_col = [0]
		_saved_cursor = [(1, 0)]
		_pending_esc = ['']
		_sgr_sel = [False]
		def colourprompts():
			lines = int(self.shellcmd.index('end-1c').split('.')[0])
			self.shellcmd.tag_remove('prompt', '1.0', 'end')
			for i in range(1, lines + 1):
				if not self.shellcmd.get(f'{i}.0', f'{i}.{lenprompt}') in {'>>> ', '... '}:
					continue
				self.shellcmd.tag_add('prompt', f'{i}.0', f'{i}.{lenprompt}')
			self.shellcmd.tag_config('prompt', foreground = 'green', font = (monospace, 14, 'bold'))
		def _process(text):
			if isinstance(text, bytes):
				text = text.decode('utf-8', errors = 'replace')
			if _pending_esc[0]:
				text = _pending_esc[0] + text
				_pending_esc[0] = ''
			self.shellcmd.mark_set('insert', f'{_cursor_line[0]}.{_cursor_col[0]}')
			i = 0
			n = len(text)
			while i < n:
				ch = text[i]
				_was_h1 = prev_was_H1[0]
				prev_was_H1[0] = False
				if ch == '\r':
					_cursor_col[0] = 0
					self.shellcmd.mark_set('insert', f'{_cursor_line[0]}.0')
					i += 1
				elif ch == '\x08':
					if _cursor_col[0] > 0:
						_cursor_col[0] -= 1
						self.shellcmd.mark_set('insert', f'{_cursor_line[0]}.{_cursor_col[0]}')
					i += 1
				elif ch == '\n':
					_cursor_line[0] += 1
					_cursor_col[0] = 0
					if _cursor_line[0] > screen_top[0] + 23:
						screen_top[0] = _cursor_line[0] - 23
					_last = int(self.shellcmd.index('end').split('.')[0]) - 1
					if _cursor_line[0] > _last:
						self.shellcmd.insert('end', '\n' * (_cursor_line[0] - _last))
					self.shellcmd.mark_set('insert', f'{_cursor_line[0]}.0')
					i += 1
				elif ch == '\x1b':
					rest = text[i:]
					if len(rest) < 2:
						_pending_esc[0] = rest
						break
					nxt = rest[1]
					if nxt == '[':
						m = re.match(r'\x1b\[([0-9;?<=>]*[ -/]*)([@-~])', rest)
						if not m and re.fullmatch(r'\x1b\[[0-9;?<=>]*[ -/]*', rest):
							_pending_esc[0] = rest
							break
						if m:
							_prefix = m.group(1)
							ps = ''.join(c for c in _prefix if c in '0123456789;')
							cmd = m.group(2) if all(c in '0123456789;?' for c in _prefix) else ''
							p = [int(x) if x else 0 for x in ps.split(';')] if ps else [0]
							ln = _cursor_line[0]
							col = _cursor_col[0]
							if cmd == 'K':
								if p[0] == 0:
									self.shellcmd.delete(f'{ln}.{col}', f'{ln}.end')
								elif p[0] == 1:
									self.shellcmd.delete(f'{ln}.0', f'{ln}.{col}')
								else:
									self.shellcmd.delete(f'{ln}.0', f'{ln}.end')
							elif cmd == 'J':
								if p[0] == 2:
									if _was_h1:
										self.shellcmd.delete('1.0', 'end')
										screen_top[0] = 1
										_cursor_line[0] = 1
										_cursor_col[0] = 0
										self.shellcmd.mark_set('insert', '1.0')
									else:
										last_line = int(self.shellcmd.index('end').split('.')[0]) - 1
										screen_top[0] = max(screen_top[0], max(1, last_line - 23))
										if self.shellcmd.compare(f'{screen_top[0]}.0', '<', 'end'):
											self.shellcmd.delete(f'{screen_top[0]}.0', 'end')
										cur_last = int(self.shellcmd.index('end').split('.')[0]) - 1
										if screen_top[0] > cur_last:
											self.shellcmd.insert('end', '\n' * (screen_top[0] - cur_last))
										_cursor_line[0] = screen_top[0]
										_cursor_col[0] = 0
										self.shellcmd.mark_set('insert', f'{screen_top[0]}.0')
								elif p[0] == 3:
									if screen_top[0] > 1:
										lines_deleted = screen_top[0] - 1
										self.shellcmd.delete('1.0', f'{screen_top[0]}.0')
										_cursor_line[0] = max(1, _cursor_line[0] - lines_deleted)
										screen_top[0] = 1
										self.shellcmd.mark_set('insert', f'{_cursor_line[0]}.{_cursor_col[0]}')
								elif p[0] == 1:
									for _er in range(screen_top[0], ln):
										self.shellcmd.delete(f'{_er}.0', f'{_er}.end')
									self.shellcmd.delete(f'{ln}.0', f'{ln}.{col}')
									self.shellcmd.insert(f'{ln}.0', ' ' * col)
									self.shellcmd.mark_set('insert', f'{ln}.{col}')
								elif p[0] == 0:
									if self.shellcmd.compare(f'{ln}.{col}', '<', 'end-1c'):
										self.shellcmd.delete(f'{ln}.{col}', 'end-1c')
							elif cmd in ('H', 'f'):
								row_ = p[0] if p[0] else 1
								col_ = p[1] if len(p) > 1 and p[1] else 1
								last_line = int(self.shellcmd.index('end').split('.')[0]) - 1
								target_line = screen_top[0] + row_ - 1
								target_line = max(1, target_line)
								_cursor_line[0] = target_line
								_cursor_col[0] = col_ - 1
								if target_line > last_line:
									self.shellcmd.insert('end', '\n' * (target_line - last_line))
								self.shellcmd.mark_set('insert', f'{target_line}.{col_ - 1}')
							elif cmd == 'A':
								mv = p[0] or 1
								_cursor_line[0] = max(1, _cursor_line[0] - mv)
								self.shellcmd.mark_set('insert', f'{_cursor_line[0]}.{_cursor_col[0]}')
							elif cmd == 'B':
								mv = p[0] or 1
								_cursor_line[0] += mv
								self.shellcmd.mark_set('insert', f'{_cursor_line[0]}.{_cursor_col[0]}')
							elif cmd == 'C':
								mv = p[0] or 1
								_cursor_col[0] += mv
								_ll = int(self.shellcmd.index(f'{_cursor_line[0]}.end').split('.')[1])
								if _cursor_col[0] > _ll:
									self.shellcmd.insert(f'{_cursor_line[0]}.end', ' ' * (_cursor_col[0] - _ll))
								self.shellcmd.mark_set('insert', f'{_cursor_line[0]}.{_cursor_col[0]}')
							elif cmd == 'D':
								mv = p[0] or 1
								_cursor_col[0] = max(0, _cursor_col[0] - mv)
								self.shellcmd.mark_set('insert', f'{_cursor_line[0]}.{_cursor_col[0]}')
							elif cmd == 'E':
								mv = p[0] or 1
								_cursor_line[0] += mv
								_cursor_col[0] = 0
								_last = int(self.shellcmd.index('end').split('.')[0]) - 1
								if _cursor_line[0] > _last:
									self.shellcmd.insert('end', '\n' * (_cursor_line[0] - _last))
								self.shellcmd.mark_set('insert', f'{_cursor_line[0]}.0')
							elif cmd == 'F':
								mv = p[0] or 1
								_cursor_line[0] = max(1, _cursor_line[0] - mv)
								_cursor_col[0] = 0
								self.shellcmd.mark_set('insert', f'{_cursor_line[0]}.0')
							elif cmd == 's':
								_saved_cursor[0] = (_cursor_line[0], _cursor_col[0])
							elif cmd == 'u':
								_cursor_line[0], _cursor_col[0] = _saved_cursor[0]
								_last = int(self.shellcmd.index('end').split('.')[0]) - 1
								if _cursor_line[0] > _last:
									self.shellcmd.insert('end', '\n' * (_cursor_line[0] - _last))
								self.shellcmd.mark_set('insert', f'{_cursor_line[0]}.{_cursor_col[0]}')
							elif cmd == 'G':
								mv = p[0] or 1
								_cursor_col[0] = mv - 1
								_ll = int(self.shellcmd.index(f'{_cursor_line[0]}.end').split('.')[1])
								if _cursor_col[0] > _ll:
									self.shellcmd.insert(f'{_cursor_line[0]}.end', ' ' * (_cursor_col[0] - _ll))
								self.shellcmd.mark_set('insert', f'{_cursor_line[0]}.{_cursor_col[0]}')
							elif cmd == 'P':
								mv = p[0] or 1
								self.shellcmd.delete(f'{ln}.{col}', f'{ln}.{col + mv}')
							elif cmd == '@':
								mv = p[0] or 1
								self.shellcmd.insert(f'{ln}.{col}', ' ' * mv)
								self.shellcmd.mark_set('insert', f'{_cursor_line[0]}.{_cursor_col[0]}')
							elif cmd == 'n':
								if p[0] == 6 and _write_ref[0] is not None:
									row_rep = max(1, _cursor_line[0] - screen_top[0] + 1)
									try:
										_write_ref[0](f'\x1b[{row_rep};{_cursor_col[0]+1}R'.encode())
									except Exception:
										pass
							elif cmd == 'm':
								_hl = _sgr_is_highlight(p)
								if _hl is not None:
									_sgr_sel[0] = _hl
							prev_was_H1[0] = cmd in ('H', 'f') and (p[0] if p[0] else 1) == 1
							i += len(m.group(0))
						else:
							i += 2
					elif nxt == ']':
						end_osc = rest.find('\x07', 2)
						if end_osc >= 0:
							i += end_osc + 1
						else:
							st = rest.find('\x1b\\', 2)
							if st >= 0:
								i += st + 2
							elif len(rest) < _PTY_MAX_PENDING_ESC:
								_pending_esc[0] = rest
								break
							else:
								i += len(rest)
					elif nxt == 'M':
						_cursor_line[0] = max(1, _cursor_line[0] - 1)
						self.shellcmd.mark_set('insert', f'{_cursor_line[0]}.{_cursor_col[0]}')
						i += 2
					elif nxt == 'D':
						_cursor_line[0] += 1
						self.shellcmd.mark_set('insert', f'{_cursor_line[0]}.{_cursor_col[0]}')
						i += 2
					elif nxt in '()*+#':
						if len(rest) < 3:
							_pending_esc[0] = rest
							break
						i += 3
					elif nxt == '7':
						_saved_cursor[0] = (_cursor_line[0], _cursor_col[0])
						i += 2
					elif nxt == '8':
						_cursor_line[0], _cursor_col[0] = _saved_cursor[0]
						_last = int(self.shellcmd.index('end').split('.')[0]) - 1
						if _cursor_line[0] > _last:
							self.shellcmd.insert('end', '\n' * (_cursor_line[0] - _last))
						self.shellcmd.mark_set('insert', f'{_cursor_line[0]}.{_cursor_col[0]}')
						i += 2
					elif nxt == '\x1b':
						i += 1
					else:
						i += 2
				elif ch == '\t':
					sp = 8 - (_cursor_col[0] % 8)
					for _ in range(sp):
						cur = self.shellcmd.get(f'{_cursor_line[0]}.{_cursor_col[0]}', f'{_cursor_line[0]}.{_cursor_col[0] + 1}')
						if cur and cur != '\n':
							self.shellcmd.delete(f'{_cursor_line[0]}.{_cursor_col[0]}', f'{_cursor_line[0]}.{_cursor_col[0] + 1}')
						self.shellcmd.insert(f'{_cursor_line[0]}.{_cursor_col[0]}', ' ')
						_cursor_col[0] += 1
					self.shellcmd.mark_set('insert', f'{_cursor_line[0]}.{_cursor_col[0]}')
					i += 1
				elif ch >= ' ' and ch != '\x7f':
					cur = self.shellcmd.get(f'{_cursor_line[0]}.{_cursor_col[0]}', f'{_cursor_line[0]}.{_cursor_col[0] + 1}')
					if cur and cur != '\n':
						self.shellcmd.delete(f'{_cursor_line[0]}.{_cursor_col[0]}', f'{_cursor_line[0]}.{_cursor_col[0] + 1}')
					if _sgr_sel[0]:
						self.shellcmd.insert(f'{_cursor_line[0]}.{_cursor_col[0]}', ch, 'sel')
					else:
						self.shellcmd.insert(f'{_cursor_line[0]}.{_cursor_col[0]}', ch)
					_cursor_col[0] += 1
					self.shellcmd.mark_set('insert', f'{_cursor_line[0]}.{_cursor_col[0]}')
					i += 1
				else:
					i += 1
			cursor[0] = f'{_cursor_line[0]}.{_cursor_col[0]}'
			self.shellcmd.mark_set('insert', cursor[0])
			colourprompts()
		def _schedule_hl():
			if not _hl_pending[0]:
				_hl_pending[0] = True
				def _run_hl():
					_hl_pending[0] = False
					self.hapyshell()
				self.shellcmd.after_idle(_run_hl)
		def _poll(gen):
			had_output = False
			backlog = False
			processed = 0
			_at_bottom = self.shellcmd.yview()[1] >= 0.999
			try:
				while processed < _PTY_POLL_CHAR_BUDGET:
					item = out_q.get_nowait()
					item_gen, text = item
					if text is None:
						if item_gen == generation[0]:
							running[0] = False
							return
						else:
							continue
					if item_gen != generation[0]:
						continue
					_process(text)
					processed += len(text)
					had_output = True
				backlog = True
			except Exception:
				pass
			if running[0] and gen == generation[0]:
				if had_output:
					if _at_bottom:
						self.shellcmd.see('end')
					self.shellcmd.see('insert')
					_schedule_hl()
				_poll_after_id[0] = self.shellcmd.after(1 if backlog else 50, lambda: _poll(gen))
		def _start():
			running[0] = True
			generation[0] += 1
			gen = generation[0]
			env = os.environ.copy()
			env['PYTHONUNBUFFERED'] = '1'
			if platform.system() == 'Linux':
				import pty
				import select as _select
				import fcntl
				import termios
				import struct
				master_fd, slave_fd = pty.openpty()
				fcntl.ioctl(master_fd, termios.TIOCSWINSZ, struct.pack('HHHH', 24, 800, 0, 0))
				env['TERM'] = 'linux'
				def _shell_preexec():
					os.setsid()
					fcntl.ioctl(0, termios.TIOCSCTTY, 0)
				proc = subprocess.Popen([pythonexecutable], stdin = slave_fd, stdout = slave_fd, stderr = slave_fd, close_fds = True, preexec_fn = _shell_preexec, env = env)
				os.close(slave_fd)
				_proc_ref[0] = proc
				_mfd_ref[0] = master_fd
				def _read():
					_dec = codecs.getincrementaldecoder('utf-8')(errors = 'replace')
					while running[0] and gen == generation[0]:
						try:
							r, _, _ = _select.select([master_fd], [], [], 0.05)
							if r:
								data = os.read(master_fd, 4096)
								if data:
									out_q.put((gen, _dec.decode(data)))
							elif proc.poll() is not None:
								break
						except Exception:
							break
					out_q.put((gen, None))
				def _write(data):
					os.write(master_fd, data)
			else:
				proc = PtyProcess.spawn(pythonexecutable, dimensions = (24, 800))
				_proc_ref[0] = proc
				def _read():
					_dec = codecs.getincrementaldecoder('utf-8')(errors = 'replace')
					while running[0] and gen == generation[0]:
						try:
							data = proc.read(4096)
							if data:
								out_q.put((gen, data if isinstance(data, str) else _dec.decode(data)))
						except Exception:
							break
					out_q.put((gen, None))
				def _write(data):
					try:
						proc.write(data.decode('utf-8', errors = 'replace'))
					except Exception:
						pass
			_write_ref[0] = _write
			threading.Thread(target = _read, daemon = True).start()
			_poll_after_id[0] = self.shellcmd.after(50, lambda: _poll(gen))
		_shell_csi_keys = {'Up': 'A', 'Down': 'B', 'Right': 'C', 'Left': 'D'}
		_shell_tilde_keys = {'Home': '1', 'Insert': '2', 'Delete': '3', 'End': '4', 'Prior': '5', 'Next': '6', 'F6': '17', 'F7': '18', 'F8': '19', 'F9': '20', 'F10': '21', 'F11': '23', 'F12': '24'}
		_shell_fn_keys = {'F1': 'A', 'F2': 'B', 'F3': 'C', 'F4': 'D', 'F5': 'E'}
		def _key(event):
			_unpost_menu()
			if not running[0]:
				return 'break'
			sym = event.keysym
			ch = event.char
			if ch or sym in ('Return', 'BackSpace', 'Delete', 'Up', 'Down', 'Left', 'Right', 'Tab', 'ISO_Left_Tab', 'Home', 'End', 'Prior', 'Next', 'Insert'):
				_clear_selection()
			try:
				if sym == 'Return':
					_write_ref[0](b'\r')
				elif sym == 'BackSpace':
					_write_ref[0](b'\x7f')
				elif sym == 'ISO_Left_Tab' or (sym == 'Tab' and (event.state & 1)):
					_write_ref[0](b'\x1b[Z')
				elif sym == 'Tab':
					_write_ref[0](b'\t')
				elif sym in _shell_csi_keys:
					_write_ref[0](('\x1b[' + _shell_csi_keys[sym]).encode())
				elif sym in _shell_tilde_keys:
					_write_ref[0](f'\x1b[{_shell_tilde_keys[sym]}~'.encode())
				elif sym in _shell_fn_keys:
					_write_ref[0](('\x1b[[' + _shell_fn_keys[sym]).encode())
				elif (event.state & 4) and sym in ('space', 'at', '2'):
					_write_ref[0](b'\x00')
				elif (event.state & 4) and sym in ('bracketleft', '3'):
					_write_ref[0](b'\x1b')
				elif (event.state & 4) and sym in ('backslash', '4'):
					_write_ref[0](b'\x1c')
				elif (event.state & 4) and sym in ('bracketright', '5'):
					_write_ref[0](b'\x1d')
				elif (event.state & 4) and sym in ('asciicircum', '6'):
					_write_ref[0](b'\x1e')
				elif (event.state & 4) and sym in ('underscore', 'slash', '7'):
					_write_ref[0](b'\x1f')
				elif ch:
					_write_ref[0](ch.encode('utf-8'))
			except Exception:
				pass
			return 'break'
		def _clear_selection():
			try:
				self.shellcmd.tag_remove('sel', '1.0', 'end')
			except Exception:
				pass
		def _copy_selection(e = None):
			try:
				sel = self.shellcmd.get('sel.first', 'sel.last')
			except Exception:
				return 'break'
			if sel:
				root.clipboard_clear()
				root.clipboard_append(sel)
			return 'break'
		def _paste_clipboard(e = None):
			if not running[0] or _write_ref[0] is None:
				return 'break'
			try:
				data = root.clipboard_get()
			except Exception:
				return 'break'
			if data:
				data = data.replace('\r\n', '\r').replace('\n', '\r')
				try:
					_write_ref[0](data.encode('utf-8'))
					_clear_selection()
				except Exception:
					pass
			return 'break'
		def _select_all(e = None):
			self.shellcmd.tag_add('sel', '1.0', 'end-1c')
			return 'break'
		_shellmenu = root.menu(tearoff = 0)
		_shellmenu.add_command(label = 'Copy', command = _copy_selection)
		_shellmenu.add_command(label = 'Paste', command = _paste_clipboard)
		_shellmenu.add_separator()
		_shellmenu.add_command(label = 'Select All', command = _select_all)
		_menu_posted = [False]
		def _unpost_menu():
			if _menu_posted[0]:
				_menu_posted[0] = False
				try:
					_shellmenu.unpost()
				except Exception:
					pass
		def _shellmenu_keyclose(e):
			if e.keysym not in ('Up', 'Down', 'Left', 'Right', 'Return', 'space', 'Shift_L', 'Shift_R', 'Control_L', 'Control_R', 'Alt_L', 'Alt_R'):
				_unpost_menu()
				return 'break'
		_shellmenu.bind('<KeyPress>', _shellmenu_keyclose)
		_shellmenu.bind('<Unmap>', lambda e: _menu_posted.__setitem__(0, False))
		def _popup(e):
			self.shellcmd.focus_set()
			_menu_posted[0] = True
			try:
				_shellmenu.tk_popup(e.x_root, e.y_root)
			finally:
				_shellmenu.grab_release()
			return 'break'
		def cs():
			self._pyshell_last_scan_key = None
			self._pyshell_cached_scope_result = None
			self.shellcmd.delete('1.0', 'end')
			cursor[0] = '1.0'
			screen_top[0] = 1
			prev_was_H1[0] = False
			_pending_esc[0] = ''
			_sgr_sel[0] = False
			_cursor_line[0] = 1
			_cursor_col[0] = 0
			self.shellcmd.focus()
			if platform.system() == 'Linux':
				try:
					_write_ref[0](b'\x0c')
				except Exception:
					pass
			else:
				try:
					_write_ref[0](b'\r')
				except Exception:
					pass
		def ks():
			running[0] = False
			self._pyshell_last_scan_key = None
			self._pyshell_cached_scope_result = None
			self._pyshell_session_names.clear()
			self._pyshell_session_types.clear()
			self._pyshell_session_classes.clear()
			self._pyshell_session_module_bases.clear()
			self._pyshell_session_func_origins.clear()
			self._pyshell_session_attr_types.clear()
			self._pyshell_session_class_attr_types.clear()
			self._pyshell_session_aliases.clear()
			self._pyshell_session_origins.clear()
			self._pyshell_session_method_params.clear()
			self._pyshell_session_accepts_any.clear()
			self._pyshell_session_func_params.clear()
			self._pyshell_session_func_accepts_any.clear()
			self._pyshell_session_class_bases.clear()
			for _inhk in ('members', 'attr_types', 'method_params'):
				self._pyshell_session_inherited[_inhk].clear()
			self._pyshell_session_instance_only.clear()
			try:
				_proc_ref[0].terminate()
			except Exception:
				pass
			if platform.system() == 'Linux' and _mfd_ref[0] is not None:
				try:
					os.close(_mfd_ref[0])
				except Exception:
					pass
				_mfd_ref[0] = None
			self.shellcmd.delete('1.0', 'end')
			cursor[0] = '1.0'
			screen_top[0] = 1
			prev_was_H1[0] = False
			_pending_esc[0] = ''
			_sgr_sel[0] = False
			_cursor_line[0] = 1
			_cursor_col[0] = 0
			self.shellcmd.focus()
			_start()
		self.shellcmd = root.textbox(master = self.sf, font = (monospace, 12), wrap = 'none')
		def _stop_pyshell_poller():
			running[0] = False
			if _poll_after_id[0] is not None:
				try:
					self.shellcmd.after_cancel(_poll_after_id[0])
				except Exception:
					pass
				_poll_after_id[0] = None
		self._pyshell_stop_poller = _stop_pyshell_poller
		clearshell = root.button(master = self.sf, text = 'Clear Shell', command = cs)
		killshell = root.button(master = self.sf, text = 'Restart Shell', command = ks)
		self.shellcmd.pack(fill = 'both')
		clearshell.pack(anchor = 'sw', side = 'left', padx = 10, pady = 10)
		killshell.pack(anchor = 'sw', side = 'left', padx = 10, pady = 10)
		self.shellcmd.unbind('<Control-a>')
		def _snap_caret(e = None):
			def _do():
				try:
					self.shellcmd.mark_set('insert', cursor[0])
				except Exception:
					pass
			try:
				self.shellcmd.after_idle(_do)
			except Exception:
				pass
		self.shellcmd.bind('<Key>', _key)
		self.shellcmd.bind('<ISO_Left_Tab>', _key)
		self.shellcmd.bind('<Button-1>', lambda e: _unpost_menu())
		self.shellcmd.bind('<ButtonRelease-1>', _snap_caret)
		self.shellcmd.bind('<ButtonRelease-3>', _popup)
		self.shellcmd.bind('<Button-2>', _paste_clipboard)
		self.shellcmd.bind('<<Paste>>', _paste_clipboard)
		self.shellcmd.bind('<<PasteSelection>>', _paste_clipboard)
		self.shellcmd.bind('<<Cut>>', lambda e: _copy_selection())
		self.shellcmd.bind('<<Clear>>', lambda e: 'break')
		self.shellcmd.bind('<Control-Shift-C>', _copy_selection)
		self.shellcmd.bind('<Control-Shift-V>', _paste_clipboard)
		self.shellcmd.bind('<Control-C>', _copy_selection)
		self.shellcmd.bind('<Control-V>', _paste_clipboard)
		def shell_setview():
			self.hapyshell()
			self._shell_setview_after_id = self.sf.after(50, shell_setview)
		_start()
		self._shell_setview_after_id = self.sf.after(50, shell_setview)
def saveforclose():
	for editor in all_editors:
		if not editor.saveforclose():
			return False
	return True
def _init_hl_tags():
	for editor in all_editors:
		editor.init_hl_tags()
def _init_pythonshell_hl_tags():
	for editor in all_editors:
		editor.init_pythonshell_hl_tags()
def _init_plugin_tags():
	for editor in all_editors:
		editor.init_plugin_tags()
for code in first:
	try:
		exec(code[1])
	except Exception as error:
		error = str(error)
		root.error('Error!', f'There was an error in the first part of the plugin "{os.path.basename(os.path.normpath(code[0]))}":\n{error}')
def ss():
	pcrunhook('before', 'show-pynotes-source-code')
	show('open pynotes source code')
	neweditor(f'{rootdir}/PyNotes.py')
	pcrunhook('after', 'show-pynotes-source-code')
def abt():
	show('open about pynotes')
	abw = root.subwin()
	abw.title('About PyNotes')
	abw.focus()
	abw_ = abw.frame()
	abw_.pack(fill = 'both', padx = 10, pady = 10)
	abw.imgs = []
	abw.image(master = abw_, image = f'{rootdir}/Icon.png', imsize = (2, 2)).grid(column = 0, row = 0, sticky = 'w')
	abw.text(master = abw_, text = f'PyNotes v{v}', font = ('TkDefaultFont', 20)).grid(column = 0, row = 1, sticky = 'w')
	abw.text(master = abw_, text = 'Rafey <https://github.com/rafugafu>', font = ('TkDefaultFont', 15)).grid(column = 0, row = 2, sticky = 'w')
	abw.text(master = abw_, text = 'PyNotes is an advanced, extensible, cross-platform\nEmacs-like text editor and IDE made in Python.', font = ('TkDefaultFont', 12)).grid(column = 0, row = 3, sticky = 'w')
	abw.button(text = 'Close', command = abw.destroy).pack(side = 'bottom', fill = 'x', padx = 10, pady = 10)
	abw.bind('<Escape>', lambda event: abw.destroy())
	abw.bind('<Return>', lambda event: abw.destroy())
	abw.sizablefalse()
def changes():
	show('show pynotes changes')
	cw = root.subwin()
	cw.title(f'Changes in v{v}')
	chtextbox = cw.textbox(scrolled = True, font = ('TkDefaultFont', 13), wrap = 'word')
	chtextbox.insert('end', changestr)
	chtextbox.text.config(state = 'disabled')
	chtextbox.yview_moveto(1)
	chtextbox.pack(fill = 'both', expand = True)
	cw.bind('<Escape>', lambda event: cw.destroy())
	cw.bind('<Return>', lambda event: cw.destroy())
	cw.sizablefalse()
	cw.style(root.gettheme())
	cw.focus()
def hemail():
	show('open email help')
	hew = root.subwin()
	hew.title('Help with Email')
	tabs = hew.tabs()
	mf = hew.frame()
	tabs.add(mf, text = 'Setup')
	tabs.pack(fill = 'both', expand = True, padx = 10, pady = 10)
	hew.text(master = mf, text = 'First change the HMode to Email with Alt-X and \'hmode:em\'.\nThis will enable the tab \'Email\'.\nGo to that tab and give the username and password of your email.\nThen you can type and send any email from PyNotes!').grid(padx = 10, pady = 10)
	dt = hew.frame()
	tabs.add(dt, text = 'Dictionaries')
	hew.text(master = dt, text = 'The email textbox has a spellcheck. The default dictionary for spellchecking is English,\nbut you can add or remove extra dictionaries to this.\nTo add another language or dictionary, you need to find or make a text file that has\none word in each line, without any spaces. (It can be any language)\nThen go to Preferences → Email to upload that dictionary.\n\nOnce you have added a dictionary, don\'t move or remove the\ndictionary before removing it in the settings.').grid(padx = 10, pady = 10)
	hew.sizablefalse()
	hew.style(root.gettheme())
	hew.focus()
def ext():
	answer = root.ask('Warning', 'Do you want to save files before closing?', options = ('yes', 'no', 'cancel')) if any(editor.unsaved for editor in all_editors) else False
	if answer != None:
		if answer:
			if not saveforclose():
				return
		try:
			pcrunhook('before', 'exit-pynotes')
		except Exception:
			pass
		try:
			if os.path.exists(f'{homedir}/.local/share/PyNotes/tempfiles'):
				shutil.rmtree(f'{homedir}/.local/share/PyNotes/tempfiles')
		except Exception:
			pass
		sys.stderr = open(os.devnull, 'w')
		for editor in all_editors:
			try:
				editor._cancel_all_after_ids()
			except Exception:
				pass
		for closer in list(_open_terminal_closers):
			try:
				closer()
			except Exception:
				pass
		try:
			root.destroy()
		except Exception:
			pass
		for editor in all_editors:
			try:
				editor.observer.stop()
			except Exception:
				pass
		try:
			pcrunhook('after', 'exit-pynotes')
		except Exception:
			pass
		os._exit(0)
def svprf():
	global bfr
	global theme
	global colours
	file = open(f'{homedir}/.local/share/PyNotes/defs', 'w+', encoding = 'utf-8')
	font = all_editors[0].type_.cget('font')[:-3].strip('{}')
	theme = colours.get('1.0', 'end-1c').replace('\n', '').replace('orgfont', 'type_.cget(\'font\')[:-3].strip(\'{}\')')
	file.write(f'{v}\n{str(bfr)}\n{font}\n{root.gettheme()}\n{",".join(dicts)}\n{emacskeysforsearch}\n{taborspace}\n{nographicalfiledialogs}\n{pythonexecutable}\n{theme}')
	file.close()
	exec('theme = {' + theme + '}', globals())
	_init_hl_tags()
	_init_pythonshell_hl_tags()
	_init_plugin_tags()
	for editor in all_editors:
		editor.keypress()
def prf():
	global bfr
	global colours
	pcrunhook('before', 'open-preferences')
	show('open preferences')
	def removedict():
		try:
			dicts.remove(dictlist.selection_get())
		except Exception:
			pass
		else:
			dictlist.delete(dictlist.curselection())
		emailwordlist.clear()
		try:
			for dictionary in dicts:
				if dictionary:
					emailwordlist.extend(open(dictionary, 'r', encoding = 'utf-8').read().split('\n'))
		except Exception as error:
			error = str(error)
			root.error('Error', error)
	def setts(val):
		global taborspace
		taborspace = val
	def setffre(val):
		global emacskeysforsearch
		emacskeysforsearch = val
	def setnoguifd(val):
		global nographicalfiledialogs
		nographicalfiledialogs = val
	def bf(opt):
		global bfr
		bfr = opt
	def adddict():
		dicttoadd = openfileget(prompttext = 'Email Dictionary File: ', filetypes = (('Text Files', '*.txt')))
		if dicttoadd:
			dicts.append(dicttoadd)
			dictlist.insert('end', dicttoadd)
			emailwordlist.clear()
			try:
				for dictionary in dicts:
					if dictionary:
						emailwordlist.extend(open(dictionary, 'r', encoding = 'utf-8').read().split('\n'))
			except Exception as error:
				error = str(error)
				root.error('Error', error)
	def changepyexec():
		global pythonexecutable
		nonlocal pyexecshowtext
		fn = openfileget(prompttext = 'New Python Executable: ', filetypes = (('All Files', '*')))
		if fn:
			pythonexecutable = fn
			pyexecshowtext.config(text = f'Python interpreter: \'{pythonexecutable}\'')
	def makeowntheme():
		pr.info('Info', 'Click Save after you\'re done. You can edit the theme later at any time.')
		ttkcreator = subprocess.Popen([sys.executable, '-m', 'ttkcreator'], stdout = subprocess.DEVNULL, stderr = subprocess.PIPE)
		ttkcreatorerrorhandler = ErrorHandler()
		for error in ttkcreator.stderr:
			ttkcreatorerrorhandler.write(error)
			ttkcreator.terminate()
		menu = sts['menu']
		menu.delete(0, 'end')
		for theme in tuple(sorted(root.themes())):
			menu.add_command(label = theme, command = lambda nt = theme: stsvar.set(nt))
	pr = root.subwin()
	pr.title('Preferences')
	tabs = pr.tabs()
	gt = pr.frame()
	tft = pr.frame()
	et = pr.frame()
	tabs.add(gt, text = 'General')
	bfc = pr.booleanvar(value = bfr)
	pr.check(master = gt, text = 'Backup file regularly', command = lambda: bf(bfc.get()), var = bfc).grid(column = 0, row = 0, sticky = 'w')
	varts = pr.booleanvar(value = taborspace)
	pr.check(master = gt, text = 'Use spaces instead of tabs for indentation commands', command = lambda: setts(varts.get()), var = varts).grid(column = 0, row = 1, sticky = 'w')
	varffre = pr.booleanvar(value = emacskeysforsearch)
	pr.check(master = gt, text = 'Use Emacs-like keybindings for the Find and Find & Replace', command = lambda: setffre(varffre.get()), var = varffre).grid(column = 0, row = 2, sticky = 'w')
	pr.text(master = gt, text = 'Emacs-like keys:\nFind keys:\nControl-R for previous match\nControl-S for next match\nEnter to close search\nFind & Replace keys:\n^ for previous\nAlt-Enter for next\nControl-T for replace and next\nEnter to close search').grid(column = 0, row = 3, sticky = 'w')
	varnoguifd = pr.booleanvar(value = nographicalfiledialogs)
	pr.check(master = gt, text = 'File prompts in the Alt-X command box (minibuffer) instead of a graphical file dialogue', command = lambda: setnoguifd(varnoguifd.get()), var = varnoguifd).grid(column = 0, row = 4, sticky = 'w')
	pr.frame(master = gt, height = 20).grid(column = 0, row = 4, sticky = 'w')
	pyexecshowtext = pr.text(master = gt, text = f'Python interpreter: \'{pythonexecutable}\'')
	pyexecshowtext.grid(column = 0, row = 5, sticky = 'w')
	pr.text(master = gt, text = 'Python executable to use for running Python code and the Python shell.\nNote: restart Python shell for this to take effect.').grid(column = 0, row = 6, sticky = 'w')
	pr.button(master = gt, text = 'Change', command = changepyexec).grid(column = 0, row = 7, sticky = 'ew')
	tabs.add(tft, text = 'Theme & Font')
	tabs.select(tft)
	tabs.pack(side = 'top', fill = 'x', padx = 10, pady = 10)
	mf = pr.frame(master = tft)
	mf.grid(column = 0, row = 0)
	pr.text(text = 'UI Theme', master = mf).grid(column = 0, row = 0, padx = 10, pady = 10)
	stsvar = pr.stringvar()
	sts = pr.dropdown(stringvar = stsvar, showdefault = root.gettheme(), options = tuple(sorted(root.themes())), command = lambda nt: [pr.sizabletrue(), pr.style(nt), root.style(nt), pr.sizablefalse()], master = mf)
	sts.grid(column = 1, row = 0, padx = 10, pady = 10, sticky = 'ew')
	pr.button(master = mf, text = 'Make your own!', command = makeowntheme).grid(column = 2, row = 0, padx = 10, pady = 10, sticky = 'w')
	pr.text(text = 'Editor Font', master = mf).grid(column = 0, row = 1, padx = 10, pady = 10)
	showfont = pr.textbox(master = tft, font = (all_editors[0].type_.cget('font')[:-3].strip('{}'), 12), wrap = 'word', height = 5)
	showfont.insert('end', 'The quick brown fox jumped over the lazy dogs\nAaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz\n1234567890\n?.,<>;:\'"{}[]\\|\n!@#$%^&*()-_+=')
	showfont.grid(column = 0, row = 1)
	f = pr.droptype(options = [monospace] + sorted(pr.getfonts()), master = mf, command = lambda: [pr.sizabletrue(), [editor.type_.config(font = (f.get(), 12)) for editor in all_editors], showfont.config(font = (f.get(), 12)), pr.sizablefalse()])
	f.grid(column = 1, row = 1, padx = 10, pady = 10, sticky = 'ew')
	f.insert('end', all_editors[0].type_.cget('font')[:-3].strip('{}'))
	f.config(state = 'readonly')
	pr.text(master = tft, text = 'Colours:').grid(column = 0, row = 2, padx = 10, pady = 10)
	colours = pr.textbox(master = tft, font = monospace, wrap = 'word', height = 5)
	colours.insert('end', str(theme)[:-1][1:].replace('type_.cget(\'font\')[:-3].strip(\'{}\')', 'orgfont'))
	colours.grid(column = 0, row = 3)
	pr.bind('<Escape>', lambda event: [svprf(), show('change / view preferences'), pr.destroy()])
	tabs.add(et, text = 'Email')
	pr.text(master = et, text = 'Dictionaries:').pack(padx = 10, pady = 10, side = 'top', anchor = 'n')
	dictlist = pr.listbox(master = et)
	for dictionary in dicts:
		dictlist.insert('end', dictionary)
	dictlist.pack(fill = 'both', expand = True, padx = 10, pady = 10, anchor = 'center')
	pr.button(master = et, text = 'Remove', command = removedict).pack(fill = 'x', expand = True, padx = 10, pady = 10, side = 'left', anchor = 'sw')
	pr.button(master = et, text = 'Add', command = adddict).pack(fill = 'x', expand = True, padx = 10, pady = 10, side = 'right', anchor = 'se')
	pr.button(text = 'OK', command = lambda: [svprf(), show('change / view preferences'), pr.destroy()]).pack(side = 'bottom', fill = 'x', padx = 10, pady = 10)
	pr.protocol('WM_DELETE_WINDOW', lambda: [svprf(), show('change / view preferences'), pr.destroy()])
	for code in plgnsprf:
		try:
			exec(code[1])
		except Exception as error:
			error = str(error)
			root.error('Error!', f'There was an error in setting up the preferences of the plugin "{os.path.basename(os.path.normpath(code[0]))}":\n{error}')
	pr.sizablefalse()
	pr.style(root.gettheme())
	pr.focus()
	pcrunhook('after', 'open-preferences')
_PYTHON_EDITOR_HL_SKIP_REMOVE_TAGS = {'sel', 'marked', 'found', 'foundhighlight'}
_PYTHON_SHELL_HL_SKIP_REMOVE_TAGS = {'sel', 'prompt'}
skiptags = {}
skiptagspythonshell = {}
plugin_hl = {}
def _find_closing_brace(text, start):
	depth = 1
	i = start + 1
	while i < len(text) and depth > 0:
		if text[i] == '\\' and i + 1 < len(text):
			i += 2
			continue
		if text[i] == '{':
			depth += 1
		elif text[i] == '}':
			depth -= 1
		i += 1
	return i if depth == 0 else len(text)
def _find_closing_bracket(text, start):
	depth = 1
	i = start + 1
	while i < len(text) and depth > 0:
		if text[i] == '\\' and i + 1 < len(text):
			i += 2
			continue
		if text[i] == '[':
			depth += 1
		elif text[i] == ']':
			depth -= 1
		i += 1
	return i if depth == 0 else len(text)
def _find_closing_tag(text, start):
	i = start + 1
	in_quote = None
	while i < len(text):
		if text[i] == '\\' and i + 1 < len(text) and in_quote:
			i += 2
			continue
		if in_quote:
			if text[i] == in_quote:
				in_quote = None
		else:
			if text[i] in ('"', '\''):
				in_quote = text[i]
			elif text[i] == '>':
				return i + 1
		i += 1
	return len(text)
def _python_bytecol_to_charcol(line_str, bytecol):
	if bytecol <= 0:
		return bytecol
	encoded = line_str.encode('utf-8')
	if bytecol >= len(encoded):
		return len(line_str)
	return len(encoded[:bytecol].decode('utf-8', 'ignore'))
_PYTHON_KW_PAT = re.compile(r'(?<!\.)\b(?:' + '|'.join(re.escape(k) for k in keyword.kwlist) + r')\b')
_PYTHON_OP_PAT = re.compile(r'\*\*=|//=|<<=|>>=|:=|==|!=|<=|>=|\+=|-=|\*=|/=|%=|&=|\|=|\^=|@=|->|\*\*|//|<<|>>|[+\-*/%@&|^~=<>]')
_LH_PAT = re.compile(r'(?<!\\)%[^\n]*(?:\n|$)')
_LATEX_MATH_PAT = re.compile(r'\$\$[\s\S]*?\$\$|\\\[[\s\S]*?\\\]|\\\([\s\S]*?\\\)|\$(?!\$)(?:[^$\\]|\\.)*?\$(?!\$)')
_HC_PAT = re.compile(r'<!--.*?-->', re.DOTALL)
_HTML_ATTR_PAT = re.compile(r'\s([\w:-]+)\s*=\s*("(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\'|[^\s"\'=<>]+)', re.IGNORECASE)
_HTML_BOOL_ATTR_PAT = re.compile(r'\b(?:async|autofocus|autoplay|checked|controls|default|defer|disabled|formnovalidate|hidden|ismap|loop|multiple|muted|nomodule|novalidate|open|readonly|required|reversed|selected)\b', re.IGNORECASE)
_MDH_PAT = re.compile(r'(?m)^(#{1,6})(?:[ \t].*)?$')
_MDBI_PAT = re.compile(r'(?<!\\)\*\*\*(?:\\.|[^*\n])+?\*\*\*|(?<!\\)___(?:\\.|[^_\n])+?___|(?<!\\)\*\*_(?:\\.|[^_\n])+?_\*\*|(?<!\\)__\*(?:\\.|[^*\n])+?\*__|(?<!\\)\*__(?:\\.|[^_\n])+?__\*|(?<!\\)_\*\*(?:\\.|[^*\n])+?\*\*_')
_MDB_PAT = re.compile(r'(?<!\\)\*\*(?:\\.|[^*\n])+?\*\*|(?<!\\)__(?:\\.|[^_\n])+?__')
_MDI_PAT = re.compile(r'(?<!\\)(?<!\*)\*(?:\\.|[^*\n])+?\*(?!\*)|(?<!\\)(?<!_)_(?:\\.|[^_\n])+?_(?!_)')
_MDS_PAT = re.compile(r'(?<!\\)~~(?:\\.|[^~\n])+?~~')
_MDC_PAT = re.compile(r'(?<!\\)`(?:\\.|[^`\n])+?`')
_MDL_PAT = re.compile(r'(?<!\\)\[(?:\\.|[^\]\n])*\]\((?:\\.|[^)\n])*\)')
_MDQ_PAT = re.compile(r'(?m)^>.*$')
_MD_HTML_TAGS = ('hstuff', 'hattr', 'hstr', 'hcmt')
DEBOUNCE_TIME = 300
class _PythonScanCancelled(BaseException):
	pass
class _PythonScopeBuilder(ast.NodeVisitor):
	def __init__(self):
		self.scopes = [{'start': 1, 'end': 1, 'start_col': 0, 'end_col': None, 'parent': None, 'kind': 'module', 'names': {}, 'globals': {}, 'nonlocals': {}}]
		self.scope_stack = [0]
		self.func_params = {}
		self.func_accepts_any = {}
		self.pending_calls = []
		self.module_aliases = {}
		self.module_alias_lines = {}
		self.module_alias_defs = {}
		self.from_imports = []
		self.import_names = []
		self.module_literals = []
		self.import_dotted_lines = []
		self.import_orig_names = []
		self.def_names = []
		self.kwarg_positions = []
		self.alias_assigns = []
		self.dotted_alias_assigns = []
		self.dynamic_imports = []
		self.class_def_kwargs = []
		self.global_seed_names = set()
		self.nonlocal_seeds = []
		self._in_class_body = False
	def add_name(self, name, lineno, kind):
		sc_idx = self.scope_stack[-1]
		sc = self.scopes[sc_idx]
		if name in sc.get('globals', {}):
			sc_idx = 0
		elif name in sc.get('nonlocals', {}):
			_p = sc['parent']
			while _p is not None:
				_ps = self.scopes[_p]
				if _ps.get('kind') == 'function' and name not in _ps.get('globals', {}) and name not in _ps.get('nonlocals', {}):
					sc_idx = _p
					break
				_p = _ps['parent']
		names = self.scopes[sc_idx]['names']
		names.setdefault(name, []).append((lineno, kind))
	def targets(self, node):
		out = []
		if isinstance(node, ast.Name):
			out.append(node)
		elif isinstance(node, ast.Attribute):
			out.append(node)
		elif isinstance(node, (ast.Tuple, ast.List)):
			for elt in node.elts:
				out.extend(self.targets(elt))
		elif isinstance(node, ast.Starred):
			out.extend(self.targets(node.value))
		return out
	def push_scope(self, start, end, kind = 'function', start_col = 0, end_col = None):
		idx = len(self.scopes)
		self.scopes.append({'start': start, 'end': end, 'start_col': start_col, 'end_col': end_col, 'parent': self.scope_stack[-1], 'kind': kind, 'names': {}, 'globals': {}, 'nonlocals': {}})
		self.scope_stack.append(idx)
		return idx
	def add_args(self, args, lineno, is_method = False):
		all_args = list(args.posonlyargs) + list(args.args) + list(args.kwonlyargs)
		for i, a in enumerate(all_args):
			self.add_name(a.arg, lineno, 'first_param' if (is_method and i == 0) else 'func_arg')
		if args.vararg:
			self.add_name(args.vararg.arg, lineno, 'func_arg')
		if args.kwarg:
			self.add_name(args.kwarg.arg, lineno, 'func_arg')
	def visit_FunctionDef(self, node):
		self.visit_function(node)
	def visit_AsyncFunctionDef(self, node):
		self.visit_function(node)
	def visit_function(self, node):
		self.add_name(node.name, node.lineno, 'func')
		self.def_names.append((node.lineno, node.name, 'func'))
		params = set()
		for a in list(node.args.args) + list(node.args.kwonlyargs):
			params.add(a.arg)
		self.func_params.setdefault(node.name, []).append((node.lineno, params, self.scope_stack[-1]))
		self.func_accepts_any.setdefault(node.name, []).append((node.lineno, bool(node.args.kwarg), self.scope_stack[-1]))
		for dec in node.decorator_list:
			self.visit(dec)
		for d in list(node.args.defaults) + [kd for kd in node.args.kw_defaults if kd is not None]:
			self.visit(d)
		end = getattr(node, 'end_lineno', node.lineno)
		is_method = self._in_class_body and _python_method_has_implicit_first_param(node)
		prev_in_class_body = self._in_class_body
		self._in_class_body = False
		self.push_scope(node.lineno, end, start_col = node.col_offset)
		self.add_args(node.args, node.lineno, is_method)
		for stmt in node.body:
			self.visit(stmt)
		self.scope_stack.pop()
		self._in_class_body = prev_in_class_body
	def _dotted_path(self, node):
		parts = []
		cur = node
		while isinstance(cur, ast.Attribute):
			parts.append(cur.attr)
			cur = cur.value
		if isinstance(cur, ast.Name):
			parts.append(cur.id)
			parts.reverse()
			return parts
		return None
	def visit_Call(self, node):
		func_name = None
		is_name = isinstance(node.func, ast.Name)
		if is_name:
			func_name = node.func.id
		elif isinstance(node.func, ast.Attribute):
			func_name = node.func.attr
		dotted = self._dotted_path(node.func)
		for kw in node.keywords:
			if kw.arg is not None:
				self.pending_calls.append((getattr(kw, 'lineno', node.lineno), func_name, kw.arg, is_name, dotted, node))
				kw_lineno = getattr(kw, 'lineno', None)
				kw_col = getattr(kw, 'col_offset', None)
				if kw_lineno is not None and kw_col is not None:
					self.kwarg_positions.append((kw_lineno, kw_col, kw.arg))
		self.generic_visit(node)
	def visit_ClassDef(self, node):
		self.add_name(node.name, node.lineno, 'class')
		self.def_names.append((node.lineno, node.name, 'class'))
		for _ckw in node.keywords:
			if _ckw.arg is None:
				continue
			_ckwl = getattr(_ckw, 'lineno', node.lineno)
			_ckwc = getattr(_ckw, 'col_offset', None)
			if _ckwc is not None:
				self.kwarg_positions.append((_ckwl, _ckwc, _ckw.arg))
			self.class_def_kwargs.append((_ckwl, node.name, node.lineno, _ckw.arg))
		for dec in node.decorator_list:
			self.visit(dec)
		end = getattr(node, 'end_lineno', node.lineno)
		self.push_scope(node.lineno, end, 'class', node.col_offset)
		prev_in_class_body = self._in_class_body
		self._in_class_body = True
		for stmt in node.body:
			self.visit(stmt)
		self._in_class_body = prev_in_class_body
		self.scope_stack.pop()
		for stmt in node.body:
			if isinstance(stmt, ast.FunctionDef) and stmt.name == '__init__':
				_iargs = list(stmt.args.posonlyargs) + list(stmt.args.args) + list(stmt.args.kwonlyargs)
				params = set(a.arg for a in _iargs[1:]) - set(a.arg for a in stmt.args.posonlyargs)
				if stmt.args.vararg:
					params.add(stmt.args.vararg.arg)
				if stmt.args.kwarg:
					params.add(stmt.args.kwarg.arg)
				self.func_accepts_any.setdefault(node.name, []).append((node.lineno, bool(stmt.args.kwarg), self.scope_stack[-1]))
				self.func_params.setdefault(node.name, []).append((node.lineno, params, self.scope_stack[-1]))
				break
	def visit_Lambda(self, node):
		end = getattr(node, 'end_lineno', node.lineno)
		self.push_scope(node.lineno, end, start_col = node.col_offset, end_col = getattr(node, 'end_col_offset', None))
		self.add_args(node.args, node.lineno)
		self.visit(node.body)
		self.scope_stack.pop()
	def visit_comp(self, node):
		end = getattr(node, 'end_lineno', node.lineno)
		self.push_scope(node.lineno, end, start_col = node.col_offset, end_col = getattr(node, 'end_col_offset', None))
		for gen in node.generators:
			for nm in self.targets(gen.target):
				if not isinstance(nm, ast.Attribute):
					self.add_name(nm.id, node.lineno, 'var')
			self.visit(gen.iter)
			for cond in gen.ifs:
				self.visit(cond)
		if isinstance(node, ast.DictComp):
			self.visit(node.key)
			self.visit(node.value)
		else:
			self.visit(node.elt)
		self.scope_stack.pop()
	def visit_ListComp(self, node):
		self.visit_comp(node)
	def visit_SetComp(self, node):
		self.visit_comp(node)
	def visit_DictComp(self, node):
		self.visit_comp(node)
	def visit_GeneratorExp(self, node):
		self.visit_comp(node)
	def _register_lambda(self, name, lineno, lam):
		_largs = lam.args
		_lparams = set(a.arg for a in list(_largs.args) + list(_largs.kwonlyargs))
		self.func_params.setdefault(name, []).append((lineno, _lparams, self.scope_stack[-1]))
		self.func_accepts_any.setdefault(name, []).append((lineno, bool(_largs.kwarg), self.scope_stack[-1]))
	def visit_Assign(self, node):
		_is_lambda = isinstance(node.value, ast.Lambda)
		for t in node.targets:
			if _is_lambda and isinstance(t, ast.Name):
				self.add_name(t.id, node.lineno, 'func')
				self._register_lambda(t.id, node.lineno, node.value)
				continue
			for nm in self.targets(t):
				if not isinstance(nm, ast.Attribute):
					self.add_name(nm.id, node.lineno, 'var')
		for _ntgt in node.targets:
			if not isinstance(_ntgt, ast.Name):
				continue
			tgt_name = _ntgt.id
			val = node.value
			if isinstance(val, ast.Name):
				self.alias_assigns.append((self.scope_stack[-1], node.lineno, tgt_name, val.id))
			elif isinstance(val, ast.Attribute):
				self.dotted_alias_assigns.append((self.scope_stack[-1], node.lineno, tgt_name, val))
			elif isinstance(val, ast.Call):
				_dr = self._dynamic_import_module(val)
				if _dr is not None:
					self.dynamic_imports.append((self.scope_stack[-1], node.lineno, tgt_name, _dr[0], _dr[1]))
				_pt = _python_partial_target(val)
				if _pt is not None:
					self.alias_assigns.append((self.scope_stack[-1], node.lineno, tgt_name, _pt))
		for _ttgt in node.targets:
			if not (isinstance(_ttgt, (ast.Tuple, ast.List)) and isinstance(node.value, (ast.Tuple, ast.List)) and len(_ttgt.elts) == len(node.value.elts)):
				continue
			for _tgt_el, _val_el in zip(_ttgt.elts, node.value.elts):
				if not isinstance(_tgt_el, ast.Name):
					continue
				if isinstance(_val_el, ast.Name):
					self.alias_assigns.append((self.scope_stack[-1], node.lineno, _tgt_el.id, _val_el.id))
				elif isinstance(_val_el, ast.Attribute):
					self.dotted_alias_assigns.append((self.scope_stack[-1], node.lineno, _tgt_el.id, _val_el))
				elif isinstance(_val_el, ast.Call):
					_dr = self._dynamic_import_module(_val_el)
					if _dr is not None:
						self.dynamic_imports.append((self.scope_stack[-1], node.lineno, _tgt_el.id, _dr[0], _dr[1]))
		self.visit(node.value)
	def _dynamic_import_module(self, call):
		fn = call.func
		is_builtin_import = isinstance(fn, ast.Name) and fn.id == '__import__'
		is_importlib = isinstance(fn, ast.Attribute) and fn.attr == 'import_module'
		if not (is_builtin_import or is_importlib) or not call.args:
			return None
		arg = call.args[0]
		if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
			if is_builtin_import and not _python_import_fromlist_is_nonempty(call):
				return arg.value.split('.')[0], is_builtin_import
			return arg.value, is_builtin_import
		return None
	def visit_AnnAssign(self, node):
		if isinstance(node.value, ast.Lambda) and isinstance(node.target, ast.Name):
			self.add_name(node.target.id, node.lineno, 'func')
			self._register_lambda(node.target.id, node.lineno, node.value)
			self.visit(node.value)
			return
		for nm in self.targets(node.target):
			if not isinstance(nm, ast.Attribute):
				self.add_name(nm.id, node.lineno, 'var')
		if node.value is not None:
			self.visit(node.value)
	def visit_AugAssign(self, node):
		for nm in self.targets(node.target):
			if not isinstance(nm, ast.Attribute):
				self.add_name(nm.id, node.lineno, 'var')
		self.visit(node.value)
	def visit_For(self, node):
		self.visit_for(node)
	def visit_AsyncFor(self, node):
		self.visit_for(node)
	def visit_for(self, node):
		for nm in self.targets(node.target):
			if not isinstance(nm, ast.Attribute):
				self.add_name(nm.id, node.lineno, 'var')
		self.visit(node.iter)
		for stmt in node.body:
			self.visit(stmt)
		for stmt in node.orelse:
			self.visit(stmt)
	def visit_With(self, node):
		self.visit_with(node)
	def visit_AsyncWith(self, node):
		self.visit_with(node)
	def visit_with(self, node):
		for item in node.items:
			self.visit(item.context_expr)
			if item.optional_vars is not None:
				for nm in self.targets(item.optional_vars):
					if not isinstance(nm, ast.Attribute):
						self.add_name(nm.id, node.lineno, 'var')
		for stmt in node.body:
			self.visit(stmt)
	def visit_ExceptHandler(self, node):
		if node.name:
			self.add_name(node.name, node.lineno, 'var')
		if node.type is not None:
			self.visit(node.type)
		for stmt in node.body:
			self.visit(stmt)
	def visit_Import(self, node):
		for alias in node.names:
			imported_name = alias.name
			top_name = imported_name.split('.')[0]
			used_name = alias.asname if alias.asname else top_name
			self.import_names.append((self.scope_stack[-1], imported_name, top_name, used_name, node.lineno))
			self.module_literals.append((node.lineno, top_name))
			if '.' in imported_name:
				_acol = getattr(alias, 'col_offset', None)
				if _acol is not None:
					self.import_dotted_lines.append((node.lineno, _acol, imported_name))
			if alias.asname:
				self.module_aliases[alias.asname] = imported_name
				self.module_alias_lines[alias.asname] = node.lineno
				self.module_alias_defs.setdefault(alias.asname, []).append((node.lineno, imported_name))
	def visit_ImportFrom(self, node):
		if node.module:
			self.module_literals.append((node.lineno, node.module.split('.')[0]))
			if '.' in node.module:
				_fcol = getattr(node, 'col_offset', None)
				if _fcol is not None:
					self.import_dotted_lines.append((node.lineno, _fcol + 5, node.module))
		for alias in node.names:
			name = alias.asname if alias.asname else alias.name
			self.from_imports.append((self.scope_stack[-1], node.module, name, alias.name, node.lineno))
			if alias.asname and alias.name != '*':
				_ocol = getattr(alias, 'col_offset', None)
				if _ocol is not None:
					self.import_orig_names.append((node.lineno, _ocol, alias.name, node.module))
	def visit_NamedExpr(self, node):
		for nm in self.targets(node.target):
			if not isinstance(nm, ast.Attribute):
				self.add_name(nm.id, node.lineno, 'var')
		self.visit(node.value)
	def visit_Global(self, node):
		scope_idx = self.scope_stack[-1]
		for name in node.names:
			self.scopes[scope_idx]['globals'][name] = node.lineno
			self.global_seed_names.add(name)
	def visit_Nonlocal(self, node):
		scope_idx = self.scope_stack[-1]
		for name in node.names:
			self.scopes[scope_idx]['nonlocals'][name] = node.lineno
			parent_idx = self.scopes[scope_idx]['parent']
			if parent_idx is not None:
				self.nonlocal_seeds.append((parent_idx, name))
def _python_method_has_implicit_first_param(node):
	for dec in getattr(node, 'decorator_list', []):
		_dn = None
		if isinstance(dec, ast.Name):
			_dn = dec.id
		elif isinstance(dec, ast.Attribute):
			_dn = dec.attr
		elif isinstance(dec, ast.Call):
			_df = dec.func
			if isinstance(_df, ast.Name):
				_dn = _df.id
			elif isinstance(_df, ast.Attribute):
				_dn = _df.attr
		if _dn == 'staticmethod':
			return False
	return True
_PYTHON_DESCRIPTOR_WRAPPERS = {'staticmethod', 'classmethod'}
def _python_c3_linearize(cls, bases_map, seen, depth = 0):
	if cls in seen or depth > 40:
		return [cls]
	_seen2 = seen | {cls}
	_seqs = []
	for _b in bases_map.get(cls, []):
		_bl = _python_c3_linearize(_b, bases_map, _seen2, depth + 1)
		if _bl:
			_seqs.append(list(_bl))
	_direct = list(bases_map.get(cls, []))
	if _direct:
		_seqs.append(_direct)
	out = [cls]
	while _seqs:
		cand = None
		for _s in _seqs:
			_h = _s[0]
			if not any(_h in _o[1:] for _o in _seqs):
				cand = _h
				break
		if cand is None:
			cand = _seqs[0][0]
		if cand not in out:
			out.append(cand)
		_next = []
		for _s in _seqs:
			_s = [_x for _x in _s if _x != cand]
			if _s:
				_next.append(_s)
		_seqs = _next
	return out
def _python_partial_target(call):
	if not isinstance(call, ast.Call) or not call.args:
		return None
	_fn = call.func
	_isp = (isinstance(_fn, ast.Name) and _fn.id == 'partial') or (isinstance(_fn, ast.Attribute) and _fn.attr == 'partial')
	if not _isp:
		return None
	if isinstance(call.args[0], ast.Name):
		return call.args[0].id
	return None
def _python_unwrap_descriptor(val):
	while isinstance(val, ast.Call) and isinstance(val.func, ast.Name) and val.func.id in _PYTHON_DESCRIPTOR_WRAPPERS and len(val.args) == 1 and not val.keywords:
		val = val.args[0]
	return val
def _python_import_fromlist_is_nonempty(call):
	_fl = None
	if len(call.args) >= 4:
		_fl = call.args[3]
	else:
		for _kw in call.keywords:
			if _kw.arg == 'fromlist':
				_fl = _kw.value
				break
	if _fl is None:
		return False
	if isinstance(_fl, (ast.List, ast.Tuple, ast.Set)):
		return len(_fl.elts) > 0
	if isinstance(_fl, ast.Constant) and _fl.value is None:
		return False
	return True
def _python_static_value_kind(val, members, prefix):
	val = _python_unwrap_descriptor(val)
	if isinstance(val, ast.Lambda):
		return 'func'
	if isinstance(val, ast.Name):
		_k = members.get(f'{prefix}.{val.id}') if prefix else members.get(val.id)
		if _k is None:
			_k = members.get(val.id)
		if _k in ('func', 'class'):
			return _k
		if val.id in _PYTHON_BUILTIN_MEMBERS:
			return 'class'
		if val.id in _PYTHON_BUILTIN_CALLABLE_NAMES:
			return 'func'
	return None
def _python_inspect_ast_members(node_list, prefix = ''):
	members = {}
	for node in node_list:
		if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
			key = f'{prefix}.{node.name}' if prefix else node.name
			members[key] = 'func'
		elif isinstance(node, ast.ClassDef):
			key = f'{prefix}.{node.name}' if prefix else node.name
			members[key] = 'class'
			class_members = _python_inspect_ast_members(node.body, key)
			members.update(class_members)
			for _sub in node.body:
				if isinstance(_sub, (ast.FunctionDef, ast.AsyncFunctionDef)) and _sub.args.args and _python_method_has_implicit_first_param(_sub):
					_sfp = _sub.args.args[0].arg
					for _sst in ast.walk(_sub):
						_stgts = _sst.targets if isinstance(_sst, ast.Assign) else ([_sst.target] if isinstance(_sst, (ast.AnnAssign, ast.AugAssign)) else [])
						_sval = _sst.value if isinstance(_sst, (ast.Assign, ast.AnnAssign)) else None
						for _st in _stgts:
							_sdirect = not isinstance(_st, (ast.Tuple, ast.List))
							for _ste in (_st.elts if isinstance(_st, (ast.Tuple, ast.List)) else [_st]):
								if isinstance(_ste, ast.Starred):
									_ste = _ste.value
								if isinstance(_ste, ast.Attribute) and isinstance(_ste.value, ast.Name) and _ste.value.id == _sfp:
									_skind = (_python_static_value_kind(_sval, members, prefix) if _sdirect and _sval is not None else None) or 'var'
									members.setdefault(f'{key}.{_ste.attr}', _skind)
			if not prefix:
				is_global_enum = any(
					(isinstance(d, ast.Name) and d.id == 'global_enum') or
					(isinstance(d, ast.Attribute) and d.attr == 'global_enum')
					for d in node.decorator_list
				)
				if is_global_enum:
					pfx = key + '.'
					for sub_key, val in class_members.items():
						bare = sub_key[len(pfx):]
						if '.' not in bare:
							members[bare] = val
		elif isinstance(node, ast.Assign):
			for target in node.targets:
				for _tel in (target.elts if isinstance(target, (ast.Tuple, ast.List)) else [target]):
					if isinstance(_tel, ast.Starred):
						_tel = _tel.value
					if isinstance(_tel, ast.Name):
						key = f'{prefix}.{_tel.id}' if prefix else _tel.id
						members[key] = (_python_static_value_kind(node.value, members, prefix) if _tel is target else None) or 'var'
		elif isinstance(node, ast.AnnAssign):
			if isinstance(node.target, ast.Name):
				key = f'{prefix}.{node.target.id}' if prefix else node.target.id
				members[key] = _python_static_value_kind(node.value, members, prefix) or 'var'
		elif isinstance(node, (ast.For, ast.AsyncFor, ast.While)):
			members.update(_python_inspect_ast_members(node.body, prefix))
			members.update(_python_inspect_ast_members(node.orelse, prefix))
		elif isinstance(node, ast.If):
			members.update(_python_inspect_ast_members(node.body, prefix))
			members.update(_python_inspect_ast_members(node.orelse, prefix))
		elif isinstance(node, (ast.With, ast.AsyncWith)):
			members.update(_python_inspect_ast_members(node.body, prefix))
		elif isinstance(node, ast.Try):
			members.update(_python_inspect_ast_members(node.body, prefix))
			for _th in node.handlers:
				members.update(_python_inspect_ast_members(_th.body, prefix))
			members.update(_python_inspect_ast_members(node.orelse, prefix))
			members.update(_python_inspect_ast_members(node.finalbody, prefix))
	return members
import importlib.machinery as _python_importlib_machinery
_PYTHON_EXTENSION_SUFFIXES = tuple(_python_importlib_machinery.EXTENSION_SUFFIXES)
_PYTHON_STDLIB_BUILTIN_MODULES = set(sys.builtin_module_names)
class _PythonModuleSpec:
	def __init__(self, name, origin, search_locations):
		self.name = name
		self.origin = origin
		self.submodule_search_locations = search_locations
def _python_resolve_toplevel_fs(name):
	for _dir in sys.path:
		try:
			_dir = _dir or os.getcwd()
		except Exception:
			continue
		_pkg = os.path.join(_dir, name, '__init__.py')
		if os.path.isfile(_pkg):
			return _PythonModuleSpec(name, _pkg, [os.path.dirname(_pkg)])
		_pdir = os.path.join(_dir, name)
		if os.path.isdir(_pdir):
			return _PythonModuleSpec(name, None, [_pdir])
		_mod = os.path.join(_dir, name + '.py')
		if os.path.isfile(_mod):
			return _PythonModuleSpec(name, _mod, None)
		for _ext in _PYTHON_EXTENSION_SUFFIXES:
			if os.path.isfile(os.path.join(_dir, name + _ext)):
				return _PythonModuleSpec(name, os.path.join(_dir, name + _ext), None)
	if name in _PYTHON_STDLIB_BUILTIN_MODULES:
		return _PythonModuleSpec(name, 'built-in', None)
	return None
def _python_module_src_path(spec, name):
	if spec is None or not spec.origin:
		return None
	if spec.origin.endswith('.py') and os.path.isfile(spec.origin):
		return spec.origin
	for _cand_name in (name, getattr(spec, 'name', None)):
		if not _cand_name:
			continue
		for _sp in sys.path:
			_candidate = os.path.join(_sp, *_cand_name.split('.')) + '.py'
			if os.path.isfile(_candidate):
				return _candidate
			_pkg_init = os.path.join(_sp, *_cand_name.split('.'), '__init__.py')
			if os.path.isfile(_pkg_init):
				return _pkg_init
	return None
def _python_relative_import_target(name, level, module, is_package):
	if level == 0:
		return module
	base = name.split('.')
	_strip = level - 1 if is_package else level
	if _strip > 0:
		base = base[:-_strip] if _strip < len(base) else []
	if module:
		base = base + module.split('.')
	return '.'.join(base) if base else module
def pdf(title):
	if os.path.splitext(title)[1] == '.tex':
		pdf_ = os.path.splitext(title)[0]
	else:
		pdf_ = title
	pdf_ += '.pdf'
	if not os.path.exists(pdf_):
		if root.ask('Error', 'The pdf could not be shown, there might have been an error in your code.\nDo you want to see the log?', ('yes', 'no')):
			logwin = root.subwin()
			logwin.title(f'LaTeX log for {os.path.basename(title)}')
			logtextboxscroll = logwin.scroll()
			logtextbox = logwin.textbox(yscrollcommand = logtextboxscroll.set, font = (monospace, 12))
			try:
				logtextbox.insert('1.0', open(f'{os.path.splitext(title)[0]}.log', 'r', encoding = 'utf-8').read())
			except:
				root.error('Error!', f'The log was not found at "{os.path.splitext(title)[0]}.log".')
			logtextbox.config(state = 'disabled')
			logtextboxscroll.config(command = logtextbox.yview)
			logtextboxscroll.pack(fill = 'y', side = 'right')
			logtextbox.pack(fill = 'both', expand = True, side = 'left')
			logwin.style(root.gettheme())
	elif platform.system() == 'Linux':
		subprocess.run(['xdg-open', pdf_], cwd = os.path.dirname(title))
	else:
		subprocess.run(['start', pdf_], cwd = os.path.dirname(title))
def rb():
	root.info('Recover Backup', '1. Go to the directory of the lost file\n2. Press Ctrl+h to show hidden files if on Linux\n3. You will see something like .filebackpynotes.txt\n4. Copy it into the original lost file.\n(This may not be an exact copy)')
def termexec(command):
	pcrunhook('before', 'term-exec', command)
	if command[:2] == 'cd':
		try:
			os.chdir(command[3:])
		except Exception as error:
			item = str(error)
		else:
			item = ''
	else:
		try:
			result = subprocess.run(command, shell = True, text = True, capture_output = True, timeout = 5)
			item = result.stdout + result.stderr
		except Exception as error:
			item = str(error)
	pcrunhook('after', 'term-exec', command)
	return item
_PTY_POLL_CHAR_BUDGET = 16384
_PTY_MAX_PENDING_ESC = 4096
_TERM_FRAME_MS = 16
_TERM_FRAME_BUDGET = 0.008
def _sgr_is_highlight(params):
	result = None
	idx = 0
	while idx < len(params):
		code = params[idx]
		if code == 0:
			result = False
		elif code == 7:
			result = True
		elif code == 27 or code == 49:
			result = False
		elif code in (41, 42, 43, 44, 45, 46, 47) or (100 <= code <= 107):
			result = True
		elif code == 40:
			result = False
		elif code == 48:
			result = True
			if idx + 1 < len(params) and params[idx + 1] == 5:
				idx += 2
			elif idx + 1 < len(params) and params[idx + 1] == 2:
				idx += 4
		idx += 1
	return result
_TERM_ANSI_16_HEX = ('#000000', '#cd0000', '#00cd00', '#cdcd00', '#0000ee', '#cd00cd', '#00cdcd', '#e5e5e5', '#7f7f7f', '#ff0000', '#00ff00', '#ffff00', '#5c5cff', '#ff00ff', '#00ffff', '#ffffff')
_TERM_ANSI_CUBE_LEVELS = (0, 95, 135, 175, 215, 255)
def _ansi_256_hex(n):
	if n < 16:
		return _TERM_ANSI_16_HEX[n]
	if n < 232:
		n -= 16
		return f'#{_TERM_ANSI_CUBE_LEVELS[n // 36]:02x}{_TERM_ANSI_CUBE_LEVELS[(n % 36) // 6]:02x}{_TERM_ANSI_CUBE_LEVELS[n % 6]:02x}'
	v = 8 + (n - 232) * 10
	return f'#{v:02x}{v:02x}{v:02x}'
def _sgr_new_state():
	return {'fg': None, 'bg': None, 'bold': False, 'italic': False, 'underline': False, 'reverse': False}
def _sgr_apply(state, params):
	if not params:
		params = [0]
	i = 0
	while i < len(params):
		c = params[i]
		if c == 0:
			state.update(fg = None, bg = None, bold = False, italic = False, underline = False, reverse = False)
		elif c == 1:
			state['bold'] = True
		elif c == 3:
			state['italic'] = True
		elif c == 4:
			state['underline'] = True
		elif c == 7:
			state['reverse'] = True
		elif c == 22:
			state['bold'] = False
		elif c == 23:
			state['italic'] = False
		elif c == 24:
			state['underline'] = False
		elif c == 27:
			state['reverse'] = False
		elif 30 <= c <= 37:
			state['fg'] = c - 30
		elif c == 38:
			if i + 2 < len(params) and params[i + 1] == 5:
				state['fg'] = params[i + 2]; i += 2
			elif i + 4 < len(params) and params[i + 1] == 2:
				state['fg'] = (params[i + 2], params[i + 3], params[i + 4]); i += 4
		elif c == 39:
			state['fg'] = None
		elif 40 <= c <= 47:
			state['bg'] = c - 40
		elif c == 48:
			if i + 2 < len(params) and params[i + 1] == 5:
				state['bg'] = params[i + 2]; i += 2
			elif i + 4 < len(params) and params[i + 1] == 2:
				state['bg'] = (params[i + 2], params[i + 3], params[i + 4]); i += 4
		elif c == 49:
			state['bg'] = None
		elif 90 <= c <= 97:
			state['fg'] = c - 90 + 8
		elif 100 <= c <= 107:
			state['bg'] = c - 100 + 8
		i += 1
def _sgr_colour_hex(c):
	if c is None:
		return None
	if isinstance(c, tuple):
		return f'#{c[0]:02x}{c[1]:02x}{c[2]:02x}'
	return _ansi_256_hex(c)
def _term_sgr_resolve(state, default_fg, default_bg):
	fg = default_fg if state['fg'] is None else _sgr_colour_hex(state['fg'])
	bg = default_bg if state['bg'] is None else _sgr_colour_hex(state['bg'])
	if state['bold'] and isinstance(state['fg'], int) and state['fg'] < 8:
		fg = _ansi_256_hex(state['fg'] + 8)
	if state['reverse']:
		oldfg = fg
		fg = bg if bg is not None else default_bg
		bg = oldfg if oldfg is not None else default_fg
	return fg, bg
def term(command = None, title = 'Terminal', endmessage = None, blocking = False, **kwargs):
	pcrunhook('before', 'open-terminal', command)
	if not command:
		show('open pynotes terminal')
	import queue as _queue
	tw = root.subwin()
	tw.title(title)
	term = tw.textbox(font = (monospace, 12), wrap = 'none')
	term.pack(fill = 'both')
	tw.update()
	tw.sizablefalse()
	pcrunhook('after', 'open-terminal', command)
	_term_default_bg = term.cget('background')
	_term_default_fg = term.cget('foreground')
	_default_fg_rgb = term.winfo_rgb(_term_default_fg)
	_default_bg_rgb = term.winfo_rgb(_term_default_bg)
	def _is_default_colour(colour, default_rgb):
		return colour is None or term.winfo_rgb(colour) == default_rgb
	term.config(insertbackground = _term_default_fg, blockcursor = True)
	running = [True]
	out_q = _queue.Queue(maxsize = 64)
	cursor = ['1.0']
	screen_top = [1]
	_cur_line = [1]
	_saved_cursor = [None]
	_VT_ROWS = 24
	_pending_esc = ['']
	_sgr_state = _sgr_new_state()
	_sgr_tags_done = set()
	_bracketed_paste = [False]
	_focus_reporting = [False]
	_autowrap = [True]
	_app_cursor = [False]
	term.tag_configure('sel', background = _term_default_fg, foreground = _term_default_bg)
	term.tag_configure('wrapcont')
	_sgr_tag_cache = [None]
	def _recompute_sgr_tag():
		fg, bg = _term_sgr_resolve(_sgr_state, _term_default_fg, _term_default_bg)
		if _is_default_colour(fg, _default_fg_rgb) and _is_default_colour(bg, _default_bg_rgb) and not _sgr_state['bold'] and not _sgr_state['italic'] and not _sgr_state['underline']:
			_sgr_tag_cache[0] = None
			return
		name = 'sgr_' + (fg.replace('#', '') if fg else 'x') + '_' + (bg.replace('#', '') if bg else 'x')
		if _sgr_state['bold']:
			name += '_b'
		if _sgr_state['italic']:
			name += '_i'
		if _sgr_state['underline']:
			name += '_u'
		if name not in _sgr_tags_done:
			fnt = (monospace, 12, 'bold') if _sgr_state['bold'] else ((monospace, 12, 'italic') if _sgr_state['italic'] else (monospace, 12))
			term.tag_configure(name, foreground = fg if fg else '', background = bg if bg else '', underline = _sgr_state['underline'], font = fnt)
			term.tag_lower(name, 'sel')
			_sgr_tags_done.add(name)
		_sgr_tag_cache[0] = name
	def _term_insert(index, ch):
		if _sgr_tag_cache[0] is None:
			term.insert(index, ch)
		else:
			term.insert(index, ch, _sgr_tag_cache[0])
	_alt_saved = [None]
	_alt_mode = [False]
	_GRID_ROWS = 24
	_GRID_COLS = 80
	_scroll_top = [1]
	_scroll_bot = [24]
	def _grid_row_runs(r):
		runs = []
		text = ''
		tag = None
		for kind, value, index in term.dump(f'{r}.0', f'{r}.end', text = True, tag = True):
			if kind == 'text':
				text += value
			elif kind == 'tagon':
				if value.startswith('sgr'):
					if text:
						runs.append((text, tag))
						text = ''
					tag = value
			elif kind == 'tagoff':
				if value == tag:
					if text:
						runs.append((text, tag))
						text = ''
					tag = None
		if text:
			runs.append((text, tag))
		return runs
	def _grid_scroll_region(top, bot, up):
		n = bot - top + 1
		rows = [_grid_row_runs(r) for r in range(top, bot + 1)]
		blank = [(' ' * _GRID_COLS, None)]
		if up > 0:
			up = min(up, n)
			rows = rows[up:] + [blank] * up
		elif up < 0:
			down = min(-up, n)
			rows = [blank] * down + rows[:n - down]
		else:
			return
		for idx, r in enumerate(range(top, bot + 1)):
			term.delete(f'{r}.0', f'{r}.end')
			for text, tag in rows[idx]:
				if tag is None:
					term.insert(f'{r}.end', text)
				else:
					term.insert(f'{r}.end', text, tag)
	def _osc_colour_reply(which, colour):
		r, g, b = term.winfo_rgb(colour)
		try:
			_write(f'\x1b]{which};rgb:{r:04x}/{g:04x}/{b:04x}\x1b\\'.encode())
		except Exception:
			pass
	def _osc_parse_colour(spec):
		spec = spec.strip()
		if spec.startswith('rgb:'):
			parts = spec[4:].split('/')
			if len(parts) == 3:
				try:
					return '#' + ''.join(f'{int(p[:2], 16):02x}' if len(p) >= 2 else f'{int(p, 16):02x}' for p in parts)
				except Exception:
					return None
			return None
		try:
			term.winfo_rgb(spec)
			return spec
		except Exception:
			return None
	def _handle_osc(body):
		if body.startswith('52;'):
			parts = body.split(';', 2)
			if len(parts) == 3 and parts[2] not in ('', '?'):
				try:
					text = base64.b64decode(parts[2]).decode('utf-8', errors = 'replace')
				except Exception:
					return
				tw.clipboard_clear()
				tw.clipboard_append(text)
		elif body.startswith('11;?'):
			_osc_colour_reply('11', _term_default_bg)
		elif body.startswith('10;?'):
			_osc_colour_reply('10', _term_default_fg)
		elif body.startswith('12;'):
			_spec = body[3:]
			if _spec == '?':
				_osc_colour_reply('12', term.cget('insertbackground'))
			else:
				_col = _osc_parse_colour(_spec)
				if _col:
					try:
						term.config(insertbackground = _col)
					except Exception:
						pass
		elif body == '112' or body.startswith('112;'):
			try:
				term.config(insertbackground = _term_default_fg)
			except Exception:
				pass
	def _enter_alt_screen():
		if _alt_saved[0] is not None:
			return
		_alt_saved[0] = (term.dump('1.0', 'end', text = True, tag = True), screen_top[0], cursor[0], dict(_sgr_state), _cur_line[0])
		_alt_mode[0] = True
		_cur_line[0] = 1
		_scroll_top[0] = 1
		_scroll_bot[0] = _GRID_ROWS
		term.delete('1.0', 'end')
		term.insert('1.0', '\n'.join([' ' * _GRID_COLS] * _GRID_ROWS))
		screen_top[0] = 1
		term.mark_set('insert', '1.0')
		cursor[0] = '1.0'
		_sgr_apply(_sgr_state, [0])
		_recompute_sgr_tag()
	def _leave_alt_screen():
		if _alt_saved[0] is None:
			return
		dump, saved_top, saved_cursor, saved_sgr, saved_curline = _alt_saved[0]
		_alt_saved[0] = None
		_alt_mode[0] = False
		term.delete('1.0', 'end')
		_open_tags = []
		for kind, value, index in dump:
			if kind == 'text':
				term.insert('end', value, tuple(_open_tags))
			elif kind == 'tagon':
				if value not in _open_tags:
					_open_tags.append(value)
			elif kind == 'tagoff':
				if value in _open_tags:
					_open_tags.remove(value)
		screen_top[0] = saved_top
		_sgr_state.update(saved_sgr)
		_recompute_sgr_tag()
		_cur_line[0] = saved_curline
		term.mark_set('insert', saved_cursor)
		cursor[0] = saved_cursor
		term.config(insertwidth = 2)
	def _grid_goto(row, gcol):
		row = min(max(1, row), _GRID_ROWS)
		gcol = min(max(0, gcol), _GRID_COLS)
		term.mark_set('insert', f'{row}.{gcol}')
	def _grid_put(ch):
		row = int(term.index('insert').split('.')[0])
		gcol = int(term.index('insert').split('.')[1])
		if gcol >= _GRID_COLS:
			if row < _GRID_ROWS:
				row += 1
				gcol = 0
				term.mark_set('insert', f'{row}.0')
			else:
				gcol = _GRID_COLS - 1
				term.mark_set('insert', f'{row}.{gcol}')
		term.delete(f'{row}.{gcol}', f'{row}.{gcol + 1}')
		_term_insert(f'{row}.{gcol}', ch)
		term.mark_set('insert', f'{row}.{gcol + 1}')
	if platform.system() == 'Linux':
		import pty
		import select as _select
		import fcntl
		import termios
		import struct
		master_fd, slave_fd = pty.openpty()
		fcntl.ioctl(master_fd, termios.TIOCSWINSZ, struct.pack('HHHH', 24, 80, 0, 0))
		shell = None if command else os.environ.get('SHELL', '/bin/bash')
		env = os.environ.copy()
		env['TERM'] = 'xterm-256color'
		env['COLORTERM'] = 'truecolor'
		_bg_r, _bg_g, _bg_b = term.winfo_rgb(_term_default_bg)
		_fg_r, _fg_g, _fg_b = term.winfo_rgb(_term_default_fg)
		_bg_is_light = (0.299 * _bg_r + 0.587 * _bg_g + 0.114 * _bg_b) / 256 >= 128
		_fg_is_light = (0.299 * _fg_r + 0.587 * _fg_g + 0.114 * _fg_b) / 256 >= 128
		env['COLORFGBG'] = f'{15 if _fg_is_light else 0};{15 if _bg_is_light else 0}'
		def _term_preexec():
			os.setsid()
			fcntl.ioctl(0, termios.TIOCSCTTY, 0)
		proc = subprocess.Popen(command if command else [shell], stdin = slave_fd, stdout = slave_fd, stderr = slave_fd, close_fds = True, preexec_fn = _term_preexec, env = env, **kwargs)
		os.close(slave_fd)
		def _read():
			_dec = codecs.getincrementaldecoder('utf-8')(errors = 'replace')
			while running[0]:
				try:
					r, _, _ = _select.select([master_fd], [], [], 0.05)
					if r:
						data = os.read(master_fd, 4096)
						if not data:
							break
						out_q.put(_dec.decode(data))
					elif proc.poll() is not None:
						break
				except Exception:
					break
			running[0] = False
			out_q.put(None)
		def _write(data):
			os.write(master_fd, data)
		def _close():
			running[0] = False
			try:
				while True:
					out_q.get_nowait()
			except Exception:
				pass
			try:
				proc.terminate()
			except Exception:
				pass
			try:
				os.close(master_fd)
			except Exception:
				pass
			if _poll_after_id[0] is not None:
				try:
					term.after_cancel(_poll_after_id[0])
				except Exception:
					pass
				_poll_after_id[0] = None
			try:
				tw.destroy()
			except Exception:
				pass
			try:
				_open_terminal_closers.remove(_close)
			except Exception:
				pass
	else:
		proc = PtyProcess.spawn(command if command else 'powershell.exe', dimensions = (24, 80), **kwargs)
		def _read():
			_dec = codecs.getincrementaldecoder('utf-8')(errors = 'replace')
			while running[0]:
				try:
					data = proc.read(4096)
					if data:
						out_q.put(data if isinstance(data, str) else _dec.decode(data))
				except Exception:
					break
			running[0] = False
			out_q.put(None)
		def _write(data):
			try:
				proc.write(data.decode('utf-8', errors = 'replace'))
			except Exception:
				pass
		def _close():
			running[0] = False
			try:
				proc.close()
			except Exception:
				pass
			if _poll_after_id[0] is not None:
				try:
					term.after_cancel(_poll_after_id[0])
				except Exception:
					pass
				_poll_after_id[0] = None
			try:
				tw.destroy()
			except Exception:
				pass
			try:
				_open_terminal_closers.remove(_close)
			except Exception:
				pass
	_open_terminal_closers.append(_close)
	def _vt_sync():
		last = int(term.index('end').split('.')[0]) - 1
		if _cur_line[0] > last:
			term.insert('end', '\n' * (_cur_line[0] - last))
	def _term_goto(_gl, _gc):
		_ll = int(term.index(f'{_gl}.end').split('.')[1])
		if _gc > _ll:
			term.insert(f'{_gl}.end', ' ' * (_gc - _ll))
		term.mark_set('insert', f'{_gl}.{_gc}')
	def _primary_scroll_up():
		if _scroll_top[0] == 1:
			screen_top[0] += 1
			_ins = screen_top[0] + _scroll_bot[0] - 1
			term.insert(f'{_ins}.0', '\n')
		else:
			_lt = screen_top[0] + _scroll_top[0] - 1
			_lb = screen_top[0] + _scroll_bot[0] - 1
			term.delete(f'{_lt}.0', f'{_lt + 1}.0')
			term.insert(f'{_lb}.0', '\n')
	def _primary_scroll_down():
		_lt = screen_top[0] + _scroll_top[0] - 1
		_lb = screen_top[0] + _scroll_bot[0] - 1
		term.insert(f'{_lt}.0', '\n')
		term.delete(f'{_lb + 1}.0', f'{_lb + 2}.0')
	def _on_modified(e = None):
		if term.edit_modified():
			term.edit_modified(False)
	def _process(text):
		if _pending_esc[0]:
			text = _pending_esc[0] + text
			_pending_esc[0] = ''
		term.mark_set('insert', cursor[0])
		i = 0
		n = len(text)
		while i < n:
			ch = text[i]
			if ch == '\r':
				if _alt_mode[0]:
					ln = int(term.index('insert').split('.')[0])
					term.mark_set('insert', f'{ln}.0')
				else:
					term.mark_set('insert', f'{_cur_line[0]}.0')
				i += 1
			elif ch == '\x08':
				c = int(term.index('insert').split('.')[1])
				if c > 0:
					ln = int(term.index('insert').split('.')[0])
					term.mark_set('insert', f'{ln}.{c - 1}')
				i += 1
			elif ch == '\n':
				if _alt_mode[0]:
					ln = int(term.index('insert').split('.')[0])
					gcol = int(term.index('insert').split('.')[1])
					if ln >= _scroll_bot[0]:
						_grid_scroll_region(_scroll_top[0], _scroll_bot[0], 1)
						_grid_goto(_scroll_bot[0], gcol)
					else:
						_grid_goto(ln + 1, gcol)
					i += 1
					continue
				c = int(term.index('insert').split('.')[1])
				_srow = _cur_line[0] - screen_top[0] + 1
				if (_scroll_top[0] > 1 or _scroll_bot[0] < _VT_ROWS) and _srow == _scroll_bot[0]:
					_primary_scroll_up()
					_cur_line[0] = screen_top[0] + _scroll_bot[0] - 1
					term.tag_remove('wrapcont', f'{_cur_line[0]}.0', f'{_cur_line[0]}.end')
					term.mark_set('insert', f'{_cur_line[0]}.{c}')
					i += 1
					continue
				_cur_line[0] += 1
				if _cur_line[0] > screen_top[0] + _VT_ROWS - 1:
					screen_top[0] = _cur_line[0] - (_VT_ROWS - 1)
				_vt_sync()
				term.tag_remove('wrapcont', f'{_cur_line[0]}.0', f'{_cur_line[0]}.end')
				_term_goto(_cur_line[0], c)
				i += 1
			elif ch == '\x1b':
				rest = text[i:]
				if len(rest) < 2:
					_pending_esc[0] = rest
					break
				nxt = rest[1]
				if nxt == '[':
					m = re.match(r'\x1b\[([0-9;?<=>]*[ -/]*)([@-~])', rest)
					if not m and re.fullmatch(r'\x1b\[[0-9;?<=>]*[ -/]*', rest):
						_pending_esc[0] = rest
						break
					if m:
						_prefix = m.group(1)
						_private = _prefix.startswith('?')
						ps = ''.join(c for c in _prefix if c in '0123456789;')
						cmd = m.group(2) if all(c in '0123456789;?' for c in _prefix) else ''
						p = [int(x) if x else 0 for x in ps.split(';')] if ps else [0]
						ln = term.index('insert').split('.')[0]
						col = term.index('insert').split('.')[1]
						if cmd == 'K':
							if _alt_mode[0]:
								gcol = int(col)
								if p[0] == 0:
									term.delete(f'{ln}.{gcol}', f'{ln}.end')
									_term_insert(f'{ln}.{gcol}', ' ' * (_GRID_COLS - gcol))
								elif p[0] == 1:
									term.delete(f'{ln}.0', f'{ln}.{gcol}')
									_term_insert(f'{ln}.0', ' ' * gcol)
								else:
									term.delete(f'{ln}.0', f'{ln}.end')
									_term_insert(f'{ln}.0', ' ' * _GRID_COLS)
								term.mark_set('insert', f'{ln}.{gcol}')
							else:
								if p[0] == 0:
									term.delete('insert', f'{ln}.end')
								elif p[0] == 1:
									term.delete(f'{ln}.0', f'{ln}.{int(col) + 1}')
									term.insert(f'{ln}.0', ' ' * (int(col) + 1))
									term.mark_set('insert', f'{ln}.{col}')
								else:
									term.delete(f'{ln}.0', f'{ln}.end')
									_term_goto(int(ln), int(col))
						elif cmd == 'J':
							if _alt_mode[0]:
								gcol = int(col)
								if p[0] == 0:
									term.delete(f'{ln}.{gcol}', f'{ln}.end')
									_term_insert(f'{ln}.{gcol}', ' ' * (_GRID_COLS - gcol))
									if int(ln) < _GRID_ROWS:
										term.delete(f'{int(ln) + 1}.0', 'end')
										for _er in range(_GRID_ROWS - int(ln)):
											term.insert('end', '\n')
											_term_insert('end', ' ' * _GRID_COLS)
								else:
									term.delete('1.0', 'end')
									for _er in range(_GRID_ROWS):
										if _er:
											term.insert('end', '\n')
										_term_insert('end', ' ' * _GRID_COLS)
								term.mark_set('insert', f'{ln}.{gcol}')
							elif p[0] == 2:
								cur_col = int(col)
								cur_off = _cur_line[0] - screen_top[0]
								old_last = int(term.index('end').split('.')[0]) - 1
								term.insert('end', '\n' * _VT_ROWS)
								screen_top[0] = old_last + 1
								_cur_line[0] = screen_top[0] + cur_off
								ll = int(term.index(f'{_cur_line[0]}.end').split('.')[1])
								if cur_col > ll:
									term.insert(f'{_cur_line[0]}.end', ' ' * (cur_col - ll))
								term.mark_set('insert', f'{_cur_line[0]}.{cur_col}')
							elif p[0] == 3:
								if screen_top[0] > 1:
									del_n = screen_top[0] - 1
									term.delete('1.0', f'{screen_top[0]}.0')
									_cur_line[0] = max(1, _cur_line[0] - del_n)
									screen_top[0] = 1
									term.mark_set('insert', f'{_cur_line[0]}.{col}')
							elif p[0] == 1:
								_il = int(ln)
								_ic = int(col)
								for _er in range(screen_top[0], _il):
									term.delete(f'{_er}.0', f'{_er}.end')
								term.delete(f'{_il}.0', f'{_il}.{_ic + 1}')
								term.insert(f'{_il}.0', ' ' * (_ic + 1))
								term.mark_set('insert', f'{_il}.{_ic}')
							elif p[0] == 0:
								if term.compare('insert', '<', 'end-1c'):
									term.delete('insert', 'end-1c')
						elif cmd in ('H', 'f'):
							row_ = p[0] if p[0] else 1
							col_ = p[1] if len(p) > 1 and p[1] else 1
							if _alt_mode[0]:
								_grid_goto(row_, col_ - 1)
							else:
								_cur_line[0] = screen_top[0] + min(row_, _VT_ROWS) - 1
								_vt_sync()
								ll = int(term.index(f'{_cur_line[0]}.end').split('.')[1])
								if col_ - 1 > ll:
									term.insert(f'{_cur_line[0]}.end', ' ' * (col_ - 1 - ll))
								term.mark_set('insert', f'{_cur_line[0]}.{col_ - 1}')
						elif cmd == 'A':
							mv = p[0] or 1
							if _alt_mode[0]:
								_grid_goto(int(ln) - mv, int(col))
							else:
								_cur_line[0] = max(screen_top[0], int(ln) - mv)
								_term_goto(_cur_line[0], int(col))
						elif cmd == 'B':
							mv = p[0] or 1
							if _alt_mode[0]:
								_grid_goto(int(ln) + mv, int(col))
							else:
								_cur_line[0] = min(int(ln) + mv, screen_top[0] + _VT_ROWS - 1)
								_vt_sync()
								_term_goto(_cur_line[0], int(col))
						elif cmd == 'C':
							mv = p[0] or 1
							_tc = int(col) + mv
							if not _alt_mode[0]:
								ll = int(term.index(f'{ln}.end').split('.')[1])
								if _tc > ll:
									term.insert(f'{ln}.end', ' ' * (_tc - ll))
							term.mark_set('insert', f'{ln}.{_tc}')
						elif cmd == 'D':
							mv = p[0] or 1
							_term_goto(int(ln), max(0, int(col) - mv))
						elif cmd == 'E':
							mv = p[0] or 1
							if _alt_mode[0]:
								_grid_goto(int(ln) + mv, 0)
							else:
								_cur_line[0] = int(ln) + mv
								_vt_sync()
								term.mark_set('insert', f'{_cur_line[0]}.0')
						elif cmd == 'F':
							mv = p[0] or 1
							if _alt_mode[0]:
								_grid_goto(int(ln) - mv, 0)
							else:
								_cur_line[0] = max(screen_top[0], int(ln) - mv)
								term.mark_set('insert', f'{_cur_line[0]}.0')
						elif cmd == 's' and not _private:
							if _alt_mode[0]:
								_saved_cursor[0] = term.index('insert')
							else:
								_saved_cursor[0] = (_cur_line[0], int(col))
						elif cmd == 'u' and not _private:
							if _saved_cursor[0] is not None:
								if _alt_mode[0]:
									term.mark_set('insert', _saved_cursor[0])
								else:
									_cur_line[0], _sc = _saved_cursor[0]
									_vt_sync()
									term.mark_set('insert', f'{_cur_line[0]}.{_sc}')
						elif cmd == 'G':
							mv = p[0] or 1
							if _alt_mode[0]:
								_grid_goto(int(ln), mv - 1)
							else:
								ll = int(term.index(f'{_cur_line[0]}.end').split('.')[1])
								if mv - 1 > ll:
									term.insert(f'{_cur_line[0]}.end', ' ' * (mv - 1 - ll))
								term.mark_set('insert', f'{_cur_line[0]}.{mv - 1}')
						elif cmd == 'd':
							mv = p[0] or 1
							if _alt_mode[0]:
								_grid_goto(mv, int(col))
							else:
								_cur_line[0] = screen_top[0] + min(mv, _VT_ROWS) - 1
								_vt_sync()
								_term_goto(_cur_line[0], int(col))
						elif cmd == 'P':
							mv = p[0] or 1
							_pend = f'insert+{mv}c'
							if term.compare(_pend, '>', f'{ln}.end'):
								_pend = f'{ln}.end'
							term.delete('insert', _pend)
						elif cmd == '@':
							mv = p[0] or 1
							term.insert('insert', ' ' * mv)
							term.mark_set('insert', f'insert-{mv}c')
						elif cmd == 'L':
							if _alt_mode[0]:
								r0 = int(ln)
								if _scroll_top[0] <= r0 <= _scroll_bot[0]:
									_grid_scroll_region(r0, _scroll_bot[0], -(p[0] or 1))
									term.mark_set('insert', f'{r0}.0')
						elif cmd == 'M':
							if _alt_mode[0]:
								r0 = int(ln)
								if _scroll_top[0] <= r0 <= _scroll_bot[0]:
									_grid_scroll_region(r0, _scroll_bot[0], (p[0] or 1))
									term.mark_set('insert', f'{r0}.0')
						elif cmd == 'S':
							if _alt_mode[0]:
								_grid_scroll_region(_scroll_top[0], _scroll_bot[0], (p[0] or 1))
						elif cmd == 'T':
							if _alt_mode[0]:
								_grid_scroll_region(_scroll_top[0], _scroll_bot[0], -(p[0] or 1))
						elif cmd == 'r':
							if len(p) >= 2:
								_scroll_top[0] = min(max(1, p[0] or 1), _GRID_ROWS)
								_scroll_bot[0] = min(max(_scroll_top[0], p[1] or _GRID_ROWS), _GRID_ROWS)
							else:
								_scroll_top[0] = 1
								_scroll_bot[0] = _GRID_ROWS
						elif cmd == 'X':
							mv = p[0] or 1
							if _alt_mode[0]:
								gcol = int(col)
								endc = min(gcol + mv, _GRID_COLS)
								term.delete(f'{ln}.{gcol}', f'{ln}.{endc}')
								_term_insert(f'{ln}.{gcol}', ' ' * (endc - gcol))
								term.mark_set('insert', f'{ln}.{gcol}')
							else:
								_x0 = int(col)
								_xll = int(term.index(f'{ln}.end').split('.')[1])
								term.delete(f'{ln}.{_x0}', f'{ln}.{min(_x0 + mv, _xll)}')
								term.insert(f'{ln}.{_x0}', ' ' * mv)
								term.mark_set('insert', f'{ln}.{_x0}')
						elif cmd == 'n':
							if p[0] == 6:
								cur_col = int(term.index('insert').split('.')[1])
								row_rep = max(1, _cur_line[0] - screen_top[0] + 1)
								try:
									_write(f'\x1b[{row_rep};{cur_col + 1}R'.encode())
								except Exception:
									pass
						elif cmd == 'm':
							_sgr_apply(_sgr_state, p)
							_recompute_sgr_tag()
						elif cmd == 'h' and _private:
							if p[0] in (1049, 1047, 47):
								_enter_alt_screen()
							elif p[0] == 25:
								term.config(insertwidth = 2)
							elif p[0] == 12:
								term.config(insertofftime = 300, insertontime = 600)
							elif p[0] == 2004:
								_bracketed_paste[0] = True
							elif p[0] == 1004:
								_focus_reporting[0] = True
							elif p[0] == 7:
								_autowrap[0] = True
							elif p[0] == 1:
								_app_cursor[0] = True
						elif cmd == 'l' and _private:
							if p[0] in (1049, 1047, 47):
								_leave_alt_screen()
							elif p[0] == 25:
								term.config(insertwidth = 0)
							elif p[0] == 12:
								term.config(insertofftime = 0)
							elif p[0] == 2004:
								_bracketed_paste[0] = False
							elif p[0] == 1004:
								_focus_reporting[0] = False
							elif p[0] == 7:
								_autowrap[0] = False
							elif p[0] == 1:
								_app_cursor[0] = False
						i += len(m.group(0))
					else:
						i += 2
				elif nxt == ']':
					end_osc = rest.find('\x07', 2)
					if end_osc >= 0:
						_handle_osc(rest[2:end_osc])
						i += end_osc + 1
					else:
						st = rest.find('\x1b\\', 2)
						if st >= 0:
							_handle_osc(rest[2:st])
							i += st + 2
						elif len(rest) < _PTY_MAX_PENDING_ESC:
							_pending_esc[0] = rest
							break
						else:
							i += len(rest)
				elif nxt == 'M':
					if _alt_mode[0]:
						cl = int(term.index('insert').split('.')[0])
						co = term.index('insert').split('.')[1]
						term.mark_set('insert', f'{max(1, cl - 1)}.{co}')
					else:
						co = int(term.index('insert').split('.')[1])
						_srow = _cur_line[0] - screen_top[0] + 1
						if (_scroll_top[0] > 1 or _scroll_bot[0] < _VT_ROWS) and _srow == _scroll_top[0]:
							_primary_scroll_down()
							_cur_line[0] = screen_top[0] + _scroll_top[0] - 1
							term.mark_set('insert', f'{_cur_line[0]}.{co}')
							i += 2
							continue
						if _srow <= 1 and _scroll_top[0] == 1 and _scroll_bot[0] == _VT_ROWS:
							term.insert(f'{screen_top[0]}.0', '\n')
							_cur_line[0] = screen_top[0]
							_term_goto(_cur_line[0], co)
						else:
							_cur_line[0] = max(screen_top[0], _cur_line[0] - 1)
							_term_goto(_cur_line[0], co)
					i += 2
				elif nxt == 'D':
					if _alt_mode[0]:
						cl = int(term.index('insert').split('.')[0])
						co = term.index('insert').split('.')[1]
						last_line = int(term.index('end').split('.')[0]) - 1
						if cl + 1 > last_line:
							term.insert('end', '\n')
						term.mark_set('insert', f'{cl + 1}.{co}')
					else:
						co = int(term.index('insert').split('.')[1])
						_srow = _cur_line[0] - screen_top[0] + 1
						if (_scroll_top[0] > 1 or _scroll_bot[0] < _VT_ROWS) and _srow == _scroll_bot[0]:
							_primary_scroll_up()
							_cur_line[0] = screen_top[0] + _scroll_bot[0] - 1
							term.mark_set('insert', f'{_cur_line[0]}.{co}')
							i += 2
							continue
						_cur_line[0] += 1
						if _cur_line[0] > screen_top[0] + _VT_ROWS - 1:
							screen_top[0] = _cur_line[0] - (_VT_ROWS - 1)
						_vt_sync()
						_term_goto(_cur_line[0], co)
					i += 2
				elif nxt in '()*+#':
					if len(rest) < 3:
						_pending_esc[0] = rest
						break
					i += 3
				elif nxt == 'c':
					_alt_saved[0] = None
					_alt_mode[0] = False
					term.delete('1.0', 'end')
					_cur_line[0] = 1
					screen_top[0] = 1
					_scroll_top[0] = 1
					_scroll_bot[0] = _GRID_ROWS
					_autowrap[0] = True
					_app_cursor[0] = False
					_saved_cursor[0] = None
					_sgr_apply(_sgr_state, [0])
					_recompute_sgr_tag()
					term.mark_set('insert', '1.0')
					cursor[0] = '1.0'
					term.config(insertwidth = 2)
					i += 2
				elif nxt == '7':
					if _alt_mode[0]:
						_saved_cursor[0] = term.index('insert')
					else:
						_saved_cursor[0] = (_cur_line[0], int(term.index('insert').split('.')[1]))
					i += 2
				elif nxt == '8':
					if _saved_cursor[0] is not None:
						if _alt_mode[0]:
							term.mark_set('insert', _saved_cursor[0])
						else:
							_cur_line[0], _sc = _saved_cursor[0]
							_vt_sync()
							term.mark_set('insert', f'{_cur_line[0]}.{_sc}')
					i += 2
				elif nxt == '\x1b':
					i += 1
				else:
					i += 2
			elif ch == '\t':
				if _alt_mode[0]:
					ln = int(term.index('insert').split('.')[0])
					col = int(term.index('insert').split('.')[1])
					target = min(col + (8 - (col % 8)), _GRID_COLS - 1)
					_grid_goto(ln, target)
					i += 1
					continue
				col = int(term.index('insert').split('.')[1])
				sp = 8 - (col % 8)
				line_len = int(term.index(f'{_cur_line[0]}.end').split('.')[1])
				if col > line_len:
					term.insert(f'{_cur_line[0]}.end', ' ' * (col - line_len))
					line_len = col
				ovw = min(sp, line_len - col)
				if ovw > 0:
					term.delete(f'{_cur_line[0]}.{col}', f'{_cur_line[0]}.{col + ovw}')
				if _sgr_tag_cache[0] is None:
					term.insert(f'{_cur_line[0]}.{col}', ' ' * sp)
				else:
					term.insert(f'{_cur_line[0]}.{col}', ' ' * sp, _sgr_tag_cache[0])
				term.mark_set('insert', f'{_cur_line[0]}.{col + sp}')
				i += 1
			elif ch >= ' ' and ch != '\x7f':
				if _alt_mode[0]:
					_grid_put(ch)
					i += 1
					continue
				j = i
				while j < n and text[j] >= ' ' and text[j] != '\x7f':
					j += 1
				run = text[i:j]
				i = j
				col = int(term.index('insert').split('.')[1])
				if not _autowrap[0]:
					if col >= _GRID_COLS:
						col = _GRID_COLS - 1
					space = _GRID_COLS - col
					if len(run) <= space:
						chunk = run
					else:
						chunk = run[:space - 1] + run[-1]
					line_len = int(term.index(f'{_cur_line[0]}.end').split('.')[1])
					if col > line_len:
						term.insert(f'{_cur_line[0]}.end', ' ' * (col - line_len))
						line_len = col
					ovw = min(len(chunk), line_len - col)
					if ovw > 0:
						term.delete(f'{_cur_line[0]}.{col}', f'{_cur_line[0]}.{col + ovw}')
					if _sgr_tag_cache[0] is None:
						term.insert(f'{_cur_line[0]}.{col}', chunk)
					else:
						term.insert(f'{_cur_line[0]}.{col}', chunk, _sgr_tag_cache[0])
					col += len(chunk)
					term.mark_set('insert', f'{_cur_line[0]}.{col}')
					continue
				while run:
					wrapped = False
					space = _GRID_COLS - col
					if space <= 0:
						_cur_line[0] += 1
						if _cur_line[0] > screen_top[0] + _VT_ROWS - 1:
							screen_top[0] = _cur_line[0] - (_VT_ROWS - 1)
						_vt_sync()
						col = 0
						wrapped = True
						space = _GRID_COLS
					chunk = run[:space]
					run = run[space:]
					line_len = int(term.index(f'{_cur_line[0]}.end').split('.')[1])
					if col > line_len:
						term.insert(f'{_cur_line[0]}.end', ' ' * (col - line_len))
						line_len = col
					ovw = min(len(chunk), line_len - col)
					if ovw > 0:
						term.delete(f'{_cur_line[0]}.{col}', f'{_cur_line[0]}.{col + ovw}')
					if _sgr_tag_cache[0] is None:
						term.insert(f'{_cur_line[0]}.{col}', chunk)
					else:
						term.insert(f'{_cur_line[0]}.{col}', chunk, _sgr_tag_cache[0])
					if wrapped:
						term.tag_add('wrapcont', f'{_cur_line[0]}.0', f'{_cur_line[0]}.1')
					col += len(chunk)
					term.mark_set('insert', f'{_cur_line[0]}.{col}')
			else:
				i += 1
		cursor[0] = term.index('insert')
	_polling = [False]
	_poll_after_id = [None]
	def _poll():
		if _polling[0]:
			return
		_polling[0] = True
		try:
			term.update()
			closed = False
			backlog = False
			_at_bottom = term.yview()[1] >= 0.999
			_had = False
			deadline = time.monotonic() + _TERM_FRAME_BUDGET
			try:
				while True:
					text = out_q.get_nowait()
					if text is None:
						closed = True
						break
					_process(text)
					_had = True
					if time.monotonic() > deadline:
						backlog = True
						break
			except Exception:
				pass
			if _had and _at_bottom:
				term.see('end')
				term.see('insert')
			if closed:
				if endmessage:
					term.insert('end', '\n\n' + endmessage)
					term.see('end')
					term.unbind('<Key>')
					term.bind('<Key>', lambda e: _close())
				else:
					tw.destroy()
				_polling[0] = False
				return
			_poll_after_id[0] = term.after(_TERM_FRAME_MS if backlog else 50, _poll)
		except Exception:
			try:
				if tw.winfo_exists():
					_poll_after_id[0] = term.after(_TERM_FRAME_MS, _poll)
			except Exception:
				pass
		_polling[0] = False
	_term_csi_keys = {'Up': 'A', 'Down': 'B', 'Right': 'C', 'Left': 'D', 'Home': 'H', 'End': 'F'}
	_term_tilde_keys = {'Insert': '2', 'Delete': '3', 'Prior': '5', 'Next': '6', 'F5': '15', 'F6': '17', 'F7': '18', 'F8': '19', 'F9': '20', 'F10': '21', 'F11': '23', 'F12': '24'}
	_term_ss3_keys = {'F1': 'P', 'F2': 'Q', 'F3': 'R', 'F4': 'S'}
	def _key(event):
		_unpost_menu()
		if not running[0]:
			return 'break'
		sym = event.keysym
		ch = event.char
		if ch or sym in ('Return', 'BackSpace', 'Delete', 'Up', 'Down', 'Left', 'Right', 'Tab', 'ISO_Left_Tab', 'Home', 'End', 'Prior', 'Next', 'Insert'):
			_clear_selection()
		_kmod = 1 + (1 if event.state & 1 else 0) + (4 if event.state & 4 else 0)
		try:
			if sym == 'Return':
				_write(b'\r')
			elif sym == 'BackSpace':
				_write(b'\x7f')
			elif sym == 'ISO_Left_Tab' or (sym == 'Tab' and (event.state & 1)):
				_write(b'\x1b[Z')
			elif sym == 'Tab':
				_write(b'\t')
			elif sym in _term_csi_keys:
				_kl = _term_csi_keys[sym]
				if _kmod > 1:
					_write(f'\x1b[1;{_kmod}{_kl}'.encode())
				elif _app_cursor[0]:
					_write(('\x1bO' + _kl).encode())
				else:
					_write(('\x1b[' + _kl).encode())
			elif sym in _term_tilde_keys:
				_kn = _term_tilde_keys[sym]
				if _kmod > 1:
					_write(f'\x1b[{_kn};{_kmod}~'.encode())
				else:
					_write(f'\x1b[{_kn}~'.encode())
			elif sym in _term_ss3_keys:
				_kl = _term_ss3_keys[sym]
				if _kmod > 1:
					_write(f'\x1b[1;{_kmod}{_kl}'.encode())
				else:
					_write(('\x1bO' + _kl).encode())
			elif (event.state & 4) and sym in ('space', 'at', '2'):
				_write(b'\x00')
			elif (event.state & 4) and sym in ('bracketleft', '3'):
				_write(b'\x1b')
			elif (event.state & 4) and sym in ('backslash', '4'):
				_write(b'\x1c')
			elif (event.state & 4) and sym in ('bracketright', '5'):
				_write(b'\x1d')
			elif (event.state & 4) and sym in ('asciicircum', '6'):
				_write(b'\x1e')
			elif (event.state & 4) and sym in ('underscore', 'slash', '7'):
				_write(b'\x1f')
			elif ch:
				_write(ch.encode('utf-8'))
		except Exception:
			pass
		return 'break'
	def _meta_key(event):
		_unpost_menu()
		if not running[0]:
			return 'break'
		_clear_selection()
		sym = event.keysym
		ch = event.char
		try:
			if ch:
				_write(b'\x1b' + ch.encode('utf-8'))
			elif sym in ('Left', 'Right', 'Up', 'Down'):
				_pfx = b'\x1bO' if _app_cursor[0] else b'\x1b['
				_write(b'\x1b' + {'Left': b'b', 'Right': b'f', 'Up': _pfx + b'A', 'Down': _pfx + b'B'}[sym])
		except Exception:
			pass
		return 'break'
	def _clear_selection():
		try:
			term.tag_remove('sel', '1.0', 'end')
		except Exception:
			pass
	def _copy_selection(e = None):
		try:
			first = term.index('sel.first')
			last = term.index('sel.last')
		except Exception:
			return 'break'
		start_line = int(first.split('.')[0])
		end_line = int(last.split('.')[0])
		parts = []
		for ln in range(start_line, end_line + 1):
			a = first if ln == start_line else f'{ln}.0'
			b = last if ln == end_line else f'{ln}.end'
			seg = term.get(a, b)
			if parts and 'wrapcont' in term.tag_names(f'{ln}.0'):
				parts[-1] += seg
			else:
				parts.append(seg)
		sel = '\n'.join(parts)
		if sel:
			tw.clipboard_clear()
			tw.clipboard_append(sel)
		return 'break'
	def _paste_clipboard(e = None):
		if not running[0]:
			return 'break'
		try:
			data = tw.clipboard_get()
		except Exception:
			return 'break'
		if data:
			data = data.replace('\r\n', '\r').replace('\n', '\r')
			payload = data.encode('utf-8')
			if _bracketed_paste[0]:
				payload = b'\x1b[200~' + payload + b'\x1b[201~'
			try:
				_write(payload)
				_clear_selection()
			except Exception:
				pass
		return 'break'
	def _select_all(e = None):
		term.tag_add('sel', '1.0', 'end-1c')
		return 'break'
	_termmenu = tw.menu(tearoff = 0)
	_termmenu.add_command(label = 'Copy', command = _copy_selection)
	_termmenu.add_command(label = 'Paste', command = _paste_clipboard)
	_termmenu.add_separator()
	_termmenu.add_command(label = 'Select All', command = _select_all)
	_menu_posted = [False]
	def _unpost_menu():
		if _menu_posted[0]:
			_menu_posted[0] = False
			try:
				_termmenu.unpost()
			except Exception:
				pass
	def _termmenu_keyclose(e):
		if e.keysym not in ('Up', 'Down', 'Left', 'Right', 'Return', 'space', 'Shift_L', 'Shift_R', 'Control_L', 'Control_R', 'Alt_L', 'Alt_R'):
			_unpost_menu()
			return 'break'
	_termmenu.bind('<KeyPress>', _termmenu_keyclose)
	_termmenu.bind('<Unmap>', lambda e: _menu_posted.__setitem__(0, False))
	def _popup(e):
		term.focus_set()
		_menu_posted[0] = True
		try:
			_termmenu.tk_popup(e.x_root, e.y_root)
		finally:
			_termmenu.grab_release()
		return 'break'
	term.unbind('<Control-a>')
	def _snap_caret(e = None):
		def _do():
			try:
				term.mark_set('insert', cursor[0])
			except Exception:
				pass
		try:
			term.after_idle(_do)
		except Exception:
			pass
	term.bind('<Key>', _key)
	term.bind('<ISO_Left_Tab>', _key)
	term.bind('<Control-Key>', _key)
	term.bind('<Meta-Key>', _meta_key)
	term.bind('<Alt-Key>', _meta_key)
	term.bind('<Control-x>', _key)
	term.bind('<Control-w>', _key)
	term.bind('<Control-c>', _key)
	term.bind('<Control-v>', _key)
	term.bind('<Control-y>', _key)
	term.bind('<Meta-w>', _meta_key)
	def _focus_in(e):
		if _focus_reporting[0] and running[0]:
			try:
				_write(b'\x1b[I')
			except Exception:
				pass
	def _focus_out(e):
		if _focus_reporting[0] and running[0]:
			try:
				_write(b'\x1b[O')
			except Exception:
				pass
	term.bind('<FocusIn>', _focus_in)
	term.bind('<FocusOut>', _focus_out)
	term.bind('<Button-1>', lambda e: _unpost_menu())
	term.bind('<ButtonRelease-1>', _snap_caret)
	term.bind('<ButtonRelease-3>', _popup)
	term.bind('<Button-2>', _paste_clipboard)
	term.bind('<<PasteSelection>>', lambda e: 'break')
	term.bind('<<Clear>>', lambda e: 'break')
	term.bind('<Control-Shift-C>', _copy_selection)
	term.edit_modified(False)
	term.bind('<<Modified>>', _on_modified)
	term.bind('<Control-Shift-V>', _paste_clipboard)
	tw.protocol('WM_DELETE_WINDOW', _close)
	threading.Thread(target = _read, daemon = True).start()
	term.after(50, _poll)
	term.focus()
	tw.deiconify()
	if blocking == True:
		while tw.winfo_exists():
			tw.update()
def hx():
	show('open alt-x commands help')
	hxw = root.subwin()
	hxw.title('Help with commands')
	hxs = hxw.scroll()
	hxs.pack(side = 'right', fill = 'y', padx = 10, pady = 10)
	hxh = hxw.textbox(wrap = 'word', yscrollcommand = hxs.set)
	hxs.config(command = hxh.yview)
	l1 = hxh.index('end-1c')
	hxh.insert('end', 'General\n\n')
	r1 = hxh.index('end-1c')
	hxh.tag_add('bigstuff', l1, r1)
	hxh.insert('end', 'Pressing Alt-X will open a box where you can type commands to do things in PyNotes.\nMany commands have many different aliases; for example, \'sh\', \'splithoriz\', and \'split-editor-horizontal\' all split the currently open editor horizontally.\n\':\' separates commands from their input.\nTo nest commands, use brackets like cmd1:(cmd2:(...)).\nExample: re:(hmode:py;switch)*3.')
	l2 = hxh.index('end-1c')
	hxh.insert('end', '\n\nPyNotes\' Commands\n\n')
	r2 = hxh.index('end-1c')
	hxh.tag_add('bigstuff', l2, r2)
	hxh.insert('end', ("'editor' or 'ed': Switch to the Editor tab and focus on the textbox\n'mathgod' or 'mg': Open MathGod\n'exit' or 'e': Cleanly exit PyNotes\n'save' or 's': Save the current file\n'saveas' or 'sa': Copy the current file to another filename\n'u' or 'undo': Undo the last edit\n'r' or 'redo': Redo the last undoed edit\n'termexec:{string}' or 'te:{string}': Run the given string as a terminal command\n'write:{string}*{n}' or 'w:{string}*{n}': Copy the given text {n} times after the cursor position\n'search' or 'f': Find a string in the current editor\n'fr' or 'find-replace' or 'findreplace': Find and replace a string in the current editor\n'show-source' or 'source-code': Show the main source code of PyNotes (/usr/share/PyNotes/PyNotes.py on Linux and C:/Program Files/PyNotes/PyNotes.py on Windows)\n'new' or 'n': Open a new file in the same editor\n'gotoline:n' or 'gl:n' or 'l:n': Go to the nth line in the active editor if n is given, otherwise prompts for a line number and goes to it\n'pyshell' or 'ps': Open the Python shell if you are in Python HMode\n'o' or or 'load' or 'find' or 'open': Load a new file into the currently active editor\n't:{optional command}' or 'term:{optional command}' or 'terminal:{optional command}' or 'cmd:{optional command}': Open a full terminal running command if given, otherwise /bin/bash or powershell.exe\n'prf' or 'preferences': Change the preferences\n'cancel' or 'z': Cancel the command and go back to the active editor\n'a' or 'selall' or 'all': Select all the text in the active editor\n'c' or 'copy': Copy the selected text\n'cut': Cut the selected text\n'p' or 'paste': Paste the last copied text\n'h:{(x/em/pc/mg/pl)}' or 'help:{(x/em/pc/mg/pl)}': Open the Help of Alt-X commands (this), Email, PyCode, MathGod, Plugins\n'hmode:{(py/la/norm/em/html/md)}': Change the HMode to Python / LaTeX / Normal / Email / HTML / Markdown (PyNotes mode)\n'pf' or 'pagenext': Scroll down a page in the active editor\n'pb' or 'pageback': Scroll up a page in the active editor\n'clear': Clear the active editor completely\n'full': Make the window fullscreen\n'unfull': Make PyNotes windowed mode from fullscreen\n'max' or 'maximize': Maximize the window\n'unmax' or 'unmaximize': Unmaximize the main window\n'min': Minimize the window\n'pycode' or 'pc': Open PyCode\n'<Esc>': 'cancel'\n'sp' or 'speak': Speak the text selected out loud\n'ir' or 'indent-region': Indent the selected region with tabs or spaces\n'unir' or 'unindent-region': Unindent the selected region (handles tabs, spaces, and mixed)\n'st' or 'speech-to-text': Use speech-to-text\n'opd' or 'openplugindir': Open the Plugin's Directory\n'dp' or 'downloadplugins': Download plugins from the PyNotes' GitHub\n'ch' or 'changes': Open a list of the changes made in PyNotes v" + v + "\n'ab' or 'abt' or 'about' or 'pynotes': Open the PyNotes About\n're:{command}*{n}' or 'repeat:{command}*{n}': Repeat the given command {n} times\n'run': Run the code in the active editor if the HMode is Python / LaTeX / HTML\n'cr' or 'comment' or 'comment-region': Comment the selected code if the HMode is Python / LaTeX / HTML / Markdown\n'uncr' or 'uncomment' or 'uncomment-region': Uncomment the selected code if the HMode is Python / LaTeX / HTML / Markdown\n'fullup': Moves the cursor to the beginning of the file\n'fulldown': Moves the cursor to the end of the file\n'ms' or 'mark' or 'markset' or 'mark-selection': Visually marks the selected text in the active editor\n'unms' or 'unmark' or 'unmark-selection': Unmarks the visually marked text inside the selection in the active editor\n'unma' or 'unmarkall': Unmarks all the visually marked text in the active editor\n'sol' or 'startofline': Move the cursor to the start of the line\n'eol' or 'endofline': Move the cursor to the end of the line\n'sendemail' or 'sendmail': Switch to the Email tab if the HMode is Email\n'sh' or 'splithoriz' or 'split-editor-horizontal': Split the currently active editor horizontally\n'sv' or 'splitvert' or 'split-editor-vertical': Split the currently active editor vertically\n'be' or 'balance' or 'balance-editors': Make all the open editors equal size\n'neh' or 'newedithoriz' or 'new-editor-horizontal': Opens a new horizontal editor\n'nev' or 'neweditvert' or 'new-editor-vertical': Opens a new vertical editor\n'onh' or 'opennewhoriz' or 'open-file-horizontal': Opens a file in a new horizontal editor\n'onv' or 'opennewvert' or 'open-file-vertical': Opens a file in a new vertical editor\n'close' or 'closecuredit' or 'close-current-editor': Close the currently active editor\n'switch' or 'switchedit' or 'switch-editor': Cycle between open editors\n'pynavstart:{f/fun/func/function/c/class/name}' or 'pyjumpstart:{f/fun/func/function/c/class/name}' or 'python-jump-startof:{f/fun/func/function/c/class/name}': If the HMode is Python, jump to the start of the current function/class the cursor is in if given f/fun/func/function/c/class, or jump to the start of the given function/class name\n'pynavend:{f/fun/func/function/c/class/name}' or 'pyjumpend:{f/fun/func/function/c/class/name}' or 'python-jump-endof:{f/fun/func/function/c/class/name}': If the HMode is Python, jump to the end of the current function/class the cursor is in if given f/fun/func/function/c/class, or jump to the end of the given function/class name\n'pygodef:{name}': If the HMode is Python, jump to the definition of the given variable name relative to the current scope\n'setsel' or 'selpointset' or 'selection-point-set': Set the selection point at the cursor\n'unsetsel' or 'selpointunset' or 'selection-point-remove': Remove the selection point if set").replace('\n', '\n\n'))
	l3 = hxh.index('end-1c')
	if plgnscmdhelp:
		hxh.insert('end', '\n\nPlugin Commands')
	r3 = hxh.index('end-1c') + '+2c'
	hxh.insert('end', plgnscmdhelp)
	hxh.tag_add('bigstuff', l3, r3)
	hxh.tag_config('bigstuff', font = (monospace, 15, 'bold'))
	hxh.pack(fill = 'both', padx = 10, pady = 10)
	hxh.config(state = 'disabled')
	hxw.sizablefalse()
	hxw.style(root.gettheme())
	hxh.bind('<Escape>', lambda event: hxh.destroy())
	hxh.bind('<Return>', lambda event: hxh.destroy())
	hxh.focus()
def st():
	show('open speech-to-text')
	global recording
	global audio
	recording = False
	audio = []
	def record():
		global recording
		global audio
		def callback(indata, frames, time, status):
			audio.append(indata.copy())
		with sd.InputStream(callback = callback, channels = channels, dtype = dtype, samplerate = samplerate):
			recording = True
			while recording:
				sd.sleep(1000)
	def stop():
		global recording
		global audio
		audio = np.concatenate(audio, axis = 0)
		file = io.BytesIO()
		with wave.open(file, 'wb') as wf:
			wf.setnchannels(1)
			wf.setsampwidth(2)
			wf.setframerate(16000)
			wf.writeframes(audio.tobytes())
		file.seek(0)
		recognizer = sr.Recognizer()
		with sr.AudioFile(file) as source:
			audio_ = recognizer.record(source)
		try:
			text = recognizer.recognize_google(audio_)
		except Exception as e:
			text = f'Error:\n{e}'
		audio = []
		text = re.sub(r'\bfull stop\b', '.', re.sub(r'\bFull Stop\b', '.', re.sub(r'\bfull Stop\b', '.', re.sub(r'\bFull stop\b', '.', re.sub(r'\bComma\b', ',', re.sub(r'\bcomma\b', ',', re.sub(r'\bColon\b', ':', re.sub(r'\bcolon\b', ':', re.sub(r'\bsemi colon\b', ';', re.sub(r'\bSemi Colon\b', ';', re.sub(r'\bsemi Colon\b', ';', re.sub(r'\bSemi colon\b', ';', re.sub(r'\bExclamation Mark\b', '!', re.sub(r'\bexclamation mark', '!', re.sub(r'\bExclamation mark\b', '!', re.sub(r'\bexclamation Mark\b', '!', re.sub(r'\bsemicolon\b', ';', re.sub(r'\bSemicolon\b', ';', re.sub(r'\bNew Line\b', '\n', re.sub(r'\bnew line\b', '\n', re.sub(r'\bNew line\b', '\n', re.sub(r'\bnew Line\b', '\n', re.sub(r'\bnewline\b', '\n', re.sub(r'\bNewline\b', '\n', text))))))))))))))))))))))))
		return text
	samplerate = 16000
	channels = 1
	dtype = np.int16
	dwin = easytk.win()
	dwin.title('Control')
	bframe = dwin.frame()
	bframe.pack(side = 'top', expand = True)
	dwin.button(master = bframe, text = 'Start Recording', command = lambda: threading.Thread(target = record, daemon = True).start()).grid(column = 0, row = 0, padx = 10, pady = 10, sticky = 'w')
	dwin.button(master = bframe, text = 'Stop Recording', command = lambda: [output.delete('1.0', 'end'), output.insert('end', stop())]).grid(column = 1, row = 0, padx = 10, pady = 10, sticky = 'e')
	oframe = dwin.frame()
	output = dwin.textbox(master = oframe)
	output.pack(fill = 'both', expand = True)
	dwin.button(master = oframe, text = 'Write to Active Editor', command = lambda: [active.type_.edit_separator(), active.type_.insert('insert', output.get('1.0', 'end-1c')), active.type_.edit_separator(), dwin.destroy()]).pack(side = 'bottom', fill = 'x', expand = True)
	oframe.pack(side = 'bottom', fill = 'both', expand = True)
	dwin.sizablefalse()
def cmdsplit(s):
	parts = []
	depth = 0
	current = ''
	for ch in s:
		if ch == '(':
			depth += 1
		elif ch == ')':
			depth -= 1
		if ch == ';' and depth <= 0:
			parts.append(current)
			current = ''
		else:
			current += ch
	parts.append(current)
	return parts
def cmdparsegroup(s):
	s = s.strip()
	if s.startswith('('):
		depth = 0
		for i, ch in enumerate(s):
			if ch == '(':
				depth += 1
			elif ch == ')':
				depth -= 1
				if depth == 0:
					content = s[1:i]
					remainder = s[i + 1:]
					if not remainder.startswith('*'):
						raise Exception
					return content, int(remainder[1:])
		raise Exception
	content, n = s.split('*', 1)
	return content, int(n)
def cmdrun(fullcommand):
	cmdparts = cmdsplit(fullcommand)
	if len(cmdparts) > 1:
		for command in cmdparts:
			cmdrun(command)
		return
	if ':' in fullcommand:
		command, commandinput = fullcommand.split(':', 1)
	else:
		command = fullcommand
		commandinput = None
	command = command.strip()
	if commandinput:
		commandinput = commandinput.strip()
	pcrunhook('before', f'alt-x-command:{command}', commandinput)
	if command in pcwrittencommands:
		pcrunhook('before', f'pycode-command:{command}', commandinput)
	if command in plgncmds:
		try:
			execvars = globals().copy()
			execvars['__file__'] = os.path.join(plgncmds[command][0], 'commands')
			execvars['commandinput'] = commandinput
			exec(plgncmds[command][1], execvars)
		except Exception as error:
			error = str(error)
			root.error('Error!', f'There was an error in running the command \'{command}\' from the plugin "{os.path.basename(os.path.normpath(plgncmds[command][0]))}":\n{error}')
		pcrunhook('after', f'alt-x-command:{command}', commandinput)
		return
	if command in pcwrittencommands:
		try:
			execvars = globals().copy()
			execvars['commandinput'] = commandinput
			exec(pcwrittencommands[command], execvars)
		except Exception as error:
			error = str(error)
			root.error('Error!', f'There was an error in running the command \'{command}\' defined in PyCode:\n{error}')
		pcrunhook('after', f'pycode-command:{command}', commandinput)
		pcrunhook('after', f'alt-x-command:{command}', commandinput)
		return
	elif command == 'exit' or command == 'e':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			active.keypress()
			return
		ext()
	elif command == 'sh' or command == 'splithoriz' or command == 'split-editor-horizontal':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			active.keypress()
			return
		if active.title:
			neweditor(active.title)
			show('split editor horizontally')
		else:
			show('no file open to split editor')
	elif command == 'sv' or command == 'splitvert' or command == 'split-editor-vertical':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			active.keypress()
			return
		if active.title:
			neweditor(active.title, 'vertical')
			show('split editor vertically')
		else:
			show('no file open to split editor')
	elif command == 'setsel' or command == 'selpointset' or command == 'selection-point-set':
		active.setselpoint()
	elif command == 'unsetsel' or command == 'selpointunset' or command == 'selection-point-remove':
		active.removeselpoint()
	elif command == 'be' or command == 'balance' or command == 'balance-editors':
		if not commandinput:
			balance()
			show('balanced editors')
		elif commandinput in ('h', 'horiz', 'horizontal'):
			balance('horizontal')
			show('balanced horizontal editors')
		elif commandinput in ('v', 'vert', 'vertical'):
			balance('vertical')
			show('balanced vertical editors')
		else:
			show(f'error: invalid direction \'{commandinput}\' for balance command')
			active.keypress()
			return
	elif command == 'close' or command == 'closecuredit' or command == 'close-current-editor':
		if commandinput:
			try:
				n = int(commandinput)
			except Exception:
				show(f'error: invalid input \'{commandinput}\' to close editor command')
				active.keypress()
				return
			if n < 0 or n >= len(all_editors):
				show(f'error: editor {n} does not exist')
				return
		else:
			n = editindex
		if len(all_editors) == 1:
			show('cannot close only open editor')
			active.keypress()
			return
		editor = all_editors[n]
		was_last_reference = editor.view_master is None and not editor.view_children
		if not editor.close():
			return
		pcrunhook('before', 'close-editor')
		if editor in horizontal.winfo_children():
			horizontal.remove(editor)
		if editor in vertical.winfo_children():
			vertical.remove(editor)
		editor._cancel_all_after_ids()
		if was_last_reference:
			try:
				editor.observer.stop()
				editor.observer.join()
			except Exception:
				pass
		editor.destroy()
		if not horizontal.winfo_children():
			for pane in vertical.winfo_children():
				if pane is not horizontal:
					vertical.remove(pane)
					horizontal.add(pane)
					break
		all_editors.remove(editor)
		if n <= editindex:
			setactive(editindex - 1, force = True)
		show('closed editor')
		pcrunhook('after', 'close-editor')
	elif command == 'switch' or command == 'switchedit' or command == 'switch-editor':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			active.keypress()
			return
		setactive()
	elif command == 'sol' or command == 'startofline':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			active.keypress()
			return
		n = active.type_.index('insert').split('.')[0]
		active.type_.mark_set('insert', n + '.0')
		show(f'moved to start of line {n}')
	elif command == 'eol' or command == 'endofline':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			active.keypress()
			return
		n = active.type_.index('insert').split('.')[0]
		active.type_.mark_set('insert', n + '.end')
		show(f'moved to end of line {n}')
	elif command == 'neh' or command == 'newedithoriz' or command == 'new-editor-horizontal':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			active.keypress()
			return
		neweditor()
	elif command == 'nev' or command == 'neweditvert' or command == 'new-editor-vertical':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			active.keypress()
			return
		neweditor(orient = 'vertical')
	elif command == 'onh' or command == 'opennewhoriz' or command == 'open-file-horizontal':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			active.keypress()
			return
		neweditor(True)
	elif command == 'onv' or command == 'opennewvert' or command == 'open-file-vertical':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			active.keypress()
			return
		neweditor(True, 'vertical')
	elif command == 'changes' or command == 'ch':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			active.keypress()
			return
		changes()
	elif command == 'run':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			active.keypress()
			return
		active.f5()
	elif command == 'ms' or command == 'mark' or command == 'markset' or command == 'mark-selection':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			active.keypress()
			return
		try:
			start = active.type_.index('sel.first')
			end = active.type_.index('sel.last')
		except Exception:
			show('nothing is selected')
		else:
			pcrunhook('before', 'mark-region', (start, end))
			active.type_.tag_add('marked', start, end)
			exec("active.type_.tag_config('marked'," + theme['pynotes:marked'] + ')')
			show(f'marked text from {start} to {end}')
			pcrunhook('after', 'mark-region', (start, end))
	elif command == 'unms' or command == 'unmark' or command == 'unmark-selection':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			active.keypress()
			return
		try:
			start = active.type_.index('sel.first')
			end = active.type_.index('sel.last')
		except Exception:
			show('nothing is selected')
		else:
			pcrunhook('before', 'unmark-region', (start, end))
			active.type_.tag_remove('marked', start, end)
			show(f'unmarked text from {start} to {end}')
			pcrunhook('after', 'unmark-region', (start, end))
	elif command == 'sendemail' or command == 'sendmail':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			active.keypress()
			return
		active.pcswitchemailtab()
	elif command == 'unma' or command == 'unmarkall':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			active.keypress()
			return
		active.type_.tag_remove('marked', '1.0', 'end')
		show('unmarked all text')
	elif command == 'comment' or command == 'cr' or command == 'comment-region':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			active.keypress()
			return
		if not active.hmode in ('python', 'latex', 'html', 'markdown'):
			show('hmode is not python / latex / html / markdown')
			return
		try:
			start = int(active.type_.index('sel.first').split('.')[0])
			end = int(active.type_.index('sel.last').split('.')[0])
		except Exception:
			show('nothing is selected')
		else:
			pcrunhook('before', 'comment-region', (start, end))
			ender = ''
			if active.hmode == 'python':
				commentor = '#'
			elif active.hmode == 'latex':
				commentor = '%'
			elif active.hmode == 'html' or active.hmode == 'markdown':
				commentor = '<!--'
				ender = '-->'
			l = start
			active.type_.edit_separator()
			while not l > end:
				if not active.type_.get(f'{l}.0', f'{l}.end').strip():
					l += 1
					continue
				active.type_.insert(f'{l}.0', commentor)
				active.type_.insert(f'{l}.end', ender)
				l += 1
			active.type_.edit_separator()
			show('comment region')
			pcrunhook('after', 'comment-region', (start, end))
	elif command == 'uncomment' or command == 'uncr' or command == 'uncomment-region':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			active.keypress()
			return
		if not active.hmode in ('python', 'latex', 'html', 'markdown'):
			show('hmode is not python / latex / html / markdown')
			return
		try:
			start = int(active.type_.index('sel.first').split('.')[0])
			end = int(active.type_.index('sel.last').split('.')[0])
		except Exception:
			show('nothing is selected')
		else:
			pcrunhook('before', 'uncomment-region', (start, end))
			active.type_.edit_separator()
			ender = ''
			if active.hmode == 'python':
				commentor = '#'
			elif active.hmode == 'latex':
				commentor = '%'
			elif active.hmode == 'html' or active.hmode == 'markdown':
				commentor = '<!--'
				ender = '-->'
			l = start
			while not l > end:
				stripped = active.type_.get(f'{l}.0', f'{l}.end').lstrip()
				if stripped.startswith(commentor):
					a = len(active.type_.get(f'{l}.0', f'{l}.end')) - len(stripped)
					b = a + len(commentor)
					active.type_.delete(f'{l}.{a}', f'{l}.{b}')
				if ender:
					stripped = active.type_.get(f'{l}.0', f'{l}.end').rstrip()
					if stripped.endswith(ender):
						active.type_.delete(f'{l}.end-{len(ender)}c', f'{l}.end')
				l += 1
			active.type_.edit_separator()
			show('uncomment region')
			pcrunhook('after', 'uncomment-region', (start, end))
	elif command == 'pyshell' or command == 'ps':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			active.keypress()
			return
		active.pcpyshell()
	elif command == 'fullup':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			active.keypress()
			return
		active.type_.mark_set('insert', '1.0')
		active.type_.see('1.0')
	elif command == 'fulldown':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			active.keypress()
			return
		active.type_.mark_set('insert', 'end-1c')
		active.type_.see('end-1c')
	elif command == 'editor' or command == 'ed':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			active.keypress()
			return
		active.pcswitchedittab()
	elif command == 'h' or command == 'help':
		if not commandinput:
			show(f'error: no input given to command \'{command}\'')
			active.keypress()
			return
		if commandinput == 'x' or commandinput == 'commands':
			hx()
		elif commandinput == 'em' or commandinput == 'email':
			hemail()
		elif commandinput == 'pc' or commandinput == 'pycode':
			helppycode()
		elif commandinput == 'mg' or commandinput == 'mathgod':
			helpmathgod()
		elif commandinput == 'pl' or commandinput == 'plugins':
			ap()
		else:
			show(f'error: invalid input \'{commandinput}\'')
	elif command == 'st' or command == 'speech-to-text':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			active.keypress()
			return
		st()
	elif command == 'opd' or command == 'openplugindir':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			active.keypress()
			return
		op()
	elif command == 'dp' or command == 'downloadplugins':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			active.keypress()
			return
		dp()
	elif command == 'indent-region' or command == 'ir':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			active.keypress()
			return
		try:
			start = int(active.type_.index('sel.first').split('.')[0])
			end = int(active.type_.index('sel.last').split('.')[0])
		except Exception:
			show('nothing is selected')
		else:
			pcrunhook('before', 'indent-region', (start, end))
			if taborspace:
				whitespace = '    '
			else:
				whitespace = '	'
			l = start
			active.type_.edit_separator()
			while not l == end:
				active.type_.insert(f'{l}.0', whitespace)
				l += 1
			active.type_.insert(f'{l}.0', whitespace)
			active.type_.edit_separator()
			show('indent region')
			pcrunhook('after', 'indent-region', (start, end))
	elif command == 'unindent-region' or command == 'unir':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			active.keypress()
			return
		try:
			start = int(active.type_.index('sel.first').split('.')[0])
			end = int(active.type_.index('sel.last').split('.')[0])
		except Exception:
			show('nothing is selected')
		else:
			pcrunhook('before', 'unindent-region', (start, end))
			active.type_.edit_separator()
			lines = [active.type_.get(f'{l}.0', f'{l}.end') for l in range(start, end + 1)]
			min_spaces = None
			for line in lines:
				if not line.strip() or line.startswith('\t'):
					continue
				n = len(line) - len(line.lstrip(' '))
				if n > 0 and (min_spaces is None or n < min_spaces):
					min_spaces = n
			if min_spaces is None:
				min_spaces = 4
			for i, l in enumerate(range(start, end + 1)):
				line = lines[i]
				if not line.strip():
					continue
				if line.startswith('\t'):
					active.type_.delete(f'{l}.0', f'{l}.1')
				elif line.startswith(' '):
					remove = 0
					for ch in line:
						if ch == ' ' and remove < min_spaces:
							remove += 1
						else:
							break
					if remove:
						active.type_.delete(f'{l}.0', f'{l}.{remove}')
			active.type_.edit_separator()
			show('unindent region')
			pcrunhook('after', 'unindent-region', (start, end))
	elif command == 'te' or command == 'termexec':
		if not commandinput:
			show(f'error: no input given to command \'{command}\'')
			active.keypress()
			return
		try:
			show('output: ' + termexec(commandinput))
		except Exception:
			show(f'error: invalid input \'{commandinput}\'')
	elif command == 'mathgod' or command == 'mg':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			active.keypress()
			return
		mathgod()
	elif command == 'write' or command == 'w':
		if not commandinput:
			show(f'error: no input given to command \'{command}\'')
			active.keypress()
			return
		active.type_.edit_separator()
		try:
			textwrote, timeswrote = cmdparsegroup(commandinput)
			active.type_.insert(active.type_.index('insert'), textwrote.encode().decode('unicode_escape') * timeswrote)
			show(f'wrote \'{textwrote}\' {timeswrote} times')
		except Exception:
			show(f'error: invalid input \'{commandinput}\'')
		active.type_.edit_separator()
	elif command == 'repeat' or command == 're':
		try:
			content, n = cmdparsegroup(commandinput)
			for i in range(n):
				cmdrun(content)
		except Exception:
			show(f'error: invalid input \'{commandinput}\'')
	elif command == 'u' or command == 'undo':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			active.keypress()
			return
		active.undo()
	elif command == 'r' or command == 'redo':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			active.keypress()
			return
		active.redo()
	elif command == 'save' or command == 's':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			active.keypress()
			return
		active.sssv()
	elif command == 'saveas' or command == 'sa':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			active.keypress()
			return
		active.ssv()
	elif command == 'search' or command == 'f':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			active.keypress()
			return
		active.f()
	elif command == 'find-replace' or command == 'findreplace' or command == 'fr':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			active.keypress()
			return
		active.fr()
	elif command == 'show-source' or command == 'source-code':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			active.keypress()
			return
		ss()
	elif command == 'new' or command == 'n':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			active.keypress()
			return
		active.nw()
	elif command == 'l' or command == 'gl' or command == 'gotoline':
		active.gl(commandinput)
	elif command == 'open' or command == 'find' or command == 'o' or command == 'load':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			active.keypress()
			return
		active.llld()
	elif command == 'terminal' or command == 'cmd' or command == 'term' or command == 't':
		if commandinput:
			commandlist = commandinput.split(' ')
			if not shutil.which(commandlist[0]):
				show(f'error: \'{commandlist[0]}\' not found or not executable')
				active.keypress()
				return
			term(command = commandlist, endmessage = '--- Command finished, press any key to continue ---')
		else:
			term()
	elif command == 'prf' or command == 'preferences':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			active.keypress()
			return
		prf()
	elif command == 'cancel' or command == 'z':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			active.keypress()
			return
		pass
	elif command == '':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			active.keypress()
			return
		pass
	elif command == 'a' or command == 'selall' or command == 'all':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			active.keypress()
			return
		active.selall()
	elif command == 'copy' or command == 'c':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			active.keypress()
			return
		active.cp()
	elif command == 'cut':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			active.keypress()
			return
		active.cut()
	elif command == 'pf' or command == 'pagenext':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			active.keypress()
			return
		active.ptf()
	elif command == 'pb' or command == 'pageback':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			active.keypress()
			return
		active.ptb()
	elif command == 'paste' or command == 'p':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			active.keypress()
			return
		active.pst()
	elif command == 'sp' or command == 'speak':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			active.keypress()
			return
		active.spk()
	elif command == 'full':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			active.keypress()
			return
		pcfullscreen()
	elif command == 'unfull':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			active.keypress()
			return
		pcunfullscreen()
	elif command == 'max' or command == 'maximize':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			active.keypress()
			return
		pcmax()
	elif command == 'unmax' or command == 'unmaximize':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			active.keypress()
			return
		pcunmax()
	elif command == 'min':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			active.keypress()
			return
		pcmin()
	elif command == 'clear':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			active.keypress()
			return
		active.pccleareditor()
	elif command == 'pycode' or command == 'pc':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			active.keypress()
			return
		pc()
	elif command == 'ab' or command == 'abt' or command == 'about' or command == 'pynotes':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			active.keypress()
			return
		abt()
	elif not (active.hmode in ['png', 'pdf', 'epub']) and command == 'hmode':
		if not commandinput:
			show(f'error: no input given to command \'{command}\'')
			active.keypress()
			return
		if not (commandinput in ('python', 'py', 'latex', 'la', 'normal', 'norm', 'email', 'em', 'html', 'markdown', 'md') or commandinput in plgnhmodes):
			show(f'hmode \'{commandinput}\' does not exist')
			return
		try:
			active.pchmode(commandinput)
		except Exception:
			show(f'error: invalid command \'{command}\'')
	elif command == 'pynavstart' or command == 'pyjumpstart' or command == 'python-jump-startof':
		if not commandinput:
			show(f'error: no input given to command \'{command}\'')
			active.keypress()
			return
		active.pcpystartof(commandinput)
	elif command == 'pynavend' or command == 'pyjumpend' or command == 'python-jump-endof':
		if not commandinput:
			show(f'error: no input given to command \'{command}\'')
			active.keypress()
			return
		active.pcpyendof(commandinput)
	elif command == 'pygodef':
		if not commandinput:
			show(f'error: no input given to command \'{command}\'')
			active.keypress()
			return
		active.pcgovardef(commandinput)
	else:
		show(text = f'error: invalid command \'{command}\'')
	pcrunhook('after', f'alt-x-command:{command}', commandinput)
	active.keypress()
def show(text):
	global prompting
	prompting = False
	cmdentry.config(state = 'normal')
	cmdentry.delete('1.0', 'end')
	cmdentry.insert('end', text.replace('\n', '\\n'))
	cmdentry.unbind('<KeyPress>')
	cmdentry.unbind('<Return>')
	cmdentry.unbind('<Escape>')
	cmdentry.config(state = 'disabled')
	cmdautocomplete.pack_forget()
engine = stt.init()
def actualspk(text):
	global engine
	try:
		engine.say(text)
		engine.runAndWait()
	except Exception as error:
		error = str(error)
		root.error('Error', f'An error occured:{error}')
def prompt(text, autocompletefunc = None, defaultinput = None):
	global prompting
	def check_edit(event, text, promptend):
		cmdentry.delete('1.0', promptend)
		cmdentry.insert('1.0', text)
		cmdentry.tag_add('prompt', '1.0', promptend)
		cmdentry.mark_set('insert', '1.end')
		cmdautocomplete.pack_forget()
		if event.keysym == 'BackSpace' and cmdentry.compare('insert', '==', promptend):
			return 'break'
	def setreturninput(promptend):
		global prompting
		nonlocal inputtext
		inputtext = cmdentry.get(promptend, '1.end')
		prompting = False
	def autocomplete(cmdentry, promptend, autocompletefunc):
		completes = []
		typedtext = cmdentry.get(promptend, '1.end')
		if callable(autocompletefunc):
			autocompletelist = sorted(autocompletefunc(typedtext))
		else:
			autocompletelist = autocompletefunc
		for option in autocompletelist:
			if option.startswith(typedtext):
				completes.append(option)
		if (newcomplete := os.path.commonprefix(completes)[len(typedtext):]):
			cmdentry.insert('1.end', newcomplete)
		else:
			if not completes:
				completes.append('[no match]')
			cmdautocomplete.config(state = 'normal')
			cmdautocomplete.delete('1.0', 'end')
			cmdautocomplete.insert('1.0', '    '.join(completes))
			cmdautocomplete.pack(padx = 10, pady = 10, fill = 'x', anchor = 'n', after = cmdentry)
			cmdautocomplete.update_idletasks()
			displaylines = cmdautocomplete.count('1.0', 'end-1c', 'displaylines')
			cmdautocomplete.config(height = min(displaylines[0], 5) if displaylines else 1)
			cmdautocomplete.config(state = 'disabled')
	prompting = True
	inputtext = ''
	cmdentry.config(state = 'normal')
	cmdentry.delete('1.0', 'end')
	cmdentry.insert('1.0', text)
	promptend = cmdentry.index('1.end')
	cmdentry.tag_add('prompt', '1.0', promptend)
	cmdentry.tag_config('prompt', font = (monospace, 12, 'bold'))
	if defaultinput:
		cmdentry.insert('end', defaultinput)
		cmdentry.mark_set('insert', 'end')
	cmdentry.bind('<KeyPress>', lambda event, text = text, promptend = promptend: check_edit(event, text, promptend))
	cmdentry.bind('<Return>', lambda event, promptend = promptend: setreturninput(promptend))
	cmdentry.bind('<Escape>', lambda event: show(''))
	if autocompletefunc:
		cmdentry.bind('<Tab>', lambda event, cmdentry = cmdentry, promptend = promptend, autocompletefunc = autocompletefunc: (autocomplete(cmdentry, promptend, autocompletefunc), 'break')[1])
	root.update()
	cmdentry.focus_set()
	while prompting:
		root.update()
	cmdentry.delete('1.0', 'end')
	cmdentry.unbind('<KeyPress>')
	cmdentry.unbind('<Return>')
	cmdentry.unbind('<Escape>')
	cmdentry.config(state = 'disabled')
	cmdautocomplete.pack_forget()
	root.update()
	return inputtext
def cmdcommandgroups():
	return (((('exit', 'e'), None), (('sh', 'splithoriz', 'split-editor-horizontal'), None), (('sv', 'splitvert', 'split-editor-vertical'), None), (('setsel', 'selpointset', 'selection-point-set'), None), (('unsetsel', 'selpointunset', 'selection-point-remove'), None), (('be', 'balance', 'balance-editors'), None), (('close', 'closecuredit', 'close-current-editor'), None), (('switch', 'switchedit', 'switch-editor'), None), (('sol', 'startofline'), None), (('eol', 'endofline'), None), (('neh', 'newedithoriz', 'new-editor-horizontal'), None), (('nev', 'neweditvert', 'new-editor-vertical'), None), (('onh', 'opennewhoriz', 'open-file-horizontal'), None), (('onv', 'opennewvert', 'open-file-vertical'), None), (('changes', 'ch'), None), (('run',), ('python', 'latex', 'html')), (('ms', 'mark', 'markset', 'mark-selection'), None), (('unms', 'unmark', 'unmark-selection'), None), (('sendemail', 'sendmail'), ('email',)), (('unma', 'unmarkall'), None), (('comment', 'cr', 'comment-region'), ('python', 'latex', 'html', 'markdown')), (('uncomment', 'uncr', 'uncomment-region'), ('python', 'latex', 'html', 'markdown')), (('pyshell', 'ps'), ('python',)), (('fullup',), None), (('fulldown',), None), (('editor', 'ed'), None), (('h', 'help'), None), (('st', 'speech-to-text'), None), (('opd', 'openplugindir'), None), (('dp', 'downloadplugins'), None), (('indent-region', 'ir'), None), (('unindent-region', 'unir'), None), (('te', 'termexec'), None), (('mathgod', 'mg'), None), (('write', 'w'), None), (('repeat', 're'), None), (('u', 'undo'), None), (('r', 'redo'), None), (('save', 's'), None), (('saveas', 'sa'), None), (('search', 'f'), None), (('find-replace', 'findreplace', 'fr'), None), (('show-source', 'source-code'), None), (('new', 'n'), None), (('l', 'gl', 'gotoline'), None), (('open', 'find', 'o', 'load'), None), (('terminal', 'cmd', 'term', 't'), None), (('prf', 'preferences'), None), (('cancel', 'z'), None), (('a', 'selall', 'all'), None), (('copy', 'c'), None), (('cut',), None), (('pf', 'pagenext'), None), (('pb', 'pageback'), None), (('paste', 'p'), None), (('sp', 'speak'), None), (('full',), None), (('unfull',), None), (('max', 'maximize'), None), (('unmax', 'unmaximize'), None), (('min',), None), (('clear',), None), (('pycode', 'pc'), None), (('ab', 'abt', 'about', 'pynotes'), None), (('pynavstart', 'pyjumpstart', 'python-jump-startof'), ('python',)), (('pynavend', 'pyjumpend', 'python-jump-endof'), ('python',)), (('pygodef',), ('python',))))
cmdmandatoryinputaliases = frozenset(('h', 'help', 'te', 'termexec', 'write', 'w', 'repeat', 're', 'pynavstart', 'pyjumpstart', 'python-jump-startof', 'pynavend', 'pyjumpend', 'python-jump-endof', 'pygodef'))
def cmdbasecommandnames():
	basecommandnames = []
	for aliases, hmodes in cmdcommandgroups():
		if hmodes is not None and (active is None or active.hmode not in hmodes):
			continue
		for alias in aliases:
			basecommandnames.append(alias + ':' if alias in cmdmandatoryinputaliases else alias)
	if active is None or active.hmode not in ('png', 'pdf', 'epub'):
		basecommandnames.append('hmode:')
	basecommandnames.extend(plgncmds)
	basecommandnames.extend(pcwrittencommands)
	return basecommandnames
def cmdcommandvalues(command):
	if command == 'hmode':
		if active is None or active.hmode in ('png', 'pdf', 'epub'):
			return []
		return list(('python', 'py', 'latex', 'la', 'normal', 'norm', 'email', 'em', 'html', 'markdown', 'md')) + list(plgnhmodes)
	if command in ('h', 'help'):
		return ['x', 'commands', 'em', 'email', 'pc', 'pycode', 'mg', 'mathgod', 'pl', 'plugins']
	if command in ('be', 'balance', 'balance-editors'):
		return ['h', 'horiz', 'horizontal', 'v', 'vert', 'vertical']
	if command in ('pynavstart', 'pyjumpstart', 'python-jump-startof', 'pynavend', 'pyjumpend', 'python-jump-endof'):
		if active is None or active.hmode != 'python':
			return []
		return ['f', 'fun', 'func', 'function', 'c', 'class'] + sorted(set(dname for dl, dc, dname, dkind in active._python_def_names))
	if command == 'pygodef':
		if active is None or active.hmode != 'python':
			return []
		return sorted(set(name for scope in active._python_scopes for name in scope['names']))
	return None
def cmdactivesegment(typedtext):
	prefix = ''
	while True:
		stripped = typedtext.lstrip()
		if stripped != typedtext:
			prefix += typedtext[:len(typedtext) - len(stripped)]
			typedtext = stripped
			continue
		parts = cmdsplit(typedtext)
		if len(parts) > 1:
			prefix += typedtext[:len(typedtext) - len(parts[-1])]
			typedtext = parts[-1]
			continue
		matched = False
		for keyword in ('re:', 'repeat:'):
			if typedtext.startswith(keyword):
				prefix += keyword
				typedtext = typedtext[len(keyword):]
				matched = True
				break
		if matched:
			continue
		if typedtext.startswith('('):
			prefix += '('
			typedtext = typedtext[1:]
			continue
		break
	return prefix, typedtext
def cmdautocompletefunc(typedtext):
	prefix, activesegment = cmdactivesegment(typedtext)
	if ':' in activesegment:
		commandpart, valuepart = activesegment.split(':', 1)
		valuestripped = valuepart.lstrip()
		valueprefix = valuepart[:len(valuepart) - len(valuestripped)]
		values = cmdcommandvalues(commandpart)
		if not values:
			return []
		return [prefix + commandpart + ':' + valueprefix + value for value in sorted(values) if value.startswith(valuestripped)]
	candidates = [name for name in cmdbasecommandnames() if name.startswith(activesegment)]
	values = cmdcommandvalues(activesegment)
	if values:
		if activesegment in candidates:
			candidates.remove(activesegment)
		candidates.extend(activesegment + ':' + value for value in sorted(values))
	return [prefix + candidate for candidate in candidates]
def cmd():
	cmdrun(prompt('Alt-X- ', cmdautocompletefunc))
def pcprompt(text, autocompletefunc = None, defaultinput = None):
	return prompt(text, globals()[autocompletefunc] if isinstance(autocompletefunc, str) else autocompletefunc, defaultinput)
def pcdone(nc):
	open(f'{homedir}/.pynotes', 'w+', encoding = 'utf-8').write(nc)
	pcread(nc)
def say(string):
	root.info('Print PyCode', string)
def ask(string):
	return root.askstring('Input PyCode', string)
def pcrun(code):
	code = code.split('\n')
	for line in code:
		try:
			exec(line, globals())
		except easytk.tk.TclError:
			pass
		except Exception as error:
			error = str(error)
			root.error('Error', f'Error in running the translated PyCode line\n"{line}":\n{error}')
def pcexecaction(code):
	try:
		exec(code, globals())
	except easytk.tk.TclError:
		pass
	except Exception as error:
		error = str(error)
		root.error('Error', f'Error in running the translated PyCode line\n"{code}":\n{error}')
def pcopenhelp(thing):
	if thing == 'commands':
		show('open alt-x commands help')
		hx()
	elif thing == 'email':
		show('open email help')
		hemail()
	elif thing == 'pycode':
		show('open pycode help')
		helppycode()
	elif thing == 'mathgod':
		show('open mathgod help')
		helpmathgod()
	elif thing == 'plugins':
		show('open plugin help')
		ap()
def pctermexec(command):
	show('output: ' + termexec(command))
def pcrepeatx(command, n):
	for i in range(n):
		cmdrun(command)
def pcfullscreen():
	pcrunhook('before', 'fullscreen')
	root.update()
	root.attributes('-fullscreen', True)
	root.update()
	show('fullscreen mode')
	pcrunhook('after', 'fullscreen')
def pcunfullscreen():
	pcrunhook('before', 'un-fullscreen')
	root.update()
	root.attributes('-fullscreen', False)
	root.update()
	show('windowed mode')
	pcrunhook('after', 'un-fullscreen')
def pcmax():
	pcrunhook('before', 'maximize-window')
	root.update()
	if platform.system() == 'Linux':
		root.attributes('-zoomed', True)
	else:
		root.state('zoomed')
	root.update()
	show('maximized window')
	pcrunhook('after', 'maximize-window')
def pcunmax():
	pcrunhook('before', 'unmaximize-window')
	root.update()
	if platform.system() == 'Linux':
		root.attributes('-zoomed', False)
	else:
		root.state('normal')
	root.update()
	show('unmaximize window')
	pcrunhook('after', 'unmaximize-window')
def pcmin():
	pcrunhook('before', 'minimize-window')
	root.iconify()
	pcrunhook('after', 'minimize-window')
pcwrittencommands = {}
pcbeforehooks = {}
pcafterhooks = {}
def pcrunhook(when, event, commandinput = None):
	try:
		root.update()
	except Exception:
		pass
	hooks = pcbeforehooks if when == 'before' else pcafterhooks
	for key in dict.fromkeys((event, event.split(':', 1)[0])):
		for code in hooks.get(key, []):
			try:
				globals()['commandinput'] = commandinput
				for line in code.split('\n'):
					exec(line, globals())
			except Exception as error:
				error = str(error)
				root.error('Error in PyCode', f'There was an error in running the \'{when}:{event}\' hook:\n{error}')
def pcask(askstring):
	return root.askstring('PyCode Input', askstring)
def pccopytext(text):
	root.clipboard_clear()
	root.clipboard_append(text)
	show(f'copied \'{text}\'')
	root.update()
def pcgosettitle(title):
	global pcsettitle
	root.title(title)
	show(f'set window title to \'{title}\'')
	pcsettitle = True
def pcunsettitle():
	global pcsettitle
	show('unset window title')
	pcsettitle = False
	active.keypress()
def pckillexit():
	os._exit(0)
def pcsetvar(var, val):
	globals()[var] = val
def pcwhileloop(condfunc, bodyfunc):
	while condfunc():
		bodyfunc()
def pccolor(name, *args, **kwargs):
	theme_key = f'pccolor:{name}'
	theme[theme_key] = ', '.join([repr(arg) for arg in args] + [f'{kw} = {repr(val)}' for kw, val in kwargs.items()])
	plugin_hl[theme_key] = {name: (None, theme_key)}
	_PYTHON_EDITOR_HL_SKIP_REMOVE_TAGS.add(name)
	for editor in all_editors:
		editor.type_.tag_config(name, *args, **kwargs)
def pcneweditfile(orient = 'horizontal'):
	neweditor(True, orient)
def pccloseedit(n = None):
	if len(all_editors) == 1:
		show('error: cannot close only open editor')
		return
	if n is None:
		n = editindex
	else:
		n = int(n)
	editor = all_editors[n]
	was_last_reference = editor.view_master is None and not editor.view_children
	if not editor.close():
		return
	pcrunhook('before', 'close-editor')
	if editor in horizontal.winfo_children():
		horizontal.remove(editor)
	if editor in vertical.winfo_children():
		vertical.remove(editor)
	editor._cancel_all_after_ids()
	if was_last_reference:
		try:
			editor.observer.stop()
			editor.observer.join()
		except Exception:
			pass
	editor.destroy()
	if not horizontal.winfo_children():
		for pane in vertical.winfo_children():
			if pane is not horizontal:
				vertical.remove(pane)
				horizontal.add(pane)
				break
	all_editors.remove(editor)
	if n <= editindex:
		setactive(editindex - 1, force = True)
	show('closed editor')
	pcrunhook('after', 'close-editor')
def pcsplitedit(n = None, orient = 'horizontal'):
	if n is None:
		n = editindex
	else:
		n = int(n)
	editor = all_editors[n]
	if editor.title:
		neweditor(editor.title, orient)
		show('split editor horizontally' if orient == 'horizontal' else 'split editor vertically')
	else:
		show('no file open to split editor')
pycodetopythoncommands = {'aboutpynotes': 'abt', 'ask': 'pcask', 'balanceeditors': 'balance', 'cleareditor': 'active.pccleareditor', 'closeeditor': 'pccloseedit', 'cmdrun': 'cmdrun', 'color': 'pccolor', 'commentregion': 'active.pccommentregion', 'commentselection': 'active.pccommentselection', 'copy': 'active.cp', 'copytext': 'pccopytext', 'cut': 'active.cut', 'delete': 'active.pcdelete', 'dictate': 'st', 'downloadplugins': 'dp', 'findreplace': 'active.fr', 'findtext': 'active.f', 'fullscreen': 'pcfullscreen', 'get': 'active.type_.get', 'getselection': 'active.pcgetselection', 'gotoline': 'active.gl', 'hmode': 'active.pchmode', 'indentregion': 'active.pcindentregion', 'indentselection': 'active.pcindentselection', 'insert': 'active.type_.insert', 'killquit': 'pckillexit', 'mark': 'active.pcmark', 'markselection': 'active.pcmarkselection', 'mathgod': 'mathgod', 'maximize': 'pcmax', 'minimize': 'pcmin', 'movecursor': 'active.pcmovecursor', 'neweditor': 'neweditor', 'newfile': 'active.nw', 'openfile': 'active.llld', 'openfilenewedit': 'pcneweditfile', 'openhelp': 'pcopenhelp', 'openplugindir': 'op', 'openpycode': 'pc', 'openterm': 'term', 'pageback': 'active.ptb', 'pageforw': 'active.ptf', 'pass': 'pass', 'paste': 'active.pst', 'preferences': 'prf', 'prompt': 'pcprompt', 'pynotessourcecode': 'ss', 'pyshell': 'active.pcpyshell', 'pythongoendof': 'active.pcpyendof', 'pythongostartof': 'active.pcpystartof', 'pythongovardef': 'active.pcgovardef', 'quit': 'ext', 'redo': 'active.redo', 'repeatxcommand': 'pcrepeatx', 'removeselectionpoint': 'active.removeselpoint', 'return': 'return', 'runcode': 'active.f5', 'saveasfile': 'active.ssv', 'savefile': 'active.sssv', 'say': 'say', 'selall': 'active.selall', 'select': 'active.pcselecttext', 'setselectionpoint': 'active.setselpoint', 'setvar': 'pcsetvar', 'setwintitle': 'pcgosettitle', 'show': 'show', 'speaktext': 'active.spk', 'spliteditor': 'pcsplitedit', 'switcheditor': 'setactive', 'switcheditortab': 'active.pcswitchedittab', 'switchemailtab': 'active.pcswitchemailtab', 'tag': 'active.type_.tag_add', 'termexec': 'pctermexec', 'tkindex': 'active.pctkindex', 'toggleselectionpoint': 'active.toggleselpoint', 'typecommand': 'cmd', 'uncommentregion': 'active.pcuncommentregion', 'uncommentselection': 'active.pcuncommentselection', 'undo': 'active.undo', 'unfullscreen': 'pcunfullscreen', 'unindentregion': 'active.pcunindentregion', 'unindentselection': 'active.pcunindentselection', 'unmark': 'active.pcunmark', 'unmarkall': 'active.pcunmarkall', 'unmaximize': 'pcunmax', 'unsetwintitle': 'pcunsettitle', 'untag': 'active.type_.tag_remove', 'wait': 'time.sleep', 'write': 'active.pccmdwrite'}
def pcread(code):
	global pcwrittencommands
	global pcbeforehooks
	global pcafterhooks
	global pycodecommands
	global pythoncommands
	global pycode_keybindings_cdt
	pycodecommands = sorted(list(pycodetopythoncommands))
	pythoncommands = [pycodetopythoncommands[x] for x in pycodecommands]
	pcwrittencommands = {}
	pcbeforehooks = {}
	pcafterhooks = {}
	def finddelimitedspans(s, opener, closer):
		spans = []
		depth = 0
		instring = False
		start = -1
		i = 0
		while i < len(s):
			ch = s[i]
			if ch == '\'':
				instring = not instring
			if not instring:
				if s.startswith(opener, i):
					if depth == 0:
						start = i
					depth += 1
					i += len(opener)
					continue
				elif s.startswith(closer, i):
					depth -= 1
					i += len(closer)
					if depth == 0 and start != -1:
						spans.append((start, i))
						start = -1
					continue
			i += 1
		return spans
	def pycodesplitdownarrow(s):
		parts = []
		depth = 0
		instring = False
		current = ''
		i = 0
		while i < len(s):
			ch = s[i]
			if ch == '\'':
				instring = not instring
			if not instring:
				if ch in '([{':
					depth += 1
				elif ch in ')]}':
					depth -= 1
			if not instring and depth == 0 and s.startswith('↓', i):
				parts.append(current)
				current = ''
				i += 1
				continue
			current += ch
			i += 1
		parts.append(current)
		return parts
	def pycodeblocktoexpr(blockcode):
		pieces = [piece.strip() for piece in pycodesplitdownarrow(blockcode) if piece.strip()]
		if not pieces:
			return 'None'
		exprs = []
		for piece in pieces:
			expr = pycodeindex(piece)
			if not expr:
				return None
			exprs.append(expr)
		if len(exprs) == 1:
			return f'({exprs[0]})'
		return '(' + ', '.join(exprs) + ')'
	def pycodecondexpr(condition):
		return pycodeindex(condition) or condition
	def pycodeifexpr(pycodecode):
		text = pycodecode.strip()
		ifmatch = re.match(r'if\s*(?=\()', text)
		if not ifmatch:
			return None
		pos = ifmatch.end()
		condspans = finddelimitedspans(text[pos:], '(', ')')
		if not condspans or condspans[0][0] != 0:
			return None
		cs, ce = condspans[0]
		condition = pycodecondexpr(text[pos + cs + 1:pos + ce - 1].strip())
		pos += ce
		gapmatch = re.match(r'\s*', text[pos:])
		pos += gapmatch.end()
		if pos >= len(text) or text[pos] != '{':
			return None
		codespans = finddelimitedspans(text[pos:], '{', '}')
		if not codespans or codespans[0][0] != 0:
			return None
		bs, be = codespans[0]
		blockcode = text[pos + bs + 1:pos + be - 1]
		trueexpr = pycodeblocktoexpr(blockcode)
		if trueexpr is None:
			raise Exception(f'Invalid command "{blockcode.strip()}"')
		pos += be
		branches = []
		while True:
			gapmatch = re.match(r'\s*', text[pos:])
			nextpos = pos + gapmatch.end()
			elifmatch = re.match(r'elif\s*(?=\()', text[nextpos:])
			if not elifmatch:
				break
			nextpos += elifmatch.end()
			econdspans = finddelimitedspans(text[nextpos:], '(', ')')
			if not econdspans or econdspans[0][0] != 0:
				raise Exception(f'Invalid condition in "{text}"')
			ecs, ece = econdspans[0]
			econdition = pycodecondexpr(text[nextpos + ecs + 1:nextpos + ece - 1].strip())
			nextpos += ece
			ebracematch = re.match(r'\s*', text[nextpos:])
			nextpos += ebracematch.end()
			if nextpos >= len(text) or text[nextpos] != '{':
				raise Exception(f'Invalid syntax in "{text}"')
			ecodespans = finddelimitedspans(text[nextpos:], '{', '}')
			if not ecodespans or ecodespans[0][0] != 0:
				raise Exception(f'Invalid syntax in "{text}"')
			ebs, ebe = ecodespans[0]
			eblockcode = text[nextpos + ebs + 1:nextpos + ebe - 1]
			eexpr = pycodeblocktoexpr(eblockcode)
			if eexpr is None:
				raise Exception(f'Invalid command "{eblockcode.strip()}"')
			branches.append((econdition, eexpr))
			pos = nextpos + ebe
		gapmatch = re.match(r'\s*', text[pos:])
		nextpos = pos + gapmatch.end()
		elseexpr = 'None'
		if re.match(r'else\s*(?=\{)', text[nextpos:]):
			elsematch = re.match(r'else\s*', text[nextpos:])
			nextpos += elsematch.end()
			ocodespans = finddelimitedspans(text[nextpos:], '{', '}')
			if not ocodespans or ocodespans[0][0] != 0:
				raise Exception(f'Invalid syntax in "{text}"')
			obs, obe = ocodespans[0]
			oblockcode = text[nextpos + obs + 1:nextpos + obe - 1]
			oexpr = pycodeblocktoexpr(oblockcode)
			if oexpr is None:
				raise Exception(f'Invalid command "{oblockcode.strip()}"')
			elseexpr = oexpr
			pos = nextpos + obe
		if text[pos:].strip():
			raise Exception(f'Invalid syntax in "{text}"')
		result = elseexpr
		for econdition, eexpr in reversed(branches):
			result = f'({eexpr} if ({econdition}) else {result})'
		return f'({trueexpr} if ({condition}) else {result})'
	def pycodewhileexpr(pycodecode):
		text = pycodecode.strip()
		whilematch = re.match(r'while\s*(?=\()', text)
		if not whilematch:
			return None
		pos = whilematch.end()
		condspans = finddelimitedspans(text[pos:], '(', ')')
		if not condspans or condspans[0][0] != 0:
			return None
		cs, ce = condspans[0]
		condition = pycodecondexpr(text[pos + cs + 1:pos + ce - 1].strip())
		pos += ce
		gapmatch = re.match(r'\s*', text[pos:])
		pos += gapmatch.end()
		if pos >= len(text) or text[pos] != '{':
			return None
		codespans = finddelimitedspans(text[pos:], '{', '}')
		if not codespans or codespans[0][0] != 0:
			return None
		bs, be = codespans[0]
		blockcode = text[pos + bs + 1:pos + be - 1]
		bodyexpr = pycodeblocktoexpr(blockcode)
		if bodyexpr is None:
			raise Exception(f'Invalid command "{blockcode.strip()}"')
		pos += be
		if text[pos:].strip():
			raise Exception(f'Invalid syntax in "{text}"')
		return f'pcwhileloop(lambda: ({condition}), lambda: {bodyexpr})'
	def splittoplevelcommas(s):
		parts = []
		depth = 0
		instring = False
		current = ''
		for ch in s:
			if ch == '\'':
				instring = not instring
			if not instring:
				if ch == '(':
					depth += 1
				elif ch == ')':
					depth -= 1
			if ch == ',' and depth == 0 and not instring:
				parts.append(current)
				current = ''
			else:
				current += ch
		parts.append(current)
		return parts
	def indexargs(s):
		parts = splittoplevelcommas(s)
		for i, part in enumerate(parts):
			partstripped = part.strip()
			if partstripped in pycodecommands or partstripped.split(' ')[0] in pycodecommands:
				parts[i] = pycodeindex(partstripped)
		return ','.join(parts)
	def pycodeindex(pycodecode):
		ifexpr = pycodeifexpr(pycodecode)
		if ifexpr is not None:
			return ifexpr
		whileexpr = pycodewhileexpr(pycodecode)
		if whileexpr is not None:
			return whileexpr
		if pycodecode in pycodecommands:
			if pycodecode in ('pass', 'return'):
				return pythoncommands[pycodecommands.index(pycodecode)]
			return pythoncommands[pycodecommands.index(pycodecode)] + '()'
		elif pycodecode.split(' ', 1)[0] in pycodecommands:
			func = pycodecode.split(' ', 1)[0]
			rest = pycodecode.split(' ', 1)[1]
			rest_lstripped = rest.lstrip()
			if rest_lstripped.startswith('('):
				depth = 0
				close_idx = -1
				for i, ch in enumerate(rest_lstripped):
					if ch == '(':
						depth += 1
					elif ch == ')':
						depth -= 1
						if depth == 0:
							close_idx = i
							break
				if close_idx != -1:
					inner = rest_lstripped[1:close_idx].strip()
					after = rest_lstripped[close_idx + 1:]
					return pythoncommands[pycodecommands.index(func)] + f'({indexargs(inner)})' + after
			giveninput = rest
			if giveninput.strip() in pycodecommands or giveninput.strip().split(' ')[0] in pycodecommands:
				giveninput = pycodeindex(giveninput)
			elif ',' in giveninput:
				giveninput = indexargs(giveninput)
			return pythoncommands[pycodecommands.index(func)] + f'({giveninput})'
	code = code.replace('\n', '').split(';')
	cdt = ''
	type_bind_cdt = ''
	startupcdt = ''
	simple_bindings_seen = {}
	chord_any_defined = False
	nonmod_completions = []
	nonmod_transitions = []
	mod_key_transitions = {}
	mod_key_completions = {}
	for line_ in code:
		line = line_.strip() + ';'
		if line_:
			try:
				def matchtransition(s, opener, closer, arrow, requireafterarrow = None):
					lhsspans = finddelimitedspans(s, opener, closer)
					if not lhsspans:
						return []
					lhsstart, lhsend = lhsspans[0]
					rest = s[lhsend:]
					arrowmatch = re.match(r'\s*' + re.escape(arrow) + r'\s*', rest)
					if not arrowmatch:
						return []
					if requireafterarrow is not None and not re.match(requireafterarrow, s[lhsstart:lhsend]):
						return []
					afterarrow = rest[arrowmatch.end():]
					rhsspans = finddelimitedspans(afterarrow, opener, closer)
					if not rhsspans:
						return []
					rhsstart, rhsend = rhsspans[0]
					tailmatch = re.match(r'\s*;', afterarrow[rhsend:])
					if not tailmatch:
						return []
					fullend = lhsend + arrowmatch.end() + rhsend + tailmatch.end()
					return [s[:fullend]]
				def matchpipeblock(s):
					if not s.startswith('|'):
						return []
					instring = False
					for i in range(1, len(s)):
						ch = s[i]
						if ch == '\'':
							instring = not instring
						elif ch == '|' and not instring:
							return [s[:i + 1]]
					return []
				ks = matchtransition(line, '<', '>', '→')
				f = matchtransition(line, '(', ')', '→:')
				c = matchtransition(line, '⌊', '⌋', '→')
				s = matchpipeblock(line)
				p = matchtransition(line, '(', ')', '→:', requireafterarrow = r'\(\s*python\s*:')
				h = matchtransition(line, '[', ']', ':→', requireafterarrow = r'\[\s*(before|after)\s*:')
				def nonlambdafunc(string):
					nonlocal action_parts
					if not pycodeindex(string.strip()):
						raise Exception(f'Invalid command "{string.strip()}"')
					else:
						return pycodeindex(string.strip())
				if ks and len(ks) == 1:
					ks = ks[0].strip()[:-1]
					key_part = ks.split('→')[0].strip()
					action_parts = '\\n'.join(map(nonlambdafunc, ks.split('→')[1].strip()[:-1][1:].strip().split('↩')))
					if re.match(r'^<.+&.+>$', key_part):
						chord_keys = ['<' + k.strip() + '>' for k in key_part[1:-1].split('&')]
						for ck in chord_keys:
							wholenewwords.append(ck)
						chord_any_defined = True
						last_key = chord_keys[-1]
						expected_state = '+'.join(chord_keys[:-1])
						prefix_positions = {}
						for i in range(len(chord_keys) - 1):
							prefix_positions.setdefault(chord_keys[i], []).append(i)
						for ck, positions in prefix_positions.items():
							if ck == last_key:
								continue
							if re.match(r'^<(Control|Shift|Alt|Meta|Super)-', ck):
								for pos in sorted(positions):
									from_s = '+'.join(chord_keys[:pos]) if pos > 0 else None
									to_s = '+'.join(chord_keys[:pos + 1])
									mod_key_transitions.setdefault(ck, []).append((from_s, to_s))
							else:
								ck_inner = ck[1:-1]
								for pos in sorted(positions):
									from_s = '+'.join(chord_keys[:pos]) if pos > 0 else None
									to_s = '+'.join(chord_keys[:pos + 1])
									nonmod_transitions.append((from_s, ck_inner, to_s))
						last_key_inner = last_key[1:-1]
						last_key_is_mod = bool(re.match(r'^(Control|Shift|Alt|Meta|Super)-', last_key_inner))
						overlap_positions = sorted([i for i, k in enumerate(chord_keys[:-1]) if k == last_key], reverse = True)
						if last_key_is_mod:
							mod_key_completions.setdefault(last_key, []).append((expected_state, action_parts))
							for pos in overlap_positions:
								from_s = '+'.join(chord_keys[:pos]) if pos > 0 else None
								to_s = '+'.join(chord_keys[:pos + 1])
								mod_key_transitions.setdefault(last_key, []).append((from_s, to_s))
						else:
							nonmod_completions.append((expected_state, last_key_inner, action_parts))
							for pos in overlap_positions:
								from_s = '+'.join(chord_keys[:pos]) if pos > 0 else None
								to_s = '+'.join(chord_keys[:pos + 1])
								nonmod_transitions.append((from_s, last_key_inner, to_s))
					else:
						wholenewwords.append(key_part)
						simple_bindings_seen[key_part] = action_parts
						type_bind_cdt += f"for editor in all_editors: editor._own_type.bind('{key_part}', lambda event: pcexecaction(\"{action_parts}\") or 'break')" + '\n'
						cdt += f'root.bind(\'{key_part}\', lambda event: pcexecaction("{action_parts}"))' + '\n'
				elif p and len(p) == 1:
					p = p[0].strip()[:-1]
					func_name = p.split('→:')[0].strip()[:-1][1:].strip()
					to_do = p.split('→:')[1].strip()[:-1][1:].strip().split('↩')
					for i in range(len(to_do)):
						if not to_do[i].strip():
							continue
						if 'pycode:' in to_do[i]:
							def replacepycodeblocks(text):
								out = ''
								pos = 0
								while True:
									idx = text.find('pycode:', pos)
									if idx == -1:
										out += text[pos:]
										break
									out += text[pos:idx]
									bracematch = re.match(r'\s*', text[idx + len('pycode:'):])
									braceidx = idx + len('pycode:') + bracematch.end()
									if braceidx >= len(text) or text[braceidx] != '{':
										out += text[idx:braceidx + 1]
										pos = braceidx + 1
										continue
									spans = finddelimitedspans(text[braceidx:], '{', '}')
									if not spans:
										out += text[idx:]
										break
									spanstart, spanend = spans[0]
									inner = text[braceidx + spanstart + 1:braceidx + spanend - 1]
									indexedinner = pycodeindex(inner.strip())
									if not indexedinner:
										raise Exception(f'Invalid command "{inner.strip()}"')
									out += indexedinner
									pos = braceidx + spanend
								return out
							to_do[i] = replacepycodeblocks(to_do[i])
						to_do[i] = '    ' + re.sub(r'^\s*', lambda m: m.group(0).replace('\t', '    '), to_do[i]).rstrip()
					to_do = '\\n'.join(to_do)
					funcrest = func_name.split(':', 1)[1]
					funcrealname, _, funcparams = funcrest.partition(':')
					funcrealname = funcrealname.strip()
					funcparams = funcparams.strip()
					if funcparams:
						cdt += f'exec("def {funcrealname}({funcparams}):\\n{to_do}")\n'
					else:
						cdt += f'exec("def {funcrealname}():\\n{to_do}")\n'
					if not funcrealname in pycodecommands:
						pycodecommands.append(funcrealname)
						pythoncommands.append(funcrealname)
				elif f and len(f) == 1:
					f = f[0].strip()[:-1]
					func_name = f.split('→:')[0].strip()[:-1][1:].strip()
					to_do = f.split('→:')[1].strip()[:-1][1:].strip().split('↩')
					for i in range(len(to_do)):
						if not to_do[i].strip():
							continue
						oldtodo = to_do[i].strip()
						to_do[i] = pycodeindex(to_do[i].strip())
						if not to_do[i]:
							raise Exception(f'Invalid command "{oldtodo}"')
						to_do[i] = '    ' + re.sub(r'^\s*', lambda m: m.group(0).replace('\t', '    '), to_do[i]).rstrip()
					to_do = '\\n'.join(to_do)
					funcrealname, _, funcparams = func_name.partition(':')
					funcrealname = funcrealname.strip()
					funcparams = funcparams.strip()
					if funcparams:
						cdt += f'exec("def {funcrealname}({funcparams}):\\n{to_do}")\n'
					else:
						cdt += f'exec("def {funcrealname}():\\n{to_do}")\n'
					if not funcrealname in pycodecommands:
						pycodecommands.append(funcrealname)
						pythoncommands.append(funcrealname)
				elif c and len(c) == 1:
					c = c[0].strip()[:-1]
					cmd = c.split('→')[0].strip()[:-1][1:].strip()
					to_do = c.split('→')[1].strip()[:-1][1:].strip().split('↩')
					for i in range(len(to_do)):
						if to_do[i]:
							oldtodo = to_do[i].strip()
							to_do[i] = pycodeindex(to_do[i].strip())
							if not to_do[i]:
								raise Exception(f'Invalid command "{oldtodo}"')
						else:
							to_do[i] = ''
					to_do = '\n'.join(to_do)
					pcwrittencommands[cmd] = to_do
				elif h and len(h) == 1:
					h = h[0].strip()[:-1]
					hookdef = h.split(':→')[0].strip()[:-1][1:].strip()
					to_do = h.split(':→')[1].strip()[:-1][1:].strip().split('↩')
					for i in range(len(to_do)):
						if to_do[i]:
							oldtodo = to_do[i].strip()
							to_do[i] = pycodeindex(to_do[i].strip())
							if not to_do[i]:
								raise Exception(f'Invalid command "{oldtodo}"')
						else:
							to_do[i] = ''
					to_do = '\n'.join(to_do)
					when, _, event = hookdef.partition(':')
					when = when.strip()
					event = event.strip()
					if event.split(':', 1)[0] not in pchookevents:
						raise Exception(f'Invalid event \'{event}\'')
					(pcbeforehooks if when == 'before' else pcafterhooks).setdefault(event, []).append(to_do)
				elif s and len(s) == 1:
					s = s[0].strip()
					startupcdt += f'{'\n'.join(map(nonlambdafunc, s[1:-1].strip().split('↩')))}' + '\n'
				else:
					root.error('Error in PyCode', f'Invalid syntax in line:\n"{line}"')
			except Exception as error:
				error = str(error)
				root.error('Error in PyCode', f'Error in line "{line}":\n{error}')
	defaults_cdt_root = '''\
root.bind('<Alt-x>', lambda event: cmd())
root.bind('<Control-N>', lambda event: neweditor())
root.bind('<Control-O>', lambda event: neweditor(True))
root.bind('<Control-w>', lambda event: ext())
'''
	defaults_cdt_type_ = '''\
for editor in all_editors: editor._own_type.bind('<Control-a>', lambda event, editor = editor: editor.selall())
for editor in all_editors: editor._own_type.bind('<Control-n>', lambda event, editor = editor: editor.nw())
for editor in all_editors: editor._own_type.bind('<Control-o>', lambda event, editor = editor: editor.llld())
for editor in all_editors: editor._own_type.bind('<Control-c>', lambda event, editor = editor: editor.cp())
for editor in all_editors: editor._own_type.bind('<Control-v>', lambda event, editor = editor: editor.pst())
for editor in all_editors: editor._own_type.bind('<Control-x>', lambda event, editor = editor: editor.cut())
for editor in all_editors: editor._own_type.bind('<KeyRelease>', lambda event, editor = editor: editor.keypress())
for editor in all_editors: editor._own_type.bind('<BackSpace>', lambda event: show('delete text'))
for editor in all_editors: editor._own_type.bind('<Delete>', lambda event: show('delete text'))
for editor in all_editors: editor._own_type.bind('<Return>', lambda event, editor = editor: editor.indent())
for editor in all_editors: editor._own_type.bind('<Alt-l>', lambda event, editor = editor: editor.gl())
for editor in all_editors: editor._own_type.bind('<Control-p>', lambda event, editor = editor: editor.ptf())
for editor in all_editors: editor._own_type.bind('<Control-P>', lambda event, editor = editor: editor.ptb())
for editor in all_editors: editor._own_type.bind('<Control-f>', lambda event, editor = editor: editor.f())
for editor in all_editors: editor._own_type.bind('<Control-F>', lambda event, editor = editor: editor.fr())
for editor in all_editors: editor._own_type.bind('<Control-z>', lambda event, editor = editor: editor.undo())
for editor in all_editors: editor._own_type.bind('<Control-Z>', lambda event, editor = editor: editor.redo())
for editor in all_editors: editor._own_type.bind('<Control-s>', lambda event, editor = editor: editor.sssv())
for editor in all_editors: editor._own_type.bind('<Control-S>', lambda event, editor = editor: editor.ssv())
for editor in all_editors: editor._own_type.bind('<F5>', lambda event, editor = editor: editor.f5())
for editor in all_editors: editor._own_type.bind('<Control-space>', lambda event, editor = editor: editor.toggleselpoint())
for editor in all_editors: editor._own_type.bind('<KeyPress>', lambda event, editor = editor: editor.selkeypress(event))
'''
	cdt = defaults_cdt_root + cdt
	type_bind_cdt = defaults_cdt_type_ + type_bind_cdt
	for mod_key in set(list(mod_key_transitions) + list(mod_key_completions)):
		transitions = mod_key_transitions.get(mod_key, [])
		completions = mod_key_completions.get(mod_key, [])
		is_pure_completion = bool(completions) and not bool(transitions)
		if is_pure_completion and mod_key in simple_bindings_seen:
			else_t = f'(pcexecaction("{simple_bindings_seen[mod_key]}") or \'break\')'
			else_r = f'pcexecaction("{simple_bindings_seen[mod_key]}")'
		else:
			else_t = '_pychord_state.__setitem__(0, None)'
			else_r = '_pychord_state.__setitem__(0, None)'
		handler_t = else_t
		handler_r = else_r
		for from_s, to_s in reversed(transitions):
			check = f'_pychord_state[0] in (None,)' if from_s is None else f'_pychord_state[0] in (\'{from_s}\',)'
			handler_t = f"((_pychord_state.__setitem__(0, '{to_s}') or 'break') if {check} else {handler_t})"
			handler_r = f'(_pychord_state.__setitem__(0, \'{to_s}\') if {check} else {handler_r})'
		for es, ap in reversed(completions):
			handler_t = f"((pcexecaction(\"{ap}\") or _pychord_state.__setitem__(0, None) or 'break') if _pychord_state[0] in ('{es}',) else {handler_t})"
			handler_r = f'((pcexecaction("{ap}") or _pychord_state.__setitem__(0, None)) if _pychord_state[0] in (\'{es}\',) else {handler_r})'
		type_bind_cdt += f'for editor in all_editors: editor._own_type.bind(\'{mod_key}\', lambda event: {handler_t})\n'
		cdt += f'root.bind(\'{mod_key}\', lambda event: {handler_r})\n'
	if chord_any_defined:
		MODS = "('Control_L', 'Control_R', 'Shift_L', 'Shift_R', 'Alt_L', 'Alt_R', 'Meta_L', 'Meta_R', 'Super_L', 'Super_R', 'Caps_Lock', 'Num_Lock', 'Scroll_Lock', 'ISO_Level3_Shift')"
		kp_body = f'None if event.keysym in {MODS} else _pychord_state.__setitem__(0, None)'
		for from_s, ks_, to_s in reversed(nonmod_transitions):
			state_check = f'_pychord_state[0] in (None,)' if from_s is None else f'_pychord_state[0] in (\'{from_s}\',)'
			kp_body = f"((_pychord_state.__setitem__(0, '{to_s}') or 'break') if {state_check} and event.keysym in ('{ks_}',) and not (event.state & 12) else {kp_body})"
		for es, ks_, ap in reversed(nonmod_completions):
			kp_body = f"((pcexecaction(\"{ap}\") or _pychord_state.__setitem__(0, None) or 'break') if _pychord_state[0] in ('{es}',) and event.keysym in ('{ks_}',) and not (event.state & 12) else {kp_body})"
		chord_init = 'globals().setdefault(\'_pychord_state\', [None])\n'
		chord_init += f'root.bind(\'<KeyPress>\', lambda event: {kp_body})\n'
		type_bind_cdt = f'for editor in all_editors: editor._own_type.bind(\'<KeyPress>\', lambda event: {kp_body})\n' + type_bind_cdt
		cdt = chord_init + cdt
	pycode_keybindings_cdt = type_bind_cdt
	pcrun(cdt)
	pcrun(type_bind_cdt)
	return startupcdt
def edit(widget, editfrom):
	if editfrom == 'c=':
		widget.insert('insert', '→')
		return 'break'
	elif editfrom == 'ce':
		widget.insert('insert', '↩')
		return 'break'
	elif editfrom == 'cd':
		widget.insert('insert', '↓')
		return 'break'
	elif editfrom == 'fbl':
		widget.insert('insert', '⌊⌋')
		widget.mark_set('insert', 'insert-1c')
		return 'break'
	elif editfrom == 'fbr':
		widget.insert('insert', '⌋')
		return 'break'
	elif editfrom == '|':
		widget.insert('insert', '|')
		widget.mark_set('insert', 'insert-1c')
	elif editfrom == '<':
		widget.insert('insert', '>')
		widget.mark_set('insert', 'insert-1c')
	elif editfrom == ';':
		widget.insert('insert', ';\n')
		return 'break'
	elif editfrom == '(':
		widget.insert('insert', ')')
		widget.mark_set('insert', 'insert-1c')
	elif editfrom == '[':
		widget.insert('insert', ']')
		widget.mark_set('insert', 'insert-1c')
	elif editfrom == "'":
		widget.insert('insert', "'")
		widget.mark_set('insert', 'insert-1c')
	elif editfrom == '"':
		widget.insert('insert', '"')
		widget.mark_set('insert', 'insert-1c')
pchookevents = ['new-file-current-editor', 'new-file-new-editor', 'open-file-current-editor', 'open-file-new-editor', 'save-file', 'save-as-file', 'exit-pynotes', 'close-editor', 'switch-editor', 'run-code', 'mark-region', 'unmark-region', 'comment-region', 'uncomment-region', 'indent-region', 'unindent-region', 'open-mathgod', 'term-exec', 'alt-x-command', 'pycode-command', 'undo', 'redo', 'show-pynotes-source-code', 'open-terminal', 'open-preferences', 'next-page', 'previous-page', 'copy-text', 'paste-text', 'cut-text', 'fullscreen', 'un-fullscreen', 'maximize-window', 'unmaximize-window', 'minimize-window', 'clear-editor', 'open-pycode', 'change-hmode', 'switch-to-editor-tab', 'switch-to-python-shell-tab', 'switch-to-email-tab', 'resize-window']
def pc():
	global defs
	global wholenewwords
	pcrunhook('before', 'open-pycode')
	show('open pycode')
	for binded in wholenewwords:
		root.unbind(binded)
		for editor in all_editors:
			editor.type_.unbind(binded)
	wholenewwords.clear()
	pcwin = root.subwin()
	pcwin.title('PyCode - PyNotes')
	gcframe = pcwin.frame()
	buttonframe = pcwin.frame(master = gcframe, scrolled = True)
	buttonframe.pack(side = 'top', fill = 'y', expand = True)
	_bf_active = [False]
	pccmddonebutton = pcwin.button(master = gcframe, text = 'Done', command = lambda: [setcommand('Done'), gcframe.update()])
	gcframe.pack(side = 'left', fill = 'y', expand = True, padx = 10, pady = 10)
	pcwin.text(master = buttonframe, text = 'Define:').grid(column = 0)
	todefine = pcwin.stringvar()
	def define(todefine):
		def shortcutselected():
			shortcut.append(showkey.cget('text'))
		def keypressforshortcut(event):
			state = event.state
			key = event.keysym
			keycombination = []
			if state & 0x0001:
				keycombination.append('Shift')
			if state & 0x0004:
				keycombination.append('Control')
			if state & 0x0008:
				keycombination.append('Alt')
			keycombination.append(key)
			showkey.config(text = '+'.join(keycombination))
		def pyfunccodedone():
			code = pyfunccodeedit.get('1.0', 'end-1c')
			pyfunccodewin.destroy()
			codeedit.insert('insert', f'\n(python:{pyfuncname}) →: (\n{code.replace("\n", " ↩\n")}\n);')
			codeedit.focus()
		if todefine == 'Function':
			funcname = pcwin.askstring('Name', 'Name of the Function:')
			if not funcname:
				return
			prompttext = pcwin.text(master = buttonframe, text = 'Commands:')
			prompttext.grid(column = 0, row = 0)
			row = 0
			for button in buttons:
				row += 1
				button.grid(column = 0, row = row, sticky = 'ew', pady = 2)
			pccmddonebutton.pack(side = 'bottom', fill = 'x')
			_bf_active[0] = True
			while not commanddone:
				pcwin.update()
			codeedit.insert('insert', f'\n({funcname}) →: (\n{" ↩\n".join(commandtodo)}\n);\n')
			commandtodo.clear()
			commanddone.clear()
			prompttext.grid_forget()
		elif todefine == 'Python Function':
			pyfuncname = pcwin.askstring('Name', 'Name of the Python Function:')
			if not pyfuncname:
				return
			pyfunccodewin = root.subwin()
			pyfunccodewin.title('PyCode Python Function Code')
			pyfunccodeedit = pyfunccodewin.textbox(font = (monospace, 11))
			pyfunccodeedit.grid(column = 0, row = 0, sticky = 'nsew')
			pyfunccodeedit.focus()
			pyfunccodewin.button(text = 'Done', command = pyfunccodedone).grid(column = 0, row = 1, sticky = 'ew')
			pyfunccodewin.update()
			pyfunccodewin.sizablefalse()
			pyfunccodewin.wait_window(pyfunccodewin)
		elif todefine == 'Variable':
			varname = pcwin.askstring('Name', 'Name of the Variable:')
			if not varname:
				return
			value = pcwin.askstring('Value', 'Value of the Variable:')
			if not value:
				return
			codeedit.insert('insert', f'\n[{varname}] :→ [{value}];')
		elif todefine == 'Startup Code':
			prompttext = pcwin.text(master = buttonframe, text = 'Commands:')
			prompttext.grid(column = 0)
			row = 0
			for button in buttons:
				row += 1
				button.grid(column = 0, row = row, sticky = 'ew')
			pccmddonebutton.pack(side = 'bottom', fill = 'x')
			_bf_active[0] = True
			while not commanddone:
				pcwin.update()
			codeedit.insert('insert', f'\n|\n{" ↩\n".join(commandtodo)}\n|;\n')
			prompttext.grid_forget()
			commandtodo.clear()
			commanddone.clear()
		elif todefine == 'Keyboard Shortcut':
			keygetting = root.subwin()
			keygetting.title('Keyboard Shortcut')
			style = keygetting.style()
			style.configure('ShowStyle.TLabel', background = 'white', padding = (7, 7, 7, 7), relief = 'sunken')
			keygetting.text(text = 'Press a key:').grid(padx = 10, pady = 10, column = 0, row = 0)
			showkey = keygetting.text(text = '', style = 'ShowStyle.TLabel')
			showkey.grid(column = 0, row = 1, padx = 10, pady = 10)
			keygetting.bind('<KeyPress>', lambda event: [keygetting.sizabletrue(), keypressforshortcut(event), keygetting.update(), keygetting.sizablefalse()])
			keygetting.protocol('WM_DELETE_WINDOW', 'break')
			keygetting.button(text = 'Done', command = shortcutselected).grid(column = 0, row = 2, padx = 10, pady = 10)
			shortcut = []
			keygetting.update()
			keygetting.sizablefalse()
			while not shortcut:
				keygetting.update()
			keygetting.destroy()
			shortcut = ''.join(shortcut).replace('+', '-')
			prompttext = pcwin.text(master = buttonframe, text = 'Commands:')
			prompttext.grid(column = 0)
			row = 0
			for button in buttons:
				row += 1
				button.grid(column = 0, row = row, sticky = 'ew')
			pccmddonebutton.pack(side = 'bottom', fill = 'x')
			_bf_active[0] = True
			while not commanddone:
				pcwin.update()
			codeedit.insert('insert', f'\n<{shortcut}> → <\n{" ↩\n".join(commandtodo)}\n>;\n')
			prompttext.grid_forget()
			commandtodo.clear()
			commanddone.clear()
		elif todefine == 'Alt-X Command':
			cmdname = pcwin.askstring('Name', 'Name of the Alt-X Command:')
			if not cmdname:
				return
			prompttext = pcwin.text(master = buttonframe, text = 'Commands:')
			prompttext.grid(column = 0, row = 0)
			row = 0
			for button in buttons:
				row += 1
				button.grid(column = 0, row = row, sticky = 'ew')
			pccmddonebutton.pack(side = 'bottom', fill = 'x')
			_bf_active[0] = True
			while not commanddone:
				pcwin.update()
			codeedit.insert('insert', f'\n⌊{cmdname}⌋ →: ⌊\n{" ↩\n".join(commandtodo)}\n⌋;\n')
			commandtodo.clear()
			commanddone.clear()
			prompttext.grid_forget()
		elif todefine == 'Event Hook':
			hookwin = root.subwin()
			hookwin.title('PyCode Event Hook Definition')
			hookwin.text(text = 'When:').grid(column = 0, row = 0, padx = 10, pady = 10, sticky = 'e')
			whenvar = hookwin.stringvar()
			hookwin.dropdown(master = hookwin, stringvar = whenvar, showdefault = 'before', options = ['before', 'after']).grid(column = 1, row = 0, padx = 10, pady = 10, sticky = 'ew')
			hookwin.text(text = 'Event:').grid(column = 0, row = 1, padx = 10, pady = 10, sticky = 'e')
			eventtype = hookwin.droptype(master = hookwin, options = pchookevents, state = 'readonly', command = lambda: None)
			eventtype.set(pchookevents[0])
			eventtype.grid(column = 1, row = 1, padx = 10, pady = 10, sticky = 'ew')
			hookdone = []
			hookwin.button(text = 'Done', command = lambda: [hookdone.append((whenvar.get(), eventtype.get())), hookwin.destroy()]).grid(column = 1, row = 2, columnspan = 2, padx = 10, pady = 10, sticky = 'ew')
			hookwin.update()
			hookwin.sizablefalse()
			while hookwin.winfo_exists():
				hookwin.update()
			if not hookdone:
				return
			when, event = hookdone[0]
			if event in ('alt-x-command', 'pycode-command'):
				subcmd = pcwin.askstring('Command Name', f'{"Alt-X" if event == "alt-x-command" else "PyCode"} command (leave blank for all):')
				if subcmd:
					event = f'{event}:{subcmd.strip()}'
			prompttext = pcwin.text(master = buttonframe, text = 'Commands:')
			prompttext.grid(column = 0, row = 0)
			row = 0
			for button in buttons:
				row += 1
				button.grid(column = 0, row = row, sticky = 'ew')
			pccmddonebutton.pack(side = 'bottom', fill = 'x')
			_bf_active[0] = True
			while not commanddone:
				pcwin.update()
			codeedit.insert('insert', f'\n[{when}:{event}] :→ [\n{" ↩\n".join(commandtodo)}\n];\n')
			commandtodo.clear()
			commanddone.clear()
			prompttext.grid_forget()
		optionsdropdown.config(state = 'normal')
	optionsdropdown = pcwin.dropdown(stringvar = todefine, showdefault = 'Function', options = ['Function', 'Python Function', 'Variable', 'Startup Code', 'Keyboard Shortcut', 'Alt-X Command', 'Event Hook'], master = buttonframe, command = lambda inpt: [optionsdropdown.config(state = 'disabled'), define(inpt), optionsdropdown.config(state = 'normal')])
	optionsdropdown.grid(column = 0)
	commands = pycodecommands
	buttons = []
	commandtodo = []
	commanddone = []
	def setcommand(command):
		if command == 'Done':
			hidebuttons()
			commanddone.append('True')
		else:
			commandtodo.append(command)
	def hidebuttons():
		for button in buttons:
			button.grid_forget()
		pccmddonebutton.pack_forget()
		_bf_active[0] = False
	for command in commands:
		button = pcwin.button(master = buttonframe, text = command, command = lambda command = command: setcommand(command))
		buttons.append(button)
	done = pcwin.button(text = 'Done', command = lambda: [pcdone(codeedit.get('1.0', 'end-1c')), pcwin.destroy()])
	done.pack(side = 'bottom', fill = 'x', expand = True)
	scrolly = pcwin.scroll()
	scrolly.pack(side = 'right', fill = 'y')
	codeedit = pcwin.textbox(yscrollcommand = scrolly.set, font = monospace, wrap = 'word')
	codeedit.pack(side = 'left', fill = 'both')
	codeedit.focus_set()
	codeedit.bind('<Control-equal>', lambda event: edit(codeedit, 'c='))
	codeedit.bind('<Control-Return>', lambda event: edit(codeedit, 'ce'))
	codeedit.bind('<Control-Down>', lambda event: edit(codeedit, 'cd'))
	codeedit.bind('<less>', lambda event: edit(codeedit, '<'))
	codeedit.bind('<semicolon>', lambda event: edit(codeedit, ';'))
	codeedit.bind('(', lambda event: edit(codeedit, '('))
	codeedit.bind('[', lambda event: edit(codeedit, '['))
	codeedit.bind('|', lambda event: edit(codeedit, '|'))
	codeedit.bind('<Control-bracketleft>', lambda event: edit(codeedit, 'fbl'))
	codeedit.bind('<Control-bracketright>', lambda event: edit(codeedit, 'fbr'))
	codeedit.bind('<quoteright>', lambda event: edit(codeedit, "'"))
	codeedit.bind('<quotedbl>', lambda event: edit(codeedit, '"'))
	scrolly.config(command = codeedit.yview)
	try:
		open(f'{homedir}/.pynotes', 'r', encoding = 'utf-8')
	except Exception:
		open(f'{homedir}/.pynotes', 'w+', encoding = 'utf-8')
	codeedit.insert('end', open(f'{homedir}/.pynotes', 'r', encoding = 'utf-8').read())
	pcwin.style(root.gettheme())
	pcwin.update()
	pcwin.sizablefalse()
	pcrunhook('after', 'open-pycode')
def helppycode():
	show('open pycode help')
	hpwin = root.subwin()
	hpwin.title('Help with PyCode')
	hptabs = hpwin.tabs()
	hptabs.pack(side = 'top', fill = 'both', padx = 10, pady = 10)
	bt = hpwin.frame()
	hptabs.add(bt, text = 'Basics')
	ct = hpwin.frame()
	hptabs.add(ct, text = 'Commands')
	gt = hpwin.frame()
	hptabs.add(gt, text = 'Graphical Coding')
	kst = hpwin.frame()
	hptabs.add(kst, text = 'Keyboard Shortcuts')
	vt = hpwin.frame()
	hptabs.add(vt, text = 'Variables')
	ft = hpwin.frame()
	hptabs.add(ft, text = 'Functions')
	st = hpwin.frame()
	hptabs.add(st, text = 'Startup Code')
	act = hpwin.frame()
	hptabs.add(act, text = 'Alt-X Command Definition')
	ht = hpwin.frame()
	hptabs.add(ht, text = 'Event Hooks')
	lct = hpwin.frame()
	hptabs.add(lct, text = 'Loops and Conditions')
	code = hpwin.style()
	code.configure('CodeStyle.TLabel', background = 'white', padding = (7, 7, 7, 7), relief = 'sunken')
	hpwin.text(master = bt, text = 'Syntax -\nAll Keyboard Shortcuts, Event Hooks, Functions, and Startup Code should end with a semicolon \';\'.\nInputs to a command must be given with one and only one space between\nthe command and the input.\nIf the input to a command is a string, it can only be inside single quotes \'input\'.\nSpaces do not matter between full commands and between brackets.\nNewlines do not matter between full commands and between brackets.\nFor example, the code').grid(column = 0, row = 0, padx = 10, pady = 10, sticky = 'w')
	hpwin.text(master = bt, text = '(something) →: (say \'hello\' ↩ say \'this is a test\');', style = 'CodeStyle.TLabel').grid(column = 0, row = 1, padx = 10, pady = 10, sticky = 'w')
	hpwin.text(master = bt, text = 'is the same as').grid(column = 0, row = 2, padx = 10, pady = 10, sticky = 'w')
	hpwin.text(master = bt, text = '(\nsomething\n)\n→:\n(\nsay \'hello\'\n↩\nsay \'this is a test\'\n);', style = 'CodeStyle.TLabel').grid(column = 0, row = 3, padx = 10, pady = 10, sticky = 'w')
	hpwin.text(master = bt, text = "PyCode uses some symbols which are not on the keyboard.\nTo type '→', press 'Control + =' on your keyboard.\nTo type '↩', press 'Control + Enter'.\nTo type '↓', press 'Control + Down Arrow'.\nTo type '⌊', press 'Control + ['.\nTo type '⌋', press 'Control + ]'.\nThe functions and uses of these symbols are explained later in the Help.\nPyCode also has a simple autocomplete to help you type code faster.\nTyping any of these characters will make PyCode automatically close them with the opposite,\nand put your cursor in the middle: '|/|', '</>', '(/)', '[/]', \"'/'\", '\"/\"'.\nPressing ';' will automatically put your cursor on a new line after the semicolon.\nPyCode runs in the same global space as the rest of PyNotes.\nSo, you can access PyNotes variables directly, like 'active' for the currently active editor.").grid(column = 0, row = 4, padx = 10, pady = 10, sticky = 'w')
	hpwin.text(master = ct, text = 'These are all the commands in PyCode which you can use to make or change Functions, Keyboard Shortcuts,\nStartup Code, and Alt-X commands:').grid(column = 0, row = 0, padx = 10, pady = 10, sticky = 'w')
	pccmdlistcontainer = hpwin.textbox(master = ct, scrolled = True)
	pccmdlist = pccmdlistcontainer.text
	l1 = pccmdlist.index('end-1c')
	pccmdlist.insert('end', 'PyNotes\' Commands Help\n\n')
	r1 = pccmdlist.index('end-1c')
	pccmdlist.tag_add('bigstuff', l1, r1)
	pccmdlist.insert('end', "aboutpynotes - Opens the PyNotes About.\n\nask 'prompt' - Asks an input from the user and returns the answer.\n\nbalanceeditors 'all/horizontal/vertical' - Balance the horizontal/vertical/both editors to make them equal size.`\n\ncleareditor - Clears the active editor.\n\ncloseeditor n = current - Closes the nth editor if n is given, defaults to the currently active editor.\n\ncmdrun 'command' - Runs the given Alt-X command.\n\ncolor name, ... - Makes a tag named 'name' with the options .... Same options as tkinter textbox.tag_config. Can be used later with tag name, a, b.\n\ncommentregion 'a', 'b' - Coments the text from a given line number 'a' to a given line number 'b' in the active editor if the HMode is Python / LaTeX / HTML / Markdown.\n\ncommentselection - Comments the selected code if the HMode is Python / LaTeX / HTML / Markdown.\n\ncopy - Copies the selected text in the active editor.\n\ncopytext 'text' - Copies the given input to the clipboard\n\ncut - Cuts the selected text in the active editor.\n\ndelete 'a', 'b' - Deletes the text from a given tkinter-style index 'a' to a given tkinter-style index 'b' in the active editor.\n\ndictate - Opens the speech-to-text, lets you dictate text to the active editor.\n\ndownloadplugins - Automatically opens a link to the PyNotes GitHub Plugin page to let you download plugins in your default browser.\n\nfindreplace - Opens Find & Replace.\n\nfindtext - Opens Find.\n\nfullscreen - Makes the PyNotes window fullscreen.\n\nget 'a', 'b' - Gets the text in the active editor from a given tkinter style index 'a' to a given tkinter-style index 'b'.\n\ngetselection - Gets the range of the selected text in the active editor and returns it.\n\ngotoline n = None - Moves the cursor to the given line number n if given, otherwise prompts the user for a line number and goes to it.\n\nhmode 'py/la/html/md/em/norm' - Switches the HMode (PyNotes mode) to Python / LaTeX / HTML / Markdown / Email / Normal.\n\nindentregion 'a', 'b' - Indents the text from a given line number 'a' to a given line number 'b' in the active editor.\n\nindentselection - Indents the selected region in the active editor.\n\ninsert 'index', 'text' - Inserts the text at a given tkinter-style index in the active editor.\n\nkillquit - Forcibly kills PyNotes without saving files or cleaning up.\n\nmark 'a', 'b' - Visually marks the text between a tkinter-style index 'a' and a tkinter-style index 'b' in the active editor.\n\nmarkselection - Visually marks the selected text in the active editor.\n\nmathgod - Opens MathGod.\n\nmaximize - Maximizes the PyNotes window.\n\nminimize - Minimizes the PyNotes window.\n\nmovecursor 'index' - Moves the cursor to a given tkinter-style index in the active editor.\n\nneweditor file = None, orient = 'horizontal' - Opens a new editor loading file if given and being horizontal or vertical depending on orient (default 'horizontal').\n\nnewfile - Opens a new file in the currently active editor.\n\nopenfile - Opens a file picker to open a file in the currently active editor.\n\nopenfilenewedit orient = 'horizontal' - Opens a new editor with orientation orient (default horizontal) loading the file from a filedialog that is shown.\n\nopenhelp 'commands/email/pycode/mathgod/plugins' - Opens the Help about the given feature.\n\nopenplugindir - Opens the plugins directory in your file manager.\n\nopenpycode - Opens PyCode.\n\nopenterm command = None, title = 'Terminal', endmessage = None, blocking = False - Opens the PyNotes terminal with a given command list (example [command, input1, input2]), /bin/bash or powershell.exe if not specified. Set optional title (the title of the terminal window) and endmessage (the message shown at the end after the process stops, terminal window closes immediately if no endmessage is set). If blocking is set to True (default False), it pauses execution till the process finishes.\n\npageback - Goes to the previous page in the active editor.\n\npageforw - Goes to the next page in the active editor.\n\npass - Do nothing.\n\npaste - Pastes your clipboard in the active editor.\n\npreferences - Opens the PyNotes preferences.\n\nprompt text, autocompletefunc = None, defaultinput = None - Prompts the user with text in the Alt-X command box and returns input. Calls the function inside the string autocomplete with the currently typed text if it is a string, otherwise uses the fixed list/tuple if given in it when Tab is pressed. If defaultinput is given, starts the prompt with it.\n\npynotessourcecode - Opens the PyNotes source code in a new editor.\n\npyshell - Opens the Python Shell if you are in Python HMode.\n\npythongoendof 'f/fun/func/function/c/class/name' - If the HMode is Python, jumps to the end of the current function/class the cursor is in if given 'f/fun/func/function/c/class', otherwise jumps to the end of the given function/class name if it exists in the active editor.\n\npythongostartof 'f/fun/func/function/c/class/name' - If the HMode is Python, jumps to the start of the current function/class the cursor is in if given 'f/fun/func/function/c/class', otherwise jumps to the start of the given function/class name if it exists in the active editor.\n\npythongovardef 'name' - If the HMode is Python, jumps to the definition of the given variable name relative to the current scope in the active editor.\n\nquit - Cleanly closes PyNotes.\n\nredo - Redos the last undo in the active editor.\n\nrepeatxcommand 'command', n - Repeats the given Alt-X command n times.\n\nremoveselectionpoint - Removes the selection point if set.\n\nreturn valu' - Returns the given value from a function.\n\nruncode - Runs the code in the active editor if the HMode is Python / LaTeX / HTML.\n\nsaveasfile - Save the text in the active editor to another filename.\n\nsavefile - Saves the file in the active editor.\n\nsay 'input' - Opens a graphical messagebox showing the given input. You can also use a variable here.\n\nselall - Selects all the text in the active editor.\n\nselect 'a', 'b' - Selects the text from a given tkinter-style index 'a' to a given tkinter-style index 'b' in the active editor.\n\nsetselectionpoint index = None - Sets the selection point at the index if given, otherwise cursor position.\n\nsetvar 'var', 'val' - Makes a variable with a given name 'var' and a given value 'val'.\n\nsetwintitle 'title' - Sets the title of the PyNotes window to a given string.\n\nshow 'text' - Shows the given text in the Alt-X command box.\n\nspeaktext - Speaks the selected text in the active editor.\n\nspliteditor n = active, orient = 'horizontal' - Splits the nth editor (default active) horizontally or vertically depending on orient (default horizontal).\n\nswitcheditor n = current + 1 - Switches focus to the nth editor if given n, otherwise cycle editors.\n\nswitcheditortab - Switches to the editor tab.\n\nswitchemailtab - Switches to the Email tab if the HMode is Email.\n\ntag ... - Uses a tag previously set with color name, ... . Same options as tkinter textbox.tag_add.\n\ntermexec 'command' - Executes the given command in a terminal and shows the output in the Alt-X command box.\n\ntkindex 'toindex', (optional: 'line') - Indexes the given tkinter-style input in the active editor and returns the output. If the optional 'line' input is also given, it returns only the linenumber as a string.\n\ntoggleselectionpoint - Sets the selection point at the cursor if not set, otherwise removes it.\n\ntypecommand - Lets you type an Alt-X command.\n\nuncommentregion a, b - Uncomments the text from a given line number a to another given line number b in the active editor if the HMode is Python / LaTeX / HTML / Markdown.\n\nuncommentselection - Uncomments the selected text in the active editor if the HMode is Python / LaTeX / HTML / Markdown.\n\nundo - Undoes the last edit in the active editor.\n\nunfullscreen - Makes PyNotes windowed mode from fullscreen.\n\nunindentregion a, b - Unindents the text from a given line number a to another given line number b in the active editor if the HMode is Python / LaTeX / HTML / Markdown.\n\nunindentselection - Unindents the selected text in the active editor.\n\nunmark 'a', 'b' - Unmark the visually marked text in the active editor from a tkinter-style index 'a' to a tkinter-style index 'b'.\n\nunmarkall - Unmarks all the visually marked text in the active editor.\n\nunmaximize - Unmaximizes the main window.\n\nunsetwintitle - Sets the window title back to normal after the command 'setwintitle'\n\nuntag ... - Untags a tag previouslyl set with tag .... Same options as tkinter textbox.tag_remove.\n\nwait n - Freezes PyNotes for n seconds.\n\nwrite 'text', n - Writes the given text repeated n times in the active editor.")
	l2 = pccmdlist.index('end-1c')
	if plgnspccmdhelp:
		pccmdlist.insert('end', '\n\nPlugins\' Commands Help')
	r2 = pccmdlist.index('end-1c') + '+2c'
	pccmdlist.insert('end-1c', plgnspccmdhelp)
	pccmdlist.tag_add('bigstuff', l2, r2)
	pccmdlist.tag_config('bigstuff', font = (monospace, 15, 'bold'))
	pccmdlist.config(state = 'disabled')
	pccmdlistcontainer.grid(column = 0, row = 1, padx = 10, pady = 10, sticky = 'nsew')
	hpwin.text(master = ct, text = 'By default, a command will take all the text that comes after it after a space as it\'s input.\nTo avoid that, you can give the input inside () brackets.\nThen, the command will only take the text after itself which is inside the brackets as input.').grid(column = 0, row = 2, padx = 10, pady = 10, sticky = 'w')
	ct.grid_columnconfigure(0, weight = 1)
	hpwin.text(master = gt, text = 'There is a dropdown menu in the top left corner, using which you can code graphically.\nWhenever you click something in it, it will ask for inputs.\nIt will also show a list of all the commands on the side if it needs it.\nThen, you can click any commands you want, and it will put them in the\nFunction / Keyboard Shortcut / Startup Code in order.\nIt will not ask for the inputs of commands that take inputs,\nyou will have to put those in the code yourself.').grid(column = 0, row = 0, padx = 10, pady = 10, sticky = 'w')
	root.image(master = gt, image = f'{rootdir}/Images/PYCODE1.png', imsize = (2, 2)).grid(column = 0, row = 1, padx = 10, pady = 10, sticky = 'w')
	root.image(master = gt, image = f'{rootdir}/Images/PYCODE2.png', imsize = (2, 2)).grid(column = 1, row = 1, padx = 10, pady = 10, sticky = 'e')
	hpwin.text(master = kst, text = 'You can bind or rebind Keyboard Shortcuts to any of the PyCode commands.\nTo put more than one command in a Keyboard Shortcut, separate them with \'↩\'.\nIf you want to make a keyboard shortcut where you have to press and hold 2 keys,\n(eg. Control or Alt + something else), you will have to put a dash between them.\nControl and Alt keys, when used, can never be after a normal letter.\nYou can never repeat Control or Alt keys in the same keyboard shortcut.\nYou can bind keys to any commands, or a function made by you.\nThis uses the same syntax as tkinter\'s bindings.\nIf you do not know how to bind a key to something, you can use the graphical coding.\nThere, PyCode will automatically detect which keys you press and put them in the code.\nYou can also bind chord keys like Control-x Control-s by separating the keys inside the first \'<>\' with \'&\'.\nYou cannot bind chord keys using the graphical programming till now.\nExamples:').grid(column = 0, row = 0, padx = 10, pady = 10, sticky = 'w')
	hpwin.text(master = kst, text = '<Control-q> → <close>;', style = 'CodeStyle.TLabel').grid(column = 0, row = 1, padx = 10, pady = 10, sticky = 'w')
	hpwin.text(master = kst, text = '<Control-x & Control-s> → <savefile>;', style = 'CodeStyle.TLabel').grid(column = 0, row = 2, padx = 10, pady = 10, sticky = 'w')
	hpwin.text(master = kst, text = '<Control-t> → <say \'Hello!\' ↩ say \'PyNotes is the best!\'>;', style = 'CodeStyle.TLabel').grid(column = 0, row = 3, padx = 10, pady = 10, sticky = 'w')
	hpwin.text(master = vt, text = 'Variables can be defined using the PyCode command \'setvar\'.\nThis can be used like a normal PyCode command.\nThe syntax is: setvar \'varname\', value.\nFor example, here is how to make a variable named \'something\' with the value \'something else\' on startup:').grid(column = 0, row = 0, padx = 10, pady = 10, sticky = 'w')
	hpwin.text(master = vt, text = '|setvar \'something\', \'something else\'|;', style = 'CodeStyle.TLabel').grid(column = 0, row = 1, padx = 10, pady = 10, sticky = 'w')
	hpwin.text(master = vt, text = 'This can then be used in Keyboard Shortcuts and Functions like this:').grid(column = 0, row = 2, padx = 10, pady = 10, sticky = 'w')
	hpwin.text(master = vt, text = '<Control-q> → <say something>;', style = 'CodeStyle.TLabel').grid(column = 0, row = 3, padx = 10, pady = 10, sticky = 'w')
	hpwin.text(master = ft, text = 'The syntax to define a function is:').grid(column = 0, row = 0, padx = 10, pady = 10, sticky = 'w')
	hpwin.text(master = ft, text = '(funcname:args) →: (commands);', style = 'CodeStyle.TLabel').grid(column = 0, row = 1, padx = 10, pady = 10, sticky = 'w')
	hpwin.text(master = ft, text = 'The input definition syntax is exactly like Python\'s function inputs.\nThe commands inside the function are separated by a \'↩\'. For example, here is how to make a function named \'something\'\nwhich clears the editor and writes any given text 5 times\nwith a default value of \'text\':').grid(column = 0, row = 2, padx = 10, pady = 10, sticky = 'w')
	hpwin.text(master = ft, text = '(something:text = \'text\') →: (cleareditor ↩ write text, 5);', style = 'CodeStyle.TLabel').grid(column = 0, row = 3, padx = 10, pady = 10, sticky = 'w')
	hpwin.text(master = ft, text = 'This can then be used in other Functions, Keyboard Shortcuts, Startup Code, and Alt-X commands like a normal PyCode command.').grid(column = 0, row = 4, padx = 10, pady = 10, sticky = 'w')
	hpwin.text(master = ft, text = 'If you want to make a more complex function that cannot be made with normal PyCode commands,\nyou can make a Python Function in PyCode.\nThe syntax is:').grid(column = 0, row = 5, padx = 10, pady = 10, sticky = 'w')
	hpwin.text(master = ft, text = '(python:funcname:args) → (python code);', style = 'CodeStyle.TLabel').grid(column = 0, row = 6, padx = 10, pady = 10, sticky = 'w')
	hpwin.text(master = ft, text = 'The input definition syntax is exactly the same as normal PyCode functions,\nand the inputs also work exactly the same way.\nThe lines of the Python code are separated by a \'↩\', not newlines.\nAlso remember to put the \'python:\' prefix before the name of the function.\nTo use PyCode commands in a Python function, use the prefix \'pycode:\' before the command, and put the command in curly brackets.\nThere cannot be any spaces between the \'pycode\' and the semicolon.\nPyCode commands used in a Python function should maintain proper indentation in the Python code.\nFor example, here is how to make a Python function named \'something\' that asks for 1+1 and shows \'correct\' or \'wrong\' for the answer in the Alt-X command box:').grid(column = 0, row = 7, padx = 10, pady = 10, sticky = 'w')
	hpwin.text(master = ft, text = "(python:something) →: (\nuseranswer = int(root.askstring('Question', 'What is 1+1?')) ↩\nif useranswer == 2: ↩\n    pycode:{show 'correct'} ↩\nelse: ↩\n    pycode:{show 'wrong'}\n);", style = 'CodeStyle.TLabel').grid(column = 0, row = 8, padx = 10, pady = 10, sticky = 'w')
	hpwin.text(master = st, text = 'Startup Code runs automatically every time PyNotes starts.\nThis can be used to execute some commands everytime on startup or configure PyNotes in some way.\nEverything that is inside a \'| |\' is executed as startup code.\nTo run multiple commands on startup, you can use a Function,\nhave multiple \'| |\'s, or separate the commands inside one\n\'| |\' with \'↩\'.\nFor example, these are all the ways you can make PyNotes start with an empty editor instead of the Zen of Python in Python HMode:').grid(column = 0, row = 0, padx = 10, pady = 10, sticky = 'w')
	hpwin.text(master = st, text = '(startup) →: (newfile ↩ hmode \'py\');\n|startup|;', style = 'CodeStyle.TLabel').grid(column = 0, row = 1, padx = 10, pady = 10, sticky = 'w')
	hpwin.text(master = st, text = '|newfile|;\n|hmode \'py\'|;', style = 'CodeStyle.TLabel').grid(column = 0, row = 2, padx = 10, pady = 10, sticky = 'w')
	hpwin.text(master = st, text = '|newfile ↩ hmode \'py\'|;', style = 'CodeStyle.TLabel').grid(column = 0, row = 3, padx = 10, pady = 10, sticky = 'w')
	hpwin.text(master = act, text = 'You can make or change Alt-X commands in PyCode.\nPyCode commands inside the Alt-X command definition are separated by a \'↩\'. The syntax is:').grid(column = 0, row = 0, padx = 10, pady = 10, sticky = 'w')
	hpwin.text(master = act, text = '⌊cmdname⌋ → ⌊commands⌋;', style = 'CodeStyle.TLabel').grid(column = 0, row = 1, padx = 10, pady = 10, sticky = 'w')
	hpwin.text(master = act, text = 'Any input given from the Alt-X command will be saved to the variable \'commandinput\'.\nYou can then use it in PyCode commands. For example, here is how to make an Alt-X command named \'tktemplate\' which writes code in the editor that\nopens a window using easytk with the title and text \'PyCode Easytk Window Template\':').grid(column = 0, row = 2, padx = 10, pady = 10, sticky = 'w')
	hpwin.text(master = act, text =\
r'''
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
''', style = 'CodeStyle.TLabel').grid(column = 0, row = 3, padx = 10, pady = 10, sticky = 'w')
	hpwin.text(master = ht, text = 'You can make event hooks to execute some code before or after the event runs.\nThe syntax is:').grid(column = 0, row = 0, padx = 10, pady = 10, sticky = 'w')
	hpwin.text(master = ht, text = '[before/after:event] :→ [pycode];', style = 'CodeStyle.TLabel').grid(column = 0, row = 1, padx = 10, pady = 10, sticky = 'w')
	hpwin.text(master = ht, text = 'Commands should be separated with a \'↩\'.\nThese are all the events you can hook into:').grid(column = 0, row = 2, padx = 10, pady = 10, sticky = 'w')
	pceventhooklistcontainer = hpwin.textbox(master = ht, scrolled = True)
	pceventhooklist = pceventhooklistcontainer.text
	pceventhooklist.insert('end', 'new-file-current-editor\n\nnew-file-new-editor\n\nopen-file-current-editor\n\nopen-file-new-editor\n\nsave-file\n\nsave-as-file\n\nexit-pynotes\n\nclose-editor\n\nswitch-editor\n\nrun-code\n\nmark-region\n\nunmark-region\n\ncomment-region\n\nuncomment-region\n\nindent-region\n\nunindent-region\n\nopen-mathgod\n\nterm-exec\n\nalt-x-command:{command}\n\npycode-command:{command}\n\nundo\n\nredo\n\nshow-pynotes-source-code\n\nopen-terminal\n\nopen-preferences\n\nnext-page\n\nprevious-page\n\ncopy-text\n\npaste-text\n\ncut-text\n\nfullscreen\n\nun-fullscreen\n\nmaximize-window\n\nunmaximize-window\n\nminimize-window\n\nclear-editor\n\nopen-pycode\n\nchange-hmode\n\nswitch-to-editor-tab\n\nswitch-to-python-shell-tab\n\nswitch-to-email-tab\n\nresize-window')
	pceventhooklist.config(state = 'disabled')
	pceventhooklistcontainer.grid(column = 0, row = 3, padx = 10, pady = 10, sticky = 'nsew')
	hpwin.text(master = ht, text = 'The events \'open-file-current-editor\' (filename, or None if cancelled), \'open-file-new-editor\' (filename, or None if cancelled),\n\'save-as-file\' (filename, or None if cancelled), \'switch-editor\' (new editor number),\'*-region\' (tuple (a, b) containing the incides of the region), \'term-exec\' (command), \'open-terminal\' (command),\nalt-x-command (command input),pycode-command (command input), \'change-hmode\' (new HMode), \'copy-text\' (selected text),\n\'cut-text\' (selected text), \'paste-text\' (pasted text) will all set a variable \'commandinput\' for the code to run which contains\nthe previously shown possible inputs. For events involving a file dialog, the \'before\' hook runs after the dialog closes (with commandinput\nset to None if the dialog was cancelled), but the \'after\' hook only runs if the dialog was not cancelled.').grid(column = 0, row = 4, padx = 10, pady = 10, sticky = 'w')
	hpwin.text(master = ht, text = 'Example:').grid(column = 0, row = 5, padx = 10, pady = 10, sticky = 'w')
	hpwin.text(master = ht, text = '[after:new-file-current-editor] :→ [hmode \'py\'];\n[after:new-file-new-editor] :→ [hmode \'py\'];', style = 'CodeStyle.TLabel').grid(column = 0, row = 6, padx = 10, pady = 10, sticky = 'w')
	hpwin.text(master = lct, text = 'The syntax to make conditions in PyCode is:').grid(column = 0, row = 0, padx = 10, pady = 10, sticky = 'w')
	hpwin.text(master = lct, text = 'if (condition) {code} elif (condition) {code} else (condition) {code}', style = 'CodeStyle.TLabel').grid(column = 0, row = 1, padx = 10, pady = 10, sticky = 'w')
	hpwin.text(master = lct, text = 'These can be put anywhere where normal PyCode commands can be used, in Keyboard Shortcuts, Functions, Python Functions pycode:{} wrappers, etc.\nYou can have any number of \'elif\'s in the condition.\nThe code inside these conditions is separated by \'↓\'s.\nMake sure to not put any \'↩\'s, semicolons, etc between the \'if\'s, \'elif\'s, and \'else\'s, because they are all part of the same statement.\nExample:').grid(column = 0, row = 2, padx = 10, pady = 10, sticky = 'w')
	hpwin.text(master = lct, text = '(sayhellofunc) →:\n(\nif (ask (\'Say hello.\') == \'hello\') {\nsay \'Good job!\'\n}\nelse {\nsay \'You did not say hello\'\n}\n);', style = 'CodeStyle.TLabel').grid(column = 0, row = 3, padx = 10, pady = 10, sticky = 'w')
	hpwin.text(master = lct, text = 'The syntax of making loops in PyCode is very similar:').grid(column = 0, row = 4, padx = 10, pady = 10, sticky = 'w')
	hpwin.text(master = lct, text = 'while (condition) {code}', style = 'CodeStyle.TLabel').grid(column = 0, row = 5, padx = 10, pady = 10, sticky = 'w')
	hpwin.text(master = lct, text = 'The code inside the loop is also separated by \'↓\'s.\nExample:').grid(column = 0, row = 6, padx = 10, pady = 10, sticky = 'w')
	hpwin.text(master = lct, text = 'while (True) {say \'Spam\'}', style = 'CodeStyle.TLabel').grid(column = 0, row = 7, padx = 10, pady = 10, sticky = 'w')
	hpwin.sizablefalse()
	hpwin.style(root.gettheme())
	hpwin.focus()
def find_open_editor(abspath):
	for editor in all_editors:
		if editor.view_master is None and editor.title == abspath and not editor.hmode in ('png', 'pdf', 'epub'):
			return editor
	return None
def _promote_new_master(old_master):
	children = list(old_master.view_children)
	if not children:
		return None
	new_master, rest = children[0], children[1:]
	carried_values = dict((name, value) for name, value in old_master.__dict__.items() if name not in Editor._PER_PANE_ATTRS and name not in Editor._TK_INTERNAL_ATTRS)
	new_master.view_master = None
	for name, value in carried_values.items():
		setattr(new_master, name, value)
	new_master.view_children = rest
	for child in rest:
		child.view_master = new_master
	new_master.m = root.menu()
	for label, menu in all_editor_menus.items():
		new_master.m.add_cascade(label = label, menu = menu)
	for child in rest:
		child.m = new_master.m
	if new_master.hmode == 'python':
		new_master.sethmenu('python')
	elif new_master.hmode == 'latex':
		new_master.sethmenu('latex')
	if new_master.title:
		new_master.clt(new_master.title)
	global active
	if active is old_master:
		active = new_master
	return new_master
def setactive(newindex = None, force = False):
	global editindex
	global active
	if newindex is None:
		newindex = editindex + 1
	if newindex == -1:
		newindex = len(all_editors) - 1
	if newindex == len(all_editors):
		newindex = 0
	if newindex == editindex and not force:
		return
	if 0 <= editindex < len(all_editors):
		all_editors[editindex].active = False
	pcrunhook('before', 'switch-editor', newindex)
	editindex = newindex
	editor = all_editors[editindex]
	resolved = editor.view_master if editor.view_master else editor
	editor.active = True
	root.config(menu = resolved.m)
	active = resolved
	editor.mainwidget.focus_set()
	if resolved.title and not pcsettitle:
		root.title(('PyNotes - ' + os.path.basename(resolved.title)) if not resolved.unsaved else 'PyNotes - ' + os.path.basename(resolved.title) + ' *')
	else:
		root.title('PyNotes - Untitled')
	pcrunhook('after', 'switch-editor', editindex)
def balance(orient = 'all'):
	if orient == 'all':
		balance('horizontal')
		balance('vertical')
		return
	if orient == 'horizontal':
		pw = horizontal
		tw = pw.winfo_width()
	else:
		pw = vertical
		tw = pw.winfo_height()
	panes = pw.panes()
	n = len(panes)
	if n > 1:
		step = tw // n
		for i in range(n - 1):
			pw.sashpos(i, (i + 1) * step)
def neweditor(file = None, orient = 'horizontal'):
	if file == True:
		fn = openfileget(filetypes = (('All Files', '*'), ('Python Files', '*.py'), ('Text Files', '*.txt'), ('LaTeX Files', '*.tex'), ('PNG Images', '*.png'), ('PDF Files', '*.pdf'), ('ePub Files', '*.epub')))
		if fn:
			show('open file')
			neweditor(fn, orient = orient)
		else:
			pcrunhook('before', 'open-file-new-editor', None)
		return
	if file and os.path.isdir(file):
		root.error('Error', f'"{os.path.basename(file)}" is a directory.')
		return
	hookevent = 'open-file-new-editor' if file else 'new-file-new-editor'
	pcrunhook('before', hookevent, file)
	match = find_open_editor(os.path.abspath(file)) if file else None
	newedit = Editor((horizontal if orient == 'horizontal' else vertical), file = None if match else file, view_master = match, padding = 10)
	all_editors.append(newedit)
	pcrun(pycode_keybindings_cdt)
	if orient == 'horizontal':
		horizontal.add(newedit)
		root.update()
		balance('horizontal')
	elif orient == 'vertical':
		vertical.add(newedit)
		root.update()
		balance('vertical')
	root.update()
	setactive(-1)
	pcrunhook('after', hookevent, file)
cmdentry = root.textbox(state = 'disabled', height = 1, bd = 1, font = (monospace, 12))
cmdentry.pack(padx = 10, pady = 10, fill = 'x', anchor = 'n')
cmdautocomplete = root.textbox(state = 'disabled', bd = 1, font = (monospace, 10), wrap = 'word')
def dp():
	show('open download plugins url')
	webbrowser.open('https://github.com/rafugafu/PyNotes/tree/main/Plugins')
def op():
	show('open plugin directory')
	pp = f'{homedir}/.local/share/PyNotes/add-ons'
	if platform.system() == 'Linux':
		subprocess.run(['xdg-open', pp])
	else:
		os.startfile(pp)
def ap():
	show('open plugin help')
	apw = root.subwin()
	apw.title('Add Plugins')
	apw.text(text = f'1. Download a plugin\n2. Extract the plugin if it is a zip\n3. Move the folder to {homedir}/.local/share/PyNotes/add-ons\n4. Restart PyNotes').grid(column = 0, row = 0, padx = 10, pady = 10, sticky = 'w')
	apw.button(text = 'Download From PyNotes\' GitHub', command = dp).grid(column = 0, row = 1, padx = 10, pady = 10, sticky = 'w')
	apw.button(text = 'Open Plugins Directory', command = op).grid(column = 0, row = 2, padx = 10, pady = 10, sticky  = 'w')
	apw.text(text = 'Warning: Plugins have full access to PyNotes and your system\nand can run any commands. Be careful in downloading and using\nplugins from other websites.', font = (monospace, 12, 'bold')).grid(column = 0, row = 3, padx = 10, pady = 10, sticky = 'w')
	apw.style(root.gettheme())
	apw.focus()
def helpmathgod():
	show('open mathgod help')
	hmgwin = root.subwin()
	hmgwin.title('Help with MathGod')
	code = hmgwin.style()
	code.configure('CodeStyle.TLabel', background = 'white', padding = (7, 7, 7, 7), relief = 'sunken')
	tabs = hmgwin.tabs()
	vars = hmgwin.frame()
	tabs.add(vars, text = 'Variables')
	hmgwin.text(master = vars, text = 'You can define variables using the standard python syntax:').grid(column = 0, row = 0, padx = 10, pady = 10)
	hmgwin.text(master = vars, text = '{varname} = {varval}', style = 'CodeStyle.TLabel').grid(column = 0, row = 1, padx = 10, pady = 10)
	hmgwin.text(master = vars, text = 'Here is an example:').grid(column = 0, row = 2, padx = 10, pady = 10)
	hmgwin.text(master = vars, text = 'v = 5\nv\nv + 1', style = 'CodeStyle.TLabel').grid(column = 0, row = 3, padx = 10, pady = 10)
	hmgwin.text(master = vars, text = 'This will return 5 and 6.').grid(column = 0, row = 4, padx = 10, pady = 10)
	func = hmgwin.frame()
	tabs.add(func, text = 'Functions')
	hmgwin.text(master = func, text = 'You can define functions of any number of variables to be used later.\nHere is how to define a function \'f\' of a variable \'x\' which will return x^2:').grid(column = 0, row = 0, padx = 10, pady = 10)
	hmgwin.text(master = func, text = '{func f, x, x^2}', style = 'CodeStyle.TLabel').grid(column = 0, row = 1, padx = 10, pady = 10)
	hmgwin.text(master = func, text = 'You can now use it like this:').grid(column = 0, row = 2, padx = 10, pady = 10)
	hmgwin.text(master = func, text = 'f(5)', style = 'CodeStyle.TLabel').grid(column = 0, row = 3, padx = 10, pady = 10)
	hmgwin.text(master = func, text = 'This will return 25.\nYou can also now use this function in things which take a function as an input. Eg:').grid(column = 0, row = 4, padx = 10, pady = 10)
	hmgwin.text(master = func, text = '{plot f(x), x, -10, 10}', style = 'CodeStyle.TLabel').grid(column = 0, row = 5, padx = 10, pady = 10)
	hmgwin.text(master = func, text = 'You can use this function in other things as well, for example integrals, derivatives, limits, etc...\nYou can also define a function of two or more variables.\nThis is the syntax:').grid(column = 0, row = 6, padx = 10, pady = 10)
	hmgwin.text(master = func, text = '{func {function name}, {vars separated by spaces}, {return value}}', style = 'CodeStyle.TLabel').grid(column = 0, row = 7, padx = 10, pady = 10)
	hmgwin.text(master = func, text = 'Here is an example of a function of two variables:').grid(column = 0, row = 8, padx = 10, pady = 10)
	hmgwin.text(master = func, text = '{func f, x y, x^2+y^2}', style = 'CodeStyle.TLabel').grid(column = 0, row = 9, padx = 10, pady = 10)
	hmgwin.text(master = func, text = 'You can now even plot this function using').grid(column = 0, row = 10, padx = 10, pady = 10)
	hmgwin.text(master = func, text = '{plot3 f(x, y), x, y, -10, 10}', style = 'CodeStyle.TLabel').grid(column = 0, row = 11, padx = 10, pady = 10)
	hmgwin.text(master = func, text = 'Images:').grid(column = 1, row = 0, padx = 10, pady = 10)
	root.image(master = func, image = f'{rootdir}/Images/plotim.png', imsize = (3, 3)).grid(column = 1, row = 1, padx = 10, pady = 10)
	root.image(master = func, image = f'{rootdir}/Images/plotim2.png', imsize = (3, 3)).grid(column = 1, row = 2, padx = 10, pady = 10)
	eq = hmgwin.frame()
	tabs.add(eq, text = 'Defining Equations')
	hmgwin.text(master = eq, text = 'If you have a long equation and want to solve it, you can define it first.\nHere is how to define an equation named \'something\' which is 5x^2=25:').grid(column = 0, row = 0, padx = 10, pady = 10)
	hmgwin.text(master = eq, text = '{eq something, 5x^2=25}', style = 'CodeStyle.TLabel').grid(column = 0, row = 1, padx = 10, pady = 10)
	hmgwin.text(master = eq, text = 'You can now solve this using').grid(column = 0, row = 2, padx = 10, pady = 10)
	hmgwin.text(master = eq, text = '{solve something, x}', style = 'CodeStyle.TLabel').grid(column = 0, row = 3, padx = 10, pady = 10)
	hmgwin.text(master = eq, text = 'to get \'[-sqrt(5), sqrt(5)]\'.').grid(column = 0, row = 4, padx = 10, pady = 10)
	int = hmgwin.frame()
	tabs.add(int, text = 'Integrals')
	hmgwin.text(master = int, text = 'You can use defined functions as variables here.\nHere is how to find the indefinite integral of a function \'x^2\':').grid(column = 0, row = 0, padx = 10, pady = 10)
	hmgwin.text(master = int, text = '{integrate x^2, x}', style = 'CodeStyle.TLabel').grid(column = 0, row = 1, padx = 10, pady = 10)
	hmgwin.text(master = int, text = 'This will return \'x^3/3\'.\nIf you want to calculate a definite integral, just put the bounds at the end, separated by commas.\nFor example,').grid(column = 0, row = 2, padx = 10, pady = 10)
	hmgwin.text(master = int, text = '{integrate x^2, x, 0, 1}', style = 'CodeStyle.TLabel').grid(column = 0, row = 3, padx = 10, pady = 10)
	hmgwin.text(master = int, text = 'This will return \'0.333333333333333\'.\nIf you have defined a function as a variable, you can integrate that too.\nYou can also put another command which returns a function like integral and derivative inside.\nFor example,').grid(column = 0, row = 4, padx = 10, pady = 10)
	hmgwin.text(master = int, text = '{func f, x, x^2}\n{integrate f(x), x}', style = 'CodeStyle.TLabel').grid(column = 0, row = 5, padx = 10, pady = 10)
	hmgwin.text(master = int, text = 'This will also return \'x^3/3\'.').grid(column = 0, row = 6, padx = 10, pady = 10)
	der = hmgwin.frame()
	tabs.add(der, text = 'Derivatives')
	hmgwin.text(master = der, text = 'The syntax of finding derivatives is very similar to finding integrals.\nJust type \'derivative\' instead of \'integrate\'.\nFor example, here is how to find the derivative of x^2:').grid(column = 0, row = 0, padx = 10, pady = 10)
	hmgwin.text(master = der, text = '{derivative x^2, x}', style = 'CodeStyle.TLabel').grid(column = 0, row = 1, padx = 10, pady = 10)
	hmgwin.text(master = der, text = 'In this too, like integrals (see Functions), you can put a named function inside.\nYou can also put another command which returns a function like integral and derivative inside.').grid(column = 0, row = 2, padx = 10, pady = 10)
	lim = hmgwin.frame()
	tabs.add(lim, text = 'Limits')
	hmgwin.text(master = lim, text = 'The syntax of finding limits is very similar to finding integrals and derivatives.\nYou can also specify the direction from which the limit is calculated.\nThe default is +. For example,').grid(column = 0, row = 0, padx = 10, pady = 10)
	hmgwin.text(master = lim, text = '{limit abs(x)/x, x, 0}', style = 'CodeStyle.TLabel').grid(column = 0, row = 1, padx = 10, pady = 10)
	hmgwin.text(master = lim, text = 'will give you \'1\', and').grid(column = 0, row = 2, padx = 10, pady = 10)
	hmgwin.text(master = lim, text = '{limit abs(x)/x, x, 0, dir=\'-\'}', style = 'CodeStyle.TLabel').grid(column = 0, row = 3, padx = 10, pady = 10)
	hmgwin.text(master = lim, text = 'will give you \'-1\'.\nIn this too, like integrals and derivatives (see Functions), you can put a named function inside.\nYou can also put another command which returns a function like integral and derivative inside.').grid(column = 0, row = 4, padx = 10, pady = 10)
	sol = hmgwin.frame()
	tabs.add(sol, text = 'Solving Equations')
	hmgwin.text(master = sol, text = 'You can solve an equation that has been defined (See Defining Equations).\nYou can either have an equation with one variable, or many equations with many variables.\nLet us first look at how to solve an equation with one variable:').grid(column = 0, row = 0, padx = 10, pady = 10)
	hmgwin.text(master = sol, text = '{solve {equation_name}, {equation_var}}', style = 'CodeStyle.TLabel').grid(column = 0, row = 1, padx = 10, pady = 10)
	hmgwin.text(master = sol, text = 'is the general syntax. Fox example,').grid(column = 0, row = 2, padx = 10, pady = 10)
	hmgwin.text(master = sol, text = '{eq something, x+3=5}\n{solve something, x}', style = 'CodeStyle.TLabel').grid(column = 0, row = 3, padx = 10, pady = 10)
	hmgwin.text(master = sol, text = 'will give you \'[2]\'.\nThis can solve things of any order.\nIf there are multiple answers, you will get a list of the format \'[a, b, c, ...]\'.').grid(column = 0, row = 4, padx = 10, pady = 10)
	hmgwin.text(master = sol, text = 'The next is multiple equations with multiple variables.\nThis is also very easy.\nInstead of one equation, you put a list of all your equations,\nand instead of one variable, you put a list of all the variables.\nFor example, here is how to solve two simultaneous linear equations').grid(column = 0, row = 5, padx = 10, pady = 10)
	hmgwin.text(master = sol, text = '5x+6y=15\n2x+8y=9', style = 'CodeStyle.TLabel').grid(column = 0, row = 6, padx = 10, pady = 10)
	hmgwin.text(master = sol, text = ':').grid(column = 0, row = 7, padx = 10, pady = 10)
	hmgwin.text(master = sol, text = '{eq one, 5x+6y=15}\n{eq two 2x+8y=9}\n{solve [one, two], [x, y]}', style = 'CodeStyle.TLabel').grid(column = 0, row = 8, padx = 10, pady = 10)
	hmgwin.text(master = sol, text = 'This will give you an answer like \'{x: 33/14, y: 15/28}\'.').grid(column = 0, row = 9, padx = 10, pady = 10)
	plt2 = hmgwin.frame()
	tabs.add(plt2, text = 'Plotting 2D')
	hmgwin.text(master = plt2, text = 'You can either plot a function of one variable, or a list of coordinates.\nBy default, if you close the plot and plot something else, that will get added to this plot,\nnot make a new graph. If you want to clear the plot, just type:').grid(column = 0, row = 0, padx = 10, pady = 10)
	hmgwin.text(master = plt2, text = 'clearplot', style = 'CodeStyle.TLabel').grid(column = 0, row = 1, padx = 10, pady = 10)
	hmgwin.text(master = plt2, text = 'First, let\'s look at how to plot a function. The general syntax is:').grid(column = 0, row = 2, padx = 10, pady = 10)
	hmgwin.text(master = plt2, text = '{plot {function}, {variable}, {start}, {end}, {options}}', style = 'CodeStyle.TLabel').grid(column = 0, row = 3, padx = 10, pady = 10)
	hmgwin.text(master = plt2, text = 'In this too, you can put a named function (see Functions) inside.\nYou can also put another command which returns a function like an indefinite integral or derivative inside.\nHere is an example of a plot of x^2:').grid(column = 0, row = 4, padx = 10, pady = 10)
	hmgwin.text(master = plt2, text = '{plot x^2, x, 0, 10}', style = 'CodeStyle.TLabel').grid(column = 0, row = 5, padx = 10, pady = 10)
	root.image(master = plt2, image = f'{rootdir}/Images/plotim.png', imsize = (3, 3)).grid(column = 2, row = 1, padx = 10, pady = 10)
	hmgwin.text(master = plt2, text = 'Here is an example of a plot of x^3 using a named function:').grid(column = 0, row = 6, padx = 10, pady = 10)
	hmgwin.text(master = plt2, text = '{func f, x, x^3}\n{plot f(x), x, -10, 10}', style = 'CodeStyle.TLabel').grid(column = 0, row = 7, padx = 10, pady = 10)
	root.image(master = plt2, image = f'{rootdir}/Images/plotim3.png', imsize = (3, 3)).grid(column = 2, row = 2, padx = 10, pady = 10)
	hmgwin.text(master = plt2, text = 'You can also specify various \'options\'. The basic ones for plotting a function are:').grid(column = 1, row = 0, padx = 10, pady = 10)
	ops = ['label: Makes a legend with the label', 'xticks: Sets the xticks of the plot', 'yticks: Sets the yticks of the plot', 'x_label: Sets the label of the x axis', 'y_label: Sets the label of the y axis', 'title: Sets the title of the plot (by default just \'Plot\')', 'linspace: Sets the smoothness of the plot', 'grid: Sets grid to \'True\' or \'False\'']
	opl = hmgwin.listbox(master = plt2, width = 50)
	for op in ops:
		opl.insert('end', op)
	opl.grid(column = 1, row = 1, padx = 10, pady = 10)
	hmgwin.text(master = plt2, text = 'The xticks and yticks options take an input in the format of a list made with square brackets, and separated by commas.\nYou will have to use the option followed by an \'=\' and the value, separated by commas at the end of the plot command.\nHere is an example of a plot with a title:').grid(column = 1, row = 2, padx = 10, pady = 10)
	hmgwin.text(master = plt2, text = '{plot x^2, x, 0, 10, title=\'Title\'}', style = 'CodeStyle.TLabel').grid(column = 1, row = 3, padx = 10, pady = 10)
	hmgwin.text(master = plt2, text = 'The syntax of plotting a list of coordinates is also very easy.\nHere is the general syntax:').grid(column = 1, row = 4, padx = 10, pady = 10)
	hmgwin.text(master = plt2, text = '{plotlist {xs}, {ys}, {options}}', style = 'CodeStyle.TLabel').grid(column = 1, row = 5, padx = 10, pady = 10)
	hmgwin.text(master = plt2, text = 'For example,').grid(column = 1, row = 6, padx = 10, pady = 10)
	hmgwin.text(master = plt2, text = '{plotlist [1, 2, 3], [1, 2, 3]}', style = 'CodeStyle.TLabel').grid(column = 1, row = 7, padx = 10, pady = 10)
	root.image(master = plt2, image = f'{rootdir}/Images/plotim4.png', imsize = (3, 3)).grid(column = 2, row = 3, padx = 10, pady = 10)
	root.image(master = plt2, image = f'{rootdir}/Images/plotim5.png', imsize = (3, 3)).grid(column = 2, row = 3, padx = 10, pady = 10)
	hmgwin.text(master = plt2, text = 'Images:').grid(column = 2, row = 0, padx = 10, pady = 10)
	pltpie = hmgwin.frame()
	tabs.add(pltpie, text = 'Pie Charts')
	hmgwin.text(master = pltpie, text = 'Making Pie Charts with MathGod is very easy.\nYou do not have to make the values add up to 1 or 100.\nHere is an example of a simple pie chart of 40% and 60%:').grid(column = 0, row = 0, padx = 10, pady = 10)
	hmgwin.text(master = pltpie, text = '{pie [40, 60]}', style = 'CodeStyle.TLabel').grid(column = 0, row = 1, padx = 10, pady = 10)
	hmgwin.text(master = pltpie, text = 'There are various options for a pie chart. The basic ones are:').grid(column = 0, row = 2, padx = 10, pady = 10)
	opspie = ['labels: Sets the labels of the sectors', 'colors: Sets the colors of the sectors', 'explode: Sets the distance each sector comes out by', 'startangle: Sets the starting point of the first sector']
	oplpie = hmgwin.listbox(master = pltpie, width = 50)
	for op in opspie:
		oplpie.insert('end', op)
	oplpie.grid(column = 0, row = 3, padx = 10, pady = 10)
	hmgwin.text(master = pltpie, text = 'The labels, colors, and explode options get a list of the same size as the list of input values.\nThe startangle option is in degrees.\nHere is an example of a pie chart of 3 sectors of the same size,\nwith labels \'a\', \'b\', \'c\', the first one (\'a\') set to explode \'0.1\', and colors red, blue, and green:').grid(column = 0, row = 4, padx = 10, pady = 10)
	hmgwin.text(master = pltpie, text = '{pie [1, 1, 1], labels=[\'a\', \'b\', \'c\'], colors=[\'red\', \'blue\', \'green\'], explode=[0.1, 0, 0]}', style = 'CodeStyle.TLabel').grid(column = 0, row = 5, padx = 10, pady = 10)
	hmgwin.text(master = pltpie, text = 'Images:').grid(column = 1, row = 0, padx = 10, pady = 10)
	root.image(master = pltpie, image = f'{rootdir}/Images/plotim6.png', imsize = (3, 3)).grid(column = 1, row = 1, padx = 10, pady = 10)
	root.image(master = pltpie, image = f'{rootdir}/Images/plotim7.png', imsize = (3, 3)).grid(column = 1, row = 2, padx = 10, pady = 10)
	pltbar = hmgwin.frame()
	tabs.add(pltbar, text = 'Bar Charts')
	hmgwin.text(master = pltbar, text = 'Making Bar Charts with MathGod is very simple. This is the general syntax:').grid(column = 0, row = 0, padx = 10, pady = 10)
	hmgwin.text(master = pltbar, text = '{bar {xs}, {ys}, {options}}', style = 'CodeStyle.TLabel').grid(column = 0, row = 1, padx = 10, pady = 10)
	hmgwin.text(master = pltbar, text = 'The basic options are:').grid(column = 0, row = 2, padx = 10, pady = 10)
	oplbar = hmgwin.listbox(master = pltbar, width = 50)
	opbar = ['color: Sets the color of the bars', 'tick_label: Sets the label of each bar', 'width: Sets the width of the bars']
	for op in opbar:
		oplbar.insert('end', op)
	oplbar.grid(column = 0, row = 3, padx = 10, pady = 10)
	hmgwin.text(master = pltbar, text = 'Here is an example of a basic bar chart:').grid(column = 0, row = 4, padx = 10, pady = 10)
	hmgwin.text(master = pltbar, text = '{bar [1, 2, 3], [1, 5, 3]}', style = 'CodeStyle.TLabel').grid(column = 0, row = 5, padx = 10, pady = 10)
	hmgwin.text(master = pltbar, text = 'Images:').grid(column = 1, row = 0, padx = 10, pady = 10)
	root.image(master = pltbar, image = f'{rootdir}/Images/plotim8.png', imsize = (3, 3)).grid(column = 1, row = 1, padx = 10, pady = 10)
	hmgwin.text(master = pltbar, text = 'Here is an example of a bar chart labeled \'a\', \'b\', and \'c\' with the color green with the width \'0.1\' of each bar:').grid(column = 0, row = 6, padx = 10, pady = 10)
	hmgwin.text(master = pltbar, text = '{bar [1, 2, 3], [1, 5, 3], tick_label=[\'a\', \'b\', \'c\'], color=\'green\', width=0.1}', style = 'CodeStyle.TLabel').grid(column = 0, row = 7, padx = 10, pady = 10)
	root.image(master = pltbar, image = f'{rootdir}/Images/plotim9.png', imsize = (3, 3)).grid(column = 1, row = 2, padx = 10, pady = 10)
	plt3 = hmgwin.frame()
	tabs.add(plt3, text = 'Plotting 3D')
	hmgwin.text(master = plt3, text = 'You can only 3D plot a function of two variables.\nThe general syntax is:').grid(column = 0, row = 0, padx = 10, pady = 10)
	hmgwin.text(master = plt3, text = '{plot3  {func}, {var1}, {var2}, [{var1 start}, {var1 end}], [{var2 start}, {var2 end}], options}', style = 'CodeStyle.TLabel').grid(column = 0, row = 1, padx = 10, pady = 10)
	hmgwin.text(master = plt3, text = 'The options are').grid(column = 0, row = 2, padx = 10, pady = 10)
	oplpl3 = hmgwin.listbox(master = plt3, width = 50)
	opspl3 = ['title: Sets the title of the plot', 'grid: Sets the grid to True or False', 'x_label: Sets the label of the x-axis', 'y_label: Sets the label of the y-axis', 'z_label: Sets the label of the z-axis', 'linspace: Sets the smoothness of the plot']
	for op in opspl3:
		oplpl3.insert('end', op)
	oplpl3.grid(column = 0, row = 3, padx = 10, pady = 10)
	hmgwin.text(master = plt3, text = 'You have to use the options followed by an \'=\' and then the value.\nHere is an example of a plot of x^2+y^2:').grid(column = 0, row = 4, padx = 10, pady = 10)
	hmgwin.text(master = plt3, text = '{plot3 x^2+y^2, x, y, [-10, 10], [-10, 10]}', style = 'CodeStyle.TLabel').grid(column = 0, row = 5, padx = 10, pady = 10)
	hmgwin.text(master = plt3, text = 'Here is an example of a plot of the same function but using a named function:').grid(column = 0, row = 6, padx = 10, pady = 10)
	hmgwin.text(master = plt3, text = '{func f, x y, x^2+y^2}\n{plot3 f(x, y), x, y, [-10, 10], [-10, 10]}', style = 'CodeStyle.TLabel').grid(column = 0, row = 7, padx = 10, pady = 10)
	hmgwin.text(master = plt3, text = 'Images:').grid(column = 1, row = 0, padx = 10, pady = 10)
	root.image(master = plt3, image = f'{rootdir}/Images/plotim10.png', imsize = (3, 3)).grid(column = 1, row = 1, padx = 10, pady = 10)
	sum = hmgwin.frame()
	tabs.add(sum, text = 'Summation and Products')
	hmgwin.text(master = sum, text = 'Summation with MathGod is very easy.\nYou can either put an named function inside, or an unnamed one.\nHere is the general syntax:').grid(column = 0, row = 0, padx = 10, pady = 10)
	hmgwin.text(master = sum, text = '{sum {func}, {var}, {start}, {end}}', style = 'CodeStyle.TLabel').grid(column = 0, row = 1, padx = 10, pady = 10)
	hmgwin.text(master = sum, text = 'Here is an example of a sum of i from 1 to 10:').grid(column = 0, row = 2, padx = 10, pady = 10)
	hmgwin.text(master = sum, text = '{sum i, i, 1, 10}', style = 'CodeStyle.TLabel').grid(column = 0, row = 3, padx = 10, pady = 10)
	hmgwin.text(master = sum, text = 'This will return \'55\'. You can also put in named functions.\nHere is an example:').grid(column = 0, row = 4, padx = 10, pady = 10)
	hmgwin.text(master = sum, text = '{func f, x, x}\n{sum f(i), i, 1, 10}', style = 'CodeStyle.TLabel').grid(column = 0, row = 5, padx = 10, pady = 10)
	hmgwin.text(master = sum, text = 'This will also return the same output.\nYou can also put another variable inside the bounds.\nHere is an example:').grid(column = 0, row = 6, padx = 10, pady = 10)
	hmgwin.text(master = sum, text = '{sum i, i, 1, n}', style = 'CodeStyle.TLabel').grid(column = 0, row = 7, padx = 10, pady = 10)
	hmgwin.text(master = sum, text = 'This will return \'n^2/2 + n/2\'.\nFinding products is exactly the same, except just \'prod\' instead of \'sum\'.\nHere is an example:').grid(column = 0, row = 8, padx = 10, pady = 10)
	hmgwin.text(master = sum, text = '{prod i, i, 1, 10}', style = 'CodeStyle.TLabel').grid(column = 0, row = 9, padx = 10, pady = 10)
	hmgwin.text(master = sum, text = 'This will return \'3628800\'.').grid(column = 0, row = 10, padx = 10, pady = 10)
	intp = hmgwin.frame()
	tabs.add(intp, text = 'Interpolation')
	hmgwin.text(master = intp, text = 'Interpolation returns a function that is the given value for all the given points. The general syntax is:').grid(column = 0, row = 0, padx = 10, pady = 10)
	hmgwin.text(master = intp, text = '{interpolate [(x_1, y_1), (x_2, y_2), ...], {var}}', style = 'CodeStyle.TLabel').grid(column = 0, row = 1, padx = 10, pady = 10)
	hmgwin.text(master = intp, text = 'Here is an example:').grid(column = 0, row = 2, padx = 10, pady = 10)
	hmgwin.text(master = intp, text = '{interpolate [(0, 10), (1, 5), (2, -3)], x}', style = 'CodeStyle.TLabel').grid(column = 0, row = 3, padx = 10, pady = 10)
	hmgwin.text(master = intp, text = 'This will return \'-3x^2/2 - 7x/2 + 10\'.\nIf you plot it, you can see that it actually passes through all the exact points:').grid(column = 0, row = 4, padx = 10, pady = 10)
	hmgwin.text(master = intp, text = '{func f, x, {interpolate [(0, 10), (1, 5), (2, -3)], x}}\n{plot f(x), x, -5, 5, xticks=[0, 1, 2], yticks=[10, 5, -3], grid=True}', style = 'CodeStyle.TLabel').grid(column = 0, row = 5, padx = 10, pady = 10)
	hmgwin.text(master = intp, text = 'Images:').grid(column = 1, row = 0, padx = 10, pady = 10)
	root.image(master = intp, image = f'{rootdir}/Images/plotim11.png', imsize = (3, 3)).grid(column = 1, row = 1, padx = 10, pady = 10)
	cnd = hmgwin.frame()
	tabs.add(cnd, text = 'Conditions')
	hmgwin.text(master = cnd, text = 'There are two ways to create a function with a condition.\nThe first is using \'Piecewise\', and the second is just using \'if\'.\nLet\'s first look at the first method:').grid(column = 0, row = 0, padx = 10, pady = 10)
	hmgwin.text(master = cnd, text = '{func f, x, Piecewise((x-1, x<0), (x+1, x>=0))}', style = 'CodeStyle.TLabel').grid(column = 0, row = 1, padx = 10, pady = 10)
	hmgwin.text(master = cnd, text = 'This creates a function \'f\', which is x-1 for x<0, and x+1 for x>=0.\nNow, the other way to create the same function is this:').grid(column = 0, row = 2, padx = 10, pady = 10)
	hmgwin.text(master = cnd, text = '{func f, x, (x-1 if x<0 else x+1)}', style = 'CodeStyle.TLabel').grid(column = 0, row = 3, padx = 10, pady = 10)
	hmgwin.text(master = cnd, text = 'With this method, to make multiple \'elif\' conditions, you can stack the \'if\'s up.').grid(column = 0, row = 4, padx = 10, pady = 10)
	tabs.pack(fill = 'both', expand = True)
	ot = hmgwin.frame()
	tabs.add(ot, text = 'Other')
	hmgwin.text(master = ot, text = 'Additionally, you can use any function from sympy, or any basic function from python.\nFor example, you can use range, map, min, max, subs, sin, cos, etc...\nThe functions from sympy like sin, cos, log, etc... will work with both symbols, and numbers.\nMultiline python things like \'while\', \'for\', \'if\', etc... will not work.\nFor example, if you want to just output the integral back without calculating it, you can type:').grid(column = 0, row = 0, padx = 10, pady = 10)
	hmgwin.text(master = ot, text = 'Integral(x^2, x)', style = 'CodeStyle.TLabel').grid(column = 0, row = 1, padx = 10, pady = 10)
	hmgwin.text(master = ot, text = 'OR').grid(column = 0, row = 2, padx = 10, pady = 10)
	hmgwin.text(master = ot, text = 'Integral(y^2, (y, 0, x))', style = 'CodeStyle.TLabel').grid(column = 0, row = 3, padx = 10, pady = 10)
	hmgwin.style(root.gettheme())
	hmgwin.focus()
plgnm.add_command(label = 'Download From PyNotes\' GitHub', command = dp)
plgnm.add_command(label = 'Open Plugins Directory', command = op)
plgnm.add_separator()
plgnm.add_command(label = 'Help with Adding Plugins', command = ap)
pm.add_command(label = 'Run → F5', command = lambda: active.rp())
lm.add_command(label = 'Run LuaLaTeX → F5', command = lambda: active.runtex('lua'))
lm.add_command(label = 'Run PdfLaTeX', command = lambda: active.runtex('pdf'))
em.add_command(label = 'Undo in Current Editor → Ctrl + Z / Alt + X - u', command = lambda: active.undo())
em.add_command(label = 'Redo in Current Editor → Ctrl + Shift + Z / Alt + X - r', command = lambda: active.redo())
em.add_separator()
em.add_command(label = 'Copy selection in Current Editor → Ctrl + C / Alt + X - c', command = lambda: active.cp())
em.add_command(label = 'Paste clipboard in Current Editor → Ctrl + V / Alt + X - p', command = lambda: active.pst())
em.add_command(label = 'Cut selection in Current Editor → Ctrl + X / Alt + X - cut', command = lambda: active.cut())
em.add_command(label = 'Select all in Current Editor → Ctrl + A / Alt + X - a', command = lambda: active.selall())
hm.add_command(label = 'About', command = abt)
hm.add_command(label = f'What\'s new in {v}?', command = changes)
hm.add_command(label = 'Help with commands → Alt + X - h', command = hx)
hm.add_command(label = 'Help with Email', command = hemail)
hm.add_command(label = 'Help with PyCode', command = helppycode)
hm.add_command(label = 'Help with MathGod', command = helpmathgod)
hm.add_command(label = 'Help with Adding Plugins', command = ap)
hm.add_separator()
hm.add_command(label = 'Recover backup', command = rb)
fm.add_command(label = 'New in Current Editor → Ctrl + N / Alt + X - n', command = lambda: active.nw())
fm.add_command(label = 'New Editor Horizontal → Ctrl + Shift + N / Alt + X - neh', command = lambda: neweditor(orient = 'horizontal'))
fm.add_command(label = 'New Editor Vertical → Alt + X - nev', command = lambda: neweditor(orient = 'vertical'))
fm.add_command(label = 'Open in Current Editor → Ctrl + O / Alt + X - o', command = lambda: active.llld())
fm.add_command(label = 'Open in New Editor Horizontal → Ctrl + Shift + O / Alt + X - onh', command = lambda: neweditor(True))
fm.add_command(label = 'Open in New Editor Vertical → Alt + X - onv', command = lambda: neweditor(True, 'vertical'))
fm.add_separator()
fm.add_command(label = 'Save → Ctrl + S / Alt + X - s', command = lambda: active.sssv())
fm.add_command(label = 'Save As → Ctrl + Shift + S / Alt + X - sa', command = lambda: active.ssv())
fm.add_separator()
fm.add_command(label = 'Quit PyNotes → Ctrl + W / Alt + X - e', command = ext)
pcm.add_command(label = 'Start', command = pc)
pcm.add_separator()
pcm.add_command(label = 'Help', command = helppycode)
om.add_command(label = 'Preferences → Alt + X - prf', command = prf)
om.add_command(label = 'Open PyNotes Source Code → Alt + X - source-code', command = ss)
om.add_separator()
om.add_command(label = 'Go to line → Alt + L / Alt + X - gl', command = lambda: active.gl())
om.add_command(label = 'Page turn forward in Current Editor → Ctrl + P / Alt + X - pf', command = lambda: active.ptf())
om.add_command(label = 'Page turn backward in Current Editor → Ctrl + Shift + P / Alt + X - pb', command = lambda: active.ptb())
om.add_separator()
om.add_command(label = 'Command → Alt + X', command = cmd)
om.add_command(label = 'PyCode → Alt + X - pc', command = pc)
om.add_separator()
om.add_command(label = 'Speech to Text → Alt + X - st', command = st)
em.add_separator()
em.add_command(label = 'Find in Current Editor → Ctrl + F / Alt + X - f', command = lambda: active.f())
em.add_command(label = 'Find & Replace in Current Editor → Ctrl + Shift + F / Alt + X - fr', command = lambda: active.fr())
readonlytextforshellpy = '>>> '
readonlyendforshellpy = '1.' + str(len('>>> '))
continuation = False
continuationcodeforshellpy = ''
def mathgod():
	pcrunhook('before', 'open-mathgod')
	show('open mathgod')
	subprocess.Popen([sys.executable, f'{rootdir}/MathGod.py'])
	pcrunhook('after', 'open-mathgod')
emailwordlist = []
try:
	for dictionary in dicts:
		if dictionary:
			emailwordlist.extend(open(dictionary, 'r', encoding = 'utf-8').read().split('\n'))
except Exception as error:
	error = str(error)
	root.error('Error', error)
om.add_command(label = 'Terminal → Alt + X - t', command = term)
om.add_separator()
om.add_command(label = 'Speak Text → Alt + X - sp', command = lambda: active.spk())
root.protocol('WM_DELETE_WINDOW', ext)
mg.add_command(label = 'Start', command = mathgod)
mg.add_separator()
mg.add_command(label = 'Help', command = helpmathgod)
wholenewwords = []
for command in plgnpccmds:
	pycodetopythoncommands[command] = plgnpccmds[command][1]
pycode_keybindings_cdt = ''
_open_terminal_closers = []
all_editors = []
editindex = -1
vertical = easytk.ttk.Panedwindow(root, orient = 'vertical')
vertical.pack(side = 'bottom', fill = 'both', expand = True)
horizontal = easytk.ttk.Panedwindow(vertical, orient = 'horizontal')
vertical.add(horizontal)
sashconfig = lambda: [root.style().configure('Sash', sashthickness = 15, relief = 'raised')]
active = None
sashconfig()
root.bind('<<ThemeChanged>>', lambda event: sashconfig())
_resize_after_id = None
_last_root_size = (root.winfo_width(), root.winfo_height())
def _on_root_resize(event):
	global _resize_after_id
	global _last_root_size
	size = (event.width, event.height)
	if size == _last_root_size:
		return
	_last_root_size = size
	if _resize_after_id is not None:
		root.after_cancel(_resize_after_id)
	_resize_after_id = root.after(DEBOUNCE_TIME, _do_resize_balance)
def _do_resize_balance():
	global _resize_after_id
	_resize_after_id = None
	if not root.winfo_exists():
		return
	pcrunhook('before', 'resize-window')
	balance()
	pcrunhook('after', 'resize-window')
root.bind('<Configure>', _on_root_resize)
neweditor()
_init_hl_tags()
_init_pythonshell_hl_tags()
if defs[3] in root.themes():
	root.style(defs[3])
root.bind('<Alt-x>', lambda event: cmd())
root.bind('<Control-N>', lambda event: neweditor())
root.bind('<Control-O>', lambda event: neweditor(True))
root.bind('<Control-w>', lambda event: ext())
if not options['no-load-pycode']:
	try:
		pycodestartupcdt = pcread(open(f'{homedir}/.pynotes', 'r', encoding = 'utf-8').read())
	except Exception:
		pass
	else:
		for line in pycodestartupcdt.split('\n'):
			try:
				exec(line, globals())
			except Exception as error:
				error = str(error)
				root.error('Error', f'Error in PyCode: {error}')
if options['pycode-exec']:
	givenpcstartuplines = pcread(options['pycode-exec']).split('\n')
	for line in givenpcstartuplines:
		try:
			exec(line, globals())
		except Exception as error:
			error = str(error)
			root.error('Error', f'Error in PyCode: {error}')
if options['command-exec']:
	cmdrun(options['command-exec'])
for code in last:
	try:
		exec(code[1])
	except Exception as error:
		error = str(error)
		root.error('Error!', f'There was an error in the last part of the plugin "{os.path.basename(os.path.normpath(code[0]))}":\n{error}')
_init_plugin_tags()
if files_to_open:
	all_editors[0].ld(files_to_open.pop(0))
for file in files_to_open:
	neweditor(file)
if new:
	prf()
root.show()
