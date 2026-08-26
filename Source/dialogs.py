import os
import sys
import platform
import getpass
import subprocess
import time
import state
from init import v, homedir, monospace
import utils
def faketerm(command):
	import easytk
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
def openfileget(filetypes = (('All Files', '*'),), prompttext = 'Open File: ', initialfile = None):
	if not state.nographicalfiledialogs:
		if platform.system() == 'Linux':
			fn = subprocess.run(['zenity', '--file-selection', f'--filename={initialfile or "./"}', '--title=Open File'] + [f'--file-filter={ft[0]} | {ft[1]}' for ft in filetypes], capture_output = True, text = True).stdout.strip()
		else:
			import easytk
			initialdir = os.path.dirname(initialfile)
			initialfile = os.path.basename(initialfile)
			fn = easytk.fd.askopenfilename(title = 'Open File', filetypes = filetypes, initialfile = initialfile or '', initialdir = initialdir or '')
	else:
		fn = utils.prompt(prompttext, fileautocompletefunc, initialfile)
	if not fn.strip():
		return ''
	fn = os.path.abspath(os.path.expanduser(fn))
	if not os.path.exists(fn):
		utils.show(f'error: \'{fn}\' does not exist')
		return None
	if os.path.isdir(fn):
		utils.show(f'error: \'{fn}\' is a directory')
		return None
	return fn
def saveasfileget(prompttext = 'Save File: ', initialfile = None):
	if not state.nographicalfiledialogs:
		if platform.system() == 'Linux':
			fn = subprocess.run(['zenity', '--file-selection', f'--filename={initialfile or "./"}', '--save', '--confirm-overwrite', '--title=Save As', '--file-filter=All Files | *'], capture_output = True, text = True).stdout.strip()
		else:
			import easytk
			initialdir = os.path.dirname(initialfile)
			initialfile = os.path.basename(initialfile)
			fn = easytk.fd.asksaveasfilename(initialfile = initialfile or '', initialdir = initialdir or '')
		if not fn.strip():
			return ''
	else:
		while True:
			fn = utils.prompt(prompttext, fileautocompletefunc, initialfile)
			if not fn.strip():
				return ''
			fn = os.path.abspath(os.path.expanduser(fn))
			if os.path.isdir(fn):
				utils.show(f'error: \'{fn}\' is an already existing directory')
				return None
			if os.path.exists(fn):
				overwrite = utils.prompt('File already exists. Overwrite (y/yes) or no (other): ', ('y', 'yes', 'n', 'no'))
				if overwrite.strip().lower() in ('y', 'yes'):
					break
				initialfile = fn
			else:
				break
	return fn
def svprf():
	global colours
	import editor
	file = open(f'{homedir}/.local/share/PyNotes/defs', 'w+', encoding = 'utf-8')
	font = state.defs[2]
	state.theme = colours.get('1.0', 'end-1c').replace('\n', '').replace('orgfont', 'type_.cget(\'font\')[:-3].strip(\'{}\')')
	file.write(f'{v}\n{str(state.bfr)}\n{font}\n{state.root.gettheme()}\n{",".join(state.dicts)}\n{state.emacskeysforsearch}\n{state.taborspace}\n{state.nographicalfiledialogs}\n{state.pythonexecutable}\n{state.theme}')
	file.close()
	exec('theme = {' + state.theme + '}', vars(state))
	editor._init_hl_tags()
	editor._init_pythonshell_hl_tags()
	editor._init_plugin_tags()
	for buffer in state.all_buffers:
		if hasattr(buffer, 'keypress'):
			buffer.keypress()
