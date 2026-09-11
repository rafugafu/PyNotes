import os
import sys
import shutil
import queue
import threading
import textwrap
import ttkbootstrap as ttk
import state
from init import homedir, rootdir, DEBOUNCE_TIME
import editor
import dialogs
import pycode
import utils
import easytk
_MSG_ICONS = {'info': ('info-circle-fill', 'info'), 'warning': ('exclamation-triangle-fill', 'warning'), 'error': ('x-circle-fill', 'danger')}
_MSG_ICON_SIZE = 30
_ASK_PRESETS = {('yes', 'no'): {'Yes': True, 'No': False, None: None}, ('ok', 'cancel'): {'OK': True, 'Cancel': False, None: None}, ('yes', 'no', 'cancel'): {'Yes': True, 'No': False, 'Cancel': None, None: None}, ('retry', 'cancel'): {'Retry': True, 'Cancel': False, None: None}}
_ASK_PRESET_LABELS = {('yes', 'no'): ['No', 'Yes'], ('ok', 'cancel'): ['Cancel', 'OK'], ('yes', 'no', 'cancel'): ['Cancel', 'No', 'Yes'], ('retry', 'cancel'): ['Cancel', 'Retry']}
class pynoteswindow(easytk.win):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
	def _build_message_dialog(self, kind, title, message, button_labels, default_label = None, alert = False):
		self.update_idletasks()
		top = ttk.Toplevel(transient = self, title = title or ' ', resizable = (False, False), minsize = (250, 15), window_type = 'dialog', iconify = True)
		top.withdraw()
		state_ = {'result': None}
		def press(label):
			state_['result'] = label
			top.after_idle(lambda: top.destroy() if top.winfo_exists() else None)
		def close_dialog():
			if top.winfo_exists():
				top.destroy()
		body = ttk.Frame(top, padding = (20, 20))
		if kind in _MSG_ICONS:
			name, color = _MSG_ICONS[kind]
			icon_img = ttk.Icon(name, _MSG_ICON_SIZE, color)
			ttk.Label(body, image = icon_img).pack(side = 'left', anchor = 'center', padx = (0, 5))
		msg_frame = ttk.Frame(body)
		for line in message.split('\n'):
			wrapped = '\n'.join(textwrap.wrap(line, width = 50))
			ttk.Label(msg_frame, text = wrapped).pack(pady = (0, 3), fill = 'x', anchor = 'n')
		msg_frame.pack(side = 'left', fill = 'x', expand = True, anchor = 'center')
		body.pack(fill = 'x', expand = True)
		buttonframe = ttk.Frame(top, padding = (5, 5))
		default_label = default_label or button_labels[-1]
		buttons = []
		initial_focus = None
		for label in reversed(button_labels):
			is_default = label == default_label
			btn = ttk.Button(buttonframe, bootstyle = 'primary' if is_default else 'default', text = label)
			btn.configure(command = lambda l = label: press(l))
			btn.pack(padx = 2, side = 'right')
			btn.lower()
			btn.bind('<Return>', lambda e, b = btn: b.invoke())
			btn.bind('<KP_Enter>', lambda e, b = btn: b.invoke())
			buttons.append(btn)
			if is_default:
				initial_focus = btn
		for i, btn in enumerate(buttons):
			if i > 0:
				btn.bind('<Right>', lambda e, b = buttons[i - 1]: b.focus_set())
			if i < len(buttons) - 1:
				btn.bind('<Left>', lambda e, b = buttons[i + 1]: b.focus_set())
		ttk.Separator(top).pack(fill = 'x')
		buttonframe.pack(side = 'bottom', fill = 'x', anchor = 's')
		top.bind('<Escape>', lambda e: close_dialog())
		top.protocol('WM_DELETE_WINDOW', close_dialog)
		top.update_idletasks()
		w, h = top.winfo_reqwidth(), top.winfo_reqheight()
		top.geometry(f'{w}x{h}')
		x = self.winfo_rootx() + (self.winfo_width() - w) // 2
		y = self.winfo_rooty() + (self.winfo_height() - h) // 2
		top.geometry(f'+{max(0, x)}+{max(0, y)}')
		top.deiconify()
		if alert:
			top.bell()
		initial_focus.focus_force()
		return top, state_
	def _build_query_dialog(self, title, prompt):
		self.update_idletasks()
		top = ttk.Toplevel(transient = self, title = title or ' ', resizable = (False, False), minsize = (250, 15), window_type = 'dialog', iconify = True)
		top.withdraw()
		state_ = {'result': None}
		body = ttk.Frame(top, padding = (20, 20))
		for line in prompt.split('\n'):
			wrapped = '\n'.join(textwrap.wrap(line, width = 65))
			ttk.Label(body, text = wrapped).pack(pady = (0, 5), fill = 'x', anchor = 'n')
		entry = ttk.Entry(body)
		entry.pack(pady = (0, 5), fill = 'x')
		body.pack(fill = 'x', expand = True)
		def submit(*_):
			state_['result'] = entry.get()
			if top.winfo_exists():
				top.destroy()
		def cancel(*_):
			if top.winfo_exists():
				top.destroy()
		entry.bind('<Return>', submit)
		entry.bind('<KP_Enter>', submit)
		entry.bind('<Escape>', cancel)
		top.bind('<Escape>', cancel)
		buttonframe = ttk.Frame(top, padding = (5, 10))
		submitbtn = ttk.Button(buttonframe, bootstyle = 'primary', text = 'Submit', command = submit)
		submitbtn.pack(padx = 2, side = 'right')
		submitbtn.lower()
		cancelbtn = ttk.Button(buttonframe, text = 'Cancel', command = cancel)
		cancelbtn.pack(padx = 2, side = 'right')
		cancelbtn.lower()
		ttk.Separator(top).pack(fill = 'x')
		buttonframe.pack(side = 'bottom', fill = 'x', anchor = 's')
		top.protocol('WM_DELETE_WINDOW', cancel)
		top.update_idletasks()
		w, h = top.winfo_reqwidth(), top.winfo_reqheight()
		top.geometry(f'{w}x{h}')
		x = self.winfo_rootx() + (self.winfo_width() - w) // 2
		y = self.winfo_rooty() + (self.winfo_height() - h) // 2
		top.geometry(f'+{max(0, x)}+{max(0, y)}')
		top.deiconify()
		entry.focus_force()
		return top, state_
	def _race_console(self, console_call, top, state_):
		cancel_event = threading.Event()
		resultq = queue.Queue()
		def worker():
			resultq.put(console_call(cancel_event))
		threading.Thread(target = worker, daemon = True).start()
		top.grab_set()
		def poll():
			try:
				value = resultq.get_nowait()
			except queue.Empty:
				if top.winfo_exists():
					top.after(50, poll)
				return
			state_['console_result'] = ('console', value)
			if top.winfo_exists():
				top.destroy()
		top.after(50, poll)
		top.wait_window()
		if 'console_result' in state_:
			return state_['console_result'][1]
		cancel_event.set()
		return state_['result']
	def _resolve_clicked(self, clicked, button_labels):
		if isinstance(clicked, int):
			return button_labels[clicked - 1] if 1 <= clicked <= len(button_labels) else None
		return clicked
	def ask(self, title, question, options):
		options_tuple = tuple(options)
		button_labels = _ASK_PRESET_LABELS.get(options_tuple, list(options))
		top, state_ = self._build_message_dialog(None, title, question, button_labels)
		console_call = lambda cancel_event: state.console.ask(title, question, button_labels, cancel_event = cancel_event)
		clicked = self._resolve_clicked(self._race_console(console_call, top, state_), button_labels)
		return _ASK_PRESETS[options_tuple].get(clicked, None) if options_tuple in _ASK_PRESETS else clicked
	def askstring(self, title, prompt):
		top, state_ = self._build_query_dialog(title, prompt)
		console_call = lambda cancel_event: state.console.prompt(title, prompt, cancel_event = cancel_event)
		return self._race_console(console_call, top, state_)
	def _notice_with_buttons(self, kind, title, message, buttons, alert):
		color = '43m' if kind == 'warning' else ('41m' if kind == 'error' else '100m')
		button_labels = list(buttons)
		top, state_ = self._build_message_dialog(kind, title, message, button_labels, alert = alert)
		console_call = lambda cancel_event: state.console.ask(title, message, button_labels, color = color, cancel_event = cancel_event)
		return self._resolve_clicked(self._race_console(console_call, top, state_), button_labels)
	def info(self, title, message, buttons = None, **kwargs):
		if buttons:
			return self._notice_with_buttons('info', title, message, buttons, alert = False)
		state.console.dialog(title, message)
		return super().info(title, message, **kwargs)
	def error(self, title, message, buttons = None, **kwargs):
		if buttons:
			return self._notice_with_buttons('error', title, message, buttons, alert = True)
		state.console.dialog(title, message, color = '41m')
		return super().error(title, message, **kwargs)
	def warning(self, title, message, buttons = None, **kwargs):
		if buttons:
			return self._notice_with_buttons('warning', title, message, buttons, alert = True)
		state.console.dialog(title, message, color = '43m')
		return super().warning(title, message, **kwargs)
