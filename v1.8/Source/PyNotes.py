import sys
v = '1.8'
if len(sys.argv) > 1:
	if sys.argv[1] == '--version':
		print(v)
		exit()
import os
import subprocess
import getpass
import platform
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
import easytk
if platform.system() != 'Linux':
	fd = easytk.fd
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
		info('Making Python virtual environment', 'Making the Python virtual environment for PyNotes. This only happens on the first startup of a new\ninstallation of PyNotes.')
		subprocess.run([sys.executable, '-m', 'venv', venvdir], check = True)
	if sys.prefix != venvdir:
		os.execv(f'{venvdir}/bin/python', [f'{venvdir}/bin/python'] + sys.argv)
if platform.system() == 'Linux':
	os.environ['PATH'] = f'{homedir}/.local/share/PyNotes/venv/bin:' + os.environ['PATH']
switchvenv()
from encrypter import encryptdecrypt
import io
import time
import shutil
import copy
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
		command = 'pip install ttkthemes'
	elif number == 6:
		command = 'pip install sounddevice'
	elif number == 7:
		command = 'pip install SpeechRecognition'
	elif number == 8:
		command = 'pip install numpy'
	elif number == 9:
		command = 'pip install tklinenums'
	elif number == 10:
		command = 'pip install ttkwidgets'
	elif number == 11:
		command = 'pip install pywinpty'
	elif number == 12:
		command = 'pip install ziamath'
	elif number == 13:
		command = 'pip install cairosvg'
	elif number == 14:
		command = 'pip install Pillow'
	term.insert('end', f'{getpass.getuser()}@PyNotes:~$ {command}\n')
	term.pack(fill = 'both')
	termwin.update()
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
	import ttkthemes
except Exception:
	ans = ask('Error!', 'The module \'ttkthemes\' is not installed. Should PyNotes install it locally?')
	if not ans:
		exit()
	else:
		faketerm(5)
try:
	import sounddevice as sd
except Exception:
	ans = ask('Error!', 'The module \'sounddevice\' is not installed. Should PyNotes install it locally?')
	if not ans:
		exit()
	else:
		faketerm(6)
try:
	import speech_recognition as sr
except Exception:
	ans = ask('Error!', 'The module \'speech_recognition\' is not installed. Should PyNotes install it locally?')
	if not ans:
		exit()
	else:
		faketerm(7)
try:
	import numpy as np
except Exception:
	ans = ask('Error!', 'The module \'numpy\' is not installed. Should PyNotes install it locally?')
	if not ans:
		exit()
	else:
		faketerm(8)
try:
	from tklinenums import TkLineNumbers
except Exception:
	ans = ask('Error!', 'The module \'tklinenums\' is not installed. Should PyNotes install it locally?')
	if not ans:
		exit()
	else:
		faketerm(9)
try:
	import ttkwidgets.frames
except Exception:
	ans = ask('Error!', 'The module \'ttkwidgets\' is not installed. Should PyNotes install it locally?')
	if not ans:
		exit()
	else:
		faketerm(10)
if platform.system() != 'Linux':
	try:
		from winpty import PtyProcess
	except Exception:
		ans = ask('Error!', 'The module \'pywinpty\' is not installed. Should PyNotes install it locally?')
		if not ans:
			exit()
		else:
			faketerm(11)
try:
	import ziamath
except Exception:
	ans = ask('Error!', 'The module \'ziamath\' is not installed. Should PyNotes install it locally?')
	if not ans:
		exit()
	else:
		faketerm(12)
try:
	import cairosvg
except Exception:
	ans = ask('Error!', 'The module \'cairosvg\' is not installed. Should PyNotes install it locally?')
	if not ans:
		exit()
	else:
		faketerm(13)
try:
	from PIL import Image
except Exception:
	ans = ask('Error!', 'The module \'Pillow\' is not installed. Should PyNotes install it locally?')
	if not ans:
		exit()
	else:
		faketerm(14)
new = False
try:
	import tika
	from tika import parser
	import pdfplumber
	import pyttsx3 as stt
	import matplotlib.pyplot as plt
	import sympy
	import ttkthemes
	import sounddevice as sd
	import speech_recognition as sr
	import numpy as np
	from tklinenums import TkLineNumbers
	import ttkwidgets.frames
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
try:
	file = open(f'{homedir}/.local/share/PyNotes/defs', 'r', encoding = 'utf-8')
except Exception:
	file = open(f'{homedir}/.local/share/PyNotes/defs', 'w+', encoding = 'utf-8')
	defaultpythonexec = '/usr/bin/python3' if platform.system() == 'Linux' else 'python'
	file.write(f"{v}\nFalse\n{monospace}\nbreeze\n{rootdir}/english.txt\nFalse\nFalse\n{defaultpythonexec}\n'pynotes:found': \"foreground = 'white', background = 'green'\", 'pynotes:foundhighlight': \"foreground = 'white', background = 'black'\", 'python:keywords': \"foreground = 'purple', font = (type_.cget('font')[:-3].strip('{{}}'), 12, 'bold')\", 'python:inbuilt': \"foreground = 'red'\", 'python:comments': \"foreground = 'gray'\", 'python:strings': \"foreground = 'green'\", 'python:variable_names': \"foreground = 'brown'\", 'python:function_names': \"foreground = 'brown'\", 'python:operators': \"background = 'gray'\", 'latex:inlinemath': \"foreground = 'green'\", 'latex:environment': \"background = 'light green'\", 'latex:comments': \"foreground = 'gray'\", 'latex:commands': \"foreground = 'magenta'\", 'latex:arguments': \"foreground = 'blue'\", 'latex:operators': \"foreground = 'white', background = 'grey'\", 'latex:square_brackets': \"foreground = 'brown'\", 'html:attributes': \"foreground = 'red'\", 'html:tags': \"foreground = 'dark green'\", 'html:comments': \"foreground = 'gray'\", 'html:quotes': \"foreground = 'blue'\", 'pynotes:marked': \"background = 'light grey'\"")
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
plgnscmdhelp = ''
for plgn in plgns:
	inf = os.path.join(plgn, 'init')
	ff = os.path.join(plgn, 'first')
	lf = os.path.join(plgn, 'last')
	pchf = os.path.join(plgn, 'helpcommands')
	plgncmdf = os.path.join(plgn, 'commands')
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
		pchfr = open(pchf, 'r', encoding = 'utf-8').read()
	except Exception:
		pass
	else:
		if pchfr.strip():
			plgnscmdhelp += '\n\n' + pchfr.strip().replace('\n\n', '\n')
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
			info('Error!', f'There was an error in loading the commands of the plugin "{os.path.basename(os.path.normpath(plgn))}":\n{error}')
			exit()
for code in init:
	try:
		exec(code[1])
	except Exception as error:
		info('Error!', f'There was an error in initializing the plugin "{os.path.basename(os.path.normpath(code[0]))}":\n{error}')
def error_handler(error):
	root.error('Error', f'An error occured:\n{error}')
class ErrorHandler:
	def __init__(self, function):
		self.function = function
	def write(self, error):
		if error.strip():
			self.function(error)
	def flush(self):
		pass
root = easytk.win()
unsaved = False
unsavedtext = ''
hmode = 'norm'
os.makedirs(f'{homedir}/.local/share/PyNotes/tempfiles', exist_ok = True)
sys.stderr = ErrorHandler(error_handler)
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
	theme['python:operators']
	theme['python:function_names']
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
except Exception:
	truncate = root.ask('Warning', f'You are using preferences from an older version of PyNotes which are not compatible with this one, or the preferences are corrupted.\nDo you want to reset the preferences and continue?\n(File: {homedir}/.local/share/PyNotes/defs)', ('yes', 'no'))
	if not truncate:
		root.error('Error!', 'Quitting PyNotes')
		root.destroy()
		exit()
	os.remove(f'{homedir}/.local/share/PyNotes/defs')
	file = open(f'{homedir}/.local/share/PyNotes/defs', 'w+', encoding = 'utf-8')
	defaultpythonexec = '/usr/bin/python3' if platform.system() == 'Linux' else 'python'
	file.write(f"{v}\nFalse\n{monospace}\nbreeze\n{rootdir}/english.txt\nFalse\nFalse\n{defaultpythonexec}\n'pynotes:found': \"foreground = 'white', background = 'green'\", 'pynotes:foundhighlight': \"foreground = 'white', background = 'black'\", 'python:keywords': \"foreground = 'purple', font = (type_.cget('font')[:-3].strip('{{}}'), 12, 'bold')\", 'python:inbuilt': \"foreground = 'red'\", 'python:comments': \"foreground = 'gray'\", 'python:strings': \"foreground = 'green'\", 'python:variable_names': \"foreground = 'brown'\", 'python:function_names': \"foreground = 'brown'\", 'python:operators': \"background = 'gray'\", 'latex:inlinemath': \"foreground = 'green'\", 'latex:environment': \"background = 'light green'\", 'latex:comments': \"foreground = 'gray'\", 'latex:commands': \"foreground = 'magenta'\", 'latex:arguments': \"foreground = 'blue'\", 'latex:operators': \"foreground = 'white', background = 'grey'\", 'latex:square_brackets': \"foreground = 'brown'\", 'html:attributes': \"foreground = 'red'\", 'html:tags': \"foreground = 'dark green'\", 'html:comments': \"foreground = 'gray'\", 'html:quotes': \"foreground = 'blue'\", 'pynotes:marked': \"background = 'light grey'\"")
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
title = ''
type_top = '1.0'
type_bottom = 'end'
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
		ld(f'{rootdir}/PyNotes.py')
def abt(event = None):
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
def changes(event = None):
	cw = root.subwin()
	cw.title(f'Changes in v{v}')
	changelist = ['You can now bind chord keyboard shortcuts in PyCode!', 'Made the running of Python code much better!\n(Also change Python interpreter in Preferences)', 'Changed and improved the file picker.', 'Improved the LaTeX syntax highlighting.', 'Improved the PyCode graphical programming UI.', 'Made the MathGod math rendering much better using LaTeX.', 'Made the Alt-X and PyCode unindent command.' ,'Added some PyCode commands.', 'Added some Alt-X commands.', 'Fixed some syntax highlighting bugs.', 'Made the Find and Find & Replace much faster and stopped it lagging the entire editor.', 'Made the syntax highlighting much more efficient.', 'Made the editor more efficient in each keypress.', 'Made the undo better.', 'Fixed bug in opening multiple files through the terminal / command line.', 'Made PyNotes make files that do not exist.','Fixed some minor bugs.']
	for i in range(len(changelist)):
		cw.text(text = f'{i + 1}. {changelist[i]}').grid(column = 0, row = i, padx = 10, pady = 10, sticky = 'w')
	cw.bind('<Escape>', lambda event: cw.destroy())
	cw.bind('<Return>', lambda event: cw.destroy())
	cw.sizablefalse()
	cw.style(root.gettheme())
	cw.focus()
def hemail(event = None):
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
		fn = subprocess.run(['zenity', '--file-selection', '--filename=./', '--title=Open File', '--file-filter=All Files | *.*', '--file-filter=Python Files | *.py', '--file-filter=Text Files | *.txt', '--file-filter=LaTeX Files | *.tex', '--file-filter=PNG Images | *.png', '--file-filter=PDF Files | *.pdf', '--file-filter=ePub Files | *.epub'], capture_output = True, text = True).stdout.strip()
	else:
		fd.askopenfilename(title = 'Open File', filetypes = (('All Files', '*.*'), ('Python Files', '*.py'), ('Text Files', '*.txt'), ('LaTeX Files', '*.tex'), ('PNG Images', '*.png'), ('PDF Files', '*.pdf'), ('ePub Files', '*.epub')))
	if fn:
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
		else:
			root.title('PyNotes - Untitled')
			filename.config(text = 'Untitled')
		title = nt
		unsaved = False
	except Exception:
		pass
