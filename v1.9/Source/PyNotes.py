import sys
v = '1.9'
if len(sys.argv) > 1:
	if sys.argv[1] == '--version':
		print(v)
		exit()
import os
import subprocess
import getpass
import platform
from tkinter import messagebox as mb
if platform.system() == 'Linux':
	rootdir = '/usr/share/PyNotes'
	homedir = f'/home/{getpass.getuser()}'
	monospace = 'monospace'
else:
	rootdir = 'C:/Program Files/PyNotes'
	homedir = f'C:/Users/{getpass.getuser()}'
	monospace = 'Courier'
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
		exit()
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
import importlib.util
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
del _bmod
_PYTHON_BUILTIN_METHOD_RETURNS = {'str': {'capitalize': 'str', 'casefold': 'str', 'center': 'str', 'expandtabs': 'str', 'format': 'str', 'format_map': 'str', 'join': 'str', 'ljust': 'str', 'lower': 'str', 'lstrip': 'str', 'removeprefix': 'str', 'removesuffix': 'str', 'replace': 'str', 'rjust': 'str', 'rstrip': 'str', 'strip': 'str', 'swapcase': 'str', 'title': 'str', 'translate': 'str', 'upper': 'str', 'zfill': 'str', 'split': 'list', 'rsplit': 'list', 'splitlines': 'list', 'partition': 'tuple', 'rpartition': 'tuple', 'encode': 'bytes', 'count': 'int', 'find': 'int', 'index': 'int', 'rfind': 'int', 'rindex': 'int', 'maketrans': 'dict', 'isalnum': 'bool', 'isalpha': 'bool', 'isascii': 'bool', 'isdecimal': 'bool', 'isdigit': 'bool', 'isidentifier': 'bool', 'islower': 'bool', 'isnumeric': 'bool', 'isprintable': 'bool', 'isspace': 'bool', 'istitle': 'bool', 'isupper': 'bool', 'startswith': 'bool', 'endswith': 'bool'}, 'bytes': {'capitalize': 'bytes', 'center': 'bytes', 'expandtabs': 'bytes', 'hex': 'str', 'join': 'bytes', 'ljust': 'bytes', 'lower': 'bytes', 'lstrip': 'bytes', 'removeprefix': 'bytes', 'removesuffix': 'bytes', 'replace': 'bytes', 'rjust': 'bytes', 'rstrip': 'bytes', 'strip': 'bytes', 'swapcase': 'bytes', 'title': 'bytes', 'translate': 'bytes', 'upper': 'bytes', 'zfill': 'bytes', 'decode': 'str', 'split': 'list', 'rsplit': 'list', 'splitlines': 'list', 'partition': 'tuple', 'rpartition': 'tuple', 'count': 'int', 'find': 'int', 'index': 'int', 'rfind': 'int', 'rindex': 'int', 'maketrans': 'dict', 'isalnum': 'bool', 'isalpha': 'bool', 'isascii': 'bool', 'isdigit': 'bool', 'islower': 'bool', 'isspace': 'bool', 'istitle': 'bool', 'isupper': 'bool', 'startswith': 'bool', 'endswith': 'bool'}, 'bytearray': {'capitalize': 'bytearray', 'center': 'bytearray', 'expandtabs': 'bytearray', 'hex': 'str', 'join': 'bytearray', 'ljust': 'bytearray', 'lower': 'bytearray', 'lstrip': 'bytearray', 'removeprefix': 'bytearray', 'removesuffix': 'bytearray', 'replace': 'bytearray', 'rjust': 'bytearray', 'rstrip': 'bytearray', 'strip': 'bytearray', 'swapcase': 'bytearray', 'title': 'bytearray', 'translate': 'bytearray', 'upper': 'bytearray', 'zfill': 'bytearray', 'decode': 'str', 'split': 'list', 'rsplit': 'list', 'splitlines': 'list', 'partition': 'tuple', 'rpartition': 'tuple', 'count': 'int', 'find': 'int', 'index': 'int', 'rfind': 'int', 'rindex': 'int', 'maketrans': 'dict', 'isalnum': 'bool', 'isalpha': 'bool', 'isascii': 'bool', 'isdigit': 'bool', 'islower': 'bool', 'isspace': 'bool', 'istitle': 'bool', 'isupper': 'bool', 'startswith': 'bool', 'endswith': 'bool'}, 'list': {'copy': 'list', 'count': 'int', 'index': 'int'}, 'dict': {'copy': 'dict', 'keys': 'list', 'values': 'list', 'items': 'list', 'fromkeys': 'dict'}, 'set': {'copy': 'set', 'union': 'set', 'intersection': 'set', 'difference': 'set', 'symmetric_difference': 'set', 'isdisjoint': 'bool', 'issubset': 'bool', 'issuperset': 'bool'}, 'frozenset': {'copy': 'frozenset', 'union': 'frozenset', 'intersection': 'frozenset', 'difference': 'frozenset', 'symmetric_difference': 'frozenset', 'isdisjoint': 'bool', 'issubset': 'bool', 'issuperset': 'bool'}, 'int': {'bit_length': 'int', 'bit_count': 'int', 'conjugate': 'int', 'as_integer_ratio': 'tuple', 'to_bytes': 'bytes'}, 'float': {'conjugate': 'float', 'as_integer_ratio': 'tuple', 'hex': 'str', 'is_integer': 'bool'}}
def faketerm(number):
	termwin = easytk.win()
	termwin.title('Terminal')
	term = termwin.textbox(background = 'black', foreground = 'white', font = (monospace, 12))
	if number == 0:
		command = 'pip install tika'
	elif number == 1:
		command = 'pip install pdfplumber'
	elif number == 2:
		command = 'pip install pyttsx3'
	elif number == 3:
		command = 'pip install matplotlib'
	elif number == 4:
		command = 'pip install sympy'
	elif number == 5:
		command = 'pip install sounddevice'
	elif number == 6:
		command = 'pip install SpeechRecognition'
	elif number == 7:
		command = 'pip install numpy'
	elif number == 8:
		command = 'pip install ttkwidgets'
	elif number == 9:
		command = 'pip install pywinpty'
	elif number == 10:
		command = 'pip install ziamath'
	elif number == 11:
		command = 'pip install cairosvg'
	elif number == 12:
		command = 'pip install Pillow'
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
		faketerm(0)
try:
	import pdfplumber
except Exception:
	ans = ask('Error!', 'The module \'pdfplumber\' is not installed. Should PyNotes install it locally?')
	if not ans:
		exit()
	else:
		faketerm(1)
try:
	import pyttsx3 as stt
except Exception:
	ans = ask('Error!', 'The module \'pyttsx3\' is not installed. Should PyNotes install it locally?')
	if not ans:
		exit()
	else:
		faketerm(2)
try:
	import matplotlib.pyplot as plt
except Exception:
	ans = ask('Error!', 'The module \'matplotlib\' is not installed. Should PyNotes install it locally?')
	if not ans:
		exit()
	else:
		faketerm(3)
try:
	import sympy
except Exception:
	ans = ask('Error!', 'The module \'sympy\' is not installed. Should PyNotes install it locally?')
	if not ans:
		exit()
	else:
		faketerm(4)
try:
	import sounddevice as sd
except Exception:
	ans = ask('Error!', 'The module \'sounddevice\' is not installed. Should PyNotes install it locally?')
	if not ans:
		exit()
	else:
		faketerm(5)
try:
	import speech_recognition as sr
except Exception:
	ans = ask('Error!', 'The module \'speech_recognition\' is not installed. Should PyNotes install it locally?')
	if not ans:
		exit()
	else:
		faketerm(6)
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
		faketerm(8)
if platform.system() != 'Linux':
	try:
		from winpty import PtyProcess
	except Exception:
		ans = ask('Error!', 'The module \'pywinpty\' is not installed. Should PyNotes install it locally?')
		if not ans:
			exit()
		else:
			faketerm(9)
try:
	import ziamath
except Exception:
	ans = ask('Error!', 'The module \'ziamath\' is not installed. Should PyNotes install it locally?')
	if not ans:
		exit()
	else:
		faketerm(10)
try:
	import cairosvg
except Exception:
	ans = ask('Error!', 'The module \'cairosvg\' is not installed. Should PyNotes install it locally?')
	if not ans:
		exit()
	else:
		faketerm(11)
try:
	from PIL import Image
except Exception:
	ans = ask('Error!', 'The module \'Pillow\' is not installed. Should PyNotes install it locally?')
	if not ans:
		exit()
	else:
		faketerm(12)
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
	if platform.system() != 'Linux':
		from winpty import PtyProcess
except Exception:
	info('Error!', 'The modules were not installed properly. Quitting PyNotes.')
	exit()
try:
	os.mkdir(f'{homedir}/.local/')
except Exception:
	pass
try:
	os.mkdir(f'{homedir}/.local/share/')
except Exception:
	pass
try:
	os.mkdir(f'{homedir}/.local/share/PyNotes')
except Exception:
	pass
try:
	os.mkdir(f'{homedir}/.local/share/PyNotes/add-ons')
except Exception:
	pass
defaultpythonexec = '/usr/bin/python3' if platform.system() == 'Linux' else 'python'
defaultdefs = f"{v}\nFalse\n{monospace}\npulse\n{rootdir}/english.txt\nFalse\nFalse\n{defaultpythonexec}\n'pynotes:found': \"foreground = '#FFFFFF', background = '#16A34A'\", 'pynotes:foundhighlight': \"foreground = '#FFFFFF', background = '#1F2937'\", 'pynotes:marked': \"background = '#E5E7EB'\", 'python:keywords': \"foreground = '#7C3AED', font = (type_.cget('font')[:-3].strip('{{}}'), 12, 'bold')\", 'python:inbuilt': \"foreground = '#D97706'\", 'python:comments': \"foreground = '#6B7280', font = (type_.cget('font')[:-3].strip('{{}}'), 12, 'italic')\", 'python:strings': \"foreground = '#15803D'\", 'python:variable_names': \"foreground = '#DC2626'\", 'python:function_names': \"foreground = '#2563EB'\", 'python:class_names': \"foreground = '#0891B2'\", 'python:function_arguments': \"foreground = '#0F766E'\", 'python:operators': \"foreground = 'white', background = 'light grey'\", 'python:module_names': \"foreground = '#0369A1'\", 'latex:inlinemath': \"foreground = '#15803D'\", 'latex:environment': \"background = '#DCFCE7'\", 'latex:comments': \"foreground = '#6B7280', font = (type_.cget('font')[:-3].strip('{{}}'), 12, 'italic')\", 'latex:commands': \"foreground = '#C026D3'\", 'latex:arguments': \"foreground = '#2563EB'\", 'latex:operators': \"foreground = 'white', background = 'light grey'\", 'latex:square_brackets': \"foreground = '#92400E'\", 'html:attributes': \"foreground = '#DC2626'\", 'html:tags': \"foreground = '#047857'\", 'html:comments': \"foreground = '#6B7280', font = (type_.cget('font')[:-3].strip('{{}}'), 12, 'italic')\", 'html:quotes': \"foreground = '#2563EB'\", 'markdown:headers1': \"foreground = '#111827', font = (type_.cget('font')[:-3].strip('{{}}'), 29, 'bold')\", 'markdown:headers2': \"foreground = '#1F2937', font = (type_.cget('font')[:-3].strip('{{}}'), 26, 'bold')\", 'markdown:headers3': \"foreground = '#374151', font = (type_.cget('font')[:-3].strip('{{}}'), 23, 'bold')\", 'markdown:headers4': \"foreground = '#4B5563', font = (type_.cget('font')[:-3].strip('{{}}'), 20, 'bold')\", 'markdown:headers5': \"foreground = '#6B7280', font = (type_.cget('font')[:-3].strip('{{}}'), 17, 'bold')\", 'markdown:headers6': \"foreground = '#9CA3AF', font = (type_.cget('font')[:-3].strip('{{}}'), 14, 'bold')\", 'markdown:bold': \"font = (type_.cget('font')[:-3].strip('{{}}'), 12, 'bold')\", 'markdown:italic': \"font = (type_.cget('font')[:-3].strip('{{}}'), 12, 'italic')\", 'markdown:bold_italic': \"font = (type_.cget('font')[:-3].strip('{{}}'), 12, 'bold italic')\", 'markdown:strike': 'overstrike = True', 'markdown:inlinecode': \"foreground = '#BE123C', background = '#F3F4F6'\", 'markdown:links': \"foreground = '#2563EB', underline = True, underlinefg = '#2563EB'\", 'markdown:blockquotes': \"foreground = '#374151', background = '#F3F4F6'\", 'markdown:codeblocks': \"background = '#F3F4F6'\""
try:
	file = open(f'{homedir}/.local/share/PyNotes/defs', 'r', encoding = 'utf-8')
except Exception:
	file = open(f'{homedir}/.local/share/PyNotes/defs', 'w+', encoding = 'utf-8')
	file.write(defaultdefs)
	file.close()
	file = open(f'{homedir}/.local/share/PyNotes/defs', 'r', encoding = 'utf-8')
	info('', 'Welcome to PyNotes!')
	new = True
plgns = os.listdir(f'{homedir}/.local/share/PyNotes/add-ons')
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
			info('Error!', f'There was an error in loading the Alt-X commands of the plugin "{os.path.basename(os.path.normpath(plgn))}":\n{error}')
			exit()
for code in init:
	try:
		exec(code[1])
	except Exception as error:
		info('Error!', f'There was an error in initializing the plugin "{os.path.basename(os.path.normpath(code[0]))}":\n{error}')
class ErrorHandler:
	def __init__(self):
		self.win = None
		self.textbox = None
	def write(self, error):
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
			try:
				_main_queue.put(_do_write)
			except NameError:
				root.after(0, _do_write)
	def flush(self):
		pass
root = easytk.win()
unsaved = False
unsavedtext = ''
hmode = 'norm'
os.makedirs(f'{homedir}/.local/share/PyNotes/tempfiles', exist_ok = True)
sys.stderr = ErrorHandler()
pcsettitle = False
import math as mathmod
try:
	defs = file.read().split('\n')
	file.close()
	dicts = defs[4].split(',')
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
	pythonexecutable = defs[7]
	exec('theme = ' + '{' + defs[8] + '}')
	theme['python:variable_names']
	theme['python:function_names']
	theme['python:class_names']
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
	if defs[5] == 'True':
		emacskeysforsearch = True
	elif defs[5] == 'False':
		emacskeysforsearch = False
	if defs[6] == 'True':
		taborspace = True
	elif defs[6] == 'False':
		taborspace = False
	pythonexecutable = defs[7]
	exec('theme = ' + '{' + defs[8] + '}')
if not v == defs[0]:
	root.info('Info', 'PyNotes has been updated!')
	defs[0] = v
	file = open(f'{homedir}/.local/share/PyNotes/defs', 'w+', encoding = 'utf-8')
	for d in defs:
		file.write(d + '\n')
	file.close()
if defs[1] == 'False':
	bfr = False
elif defs[1] == 'True':
	bfr = True
try:
	icon = f'{rootdir}/Icon.png'
	root.seticon(icon)
except Exception:
	root.error('Error', f'Could not find the icon at {rootdir}/Icon.png.\nQuitting PyNotes.')
	root.destroy()
	exit()
root.title('PyNotes - Untitled')
root.geometry('820x800')
title = ''
type_top = '1.0'
type_bottom = 'end'
def _init_hl_tags():
	[type_.tag_delete(tag) for tag in ('hpa', 'hpb', 'hpv', 'hpf', 'hpx', 'hpfa', 'hpm', 'hpo', 'hpd', 'hpc', 'hla', 'hlb', 'hld', 'hle', 'hlf', 'hlg', 'hlh', 'hstuff', 'hattr', 'hstr', 'hcmt', 'hmh1', 'hmh2', 'hmh3', 'hmh4', 'hmh5', 'hmh6', 'hmb', 'hmi', 'hmbi')]
	exec("type_.tag_config('hpa'," + theme['python:keywords'] + ')')
	exec("type_.tag_config('hpb'," + theme['python:inbuilt'] + ')')
	exec("type_.tag_config('hpv'," + theme['python:variable_names'] + ')')
	exec("type_.tag_config('hpf'," + theme['python:function_names'] + ')')
	exec("type_.tag_config('hpx'," + theme['python:class_names'] + ')')
	exec("type_.tag_config('hpfa'," + theme['python:function_arguments'] + ')')
	exec("type_.tag_config('hpm'," + theme['python:module_names'] + ')')
	exec("type_.tag_config('hpo'," + theme['python:operators'] + ')')
	exec("type_.tag_config('hpd'," + theme['python:strings'] + ')')
	exec("type_.tag_config('hpc'," + theme['python:comments'] + ')')
	exec("type_.tag_config('hla'," + theme['latex:inlinemath'] + ')')
	exec("type_.tag_config('hlb'," + theme['latex:environment'] + ')')
	exec("type_.tag_config('hld'," + theme['latex:commands'] + ')')
	exec("type_.tag_config('hle'," + theme['latex:arguments'] + ')')
	exec("type_.tag_config('hlf'," + theme['latex:operators'] + ')')
	exec("type_.tag_config('hlg'," + theme['latex:square_brackets'] + ')')
	exec("type_.tag_config('hlh'," + theme['latex:comments'] + ')')
	exec("type_.tag_config('hstuff'," + theme['html:tags'] + ')')
	exec("type_.tag_config('hattr'," + theme['html:attributes'] + ')')
	exec("type_.tag_config('hstr'," + theme['html:quotes'] + ')')
	exec("type_.tag_config('hcmt'," + theme['html:comments'] + ')')
	exec("type_.tag_config('hmh1'," + theme['markdown:headers1'] + ')')
	exec("type_.tag_config('hmh2'," + theme['markdown:headers2'] + ')')
	exec("type_.tag_config('hmh3'," + theme['markdown:headers3'] + ')')
	exec("type_.tag_config('hmh4'," + theme['markdown:headers4'] + ')')
	exec("type_.tag_config('hmh5'," + theme['markdown:headers5'] + ')')
	exec("type_.tag_config('hmh6'," + theme['markdown:headers6'] + ')')
	exec("type_.tag_config('hmb'," + theme['markdown:bold'] + ')')
	exec("type_.tag_config('hmi'," + theme['markdown:italic'] + ')')
	exec("type_.tag_config('hmbi'," + theme['markdown:bold_italic'] + ')')
	exec("type_.tag_config('hms'," + theme['markdown:strike'] + ')')
	exec("type_.tag_config('hmc'," + theme['markdown:inlinecode'] + ')')
	exec("type_.tag_config('hml'," + theme['markdown:links'] + ')')
	exec("type_.tag_config('hmq'," + theme['markdown:blockquotes'] + ')')
	exec("type_.tag_config('hmf'," + theme['markdown:codeblocks'] + ')')
	exec("type_.tag_config('marked'," + theme['pynotes:marked'] + ')')
def _init_pythonshell_hl_tags():
	exec("shellcmd.tag_config('hpa'," + theme['python:keywords'].replace('type_', 'shellcmd') + ')')
	exec("shellcmd.tag_config('hpb'," + theme['python:inbuilt'].replace('type_', 'shellcmd') + ')')
	exec("shellcmd.tag_config('hpv'," + theme['python:variable_names'].replace('type_', 'shellcmd') + ')')
	exec("shellcmd.tag_config('hpf'," + theme['python:function_names'].replace('type_', 'shellcmd') + ')')
	exec("shellcmd.tag_config('hpx'," + theme['python:class_names'].replace('type_', 'shellcmd') + ')')
	exec("shellcmd.tag_config('hpfa'," + theme['python:function_arguments'].replace('type_', 'shellcmd') + ')')
	exec("shellcmd.tag_config('hpm'," + theme['python:module_names'].replace('type_', 'shellcmd') + ')')
	exec("shellcmd.tag_config('hpo'," + theme['python:operators'].replace('type_', 'shellcmd') + ')')
	exec("shellcmd.tag_config('hpd'," + theme['python:strings'].replace('type_', 'shellcmd') + ')')
	exec("shellcmd.tag_config('hpc'," + theme['python:comments'].replace('type_', 'shellcmd') + ')')
def _init_plugin_tags():
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
				exec("type_.tag_config('" + tag + "'," + theme[theme_key] + ')')
			except Exception:
				pass
for code in first:
	try:
		exec(code[1])
	except Exception as error:
		root.error('Error!', f'There was an error in the first part of the plugin "{os.path.basename(os.path.normpath(code[0]))}":\n{error}')
def ss():
	answer = root.ask('Warning', 'Do you want to save file before closing ?', options = ('yes', 'no', 'cancel'), icon = 'warning') if unsaved else False
	if answer != None:
		if answer:
			if not saveforclose():
				return
		show('open pynotes source code')
		ld(f'{rootdir}/PyNotes.py')
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
	changelist = ['Changed easytk and PyNotes to use ttkbootstrap!\nYou can now also easily make your own themes using TTK Creator in the Preferences and use them in PyNotes!', 'Added a Markdown HMode and Markdown formatting / syntax highlighting to PyNotes!', 'Made the Python syntax highlighting much better!', 'Made the syntax highlighting of Python variables and functions scope aware!', 'Python function arguments, class names, and module names and methods are now also syntax highlighted, separate from the variables!', 'Added full 256-color/truecolor support in the PyNotes terminal!', 'Completely fixed syntax highlighting lag in large files and added debouncing to all syntax highlighting.', 'Plugins can now make their own HModes and syntax highlighting!', 'Made the HTML syntax highlighting much better.', 'Plugin and PyCode defined Alt-X commands can now take any inputs, not just predefined ones!', 'PyCode functions can now take inputs and return values!', 'Plugins can now directly define PyCode commands (with inputs)!', 'Made more space in the main window by hiding widgets instead of disabling them when they are not needed.', 'Made the Python variable definition detection much smarter.', 'Plugins can now make their own preferences with the main PyNotes preferences.', 'Fixed a bug where some nested PyCode code would not get translated.', 'Made the PyCode error messages better.', 'Fixed an important bug in MathGod in the last version of PyNotes where builtins and functions like I, E, N() were not defined.', 'Made MathGod automatically create all undefined variables as symbols, not just everything from sympy.abc.', 'Made the superscripting and subscripting in MathGod a little better by handling nested brackets.', 'Completely changed and improved the default PyNotes syntax highlighting theme.', 'Completed the Python builtins list for syntax higlighting.', 'Added all the other Python operators to syntax highlighting.', 'Fixed a bug in opening multiple files with spaces in them with a single terminal command.', 'Fixed a small bug in the Windows terminal and made it a little better.', 'Made the MathGod syntax highlighting better by including all Sympy functions.', 'Fixed a bug in the PyCode parser where it stopped at the first closing bracket instead of the matching closing bracket because of using regex.', 'Fixed a small bug in MathGod where the Linux save file dialogue would not show files without extensions.', 'Made the scope-aware AST part of the Python syntax highlighting not give up completely and still highlight the valid parts in a gibberish file.', 'Corrupted saved email details are now handled.', 'Made the PyNotes changes show in a scrollable textbox.']
	chtextbox = cw.textbox(scrolled = True, font = ('TkDefaultFont', 13), wrap = 'word')
	for i in range(len(changelist) - 1):
		chtextbox.insert('end', f'{i + 1}. {changelist[i]}\n\n')
	chtextbox.insert('end', f'{len(changelist)}. {changelist[-1]}')
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
def lld():
	if platform.system() == 'Linux':
		fn = subprocess.run(['zenity', '--file-selection', '--filename=./', '--title=Open File', '--file-filter=All Files | *', '--file-filter=Python Files | *.py', '--file-filter=Text Files | *.txt', '--file-filter=LaTeX Files | *.tex', '--file-filter=PNG Images | *.png', '--file-filter=PDF Files | *.pdf', '--file-filter=ePub Files | *.epub'], capture_output = True, text = True).stdout.strip()
	else:
		fd.askopenfilename(title = 'Open File', filetypes = (('All Files', '*'), ('Python Files', '*.py'), ('Text Files', '*.txt'), ('LaTeX Files', '*.tex'), ('PNG Images', '*.png'), ('PDF Files', '*.pdf'), ('ePub Files', '*.epub')))
	if fn:
		show('open file')
		ld(fn)
def ssssv(nm):
	if not nm == '':
		sv(nm)
	clt(nm)
def clt(nt):
	global title
	global pcsettitle
	global unsaved
	pcsettitle = False
	try:
		if not nt == '':
			root.title('PyNotes' + ' - ' + os.path.basename(nt))
			filename.config(text = os.path.basename(nt))
			title = os.path.abspath(nt)
		else:
			root.title('PyNotes - Untitled')
			filename.config(text = 'Untitled')
			title = ''
		unsaved = False
	except Exception:
		pass
def sssv():
	if not title == '':
		ssssv(title)
	else:
		ssv()
def saveforclose():
	if not title == '':
		ssssv(title)
	else:
		if ssv() == False:
			return False
		else:
			return True
def ext():
	global stoperrors
	answer = root.ask('Warning', 'Do you want to save file before closing ?', options = ('yes', 'no', 'cancel'), icon = 'warning') if unsaved else False
	if answer != None:
		if answer:
			if not saveforclose():
				return
		if os.path.exists(f'{homedir}/.local/share/PyNotes/tempfiles'):
			shutil.rmtree(f'{homedir}/.local/share/PyNotes/tempfiles')
		sys.stderr = open(os.devnull, 'w')
		stoperrors = True
		root.destroy()
		os._exit(0)
def ld(nm):
	global m
	global imageload
	global hmode
	global unsavedtext
	if not nm == '':
		try:
			imageload.pack_forget()
		except Exception:
			pass
		else:
			hmode = 'normal'
			ln.pack(side = 'left', fill = 'y', anchor = 'n')
			type_.pack(fill = 'both', expand = True, anchor = 'n')
			tabs.pack(padx = 10, pady = 10, fill = 'both', expand = True)
		type_.delete('1.0', 'end')
		if os.path.dirname(nm):
			try:
				os.chdir(os.path.dirname(nm))
			except Exception:
				root.error('Error', f'The directory \'{os.path.dirname(nm)}\' does not exist.')
				return
			else:
				nm = os.path.basename(nm)
				type_.edit_reset()
				_python_reset_scan_state()
		if not os.path.exists(nm):
			open(nm, 'w', encoding = 'utf-8')
		try:
			file = open(nm, 'r', encoding = 'utf-8')
			content = file.read()
			type_.delete('1.0', 'end')
			type_.insert('end', content)
			file.close()
		except Exception as error:
			try:
				imageload = root.image(image = nm, imsize = (1, 1))
			except Exception:
				try:
					pdf = pdfplumber.open(nm)
					type_.delete('1.0', 'end')
					for page in pdf.pages:
						type_.insert('end', page.extract_text())
				except Exception:
					try:
						parsed = parser.from_file(nm, service = 'text')
						content = parsed['content']
						type_.delete('1.0', 'end')
						type_.insert('end', content)
					except Exception:
						root.error('Error', error)
					else:
						clt(nm)
						filesize.config(text = str(os.path.getsize(nm)) + 'bytes')
						sethmenu(None)
						tabs.tab(ef, state = 'hidden')
						lf.pack_forget()
						hmode = 'epub'
						filetype.config(text = 'EPUB File (*.epub)')
						keypress()
				else:
					clt(nm)
					filesize.config(text = str(os.path.getsize(nm)) + 'bytes')
					sethmenu(None)
					tabs.tab(ef, state = 'hidden')
					lf.pack_forget()
					hmode = 'pdf'
					filetype.config(text = 'PDF File (*.pdf)')
					keypress()
			else:
				type_.pack_forget()
				ln.pack_forget()
				tabs.pack_forget()
				imageload.pack(fill = 'both', expand = True)
				clt(nm)
				filesize.config(text = str(os.path.getsize(nm)) + ' bytes')
				hmode = 'png'
				filetype.config(text = 'PNG Image (*.png)')
				imageload.focus_force()
				sethmenu(None)
				tabs.tab(ef, state = 'hidden')
				lf.pack_forget()
		else:
			unsavedtext = type_.get('1.0', 'end-1c')
			clt(nm)
			filesize.config(text = str(os.path.getsize(nm)) + ' bytes')
			if os.path.splitext(nm)[1] == '.py':
				pchmode('python')
				filetype.config(text = 'Python File (*.py)')
			elif os.path.splitext(nm)[1] == '.tex':
				pchmode('latex')
				tabs.tab(ef, state = 'hidden')
				filetype.config(text = 'LaTeX / TeX File (*.tex)')
			elif os.path.splitext(nm)[1] == '.html':
				pchmode('html')
				filetype.config(text = 'HTML File (*.html)')
			elif os.path.splitext(nm)[1] == '.md':
				pchmode('markdown')
			else:
				pchmode('norm')
				tabs.tab(ef, state = 'hidden')
			keypress()
		type_.edit_reset()
		_python_reset_scan_state()
def llld():
	answer = root.ask('Warning', 'Do you want to save file before closing ?', options = ('yes', 'no', 'cancel'), icon = 'warning') if unsaved else False
	if answer != None:
		if answer:
			if not saveforclose():
				return
		lld()
