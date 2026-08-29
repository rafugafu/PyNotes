import os
import sys
import shutil
import state
from init import homedir, rootdir
import editor
from buffer import DEBOUNCE_TIME, saveforclose
import dialogs
import pycode
import utils
def find_open_editor(abspath):
	for buffer in state.all_buffers:
		if not isinstance(buffer, editor.Editor):
			continue
		if buffer.view_master is None and buffer.title == abspath and not buffer.hmode in ('png', 'pdf', 'epub'):
			return buffer
def _promote_new_master(old_master):
	children = list(old_master.view_children)
	if not children:
		return
	new_master, rest = children[0], children[1:]
	carried_values = dict((name, value) for name, value in old_master.__dict__.items() if name not in editor.Editor._PER_PANE_ATTRS and name not in editor.Editor._TK_INTERNAL_ATTRS)
	new_master.view_master = None
	for name, value in carried_values.items():
		setattr(new_master, name, value)
	new_master._file_watch_prompt_pending = False
	new_master.view_children = rest
	for child in rest:
		child.view_master = new_master
	new_master.m = state.root.menu()
	for label, menu in state.all_editor_menus.items():
		new_master.m.add_cascade(label = label, menu = menu)
	for child in rest:
		child.m = new_master.m
	if new_master.hmode == 'python':
		new_master.sethmenu('python')
	elif new_master.hmode == 'latex':
		new_master.sethmenu('latex')
	if new_master.title:
		new_master.clt(new_master.title)
	if state.active is old_master:
		state.active = new_master
	return new_master
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
	state.mainmenu.delete(0, 'end')
	lastentry = buffer.m.index('end')
	if lastentry is not None:
		for i in range(lastentry + 1):
			if buffer.m.type(i) == 'cascade':
				state.mainmenu.add_cascade(label = buffer.m.entrycget(i, 'label'), menu = state.root.nametowidget(buffer.m.entrycget(i, 'menu')))
	state.active = buffer
	state.root.update()
	buffer.mainwidget.focus_set()
	settitle()
	pycode.pcrunhook('after', 'switch-buffer', state.buffindex)
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
		os._exit(0)
def ss():
	pycode.pcrunhook('before', 'show-pynotes-source-code')
	utils.show('open pynotes source code')
	fn = dialogs.openfileget((('Python Files', '*.py'),), 'Open PyNotes Source Code File: ', rootdir + '/')
	if not fn:
		return
	neweditor(fn)
	pycode.pcrunhook('after', 'show-pynotes-source-code')