def saveforclose():
	for buffer in state.all_buffers:
		if hasattr(buffer, 'saveforclose') and not buffer.saveforclose():
			return False
	return True
def find_open_editor(abspath):
	for buffer in state.all_buffers:
		if not isinstance(buffer, editor.Editor):
			continue
		if buffer.view_master is None and buffer.title == abspath and not buffer.hmode in ('png', 'pdf', 'epub'):
			return buffer
def setactive(newindex = None, force = False):
	if newindex is None:
		newindex = state.buffindex + 1
	if newindex == -1:
		newindex = len(state.all_buffers) - 1
	if newindex == len(state.all_buffers):
		newindex = 0
	if newindex == state.buffindex and not force:
		return
	if 0 <= state.buffindex < len(state.all_buffers):
		state.all_buffers[state.buffindex].active = False
	try:
		buffer = state.all_buffers[newindex]
	except Exception:
		return
	pycode.pcrunhook('before', 'switch-buffer', newindex)
	state.buffindex = newindex
	buffer.active = True
	state.active = buffer
	update_menus()
	state.root.update()
	buffer.mainwidget.focus_set()
	settitle()
	pycode.pcrunhook('after', 'switch-buffer', state.buffindex)
def update_menus():
	state.mainmenu.delete(0, 'end')
	lastentry = state.active.m.index('end')
	if lastentry is not None:
		for i in range(lastentry + 1):
			if state.active.m.type(i) == 'cascade':
				state.mainmenu.add_cascade(label = state.active.m.entrycget(i, 'label'), menu = state.root.nametowidget(state.active.m.entrycget(i, 'menu')))
