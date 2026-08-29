import os
import shutil
import state
import editor
import dialogs
import help
import pycode
import speech
import terminal
import utils
import window
import preferences
def cmdfindgroupclose(s, openindex):
	depth = 0
	i = openindex
	n = len(s)
	while i < n:
		ch = s[i]
		if ch == '\\' and i + 1 < n:
			i += 2
			continue
		if ch == '(':
			depth += 1
		elif ch == ')':
			depth -= 1
			if depth == 0:
				return i
		i += 1
	return None
def cmdcheckbrackets(s):
	i = 0
	n = len(s)
	while i < n:
		ch = s[i]
		if ch == '\\' and i + 1 < n:
			i += 2
			continue
		if ch == ':' and s[i + 1:].lstrip().startswith('('):
			openindex = i + 1 + (len(s[i + 1:]) - len(s[i + 1:].lstrip()))
			closeindex = cmdfindgroupclose(s, openindex)
			if closeindex is None:
				return False
			i = closeindex + 1
			continue
		i += 1
	return True
def cmdstripgroup(commandinput):
	if commandinput.startswith('('):
		closeindex = cmdfindgroupclose(commandinput, 0)
		if closeindex is not None and closeindex == len(commandinput) - 1:
			return commandinput[1:closeindex]
	return commandinput
def cmdsplit(s):
	parts = []
	current = ''
	i = 0
	n = len(s)
	while i < n:
		ch = s[i]
		if ch == '\\' and i + 1 < n:
			current += s[i:i + 2]
			i += 2
			continue
		if ch == ':' and s[i + 1:].lstrip().startswith('('):
			openindex = i + 1 + (len(s[i + 1:]) - len(s[i + 1:].lstrip()))
			closeindex = cmdfindgroupclose(s, openindex)
			if closeindex is None:
				current += s[i:]
				i = n
				continue
			current += s[i:closeindex + 1]
			i = closeindex + 1
			continue
		if ch == ';':
			parts.append(current)
			current = ''
			i += 1
			continue
		current += ch
		i += 1
	parts.append(current)
	return parts
def cmdparsegroup(s):
	s = s.strip()
	if s.startswith('('):
		depth = 0
		for i, ch in enumerate(s):
			if ch == '(':
				depth += 1
			elif ch == ')':
				depth -= 1
				if depth == 0:
					content = s[1:i]
					remainder = s[i + 1:]
					if not remainder.startswith('*'):
						raise Exception
					return content, int(remainder[1:])
		raise Exception
	content, n = s.split('*', 1)
	return content, int(n)