def prf():
	global colours
	import editor
	import pycode
	pycode.pcrunhook('before', 'open-preferences')
	utils.show('open preferences')
	def removedict():
		try:
			state.dicts.remove(dictlist.selection_get())
		except Exception:
			pass
		else:
			dictlist.delete(dictlist.curselection())
		state.emailwordlist.clear()
		try:
			for dictionary in state.dicts:
				if dictionary:
					state.emailwordlist.extend(open(dictionary, 'r', encoding = 'utf-8').read().split('\n'))
		except Exception as error:
			error = str(error)
			state.root.error('Error', error)
	def setts(val):
		state.taborspace = val
	def setffre(val):
		state.emacskeysforsearch = val
	def setnoguifd(val):
		state.nographicalfiledialogs = val
	def bf(opt):
		state.bfr = opt
	def adddict():
		dicttoadd = openfileget(prompttext = 'Email Dictionary File: ', filetypes = (('Text Files', '*.txt')))
		if dicttoadd:
			state.dicts.append(dicttoadd)
			dictlist.insert('end', dicttoadd)
			state.emailwordlist.clear()
			try:
				for dictionary in state.dicts:
					if dictionary:
						state.emailwordlist.extend(open(dictionary, 'r', encoding = 'utf-8').read().split('\n'))
			except Exception as error:
				error = str(error)
				state.root.error('Error', error)
	def changepyexec():
		nonlocal pyexecshowtext
		fn = openfileget(prompttext = 'New Python Executable: ', filetypes = (('All Files', '*')))
		if fn:
			state.pythonexecutable = fn
			pyexecshowtext.config(text = f'Python interpreter: \'{state.pythonexecutable}\'')
	def makeowntheme():
		pr.info('Info', f'Click Save after you\'re done. You can edit the theme later at any time. To import and use it in PyNotes, save the resulting file to {homedir}/.local/share/PyNotes/themes/.')
		ttkcreator = subprocess.Popen([sys.executable, '-m', 'ttkcreator'], stdout = subprocess.DEVNULL, stderr = subprocess.PIPE)
		ttkcreatorerrorhandler = utils.ErrorHandler()
		for error in ttkcreator.stderr:
			ttkcreatorerrorhandler.write(error)
			ttkcreator.terminate()
		utils.load_themes()
		current = sts.get()
		themes = sorted(state.root.themes())
		sts['values'] = themes
		if current in themes:
			sts.set(current)
		elif themes:
			sts.set(themes[0])
		(lambda: [pr.sizabletrue(), pr.style(sts.get()), state.root.style(sts.get()), pr.sizablefalse()])()
	pr = state.root.subwin()
	pr.title('Preferences')
	tabs = pr.tabs()
	gt = pr.frame()
	tft = pr.frame()
	et = pr.frame()
	tabs.add(gt, text = 'General')
	bfc = pr.booleanvar(value = state.bfr)
	pr.check(master = gt, text = 'Backup file regularly', command = lambda: bf(bfc.get()), var = bfc).grid(column = 0, row = 0, sticky = 'w')
	varts = pr.booleanvar(value = state.taborspace)
	pr.check(master = gt, text = 'Use spaces instead of tabs for indentation commands', command = lambda: setts(varts.get()), var = varts).grid(column = 0, row = 1, sticky = 'w')
	varffre = pr.booleanvar(value = state.emacskeysforsearch)
	pr.check(master = gt, text = 'Use Emacs-like keybindings for the Find and Find & Replace', command = lambda: setffre(varffre.get()), var = varffre).grid(column = 0, row = 2, sticky = 'w')
	pr.text(master = gt, text = 'Emacs-like keys:\nFind keys:\nControl-R for previous match\nControl-S for next match\nEnter to close search\nFind & Replace keys:\n^ for previous\nAlt-Enter for next\nControl-T for replace and next\nEnter to close search').grid(column = 0, row = 3, sticky = 'w')
	varnoguifd = pr.booleanvar(value = state.nographicalfiledialogs)
	pr.check(master = gt, text = 'File prompts in the Alt-X command box (minibuffer) instead of a graphical file dialogue', command = lambda: setnoguifd(varnoguifd.get()), var = varnoguifd).grid(column = 0, row = 4, sticky = 'w')
	pr.frame(master = gt, height = 20).grid(column = 0, row = 4, sticky = 'w')
	pyexecshowtext = pr.text(master = gt, text = f'Python interpreter: \'{state.pythonexecutable}\'')
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
	sts = pr.droptype(options = tuple(sorted(state.root.themes())), command = lambda: [pr.sizabletrue(), pr.style(sts.get()), state.root.style(sts.get()), pr.sizablefalse()], master = mf)
	sts.grid(column = 1, row = 0, padx = 10, pady = 10, sticky = 'ew')
	sts.insert('end', state.root.gettheme())
	sts.config(state = 'readonly')
	pr.button(master = mf, text = 'Make your own!', command = makeowntheme).grid(column = 2, row = 0, padx = 10, pady = 10, sticky = 'w')
	pr.text(text = 'Editor Font', master = mf).grid(column = 0, row = 1, padx = 10, pady = 10)
	showfont = pr.textbox(master = tft, font = (state.defs[2], 12), wrap = 'word', height = 5)
	showfont.insert('end', 'The quick brown fox jumped over the lazy dogs\nAaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz\n1234567890\n?.,<>;:\'"{}[]\\|\n!@#$%^&*()-_+=')
	showfont.grid(column = 0, row = 1)
	f = pr.droptype(options = [monospace] + sorted(pr.getfonts()), master = mf, command = lambda: [pr.sizabletrue(), [buffer.type_.config(font = (f.get(), 12)) for buffer in state.all_buffers if isinstance(buffer, editor.Editor)], showfont.config(font = (f.get(), 12)), state.defs.__setitem__(2, f.get()), pr.sizablefalse()])
	f.grid(column = 1, row = 1, padx = 10, pady = 10, sticky = 'ew')
	f.insert('end', state.defs[2])
	f.config(state = 'readonly')
	pr.text(master = tft, text = 'Colours:').grid(column = 0, row = 2, padx = 10, pady = 10)
	colours = pr.textbox(master = tft, font = monospace, wrap = 'word', height = 5)
	colours.insert('end', str(state.theme)[:-1][1:].replace('type_.cget(\'font\')[:-3].strip(\'{}\')', 'orgfont'))
	colours.grid(column = 0, row = 3)
	pr.bind('<Escape>', lambda event: [svprf(), utils.show('change / view preferences'), pr.destroy()])
	tabs.add(et, text = 'Email')
	pr.text(master = et, text = 'Dictionaries:').pack(padx = 10, pady = 10, side = 'top', anchor = 'n')
	dictlist = pr.listbox(master = et)
	for dictionary in state.dicts:
		dictlist.insert('end', dictionary)
	dictlist.pack(fill = 'both', expand = True, padx = 10, pady = 10, anchor = 'center')
	pr.button(master = et, text = 'Remove', command = removedict).pack(fill = 'x', expand = True, padx = 10, pady = 10, side = 'left', anchor = 'sw')
	pr.button(master = et, text = 'Add', command = adddict).pack(fill = 'x', expand = True, padx = 10, pady = 10, side = 'right', anchor = 'se')
	pr.button(text = 'OK', command = lambda: [svprf(), utils.show('change / view preferences'), pr.destroy()]).pack(side = 'bottom', fill = 'x', padx = 10, pady = 10)
	pr.protocol('WM_DELETE_WINDOW', lambda: [svprf(), utils.show('change / view preferences'), pr.destroy()])
	for code in state.plgnsprf:
		try:
			exec(code[1], vars(state))
		except Exception as error:
			error = str(error)
			state.root.error('Error!', f'There was an error in setting up the preferences of the plugin "{os.path.basename(os.path.normpath(code[0]))}":\n{error}')
	pr.sizablefalse()
	pr.style(state.root.gettheme())
	pr.focus()
	pycode.pcrunhook('after', 'open-preferences')