def sssv(event = None):
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
def ext(event = None):
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
	global type_
	global root
	global m
	global imageload
	global hmode
	global unsavedtext
	if not nm == '':
		type_.delete('1.0', 'end')
		if os.path.dirname(nm):
			try:
				os.chdir(os.path.dirname(nm))
			except:
				root.error('Error', f'The directory \'{os.path.dirname(nm)}\' does not exist.')
				type_.edit_reset()
				return
		if not os.path.exists(nm):
			open(nm, 'w', encoding = 'utf-8')
		try:
			file = open(nm, 'r', encoding = 'utf-8')
			lines = file.readlines()
			type_.delete('1.0', 'end')
			for i in range(len(lines)):
				type_.insert('end', lines[i])
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
						m.entryconfig(4, state = 'disabled')
						m.entryconfig(5, state = 'disabled')
						tabs.tab(2, state = 'hidden')
						for widget in lf.winfo_children()[1:]:
							widget.config(state = 'disabled')
						hmode = 'epub'
						filetype.config(text = 'EPUB File (*.epub)')
						keypress()
				else:
					clt(nm)
					filesize.config(text = str(os.path.getsize(nm)) + 'bytes')
					m.entryconfig(4, state = 'disabled')
					m.entryconfig(5, state = 'disabled')
					tabs.tab(2, state = 'hidden')
					for widget in lf.winfo_children()[1:]:
						widget.config(state = 'disabled')
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
				m.entryconfig(4, state = 'disabled')
				m.entryconfig(5, state = 'disabled')
				tabs.tab(2, state = 'hidden')
				for widget in lf.winfo_children()[1:]:
					widget.config(state = 'disabled')
		else:
			unsavedtext = type_.get('1.0', 'end-1c')
			clt(nm)
			filesize.config(text = str(os.path.getsize(nm)) + ' bytes')
			if os.path.splitext(nm)[1] == '.py':
				m.entryconfig(4, state = 'normal')
				m.entryconfig(5, state = 'disabled')
				tabs.tab(2, state = 'hidden')
				for widget in lf.winfo_children()[1:]:
					widget.config(state = 'disabled')
				hmode = 'py'
				filetype.config(text = 'Python File (*.py)')
			elif os.path.splitext(nm)[1] == '.tex':
				m.entryconfig(4, state = 'disabled')
				m.entryconfig(5, state = 'normal')
				tabs.tab(2, state = 'hidden')
				for widget in lf.winfo_children()[1:]:
					widget.config(state = 'normal')
				hmode = 'la'
				filetype.config(text = 'LaTeX / TeX File (*.tex)')
			elif os.path.splitext(nm)[1] == '.html':
				m.entryconfig(4, state = 'disabled')
				m.entryconfig(5, state = 'disabled')
				for widget in lf.winfo_children()[1:]:
					widget.config(state = 'normal')
				hmode = 'html'
				filetype.config(text = 'HTML File (*.html)')
			else:
				hmode = 'norm'
				filetype.config(text = 'Plain Text (*.*)')
				m.entryconfig(4, state = 'disabled')
				m.entryconfig(5, state = 'disabled')
				tabs.tab(2, state = 'hidden')
				for widget in lf.winfo_children()[1:]:
					widget.config(state = 'disabled')
			keypress()
		type_.edit_reset()
def llld(event = None):
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
				file = open(nm, 'w', encoding = 'utf-8')
				file.writelines(content)
				file.close()
				unsavedtext = content
				clt(nm)
			except Exception:
				pass
		else:
			root.error('Error!', 'Cannot save files of this type')
def ssv(event = None):
	if platform.system() == 'Linux':
		fn = subprocess.run(['zenity', '--file-selection', '--filename=./', '--save', '--confirm-overwrite', '--title=Save As', '--file-filter=All Files | *.*'], capture_output = True, text = True).stdout.strip()
	else:
		fn = fd.asksaveasfilename()
	if fn:
		sv(fn)
		clt(fn)
	else:
		return False
def nw(event = None):
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
		pchmode('norm')
		filename.config(text = 'Untitled')
		filesize.config(text = '0 bytes')
		type_.edit_reset()
def fr(event = None):
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
				flags = re.IGNORECASE if case else 0
				compiled = re.compile(pat, flags)
			except re.error:
				type_.after(0, lambda: _start_apply([]))
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
				type_.after(0, lambda: _start_apply(tk_results))
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
def f(event = None):
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
				type_.after(0, lambda: _start_apply([]))
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
				type_.after(0, lambda: _start_apply(tk_results))
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
	keypress()
def prf(event = None):
	global bfr
	global colours
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
			fn = subprocess.run(['zenity', '--file-selection', '--filename=./', '--title=Open File', '--file-filter=All Files | *.*'], capture_output = True, text = True).stdout.strip()
		else:
			fn = fd.askopenfilename(title = 'Open File', filetypes = (('All Files', '*.*')))
		if fn:
			pythonexecutable = fn
			pyexecshowtext.config(text = f'Python interpreter: \'{pythonexecutable}\'')
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
	mf = root.frame(master = tft)
	mf.grid(column = 0, row = 0)
	pr.text(text = 'UI Theme', master = mf).grid(column = 0, row = 0, padx = 10, pady = 10)
	stsvar = pr.stringvar()
	sts = pr.dropdown(stringvar = stsvar, showdefault = root.style().current_theme, options = tuple(sorted(pr.style().get_themes())), command = lambda nt: [pr.sizabletrue(), pr.style(nt), root.style(nt), pr.sizablefalse()], master = mf)
	sts.grid(column = 1, row = 0, padx = 10, pady = 10, sticky = 'w')
	pr.text(text = 'Editor Font', master = mf).grid(column = 0, row = 1, padx = 10, pady = 10)
	showfont = pr.textbox(master = tft, font = (type_.cget('font')[:-3].strip('{}'), 12), wrap = 'word', height = 5)
	showfont.insert('end', 'The quick brown fox jumped over the lazy dogs\nAaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz\n1234567890\n?.,<>;:\'"{}[]\\|\n!@#$%^&*()-_+=')
	showfont.grid(column = 0, row = 1)
	f = pr.droptype(options = [monospace] + sorted(pr.getfonts()), master = mf, command = lambda: [pr.sizabletrue(), type_.config(font = (f.get(), 12)), showfont.config(font = (f.get(), 12)), pr.sizablefalse()])
	f.grid(column = 1, row = 1, padx = 10, pady = 10)
	f.insert('end', type_.cget('font')[:-3].strip('{}'))
	root.text(master = tft, text = 'Colours:').grid(column = 0, row = 2, padx = 10, pady = 10)
	colours = root.textbox(master = tft, font = monospace, wrap = 'word', height = 5)
	colours.insert('end', str(theme)[:-1][1:].replace('type_.cget(\'font\')[:-3].strip(\'{}\')', 'orgfont'))
	colours.grid(column = 0, row = 3)
	pr.bind('<Escape>', lambda event: [svprf(), show('change / view preferences'), pr.destroy()])
	pr.bind('<Return>', lambda event: [svprf(), show('change / view preferences'), pr.destroy()])
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
_KW_PAT = re.compile(r'\b(?:' + '|'.join(re.escape(k) for k in keyword.kwlist if k not in ('True', 'False')) + r')\b')
_BI_PAT = re.compile(r'\b(?:' + '|'.join(re.escape(k) for k in ('file', 'open', 'map', 'int', 'str', 'print', 'range', 'set', 'input', 'list', 'len', 'self', 'type', 'exec', 'sum', 'iter', 'dir', 'compile', 'eval', 'format', 'locals', 'cls', 'exit', 'quit', 'dict', 'repr', 'hasattr', 'setattr', 'super', 'isinstance', 'object', 'tuple', 'float', 'True', 'False')) + r')\b')
_OP_PAT = re.compile(r'==|!=|<|>|<=|>=')
_LH_PAT = re.compile(r'(?<!\\)%[^\n]*(?:\n|$)')
_HS_PAT = re.compile(r'<[^\n>]*>')
_HC_PAT = re.compile(r'<!--.*?-->', re.DOTALL)
_HSTR_PAT = re.compile(r"'[^'\n]*'|\"[^\"\n]*\"")
_HATTR_PAT = re.compile(r'\b(?:class|id|href|src|alt|style|type|name|value)\b', re.IGNORECASE)
_ALL_HL_TAGS = ('hpa', 'hpb', 'hpv', 'hpf', 'hpo', 'hpd', 'hpc', 'hla', 'hlb', 'hld', 'hle', 'hlf', 'hlg', 'hlh', 'hattr', 'hstuff', 'hcmt', 'hstr')
_defined_vars = []
_defined_funcs = []
_names_scan_thread = None
_var_pat = re.compile(r'^\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*=', re.MULTILINE)
_func_pat = re.compile(r'^\s*def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', re.MULTILINE)
def _scan_names(text):
	global _defined_vars, _defined_funcs
	new_vars = list(dict.fromkeys(m.group(1) for m in _var_pat.finditer(text)))
	new_funcs = list(dict.fromkeys(m.group(1) for m in _func_pat.finditer(text)))
	_defined_vars = new_vars
	_defined_funcs = new_funcs
def trigger_name_scan():
	global _names_scan_thread
	if _names_scan_thread is not None and _names_scan_thread.is_alive():
		return
	text = type_.get('1.0', 'end')
	_names_scan_thread = threading.Thread(target = _scan_names, args = (text,), daemon = True)
	_names_scan_thread.start()
def ha(ft):
	if _ha_running[0]:
		_ha_pending[0] = ft
		return
	_ha_running[0] = True
	text = type_.get(type_top, type_bottom)
	top = type_top
	bottom = type_bottom
	pre_text = type_.get('1.0', type_top)
	full_text = type_.get('1.0', type_bottom) if ft == 'latex' else None
	dvars = list(_defined_vars)
	dfuncs = list(_defined_funcs)
	_SKIP = frozenset({'sel', 'marked', 'found', 'foundhighlight'})
	def do_hl():
		ops = []
		try:
			for tag in _ALL_HL_TAGS:
				ops.append(('remove', tag))
			if ft == 'py':
				for m in _KW_PAT.finditer(text):
					ops.append(('add', 'hpa', f'{top}+{m.start()}c', f'{top}+{m.end()}c'))
				ops.append(('config', 'hpa', theme['python:keywords']))
				for m in _BI_PAT.finditer(text):
					ops.append(('add', 'hpb', f'{top}+{m.start()}c', f'{top}+{m.end()}c'))
				ops.append(('config', 'hpb', theme['python:inbuilt']))
				if dvars:
					vpat = re.compile(r'\b(?:' + '|'.join(re.escape(v) for v in dvars) + r')\b')
					for m in vpat.finditer(text):
						ops.append(('add', 'hpv', f'{top}+{m.start()}c', f'{top}+{m.end()}c'))
				ops.append(('config', 'hpv', theme['python:variable_names']))
				if dfuncs:
					fpat = re.compile(r'\b(?:' + '|'.join(re.escape(v) for v in dfuncs) + r')\b')
					for m in fpat.finditer(text):
						ops.append(('add', 'hpf', f'{top}+{m.start()}c', f'{top}+{m.end()}c'))
				ops.append(('config', 'hpf', theme['python:function_names']))
				for m in _OP_PAT.finditer(text):
					s = f'{top}+{m.start()}c'
					e = f'{top}+{m.end()}c'
					ops.append(('clear_other', s, e))
					ops.append(('add', 'hpo', s, e))
				ops.append(('config', 'hpo', theme['python:operators']))
				pre_n = len(pre_text)
				pre_i = 0
				in_triple = False
				triple_ch = None
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
						while j < pre_n:
							if pre_text[j] == '\\':
								j += 2
								continue
							if pre_text[j] == pquote:
								j += 1
								break
							if pre_text[j] == '\n':
								break
							j += 1
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
				ops.append(('config', 'hpd', theme['python:strings']))
				ops.append(('config', 'hpc', theme['python:comments']))
			elif ft == 'latex':
				pre_n = len(pre_text)
				pre_i = 0
				in_lmath = False
				while pre_i < pre_n:
					pch = pre_text[pre_i]
					if pch == '\\':
						pre_i += 2
						continue
					if pch == '%':
						while pre_i < pre_n and pre_text[pre_i] != '\n':
							pre_i += 1
						continue
					if pch == '$':
						in_lmath = not in_lmath
					pre_i += 1
				if in_lmath:
					n_vis = len(text)
					j = 0
					found_close = False
					while j < n_vis:
						if text[j] == '\\':
							j += 2
							continue
						if text[j] == '$':
							j += 1
							found_close = True
							break
						j += 1
					if not found_close:
						j = n_vis
					ops.append(('add', 'hla', f'{top}+0c', f'{top}+{j}c'))
				for m in re.finditer(r'\$.+?\$', text, re.DOTALL):
					ops.append(('add', 'hla', f'{top}+{m.start()}c', f'{top}+{m.end()}c'))
				ops.append(('config', 'hla', theme['latex:inlinemath']))
				if full_text:
					for begin_m in re.finditer(r'\\begin\{\s*(\w+\*?)\s*\}', full_text):
						if begin_m.group(1) == 'document':
							continue
						env_name = re.escape(begin_m.group(1))
						search_from = begin_m.end()
						depth = 1
						env_pat = re.compile(r'\\(begin|end)\{\s*' + env_name + r'\s*\}')
						while depth > 0:
							em = env_pat.search(full_text, search_from)
							if not em:
								break
							if em.group(1) == 'begin':
								depth += 1
							else:
								depth -= 1
							search_from = em.end()
						if depth == 0:
							ops.append(('add', 'hlb', f'1.0+{begin_m.start()}c', f'1.0+{search_from}c'))
				ops.append(('config', 'hlb', theme['latex:environment']))
				for m in re.finditer(r'\\(\w+)', text):
					ops.append(('add', 'hld', f'{top}+{m.start()}c', f'{top}+{m.end()}c'))
				ops.append(('config', 'hld', theme['latex:commands']))
				for m in re.finditer(r'\{.+?\}', text, re.DOTALL):
					ops.append(('add', 'hle', f'{top}+{m.start()}c', f'{top}+{m.end()}c'))
				ops.append(('config', 'hle', theme['latex:arguments']))
				for m in re.finditer(r'\\\\|&|\|', text):
					ops.append(('add', 'hlf', f'{top}+{m.start()}c', f'{top}+{m.end()}c'))
				ops.append(('config', 'hlf', theme['latex:operators']))
				for m in re.finditer(r'\[.+?\]', text, re.DOTALL):
					ops.append(('add', 'hlg', f'{top}+{m.start()}c', f'{top}+{m.end()}c'))
				ops.append(('config', 'hlg', theme['latex:square_brackets']))
				for m in _LH_PAT.finditer(text):
					s = f'{top}+{m.start()}c'
					e = f'{top}+{m.end()}c'
					ops.append(('clear_other', s, e))
					ops.append(('add', 'hlh', s, e))
				ops.append(('config', 'hlh', theme['latex:comments']))
			elif ft == 'html':
				for m in _HS_PAT.finditer(text):
					ops.append(('add', 'hstuff', f'{top}+{m.start()}c', f'{top}+{m.end()}c'))
				ops.append(('config', 'hstuff', theme['html:tags']))
				for m in _HATTR_PAT.finditer(text):
					ops.append(('add', 'hattr', f'{top}+{m.start()}c', f'{top}+{m.end()}c'))
				ops.append(('config', 'hattr', theme['html:attributes']))
				for m in _HSTR_PAT.finditer(text):
					s = f'{top}+{m.start()}c'
					e = f'{top}+{m.end()}c'
					ops.append(('clear_other', s, e))
					ops.append(('add', 'hstr', s, e))
				ops.append(('config', 'hstr', theme['html:quotes']))
				# Detect if visible region starts inside <!-- ... --> comment
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
				ops.append(('config', 'hcmt', theme['html:comments']))
		except Exception:
			pass
		type_.after(0, lambda: _finish_ha(ops))
	def _finish_ha(ops):
		try:
			if type_.get(top, bottom) == text:
				all_tags = set(type_.tag_names())
				for op in ops:
					if op[0] == 'remove':
						type_.tag_remove(op[1], top, bottom)
					elif op[0] == 'add':
						type_.tag_add(op[1], op[2], op[3])
					elif op[0] == 'config':
						exec("type_.tag_config('" + op[1] + "'," + op[2] + ')')
					elif op[0] == 'clear_other':
						for tag in all_tags:
							if tag in _SKIP:
								continue
							type_.tag_remove(tag, op[1], op[2])
		except Exception as e:
			root.error('Error!', f'Error:{e}\nInvalid colour settings.\nQuitting syntax highlighting.')
		finally:
			_ha_running[0] = False
			pending = _ha_pending[0]
			if pending is not None:
				_ha_pending[0] = None
				ha(pending)
	threading.Thread(target = do_hl, daemon = True).start()
