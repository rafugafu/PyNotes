import os
import platform
import re
import easytk
import state
from init import homedir, monospace
import editor
from utils import unbindrecur
import help
import terminal
import utils
import window
def pcprompt(text, autocompletefunc = None, defaultinput = None):
	return utils.prompt(text, vars(state)[autocompletefunc] if isinstance(autocompletefunc, str) else autocompletefunc, defaultinput)
def pcdone(nc):
	open(f'{homedir}/.pynotes', 'w+', encoding = 'utf-8').write(nc)
	pcread(nc)
def say(string):
	state.root.info('Print PyCode', string)
def pcrun(code):
	code = code.split('\n')
	for line in code:
		try:
			exec(line, vars(state))
		except easytk.tk.TclError:
			pass
		except Exception as error:
			error = str(error)
			state.root.error('Error', f'Error in running the translated PyCode line\n"{line}":\n{error}')
def pcexecaction(code):
	try:
		exec(code, vars(state))
	except easytk.tk.TclError:
		pass
	except Exception as error:
		error = str(error)
		state.root.error('Error', f'Error in running the translated PyCode line\n"{code}":\n{error}')
def pcopenhelp(thing):
	if thing == 'commands':
		utils.show('open alt-x commands help')
		help.hx()
	elif thing == 'email':
		utils.show('open email help')
		help.hemail()
	elif thing == 'pycode':
		utils.show('open pycode help')
		help.helppycode()
	elif thing == 'mathgod':
		utils.show('open mathgod help')
		help.helpmathgod()
	elif thing == 'plugins':
		utils.show('open plugin help')
		help.ap()
def pctermexec(command):
	utils.show('output: ' + terminal.termexec(command))
def pcrepeatx(command, n):
	import command as _command_module
	for i in range(n):
		_command_module.cmdrun(command)
def pcfullscreen():
	pcrunhook('before', 'fullscreen')
	state.root.update()
	state.root.attributes('-fullscreen', True)
	state.root.update()
	utils.show('fullscreen mode')
	pcrunhook('after', 'fullscreen')
def pcunfullscreen():
	pcrunhook('before', 'un-fullscreen')
	state.root.update()
	state.root.attributes('-fullscreen', False)
	state.root.update()
	utils.show('windowed mode')
	pcrunhook('after', 'un-fullscreen')
def pcmax():
	pcrunhook('before', 'maximize-window')
	state.root.update()
	if platform.system() == 'Linux':
		state.root.attributes('-zoomed', True)
	else:
		state.root.state('zoomed')
	state.root.update()
	utils.show('maximized window')
	pcrunhook('after', 'maximize-window')
def pcunmax():
	pcrunhook('before', 'unmaximize-window')
	state.root.update()
	if platform.system() == 'Linux':
		state.root.attributes('-zoomed', False)
	else:
		state.root.state('normal')
	state.root.update()
	utils.show('unmaximize window')
	pcrunhook('after', 'unmaximize-window')
def pcmin():
	pcrunhook('before', 'minimize-window')
	state.root.iconify()
	pcrunhook('after', 'minimize-window')
def pcrunhook(when, event, commandinput = None):
	try:
		state.root.update()
	except Exception:
		pass
	hooks = state.pcbeforehooks if when == 'before' else state.pcafterhooks
	for key in dict.fromkeys((event, event.split(':', 1)[0])):
		for code in hooks.get(key, []):
			try:
				vars(state)['commandinput'] = commandinput
				for line in code.split('\n'):
					exec(line, vars(state))
			except Exception as error:
				error = str(error)
				state.root.error('Error in PyCode', f'There was an error in running the \'{when}:{event}\' hook:\n{error}')
def pcask(askstring):
	return state.root.askstring('PyCode Input', askstring)
def pccopytext(text):
	state.root.clipboard_clear()
	state.root.clipboard_append(text)
	utils.show(f'copied \'{text}\'')
	state.root.update()
def pcgosettitle(title):
	state.root.title(title)
	utils.show(f'set window title to \'{title}\'')
	state.pcsettitle = True
def pcunsettitle():
	utils.show('unset window title')
	state.pcsettitle = False
	if getattr(state.active, 'title', False):
		state.root.title(('PyNotes - ' + os.path.basename(state.active.title)) if not getattr(state.active, 'unsaved', False) else 'PyNotes - ' + os.path.basename(state.active.title) + ' *')
	else:
		state.root.title('PyNotes - Untitled')
	if hasattr(state.active, 'keypress'):
		state.active.keypress()
def pckillexit():
	os._exit(0)
def pcsetvar(var, val):
	vars(state)[var] = val
def pcwhileloop(condfunc, bodyfunc):
	while condfunc():
		bodyfunc()