def sv(nm):
	global root
	global unsavedtext
	if not nm == '':
		if not hmode in ['png', 'pdf', 'epub']:
			try:
				content = type_.get('1.0', 'end-1c')
				if content == unsavedtext:
					show('no changes to save')
					return
				if os.path.dirname(nm):
					os.chdir(os.path.dirname(nm))
					nm = os.path.basename(nm)
				file = open(nm, 'w', encoding = 'utf-8')
				file.writelines(content)
				file.close()
				unsavedtext = content
				show('save file')
				clt(nm)
			except Exception:
				pass
		else:
			root.error('Error!', 'Cannot save files of this type')
def ssv():
	if platform.system() == 'Linux':
		fn = subprocess.run(['zenity', '--file-selection', '--filename=./', '--save', '--confirm-overwrite', '--title=Save As', '--file-filter=All Files | *'], capture_output = True, text = True).stdout.strip()
	else:
		fn = fd.asksaveasfilename()
	if fn:
		show('save as file')
		sv(fn)
		clt(fn)
	else:
		return False
def nw():
	global hmode
	global unsaved
	global unsavedtext
	answer = root.ask('Warning', 'Do you want to save file before closing ?', options = ('yes', 'no', 'cancel'), icon = 'warning') if unsaved else False
	if answer != None:
		if answer:
			if not saveforclose():
				return
		try:
			imageload.pack_forget()
		except Exception:
			pass
		else:
			ln.pack(side = 'left', fill = 'y', anchor = 'n')
			type_.pack(fill = 'both', expand = True, anchor = 'n')
			tabs.pack(padx = 10, pady = 10, fill = 'both', expand = True)
		type_.delete('1.0', 'end')
		unsavedtext = ''
		clt('')
		type_.edit_reset()
		_python_reset_scan_state()
		sethmenu(None)
		tabs.tab(ef, state = 'hidden')
		lf.pack_forget()
		hmode = 'norm'
		filetype.config(text = 'Plain Text (*.*)')
		show('open new file')
		filename.config(text = 'Untitled')
		filesize.config(text = '0 bytes')
def fr():
	show('find & replace text')
	def fback():
		nonlocal i
		if searching[0]:
			return
		type_.tag_remove('foundhighlight', '1.0', 'end')
		if not foundlist:
			return
		if i != 0:
			i -= 1
		else:
			i = len(foundlist) - 1
		type_.tag_add('foundhighlight', foundlist[i][0], foundlist[i][1])
		exec("type_.tag_config('foundhighlight'," + theme['pynotes:foundhighlight'] + ')')
		type_.see(foundlist[i][1])
		type_.mark_set('insert', foundlist[i][1])
		keypress()
	def fnext(replacetext = None):
		nonlocal i
		if searching[0]:
			return
		type_.tag_remove('foundhighlight', '1.0', 'end')
		if not foundlist:
			return
		if replacetext is not None:
			replace_start = foundlist[i][0]
			type_.delete(foundlist[i][0], foundlist[i][1])
			type_.insert(foundlist[i][0], replacetext)
			after_replace = '%s+%dc' % (replace_start, len(replacetext))
			def after_search():
				nonlocal i
				for j in range(len(foundlist)):
					if type_.compare(foundlist[j][0], '>=', after_replace):
						i = j
						type_.tag_add('foundhighlight', foundlist[i][0], foundlist[i][1])
						exec("type_.tag_config('foundhighlight'," + theme['pynotes:foundhighlight'] + ')')
						type_.see(foundlist[i][1])
						type_.mark_set('insert', foundlist[i][1])
						return
				type_.tag_remove('found', '1.0', 'end')
				type_.tag_remove('foundhighlight', '1.0', 'end')
				ok.destroy()
			pending_action[0] = after_search
			updatef()
		else:
			if i != len(foundlist) - 1:
				i += 1
			else:
				type_.tag_remove('found', '1.0', 'end')
				type_.tag_remove('foundhighlight', '1.0', 'end')
				ok.destroy()
				return
			type_.tag_add('foundhighlight', foundlist[i][0], foundlist[i][1])
			exec("type_.tag_config('foundhighlight'," + theme['pynotes:foundhighlight'] + ')')
			type_.see(foundlist[i][1])
			type_.mark_set('insert', foundlist[i][1])
		keypress()
	def replaceall(replacetext):
		nonlocal i
		if searching[0]:
			return
		type_.tag_remove('foundhighlight', '1.0', 'end')
		if not foundlist:
			return
		for j in range(len(foundlist) - 1, i - 1, -1):
			type_.delete(foundlist[j][0], foundlist[j][1])
			type_.insert(foundlist[j][0], replacetext)
		type_.tag_remove('found', '1.0', 'end')
		ok.destroy()
		keypress()
	search_cancel = [None]
	searching = [False]
	pending_action = [None]
	def updatef():
		nonlocal i
		nonlocal foundlist
		find = findbox.get()
		useregx = regx.get()
		case = cs.get()
		if search_cancel[0]:
			search_cancel[0].set()
		if not find:
			type_.tag_remove('found', '1.0', 'end')
			type_.tag_remove('foundhighlight', '1.0', 'end')
			foundlist.clear()
			searching[0] = False
			return
		type_.tag_remove('found', '1.0', 'end')
		type_.tag_remove('foundhighlight', '1.0', 'end')
		text_content = type_.get('1.0', 'end')
		cancel = threading.Event()
		search_cancel[0] = cancel
		searching[0] = True
		def do_search():
			try:
				pat = find if useregx else re.escape(find)
				flags = 0 if case else re.IGNORECASE
				compiled = re.compile(pat, flags)
			except re.error:
				_main_queue.put(lambda: _start_apply([]))
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
				_main_queue.put(lambda: _start_apply(tk_results))
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
				type_.tag_remove('found', '1.0', 'end')
				searching[0] = False
				return
			end = idx + 500
			if end > n:
				end = n
			for k in range(idx, end):
				st, et = tk_results[k]
				type_.tag_add('found', st, et)
				foundlist.append((st, et))
			if end < n:
				type_.after(1, lambda: _apply_batch(tk_results, n, end))
			else:
				searching[0] = False
				if foundlist:
					exec("type_.tag_config('found'," + theme['pynotes:found'] + ')')
				action = pending_action[0]
				pending_action[0] = None
				if action:
					action()
				elif foundlist:
					type_.tag_add('foundhighlight', foundlist[i][0], foundlist[i][1])
					exec("type_.tag_config('foundhighlight'," + theme['pynotes:foundhighlight'] + ')')
					type_.see(foundlist[i][1])
					type_.mark_set('insert', foundlist[i][1])
		threading.Thread(target = do_search, daemon = True).start()
	def updateff(event = None):
		if not event or event and not event.keysym == 'Return' and not (event.state & 4):
			updatef()
			return
		if not foundlist:
			return
		type_.tag_add('foundhighlight', foundlist[i][0], foundlist[i][1])
		exec("type_.tag_config('foundhighlight'," + theme['pynotes:foundhighlight'] + ')')
		type_.see(foundlist[i][1])
		type_.mark_set('insert', foundlist[i][1])
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
		type_.delete(foundlist[i][0], foundlist[i][1])
		type_.insert(foundlist[i][0], replacebox.get())
		saved_i = i
		def after_search():
			nonlocal i
			if not foundlist:
				return
			i = saved_i if saved_i < len(foundlist) else len(foundlist) - 1
			type_.tag_add('foundhighlight', foundlist[i][0], foundlist[i][1])
			exec("type_.tag_config('foundhighlight'," + theme['pynotes:foundhighlight'] + ')')
			type_.see(foundlist[i][1])
			type_.mark_set('insert', foundlist[i][1])
		pending_action[0] = after_search
		updatef()
	ok.button(text = 'Replace', command = replace_current).grid(column = 0, row = 4, padx = 10, pady = 10, sticky = 'ew')
	ok.button(text = 'Replace and next', command = lambda: fnext(replacebox.get())).grid(column = 1, row = 4, padx = 10, pady = 10, sticky = 'ew')
	ok.button(text = 'Replace all', command = lambda: replaceall(replacebox.get())).grid(column = 0, row = 5, padx = 10, pady = 10, sticky = 'ew')
	type_.bind('<KeyPress>', lambda event: [type_.tag_remove('found', '1.0', 'end'), type_.tag_remove('foundhighlight', '1.0', 'end'), ok.destroy(), type_.unbind('<KeyPress>')])
	ok.button(text = 'Close', command = lambda: [type_.tag_remove('found', '1.0', 'end'), type_.tag_remove('foundhighlight', '1.0', 'end'), ok.destroy(), type_.unbind('<KeyPress>')]).grid(column = 1, row = 5, padx = 10, pady = 10, sticky = 'ew')
	if emacskeysforsearch:
		ok.bind('<Alt-Return>', lambda event: fnext())
		ok.bind('^', lambda event: fback())
		ok.bind('<Control-t>', lambda event: fnext(replacebox.get()))
		ok.bind('!', lambda event: replaceall(replacebox.get()))
		ok.bind('<Return>', lambda event: [type_.tag_remove('found', '1.0', 'end'), type_.tag_remove('foundhighlight', '1.0', 'end'), ok.destroy(), type_.unbind('<KeyPress>')])
		for w in (findbox, replacebox):
			w.bind('^', lambda event: fback() or 'break')
			w.bind('!', lambda event: replaceall(replacebox.get()) or 'break')
	ok.update()
	ok.sizablefalse()
	ok.style(root.gettheme())
	ok.bind('<Escape>', lambda event: [type_.tag_remove('found', '1.0', 'end'), type_.tag_remove('foundhighlight', '1.0', 'end'), ok.destroy(), type_.unbind('<KeyPress>')])
	ok.protocol('WM_DELETE_WINDOW', lambda: [type_.tag_remove('found', '1.0', 'end'), type_.tag_remove('foundhighlight', '1.0', 'end'), ok.destroy(), type_.unbind('<KeyPress>')])
def f():
	show('find text')
	def fback():
		nonlocal i
		type_.tag_remove('foundhighlight', '1.0', 'end')
		if not foundlist:
			return
		if i != 0:
			i -= 1
		else:
			i = len(foundlist) - 1
		type_.tag_add('foundhighlight', foundlist[i][0], foundlist[i][1])
		exec("type_.tag_config('foundhighlight'," + theme['pynotes:foundhighlight'] + ')')
		type_.see(foundlist[i][1])
		type_.mark_set('insert', foundlist[i][1])
		keypress()
	def fnext():
		nonlocal i
		type_.tag_remove('foundhighlight', '1.0', 'end')
		if not foundlist:
			return
		if i != len(foundlist) - 1:
			i += 1
		else:
			i = 0
		type_.tag_add('foundhighlight', foundlist[i][0], foundlist[i][1])
		exec("type_.tag_config('foundhighlight'," + theme['pynotes:foundhighlight'] + ')')
		type_.see(foundlist[i][1])
		type_.mark_set('insert', foundlist[i][1])
		keypress()
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
			type_.tag_remove('found', '1.0', 'end')
			type_.tag_remove('foundhighlight', '1.0', 'end')
			foundlist.clear()
			return
		type_.tag_remove('found', '1.0', 'end')
		type_.tag_remove('foundhighlight', '1.0', 'end')
		text_content = type_.get('1.0', 'end')
		cancel = threading.Event()
		search_cancel[0] = cancel
		def do_search():
			try:
				pat = find if useregx else re.escape(find)
				flags = 0 if case else re.IGNORECASE
				compiled = re.compile(pat, flags)
			except re.error:
				_main_queue.put(lambda: _start_apply([]))
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
				_main_queue.put(lambda: _start_apply(tk_results))
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
				type_.tag_remove('found', '1.0', 'end')
				return
			end = idx + 500
			if end > n:
				end = n
			for k in range(idx, end):
				st, et = tk_results[k]
				type_.tag_add('found', st, et)
				foundlist.append((st, et))
			if end < n:
				type_.after(1, lambda: _apply_batch(tk_results, n, end))
			else:
				if foundlist:
					exec("type_.tag_config('found'," + theme['pynotes:found'] + ')')
					type_.tag_add('foundhighlight', foundlist[i][0], foundlist[i][1])
					exec("type_.tag_config('foundhighlight'," + theme['pynotes:foundhighlight'] + ')')
					type_.see(foundlist[i][1])
					type_.mark_set('insert', foundlist[i][1])
		threading.Thread(target = do_search, daemon = True).start()
	def updateff(event = None):
		if not event or event and not event.keysym == 'Return' and not (event.state & 4):
			updatef()
			return
		if not foundlist:
			return
		type_.tag_add('foundhighlight', foundlist[i][0], foundlist[i][1])
		exec("type_.tag_config('foundhighlight'," + theme['pynotes:foundhighlight'] + ')')
		type_.see(foundlist[i][1])
		type_.mark_set('insert', foundlist[i][1])
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
	type_.bind('<KeyPress>', lambda event: [type_.tag_remove('found', '1.0', 'end'), type_.tag_remove('foundhighlight', '1.0', 'end'), ok.destroy(), type_.unbind('<KeyPress>')])
	ok.button(text = 'Close', command = lambda: [type_.tag_remove('found', '1.0', 'end'), type_.tag_remove('foundhighlight', '1.0', 'end'), ok.destroy(), type_.unbind('<KeyPress>')]).grid(column = 1, row = 3, padx = 10, pady = 10, sticky = 'ew')
	if emacskeysforsearch:
		ok.bind('<Control-s>', lambda event: fnext())
		ok.bind('<Control-r>', lambda event: fback())
		ok.bind('<Return>', lambda event: [type_.tag_remove('found', '1.0', 'end'), type_.tag_remove('foundhighlight', '1.0', 'end'), ok.destroy(), type_.unbind('<KeyPress>')])
	ok.update()
	ok.sizablefalse()
	ok.style(root.gettheme())
	ok.bind('<Escape>', lambda event: [type_.tag_remove('found', '1.0', 'end'), type_.tag_remove('foundhighlight', '1.0', 'end'), ok.destroy(), type_.unbind('<KeyPress>')])
	ok.protocol('WM_DELETE_WINDOW', lambda: [type_.tag_remove('found', '1.0', 'end'), type_.tag_remove('foundhighlight', '1.0', 'end'), ok.destroy(), type_.unbind('<KeyPress>')])
def svprf():
	global bfr
	global theme
	global colours
	file = open(f'{homedir}/.local/share/PyNotes/defs', 'w+', encoding = 'utf-8')
	font = type_.cget('font')[:-3].strip('{}')
	theme = colours.get('1.0', 'end-1c').replace('\n', '').replace('orgfont', 'type_.cget(\'font\')[:-3].strip(\'{}\')')
	file.write(f'{v}\n{str(bfr)}\n{font}\n{root.gettheme()}\n{",".join(dicts)}\n{emacskeysforsearch}\n{taborspace}\n{pythonexecutable}\n{theme}')
	file.close()
	exec('theme = {' + theme + '}', globals())
	_init_hl_tags()
	_init_pythonshell_hl_tags()
	_init_plugin_tags()
	keypress()
def prf():
	global bfr
	global colours
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
			root.error('Error', error)
	def setts(val):
		global taborspace
		taborspace = val
	def setffre(val):
		global emacskeysforsearch
		emacskeysforsearch = val
	def bf(opt):
		global bfr
		bfr = opt
	def adddict():
		if platform.system() == 'Linux':
			dicttoadd = subprocess.run(['zenity', '--file-selection', '--filename=./', '--title=Open File', '--file-filter=Text Files | *.txt'], capture_output = True, text = True).stdout.strip()
		else:
			dicttoadd = fd.askopenfilename(title = 'Open File', filetypes = (('Text Files', '*.txt')))
		if dicttoadd:
			dicts.append(dicttoadd)
			dictlist.insert('end', dicttoadd)
			emailwordlist.clear()
			try:
				for dictionary in dicts:
					if dictionary:
						emailwordlist.extend(open(dictionary, 'r', encoding = 'utf-8').read().split('\n'))
			except Exception as error:
				root.error('Error', error)
	def changepyexec():
		global pythonexecutable
		nonlocal pyexecshowtext
		if platform.system() == 'Linux':
			fn = subprocess.run(['zenity', '--file-selection', '--filename=./', '--title=Open File', '--file-filter=All Files | *'], capture_output = True, text = True).stdout.strip()
		else:
			fn = fd.askopenfilename(title = 'Open File', filetypes = (('All Files', '*')))
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
	showfont = pr.textbox(master = tft, font = (type_.cget('font')[:-3].strip('{}'), 12), wrap = 'word', height = 5)
	showfont.insert('end', 'The quick brown fox jumped over the lazy dogs\nAaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz\n1234567890\n?.,<>;:\'"{}[]\\|\n!@#$%^&*()-_+=')
	showfont.grid(column = 0, row = 1)
	f = pr.droptype(options = [monospace] + sorted(pr.getfonts()), master = mf, command = lambda: [pr.sizabletrue(), type_.config(font = (f.get(), 12)), showfont.config(font = (f.get(), 12)), pr.sizablefalse()])
	f.grid(column = 1, row = 1, padx = 10, pady = 10, sticky = 'ew')
	f.insert('end', type_.cget('font')[:-3].strip('{}'))
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
			root.error('Error!', f'There was an error in setting up the preferences of the plugin "{os.path.basename(os.path.normpath(code[0]))}":\n{error}')
	pr.sizablefalse()
	pr.style(root.gettheme())
	pr.focus()
def type_getvisible():
	type_.update_idletasks()
	top = type_.index('@0,0-2l')
	bottom = type_.index(f'@0,{type_.winfo_height()}+2l')
	return (top, bottom)
_ha_running = [False]
_ha_pending = [None]
_main_queue = queue.Queue()
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
_PYTHON_NAME_LEAD = '(?<![\\w.\'"])'
_PYTHON_NAME_TRAIL = '(?![\\w\'"])'
def _python_bytecol_to_charcol(line_str, bytecol):
	if bytecol <= 0:
		return bytecol
	encoded = line_str.encode('utf-8')
	if bytecol >= len(encoded):
		return len(line_str)
	return len(encoded[:bytecol].decode('utf-8', 'ignore'))
_PYTHON_KW_PAT = re.compile(r'(?<!\.)\b(?:' + '|'.join(re.escape(k) for k in keyword.kwlist) + r')\b')
_PYTHON_BI_PAT = re.compile(r'(?<!\.)\b(?:' + '|'.join(re.escape(k) for k in ('ArithmeticError', 'AssertionError', 'AttributeError', 'BaseException', 'BaseExceptionGroup', 'BlockingIOError', 'BrokenPipeError', 'BufferError', 'BytesWarning', 'ChildProcessError', 'ConnectionAbortedError', 'ConnectionError', 'ConnectionRefusedError', 'ConnectionResetError', 'DeprecationWarning', 'EOFError', 'Ellipsis', 'EncodingWarning', 'EnvironmentError', 'Exception', 'ExceptionGroup', 'FileExistsError', 'FileNotFoundError', 'FloatingPointError', 'FutureWarning', 'GeneratorExit', 'IOError', 'ImportError', 'ImportWarning', 'IndentationError', 'IndexError', 'InterruptedError', 'IsADirectoryError', 'KeyError', 'KeyboardInterrupt', 'LookupError', 'MemoryError', 'ModuleNotFoundError', 'NameError', 'NotADirectoryError', 'NotImplemented', 'NotImplementedError', 'OSError', 'OverflowError', 'PendingDeprecationWarning', 'PermissionError', 'ProcessLookupError', 'PythonFinalizationError', 'RecursionError', 'ReferenceError', 'ResourceWarning', 'RuntimeError', 'RuntimeWarning', 'StopAsyncIteration', 'StopIteration', 'SyntaxError', 'SyntaxWarning', 'SystemError', 'SystemExit', 'TabError', 'TimeoutError', 'TypeError', 'UnboundLocalError', 'UnicodeDecodeError', 'UnicodeEncodeError', 'UnicodeError', 'UnicodeTranslateError', 'UnicodeWarning', 'UserWarning', 'ValueError', 'Warning', 'ZeroDivisionError', '_IncompleteInputError', '__build_class__', '__debug__', '__doc__', '__import__', '__loader__', '__name__', '__package__', '__spec__', 'abs', 'aiter', 'all', 'anext', 'any', 'ascii', 'bin', 'bool', 'breakpoint', 'bytearray', 'bytes', 'callable', 'chr', 'classmethod', 'compile', 'complex', 'copyright', 'credits', 'delattr', 'dict', 'dir', 'divmod', 'enumerate', 'eval', 'exec', 'exit', 'filter', 'float', 'format', 'frozenset', 'getattr', 'globals', 'hasattr', 'hash', 'help', 'hex', 'id', 'input', 'int', 'isinstance', 'issubclass', 'iter', 'len', 'license', 'list', 'locals', 'map', 'max', 'memoryview', 'min', 'next', 'object', 'oct', 'open', 'ord', 'pow', 'print', 'property', 'quit', 'range', 'repr', 'reversed', 'round', 'set', 'setattr', 'slice', 'sorted', 'staticmethod', 'str', 'sum', 'super', 'tuple', 'type', 'vars', 'zip')) + r')\b')
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
debounce_time = 300
_python_scopes = [{'start': 1, 'end': 1, 'parent': None, 'names': {}}]
_python_call_kwargs = {}
_python_module_literals = []
_python_literal_attrs = []
_python_def_names = []
_python_typed_attrs = []
_python_param_default_tags = []
_python_kwarg_positions = []
_python_import_dotted_lines = []
_python_import_orig_name_tags = []
_python_names_scan_thread = None
_python_scan_after_id = None
_ha_after_id = None
_filesize_after_id = None
_unsaved_after_id = None
_prev_visible_region = None
_python_edit_generation = [0]
def _python_reset_scan_state():
	global _python_scopes, _python_call_kwargs, _python_module_literals, _python_literal_attrs, _python_def_names, _python_typed_attrs, _python_param_default_tags, _python_kwarg_positions, _python_import_dotted_lines, _python_import_orig_name_tags
	_python_edit_generation[0] += 1
	_python_scopes = [{'start': 1, 'end': 1, 'parent': None, 'names': {}}]
	_python_call_kwargs = {}
	_python_module_literals = []
	_python_literal_attrs = []
	_python_def_names = []
	_python_typed_attrs = []
	_python_param_default_tags = []
	_python_kwarg_positions = []
	_python_import_dotted_lines = []
	_python_import_orig_name_tags = []
	if hmode == 'python':
		python_trigger_name_scan()
class _PythonScanCancelled(BaseException):
	pass
class _PythonScopeBuilder(ast.NodeVisitor):
	def __init__(self):
		self.scopes = [{'start': 1, 'end': 1, 'parent': None, 'kind': 'module', 'names': {}, 'globals': {}, 'nonlocals': {}}]
		self.scope_stack = [0]
		self.func_params = {}
		self.func_accepts_any = set()
		self.pending_calls = []
		self.module_aliases = {}
		self.from_imports = []
		self.import_names = []
		self.module_literals = []
		self.import_dotted_lines = []
		self.import_orig_names = []
		self.def_names = []
		self.kwarg_positions = []
		self.alias_assigns = []
		self.attr_alias_assigns = []
		self.dynamic_imports = []
		self._in_class_body = False
	def add_name(self, name, lineno, kind):
		names = self.scopes[self.scope_stack[-1]]['names']
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
	def push_scope(self, start, end, kind = 'function'):
		idx = len(self.scopes)
		self.scopes.append({'start': start, 'end': end, 'parent': self.scope_stack[-1], 'kind': kind, 'names': {}, 'globals': {}, 'nonlocals': {}})
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
		for a in list(node.args.posonlyargs) + list(node.args.args) + list(node.args.kwonlyargs):
			params.add(a.arg)
		self.func_params.setdefault(node.name, set()).update(params)
		if node.args.kwarg:
			self.func_accepts_any.add(node.name)
		for dec in node.decorator_list:
			self.visit(dec)
		for d in list(node.args.defaults) + [kd for kd in node.args.kw_defaults if kd is not None]:
			self.visit(d)
		end = getattr(node, 'end_lineno', node.lineno)
		is_method = self._in_class_body
		prev_in_class_body = self._in_class_body
		self._in_class_body = False
		self.push_scope(node.lineno, end)
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
		for dec in node.decorator_list:
			self.visit(dec)
		end = getattr(node, 'end_lineno', node.lineno)
		self.push_scope(node.lineno, end, 'class')
		prev_in_class_body = self._in_class_body
		self._in_class_body = True
		for stmt in node.body:
			self.visit(stmt)
		self._in_class_body = prev_in_class_body
		self.scope_stack.pop()
		for stmt in node.body:
			if isinstance(stmt, ast.FunctionDef) and stmt.name == '__init__':
				params = set(a.arg for a in list(stmt.args.posonlyargs) + list(stmt.args.args) + list(stmt.args.kwonlyargs))
				if stmt.args.vararg:
					params.add(stmt.args.vararg.arg)
				if stmt.args.kwarg:
					params.add(stmt.args.kwarg.arg)
					self.func_accepts_any.add(node.name)
				self.func_params.setdefault(node.name, set()).update(params)
				break
	def visit_Lambda(self, node):
		end = getattr(node, 'end_lineno', node.lineno)
		self.push_scope(node.lineno, end)
		self.add_args(node.args, node.lineno)
		self.visit(node.body)
		self.scope_stack.pop()
	def visit_comp(self, node):
		end = getattr(node, 'end_lineno', node.lineno)
		self.push_scope(node.lineno, end)
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
	def _register_lambda(self, name, lam):
		_largs = lam.args
		_lparams = set(a.arg for a in list(_largs.posonlyargs) + list(_largs.args) + list(_largs.kwonlyargs))
		self.func_params.setdefault(name, set()).update(_lparams)
		if _largs.kwarg:
			self.func_accepts_any.add(name)
	def visit_Assign(self, node):
		_is_lambda = isinstance(node.value, ast.Lambda)
		for t in node.targets:
			if _is_lambda and isinstance(t, ast.Name):
				self.add_name(t.id, node.lineno, 'func')
				self._register_lambda(t.id, node.value)
				continue
			for nm in self.targets(t):
				if not isinstance(nm, ast.Attribute):
					self.add_name(nm.id, node.lineno, 'var')
		if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
			tgt_name = node.targets[0].id
			val = node.value
			if isinstance(val, ast.Name):
				self.alias_assigns.append((self.scope_stack[-1], node.lineno, tgt_name, val.id))
			elif isinstance(val, ast.Attribute) and isinstance(val.value, ast.Name):
				self.attr_alias_assigns.append((self.scope_stack[-1], node.lineno, tgt_name, val.value.id, val.attr))
			elif isinstance(val, ast.Call):
				dmod = self._dynamic_import_module(val)
				if dmod is not None:
					self.dynamic_imports.append((self.scope_stack[-1], node.lineno, tgt_name, dmod))
		self.visit(node.value)
	def _dynamic_import_module(self, call):
		fn = call.func
		is_import = (isinstance(fn, ast.Name) and fn.id == '__import__') or (isinstance(fn, ast.Attribute) and fn.attr == 'import_module')
		if not is_import or not call.args:
			return None
		arg = call.args[0]
		if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
			return arg.value
		return None
	def visit_AnnAssign(self, node):
		if isinstance(node.value, ast.Lambda) and isinstance(node.target, ast.Name):
			self.add_name(node.target.id, node.lineno, 'func')
			self._register_lambda(node.target.id, node.value)
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
			self.scopes[0]['names'].setdefault(name, []).append((1, 'var'))
	def visit_Nonlocal(self, node):
		scope_idx = self.scope_stack[-1]
		for name in node.names:
			self.scopes[scope_idx]['nonlocals'][name] = node.lineno
			parent_idx = self.scopes[scope_idx]['parent']
			if parent_idx is not None:
				parent_start = self.scopes[parent_idx]['start']
				self.scopes[parent_idx]['names'].setdefault(name, []).append((parent_start, 'var'))
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
				if isinstance(target, ast.Name):
					key = f'{prefix}.{target.id}' if prefix else target.id
					members[key] = 'var'
		elif isinstance(node, ast.AnnAssign):
			if isinstance(node.target, ast.Name):
				key = f'{prefix}.{node.target.id}' if prefix else node.target.id
				members[key] = 'var'
	return members
_python_module_spec_cache = {}
def _python_find_spec_cached(name):
	if name in _python_module_spec_cache:
		return _python_module_spec_cache[name]
	try:
		spec = importlib.util.find_spec(name)
	except Exception:
		spec = None
	_python_module_spec_cache[name] = spec
	return spec
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
_python_module_members_cache = {}
def _python_resolve_module_members(name, visited = None):
	if name in _python_module_members_cache:
		return _python_module_members_cache[name]
	if visited is None:
		visited = set()
	if name in visited:
		return {}
	visited.add(name)
	spec = _python_find_spec_cached(name)
	src_path = _python_module_src_path(spec, name)
	if src_path is None:
		_python_module_members_cache[name] = {}
		return {}
	try:
		with open(src_path, 'r', encoding = 'utf-8') as f:
			src = f.read()
		with warnings.catch_warnings():
			warnings.simplefilter('ignore')
			mod_ast = ast.parse(src)
	except Exception:
		_python_module_members_cache[name] = {}
		return {}
	members = _python_inspect_ast_members(mod_ast.body)
	for node in mod_ast.body:
		if isinstance(node, ast.ImportFrom):
			sub_name = (node.module if node.level == 0 else f'{name}.{node.module}') if node.module else name
			sub_members = None
			for alias in node.names:
				if alias.name == '*':
					if sub_members is None:
						sub_members = _python_resolve_module_members(sub_name, visited)
					for k, v in sub_members.items():
						members.setdefault(k, v)
				else:
					exported = alias.asname if alias.asname else alias.name
					if exported not in members:
						if sub_members is None:
							sub_members = _python_resolve_module_members(sub_name, visited)
						if alias.name in sub_members:
							members[exported] = sub_members[alias.name]
							pfx = alias.name + '.'
							for k, v in sub_members.items():
								if k.startswith(pfx):
									members[exported + k[len(alias.name):]] = v
						elif _python_find_spec_cached(f'{sub_name}.{alias.name}') is not None:
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
	_python_module_members_cache[name] = members
	return members
