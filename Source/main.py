import os
import sys
import platform
import getpass
import subprocess
import shutil
import copy
import codecs
import base64
import smtplib
import webbrowser
import keyword
import wave
import re
import threading
import queue
import ast
import warnings
import io
import time
import math as mathmod
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import state
from encrypter import encryptdecrypt
import urllib.request
import zipfile
from init import v, rootdir, homedir, monospace, info, switchvenv
import init
from cli import argparse
from tkinter import messagebox as mb
options, files_to_open = argparse({'version': False, 'changes': False, 'plugin-list-github': False, 'plugin-list-installed': False, 'no-load-pycode': False, 'no-load-plugins': False, 'pycode-exec': True, 'command-exec': True, 'help': False, 'plugin-install': True, 'plugin-remove': True, 'plugin-describe': True}, sys.argv[1:])
changelist = ['Added reverse search and separated forward search from search from beginning.', 'Added setattr and getattr commands to PyCode.', 'Fixed upgrading ttkbootstrap from 1.x failing.', 'Fixed some bugs.']
state.changestr = ''
for i in range(len(changelist) - 1):
	state.changestr += f'{i + 1}. {changelist[i]}\n\n'
state.changestr += f'{len(changelist)}. {changelist[-1]}'
if sum([bool(options[op]) for op in ('version', 'changes', 'help', 'plugin-list-github', 'plugin-list-installed', 'plugin-install', 'plugin-describe')]) > 1:
	print(options)
	print(f'error: cannot combine --version, --changes, --help, --plugin-list-github, --plugin-list-installed, --plugin-install, --plugin-describe arguments')
	exit(1)
if options['version']:
	print(f'This is PyNotes v{v}.')
	exit()
if options['changes']:
	print(f'Changes in v{v}:\n' + state.changestr.replace('\n\n', '\n'))
	exit()
os.makedirs(f'{homedir}/.local/share/PyNotes/add-ons', exist_ok = True)
os.makedirs(f'{homedir}/.local/share/PyNotes/themes', exist_ok = True)
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
		plgn = urllib.request.urlopen(f'https://raw.githubusercontent.com/rafugafu/PyNotes/main/Plugins/{options["plugin-install"].replace(" ", "%20")}.zip').read()
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
if platform.system() == 'Linux':
	os.environ['PATH'] = f'{homedir}/.local/share/PyNotes/venv/bin:' + os.environ['PATH']
switchvenv()
try:
	import easytk
except Exception:
	if mb.askyesno('Info', 'The module \'ttkbootstrap\' is not installed. PyNotes will not be able to run without this module. Should PyNotes install it locally?'):
		pipdir = os.path.dirname(sys.executable)
		subprocess.run([os.path.join(pipdir, 'pip'), 'install', '-U', 'ttkbootstrap'])
	try:
		import easytk
	except Exception:
		mb.showerror('Error', 'ttkbootstrap was not installed successfully. Quitting PyNotes.')
		exit(1)
if platform.system() != 'Linux':
	fd = easytk.fd
from python_scope_build import _PYTHON_BUILTIN_MEMBERS, _PYTHON_BUILTIN_CALLABLE_PARAMS, _PYTHON_BUILTIN_CALLABLE_NAMES, _PYTHON_BUILTIN_NAMES, _PYTHON_BUILTIN_METHOD_RETURNS, _PythonScanCancelled, _PythonScopeBuilder, _python_method_has_implicit_first_param, _python_c3_linearize, _python_partial_target, _python_unwrap_descriptor, _python_import_fromlist_is_nonempty, _python_static_value_kind, _python_inspect_ast_members, _PythonModuleSpec, _python_resolve_toplevel_fs, _python_module_src_path, _python_relative_import_target
init.ensure_dependencies()
file, new, defaultdefs = init.load_or_create_defs()
init_plugin, first_plugin, last_plugin = init.load_plugins(options['no-load-plugins'])
vars(state).update(globals())
for code in init_plugin:
	try:
		exec(code[1], vars(state))
	except Exception as error:
		error = str(error)
		info('Error!', f'There was an error in initializing the plugin "{os.path.basename(os.path.normpath(code[0]))}":\n{error}')