def pccolor(name, *args, **kwargs):
	theme_key = f'pccolor:{name}'
	state.theme[theme_key] = ', '.join([repr(arg) for arg in args] + [f'{kw} = {repr(val)}' for kw, val in kwargs.items()])
	state.plugin_hl[theme_key] = {name: (None, theme_key)}
	state._PYTHON_EDITOR_HL_SKIP_REMOVE_TAGS.add(name)
	for buffer in state.all_buffers:
		if isinstance(buffer, editor.Editor):
			buffer.type_.tag_config(name, *args, **kwargs)
def pcneweditfile(orient = 'horizontal'):
	window.neweditor(True, orient)
def pcclosebuff(n = None):
	if len(state.all_buffers) == 1:
		utils.show('cannot close only open buffer')
		return False
	if n is None:
		n = state.buffindex
	else:
		n = int(n)
	buffer = state.all_buffers[n]
	was_last_reference = (buffer.view_master is None and not buffer.view_children) if hasattr(buffer, 'view_master') and hasattr(buffer, 'view_children') else False
	if not buffer.close():
		return False
	pcrunhook('before', 'close-buffer')
	if str(buffer) in state.horizontal.panes():
		state.horizontal.remove(buffer)
		window.balance('horizontal')
	if str(buffer) in state.vertical.panes():
		state.vertical.remove(buffer)
		window.balance('vertical')
	if hasattr(buffer, '_cancel_all_after_ids'):
		buffer._cancel_all_after_ids()
	if was_last_reference:
		try:
			buffer.observer.stop()
			buffer.observer.join()
		except Exception:
			pass
	buffer.destroy()
	if not state.horizontal.panes():
		for pane_name in state.vertical.panes():
			if pane_name != str(state.horizontal):
				pane = state.vertical.nametowidget(pane_name)
				state.vertical.remove(pane)
				state.horizontal.add(pane)
				break
	state.all_buffers.remove(buffer)
	if n <= state.buffindex:
		window.setactive(state.buffindex - 1, force = True)
	utils.show('closed buffer')
	pcrunhook('after', 'close-buffer')
	return True
def pcsplitedit(n = None, orient = 'horizontal'):
	if n is None:
		n = state.buffindex
	else:
		n = int(n)
	buffer = state.all_buffers[n]
	if not isinstance(buffer, editor.Editor):
		utils.show('not an editor')
		return
	if buffer.title:
		window.neweditor(buffer.title, orient)
		utils.show('split editor horizontally' if orient == 'horizontal' else 'split editor vertically')
	else:
		utils.show('no file open to split editor')
def pcruncode():
	if not isinstance(state.active, editor.Editor):
		utils.show('not an editor')
		return
	state.active.f5()
def pccopy(*args, **kwargs):
	if not isinstance(state.active, editor.Editor):
		return
	return state.active.cp(*args, **kwargs)
def pccut(*args, **kwargs):
	if not isinstance(state.active, editor.Editor):
		return
	return state.active.cut(*args, **kwargs)
def pcfindreplace(*args, **kwargs):
	if not isinstance(state.active, editor.Editor):
		return
	return state.active.fr(*args, **kwargs)
def pcfindtext(*args, **kwargs):
	if not isinstance(state.active, editor.Editor):
		return
	return state.active.f(*args, **kwargs)
def pcget(*args, **kwargs):
	if not isinstance(state.active, editor.Editor):
		return
	return state.active.type_.get(*args, **kwargs)
def pcgotoline(*args, **kwargs):
	if not isinstance(state.active, editor.Editor):
		return
	return state.active.gl(*args, **kwargs)
def pchmode(*args, **kwargs):
	if not isinstance(state.active, editor.Editor):
		return
	return state.active.pchmode(*args, **kwargs)
def pcinsert(*args, **kwargs):
	if not isinstance(state.active, editor.Editor):
		return
	return state.active.type_.insert(*args, **kwargs)
def pcnewfile(*args, **kwargs):
	if not isinstance(state.active, editor.Editor):
		return
	return state.active.nw(*args, **kwargs)
def pcopenfile(*args, **kwargs):
	if not isinstance(state.active, editor.Editor):
		return
	return state.active.llld(*args, **kwargs)
def pcpageback(*args, **kwargs):
	if not isinstance(state.active, editor.Editor):
		return
	return state.active.ptb(*args, **kwargs)
def pcpageforw(*args, **kwargs):
	if not isinstance(state.active, editor.Editor):
		return
	return state.active.ptf(*args, **kwargs)
def pcpaste(*args, **kwargs):
	if not isinstance(state.active, editor.Editor):
		return
	return state.active.pst(*args, **kwargs)
def pcredo(*args, **kwargs):
	if not isinstance(state.active, editor.Editor):
		return
	return state.active.redo(*args, **kwargs)
