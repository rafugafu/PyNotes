from init import exit
import state
import os
import sys
import select
import queue
import subprocess
import shutil
import threading
claht = '''\
\x1b[1mCommand line arguments:\x1b[0m
\x1b[3m--version\x1b[0m: Print the current PyNotes version number.
\x1b[3m--changes\x1b[0m: Print the current PyNotes version's changelog.
\x1b[3m--wait-start\x1b[0m: Does not launch the PyNotes window till 'start' is typed into the console.
\x1b[3m--plugin-list-github\x1b[0m: List the plugins on the PyNotes GitHub with a one line description for each.
\x1b[3m--plugin-list-installed\x1b[0m: List the currently installed plugins with a one line description for each if provided.
\x1b[3m--plugin-install "name"\x1b[0m: Installs the given plugin from the PyNotes GitHub if present.
\x1b[3m--plugin-remove "name"\x1b[0m: Uninstalls the given plugin if installed.
\x1b[3m--plugin-describe "name"\x1b[0m: Give a full description of the given plugin if installed and provided, fallback to checking in the PyNotes GitHub if not.
\x1b[3m--no-load-pycode\x1b[0m: Start PyNotes without loading your PyCode configuration until you open and close PyCode yourself.
\x1b[3m--no-load-plugins\x1b[0m: Start PyNotes without loading any plugins.
\x1b[3m--pycode-exec "string"\x1b[0m: Execute the given string as PyCode after loading your normal configuration.
\x1b[3m--command-exec "string"\x1b[0m: Execute the given string as Alt-X commands.\
'''
clcht = '''\
\x1b[1mConsole:\x1b[0m
PyNotes has a live cli console in the launching terminal which can interact with and control PyNotes while it runs. Commands:
'\x1b[3mstart\x1b[0m' - Finally shows the PyNotes window if the \x1b[3m--wait-start\x1b[0m option was used.
'\x1b[3mcommand-exec {command}\x1b[0m' - Runs the given command as an Alt-X command after 'start' is done.
'\x1b[3mpycode-eval {command}\x1b[0m' - Directly takes and evaluates a single PyCode expression after 'start' is done.
'\x1b[3mextra-pycode\x1b[0m' - If the \x1b[3m--wait-start\x1b[0m option was used, take normal PyCode code as if it was passed to --pycode-exec at the start until exactly 'DONE' or 'CANCEL' is typed on a new line before 'start' is done. If 'CANCEL' is typed, it cancels the whole command.
'\x1b[3mopen-file {optional filename}\x1b[0m' - Prompts for a filename if not given directly and opens it in a new editor after 'start' is done.
'\x1b[3mexit\x1b[0m' / '\x1b[3mclose\x1b[0m' - Cleanly exits PyNotes after prompting to save files and close running processes.
'\x1b[31m\x1b[3mkill\x1b[0m' - Forcefully kills PyNotes without saving any files or cleaning up.
'\x1b[3mrun {optional command}\x1b[0m' - Prompts for a shell command to run in the same terminal if not given directly and runs it.
'\x1b[3mclear\x1b[0m' - Clears the terminal screen.
'\x1b[3mhelp\x1b[0m'- Shows help on the PyNotes terminal console (this screen).\
'''
def argparse(options, args):
	options = {key: (item if item != [True] else []) for key, item in options.copy().items()}
	exitwith = lambda message: [print(message), exit(1)]
	curarg = None
	files_to_open = []
	for arg in args:
		if not curarg and not arg.startswith('--'):
			files_to_open.append(arg)
			continue
		if curarg and options[curarg] in (False, None) and not arg.startswith('--'):
			files_to_open.append(arg)
			continue
		if arg.startswith('--'):
			if curarg and options[curarg] not in (False, None):
				exitwith(f'unexpected "{arg}" after option "--{curarg}"')
			arg = arg[2:]
		if curarg and options[curarg] in (False, None):
			curarg = None
		if not curarg:
			if '=' in arg:
				opn, opv = arg.split('=', 1)
				if opn not in options:
					exitwith(f'error: unknown option "--{opn}"')
				if options[opn] == True:
					options[opn] = opv
				elif type(options[opn]) == list:
					options[opn].append(opv)
				elif options[opn] in (False, None):
					exitwith(f'error: option "--{opn}" does not take any argument')
				else:
					exitwith(f'error: repeated argument "--{arg}"')
			else:
				if arg not in options:
					exitwith(f'error: unknown option "--{arg}"')
				if options[arg] == True or type(options[arg]) == list:
					curarg = arg
				elif options[arg] == False:
					curarg = arg
					options[arg] = None
				else:
					exitwith(f'error: repeated argument "--{arg}"')
		elif curarg:
			if type(options[curarg]) == list:
				options[curarg].append(arg)
			else:
				options[curarg] = arg
			curarg = None
	if curarg and options[curarg] not in (False, None):
		exitwith(f'error: unspecified option "{curarg}"')
	for option in options:
		if options[option] is None:
			options[option] = True
		elif options[option] == True:
			options[option] = None
	return options, files_to_open