try:
	import tika
	from tika import parser
except Exception:
	pass
try:
	import pdfplumber
except Exception:
	pass
try:
	import pyttsx3 as stt
except Exception:
	pass
try:
	import matplotlib.pyplot as plt
except Exception:
	pass
try:
	import sympy
except Exception:
	pass
try:
	import sounddevice as sd
except Exception:
	pass
try:
	import speech_recognition as sr
except Exception:
	pass
try:
	import numpy as np
except Exception:
	pass
try:
	from tklinenums import TkLineNumbers
except Exception:
	pass
try:
	import ziamath
except Exception:
	pass
try:
	import cairosvg
except Exception:
	pass
try:
	from PIL import Image
except Exception:
	pass
try:
	from watchdog.observers import Observer
	from watchdog.events import FileSystemEventHandler
except Exception:
	pass
if platform.system() != 'Linux':
	from winpty import PtyProcess
import utils
import buffer
import speech
import dialogs
import editor
import terminal
import command
import pycode
import window
import help
import preferences
for _m in (utils, buffer, speech, dialogs, editor, terminal, command, pycode, window, help, preferences):
	globals().update({_k: _v for _k, _v in vars(_m).items() if not _k.startswith('__')})
del _m
init.create_root_and_menus()
init.load_config(file, defaultdefs)
vars(state).update(globals())
for code in first_plugin:
	try:
		exec(code[1], vars(state))
	except Exception as error:
		error = str(error)
		state.root.error('Error!', f'There was an error in the first part of the plugin "{os.path.basename(os.path.normpath(code[0]))}":\n{error}')