def pcremoveselectionpoint(*args, **kwargs):
	if not isinstance(state.active, editor.Editor):
		return
	return state.active.removeselpoint(*args, **kwargs)
def pcsaveasfile(*args, **kwargs):
	if not isinstance(state.active, editor.Editor):
		return
	return state.active.ssv(*args, **kwargs)
def pcsavefile(*args, **kwargs):
	if not isinstance(state.active, editor.Editor):
		return
	return state.active.sssv(*args, **kwargs)
def pcselall(*args, **kwargs):
	if not isinstance(state.active, editor.Editor):
		return
	return state.active.selall(*args, **kwargs)
def pcsetselectionpoint(*args, **kwargs):
	if not isinstance(state.active, editor.Editor):
		return
	return state.active.setselpoint(*args, **kwargs)
def pcspeaktext(*args, **kwargs):
	if not isinstance(state.active, editor.Editor):
		return
	return state.active.spk(*args, **kwargs)
def pctag(*args, **kwargs):
	if not isinstance(state.active, editor.Editor):
		return
	return state.active.type_.tag_add(*args, **kwargs)
def pctoggleselectionpoint(*args, **kwargs):
	if not isinstance(state.active, editor.Editor):
		return
	return state.active.toggleselpoint(*args, **kwargs)
def pcundo(*args, **kwargs):
	if not isinstance(state.active, editor.Editor):
		return
	return state.active.undo(*args, **kwargs)
def pcuntag(*args, **kwargs):
	if not isinstance(state.active, editor.Editor):
		return
	return state.active.type_.tag_remove(*args, **kwargs)
def pccommentregion(start, end):
	if not isinstance(state.active, editor.Editor):
		utils.show('not an editor')
		return
	if not state.active.hmode in ('python', 'latex', 'html', 'markdown'):
		return
	pcrunhook('before', 'comment-region', (start, end))
	ender = ''
	if state.active.hmode == 'python':
		commentor = '#'
	elif state.active.hmode == 'latex':
		commentor = '%'
	elif state.active.hmode == 'html' or state.active.hmode == 'markdown':
		commentor = '<!--'
		ender = '-->'
	l = start
	state.active.type_.edit_separator()
	while not l > end:
		if not state.active.type_.get(f'{l}.0', f'{l}.end').strip():
			l += 1
			continue
		state.active.type_.insert(f'{l}.0', commentor)
		state.active.type_.insert(f'{l}.end', ender)
		l += 1
	state.active.type_.edit_separator()
	utils.show('comment region')
	state.active.keypress()
	pcrunhook('after', 'comment-region', (start, end))
def pccommentselection():
	if not isinstance(state.active, editor.Editor):
		utils.show('not an editor')
		return
	if not state.active.hmode in ('python', 'latex', 'html', 'markdown'):
		return
	try:
		start = int(state.active.type_.index('sel.first').split('.')[0])
		end = int(state.active.type_.index('sel.last').split('.')[0])
	except Exception:
		utils.show('nothing is selected')
		return
	else:
		pcrunhook('before', 'comment-region', (start, end))
		ender = ''
		if state.active.hmode == 'python':
			commentor = '#'
		elif state.active.hmode == 'latex':
			commentor = '%'
		elif state.active.hmode == 'html' or state.active.hmode == 'markdown':
			commentor = '<!--'
			ender = '-->'
		l = start
		state.active.type_.edit_separator()
		while not l > end:
			if not state.active.type_.get(f'{l}.0', f'{l}.end').strip():
				l += 1
				continue
			state.active.type_.insert(f'{l}.0', commentor)
			state.active.type_.insert(f'{l}.end', ender)
			l += 1
		state.active.type_.edit_separator()
	utils.show('comment selection')
	state.active.keypress()
	pcrunhook('after', 'comment-region', (start, end))
def pcuncommentregion(start, end):
	if not isinstance(state.active, editor.Editor):
		utils.show('not an editor')
		return
	if not state.active.hmode in ('python', 'latex', 'html', 'markdown'):
		return
	pcrunhook('before', 'uncomment-region', (start, end))
	state.active.type_.edit_separator()
	ender = ''
	if state.active.hmode == 'python':
		commentor = '#'
	elif state.active.hmode == 'latex':
		commentor = '%'
	elif state.active.hmode == 'html' or state.active.hmode == 'markdown':
		commentor = '<!--'
		ender = '-->'
	l = start
	while not l > end:
		stripped = state.active.type_.get(f'{l}.0', f'{l}.end').lstrip()
		if stripped.startswith(commentor):
			a = len(state.active.type_.get(f'{l}.0', f'{l}.end')) - len(stripped)
			b = a + len(commentor)
			state.active.type_.delete(f'{l}.{a}', f'{l}.{b}')
		if ender:
			stripped = state.active.type_.get(f'{l}.0', f'{l}.end').rstrip()
			if stripped.endswith(ender):
				state.active.type_.delete(f'{l}.end-{len(ender)}c', f'{l}.end')
		l += 1
	state.active.type_.edit_separator()
	utils.show('uncomment region')
	state.active.keypress()
	pcrunhook('after', 'uncomment-region', (start, end))