def type_setview():
	global type_top
	global type_bottom
	type_top, type_bottom = type_getvisible()
	ha(hmode.replace('la', 'latex'))
	root.after(10, type_setview)
def do_backup():
	if all((not hmode in ['png', 'pdf', 'epub'], bfr, title)):
		open(os.path.join(os.path.dirname(os.path.splitext(title)[0]), '.' + os.path.basename(os.path.splitext(title)[0]) + 'backpynotes' + os.path.splitext(title)[1]), 'w+', encoding = 'utf-8').write(type_.get('1.0', 'end'))
		show('saved backup.')
	root.after(5000, do_backup)
do_backup
def keypress(event = None):
	global bfr
	global type_
	global tabs
	global unsaved
	global unsavedtext
	ln.redraw()
	exec("type_.tag_config('marked'," + theme['pynotes:marked'] + ')')
	filesize.config(text = str(len(io.StringIO(type_.get('1.0', 'end')).read()) - 1) + ' bytes')
	if hmode == 'py':
		tabs.tab(1, state = 'normal')
		trigger_name_scan()
		ha('py')
	else:
		tabs.tab(1, state = 'hidden')
		ha(hmode.replace('la', 'latex'))
	filename.config(text = os.path.basename(title) + ' *')
	if title:
		filename.config(text = os.path.basename(title))
	else:
		if not pcsettitle:
			root.title('PyNotes - Untitled')
		filename.config(text = 'Untitled')
	if title and not hmode in ['png', 'pdf', 'epub']:
		if type_.get('1.0', 'end-1c').strip() != unsavedtext.strip():
			unsaved = True
			if title and not pcsettitle:
					root.title('PyNotes - ' + os.path.basename(title) + ' *')
		else:
			unsaved = False
			if title and not pcsettitle:
					root.title('PyNotes - ' + os.path.basename(title))
	if not title:
		if type_.get('1.0', 'end-1c'):
			unsaved = True
		else:
			unsaved = False
	if hmode in ['png', 'pdf', 'epub']:
		root.title('PyNotes - ' + os.path.basename(title))
def indent():
	type_.edit_separator()
	if not hmode == 'py':
		return
	l = int(type_.index('insert').split('.')[0])
	type_.insert(f'insert', '\n')
	line = type_.get(f'{l}.0', f'{l}.end')
	whitespace = re.match(r'\s*', line).group()
	type_.insert(f'{l + 1}.0', whitespace)
	comments = re.findall(r'#.+', line)
	for comment in comments:
		line = line.replace(comment, '')
	line = line.strip()
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
def f5(event = None):
	if hmode == 'py':
		rp()
	elif hmode == 'la':
		runtex('lua')
	elif hmode == 'html':
		hp()
	else:
		return
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
def term(pythonfile = None):
	import queue as _queue
	tw = root.subwin()
	tw.title(pythonfile if pythonfile else 'Terminal')
	term = tw.textbox(background = 'black', foreground = 'white', font = (monospace, 12), insertbackground = 'white')
	term.pack(fill = 'both')
	tw.update()
	tw.sizablefalse()
	running = [True]
	out_q = _queue.Queue()
	cursor = ['1.0']
	screen_top = [1]
	prev_was_H1 = [False]
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
		proc = subprocess.Popen([shell, pythonfile] if pythonfile else [shell], stdin = slave_fd, stdout = slave_fd, stderr = slave_fd, close_fds = True, preexec_fn = os.setsid, env = env)
		os.close(slave_fd)
		def _read():
			while running[0]:
				try:
					r, _, _ = _select.select([master_fd], [], [], 0.05)
					if r:
						data = os.read(master_fd, 4096)
						if data:
							out_q.put(data.decode('utf-8', errors = 'replace'))
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
			try: proc.terminate()
			except Exception: pass
			try: os.close(master_fd)
			except Exception: pass
			try: tw.destroy()
			except Exception: pass
		_local_newline = False
	else:
		proc = PtyProcess.spawn([pythonexecutable, pythonfile] if pythonfile else 'powershell.exe', dimensions = (999999, 80))
		def _read():
			while running[0]:
				try:
					data = proc.read(4096)
					if data:
						out_q.put(data)
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
		_local_newline = True
	def _process(text):
		prev_was_H1[0] = False
		term.mark_set('insert', cursor[0])
		i = 0
		n = len(text)
		while i < n:
			ch = text[i]
			if ch == '\r':
				ln = term.index('insert').split('.')[0]
				term.mark_set('insert', f'{ln}.0')
				i += 1
			elif ch == '\x08':
				ln = term.index('insert').split('.')[0]
				if term.compare('insert', '>', f'{ln}.0'):
					term.mark_set('insert', 'insert-1c')
				i += 1
			elif ch == '\n':
				ln = int(term.index('insert').split('.')[0])
				if term.compare(f'{ln + 1}.0', '<', 'end'):
					term.mark_set('insert', f'{ln + 1}.0')
				else:
					term.mark_set('insert', f'{ln}.end')
					term.insert('insert', '\n')
				i += 1
			elif ch == '\x1b':
				rest = text[i:]
				if len(rest) < 2:
					i += 1
					continue
				nxt = rest[1]
				if nxt == '[':
					m = re.match(r'\x1b\[([0-9;?]*)([A-Za-z@`])', rest)
					if m:
						ps = m.group(1).lstrip('?')
						cmd = m.group(2)
						p = [int(x) if x else 0 for x in ps.split(';')] if ps else [0]
						ln = term.index('insert').split('.')[0]
						col = term.index('insert').split('.')[1]
						if cmd == 'K':
							if p[0] == 0: term.delete('insert', f'{ln}.end')
							elif p[0] == 1: term.delete(f'{ln}.0', 'insert')
							else: term.delete(f'{ln}.0', f'{ln}.end')
						elif cmd == 'J':
							if p[0] == 2:
								if prev_was_H1[0]:
									term.delete('1.0', 'end')
									screen_top[0] = 1
									term.mark_set('insert', '1.0')
								else:
									last_line = int(term.index('end').split('.')[0]) - 1
									screen_top[0] = max(screen_top[0], max(1, last_line - 23))
									if term.compare(f'{screen_top[0]}.0', '<', 'end'):
										term.delete(f'{screen_top[0]}.0', 'end')
									cur_last = int(term.index('end').split('.')[0]) - 1
									if screen_top[0] > cur_last:
										term.insert('end', '\n' * (screen_top[0] - cur_last))
									term.mark_set('insert', f'{screen_top[0]}.0')
							elif p[0] == 3:
								if screen_top[0] > 1:
									term.delete('1.0', f'{screen_top[0]}.0')
									screen_top[0] = 1
							elif p[0] == 0:
								term.delete('insert', 'end')
						elif cmd in ('H', 'f'):
							row_ = p[0] if p[0] else 1
							col_ = p[1] if len(p) > 1 and p[1] else 1
							target_line = screen_top[0] + row_ - 1
							last_line = int(term.index('end').split('.')[0]) - 1
							if target_line > last_line:
								term.insert('end', '\n' * (target_line - last_line))
							term.mark_set('insert', f'{target_line}.{col_ - 1}')
						elif cmd == 'A':
							mv = p[0] or 1
							term.mark_set('insert', f'{max(1, int(ln) - mv)}.{col}')
						elif cmd == 'B':
							mv = p[0] or 1
							term.mark_set('insert', f'{int(ln) + mv}.{col}')
						elif cmd == 'C':
							mv = p[0] or 1
							term.mark_set('insert', f'insert+{mv}c')
						elif cmd == 'D':
							mv = p[0] or 1
							term.mark_set('insert', f'insert-{mv}c')
							if term.compare('insert', '<', f'{ln}.0'):
								term.mark_set('insert', f'{ln}.0')
						elif cmd == 'G':
							mv = p[0] or 1
							term.mark_set('insert', f'{ln}.{mv - 1}')
						elif cmd == 'P':
							mv = p[0] or 1
							term.delete('insert', f'insert+{mv}c')
						elif cmd == '@':
							mv = p[0] or 1
							term.insert('insert', ' ' * mv)
							term.mark_set('insert', f'insert-{mv}c')
							end_col = int(term.index(f'{ln}.end').split('.')[1])
							if end_col > 80:
								term.delete(f'{ln}.80', f'{ln}.end')
						prev_was_H1[0] = cmd in ('H', 'f') and (p[0] if p[0] else 1) == 1
						i += len(m.group(0))
					else:
						i += 2
				elif nxt == ']':
					end_osc = rest.find('\x07', 2)
					if end_osc >= 0: i += end_osc + 1
					else:
						st = rest.find('\x1b\\', 2)
						i += st + 2 if st >= 0 else len(rest)
				elif nxt in '()':
					i += 3 if len(rest) >= 3 else 2
				else:
					i += 2
			elif ch == '\t':
				col = int(term.index('insert').split('.')[1])
				sp = 8 - (col % 8)
				for _ in range(sp):
					col = int(term.index('insert').split('.')[1])
					if col >= 80:
						ln2 = int(term.index('insert').split('.')[0])
						if term.compare(f'{ln2 + 1}.0', '<', 'end'):
							term.mark_set('insert', f'{ln2 + 1}.0')
						else:
							term.mark_set('insert', f'{ln2}.end')
							term.insert('insert', '\n')
					cur = term.get('insert', 'insert+1c')
					if cur and cur != '\n':
						term.delete('insert', 'insert+1c')
					term.insert('insert', ' ')
				i += 1
			elif ch >= ' ' and ch != '\x7f':
				col = int(term.index('insert').split('.')[1])
				if col >= 80:
					ln2 = int(term.index('insert').split('.')[0])
					if term.compare(f'{ln2 + 1}.0', '<', 'end'):
						term.mark_set('insert', f'{ln2 + 1}.0')
					else:
						term.mark_set('insert', f'{ln2}.end')
						term.insert('insert', '\n')
				cur = term.get('insert', 'insert+1c')
				if cur and cur != '\n':
					term.delete('insert', 'insert+1c')
				term.insert('insert', ch)
				i += 1
			else:
				i += 1
		cursor[0] = term.index('insert')
	def _poll():
		try:
			while True:
				text = out_q.get_nowait()
				if text is None:
					if pythonfile:
						term.insert('end', '\n\n--- Python code finished, press any key to continue ---')
						term.see('end')
						term.unbind('<Key>')
						term.bind('<Key>', lambda e: _close())
					else:
						try: tw.destroy()
						except Exception: pass
					return
				_process(text)
				term.see('insert')
		except _queue.Empty:
			pass
		if running[0]:
			term.after(50, _poll)
	def _key(event):
		if not running[0]:
			return 'break'
		sym = event.keysym
		ch = event.char
		try:
			if sym == 'Return':
				_write(b'\r')
				if _local_newline:
					_process('\r\n')
			elif sym == 'BackSpace': _write(b'\x7f')
			elif sym == 'Delete': _write(b'\x1b[3~')
			elif sym == 'Up': _write(b'\x1b[A')
			elif sym == 'Down': _write(b'\x1b[B')
			elif sym == 'Left': _write(b'\x1b[D')
			elif sym == 'Right': _write(b'\x1b[C')
			elif sym == 'Tab': _write(b'\t')
			elif sym == 'Home': _write(b'\x1b[H')
			elif sym == 'End': _write(b'\x1b[F')
			elif ch: _write(ch.encode('utf-8'))
		except OSError:
			pass
		return 'break'
	def _snap_cursor():
		term.mark_set('insert', cursor[0])
	def _click(e):
		term.focus_set()
		term.after_idle(_snap_cursor)
		return 'break'
	term.bind('<Key>', _key)
	term.bind('<Button-1>', _click)
	term.bind('<ButtonRelease-1>', lambda e: 'break')
	term.bind('<B1-Motion>', lambda e: 'break')
	term.bind('<Button-2>', lambda e: 'break')
	tw.protocol('WM_DELETE_WINDOW', _close)
	threading.Thread(target = _read, daemon = True).start()
	term.after(50, _poll)
	term.focus()
	tw.deiconify()