state._PYTHON_EDITOR_HL_SKIP_REMOVE_TAGS = {'sel', 'marked', 'found', 'foundhighlight'}
state._PYTHON_SHELL_HL_SKIP_REMOVE_TAGS = {'sel', 'prompt', 'wrapcont'}
state.skiptags = {}
state.skiptagspythonshell = {}
state.plugin_hl = {}
state.engine = stt.init()
state.pcwrittencommands = {}
state.pcbeforehooks = {}
state.pcafterhooks = {}
state.cmdentry = state.root.textbox(state = 'disabled', height = 1, bd = 1, font = (monospace, 12))
state.cmdentry.pack(padx = 10, pady = 10, fill = 'x', anchor = 'n')
state.cmdautocomplete = state.root.textbox(state = 'disabled', bd = 1, font = (monospace, 10), wrap = 'word')
state.plgnm.add_command(label = 'Download From PyNotes\' GitHub', command = dp)
state.plgnm.add_command(label = 'Open Plugins Directory', command = op)
state.plgnm.add_separator()
state.plgnm.add_command(label = 'Help with Adding Plugins', command = ap)
state.pm.add_command(label = 'Run → F5', command = lambda: state.active.rp())
state.lm.add_command(label = 'Run LuaLaTeX → F5', command = lambda: state.active.runtex('lua'))
state.lm.add_command(label = 'Run PdfLaTeX', command = lambda: state.active.runtex('pdf'))
state.em.add_command(label = 'Undo → Ctrl + Z / Alt + X - u', command = lambda: state.active.undo())
state.em.add_command(label = 'Redo → Ctrl + Shift + Z / Alt + X - r', command = lambda: state.active.redo())
state.em.add_separator()
state.em.add_command(label = 'Copy selection → Ctrl + C / Alt + X - c', command = lambda: state.active.cp() if hasattr(state.active, 'cp') else show('cannot copy in current buffer'))
state.em.add_command(label = 'Paste clipboard → Ctrl + V / Alt + X - p', command = lambda: state.active.pst() if hasattr(state.active, 'pst') else show('cannot paste in current buffer'))
state.em.add_command(label = 'Cut selection → Ctrl + X / Alt + X - cut', command = lambda: state.active.cut())
state.em.add_separator()
state.em.add_command(label = 'Select all → Ctrl + A / Alt + X - a', command = lambda: state.active.selall() if hasattr(state.active, 'selall') else show('cannot select all in current buffer'))
state.hm.add_command(label = 'About', command = abt)
state.hm.add_command(label = f'What\'s new in {v}?', command = changes)
state.hm.add_command(label = 'Help with commands → Alt + X - h', command = hx)
state.hm.add_command(label = 'Help with Email', command = hemail)
state.hm.add_command(label = 'Help with PyCode', command = helppycode)
state.hm.add_command(label = 'Help with MathGod', command = helpmathgod)
state.hm.add_command(label = 'Help with Adding Plugins', command = ap)
state.hm.add_separator()
state.hm.add_command(label = 'Recover backup', command = rb)
state.tem.add_command(label = 'Copy → Ctrl + Shift + C / Alt + X - c', command = lambda: state.active.cp() if hasattr(state.active, 'cp') else show('cannot copy in current buffer'))
state.tem.add_command(label = 'Paste → Ctrl + Shift + V / Alt + X - p', command = lambda: state.active.pst() if hasattr(state.active, 'pst') else show('cannot paste in current buffer'))
state.tem.add_separator()
state.tem.add_command(label = 'Select All → Ctrl + Shift + A / Alt + X - a', command = lambda: state.active.selall() if hasattr(state.active, 'selall') else show('cannot select all in current buffer'))
state.fm.add_command(label = 'New → Ctrl + N / Alt + X - n', command = lambda: state.active.nw() if hasattr(state.active, 'nw') else show('cannot open new file in current buffer'))
state.fm.add_command(label = 'New Editor Horizontal → Ctrl + Shift + N / Alt + X - neh', command = lambda: neweditor(orient = 'horizontal'))
state.fm.add_command(label = 'New Editor Vertical → Alt + X - nev', command = lambda: neweditor(orient = 'vertical'))
state.fm.add_command(label = 'Open → Ctrl + O / Alt + X - o', command = lambda: state.active.llld() if hasattr(state.active, 'llld') else show('cannot open file in current buffer'))
state.fm.add_command(label = 'Open in New Editor Horizontal → Ctrl + Shift + O / Alt + X - onh', command = lambda: neweditor(True))
state.fm.add_command(label = 'Open in New Editor Vertical → Alt + X - onv', command = lambda: neweditor(True, 'vertical'))
state.fm.add_separator()
state.fm.add_command(label = 'Save → Ctrl + S / Alt + X - s', command = lambda: state.active.sssv() if hasattr(state.active, 'sssv') else show('cannot save file in current buffer'))
state.fm.add_command(label = 'Save As → Ctrl + Shift + S / Alt + X - sa', command = lambda: state.active.ssv() if hasattr(state.active, 'ssv') else show('cannot save file in current buffer'))
state.fm.add_separator()
state.fm.add_command(label = 'Switch Buffer → Alt + X - sw', command = setactive)
state.fm.add_command(label = 'Close Current Buffer → Ctrl + W / Alt + X - cb', command = pcclosebuff)
state.fm.add_separator()
state.fm.add_command(label = 'Quit PyNotes → Ctrl + Q / Alt + X - e', command = ext)
state.pcm.add_command(label = 'Start', command = pc)
state.pcm.add_separator()
state.pcm.add_command(label = 'Help', command = helppycode)
state.om.add_command(label = 'Preferences → Alt + X - prf', command = prf)
state.om.add_command(label = 'Open PyNotes Source Code → Alt + X - source-code', command = ss)
state.om.add_separator()
state.om.add_command(label = 'Go to line → Alt + L / Alt + X - gl', command = lambda: state.active.gl() if isinstance(state.active, Editor) else show('not an editor'))
state.om.add_command(label = 'Page turn forward → Ctrl + P / Alt + X - pf', command = lambda: state.active.ptf())
state.om.add_command(label = 'Page turn backward → Ctrl + Shift + P / Alt + X - pb', command = lambda: state.active.ptb())
state.om.add_separator()
state.om.add_command(label = 'Command → Alt + X', command = cmd)
state.om.add_command(label = 'PyCode → Alt + X - pc', command = pc)
state.om.add_separator()
state.om.add_command(label = 'Speech to Text → Alt + X - st', command = st)
state.em.add_separator()
state.em.add_command(label = 'Find → Ctrl + F / Alt + X - f', command = lambda: state.active.f())
state.em.add_command(label = 'Find & Replace → Ctrl + Shift + F / Alt + X - fr', command = lambda: state.active.fr())
state.emailwordlist = []
try:
	for dictionary in state.dicts:
		if dictionary:
			state.emailwordlist.extend(open(dictionary, 'r', encoding = 'utf-8').read().split('\n'))