def settitle():
	if state.active and not state.pcsettitle:
		state.root.title('PyNotes - ' + state.active.wanttitle)
def balance(orient = 'all'):
	if orient == 'all':
		balance('horizontal')
		balance('vertical')
		return
	if orient == 'horizontal':
		pw = state.horizontal
		tw = pw.winfo_width()
	else:
		pw = state.vertical
		tw = pw.winfo_height()
	panes = pw.panes()
	n = len(panes)
	if n > 1:
		step = tw // n
		for i in range(n - 1):
			pw.sashpos(i, (i + 1) * step)
def newbuffer(buffer, orient, *args, **kwargs):
	newbuff = buffer(state.root, *args, **kwargs)
	state.all_buffers.append(newbuff)
	pycode.pcrun(state.pycode_keybindings_cdt)
	if orient == 'horizontal':
		state.horizontal.add(newbuff)
		state.root.update()
		balance('horizontal')
	else:
		state.vertical.add(newbuff)
		state.root.update()
		balance('vertical')
	state.root.update()
	setactive(-1)
	return newbuff
def neweditor(file = None, orient = 'horizontal'):
	if file == True:
		fn = dialogs.openfileget((('All Files', '*'), ('Python Files', '*.py'), ('Text Files', '*.txt'), ('LaTeX Files', '*.tex'), ('PNG Images', '*.png'), ('PDF Files', '*.pdf'), ('ePub Files', '*.epub')))
		if fn:
			utils.show('open file')
			neweditor(fn, orient = orient)
		return
	if file and os.path.isdir(file):
		state.root.error('Error', f'"{os.path.basename(file)}" is a directory.')
		return
	hookevent = 'open-file-new-editor' if file else 'new-file-new-editor'
	pycode.pcrunhook('before', hookevent, file)
	match = find_open_editor(os.path.abspath(file)) if file else None
	newedit = newbuffer(editor.Editor, orient, file = None if match else file, view_master = match, padding = 10)
	pycode.pcrunhook('after', hookevent, file)
	return newedit
