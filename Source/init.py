import os
import sys
import platform
import getpass
import subprocess
import state
from tkinter import messagebox as mb
exit = sys.exit
v = '2.1'
if platform.system() == 'Linux':
	rootdir = '/usr/share/PyNotes'
	homedir = f'/home/{getpass.getuser()}'
	monospace = 'monospace'
else:
	rootdir = 'C:/Program Files/PyNotes'
	homedir = f'C:/Users/{getpass.getuser()}'
	monospace = 'Courier'
def info(title, inf):
	import easytk
	infowin = easytk.win()
	infowin.title(title)
	infowin.text(text = inf).pack(side = 'top', anchor = 'n', padx = 10, pady = 10)
	infowin.button(text = 'Close', command = infowin.destroy).pack(side = 'right', anchor = 'se', padx = 10, pady = 10)
	infowin.show()
def ask(title, askinput):
	import easytk
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
def ensure_dependencies():
	import dialogs
	try:
		import tika
		from tika import parser
	except Exception:
		ans = ask('Error!', 'The module \'tika\' is not installed. Should PyNotes install it locally?')
		if not ans:
			exit()
		else:
			dialogs.faketerm('pip3 install tika')
	try:
		import pdfplumber
	except Exception:
		ans = ask('Error!', 'The module \'pdfplumber\' is not installed. Should PyNotes install it locally?')
		if not ans:
			exit()
		else:
			dialogs.faketerm('pip3 install pdfplumber')
	try:
		import pyttsx3 as stt
	except Exception:
		ans = ask('Error!', 'The module \'pyttsx3\' is not installed. Should PyNotes install it locally?')
		if not ans:
			exit()
		else:
			dialogs.faketerm('pip3 install pyttsx3')
	try:
		import matplotlib.pyplot as plt
	except Exception:
		ans = ask('Error!', 'The module \'matplotlib\' is not installed. Should PyNotes install it locally?')
		if not ans:
			exit()
		else:
			dialogs.faketerm('pip3 install matplotlib')
	try:
		import sympy
	except Exception:
		ans = ask('Error!', 'The module \'sympy\' is not installed. Should PyNotes install it locally?')
		if not ans:
			exit()
		else:
			dialogs.faketerm('pip3 install sympy')
	try:
		import sounddevice as sd
	except Exception:
		ans = ask('Error!', 'The module \'sounddevice\' is not installed. Should PyNotes install it locally?')
		if not ans:
			exit()
		else:
			dialogs.faketerm('pip3 install sounddevice')
	try:
		import speech_recognition as sr
	except Exception:
		ans = ask('Error!', 'The module \'speech_recognition\' is not installed. Should PyNotes install it locally?')
		if not ans:
			exit()
		else:
			dialogs.faketerm('pip3 install SpeechRecognition')
	try:
		import numpy as np
	except Exception:
		ans = ask('Error!', 'The module \'numpy\' is not installed. Should PyNotes install it locally?')
		if not ans:
			exit()
		else:
			dialogs.faketerm('pip3 install numpy')
	try:
		from tklinenums import TkLineNumbers
	except Exception:
		ans = ask('Error!', 'The module \'tklinenums\' is not installed. Should PyNotes install it locally?')
		if not ans:
			exit()
		else:
			dialogs.faketerm('pip3 install tklinenums')
	try:
		import ziamath
	except Exception:
		ans = ask('Error!', 'The module \'ziamath\' is not installed. Should PyNotes install it locally?')
		if not ans:
			exit()
		else:
			dialogs.faketerm('pip3 install ziamath')
	try:
		import cairosvg
	except Exception:
		ans = ask('Error!', 'The module \'cairosvg\' is not installed. Should PyNotes install it locally?')
		if not ans:
			exit()
		else:
			dialogs.faketerm('pip3 install cairosvg')
	try:
		from PIL import Image
	except Exception:
		ans = ask('Error!', 'The module \'Pillow\' is not installed. Should PyNotes install it locally?')
		if not ans:
			exit()
		else:
			dialogs.faketerm('pip3 install Pillow')
	try:
		from watchdog.observers import Observer
		from watchdog.events import FileSystemEventHandler
	except Exception:
		ans = ask('Error!', 'The module \'watchdog\' is not installed. Should PyNotes install it locally?')
		if not ans:
			exit()
		else:
			dialogs.faketerm('pip3 install watchdog')
	if platform.system() != 'Linux':
		try:
			from winpty import PtyProcess
		except Exception:
			ans = ask('Error!', 'The module \'pywinpty\' is not installed. Should PyNotes install it locally?')
			if not ans:
				exit()
			else:
				dialogs.faketerm('pip3 install pywinpty')
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
def load_or_create_defs():
	defaultpythonexec = '/usr/bin/python3' if platform.system() == 'Linux' else 'python'
	defaultdefs = f"{v}\nFalse\n{monospace}\nbootstrap-light\n{rootdir}/english.txt\nFalse\nFalse\nFalse\n{defaultpythonexec}\n'pynotes:found': \"foreground = '#FFFFFF', background = '#16A34A'\", 'pynotes:foundhighlight': \"foreground = '#FFFFFF', background = '#1F2937'\", 'pynotes:marked': \"background = 'yellow'\", 'python:keywords': \"foreground = '#7C3AED', font = (type_.cget('font')[:-3].strip('{{}}'), 12, 'bold')\", 'python:inbuilt': \"foreground = '#D97706'\", 'python:comments': \"foreground = '#6B7280', font = (type_.cget('font')[:-3].strip('{{}}'), 12, 'italic')\", 'python:strings': \"foreground = '#15803D'\", 'python:variable_names': \"foreground = '#DC2626'\", 'python:function_names': \"foreground = '#2563EB'\", 'python:class_names': \"foreground = '#0891B2'\", 'python:class_instances': \"foreground = '#155E75'\", 'python:function_arguments': \"foreground = '#0F766E'\", 'python:operators': \"foreground = 'white', background = 'light grey'\", 'python:module_names': \"foreground = '#0369A1'\", 'latex:inlinemath': \"foreground = '#15803D'\", 'latex:environment': \"background = '#DCFCE7'\", 'latex:comments': \"foreground = '#6B7280', font = (type_.cget('font')[:-3].strip('{{}}'), 12, 'italic')\", 'latex:commands': \"foreground = '#C026D3'\", 'latex:arguments': \"foreground = '#2563EB'\", 'latex:operators': \"foreground = 'white', background = 'light grey'\", 'latex:square_brackets': \"foreground = '#92400E'\", 'html:attributes': \"foreground = '#DC2626'\", 'html:tags': \"foreground = '#047857'\", 'html:comments': \"foreground = '#6B7280', font = (type_.cget('font')[:-3].strip('{{}}'), 12, 'italic')\", 'html:quotes': \"foreground = '#2563EB'\", 'markdown:headers1': \"foreground = '#111827', font = (type_.cget('font')[:-3].strip('{{}}'), 29, 'bold')\", 'markdown:headers2': \"foreground = '#1F2937', font = (type_.cget('font')[:-3].strip('{{}}'), 26, 'bold')\", 'markdown:headers3': \"foreground = '#374151', font = (type_.cget('font')[:-3].strip('{{}}'), 23, 'bold')\", 'markdown:headers4': \"foreground = '#4B5563', font = (type_.cget('font')[:-3].strip('{{}}'), 20, 'bold')\", 'markdown:headers5': \"foreground = '#6B7280', font = (type_.cget('font')[:-3].strip('{{}}'), 17, 'bold')\", 'markdown:headers6': \"foreground = '#9CA3AF', font = (type_.cget('font')[:-3].strip('{{}}'), 14, 'bold')\", 'markdown:bold': \"font = (type_.cget('font')[:-3].strip('{{}}'), 12, 'bold')\", 'markdown:italic': \"font = (type_.cget('font')[:-3].strip('{{}}'), 12, 'italic')\", 'markdown:bold_italic': \"font = (type_.cget('font')[:-3].strip('{{}}'), 12, 'bold italic')\", 'markdown:strike': 'overstrike = True', 'markdown:inlinecode': \"foreground = '#BE123C', background = '#F3F4F6'\", 'markdown:links': \"foreground = '#2563EB', underline = True, underlinefg = '#2563EB'\", 'markdown:blockquotes': \"foreground = '#374151', background = '#F3F4F6'\", 'markdown:codeblocks': \"background = '#F3F4F6'\""
	new = False
	try:
		file = open(f'{homedir}/.local/share/PyNotes/defs', 'r', encoding = 'utf-8')
	except Exception:
		file = open(f'{homedir}/.local/share/PyNotes/defs', 'w+', encoding = 'utf-8')
		file.write(defaultdefs)
		file.close()
		file = open(f'{homedir}/.local/share/PyNotes/defs', 'r', encoding = 'utf-8')
		info('', 'Welcome to PyNotes!')
		new = True
	return file, new, defaultdefs