def gl(event = None):
	l = root.askstring('Go to line', 'Go to line no. :')
	if not l:
		return
	try:
		l = int(l)
	except Exception:
		root.error('Error', f'Cannot go to line number \'{l}\'')
		return
	else:
		type_.see(f'{l}.0')
		type_.mark_set('insert', f'{l}.0')
		type_.tag_add('sel', f'{l}.0', f'{l}.end')
def hx():
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
	hxh.insert('end', ("'editor' or 'ed': Switch to the Editor tab and focus on the textbox\n'mathgod' or 'mg': Open MathGod\n'exit' or 'e': Exit the window (the same as File → Exit)\n'save' or 's': Save the current file (the same as File → Save)\n'saveas' or 'sa': Copy the current file to another filename (the same as File → Save As)\n'u' or 'undo': Undo the last edit\n'r' or 'redo': Redo the last undoed edit\n'termexec:{string}' or 'te:{string}': Run the given string as a terminal command\n'write:{string}*{n}' or 'w:{string}*{n}': Copy the given text {n} times after the cursor position\n'search' or 'f': Find a string in the editor (the same as Edit → Find)\n'fr' or 'find-replace' or 'findreplace': Find and replace a string in the editor instantly (the same as Edit → Find & Replace)\n'show-source' or 'source-code': Show the main source code of PyNotes (/usr/share/PyNotes/ or C:/Program Files/PyNotes/) (the same as Options → Source Code)\n'new' or 'n': Open a new document (the same as File → New)\n'gotoline' or 'gl' or 'l': Go to a specified line\n'pyshell' or 'ps': Open the Python shell if you are in Python HMode.\n'o' or or 'load' or 'find' or 'open': Load a new file into the editor (the same as File → Open)\n't' or 'term' or 'terminal' or 'cmd': Open the terminal (the same as Options → Terminal)\n'prf' or 'preferences': Change the preferences (the same as Options → Preferences)\n'cancel' or 'z': Cancel the command and go back to the editor\n'a' or 'selall' or 'all': Select all the text in the editor\n'c' or 'copy': Copy the selected text\n'cut': Cut the selected text\n'p' or 'paste': Paste the last copied text\n'h:{(x/em/pc/mg/pl)}' or 'help:{(x/em/pc/mg/pl)}': Open the Help of Alt-X commands (this), Email, PyCode, MathGod, Plugins\n'hmode:{(py/la/norm/em/html)}': Change the HMode (PyNotes mode)\n'pf' or 'pagenext': Scroll down a page in the editor\n'pb' or 'pageback': Scroll up a page in the editor\n'clear': Clear the editor completely\n'full': Make the window fullscreen\n'max' or 'maximize': Maximize the window\n'min': Minimize the window\n'pycode' or 'pc': Open PyCode\n'<Esc>': 'cancel'\n'sp' or 'speak': Speak the text selected out loud\n'ir' or 'indent-region': Indent the selected region with tabs or spaces\n'unir' or 'unindent-region': Unindent the selected region (handles tabs, spaces, and mixed)\n'st' or 'speech-to-text': Use speech-to-text\n'opd' or 'openplugindir': Open the Plugin's Directory\n'dp' or 'downloadplugins': Download plugins from the PyNotes' GitHub\n'ch' or 'changes': Open a list of the changes made in PyNotes v" + v + "\n'ab' or 'abt' or 'about' or 'pynotes': Open the PyNotes About\n're:{command}*{n}' or 'repeat:{command}*{n}': Repeat the given command {n} times\n'run': Run the code in the editor if the HMode is Python / LaTeX / HTML\n'cr' or 'comment' or 'comment-region': Comment the selected code if the HMode is Python / LaTeX / HTML\n'uncr' or 'uncomment' or 'uncomment-region': Uncomment the selected code if the HMode is Python / LaTeX / HTML\n'fullup': Moves the cursor to the beginning of the fil\n'fulldown': Moves the cursor to the end of the file\n'ms' or 'mark' or 'markset' or 'mark-selection': Visually marks the selected text in the editor\n'unms' or 'unmark' or 'unmark-selection': Unmarks the visually marked text inside the selection in the editor\n'unma' or 'unmarkall': Unmarks all the visually marked text in the editor\n'sol' or 'startofline': Move the cursor to the start of the line\n'eol' or 'endofline': Move the cursor to the end of the line\n'sendemail' or 'sendmail': Switch to the Email tab if the HMode is Email").replace('\n', '\n\n'))
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
def cmdrun(command):
	global hmode
	type_.focus_set()
	cmdentry.delete('1.0', 'end')
	cmdlabel.config(text = '')
	cmdentry.config(state = 'disabled')
	type_.config(state = 'normal')
	cmdentry.unbind('<Return>')
	cmdentry.unbind('<Escape>')
	if command in plgncmds.keys():
		try:
			execvars = globals()
			execvars['__file__'] = os.path.join(plgncmds[command][0], 'commands')
			exec(plgncmds[command][1], execvars)
		except Exception as error:
			root.error('Error!', f'There was an error in running the command \'{command}\' from the plugin "{os.path.basename(os.path.normpath(plgncmds[command][0]))}":\n{error}')
		return
	if command in pcwrittencommands.keys():
		try:
			exec(pcwrittencommands[command], globals())
		except Exception as error:
			root.error('Error!', f'There was an error in running the command \'{command}\' defined in PyCode:\n{error}')
		return
	elif command == 'exit' or command == 'e':
		ext()
	elif command == 'sol' or command == 'startofline':
		n = type_.index('insert').split('.')[0]
		type_.mark_set('insert', n + '.end')
		show(f'moved to start of line {n}')
	elif command == 'eol' or command == 'endofline':
		n = type_.index('insert').split('.')[0]
		type_.mark_set('insert', n + '.0')
		show(f'moved to end of line {n}')
	elif command == 'changes' or command == 'ch':
		changes()
		show('show pynotes changes')
	elif command == 'run':
		f5()
		show('run code')
	elif command == 'ms' or command == 'mark' or command == 'markset' or command == 'mark-selection':
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
		try:
			start = type_.index('sel.first')
			end = type_.index('sel.last')
		except Exception:
			show('nothing is selected')
		else:
			type_.tag_remove('marked', start, end)
			show(f'unmarked text from {start} to {end}')
	elif command == 'sendemail' or command == 'sendmail':
		if hmode == 'email':
			tabs.select(ef)
			show('switch to email tab')
		else:
			show('not in email hmode')
	elif command == 'unma' or command == 'unmarkall':
		type_.tag_remove('marked', '1.0', 'end')
		show('unmarked all text')
	elif command == 'comment' or command == 'cr' or command == 'comment-region':
		if not hmode in ('py', 'la', 'html'):
			show('hmode is not python / latex / html')
			return
		try:
			start = int(type_.index('sel.first').split('.')[0])
			end = int(type_.index('sel.last').split('.')[0])
		except Exception:
			show('nothing is selected')
		else:
			ender = ''
			if hmode == 'py':
				commentor = '#'
			elif hmode == 'la':
				commentor = '%'
			elif hmode == 'html':
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
			show('comment-region')
	elif command == 'uncomment' or command == 'uncr' or command == 'uncomment-region':
		if not hmode in ('py', 'la', 'html'):
			show('hmode is not python / latex / html')
			return
		try:
			start = int(type_.index('sel.first').split('.')[0])
			end = int(type_.index('sel.last').split('.')[0])
		except Exception:
			show('nothing is selected')
		else:
			ender = ''
			if hmode == 'py':
				commentor = '#'
			elif hmode == 'la':
				commentor = '%'
			elif hmode == 'html':
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
			show('uncomment-region')
	elif command == 'pyshell' or command == 'ps':
		if hmode == 'py':
			tabs.select(sf)
			shellcmd.focus()
			show('switch to python shell')
		else:
			show('not in python hmode')
	elif command == 'fullup':
		type_.mark_set('insert', '1.0')
		type_.see('1.0')
	elif command == 'fulldown':
		type_.mark_set('insert', 'end-1c')
		type_.see('end-1c')
	elif command == 'editor' or command == 'ed':
		tabs.select(mf)
		type_.focus()
		show('switch to editor')
	elif command[:2] == 'h:' or command[:5] == 'help:':
		thing = command.split(':')[1].strip()
		if thing == 'x' or thing == 'commands':
			hx()
			show('open alt-x commands help')
		elif thing == 'em' or thing == 'email':
			hemail()
			show('open email help')
		elif thing == 'pc' or thing == 'pycode':
			helppycode()
			show('open pycode help')
		elif thing == 'mg' or thing == 'mathgod':
			helpmathgod()
			show('open mathgod help')
		elif thing == 'pl' or thing == 'plugins':
			ap()
			show('open plugins help')
	elif command == 'st' or command == 'speech-to-text':
		st()
		show('open speech-to-text')
	elif command == 'opd' or command == 'openplugindir':
		op()
		show('open plugin directory')
	elif command == 'dp' or command == 'downloadplugins':
		dp()
		show('open download plugins url')
	elif command == 'indent-region' or command == 'ir':
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
			show('indent-region')
	elif command == 'unindent-region' or command == 'unir':
		try:
			start = int(type_.index('sel.first').split('.')[0])
			end = int(type_.index('sel.last').split('.')[0])
		except Exception:
			show('nothing is selected')
		else:
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
			show('unindent-region')
	elif command[:9] == 'termexec:' or command[:3] == 'te:':
		try:
			show('output: ' + termexec(command.split(':')[1]))
		except Exception:
			show(f'invalid command \'{command}\'')
	elif command == 'mathgod' or command == 'mg':
		mathgod()
		show('open mathgod')
	elif command[:6] == 'write:' or command[:2] == 'w:':
		type_.edit_separator()
		try:
			type_.insert(type_.index('insert'), command.split(':')[1].split('*')[0].encode().decode('unicode_escape') * int(command.split('*')[1]))
			show(f'wrote {command.split(":")[1]} text')
		except Exception:
			show(f'invalid command \'{command}\'')
		type_.edit_separator()
	elif command[:7] == 'repeat:' or command [:3] == 're:':
		try:
			for i in range(int(command.split(':')[1].split('*')[1])):
				cmdrun(command.split(':')[1].split('*')[0])
			show(f'repeated {command.split(":")[1].replace("*", " ")} times')
		except Exception:
			show(f'invalid command \'{command}\'')
	elif command == 'u' or command == 'undo':
		undo()
	elif command == 'r' or command == 'redo':
		redo()
	elif command == 'save' or command == 's':
		sssv()
		show('save file')
	elif command == 'saveas' or command == 'sa':
		ssv()
		show('save as file')
	elif command == 'search' or command == 'f':
		f()
		show('find text')
	elif command == 'find-replace' or command == 'findreplace' or command == 'fr':
		fr()
		show('find & replace text')
	elif command == 'show-source' or command == 'source-code':
		ss()
		show('open pynotes source code')
	elif command == 'new' or command == 'n':
		nw()
		show('open new file')
	elif command == 'l' or command == 'gl' or command == 'gotoline':
		gl()
	elif command == 'open' or command == 'find' or command == 'o' or command == 'load':
		llld()
		show('open file')
	elif command == 'terminal' or command == 'cmd' or command == 'term' or command == 't':
		term()
		show('open pynotes terminal')
	elif command == 'prf' or command == 'preferences':
		prf()
		show('open preferences')
	elif command == 'cancel' or command == 'z':
		pass
	elif command == '':
		pass
	elif command == 'a' or command == 'selall' or command == 'all':
		selall()
		show('selected all text')
	elif command == 'copy' or command == 'c':
		cp()
		show('copied text')
	elif command == 'cut':
		cut()
		show('cut text')
	elif command == 'pf' or command == 'pagenext':
		ptf()
		show('go to next page')
	elif command == 'pb' or command == 'pageback':
		ptb()
		show('go to previous page')
	elif command == 'paste' or command == 'p':
		pst()
		show('paste text')
	elif command == 'sp' or command == 'speak':
		spk()
		show('speak text')
	elif command == 'full':
		root.attributes('-fullscreen', True)
		show('fullscreen mode')
	elif command == 'unfull':
		root.attributes('-fullscreen', False)
		show('windowed mode')
	elif command == 'max' or command == 'maximize':
		root.geometry(f'{root.winfo_screenwidth()}x{root.winfo_screenheight()}')
		if platform.system() == 'Linux':
			root.attributes('-zoomed', True)
		else:
			root.state('zoomed')
		show('maximize window')
	elif command == 'min':
		root.iconify()
		show('minimize window')
	elif command == 'clear':
		if root.ask('Warning', 'Clear the editor?', options = ('ok', 'cancel'), icon = 'warning'):
			type_.delete('1.0', 'end')
			show('cleared editor')
	elif command == 'pycode' or command == 'pc':
		pc()
		show('open pycode')
	elif command == 'ab' or command == 'abt' or command == 'about' or command == 'pynotes':
		abt()
		show('about pynotes')
	elif command[:6] == 'hmode:':
		if hmode in ['png', 'pdf', 'epub']:
			show(f'invalid command \'{command}\'')
		else:
			try:
				ans = command.split(':')[1]
				ans = ans.lower().replace(' ', '')
				if ans == 'python' or ans == 'py':
					m.entryconfig(4, state = 'normal')
					m.entryconfig(5, state = 'disabled')
					tabs.tab(2, state = 'hidden')
					for widget in lf.winfo_children()[1:]:
						widget.config(state = 'disabled')
					hmode = 'py'
					filetype.config(text = 'Python File (*.py)')
				elif ans == 'latex' or ans == 'la':
					m.entryconfig(5, state = 'normal')
					m.entryconfig(4, state = 'disabled')
					tabs.tab(2, state = 'hidden')
					for widget in lf.winfo_children()[1:]:
						widget.config(state = 'enabled')
					hmode = 'la'
					filetype.config(text = 'LaTeX / TeX File (*.tex)')
				elif ans == 'normal' or ans == 'norm':
					m.entryconfig(4, state = 'disabled')
					m.entryconfig(5, state = 'disabled')
					tabs.tab(2, state = 'hidden')
					for widget in lf.winfo_children()[1:]:
						widget.config(state = 'disabled')
					hmode = 'norm'
					filetype.config(text = 'Plain Text (*.*)')
				elif ans == 'email' or ans == 'em':
					m.entryconfig(4, state = 'disabled')
					m.entryconfig(5, state = 'disabled')
					hmode = 'email'
					filetype.config(text = 'Plain Text (*.*)')
					tabs.tab(2, state = 'normal')
				elif ans == 'html':
					m.entryconfig(4, state = 'disabled')
					m.entryconfig(5, state = 'disabled')
					hmode = 'html'
					filetype.config(text = 'HTML File (*.html)')
					tabs.tab(2, state = 'hidden')
					for widget in lf.winfo_children()[1:]:
						widget.config(state = 'disabled')
				else:
					show(f'invalid command \'{command}\'')
					cmdlabel.config(text = '')
					return
				show('changed hmode')
			except Exception:
				show(f'invalid command \'{command}\'')
	else:
		show(text = f'invalid command \'{command}\'')
	cmdlabel.config(text = '')
	keypress()