def _on_root_resize(event):
	if event.widget is not state.root:
		return
	size = (event.width, event.height)
	if size == state._last_root_size:
		return
	state._last_root_size = size
	if state._resize_after_id is not None:
		state.root.after_cancel(state._resize_after_id)
	state._resize_after_id = state.root.after(DEBOUNCE_TIME, _do_resize_balance)
def _do_resize_balance():
	state._resize_after_id = None
	if not state.root.winfo_exists():
		return
	pycode.pcrunhook('before', 'resize-window')
	balance()
	pycode.pcrunhook('after', 'resize-window')
def ext():
	if any(getattr(buffer, 'running', False) for buffer in state.all_buffers):
		answer = state.root.ask('Warning', 'Kill active process(es) and close?', options = ('ok', 'cancel'))
		if answer != True:
			return
	if any(isinstance(buffer, editor.Editor) and buffer._file_watch_prompt_pending for buffer in state.all_buffers):
		utils.show('select \'Discard Changes & Reload\' or \'Ignore\' external changes before closing the editor')
		return
	answer = state.root.ask('Warning', 'Do you want to save files before closing?', options = ('yes', 'no', 'cancel')) if any(getattr(buffer, 'unsaved', False) for buffer in state.all_buffers) else False
	if answer != None:
		if answer:
			if not saveforclose():
				return
		try:
			pycode.pcrunhook('before', 'exit-pynotes')
		except Exception:
			pass
		try:
			if os.path.exists(f'{homedir}/.local/share/PyNotes/tempfiles'):
				shutil.rmtree(f'{homedir}/.local/share/PyNotes/tempfiles')
		except Exception:
			pass
		sys.stderr = open(os.devnull, 'w')
		try:
			state.root.after_cancel(state.consoleqafter)
		except Exception:
			pass
		for buffer in state.all_buffers:
			try:
				if hasattr(buffer, '_cancel_all_after_ids'):
					buffer._cancel_all_after_ids()
			except Exception:
				pass
		for closer in list(state._open_terminal_closers):
			try:
				closer()
			except Exception:
				pass
		try:
			state.root.destroy()
		except Exception:
			pass
		for buffer in state.all_buffers:
			try:
				buffer.observer.stop()
			except Exception:
				pass
		try:
			pycode.pcrunhook('after', 'exit-pynotes')
		except Exception:
			pass
		try:
			import cli
			cli.unset_raw_mode()
			print('\n\x1b[H\x1b[2J', end = '', file = state.stdout)
		except Exception:
			pass
		os._exit(0)
def ss():
	pycode.pcrunhook('before', 'show-pynotes-source-code')
	utils.show('open pynotes source code')
	fn = dialogs.openfileget((('Python Files', '*.py'),), 'Open PyNotes Source Code File: ', rootdir + '/')
	if not fn:
		return
	neweditor(fn)
	pycode.pcrunhook('after', 'show-pynotes-source-code')