def load_plugins(no_load_plugins):
	init = []
	first = []
	last = []
	if not no_load_plugins:
		plgns = os.listdir(f'{homedir}/.local/share/PyNotes/add-ons')
	else:
		plgns = []
	state.buffer_init_code = []
	state.buffer_init_functions = []
	state.editor_init_code = []
	state.editor_init_functions = []
	plgns = [os.path.join(f'{homedir}/.local/share/PyNotes/add-ons', plgn) for plgn in plgns if os.path.isdir(os.path.join(f'{homedir}/.local/share/PyNotes/add-ons', plgn))]
	state.plgncmds = dict()
	init = []
	first = []
	last = []
	state.plgnsprf = []
	state.plgnhmodes = dict()
	state.plgnpccmds = dict()
	state.plgnscmdhelp = ''
	state.plgnspccmdhelp = ''
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
			state.plgnsprf.append((plgn, open(plgnprff, 'r', encoding = 'utf-8').read()))
		except Exception:
			pass
		try:
			pchfr = open(pchf, 'r', encoding = 'utf-8').read()
		except Exception:
			pass
		else:
			if pchfr.strip():
				state.plgnscmdhelp += '\n\n' + pchfr.strip()
		try:
			plgnhmoder = open(plgnhmodesf, 'r', encoding = 'utf-8').read().split('\n')
		except Exception:
			pass
		else:
			try:
				for p in plgnhmoder:
					ps = p[1:].split('"', 1)
					state.plgnhmodes[ps[0]] = (plgn, ps[1].replace('\\n', '\n'))
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
					state.plgnpccmds[ps[0]] = (plgn, ps[1])
			except Exception as error:
				error = str(error)
				info('Error!', f'There was an error in loading the PyCode commands of the plugin "{os.path.basename(os.path.normpath(plgn))}":\n{error}')
				exit()
		try:
			plgnpchr = open(plgnpccmdhf, 'r', encoding = 'utf-8').read()
		except Exception:
			pass
		else:
			state.plgnspccmdhelp += '\n\n' + plgnpchr.strip()
		try:
			plgncmdfr = open(plgncmdf, 'r', encoding = 'utf-8').read().split('\n')
		except Exception:
			pass
		else:
			try:
				for p in plgncmdfr:
					ps = p[1:].split('"', 1)
					state.plgncmds[ps[0]] = (plgn, ps[1].replace('\\n', '\n'))
			except Exception as error:
				error = str(error)
				info('Error!', f'There was an error in loading the Alt-X commands of the plugin "{os.path.basename(os.path.normpath(plgn))}":\n{error}')
				exit()
	return init, first, last