def pcuncommentselection():
	if not isinstance(state.active, editor.Editor):
		utils.show('not an editor')
		return
	if not state.active.hmode in ('python', 'latex', 'html', 'markdown'):
		return
	try:
		start = int(state.active.type_.index('sel.first').split('.')[0])
		end = int(state.active.type_.index('sel.last').split('.')[0])
	except Exception:
		utils.show('nothing is selected')
		return
	else:
		pcrunhook('before', 'uncomment-region', (start, end))
		state.active.type_.edit_separator()
		ender = ''
		if state.active.hmode == 'python':
			commentor = '#'
		elif state.active.hmode == 'latex':
			commentor = '%'
		elif state.active.hmode == 'html' or state.active.hmode == 'markdown':
			commentor = '<!--'
			ender = '-->'
		l = start
		while not l > end:
			stripped = state.active.type_.get(f'{l}.0', f'{l}.end').lstrip()
			if stripped.startswith(commentor):
				a = len(state.active.type_.get(f'{l}.0', f'{l}.end')) - len(stripped)
				b = a + len(commentor)
				state.active.type_.delete(f'{l}.{a}', f'{l}.{b}')
			if ender:
				stripped = state.active.type_.get(f'{l}.0', f'{l}.end').rstrip()
				if stripped.endswith(ender):
					state.active.type_.delete(f'{l}.end-{len(ender)}c', f'{l}.end')
			l += 1
		state.active.type_.edit_separator()
		utils.show('uncomment selection')
		state.active.keypress()
		pcrunhook('after', 'uncomment-region', (start, end))
def pccleareditor():
	if not isinstance(state.active, editor.Editor):
		utils.show('not an editor')
		return
	if state.root.ask('Warning', 'Clear the active editor?', options = ('ok', 'cancel')):
		pcrunhook('before', 'clear-editor')
		state.active.type_.edit_separator()
		state.active.type_.delete('1.0', 'end')
		state.active.type_.edit_separator()
		utils.show('cleared editor')
		pcrunhook('after', 'clear-editor')
def pcselecttext(a, b):
	if not isinstance(state.active, editor.Editor):
		utils.show('not an editor')
		return
	state.active.type_.tag_remove('sel', '1.0', 'end')
	state.active.type_.tag_add('sel', a, b)
	utils.show(f'selected text from {a} to {b}')
def pcgetselection():
	if not isinstance(state.active, editor.Editor):
		return
	try:
		start = state.active.type_.index('sel.first')
		end = state.active.type_.index('sel.last')
		ans = (str(start), str(end))
	except Exception:
		ans = tuple()
	return ans
def pcmark(a, b = None):
	if not isinstance(state.active, editor.Editor):
		utils.show('not an editor')
		return
	if not b:
		a, b = a[0], a[1]
	pcrunhook('before', 'mark-region', (a, b))
	state.active.type_.tag_add('marked', a, b)
	utils.show(f'marked text from {a} to {b}')
	pcrunhook('after', 'mark-region', (a, b))
def pcmarkselection():
	if not isinstance(state.active, editor.Editor):
		utils.show('not an editor')
		return
	try:
		start = state.active.type_.index('sel.first')
		end = state.active.type_.index('sel.last')
	except Exception:
		return
	pcrunhook('before', 'mark-region', (start, end))
	state.active.type_.tag_add('marked', start, end)
	utils.show(f'marked text from {start} to {end}')
	pcrunhook('after', 'mark-region', (start, end))
def pcunmark(a, b = None):
	if not isinstance(state.active, editor.Editor):
		utils.show('not an editor')
		return
	if not b:
		a, b = a[0], a[1]
	pcrunhook('before', 'unmark-region', (a, b))
	state.active.type_.tag_remove('marked', a, b)
	utils.show(f'unmarked text from {a} to {b}')
	pcrunhook('after', 'unmark-region', (a, b))
def pcunmarkall():
	if not isinstance(state.active, editor.Editor):
		utils.show('not an editor')
		return
	state.active.type_.tag_remove('marked', '1.0', 'end')
	utils.show(f'unmarked all text')
def pctkindex(toindex, line = False):
	if not isinstance(state.active, editor.Editor):
		return
	ans = state.active.type_.index(toindex)
	if line == 'line':
		ans = ans.split('.')[0]
	return ans
def pcdelete(*args, **kwargs):
	if not isinstance(state.active, editor.Editor):
		utils.show('not an editor')
		return
	utils.show('delete text')
	state.active.type_.delete(*args, **kwargs)