def selall(event = None):
	show(text = 'select all')
	type_.tag_add('sel', '1.0', 'end')
	return 'break'
def show(text):
	cmdentry.config(state = 'normal')
	cmdentry.delete('1.0', 'end')
	cmdentry.insert('end', text)
	cmdentry.config(state = 'disabled')
def cp(event = None):
	global root
	try:
		select = type_.get('sel.first', 'sel.last')
	except Exception:
		return
	root.clipboard_clear()
	root.clipboard_append(select)
	show(text = 'copy text')
def cut(event = None):
	try:
		select = type_.get('sel.first', 'sel.last')
	except Exception:
		return
	type_.delete('sel.first', 'sel.last')
	root.clipboard_clear()
	root.clipboard_append(select)
	show(text = 'cut text')
engine = stt.init()
def actualspk(text):
	global engine
	try:
		engine.say(text)
		engine.runAndWait()
	except Exception as error:
		root.error('Error', f'An error occured:{error}')
def spk(event = None):
	try:
		select = type_.get('sel.first', 'sel.last')
	except Exception:
		return
	else:
		speakthread = threading.Thread(target = actualspk, args = (select,), daemon = True)
		speakthread.start()
def pst(event = None):
	global root
	try:
		text = root.clipboard_get()
	except Exception:
		return
	type_.edit_separator()
	type_.insert('insert', text)
	type_.edit_separator()
	show(text = 'paste text')
	return 'break'
def cmd(event = None):
	cmdentry.config(state = 'normal')
	cmdentry.delete('1.0', 'end')
	cmdentry.focus_set()
	type_.config(state = 'disabled')
	cmdlabel.config(text = 'Alt-x-')
	cmdentry.bind('<Return>', lambda event: cmdrun(cmdentry.get('1.0', 'end')[:-1]))
	cmdentry.bind('<Escape>', lambda event: cmdrun('cancel'))
def ptf(event = None):
	type_.yview_scroll(1, 'pages')
def ptb(event = None):
	type_.yview_scroll(-1, 'pages')
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
	variables = list()
	for line in code:
		if line[:7] != 'python:' and re.findall(r'.+?=.+?', line):
			variables.append((line.split('=')[0].strip(), line.split('=')[1].strip()))
		else:
			line = line[7:] if line[:7] == 'python:' else line
			line_ = line
			if variables:
				for var in variables:
					varreplaces = re.findall(r'(?<!\')' + var[0] + r'(?!\')', line_)
					if varreplaces:
						for found in varreplaces:
							line_ = line_.replace(found, var[1])
			try:
				exec(line_, globals())
			except Exception as error:
				root.error('Error', f'Error in translated PyCode: {error}')
def pccmdwrite(text, n):
	type_.edit_separator()
	type_.insert(type_.index('insert'), text * n)
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
def pcindentselection():
	try:
		start = int(type_.index('sel.first').split('.')[0])
		end = int(type_.index('sel.last').split('.')[0])
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
	except Exception:
		pass
	keypress()
def pcunindentregion(start, end):
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
def pcunindentselection():
	try:
		start = int(type_.index('sel.first').split('.')[0])
		end = int(type_.index('sel.last').split('.')[0])
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
	except Exception:
		pass
	keypress()
def pcopenhelp(thing):
	if thing == 'commands':
		hx()
	elif thing == 'email':
		hemail()
	elif thing == 'pycode':
		helppycode()
	elif thing == 'mathgod':
		helpmathgod()
	elif thing == 'plugins':
		ap()
def pcpyshell():
	if hmode == 'py':
		tabs.select(sf)
		shellcmd.focus()
	keypress()
def pcswitchedit():
	tabs.select(mf)
	type_.focus()
	keypress()
def pctermexec(command):
	show('output: ' + termexec(command))
def pcrepeatx(command, n):
	for i in range(n):
		cmdrun(command)
	keypress()
def pcfullscreen():
	root.attributes('-fullscreen', True)
def pcunfullscreen():
	root.attributes('-fullscreen', False)
def pcmax():
	root.geometry(f'{root.winfo_screenwidth()}x{root.winfo_screenheight()}')
	if platform.system() == 'Linux':
		root.attributes('-zoomed', True)
	else:
		root.state('zoomed')
def pccleareditor():
	if root.ask('Warning', 'Clear the editor?', options = ('ok', 'cancel'), icon = 'warning'):
		type_.delete('1.0', 'end')
def pchmode(mode):
	global hmode
	if hmode in ['png', 'pdf', 'epub']:
		return
	if mode == 'python' or mode == 'py':
		m.entryconfig(4, state = 'normal')
		m.entryconfig(5, state = 'disabled')
		tabs.tab(2, state = 'hidden')
		for widget in lf.winfo_children()[1:]:
			widget.config(state = 'disabled')
		hmode = 'py'
		filetype.config(text = 'Python File (*.py)')
	elif mode == 'latex' or mode == 'la':
		m.entryconfig(5, state = 'normal')
		m.entryconfig(4, state = 'disabled')
		tabs.tab(2, state = 'hidden')
		for widget in lf.winfo_children()[1:]:
			widget.config(state = 'enabled')
		hmode = 'la'
		filetype.config(text = 'LaTeX / TeX File (*.tex)')
	elif mode == 'normal' or mode == 'norm':
		m.entryconfig(4, state = 'disabled')
		m.entryconfig(5, state = 'disabled')
		tabs.tab(2, state = 'hidden')
		for widget in lf.winfo_children()[1:]:
			widget.config(state = 'disabled')
		hmode = 'norm'
		filetype.config(text = 'Plain Text (*.*)')
	elif mode == 'email' or mode == 'em':
		m.entryconfig(4, state = 'disabled')
		m.entryconfig(5, state = 'disabled')
		hmode = 'email'
		filetype.config(text = 'Plain Text (*.*)')
		tabs.tab(2, state = 'normal')
	elif mode == 'html':
		m.entryconfig(4, state = 'disabled')
		m.entryconfig(5, state = 'disabled')
		hmode = 'html'
		filetype.config(text = 'HTML File (*.html)')
		tabs.tab(2, state = 'hidden')
		for widget in lf.winfo_children()[1:]:
			widget.config(state = 'disabled')
	keypress()
def pccommentregion(start, end):
	if not hmode in ('py', 'la', 'html'):
		return
	ender = ''
	if hmode == 'py':
		commentor = '#'
	elif hmode == 'la':
		commentor = '%'
	elif hmode == 'html':
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
def pccommentselection():
	if not hmode in ('py', 'la', 'html'):
		return
	try:
		start = int(type_.index('sel.first').split('.')[0])
		end = int(type_.index('sel.last').split('.')[0])
	except Exception:
		pass
	else:
		ender = ''
		if hmode == 'py':
			commentor = '#'
		elif hmode == 'la':
			commentor = '%'
		elif hmode == 'html':
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
	keypress()
def pcuncommentregion(start, end):
	if not hmode in ('py', 'la', 'html'):
		return
	ender = ''
	if hmode == 'py':
		commentor = '#'
	elif hmode == 'la':
		commentor = '%'
	elif hmode == 'html':
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
def pcuncommentselection():
	if not hmode in ('py', 'la', 'html'):
		return
	try:
		start = int(type_.index('sel.first').split('.')[0])
		end = int(type_.index('sel.last').split('.')[0])
	except Exception:
		pass
	else:
		ender = ''
		if hmode == 'py':
			commentor = '#'
		elif hmode == 'la':
			commentor = '%'
		elif hmode == 'html':
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
	exec("type_.tag_config('marked'," + theme['pynotes:marked'] + ')')
def pcmarkselection():
	try:
		start = type_.index('sel.first')
		end = type_.index('sel.last')
	except Exception:
		return
	type_.tag_add('marked', start, end)
	exec("type_.tag_config('marked'," + theme['pynotes:marked'] + ')')
def pcunmark(a, b = None):
	if not b:
		a, b = a[0], a[1]
	type_.tag_remove('marked', a, b)
def pcunmarkall():
	type_.tag_remove('marked', '1.0', 'end')
def pctkindex(toindex, line = False):
	ans = type_.index(toindex)
	if line == 'line':
		ans = ans.split('.')[0]
	return ans
def pccopytext(text):
	root.clipboard_clear()
	root.clipboard_append(text)
	root.update()
def pcgosettitle(title):
	global pcsettitle
	root.title(title)
	pcsettitle = True
def pcunsettitle():
	global pcsettitle
	pcsettitle = False
	keypress()
def pckillexit():
	os._exit(0)
def pcswitchemailtab():
	if hmode == 'email':
		tabs.select(ef)