def cmdrun(fullcommand):
	if not fullcommand:
		return
	fullcommand = fullcommand.strip()
	if not cmdcheckbrackets(fullcommand):
		utils.show('error: unmatched opening and closing brackets')
		return
	cmdparts = cmdsplit(fullcommand)
	if len(cmdparts) > 1:
		for command in cmdparts:
			cmdrun(command)
		return
	if ':' in fullcommand:
		command, commandinput = fullcommand.split(':', 1)
	else:
		command = fullcommand
		commandinput = None
	command = command.strip()
	if commandinput:
		commandinput = commandinput.strip()
		commandinput = cmdstripgroup(commandinput)
		commandinput = commandinput.strip()
	pycode.pcrunhook('before', f'alt-x-command:{command}', commandinput)
	if command in state.pcwrittencommands:
		pycode.pcrunhook('before', f'pycode-command:{command}', commandinput)
	if command in state.plgncmds:
		try:
			execvars = vars(state).copy()
			execvars['__file__'] = os.path.join(state.plgncmds[command][0], 'commands')
			execvars['commandinput'] = commandinput
			exec(state.plgncmds[command][1], execvars)
		except Exception as error:
			error = str(error)
			state.root.error('Error!', f'There was an error in running the command \'{command}\' from the plugin "{os.path.basename(os.path.normpath(state.plgncmds[command][0]))}":\n{error}')
		pycode.pcrunhook('after', f'alt-x-command:{command}', commandinput)
		return
	if command in state.pcwrittencommands:
		try:
			execvars = vars(state).copy()
			execvars['commandinput'] = commandinput
			exec(state.pcwrittencommands[command], execvars)
		except Exception as error:
			error = str(error)
			state.root.error('Error!', f'There was an error in running the command \'{command}\' defined in PyCode:\n{error}')
		pycode.pcrunhook('after', f'pycode-command:{command}', commandinput)
		pycode.pcrunhook('after', f'alt-x-command:{command}', commandinput)
		return
	elif command == 'exit' or command == 'e':
		if commandinput:
			utils.show(f'error: command \'{command}\' does not take input')
			return
		window.ext()
	elif command == 'sh' or command == 'splithoriz' or command == 'split-editor-horizontal':
		if commandinput:
			utils.show(f'error: command \'{command}\' does not take input')
			return
		if not isinstance(state.active, editor.Editor):
			utils.show('not an editor')
			return
		if state.active.title:
			window.neweditor(state.active.title)
			utils.show('split editor horizontally')
		else:
			utils.show('no file open to split editor')
	elif command == 'sv' or command == 'splitvert' or command == 'split-editor-vertical':
		if commandinput:
			utils.show(f'error: command \'{command}\' does not take input')
			return
		if not isinstance(state.active, editor.Editor):
			utils.show('not an editor')
			return
		if state.active.title:
			window.neweditor(state.active.title, 'vertical')
			utils.show('split editor vertically')
		else:
			utils.show('no file open to split editor')
	elif command == 'setsel' or command == 'selpointset' or command == 'selection-point-set':
		if not isinstance(state.active, editor.Editor):
			utils.show('not an editor')
			return
		state.active.setselpoint()
	elif command == 'unsetsel' or command == 'selpointunset' or command == 'selection-point-remove':
		if not isinstance(state.active, editor.Editor):
			utils.show('not an editor')
			return
		state.active.removeselpoint()
	elif command == 'bb' or command == 'balance' or command == 'balance-buffers':
		if not commandinput:
			window.balance()
			utils.show('balanced buffers')
		elif commandinput in ('h', 'horiz', 'horizontal'):
			window.balance('horizontal')
			utils.show('balanced horizontal buffers')
		elif commandinput in ('v', 'vert', 'vertical'):
			window.balance('vertical')
			utils.show('balanced vertical buffers')
		else:
			utils.show(f'error: invalid direction \'{commandinput}\' for balance command')
			return
	elif command == 'cb' or command == 'close' or command == 'closecurbuf' or command == 'close-current-buffer':
		if commandinput:
			try:
				n = int(commandinput)
			except Exception:
				utils.show(f'error: invalid input \'{commandinput}\' to close editor command')
				return
			if n < 0 or n >= len(state.all_buffers):
				utils.show(f'error: editor {n} does not exist')
				return
		else:
			n = state.buffindex
		pycode.pcclosebuff(n)
	elif command == 'sw' or command == 'switch' or command == 'switchbuf' or command == 'switch-buffer':
		if commandinput:
			utils.show(f'error: command \'{command}\' does not take input')
			return
		window.setactive()
	elif command == 'sol' or command == 'startofline':
		if commandinput:
			utils.show(f'error: command \'{command}\' does not take input')
			return
		if not isinstance(state.active, editor.Editor):
			utils.show('not an editor')
			return
		n = state.active.type_.index('insert').split('.')[0]
		state.active.type_.mark_set('insert', n + '.0')
		utils.show(f'moved to start of line {n}')
	elif command == 'eol' or command == 'endofline':
		if commandinput:
			utils.show(f'error: command \'{command}\' does not take input')
			return
		if not isinstance(state.active, editor.Editor):
			utils.show('not an editor')
			return
		n = state.active.type_.index('insert').split('.')[0]
		state.active.type_.mark_set('insert', n + '.end')
		utils.show(f'moved to end of line {n}')
	elif command == 'neh' or command == 'newedithoriz' or command == 'new-editor-horizontal':
		if commandinput:
			utils.show(f'error: command \'{command}\' does not take input')
			return
		window.neweditor()
	elif command == 'nev' or command == 'neweditvert' or command == 'new-editor-vertical':
		if commandinput:
			utils.show(f'error: command \'{command}\' does not take input')
			return
		window.neweditor(orient = 'vertical')
	elif command == 'onh' or command == 'opennewhoriz' or command == 'open-file-horizontal':
		if commandinput:
			utils.show(f'error: command \'{command}\' does not take input')
			return
		window.neweditor(True)
	elif command == 'onv' or command == 'opennewvert' or command == 'open-file-vertical':
		if commandinput:
			utils.show(f'error: command \'{command}\' does not take input')
			return
		window.neweditor(True, 'vertical')
	elif command == 'changes' or command == 'ch':
		if commandinput:
			utils.show(f'error: command \'{command}\' does not take input')
			return
		help.changes()
	elif command == 'run':
		if commandinput:
			utils.show(f'error: command \'{command}\' does not take input')
			return
		if not isinstance(state.active, editor.Editor):
			utils.show('not an editor')
			return
		state.active.f5()
	elif command == 'ms' or command == 'mark' or command == 'markset' or command == 'mark-selection':
		if commandinput:
			utils.show(f'error: command \'{command}\' does not take input')
			return
		if not isinstance(state.active, editor.Editor):
			utils.show('not an editor')
			return
		try:
			start = state.active.type_.index('sel.first')
			end = state.active.type_.index('sel.last')
		except Exception:
			utils.show('nothing is selected')
		else:
			pycode.pcmark(start, end)
	elif command == 'unms' or command == 'unmark' or command == 'unmark-selection':
		if commandinput:
			utils.show(f'error: command \'{command}\' does not take input')
			return
		if not isinstance(state.active, editor.Editor):
			utils.show('not an editor')
			return
		try:
			start = state.active.type_.index('sel.first')
			end = state.active.type_.index('sel.last')
		except Exception:
			utils.show('nothing is selected')
		else:
			pycode.pcunmark(start, end)
	elif command == 'sendemail' or command == 'sendmail':
		if commandinput:
			utils.show(f'error: command \'{command}\' does not take input')
			return
		pycode.pcswitchemailtab()
	elif command == 'unma' or command == 'unmarkall':
		if commandinput:
			utils.show(f'error: command \'{command}\' does not take input')
			return
		pycode.pcunmarkall()
	elif command == 'comment' or command == 'cr' or command == 'comment-region':
		if commandinput:
			utils.show(f'error: command \'{command}\' does not take input')
			return
		if not isinstance(state.active, editor.Editor):
			utils.show('not an editor')
			return
		if not state.active.hmode in ('python', 'latex', 'html', 'markdown'):
			utils.show('hmode is not python / latex / html / markdown')
			return
		pycode.pccommentselection()
	elif command == 'uncomment' or command == 'uncr' or command == 'uncomment-region':
		if commandinput:
			utils.show(f'error: command \'{command}\' does not take input')
			return
		if not isinstance(state.active, editor.Editor):
			utils.show('not an editor')
			return
		if not state.active.hmode in ('python', 'latex', 'html', 'markdown'):
			utils.show('hmode is not python / latex / html / markdown')
			return
		pycode.pcuncommentselection()
	elif command == 'pyshell' or command == 'ps':
		if commandinput:
			utils.show(f'error: command \'{command}\' does not take input')
			return
		pycode.pcpyshell()
	elif command == 'fullup':
		if commandinput:
			utils.show(f'error: command \'{command}\' does not take input')
			return
		if not isinstance(state.active, editor.Editor):
			utils.show('not an editor')
			return
		state.active.type_.mark_set('insert', '1.0')
		state.active.type_.see('1.0')
	elif command == 'fulldown':
		if commandinput:
			utils.show(f'error: command \'{command}\' does not take input')
			return
		if not isinstance(state.active, editor.Editor):
			utils.show('not an editor')
			return
		state.active.type_.mark_set('insert', 'end-1c')
		state.active.type_.see('end-1c')
	elif command == 'editor' or command == 'ed':
		if commandinput:
			utils.show(f'error: command \'{command}\' does not take input')
			return
		pycode.pcswitchedittab()
	elif command == 'h' or command == 'help':
		if not commandinput:
			utils.show(f'error: no input given to command \'{command}\'')
			return
		if commandinput == 'x' or commandinput == 'commands':
			help.hx()
		elif commandinput == 'em' or commandinput == 'email':
			help.hemail()
		elif commandinput == 'pc' or commandinput == 'pycode':
			help.helppycode()
		elif commandinput == 'mg' or commandinput == 'mathgod':
			help.helpmathgod()
		elif commandinput == 'pl' or commandinput == 'plugins':
			help.ap()
		else:
			utils.show(f'error: invalid input \'{commandinput}\'')
	elif command == 'st' or command == 'speech-to-text':
		if commandinput:
			utils.show(f'error: command \'{command}\' does not take input')
			return
		speech.st()
	elif command == 'opd' or command == 'openplugindir':
		if commandinput:
			utils.show(f'error: command \'{command}\' does not take input')
			return
		utils.op()
	elif command == 'dp' or command == 'downloadplugins':
		if commandinput:
			utils.show(f'error: command \'{command}\' does not take input')
			return
		utils.dp()
	elif command == 'indent-region' or command == 'ir':
		if commandinput:
			utils.show(f'error: command \'{command}\' does not take input')
			return
		pycode.pcindentselection()
	elif command == 'unindent-region' or command == 'unir':
		if commandinput:
			utils.show(f'error: command \'{command}\' does not take input')
			return
		pycode.pcunindentselection()
	elif command == 'te' or command == 'termexec':
		if not commandinput:
			utils.show(f'error: no input given to command \'{command}\'')
			return
		try:
			utils.show('output: ' + terminal.termexec(commandinput))
		except Exception:
			utils.show(f'error: invalid input \'{commandinput}\'')
	elif command == 'mathgod' or command == 'mg':
		if commandinput:
			utils.show(f'error: command \'{command}\' does not take input')
			return
		utils.mathgod()
	elif command == 'write' or command == 'w':
		if not commandinput:
			utils.show(f'error: no input given to command \'{command}\'')
			return
		if not isinstance(state.active, editor.Editor):
			utils.show('not an editor')
			return
		state.active.type_.edit_separator()
		try:
			textwrote, timeswrote = cmdparsegroup(commandinput)
			state.active.type_.insert(state.active.type_.index('insert'), textwrote.encode().decode('unicode_escape') * timeswrote)
			utils.show(f'wrote \'{textwrote}\' {timeswrote} times')
		except Exception:
			utils.show(f'error: invalid input \'{commandinput}\'')
		state.active.type_.edit_separator()
	elif command == 'repeat' or command == 're':
		try:
			content, n = cmdparsegroup(commandinput)
			for i in range(n):
				cmdrun(content)
		except Exception:
			utils.show(f'error: invalid input \'{commandinput}\'')
	elif command == 'u' or command == 'undo':
		if commandinput:
			utils.show(f'error: command \'{command}\' does not take input')
			return
		state.active.undo()
	elif command == 'r' or command == 'redo':
		if commandinput:
			utils.show(f'error: command \'{command}\' does not take input')
			return
		state.active.redo()
	elif command == 'save' or command == 's':
		if commandinput:
			utils.show(f'error: command \'{command}\' does not take input')
			return
		if not hasattr(state.active, 'sssv'):
			utils.show('cannot save file in current buffer')
			return
		state.active.sssv()
	elif command == 'saveas' or command == 'sa':
		if commandinput:
			utils.show(f'error: command \'{command}\' does not take input')
			return
		if not hasattr(state.active, 'ssv'):
			utils.show('cannot save file in current buffer')
			return
		state.active.ssv()
	elif command == 'search' or command == 'f':
		if commandinput and not commandinput in ('b', 'back'):
			utils.show(f'error: invalid input \'{commandinput}\' for find command')
			return
		if not isinstance(state.active, editor.Editor):
			utils.show('not an editor')
		if commandinput:
			state.active.f('backward')
		else:
			state.active.f()
	elif command == 'find-replace' or command == 'findreplace' or command == 'fr':
		if commandinput and not commandinput in ('b', 'back'):
			utils.show(f'error: invalid input \'{commandinput}\' for find & replace command')
			return
		if not isinstance(state.active, editor.Editor):
			utils.show('not an editor')
		if commandinput:
			state.active.fr('backward')
		else:
			state.active.fr()
	elif command == 'show-source' or command == 'source-code':
		if commandinput:
			utils.show(f'error: command \'{command}\' does not take input')
			return
		window.ss()
	elif command == 'new' or command == 'n':
		if commandinput:
			utils.show(f'error: command \'{command}\' does not take input')
			return
		if not hasattr(state.active, 'nw'):
			utils.show('cannot open new file in current buffer')
			return
		state.active.nw()
	elif command == 'l' or command == 'gl' or command == 'gotoline':
		if not isinstance(state.active, editor.Editor):
			utils.show('not an editor')
			return
		state.active.gl(commandinput)
	elif command == 'open' or command == 'find' or command == 'o' or command == 'load':
		if commandinput:
			utils.show(f'error: command \'{command}\' does not take input')
			return
		if not hasattr(state.active, 'llld'):
			utils.show('cannot open file in current buffer')
			return
		state.active.llld()
	elif command == 'terminal' or command == 'cmd' or command == 'term' or command == 't':
		if commandinput:
			commandlist = commandinput.split(' ')
			if not shutil.which(commandlist[0]):
				utils.show(f'error: \'{commandlist[0]}\' not found or not executable')
				return
			terminal.term(command = commandlist, endmessage = '--- Command finished, press any key to continue ---')
		else:
			terminal.term()
	elif command == 'prf' or command == 'preferences':
		if commandinput:
			utils.show(f'error: command \'{command}\' does not take input')
			return
		preferences.prf()
	elif command == 'cancel' or command == 'z':
		if commandinput:
			utils.show(f'error: command \'{command}\' does not take input')
			return
		pass
	elif command == '':
		if commandinput:
			utils.show(f'error: command \'{command}\' does not take input')
			return
		pass
	elif command == 'a' or command == 'selall' or command == 'all':
		if commandinput:
			utils.show(f'error: command \'{command}\' does not take input')
			return
		if not hasattr(state.active, 'selall'):
			utils.show('cannot select all in current buffer')
			return
		state.active.selall()
	elif command == 'copy' or command == 'c':
		if commandinput:
			utils.show(f'error: command \'{command}\' does not take input')
			return
		if not hasattr(state.active, 'cp'):
			utils.show('cannot copy in current buffer')
			return
		state.active.cp()
	elif command == 'cut':
		if commandinput:
			utils.show(f'error: command \'{command}\' does not take input')
			return
		state.active.cut()
	elif command == 'pf' or command == 'pagenext':
		if commandinput:
			utils.show(f'error: command \'{command}\' does not take input')
			return
		state.active.ptf()
	elif command == 'pb' or command == 'pageback':
		if commandinput:
			utils.show(f'error: command \'{command}\' does not take input')
			return
		state.active.ptb()
	elif command == 'paste' or command == 'p':
		if commandinput:
			utils.show(f'error: command \'{command}\' does not take input')
			return
		if not hasattr(state.active, 'pst'):
			utils.show('cannot paste in current buffer')
			return
		state.active.pst()
	elif command == 'sp' or command == 'speak':
		if commandinput:
			utils.show(f'error: command \'{command}\' does not take input')
			return
		state.active.spk()
	elif command == 'full':
		if commandinput:
			utils.show(f'error: command \'{command}\' does not take input')
			return
		pycode.pcfullscreen()
	elif command == 'unfull':
		if commandinput:
			utils.show(f'error: command \'{command}\' does not take input')
			return
		pycode.pcunfullscreen()
	elif command == 'max' or command == 'maximize':
		if commandinput:
			utils.show(f'error: command \'{command}\' does not take input')
			return
		pycode.pcmax()
	elif command == 'unmax' or command == 'unmaximize':
		if commandinput:
			utils.show(f'error: command \'{command}\' does not take input')
			return
		pycode.pcunmax()
	elif command == 'min':
		if commandinput:
			utils.show(f'error: command \'{command}\' does not take input')
			return
		pycode.pcmin()
	elif command == 'clear':
		if commandinput:
			utils.show(f'error: command \'{command}\' does not take input')
			return
		pycode.pccleareditor()
	elif command == 'pycode' or command == 'pc':
		if commandinput:
			utils.show(f'error: command \'{command}\' does not take input')
			return
		pycode.pc()
	elif command == 'ab' or command == 'abt' or command == 'about' or command == 'pynotes':
		if commandinput:
			utils.show(f'error: command \'{command}\' does not take input')
			return
		help.abt()
	elif not (getattr(state.active, 'hmode', False) in ['png', 'pdf', 'epub']) and command == 'hmode':
		if not commandinput:
			utils.show(f'error: no input given to command \'{command}\'')
			return
		if not (commandinput in ('python', 'py', 'latex', 'la', 'normal', 'norm', 'email', 'em', 'html', 'markdown', 'md') or commandinput in state.plgnhmodes):
			utils.show(f'hmode \'{commandinput}\' does not exist')
			return
		if not isinstance(state.active, editor.Editor):
			utils.show('not an editor')
			return
		try:
			state.active.pchmode(commandinput)
		except Exception:
			utils.show(f'error: invalid command \'{command}\'')
	elif command == 'pynavstart' or command == 'pyjumpstart' or command == 'python-jump-startof':
		if not commandinput:
			utils.show(f'error: no input given to command \'{command}\'')
			return
		pycode.pcpystartof(commandinput)
	elif command == 'pynavend' or command == 'pyjumpend' or command == 'python-jump-endof':
		if not commandinput:
			utils.show(f'error: no input given to command \'{command}\'')
			return
		pycode.pcpyendof(commandinput)
	elif command == 'pygodef' or command == 'python-go-definition':
		if not commandinput:
			utils.show(f'error: no input given to command \'{command}\'')
			return
		pycode.pcgodef(commandinput)
	else:
		utils.show(text = f'error: invalid command \'{command}\'')
	pycode.pcrunhook('after', f'alt-x-command:{command}', commandinput)
