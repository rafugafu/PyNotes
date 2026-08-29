import os
import platform
import subprocess
import codecs
import base64
import re
import threading
import time
import easytk
import state
from init import monospace
if platform.system() != 'Linux':
	from winpty import PtyProcess
from buffer import Buffer, DEBOUNCE_TIME
from utils import bindrecur
import pycode
import utils
import window
def termexec(command):
	pycode.pcrunhook('before', 'term-exec', command)
	if command[:2] == 'cd':
		try:
			os.chdir(command[3:])
		except Exception as error:
			item = str(error)
		else:
			item = ''
	else:
		try:
			result = subprocess.run(command, shell = True, text = True, capture_output = True, timeout = 5)
			item = result.stdout + result.stderr
		except Exception as error:
			item = str(error)
	pycode.pcrunhook('after', 'term-exec', command)
	return item
_TERM_FRAME_MS = 16
_TERM_FRAME_BUDGET = 0.008
_PTY_MAX_PENDING_ESC = 4096
def _sgr_is_highlight(params):
	result = None
	idx = 0
	while idx < len(params):
		code = params[idx]
		if code == 0:
			result = False
		elif code == 7:
			result = True
		elif code == 27 or code == 49:
			result = False
		elif code in (41, 42, 43, 44, 45, 46, 47) or (100 <= code <= 107):
			result = True
		elif code == 40:
			result = False
		elif code == 48:
			result = True
			if idx + 1 < len(params) and params[idx + 1] == 5:
				idx += 2
			elif idx + 1 < len(params) and params[idx + 1] == 2:
				idx += 4
		idx += 1
	return result
_TERM_ANSI_16_HEX = ('#000000', '#cd0000', '#00cd00', '#cdcd00', '#0000ee', '#cd00cd', '#00cdcd', '#e5e5e5', '#7f7f7f', '#ff0000', '#00ff00', '#ffff00', '#5c5cff', '#ff00ff', '#00ffff', '#ffffff')
_TERM_ANSI_CUBE_LEVELS = (0, 95, 135, 175, 215, 255)
def _ansi_256_hex(n):
	if n < 16:
		return _TERM_ANSI_16_HEX[n]
	if n < 232:
		n -= 16
		return f'#{_TERM_ANSI_CUBE_LEVELS[n // 36]:02x}{_TERM_ANSI_CUBE_LEVELS[(n % 36) // 6]:02x}{_TERM_ANSI_CUBE_LEVELS[n % 6]:02x}'
	v = 8 + (n - 232) * 10
	return f'#{v:02x}{v:02x}{v:02x}'
def _sgr_new_state():
	return {'fg': None, 'bg': None, 'bold': False, 'italic': False, 'underline': False, 'reverse': False, 'blink': False}
def _sgr_apply(state, params):
	if not params:
		params = [0]
	i = 0
	while i < len(params):
		c = params[i]
		if c == 0:
			state.update(fg = None, bg = None, bold = False, italic = False, underline = False, reverse = False, blink = False)
		elif c == 1:
			state['bold'] = True
		elif c == 3:
			state['italic'] = True
		elif c == 4:
			state['underline'] = True
		elif c == 5 or c == 6:
			state['blink'] = True
		elif c == 7:
			state['reverse'] = True
		elif c == 22:
			state['bold'] = False
		elif c == 23:
			state['italic'] = False
		elif c == 24:
			state['underline'] = False
		elif c == 25:
			state['blink'] = False
		elif c == 27:
			state['reverse'] = False
		elif 30 <= c <= 37:
			state['fg'] = c - 30
		elif c == 38:
			if i + 2 < len(params) and params[i + 1] == 5:
				state['fg'] = params[i + 2]; i += 2
			elif i + 4 < len(params) and params[i + 1] == 2:
				state['fg'] = (params[i + 2], params[i + 3], params[i + 4]); i += 4
		elif c == 39:
			state['fg'] = None
		elif 40 <= c <= 47:
			state['bg'] = c - 40
		elif c == 48:
			if i + 2 < len(params) and params[i + 1] == 5:
				state['bg'] = params[i + 2]; i += 2
			elif i + 4 < len(params) and params[i + 1] == 2:
				state['bg'] = (params[i + 2], params[i + 3], params[i + 4]); i += 4
		elif c == 49:
			state['bg'] = None
		elif 90 <= c <= 97:
			state['fg'] = c - 90 + 8
		elif 100 <= c <= 107:
			state['bg'] = c - 100 + 8
		i += 1
def _sgr_colour_hex(c):
	if c is None:
		return None
	if isinstance(c, tuple):
		return f'#{c[0]:02x}{c[1]:02x}{c[2]:02x}'
	return _ansi_256_hex(c)
def _term_sgr_resolve(state, default_fg, default_bg):
	fg = default_fg if state['fg'] is None else _sgr_colour_hex(state['fg'])
	bg = default_bg if state['bg'] is None else _sgr_colour_hex(state['bg'])
	if state['bold'] and isinstance(state['fg'], int) and state['fg'] < 8:
		fg = _ansi_256_hex(state['fg'] + 8)
	if state['reverse']:
		oldfg = fg
		fg = bg if bg is not None else default_bg
		bg = oldfg if oldfg is not None else default_fg
	return fg, bg