_python_module_func_params_cache = {}
def _python_resolve_module_func_params(name):
	if name in _python_module_func_params_cache:
		return _python_module_func_params_cache[name]
	spec = _python_find_spec_cached(name)
	src_path = _python_module_src_path(spec, name)
	if src_path is None:
		_python_module_func_params_cache[name] = {}
		return {}
	try:
		with open(src_path, 'r', encoding = 'utf-8') as f:
			src = f.read()
		with warnings.catch_warnings():
			warnings.simplefilter('ignore')
			mod_ast = ast.parse(src)
	except Exception:
		_python_module_func_params_cache[name] = {}
		return {}
	out = {}
	_imp = {}
	for node in mod_ast.body:
		if isinstance(node, ast.ImportFrom):
			_imod = node.module if node.level == 0 else (f'{name}.{node.module}' if node.module else name)
			if _imod:
				for alias in node.names:
					if alias.name != '*':
						_imp[alias.asname or alias.name] = (_imod, alias.name)
			continue
		if isinstance(node, ast.Import):
			for alias in node.names:
				_imp[alias.asname or alias.name.split('.')[0]] = (alias.name, None)
			continue
		if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
			params = set(a.arg for a in list(node.args.posonlyargs) + list(node.args.args) + list(node.args.kwonlyargs))
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
					mparams = set(a.arg for a in margs[1:]) | set(a.arg for a in sub.args.kwonlyargs)
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
	_python_module_func_params_cache[name] = out
	return out
def _python_resolve_module_member_kind(mod, class_name, member, seen = None):
	if seen is None:
		seen = set()
	key = (mod, class_name)
	if key in seen:
		return None
	seen.add(key)
	mems = _python_resolve_module_members(mod)
	_dk = f'{class_name}.{member}'
	if _dk in mems:
		if _dk in _python_resolve_module_func_params(mod):
			return 'func'
		return mems[_dk]
	fp = _python_resolve_module_func_params(mod)
	imports = fp.get('@imports', {})
	if '@bases:' + class_name not in fp and class_name in imports and imports[class_name][1] is not None:
		return _python_resolve_module_member_kind(imports[class_name][0], imports[class_name][1], member, seen)
	for base in fp.get('@bases:' + class_name, []):
		bparts = base.split('.')
		if len(bparts) == 1:
			if '@bases:' + base in fp:
				_r = _python_resolve_module_member_kind(mod, base, member, seen)
				if _r is not None:
					return _r
			elif base in imports and imports[base][1] is not None:
				_r = _python_resolve_module_member_kind(imports[base][0], imports[base][1], member, seen)
				if _r is not None:
					return _r
		else:
			broot = bparts[0]
			if broot in imports:
				bmod = imports[broot][0]
				full_mod = '.'.join([bmod] + bparts[1:-1]) if len(bparts) > 2 else bmod
				_r = _python_resolve_module_member_kind(full_mod, bparts[-1], member, seen)
				if _r is not None:
					return _r
	return None
def _python_resolve_module_method(mod, class_name, method, seen = None):
	if seen is None:
		seen = set()
	key = (mod, class_name)
	if key in seen:
		return False, None
	seen.add(key)
	fp = _python_resolve_module_func_params(mod)
	if f'{class_name}.{method}' in fp:
		return True, fp[f'{class_name}.{method}']
	imports = fp.get('@imports', {})
	if '@bases:' + class_name not in fp and class_name in imports and imports[class_name][1] is not None:
		return _python_resolve_module_method(imports[class_name][0], imports[class_name][1], method, seen)
	for base in fp.get('@bases:' + class_name, []):
		bparts = base.split('.')
		if len(bparts) == 1:
			if '@bases:' + base in fp:
				ok, params = _python_resolve_module_method(mod, base, method, seen)
				if ok:
					return True, params
			elif base in imports:
				bmod, bname = imports[base]
				if bname is not None:
					ok, params = _python_resolve_module_method(bmod, bname, method, seen)
					if ok:
						return True, params
		else:
			broot = bparts[0]
			if broot in imports:
				bmod = imports[broot][0]
				full_mod = '.'.join([bmod] + bparts[1:-1]) if len(bparts) > 2 else bmod
				ok, params = _python_resolve_module_method(full_mod, bparts[-1], method, seen)
				if ok:
					return True, params
	return False, None
_python_module_class_members_cache = {}
def _python_resolve_module_class_members(mod, class_name, seen = None):
	_top_call = seen is None
	if _top_call and (mod, class_name) in _python_module_class_members_cache:
		return _python_module_class_members_cache[(mod, class_name)]
	if seen is None:
		seen = set()
	key = (mod, class_name)
	if key in seen:
		return {}
	seen.add(key)
	mems = _python_resolve_module_members(mod)
	prefix = class_name + '.'
	out = {k[len(prefix):]: v for k, v in mems.items() if k.startswith(prefix) and '.' not in k[len(prefix):]}
	fp = _python_resolve_module_func_params(mod)
	for _mk in out:
		if prefix + _mk in fp:
			out[_mk] = 'func'
	imports = fp.get('@imports', {})
	if '@bases:' + class_name not in fp and class_name in imports and imports[class_name][1] is not None:
		for k, v in _python_resolve_module_class_members(imports[class_name][0], imports[class_name][1], seen).items():
			out.setdefault(k, v)
	for base in fp.get('@bases:' + class_name, []):
		bparts = base.split('.')
		if len(bparts) == 1:
			if '@bases:' + base in fp:
				for k, v in _python_resolve_module_class_members(mod, base, seen).items():
					out.setdefault(k, v)
			elif base in imports and imports[base][1] is not None:
				for k, v in _python_resolve_module_class_members(imports[base][0], imports[base][1], seen).items():
					out.setdefault(k, v)
		else:
			broot = bparts[0]
			if broot in imports:
				bmod = imports[broot][0]
				full_mod = '.'.join([bmod] + bparts[1:-1]) if len(bparts) > 2 else bmod
				for k, v in _python_resolve_module_class_members(full_mod, bparts[-1], seen).items():
					out.setdefault(k, v)
	if _top_call:
		_python_module_class_members_cache[(mod, class_name)] = out
	return out
def _python_build_scopes(text, gen = None, seed_names = None, seed_types = None, seed_classes = None, seed_aliases = None, seed_origins = None, seed_method_params = None, seed_accepts_any = None):
	def _ck():
		if gen is not None and _python_edit_generation[0] != gen:
			raise _PythonScanCancelled()
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
	builder.visit(tree)
	if seed_names:
		for _sn, _sk in seed_names.items():
			if _sn not in builder.scopes[0]['names']:
				builder.scopes[0]['names'][_sn] = [(0, _sk)]
	if seed_aliases:
		for _sa, _sm in seed_aliases.items():
			builder.module_aliases.setdefault(_sa, _sm)
	if seed_names:
		for _sn, _sk in seed_names.items():
			if _sk == 'module':
				builder.module_aliases.setdefault(_sn, _sn)
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
				for dl, kind in sc['names'][name]:
					if sidx == inner and dl > lineno:
						continue
					if best is None or dl > best[0]:
						best = (dl, kind)
				return best[1] if best is not None else '_local'
			sidx = sc['parent']
		return None
	module_contents = {}
	local_classes = {}
	class_module_origin = dict(seed_origins) if seed_origins else {}
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
	_tw = 0
	for _tn in ast.walk(tree):
		_tw += 1
		if _tw % 2000 == 0:
			_ck()
		if isinstance(_tn, ast.Attribute):
			tree_attributes.append(_tn)
		elif isinstance(_tn, ast.Assign):
			tree_assigns.append(_tn)
		elif isinstance(_tn, ast.ClassDef):
			tree_class_defs.append(_tn)
		elif isinstance(_tn, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
			tree_func_defs.append(_tn)
	_class_def_by_name = {}
	for _tn in tree_class_defs:
		if _tn.name not in _class_def_by_name:
			_class_def_by_name[_tn.name] = _tn
	for scope in builder.scopes:
		for name, defs in scope['names'].items():
			for _, kind in defs:
				if kind == 'class' and name in _class_def_by_name and name not in local_classes:
					try:
						node = _class_def_by_name[name]
						members = _python_inspect_ast_members(node.body)
						for meth in node.body:
							if isinstance(meth, (ast.FunctionDef, ast.AsyncFunctionDef)):
								_fp = meth.args.args[0].arg if meth.args.args else None
								for stmt in ast.walk(meth):
									tgts = stmt.targets if isinstance(stmt, ast.Assign) else ([stmt.target] if isinstance(stmt, (ast.AnnAssign, ast.AugAssign)) else [])
									for tgt in tgts:
										if _fp and isinstance(tgt, ast.Attribute) and isinstance(tgt.value, ast.Name) and tgt.value.id == _fp:
											members.setdefault(tgt.attr, 'var')
						local_classes[name] = members
					except Exception:
						pass
	if seed_classes:
		for _scn, _scm in seed_classes.items():
			local_classes.setdefault(_scn, dict(_scm))
	_ck()
	class_bases = {}
	for node in tree_class_defs:
		if node.name in local_classes:
			bases = []
			for base in node.bases:
				if isinstance(base, ast.Name):
					bases.append(base.id)
				elif isinstance(base, ast.Attribute):
					bases.append(base.attr)
			class_bases[node.name] = bases
	local_class_method_params = {}
	local_class_accepts_any = set()
	for node in tree_class_defs:
		if node.name in local_classes:
			for sub in node.body:
				if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)):
					_margs = list(sub.args.posonlyargs) + list(sub.args.args) + list(sub.args.kwonlyargs)
					_mp = set(a.arg for a in _margs[1:]) | set(a.arg for a in sub.args.kwonlyargs)
					if sub.args.kwarg:
						local_class_accepts_any.add(node.name + '.' + sub.name)
					local_class_method_params[node.name + '.' + sub.name] = _mp
	if seed_method_params:
		for _smk, _smv in seed_method_params.items():
			local_class_method_params.setdefault(_smk, _smv)
	if seed_accepts_any:
		local_class_accepts_any.update(seed_accepts_any)
	for _ in range(10):
		changed = False
		for cls, bases in class_bases.items():
			for base in bases:
				if base in local_classes:
					for k, v in local_classes[base].items():
						if k not in local_classes[cls]:
							local_classes[cls][k] = v
							changed = True
					for _mk in list(local_class_method_params):
						if _mk.startswith(base + '.'):
							_meth = _mk[len(base) + 1:]
							_ck2 = cls + '.' + _meth
							if _ck2 not in local_class_method_params:
								local_class_method_params[_ck2] = local_class_method_params[_mk]
								if _mk in local_class_accepts_any:
									local_class_accepts_any.add(_ck2)
								changed = True
		if not changed:
			break
	_ck()
	for _bname, _bmembers in _PYTHON_BUILTIN_MEMBERS.items():
		local_classes.setdefault(_bname, dict(_bmembers))
	class_type_maps = {}
	for node in tree_class_defs:
		if node.name in local_classes:
			class_type_maps[node.name] = {}
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
	for _sm in builder.module_aliases.values():
		candidate_modules.add(_sm)
	valid_modules = set()
	imported_modules = set()
	for name in candidate_modules:
		spec = _python_find_spec_cached(name)
		if spec is not None:
			valid_modules.add(name)
			imported_modules.add(name)
			members = _python_resolve_module_members(name)
			if members:
				module_contents[name] = members
	_ck()
	for scope_idx, imported_name, top_name, used_name, lineno in builder.import_names:
		if used_name == top_name:
			if top_name in valid_modules:
				builder.scopes[scope_idx]['names'].setdefault(used_name, []).append((lineno, 'module'))
		elif imported_name in valid_modules:
			builder.scopes[scope_idx]['names'].setdefault(used_name, []).append((lineno, 'module'))
	for scope_idx, module_name, imported_name, _orig_name, lineno in builder.from_imports:
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
			elif f'{module_name}.{_orig_name}' in valid_modules or _python_find_spec_cached(f'{module_name}.{_orig_name}') is not None:
				kind = 'module'
				builder.module_aliases[imported_name] = f'{module_name}.{_orig_name}'
			else:
				continue
			builder.scopes[scope_idx]['names'].setdefault(imported_name, []).append((lineno, kind))
	for _, module_name, imported_name, _orig_name, _ in builder.from_imports:
		if not module_name:
			continue
		mc = module_contents.get(module_name, {})
		if imported_name == '*':
			for _wname, _wkind in mc.items():
				if '.' not in _wname and _wkind == 'class' and _wname not in local_classes:
					_wmems = _python_resolve_module_class_members(module_name, _wname)
					if _wmems:
						local_classes[_wname] = _wmems
						class_module_origin[_wname] = (module_name, _wname)
		elif mc.get(_orig_name) == 'class' and imported_name not in local_classes:
			_imp_mems = _python_resolve_module_class_members(module_name, _orig_name)
			if _imp_mems:
				local_classes[imported_name] = _imp_mems
				class_module_origin[imported_name] = (module_name, _orig_name)
	base_to_module = {}
	for _, imported_name, top_name, used_name, _ in builder.import_names:
		if used_name == top_name:
			if top_name in valid_modules:
				base_to_module[used_name] = top_name
		elif imported_name in valid_modules:
			base_to_module[used_name] = imported_name
		elif top_name in valid_modules:
			base_to_module[used_name] = top_name
	for _alias, _full in builder.module_aliases.items():
		if _full in valid_modules:
			base_to_module[_alias] = _full
	for _dsc, _dln, _dname, _dmod in builder.dynamic_imports:
		if _python_find_spec_cached(_dmod) is not None:
			valid_modules.add(_dmod)
			base_to_module[_dname] = _dmod
			builder.module_aliases[_dname] = _dmod
			if _dmod not in module_contents:
				_dmems = _python_resolve_module_members(_dmod)
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
				for _dl, _k in sc['names'][name]:
					if sidx == inner and _dl > lineno:
						continue
					if best is None or _dl > best[0]:
						best = (_dl, _k)
				return best[1] if best is not None else None
			sidx = sc['parent']
		return None
	for _asc, _aln, _aname, _asrc in builder.alias_assigns:
		_srckind = _resolve_name_kind_scope(_asc, _asrc, _aln)
		if _srckind is None and _asrc in _PYTHON_BUILTIN_MEMBERS:
			_srckind = 'class'
		elif _srckind is None and _asrc in _PYTHON_BUILTIN_CALLABLE_NAMES:
			_srckind = 'func'
			if _aname not in builder.func_params and _asrc in _PYTHON_BUILTIN_CALLABLE_PARAMS:
				builder.func_params[_aname] = _PYTHON_BUILTIN_CALLABLE_PARAMS[_asrc]
		if _srckind in ('class', 'func'):
			_anames = builder.scopes[_asc]['names'].setdefault(_aname, [])
			_anames[:] = [(_l, _k) for _l, _k in _anames if not (_l == _aln and _k == 'var')]
			_anames.append((_aln, _srckind))
			if _srckind == 'func' and _asrc in builder.func_params and _aname not in builder.func_params:
				builder.func_params[_aname] = builder.func_params[_asrc]
				if _asrc in builder.func_accepts_any:
					builder.func_accepts_any.add(_aname)
			if _srckind == 'class' and _asrc in local_classes and _aname not in local_classes:
				local_classes[_aname] = local_classes[_asrc]
				class_type_maps[_aname] = class_type_maps.setdefault(_asrc, {})
				if _asrc in class_module_origin:
					class_module_origin[_aname] = class_module_origin[_asrc]
				for _mk in list(local_class_method_params):
					if _mk.startswith(_asrc + '.'):
						_ameth = _mk[len(_asrc) + 1:]
						local_class_method_params[_aname + '.' + _ameth] = local_class_method_params[_mk]
						if _mk in local_class_accepts_any:
							local_class_accepts_any.add(_aname + '.' + _ameth)
	name_module_class = {}
	for _asc, _aln, _aname, _abase, _aattr in builder.attr_alias_assigns:
		_amod = base_to_module.get(_abase)
		if _amod is None or _python_resolve_module_members(_amod).get(_aattr) != 'class':
			continue
		_anames = builder.scopes[_asc]['names'].setdefault(_aname, [])
		_anames[:] = [(_l, _k) for _l, _k in _anames if not (_l == _aln and _k == 'var')]
		_anames.append((_aln, 'class'))
		name_module_class[_aname] = (_amod, _aattr)
		if _aname not in local_classes:
			_amems = _python_resolve_module_class_members(_amod, _aattr)
			if _amems:
				local_classes[_aname] = _amems
			class_module_origin[_aname] = (_amod, _aattr)
	from_func_module = {}
	for _, module_name, imported_name, _orig_name, _fln in builder.from_imports:
		if module_name and imported_name != '*' and module_name in valid_modules:
			_prev = from_func_module.get(imported_name)
			if _prev is None or _fln > _prev[2]:
				from_func_module[imported_name] = (module_name, _orig_name, _fln)
	local_def_lines = {}
	for _dln, _dnm, _dk in builder.def_names:
		local_def_lines.setdefault(_dnm, []).append(_dln)
	def _lookup_module_callable(mod_name, key):
		if mod_name not in valid_modules and _python_find_spec_cached(mod_name) is None:
			return None, None
		fp = _python_resolve_module_func_params(mod_name)
		if key not in fp:
			return None, None
		v = fp[key]
		if v is None:
			return True, None
		return True, v
	def _resolve_through_module(mod_name, rest):
		cur_mod = mod_name
		idx = 0
		while idx < len(rest):
			seg = rest[idx]
			sub_full = cur_mod + '.' + seg
			if sub_full in valid_modules or _python_find_spec_cached(sub_full) is not None:
				cur_mod = sub_full
				idx += 1
				continue
			mems = _python_resolve_module_members(cur_mod)
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
			_imp = from_func_module.get(root)
			_imp_line = _imp[2] if _imp is not None and _imp[2] <= lineno else None
			if _local_line is not None and (_imp_line is None or _local_line >= _imp_line):
				if root in builder.func_accepts_any:
					return True, None
				return True, builder.func_params.get(root, set())
			if _imp_line is not None and kind in ('func', 'module', None):
				return _lookup_module_callable(_imp[0], _imp[1])
			if kind is None and root in _PYTHON_BUILTIN_CALLABLE_NAMES:
				return True, _PYTHON_BUILTIN_CALLABLE_PARAMS.get(root, set())
			if kind == 'func' and root in builder.func_params:
				if root in builder.func_accepts_any:
					return True, None
				return True, builder.func_params.get(root, set())
			return None, None
		if root in base_to_module and _call_name_kind(root, lineno) in ('module', None):
			return _resolve_through_module(base_to_module[root], rest)
		return None, None
	_ck()
	module_literals = [(lineno, name) for lineno, name in builder.module_literals if name in valid_modules]
	import_dotted_lines = [(lineno, col, dotted) for lineno, col, dotted in builder.import_dotted_lines if dotted in valid_modules or _python_find_spec_cached(dotted) is not None]
	import_orig_name_tags = []
	_kind_to_tag = {'func': 'hpf', 'class': 'hpx', 'var': 'hpv', 'module': 'hpm'}
	for _oln, _ocol, _oname, _omod in builder.import_orig_names:
		if not _omod or _omod not in valid_modules:
			continue
		_okind = None
		if f'{_omod}.{_oname}' in valid_modules or _python_find_spec_cached(f'{_omod}.{_oname}') is not None:
			_okind = 'module'
		else:
			_ocontents = module_contents.get(_omod) or _python_resolve_module_members(_omod)
			_okind = _ocontents.get(_oname)
		_otag = _kind_to_tag.get(_okind)
		if _otag is not None:
			import_orig_name_tags.append((_oln, _ocol, _oname, _otag))
	_from_import_map = {}
	for _, module_name, imported_name, _orig_name, _ in builder.from_imports:
		if module_name and imported_name != '*':
			_from_import_map[imported_name] = module_name
	_ck()
	scope_var_types = {}
	if seed_types:
		for _stn, _stt in seed_types.items():
			if _stt in local_classes:
				scope_var_types.setdefault(0, {}).setdefault(_stn, []).append((0, _stt))
	_var_type_alias_assigns = []
	for node in tree_assigns:
		for tgt in node.targets:
			if not isinstance(tgt, ast.Name):
				continue
			val = node.value
			type_name = None
			if isinstance(val, ast.Call):
				func = val.func
				mod_name = None
				if isinstance(func, ast.Name):
					type_name = func.id
					mod_name = _from_import_map.get(type_name)
				elif isinstance(func, ast.Attribute):
					type_name = func.attr
					mod_name = base_to_module.get(func.value.id) if isinstance(func.value, ast.Name) else None
				if type_name and type_name not in local_classes and mod_name:
					if _python_resolve_module_members(mod_name).get(type_name) == 'class':
						class_module_origin[type_name] = (mod_name, type_name)
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
			if type_name and (type_name in local_classes or type_name in class_module_origin):
				sc_idx = _scope_for_line(node.lineno)
				if sc_idx is not None:
					scope_var_types.setdefault(sc_idx, {}).setdefault(tgt.id, []).append((node.lineno, type_name))
	for _valn, _vatgt, _vasrc in sorted(_var_type_alias_assigns):
		_vsc = _scope_for_line(_valn)
		_scur = _vsc
		_vtype = None
		while _scur is not None and _vtype is None:
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
			_scur = builder.scopes[_scur]['parent']
		if _vtype is not None and _vsc is not None:
			scope_var_types.setdefault(_vsc, {}).setdefault(_vatgt, []).append((_valn, _vtype))
	_ck()
	for cls_node in tree_class_defs:
		for meth in cls_node.body:
			if not isinstance(meth, (ast.FunctionDef, ast.AsyncFunctionDef)):
				continue
			_fp = meth.args.args[0].arg if meth.args.args else None
			if not _fp:
				continue
			for stmt in ast.walk(meth):
				if not isinstance(stmt, ast.Assign):
					continue
				for tgt in stmt.targets:
					if not (isinstance(tgt, ast.Attribute) and isinstance(tgt.value, ast.Name) and tgt.value.id == _fp):
						continue
					val = stmt.value
					type_name = None
					if isinstance(val, ast.Call):
						func = val.func
						mod_name = None
						if isinstance(func, ast.Name):
							type_name = func.id
							mod_name = _from_import_map.get(type_name)
						elif isinstance(func, ast.Attribute):
							type_name = func.attr
							mod_name = base_to_module.get(func.value.id) if isinstance(func.value, ast.Name) else None
						if type_name and type_name not in local_classes and mod_name:
							mems = _python_resolve_module_class_members(mod_name, type_name)
							if mems:
								local_classes[type_name] = mems
								class_module_origin[type_name] = (mod_name, type_name)
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
						class_type_maps.setdefault(cls_node.name, {})[tgt.attr] = type_name
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
				for tgt in stmt.targets:
					if isinstance(tgt, ast.Name):
						class_type_maps.setdefault(cls_node.name, {})[tgt.id] = type_name
	_ck()
	_ck()
	method_fp_ranges = []
	for _cnode in tree_class_defs:
		if _cnode.name in local_classes:
			for _meth in _cnode.body:
				if isinstance(_meth, (ast.FunctionDef, ast.AsyncFunctionDef)) and _meth.args.args:
					method_fp_ranges.append((_meth.lineno, getattr(_meth, 'end_lineno', _meth.lineno), _meth.args.args[0].arg, _cnode.name))
	def _fp_class_at(name, lineno):
		best = None
		for ms, me, fp, cn in method_fp_ranges:
			if ms <= lineno <= me and name == fp and (best is None or ms > best[0]):
				best = (ms, cn)
		return best[1] if best else None
	def _var_type_at(name, lineno):
		sidx = _scope_for_line(lineno)
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
	def _assign_type_name(val):
		if isinstance(val, ast.Call):
			func = val.func
			if isinstance(func, ast.Name):
				return func.id if func.id in local_classes else None
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
		_mm = _python_resolve_module_members(mod)
		_k = _mm.get(attr)
		if _k is not None:
			return _k
		_dk = dynamic_module_attrs.get(mod, {}).get(attr)
		if _dk is not None:
			return _dk
		_sub = f'{mod}.{attr}'
		if _sub in valid_modules:
			return 'module'
		_spec = _python_find_spec_cached(mod)
		if _spec is not None and getattr(_spec, 'submodule_search_locations', None) and _python_find_spec_cached(_sub) is not None:
			return 'module'
		return None
	def _infer_type(node):
		if isinstance(node, ast.Name):
			fpc = _fp_class_at(node.id, node.lineno)
			if fpc is not None:
				return ('instance', fpc)
			vt = _var_type_at(node.id, node.lineno)
			if vt is not None:
				if vt in class_module_origin and vt not in local_classes:
					return ('minstance', class_module_origin[vt][0], class_module_origin[vt][1])
				return ('instance', vt)
			if node.id in class_module_origin and _call_name_kind(node.id, node.lineno) == 'class':
				return ('modclass', class_module_origin[node.id][0], class_module_origin[node.id][1])
			if node.id in local_classes:
				return ('class', node.id)
			if node.id in base_to_module and _call_name_kind(node.id, node.lineno) == 'module':
				return ('module', base_to_module[node.id])
			return None
		_lt = _literal_type(node)
		if _lt is not None and _lt in local_classes:
			return ('instance', _lt)
		if isinstance(node, ast.Call):
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
			if r[0] == 'module':
				_mk = _module_attr_kind(r[1], node.attr)
				if _mk == 'module':
					_tgt = _python_resolve_module_members(r[1]).get('@modtarget:' + node.attr)
					return ('module', _tgt if _tgt is not None else f'{r[1]}.{node.attr}')
				if _mk == 'class':
					return ('modclass', r[1], node.attr)
				_dmt = dynamic_module_attr_types.get(r[1], {}).get(node.attr)
				if _dmt is not None and _dmt in local_classes:
					return ('instance', _dmt)
				return None
			if r[0] in ('modclass', 'minstance'):
				_dt = dynamic_class_attr_types.get(r[2], {}).get(node.attr)
				if _dt is None and r[0] == 'modclass':
					_dt = dynamic_modclass_attr_types.get(r[2], {}).get(node.attr)
				if _dt is not None and _dt in local_classes:
					return ('instance', _dt)
				return None
			members = local_classes.get(r[1], {})
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
	for _an in tree_assigns:
		for _atgt in _an.targets:
			if not isinstance(_atgt, ast.Attribute):
				continue
			_atn = _assign_type_name(_an.value)
			if isinstance(_atgt.value, ast.Name) and _call_name_kind(_atgt.value.id, _an.lineno) == 'class' and _atgt.value.id in local_classes and _atgt.value.id not in class_module_origin:
				local_classes[_atgt.value.id].setdefault(_atgt.attr, 'var')
				if _atn is not None and _atn in local_classes:
					class_type_maps.setdefault(_atgt.value.id, {})[_atgt.attr] = _atn
				continue
			_br = _infer_type(_atgt.value)
			if _br is None:
				continue
			if _br[0] == 'module':
				dynamic_module_attrs.setdefault(_br[1], {})[_atgt.attr] = 'var'
				if _atn is not None and _atn in local_classes:
					dynamic_module_attr_types.setdefault(_br[1], {})[_atgt.attr] = _atn
			elif _br[0] == 'modclass':
				dynamic_modclass_attrs.setdefault(_br[2], {})[_atgt.attr] = 'var'
				if _atn is not None and _atn in local_classes:
					dynamic_modclass_attr_types.setdefault(_br[2], {})[_atgt.attr] = _atn
			elif _br[0] == 'minstance':
				dynamic_class_attrs.setdefault(_br[2], {})[_atgt.attr] = 'var'
				if _atn is not None and _atn in local_classes:
					dynamic_class_attr_types.setdefault(_br[2], {})[_atgt.attr] = _atn
			elif _br[0] == 'class' and _br[1] in class_module_origin:
				_ocls = class_module_origin[_br[1]][1]
				dynamic_modclass_attrs.setdefault(_ocls, {})[_atgt.attr] = 'var'
				if _atn is not None and _atn in local_classes:
					dynamic_modclass_attr_types.setdefault(_ocls, {})[_atgt.attr] = _atn
			elif _br[0] == 'class' and _br[1] in local_classes:
				local_classes[_br[1]].setdefault(_atgt.attr, 'var')
				if _atn is not None and _atn in local_classes:
					class_type_maps.setdefault(_br[1], {})[_atgt.attr] = _atn
			elif _br[0] == 'instance' and _br[1] in local_classes:
				dynamic_class_attrs.setdefault(_br[1], {})[_atgt.attr] = 'var'
				if _atn is not None and _atn in local_classes:
					dynamic_class_attr_types.setdefault(_br[1], {})[_atgt.attr] = _atn
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
			_k = _python_resolve_module_member_kind(r[1], r[2], node.attr)
			if _k is None and r[0] == 'minstance':
				_k = dynamic_class_attrs.get(r[2], {}).get(node.attr)
			if _k is None and r[0] == 'modclass':
				_k = dynamic_modclass_attrs.get(r[2], {}).get(node.attr)
		else:
			_k = local_classes.get(r[1], {}).get(node.attr)
			if _k is None and r[0] == 'instance':
				_k = dynamic_class_attrs.get(r[1], {}).get(node.attr)
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
			_bmod = base_to_module.get(_fn.value.id)
			if _bmod is not None and _python_resolve_module_members(_bmod).get(_fn.attr) == 'class':
				_cmod = _bmod
				_ccls = _fn.attr
		elif isinstance(_fn, ast.Name) and _fn.id in from_func_module:
			_fm, _forig, _ = from_func_module[_fn.id]
			if _python_resolve_module_members(_fm).get(_forig) == 'class':
				_cmod = _fm
				_ccls = _forig
		elif isinstance(_fn, ast.Name) and _fn.id in name_module_class:
			_cmod, _ccls = name_module_class[_fn.id]
		if _cmod is None:
			continue
		_vsc = _scope_for_line(_vn.lineno)
		for _t in _vn.targets:
			if isinstance(_t, ast.Name):
				var_module_class.setdefault((_vsc, _t.id), []).append((_vn.lineno, _cmod, _ccls))
	def _var_modclass_at(name, lineno):
		sidx = _scope_for_line(lineno)
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
				found, mp = _python_resolve_module_method(_mc[0], _mc[1], func_name)
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
					elif _lcls in class_module_origin:
						found, mp = _python_resolve_module_method(class_module_origin[_lcls][0], class_module_origin[_lcls][1], func_name)
						if found:
							ok, params = True, mp
		if not ok and isinstance(_cnode.func, ast.Attribute):
			_rcv = _infer_type(_cnode.func.value)
			if _rcv is not None:
				if _rcv[0] in ('modclass', 'minstance'):
					found, mp = _python_resolve_module_method(_rcv[1], _rcv[2], func_name)
					if found:
						ok, params = True, mp
				elif _rcv[0] == 'module':
					_mok, _mp = _lookup_module_callable(_rcv[1], func_name)
					if _mok:
						ok, params = _mok, _mp
				elif _rcv[0] in ('instance', 'class'):
					_lkey = _rcv[1] + '.' + func_name
					if _lkey in local_class_accepts_any:
						ok, params = True, None
					elif _lkey in local_class_method_params:
						ok, params = True, local_class_method_params[_lkey]
					elif _rcv[1] in class_module_origin:
						found, mp = _python_resolve_module_method(class_module_origin[_rcv[1]][0], class_module_origin[_rcv[1]][1], func_name)
						if found:
							ok, params = True, mp
		if ok and (params is None or kwarg_name in params):
			call_kwargs.setdefault(lineno, set()).add(kwarg_name)
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
				for dl, kind in sc['names'][name]:
					if sidx == inner and dl > lineno:
						continue
					if best is None or dl > best[0]:
						best = (dl, kind)
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
	return builder.scopes, call_kwargs, builder.module_aliases, local_classes, module_literals, scope_var_types, literal_attrs, builder.def_names, typed_attrs, param_default_tags, builder.kwarg_positions, import_dotted_lines, import_orig_name_tags, class_module_origin, local_class_method_params, local_class_accepts_any
