import os
import sys
import platform
import subprocess
import webbrowser
import state
from init import homedir, rootdir, monospace
def bindrecur(widget, event, func, break_ = True, *args, **kwargs):
	if break_:
		f = lambda *args, **kwargs: func(*args, **kwargs) or 'break'
	else:
		f = func
	widget.bind(event, lambda event, f = f: f(event), *args, **kwargs)
	for child in widget.winfo_children():
		bindrecur(child, event, func, break_, *args, **kwargs)
def unbindrecur(widget, *args, **kwargs):
	widget.unbind(*args, **kwargs)
	for child in widget.winfo_children():
		unbindrecur(child, *args, **kwargs)
def bindtype_(buffer, event, func, break_ = True, *args, **kwargs):
	import editor
	if break_:
		f = lambda *args, **kwargs: func(*args, **kwargs) or 'break'
	else:
		f = func
	if isinstance(buffer, editor.Editor):
		buffer._own_type.bind(event, lambda event, f = f: f(event), *args, **kwargs)
def unbindtype_(buffer, *args, **kwargs):
	if isinstance(buffer, editor.Editor):
		buffer._own_type.unbind(*args, **kwargs)
def load_themes():
	themesdir = f'{homedir}/.local/share/PyNotes/themes'
	for file in os.listdir(themesdir):
		try:
			state.root.import_theme(f'{themesdir}/{file}')
		except Exception:
			pass
def show(text):
	state.prompting = False
	state.cmdentry.config(state = 'normal')
	state.cmdentry.delete('1.0', 'end')
	state.cmdentry.insert('end', text.replace('\n', '\\n'))
	state.cmdentry.unbind('<KeyPress>')
	state.cmdentry.unbind('<Return>')
	state.cmdentry.unbind('<Escape>')
	state.cmdentry.config(state = 'disabled')
	state.cmdautocomplete.pack_forget()
def prompt(text, autocompletefunc = None, defaultinput = None):
	def check_edit(event, text, promptend):
		state.cmdentry.delete('1.0', promptend)
		state.cmdentry.insert('1.0', text)
		state.cmdentry.tag_add('prompt', '1.0', promptend)
		state.cmdentry.mark_set('insert', '1.end')
		state.cmdautocomplete.pack_forget()
		if event.keysym == 'BackSpace' and state.cmdentry.compare('insert', '==', promptend):
			return 'break'
	def setreturninput(promptend):
		nonlocal inputtext
		inputtext = state.cmdentry.get(promptend, '1.end')
		state.prompting = False
	def autocomplete(cmdentry, promptend, autocompletefunc):
		completes = []
		typedtext = cmdentry.get(promptend, '1.end')
		if callable(autocompletefunc):
			autocompletelist = sorted(autocompletefunc(typedtext))
		else:
			autocompletelist = sorted(autocompletefunc)
		for option in autocompletelist:
			if option.startswith(typedtext):
				completes.append(option)
		if (newcomplete := os.path.commonprefix(completes)[len(typedtext):]):
			cmdentry.insert('1.end', newcomplete)
		else:
			if not completes:
				completes.append('[no match]')
			state.cmdautocomplete.config(state = 'normal')
			state.cmdautocomplete.delete('1.0', 'end')
			state.cmdautocomplete.insert('1.0', '    '.join(completes))
			state.cmdautocomplete.pack(padx = 10, pady = 10, fill = 'x', anchor = 'n', after = cmdentry)
			state.cmdautocomplete.update_idletasks()
			displaylines = state.cmdautocomplete.count('1.0', 'end-1c', 'displaylines')
			state.cmdautocomplete.config(height = min(displaylines[0], 5) if displaylines else 1)
			state.cmdautocomplete.config(state = 'disabled')
	state.prompting = True
	inputtext = ''
	state.cmdentry.config(state = 'normal')
	state.cmdentry.delete('1.0', 'end')
	state.cmdentry.insert('1.0', text)
	promptend = state.cmdentry.index('1.end')
	state.cmdentry.tag_add('prompt', '1.0', promptend)
	state.cmdentry.tag_config('prompt', font = (monospace, 12, 'bold'))
	if defaultinput:
		state.cmdentry.insert('end', defaultinput)
		state.cmdentry.mark_set('insert', 'end')
	state.cmdentry.bind('<KeyPress>', lambda event, text = text, promptend = promptend: check_edit(event, text, promptend))
	state.cmdentry.bind('<Return>', lambda event, promptend = promptend: setreturninput(promptend))
	state.cmdentry.bind('<Escape>', lambda event: show(''))
	if autocompletefunc:
		state.cmdentry.bind('<Tab>', lambda event, cmdentry = state.cmdentry, promptend = promptend, autocompletefunc = autocompletefunc: autocomplete(cmdentry, promptend, autocompletefunc) or 'break')
	state.root.update()
	state.cmdentry.focus_set()
	while state.prompting:
		state.root.update()
	state.cmdentry.delete('1.0', 'end')
	state.cmdentry.unbind('<KeyPress>')
	state.cmdentry.unbind('<Return>')
	state.cmdentry.unbind('<Escape>')
	state.cmdentry.config(state = 'disabled')
	state.cmdautocomplete.pack_forget()
	state.active.mainwidget.focus_set()
	state.root.update()
	return inputtext
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
def mathgod():
	import pycode
	pycode.pcrunhook('before', 'open-mathgod')
	show('open mathgod')
	subprocess.Popen([sys.executable, f'{rootdir}/MathGod.py'])
	pycode.pcrunhook('after', 'open-mathgod')
class ErrorHandler:
	def __init__(self):
		self.win = None
		self.textbox = None
	def write(self, error):
		try:
			if error.strip():
				def _do_write(error = error):
					if self.win == None or not self.win.exists:
						self.win = state.root.subwin()
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
						self.win.style(state.root.gettheme())
						self.win.update()
						self.win.sizablefalse()
					else:
						self.textbox.config(state = 'normal')
						self.textbox.insert('end', f'\n{error}')
						self.textbox.see('end')
						self.textbox.config(state = 'disabled')
				state.root.after(0, _do_write)
		except Exception:
			print(error)
	def flush(self):
		pass
def _report_callback_exception(exc, val, tb):
	import easytk
	if issubclass(exc, easytk.tk.TclError):
		return
	easytk.tk.Tk.report_callback_exception(state.root, exc, val, tb)
