import os
import sys
import platform
import getpass
import subprocess
import time
import state
from init import homedir, monospace
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