def _python_scan_names(text, gen = None):
	global _python_scopes
	global _python_call_kwargs
	global _python_module_literals
	global _python_literal_attrs
	global _python_def_names
	global _python_typed_attrs
	global _python_param_default_tags
	global _python_kwarg_positions, _python_import_dotted_lines, _python_import_orig_name_tags
	result = _python_build_scopes(text, gen)
	if result is not None:
		scopes, call_kwargs, module_aliases, local_classes, module_literals, scope_var_types, literal_attrs, def_names, typed_attrs, param_default_tags, kwarg_positions, import_dotted_lines, import_orig_name_tags, class_module_origin, local_class_method_params, local_class_accepts_any = result
		_python_scopes = scopes
		_python_call_kwargs = call_kwargs
		_python_module_literals = module_literals
		_python_literal_attrs = literal_attrs
		_python_def_names = def_names
		_python_typed_attrs = typed_attrs
		_python_param_default_tags = param_default_tags
		_python_kwarg_positions = kwarg_positions
		_python_import_dotted_lines = import_dotted_lines
		_python_import_orig_name_tags = import_orig_name_tags
		_main_queue.put(lambda: ha('python') if hmode == 'python' else None)
def _python_scan_start():
	global _python_names_scan_thread
	global _python_scan_after_id
	_python_scan_after_id = None
	if _python_names_scan_thread is not None and _python_names_scan_thread.is_alive():
		_python_scan_after_id = type_.after(10, _python_scan_start)
		return
	def _get_and_scan():
		gen = _python_edit_generation[0]
		text = type_.get('1.0', 'end')
		try:
			_python_scan_names(text, gen)
		except _PythonScanCancelled:
			pass
	_python_names_scan_thread = threading.Thread(target = _get_and_scan, daemon = True)
	_python_names_scan_thread.start()
def _update_filesize():
	global filesize
	size = len(io.StringIO(type_.get('1.0', 'end')).read()) - 1
	filesize.config(text = str(size) + ' bytes')
def trigger_filesize():
	global _filesize_after_id
	if _filesize_after_id is not None:
		type_.after_cancel(_filesize_after_id)
	_filesize_after_id = type_.after(debounce_time, _update_filesize)
def _update_unsaved():
	global unsaved, title, pcsettitle
	if title and not hmode in ['png', 'pdf', 'epub']:
		if type_.get('1.0', 'end-1c') != unsavedtext:
			unsaved = True
			if title and not pcsettitle:
				root.title('PyNotes - ' + os.path.basename(title) + ' *')
		else:
			unsaved = False
			if title and not pcsettitle:
				root.title('PyNotes - ' + os.path.basename(title))
def trigger_unsaved():
	global _unsaved_after_id
	if _unsaved_after_id is not None:
		type_.after_cancel(_unsaved_after_id)
	_unsaved_after_id = type_.after(debounce_time, _update_unsaved)
def trigger_ha(ft):
	global _ha_after_id
	if _ha_after_id is not None:
		type_.after_cancel(_ha_after_id)
	_ha_after_id = type_.after(debounce_time, lambda: ha(ft))
def python_trigger_name_scan():
	global _python_scan_after_id
	if _python_scan_after_id is not None:
		type_.after_cancel(_python_scan_after_id)
	_python_scan_after_id = type_.after(debounce_time, _python_scan_start)
def ha(ft):
	if _ha_running[0]:
		_ha_pending[0] = ft
		return
	_ha_running[0] = True
	text = type_.get(type_top, type_bottom)
	top = type_top
	bottom = type_bottom
	pre_text = type_.get('1.0', type_top)
	python_scopes = _python_scopes
	python_call_kwargs = _python_call_kwargs
	python_module_literals = _python_module_literals
	python_def_names = _python_def_names
	python_typed_attrs = _python_typed_attrs
	python_param_default_tags = _python_param_default_tags
	python_kwarg_positions = _python_kwarg_positions
	python_import_dotted_lines = _python_import_dotted_lines
	python_import_orig_name_tags = _python_import_orig_name_tags
	def do_hl():
		ops = []
		try:
			ops.append(('remove_all',))
			if ft == 'python':
				for m in _PYTHON_KW_PAT.finditer(text):
					ops.append(('add', 'hpa', f'{top}+{m.start()}c', f'{top}+{m.end()}c'))
				for m in _PYTHON_BI_PAT.finditer(text):
					ops.append(('add', 'hpb', f'{top}+{m.start()}c', f'{top}+{m.end()}c'))
				top_line = int(top.split('.')[0])
				line_scopes = {}
				for line in range(top_line, top_line + len(text.split('\n'))):
					for k, sc in enumerate(python_scopes):
						if sc['start'] <= line <= sc['end']:
							if line not in line_scopes or sc['start'] >= python_scopes[line_scopes[line]]['start']:
								line_scopes[line] = k
				module_literal_lines = {}
				for lineno, name in python_module_literals:
					module_literal_lines.setdefault(lineno, []).append(name)
				import_dotted_by_line = {}
				for lineno, dcol, dotted in python_import_dotted_lines:
					import_dotted_by_line.setdefault(lineno, []).append((dcol, dotted))
				import_orig_by_line = {}
				for _oln, _ocol, _oname, _otag in python_import_orig_name_tags:
					import_orig_by_line.setdefault(_oln, []).append((_ocol, _oname, _otag))
				def_names_by_line = {}
				for _dl, _dname, _dkind in python_def_names:
					def_names_by_line.setdefault(_dl, []).append((_dname, _dkind))
				python_literal_attrs = _python_literal_attrs
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
				offset = 0
				for li, line_str in enumerate(text.split('\n')):
					abs_line = top_line + li
					active = {}
					prior_kinds = {}
					bound = set()
					scope_idx = line_scopes.get(abs_line)
					innermost_scope = scope_idx
					innermost_parent = python_scopes[innermost_scope]['parent'] if innermost_scope is not None else None
					on_header = innermost_scope is not None and abs_line == python_scopes[innermost_scope]['start']
					while scope_idx is not None:
						sc = python_scopes[scope_idx]
						if sc.get('kind') == 'class' and scope_idx != innermost_scope and not (on_header and scope_idx == innermost_parent):
							scope_idx = sc['parent']
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
							earliest = None
							for dl, kind in defs:
								if earliest is None or dl < earliest[0]:
									earliest = (dl, kind)
								if scope_idx == innermost_scope and dl > abs_line:
									continue
								if best is None or dl > best[0]:
									second_best = best
									best = (dl, kind)
								elif second_best is None or dl > second_best[0]:
									second_best = (dl, kind)
							if best is None:
								best = earliest
							bound.add(name)
							if best is not None:
								active[name] = best[1]
								if best[0] == abs_line and second_best is not None and second_best[1] != best[1]:
									prior_kinds[name] = second_best[1]
						scope_idx = sc['parent']
					groups = {}
					for name, kind in active.items():
						groups.setdefault(prior_kinds.get(name, kind), []).append(name)
					for kind, names_list in groups.items():
						if not names_list:
							continue
						tag = {'var': 'hpv', 'func': 'hpf', 'func_arg': 'hpfa', 'first_param': 'hpb', 'module': 'hpm', 'class': 'hpx'}.get(kind)
						if tag is None:
							continue
						pat = re.compile(_PYTHON_NAME_LEAD + r'(?:' + '|'.join(re.escape(nm) for nm in names_list) + r')' + _PYTHON_NAME_TRAIL)
						for m in pat.finditer(line_str):
							ops.append(('add', tag, f'{top}+{offset + m.start()}c', f'{top}+{offset + m.end()}c'))
					for name in prior_kinds:
						new_tag = {'var': 'hpv', 'func': 'hpf', 'func_arg': 'hpfa', 'first_param': 'hpb', 'module': 'hpm', 'class': 'hpx'}.get(active[name])
						if new_tag is None:
							continue
						m = re.search(_PYTHON_NAME_LEAD + re.escape(name) + _PYTHON_NAME_TRAIL, line_str)
						if m:
							s = f'{top}+{offset + m.start()}c'
							e = f'{top}+{offset + m.end()}c'
							ops.append(('clear_other', s, e))
							ops.append(('add', new_tag, s, e))
					for _dname, _dkind in def_names_by_line.get(abs_line, []):
						_dm = re.match(r'\s*(?:async\s+)?def\s+(' + re.escape(_dname) + r')\b', line_str) if _dkind == 'func' else re.match(r'\s*class\s+(' + re.escape(_dname) + r')\b', line_str)
						if _dm:
							s = f'{top}+{offset + _dm.start(1)}c'
							e = f'{top}+{offset + _dm.end(1)}c'
							ops.append(('clear_other', s, e))
							ops.append(('add', 'hpf' if _dkind == 'func' else 'hpx', s, e))
					for _pcol, _pname, _pkind in param_default_by_line.get(abs_line, []):
						_pcol = _python_bytecol_to_charcol(line_str, _pcol)
						_ptag = {'var': 'hpv', 'func': 'hpf', 'func_arg': 'hpfa', 'first_param': 'hpb', 'module': 'hpm', 'class': 'hpx'}.get(_pkind)
						if _ptag is not None:
							s = f'{top}+{offset + _pcol}c'
							e = f'{top}+{offset + _pcol + len(_pname)}c'
							ops.append(('clear_other', s, e))
							ops.append(('add', _ptag, s, e))
					for name in module_literal_lines.get(abs_line, []):
						lit_pat = re.compile(_PYTHON_NAME_LEAD + re.escape(name) + _PYTHON_NAME_TRAIL)
						for m in lit_pat.finditer(line_str):
							ops.append(('add', 'hpm', f'{top}+{offset + m.start()}c', f'{top}+{offset + m.end()}c'))
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
						_ttag = {'func': 'hpf', 'var': 'hpv', 'module': 'hpm', 'class': 'hpx'}.get(_tkind, 'hpx')
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
					ops.append(('clear_other', s, e))
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
					ops.append(('clear_other', f'{top}+0c', f'{top}+{j}c'))
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
					ops.append(('clear_other', f'{top}+0c', f'{top}+{j}c'))
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
						ops.append(('clear_other', f'{top}+{i}c', f'{top}+{j}c'))
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
						ops.append(('clear_other', f'{top}+{i}c', f'{top}+{j}c'))
						ops.append(('add', 'hpd', f'{top}+{i}c', f'{top}+{j}c'))
						i = j
					elif ch == '#':
						j = i + 1
						while j < n and text[j] != '\n':
							j += 1
						if j < n:
							j += 1
						ops.append(('clear_other', f'{top}+{i}c', f'{top}+{j}c'))
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
					region = type_.get(f'1.0+{outer_start}c', bottom)
					env_pat = re.compile(r'\\(begin|end)\{\s*' + re.escape(outer_name) + r'\s*\}')
					m0 = env_pat.match(region)
					depth = 1
					search_from = m0.end() if m0 else len(region)
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
					ops.append(('add', 'hlb', f'1.0+{outer_start}c', f'1.0+{end_abs}c'))
					scan_from = max(0, end_abs - pre_n)
				tn = len(text)
				for begin_m in re.finditer(r'\\begin\{\s*(\w+\*?)\s*\}', text[scan_from:]):
					if begin_m.group(1) == 'document':
						continue
					env_name = re.escape(begin_m.group(1))
					bstart = scan_from + begin_m.start()
					search_from2 = scan_from + begin_m.end()
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
					ops.append(('clear_other', s, e))
					ops.append(('add', 'hlh', s, e))
			elif ft == 'html':
				last_open = pre_text.rfind('<!--')
				last_close = pre_text.rfind('-->')
				if last_open != -1 and last_close < last_open:
					close_pos = text.find('-->')
					j = (close_pos + 3) if close_pos != -1 else len(text)
					ops.append(('clear_other', f'{top}+0c', f'{top}+{j}c'))
					ops.append(('add', 'hcmt', f'{top}+0c', f'{top}+{j}c'))
				for m in _HC_PAT.finditer(text):
					s = f'{top}+{m.start()}c'
					e = f'{top}+{m.end()}c'
					ops.append(('clear_other', s, e))
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
					ops.append(('clear_other', f'{top}+0c', f'{top}+{j}c'))
					ops.append(('add', 'hcmt', f'{top}+0c', f'{top}+{j}c'))
				for m in _HC_PAT.finditer(text):
					s = f'{top}+{m.start()}c'
					e = f'{top}+{m.end()}c'
					ops.append(('clear_other', s, e))
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
					ops.append(('clear_other', s, e))
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
					ops.append(('clear_other', s, e))
					ops.append(('add', 'hmc', s, e))
				for m in _MDL_PAT.finditer(text):
					s = f'{top}+{m.start()}c'
					e = f'{top}+{m.end()}c'
					ops.append(('clear_other', s, e))
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
					ops.append(('clear_other', f'{top}+0c', f'{top}+{j}c'))
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
						ops.append(('clear_other', f'{top}+{i}c', f'{top}+{k}c'))
						ops.append(('add', 'hmf', f'{top}+{i}c', f'{top}+{k}c'))
						i = k
					else:
						i += 1
		except Exception:
			pass
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
						msg = f'There was an error in running the function "{func}" before syntax highlighting by the plugin "{plugin_name}":\n{error}'
						_main_queue.put(lambda msg = msg: root.error('Error', msg))
				try:
					cond_result = bool(eval(cond, globals()))
				except Exception as error:
					msg = f'There was an error in evaluating the condition "{cond}" for syntax highlighting by the plugin "{plugin_name}":\n{error}'
					_main_queue.put(lambda msg = msg: root.error('Error', msg))
					cond_result = False
				if cond_result:
					try:
						hl_value = eval(hl, globals())
					except Exception as error:
						msg = f'There was an error in syntax highlighting of the plugin "{plugin_name}":\n{error}'
						_main_queue.put(lambda msg = msg: root.error('Error', msg))
						hl_value = {}
					if callable(hl_value):
						try:
							hl_value(text, top, ops)
						except Exception as error:
							msg = f'There was an error in syntax highlighting of the plugin "{plugin_name}":\n{error}'
							_main_queue.put(lambda msg = msg: root.error('Error', msg))
					else:
						for tag, (pat, theme_key) in hl_value.items():
							try:
								for m in pat.finditer(text):
									ops.append(('add', tag, f'{top}+{m.start()}c', f'{top}+{m.end()}c'))
								ops.append(('config', tag, theme[theme_key]))
							except Exception as error:
								msg = f'There was an error in syntax highlighting of the plugin "{plugin_name}":\n{error}'
								_main_queue.put(lambda msg = msg: root.error('Error', msg))
				elif else_fn is not None:
					try:
						exec(else_fn, globals())
					except Exception as error:
						msg = f'There was an error in running the else block in the syntax highlighting of the plugin "{plugin_name}":\n{error}'
						_main_queue.put(lambda msg = msg: root.error('Error', msg))
			elif callable(entry):
				try:
					entry(text, top, ops)
				except Exception as error:
					msg = f'There was an error in syntax highlighting of the plugin "{plugin_name}":\n{error}'
					_main_queue.put(lambda msg = msg: root.error('Error', msg))
			else:
				for tag, (pat, theme_key) in entry.items():
					try:
						for m in pat.finditer(text):
							ops.append(('add', tag, f'{top}+{m.start()}c', f'{top}+{m.end()}c'))
					except Exception as error:
						msg = f'There was an error in syntax highlighting of the plugin "{plugin_name}":\n{error}'
						_main_queue.put(lambda msg = msg: root.error('Error', msg))
		_main_queue.put(lambda: _finish_ha(ops))
	def _finish_ha(ops):
		def _done():
			_ha_running[0] = False
			pending = _ha_pending[0]
			if pending is not None:
				_ha_pending[0] = None
				ha(pending)
		try:
			if type_.get(top, bottom) != text:
				_done()
				return
			all_tags = set(type_.tag_names())
			_HA_CHUNK_SIZE = 4000
			def _apply_chunk(start):
				try:
					end = min(start + _HA_CHUNK_SIZE, len(ops))
					for op in ops[start:end]:
						if op[0] == 'remove_all':
							for tag in all_tags:
								if tag not in _PYTHON_EDITOR_HL_SKIP_REMOVE_TAGS and (tag not in skiptags or hmode not in skiptags[tag]):
									type_.tag_remove(tag, top, bottom)
						elif op[0] == 'add':
							type_.tag_add(op[1], op[2], op[3])
						elif op[0] == 'remove':
							type_.tag_remove(op[1], op[2], op[3])
						elif op[0] == 'config':
							exec("type_.tag_config('" + op[1] + "'," + op[2] + ')')
						elif op[0] == 'clear_other':
							for tag in all_tags:
								if tag in _PYTHON_EDITOR_HL_SKIP_REMOVE_TAGS or (tag in skiptags and hmode in skiptags[tag]):
									continue
								type_.tag_remove(tag, op[1], op[2])
					if end < len(ops):
						root.after(0, lambda: _apply_chunk(end))
					else:
						_done()
				except Exception as error:
					root.error('Error!', f'Error:{error}\nInvalid colour settings.\nQuitting syntax highlighting.')
					_done()
			_apply_chunk(0)
		except Exception as error:
			root.error('Error!', f'Error:{error}\nInvalid colour settings.\nQuitting syntax highlighting.')
			_done()
	threading.Thread(target = do_hl, daemon = True).start()
def _main_poll():
	try:
		while True:
			task = _main_queue.get_nowait()
			task()
	except queue.Empty:
		pass
	type_.after(10, _main_poll)
def type_setview():
	global type_top
	global type_bottom
	global _prev_visible_region
	new_region = type_getvisible()
	if new_region != _prev_visible_region:
		_prev_visible_region = new_region
		type_top, type_bottom = new_region
		trigger_ha(hmode)
	else:
		type_top, type_bottom = new_region
	root.after(10, type_setview)
def do_backup():
	if all((not hmode in ['png', 'pdf', 'epub'], bfr, title)):
		open(os.path.join(os.path.dirname(os.path.splitext(title)[0]), '.' + os.path.basename(os.path.splitext(title)[0]) + 'backpynotes' + os.path.splitext(title)[1]), 'w+', encoding = 'utf-8').write(type_.get('1.0', 'end'))
		show('saved backup')
	root.after(10000, do_backup)
def keypress():
	global bfr
	global type_
	global tabs
	global unsaved
	global unsavedtext
	_python_edit_generation[0] += 1
	ln.redraw()
	trigger_filesize()
	if hmode == 'python':
		tabs.tab(sf, state = 'normal')
		python_trigger_name_scan()
	else:
		tabs.tab(sf, state = 'hidden')
		trigger_ha(hmode)
	filename.config(text = os.path.basename(title) + ' *')
	if title:
		filename.config(text = os.path.basename(title))
	else:
		if not pcsettitle:
			root.title('PyNotes - Untitled')
		filename.config(text = 'Untitled')
	trigger_unsaved()
	if not title:
		if type_.get('1.0', 'end-1c'):
			unsaved = True
		else:
			unsaved = False
	if hmode in ['png', 'pdf', 'epub']:
		root.title('PyNotes - ' + os.path.basename(title))
def indent():
	type_.edit_separator()
	if not hmode == 'python':
		return
	l = int(type_.index('insert').split('.')[0])
	type_.insert(f'insert', '\n')
	line = type_.get(f'{l}.0', f'{l}.end')
	whitespace = re.match(r'\s*', line).group()
	type_.insert(f'{l + 1}.0', whitespace)
	line = re.sub(r'\'[^\'\\]*(?:\\.[^\'\\]*)*\'|"[^"\\]*(?:\\.[^"\\]*)*"', '', line)
	line = re.sub(r'#.*', '', line).strip()
	if taborspace:
		indentthing = '    '
	else:
		indentthing = '	'
	if not line:
		return 'break'
	if line[-1] == ':':
		type_.insert(f'{l + 1}.0', indentthing)
	type_.edit_separator()
	return 'break'
stoperrors = False
def rp():
	if not globals()['title']:
		os.makedirs(f'{homedir}/.local/share/PyNotes/tempfiles', exist_ok = True)
		f = open(f'{homedir}/.local/share/PyNotes/tempfiles/tempcode', 'w', encoding = 'utf-8')
		f.write(type_.get('1.0', 'end-1c'))
		f.close()
		title = f'{homedir}/.local/share/PyNotes/tempfiles/tempcode'
	else:
		title = globals()['title']
		sv(title)
	term(title)
def hp():
	if not globals()['title']:
		os.makedirs(f'{homedir}/.local/share/PyNotes/tempfiles', exist_ok = True)
		f = open(f'{homedir}/.local/share/PyNotes/tempfiles/tempcode', 'w', encoding = 'utf-8')
		f.write(type_.get('1.0', 'end-1c'))
		f.close()
		title = f'{homedir}/.local/share/PyNotes/tempfiles/tempcode'
	else:
		title = globals()['title']
		sv(title)
	if platform.system() == 'Linux':
		subprocess.run(['xdg-open', title], cwd = os.path.dirname(title))
	else:
		subprocess.run(['start', title], cwd = os.path.dirname(title))
def f5():
	if hmode == 'python':
		rp()
	elif hmode == 'latex':
		runtex('lua')
	elif hmode == 'html':
		hp()
	else:
		show('hmode not in python / latex / html')
		return
	show(f'run {hmode} code')
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
			logtextbox.insert('1.0', open(f'{homedir}/.local/share/PyNotes/tempfiles/{os.path.basename(title)}.log', 'r', encoding = 'utf-8').read())
			logtextbox.config(state = 'disabled')
			logtextboxscroll.config(command = logtextbox.yview)
			logtextboxscroll.pack(fill = 'y', side = 'right')
			logtextbox.pack(fill = 'both', expand = True, side = 'left')
			logwin.style(root.gettheme())
	elif platform.system() == 'Linux':
		subprocess.run(['xdg-open', pdf_], cwd = os.path.dirname(title))
	else:
		subprocess.run(['start', pdf_], cwd = os.path.dirname(title))
def runtex(compiler):
	if not globals()['title']:
		os.makedirs(f'{homedir}/.local/share/PyNotes/tempfiles', exist_ok = True)
		f = open(f'{homedir}/.local/share/PyNotes/tempfiles/tempcode', 'w', encoding = 'utf-8')
		f.write(type_.get('1.0', 'end-1c'))
		f.close()
		title = f'{homedir}/.local/share/PyNotes/tempfiles/tempcode'
	else:
		title = globals()['title']
		sv(title)
	compiler += 'latex'
	if not shutil.which(compiler):
		root.error('Error', f'Error in running LaTeX - {compiler} is not installed')
		return
	if os.path.splitext(title)[1] == '.tex':
		pdf_ = os.path.splitext(title)[0]
	else:
		pdf_ = title
	pdf_ += '.pdf'
	try:
		os.remove(pdf_)
	except Exception:
		pass
	subprocess.run([compiler, '-interaction=nonstopmode', '-halt-on-error', '-file-line-error', title], stdout = open(f'{homedir}/.local/share/PyNotes/tempfiles/{os.path.basename(title)}.log', 'w', encoding = 'utf-8'), stderr = subprocess.STDOUT, cwd = os.path.dirname(title))
	pdf(title)
def rb():
	root.info('Recover Backup', '1. Go to the directory of the lost file\n2. Press Ctrl-h to show hidden files\n3. You will see something like .filebackpynotes.txt\n4. Copy it into the original lost file.\n(This may not be an exact copy)')