def cmdallhmodenames():
	return ['python', 'latex', 'normal', 'email', 'html', 'markdown'] + list(state.plgnhmodes)
def cmdhmodevalues(currentinput):
	return list(('python', 'py', 'latex', 'la', 'normal', 'norm', 'email', 'em', 'html', 'markdown', 'md')) + list(state.plgnhmodes)
def cmdpynavvalues(currentinput):
	if state.active is None or state.active.hmode != 'python':
		return []
	return ['f', 'fun', 'func', 'function', 'c', 'class'] + sorted(set(dname for dl, dc, dname, dkind in state.active._python_def_names))
def cmdpygodefvalues(currentinput):
	if state.active is None or state.active.hmode != 'python':
		return []
	return sorted(set(name for scope in state.active._python_scopes for name in scope['names']))
def cmdrevalues(currentinput):
	if currentinput.startswith('('):
		closeindex = cmdfindgroupclose(currentinput, 0)
		if closeindex is None:
			return ['(' + candidate for candidate in cmdautocompletefunc(currentinput[1:])]
		return []
	if '*' in currentinput:
		content, multiplier = currentinput.split('*', 1)
		return [candidate + '*' + multiplier for candidate in cmdautocompletefunc(content)]
	return cmdautocompletefunc(currentinput)