def _pcmovecursor(index):
	state.active.type_.mark_set('insert', index)
	state.active.type_.see(index)
def pcmovecursor(index):
	if not isinstance(state.active, editor.Editor):
		return
	_pcmovecursor(index)
def pcswitchemailtab():
	if not isinstance(state.active, editor.Editor):
		utils.show('not an editor')
		return
	if state.active.hmode == 'email':
		pcrunhook('before', 'switch-to-email-tab')
		state.active.tabs.select(state.active.ef)
		utils.show('switched to email tab')
		pcrunhook('after', 'switch-to-email-tab')
	else:
		utils.show('not in email hmode')
def pcpyshell():
	if not isinstance(state.active, editor.Editor):
		utils.show('not an editor')
		return
	if state.active.hmode == 'python':
		pcrunhook('before', 'switch-to-python-shell-tab')
		state.active.tabs.select(state.active.sf)
		state.active.shellcmd.focus()
		utils.show('switch to python shell')
		state.active.keypress()
		pcrunhook('after', 'switch-to-python-shell-tab')
	else:
		utils.show('not in python hmode')
def _pcpyresolve(commandinput):
	if state.active.hmode != 'python':
		utils.show('not in python hmode')
		return None
	raw = commandinput.strip()
	word = raw.lower()
	if word in ('f', 'fun', 'func', 'function', 'c', 'class'):
		wantclass = word in ('c', 'class')
		want_scope_kind = 'class' if wantclass else 'function'
		want_def_kind = 'class' if wantclass else 'func'
		line = int(state.active.type_.index('insert').split('.')[0])
		defs_by_start = {}
		for dl, dc, dname, dkind in state.active._python_def_names:
			if dkind == want_def_kind:
				defs_by_start[dl] = dname
		best = None
		for sc in state.active._python_scopes:
			if sc.get('kind') != want_scope_kind:
				continue
			if not (sc['start'] <= line <= sc['end']):
				continue
			if sc['start'] not in defs_by_start:
				continue
			if best is None or sc['start'] > best[0]:
				best = (sc['start'], sc['end'], defs_by_start[sc['start']])
		if best is None:
			utils.show('error: currently in no class' if wantclass else 'error: currently in no function')
			return None
		startline, endline, name = best
		return startline, endline, name, want_def_kind
	for dl, dc, dname, dkind in state.active._python_def_names:
		if dname == raw:
			want_scope_kind = 'class' if dkind == 'class' else 'function'
			endline = dl
			for sc in state.active._python_scopes:
				if sc.get('kind') == want_scope_kind and sc['start'] == dl:
					endline = sc['end']
					break
			return dl, endline, dname, dkind
	utils.show(f'error: function or class \'{raw}\' does not exist in current editor')
	return None
def pcpystartof(commandinput):
	if not isinstance(state.active, editor.Editor):
		utils.show('not an editor')
		return
	result = _pcpyresolve(commandinput)
	if result is None:
		return
	startline, endline, name, kind = result
	label = 'class' if kind == 'class' else 'function'
	_pcmovecursor(f'{startline}.end')
	state.active.keypress()
	utils.show(f'jumped to start of {label} \'{name}\'')
def pcpyendof(commandinput):
	if not isinstance(state.active, editor.Editor):
		utils.show('not an editor')
		return
	result = _pcpyresolve(commandinput)
	if result is None:
		return
	startline, endline, name, kind = result
	label = 'class' if kind == 'class' else 'function'
	_pcmovecursor(f'{endline}.end')
	state.active.keypress()
	utils.show(f'jumped to end of {label} {name}')
def pcgodef(commandinput):
	if not isinstance(state.active, editor.Editor):
		utils.show('not an editor')
		return
	if state.active.hmode != 'python':
		utils.show('not in python hmode')
		return
	name = commandinput.strip()
	line = int(state.active.type_.index('insert').split('.')[0])
	scope_idx = None
	best_start = None
	for i, sc in enumerate(state.active._python_scopes):
		if sc['start'] <= line <= sc['end']:
			if best_start is None or sc['start'] > best_start:
				best_start = sc['start']
				scope_idx = i
	target_line = None
	idx = scope_idx
	while idx is not None:
		sc = state.active._python_scopes[idx]
		bindings = sc['names'].get(name)
		if bindings:
			candidates = [ln for ln, kd in bindings if ln <= line]
			target_line = max(candidates) if candidates else min(ln for ln, kd in bindings)
			break
		idx = sc['parent']
	if target_line is None:
		utils.show(f'error: name \'{name}\' does not exist in current editor')
		return
	_pcmovecursor(f'{target_line}.end')
	state.active.keypress()
	utils.show(f'jumped to definition of \'{name}\'')