def termexec(command):
	if command[:2] == 'cd':
		try:
			os.chdir(command[3:])
		except Exception as error:
			return str(error)
		else:
			return ''
	else:
		try:
			result = subprocess.run(command, shell = True, text = True, capture_output = True, timeout = 5)
			item = result.stdout + result.stderr
		except subprocess.TimeoutExpired:
			item = 'error: time expired'
		except Exception as error:
			item = str(error)
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
_ANSI_16_HEX = ('#000000', '#cd0000', '#00cd00', '#cdcd00', '#0000ee', '#cd00cd', '#00cdcd', '#e5e5e5', '#7f7f7f', '#ff0000', '#00ff00', '#ffff00', '#5c5cff', '#ff00ff', '#00ffff', '#ffffff')
_ANSI_CUBE_LEVELS = (0, 95, 135, 175, 215, 255)
def _ansi_256_hex(n):
	if n < 16:
		return _ANSI_16_HEX[n]
	if n < 232:
		n -= 16
		return f'#{_ANSI_CUBE_LEVELS[n // 36]:02x}{_ANSI_CUBE_LEVELS[(n % 36) // 6]:02x}{_ANSI_CUBE_LEVELS[n % 6]:02x}'
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
		elif c == 1: state['bold'] = True
		elif c == 3: state['italic'] = True
		elif c == 4: state['underline'] = True
		elif c == 7: state['reverse'] = True
		elif c == 22: state['bold'] = False
		elif c == 23: state['italic'] = False
		elif c == 24: state['underline'] = False
		elif c == 27: state['reverse'] = False
		elif 30 <= c <= 37: state['fg'] = c - 30
		elif c == 38:
			if i + 2 < len(params) and params[i + 1] == 5: state['fg'] = params[i + 2]; i += 2
			elif i + 4 < len(params) and params[i + 1] == 2: state['fg'] = (params[i + 2], params[i + 3], params[i + 4]); i += 4
		elif c == 39: state['fg'] = None
		elif 40 <= c <= 47: state['bg'] = c - 40
		elif c == 48:
			if i + 2 < len(params) and params[i + 1] == 5: state['bg'] = params[i + 2]; i += 2
			elif i + 4 < len(params) and params[i + 1] == 2: state['bg'] = (params[i + 2], params[i + 3], params[i + 4]); i += 4
		elif c == 49: state['bg'] = None
		elif 90 <= c <= 97: state['fg'] = c - 90 + 8
		elif 100 <= c <= 107: state['bg'] = c - 100 + 8
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
def term(pythonfile = None):
	if not pythonfile:
		show('open pynotes terminal')
	import queue as _queue
	tw = root.subwin()
	tw.title(pythonfile if pythonfile else 'Terminal')
	term = tw.textbox(font = (monospace, 12), wrap = 'none')
	term.pack(fill = 'both')
	tw.update()
	tw.sizablefalse()
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
	term.tag_configure('sel', background = _term_default_fg, foreground = _term_default_bg)
	term.tag_configure('wrapcont')
	_sgr_tag_cache = [None]
	def _recompute_sgr_tag():
		fg, bg = _term_sgr_resolve(_sgr_state, _term_default_fg, _term_default_bg)
		if _is_default_colour(fg, _default_fg_rgb) and _is_default_colour(bg, _default_bg_rgb) and not _sgr_state['bold'] and not _sgr_state['italic'] and not _sgr_state['underline']:
			_sgr_tag_cache[0] = None
			return
		name = 'sgr_' + (fg.replace('#', '') if fg else 'x') + '_' + (bg.replace('#', '') if bg else 'x')
		if _sgr_state['bold']: name += '_b'
		if _sgr_state['italic']: name += '_i'
		if _sgr_state['underline']: name += '_u'
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
		try: _write(f'\x1b]{which};rgb:{r:04x}/{g:04x}/{b:04x}\x1b\\'.encode())
		except OSError: pass
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
				if value not in _open_tags: _open_tags.append(value)
			elif kind == 'tagoff':
				if value in _open_tags: _open_tags.remove(value)
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
		shell = pythonexecutable if pythonfile else os.environ.get('SHELL', '/bin/bash')
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
		proc = subprocess.Popen([shell, pythonfile] if pythonfile else [shell], stdin = slave_fd, stdout = slave_fd, stderr = slave_fd, close_fds = True, preexec_fn = _term_preexec, env = env)
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
				except OSError:
					break
			running[0] = False
			out_q.put(None)
		def _write(data):
			os.write(master_fd, data)
		def _close():
			running[0] = False
			try:
				while True: out_q.get_nowait()
			except _queue.Empty: pass
			try: proc.terminate()
			except Exception: pass
			try: os.close(master_fd)
			except Exception: pass
			try: tw.destroy()
			except Exception: pass
	else:
		proc = PtyProcess.spawn([pythonexecutable, pythonfile] if pythonfile else 'powershell.exe', dimensions = (24, 80))
		def _read():
			_dec = codecs.getincrementaldecoder('utf-8')(errors = 'replace')
			while running[0]:
				try:
					data = proc.read(4096)
					if data:
						out_q.put(data if isinstance(data, str) else _dec.decode(data))
				except EOFError:
					break
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
			try:
				tw.destroy()
			except Exception:
				pass
	def _vt_sync():
		last = int(term.index('end').split('.')[0]) - 1
		if _cur_line[0] > last:
			term.insert('end', '\n' * (_cur_line[0] - last))
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
				_cur_line[0] += 1
				if _cur_line[0] > screen_top[0] + _VT_ROWS - 1:
					screen_top[0] = _cur_line[0] - (_VT_ROWS - 1)
				_vt_sync()
				term.tag_remove('wrapcont', f'{_cur_line[0]}.0', f'{_cur_line[0]}.end')
				term.mark_set('insert', f'{_cur_line[0]}.{c}')
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
								if p[0] == 0: term.delete('insert', f'{ln}.end')
								elif p[0] == 1: term.delete(f'{ln}.0', 'insert')
								else: term.delete(f'{ln}.0', f'{ln}.end')
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
							elif p[0] == 0:
								term.delete('insert', 'end')
						elif cmd in ('H', 'f'):
							row_ = p[0] if p[0] else 1
							col_ = p[1] if len(p) > 1 and p[1] else 1
							if _alt_mode[0]:
								_grid_goto(row_, col_ - 1)
							else:
								_cur_line[0] = screen_top[0] + row_ - 1
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
								term.mark_set('insert', f'{_cur_line[0]}.{col}')
						elif cmd == 'B':
							mv = p[0] or 1
							if _alt_mode[0]:
								_grid_goto(int(ln) + mv, int(col))
							else:
								_cur_line[0] = int(ln) + mv
								_vt_sync()
								term.mark_set('insert', f'{_cur_line[0]}.{col}')
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
							term.mark_set('insert', f'{ln}.{max(0, int(col) - mv)}')
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
								_cur_line[0] = screen_top[0] + mv - 1
								_vt_sync()
								term.mark_set('insert', f'{_cur_line[0]}.{col}')
						elif cmd == 'P':
							mv = p[0] or 1
							term.delete('insert', f'insert+{mv}c')
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
							if len(p) >= 2 and p[0] and p[1]:
								_scroll_top[0] = min(max(1, p[0]), _GRID_ROWS)
								_scroll_bot[0] = min(max(_scroll_top[0], p[1]), _GRID_ROWS)
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
								term.delete('insert', f'insert+{mv}c')
								term.insert('insert', ' ' * mv)
								term.mark_set('insert', f'insert-{mv}c')
						elif cmd == 'n':
							if p[0] == 6:
								cur_col = int(term.index('insert').split('.')[1])
								row_rep = max(1, _cur_line[0] - screen_top[0] + 1)
								try: _write(f'\x1b[{row_rep};{cur_col + 1}R'.encode())
								except OSError: pass
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
						_cur_line[0] = max(screen_top[0], _cur_line[0] - 1)
						term.mark_set('insert', f'{_cur_line[0]}.{co}')
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
						_cur_line[0] += 1
						if _cur_line[0] > screen_top[0] + _VT_ROWS - 1:
							screen_top[0] = _cur_line[0] - (_VT_ROWS - 1)
						_vt_sync()
						term.mark_set('insert', f'{_cur_line[0]}.{co}')
					i += 2
				elif nxt in '()':
					if len(rest) < 3:
						_pending_esc[0] = rest
						break
					i += 3
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
			except _queue.Empty:
				pass
			if _had and _at_bottom:
				term.see('end')
				term.see('insert')
			if closed:
				if pythonfile:
					term.insert('end', '\n\n--- Python code finished, press any key to continue ---')
					term.see('end')
					term.unbind('<Key>')
					term.bind('<Key>', lambda e: _close())
				else:
					tw.destroy()
				_polling[0] = False
				return
			term.after(_TERM_FRAME_MS if backlog else 50, _poll)
		except Exception:
			try:
				if tw.winfo_exists():
					term.after(_TERM_FRAME_MS, _poll)
			except Exception:
				pass
		_polling[0] = False
	def _key(event):
		_unpost_menu()
		if not running[0]:
			return 'break'
		sym = event.keysym
		ch = event.char
		if ch or sym in ('Return', 'BackSpace', 'Delete', 'Up', 'Down', 'Left', 'Right', 'Tab', 'Home', 'End'):
			_clear_selection()
		try:
			if sym == 'Return':
				_write(b'\r')
			elif sym == 'BackSpace': _write(b'\x7f')
			elif sym == 'Delete': _write(b'\x1b[3~')
			elif sym == 'Up': _write(b'\x1b[A')
			elif sym == 'Down': _write(b'\x1b[B')
			elif sym == 'Left': _write(b'\x1b[D')
			elif sym == 'Right': _write(b'\x1b[C')
			elif sym == 'Tab': _write(b'\t')
			elif sym == 'Home': _write(b'\x1b[H')
			elif sym == 'End': _write(b'\x1b[F')
			elif (event.state & 4) and sym in ('space', 'at', '2'): _write(b'\x00')
			elif (event.state & 4) and sym in ('bracketleft', '3'): _write(b'\x1b')
			elif (event.state & 4) and sym in ('backslash', '4'): _write(b'\x1c')
			elif (event.state & 4) and sym in ('bracketright', '5'): _write(b'\x1d')
			elif (event.state & 4) and sym in ('asciicircum', '6'): _write(b'\x1e')
			elif (event.state & 4) and sym in ('underscore', 'slash', '7'): _write(b'\x1f')
			elif ch: _write(ch.encode('utf-8'))
		except OSError:
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
				_write(b'\x1b' + {'Left': b'b', 'Right': b'f', 'Up': b'[A', 'Down': b'[B'}[sym])
		except OSError:
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
			except OSError:
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
			try: _termmenu.unpost()
			except Exception: pass
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
			try: term.mark_set('insert', cursor[0])
			except Exception: pass
		try: term.after_idle(_do)
		except Exception: pass
	term.bind('<Key>', _key)
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
			try: _write(b'\x1b[I')
			except OSError: pass
	def _focus_out(e):
		if _focus_reporting[0] and running[0]:
			try: _write(b'\x1b[O')
			except OSError: pass
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
def gl():
	l = root.askstring('Go to line', 'Go to line no. :')
	if not l:
		return
	try:
		l = int(l)
	except Exception:
		root.error('Error', f'Cannot go to line number \'{l}\'')
		return
	else:
		show(f'go to line no. {l}')
		type_.see(f'{l}.0')
		type_.mark_set('insert', f'{l}.0')
		type_.tag_add('sel', f'{l}.0', f'{l}.end')
def hx():
	show('open alt-x commands help')
	hxw = root.subwin()
	hxw.title('Help with commands')
	hxs = hxw.scroll()
	hxs.pack(side = 'right', fill = 'y')
	hxh = hxw.textbox(wrap = 'word', yscrollcommand = hxs.set)
	hxs.config(command = hxh.yview)
	l1 = hxh.index('end-1c')
	hxh.insert('end', 'PyNotes\' Commands Help\n\n')
	r1 = hxh.index('end-1c')
	hxh.tag_add('bigstuff', l1, r1)
	hxh.insert('end', ("'editor' or 'ed': Switch to the Editor tab and focus on the textbox\n'mathgod' or 'mg': Open MathGod\n'exit' or 'e': Exit the window (the same as File → Exit)\n'save' or 's': Save the current file (the same as File → Save)\n'saveas' or 'sa': Copy the current file to another filename (the same as File → Save As)\n'u' or 'undo': Undo the last edit\n'r' or 'redo': Redo the last undoed edit\n'termexec:{string}' or 'te:{string}': Run the given string as a terminal command\n'write:{string}*{n}' or 'w:{string}*{n}': Copy the given text {n} times after the cursor position\n'search' or 'f': Find a string in the editor (the same as Edit → Find)\n'fr' or 'find-replace' or 'findreplace': Find and replace a string in the editor instantly (the same as Edit → Find & Replace)\n'show-source' or 'source-code': Show the main source code of PyNotes (/usr/share/PyNotes/ or C:/Program Files/PyNotes/) (the same as Options → Source Code)\n'new' or 'n': Open a new document (the same as File → New)\n'gotoline' or 'gl' or 'l': Go to a specified line\n'pyshell' or 'ps': Open the Python shell if you are in Python HMode.\n'o' or or 'load' or 'find' or 'open': Load a new file into the editor (the same as File → Open)\n't' or 'term' or 'terminal' or 'cmd': Open the terminal (the same as Options → Terminal)\n'prf' or 'preferences': Change the preferences (the same as Options → Preferences)\n'cancel' or 'z': Cancel the command and go back to the editor\n'a' or 'selall' or 'all': Select all the text in the editor\n'c' or 'copy': Copy the selected text\n'cut': Cut the selected text\n'p' or 'paste': Paste the last copied text\n'h:{(x/em/pc/mg/pl)}' or 'help:{(x/em/pc/mg/pl)}': Open the Help of Alt-X commands (this), Email, PyCode, MathGod, Plugins\n'hmode:{(py/la/norm/em/html/md)}': Change the HMode to Python / LaTeX / Normal / Email / HTML / Markdown (PyNotes mode)\n'pf' or 'pagenext': Scroll down a page in the editor\n'pb' or 'pageback': Scroll up a page in the editor\n'clear': Clear the editor completely\n'full': Make the window fullscreen\n'max' or 'maximize': Maximize the window\n'min': Minimize the window\n'pycode' or 'pc': Open PyCode\n'<Esc>': 'cancel'\n'sp' or 'speak': Speak the text selected out loud\n'ir' or 'indent-region': Indent the selected region with tabs or spaces\n'unir' or 'unindent-region': Unindent the selected region (handles tabs, spaces, and mixed)\n'st' or 'speech-to-text': Use speech-to-text\n'opd' or 'openplugindir': Open the Plugin's Directory\n'dp' or 'downloadplugins': Download plugins from the PyNotes' GitHub\n'ch' or 'changes': Open a list of the changes made in PyNotes v" + v + "\n'ab' or 'abt' or 'about' or 'pynotes': Open the PyNotes About\n're:{command}*{n}' or 'repeat:{command}*{n}': Repeat the given command {n} times\n'run': Run the code in the editor if the HMode is Python / LaTeX / HTML\n'cr' or 'comment' or 'comment-region': Comment the selected code if the HMode is Python / LaTeX / HTML / Markdown\n'uncr' or 'uncomment' or 'uncomment-region': Uncomment the selected code if the HMode is Python / LaTeX / HTML / Markdown\n'fullup': Moves the cursor to the beginning of the file\n'fulldown': Moves the cursor to the end of the file\n'ms' or 'mark' or 'markset' or 'mark-selection': Visually marks the selected text in the editor\n'unms' or 'unmark' or 'unmark-selection': Unmarks the visually marked text inside the selection in the editor\n'unma' or 'unmarkall': Unmarks all the visually marked text in the editor\n'sol' or 'startofline': Move the cursor to the start of the line\n'eol' or 'endofline': Move the cursor to the end of the line\n'sendemail' or 'sendmail': Switch to the Email tab if the HMode is Email").replace('\n', '\n\n'))
	l2 = hxh.index('end-1c')
	if plgnscmdhelp:
		hxh.insert('end', '\n\nPlugins\' Commands Help')
	r2 = hxh.index('end-1c') + '+2c'
	hxh.insert('end', plgnscmdhelp)
	hxh.tag_add('bigstuff', l2, r2)
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
	dwin.button(master = oframe, text = 'Write to Editor', command = lambda: [type_.edit_separator(), type_.insert('insert', output.get('1.0', 'end-1c')), type_.edit_separator(), dwin.destroy()]).pack(side = 'bottom', fill = 'x', expand = True)
	oframe.pack(side = 'bottom', fill = 'both', expand = True)
	dwin.sizablefalse()
def cmdrun(fullcommand):
	global hmode
	type_.focus_set()
	cmdentry.delete('1.0', 'end')
	cmdlabel.config(text = '')
	cmdentry.config(state = 'disabled')
	type_.config(state = 'normal')
	cmdentry.unbind('<Return>')
	cmdentry.unbind('<Escape>')
	if ':' in fullcommand:
		command, commandinput = fullcommand.split(':', 1)
	else:
		command = fullcommand
		commandinput = None
	command = command.strip()
	if commandinput:
		commandinput = commandinput.strip()
	if command in plgncmds:
		try:
			execvars = globals().copy()
			execvars['__file__'] = os.path.join(plgncmds[command][0], 'commands')
			execvars['commandinput'] = commandinput
			exec(plgncmds[command][1], execvars)
		except Exception as error:
			root.error('Error!', f'There was an error in running the command \'{command}\' from the plugin "{os.path.basename(os.path.normpath(plgncmds[command][0]))}":\n{error}')
		return
	if command in pcwrittencommands:
		try:
			execvars = globals().copy()
			execvars['commandinput'] = commandinput
			exec(pcwrittencommands[command], execvars)
		except Exception as error:
			root.error('Error!', f'There was an error in running the command \'{command}\' defined in PyCode:\n{error}')
		return
	elif command == 'exit' or command == 'e':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			cmdlabel.config(text = '')
			keypress()
			return
		ext()
	elif command == 'sol' or command == 'startofline':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			cmdlabel.config(text = '')
			keypress()
			return
		n = type_.index('insert').split('.')[0]
		type_.mark_set('insert', n + '.0')
		show(f'moved to start of line {n}')
	elif command == 'eol' or command == 'endofline':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			cmdlabel.config(text = '')
			keypress()
			return
		n = type_.index('insert').split('.')[0]
		type_.mark_set('insert', n + '.end')
		show(f'moved to end of line {n}')
	elif command == 'changes' or command == 'ch':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			cmdlabel.config(text = '')
			keypress()
			return
		changes()
	elif command == 'run':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			cmdlabel.config(text = '')
			keypress()
			return
		f5()
	elif command == 'ms' or command == 'mark' or command == 'markset' or command == 'mark-selection':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			cmdlabel.config(text = '')
			keypress()
			return
		try:
			start = type_.index('sel.first')
			end = type_.index('sel.last')
		except Exception:
			show('nothing is selected')
		else:
			type_.tag_add('marked', start, end)
			exec("type_.tag_config('marked'," + theme['pynotes:marked'] + ')')
			show(f'marked text from {start} to {end}')
	elif command == 'unms' or command == 'unmark' or command == 'unmark-selection':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			cmdlabel.config(text = '')
			keypress()
			return
		try:
			start = type_.index('sel.first')
			end = type_.index('sel.last')
		except Exception:
			show('nothing is selected')
		else:
			type_.tag_remove('marked', start, end)
			show(f'unmarked text from {start} to {end}')
	elif command == 'sendemail' or command == 'sendmail':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			cmdlabel.config(text = '')
			keypress()
			return
		if hmode == 'email':
			tabs.select(ef)
			show('switch to email tab')
		else:
			show('not in email hmode')
	elif command == 'unma' or command == 'unmarkall':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			cmdlabel.config(text = '')
			keypress()
			return
		type_.tag_remove('marked', '1.0', 'end')
		show('unmarked all text')
	elif command == 'comment' or command == 'cr' or command == 'comment-region':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			cmdlabel.config(text = '')
			keypress()
			return
		if not hmode in ('python', 'latex', 'html', 'markdown'):
			show('hmode is not python / latex / html / markdown')
			return
		try:
			start = int(type_.index('sel.first').split('.')[0])
			end = int(type_.index('sel.last').split('.')[0])
		except Exception:
			show('nothing is selected')
		else:
			ender = ''
			if hmode == 'python':
				commentor = '#'
			elif hmode == 'latex':
				commentor = '%'
			elif hmode == 'html' or hmode == 'markdown':
				commentor = '<!--'
				ender = '-->'
			l = start
			type_.edit_separator()
			while not l > end:
				if not type_.get(f'{l}.0', f'{l}.end').strip():
					l += 1
					continue
				type_.insert(f'{l}.0', commentor)
				type_.insert(f'{l}.end', ender)
				l += 1
			type_.edit_separator()
			show('comment region')
	elif command == 'uncomment' or command == 'uncr' or command == 'uncomment-region':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			cmdlabel.config(text = '')
			keypress()
			return
		if not hmode in ('python', 'latex', 'html', 'markdown'):
			show('hmode is not python / latex / html / markdown')
			return
		try:
			start = int(type_.index('sel.first').split('.')[0])
			end = int(type_.index('sel.last').split('.')[0])
		except Exception:
			show('nothing is selected')
		else:
			type_.edit_separator()
			ender = ''
			if hmode == 'python':
				commentor = '#'
			elif hmode == 'latex':
				commentor = '%'
			elif hmode == 'html' or hmode == 'markdown':
				commentor = '<!--'
				ender = '-->'
			l = start
			while not l > end:
				stripped = type_.get(f'{l}.0', f'{l}.end').lstrip()
				if stripped.startswith(commentor):
					a = len(type_.get(f'{l}.0', f'{l}.end')) - len(stripped)
					b = a + len(commentor)
					type_.delete(f'{l}.{a}', f'{l}.{b}')
				if ender:
					stripped = type_.get(f'{l}.0', f'{l}.end').rstrip()
					if stripped.endswith(ender):
						type_.delete(f'{l}.end-{len(ender)}c', f'{l}.end')
				l += 1
			type_.edit_separator()
			show('uncomment region')
	elif command == 'pyshell' or command == 'ps':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			cmdlabel.config(text = '')
			keypress()
			return
		if hmode == 'python':
			tabs.select(sf)
			shellcmd.focus()
			show('switch to python shell')
		else:
			show('not in python hmode')
	elif command == 'fullup':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			cmdlabel.config(text = '')
			keypress()
			return
		type_.mark_set('insert', '1.0')
		type_.see('1.0')
	elif command == 'fulldown':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			cmdlabel.config(text = '')
			keypress()
			return
		type_.mark_set('insert', 'end-1c')
		type_.see('end-1c')
	elif command == 'editor' or command == 'ed':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			cmdlabel.config(text = '')
			keypress()
			return
		tabs.select(mf)
		type_.focus()
		show('switch to editor')
	elif command == 'h' or command == 'help':
		if not commandinput:
			show(f'error: no input given to command \'{command}\'')
			cmdlabel.config(text = '')
			keypress()
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
			cmdlabel.config(text = '')
			keypress()
			return
		st()
	elif command == 'opd' or command == 'openplugindir':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			cmdlabel.config(text = '')
			keypress()
			return
		op()
	elif command == 'dp' or command == 'downloadplugins':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			cmdlabel.config(text = '')
			keypress()
			return
		dp()
	elif command == 'indent-region' or command == 'ir':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			cmdlabel.config(text = '')
			keypress()
			return
		try:
			start = int(type_.index('sel.first').split('.')[0])
			end = int(type_.index('sel.last').split('.')[0])
		except Exception:
			show('nothing is selected')
		else:
			if taborspace:
				whitespace = '    '
			else:
				whitespace = '	'
			l = start
			type_.edit_separator()
			while not l == end:
				type_.insert(f'{l}.0', whitespace)
				l += 1
			type_.insert(f'{l}.0', whitespace)
			type_.edit_separator()
			show('indent region')
	elif command == 'unindent-region' or command == 'unir':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			cmdlabel.config(text = '')
			keypress()
			return
		try:
			start = int(type_.index('sel.first').split('.')[0])
			end = int(type_.index('sel.last').split('.')[0])
		except Exception:
			show('nothing is selected')
		else:
			type_.edit_separator()
			lines = [type_.get(f'{l}.0', f'{l}.end') for l in range(start, end + 1)]
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
					type_.delete(f'{l}.0', f'{l}.1')
				elif line.startswith(' '):
					remove = 0
					for ch in line:
						if ch == ' ' and remove < min_spaces:
							remove += 1
						else:
							break
					if remove:
						type_.delete(f'{l}.0', f'{l}.{remove}')
			type_.edit_separator()
			show('unindent region')
	elif command == 'te' or command == 'termexec':
		if not commandinput:
			show(f'error: no input given to command \'{command}\'')
			cmdlabel.config(text = '')
			keypress()
			return
		try:
			show('output: ' + termexec(commandinput))
		except Exception:
			show(f'error: invalid input \'{commandinput}\'')
	elif command == 'mathgod' or command == 'mg':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			cmdlabel.config(text = '')
			keypress()
			return
		mathgod()
	elif command == 'write' or command == 'w':
		if not commandinput:
			show(f'error: no input given to command \'{command}\'')
			cmdlabel.config(text = '')
			keypress()
			return
		type_.edit_separator()
		try:
			type_.insert(type_.index('insert'), commandinput.split('*', 1)[0].encode().decode('unicode_escape') * int(commandinput.split('*', 1)[1]))
			textwrote, timeswrote = commandinput.split('*', 1)
			show(f'wrote \'{textwrote}\' {timeswrote} times')
		except Exception:
			show(f'error: invalid input \'{commandinput}\'')
		type_.edit_separator()
	elif command == 'repeat' or command == 're':
		try:
			for i in range(int(commandinput.split('*', 1)[1])):
				cmdrun(commandinput.split('*', 1)[0])
		except Exception:
			show(f'error: invalid input \'{commandinput}\'')
	elif command == 'u' or command == 'undo':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			cmdlabel.config(text = '')
			keypress()
			return
		undo()
	elif command == 'r' or command == 'redo':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			cmdlabel.config(text = '')
			keypress()
			return
		redo()
	elif command == 'save' or command == 's':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			cmdlabel.config(text = '')
			keypress()
			return
		sssv()
	elif command == 'saveas' or command == 'sa':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			cmdlabel.config(text = '')
			keypress()
			return
		ssv()
	elif command == 'search' or command == 'f':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			cmdlabel.config(text = '')
			keypress()
			return
		f()
	elif command == 'find-replace' or command == 'findreplace' or command == 'fr':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			cmdlabel.config(text = '')
			keypress()
			return
		fr()
	elif command == 'show-source' or command == 'source-code':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			cmdlabel.config(text = '')
			keypress()
			return
		ss()
	elif command == 'new' or command == 'n':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			cmdlabel.config(text = '')
			keypress()
			return
		nw()
	elif command == 'l' or command == 'gl' or command == 'gotoline':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			cmdlabel.config(text = '')
			keypress()
			return
		gl()
	elif command == 'open' or command == 'find' or command == 'o' or command == 'load':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			cmdlabel.config(text = '')
			keypress()
			return
		llld()
	elif command == 'terminal' or command == 'cmd' or command == 'term' or command == 't':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			cmdlabel.config(text = '')
			keypress()
			return
		term()
	elif command == 'prf' or command == 'preferences':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			cmdlabel.config(text = '')
			keypress()
			return
		prf()
	elif command == 'cancel' or command == 'z':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			cmdlabel.config(text = '')
			keypress()
			return
		pass
	elif command == '':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			cmdlabel.config(text = '')
			keypress()
			return
		pass
	elif command == 'a' or command == 'selall' or command == 'all':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			cmdlabel.config(text = '')
			keypress()
			return
		selall()
	elif command == 'copy' or command == 'c':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			cmdlabel.config(text = '')
			keypress()
			return
		cp()
	elif command == 'cut':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			cmdlabel.config(text = '')
			keypress()
			return
		cut()
	elif command == 'pf' or command == 'pagenext':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			cmdlabel.config(text = '')
			keypress()
			return
		ptf()
	elif command == 'pb' or command == 'pageback':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			cmdlabel.config(text = '')
			keypress()
			return
		ptb()
	elif command == 'paste' or command == 'p':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			cmdlabel.config(text = '')
			keypress()
			return
		pst()
	elif command == 'sp' or command == 'speak':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			cmdlabel.config(text = '')
			keypress()
			return
		spk()
	elif command == 'full':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			cmdlabel.config(text = '')
			keypress()
			return
		root.update()
		root.attributes('-fullscreen', True)
		root.update()
	elif command == 'unfull':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			cmdlabel.config(text = '')
			keypress()
			return
		root.update()
		root.attributes('-fullscreen', False)
		root.update()
	elif command == 'max' or command == 'maximize':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			cmdlabel.config(text = '')
			keypress()
			return
		root.update()
		if platform.system() == 'Linux':
			root.attributes('-zoomed', True)
		else:
			root.state('zoomed')
		root.update()
		show('maximized window')
	elif command == 'min':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			cmdlabel.config(text = '')
			keypress()
			return
		root.update()
		root.iconify()
		root.update()
		show('minimized window')
	elif command == 'clear':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			cmdlabel.config(text = '')
			keypress()
			return
		if root.ask('Warning', 'Clear the editor?', options = ('ok', 'cancel'), icon = 'warning'):
			type_.edit_separator()
			type_.delete('1.0', 'end')
			type_.edit_separator()
			show('cleared editor')
	elif command == 'pycode' or command == 'pc':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			cmdlabel.config(text = '')
			keypress()
			return
		pc()
	elif command == 'ab' or command == 'abt' or command == 'about' or command == 'pynotes':
		if commandinput:
			show(f'error: command \'{command}\' does not take input')
			cmdlabel.config(text = '')
			keypress()
			return
		abt()
	elif not (hmode in ['png', 'pdf', 'epub']) and command == 'hmode':
		if not commandinput:
			show(f'error: no input given to command \'{command}\'')
			cmdlabel.config(text = '')
			keypress()
			return
		try:
			if commandinput == 'python' or commandinput == 'py':
				sethmenu('python')
				tabs.tab(ef, state = 'hidden')
				lf.pack_forget()
				hmode = 'python'
				filetype.config(text = 'Python File (*.py)')
				python_trigger_name_scan()
			elif commandinput == 'latex' or commandinput == 'la':
				sethmenu('latex')
				tabs.tab(ef, state = 'hidden')
				lf.pack(padx = 10, pady = 10, side = 'top', fill = 'x', before = cmdlabel)
				hmode = 'latex'
				filetype.config(text = 'LaTeX / TeX File (*.tex)')
			elif commandinput == 'normal' or commandinput == 'norm':
				sethmenu(None)
				tabs.tab(ef, state = 'hidden')
				lf.pack_forget()
				hmode = 'norm'
				filetype.config(text = 'Plain Text (*.*)')
			elif commandinput == 'email' or commandinput == 'em':
				sethmenu(None)
				hmode = 'email'
				filetype.config(text = 'Plain Text (*.*)')
				tabs.tab(ef, state = 'normal')
			elif commandinput == 'html':
				sethmenu(None)
				hmode = 'html'
				filetype.config(text = 'HTML File (*.html)')
				tabs.tab(ef, state = 'hidden')
				lf.pack_forget()
			elif commandinput == 'markdown' or commandinput == 'md':
				sethmenu(None)
				tabs.tab(ef, state = 'hidden')
				lf.pack_forget()
				hmode = 'markdown'
				filetype.config(text = 'Markdown File (*.md)')
			elif commandinput in plgnhmodes:
				try:
					hmode = commandinput
					exec(plgnhmodes[commandinput][1])
				except Exception as error:
					root.error('Error!', f'There was an error in switching to the HMode "{commandinput}" from the plugin "{os.path.basename(os.path.normpath(plgnhmodes[commandinput][0]))}":\n{error}')
			else:
				show(f'hmode \'{commandinput}\' does not exist')
				cmdlabel.config(text = '')
				return
		except Exception:
			show(f'invalid command \'{command}\'')
		else:
			show(f'{hmode} hmode')
	else:
		show(text = f'invalid command \'{command}\'')
	cmdlabel.config(text = '')
	keypress()