def pcread():
	global pcwrittencommands
	global pycodecommands
	global pythoncommands
	pycodecommands = ['aboutpynotes', 'ask', 'cleareditor', 'close', 'cmdrun', 'commentregion', 'commentselection', 'copy', 'copytext', 'cut', 'delete', 'dictate', 'downloadplugins', 'findreplace', 'findtext', 'fullscreen', 'get', 'getselection', 'gotoline', 'hmode', 'indentregion', 'indentselection', 'insert', 'killquit', 'mark', 'markselection', 'mathgod', 'maximize', 'minimize', 'movecursor', 'newfile', 'openfile', 'openhelp', 'openplugindir', 'openpycode', 'openterm', 'pageback', 'pageforw', 'pass', 'paste', 'preferences', 'pynotessourcecode', 'pyshell', 'redo', 'repeatxcommand', 'runcode', 'saveasfile', 'savefile', 'say', 'selall', 'select', 'show', 'speaktext', 'switcheditor', 'switchemailtab', 'termexec', 'tkindex', 'typecommand', 'uncommentregion', 'uncommentselection', 'undo', 'unfullscreen', 'unindentregion', 'unindentselection', 'unmark', 'unmarkall', 'unsetwintitle', 'wait', 'setwintitle', 'write']
	pythoncommands = ['abt()', 'pcask', 'pccleareditor()', 'ext()', 'cmdrun', 'pccommentregion', 'pccommentselection()', 'cp()', 'pccopytext', 'cut()', 'type_.delete', 'st()', 'dp()', 'fr()', 'f()', 'pcfullscreen()', 'type_.get', 'pcgetselection()', 'gl', 'pchmode', 'pcindentregion', 'pcindentselection()', 'type_.insert', 'pckillexit()', 'pcmark', 'pcmarkselection()', 'mathgod()', 'pcmax()', 'root.iconify()', 'pcmovecursor', 'nw()', 'llld()', 'pcopenhelp', 'op()', 'pc()', 'term()', 'ptb()', 'ptf()', 'pass', 'pst()', 'prf()', 'ss()', 'pcpyshell()', 'redo()', 'pcrepeatx', 'f5()', 'ssv()', 'sssv()', 'say', 'selall()', 'pcselecttext', 'show', 'spk()', 'pcswitchedit()', 'pcswitchemailtab()', 'pctermexec', 'pctkindex', 'cmd()', 'pcuncommentregion', 'pcuncommentselection()', 'undo()', 'pcunfullscreen()', 'pcunindentregion', 'pcunindentselection()', 'pcunmark', 'pcunmarkall()', 'pcunsettitle()', 'time.sleep', 'pcgosettitle', 'pccmdwrite']
	pcwrittencommands = {}
	def pycodeindex(pycodecode):
		if pycodecode in pycodecommands:
			return pythoncommands[pycodecommands.index(pycodecode)]
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
					return pythoncommands[pycodecommands.index(func)] + f'({inner})' + after
			giveninput = rest
			if giveninput.strip() in pycodecommands or giveninput.strip().split(' ')[0] in pycodecommands:
				giveninput = pycodeindex(giveninput)
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
				ks = re.findall(r'<.+?>\s*→\s*<.+?>\s*;', line)
				v = re.findall(r'\[.+?\]\s*:→\s*\[.+?\]\s*;', line)
				f = re.findall(r'\(.+?\)\s*→:\s*\(.+?\)\s*;', line)
				c = re.findall(r'⌊.+?⌋\s*→\s*⌊.+?⌋\s*;', line)
				s = re.findall(r'\|.+?\|', line)
				p = re.findall(r'\(python\s*:.+?\)\s*→:\s*\(.+?\)\s*;', line)
				if ks and len(ks) == 1:
					ks = ks[0].strip()[:-1]
					key_part = ks.split('→')[0].strip()
					action_parts = '\\n'.join(map(lambda string: pycodeindex(string.strip()) if string else '', ks.split('→')[1].strip()[:-1][1:].strip().split('↩')))
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
				elif v and len(v) == 1:
					v = v[0].strip()[:-1]
					cdt += v.split(':→')[0].strip()[:-1][1:].strip() + '=' + v.split(':→')[1].strip()[:-1][1:].strip() + '\n'
				elif p and len(p) == 1:
					p = p[0].strip()[:-1]
					func_name = p.split('→:')[0].strip()[:-1][1:].strip()
					to_do = p.split('→:')[1].strip()[:-1][1:].strip().split('↩')
					for i in range(len(to_do)):
						if 'pycode:' in to_do[i]:
							to_do[i] = re.sub(r'pycode:\s*\{([^}]*)\}', lambda m: pycodeindex(m.group(1).strip()), to_do[i])
					to_do = r'\n'.join(to_do)
					cdt += f'python:def {func_name.split(":")[1]}(): exec("{to_do}")\n'
					if not func_name.split(':')[1].strip() in pycodecommands:
						pycodecommands.append(func_name.split(':')[1].strip())
						pythoncommands.append(func_name.split(':')[1].strip() + '()')
				elif f and len(f) == 1:
					f = f[0].strip()[:-1]
					func_name = f.split('→:')[0].strip()[:-1][1:].strip()
					cdt += f'def {func_name}(): '
					to_do = f.split('→:')[1].strip()[:-1][1:].strip().split('↩')
					for i in range(len(to_do)):
						if to_do[i]:
							to_do[i] = pycodeindex(to_do[i].strip())
						else:
							to_do[i] = ''
					to_do = r'\n'.join(to_do)
					cdt += f'exec("{to_do}")' + '\n'
					if not func_name in pycodecommands:
						pycodecommands.append(func_name)
						pythoncommands.append(func_name + '()')
				elif c and len(c) == 1:
					c = c[0].strip()[:-1]
					cmd = c.split('→')[0].strip()[:-1][1:].strip()
					to_do = c.split('→')[1].strip()[:-1][1:].strip().split('↩')
					for i in range(len(to_do)):
						if to_do[i]:
							to_do[i] = pycodeindex(to_do[i].strip())
						else:
							to_do[i] = ''
					to_do = '\n'.join(to_do)
					pcwrittencommands[cmd] = to_do
				elif s and len(s) == 1:
					s = s[0].strip()
					startupcdt += f'{'\n'.join(map(lambda string: pycodeindex(string.strip()) if string else '', s[1:-1].strip().split('↩')))}' + '\n'
				else:
					root.error('Error in PyCode', f'Invalid Syntax in line:\n{line}')
			except Exception:
				root.error('Error in PyCode', f'Invalid Syntax in line:\n{line}')
	defaults_cdt = "root.bind('<Alt-x>', cmd)\ntype_.bind('<Control-a>', selall)\ntype_.bind('<Control-c>', cp)\ntype_.bind('<Control-v>', pst)\ntype_.bind('<Control-x>', cut)\ntype_.bind('<KeyRelease>', keypress)\ntype_.bind('<BackSpace>', lambda event: show('delete text'))\ntype_.bind('<Delete>', lambda event: show('delete text'))\ntype_.bind('<Return>', lambda event: indent())\nroot.bind('<Control-n>', nw)\nroot.bind('<Control-o>', llld)\nroot.bind('<Control-s>', sssv)\nroot.bind('<Control-S>', ssv)\nroot.bind('<Control-w>', ext)\nroot.bind('<Alt-l>', gl)\nroot.bind('<Control-p>', ptf)\nroot.bind('<Control-P>', ptb)\nroot.bind('<Control-f>', f)\nroot.bind('<Control-F>', fr)\nroot.bind('<F5>', f5)\nroot.bind('<Control-z>', lambda event: undo())\nroot.bind('<Control-Z>', lambda event: redo())\n"
	cdt = defaults_cdt + cdt
	for mod_key in set(list(mod_key_transitions.keys()) + list(mod_key_completions.keys())):
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
def pc(event = None):
	global defs
	global wholenewwords
	for binded in wholenewwords:
		root.unbind(binded)
		type_.unbind(binded)
	wholenewwords.clear()
	pcwin = root.subwin()
	pcwin.title('PyCode - PyNotes')
	gcframe = pcwin.frame()
	buttonframe = ttkwidgets.frames.ScrolledFrame(gcframe)
	buttonframe.pack(side = 'top', fill = 'y', expand = True)
	_bf_active = [False]
	def _bf_scroll(event):
		if not _bf_active[0]:
			return
		if event.num == 4 or event.delta > 0:
			buttonframe._canvas.yview_scroll(-1, 'units')
		elif event.num == 5 or event.delta < 0:
			buttonframe._canvas.yview_scroll(1, 'units')
	def _bf_bind_scroll(event):
		buttonframe._canvas.bind_all('<MouseWheel>', _bf_scroll)
		buttonframe._canvas.bind_all('<Button-4>', _bf_scroll)
		buttonframe._canvas.bind_all('<Button-5>', _bf_scroll)
	def _bf_unbind_scroll(event):
		buttonframe._canvas.unbind_all('<MouseWheel>')
		buttonframe._canvas.unbind_all('<Button-4>')
		buttonframe._canvas.unbind_all('<Button-5>')
	buttonframe._canvas.bind('<Enter>', _bf_bind_scroll)
	buttonframe._canvas.bind('<Leave>', _bf_unbind_scroll)
	buttonframe.interior.bind('<Enter>', _bf_bind_scroll)
	buttonframe.interior.bind('<Leave>', _bf_unbind_scroll)
	pccmddonebutton = pcwin.button(master = gcframe, text = 'Done', command = lambda: [setcommand('Done'), gcframe.update()])
	gcframe.pack(side = 'left', fill = 'y', expand = True, padx = 10, pady = 10)
	pcwin.text(master = buttonframe.interior, text = 'Define:').grid(column = 0)
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
			prompttext = pcwin.text(master = buttonframe.interior, text = 'Commands:')
			prompttext.grid(column = 0, row = 0)
			row = 0
			for button in buttons:
				row += 1
				button.grid(column = 0, row = row, sticky = 'ew')
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
			prompttext = pcwin.text(master = buttonframe.interior, text = 'Commands:')
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
			prompttext = pcwin.text(master = buttonframe.interior, text = 'Commands:')
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
			prompttext = pcwin.text(master = buttonframe.interior, text = 'Commands:')
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
	optionsdropdown = pcwin.dropdown(stringvar = todefine, showdefault = 'Function', options = ['Function', 'Python Function', 'Variable', 'Startup Code', 'Keyboard Shortcut', 'Alt-X Command'], master = buttonframe.interior, command = lambda inpt: [optionsdropdown.config(state = 'disabled'), define(inpt), optionsdropdown.config(state = 'normal')])
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
		buttonframe._canvas.yview_moveto(0)
	for command in commands:
		button = pcwin.button(master = buttonframe.interior, text = command, command = lambda command = command: setcommand(command))
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
	pccmdlist.insert('1.0', "aboutpynotes - Opens the PyNotes About.\n\nask 'prompt' - Asks an input from the user and returns the answer.\n\ncleareditor - Clears the editor.\n\nclose - Closes PyNotes.\n\ncmdrun 'command' - Runs the given Alt-X command.\n\ncommentregion 'a', 'b' - Coments the text from a given line number 'a' to a given line number 'b' in the editor if the HMode is Python / LaTeX / HTML.\n\ncommentselection - Comments the selected code if the HMode is Python / LaTeX / HTML.\n\ncopy - Copies the selected text in the editor.\n\ncopytext 'text' - Copies the given input to the clipboard\n\ncut - Cuts the selected text in the editor.\n\ndelete 'a', 'b' - Deletes the text from a given tkinter-style index 'a' to a given tkinter-style index 'b' in the editor.\n\ndictate - Opens the speech-to-text, lets you dictate text to the editor.\n\ndownloadplugins - Automatically opens a link to the PyNotes GitHub Plugin page to let you download plugins in your default browser.\n\nfindreplace - Opens Find & Replace.\n\nfindtext - Opens Find.\n\nfullscreen - Makes the PyNotes window fullscreen.\n\nget 'a', 'b' - Gets the text in the editor from a given tkinter style index 'a' to a given tkinter-style index 'b'.\n\ngetselection - Gets the range of the selected text in the editor and returns it.\n\ngotoline - Asks for an input and goes to the given line in the editor.\n\nhmode 'py/la/html/em/norm' - Switches the HMode (PyNotes mode) to Python / LaTeX / HTML / Email / Normal.\n\nindentregion 'a', 'b' - Indents the text from a given line number 'a' to a given line number 'b' in the editor.\n\nindentselection - Indents the selected region in the editor.\n\ninsert 'index', 'text' - Inserts the text at a given tkinter-style index in the editor.\n\nkillquit - Forcibly kills PyNotes. Changes will not be saved.\n\nmark 'a', 'b' - Visually marks the text between a tkinter-style index 'a' and a tkinter-style index 'b' in the editor.\n\nmarkselection - Visually marks the selected text in the editor.\n\nmathgod - Opens MathGod.\n\nmaximize - Maximizes the PyNotes window.\n\nminimize - Minimizes the PyNotes window.\n\nmovecursor 'index' - Moves the cursor to a given tkinter-style index in the editor.\n\nnewfile - Opens a new file in the editor.\n\nopenfile - Opens a file picker to open an existing file in the editor.\n\nopenhelp 'commands/email/pycode/mathgod/plugins' - Opens the Help about the given feature.\n\nopenplugindir - Opens the plugins directory in your file manager.\n\nopenpycode - Opens PyCode.\n\nopenterm - Opens the PyNotes terminal.\n\npageback - Goes to the previous page in the editor.\n\npageforw - Goes to the next page in the editor.\n\npass - Do nothing.\n\npaste - Pastes your clipboard in the editor.\n\npreferences - Opens the PyNotes preferences.\n\npynotessourcecode - Opens the PyNotes source code in the editor.\n\npyshell - Opens the Python Shell if you are in Python HMode.\n\nredo - Redos the last undo in the editor.\n\nrepeatxcommand 'command', n - Repeats the given Alt-X command n times.\n\nruncode - Runs the code in the editor if the HMode is Python / LaTeX / HTML.\n\nsaveasfile - Save the text in the editor to another filename.\n\nsavefile - Saves the file in the editor.\n\nsay 'input' - Opens a graphical messagebox showing the given input. You can also use a variable here.\n\nselall - Selects all the text in the editor.\n\nselect 'a', 'b' - Selects the text from a given tkinter-style index 'a' to a given tkinter-style index 'b' in the editor.\n\nshow 'text' - Shows the given text in the Alt-X command box.\n\nspeaktext - Speaks the selected text in the editor.\n\nswitcheditor - Switches to the editor tab.\n\n'switchemailtab' - Switches to the Email tab if the HMode is Email.\n\ntermexec 'command' - Executes the given command in a terminal and shows the output in the Alt-X command box.\n\ntkindex 'toindex', (optional: 'line') - Indexes the given tkinter-style input in the editor and returns the output. If the optional 'line' input is also given, it returns only the linenumber as a string.\n\ntypecommand - Lets you type an Alt-X command.\n\nuncommentregion 'a', 'b' - Uncomments the text from a given line number 'a' to another given line number 'b' in the editor if the HMode is Python / LaTeX / HTML.\n\nuncommentselection - Uncomments the selected text in the editor if the HMode is Python / LaTeX / HTML.\n\nundo - Undoes the last edit in the editor.\n\nunfullscreen - Makes PyNotes windowed mode from fullscreen.\n\nunmark 'a', 'b' - Unmark the visually marked text in the editor from a tkinter-style index 'a' to a tkinter-style index 'b'.\n\nunmarkall - Unmarks all the visually marked text in the editor.\n\nunsetwintitle - Sets the window title back to normal after the command 'setwintitle'\n\nwait n - Freezes PyNotes for n seconds.\n\nsetwintitle 'title' - Sets the title of the PyNotes window to a given string.\n\nwrite 'text', n - Writes the given text repeated n times in the editor.")
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
	hpwin.text(master = vt, text = 'If you want to keep using a long string in PyCode again and again, it will be easier to use a variable.\nThis is how to define a variable \'something\' with the value \'something else\':').grid(column = 0, row = 0, padx = 10, pady = 10, sticky = 'w')
	hpwin.text(master = vt, text = '[something] :→ [\'something else\'];', style = 'CodeStyle.TLabel').grid(column = 0, row = 1, padx = 10, pady = 10, sticky = 'w')
	hpwin.text(master = vt, text = 'This can then be used in Keyboard Shortcuts and Functions like this:').grid(column = 0, row = 2, padx = 10, pady = 10, sticky = 'w')
	hpwin.text(master = vt, text = '<Control-q> → <say something>;', style = 'CodeStyle.TLabel').grid(column = 0, row = 3, padx = 10, pady = 10, sticky = 'w')
	hpwin.text(master = vt, text = 'Variables cannot be changed later in the code.').grid(column = 0, row = 4, padx = 10, pady = 10, sticky = 'w')
	hpwin.text(master = ft, text = 'Functions are shortcuts or aliases which run multiple lines of code with one command.\nFor example, they can be used to bind multiple PyCode commands to a keyboard shortcut with only a single command.\nThe syntax is:').grid(column = 0, row = 0, padx = 10, pady = 10, sticky = 'w')
	hpwin.text(master = ft, text = '(funcname) →: (commands);', style = 'CodeStyle.TLabel').grid(column = 0, row = 1, padx = 10, pady = 10, sticky = 'w')
	hpwin.text(master = ft, text = 'The commands are separated by a \'↩\'. For example, here is how to make a function named \'something\'\nthat will clear the editor and write \'hello\' 5 times:').grid(column = 0, row = 2, padx = 10, pady = 10, sticky = 'w')
	hpwin.text(master = ft, text = '(something) →: (cleareditor ↩ write \'hello\', 5);', style = 'CodeStyle.TLabel').grid(column = 0, row = 3, padx = 10, pady = 10, sticky = 'w')
	hpwin.text(master = ft, text = 'This can then be used in other Functions, Keyboard Shortcuts, Startup Code, and Alt-X commands like a normal PyCode command.').grid(column = 0, row = 4, padx = 10, pady = 10, sticky = 'w')
	hpwin.text(master = ft, text = 'If you want to make a more complex function that cannot be made with normal PyCode commands,\nyou can make a Python Function in PyCode.\nThe syntax is:').grid(column = 0, row = 5, padx = 10, pady = 10, sticky = 'w')
	hpwin.text(master = ft, text = '(python:funcname) → (python code);', style = 'CodeStyle.TLabel').grid(column = 0, row = 6, padx = 10, pady = 10, sticky = 'w')
	hpwin.text(master = ft, text = 'The lines of the Python code are separated by a \'↩\', not newlines.\nAlso remember to put the \'python:\' prefix before the name of the function.\nTo use PyCode commands in a Python function, use the prefix \'pycode:\' before the command, and put the command in curly brackets.\nThere cannot be any spaces between the \'pycode\' and the semicolon.\nPyCode commands used in a Python function should maintain proper indentation in the Python code.\nFor example, here is how to make a Python function named \'something\' that asks for 1+1 and shows \'correct\' or \'wrong\' for the answer in the Alt-X command box:').grid(column = 0, row = 7, padx = 10, pady = 10, sticky = 'w')
	hpwin.text(master = ft, text = "(python:something) →: (\nuseranswer = int(root.askstring('Question', 'What is 1+1?')) ↩\nif useranswer == 2: ↩\n    pycode:{show 'correct'} ↩\nelse: ↩\n    pycode:{show 'wrong'}\n);", style = 'CodeStyle.TLabel').grid(column = 0, row = 8, padx = 10, pady = 10, sticky = 'w')
	hpwin.text(master = st, text = 'Startup Code runs automatically every time PyNotes starts.\nThis can be used to execute some commands everytime on startup or configure PyNotes in some way.\nEverything that is inside a \'| |\' is executed as startup code.\nTo run multiple commands on startup, you can use a Function,\nhave multiple \'| |\'s, or separate the commands inside one\n\'| |\' with \'↩\'.\nFor example, these are all the ways you can make PyNotes start with an empty editor instead of the Zen of Python in Python HMode:').grid(column = 0, row = 0, padx = 10, pady = 10, sticky = 'w')
	hpwin.text(master = st, text = '(startup) →: (newfile ↩ hmode \'py\');\n|startup|;', style = 'CodeStyle.TLabel').grid(column = 0, row = 1, padx = 10, pady = 10, sticky = 'w')
	hpwin.text(master = st, text = '|newfile|;\n|hmode \'py\'|;', style = 'CodeStyle.TLabel').grid(column = 0, row = 2, padx = 10, pady = 10, sticky = 'w')
	hpwin.text(master = st, text = '|newfile ↩ hmode \'py\'|;', style = 'CodeStyle.TLabel').grid(column = 0, row = 3, padx = 10, pady = 10, sticky = 'w')
	hpwin.text(master = act, text = 'You can make or change Alt-X commands in PyCode.\nPyCode commands inside the Alt-X command definition are separated by a \'↩\'. The syntax is:').grid(column = 0, row = 0, padx = 10, pady = 10, sticky = 'w')
	hpwin.text(master = act, text = '⌊cmdname⌋ → ⌊commands⌋;', style = 'CodeStyle.TLabel').grid(column = 0, row = 1, padx = 10, pady = 10, sticky = 'w')
	hpwin.text(master = act, text = 'For example, here is how to make an Alt-X command named \'tktemplate\' which writes code in the editor that\nopens a window using easytk with the title and text \'PyCode Easytk Window Template\':').grid(column = 0, row = 2, padx = 10, pady = 10, sticky = 'w')
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
ttf = root.frame()
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
lf.pack(padx = 10, pady = 10, side = 'top', fill = 'x')
for widget in lf.winfo_children()[1:]:
	widget.config(state = 'disabled')