def pcswitchedittab():
	if not isinstance(state.active, editor.Editor):
		utils.show('not an editor')
		return
	pcrunhook('before', 'switch-to-editor-tab')
	state.active.tabs.select(state.active.mf)
	state.active.type_.focus()
	utils.show('switch to editor')
	state.active.keypress()
	pcrunhook('after', 'switch-to-editor-tab')
def pccmdwrite(text, n):
	if not isinstance(state.active, editor.Editor):
		utils.show('not an editor')
		return
	state.active.type_.edit_separator()
	state.active.type_.insert(state.active.type_.index('insert'), text * n)
	utils.show(f'wrote \'{text.replace("\n", "\\n")}\' {n} times')
	state.active.type_.edit_separator()
	state.active.keypress()
def pcindentregion(start, end):
	if not isinstance(state.active, editor.Editor):
		utils.show('not an editor')
		return
	pcrunhook('before', 'indent-region', (start, end))
	if state.taborspace:
		whitespace = '    '
	else:
		whitespace = '	'
	l = start
	state.active.type_.edit_separator()
	while not l > end:
		if not state.active.type_.get(f'{l}.0', f'{l}.end').strip():
			l += 1
			continue
		state.active.type_.insert(f'{l}.0', whitespace)
		l += 1
	state.active.type_.edit_separator()
	utils.show('indent region')
	state.active.keypress()
	pcrunhook('after', 'indent-region', (start, end))
def pcindentselection():
	if not isinstance(state.active, editor.Editor):
		utils.show('not an editor')
		return
	try:
		start = int(state.active.type_.index('sel.first').split('.')[0])
		end = int(state.active.type_.index('sel.last').split('.')[0])
	except Exception:
		utils.show('nothing is selected')
		return
	else:
		pcrunhook('before', 'indent-region', (start, end))
		if state.taborspace:
			whitespace = '    '
		else:
			whitespace = '	'
		l = start
		state.active.type_.edit_separator()
		while not l == end:
			state.active.type_.insert(f'{l}.0', whitespace)
			l += 1
		state.active.type_.insert(f'{l}.0', whitespace)
		state.active.type_.edit_separator()
		utils.show('indent selection')
		state.active.keypress()
		pcrunhook('after', 'indent-region', (start, end))
def pcunindentregion(start, end):
	if not isinstance(state.active, editor.Editor):
		utils.show('not an editor')
		return
	pcrunhook('before', 'unindent-region', (start, end))
	state.active.type_.edit_separator()
	lines = [state.active.type_.get(f'{l}.0', f'{l}.end') for l in range(start, end + 1)]
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
			state.active.type_.delete(f'{l}.0', f'{l}.1')
		elif line.startswith(' '):
			remove = 0
			for ch in line:
				if ch == ' ' and remove < min_spaces:
					remove += 1
				else:
					break
			if remove:
				state.active.type_.delete(f'{l}.0', f'{l}.{remove}')
	state.active.type_.edit_separator()
	utils.show('unindent region')
	state.active.keypress()
	pcrunhook('after', 'unindent-region', (start, end))
def pcunindentselection():
	if not isinstance(state.active, editor.Editor):
		utils.show('not an editor')
		return
	try:
		start = int(state.active.type_.index('sel.first').split('.')[0])
		end = int(state.active.type_.index('sel.last').split('.')[0])
	except Exception:
		utils.show('nothing is selected')
		return
	else:
		pcrunhook('before', 'unindent-region', (start, end))
		state.active.type_.edit_separator()
		lines = [state.active.type_.get(f'{l}.0', f'{l}.end') for l in range(start, end + 1)]
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
				state.active.type_.delete(f'{l}.0', f'{l}.1')
			elif line.startswith(' '):
				remove = 0
				for ch in line:
					if ch == ' ' and remove < min_spaces:
						remove += 1
					else:
						break
				if remove:
					state.active.type_.delete(f'{l}.0', f'{l}.{remove}')
		state.active.type_.edit_separator()
		utils.show('unindent selection')
		state.active.keypress()
		pcrunhook('after', 'unindent-region', (start, end))