def selall():
	show('select all text')
	type_.tag_add('sel', '1.0', 'end')
	return 'break'
def show(text):
	cmdentry.config(state = 'normal')
	cmdentry.delete('1.0', 'end')
	cmdentry.insert('end', text.replace('\n', '\\n'))
	cmdentry.config(state = 'disabled')
def cp():
	global root
	try:
		select = type_.get('sel.first', 'sel.last')
	except Exception:
		show('no text is selected')
		return
	else:
		show('copy text')
	root.clipboard_clear()
	root.clipboard_append(select)
def cut():
	try:
		select = type_.get('sel.first', 'sel.last')
	except Exception:
		show('no text is selected')
		return
	else:
		show('cut text')
	type_.delete('sel.first', 'sel.last')
	root.clipboard_clear()
	root.clipboard_append(select)
	show('cut text')
engine = stt.init()
def actualspk(text):
	global engine
	try:
		engine.say(text)
		engine.runAndWait()
	except Exception as error:
		root.error('Error', f'An error occured:{error}')
def spk():
	try:
		select = type_.get('sel.first', 'sel.last')
	except Exception:
		show('no text is selected')
		return
	else:
		show('speak selected text')
		speakthread = threading.Thread(target = actualspk, args = (select,), daemon = True)
		speakthread.start()
def pst():
	global root
	try:
		text = root.clipboard_get()
	except Exception:
		show('no text is on clipboard')
		return
	else:
		show('paste text')
	type_.edit_separator()
	type_.insert('insert', text)
	type_.edit_separator()
	return 'break'
def cmd():
	cmdentry.config(state = 'normal')
	cmdentry.delete('1.0', 'end')
	cmdentry.focus_set()
	type_.config(state = 'disabled')
	cmdlabel.config(text = 'Alt-x-')
	cmdentry.bind('<Return>', lambda event: cmdrun(cmdentry.get('1.0', 'end')[:-1]))
	cmdentry.bind('<Escape>', lambda event: cmdrun('cancel'))
def ptb():
	if type_.yview()[0] == 0.0:
		show('already at beginning')
		return
	type_.yview_scroll(-1, 'pages')
	show('go to previous page')
def ptf():
	if type_.yview()[1] == 1.0:
		show('already at end')
		return
	type_.yview_scroll(1, 'pages')
	show('go to next page')
def pcdone(nc):
	open(f'{homedir}/.pynotes', 'w+', encoding = 'utf-8').write(nc)
	pcread()
def say(string):
	root.info('Print PyCode', string)
def ask(string):
	ans = root.askstring('Input PyCode', string)
	exec(f'answer = \'{ans}\'', globals())
def pcrun(code):
	code = code.split('\n')
	for line in code:
		try:
			exec(line, globals())
		except Exception as error:
			root.error('Error', f'Error in running the translated PyCode line\n"{line}":\n{error}')
def pccmdwrite(text, n):
	type_.edit_separator()
	type_.insert(type_.index('insert'), text * n)
	show(f'wrote \'{text.replace("\n", "\\n")}\' {n} times')
	type_.edit_separator()
	keypress()
def pcindentregion(start, end):
	if taborspace:
		whitespace = '    '
	else:
		whitespace = '	'
	l = start
	type_.edit_separator()
	while not l > end:
		if not type_.get(f'{l}.0', f'{l}.end').strip():
			l += 1
			continue
		type_.insert(f'{l}.0', whitespace)
		l += 1
	type_.edit_separator()
	show('indent region')
	keypress()
def pcindentselection():
	try:
		start = int(type_.index('sel.first').split('.')[0])
		end = int(type_.index('sel.last').split('.')[0])
	except Exception:
		show('nothing is selected')
		return
	else:
		if taborspace:
			whitespace = '    '
		else:
			whitespace = '	'
		l = start
		type_.edit_separator()
		while not l == end:
			type_.insert(f'{l}.0', whitespace)
			l += 1
		type_.insert(f'{l}.0', whitespace)
		type_.edit_separator()
		show('indent selection')
		keypress()
def pcunindentregion(start, end):
	type_.edit_separator()
	lines = [type_.get(f'{l}.0', f'{l}.end') for l in range(start, end + 1)]
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
			type_.delete(f'{l}.0', f'{l}.1')
		elif line.startswith(' '):
			remove = 0
			for ch in line:
				if ch == ' ' and remove < min_spaces:
					remove += 1
				else:
					break
			if remove:
				type_.delete(f'{l}.0', f'{l}.{remove}')
	type_.edit_separator()
	show('unindent region')
	keypress()
def pcunindentselection():
	try:
		start = int(type_.index('sel.first').split('.')[0])
		end = int(type_.index('sel.last').split('.')[0])
	except Exception:
		show('nothing is selected')
		return
	else:
		type_.edit_separator()
		lines = [type_.get(f'{l}.0', f'{l}.end') for l in range(start, end + 1)]
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
				type_.delete(f'{l}.0', f'{l}.1')
			elif line.startswith(' '):
				remove = 0
				for ch in line:
					if ch == ' ' and remove < min_spaces:
						remove += 1
					else:
						break
				if remove:
					type_.delete(f'{l}.0', f'{l}.{remove}')
		type_.edit_separator()
		show('unindent selection')
		keypress()
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
def pcpyshell():
	if hmode == 'python':
		tabs.select(sf)
		shellcmd.focus()
		show('switch to python shell')
		keypress()
	else:
		show('not in python hmode')
def pcswitchedit():
	tabs.select(mf)
	type_.focus()
	show('switch to editor')
	keypress()
def pctermexec(command):
	show('output: ' + termexec(command))
def pcrepeatx(command, n):
	for i in range(n):
		cmdrun(command)
	keypress()
def pcfullscreen():
	root.update()
	root.attributes('-fullscreen', True)
	root.update()
	show('fullscreen mode')
def pcunfullscreen():
	root.update()
	root.attributes('-fullscreen', False)
	root.update()
	show('windowed mode')
def pcmax():
	root.update()
	if platform.system() == 'Linux':
		root.attributes('-zoomed', True)
	else:
		root.state('zoomed')
	root.update()
	show('maximize window')
def pccleareditor():
	if root.ask('Warning', 'Clear the editor?', options = ('ok', 'cancel'), icon = 'warning'):
		type_.edit_separator()
		type_.delete('1.0', 'end')
		type_.edit_separator()
		show('cleared editor')
def sethmenu(mode):
	try:
		m.delete('Python')
	except Exception:
		pass
	try:
		m.delete('LaTeX')
	except Exception:
		pass
	if mode == 'python':
		m.insert_cascade(m.index('Options') + 1, label = 'Python', menu = pm)
	elif mode == 'latex':
		m.insert_cascade(m.index('Options') + 1, label = 'LaTeX', menu = lm)
def pchmode(mode):
	global hmode
	if hmode in ['png', 'pdf', 'epub']:
		return
	if mode == 'python' or mode == 'py':
		sethmenu('python')
		tabs.tab(ef, state = 'hidden')
		lf.pack_forget()
		hmode = 'python'
		filetype.config(text = 'Python File (*.py)')
		python_trigger_name_scan()
	elif mode == 'latex' or mode == 'la':
		sethmenu('latex')
		tabs.tab(ef, state = 'hidden')
		lf.pack(padx = 10, pady = 10, side = 'top', fill = 'x', before = cmdlabel)
		hmode = 'latex'
		filetype.config(text = 'LaTeX / TeX File (*.tex)')
	elif mode == 'normal' or mode == 'norm':
		sethmenu(None)
		tabs.tab(ef, state = 'hidden')
		lf.pack_forget()
		hmode = 'norm'
		filetype.config(text = 'Plain Text (*.*)')
	elif mode == 'email' or mode == 'em':
		sethmenu(None)
		hmode = 'email'
		filetype.config(text = 'Plain Text (*.*)')
		tabs.tab(ef, state = 'normal')
	elif mode == 'html':
		sethmenu(None)
		hmode = 'html'
		filetype.config(text = 'HTML File (*.html)')
		tabs.tab(ef, state = 'hidden')
		lf.pack_forget()
	elif mode == 'markdown' or mode == 'md':
		sethmenu(None)
		tabs.tab(ef, state = 'hidden')
		lf.pack_forget()
		hmode = 'markdown'
		filetype.config(text = 'Markdown File (*.md)')
	elif mode in plgnhmodes:
		try:
			hmode = mode
			exec(plgnhmodes[mode][1])
		except Exception as error:
			root.error('Error!', f'There was an error in switching to the HMode {mode} from the plugin "{os.path.basename(os.path.normpath(plgnhmodes[mode][0]))}":\n{error}')
	show(f'{hmode} hmode')
	keypress()
def pccommentregion(start, end):
	if not hmode in ('python', 'latex', 'html'):
		return
	ender = ''
	if hmode == 'python':
		commentor = '#'
	elif hmode == 'latex':
		commentor = '%'
	elif hmode == 'html' or hmode == 'markdown':
		commentor = '<!--'
		ender = '-->'
	l = start
	type_.edit_separator()
	while not l > end:
		if not type_.get(f'{l}.0', f'{l}.end').strip():
			l += 1
			continue
		type_.insert(f'{l}.0', commentor)
		type_.insert(f'{l}.end', ender)
		l += 1
	type_.edit_separator()
	show('comment region')
	keypress()
def pccommentselection():
	if not hmode in ('python', 'latex', 'html', 'markdown'):
		return
	try:
		start = int(type_.index('sel.first').split('.')[0])
		end = int(type_.index('sel.last').split('.')[0])
	except Exception:
		show('nothing is selected')
		return
	else:
		ender = ''
		if hmode == 'python':
			commentor = '#'
		elif hmode == 'latex':
			commentor = '%'
		elif hmode == 'html' or hmode == 'markdown':
			commentor = '<!--'
			ender = '-->'
		l = start
		type_.edit_separator()
		while not l > end:
			if not type_.get(f'{l}.0', f'{l}.end').strip():
				l += 1
				continue
			type_.insert(f'{l}.0', commentor)
			type_.insert(f'{l}.end', ender)
			l += 1
		type_.edit_separator()
	show('comment selection')
	keypress()
def pcuncommentregion(start, end):
	if not hmode in ('python', 'latex', 'html', 'markdown'):
		return
	type_.edit_separator()
	ender = ''
	if hmode == 'python':
		commentor = '#'
	elif hmode == 'latex':
		commentor = '%'
	elif hmode == 'html' or hmode == 'markdown':
		commentor = '<!--'
		ender = '-->'
	l = start
	while not l > end:
		stripped = type_.get(f'{l}.0', f'{l}.end').lstrip()
		if stripped.startswith(commentor):
			a = len(type_.get(f'{l}.0', f'{l}.end')) - len(stripped)
			b = a + len(commentor)
			type_.delete(f'{l}.{a}', f'{l}.{b}')
		if ender:
			stripped = type_.get(f'{l}.0', f'{l}.end').rstrip()
			if stripped.endswith(ender):
				type_.delete(f'{l}.end-{len(ender)}c', f'{l}.end')
		l += 1
	type_.edit_separator()
	show('uncomment region')
	keypress()
def pcuncommentselection():
	if not hmode in ('python', 'latex', 'html', 'markdown'):
		return
	try:
		start = int(type_.index('sel.first').split('.')[0])
		end = int(type_.index('sel.last').split('.')[0])
	except Exception:
		show('nothing is selected')
		return
	else:
		type_.edit_separator()
		ender = ''
		if hmode == 'python':
			commentor = '#'
		elif hmode == 'latex':
			commentor = '%'
		elif hmode == 'html' or hmode == 'markdown':
			commentor = '<!--'
			ender = '-->'
		l = start
		while not l > end:
			stripped = type_.get(f'{l}.0', f'{l}.end').lstrip()
			if stripped.startswith(commentor):
				a = len(type_.get(f'{l}.0', f'{l}.end')) - len(stripped)
				b = a + len(commentor)
				type_.delete(f'{l}.{a}', f'{l}.{b}')
			if ender:
				stripped = type_.get(f'{l}.0', f'{l}.end').rstrip()
				if stripped.endswith(ender):
					type_.delete(f'{l}.end-{len(ender)}c', f'{l}.end')
			l += 1
		type_.edit_separator()
		show('uncomment selection')
		keypress()
pcwrittencommands = {}
def pcask(askstring):
	return root.askstring('PyCode Input', askstring)
def pcmovecursor(index):
	type_.mark_set('insert', index)
	type_.see(index)
def pcselecttext(a, b):
	type_.tag_remove('sel', '1.0', 'end')
	type_.tag_add('sel', a, b)
	show(f'selected text from {a} to {b}')
def pcgetselection():
	try:
		start = type_.index('sel.first')
		end = type_.index('sel.last')
		ans = (str(start), str(end))
	except Exception:
		ans = tuple()
	return ans
def pcmark(a, b = None):
	if not b:
		a, b = a[0], a[1]
	type_.tag_add('marked', a, b)
	show(f'marked text from {a} to {b}')
	exec("type_.tag_config('marked'," + theme['pynotes:marked'] + ')')
def pcmarkselection():
	try:
		start = type_.index('sel.first')
		end = type_.index('sel.last')
	except Exception:
		return
	type_.tag_add('marked', start, end)
	show(f'marked text from {start} to {end}')
	exec("type_.tag_config('marked'," + theme['pynotes:marked'] + ')')
def pcunmark(a, b = None):
	if not b:
		a, b = a[0], a[1]
	type_.tag_remove('marked', a, b)
	show(f'unmarked text from {a} to {b}')
def pcunmarkall():
	type_.tag_remove('marked', '1.0', 'end')
	show(f'unmarked all text')
def pctkindex(toindex, line = False):
	ans = type_.index(toindex)
	if line == 'line':
		ans = ans.split('.')[0]
	return ans
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
	keypress()
def pckillexit():
	os._exit(0)
def pcswitchemailtab():
	if hmode == 'email':
		tabs.select(ef)
		show('switched to email tab')
	else:
		show('not in email hmode')
def pcdelete(*args, **kwargs):
	show('delete text')
	type_.delete(*args, **kwargs)
def pcsetvar(var, val):
	globals()[var] = val
pycodetopythoncommands = {'aboutpynotes': 'abt', 'ask': 'pcask', 'cleareditor': 'pccleareditor', 'close': 'ext', 'cmdrun': 'cmdrun', 'commentregion': 'pccommentregion', 'commentselection': 'pccommentselection', 'copy': 'cp', 'copytext': 'pccopytext', 'cut': 'cut', 'delete': 'pcdelete', 'dictate': 'st', 'downloadplugins': 'dp', 'findreplace': 'fr', 'findtext': 'f', 'fullscreen': 'pcfullscreen', 'get': 'type_.get', 'getselection': 'pcgetselection', 'gotoline': 'gl', 'hmode': 'pchmode', 'indentregion': 'pcindentregion', 'indentselection': 'pcindentselection', 'insert': 'type_.insert', 'killquit': 'pckillexit', 'mark': 'pcmark', 'markselection': 'pcmarkselection', 'mathgod': 'mathgod', 'maximize': 'pcmax', 'minimize': 'root.iconify', 'movecursor': 'pcmovecursor', 'newfile': 'nw', 'openfile': 'llld', 'openhelp': 'pcopenhelp', 'openplugindir': 'op', 'openpycode': 'pc', 'openterm': 'term', 'pageback': 'ptb', 'pageforw': 'ptf', 'pass': 'pass', 'paste': 'pst', 'preferences': 'prf', 'pynotessourcecode': 'ss', 'pyshell': 'pcpyshell', 'redo': 'redo', 'repeatxcommand': 'pcrepeatx', 'return': 'return', 'runcode': 'f5', 'saveasfile': 'ssv', 'savefile': 'sssv', 'say': 'say', 'selall': 'selall', 'select': 'pcselecttext', 'setvar': 'pcsetvar', 'show': 'show', 'speaktext': 'spk', 'switcheditor': 'pcswitchedit', 'switchemailtab': 'pcswitchemailtab', 'termexec': 'pctermexec', 'tkindex': 'pctkindex', 'typecommand': 'cmd', 'uncommentregion': 'pcuncommentregion', 'uncommentselection': 'pcuncommentselection', 'undo': 'undo', 'unfullscreen': 'pcunfullscreen', 'unindentregion': 'pcunindentregion', 'unindentselection': 'pcunindentselection', 'unmark': 'pcunmark', 'unmarkall': 'pcunmarkall', 'unsetwintitle': 'pcunsettitle', 'wait': 'time.sleep', 'setwintitle': 'pcgosettitle', 'write': 'pccmdwrite'}
def pcread():
	global pcwrittencommands
	global pycodecommands
	global pythoncommands
	pycodecommands = sorted(list(pycodetopythoncommands))
	pythoncommands = [pycodetopythoncommands[x] for x in pycodecommands]
	pcwrittencommands = {}
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
	try:
		code = open(f'{homedir}/.pynotes', 'r', encoding = 'utf-8').read().replace('\n', '').split(';')
	except Exception:
		return
	cdt = ''
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
				def nonlambdafunc(string):
					nonlocal action_parts
					if not pycodeindex(string.strip()):
						raise Exception(f'Invalid expression "{string.strip()}"')
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
						cdt += f"type_.bind('{key_part}', lambda event: exec(\"{action_parts}\") or 'break')" + '\n'
						cdt += f'root.bind(\'{key_part}\', lambda event: exec("{action_parts}"))' + '\n'
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
									out += pycodeindex(inner.strip())
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
							raise Exception(f'Invalid expression "{oldtodo}"')
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
								raise Exception(f'Invalid expression "{oldtodo}"')
						else:
							to_do[i] = ''
					to_do = '\n'.join(to_do)
					pcwrittencommands[cmd] = to_do
				elif s and len(s) == 1:
					s = s[0].strip()
					startupcdt += f'{'\n'.join(map(nonlambdafunc, s[1:-1].strip().split('↩')))}' + '\n'
				else:
					root.error('Error in PyCode', f'Invalid syntax in line:\n"{line}"')
			except Exception as error:
				root.error('Error in PyCode', f'Error in line "{line}":\n{error}')
	defaults_cdt = "root.bind('<Alt-x>', lambda event: cmd())\ntype_.bind('<Control-a>', lambda event: selall())\ntype_.bind('<Control-c>', lambda event: cp())\ntype_.bind('<Control-v>', lambda event: pst())\ntype_.bind('<Control-x>', lambda event: cut())\ntype_.bind('<KeyRelease>', lambda event: keypress())\ntype_.bind('<BackSpace>', lambda event: show('delete text'))\ntype_.bind('<Delete>', lambda event: show('delete text'))\ntype_.bind('<Return>', lambda event: indent())\nroot.bind('<Control-n>', lambda event: nw())\nroot.bind('<Control-o>', lambda event: llld())\nroot.bind('<Control-s>', lambda event: sssv())\nroot.bind('<Control-S>', lambda event: ssv())\nroot.bind('<Control-w>', lambda event: ext())\nroot.bind('<Alt-l>', lambda event: gl())\nroot.bind('<Control-p>', lambda event: ptf())\nroot.bind('<Control-P>', lambda event: ptb())\nroot.bind('<Control-f>', lambda event: f())\nroot.bind('<Control-F>', lambda event: fr())\nroot.bind('<F5>', lambda event: f5())\nroot.bind('<Control-z>', lambda event: undo())\nroot.bind('<Control-Z>', lambda event: redo())\n"
	cdt = defaults_cdt + cdt
	for mod_key in set(list(mod_key_transitions) + list(mod_key_completions)):
		transitions = mod_key_transitions.get(mod_key, [])
		completions = mod_key_completions.get(mod_key, [])
		is_pure_completion = bool(completions) and not bool(transitions)
		if is_pure_completion and mod_key in simple_bindings_seen:
			else_t = f'(exec("{simple_bindings_seen[mod_key]}") or \'break\')'
			else_r = f'exec("{simple_bindings_seen[mod_key]}")'
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
			handler_t = f"((exec(\"{ap}\") or _pychord_state.__setitem__(0, None) or 'break') if _pychord_state[0] in ('{es}',) else {handler_t})"
			handler_r = f'((exec("{ap}") or _pychord_state.__setitem__(0, None)) if _pychord_state[0] in (\'{es}\',) else {handler_r})'
		cdt += f'type_.bind(\'{mod_key}\', lambda event: {handler_t})\n'
		cdt += f'root.bind(\'{mod_key}\', lambda event: {handler_r})\n'
	if chord_any_defined:
		MODS = "('Control_L', 'Control_R', 'Shift_L', 'Shift_R', 'Alt_L', 'Alt_R', 'Meta_L', 'Meta_R', 'Super_L', 'Super_R', 'Caps_Lock', 'Num_Lock', 'Scroll_Lock', 'ISO_Level3_Shift')"
		kp_body = f'None if event.keysym in {MODS} else _pychord_state.__setitem__(0, None)'
		for from_s, ks_, to_s in reversed(nonmod_transitions):
			state_check = f'_pychord_state[0] in (None,)' if from_s is None else f'_pychord_state[0] in (\'{from_s}\',)'
			kp_body = f"((_pychord_state.__setitem__(0, '{to_s}') or 'break') if {state_check} and event.keysym in ('{ks_}',) and not (event.state & 12) else {kp_body})"
		for es, ks_, ap in reversed(nonmod_completions):
			kp_body = f"((exec(\"{ap}\") or _pychord_state.__setitem__(0, None) or 'break') if _pychord_state[0] in ('{es}',) and event.keysym in ('{ks_}',) and not (event.state & 12) else {kp_body})"
		chord_init = 'globals().setdefault(\'_pychord_state\', [None])\n'
		chord_init += f'type_.bind(\'<KeyPress>\', lambda event: {kp_body})\n'
		chord_init += f'root.bind(\'<KeyPress>\', lambda event: {kp_body})\n'
		cdt = chord_init + cdt
	file = open(f'{homedir}/.pynotesstartup', 'w+', encoding = 'utf-8')
	file.write(startupcdt)
	file.close()
	pcrun(cdt)
def edit(widget, editfrom):
	if editfrom == 'c=':
		widget.insert('insert', '→')
		return 'break'
	elif editfrom == 'ce':
		widget.insert('insert', '↩')
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
def pc():
	global defs
	global wholenewwords
	show('open pycode')
	for binded in wholenewwords:
		root.unbind(binded)
		type_.unbind(binded)
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
		optionsdropdown.config(state = 'normal')
	optionsdropdown = pcwin.dropdown(stringvar = todefine, showdefault = 'Function', options = ['Function', 'Python Function', 'Variable', 'Startup Code', 'Keyboard Shortcut', 'Alt-X Command'], master = buttonframe, command = lambda inpt: [optionsdropdown.config(state = 'disabled'), define(inpt), optionsdropdown.config(state = 'normal')])
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
	hptabs.add(act, text = 'Alt-X Commands')
	code = hpwin.style()
	code.configure('CodeStyle.TLabel', background = 'white', padding = (7, 7, 7, 7), relief = 'sunken')
	hpwin.text(master = bt, text = 'Syntax -\nAll Keyboard Shortcuts, definitions of Variables and Functions, and Startup Code should end with a semicolon \';\'.\nInputs to a command must be given with one and only one space between\nthe command and the input.\nIf the input to a command is a string, it can only be inside single quotes \'input\'.\nSpaces do not matter between full commands and between brackets.\nNewlines do not matter between full commands and between brackets.\nFor example, the code').grid(column = 0, row = 0, padx = 10, pady = 10, sticky = 'w')
	hpwin.text(master = bt, text = '(something) →: (say \'hello\' ↩ say \'this is a test\');', style = 'CodeStyle.TLabel').grid(column = 0, row = 1, padx = 10, pady = 10, sticky = 'w')
	hpwin.text(master = bt, text = 'is the same as').grid(column = 0, row = 2, padx = 10, pady = 10, sticky = 'w')
	hpwin.text(master = bt, text = '(\nsomething\n)\n→:\n(\nsay \'hello\'\n↩\nsay \'this is a test\'\n);', style = 'CodeStyle.TLabel').grid(column = 0, row = 3, padx = 10, pady = 10, sticky = 'w')
	hpwin.text(master = bt, text = "PyCode uses some symbols which are not on the standard keyboard.\nTo type '→', press 'Control + =' on your keyboard.\nTo type '↩', press 'Control + Enter'.\nTo type '⌊', press 'Control + ['.\nTo type '⌋', press 'Control + ]'.\nThe functions and uses of these symbols are explained later in the Help.\nPyCode also has a simple autocomplete to help you type code faster.\nTyping any of these characters will make PyCode automatically close them with the opposite,\nand put your cursor in the middle: '|/|', '</>', '(/)', '[/]', \"'/'\", '\"/\"'.\nPressing ';' will automatically put your cursor on a new line after the semicolon.").grid(column = 0, row = 4, padx = 10, pady = 10, sticky = 'w')
	hpwin.text(master = ct, text = 'These are all the commands in PyCode which you can use to make or change Functions, Keyboard Shortcuts,\nStartup Code, and Alt-X commands:').grid(column = 0, row = 0, padx = 10, pady = 10, sticky = 'w')
	pccmdlistscroll = hpwin.scroll(master = ct)
	pccmdlist = hpwin.textbox(master = ct, yscrollcommand = pccmdlistscroll.set)
	l1 = pccmdlist.index('end-1c')
	pccmdlist.insert('end', 'PyNotes\' Commands Help\n\n')
	r1 = pccmdlist.index('end-1c')
	pccmdlist.tag_add('bigstuff', l1, r1)
	pccmdlist.insert('end', "aboutpynotes - Opens the PyNotes About.\n\nask 'prompt' - Asks an input from the user and returns the answer.\n\ncleareditor - Clears the editor.\n\nclose - Closes PyNotes.\n\ncmdrun 'command' - Runs the given Alt-X command.\n\ncommentregion 'a', 'b' - Coments the text from a given line number 'a' to a given line number 'b' in the editor if the HMode is Python / LaTeX / HTML / Markdown.\n\ncommentselection - Comments the selected code if the HMode is Python / LaTeX / HTML / Markdown.\n\ncopy - Copies the selected text in the editor.\n\ncopytext 'text' - Copies the given input to the clipboard\n\ncut - Cuts the selected text in the editor.\n\ndelete 'a', 'b' - Deletes the text from a given tkinter-style index 'a' to a given tkinter-style index 'b' in the editor.\n\ndictate - Opens the speech-to-text, lets you dictate text to the editor.\n\ndownloadplugins - Automatically opens a link to the PyNotes GitHub Plugin page to let you download plugins in your default browser.\n\nfindreplace - Opens Find & Replace.\n\nfindtext - Opens Find.\n\nfullscreen - Makes the PyNotes window fullscreen.\n\nget 'a', 'b' - Gets the text in the editor from a given tkinter style index 'a' to a given tkinter-style index 'b'.\n\ngetselection - Gets the range of the selected text in the editor and returns it.\n\ngotoline - Asks for an input and goes to the given line in the editor.\n\nhmode 'py/la/html/md/em/norm' - Switches the HMode (PyNotes mode) to Python / LaTeX / HTML / Markdown / Email / Normal.\n\nindentregion 'a', 'b' - Indents the text from a given line number 'a' to a given line number 'b' in the editor.\n\nindentselection - Indents the selected region in the editor.\n\ninsert 'index', 'text' - Inserts the text at a given tkinter-style index in the editor.\n\nkillquit - Forcibly kills PyNotes without saving files or cleaning up.\n\nmark 'a', 'b' - Visually marks the text between a tkinter-style index 'a' and a tkinter-style index 'b' in the editor.\n\nmarkselection - Visually marks the selected text in the editor.\n\nmathgod - Opens MathGod.\n\nmaximize - Maximizes the PyNotes window.\n\nminimize - Minimizes the PyNotes window.\n\nmovecursor 'index' - Moves the cursor to a given tkinter-style index in the editor.\n\nnewfile - Opens a new file in the editor.\n\nopenfile - Opens a file picker to open an existing file in the editor.\n\nopenhelp 'commands/email/pycode/mathgod/plugins' - Opens the Help about the given feature.\n\nopenplugindir - Opens the plugins directory in your file manager.\n\nopenpycode - Opens PyCode.\n\nopenterm - Opens the PyNotes terminal.\n\npageback - Goes to the previous page in the editor.\n\npageforw - Goes to the next page in the editor.\n\npass - Do nothing.\n\npaste - Pastes your clipboard in the editor.\n\npreferences - Opens the PyNotes preferences.\n\npynotessourcecode - Opens the PyNotes source code in the editor.\n\npyshell - Opens the Python Shell if you are in Python HMode.\n\nredo - Redos the last undo in the editor.\n\nrepeatxcommand 'command', n - Repeats the given Alt-X command n times.\n\nreturn 'value' - Returns the given value from a function.\n\nruncode - Runs the code in the editor if the HMode is Python / LaTeX / HTML.\n\nsaveasfile - Save the text in the editor to another filename.\n\nsavefile - Saves the file in the editor.\n\nsay 'input' - Opens a graphical messagebox showing the given input. You can also use a variable here.\n\nselall - Selects all the text in the editor.\n\nselect 'a', 'b' - Selects the text from a given tkinter-style index 'a' to a given tkinter-style index 'b' in the editor.\n\nsetvar 'var', 'val' - Makes a variable with a given name 'var' and a given value 'val'.\n\nshow 'text' - Shows the given text in the Alt-X command box.\n\nspeaktext - Speaks the selected text in the editor.\n\nswitcheditor - Switches to the editor tab.\n\n'switchemailtab - Switches to the Email tab if the HMode is Email.\n\ntermexec 'command' - Executes the given command in a terminal and shows the output in the Alt-X command box.\n\ntkindex 'toindex', (optional: 'line') - Indexes the given tkinter-style input in the editor and returns the output. If the optional 'line' input is also given, it returns only the linenumber as a string.\n\ntypecommand - Lets you type an Alt-X command.\n\nuncommentregion 'a', 'b' - Uncomments the text from a given line number 'a' to another given line number 'b' in the editor if the HMode is Python / LaTeX / HTML / Markdown.\n\nuncommentselection - Uncomments the selected text in the editor if the HMode is Python / LaTeX / HTML / Markdown.\n\nundo - Undoes the last edit in the editor.\n\nunfullscreen - Makes PyNotes windowed mode from fullscreen.\n\nunmark 'a', 'b' - Unmark the visually marked text in the editor from a tkinter-style index 'a' to a tkinter-style index 'b'.\n\nunmarkall - Unmarks all the visually marked text in the editor.\n\nunsetwintitle - Sets the window title back to normal after the command 'setwintitle'\n\nwait n - Freezes PyNotes for n seconds.\n\nsetwintitle 'title' - Sets the title of the PyNotes window to a given string.\n\nwrite 'text', n - Writes the given text repeated n times in the editor.")
	l2 = pccmdlist.index('end-1c')
	if plgnspccmdhelp:
		pccmdlist.insert('end', '\n\nPlugins\' Commands Help')
	r2 = pccmdlist.index('end-1c') + '+2c'
	pccmdlist.insert('end-1c', plgnspccmdhelp)
	pccmdlist.tag_add('bigstuff', l2, r2)
	pccmdlist.tag_config('bigstuff', font = (monospace, 15, 'bold'))
	pccmdlist.config(state = 'disabled')
	pccmdlistscroll.config(command = pccmdlist.yview)
	pccmdlist.grid(column = 0, row = 1, padx = 10, pady = 10, sticky = 'nsew')
	pccmdlistscroll.grid(column = 1, row = 1, padx = 10, pady = 10, sticky = 'ns')
	hpwin.text(master = ct, text = 'By default, a command will take all the text that comes after it after a space as it\'s input.\nTo avoid that, you can give the input inside () brackets.\nThen, the command will only take the text after itself which is inside brackets as input.').grid(column = 0, row = 2, padx = 10, pady = 10, sticky = 'w')
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
	hpwin.sizablefalse()
	hpwin.style(root.gettheme())
	hpwin.focus()