def cmdregister(names, hmodes = None, inputs = None):
	for name in names:
		cmdregistry[name] = {'hmodes': hmodes, 'inputs': inputs}
cmdregistry = {}
cmdregister(('exit', 'e'))
cmdregister(('sh', 'splithoriz', 'split-editor-horizontal'))
cmdregister(('sv', 'splitvert', 'split-editor-vertical'))
cmdregister(('setsel', 'selpointset', 'selection-point-set'))
cmdregister(('unsetsel', 'selpointunset', 'selection-point-remove'))
cmdregister(('bb', 'balance', 'balance-buffers'), inputs = [None, 'h', 'horiz', 'horizontal', 'v', 'vert', 'vertical'])
cmdregister(('cb', 'close', 'closecurbuf', 'close-current-buffer'))
cmdregister(('sw', 'switch', 'switchbuf', 'switch-buffer'))
cmdregister(('sol', 'startofline'))
cmdregister(('eol', 'endofline'))
cmdregister(('neh', 'newedithoriz', 'new-editor-horizontal'))
cmdregister(('nev', 'neweditvert', 'new-editor-vertical'))
cmdregister(('onh', 'opennewhoriz', 'open-file-horizontal'))
cmdregister(('onv', 'opennewvert', 'open-file-vertical'))
cmdregister(('changes', 'ch'))
cmdregister(('run',), hmodes = ('python', 'latex', 'html'))
cmdregister(('ms', 'mark', 'markset', 'mark-selection'))
cmdregister(('unms', 'unmark', 'unmark-selection'))
cmdregister(('sendemail', 'sendmail'), hmodes = ('email',))
cmdregister(('unma', 'unmarkall'))
cmdregister(('comment', 'cr', 'comment-region'), hmodes = ('python', 'latex', 'html', 'markdown'))
cmdregister(('uncomment', 'uncr', 'uncomment-region'), hmodes = ('python', 'latex', 'html', 'markdown'))
cmdregister(('pyshell', 'ps'), hmodes = ('python',))
cmdregister(('fullup',))
cmdregister(('fulldown',))
cmdregister(('editor', 'ed'))
cmdregister(('h', 'help'), inputs = ['x', 'commands', 'em', 'email', 'pc', 'pycode', 'mg', 'mathgod', 'pl', 'plugins'])
cmdregister(('st', 'speech-to-text'))
cmdregister(('opd', 'openplugindir'))
cmdregister(('dp', 'downloadplugins'))
cmdregister(('indent-region', 'ir'))
cmdregister(('unindent-region', 'unir'))
cmdregister(('te', 'termexec'), inputs = [])
cmdregister(('mathgod', 'mg'))
cmdregister(('write', 'w'), inputs = [])
cmdregister(('repeat', 're'), inputs = cmdrevalues)
cmdregister(('u', 'undo'))
cmdregister(('r', 'redo'))
cmdregister(('save', 's'))
cmdregister(('saveas', 'sa'))
cmdregister(('search', 'f'), inputs = [None, 'b', 'back'])
cmdregister(('find-replace', 'findreplace', 'fr'), inputs = [None, 'b', 'back'])
cmdregister(('show-source', 'source-code'))
cmdregister(('new', 'n'))
cmdregister(('l', 'gl', 'gotoline'))
cmdregister(('open', 'find', 'o', 'load'))
cmdregister(('terminal', 'cmd', 'term', 't'))
cmdregister(('prf', 'preferences'))
cmdregister(('cancel', 'z'))
cmdregister(('a', 'selall', 'all'))
cmdregister(('copy', 'c'))
cmdregister(('cut',))
cmdregister(('pf', 'pagenext'))
cmdregister(('pb', 'pageback'))
cmdregister(('paste', 'p'))
cmdregister(('sp', 'speak'))
cmdregister(('full',))
cmdregister(('unfull',))
cmdregister(('max', 'maximize'))
cmdregister(('unmax', 'unmaximize'))
cmdregister(('min',))
cmdregister(('clear',))
cmdregister(('pycode', 'pc'))
cmdregister(('ab', 'abt', 'about', 'pynotes'))
cmdregister(('pynavstart', 'pyjumpstart', 'python-jump-startof'), hmodes = ('python',), inputs = cmdpynavvalues)
cmdregister(('pynavend', 'pyjumpend', 'python-jump-endof'), hmodes = ('python',), inputs = cmdpynavvalues)
cmdregister(('pygodef', 'python-go-definition'), hmodes = ('python',), inputs = cmdpygodefvalues)
cmdregister(('hmode',), hmodes = cmdallhmodenames, inputs = cmdhmodevalues)
def cmdregistryentry(name):
	return cmdregistry.get(name, {'hmodes': None, 'inputs': None})
