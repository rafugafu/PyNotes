import platform
import state
from init import monospace
from buffer import Buffer
from utils import bindrecur
from python_scope_build import _PYTHON_BUILTIN_MEMBERS, _PYTHON_BUILTIN_NAMES, _PYTHON_KW_PAT, _PYTHON_OP_PAT, _python_bytecol_to_charcol
import python_scope_build
import pycode
import terminal
import utils
import window
class PythonShellBuffer(Buffer):
	def __init__(self, master, *args, **kwargs):
		super().__init__(master, *args, **kwargs)
		self.m = state.root.menu()
		for label, menu in state.all_pythonshell_menus.items():
			self.m.add_cascade(label = label, menu = menu)
		self.setwanttitle(f'*Python Shell*')
		self.fileinfoconfig(buffertype = '*Python Shell*', interpreter = state.pythonexecutable)
		self.hmode = 'python'
		self._shell_setview_after_id = None
		self._hapyshell_running = [False]
		self._pyshell_last_scan_key = None
		self._pyshell_cached_scope_result = None
		self._pyshell_session_names = {}
		self._pyshell_session_types = {}
		self._pyshell_session_classes = {}
		self._pyshell_session_aliases = {}
		self._pyshell_session_origins = {}
		self._pyshell_session_method_params = {}
		self._pyshell_session_accepts_any = set()
		self._pyshell_session_module_bases = {}
		self._pyshell_session_func_origins = {}
		self._pyshell_session_attr_types = {}
		self._pyshell_session_class_attr_types = {}
		self._pyshell_session_func_params = {}
		self._pyshell_session_func_accepts_any = {}
		self._pyshell_session_class_bases = {}
		self._pyshell_session_inherited = {'members': set(), 'attr_types': set(), 'method_params': set()}
		self._pyshell_session_instance_only = {}
		self._python_module_spec_cache = {}
		self._python_module_members_cache = {}
		self._python_module_class_members_cache = {}
		self._python_module_func_params_cache = {}
		pycode.pcrunhook('before', 'open-python-shell')
		self.shellpy()
		self.init_pythonshell_hl_tags()
		self.mainwidget = self.shellcmd
		self.cp = self.shellcmd._copy_selection
		self.pst = self.shellcmd._paste_clipboard
		self.selall = self.shellcmd._select_all
		bindrecur(self, '<FocusIn>', lambda event, buffer = self: window.setactive(state.all_buffers.index(buffer)))
		self.shellcmd.realbind('<FocusIn>', lambda event, buffer = self: window.setactive(state.all_buffers.index(buffer)), add = '+')
		pycode.pcrunhook('after', 'open-python-shell')
	def init_pythonshell_hl_tags(self):
		exec("self.shellcmd.tag_config('hpa'," + state.theme['python:keywords'].replace('type_', 'self.shellcmd') + ')')
		exec("self.shellcmd.tag_config('hpb'," + state.theme['python:inbuilt'].replace('type_', 'self.shellcmd') + ')')
		exec("self.shellcmd.tag_config('hpv'," + state.theme['python:variable_names'].replace('type_', 'self.shellcmd') + ')')
		exec("self.shellcmd.tag_config('hpi'," + state.theme['python:class_instances'].replace('type_', 'self.shellcmd') + ')')
		exec("self.shellcmd.tag_config('hpf'," + state.theme['python:function_names'].replace('type_', 'self.shellcmd') + ')')
		exec("self.shellcmd.tag_config('hpx'," + state.theme['python:class_names'].replace('type_', 'self.shellcmd') + ')')
		exec("self.shellcmd.tag_config('hpfa'," + state.theme['python:function_arguments'].replace('type_', 'self.shellcmd') + ')')
		exec("self.shellcmd.tag_config('hpm'," + state.theme['python:module_names'].replace('type_', 'self.shellcmd') + ')')
		exec("self.shellcmd.tag_config('hpo'," + state.theme['python:operators'].replace('type_', 'self.shellcmd') + ')')
		exec("self.shellcmd.tag_config('hpd'," + state.theme['python:strings'].replace('type_', 'self.shellcmd') + ')')
		exec("self.shellcmd.tag_config('hpc'," + state.theme['python:comments'].replace('type_', 'self.shellcmd') + ')')
	def shellpy(self):
		lenprompt = len('>>> ')
		_hl_pending = [False]
		def colourprompts():
			lines = int(self.shellcmd.index('end-1c').split('.')[0])
			self.shellcmd.tag_remove('prompt', '1.0', 'end')
			for i in range(1, lines + 1):
				if not self.shellcmd.get(f'{i}.0', f'{i}.{lenprompt}') in {'>>> ', '... '}:
					continue
				self.shellcmd.tag_add('prompt', f'{i}.0', f'{i}.{lenprompt}')
			self.shellcmd.tag_config('prompt', foreground = 'green', font = (monospace, 12, 'bold'))
		def _schedule_hl():
			if not _hl_pending[0]:
				_hl_pending[0] = True
				def _run_hl():
					_hl_pending[0] = False
					self.hapyshell()
				self.shellcmd.after_idle(_run_hl)
		def _on_output(event):
			colourprompts()
			_schedule_hl()
		def _make_shellcmd():
			widget = terminal.Terminal(self, [state.pythonexecutable], None, nocolor = True)
			widget.pack(fill = 'both', expand = True)
			widget.realbind('<<TerminalStopped>>', lambda event: ks())
			widget.realbind('<<TerminalOutputProcessed>>', _on_output)
			return widget
		def cs():
			self._pyshell_last_scan_key = None
			self._pyshell_cached_scope_result = None
			self.shellcmd.delete('1.0', 'end')
			self.shellcmd.focus()
			try:
				self.shellcmd._write(b'\x0c' if platform.system() == 'Linux' else b'\r')
			except Exception:
				pass
		def ks():
			self._pyshell_last_scan_key = None
			self._pyshell_cached_scope_result = None
			self._pyshell_session_names.clear()
			self._pyshell_session_types.clear()
			self._pyshell_session_classes.clear()
			self._pyshell_session_module_bases.clear()
			self._pyshell_session_func_origins.clear()
			self._pyshell_session_attr_types.clear()
			self._pyshell_session_class_attr_types.clear()
			self._pyshell_session_aliases.clear()
			self._pyshell_session_origins.clear()
			self._pyshell_session_method_params.clear()
			self._pyshell_session_accepts_any.clear()
			self._pyshell_session_func_params.clear()
			self._pyshell_session_func_accepts_any.clear()
			self._pyshell_session_class_bases.clear()
			for _inhk in ('members', 'attr_types', 'method_params'):
				self._pyshell_session_inherited[_inhk].clear()
			self._pyshell_session_instance_only.clear()
			self.shellcmd.restart()
			self.shellcmd.focus_set()
		self._shellbuttons = state.root.frame(master = self)
		clearshell = state.root.button(master = self._shellbuttons, text = 'Clear Shell', command = cs)
		killshell = state.root.button(master = self._shellbuttons, text = 'Restart Shell', command = ks)
		self._shellbuttons.pack(side = 'bottom', fill = 'x')
		clearshell.pack(anchor = 'sw', side = 'left', padx = 10, pady = 10)
		killshell.pack(anchor = 'sw', side = 'left', padx = 10, pady = 10)
		self.shellcmd = _make_shellcmd()
		def shell_setview():
			if not self.winfo_exists():
				return
			self.hapyshell()
			self._shell_setview_after_id = self.after(50, shell_setview)
		self._shell_setview_after_id = self.after(50, shell_setview)
	def hapyshell(self):
		if self._hapyshell_running[0]:
			return
		self._hapyshell_running[0] = True
		try:
			self._hapyshell_body()
		finally:
			self._hapyshell_running[0] = False
	def _hapyshell_body(self):
		lenprompt = len('>>> ')
		full_text = self.shellcmd.get('1.0', 'end')
		real_lines = full_text.split('\n')
		n_real = len(real_lines)
		wrapcont_flags = [False] * (n_real + 1)
		for _rl in range(2, n_real + 1):
			try:
				if 'wrapcont' in self.shellcmd.tag_names(f'{_rl - 1}.end'):
					wrapcont_flags[_rl] = True
			except Exception:
				pass
		stripped_lines = []
		_shell_line_blocks = []
		_shell_seg_map = []
		_shell_logical_real_range = []
		_shell_real_to_logical = {}
		_blk = 0
		_exec_boundary = 1
		_rl = 1
		while _rl <= n_real:
			content = real_lines[_rl - 1]
			prefix = content[:lenprompt]
			if prefix in ('>>> ', '... '):
				seg_text = content[lenprompt:]
				segs = [(_rl, lenprompt, len(seg_text))]
				_nxt = _rl + 1
				while _nxt <= n_real:
					_next_content = real_lines[_nxt - 1]
					if _next_content[:lenprompt] in ('>>> ', '... '):
						break
					_is_autowrap_cont = wrapcont_flags[_nxt]
					_is_pyrepl_cont = seg_text.endswith('\\')
					if not (_is_autowrap_cont or _is_pyrepl_cont):
						break
					if _is_pyrepl_cont and not _is_autowrap_cont:
						seg_text = seg_text[:-1]
						_last_line, _last_col, _last_len = segs[-1]
						segs[-1] = (_last_line, _last_col, _last_len - 1)
					segs.append((_nxt, 0, len(_next_content)))
					seg_text += _next_content
					_nxt += 1
				stripped_lines.append(seg_text)
				_shell_seg_map.append(segs)
				_shell_logical_real_range.append((_rl, _nxt - 1))
				if prefix == '>>> ':
					_blk += 1
					_exec_boundary = len(stripped_lines)
				_shell_line_blocks.append(_blk)
				for _rr in range(_rl, _nxt):
					_shell_real_to_logical[_rr] = len(stripped_lines)
				_rl = _nxt
			else:
				stripped_lines.append('')
				_shell_seg_map.append([])
				_shell_logical_real_range.append((_rl, _rl))
				_shell_line_blocks.append(0)
				_shell_real_to_logical[_rl] = len(stripped_lines)
				_rl += 1
		stripped_text = '\n'.join(stripped_lines)
		_scan_key = (stripped_text, tuple(_shell_line_blocks))
		if _scan_key == self._pyshell_last_scan_key:
			shell_result = self._pyshell_cached_scope_result
		else:
			shell_result = python_scope_build._python_build_scopes(self, stripped_text, line_blocks = _shell_line_blocks, seed_names = self._pyshell_session_names, seed_types = self._pyshell_session_types, seed_classes = self._pyshell_session_classes, seed_aliases = self._pyshell_session_aliases, seed_origins = self._pyshell_session_origins, seed_method_params = self._pyshell_session_method_params, seed_accepts_any = self._pyshell_session_accepts_any, seed_module_bases = self._pyshell_session_module_bases, seed_func_origins = self._pyshell_session_func_origins, seed_attr_types = self._pyshell_session_attr_types, seed_class_attr_types = self._pyshell_session_class_attr_types, seed_func_params = self._pyshell_session_func_params, seed_func_accepts_any = self._pyshell_session_func_accepts_any, seed_class_bases = self._pyshell_session_class_bases, seed_inherited = self._pyshell_session_inherited, seed_instance_only = self._pyshell_session_instance_only)
			self._pyshell_last_scan_key = _scan_key
			self._pyshell_cached_scope_result = shell_result
		if shell_result is None:
			shell_scopes = [{'start': 1, 'end': 1, 'parent': None, 'names': {}}]
			shell_call_kwargs = {}
			shell_module_aliases = {}
			shell_local_classes = {}
			shell_module_literals = []
			shell_scope_var_types = {}
			shell_literal_attrs = []
			shell_def_names = []
			shell_typed_attrs = []
			shell_param_default_tags = []
			shell_kwarg_positions = []
			shell_import_dotted_lines = []
			shell_import_orig_name_tags = []
			shell_name_positions = []
			shell_class_module_origin = {}
			shell_local_class_method_params = {}
			shell_local_class_accepts_any = set()
			shell_local_class_module_origins = {}
			shell_from_func_module = {}
			shell_class_type_maps = {}
			shell_class_attr_types = {}
			shell_func_params = {}
			shell_func_accepts_any = {}
			shell_class_bases = {}
			shell_inherited = {}
			shell_module_scope_class_keys = set()
			shell_instance_only = {}
			shell_instance_name_positions = set()
			shell_global_stmt_kind_positions = {}
		else:
			shell_scopes, shell_call_kwargs, shell_module_aliases, shell_local_classes, shell_module_literals, shell_scope_var_types, shell_literal_attrs, shell_def_names, shell_typed_attrs, shell_param_default_tags, shell_kwarg_positions, shell_import_dotted_lines, shell_import_orig_name_tags, shell_class_module_origin, shell_local_class_method_params, shell_local_class_accepts_any, shell_name_positions, shell_local_class_module_origins, shell_from_func_module, shell_class_type_maps, shell_class_attr_types, shell_func_params, shell_func_accepts_any, shell_class_bases, shell_inherited, shell_module_scope_class_keys, shell_instance_only, shell_instance_name_positions, shell_global_stmt_kind_positions = shell_result
		for _nm, _defs in shell_scopes[0]['names'].items():
			_exec_defs = [_d for _d in _defs if _d[0] < _exec_boundary]
			if _exec_defs and _nm not in shell_scopes[0].get('globals', {}) and _nm not in shell_scopes[0].get('nonlocals', {}):
				_best_def = _exec_defs[0]
				for _d in _exec_defs:
					if _d[0] >= _best_def[0]:
						_best_def = _d
				self._pyshell_session_names[_nm] = _best_def[1]
		for _nm, _tl in shell_scope_var_types.get(0, {}).items():
			_exec_tl = [_t for _t in _tl if _t[0] < _exec_boundary]
			if _exec_tl:
				_best_tl = _exec_tl[0]
				for _t in _exec_tl:
					if _t[0] >= _best_tl[0]:
						_best_tl = _t
				self._pyshell_session_types[_nm] = _best_tl[1]
		_text_class_lines = {}
		for _dl, _dcol, _dn, _dk in shell_def_names:
			if _dk == 'class':
				_text_class_lines.setdefault(_dn, []).append(_dl)
		for _cn, _mem in shell_local_classes.items():
			if _cn in _PYTHON_BUILTIN_MEMBERS:
				continue
			if _cn in _text_class_lines and _cn not in shell_module_scope_class_keys:
				continue
			_cls_lines = _text_class_lines.get(_cn)
			if _cls_lines is None or _cn in self._pyshell_session_classes or any(_l < _exec_boundary for _l in _cls_lines):
				self._pyshell_session_classes[_cn] = _mem
		for _an, _adefs in shell_module_aliases.items():
			_abest = None
			for _ad in _adefs:
				if _ad[0] < _exec_boundary and (_abest is None or _ad[0] >= _abest[0]):
					_abest = _ad
			if _abest is not None:
				self._pyshell_session_aliases[_an] = _abest[1]
		for _on, _odefs in shell_class_module_origin.items():
			_obest = None
			for _od in _odefs:
				if _od[0] < _exec_boundary and (_obest is None or _od[0] >= _obest[0]):
					_obest = _od
			if _obest is not None:
				self._pyshell_session_origins[_on] = _obest[1]
		for _mpk, _mpv in shell_local_class_method_params.items():
			if _mpk.split('.')[0] in shell_module_scope_class_keys:
				self._pyshell_session_method_params[_mpk] = _mpv
		for _mbk, _mbv in shell_local_class_module_origins.items():
			self._pyshell_session_module_bases.setdefault(_mbk, [])
			for _mbo in _mbv:
				if _mbo not in self._pyshell_session_module_bases[_mbk]:
					self._pyshell_session_module_bases[_mbk].append(_mbo)
		for _ffk, _ffv in shell_from_func_module.items():
			if _ffv and _ffk not in self._pyshell_session_func_origins:
				_ff_best = max(_ffv, key = lambda _x: _x[0])
				self._pyshell_session_func_origins[_ffk] = _ff_best[1]
		for _ctk, _ctv in shell_class_type_maps.items():
			self._pyshell_session_attr_types[_ctk] = dict(_ctv)
		for _catk, _catv in shell_class_attr_types.items():
			self._pyshell_session_class_attr_types[_catk] = dict(_catv)
		for _aak in shell_local_class_accepts_any:
			if _aak.split('.')[0] in shell_module_scope_class_keys:
				self._pyshell_session_accepts_any.add(_aak)
		self._pyshell_session_func_params.update(shell_func_params)
		self._pyshell_session_func_accepts_any.update(shell_func_accepts_any)
		self._pyshell_session_class_bases.update(shell_class_bases)
		for _inhk in ('members', 'attr_types', 'method_params'):
			self._pyshell_session_inherited[_inhk].update(shell_inherited.get(_inhk, ()))
		for _iok, _iov in shell_instance_only.items():
			self._pyshell_session_instance_only.setdefault(_iok, set()).update(_iov)
		try:
			shell_top = self.shellcmd.index('@0,0')
			shell_bottom = self.shellcmd.index(f'@0,{self.shellcmd.winfo_height()}')
		except Exception:
			shell_top = '1.0'
			shell_bottom = 'end'
		try:
			all_tags = set(self.shellcmd.tag_names())
			def _removable(tag):
				return tag not in state._PYTHON_SHELL_HL_SKIP_REMOVE_TAGS and (tag not in state.skiptagspythonshell or self.hmode not in state.skiptagspythonshell[tag])
			shell_top_line_real = int(shell_top.split('.')[0])
			shell_top_line = _shell_real_to_logical.get(shell_top_line_real, 1)
			if shell_top_line < _exec_boundary:
				shell_top_line = _exec_boundary
				if 0 <= shell_top_line - 1 < len(_shell_logical_real_range):
					_clamp_first_real = _shell_logical_real_range[shell_top_line - 1][0]
				else:
					_clamp_first_real = shell_top_line_real
				shell_top = f'{_clamp_first_real}.0'
			shell_bottom_line = len(stripped_lines)
			shell_bottom = 'end'
			vis_abs = list(range(shell_top_line, shell_bottom_line + 1))
			vis_code = [stripped_lines[L - 1] if 0 <= L - 1 < len(stripped_lines) else '' for L in vis_abs]
			visible_code = '\n'.join(vis_code)
			line_starts = []
			_acc = 0
			for _l in vis_code:
				line_starts.append(_acc)
				_acc += len(_l) + 1
			def widx(line, col):
				segs = _shell_seg_map[line - 1] if 0 <= line - 1 < len(_shell_seg_map) else None
				if not segs:
					_fr = _shell_logical_real_range[line - 1][0] if 0 <= line - 1 < len(_shell_logical_real_range) else line
					return f'{_fr}.{col}'
				_cum = 0
				for _seg_line, _seg_col, _seg_len in segs:
					if col <= _cum + _seg_len:
						return f'{_seg_line}.{_seg_col + (col - _cum)}'
					_cum += _seg_len
				_last_line, _last_col, _last_len = segs[-1]
				return f'{_last_line}.{_last_col + _last_len}'
			def off2lc(off):
				lo = 0
				for _i in range(len(line_starts)):
					if line_starts[_i] <= off:
						lo = _i
					else:
						break
				return shell_top_line + lo, off - line_starts[lo]
			def clear_idx(a, b):
				for _t in all_tags:
					if _removable(_t):
						self.shellcmd.tag_remove(_t, a, b)
			def add_idx(tag, a, b):
				for _t in all_tags:
					if _t != tag and _removable(_t):
						self.shellcmd.tag_remove(_t, a, b)
				self.shellcmd.tag_add(tag, a, b)
			def add_span(tag, off_s, off_e):
				l1, c1 = off2lc(off_s)
				l2, c2 = off2lc(off_e)
				add_idx(tag, widx(l1, c1), widx(l2, c2))
			for tag in all_tags:
				if _removable(tag):
					self.shellcmd.tag_remove(tag, shell_top, shell_bottom)
			for m in _PYTHON_KW_PAT.finditer(visible_code):
				add_span('hpa', m.start(), m.end())
			line_scope_candidates = {}
			for line in vis_abs:
				_cands = []
				for k, sc in enumerate(shell_scopes):
					if sc['start'] <= line <= sc['end']:
						_cands.append((sc['start'], sc.get('start_col', 0), sc['end'], sc.get('end_col'), k))
				line_scope_candidates[line] = _cands
			def _resolve_scope_idx(line, col):
				winner = None
				winner_start = None
				for _cstart, _ccol, _cend, _ecol, _ck in line_scope_candidates.get(line, ()):
					if _cstart == line and col < _ccol:
						continue
					if _cend == line and _ecol is not None and col >= _ecol:
						continue
					if winner is None or _cstart >= winner_start:
						winner = _ck
						winner_start = _cstart
				return winner
			shell_module_literal_lines = {}
			for lineno, _mcol, name in shell_module_literals:
				shell_module_literal_lines.setdefault(lineno, []).append((_mcol, name))
			shell_import_dotted_by_line = {}
			for lineno, dcol, dotted in shell_import_dotted_lines:
				shell_import_dotted_by_line.setdefault(lineno, []).append((dcol, dotted))
			shell_import_orig_by_line = {}
			for _oln, _ocol, _oname, _otag in shell_import_orig_name_tags:
				shell_import_orig_by_line.setdefault(_oln, []).append((_ocol, _oname, _otag))
			def _shell_same_block(l1, l2):
				if l1 == l2:
					return True
				if not (0 < l1 <= len(_shell_line_blocks)) or not (0 < l2 <= len(_shell_line_blocks)):
					return False
				_b1 = _shell_line_blocks[l1 - 1]
				return _b1 != 0 and _b1 == _shell_line_blocks[l2 - 1]
			shell_name_pos_by_line = {}
			for _nl, _ncol, _nname, _nstore in shell_name_positions:
				shell_name_pos_by_line.setdefault(_nl, []).append((_ncol, _nname, _nstore))
			shell_def_names_by_line = {}
			for _dl, _dcol, _dname, _dkind in shell_def_names:
				shell_def_names_by_line.setdefault(_dl, []).append((_dcol, _dname, _dkind))
			shell_kind_tags = {'var': 'hpv', 'instance': 'hpi', 'func': 'hpf', 'func_arg': 'hpfa', 'first_param': 'hpb', 'module': 'hpm', 'class': 'hpx', 'builtin': 'hpb'}
			shell_literal_attr_by_line = {}
			for _ln, _col, _attr, _tname in shell_literal_attrs:
				shell_literal_attr_by_line.setdefault(_ln, []).append((_col, _attr, _tname))
			shell_typed_attr_by_line = {}
			for _tl, _tcol, _tattr, _tkind in shell_typed_attrs:
				shell_typed_attr_by_line.setdefault(_tl, []).append((_tcol, _tattr, _tkind))
			shell_param_default_by_line = {}
			for _pl, _pcol, _pname, _pkind in shell_param_default_tags:
				shell_param_default_by_line.setdefault(_pl, []).append((_pcol, _pname, _pkind))
			shell_kwarg_pos_by_line = {}
			for _kl, _kcol, _kname in shell_kwarg_positions:
				shell_kwarg_pos_by_line.setdefault(_kl, []).append((_kcol, _kname))
			_shell_active_cache = {}
			def _shell_active_for(abs_line, scope_idx):
				_ckey = (abs_line, scope_idx)
				if _ckey in _shell_active_cache:
					return _shell_active_cache[_ckey]
				active = {}
				prior_kinds = {}
				bound = set()
				innermost_scope = scope_idx
				innermost_parent = shell_scopes[innermost_scope]['parent'] if innermost_scope is not None else None
				on_header = innermost_scope is not None and abs_line == shell_scopes[innermost_scope]['start']
				_redir_names = set()
				_rsi = innermost_scope
				while _rsi is not None:
					_rsc = shell_scopes[_rsi]
					_redir_names |= set(_rsc.get('globals', {}))
					_redir_names |= set(_rsc.get('nonlocals', {}))
					_rsi = _rsc['parent']
				_sidx = scope_idx
				while _sidx is not None:
					sc = shell_scopes[_sidx]
					if sc.get('kind') == 'class' and _sidx != innermost_scope and not (on_header and _sidx == innermost_parent):
						_sidx = sc['parent']
						continue
					sc_globals = sc.get('globals', {})
					sc_nonlocals = sc.get('nonlocals', {})
					for name, defs in sc['names'].items():
						if name in active or name in bound:
							continue
						if name in sc_globals or name in sc_nonlocals:
							continue
						best = None
						second_best = None
						latest = None
						_guard = _sidx == innermost_scope or name in _redir_names
						for dl, kind in defs:
							if latest is None or dl > latest[0]:
								latest = (dl, kind)
							if _guard and dl > abs_line:
								continue
							if best is None or dl > best[0]:
								second_best = best
								best = (dl, kind)
							elif second_best is None or dl > second_best[0]:
								second_best = (dl, kind)
						if best is None and latest is not None and _shell_same_block(latest[0], abs_line) and name not in _PYTHON_BUILTIN_NAMES:
							best = latest
						bound.add(name)
						if best is not None:
							active[name] = best[1]
							if best[0] == abs_line and second_best is not None and second_best[1] != best[1]:
								prior_kinds[name] = second_best[1]
					_sidx = sc['parent']
				_result = (active, prior_kinds)
				_shell_active_cache[_ckey] = _result
				return _result
			for li, abs_line in enumerate(vis_abs):
				line_str = vis_code[li]
				for _ncol, _nname, _nstore in shell_name_pos_by_line.get(abs_line, []):
					_nkind = shell_global_stmt_kind_positions.get((abs_line, _ncol))
					if _nkind is None:
						active, prior_kinds = _shell_active_for(abs_line, _resolve_scope_idx(abs_line, _ncol))
						_nkind = active.get(_nname)
						if _nkind is None:
							if _nname not in _PYTHON_BUILTIN_NAMES:
								continue
							_nkind = 'builtin'
						elif not _nstore and _nname in prior_kinds:
							_nkind = prior_kinds[_nname]
					_ntag = shell_kind_tags.get(_nkind)
					if _ntag is None:
						continue
					if _ntag == 'hpv' and (abs_line, _ncol) in shell_instance_name_positions:
						_ntag = 'hpi'
					_nccol = _python_bytecol_to_charcol(line_str, _ncol)
					s = widx(abs_line, _nccol)
					e = widx(abs_line, _nccol + len(_nname))
					add_idx(_ntag, s, e)
				for _dcol, _dname, _dkind in shell_def_names_by_line.get(abs_line, []):
					_dccol = _python_bytecol_to_charcol(line_str, _dcol)
					s = widx(abs_line, _dccol)
					e = widx(abs_line, _dccol + len(_dname))
					add_idx('hpf' if _dkind == 'func' else 'hpx', s, e)
				for _pcol, _pname, _pkind in shell_param_default_by_line.get(abs_line, []):
					if _pkind == 'var' and (abs_line, _pcol) in shell_instance_name_positions:
						_pkind = 'instance'
					_pcol = _python_bytecol_to_charcol(line_str, _pcol)
					_ptag = {'var': 'hpv', 'instance': 'hpi', 'func': 'hpf', 'func_arg': 'hpfa', 'first_param': 'hpb', 'module': 'hpm', 'class': 'hpx'}.get(_pkind)
					if _ptag is not None:
						s = widx(abs_line, _pcol)
						e = widx(abs_line, _pcol + len(_pname))
						add_idx(_ptag, s, e)
				for _mcol, name in shell_module_literal_lines.get(abs_line, []):
					_mccol = _python_bytecol_to_charcol(line_str, _mcol)
					if line_str[_mccol:_mccol + len(name)] != name:
						continue
					add_idx('hpm', widx(abs_line, _mccol), widx(abs_line, _mccol + len(name)))
				for dcol, dotted in shell_import_dotted_by_line.get(abs_line, []):
					dcol = _python_bytecol_to_charcol(line_str, dcol)
					if line_str[dcol:dcol + len(dotted)] != dotted:
						continue
					pos = dcol
					for part in dotted.split('.'):
						add_idx('hpm', widx(abs_line, pos), widx(abs_line, pos + len(part)))
						pos += len(part) + 1
				for _ocol, _oname, _otag in shell_import_orig_by_line.get(abs_line, []):
					_ocol = _python_bytecol_to_charcol(line_str, _ocol)
					if line_str[_ocol:_ocol + len(_oname)] != _oname:
						continue
					add_idx(_otag, widx(abs_line, _ocol), widx(abs_line, _ocol + len(_oname)))
				for _col, _attr, _tname in shell_literal_attr_by_line.get(abs_line, []):
					_col = _python_bytecol_to_charcol(line_str, _col)
					_kind = _PYTHON_BUILTIN_MEMBERS[_tname].get(_attr)
					if _kind is not None:
						add_idx('hpf' if _kind == 'func' else 'hpv', widx(abs_line, _col), widx(abs_line, _col + len(_attr)))
				for _tcol, _tattr, _tkind in shell_typed_attr_by_line.get(abs_line, []):
					_tcol = _python_bytecol_to_charcol(line_str, _tcol)
					_ttag = {'func': 'hpf', 'var': 'hpv', 'instance': 'hpi', 'module': 'hpm', 'class': 'hpx'}.get(_tkind, 'hpx')
					add_idx(_ttag, widx(abs_line, _tcol), widx(abs_line, _tcol + len(_tattr)))
				for _kcol, _kname in shell_kwarg_pos_by_line.get(abs_line, []):
					_kcol = _python_bytecol_to_charcol(line_str, _kcol)
					s = widx(abs_line, _kcol)
					e = widx(abs_line, _kcol + len(_kname))
					clear_idx(s, e)
					if _kname in shell_call_kwargs.get(abs_line, set()):
						self.shellcmd.tag_add('hpfa', s, e)
			for m in _PYTHON_OP_PAT.finditer(visible_code):
				add_span('hpo', m.start(), m.end())
			shell_pre_text = '\n'.join(stripped_lines[:shell_top_line - 1])
			if shell_pre_text:
				shell_pre_text += '\n'
			pre_n = len(shell_pre_text)
			pre_i = 0
			in_triple = False
			triple_ch = None
			in_single = False
			single_ch = None
			while pre_i < pre_n:
				pch = shell_pre_text[pre_i]
				if pch in ('"', "'") and pre_i + 2 < pre_n and shell_pre_text[pre_i + 1] == pch and shell_pre_text[pre_i + 2] == pch:
					pquote = shell_pre_text[pre_i:pre_i + 3]
					j = pre_i + 3
					found_close = False
					while j < pre_n:
						if shell_pre_text[j] == '\\':
							j += 2
							continue
						if shell_pre_text[j:j + 3] == pquote:
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
					closed = False
					while j < pre_n:
						if shell_pre_text[j] == '\\':
							j += 2
							continue
						if shell_pre_text[j] == pquote:
							j += 1
							closed = True
							break
						if shell_pre_text[j] == '\n':
							closed = True
							break
						j += 1
					if not closed:
						in_single = True
						single_ch = pquote
						break
					pre_i = j
				elif pch == '#':
					j = pre_i + 1
					while j < pre_n and shell_pre_text[j] != '\n':
						j += 1
					if j < pre_n:
						j += 1
					pre_i = j
				else:
					pre_i += 1
			n = len(visible_code)
			i = 0
			if in_triple:
				quote = triple_ch * 3
				j = 0
				found_close = False
				while j < n:
					if visible_code[j] == '\\':
						j += 2
						continue
					if visible_code[j:j + 3] == quote:
						j += 3
						found_close = True
						break
					j += 1
				if not found_close:
					j = n
				add_span('hpd', 0, j)
				i = j
			elif in_single:
				quote = single_ch
				j = 0
				while j < n:
					if visible_code[j] == '\\':
						j += 2
						continue
					if visible_code[j] == quote:
						j += 1
						break
					if visible_code[j] == '\n':
						break
					j += 1
				if j > n:
					j = n
				add_span('hpd', 0, j)
				i = j
			while i < n:
				ch = visible_code[i]
				if ch in ('"', "'") and i + 2 < n and visible_code[i + 1] == ch and visible_code[i + 2] == ch:
					quote = visible_code[i:i + 3]
					j = i + 3
					found_close = False
					while j < n:
						if visible_code[j] == '\\':
							j += 2
							continue
						if visible_code[j:j + 3] == quote:
							j += 3
							found_close = True
							break
						j += 1
					if not found_close:
						j = n
					add_span('hpd', i, j)
					i = j
				elif ch in ('"', "'"):
					quote = ch
					j = i + 1
					while j < n:
						if visible_code[j] == '\\':
							j += 2
							continue
						if visible_code[j] == quote:
							j += 1
							break
						if visible_code[j] == '\n':
							break
						j += 1
					add_span('hpd', i, j)
					i = j
				elif ch == '#':
					j = i + 1
					while j < n and visible_code[j] != '\n':
						j += 1
					add_span('hpc', i, j)
					i = j
				else:
					i += 1
		except Exception:
			pass
	@property
	def running(self):
		return self.shellcmd.running
	def close(self):
		if not self.shellcmd.running:
			return True
		answer = state.root.ask('Warning', 'Kill active process and close?', options = ('ok', 'cancel'))
		if answer != None:
			return answer
		return False
	def _cancel_all_after_ids(self):
		if self._shell_setview_after_id is not None:
			try:
				self.after_cancel(self._shell_setview_after_id)
			except Exception:
				pass
			self._shell_setview_after_id = None
def _init_pythonshell_hl_tags():
	for buffer in state.all_buffers:
		if isinstance(buffer, PythonShellBuffer):
			buffer.init_pythonshell_hl_tags()
def openpythonshell(orient = 'vertical'):
	newbuff = window.newbuffer(PythonShellBuffer, orient)
	newbuff.shellcmd.focus()
	utils.show('opened python shell')
	return newbuff