pycodetopythoncommands = {'aboutpynotes': 'abt', 'ask': 'pcask', 'balancebuffers': 'balance', 'cleareditor': 'pccleareditor', 'closebuffer': 'pcclosebuff', 'cmdrun': 'cmdrun', 'color': 'pccolor', 'commentregion': 'pccommentregion', 'commentselection': 'pccommentselection', 'copy': 'pccopy', 'copytext': 'pccopytext', 'cut': 'pccut', 'delete': 'pcdelete', 'dictate': 'st', 'downloadplugins': 'dp', 'fileinfoconfig': 'active.fileinfoconfig', 'findreplace': 'pcfindreplace', 'findtext': 'pcfindtext', 'fullscreen': 'pcfullscreen', 'get': 'pcget', 'getattr': 'getattr', 'getselection': 'pcgetselection', 'gotoline': 'pcgotoline', 'hmode': 'pchmode', 'indentregion': 'pcindentregion', 'indentselection': 'pcindentselection', 'insert': 'pcinsert', 'killquit': 'pckillexit', 'mark': 'pcmark', 'markselection': 'pcmarkselection', 'mathgod': 'mathgod', 'maximize': 'pcmax', 'minimize': 'pcmin', 'movecursor': 'pcmovecursor', 'neweditor': 'neweditor', 'newfile': 'pcnewfile', 'openfile': 'pcopenfile', 'openfilenewedit': 'pcneweditfile', 'openhelp': 'pcopenhelp', 'openplugindir': 'op', 'openpycode': 'pc', 'openterm': 'term', 'pageback': 'pcpageback', 'pageforw': 'pcpageforw', 'pass': 'pass', 'paste': 'pcpaste', 'preferences': 'prf', 'prompt': 'pcprompt', 'pynotessourcecode': 'ss', 'pyshell': 'pcpyshell', 'pythongoendof': 'pcpyendof', 'pythongostartof': 'pcpystartof', 'pythongodef': 'pcgodef', 'quit': 'ext', 'redo': 'pcredo', 'repeatxcommand': 'pcrepeatx', 'removeselectionpoint': 'pcremoveselectionpoint', 'return': 'return', 'runcode': 'pcruncode', 'saveasfile': 'pcsaveasfile', 'savefile': 'pcsavefile', 'say': 'say', 'selall': 'pcselall', 'select': 'pcselecttext', 'setattr': 'setattr', 'setselectionpoint': 'pcsetselectionpoint', 'setvar': 'pcsetvar', 'setwingeometry': 'root.geometry', 'setwintitle': 'pcgosettitle', 'show': 'show', 'speaktext': 'pcspeaktext', 'spliteditor': 'pcsplitedit', 'switchbuffer': 'setactive', 'switcheditortab': 'pcswitchedittab', 'switchemailtab': 'pcswitchemailtab', 'tag': 'pctag', 'termexec': 'pctermexec', 'tkindex': 'pctkindex', 'toggleselectionpoint': 'pctoggleselectionpoint', 'typecommand': 'cmd', 'uncommentregion': 'pcuncommentregion', 'uncommentselection': 'pcuncommentselection', 'undo': 'pcundo', 'unfullscreen': 'pcunfullscreen', 'unindentregion': 'pcunindentregion', 'unindentselection': 'pcunindentselection', 'unmark': 'pcunmark', 'unmarkall': 'pcunmarkall', 'unmaximize': 'pcunmax', 'unsetwintitle': 'pcunsettitle', 'untag': 'pcuntag', 'wait': 'time.sleep', 'write': 'pccmdwrite'}
pycodecommands = sorted(list(pycodetopythoncommands))
pythoncommands = [pycodetopythoncommands[x] for x in pycodecommands]
def pcread(code):
	global pycodecommands
	global pythoncommands
	pycodecommands = sorted(list(pycodetopythoncommands))
	pythoncommands = [pycodetopythoncommands[x] for x in pycodecommands]
	state.pcwrittencommands = {}
	state.pcbeforehooks = {}
	state.pcafterhooks = {}
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
							state.wholenewwords.append(ck)
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
						state.wholenewwords.append(key_part)
						simple_bindings_seen[key_part] = action_parts
						type_bind_cdt += f"for buffer in all_buffers: bindrecur(buffer, '{key_part}', lambda event: pcexecaction(\"{action_parts}\") or 'break')" + '\n'
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
					state.pcwrittencommands[cmd] = to_do
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
					(state.pcbeforehooks if when == 'before' else state.pcafterhooks).setdefault(event, []).append(to_do)
				elif s and len(s) == 1:
					s = s[0].strip()
					startupcdt += f'{'\n'.join(map(nonlambdafunc, s[1:-1].strip().split('↩')))}' + '\n'
				else:
					state.root.error('Error in PyCode', f'Invalid syntax in line:\n"{line}"')
			except Exception as error:
				error = str(error)
				state.root.error('Error in PyCode', f'Error in line "{line}":\n{error}')
	defaults_cdt_root = '''\
bindrecur(root, '<Alt-x>', lambda event: cmd())
bindrecur(root, '<Control-N>', lambda event: neweditor())
bindrecur(root, '<Control-O>', lambda event: neweditor(True))
bindrecur(root, '<Control-q>', lambda event: ext())
'''
	defaults_cdt_type_ = '''\
for buffer in all_buffers: bindtype_(buffer, '<Control-a>', lambda event, editor = buffer: editor.selall())
for buffer in all_buffers: bindtype_(buffer, '<Control-n>', lambda event, editor = buffer: editor.nw())
for buffer in all_buffers: bindtype_(buffer, '<Control-o>', lambda event, editor = buffer: editor.llld())
for buffer in all_buffers: bindtype_(buffer, '<Control-c>', lambda event, editor = buffer: editor.cp())
for buffer in all_buffers: bindtype_(buffer, '<Control-v>', lambda event, editor = buffer: editor.pst())
for buffer in all_buffers: bindtype_(buffer, '<Control-w>', lambda event, editor = buffer: pcclosebuff(all_buffers.index(buffer)))
for buffer in all_buffers: bindtype_(buffer, '<Control-x>', lambda event, editor = buffer: editor.cut())
for buffer in all_buffers: bindtype_(buffer, '<KeyRelease>', lambda event, editor = buffer: editor.keypress(), break_ = False)
for buffer in all_buffers: bindtype_(buffer, '<BackSpace>', lambda event: show('delete text'), break_ = False)
for buffer in all_buffers: bindtype_(buffer, '<Delete>', lambda event: show('delete text'), break_ = False)
for buffer in all_buffers: bindtype_(buffer, '<Return>', lambda event, editor = buffer: editor.indent(), break_ = False)
for buffer in all_buffers: bindtype_(buffer, '<Alt-l>', lambda event, editor = buffer: editor.gl())
for buffer in all_buffers: bindtype_(buffer, '<Control-p>', lambda event, editor = buffer: editor.ptf())
for buffer in all_buffers: bindtype_(buffer, '<Control-P>', lambda event, editor = buffer: editor.ptb())
for buffer in all_buffers: bindtype_(buffer, '<Control-f>', lambda event, editor = buffer: editor.f())
for buffer in all_buffers: bindtype_(buffer, '<Control-F>', lambda event, editor = buffer: editor.fr())
for buffer in all_buffers: bindtype_(buffer, '<Control-h>', lambda event, editor = buffer: editor.fr())
for buffer in all_buffers: bindtype_(buffer, '<Control-z>', lambda event, editor = buffer: editor.undo())
for buffer in all_buffers: bindtype_(buffer, '<Control-Z>', lambda event, editor = buffer: editor.redo())
for buffer in all_buffers: bindtype_(buffer, '<Control-s>', lambda event, editor = buffer: editor.sssv())
for buffer in all_buffers: bindtype_(buffer, '<Control-S>', lambda event, editor = buffer: editor.ssv())
for buffer in all_buffers: bindtype_(buffer, '<F5>', lambda event, editor = buffer: editor.f5())
for buffer in all_buffers: bindtype_(buffer, '<Control-space>', lambda event, editor = buffer: editor.toggleselpoint())
for buffer in all_buffers: bindtype_(buffer, '<KeyPress>', lambda event, editor = buffer: editor.selkeypress(event), break_ = False)
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
		type_bind_cdt += f'for editor in all_buffers: bindrecur(editor, \'{mod_key}\', lambda event: {handler_t})\n'
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
		type_bind_cdt = f'for editor in all_buffers: bindtype_(editor, \'<KeyPress>\', lambda event: {kp_body})\n' + type_bind_cdt
		cdt = chord_init + cdt
	state.pycode_keybindings_cdt = type_bind_cdt
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
pchookevents = ['new-file-current-editor', 'new-file-new-editor', 'open-file-current-editor', 'open-file-new-editor', 'save-file', 'save-as-file', 'exit-pynotes', 'close-buffer', 'switch-buffer', 'run-code', 'mark-region', 'unmark-region', 'comment-region', 'uncomment-region', 'indent-region', 'unindent-region', 'open-mathgod', 'term-exec', 'alt-x-command', 'pycode-command', 'undo', 'redo', 'show-pynotes-source-code', 'open-terminal', 'open-preferences', 'next-page', 'previous-page', 'copy-text', 'paste-text', 'cut-text', 'fullscreen', 'un-fullscreen', 'maximize-window', 'unmaximize-window', 'minimize-window', 'clear-editor', 'open-pycode', 'change-hmode', 'switch-to-editor-tab', 'switch-to-python-shell-tab', 'switch-to-email-tab', 'resize-window']
def pc():
	pcrunhook('before', 'open-pycode')
	utils.show('open pycode')
	for binded in state.wholenewwords:
		state.root.unbind(binded)
		for buffer in state.all_buffers:
			unbindrecur(buffer, binded)
	state.wholenewwords.clear()
	pcwin = state.root.subwin()
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
			pyfunccodewin = state.root.subwin()
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
			keygetting = state.root.subwin()
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
			hookwin = state.root.subwin()
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
	pcwin.style(state.root.gettheme())
	pcwin.update()
	pcwin.sizablefalse()
	pcrunhook('after', 'open-pycode')