tabs.add(mf, text = 'Editor')
tabs.add(sf, text = 'Python Shell', state = 'hidden')
tabs.add(ef, text = 'Email', state = 'hidden')
fileinfo = root.frame()
cmdlabel = root.text()
cmdlabel.pack(side = 'left', padx = 10, pady = 10, anchor = 'n')
cmdentry = root.textbox(state = 'disabled', height = 1)
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
	webbrowser.open('https://github.com/rafugafu/PyNotes/tree/main/Plugins')
def op():
	pp = f'{homedir}/.local/share/PyNotes/add-ons'
	if platform.system() == 'Linux':
		os.system(f'xdg-open {pp}')
	else:
		os.startfile(pp)
def ap():
	apw = root.subwin()
	apw.title('Add Plugins')
	apw.text(text = f'1. Download a plugin\n2. Extract the plugin if it is a zip\n3. Move the folder to {homedir}/.local/share/PyNotes/add-ons\n4. Restart PyNotes').grid(column = 0, row = 0, padx = 10, pady = 10, sticky = 'w')
	apw.button(text = 'Download From PyNotes\' GitHub', command = dp).grid(column = 0, row = 1, padx = 10, pady = 10, sticky = 'w')
	apw.button(text = 'Open Plugins Directory', command = op).grid(column = 0, row = 2, padx = 10, pady = 10, sticky  = 'w')
	apw.text(text = 'Warning: Plugins have full access to PyNotes and your system\nand can run any commands. Be careful in downloading and using\nplugins from other websites.', font = (monospace, 12, 'bold')).grid(column = 0, row = 3, padx = 10, pady = 10, sticky = 'w')
	apw.style(root.gettheme())
	apw.focus()