class Terminal(easytk.ttk.Text):
	_term_csi_keys = {'Up': 'A', 'Down': 'B', 'Right': 'C', 'Left': 'D', 'Home': 'H', 'End': 'F'}
	_term_tilde_keys = {'Insert': '2', 'Delete': '3', 'Prior': '5', 'Next': '6', 'F5': '15', 'F6': '17', 'F7': '18', 'F8': '19', 'F9': '20', 'F10': '21', 'F11': '23', 'F12': '24'}
	_term_ss3_keys = {'F1': 'P', 'F2': 'Q', 'F3': 'R', 'F4': 'S'}
	def __init__(self, master, command, endmessage, nocolor = False, *args, **kwargs):
		kwargs.setdefault('font', (monospace, 12))
		kwargs.setdefault('wrap', 'none')
		super().__init__(master, *args, **kwargs)
		if not command:
			utils.show('open pynotes terminal')
		import queue as _queue
		self.endmessage = endmessage
		self.nocolor = nocolor
		self._term_command = command
		self._GRID_COLS = 1
		self._GRID_ROWS = 1
		self._VT_ROWS = 1
		self._term_default_bg = self.cget('background')
		self._term_default_fg = self.cget('foreground')
		self._default_fg_rgb = self.winfo_rgb(self._term_default_fg)
		self._default_bg_rgb = self.winfo_rgb(self._term_default_bg)
		self.config(insertbackground = self._term_default_fg, blockcursor = True)
		self.running = True
		self._closed = False
		self._out_q = _queue.Queue(maxsize = 64)
		self.cursor = '1.0'
		self.screen_top = 1
		self._cur_line = 1
		self._saved_cursor = None
		self._saved_sgr = None
		self._tab_stops = set()
		self._pending_esc = ''
		self._sgr_state = _sgr_new_state()
		self._sgr_tags_done = set()
		self._blink_tags = {}
		self._blink_visible = True
		self._blink_after_id = None
		self._bracketed_paste = False
		self._focus_reporting = False
		self._autowrap = True
		self._app_cursor = False
		self._mouse_mode = 0
		self._mouse_sgr = False
		self._mouse_last_pos = None
		self.tag_configure('sel', background = self._term_default_fg, foreground = self._term_default_bg)
		self.tag_configure('wrapcont')
		self._sgr_tag_cache = None
		self._alt_saved = None
		self._alt_mode = False
		self._reverse_screen = False
		self._origin_mode = False
		self._scroll_top = 1
		self._scroll_bot = self._GRID_ROWS
		self._resize_after_id = None
		self._last_term_size = (0, 0)
		self._term_started = False
		self._polling = False
		self._read_generation = 0
		self._follow_bottom = True
		self._poll_after_id = None
		self._termmenu = state.root.menu(master = self)
		self._termmenu.add_command(label = 'Copy', command = self._copy_selection)
		self._termmenu.add_command(label = 'Paste', command = self._paste_clipboard)
		self._termmenu.add_separator()
		self._termmenu.add_command(label = 'Select All', command = self._select_all)
		self._menu_posted = False
		self._termmenu.bind('<KeyPress>', self._termmenu_keyclose)
		self._termmenu.bind('<Unmap>', lambda e: setattr(self, '_menu_posted', False))
		self.bind('<Key>', self._key)
		self.bind('<ISO_Left_Tab>', self._key)
		self.bind('<Control-Key>', self._key)
		self.bind('<Meta-Key>', self._meta_key)
		self.bind('<Alt-Key>', self._meta_key)
		self.bind('<Control-x>', self._key)
		self.bind('<Control-w>', self._key)
		self.bind('<Control-c>', self._key)
		self.bind('<Control-v>', self._key)
		self.bind('<Control-y>', self._key)
		self.bind('<Meta-w>', self._meta_key)
		self.bind('<FocusIn>', self._focus_in)
		self.bind('<FocusOut>', self._focus_out)
		self.bind('<<ThemeChanged>>', self._term_on_theme_changed)
		self.bind('<Button-1>', self._term_button1_press)
		self.bind('<ButtonRelease-1>', self._term_button1_release)
		self.bind('<B1-Motion>', self._term_button1_motion)
		self.bind('<Button-3>', self._term_button3_press)
		self.bind('<ButtonRelease-3>', self._term_button3_release)
		self.bind('<B3-Motion>', self._term_button3_motion)
		self.bind('<Button-2>', self._term_button2_press)
		self.bind('<B2-Motion>', self._term_button2_motion)
		self.bind('<ButtonRelease-2>', self._term_button2_release)
		self.bind('<Motion>', self._term_motion)
		self.bind('<Button-4>', self._term_wheel)
		self.bind('<Button-5>', self._term_wheel)
		self.bind('<MouseWheel>', self._term_wheel)
		self.bind('<<PasteSelection>>', lambda e: 'break')
		self.bind('<<Clear>>', lambda e: 'break')
		self.bind('<Control-Shift-C>', self._copy_selection)
		self.bind('<Control-Shift-A>', self._select_all)
		self.edit_modified(False)
		self.bind('<<Modified>>', self._on_modified)
		self.bind('<Control-Shift-V>', self._paste_clipboard)
		self.bind('<Configure>', self._term_on_configure)
		self.bind('<Map>', self._term_on_map)
		self.bind('<Destroy>', lambda e: self._terminate_process())
		self.realbind = self.bind
		self.bind = lambda *_, **__: None
	def _term_char_size(self):
		import tkinter.font as _tkfont
		f = _tkfont.Font(font = self.cget('font'))
		return max(1, f.measure('0')), max(1, f.metrics('linespace'))
	def _term_compute_size(self):
		state.root.update()
		charw, charh = self._term_char_size()
		_chrome = int(self.cget('borderwidth')) + int(self.cget('highlightthickness'))
		_pad_w = 2 * (_chrome + int(self.cget('padx')))
		_pad_h = 2 * (_chrome + int(self.cget('pady')))
		cols = max(1, (self.winfo_width() - _pad_w) // charw)
		rows = max(1, (self.winfo_height() - _pad_h) // charh)
		self.config(width = cols, height = rows)
		return self.cget('width'), self.cget('height')
	def _term_on_map(self, event):
		if self._term_started:
			self._term_apply_resize()
			return
		self._term_started = True
		self._term_start_process()
	def _term_reset_tabs(self):
		self._tab_stops = set(range(8, self._GRID_COLS, 8))
	def _term_next_tab(self, col):
		_cands = [_s for _s in self._tab_stops if _s > col]
		if _cands:
			return min(min(_cands), self._GRID_COLS - 1)
		return self._GRID_COLS - 1
	def _term_start_process(self):
		self._GRID_COLS, self._GRID_ROWS = self._term_compute_size()
		self._VT_ROWS = self._GRID_ROWS
		self._scroll_top = 1
		self._scroll_bot = self._GRID_ROWS
		self._term_reset_tabs()
		if platform.system() == 'Linux':
			import pty
			import fcntl
			import termios
			import struct
			self.master_fd, slave_fd = pty.openpty()
			fcntl.ioctl(self.master_fd, termios.TIOCSWINSZ, struct.pack('HHHH', self._GRID_ROWS, self._GRID_COLS, 0, 0))
			shell = None if self._term_command else os.environ.get('SHELL', '/bin/bash')
			env = os.environ.copy()
			env['TERM'] = 'xterm-256color'
			if not self.nocolor:
				env['COLORTERM'] = 'truecolor'
			_bg_r, _bg_g, _bg_b = self.winfo_rgb(self._term_default_bg)
			_fg_r, _fg_g, _fg_b = self.winfo_rgb(self._term_default_fg)
			_bg_is_light = (0.299 * _bg_r + 0.587 * _bg_g + 0.114 * _bg_b) / 256 >= 128
			_fg_is_light = (0.299 * _fg_r + 0.587 * _fg_g + 0.114 * _fg_b) / 256 >= 128
			env['COLORFGBG'] = f'{15 if _fg_is_light else 0};{15 if _bg_is_light else 0}'
			self.proc = subprocess.Popen(self._term_command if self._term_command else [shell], stdin = slave_fd, stdout = slave_fd, stderr = slave_fd, close_fds = True, preexec_fn = self._term_preexec, env = env)
			os.close(slave_fd)
		else:
			self.proc = PtyProcess.spawn(self._term_command if self._term_command else ['powershell.exe'], dimensions = (self._GRID_ROWS, self._GRID_COLS))
		state._open_terminal_closers.append(self._terminate_process)
		self._read_generation += 1
		threading.Thread(target = self._read, args = (self._read_generation, self._out_q, getattr(self, 'master_fd', None), self.proc), daemon = True).start()
		self.after(50, self._poll)
	def _term_on_configure(self, event):
		size = (event.width, event.height)
		if size == self._last_term_size:
			return
		self._last_term_size = size
		if self._resize_after_id is not None:
			self.after_cancel(self._resize_after_id)
		self._resize_after_id = self.after(DEBOUNCE_TIME, self._term_apply_resize)
	def _term_apply_resize(self):
		self._resize_after_id = None
		if not self.winfo_exists():
			return
		if not self._term_started:
			return
		cols, rows = self._term_compute_size()
		if self._follow_bottom:
			self._term_follow_view()
		if cols == self._GRID_COLS and rows == self._GRID_ROWS:
			return
		self._term_resize_grid(cols, rows)
	def _term_resize_grid(self, cols, rows):
		if self._alt_mode:
			old_rows = self._GRID_ROWS
			for ln in range(1, old_rows + 1):
				line = self.get(f'{ln}.0', f'{ln}.end')
				if len(line) > cols:
					self.delete(f'{ln}.{cols}', f'{ln}.end')
				elif len(line) < cols:
					self.insert(f'{ln}.end', ' ' * (cols - len(line)))
			if rows > old_rows:
				self.insert('end', '\n' + '\n'.join([' ' * cols] * (rows - old_rows)))
			elif rows < old_rows:
				self.delete(f'{rows + 1}.0', 'end')
			_cur_row, _cur_col = (int(_x) for _x in self.index('insert').split('.'))
			_cur_row = min(max(1, _cur_row), rows)
			_cur_col = min(max(0, _cur_col), cols)
			self.mark_set('insert', f'{_cur_row}.{_cur_col}')
			self.cursor = self.index('insert')
			self._cur_line = _cur_row
		else:
			self._cur_line = min(self._cur_line, self.screen_top + rows - 1)
		self._GRID_COLS = cols
		self._GRID_ROWS = rows
		self._VT_ROWS = rows
		self._scroll_top = 1
		self._scroll_bot = rows
		if platform.system() == 'Linux' and hasattr(self, 'master_fd'):
			import fcntl
			import termios
			import struct
			import signal
			try:
				fcntl.ioctl(self.master_fd, termios.TIOCSWINSZ, struct.pack('HHHH', rows, cols, 0, 0))
				os.killpg(self.proc.pid, signal.SIGWINCH)
			except Exception:
				pass
	def _term_preexec(self):
		import fcntl
		import termios
		os.setsid()
		fcntl.ioctl(0, termios.TIOCSCTTY, 0)
	def _read(self, gen, q, fd, proc):
		_dec = codecs.getincrementaldecoder('utf-8')(errors = 'replace')
		while self._read_generation == gen:
			try:
				if platform.system() == 'Linux':
					import select
					r, _, _ = select.select([fd], [], [], 0.05)
					if r:
						data = os.read(fd, 4096)
						if not data:
							break
						q.put(_dec.decode(data))
					elif proc.poll() is not None:
						break
				else:
					data = proc.read(4096)
					if data:
						q.put(data if isinstance(data, str) else _dec.decode(data))
			except Exception:
				break
		q.put(None)
	def _write(self, data):
		if platform.system() == 'Linux':
			os.write(self.master_fd, data)
		else:
			try:
				self.proc.write(data.decode('utf-8', errors = 'replace'))
			except Exception:
				pass
	def _emit_process_ended(self):
		if not self.running:
			return
		self.running = False
		try:
			self.event_generate('<<TerminalProcessEnded>>')
		except Exception:
			pass
	def _terminate_process(self, restarting = False):
		if self._closed:
			return
		self._closed = True
		self._emit_process_ended()
		if platform.system() == 'Linux':
			try:
				while True:
					self._out_q.get_nowait()
			except Exception:
				pass
			try:
				self.proc.terminate()
			except Exception:
				pass
			try:
				os.close(self.master_fd)
			except Exception:
				pass
		else:
			try:
				self.proc.close()
			except Exception:
				pass
		if self._poll_after_id is not None:
			try:
				self.after_cancel(self._poll_after_id)
			except Exception:
				pass
			self._poll_after_id = None
		if self._blink_after_id is not None:
			try:
				self.after_cancel(self._blink_after_id)
			except Exception:
				pass
			self._blink_after_id = None
		try:
			state._open_terminal_closers.remove(self._terminate_process)
		except Exception:
			pass
		if not restarting:
			try:
				self.event_generate('<<TerminalStopped>>')
			except Exception:
				pass
	def restart(self):
		self._terminate_process(restarting = True)
		self.unbind('<Key>')
		self.realbind('<Key>', self._key)
		self.delete('1.0', 'end')
		self.mark_set('insert', '1.0')
		self.cursor = '1.0'
		self.screen_top = 1
		self._cur_line = 1
		self._saved_cursor = None
		self._saved_sgr = None
		self._tab_stops = set()
		self._pending_esc = ''
		self._sgr_state = _sgr_new_state()
		self._sgr_tag_cache = None
		self._bracketed_paste = False
		self._focus_reporting = False
		self._autowrap = True
		self._app_cursor = False
		self._mouse_mode = 0
		self._mouse_sgr = False
		self._mouse_last_pos = None
		self._alt_saved = None
		self._alt_mode = False
		import queue as _queue
		self._out_q = _queue.Queue(maxsize = 64)
		self._closed = False
		self.running = True
		self._term_start_process()
	def _is_default_colour(self, colour, default_rgb):
		return colour is None or self.winfo_rgb(colour) == default_rgb
	def _start_blink(self):
		if self._blink_after_id is None:
			self._blink_after_id = self.after(500, self._blink_tick)
	def _blink_tick(self):
		self._blink_after_id = None
		if self._closed:
			return
		self._blink_visible = not self._blink_visible
		_dead = []
		for _bn, _cols in self._blink_tags.items():
			if not self.tag_ranges(_bn):
				_dead.append(_bn)
				continue
			try:
				self.tag_configure(_bn, foreground = _cols[0] if self._blink_visible else _cols[1])
			except Exception:
				pass
		for _bn in _dead:
			try:
				self.tag_configure(_bn, foreground = self._blink_tags[_bn][0])
			except Exception:
				pass
			del self._blink_tags[_bn]
		if not self._blink_tags:
			return
		self._blink_after_id = self.after(500, self._blink_tick)
	def _recompute_sgr_tag(self):
		fg, bg = _term_sgr_resolve(self._sgr_state, self._term_default_fg, self._term_default_bg)
		if self._is_default_colour(fg, self._default_fg_rgb) and self._is_default_colour(bg, self._default_bg_rgb) and not self._sgr_state['bold'] and not self._sgr_state['italic'] and not self._sgr_state['underline'] and not self._sgr_state['blink']:
			self._sgr_tag_cache = None
			return
		name = 'sgr_' + (fg.replace('#', '') if fg else 'x') + '_' + (bg.replace('#', '') if bg else 'x')
		if self._sgr_state['bold']:
			name += '_b'
		if self._sgr_state['italic']:
			name += '_i'
		if self._sgr_state['underline']:
			name += '_u'
		if self._sgr_state['blink']:
			name += '_bl'
		if name not in self._sgr_tags_done:
			fnt = (monospace, 12, 'bold') if self._sgr_state['bold'] else ((monospace, 12, 'italic') if self._sgr_state['italic'] else (monospace, 12))
			self.tag_configure(name, foreground = fg if fg else '', background = bg if bg else '', underline = self._sgr_state['underline'], font = fnt)
			self.tag_lower(name, 'sel')
			self._sgr_tags_done.add(name)
		self._sgr_tag_cache = name
		if self._sgr_state['blink']:
			if name not in self._blink_tags:
				_onfg = fg if fg else self._term_default_fg
				_offfg = bg if bg else self._term_default_bg
				self._blink_tags[name] = (_onfg, _offfg)
			self._start_blink()
	def _term_insert(self, index, ch):
		if self._sgr_tag_cache is None:
			self.insert(index, ch)
		else:
			self.insert(index, ch, self._sgr_tag_cache)
	def _grid_row_runs(self, r):
		runs = []
		text = ''
		tag = None
		for kind, value, index in self.dump(f'{r}.0', f'{r}.end', text = True, tag = True):
			if kind == 'text':
				text += value
			elif kind == 'tagon':
				if value.startswith('sgr'):
					if text:
						runs.append((text, tag))
						text = ''
					tag = value
			elif kind == 'tagoff':
				if value == tag:
					if text:
						runs.append((text, tag))
						text = ''
					tag = None
		if text:
			runs.append((text, tag))
		return runs
	def _grid_scroll_region(self, top, bot, up):
		n = bot - top + 1
		rows = [self._grid_row_runs(r) for r in range(top, bot + 1)]
		blank = [(' ' * self._GRID_COLS, None)]
		if up > 0:
			up = min(up, n)
			rows = rows[up:] + [blank] * up
		elif up < 0:
			down = min(-up, n)
			rows = [blank] * down + rows[:n - down]
		else:
			return
		for idx, r in enumerate(range(top, bot + 1)):
			self.delete(f'{r}.0', f'{r}.end')
			for text, tag in rows[idx]:
				if tag is None:
					self.insert(f'{r}.end', text)
				else:
					self.insert(f'{r}.end', text, tag)
	def _osc_colour_reply(self, which, colour):
		r, g, b = self.winfo_rgb(colour)
		try:
			self._write(f'\x1b]{which};rgb:{r:04x}/{g:04x}/{b:04x}\x1b\\'.encode())
		except Exception:
			pass
	def _osc_parse_colour(self, spec):
		spec = spec.strip()
		if spec.startswith('rgb:'):
			parts = spec[4:].split('/')
			if len(parts) == 3:
				try:
					return '#' + ''.join(f'{int(p[:2], 16):02x}' if len(p) >= 2 else f'{int(p, 16):02x}' for p in parts)
				except Exception:
					return None
			return None
		try:
			self.winfo_rgb(spec)
			return spec
		except Exception:
			return None
	def _handle_osc(self, body):
		if body.startswith('52;'):
			parts = body.split(';', 2)
			if len(parts) == 3 and parts[2] not in ('', '?'):
				try:
					text = base64.b64decode(parts[2]).decode('utf-8', errors = 'replace')
				except Exception:
					return
				self.clipboard_clear()
				self.clipboard_append(text)
		elif body.startswith('11;?'):
			self._osc_colour_reply('11', self._term_default_bg)
		elif body.startswith('10;?'):
			self._osc_colour_reply('10', self._term_default_fg)
		elif body.startswith('12;'):
			_spec = body[3:]
			if _spec == '?':
				self._osc_colour_reply('12', self.cget('insertbackground'))
			else:
				_col = self._osc_parse_colour(_spec)
				if _col:
					try:
						self.config(insertbackground = _col)
					except Exception:
						pass
		elif body == '112' or body.startswith('112;'):
			try:
				self.config(insertbackground = self._term_default_fg)
			except Exception:
				pass
	def _enter_alt_screen(self):
		if self._alt_saved is not None:
			return
		self._alt_saved = (self.dump('1.0', 'end', text = True, tag = True), self.screen_top, self.cursor, dict(self._sgr_state), self._cur_line)
		self._alt_mode = True
		self._cur_line = 1
		self._scroll_top = 1
		self._scroll_bot = self._GRID_ROWS
		self.delete('1.0', 'end')
		self.insert('1.0', '\n'.join([' ' * self._GRID_COLS] * self._GRID_ROWS))
		self.screen_top = 1
		self.mark_set('insert', '1.0')
		self.cursor = '1.0'
		if not self.nocolor:
			_sgr_apply(self._sgr_state, [0])
			self._recompute_sgr_tag()
	def _leave_alt_screen(self):
		if self._alt_saved is None:
			return
		dump, saved_top, saved_cursor, saved_sgr, saved_curline = self._alt_saved
		self._alt_saved = None
		self._alt_mode = False
		self.delete('1.0', 'end')
		_open_tags = []
		for kind, value, index in dump:
			if kind == 'text':
				self.insert('end', value, tuple(_open_tags))
			elif kind == 'tagon':
				if value not in _open_tags:
					_open_tags.append(value)
			elif kind == 'tagoff':
				if value in _open_tags:
					_open_tags.remove(value)
		self.screen_top = saved_top
		self._sgr_state.update(saved_sgr)
		self._recompute_sgr_tag()
		self._cur_line = saved_curline
		self.mark_set('insert', saved_cursor)
		self.cursor = saved_cursor
		self.config(insertontime = 600, insertofftime = 300)
	def _deccolm_clear(self):
		self._scroll_top = 1
		self._scroll_bot = self._GRID_ROWS
		if self._alt_mode:
			self.delete('1.0', 'end')
			for _cr in range(self._GRID_ROWS):
				if _cr:
					self.insert('end', '\n')
				self._term_insert('end', ' ' * self._GRID_COLS)
			self._grid_goto(1, 0)
		else:
			old_last = int(self.index('end').split('.')[0]) - 1
			self.insert('end', '\n' * self._VT_ROWS)
			self.screen_top = old_last + 1
			self._cur_line = self.screen_top
			self.mark_set('insert', f'{self.screen_top}.0')
	def _origin_row(self, row):
		if self._origin_mode:
			return min(max(self._scroll_top, self._scroll_top + row - 1), self._scroll_bot)
		return min(max(1, row), self._GRID_ROWS)
	def _cursor_home(self):
		r = self._scroll_top if self._origin_mode else 1
		if self._alt_mode:
			self._grid_goto(r, 0)
		else:
			self._cur_line = self.screen_top + r - 1
			self._vt_sync()
			self.mark_set('insert', f'{self._cur_line}.0')
	def _grid_goto(self, row, gcol):
		row = min(max(1, row), self._GRID_ROWS)
		gcol = min(max(0, gcol), self._GRID_COLS)
		self.mark_set('insert', f'{row}.{gcol}')
	def _grid_put(self, ch):
		row = int(self.index('insert').split('.')[0])
		gcol = int(self.index('insert').split('.')[1])
		if gcol >= self._GRID_COLS:
			if row < self._GRID_ROWS:
				row += 1
				gcol = 0
				self.mark_set('insert', f'{row}.0')
			else:
				gcol = self._GRID_COLS - 1
				self.mark_set('insert', f'{row}.{gcol}')
		self.delete(f'{row}.{gcol}', f'{row}.{gcol + 1}')
		self._term_insert(f'{row}.{gcol}', ch)
		self.mark_set('insert', f'{row}.{gcol + 1}')
	def _vt_sync(self):
		last = int(self.index('end').split('.')[0]) - 1
		if self._cur_line > last:
			_ins = self.index('insert')
			self.insert('end', '\n' * (self._cur_line - last))
			self.mark_set('insert', _ins)
	def _term_materialize_screen(self):
		if self._alt_mode:
			return
		_bb = self.screen_top + self._VT_ROWS - 1
		_last = int(self.index('end').split('.')[0]) - 1
		if _last < _bb:
			_ins = self.index('insert')
			self.insert('end', '\n' * (_bb - _last))
			self.mark_set('insert', _ins)
	def _term_goto(self, _gl, _gc):
		_ll = int(self.index(f'{_gl}.end').split('.')[1])
		if _gc > _ll:
			self.insert(f'{_gl}.end', ' ' * (_gc - _ll))
		self.mark_set('insert', f'{_gl}.{_gc}')
	def _primary_scroll_up(self):
		if self._scroll_top == 1:
			self.screen_top += 1
			_ins = self.screen_top + self._scroll_bot - 1
			self.insert(f'{_ins}.0', '\n')
		else:
			_lt = self.screen_top + self._scroll_top - 1
			_lb = self.screen_top + self._scroll_bot - 1
			self.delete(f'{_lt}.0', f'{_lt + 1}.0')
			self.insert(f'{_lb}.0', '\n')
	def _primary_scroll_down(self):
		_lt = self.screen_top + self._scroll_top - 1
		_lb = self.screen_top + self._scroll_bot - 1
		self.insert(f'{_lt}.0', '\n')
		self.delete(f'{_lb + 1}.0', f'{_lb + 2}.0')
	def _csi_embedded(self, rest):
		controls = ''
		cleaned = '\x1b['
		k = 2
		ln = len(rest)
		while k < ln:
			c = rest[k]
			o = ord(c)
			if c == '\x1b':
				return controls, '', k, 'splice'
			if c == '\x18' or c == '\x1a':
				return controls, '', k + 1, 'splice'
			if o < 0x20 or c == '\x7f':
				controls += c
				k += 1
				continue
			if 0x40 <= o <= 0x7e:
				if controls:
					return controls, cleaned + c, k + 1, 'splice'
				return '', '', 0, 'skip'
			if 0x20 <= o <= 0x3f:
				cleaned += c
				k += 1
				continue
			return '', '', 0, 'skip'
		if ln < _PTY_MAX_PENDING_ESC:
			return '', '', 0, 'pending'
		return '', '', 0, 'skip'
	def _on_modified(self, e = None):
		if self.edit_modified():
			self.edit_modified(False)
	def _process(self, text):
		if self._pending_esc:
			text = self._pending_esc + text
			self._pending_esc = ''
		self.mark_set('insert', self.cursor)
		i = 0
		n = len(text)
		while i < n:
			ch = text[i]
			if ch == '\r':
				if self._alt_mode:
					ln = int(self.index('insert').split('.')[0])
					self.mark_set('insert', f'{ln}.0')
				else:
					self.mark_set('insert', f'{self._cur_line}.0')
				i += 1
			elif ch == '\x08':
				c = int(self.index('insert').split('.')[1])
				if c > 0:
					ln = int(self.index('insert').split('.')[0])
					self.mark_set('insert', f'{ln}.{c - 1}')
				i += 1
			elif ch == '\n' or ch == '\x0b' or ch == '\x0c':
				if self._alt_mode:
					ln = int(self.index('insert').split('.')[0])
					gcol = int(self.index('insert').split('.')[1])
					if ln >= self._scroll_bot:
						self._grid_scroll_region(self._scroll_top, self._scroll_bot, 1)
						self._grid_goto(self._scroll_bot, gcol)
					else:
						self._grid_goto(ln + 1, gcol)
					i += 1
					continue
				c = int(self.index('insert').split('.')[1])
				_srow = self._cur_line - self.screen_top + 1
				if (self._scroll_top > 1 or self._scroll_bot < self._VT_ROWS) and _srow == self._scroll_bot:
					self._primary_scroll_up()
					self._cur_line = self.screen_top + self._scroll_bot - 1
					self.tag_remove('wrapcont', f'{self._cur_line}.0', f'{self._cur_line}.end')
					self.mark_set('insert', f'{self._cur_line}.{c}')
					i += 1
					continue
				self._cur_line += 1
				if self._cur_line > self.screen_top + self._VT_ROWS - 1:
					self.screen_top = self._cur_line - (self._VT_ROWS - 1)
				self._vt_sync()
				self.tag_remove('wrapcont', f'{self._cur_line}.0', f'{self._cur_line}.end')
				self._term_goto(self._cur_line, c)
				i += 1
			elif ch == '\x1b':
				rest = text[i:]
				if len(rest) < 2:
					self._pending_esc = rest
					break
				nxt = rest[1]
				if nxt == '[':
					m = re.match(r'\x1b\[([0-9;?<=>]*[ -/]*)([@-~])', rest)
					if not m and re.fullmatch(r'\x1b\[[0-9;?<=>]*[ -/]*', rest):
						self._pending_esc = rest
						break
					if m:
						_prefix = m.group(1)
						_private = _prefix.startswith('?')
						ps = ''.join(c for c in _prefix if c in '0123456789;')
						cmd = m.group(2) if all(c in '0123456789;?' for c in _prefix) else ''
						p = [int(x) if x else 0 for x in ps.split(';')] if ps else [0]
						ln = self.index('insert').split('.')[0]
						col = self.index('insert').split('.')[1]
						if cmd == 'K':
							if self._alt_mode:
								gcol = int(col)
								if p[0] == 0:
									self.delete(f'{ln}.{gcol}', f'{ln}.end')
									self._term_insert(f'{ln}.{gcol}', ' ' * (self._GRID_COLS - gcol))
								elif p[0] == 1:
									self.delete(f'{ln}.0', f'{ln}.{gcol}')
									self._term_insert(f'{ln}.0', ' ' * gcol)
								else:
									self.delete(f'{ln}.0', f'{ln}.end')
									self._term_insert(f'{ln}.0', ' ' * self._GRID_COLS)
								self.mark_set('insert', f'{ln}.{gcol}')
							else:
								if p[0] == 0:
									self.delete('insert', f'{ln}.end')
								elif p[0] == 1:
									self.delete(f'{ln}.0', f'{ln}.{int(col) + 1}')
									self.insert(f'{ln}.0', ' ' * (int(col) + 1))
									self.mark_set('insert', f'{ln}.{col}')
								else:
									self.delete(f'{ln}.0', f'{ln}.end')
									self._term_goto(int(ln), int(col))
						elif cmd == 'J':
							if self._alt_mode:
								gcol = int(col)
								if p[0] == 0:
									self.delete(f'{ln}.{gcol}', f'{ln}.end')
									self._term_insert(f'{ln}.{gcol}', ' ' * (self._GRID_COLS - gcol))
									if int(ln) < self._GRID_ROWS:
										self.delete(f'{int(ln) + 1}.0', 'end')
										for _er in range(self._GRID_ROWS - int(ln)):
											self.insert('end', '\n')
											self._term_insert('end', ' ' * self._GRID_COLS)
								else:
									self.delete('1.0', 'end')
									for _er in range(self._GRID_ROWS):
										if _er:
											self.insert('end', '\n')
										self._term_insert('end', ' ' * self._GRID_COLS)
								self.mark_set('insert', f'{ln}.{gcol}')
							elif p[0] == 2:
								cur_col = int(col)
								_bb = self.screen_top + self._VT_ROWS - 1
								_last = int(self.index('end').split('.')[0]) - 1
								if _last > _bb:
									self.delete(f'{_bb}.end', 'end - 1 char')
									_last = _bb
								if _last < _bb:
									self.insert('end', '\n' * (_bb - _last))
								for _er in range(self.screen_top, _bb + 1):
									self.delete(f'{_er}.0', f'{_er}.end')
								if cur_col > 0:
									self.insert(f'{self._cur_line}.0', ' ' * cur_col)
								self.mark_set('insert', f'{self._cur_line}.{cur_col}')
							elif p[0] == 3:
								if self.screen_top > 1:
									del_n = self.screen_top - 1
									self.delete('1.0', f'{self.screen_top}.0')
									self._cur_line = max(1, self._cur_line - del_n)
									self.screen_top = 1
									self.mark_set('insert', f'{self._cur_line}.{col}')
							elif p[0] == 1:
								_il = int(ln)
								_ic = int(col)
								for _er in range(self.screen_top, _il):
									self.delete(f'{_er}.0', f'{_er}.end')
								self.delete(f'{_il}.0', f'{_il}.{_ic + 1}')
								self.insert(f'{_il}.0', ' ' * (_ic + 1))
								self.mark_set('insert', f'{_il}.{_ic}')
							elif p[0] == 0:
								_bb = self.screen_top + self._VT_ROWS - 1
								self.delete('insert', f'{self._cur_line}.end')
								_last = int(self.index('end').split('.')[0]) - 1
								for _er in range(self._cur_line + 1, min(_bb, _last) + 1):
									self.delete(f'{_er}.0', f'{_er}.end')
								if _last < _bb:
									_ins = self.index('insert')
									self.insert('end', '\n' * (_bb - _last))
									self.mark_set('insert', _ins)
						elif cmd in ('H', 'f'):
							row_ = p[0] if p[0] else 1
							col_ = p[1] if len(p) > 1 and p[1] else 1
							if self._alt_mode:
								self._grid_goto(self._origin_row(row_), col_ - 1)
							else:
								self._cur_line = self.screen_top + self._origin_row(row_) - 1
								self._vt_sync()
								ll = int(self.index(f'{self._cur_line}.end').split('.')[1])
								if col_ - 1 > ll:
									self.insert(f'{self._cur_line}.end', ' ' * (col_ - 1 - ll))
								self.mark_set('insert', f'{self._cur_line}.{col_ - 1}')
						elif cmd == 'A':
							mv = p[0] or 1
							if self._alt_mode:
								self._grid_goto(int(ln) - mv, int(col))
							else:
								self._cur_line = max(self.screen_top, int(ln) - mv)
								self._term_goto(self._cur_line, int(col))
						elif cmd == 'B':
							mv = p[0] or 1
							if self._alt_mode:
								self._grid_goto(int(ln) + mv, int(col))
							else:
								self._cur_line = min(int(ln) + mv, self.screen_top + self._VT_ROWS - 1)
								self._vt_sync()
								self._term_goto(self._cur_line, int(col))
						elif cmd == 'C':
							mv = p[0] or 1
							_tc = min(int(col) + mv, self._GRID_COLS - 1)
							if not self._alt_mode:
								ll = int(self.index(f'{ln}.end').split('.')[1])
								if _tc > ll:
									self.insert(f'{ln}.end', ' ' * (_tc - ll))
							self.mark_set('insert', f'{ln}.{_tc}')
						elif cmd == 'D':
							mv = p[0] or 1
							self._term_goto(int(ln), max(0, int(col) - mv))
						elif cmd == 'E':
							mv = p[0] or 1
							if self._alt_mode:
								self._grid_goto(int(ln) + mv, 0)
							else:
								self._cur_line = int(ln) + mv
								self._vt_sync()
								self.mark_set('insert', f'{self._cur_line}.0')
						elif cmd == 'F':
							mv = p[0] or 1
							if self._alt_mode:
								self._grid_goto(int(ln) - mv, 0)
							else:
								self._cur_line = max(self.screen_top, int(ln) - mv)
								self.mark_set('insert', f'{self._cur_line}.0')
						elif cmd == 's' and not _private:
							if self._alt_mode:
								self._saved_cursor = self.index('insert')
							else:
								self._saved_cursor = (self._cur_line, int(col))
						elif cmd == 'u' and not _private:
							if self._saved_cursor is not None:
								if self._alt_mode:
									self.mark_set('insert', self._saved_cursor)
								else:
									self._cur_line, _sc = self._saved_cursor
									self._vt_sync()
									self.mark_set('insert', f'{self._cur_line}.{_sc}')
						elif cmd == 'G':
							mv = p[0] or 1
							if self._alt_mode:
								self._grid_goto(int(ln), mv - 1)
							else:
								ll = int(self.index(f'{self._cur_line}.end').split('.')[1])
								if mv - 1 > ll:
									self.insert(f'{self._cur_line}.end', ' ' * (mv - 1 - ll))
								self.mark_set('insert', f'{self._cur_line}.{mv - 1}')
						elif cmd == 'g':
							if p[0] == 0:
								self._tab_stops.discard(int(col))
							elif p[0] == 3:
								self._tab_stops = set()
						elif cmd == 'd':
							mv = p[0] or 1
							if self._alt_mode:
								self._grid_goto(self._origin_row(mv), int(col))
							else:
								self._cur_line = self.screen_top + self._origin_row(mv) - 1
								self._vt_sync()
								self._term_goto(self._cur_line, int(col))
						elif cmd == 'P':
							mv = p[0] or 1
							_pend = f'insert+{mv}c'
							if self.compare(_pend, '>', f'{ln}.end'):
								_pend = f'{ln}.end'
							self.delete('insert', _pend)
						elif cmd == '@':
							mv = p[0] or 1
							self.insert('insert', ' ' * mv)
							self.mark_set('insert', f'insert-{mv}c')
						elif cmd == 'L':
							if self._alt_mode:
								r0 = int(ln)
								if self._scroll_top <= r0 <= self._scroll_bot:
									self._grid_scroll_region(r0, self._scroll_bot, -(p[0] or 1))
									self.mark_set('insert', f'{r0}.0')
						elif cmd == 'M':
							if self._alt_mode:
								r0 = int(ln)
								if self._scroll_top <= r0 <= self._scroll_bot:
									self._grid_scroll_region(r0, self._scroll_bot, (p[0] or 1))
									self.mark_set('insert', f'{r0}.0')
						elif cmd == 'S':
							if self._alt_mode:
								self._grid_scroll_region(self._scroll_top, self._scroll_bot, (p[0] or 1))
						elif cmd == 'T':
							if self._alt_mode:
								self._grid_scroll_region(self._scroll_top, self._scroll_bot, -(p[0] or 1))
						elif cmd == 'r':
							if len(p) >= 2:
								self._scroll_top = min(max(1, p[0] or 1), self._GRID_ROWS)
								self._scroll_bot = min(max(self._scroll_top, p[1] or self._GRID_ROWS), self._GRID_ROWS)
							else:
								self._scroll_top = 1
								self._scroll_bot = self._GRID_ROWS
							self._cursor_home()
						elif cmd == 'X':
							mv = p[0] or 1
							if self._alt_mode:
								gcol = int(col)
								endc = min(gcol + mv, self._GRID_COLS)
								self.delete(f'{ln}.{gcol}', f'{ln}.{endc}')
								self._term_insert(f'{ln}.{gcol}', ' ' * (endc - gcol))
								self.mark_set('insert', f'{ln}.{gcol}')
							else:
								_x0 = int(col)
								_xll = int(self.index(f'{ln}.end').split('.')[1])
								self.delete(f'{ln}.{_x0}', f'{ln}.{min(_x0 + mv, _xll)}')
								self.insert(f'{ln}.{_x0}', ' ' * mv)
								self.mark_set('insert', f'{ln}.{_x0}')
						elif m.group(2) == 'c' and not _private:
							try:
								if _prefix.startswith('>'):
									self._write(b'\x1b[>1;10;0c')
								else:
									self._write(b'\x1b[?1;2c')
							except Exception:
								pass
						elif cmd == 'n':
							if p[0] == 6:
								cur_col = int(self.index('insert').split('.')[1])
								row_rep = max(1, self._cur_line - self.screen_top + 1)
								try:
									self._write(f'\x1b[{row_rep};{cur_col + 1}R'.encode())
								except Exception:
									pass
							elif p[0] == 5:
								try:
									self._write(b'\x1b[0n')
								except Exception:
									pass
						elif cmd == 'm':
							if not self.nocolor:
								_sgr_apply(self._sgr_state, p)
								self._recompute_sgr_tag()
						elif cmd == 'h' and _private:
							if p[0] in (1049, 1047, 47):
								self._enter_alt_screen()
							elif p[0] == 3:
								self._deccolm_clear()
							elif p[0] == 6:
								self._origin_mode = True
								self._cursor_home()
							elif p[0] == 25:
								self.config(insertontime = 600)
							elif p[0] == 12:
								self.config(insertofftime = 300)
								self.mark_set('insert', self.index('insert'))
							elif p[0] == 5:
								if not self._reverse_screen:
									self._reverse_screen = True
									self.config(background = self._term_default_fg, foreground = self._term_default_bg, insertbackground = self._term_default_bg)
							elif p[0] == 2004:
								self._bracketed_paste = True
							elif p[0] == 1004:
								self._focus_reporting = True
							elif p[0] == 7:
								self._autowrap = True
							elif p[0] == 1:
								self._app_cursor = True
							elif p[0] in (1000, 1002, 1003):
								self._mouse_mode = p[0]
							elif p[0] == 1006:
								self._mouse_sgr = True
						elif cmd == 'l' and _private:
							if p[0] in (1049, 1047, 47):
								self._leave_alt_screen()
							elif p[0] == 3:
								self._deccolm_clear()
							elif p[0] == 6:
								self._origin_mode = False
								self._cursor_home()
							elif p[0] == 25:
								self.config(insertontime = 0)
							elif p[0] == 12:
								self.config(insertofftime = 0)
								self.mark_set('insert', self.index('insert'))
							elif p[0] == 5:
								if self._reverse_screen:
									self._reverse_screen = False
									self.config(background = self._term_default_bg, foreground = self._term_default_fg, insertbackground = self._term_default_fg)
							elif p[0] == 2004:
								self._bracketed_paste = False
							elif p[0] == 1004:
								self._focus_reporting = False
							elif p[0] == 7:
								self._autowrap = False
							elif p[0] == 1:
								self._app_cursor = False
							elif p[0] in (1000, 1002, 1003):
								self._mouse_mode = 0
							elif p[0] == 1006:
								self._mouse_sgr = False
						i += len(m.group(0))
					else:
						_ctl, _clean, _consumed, _status = self._csi_embedded(rest)
						if _status == 'pending':
							self._pending_esc = rest
							break
						elif _status == 'splice':
							text = text[:i] + _ctl + _clean + text[i + _consumed:]
							n = len(text)
						else:
							i += 2
				elif nxt == ']':
					end_osc = rest.find('\x07', 2)
					if end_osc >= 0:
						self._handle_osc(rest[2:end_osc])
						i += end_osc + 1
					else:
						st = rest.find('\x1b\\', 2)
						if st >= 0:
							self._handle_osc(rest[2:st])
							i += st + 2
						elif len(rest) < _PTY_MAX_PENDING_ESC:
							self._pending_esc = rest
							break
						else:
							i += len(rest)
				elif nxt == 'M':
					if self._alt_mode:
						cl = int(self.index('insert').split('.')[0])
						co = self.index('insert').split('.')[1]
						self.mark_set('insert', f'{max(1, cl - 1)}.{co}')
					else:
						co = int(self.index('insert').split('.')[1])
						_srow = self._cur_line - self.screen_top + 1
						if (self._scroll_top > 1 or self._scroll_bot < self._VT_ROWS) and _srow == self._scroll_top:
							self._primary_scroll_down()
							self._cur_line = self.screen_top + self._scroll_top - 1
							self.mark_set('insert', f'{self._cur_line}.{co}')
							i += 2
							continue
						if _srow <= 1 and self._scroll_top == 1 and self._scroll_bot == self._VT_ROWS:
							self.insert(f'{self.screen_top}.0', '\n')
							self._cur_line = self.screen_top
							self._term_goto(self._cur_line, co)
						else:
							self._cur_line = max(self.screen_top, self._cur_line - 1)
							self._term_goto(self._cur_line, co)
					i += 2
				elif nxt == 'D':
					if self._alt_mode:
						cl = int(self.index('insert').split('.')[0])
						co = self.index('insert').split('.')[1]
						last_line = int(self.index('end').split('.')[0]) - 1
						if cl + 1 > last_line:
							self.insert('end', '\n')
						self.mark_set('insert', f'{cl + 1}.{co}')
					else:
						co = int(self.index('insert').split('.')[1])
						_srow = self._cur_line - self.screen_top + 1
						if (self._scroll_top > 1 or self._scroll_bot < self._VT_ROWS) and _srow == self._scroll_bot:
							self._primary_scroll_up()
							self._cur_line = self.screen_top + self._scroll_bot - 1
							self.mark_set('insert', f'{self._cur_line}.{co}')
							i += 2
							continue
						self._cur_line += 1
						if self._cur_line > self.screen_top + self._VT_ROWS - 1:
							self.screen_top = self._cur_line - (self._VT_ROWS - 1)
						self._vt_sync()
						self._term_goto(self._cur_line, co)
					i += 2
				elif nxt == 'E':
					if self._alt_mode:
						cl = int(self.index('insert').split('.')[0])
						last_line = int(self.index('end').split('.')[0]) - 1
						if cl + 1 > last_line:
							self.insert('end', '\n')
						self.mark_set('insert', f'{cl + 1}.0')
					else:
						_srow = self._cur_line - self.screen_top + 1
						if (self._scroll_top > 1 or self._scroll_bot < self._VT_ROWS) and _srow == self._scroll_bot:
							self._primary_scroll_up()
							self._cur_line = self.screen_top + self._scroll_bot - 1
							self.mark_set('insert', f'{self._cur_line}.0')
							i += 2
							continue
						self._cur_line += 1
						if self._cur_line > self.screen_top + self._VT_ROWS - 1:
							self.screen_top = self._cur_line - (self._VT_ROWS - 1)
						self._vt_sync()
						self._term_goto(self._cur_line, 0)
					i += 2
				elif nxt in '()*+#%':
					if len(rest) < 3:
						self._pending_esc = rest
						break
					if nxt == '#' and rest[2] == '8':
						if self._alt_mode:
							self.delete('1.0', 'end')
							for _dr in range(self._GRID_ROWS):
								if _dr:
									self.insert('end', '\n')
								self.insert('end', 'E' * self._GRID_COLS)
							self._grid_goto(1, 0)
						else:
							bottom = self.screen_top + self._VT_ROWS - 1
							last = int(self.index('end').split('.')[0]) - 1
							while last < bottom:
								self.insert('end', '\n')
								last += 1
							for _dr in range(self.screen_top, bottom + 1):
								self.delete(f'{_dr}.0', f'{_dr}.end')
								self.insert(f'{_dr}.0', 'E' * self._GRID_COLS)
							self._cur_line = self.screen_top
							self.mark_set('insert', f'{self.screen_top}.0')
					i += 3
				elif nxt == 'c':
					self._alt_saved = None
					self._alt_mode = False
					self.delete('1.0', 'end')
					self._cur_line = 1
					self.screen_top = 1
					self._scroll_top = 1
					self._scroll_bot = self._GRID_ROWS
					self._autowrap = True
					self._origin_mode = False
					self._app_cursor = False
					self._saved_cursor = None
					self._saved_sgr = None
					self._term_reset_tabs()
					if self._reverse_screen:
						self._reverse_screen = False
						self.config(background = self._term_default_bg, foreground = self._term_default_fg, insertbackground = self._term_default_fg)
					if not self.nocolor:
						_sgr_apply(self._sgr_state, [0])
						self._recompute_sgr_tag()
					self.mark_set('insert', '1.0')
					self.cursor = '1.0'
					self.config(insertontime = 600, insertofftime = 300)
					i += 2
				elif nxt == '7':
					if self._alt_mode:
						self._saved_cursor = self.index('insert')
					else:
						self._saved_cursor = (self._cur_line, int(self.index('insert').split('.')[1]))
					self._saved_sgr = dict(self._sgr_state)
					i += 2
				elif nxt == '8':
					if self._saved_cursor is not None:
						if self._alt_mode:
							self.mark_set('insert', self._saved_cursor)
						else:
							self._cur_line, _sc = self._saved_cursor
							self._vt_sync()
							self.mark_set('insert', f'{self._cur_line}.{_sc}')
					if self._saved_sgr is not None:
						self._sgr_state.update(self._saved_sgr)
						if not self.nocolor:
							self._recompute_sgr_tag()
					i += 2
				elif nxt == 'H':
					self._tab_stops.add(int(self.index('insert').split('.')[1]))
					i += 2
				elif nxt == '\x1b':
					i += 1
				else:
					i += 2
			elif ch == '\t':
				if self._alt_mode:
					ln = int(self.index('insert').split('.')[0])
					col = int(self.index('insert').split('.')[1])
					target = self._term_next_tab(col)
					self._grid_goto(ln, target)
					i += 1
					continue
				col = int(self.index('insert').split('.')[1])
				sp = self._term_next_tab(col) - col
				if sp <= 0:
					i += 1
					continue
				line_len = int(self.index(f'{self._cur_line}.end').split('.')[1])
				if col > line_len:
					self.insert(f'{self._cur_line}.end', ' ' * (col - line_len))
					line_len = col
				ovw = min(sp, line_len - col)
				if ovw > 0:
					self.delete(f'{self._cur_line}.{col}', f'{self._cur_line}.{col + ovw}')
				if self._sgr_tag_cache is None:
					self.insert(f'{self._cur_line}.{col}', ' ' * sp)
				else:
					self.insert(f'{self._cur_line}.{col}', ' ' * sp, self._sgr_tag_cache)
				self.mark_set('insert', f'{self._cur_line}.{col + sp}')
				i += 1
			elif ch >= ' ' and ch != '\x7f':
				if self._alt_mode:
					self._grid_put(ch)
					i += 1
					continue
				j = i
				while j < n and text[j] >= ' ' and text[j] != '\x7f':
					j += 1
				run = text[i:j]
				i = j
				col = int(self.index('insert').split('.')[1])
				if not self._autowrap:
					if col >= self._GRID_COLS:
						col = self._GRID_COLS - 1
					space = self._GRID_COLS - col
					if len(run) <= space:
						chunk = run
					else:
						chunk = run[:space - 1] + run[-1]
					line_len = int(self.index(f'{self._cur_line}.end').split('.')[1])
					if col > line_len:
						self.insert(f'{self._cur_line}.end', ' ' * (col - line_len))
						line_len = col
					ovw = min(len(chunk), line_len - col)
					if ovw > 0:
						self.delete(f'{self._cur_line}.{col}', f'{self._cur_line}.{col + ovw}')
					if self._sgr_tag_cache is None:
						self.insert(f'{self._cur_line}.{col}', chunk)
					else:
						self.insert(f'{self._cur_line}.{col}', chunk, self._sgr_tag_cache)
					col += len(chunk)
					self.mark_set('insert', f'{self._cur_line}.{col}')
					continue
				while run:
					wrapped = False
					space = self._GRID_COLS - col
					if space <= 0:
						_srow = self._cur_line - self.screen_top + 1
						if (self._scroll_top > 1 or self._scroll_bot < self._VT_ROWS) and _srow == self._scroll_bot:
							self._primary_scroll_up()
							self._cur_line = self.screen_top + self._scroll_bot - 1
						else:
							self._cur_line += 1
							if self._cur_line > self.screen_top + self._VT_ROWS - 1:
								self.screen_top = self._cur_line - (self._VT_ROWS - 1)
						self._vt_sync()
						col = 0
						wrapped = True
						space = self._GRID_COLS
					chunk = run[:space]
					run = run[space:]
					line_len = int(self.index(f'{self._cur_line}.end').split('.')[1])
					if col > line_len:
						self.insert(f'{self._cur_line}.end', ' ' * (col - line_len))
						line_len = col
					ovw = min(len(chunk), line_len - col)
					if ovw > 0:
						self.delete(f'{self._cur_line}.{col}', f'{self._cur_line}.{col + ovw}')
					if self._sgr_tag_cache is None:
						self.insert(f'{self._cur_line}.{col}', chunk)
					else:
						self.insert(f'{self._cur_line}.{col}', chunk, self._sgr_tag_cache)
					if wrapped:
						self.tag_add('wrapcont', f'{self._cur_line}.0', f'{self._cur_line}.1')
					col += len(chunk)
					self.mark_set('insert', f'{self._cur_line}.{col}')
			else:
				i += 1
		self.cursor = self.index('insert')
	def _poll(self):
		if self._polling:
			return
		self._polling = True
		try:
			self.update()
			closed = False
			backlog = False
			_had = False
			deadline = time.monotonic() + _TERM_FRAME_BUDGET
			try:
				while True:
					text = self._out_q.get_nowait()
					if text is None:
						closed = True
						break
					self._process(text)
					_had = True
					if time.monotonic() > deadline:
						backlog = True
						break
			except Exception:
				pass
			if _had and self._follow_bottom:
				self._term_follow_view()
			if _had:
				self.event_generate('<<TerminalOutputProcessed>>')
			if closed:
				self._emit_process_ended()
				if self.endmessage:
					_r = int(self.index('end').split('.')[0]) - 1
					while _r > 1 and not self.get(f'{_r}.0', f'{_r}.end').strip():
						_r -= 1
					self.delete(f'{_r}.end', 'end')
					self.insert('end', '\n\n\n' + self.endmessage)
					self.see('end')
					self.unbind('<Key>')
					self.realbind('<Key>', lambda e: self._terminate_process())
				else:
					self._terminate_process()
				self._polling = False
				return
			self._poll_after_id = self.after(_TERM_FRAME_MS if backlog else 50, self._poll)
		except Exception:
			try:
				if self.winfo_exists():
					self._poll_after_id = self.after(_TERM_FRAME_MS, self._poll)
			except Exception:
				pass
		self._polling = False
	def _key(self, event):
		self._unpost_menu()
		if not self.running:
			return 'break'
		sym = event.keysym
		ch = event.char
		if ch or sym in ('Return', 'BackSpace', 'Delete', 'Up', 'Down', 'Left', 'Right', 'Tab', 'ISO_Left_Tab', 'Home', 'End', 'Prior', 'Next', 'Insert'):
			self._clear_selection()
		_kmod = 1 + (1 if event.state & 1 else 0) + (4 if event.state & 4 else 0)
		try:
			if sym == 'Return':
				self._write(b'\r')
			elif sym == 'BackSpace':
				self._write(b'\x7f')
			elif sym == 'ISO_Left_Tab' or (sym == 'Tab' and (event.state & 1)):
				self._write(b'\x1b[Z')
			elif sym == 'Tab':
				self._write(b'\t')
			elif sym in self._term_csi_keys:
				_kl = self._term_csi_keys[sym]
				if _kmod > 1:
					self._write(f'\x1b[1;{_kmod}{_kl}'.encode())
				elif self._app_cursor:
					self._write(('\x1bO' + _kl).encode())
				else:
					self._write(('\x1b[' + _kl).encode())
			elif sym in self._term_tilde_keys:
				_kn = self._term_tilde_keys[sym]
				if _kmod > 1:
					self._write(f'\x1b[{_kn};{_kmod}~'.encode())
				else:
					self._write(f'\x1b[{_kn}~'.encode())
			elif sym in self._term_ss3_keys:
				_kl = self._term_ss3_keys[sym]
				if _kmod > 1:
					self._write(f'\x1b[1;{_kmod}{_kl}'.encode())
				else:
					self._write(('\x1bO' + _kl).encode())
			elif (event.state & 4) and sym in ('space', 'at', '2'):
				self._write(b'\x00')
			elif (event.state & 4) and sym in ('bracketleft', '3'):
				self._write(b'\x1b')
			elif (event.state & 4) and sym in ('backslash', '4'):
				self._write(b'\x1c')
			elif (event.state & 4) and sym in ('bracketright', '5'):
				self._write(b'\x1d')
			elif (event.state & 4) and sym in ('asciicircum', '6'):
				self._write(b'\x1e')
			elif (event.state & 4) and sym in ('underscore', 'slash', '7'):
				self._write(b'\x1f')
			elif ch:
				self._write(ch.encode('utf-8'))
		except Exception:
			pass
		return 'break'
	def _meta_key(self, event):
		self._unpost_menu()
		if not self.running:
			return 'break'
		self._clear_selection()
		sym = event.keysym
		ch = event.char
		try:
			if ch:
				self._write(b'\x1b' + ch.encode('utf-8'))
			elif sym in ('Left', 'Right', 'Up', 'Down'):
				_pfx = b'\x1bO' if self._app_cursor else b'\x1b['
				self._write(b'\x1b' + {'Left': b'b', 'Right': b'f', 'Up': _pfx + b'A', 'Down': _pfx + b'B'}[sym])
		except Exception:
			pass
		return 'break'
	def _clear_selection(self):
		try:
			self.tag_remove('sel', '1.0', 'end')
		except Exception:
			pass
	def _copy_selection(self, e = None):
		try:
			first = self.index('sel.first')
			last = self.index('sel.last')
		except Exception:
			return 'break'
		start_line = int(first.split('.')[0])
		end_line = int(last.split('.')[0])
		parts = []
		for ln in range(start_line, end_line + 1):
			a = first if ln == start_line else f'{ln}.0'
			b = last if ln == end_line else f'{ln}.end'
			seg = self.get(a, b)
			if parts and 'wrapcont' in self.tag_names(f'{ln}.0'):
				parts[-1] += seg
			else:
				parts.append(seg)
		sel = '\n'.join(parts)
		if sel:
			self.clipboard_clear()
			self.clipboard_append(sel)
		return 'break'
	def _paste_clipboard(self, e = None):
		if not self.running:
			return 'break'
		try:
			data = self.clipboard_get()
		except Exception:
			return 'break'
		if data:
			data = data.replace('\r\n', '\r').replace('\n', '\r')
			payload = data.encode('utf-8')
			if self._bracketed_paste:
				payload = b'\x1b[200~' + payload + b'\x1b[201~'
			try:
				self._write(payload)
				self._clear_selection()
			except Exception:
				pass
		return 'break'
	def _select_all(self, e = None):
		self.tag_add('sel', '1.0', 'end-1c')
		return 'break'
	def _unpost_menu(self):
		if self._menu_posted:
			self._menu_posted = False
			try:
				self._termmenu.unpost()
			except Exception:
				pass
	def _termmenu_keyclose(self, e):
		if e.keysym not in ('Up', 'Down', 'Left', 'Right', 'Return', 'space', 'Shift_L', 'Shift_R', 'Control_L', 'Control_R', 'Alt_L', 'Alt_R'):
			self._unpost_menu()
			return 'break'
	def _popup(self, e):
		self.focus_set()
		self._menu_posted = True
		try:
			self._termmenu.tk_popup(e.x_root, e.y_root)
		finally:
			self._termmenu.grab_release()
		return 'break'
	def _snap_caret(self, e = None):
		def _do():
			try:
				self.mark_set('insert', self.cursor)
			except Exception:
				pass
		try:
			self.after_idle(_do)
		except Exception:
			pass
	def _term_mouse_pos(self, event):
		idx = self.index(f'@{event.x},{event.y}')
		line, col = idx.split('.')
		top = self.index('@0,0').split('.')[0]
		row = int(line) - int(top) + 1
		row = max(1, min(row, max(1, self._GRID_ROWS)))
		colnum = max(1, min(int(col) + 1, max(1, self._GRID_COLS)))
		return colnum, row
	def _term_mouse_mods(self, event):
		mods = 0
		if event.state & 0x1:
			mods |= 4
		if event.state & 0x8:
			mods |= 8
		if event.state & 0x4:
			mods |= 16
		return mods
	def _term_send_mouse(self, button, event, release = False, drag = False):
		if not self.running:
			return False
		if not self._mouse_mode:
			return False
		if event.state & 0x1:
			return False
		if drag and self._mouse_mode < 1002:
			return False
		col, row = self._term_mouse_pos(event)
		if drag and not release and (col, row) == self._mouse_last_pos:
			return True
		mods = self._term_mouse_mods(event)
		cb = button + mods
		if drag:
			cb += 32
		try:
			if self._mouse_sgr:
				suffix = 'm' if release else 'M'
				self._write(f'\x1b[<{cb};{col};{row}{suffix}'.encode())
			else:
				if release:
					cb = 3 + mods
				self._write(bytes([27, ord('['), ord('M'), min(cb + 32, 255), min(col + 32, 255), min(row + 32, 255)]))
		except Exception:
			pass
		self._mouse_last_pos = (col, row)
		return True
	def _term_button1_press(self, event):
		self._unpost_menu()
		self.focus_set()
		if self._term_send_mouse(0, event):
			return 'break'
	def _term_button1_release(self, event):
		self.focus_set()
		if self._term_send_mouse(0, event, release = True):
			return 'break'
		self._snap_caret(event)
	def _term_button1_motion(self, event):
		self.focus_set()
		if self._term_send_mouse(0, event, drag = True):
			return 'break'
	def _term_button2_press(self, event):
		self.focus_set()
		if self._term_send_mouse(1, event):
			return 'break'
		return self._paste_clipboard(event)
	def _term_button2_motion(self, event):
		self.focus_set()
		if self._term_send_mouse(1, event, drag = True):
			return 'break'
	def _term_button2_release(self, event):
		self.focus_set()
		if self._term_send_mouse(1, event, release = True):
			return 'break'
	def _term_button3_press(self, event):
		self.focus_set()
		if self._term_send_mouse(2, event):
			return 'break'
	def _term_button3_release(self, event):
		self.focus_set()
		if self._term_send_mouse(2, event, release = True):
			return 'break'
		return self._popup(event)
	def _term_button3_motion(self, event):
		self.focus_set()
		if self._term_send_mouse(2, event, drag = True):
			return 'break'
	def _term_motion(self, event):
		if event.state & (0x100 | 0x200 | 0x400):
			return
		if self._mouse_mode == 1003:
			self._term_send_mouse(3, event, drag = True)
	def _term_wheel(self, event):
		self.focus_set()
		button = 65
		if event.num == 4:
			button = 64
		elif event.num == 5:
			button = 65
		elif getattr(event, 'delta', 0) > 0:
			button = 64
		if self._term_send_mouse(button, event):
			return 'break'
		self.after_idle(self._term_update_follow)
	def _term_update_follow(self):
		try:
			self._follow_bottom = self.yview()[1] >= 0.999
		except Exception:
			pass
	def _term_follow_view(self):
		if self._alt_mode:
			self.see('end')
			self.see('insert')
		else:
			self._term_materialize_screen()
			self.see(f'{self.screen_top + self._VT_ROWS - 1}.0')
			self.see(f'{self.screen_top}.0')
	def _focus_in(self, e):
		if self._focus_reporting and self.running:
			try:
				self._write(b'\x1b[I')
			except Exception:
				pass
	def _focus_out(self, e):
		if self._focus_reporting and self.running:
			try:
				self._write(b'\x1b[O')
			except Exception:
				pass
	def _term_on_theme_changed(self, e = None):
		if self._alt_mode or self._reverse_screen:
			return
		try:
			_bg = self.cget('background')
			_fg = self.cget('foreground')
		except Exception:
			return
		if _bg == self._term_default_bg and _fg == self._term_default_fg:
			return
		self._term_default_bg = _bg
		self._term_default_fg = _fg
		self._default_fg_rgb = self.winfo_rgb(_fg)
		self._default_bg_rgb = self.winfo_rgb(_bg)
		self.tag_configure('sel', background = _fg, foreground = _bg)
		if not self._alt_mode:
			self.config(insertbackground = _fg)
		if not self.nocolor:
			self._recompute_sgr_tag()
class TerminalBuffer(Buffer):
	def __init__(self, master, command, title, endmessage, *args, **kwargs):
		super().__init__(master, *args, **kwargs)
		self.m = state.root.menu()
		for label, menu in state.all_terminal_menus.items():
			self.m.add_cascade(label = label, menu = menu)
		pycode.pcrunhook('before', 'open-terminal', command)
		command = (command or (['/bin/bash'] if platform.system() == 'Linux' else ['powershell.exe']))
		self.term = Terminal(self, command, endmessage)
		command = ' '.join(command)
		self.setwanttitle('*PyNotes Terminal* - ' + command)
		self.fileinfoconfig(buffertype = '*PyNotes Terminal*', title = title, command = command)
		self.term.pack(fill = 'both', expand = True)
		self.mainwidget = self.term
		self.cp = self.term._copy_selection
		self.pst = self.term._paste_clipboard
		self.selall = self.term._select_all
		pycode.pcrunhook('after', 'open-terminal', command)
		bindrecur(self, '<FocusIn>', lambda event, buffer = self: window.setactive(state.all_buffers.index(buffer)))
		self.term.realbind('<FocusIn>', lambda event, buffer = self: window.setactive(state.all_buffers.index(buffer)), add = '+')
		self.term.realbind('<<TerminalProcessEnded>>', lambda event, buffer = self: buffer.setwanttitle('*PyNotes Terminal* - ' + command + ' - finished'))
		self.term.realbind('<<TerminalStopped>>', lambda event, buffer = self: pycode.pcclosebuff(state.all_buffers.index(buffer)))
	@property
	def running(self):
		return self.term.running
	def close(self):
		if not self.term.running:
			return True
		answer = state.root.ask('Warning', 'Kill active process and close?', options = ('ok', 'cancel'))
		if answer != None:
			return answer
		return False
def term(command = None, title = 'Terminal', endmessage = None, blocking = False, orient = 'vertical', *args, **kwargs):
	term = window.newbuffer(TerminalBuffer, orient, command, title, endmessage, *args, **kwargs)
	if blocking == True:
		while term.winfo_exists():
			state.root.update()