def _report_callback_exception(*args, **kwargs):
	import utils
	return utils._report_callback_exception(*args, **kwargs)
def create_root_and_menus():
	import easytk
	import utils
	state.root = easytk.win()
	state.root.report_callback_exception = _report_callback_exception
	utils.load_themes()
	state.fm = state.root.menu()
	state.em = state.root.menu()
	state.tem = state.root.menu()
	state.om = state.root.menu()
	state.pm = state.root.menu()
	state.lm = state.root.menu()
	state.pcm = state.root.menu()
	state.hm = state.root.menu()
	state.mg = state.root.menu()
	state.plgnm = state.root.menu()
	state.mainmenu = state.root.menu()
	state.root.config(menu = state.mainmenu)
	state.all_buffer_menus = {'File': state.fm, 'Options': state.om, 'PyCode': state.pcm, 'MathGod': state.mg, 'Plugins': state.plgnm, 'Help': state.hm}
	state.all_editor_menus = {'File': state.fm, 'Edit': state.em, **state.all_buffer_menus}
	state.all_terminal_menus = {'File': state.fm, 'Edit': state.tem, **state.all_buffer_menus}
	os.makedirs(f'{homedir}/.local/share/PyNotes/tempfiles', exist_ok = True)
	sys.stderr = utils.ErrorHandler()
	state.pcsettitle = False