def undo():
	try:
		type_.edit_undo()
		show('undoed edit')
	except Exception:
		show('nothing to undo')
def redo():
	try:
		type_.edit_redo()
		show('redoed edit')
	except Exception:
		show('nothing to redo')
tabs = root.tabs()
mf = root.frame()
sf = root.frame()
lf = root.frame()
ef = root.frame()
def boldlatex():
	try:
		select = type_.get('sel.first', 'sel.last')
	except Exception:
		return
	type_.edit_separator()
	type_.delete('sel.first', 'sel.last')
	type_.insert('insert', '{\\bf ' + select + '}')
	type_.edit_separator()
	show('bold text latex')
	keypress()
def italiclatex():
	try:
		select = type_.get('sel.first', 'sel.last')
	except Exception:
		return
	type_.edit_separator()
	type_.delete('sel.first', 'sel.last')
	type_.insert('insert', '\\textit{' + select + '}')
	type_.edit_separator()
	show('italic text latex')
	keypress()
def underlinelatex():
	try:
		select = type_.get('sel.first', 'sel.last')
	except Exception:
		return
	type_.edit_separator()
	type_.delete('sel.first', 'sel.last')
	type_.insert('insert', '\\underline{' + select + '}')
	type_.edit_separator()
	show('underline text latex')
	keypress()
def subscriptlatex():
	try:
		select = type_.get('sel.first', 'sel.last')
	except Exception:
		return
	type_.edit_separator()
	type_.delete('sel.first', 'sel.last')
	type_.insert('insert', '_{' + select + '}')
	type_.edit_separator()
	show('subscript text latex')
	keypress()
def superscriptlatex():
	try:
		select = type_.get('sel.first', 'sel.last')
	except Exception:
		return
	type_.edit_separator()
	type_.delete('sel.first', 'sel.last')
	type_.insert('insert', '^{' + select + '}')
	type_.edit_separator()
	show('superscript text latex')
	keypress()
def numberlistlatex():
	type_.edit_separator()
	try:
		select = type_.get('sel.first', 'sel.last')
	except Exception:
		type_.insert('insert', '\n\\begin{enumerate}\n\n\\end{enumerate}\n')
	else:
		tryfind = re.findall(r'\\begin{enumerate}.+\\end{enumerate}', select, re.DOTALL)
		if not tryfind:
			select = '\\item ' + select.replace('\n', '\n\\item ').replace('\\item \\item ', '\\item ')
			type_.delete('sel.first', 'sel.last')
			type_.insert('insert', '\n\\begin{enumerate}\n' + select + '\n\\end{enumerate}\n')
		else:
			keeptext = tryfind[0][len('\\begin{enumerate}'):][:-len('\\end{enumerate}')].replace('\\item ', '')
			type_.delete('sel.first', 'sel.last')
			type_.insert('insert', keeptext)
	type_.edit_separator()
	show('numbered list latex')
	keypress()
def bulletlistlatex():
	type_.edit_separator()
	try:
		select = type_.get('sel.first', 'sel.last')
	except Exception:
		type_.insert('insert', '\n\\begin{itemize}\n\n\\end{itemize}\n').replace('\\item \\item ', '\\item ')
	else:
		tryfind = re.findall(r'\\begin{itemize}.+\\end{itemize}', select, re.DOTALL)
		if not tryfind:
			select = '\\item ' + select.replace('\n', '\n\\item ').replace('\\item \\item ', '\\item ')
			type_.delete('sel.first', 'sel.last')
			type_.insert('insert', '\n\\begin{itemize}\n' + select + '\n\\end{itemize}\n')
		else:
			keeptext = tryfind[0][len('\\begin{itemize}'):][:-len('\\end{itemize}')].replace('\\item ', '')
			type_.delete('sel.first', 'sel.last')
			type_.insert('insert', keeptext)
	type_.edit_separator()
	show('bulleted list latex')
	keypress()
def paragraphlatex():
	type_.edit_separator()
	type_.insert('insert', '\\par\n')
	show('new paragraph latex')
	keypress()
def equationlatex():
	type_.edit_separator()
	try:
		select = type_.get('sel.first', 'sel.last')
	except Exception:
		type_.insert('insert', '\n\\begin{equation}\n\\begin{split}\n\n\\end{split}\n\\end{equation}\n')
	else:
		tryfind = re.findall(r'\\begin{equation}.+\\end{equation}', select, re.DOTALL)
		if not tryfind:
			select = select.replace('\n', '\\\\\n').replace('\\\\\\\\', '\\\\')
			type_.delete('sel.first', 'sel.last')
			type_.insert('insert', '\n\\begin{equation}\n' + select + '\n\\end{equation}\n')
		else:
			keeptext = tryfind[0][len('\\begin{equation}'):][:-len('\\end{equation}')].replace('\\', '')
			type_.delete('sel.first', 'sel.last')
			type_.insert('insert', keeptext)
	type_.edit_separator()
	show('equation latex')
	keypress()
def sectionlatex(typeofsection):
	type_.edit_separator()
	typeofsection = typeofsection.lower()
	secname = 'Section'
	if secname:
		type_.insert('insert', f'\n\\{typeofsection}' + '{' + secname + '}\n')
	type_.edit_separator()
	show(f'new {typeofsection} latex')
	keypress()
def mathlatex(whichchar):
	type_.edit_separator()
	original = ['Multiplication', 'Division', 'Less or equal', 'More or equal', 'Not equal', 'Infinity', 'Summation', 'Integral', 'Pi', 'Theta', 'Alpha Lower', 'Alpha Upper', 'Inline Math']
	replaces = ['\\times', '\\div', '\\leq', '\\meq', '\\neq', '\\infty', '\\sum', '\\int', '\\pi', '\\theta', '\\alpha', '\\Alpha', '$$']
	whichchar = replaces[original.index(whichchar)]
	type_.insert('insert', whichchar)
	type_.edit_separator()
	show('insert math latex')
	keypress()
root.text(master = lf, text = 'LaTeX:').grid(column = 0, row = 0, padx = 10, pady = 10)
bold = root.button(master = lf, text = 'Bold', command = boldlatex)
bold.grid(column = 1, row = 0, padx = 10, pady = 10)
italic = root.button(master = lf, text = 'Italic', command = italiclatex)
italic.grid(column = 2, row = 0, padx = 10, pady = 10)
underline = root.button(master = lf, text = 'Underline', command = underlinelatex)
underline.grid(column = 3, row = 0, padx = 10, pady = 10)
subscript = root.button(master = lf, text = 'Subscript', command = subscriptlatex)
subscript.grid(column = 4, row = 0, padx = 10, pady = 10)
superscript = root.button(master = lf, text = 'Superscript', command = superscriptlatex)
superscript.grid(column = 5, row = 0, padx = 10, pady = 10)
numberlist = root.button(master = lf, text = 'Numbered List', command = numberlistlatex)
numberlist.grid(column = 6, row = 0, padx = 10, pady = 10)
bulletlist = root.button(master = lf, text = 'Bullet List', command = bulletlistlatex)
bulletlist.grid(column = 7, row = 0, padx = 10, pady = 10)
sectionvar = root.stringvar(master = lf)
section = root.dropdown(stringvar = sectionvar, showdefault = 'Section', options = ['Section', 'Subsection', 'Subsubsection'], master = lf, command = sectionlatex)
section.grid(column = 8, row = 0, padx = 10, pady = 10)
paragraph = root.button(master = lf, text = 'Paragraph', command = paragraphlatex)
paragraph.grid(column = 9, row = 0, padx = 10, pady = 10)
equation = root.button(master = lf, text = 'Equation', command = equationlatex)
equation.grid(column = 10, row = 0, padx = 10, pady = 10)
charvar = root.stringvar()
math = root.dropdown(master = lf, stringvar = charvar, showdefault = 'Multiplication', options = ['Multiplication', 'Division', 'Less or equal', 'More or equal', 'Not equal', 'Infinity', 'Summation', 'Integral', 'Pi', 'Theta', 'Alpha Lower', 'Alpha Upper', 'Inline Math'], command = mathlatex)
math.grid(column = 11, row = 0, padx = 10, pady = 10)
tabs.add(mf, text = 'Editor')
tabs.add(sf, text = 'Python Shell', state = 'hidden')
tabs.add(ef, text = 'Email', state = 'hidden')
fileinfo = root.frame()
cmdlabel = root.text()
cmdlabel.pack(side = 'left', padx = 10, pady = 10, anchor = 'n')
cmdentry = root.textbox(state = 'disabled', height = 1, bd = 1)
cmdentry.pack(padx = 10, pady = 10, fill = 'x', anchor = 'n')
fileinfo.pack(padx = 10, pady = 10, fill = 'both')
filename = root.text(master = fileinfo, text = 'The Zen of Python', padding = (5, 5, 5, 5), relief = 'raised')
filename.grid(column = 0, row = 0)
filetype = root.text(master = fileinfo, text = 'Plain Text (*.*)', padding = (5, 5, 5, 5), relief = 'sunken')
filetype.grid(column = 1, row = 0)
filesize = root.text(master = fileinfo, text = '0 bytes', padding = (5, 5, 5, 5), relief = 'raised')
filesize.grid(column = 2, row = 0)
tabs.pack(padx = 10, pady = 10, fill = 'x')
scrlbr = root.scroll(master = mf)
scrlbr.pack(side = 'right', fill = 'y')
type_ = root.textbox(master = mf, undo = True, font = (defs[2], 12), wrap = 'word')
ln = TkLineNumbers(mf, type_, justify = 'center')
ln.pack(side = 'left', fill = 'y', anchor = 'n')
type_.pack(fill = 'both', expand = True, anchor = 'n')
type_.insert('end', "The Zen of Python, by Tim Peters\n\nBeautiful is better than ugly.\nExplicit is better than implicit.\nSimple is better than complex.\nComplex is better than complicated.\nFlat is better than nested.\nSparse is better than dense.\nReadability counts.\nSpecial cases aren't special enough to break the rules.\nAlthough practicality beats purity.\nErrors should never pass silently.\nUnless explicitly silenced.\nIn the face of ambiguity, refuse the temptation to guess.\nThere should be one-- and preferably only one --obvious way to do it.\nAlthough that way may not be obvious at first unless you're Dutch.\nNow is better than never.\nAlthough never is often better than *right* now.\nIf the implementation is hard to explain, it's a bad idea.\nIf the implementation is easy to explain, it may be a good idea.\nNamespaces are one honking great idea -- let's do more of those!")
scrlbr.config(command = type_.yview)
type_.config(yscrollcommand = lambda *args: [scrlbr.set(*args), ln.redraw()])
type_.focus_set()
_init_hl_tags()
m = root.menu()
root.config(m = m)
fm = root.menu()
em = root.menu()
om = root.menu()
pm = root.menu()
lm = root.menu()
pcm = root.menu()
hm = root.menu()
mg = root.menu()
plgnm = root.menu()
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
m.add_cascade(label = 'File', menu = fm)
m.add_cascade(label = 'Edit', menu = em)
m.add_cascade(label = 'Options', menu = om)
m.add_cascade(label = 'PyCode', menu = pcm)
m.add_cascade(label = 'MathGod', menu = mg)
m.add_cascade(label = 'Plugins', menu = plgnm)
plgnm.add_command(label = 'Download From PyNotes\' GitHub', command = dp)
plgnm.add_command(label = 'Open Plugins Directory', command = op)
plgnm.add_separator()
plgnm.add_command(label = 'Help with Adding Plugins', command = ap)
pm.add_command(label = 'Run → F5', command = rp)
lm.add_command(label = 'Run LuaLaTeX → F5', command = lambda: runtex('lua'))
root.bind('<F5>', lambda event: f5())
lm.add_command(label = 'Run PdfLaTeX', command = lambda: runtex('pdf'))
m.add_cascade(label = 'Help', menu = hm)
em.add_command(label = 'Undo → Ctrl + Z / Alt + X - u', command = undo)
em.add_command(label = 'Redo → Ctrl + Shift + Z / Alt + X - r', command = redo)
root.bind('<Control-z>', lambda event: undo())
root.bind('<Control-Z>', lambda event: redo())
em.add_separator()
em.add_command(label = 'Copy → Ctrl + C / Alt + X - c', command = cp)
em.add_command(label = 'Paste → Ctrl + V / Alt + X - p', command = pst)
em.add_command(label = 'Cut → Ctrl + X / Alt + X - cut', command = cut)
em.add_command(label = 'Select All → Ctrl + A / Alt + X - a', command = selall)
hm.add_command(label = 'About', command = abt)
hm.add_command(label = f'What\'s new in {v}?', command = changes)
hm.add_command(label = 'Help with commands → Alt + X - h', command = hx)
hm.add_command(label = 'Help with Email', command = hemail)
hm.add_command(label = 'Help with PyCode', command = helppycode)
hm.add_command(label = 'Help with MathGod', command = helpmathgod)
hm.add_command(label = 'Help with Adding Plugins', command = ap)
hm.add_separator()
hm.add_command(label = 'Recover backup', command = rb)
fm.add_command(label = 'New → Ctrl + N / Alt + X - n', command = nw)
root.bind('<Control-n>', lambda event: nw())
fm.add_command(label = 'Open → Ctrl + O / Alt + X - o', command = llld)
root.bind('<Control-o>', lambda event: llld())
fm.add_separator()
fm.add_command(label = 'Save → Ctrl + S / Alt + X - s', command = sssv)
root.bind('<Control-s>', lambda event: sssv())
fm.add_command(label = 'Save as → Ctrl + Shift + S / Alt + X - sa', command = ssv)
root.bind('<Control-S>', lambda event: ssv())
fm.add_separator()
fm.add_command(label = 'Quit → Ctrl + W / Alt + X - e', command = ext)
root.bind('<Control-w>', lambda event: ext())
pcm.add_command(label = 'Start', command = pc)
pcm.add_separator()
pcm.add_command(label = 'Help', command = helppycode)
om.add_command(label = 'Preferences → Ctrl + P / Alt + X - prf', command = prf)
om.add_command(label = 'Source Code → Alt + X - source-code', command = ss)
om.add_separator()
om.add_command(label = 'Go to line → Alt + L / Alt + X - gl', command = gl)
root.bind('<Alt-l>', lambda event: gl())
om.add_command(label = 'Page turn → Ctrl + P / Alt + X - pf', command = ptf)
root.bind('<Control-p>', lambda event: ptf())
om.add_command(label = 'Page turn (back) → Ctrl + Shift + P / Alt + X - pb', command = ptb)
root.bind('<Control-P>', lambda event: ptb())
om.add_separator()
om.add_command(label = 'Command → Alt + X', command = cmd)
om.add_command(label = 'PyCode → Alt + X - pc', command = pc)
om.add_separator()
om.add_command(label = 'Speech to Text → Alt + X - st', command = st)
em.add_separator()
em.add_command(label = 'Find → Ctrl + F / Alt + X - f', command = f)
root.bind('<Control-f>', lambda event: f())
em.add_command(label = 'Find & Replace → Ctrl + Shift + F / Alt + X - fr', command = fr)
root.bind('<Control-F>', lambda event: fr())
readonlytextforshellpy = '>>> '
readonlyendforshellpy = '1.' + str(len('>>> '))
continuation = False
continuationcodeforshellpy = ''
_hapyshell_running = [False]
_pyshell_last_stripped_text = None
_pyshell_cached_scope_result = None
_pyshell_session_names = {}
_pyshell_session_types = {}
_pyshell_session_classes = {}
_pyshell_session_aliases = {}
_pyshell_session_origins = {}
_pyshell_session_method_params = {}
_pyshell_session_accepts_any = set()
def hapyshell():
	global _pyshell_last_stripped_text
	global _pyshell_cached_scope_result
	global _pyshell_session_names
	global _pyshell_session_types
	global _pyshell_session_classes
	global _pyshell_session_aliases
	global _pyshell_session_origins
	global _pyshell_session_method_params, _pyshell_session_accepts_any
	if _hapyshell_running[0]:
		return
	_hapyshell_running[0] = True
	lenprompt = len('>>> ')
	full_text = shellcmd.get('1.0', 'end')
	stripped_lines = []
	_exec_boundary = 1
	for line in full_text.split('\n'):
		prefix = line[:lenprompt]
		if prefix in ('>>> ', '... '):
			stripped_lines.append(line[lenprompt:])
			if prefix == '>>> ':
				_exec_boundary = len(stripped_lines)
		else:
			stripped_lines.append('')
	stripped_text = '\n'.join(stripped_lines)
	if stripped_text == _pyshell_last_stripped_text:
		shell_result = _pyshell_cached_scope_result
	else:
		shell_result = _python_build_scopes(stripped_text, seed_names = _pyshell_session_names, seed_types = _pyshell_session_types, seed_classes = _pyshell_session_classes, seed_aliases = _pyshell_session_aliases, seed_origins = _pyshell_session_origins, seed_method_params = _pyshell_session_method_params, seed_accepts_any = _pyshell_session_accepts_any)
		_pyshell_last_stripped_text = stripped_text
		_pyshell_cached_scope_result = shell_result
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
		shell_class_module_origin = {}
		shell_local_class_method_params = {}
		shell_local_class_accepts_any = set()
	else:
		shell_scopes, shell_call_kwargs, shell_module_aliases, shell_local_classes, shell_module_literals, shell_scope_var_types, shell_literal_attrs, shell_def_names, shell_typed_attrs, shell_param_default_tags, shell_kwarg_positions, shell_import_dotted_lines, shell_import_orig_name_tags, shell_class_module_origin, shell_local_class_method_params, shell_local_class_accepts_any = shell_result
	for _nm, _defs in shell_scopes[0]['names'].items():
		_exec_defs = [_d for _d in _defs if _d[0] < _exec_boundary]
		if _exec_defs and _nm not in shell_scopes[0].get('globals', {}) and _nm not in shell_scopes[0].get('nonlocals', {}):
			_pyshell_session_names[_nm] = _exec_defs[-1][1]
	for _nm, _tl in shell_scope_var_types.get(0, {}).items():
		_exec_tl = [_t for _t in _tl if _t[0] < _exec_boundary]
		if _exec_tl:
			_pyshell_session_types[_nm] = _exec_tl[-1][1]
	_text_class_lines = {}
	for _dl, _dn, _dk in shell_def_names:
		if _dk == 'class':
			_text_class_lines.setdefault(_dn, []).append(_dl)
	for _cn, _mem in shell_local_classes.items():
		if _cn in _PYTHON_BUILTIN_MEMBERS:
			continue
		_cls_lines = _text_class_lines.get(_cn)
		if _cls_lines is None or _cn in _pyshell_session_classes or any(_l < _exec_boundary for _l in _cls_lines):
			_pyshell_session_classes[_cn] = _mem
	_pyshell_session_aliases.update(shell_module_aliases)
	_pyshell_session_origins.update(shell_class_module_origin)
	_pyshell_session_method_params.update(shell_local_class_method_params)
	_pyshell_session_accepts_any.update(shell_local_class_accepts_any)
	syntax_tags = ('hpv', 'hpf', 'hpfa', 'hpm', 'hpo', 'hpa', 'hpb', 'hpc', 'hpd')
	try:
		shell_top = shellcmd.index('@0,0')
		shell_bottom = shellcmd.index(f'@0,{shellcmd.winfo_height()}')
	except Exception:
		shell_top = '1.0'
		shell_bottom = 'end'
	try:
		all_tags = set(shellcmd.tag_names())
		def _removable(tag):
			return tag not in _PYTHON_SHELL_HL_SKIP_REMOVE_TAGS and (tag not in skiptagspythonshell or hmode not in skiptagspythonshell[tag])
		shell_top_line = int(shell_top.split('.')[0])
		try:
			shell_bottom_line = int(shellcmd.index(shell_bottom).split('.')[0])
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
		def add_span(tag, off_s, off_e):
			l1, c1 = off2lc(off_s)
			l2, c2 = off2lc(off_e)
			shellcmd.tag_add(tag, widx(l1, c1), widx(l2, c2))
		def clear_span(off_s, off_e):
			l1, c1 = off2lc(off_s)
			l2, c2 = off2lc(off_e)
			_a = widx(l1, c1)
			_b = widx(l2, c2)
			for tag in all_tags:
				if _removable(tag):
					shellcmd.tag_remove(tag, _a, _b)
		for tag in all_tags:
			if _removable(tag):
				shellcmd.tag_remove(tag, shell_top, shell_bottom)
		for m in _PYTHON_KW_PAT.finditer(visible_code):
			add_span('hpa', m.start(), m.end())
		for m in _PYTHON_BI_PAT.finditer(visible_code):
			add_span('hpb', m.start(), m.end())
		line_scopes = {}
		for line in vis_abs:
			for k, sc in enumerate(shell_scopes):
				if sc['start'] <= line <= sc['end']:
					if line not in line_scopes or sc['start'] >= shell_scopes[line_scopes[line]]['start']:
						line_scopes[line] = k
		shell_module_literal_lines = {}
		for lineno, name in shell_module_literals:
			shell_module_literal_lines.setdefault(lineno, []).append(name)
		shell_import_dotted_by_line = {}
		for lineno, dcol, dotted in shell_import_dotted_lines:
			shell_import_dotted_by_line.setdefault(lineno, []).append((dcol, dotted))
		shell_import_orig_by_line = {}
		for _oln, _ocol, _oname, _otag in shell_import_orig_name_tags:
			shell_import_orig_by_line.setdefault(_oln, []).append((_ocol, _oname, _otag))
		shell_def_names_by_line = {}
		for _dl, _dname, _dkind in shell_def_names:
			shell_def_names_by_line.setdefault(_dl, []).append((_dname, _dkind))
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
		for li, abs_line in enumerate(vis_abs):
			line_str = vis_code[li]
			active = {}
			prior_kinds = {}
			bound = set()
			scope_idx = line_scopes.get(abs_line)
			innermost_scope = scope_idx
			innermost_parent = shell_scopes[innermost_scope]['parent'] if innermost_scope is not None else None
			on_header = innermost_scope is not None and abs_line == shell_scopes[innermost_scope]['start']
			while scope_idx is not None:
				sc = shell_scopes[scope_idx]
				if sc.get('kind') == 'class' and scope_idx != innermost_scope and not (on_header and scope_idx == innermost_parent):
					scope_idx = sc['parent']
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
					earliest = None
					for dl, kind in defs:
						if earliest is None or dl < earliest[0]:
							earliest = (dl, kind)
						if scope_idx == innermost_scope and dl > abs_line:
							continue
						if best is None or dl > best[0]:
							second_best = best
							best = (dl, kind)
						elif second_best is None or dl > second_best[0]:
							second_best = (dl, kind)
					if best is None:
						best = earliest
					bound.add(name)
					if best is not None:
						active[name] = best[1]
						if best[0] == abs_line and second_best is not None and second_best[1] != best[1]:
							prior_kinds[name] = second_best[1]
				scope_idx = sc['parent']
			groups = {}
			for name, kind in active.items():
				groups.setdefault(prior_kinds.get(name, kind), []).append(name)
			for kind, names_list in groups.items():
				if not names_list:
					continue
				tag = {'var': 'hpv', 'func': 'hpf', 'func_arg': 'hpfa', 'first_param': 'hpb', 'module': 'hpm', 'class': 'hpx'}.get(kind)
				if tag is None:
					continue
				pat = re.compile(_PYTHON_NAME_LEAD + r'(?:' + '|'.join(re.escape(nm) for nm in names_list) + r')' + _PYTHON_NAME_TRAIL)
				for m in pat.finditer(line_str):
					shellcmd.tag_add(tag, widx(abs_line, m.start()), widx(abs_line, m.end()))
			for name in prior_kinds:
				new_tag = {'var': 'hpv', 'func': 'hpf', 'func_arg': 'hpfa', 'first_param': 'hpb', 'module': 'hpm', 'class': 'hpx'}.get(active[name])
				if new_tag is None:
					continue
				m = re.search(_PYTHON_NAME_LEAD + re.escape(name) + _PYTHON_NAME_TRAIL, line_str)
				if m:
					s = widx(abs_line, m.start())
					e = widx(abs_line, m.end())
					for tag in syntax_tags:
						shellcmd.tag_remove(tag, s, e)
					shellcmd.tag_add(new_tag, s, e)
			for _dname, _dkind in shell_def_names_by_line.get(abs_line, []):
				_dm = re.match(r'\s*(?:async\s+)?def\s+(' + re.escape(_dname) + r')\b', line_str) if _dkind == 'func' else re.match(r'\s*class\s+(' + re.escape(_dname) + r')\b', line_str)
				if _dm:
					s = widx(abs_line, _dm.start(1))
					e = widx(abs_line, _dm.end(1))
					for tag in syntax_tags:
						shellcmd.tag_remove(tag, s, e)
					shellcmd.tag_add('hpf' if _dkind == 'func' else 'hpx', s, e)
			for _pcol, _pname, _pkind in shell_param_default_by_line.get(abs_line, []):
				_pcol = _python_bytecol_to_charcol(line_str, _pcol)
				_ptag = {'var': 'hpv', 'func': 'hpf', 'func_arg': 'hpfa', 'first_param': 'hpb', 'module': 'hpm', 'class': 'hpx'}.get(_pkind)
				if _ptag is not None:
					s = widx(abs_line, _pcol)
					e = widx(abs_line, _pcol + len(_pname))
					for tag in syntax_tags:
						shellcmd.tag_remove(tag, s, e)
					shellcmd.tag_add(_ptag, s, e)
			for name in shell_module_literal_lines.get(abs_line, []):
				lit_pat = re.compile(_PYTHON_NAME_LEAD + re.escape(name) + _PYTHON_NAME_TRAIL)
				for m in lit_pat.finditer(line_str):
					shellcmd.tag_add('hpm', widx(abs_line, m.start()), widx(abs_line, m.end()))
			for dcol, dotted in shell_import_dotted_by_line.get(abs_line, []):
				dcol = _python_bytecol_to_charcol(line_str, dcol)
				if line_str[dcol:dcol + len(dotted)] != dotted:
					continue
				pos = dcol
				for part in dotted.split('.'):
					shellcmd.tag_add('hpm', widx(abs_line, pos), widx(abs_line, pos + len(part)))
					pos += len(part) + 1
			for _ocol, _oname, _otag in shell_import_orig_by_line.get(abs_line, []):
				_ocol = _python_bytecol_to_charcol(line_str, _ocol)
				if line_str[_ocol:_ocol + len(_oname)] != _oname:
					continue
				shellcmd.tag_add(_otag, widx(abs_line, _ocol), widx(abs_line, _ocol + len(_oname)))
			for _col, _attr, _tname in shell_literal_attr_by_line.get(abs_line, []):
				_col = _python_bytecol_to_charcol(line_str, _col)
				_kind = _PYTHON_BUILTIN_MEMBERS[_tname].get(_attr)
				if _kind is not None:
					shellcmd.tag_add('hpf' if _kind == 'func' else 'hpv', widx(abs_line, _col), widx(abs_line, _col + len(_attr)))
			for _tcol, _tattr, _tkind in shell_typed_attr_by_line.get(abs_line, []):
				_tcol = _python_bytecol_to_charcol(line_str, _tcol)
				_ttag = {'func': 'hpf', 'var': 'hpv', 'module': 'hpm', 'class': 'hpx'}.get(_tkind, 'hpx')
				shellcmd.tag_add(_ttag, widx(abs_line, _tcol), widx(abs_line, _tcol + len(_tattr)))
			for _kcol, _kname in shell_kwarg_pos_by_line.get(abs_line, []):
				_kcol = _python_bytecol_to_charcol(line_str, _kcol)
				s = widx(abs_line, _kcol)
				e = widx(abs_line, _kcol + len(_kname))
				for tag in syntax_tags:
					shellcmd.tag_remove(tag, s, e)
				if _kname in shell_call_kwargs.get(abs_line, set()):
					shellcmd.tag_add('hpfa', s, e)
		for m in _PYTHON_OP_PAT.finditer(visible_code):
			clear_span(m.start(), m.end())
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
			clear_span(0, j)
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
			clear_span(0, j)
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
				clear_span(i, j)
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
				clear_span(i, j)
				add_span('hpd', i, j)
				i = j
			elif ch == '#':
				j = i + 1
				while j < n and visible_code[j] != '\n':
					j += 1
				clear_span(i, j)
				add_span('hpc', i, j)
				i = j
			else:
				i += 1
	except Exception:
		pass
	_hapyshell_running[0] = False