def cmdhmodeavailable(hmodes):
	if hmodes is None:
		return True
	if callable(hmodes):
		hmodes = hmodes()
	if state.active is None:
		return False
	return state.active.hmode in hmodes
def cmdinputvariants(inputs):
	if inputs is None:
		return True, False
	if not isinstance(inputs, list):
		return False, True
	hasnone = None in inputs
	hasvalues = any(item is not None for item in inputs)
	if hasnone and not hasvalues:
		return True, False
	if hasnone and hasvalues:
		return True, True
	return False, True
def cmdbasecommandnames():
	names = list(cmdregistry)
	names.extend(name for name in state.plgncmds if name not in cmdregistry)
	names.extend(name for name in state.pcwrittencommands if name not in cmdregistry)
	basecommandnames = []
	for name in names:
		entry = cmdregistryentry(name)
		if not cmdhmodeavailable(entry['hmodes']):
			continue
		showbare, showcolon = cmdinputvariants(entry['inputs'])
		if showbare:
			basecommandnames.append(name)
		if showcolon:
			basecommandnames.append(name + ':')
	return basecommandnames
def cmdcommandvalues(command, currentinput):
	entry = cmdregistryentry(command)
	if not cmdhmodeavailable(entry['hmodes']):
		return []
	inputs = entry['inputs']
	if inputs is None:
		return []
	if not isinstance(inputs, list):
		return inputs(currentinput)
	return [item for item in inputs if item is not None]