_CANCELLED = object()
class _ConsoleRequest:
	def __init__(self, kind, args):
		self.kind = kind
		self.args = args
		self.cancel = threading.Event()
		self.resultq = queue.Queue()
class Console:
	def __init__(self, consoleq):
		import init
		self.outpt = lambda *args, **kwargs: print(*args, **kwargs, file = state.stdout, flush = True)
		self.inpt = lambda *args, **kwargs: [self.outpt(*args, **kwargs, end = ''), input()][1]
		self.dialoglock = threading.Lock()
		self.q = consoleq
		self.requestq = queue.Queue()
		self.outpt('\x1b[H\x1b[2J', end = '')
		self.outpt(f'\x1b[1mPyNotes terminal console. PyNotes v{init.v}.\x1b[0m')
	def _cancellable_inpt(self, prompt_text, cancel_event = None):
		self.outpt(prompt_text, end = '')
		while True:
			ready, _, _ = select.select([sys.stdin], [], [], 0.15)
			if ready:
				line = sys.stdin.readline()
				if line == '':
					raise EOFError
				return line.rstrip('\n')
			if cancel_event is not None and cancel_event.is_set():
				return _CANCELLED
	def _read_console_line(self, prompt_text):
		self.outpt(prompt_text, end = '')
		while True:
			ready, _, _ = select.select([sys.stdin], [], [], 0.15)
			if ready:
				line = sys.stdin.readline()
				if line == '':
					raise EOFError
				return line.rstrip('\n')
			if not self.requestq.empty():
				self._service_one_request()
	def _service_one_request(self):
		try:
			request = self.requestq.get_nowait()
		except queue.Empty:
			return
		if request.cancel.is_set():
			request.resultq.put(None)
			return
		if request.kind == 'ask':
			title, question, options, color = request.args
			result = self.ask(title, question, options, color, request.cancel)
		else:
			title, text, color = request.args
			result = self.prompt(title, text, color, request.cancel)
		request.resultq.put(None if result is _CANCELLED else result)
	def ask_async(self, title, question, options, color = '100m'):
		request = _ConsoleRequest('ask', (title, question, list(options), color))
		self.requestq.put(request)
		return request
	def prompt_async(self, title, text, color = '100m'):
		request = _ConsoleRequest('prompt', (title, text, color))
		self.requestq.put(request)
		return request
	def cancel_request(self, request):
		request.cancel.set()
	def show(self, text):
		with self.dialoglock:
			if not (text := text.strip()):
				return
			if self.n:
				moveback = f'\x1b[{self.n}B'
			else:
				moveback = ''
			if self.helping:
				moveback = '\x1b[H'
			self.outpt(f'\x1b7{moveback}\x1b[L\r\x1b[7mmessage: \x1b[3m{text}\x1b[0m\x1b8\x1b[B', end = '')
	def dialog(self, title, message, color = '100m'):
		with self.dialoglock:
			import textwrap
			width = min(shutil.get_terminal_size()[0], 80)
			if len(title) > width:
				title = title[: width - 3] + '...'
			text = textwrap.fill(message, width = width) + '\n'
			spacing = ' ' * ((width - len(title)) // 2)
			if self.n:
				moveback = f'\x1b[{self.n}B'
			else:
				moveback = ''
			if self.helping:
				moveback = '\x1b[H'
			text = '\n'.join(line.ljust(width) for line in text.split('\n'))
			self.outpt(f'\x1b7{moveback}\x1b[L\r\x1b[{color}\x1b[7m{spacing}\x1b[1m{title}\x1b[22m{spacing}{" " * ((width - len(title)) % 2)}\x1b[27m\n{text}\x1b[0m\x1b8\x1b[{text.count("\n") + 2}B'.replace('\n', f'\x1b[49m\n\x1b[L\x1b[{color}'), end = '')
	def ask(self, title, question, options, color = '100m', cancel_event = None):
		with self.dialoglock:
			import textwrap
			width = min(shutil.get_terminal_size()[0], 80)
			if len(title) > width:
				title = title[: width - 3] + '...'
			text = textwrap.fill(question, width = width) + '\n'
			spacing = ' ' * ((width - len(title)) // 2)
			if self.n:
				moveback = f'\x1b[{self.n}B'
			else:
				moveback = ''
			if self.helping:
				moveback = '\x1b[H'
			text = '\n'.join(line.ljust(width) for line in text.split('\n'))
			optionstext = ''
			optiontotalwidth = 0
			row = []
			for optioni in range(len(options)):
				option = textwrap.fill(f'{optioni + 1}. {options[optioni]}', width = width)
				if optiontotalwidth + len(option) > width:
					optionspacing = ' ' * ((width - optiontotalwidth) // ((len(row) - 1) or 1))
					current = optionspacing.join(row)
					optionstext += current + ' ' * max(0, width - len(current.split('\n')[-1].replace('\x1b[7m', '').replace('\x1b[1m', '').replace('\x1b[22m', '').replace('\x1b[27m', ''))) + '\n' + ' ' * width + '\n'
					optiontotalwidth = 0
					row = []
				optiontotalwidth += len(option)
				row.append(f'\x1b[7m\x1b[1m{option}\x1b[22m\x1b[27m')
			optionspacing = ' ' * ((width - optiontotalwidth) // ((len(row) - 1) or 1))
			current = optionspacing.join(row)
			optionstext += current + ' ' * max(0, width - len(current.split('\n')[-1].replace('\x1b[7m', '').replace('\x1b[1m', '').replace('\x1b[22m', '').replace('\x1b[27m', ''))) + '\n'
			self.outpt(f'\x1b7{moveback}\x1b[L\r\x1b[{color}\x1b[7m{spacing}\x1b[1m{title}\x1b[22m{spacing}{" " * ((width - len(title)) % 2)}\x1b[27m\n{text}\n{optionstext}\x1b[0m'.replace('\n', f'\x1b[49m\n\x1b[L\x1b[{color}'), end = '')
			options = range(1, optioni + 2)
			optionpromptslash = '/'.join(map(str, options))
			restore = lambda: self.outpt(f'\x1b8\x1b[{optionstext.count("\n") + text.count("\n") + 3}B', end = '')
			gotinput = self._cancellable_inpt(f'\x1b[7m\x1b[1mselect ({optionpromptslash}):\x1b[0m ', cancel_event)
			if gotinput is _CANCELLED:
				restore()
				return _CANCELLED
			gotinput = gotinput.strip().lower()
			try:
				gotinput = int(gotinput)
			except Exception:
				pass
			if not gotinput in options:
				while not gotinput in options:
					gotinput = self._cancellable_inpt(f'\x1b[A\r\x1b[K\x1b[7m\x1b[1m\x1b[31m[invalid input]\x1b[39m select ({optionpromptslash}):\x1b[0m ', cancel_event)
					if gotinput is _CANCELLED:
						restore()
						return _CANCELLED
					gotinput = gotinput.strip().lower()
					try:
						gotinput = int(gotinput)
					except Exception:
						pass
			restore()
			return gotinput
	def prompt(self, title, text, color = '100m', cancel_event = None):
		with self.dialoglock:
			import textwrap
			width = min(shutil.get_terminal_size()[0], 80)
			if len(title) > width:
				title = title[: width - 3] + '...'
			text = textwrap.fill(text, width = width) + '\n'
			spacing = ' ' * ((width - len(title)) // 2)
			if self.n:
				moveback = f'\x1b[{self.n}B'
			else:
				moveback = ''
			if self.helping:
				moveback = '\x1b[H'
			text = '\n'.join(line.ljust(width) for line in text.split('\n'))
			self.outpt(f'\x1b7{moveback}\x1b[L\r\x1b[{color}\x1b[7m{spacing}\x1b[1m{title}\x1b[22m{spacing}{" " * ((width - len(title)) % 2)}\x1b[27m\n{text}\n\x1b[0m'.replace('\n', f'\x1b[49m\n\x1b[L\x1b[{color}'), end = '')
			gotinput = self._cancellable_inpt(f'\x1b[7m\x1b[1mprompt:\x1b[0m ', cancel_event)
			self.outpt(f'\x1b8\x1b[{text.count("\n") + 3}B', end = '')
			if gotinput is _CANCELLED:
				return _CANCELLED
			return gotinput
	def loop(self):
		while True:
			try:
				self.n = 0
				self.helping = False
				command, commandinput = (self._read_console_line('> ').strip() + ' ').split(' ', 1)
				command = command.strip()
				commandinput = commandinput.strip()
				if not command:
					continue
				if command == 'start':
					if not state.started.is_set():
						self.outpt('\x1b[32mstarting pynotes.\x1b[0m')
						state.started.set()
					else:
						self.outpt('\x1b[31merror: pynotes has already started.\x1b[0m')
				elif command == 'command-exec':
					if not commandinput:
						self.outpt('\x1b[33mcancelled.\x1b[0m')
						continue
					if not state.started.is_set():
						self.outpt(f'\x1b[33mwill execute alt-x command \'\x1b[3m{commandinput}\x1b[23m\' on pynotes start.\x1b[0m')
					else:
						self.outpt(f'\x1b[32mexecuting alt-x command \'\x1b[3m{commandinput}\x1b[23m\'.\x1b[0m')
					self.q.put(('command-exec', commandinput))
				elif command == 'pycode-eval':
					if not commandinput:
						self.outpt('\x1b[33mcancelled.\x1b[0m')
						continue
					if not state.started.is_set():
						self.outpt(f'\x1b[33mwill evaluate pycode \'\x1b[3m{commandinput}\x1b[23m\' on pynotes start.\x1b[0m')
					else:
						self.outpt(f'\x1b[32mevaluating pycode expression \'\x1b[3m{commandinput}\x1b[32m\'.\x1b[0m')
					self.q.put(('pycode-eval', commandinput))
				elif command == 'extra-pycode':
					if commandinput:
						self.outpt('\x1b[31merror: input given to \x1b[3mextra-pycode\x1b[23m command.\x1b[0m')
						continue
					if state.started.is_set():
						self.outpt('\x1b[31merror: pynotes has already started.\x1b[3m')
						continue
					expc = ''
					while True:
						self.n += 1
						nl = self.inpt('extra-pycode> ').strip()
						if nl == 'DONE':
							break
						elif nl == 'CANCEL':
							expc = ''
							break
						expc += nl
					if not expc:
						self.outpt('\x1b[33mcancelled.\x1b[0m')
						continue
					if state.options['pycode-exec']:
						state.options['pycode-exec'] += ';' + expc
					else:
						state.options['pycode-exec'] = expc
					self.outpt('\x1b[32madded extra pycode to run on pynotes start.\x1b[0m')
				elif command == 'open-file':
					if commandinput:
						filetoopen = commandinput
					else:
						filetoopen = self.inpt('file to open: ')
						self.outpt('\r\x1b[A\x1b[K', end = '')
					if not filetoopen:
						self.outpt('\x1b[33mcancelled.\x1b[0m')
						continue
					self.outpt(f'\x1b[A\x1b[K> open-file {filetoopen}')
					filetoopen = os.path.abspath(os.path.expanduser(filetoopen))
					if not os.path.exists(filetoopen):
						self.outpt(f'\x1b[33mfile \'\x1b[3m{filetoopen}\x1b[23m\' does not exist, creating file.\x1b[0m')
					if state.started.is_set():
						self.outpt(f'\x1b[32mopening file \'\x1b[3m{filetoopen}\x1b[23m\'.\x1b[0m')
						self.q.put(('open-file', filetoopen))
					else:
						self.outpt(f'\x1b[33mfile \'\x1b[3m{filetoopen}\x1b[23m\' will be opened on pynotes start.\x1b[0m')
						state.files_to_open.append(filetoopen)
				elif command in ('exit', 'close'):
					if commandinput:
						self.outpt(f'\x1b[31merror: input given to \x1b[3mclose\x1b[23m command.\x1b[0m')
						continue
					self.outpt(f'\x1b[32mclosing pynotes.\x1b[0m')
					if state.started.is_set():
						self.q.put(('close',))
					else:
						os._exit(0)
				elif command == 'kill':
					if commandinput:
						self.outpt(f'\x1b[31merror: input given to \x1b[3mkill\x1b[23m command.\x1b[0m')
						continue
					userinput = (self.inpt('\x1b[33mkill pynotes? (y/n): \x1b[0m').strip() + 'g')[0].lower()
					if not userinput in ('y', 'n'):
						for i in range(2):
							self.outpt('\r\x1b[A\x1b[K', end = '')
							userinput = (self.inpt(f'\x1b[31m[invalid input ({i + 2}/3)]\x1b[0m \x1b[33mkill pynotes? (y/n): \x1b[0m').strip() + 'g')[0].lower()
							if userinput in ('y', 'n'):
								break
							else:
								userinput = 'n'
					if userinput != 'y':
						self.outpt('\r\x1b[A\x1b[K\x1b[32mcancelled.\x1b[0m')
						continue
					else:
						self.outpt('\x1b[31mkilling pynotes.\x1b[0m')
						os._exit(0)
				elif command == 'run':
					if commandinput:
						torun = commandinput
					else:
						torun = self.inpt('command to run: ').strip()
					if not torun:
						self.outpt('\r\x1b[A\x1b[K\x1b[33mcancelled.\x1b[0m')
						continue
					subprocess.run(torun, shell = True, stdout = state.stdout, stderr = state.stderr)
				elif command == 'clear':
					if commandinput:
						self.outpt('\x1b[31merror: input given to \x1b[3mclear\x1b[23m command.\x1b[0m')
						continue
					self.outpt('\x1b[H\x1b[2J\x1b[3J', end = '')
				elif command == 'help':
					if commandinput:
						self.outpt('\x1b[31merror: input given to \x1b[3mhelp\x1b[23m command.\x1b[0m')
						continue
					self.helping = True
					self.outpt('\x1b[?1049h', end = '')
					self.outpt(clcht)
					self.inpt('\x1b[33m\x1b[1m[PRESS ENTER TO CONTINUE]\x1b[0m')
					self.outpt('\x1b[?1049l', end = '')
					self.helping = False
					self.outpt('\x1b[32m\x1b[3mhelp text shown\x1b[0m')
				else:
					self.outpt(f'\x1b[31merror: invalid command \'\x1b[3m{command}\x1b[23m\'.\x1b[0m')
			except Exception:
				break
def start_console(consoleq):
	state.console = Console(consoleq)
	state.console.loop()
	return state.console