except Exception as error:
	error = str(error)
	state.root.error('Error', error)
state.om.add_command(label = 'Terminal → Alt + X - t', command = term)
state.om.add_separator()
state.om.add_command(label = 'Speak Text → Alt + X - sp', command = lambda: state.active.spk())
state.root.protocol('WM_DELETE_WINDOW', ext)
state.mg.add_command(label = 'Start', command = mathgod)
state.mg.add_separator()
state.mg.add_command(label = 'Help', command = helpmathgod)
state.wholenewwords = []
for command in state.plgnpccmds:
	pycodetopythoncommands[command] = state.plgnpccmds[command][1]
state.pycode_keybindings_cdt = ''
state._open_terminal_closers = []
state.all_buffers = []
state.buffindex = -1
state.vertical = easytk.ttk.Panedwindow(state.root, orient = 'vertical')
state.vertical.pack(side = 'bottom', fill = 'both', expand = True)
state.horizontal = easytk.ttk.Panedwindow(state.vertical, orient = 'horizontal')
state.vertical.add(state.horizontal)
state.sashconfig = lambda: [state.root.style().configure('Sash', sashthickness = 15, relief = 'raised')]
state.active = None
state.sashconfig()
state.root.bind('<<ThemeChanged>>', lambda event: state.sashconfig())
state._resize_after_id = None
state._last_root_size = (state.root.winfo_width(), state.root.winfo_height())
bindrecur(state.root, '<Alt-x>', lambda event: cmd())
bindrecur(state.root, '<Control-N>', lambda event: neweditor())
bindrecur(state.root, '<Control-O>', lambda event: neweditor(True))
bindrecur(state.root, '<Control-q>', lambda event: ext())
state.root.bind('<Configure>', _on_root_resize)
neweditor()
if state.defs[3] in state.root.themes():
	state.root.style(state.defs[3])
else:
	state.root.style('bootstrap-light')
vars(state).update(globals())
if not options['no-load-pycode']:
	try:
		pycodestartupcdt = pcread(open(f'{homedir}/.pynotes', 'r', encoding = 'utf-8').read())
	except Exception:
		pass
	else:
		for line in pycodestartupcdt.split('\n'):
			try:
				exec(line, vars(state))
			except Exception as error:
				error = str(error)
				state.root.error('Error', f'Error in PyCode: {error}')
if options['pycode-exec']:
	givenpcstartuplines = pcread(options['pycode-exec']).split('\n')
	for line in givenpcstartuplines:
		try:
			exec(line, vars(state))
		except Exception as error:
			error = str(error)
			state.root.error('Error', f'Error in PyCode: {error}')
if options['command-exec']:
	cmdrun(options['command-exec'])
for code in last_plugin:
	try:
		exec(code[1], vars(state))
	except Exception as error:
		error = str(error)
		state.root.error('Error!', f'There was an error in the last part of the plugin "{os.path.basename(os.path.normpath(code[0]))}":\n{error}')
if files_to_open:
	state.all_buffers[0].ld(files_to_open.pop(0))
for file in files_to_open:
	neweditor(file)
if new:
	prf()
state.root.show()