def cmdactivesegment(typedtext):
	prefix = ''
	while True:
		stripped = typedtext.lstrip()
		if stripped != typedtext:
			prefix += typedtext[:len(typedtext) - len(stripped)]
			typedtext = stripped
			continue
		parts = cmdsplit(typedtext)
		if len(parts) > 1:
			prefix += typedtext[:len(typedtext) - len(parts[-1])]
			typedtext = parts[-1]
			continue
		break
	return prefix, typedtext
def cmdautocompletefunc(typedtext):
	prefix, activesegment = cmdactivesegment(typedtext)
	if ':' in activesegment:
		commandpart, valuepart = activesegment.split(':', 1)
		valuestripped = valuepart.lstrip()
		valueprefix = valuepart[:len(valuepart) - len(valuestripped)]
		values = cmdcommandvalues(commandpart, valuestripped)
		if not values:
			return []
		return [prefix + commandpart + ':' + valueprefix + value for value in sorted(values) if value.startswith(valuestripped)]
	candidates = [name for name in cmdbasecommandnames() if name.startswith(activesegment)]
	return [prefix + candidate for candidate in candidates]
def cmd():
	cmdrun(utils.prompt('Alt-X- ', cmdautocompletefunc))
	state.root.update()
	if hasattr(state.active, 'keypress'):
		state.active.keypress()