def helpmathgod():
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
m.add_cascade(label = 'Python', menu = pm, state = 'disabled')
m.add_cascade(label = 'LaTeX', menu = lm, state = 'disabled')
m.add_cascade(label = 'PyCode', menu = pcm)
m.add_cascade(label = 'MathGod', menu = mg)
m.add_cascade(label = 'Plugins', menu = plgnm)
plgnm.add_command(label = 'Download From PyNotes\' GitHub', command = dp)
plgnm.add_command(label = 'Open Plugins Directory', command = op)
plgnm.add_separator()
plgnm.add_command(label = 'Help with Adding Plugins', command = ap)
pm.add_command(label = 'Run → F5', command = rp)
lm.add_command(label = 'Run LuaLaTeX → F5', command = lambda: runtex('lua'))
root.bind('<F5>', f5)
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
root.bind('<Control-n>', nw)
fm.add_command(label = 'Open → Ctrl + O / Alt + X - o', command = llld)
root.bind('<Control-o>', llld)
fm.add_separator()
fm.add_command(label = 'Save → Ctrl + S / Alt + X - s', command = sssv)
root.bind('<Control-s>', sssv)
fm.add_command(label = 'Save as → Ctrl + Shift + S / Alt + X - sa', command = ssv)
root.bind('<Control-S>', ssv)
fm.add_separator()
fm.add_command(label = 'Quit → Ctrl + W / Alt + X - e', command = ext)
root.bind('<Control-w>', ext)
pcm.add_command(label = 'Start', command = pc)
pcm.add_separator()
pcm.add_command(label = 'Help', command = helppycode)
om.add_command(label = 'Preferences → Ctrl + P / Alt + X - prf', command = prf)
om.add_command(label = 'Source Code → Alt + X - source-code', command = ss)
om.add_separator()
om.add_command(label = 'Go to line → Alt + L / Alt + X - gl', command = gl)
root.bind('<Alt-l>', gl)
om.add_command(label = 'Page turn → Ctrl + P / Alt + X - pf', command = ptf)
root.bind('<Control-p>', ptf)
om.add_command(label = 'Page turn (back) → Ctrl + Shift + P / Alt + X - pb', command = ptb)
root.bind('<Control-P>', ptb)
om.add_separator()
om.add_command(label = 'Command → Alt + X', command = cmd)
om.add_command(label = 'PyCode → Alt + X - pc', command = pc)
om.add_separator()
om.add_command(label = 'Speech to Text → Alt + X - st', command = st)
em.add_separator()
em.add_command(label = 'Find → Ctrl + F / Alt + X - f', command = f)
root.bind('<Control-f>', f)
em.add_command(label = 'Find & Replace → Ctrl + Shift + F / Alt + X - fr', command = fr)
root.bind('<Control-F>', fr)
readonlytextforshellpy = '>>> '
readonlyendforshellpy = '1.' + str(len('>>> '))
continuation = False
continuationcodeforshellpy = ''
_hapyshell_running = [False]
_hapyshell_pending = [False]
def hapyshell():
	if _hapyshell_running[0]:
		_hapyshell_pending[0] = True
		return
	_hapyshell_running[0] = True
	lenprompt = len('>>> ')
	text = shellcmd.get('1.0', 'end')
	dvars_local = list(dict.fromkeys(m.group(1) for m in re.finditer(r'^\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*=', text, re.MULTILINE)))
	dfuncs_local = list(dict.fromkeys(m.group(1) for m in re.finditer(r'^\s*def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', text, re.MULTILINE)))
	_SKIP_SHELL = frozenset({'sel', 'prompt'})
	syntax_tags = ('hpv', 'hpf', 'hpo', 'hpa', 'hpb', 'hpc', 'hpd')
	def do_hl():
		ops = []
		try:
			for tag in syntax_tags:
				ops.append(('remove', tag))
			for m in _KW_PAT.finditer(text):
				ops.append(('add', 'hpa', f'1.0+{m.start()}c', f'1.0+{m.end()}c'))
			ops.append(('config', 'hpa', theme['python:keywords'].replace('type_', 'shellcmd')))
			for m in _BI_PAT.finditer(text):
				ops.append(('add', 'hpb', f'1.0+{m.start()}c', f'1.0+{m.end()}c'))
			ops.append(('config', 'hpb', theme['python:inbuilt'].replace('type_', 'shellcmd')))
			if dvars_local:
				vpat = re.compile(r'\b(?:' + '|'.join(re.escape(v) for v in dvars_local) + r')\b')
				for m in vpat.finditer(text):
					ops.append(('add', 'hpv', f'1.0+{m.start()}c', f'1.0+{m.end()}c'))
			ops.append(('config', 'hpv', theme['python:variable_names'].replace('type_', 'shellcmd')))
			if dfuncs_local:
				fpat = re.compile(r'\b(?:' + '|'.join(re.escape(v) for v in dfuncs_local) + r')\b')
				for m in fpat.finditer(text):
					ops.append(('add', 'hpf', f'1.0+{m.start()}c', f'1.0+{m.end()}c'))
			ops.append(('config', 'hpf', theme['python:function_names'].replace('type_', 'shellcmd')))
			for m in _OP_PAT.finditer(text):
				last_nl = text.rfind('\n', 0, m.start())
				col = m.start() - last_nl - 1
				if col not in {0, 1, 2}:
					s = f'1.0+{m.start()}c'
					e = f'1.0+{m.end()}c'
					ops.append(('clear_shell', s, e))
					ops.append(('add', 'hpo', s, e))
			ops.append(('config', 'hpo', theme['python:operators'].replace('type_', 'shellcmd')))
			n = len(text)
			i = 0
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
					ops.append(('clear_shell', f'1.0+{i}c', f'1.0+{j}c'))
					ops.append(('add', 'hpd', f'1.0+{i}c', f'1.0+{j}c'))
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
					ops.append(('clear_shell', f'1.0+{i}c', f'1.0+{j}c'))
					ops.append(('add', 'hpd', f'1.0+{i}c', f'1.0+{j}c'))
					i = j
				elif ch == '#':
					j = i + 1
					while j < n and text[j] != '\n':
						j += 1
					if j < n:
						j += 1
					ops.append(('clear_shell', f'1.0+{i}c', f'1.0+{j}c'))
					ops.append(('add', 'hpc', f'1.0+{i}c', f'1.0+{j}c'))
					i = j
				else:
					i += 1
			ops.append(('config', 'hpd', theme['python:strings'].replace('type_', 'shellcmd')))
			ops.append(('config', 'hpc', theme['python:comments'].replace('type_', 'shellcmd')))
			lines_list = text.split('\n')
			pos = 0
			for line in lines_list:
				line_end = pos + len(line)
				prefix = line[:lenprompt]
				if prefix in {'>>> ', '... '}:
					ops.append(('strip_prompts', f'1.0+{pos}c', f'1.0+{pos + lenprompt}c'))
				else:
					ops.append(('strip_prompts', f'1.0+{pos}c', f'1.0+{line_end}c'))
				pos = line_end + 1
		except Exception:
			pass
		shellcmd.after(0, lambda: _finish_hapyshell(ops))
	def _finish_hapyshell(ops):
		try:
			if shellcmd.get('1.0', 'end') == text:
				all_tags = set(shellcmd.tag_names())
				for op in ops:
					if op[0] == 'remove':
						shellcmd.tag_remove(op[1], '1.0', 'end')
					elif op[0] == 'add':
						shellcmd.tag_add(op[1], op[2], op[3])
					elif op[0] == 'config':
						exec("shellcmd.tag_config('" + op[1] + "'," + op[2] + ')')
					elif op[0] == 'clear_shell':
						for tag in all_tags:
							if tag in _SKIP_SHELL:
								continue
							shellcmd.tag_remove(tag, op[1], op[2])
					elif op[0] == 'strip_prompts':
						for tag in syntax_tags:
							shellcmd.tag_remove(tag, op[1], op[2])
		except Exception:
			pass
		_hapyshell_running[0] = False
		if _hapyshell_pending[0]:
			_hapyshell_pending[0] = False
			hapyshell()
	threading.Thread(target = do_hl, daemon = True).start()
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
	_h_offset = [0]
	_pending_remap = [False]
	_needs_calibration = [False]
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
		prev_was_H1[0] = False
		shellcmd.mark_set('insert', f'{_cursor_line[0]}.{_cursor_col[0]}')
		i = 0
		n = len(text)
		while i < n:
			ch = text[i]
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
				ln = _cursor_line[0]
				if shellcmd.compare(f'{ln}.0', '<', 'end'):
					shellcmd.mark_set('insert', f'{ln}.0')
				else:
					shellcmd.mark_set('insert', f'{ln - 1}.end')
					shellcmd.insert('insert', '\n')
					shellcmd.mark_set('insert', f'{ln}.0')
				i += 1
			elif ch == '\x1b':
				rest = text[i:]
				if len(rest) < 2:
					i += 1
					continue
				nxt = rest[1]
				if nxt == '[':
					m = re.match(r'\x1b\[([0-9;?]*)([A-Za-z@`])', rest)
					if m:
						ps = m.group(1).lstrip('?')
						cmd = m.group(2)
						p = [int(x) if x else 0 for x in ps.split(';')] if ps else [0]
						ln = _cursor_line[0]
						col = _cursor_col[0]
						if cmd == 'K':
							if p[0] == 0: shellcmd.delete(f'{ln}.{col}', f'{ln}.end')
							elif p[0] == 1: shellcmd.delete(f'{ln}.0', f'{ln}.{col}')
							else: shellcmd.delete(f'{ln}.0', f'{ln}.end')
						elif cmd == 'J':
							if p[0] == 2:
								if prev_was_H1[0]:
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
							if _needs_calibration[0]:
								_needs_calibration[0] = False
								_h_offset[0] = _cursor_line[0] - (screen_top[0] + row_ - 1)
							if _pending_remap[0]:
								_pending_remap[0] = False
								_h_offset[0] = 1 - (screen_top[0] + row_ - 1)
								target_line = 1
							else:
								target_line = screen_top[0] + row_ - 1 + _h_offset[0]
							target_line = max(1, target_line)
							_cursor_line[0] = target_line
							_cursor_col[0] = col_ - 1
							last_line = int(shellcmd.index('end').split('.')[0]) - 1
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
							shellcmd.mark_set('insert', f'{_cursor_line[0]}.{_cursor_col[0]}')
						elif cmd == 'D':
							mv = p[0] or 1
							_cursor_col[0] = max(0, _cursor_col[0] - mv)
							shellcmd.mark_set('insert', f'{_cursor_line[0]}.{_cursor_col[0]}')
						elif cmd == 'G':
							mv = p[0] or 1
							_cursor_col[0] = mv - 1
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
								try:
									_write_ref[0](f'\x1b[{_cursor_line[0]};{_cursor_col[0]+1}R'.encode())
								except Exception:
									pass
						prev_was_H1[0] = cmd in ('H', 'f') and (p[0] if p[0] else 1) == 1
						i += len(m.group(0))
					else:
						i += 2
				elif nxt == ']':
					end_osc = rest.find('\x07', 2)
					if end_osc >= 0: i += end_osc + 1
					else:
						st = rest.find('\x1b\\', 2)
						i += st + 2 if st >= 0 else len(rest)
				elif nxt == 'M':
					_cursor_line[0] = max(1, _cursor_line[0] - 1)
					shellcmd.mark_set('insert', f'{_cursor_line[0]}.{_cursor_col[0]}')
					i += 2
				elif nxt == 'D':
					_cursor_line[0] += 1
					shellcmd.mark_set('insert', f'{_cursor_line[0]}.{_cursor_col[0]}')
					i += 2
				elif nxt in '()':
					i += 3 if len(rest) >= 3 else 2
				else:
					i += 2
			elif ch >= ' ' and ch != '\x7f':
				cur = shellcmd.get(f'{_cursor_line[0]}.{_cursor_col[0]}', f'{_cursor_line[0]}.{_cursor_col[0] + 1}')
				if cur and cur != '\n':
					shellcmd.delete(f'{_cursor_line[0]}.{_cursor_col[0]}', f'{_cursor_line[0]}.{_cursor_col[0] + 1}')
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
		try:
			while True:
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
				shellcmd.see('insert')
				had_output = True
		except _queue.Empty:
			pass
		if running[0] and gen == generation[0]:
			if had_output:
				_schedule_hl()
			shellcmd.after(50, lambda: _poll(gen))
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
			proc = subprocess.Popen([pythonexecutable, '-u', '-i'], stdin = slave_fd, stdout = slave_fd, stderr = slave_fd, close_fds = True, preexec_fn = os.setsid, env = env)
			os.close(slave_fd)
			_proc_ref[0] = proc
			_mfd_ref[0] = master_fd
			def _read():
				while running[0] and gen == generation[0]:
					try:
						r, _, _ = _select.select([master_fd], [], [], 0.05)
						if r:
							data = os.read(master_fd, 4096)
							if data:
								out_q.put((gen, data.decode('utf-8', errors = 'replace')))
						elif proc.poll() is not None:
							break
					except OSError:
						break
				out_q.put((gen, None))
			def _write(data):
				os.write(master_fd, data)
		else:
			proc = PtyProcess.spawn(pythonexecutable + ' -u -i', dimensions = (999999, 800))
			_proc_ref[0] = proc
			def _read():
				while running[0] and gen == generation[0]:
					try:
						data = proc.read(4096)
						if data:
							out_q.put((gen, data if isinstance(data, str) else data.decode('utf-8', errors = 'replace')))
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
		if platform.system() != 'Linux':
			_needs_calibration[0] = True
		threading.Thread(target = _read, daemon = True).start()
		shellcmd.after(50, lambda: _poll(gen))
	def _key(event):
		if not running[0]:
			return 'break'
		sym = event.keysym
		ch = event.char
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
	def _snap_cursor():
		shellcmd.mark_set('insert', cursor[0])
	def _click(_):
		shellcmd.focus_set()
		shellcmd.after_idle(_snap_cursor)
		return 'break'
	def cs():
		shellcmd.delete('1.0', 'end')
		cursor[0] = '1.0'
		screen_top[0] = 1
		prev_was_H1[0] = False
		_cursor_line[0] = 1
		_cursor_col[0] = 0
		shellcmd.focus()
		if platform.system() == 'Linux':
			try: _write_ref[0](b'\x0c')
			except Exception: pass
		else:
			_pending_remap[0] = True
			try: _write_ref[0](b'\r')
			except Exception: pass
	def ks():
		running[0] = False
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
		_cursor_line[0] = 1
		_cursor_col[0] = 0
		_h_offset[0] = 0
		_pending_remap[0] = False
		_needs_calibration[0] = False
		shellcmd.focus()
		_start()
	shellcmd = root.textbox(master = sf, font = (monospace, 12))
	clearshell = root.button(master = sf, text = 'Clear Shell', command = cs)
	killshell = root.button(master = sf, text = 'Restart Shell', command = ks)
	shellcmd.pack(fill = 'both')
	clearshell.pack(anchor = 'sw', side = 'left')
	killshell.pack(anchor = 'sw', side = 'left')
	shellcmd.bind('<Key>', _key)
	shellcmd.bind('<Button-1>', _click)
	shellcmd.bind('<ButtonRelease-1>', lambda _: 'break')
	shellcmd.bind('<B1-Motion>', lambda _: 'break')
	shellcmd.bind('<Button-2>', lambda _: 'break')
	_start()
shellpy()
def mathgod():
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
			fn = subprocess.run(['zenity', '--file-selection', '--filename=./', '--title=Open File', '--file-filter=All Files | *.*'], capture_output = True, text = True).stdout.strip()
		else:
			fn = fd.askopenfilename(title = 'Open File', filetypes = (('All Files', '*.*')))
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
	def sendemail(event = None):
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
		emailtextbox.tag_config('wrong', underline = True, underlinefg = 'red')
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
	emailtextbox.pack(fill = 'both', expand = True, padx = 10, pady = 10)
	emailtextbox.bind('<Control-Return>', sendemail)
	emailtextbox.bind('<KeyRelease>', lambda event: spellcheck() if emailwordlist else None)
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
	emailsetup('saved')
root.bind('<Alt-x>', cmd)
type_.bind('<Control-a>', selall)
type_.bind('<Control-c>', cp)
type_.bind('<Control-v>', pst)
type_.bind('<Control-x>', cut)
om.add_command(label = 'Terminal → Alt + X - t', command = term)
om.add_separator()
om.add_command(label = 'Speak Text → Alt + X - sp', command = spk)
type_.bind('<KeyRelease>', keypress)
type_.bind('<BackSpace>', lambda event: show('delete text'))
type_.bind('<Delete>', lambda event: show('delete text'))
root.protocol('WM_DELETE_WINDOW', ext)
mg.add_command(label = 'Start', command = mathgod)
mg.add_separator()
mg.add_command(label = 'Help', command = helpmathgod)
wholenewwords = list()
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
root.style(defs[3])
type_.edit_reset()
type_.bind('<Return>', lambda event: indent())
for code in last:
	try:
		exec(code[1])
	except Exception as error:
		root.error('Error!', f'There was an error in the last part of the plugin "{os.path.basename(os.path.normpath(code[0]))}":\n{error}')
if len(sys.argv) > 1:
	ld(sys.argv[1])
	if len(sys.argv) > 2:
		for file in sys.argv[2:]:
			subprocess.Popen(sys.executable + ' ' + sys.argv[0] + ' ' + file, shell = True)
if new:
	prf()
root.show()