def load_config(file, defaultdefs):
	import math as mathmod
	try:
		state.defs = file.read().split('\n')
		file.close()
		state.dicts = state.defs[4].split(',')
		if state.defs[1] == 'False':
			state.bfr = False
		elif state.defs[1] == 'True':
			state.bfr = True
		else:
			raise Exception
		if state.defs[5] == 'True':
			state.emacskeysforsearch = True
		elif state.defs[5] == 'False':
			state.emacskeysforsearch = False
		else:
			raise Exception
		if state.defs[6] == 'True':
			state.taborspace = True
		elif state.defs[6] == 'False':
			state.taborspace = False
		else:
			raise Exception
		if state.defs[7] == 'True':
			state.nographicalfiledialogs = True
		elif state.defs[7] == 'False':
			state.nographicalfiledialogs = False
		state.pythonexecutable = state.defs[8]
		exec('theme = ' + '{' + state.defs[9] + '}', vars(state))
		state.theme['python:variable_names']
		state.theme['python:function_names']
		state.theme['python:class_names']
		state.theme['python:class_instances']
		state.theme['python:function_arguments']
		state.theme['python:operators']
		state.theme['python:module_names']
		state.theme['pynotes:found']
		state.theme['pynotes:foundhighlight']
		state.theme['pynotes:marked']
		state.theme['latex:commands']
		state.theme['latex:arguments']
		state.theme['latex:operators']
		state.theme['latex:square_brackets']
		state.theme['python:strings']
		state.theme['python:keywords']
		state.theme['python:inbuilt']
		state.theme['python:comments']
		state.theme['latex:inlinemath']
		state.theme['latex:environment']
		state.theme['latex:comments']
		state.theme['html:attributes']
		state.theme['html:tags']
		state.theme['html:comments']
		state.theme['html:quotes']
		state.theme['markdown:headers1']
		state.theme['markdown:headers2']
		state.theme['markdown:headers3']
		state.theme['markdown:headers4']
		state.theme['markdown:headers5']
		state.theme['markdown:headers6']
		state.theme['markdown:bold']
		state.theme['markdown:italic']
		state.theme['markdown:bold_italic']
		state.theme['markdown:strike']
		state.theme['markdown:inlinecode']
		state.theme['markdown:links']
		state.theme['markdown:blockquotes']
		state.theme['markdown:codeblocks']
	except Exception:
		truncate = state.root.ask('Warning', f'You are using preferences from an older version of PyNotes which do not have all the settings of this one.\nDo you want to reset the preferences and continue?\n(File: {homedir}/.local/share/PyNotes/defs)', ('yes', 'no'))
		if not truncate:
			state.root.info('Info', 'Quitting PyNotes')
			state.root.destroy()
			exit()
		os.remove(f'{homedir}/.local/share/PyNotes/defs')
		file = open(f'{homedir}/.local/share/PyNotes/defs', 'w+', encoding = 'utf-8')
		file.write(defaultdefs)
		file.close()
		file = open(f'{homedir}/.local/share/PyNotes/defs', 'r', encoding = 'utf-8')
		state.defs = file.read().split('\n')
		file.close()
		state.dicts = state.defs[4].split(',')
		if state.defs[1] == 'False':
			state.bfr = False
		elif state.defs[1] == 'True':
			state.bfr = True
		if state.defs[5] == 'True':
			state.emacskeysforsearch = True
		elif state.defs[5] == 'False':
			state.emacskeysforsearch = False
		if state.defs[6] == 'True':
			state.taborspace = True
		elif state.defs[6] == 'False':
			state.taborspace = False
		if state.defs[7] == 'True':
			state.nographicalfiledialogs = True
		elif state.defs[7] == 'False':
			state.nographicalfiledialogs = False
		state.pythonexecutable = state.defs[8]
		exec('theme = ' + '{' + state.defs[9] + '}', vars(state))
	if not v == state.defs[0]:
		state.root.info('Info', 'PyNotes has been updated!')
		state.defs[0] = v
		file = open(f'{homedir}/.local/share/PyNotes/defs', 'w+', encoding = 'utf-8')
		for d in state.defs:
			file.write(d + '\n')
		file.close()
	try:
		icon = f'{rootdir}/Icon.png'
		state.root.seticon(icon)
	except Exception:
		state.root.error('Error', f'Could not find the icon at {rootdir}/Icon.png.\nQuitting PyNotes.')
		state.root.destroy()
		exit()
	state.root.geometry('820x800')