def shellpy():
	global shellcmd
	import queue as _queue
	lenprompt = len('>>> ')
	running = [True]
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
		lines = int(shellcmd.index('end-1c').split('.')[0])
		shellcmd.tag_remove('prompt', '1.0', 'end')
		for i in range(1, lines + 1):
			if not shellcmd.get(f'{i}.0', f'{i}.{lenprompt}') in {'>>> ', '... '}:
				continue
			shellcmd.tag_add('prompt', f'{i}.0', f'{i}.{lenprompt}')
		shellcmd.tag_config('prompt', foreground = 'green', font = (monospace, 14, 'bold'))
	def _process(text):
		if isinstance(text, bytes):
			text = text.decode('utf-8', errors = 'replace')
		if _pending_esc[0]:
			text = _pending_esc[0] + text
			_pending_esc[0] = ''
		shellcmd.mark_set('insert', f'{_cursor_line[0]}.{_cursor_col[0]}')
		i = 0
		n = len(text)
		while i < n:
			ch = text[i]
			_was_h1 = prev_was_H1[0]
			prev_was_H1[0] = False
			if ch == '\r':
				_cursor_col[0] = 0
				shellcmd.mark_set('insert', f'{_cursor_line[0]}.0')
				i += 1
			elif ch == '\x08':
				if _cursor_col[0] > 0:
					_cursor_col[0] -= 1
					shellcmd.mark_set('insert', f'{_cursor_line[0]}.{_cursor_col[0]}')
				i += 1
			elif ch == '\n':
				_cursor_line[0] += 1
				_cursor_col[0] = 0
				if _cursor_line[0] > screen_top[0] + 23:
					screen_top[0] = _cursor_line[0] - 23
				_last = int(shellcmd.index('end').split('.')[0]) - 1
				if _cursor_line[0] > _last:
					shellcmd.insert('end', '\n' * (_cursor_line[0] - _last))
				shellcmd.mark_set('insert', f'{_cursor_line[0]}.0')
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
							if p[0] == 0: shellcmd.delete(f'{ln}.{col}', f'{ln}.end')
							elif p[0] == 1: shellcmd.delete(f'{ln}.0', f'{ln}.{col}')
							else: shellcmd.delete(f'{ln}.0', f'{ln}.end')
						elif cmd == 'J':
							if p[0] == 2:
								if _was_h1:
									shellcmd.delete('1.0', 'end')
									screen_top[0] = 1
									_cursor_line[0] = 1
									_cursor_col[0] = 0
									shellcmd.mark_set('insert', '1.0')
								else:
									last_line = int(shellcmd.index('end').split('.')[0]) - 1
									screen_top[0] = max(screen_top[0], max(1, last_line - 23))
									if shellcmd.compare(f'{screen_top[0]}.0', '<', 'end'):
										shellcmd.delete(f'{screen_top[0]}.0', 'end')
									cur_last = int(shellcmd.index('end').split('.')[0]) - 1
									if screen_top[0] > cur_last:
										shellcmd.insert('end', '\n' * (screen_top[0] - cur_last))
									_cursor_line[0] = screen_top[0]
									_cursor_col[0] = 0
									shellcmd.mark_set('insert', f'{screen_top[0]}.0')
							elif p[0] == 3:
								if screen_top[0] > 1:
									lines_deleted = screen_top[0] - 1
									shellcmd.delete('1.0', f'{screen_top[0]}.0')
									_cursor_line[0] = max(1, _cursor_line[0] - lines_deleted)
									screen_top[0] = 1
									shellcmd.mark_set('insert', f'{_cursor_line[0]}.{_cursor_col[0]}')
							elif p[0] == 0:
								shellcmd.delete(f'{ln}.{col}', 'end')
						elif cmd in ('H', 'f'):
							row_ = p[0] if p[0] else 1
							col_ = p[1] if len(p) > 1 and p[1] else 1
							last_line = int(shellcmd.index('end').split('.')[0]) - 1
							target_line = screen_top[0] + row_ - 1
							target_line = max(1, target_line)
							_cursor_line[0] = target_line
							_cursor_col[0] = col_ - 1
							if target_line > last_line:
								shellcmd.insert('end', '\n' * (target_line - last_line))
							shellcmd.mark_set('insert', f'{target_line}.{col_ - 1}')
						elif cmd == 'A':
							mv = p[0] or 1
							_cursor_line[0] = max(1, _cursor_line[0] - mv)
							shellcmd.mark_set('insert', f'{_cursor_line[0]}.{_cursor_col[0]}')
						elif cmd == 'B':
							mv = p[0] or 1
							_cursor_line[0] += mv
							shellcmd.mark_set('insert', f'{_cursor_line[0]}.{_cursor_col[0]}')
						elif cmd == 'C':
							mv = p[0] or 1
							_cursor_col[0] += mv
							_ll = int(shellcmd.index(f'{_cursor_line[0]}.end').split('.')[1])
							if _cursor_col[0] > _ll:
								shellcmd.insert(f'{_cursor_line[0]}.end', ' ' * (_cursor_col[0] - _ll))
							shellcmd.mark_set('insert', f'{_cursor_line[0]}.{_cursor_col[0]}')
						elif cmd == 'D':
							mv = p[0] or 1
							_cursor_col[0] = max(0, _cursor_col[0] - mv)
							shellcmd.mark_set('insert', f'{_cursor_line[0]}.{_cursor_col[0]}')
						elif cmd == 'G':
							mv = p[0] or 1
							_cursor_col[0] = mv - 1
							_ll = int(shellcmd.index(f'{_cursor_line[0]}.end').split('.')[1])
							if _cursor_col[0] > _ll:
								shellcmd.insert(f'{_cursor_line[0]}.end', ' ' * (_cursor_col[0] - _ll))
							shellcmd.mark_set('insert', f'{_cursor_line[0]}.{_cursor_col[0]}')
						elif cmd == 'P':
							mv = p[0] or 1
							shellcmd.delete(f'{ln}.{col}', f'{ln}.{col + mv}')
						elif cmd == '@':
							mv = p[0] or 1
							shellcmd.insert(f'{ln}.{col}', ' ' * mv)
							shellcmd.mark_set('insert', f'{_cursor_line[0]}.{_cursor_col[0]}')
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
					if end_osc >= 0: i += end_osc + 1
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
					shellcmd.mark_set('insert', f'{_cursor_line[0]}.{_cursor_col[0]}')
					i += 2
				elif nxt == 'D':
					_cursor_line[0] += 1
					shellcmd.mark_set('insert', f'{_cursor_line[0]}.{_cursor_col[0]}')
					i += 2
				elif nxt in '()':
					if len(rest) < 3:
						_pending_esc[0] = rest
						break
					i += 3
				elif nxt == '7':
					_saved_cursor[0] = (_cursor_line[0], _cursor_col[0])
					i += 2
				elif nxt == '8':
					_cursor_line[0], _cursor_col[0] = _saved_cursor[0]
					_last = int(shellcmd.index('end').split('.')[0]) - 1
					if _cursor_line[0] > _last:
						shellcmd.insert('end', '\n' * (_cursor_line[0] - _last))
					shellcmd.mark_set('insert', f'{_cursor_line[0]}.{_cursor_col[0]}')
					i += 2
				elif nxt == '\x1b':
					i += 1
				else:
					i += 2
			elif ch == '\t':
				sp = 8 - (_cursor_col[0] % 8)
				for _ in range(sp):
					cur = shellcmd.get(f'{_cursor_line[0]}.{_cursor_col[0]}', f'{_cursor_line[0]}.{_cursor_col[0] + 1}')
					if cur and cur != '\n':
						shellcmd.delete(f'{_cursor_line[0]}.{_cursor_col[0]}', f'{_cursor_line[0]}.{_cursor_col[0] + 1}')
					shellcmd.insert(f'{_cursor_line[0]}.{_cursor_col[0]}', ' ')
					_cursor_col[0] += 1
				shellcmd.mark_set('insert', f'{_cursor_line[0]}.{_cursor_col[0]}')
				i += 1
			elif ch >= ' ' and ch != '\x7f':
				cur = shellcmd.get(f'{_cursor_line[0]}.{_cursor_col[0]}', f'{_cursor_line[0]}.{_cursor_col[0] + 1}')
				if cur and cur != '\n':
					shellcmd.delete(f'{_cursor_line[0]}.{_cursor_col[0]}', f'{_cursor_line[0]}.{_cursor_col[0] + 1}')
				if _sgr_sel[0]:
					shellcmd.insert(f'{_cursor_line[0]}.{_cursor_col[0]}', ch, 'sel')
				else:
					shellcmd.insert(f'{_cursor_line[0]}.{_cursor_col[0]}', ch)
				_cursor_col[0] += 1
				shellcmd.mark_set('insert', f'{_cursor_line[0]}.{_cursor_col[0]}')
				i += 1
			else:
				i += 1
		cursor[0] = f'{_cursor_line[0]}.{_cursor_col[0]}'
		shellcmd.mark_set('insert', cursor[0])
		colourprompts()
	def _schedule_hl():
		if not _hl_pending[0]:
			_hl_pending[0] = True
			def _run_hl():
				_hl_pending[0] = False
				hapyshell()
			shellcmd.after_idle(_run_hl)
	def _poll(gen):
		had_output = False
		backlog = False
		processed = 0
		_at_bottom = shellcmd.yview()[1] >= 0.999
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
		except _queue.Empty:
			pass
		if running[0] and gen == generation[0]:
			if had_output:
				if _at_bottom:
					shellcmd.see('end')
				shellcmd.see('insert')
				_schedule_hl()
			shellcmd.after(1 if backlog else 50, lambda: _poll(gen))
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
					except OSError:
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
					except EOFError:
						break
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
		shellcmd.after(50, lambda: _poll(gen))
	def _key(event):
		_unpost_menu()
		if not running[0]:
			return 'break'
		sym = event.keysym
		ch = event.char
		if ch or sym in ('Return', 'BackSpace', 'Delete', 'Up', 'Down', 'Left', 'Right', 'Tab', 'Home', 'End'):
			_clear_selection()
		try:
			if sym == 'Return':
				_write_ref[0](b'\r')
			elif sym == 'BackSpace': _write_ref[0](b'\x7f')
			elif sym == 'Delete': _write_ref[0](b'\x1b[3~')
			elif sym == 'Up': _write_ref[0](b'\x1b[A')
			elif sym == 'Down': _write_ref[0](b'\x1b[B')
			elif sym == 'Left': _write_ref[0](b'\x1b[D')
			elif sym == 'Right': _write_ref[0](b'\x1b[C')
			elif sym == 'Tab': _write_ref[0](b'\t')
			elif sym == 'Home': _write_ref[0](b'\x1b[H')
			elif sym == 'End': _write_ref[0](b'\x1b[F')
			elif ch: _write_ref[0](ch.encode('utf-8'))
		except OSError:
			pass
		return 'break'
	def _clear_selection():
		try:
			shellcmd.tag_remove('sel', '1.0', 'end')
		except Exception:
			pass
	def _copy_selection(e = None):
		try:
			sel = shellcmd.get('sel.first', 'sel.last')
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
			except OSError:
				pass
		return 'break'
	def _select_all(e = None):
		shellcmd.tag_add('sel', '1.0', 'end-1c')
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
			try: _shellmenu.unpost()
			except Exception: pass
	def _shellmenu_keyclose(e):
		if e.keysym not in ('Up', 'Down', 'Left', 'Right', 'Return', 'space', 'Shift_L', 'Shift_R', 'Control_L', 'Control_R', 'Alt_L', 'Alt_R'):
			_unpost_menu()
			return 'break'
	_shellmenu.bind('<KeyPress>', _shellmenu_keyclose)
	_shellmenu.bind('<Unmap>', lambda e: _menu_posted.__setitem__(0, False))
	def _popup(e):
		shellcmd.focus_set()
		_menu_posted[0] = True
		try:
			_shellmenu.tk_popup(e.x_root, e.y_root)
		finally:
			_shellmenu.grab_release()
		return 'break'
	def cs():
		shellcmd.delete('1.0', 'end')
		cursor[0] = '1.0'
		screen_top[0] = 1
		prev_was_H1[0] = False
		_pending_esc[0] = ''
		_sgr_sel[0] = False
		_cursor_line[0] = 1
		_cursor_col[0] = 0
		shellcmd.focus()
		if platform.system() == 'Linux':
			try: _write_ref[0](b'\x0c')
			except Exception: pass
		else:
			try: _write_ref[0](b'\r')
			except Exception: pass
	def ks():
		global _pyshell_last_stripped_text, _pyshell_cached_scope_result
		running[0] = False
		_pyshell_last_stripped_text = None
		_pyshell_cached_scope_result = None
		_pyshell_session_names.clear()
		_pyshell_session_types.clear()
		_pyshell_session_classes.clear()
		_pyshell_session_aliases.clear()
		_pyshell_session_origins.clear()
		_pyshell_session_method_params.clear()
		_pyshell_session_accepts_any.clear()
		try: _proc_ref[0].terminate()
		except Exception: pass
		if platform.system() == 'Linux' and _mfd_ref[0] is not None:
			try: os.close(_mfd_ref[0])
			except Exception: pass
			_mfd_ref[0] = None
		shellcmd.delete('1.0', 'end')
		cursor[0] = '1.0'
		screen_top[0] = 1
		prev_was_H1[0] = False
		_pending_esc[0] = ''
		_sgr_sel[0] = False
		_cursor_line[0] = 1
		_cursor_col[0] = 0
		shellcmd.focus()
		_start()
	shellcmd = root.textbox(master = sf, font = (monospace, 12), wrap = 'none')
	clearshell = root.button(master = sf, text = 'Clear Shell', command = cs)
	killshell = root.button(master = sf, text = 'Restart Shell', command = ks)
	shellcmd.pack(fill = 'both')
	clearshell.pack(anchor = 'sw', side = 'left', padx = 10, pady = 10)
	killshell.pack(anchor = 'sw', side = 'left', padx = 10, pady = 10)
	shellcmd.unbind('<Control-a>')
	def _snap_caret(e = None):
		def _do():
			try: shellcmd.mark_set('insert', cursor[0])
			except Exception: pass
		try: shellcmd.after_idle(_do)
		except Exception: pass
	shellcmd.bind('<Key>', _key)
	shellcmd.bind('<Button-1>', lambda e: _unpost_menu())
	shellcmd.bind('<ButtonRelease-1>', _snap_caret)
	shellcmd.bind('<ButtonRelease-3>', _popup)
	shellcmd.bind('<Button-2>', _paste_clipboard)
	shellcmd.bind('<<Paste>>', _paste_clipboard)
	shellcmd.bind('<<PasteSelection>>', _paste_clipboard)
	shellcmd.bind('<<Cut>>', lambda e: _copy_selection())
	shellcmd.bind('<<Clear>>', lambda e: 'break')
	shellcmd.bind('<Control-Shift-C>', _copy_selection)
	shellcmd.bind('<Control-Shift-V>', _paste_clipboard)
	shellcmd.bind('<Control-C>', _copy_selection)
	shellcmd.bind('<Control-V>', _paste_clipboard)
	def shell_setview():
		hapyshell()
		shellcmd.after(50, shell_setview)
	_start()
	shellcmd.after(50, shell_setview)
shellpy()
_init_pythonshell_hl_tags()
def mathgod():
	show('open mathgod')
	subprocess.Popen([sys.executable, f'{rootdir}/MathGod.py'])
def emailsetup(saved = None):
	global e
	global p
	global s
	global po
	attachments = []
	def removeattach():
		def actualremoveattachment(attachment):
			del attachmentslist[attachment]
			del attachments[attachment]
			attachmentslistwidget.config(text = 'Attachments: ' + ' , '.join(attachmentslist))
			raw.destroy()
		if attachmentslist:
			raw = root.subwin()
			for i in range(len(attachmentslist)):
				attachment = attachmentslist[i]
				raw.button(text = attachment, command = lambda i = i: actualremoveattachment(i)).grid(column = i % 5, row = mathmod.floor(i / 5), sticky = 'ew')
	def attach():
		if platform.system() == 'Linux':
			fn = subprocess.run(['zenity', '--file-selection', '--filename=./', '--title=Open File', '--file-filter=All Files | *'], capture_output = True, text = True).stdout.strip()
		else:
			fn = fd.askopenfilename(title = 'Open File', filetypes = (('All Files', '*')))
		if fn:
			try:
				with open(fn, 'rb') as attachment:
					part = MIMEBase('application', 'octet-stream')
					part.set_payload(attachment.read())
					encoders.encode_base64(part)
					part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(fn)}')
					if not os.path.basename(fn) in attachmentslist:
						attachments.append(part)
						attachmentslist.append(os.path.basename(fn))
						attachmentslistwidget.config(text = 'Attachments: ' + ' , '.join(attachmentslist))
			except Exception as error:
				root.error('Error', str(error))
	def changeinfo():
		def emailsetupother():
			global e
			global p
			global s
			global po
			entryframe.pack(padx = 10, pady = 10, fill = 'x', anchor = 'n', expand = True)
			buttonframe.pack(padx = 10, pady = 10, fill = 'x', anchor = 'n', expand = True)
			emailtextbox.pack(fill = 'both', expand = True, padx = 10, pady = 10)
			e = email.get()
			p = password.get()
			s = server.get()
			po = port.get()
			file = open(f'{homedir}/.pynotesemailconfig', 'w+', encoding = 'utf-8')
			file.write(f'{e}\n{p}\n{s}\n{po}')
			file.close()
			encryptdecrypt(f'{homedir}/.pynotesemailconfig')
			loginframe.pack_forget()
		entryframe.pack_forget()
		buttonframe.pack_forget()
		emailtextbox.pack_forget()
		loginframe = root.frame(master = ef)
		loginframe.pack(expand = True)
		root.text(master = loginframe, text = 'Email:').grid(column = 0, row = 0, padx = 10, pady = 10)
		email = root.entry(master = loginframe)
		email.grid(column = 1, row = 0, padx = 10, pady = 10)
		root.text(master = loginframe, text = 'Password:').grid(column = 0, row = 1, padx = 10, pady = 10)
		password = root.entry(master = loginframe, show = '*')
		password.grid(column = 1, row = 1, padx = 10, pady = 10)
		root.text(master = loginframe, text = 'Smtp Server:').grid(column = 0, row = 2, padx = 10, pady = 10)
		server = root.entry(master = loginframe)
		server.grid(column = 1, row = 2, padx = 10, pady = 10)
		root.text(master = loginframe, text = 'Smtp Port:').grid(column = 0, row = 3, padx = 10, pady = 10)
		port = root.entry(master = loginframe)
		port.grid(column = 1, row = 3, padx = 10, pady = 10)
		root.button(master = loginframe, text = 'Done', command = emailsetupother).grid(column = 1, row = 4, padx = 10, pady = 10, sticky = 'e')
	def sendemail():
		global e
		global p
		global s
		global po
		recipients = recipiententry.get().split(',')
		subject = subjectentry.get()
		if not subject:
			subject = '(No Subject)'
		body = emailtextbox.get('1.0', 'end-1c')
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
					root.error('Error', str(error))
					show('email failed')
					return
		emailtextbox.delete('1.0', 'end')
		recipiententry.delete(0, 'end')
		attachments.clear()
		attachmentslist.clear()
		attachmentslistwidget.config(text = 'Attachments:')
		subjectentry.delete(0, 'end')
		show('email sent')
		root.info('Info', 'Email Sent Successfully!')
		return 'break'
	def spellcheck():
		if not emailwordlist:
			return
		emailtextbox.tag_remove('wrong', '1.0', 'end')
		n = '1.0'
		search = r'\w+'
		while True:
			count = root.intvar()
			n = emailtextbox.search(search, n, nocase = 1, count = count, stopindex = 'end', regexp = True)
			if not n: break
			nn = '%s+%dc' % (n, count.get())
			if not emailtextbox.get(n, nn).lower() in emailwordlist and len(emailtextbox.get(n, nn)) > 1:
				try:
					int(emailtextbox.get(n, nn))
				except Exception:
					emailtextbox.tag_add('wrong', n, nn)
			n = nn
		n = '1.0'
	if not saved:
		e = email.get()
		p = password.get()
		s = server.get()
		po = port.get()
		loginframe.pack_forget()
		ans = root.ask('', 'Do you want PyNotes to save your email and password?', ['yes', 'no'])
		if ans:
			file = open(f'{homedir}/.pynotesemailconfig', 'w+', encoding = 'utf-8')
			file.write(f'{e}\n{p}\n{s}\n{po}')
			file.close()
			encryptdecrypt(f'{homedir}/.pynotesemailconfig')
	else:
		encryptdecrypt(f'{homedir}/.pynotesemailconfig')
		file = open(f'{homedir}/.pynotesemailconfig', 'r', encoding = 'utf-8').read().split('\n')
		encryptdecrypt(f'{homedir}/.pynotesemailconfig')
		e = file[0]
		p = file[1]
		s = file[2]
		po = file[3]
	entryframe = root.frame(master = ef)
	recipiententry = root.entry(master = entryframe)
	root.text(master = entryframe, text = 'Recipients (separate by commas):').grid(column = 0, row = 0, padx = 10, pady = 10, sticky = 'e')
	recipiententry.grid(column = 1, row = 0, padx = 10, pady = 10, sticky = 'ew')
	root.text(master = entryframe, text = 'Subject:').grid(column = 0, row = 1, padx = 10, pady = 10, sticky = 'e')
	subjectentry = root.entry(master = entryframe)
	subjectentry.grid(column = 1, row = 1, padx = 10, pady = 10, sticky = 'ew')
	entryframe.pack(padx = 10, pady = 10, fill = 'both', anchor = 'n', expand = True)
	entryframe.columnconfigure(1, weight = 1)
	buttonframe = root.frame(master = ef)
	buttonframe.pack(padx = 10, pady = 10, fill = 'both', anchor = 'n', expand = True)
	root.button(master = buttonframe, text = 'Send (Ctrl + Enter)', command = sendemail).pack(fill = 'x', expand = True, padx = 10, pady = 10, side = 'left', anchor = 'n')
	root.button(master = buttonframe, text = 'Attach', command = attach).pack(fill = 'x', expand = True, padx = 10, pady = 10, side = 'right', anchor = 'n')
	root.button(master = buttonframe, text = 'Change Info', command = changeinfo).pack(fill = 'x', expand = True, padx = 10, pady = 10, side = 'left', anchor = 'n')
	root.button(master = buttonframe, text = 'Remove Attachment', command = removeattach).pack(fill = 'x', expand = True, padx = 10, pady = 10, side = 'right', anchor = 'n')
	attachmentslist = []
	attachmentslistwidget = root.text(master = buttonframe, text = 'Attachments:')
	attachmentslistwidget.pack(fill = 'x', expand = True, padx = 10, pady = 10)
	emailtextbox = root.textbox(master = ef, scrolled = True, font = (monospace, 15))
	emailtextbox.tag_config('wrong', underline = True, underlinefg = 'red')
	emailtextbox.pack(fill = 'both', expand = True, padx = 10, pady = 10)
	emailtextbox.bind('<Control-Return>', lambda event: sendemail())
	emailtextbox.bind('<KeyRelease>', lambda event: spellcheck())
emailwordlist = []
try:
	for dictionary in dicts:
		if dictionary:
			emailwordlist.extend(open(dictionary, 'r', encoding = 'utf-8').read().split('\n'))
except Exception as error:
	root.error('Error', error)
try:
	open(f'{homedir}/.pynotesemailconfig', 'r', encoding = 'utf-8')
except Exception:
	loginframe = root.frame(master = ef)
	loginframe.pack(expand = True)
	root.text(master = loginframe, text = 'Email:').grid(column = 0, row = 0, padx = 10, pady = 10)
	email = root.entry(master = loginframe)
	email.grid(column = 1, row = 0, padx = 10, pady = 10)
	root.text(master = loginframe, text = 'Password:').grid(column = 0, row = 1, padx = 10, pady = 10)
	password = root.entry(master = loginframe, show = '*')
	password.grid(column = 1, row = 1, padx = 10, pady = 10)
	root.text(master = loginframe, text = 'Smtp Server:').grid(column = 0, row = 2, padx = 10, pady = 10)
	server = root.entry(master = loginframe)
	server.grid(column = 1, row = 2, padx = 10, pady = 10)
	root.text(master = loginframe, text = 'Smtp Port:').grid(column = 0, row = 3, padx = 10, pady = 10)
	port = root.entry(master = loginframe)
	port.grid(column = 1, row = 3, padx = 10, pady = 10)
	root.button(master = loginframe, text = 'Let\'s Go!', command = emailsetup).grid(column = 1, row = 4, padx = 10, pady = 10, sticky = 'e')
else:
	try:
		emailsetup('saved')
	except Exception:
		root.error('Error', 'The saved email details are corrupted. Remaking file.')
		os.remove(f'{homedir}/.pynotesemailconfig')
	loginframe = root.frame(master = ef)
	loginframe.pack(expand = True)
	root.text(master = loginframe, text = 'Email:').grid(column = 0, row = 0, padx = 10, pady = 10)
	email = root.entry(master = loginframe)
	email.grid(column = 1, row = 0, padx = 10, pady = 10)
	root.text(master = loginframe, text = 'Password:').grid(column = 0, row = 1, padx = 10, pady = 10)
	password = root.entry(master = loginframe, show = '*')
	password.grid(column = 1, row = 1, padx = 10, pady = 10)
	root.text(master = loginframe, text = 'Smtp Server:').grid(column = 0, row = 2, padx = 10, pady = 10)
	server = root.entry(master = loginframe)
	server.grid(column = 1, row = 2, padx = 10, pady = 10)
	root.text(master = loginframe, text = 'Smtp Port:').grid(column = 0, row = 3, padx = 10, pady = 10)
	port = root.entry(master = loginframe)
	port.grid(column = 1, row = 3, padx = 10, pady = 10)
	root.button(master = loginframe, text = 'Let\'s Go!', command = emailsetup).grid(column = 1, row = 4, padx = 10, pady = 10, sticky = 'e')
root.bind('<Alt-x>', lambda event: cmd())
type_.bind('<Control-a>', lambda event: selall())
type_.bind('<Control-c>', lambda event: cp())
type_.bind('<Control-v>', lambda event: pst())
type_.bind('<Control-x>', lambda event: cut())
om.add_command(label = 'Terminal → Alt + X - t', command = term)
om.add_separator()
om.add_command(label = 'Speak Text → Alt + X - sp', command = spk)
type_.bind('<KeyRelease>', lambda event: keypress())
type_.bind('<BackSpace>', lambda event: show('delete text'))
type_.bind('<Delete>', lambda event: show('delete text'))
root.protocol('WM_DELETE_WINDOW', ext)
mg.add_command(label = 'Start', command = mathgod)
mg.add_separator()
mg.add_command(label = 'Help', command = helpmathgod)
wholenewwords = []
for command in plgnpccmds:
	pycodetopythoncommands[command] = plgnpccmds[command][1]
pcread()
try:
	file = open(f'{homedir}/.pynotesstartup', 'r', encoding = 'utf-8').read().split('\n')
except Exception:
	pass
else:
	for line in file:
		try:
			exec(line, globals())
		except Exception as error:
			root.error('Error', f'Error in PyCode: {error}')
pcmax()
type_setview()
_main_poll()
if defs[3] in root.themes():
	root.style(defs[3])
type_.edit_reset()
_python_reset_scan_state()
type_.bind('<Return>', lambda event: indent())
for code in last:
	try:
		exec(code[1])
	except Exception as error:
		root.error('Error!', f'There was an error in the last part of the plugin "{os.path.basename(os.path.normpath(code[0]))}":\n{error}')
_init_plugin_tags()
if len(sys.argv) > 1:
	ld(sys.argv[1])
	if len(sys.argv) > 2:
		for file in sys.argv[2:]:
			subprocess.Popen([sys.executable, sys.argv[0], file])
if new:
	prf()
root.show()