def pdf(title):
	if os.path.splitext(title)[1] == '.tex':
		pdf_ = os.path.splitext(title)[0]
	else:
		pdf_ = title
	pdf_ += '.pdf'
	if not os.path.exists(pdf_):
		if state.root.ask('Error', 'The pdf could not be shown, there might have been an error in your code.\nDo you want to see the log?', ('yes', 'no')):
			logwin = state.root.subwin()
			logwin.title(f'LaTeX log for {os.path.basename(title)}')
			logtextboxscroll = logwin.scroll()
			logtextbox = logwin.textbox(yscrollcommand = logtextboxscroll.set, font = (monospace, 12))
			try:
				logtextbox.insert('1.0', open(f'{os.path.splitext(title)[0]}.log', 'r', encoding = 'utf-8').read())
			except:
				state.root.error('Error!', f'The log was not found at "{os.path.splitext(title)[0]}.log".')
				logtextbox.insert('1.0', 'log not found')
			logtextbox.config(state = 'disabled')
			logtextboxscroll.config(command = logtextbox.yview)
			logtextboxscroll.pack(fill = 'y', side = 'right')
			logtextbox.pack(fill = 'both', expand = True, side = 'left')
			logwin.style(state.root.gettheme())
	elif platform.system() == 'Linux':
		subprocess.run(['xdg-open', pdf_], cwd = os.path.dirname(title))
	else:
		subprocess.run(['start', pdf_], cwd = os.path.dirname(title))
