import os
import sys
import ast
import threading
import warnings
_PYTHON_BUILTIN_MEMBERS = {}
for _bt in (str, int, float, list, dict, tuple, set, frozenset, bool, bytes, bytearray):
	_ms = {}
	for _nm in dir(_bt):
		if not _nm.startswith('_'):
			_ms[_nm] = 'func' if callable(getattr(_bt, _nm, None)) else 'var'
	_PYTHON_BUILTIN_MEMBERS[_bt.__name__] = _ms
del _bt, _ms, _nm
def _python_build_builtin_callable_params():
	import builtins
	import inspect
	out = {}
	for name in dir(builtins):
		obj = getattr(builtins, name, None)
		if not callable(obj):
			continue
		try:
			sig = inspect.signature(obj)
		except (ValueError, TypeError):
			continue
		kw = {pn for pn, pp in sig.parameters.items() if pp.kind in (pp.POSITIONAL_OR_KEYWORD, pp.KEYWORD_ONLY)}
		if kw:
			out[name] = kw
	return out
try:
	_PYTHON_BUILTIN_CALLABLE_PARAMS = _python_build_builtin_callable_params()
except Exception:
	_PYTHON_BUILTIN_CALLABLE_PARAMS = {}
del _python_build_builtin_callable_params
for _bn, _bkw in {'min': {'key', 'default'}, 'max': {'key', 'default'}, 'int': {'base'}, 'str': {'encoding', 'errors'}, 'bytes': {'encoding', 'errors'}, 'bytearray': {'encoding', 'errors'}}.items():
	_PYTHON_BUILTIN_CALLABLE_PARAMS.setdefault(_bn, _bkw)
del _bn, _bkw
import builtins as _bmod
_PYTHON_BUILTIN_CALLABLE_NAMES = {n for n in dir(_bmod) if callable(getattr(_bmod, n, None))}
_PYTHON_BUILTIN_NAMES = set(dir(_bmod))
del _bmod
_PYTHON_BUILTIN_METHOD_RETURNS = {'str': {'capitalize': 'str', 'casefold': 'str', 'center': 'str', 'expandtabs': 'str', 'format': 'str', 'format_map': 'str', 'join': 'str', 'ljust': 'str', 'lower': 'str', 'lstrip': 'str', 'removeprefix': 'str', 'removesuffix': 'str', 'replace': 'str', 'rjust': 'str', 'rstrip': 'str', 'strip': 'str', 'swapcase': 'str', 'title': 'str', 'translate': 'str', 'upper': 'str', 'zfill': 'str', 'split': 'list', 'rsplit': 'list', 'splitlines': 'list', 'partition': 'tuple', 'rpartition': 'tuple', 'encode': 'bytes', 'count': 'int', 'find': 'int', 'index': 'int', 'rfind': 'int', 'rindex': 'int', 'maketrans': 'dict', 'isalnum': 'bool', 'isalpha': 'bool', 'isascii': 'bool', 'isdecimal': 'bool', 'isdigit': 'bool', 'isidentifier': 'bool', 'islower': 'bool', 'isnumeric': 'bool', 'isprintable': 'bool', 'isspace': 'bool', 'istitle': 'bool', 'isupper': 'bool', 'startswith': 'bool', 'endswith': 'bool'}, 'bytes': {'capitalize': 'bytes', 'center': 'bytes', 'expandtabs': 'bytes', 'hex': 'str', 'join': 'bytes', 'ljust': 'bytes', 'lower': 'bytes', 'lstrip': 'bytes', 'removeprefix': 'bytes', 'removesuffix': 'bytes', 'replace': 'bytes', 'rjust': 'bytes', 'rstrip': 'bytes', 'strip': 'bytes', 'swapcase': 'bytes', 'title': 'bytes', 'translate': 'bytes', 'upper': 'bytes', 'zfill': 'bytes', 'decode': 'str', 'split': 'list', 'rsplit': 'list', 'splitlines': 'list', 'partition': 'tuple', 'rpartition': 'tuple', 'count': 'int', 'find': 'int', 'index': 'int', 'rfind': 'int', 'rindex': 'int', 'maketrans': 'dict', 'isalnum': 'bool', 'isalpha': 'bool', 'isascii': 'bool', 'isdigit': 'bool', 'islower': 'bool', 'isspace': 'bool', 'istitle': 'bool', 'isupper': 'bool', 'startswith': 'bool', 'endswith': 'bool'}, 'bytearray': {'capitalize': 'bytearray', 'center': 'bytearray', 'expandtabs': 'bytearray', 'hex': 'str', 'join': 'bytearray', 'ljust': 'bytearray', 'lower': 'bytearray', 'lstrip': 'bytearray', 'removeprefix': 'bytearray', 'removesuffix': 'bytearray', 'replace': 'bytearray', 'rjust': 'bytearray', 'rstrip': 'bytearray', 'strip': 'bytearray', 'swapcase': 'bytearray', 'title': 'bytearray', 'translate': 'bytearray', 'upper': 'bytearray', 'zfill': 'bytearray', 'decode': 'str', 'split': 'list', 'rsplit': 'list', 'splitlines': 'list', 'partition': 'tuple', 'rpartition': 'tuple', 'count': 'int', 'find': 'int', 'index': 'int', 'rfind': 'int', 'rindex': 'int', 'maketrans': 'dict', 'isalnum': 'bool', 'isalpha': 'bool', 'isascii': 'bool', 'isdigit': 'bool', 'islower': 'bool', 'isspace': 'bool', 'istitle': 'bool', 'isupper': 'bool', 'startswith': 'bool', 'endswith': 'bool'}, 'list': {'copy': 'list', 'count': 'int', 'index': 'int'}, 'dict': {'copy': 'dict', 'keys': 'list', 'values': 'list', 'items': 'list', 'fromkeys': 'dict'}, 'set': {'copy': 'set', 'union': 'set', 'intersection': 'set', 'difference': 'set', 'symmetric_difference': 'set', 'isdisjoint': 'bool', 'issubset': 'bool', 'issuperset': 'bool'}, 'frozenset': {'copy': 'frozenset', 'union': 'frozenset', 'intersection': 'frozenset', 'difference': 'frozenset', 'symmetric_difference': 'frozenset', 'isdisjoint': 'bool', 'issubset': 'bool', 'issuperset': 'bool'}, 'int': {'bit_length': 'int', 'bit_count': 'int', 'conjugate': 'int', 'as_integer_ratio': 'tuple', 'to_bytes': 'bytes'}, 'float': {'conjugate': 'float', 'as_integer_ratio': 'tuple', 'hex': 'str', 'is_integer': 'bool'}}
class _PythonScanCancelled(BaseException):
	pass
class _PythonScopeBuilder(ast.NodeVisitor):
	def __init__(self):
		self.scopes = [{'start': 1, 'end': 1, 'start_col': 0, 'end_col': None, 'parent': None, 'kind': 'module', 'names': {}, 'globals': {}, 'nonlocals': {}}]
		self.scope_stack = [0]
		self.func_params = {}
		self.func_accepts_any = {}
		self.pending_calls = []
		self.module_aliases = {}
		self.module_alias_lines = {}
		self.module_alias_defs = {}
		self.from_imports = []
		self.import_names = []
		self.module_literals = []
		self.import_dotted_lines = []
		self.import_orig_names = []
		self.def_names = []
		self.kwarg_positions = []
		self.alias_assigns = []
		self.dotted_alias_assigns = []
		self.dynamic_imports = []
		self.class_def_kwargs = []
		self.global_seed_names = set()
		self.nonlocal_seeds = []
		self._in_class_body = False
	def add_name(self, name, lineno, kind):
		sc_idx = self.scope_stack[-1]
		sc = self.scopes[sc_idx]
		if name in sc.get('globals', {}):
			sc_idx = 0
		elif name in sc.get('nonlocals', {}):
			_p = sc['parent']
			while _p is not None:
				_ps = self.scopes[_p]
				if _ps.get('kind') == 'function' and name not in _ps.get('globals', {}) and name not in _ps.get('nonlocals', {}):
					sc_idx = _p
					break
				_p = _ps['parent']
		names = self.scopes[sc_idx]['names']
		names.setdefault(name, []).append((lineno, kind))
	def targets(self, node):
		out = []
		if isinstance(node, ast.Name):
			out.append(node)
		elif isinstance(node, ast.Attribute):
			out.append(node)
		elif isinstance(node, (ast.Tuple, ast.List)):
			for elt in node.elts:
				out.extend(self.targets(elt))
		elif isinstance(node, ast.Starred):
			out.extend(self.targets(node.value))
		return out
	def push_scope(self, start, end, kind = 'function', start_col = 0, end_col = None):
		idx = len(self.scopes)
		self.scopes.append({'start': start, 'end': end, 'start_col': start_col, 'end_col': end_col, 'parent': self.scope_stack[-1], 'kind': kind, 'names': {}, 'globals': {}, 'nonlocals': {}})
		self.scope_stack.append(idx)
		return idx
	def add_args(self, args, lineno, is_method = False):
		all_args = list(args.posonlyargs) + list(args.args) + list(args.kwonlyargs)
		for i, a in enumerate(all_args):
			self.add_name(a.arg, lineno, 'first_param' if (is_method and i == 0) else 'func_arg')
		if args.vararg:
			self.add_name(args.vararg.arg, lineno, 'func_arg')
		if args.kwarg:
			self.add_name(args.kwarg.arg, lineno, 'func_arg')
	def visit_FunctionDef(self, node):
		self.visit_function(node)
	def visit_AsyncFunctionDef(self, node):
		self.visit_function(node)
	def visit_function(self, node):
		self.add_name(node.name, node.lineno, 'func')
		self.def_names.append((node.lineno, node.name, 'func'))
		params = set()
		for a in list(node.args.args) + list(node.args.kwonlyargs):
			params.add(a.arg)
		self.func_params.setdefault(node.name, []).append((node.lineno, params, self.scope_stack[-1]))
		self.func_accepts_any.setdefault(node.name, []).append((node.lineno, bool(node.args.kwarg), self.scope_stack[-1]))
		for dec in node.decorator_list:
			self.visit(dec)
		for d in list(node.args.defaults) + [kd for kd in node.args.kw_defaults if kd is not None]:
			self.visit(d)
		end = getattr(node, 'end_lineno', node.lineno)
		is_method = self._in_class_body and _python_method_has_implicit_first_param(node)
		prev_in_class_body = self._in_class_body
		self._in_class_body = False
		self.push_scope(node.lineno, end, start_col = node.col_offset)
		self.add_args(node.args, node.lineno, is_method)
		for stmt in node.body:
			self.visit(stmt)
		self.scope_stack.pop()
		self._in_class_body = prev_in_class_body
	def _dotted_path(self, node):
		parts = []
		cur = node
		while isinstance(cur, ast.Attribute):
			parts.append(cur.attr)
			cur = cur.value
		if isinstance(cur, ast.Name):
			parts.append(cur.id)
			parts.reverse()
			return parts
		return None
	def visit_Call(self, node):
		func_name = None
		is_name = isinstance(node.func, ast.Name)
		if is_name:
			func_name = node.func.id
		elif isinstance(node.func, ast.Attribute):
			func_name = node.func.attr
		dotted = self._dotted_path(node.func)
		for kw in node.keywords:
			if kw.arg is not None:
				self.pending_calls.append((getattr(kw, 'lineno', node.lineno), func_name, kw.arg, is_name, dotted, node))
				kw_lineno = getattr(kw, 'lineno', None)
				kw_col = getattr(kw, 'col_offset', None)
				if kw_lineno is not None and kw_col is not None:
					self.kwarg_positions.append((kw_lineno, kw_col, kw.arg))
		self.generic_visit(node)
	def visit_ClassDef(self, node):
		self.add_name(node.name, node.lineno, 'class')
		self.def_names.append((node.lineno, node.name, 'class'))
		for _ckw in node.keywords:
			if _ckw.arg is None:
				continue
			_ckwl = getattr(_ckw, 'lineno', node.lineno)
			_ckwc = getattr(_ckw, 'col_offset', None)
			if _ckwc is not None:
				self.kwarg_positions.append((_ckwl, _ckwc, _ckw.arg))
			self.class_def_kwargs.append((_ckwl, node.name, node.lineno, _ckw.arg))
		for dec in node.decorator_list:
			self.visit(dec)
		end = getattr(node, 'end_lineno', node.lineno)
		self.push_scope(node.lineno, end, 'class', node.col_offset)
		prev_in_class_body = self._in_class_body
		self._in_class_body = True
		for stmt in node.body:
			self.visit(stmt)
		self._in_class_body = prev_in_class_body
		self.scope_stack.pop()
		for stmt in node.body:
			if isinstance(stmt, ast.FunctionDef) and stmt.name == '__init__':
				_iargs = list(stmt.args.posonlyargs) + list(stmt.args.args) + list(stmt.args.kwonlyargs)
				params = set(a.arg for a in _iargs[1:]) - set(a.arg for a in stmt.args.posonlyargs)
				if stmt.args.vararg:
					params.add(stmt.args.vararg.arg)
				if stmt.args.kwarg:
					params.add(stmt.args.kwarg.arg)
				self.func_accepts_any.setdefault(node.name, []).append((node.lineno, bool(stmt.args.kwarg), self.scope_stack[-1]))
				self.func_params.setdefault(node.name, []).append((node.lineno, params, self.scope_stack[-1]))
				break
	def visit_Lambda(self, node):
		end = getattr(node, 'end_lineno', node.lineno)
		self.push_scope(node.lineno, end, start_col = node.col_offset, end_col = getattr(node, 'end_col_offset', None))
		self.add_args(node.args, node.lineno)
		self.visit(node.body)
		self.scope_stack.pop()
	def visit_comp(self, node):
		end = getattr(node, 'end_lineno', node.lineno)
		self.push_scope(node.lineno, end, start_col = node.col_offset, end_col = getattr(node, 'end_col_offset', None))
		for gen in node.generators:
			for nm in self.targets(gen.target):
				if not isinstance(nm, ast.Attribute):
					self.add_name(nm.id, node.lineno, 'var')
			self.visit(gen.iter)
			for cond in gen.ifs:
				self.visit(cond)
		if isinstance(node, ast.DictComp):
			self.visit(node.key)
			self.visit(node.value)
		else:
			self.visit(node.elt)
		self.scope_stack.pop()
	def visit_ListComp(self, node):
		self.visit_comp(node)
	def visit_SetComp(self, node):
		self.visit_comp(node)
	def visit_DictComp(self, node):
		self.visit_comp(node)
	def visit_GeneratorExp(self, node):
		self.visit_comp(node)
	def _register_lambda(self, name, lineno, lam):
		_largs = lam.args
		_lparams = set(a.arg for a in list(_largs.args) + list(_largs.kwonlyargs))
		self.func_params.setdefault(name, []).append((lineno, _lparams, self.scope_stack[-1]))
		self.func_accepts_any.setdefault(name, []).append((lineno, bool(_largs.kwarg), self.scope_stack[-1]))
	def visit_Assign(self, node):
		_is_lambda = isinstance(node.value, ast.Lambda)
		for t in node.targets:
			if _is_lambda and isinstance(t, ast.Name):
				self.add_name(t.id, node.lineno, 'func')
				self._register_lambda(t.id, node.lineno, node.value)
				continue
			for nm in self.targets(t):
				if not isinstance(nm, ast.Attribute):
					self.add_name(nm.id, node.lineno, 'var')
		for _ntgt in node.targets:
			if not isinstance(_ntgt, ast.Name):
				continue
			tgt_name = _ntgt.id
			val = node.value
			if isinstance(val, ast.Name):
				self.alias_assigns.append((self.scope_stack[-1], node.lineno, tgt_name, val.id))
			elif isinstance(val, ast.Attribute):
				self.dotted_alias_assigns.append((self.scope_stack[-1], node.lineno, tgt_name, val))
			elif isinstance(val, ast.Call):
				_dr = self._dynamic_import_module(val)
				if _dr is not None:
					self.dynamic_imports.append((self.scope_stack[-1], node.lineno, tgt_name, _dr[0], _dr[1]))
				_pt = _python_partial_target(val)
				if _pt is not None:
					self.alias_assigns.append((self.scope_stack[-1], node.lineno, tgt_name, _pt))
		for _ttgt in node.targets:
			if not (isinstance(_ttgt, (ast.Tuple, ast.List)) and isinstance(node.value, (ast.Tuple, ast.List)) and len(_ttgt.elts) == len(node.value.elts)):
				continue
			for _tgt_el, _val_el in zip(_ttgt.elts, node.value.elts):
				if not isinstance(_tgt_el, ast.Name):
					continue
				if isinstance(_val_el, ast.Name):
					self.alias_assigns.append((self.scope_stack[-1], node.lineno, _tgt_el.id, _val_el.id))
				elif isinstance(_val_el, ast.Attribute):
					self.dotted_alias_assigns.append((self.scope_stack[-1], node.lineno, _tgt_el.id, _val_el))
				elif isinstance(_val_el, ast.Call):
					_dr = self._dynamic_import_module(_val_el)
					if _dr is not None:
						self.dynamic_imports.append((self.scope_stack[-1], node.lineno, _tgt_el.id, _dr[0], _dr[1]))
		self.visit(node.value)
	def _dynamic_import_module(self, call):
		fn = call.func
		is_builtin_import = isinstance(fn, ast.Name) and fn.id == '__import__'
		is_importlib = isinstance(fn, ast.Attribute) and fn.attr == 'import_module'
		if not (is_builtin_import or is_importlib) or not call.args:
			return None
		arg = call.args[0]
		if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
			if is_builtin_import and not _python_import_fromlist_is_nonempty(call):
				return arg.value.split('.')[0], is_builtin_import
			return arg.value, is_builtin_import
		return None
	def visit_AnnAssign(self, node):
		if isinstance(node.value, ast.Lambda) and isinstance(node.target, ast.Name):
			self.add_name(node.target.id, node.lineno, 'func')
			self._register_lambda(node.target.id, node.lineno, node.value)
			self.visit(node.value)
			return
		for nm in self.targets(node.target):
			if not isinstance(nm, ast.Attribute):
				self.add_name(nm.id, node.lineno, 'var')
		if node.value is not None:
			self.visit(node.value)
	def visit_AugAssign(self, node):
		for nm in self.targets(node.target):
			if not isinstance(nm, ast.Attribute):
				self.add_name(nm.id, node.lineno, 'var')
		self.visit(node.value)
	def visit_For(self, node):
		self.visit_for(node)
	def visit_AsyncFor(self, node):
		self.visit_for(node)
	def visit_for(self, node):
		for nm in self.targets(node.target):
			if not isinstance(nm, ast.Attribute):
				self.add_name(nm.id, node.lineno, 'var')
		self.visit(node.iter)
		for stmt in node.body:
			self.visit(stmt)
		for stmt in node.orelse:
			self.visit(stmt)
	def visit_With(self, node):
		self.visit_with(node)
	def visit_AsyncWith(self, node):
		self.visit_with(node)
	def visit_with(self, node):
		for item in node.items:
			self.visit(item.context_expr)
			if item.optional_vars is not None:
				for nm in self.targets(item.optional_vars):
					if not isinstance(nm, ast.Attribute):
						self.add_name(nm.id, node.lineno, 'var')
		for stmt in node.body:
			self.visit(stmt)
	def visit_ExceptHandler(self, node):
		if node.name:
			self.add_name(node.name, node.lineno, 'var')
		if node.type is not None:
			self.visit(node.type)
		for stmt in node.body:
			self.visit(stmt)
	def visit_Import(self, node):
		for alias in node.names:
			imported_name = alias.name
			top_name = imported_name.split('.')[0]
			used_name = alias.asname if alias.asname else top_name
			self.import_names.append((self.scope_stack[-1], imported_name, top_name, used_name, node.lineno))
			self.module_literals.append((node.lineno, top_name))
			if '.' in imported_name:
				_acol = getattr(alias, 'col_offset', None)
				if _acol is not None:
					self.import_dotted_lines.append((node.lineno, _acol, imported_name))
			if alias.asname:
				self.module_aliases[alias.asname] = imported_name
				self.module_alias_lines[alias.asname] = node.lineno
				self.module_alias_defs.setdefault(alias.asname, []).append((node.lineno, imported_name))
	def visit_ImportFrom(self, node):
		if node.module:
			self.module_literals.append((node.lineno, node.module.split('.')[0]))
			if '.' in node.module:
				_fcol = getattr(node, 'col_offset', None)
				if _fcol is not None:
					self.import_dotted_lines.append((node.lineno, _fcol + 5, node.module))
		for alias in node.names:
			name = alias.asname if alias.asname else alias.name
			self.from_imports.append((self.scope_stack[-1], node.module, name, alias.name, node.lineno))
			if alias.asname and alias.name != '*':
				_ocol = getattr(alias, 'col_offset', None)
				if _ocol is not None:
					self.import_orig_names.append((node.lineno, _ocol, alias.name, node.module))
	def visit_NamedExpr(self, node):
		for nm in self.targets(node.target):
			if not isinstance(nm, ast.Attribute):
				self.add_name(nm.id, node.lineno, 'var')
		self.visit(node.value)
	def visit_Global(self, node):
		scope_idx = self.scope_stack[-1]
		for name in node.names:
			self.scopes[scope_idx]['globals'][name] = node.lineno
			self.global_seed_names.add(name)
	def visit_Nonlocal(self, node):
		scope_idx = self.scope_stack[-1]
		for name in node.names:
			self.scopes[scope_idx]['nonlocals'][name] = node.lineno
			parent_idx = self.scopes[scope_idx]['parent']
			if parent_idx is not None:
				self.nonlocal_seeds.append((parent_idx, name))
def _python_method_has_implicit_first_param(node):
	for dec in getattr(node, 'decorator_list', []):
		_dn = None
		if isinstance(dec, ast.Name):
			_dn = dec.id
		elif isinstance(dec, ast.Attribute):
			_dn = dec.attr
		elif isinstance(dec, ast.Call):
			_df = dec.func
			if isinstance(_df, ast.Name):
				_dn = _df.id
			elif isinstance(_df, ast.Attribute):
				_dn = _df.attr
		if _dn == 'staticmethod':
			return False
	return True
_PYTHON_DESCRIPTOR_WRAPPERS = {'staticmethod', 'classmethod'}
def _python_c3_linearize(cls, bases_map, seen, depth = 0):
	if cls in seen or depth > 40:
		return [cls]
	_seen2 = seen | {cls}
	_seqs = []
	for _b in bases_map.get(cls, []):
		_bl = _python_c3_linearize(_b, bases_map, _seen2, depth + 1)
		if _bl:
			_seqs.append(list(_bl))
	_direct = list(bases_map.get(cls, []))
	if _direct:
		_seqs.append(_direct)
	out = [cls]
	while _seqs:
		cand = None
		for _s in _seqs:
			_h = _s[0]
			if not any(_h in _o[1:] for _o in _seqs):
				cand = _h
				break
		if cand is None:
			cand = _seqs[0][0]
		if cand not in out:
			out.append(cand)
		_next = []
		for _s in _seqs:
			_s = [_x for _x in _s if _x != cand]
			if _s:
				_next.append(_s)
		_seqs = _next
	return out
def _python_partial_target(call):
	if not isinstance(call, ast.Call) or not call.args:
		return None
	_fn = call.func
	_isp = (isinstance(_fn, ast.Name) and _fn.id == 'partial') or (isinstance(_fn, ast.Attribute) and _fn.attr == 'partial')
	if not _isp:
		return None
	if isinstance(call.args[0], ast.Name):
		return call.args[0].id
	return None
def _python_unwrap_descriptor(val):
	while isinstance(val, ast.Call) and isinstance(val.func, ast.Name) and val.func.id in _PYTHON_DESCRIPTOR_WRAPPERS and len(val.args) == 1 and not val.keywords:
		val = val.args[0]
	return val
def _python_import_fromlist_is_nonempty(call):
	_fl = None
	if len(call.args) >= 4:
		_fl = call.args[3]
	else:
		for _kw in call.keywords:
			if _kw.arg == 'fromlist':
				_fl = _kw.value
				break
	if _fl is None:
		return False
	if isinstance(_fl, (ast.List, ast.Tuple, ast.Set)):
		return len(_fl.elts) > 0
	if isinstance(_fl, ast.Constant) and _fl.value is None:
		return False
	return True
def _python_static_value_kind(val, members, prefix):
	val = _python_unwrap_descriptor(val)
	if isinstance(val, ast.Lambda):
		return 'func'
	if isinstance(val, ast.Name):
		_k = members.get(f'{prefix}.{val.id}') if prefix else members.get(val.id)
		if _k is None:
			_k = members.get(val.id)
		if _k in ('func', 'class'):
			return _k
		if val.id in _PYTHON_BUILTIN_MEMBERS:
			return 'class'
		if val.id in _PYTHON_BUILTIN_CALLABLE_NAMES:
			return 'func'
	return None
def _python_inspect_ast_members(node_list, prefix = ''):
	members = {}
	for node in node_list:
		if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
			key = f'{prefix}.{node.name}' if prefix else node.name
			members[key] = 'func'
		elif isinstance(node, ast.ClassDef):
			key = f'{prefix}.{node.name}' if prefix else node.name
			members[key] = 'class'
			class_members = _python_inspect_ast_members(node.body, key)
			members.update(class_members)
			for _sub in node.body:
				if isinstance(_sub, (ast.FunctionDef, ast.AsyncFunctionDef)) and _sub.args.args and _python_method_has_implicit_first_param(_sub):
					_sfp = _sub.args.args[0].arg
					for _sst in ast.walk(_sub):
						_stgts = _sst.targets if isinstance(_sst, ast.Assign) else ([_sst.target] if isinstance(_sst, (ast.AnnAssign, ast.AugAssign)) else [])
						_sval = _sst.value if isinstance(_sst, (ast.Assign, ast.AnnAssign)) else None
						for _st in _stgts:
							_sdirect = not isinstance(_st, (ast.Tuple, ast.List))
							for _ste in (_st.elts if isinstance(_st, (ast.Tuple, ast.List)) else [_st]):
								if isinstance(_ste, ast.Starred):
									_ste = _ste.value
								if isinstance(_ste, ast.Attribute) and isinstance(_ste.value, ast.Name) and _ste.value.id == _sfp:
									_skind = (_python_static_value_kind(_sval, members, prefix) if _sdirect and _sval is not None else None) or 'var'
									members.setdefault(f'{key}.{_ste.attr}', _skind)
			if not prefix:
				is_global_enum = any(
					(isinstance(d, ast.Name) and d.id == 'global_enum') or
					(isinstance(d, ast.Attribute) and d.attr == 'global_enum')
					for d in node.decorator_list
				)
				if is_global_enum:
					pfx = key + '.'
					for sub_key, val in class_members.items():
						bare = sub_key[len(pfx):]
						if '.' not in bare:
							members[bare] = val
		elif isinstance(node, ast.Assign):
			for target in node.targets:
				for _tel in (target.elts if isinstance(target, (ast.Tuple, ast.List)) else [target]):
					if isinstance(_tel, ast.Starred):
						_tel = _tel.value
					if isinstance(_tel, ast.Name):
						key = f'{prefix}.{_tel.id}' if prefix else _tel.id
						members[key] = (_python_static_value_kind(node.value, members, prefix) if _tel is target else None) or 'var'
		elif isinstance(node, ast.AnnAssign):
			if isinstance(node.target, ast.Name):
				key = f'{prefix}.{node.target.id}' if prefix else node.target.id
				members[key] = _python_static_value_kind(node.value, members, prefix) or 'var'
		elif isinstance(node, (ast.For, ast.AsyncFor, ast.While)):
			members.update(_python_inspect_ast_members(node.body, prefix))
			members.update(_python_inspect_ast_members(node.orelse, prefix))
		elif isinstance(node, ast.If):
			members.update(_python_inspect_ast_members(node.body, prefix))
			members.update(_python_inspect_ast_members(node.orelse, prefix))
		elif isinstance(node, (ast.With, ast.AsyncWith)):
			members.update(_python_inspect_ast_members(node.body, prefix))
		elif isinstance(node, ast.Try):
			members.update(_python_inspect_ast_members(node.body, prefix))
			for _th in node.handlers:
				members.update(_python_inspect_ast_members(_th.body, prefix))
			members.update(_python_inspect_ast_members(node.orelse, prefix))
			members.update(_python_inspect_ast_members(node.finalbody, prefix))
	return members
import importlib.machinery as _python_importlib_machinery
_PYTHON_EXTENSION_SUFFIXES = tuple(_python_importlib_machinery.EXTENSION_SUFFIXES)
_PYTHON_STDLIB_BUILTIN_MODULES = set(sys.builtin_module_names)
class _PythonModuleSpec:
	def __init__(self, name, origin, search_locations):
		self.name = name
		self.origin = origin
		self.submodule_search_locations = search_locations
def _python_resolve_toplevel_fs(name):
	for _dir in sys.path:
		try:
			_dir = _dir or os.getcwd()
		except Exception:
			continue
		_pkg = os.path.join(_dir, name, '__init__.py')
		if os.path.isfile(_pkg):
			return _PythonModuleSpec(name, _pkg, [os.path.dirname(_pkg)])
		_pdir = os.path.join(_dir, name)
		if os.path.isdir(_pdir):
			return _PythonModuleSpec(name, None, [_pdir])
		_mod = os.path.join(_dir, name + '.py')
		if os.path.isfile(_mod):
			return _PythonModuleSpec(name, _mod, None)
		for _ext in _PYTHON_EXTENSION_SUFFIXES:
			if os.path.isfile(os.path.join(_dir, name + _ext)):
				return _PythonModuleSpec(name, os.path.join(_dir, name + _ext), None)
	if name in _PYTHON_STDLIB_BUILTIN_MODULES:
		return _PythonModuleSpec(name, 'built-in', None)
	return None
def _python_module_src_path(spec, name):
	if spec is None or not spec.origin:
		return None
	if spec.origin.endswith('.py') and os.path.isfile(spec.origin):
		return spec.origin
	for _cand_name in (name, getattr(spec, 'name', None)):
		if not _cand_name:
			continue
		for _sp in sys.path:
			_candidate = os.path.join(_sp, *_cand_name.split('.')) + '.py'
			if os.path.isfile(_candidate):
				return _candidate
			_pkg_init = os.path.join(_sp, *_cand_name.split('.'), '__init__.py')
			if os.path.isfile(_pkg_init):
				return _pkg_init
	return None
def _python_relative_import_target(name, level, module, is_package):
	if level == 0:
		return module
	base = name.split('.')
	_strip = level - 1 if is_package else level
	if _strip > 0:
		base = base[:-_strip] if _strip < len(base) else []
	if module:
		base = base + module.split('.')
	return '.'.join(base) if base else module
def _python_reset_scan_state(buf):
	buf._python_edit_generation[0] += 1
	buf._python_scopes = [{'start': 1, 'end': 1, 'parent': None, 'names': {}}]
	buf._python_call_kwargs = {}
	buf._python_module_literals = []
	buf._python_literal_attrs = []
	buf._python_name_positions = []
	buf._python_def_names = []
	buf._python_typed_attrs = []
	buf._python_param_default_tags = []
	buf._python_kwarg_positions = []
	buf._python_import_dotted_lines = []
	buf._python_import_orig_name_tags = []
	buf._python_instance_name_positions = set()
	buf._python_global_stmt_kind_positions = {}
	if buf.hmode == 'python':
		buf.python_trigger_name_scan()
def _python_find_spec_cached(buf, name):
	if name in buf._python_module_spec_cache:
		return buf._python_module_spec_cache[name]
	spec = _python_resolve_spec_fs(buf, name)
	buf._python_module_spec_cache[name] = spec
	return spec
def _python_resolve_spec_fs(buf, name):
	parts = name.split('.')
	if '' in parts or not parts:
		return None
	if len(parts) == 1:
		return _python_resolve_toplevel_fs(parts[0])
	parent = _python_find_spec_cached(buf, '.'.join(parts[:-1]))
	if parent is None or not parent.submodule_search_locations:
		return None
	leaf = parts[-1]
	for _dir in parent.submodule_search_locations:
		_pkg = os.path.join(_dir, leaf, '__init__.py')
		if os.path.isfile(_pkg):
			return _PythonModuleSpec(name, _pkg, [os.path.dirname(_pkg)])
		_pdir = os.path.join(_dir, leaf)
		if os.path.isdir(_pdir):
			return _PythonModuleSpec(name, None, [_pdir])
		_mod = os.path.join(_dir, leaf + '.py')
		if os.path.isfile(_mod):
			return _PythonModuleSpec(name, _mod, None)
		for _ext in _PYTHON_EXTENSION_SUFFIXES:
			if os.path.isfile(os.path.join(_dir, leaf + _ext)):
				return _PythonModuleSpec(name, os.path.join(_dir, leaf + _ext), None)
	return None
def _python_resolve_module_members(buf, name, visited = None):
	if name in buf._python_module_members_cache:
		return buf._python_module_members_cache[name]
	if visited is None:
		visited = set()
	if name in visited:
		return {}
	visited.add(name)
	spec = _python_find_spec_cached(buf, name)
	src_path = _python_module_src_path(spec, name)
	if src_path is None:
		buf._python_module_members_cache[name] = {}
		return {}
	try:
		with open(src_path, 'r', encoding = 'utf-8') as f:
			src = f.read()
		with warnings.catch_warnings():
			warnings.simplefilter('ignore')
			mod_ast = ast.parse(src)
	except Exception:
		buf._python_module_members_cache[name] = {}
		return {}
	members = _python_inspect_ast_members(mod_ast.body)
	_import_nodes = []
	def _collect_scope_imports(_stmts, _globals, _depth = 0):
		if _depth > 60:
			return
		for _st in _stmts:
			if isinstance(_st, (ast.Import, ast.ImportFrom)):
				if _globals is None:
					_import_nodes.append(_st)
				else:
					for _al in _st.names:
						_bound = _al.asname if _al.asname else _al.name.split('.')[0]
						if _bound in _globals:
							_import_nodes.append(_st)
							break
			elif isinstance(_st, ast.Global):
				if _globals is not None:
					_globals.update(_st.names)
			elif isinstance(_st, ast.If):
				_collect_scope_imports(_st.body, _globals, _depth + 1)
				_collect_scope_imports(_st.orelse, _globals, _depth + 1)
			elif isinstance(_st, ast.Try):
				_collect_scope_imports(_st.body, _globals, _depth + 1)
				for _h in _st.handlers:
					_collect_scope_imports(_h.body, _globals, _depth + 1)
				_collect_scope_imports(_st.orelse, _globals, _depth + 1)
				_collect_scope_imports(_st.finalbody, _globals, _depth + 1)
			elif isinstance(_st, (ast.With, ast.AsyncWith)):
				_collect_scope_imports(_st.body, _globals, _depth + 1)
			elif isinstance(_st, (ast.For, ast.AsyncFor, ast.While)):
				_collect_scope_imports(_st.body, _globals, _depth + 1)
				_collect_scope_imports(_st.orelse, _globals, _depth + 1)
			elif isinstance(_st, (ast.FunctionDef, ast.AsyncFunctionDef)):
				_fnglobals = set()
				for _sub in ast.walk(_st):
					if isinstance(_sub, ast.Global):
						_fnglobals.update(_sub.names)
				_collect_scope_imports(_st.body, _fnglobals, _depth + 1)
			elif isinstance(_st, ast.ClassDef):
				_collect_scope_imports(_st.body, set(), _depth + 1)
	_collect_scope_imports(mod_ast.body, None)
	for node in _import_nodes:
		if isinstance(node, ast.ImportFrom):
			sub_name = _python_relative_import_target(name, node.level, node.module, bool(getattr(spec, 'submodule_search_locations', None))) if (node.module or node.level) else name
			sub_members = None
			for alias in node.names:
				if alias.name == '*':
					if sub_members is None:
						sub_members = _python_resolve_module_members(buf, sub_name, visited)
					for k, v in sub_members.items():
						members.setdefault(k, v)
				else:
					exported = alias.asname if alias.asname else alias.name
					if exported not in members:
						if sub_members is None:
							sub_members = _python_resolve_module_members(buf, sub_name, visited)
						if alias.name in sub_members:
							members[exported] = sub_members[alias.name]
							pfx = alias.name + '.'
							for k, v in sub_members.items():
								if k.startswith(pfx):
									members[exported + k[len(alias.name):]] = v
						elif _python_find_spec_cached(buf, f'{sub_name}.{alias.name}') is not None:
							members[exported] = 'module'
							members['@modtarget:' + exported] = f'{sub_name}.{alias.name}'
		elif isinstance(node, ast.Import):
			for alias in node.names:
				if alias.asname:
					members.setdefault(alias.asname, 'module')
					members.setdefault('@modtarget:' + alias.asname, alias.name)
				else:
					members.setdefault(alias.name.split('.')[0], 'module')
					members.setdefault('@modtarget:' + alias.name.split('.')[0], alias.name.split('.')[0])
	buf._python_module_members_cache[name] = members
	return members
def _python_resolve_module_member_kind(buf, mod, class_name, member, seen = None):
	if seen is None:
		seen = set()
	key = (mod, class_name)
	if key in seen:
		return None
	seen.add(key)
	mems = _python_resolve_module_members(buf, mod)
	_dk = f'{class_name}.{member}'
	if _dk in mems:
		if _dk in _python_resolve_module_func_params(buf, mod):
			return 'func'
		return mems[_dk]
	fp = _python_resolve_module_func_params(buf, mod)
	imports = fp.get('@imports', {})
	if '@bases:' + class_name not in fp and class_name in imports and imports[class_name][1] is not None:
		return _python_resolve_module_member_kind(buf, imports[class_name][0], imports[class_name][1], member, seen)
	for base in fp.get('@bases:' + class_name, []):
		bparts = base.split('.')
		if len(bparts) == 1:
			if '@bases:' + base in fp:
				_r = _python_resolve_module_member_kind(buf, mod, base, member, seen)
				if _r is not None:
					return _r
			elif base in imports and imports[base][1] is not None:
				_r = _python_resolve_module_member_kind(buf, imports[base][0], imports[base][1], member, seen)
				if _r is not None:
					return _r
		else:
			broot = bparts[0]
			if broot in imports:
				bmod = imports[broot][0]
				full_mod = '.'.join([bmod] + bparts[1:-1]) if len(bparts) > 2 else bmod
				_r = _python_resolve_module_member_kind(buf, full_mod, bparts[-1], member, seen)
				if _r is not None:
					return _r
	return None
def _python_resolve_module_class_members(buf, mod, class_name, seen = None):
	_top_call = seen is None
	if _top_call and (mod, class_name) in buf._python_module_class_members_cache:
		return buf._python_module_class_members_cache[(mod, class_name)]
	if seen is None:
		seen = set()
	key = (mod, class_name)
	if key in seen:
		return {}
	seen.add(key)
	mems = _python_resolve_module_members(buf, mod)
	prefix = class_name + '.'
	out = {k[len(prefix):]: v for k, v in mems.items() if k.startswith(prefix) and '.' not in k[len(prefix):]}
	fp = _python_resolve_module_func_params(buf, mod)
	for _mk in out:
		if prefix + _mk in fp:
			out[_mk] = 'func'
	imports = fp.get('@imports', {})
	if '@bases:' + class_name not in fp and class_name in imports and imports[class_name][1] is not None:
		for k, v in _python_resolve_module_class_members(buf, imports[class_name][0], imports[class_name][1], seen).items():
			out.setdefault(k, v)
	for base in fp.get('@bases:' + class_name, []):
		bparts = base.split('.')
		if len(bparts) == 1:
			if '@bases:' + base in fp:
				for k, v in _python_resolve_module_class_members(buf, mod, base, seen).items():
					out.setdefault(k, v)
			elif base in imports and imports[base][1] is not None:
				for k, v in _python_resolve_module_class_members(buf, imports[base][0], imports[base][1], seen).items():
					out.setdefault(k, v)
		else:
			broot = bparts[0]
			if broot in imports:
				bmod = imports[broot][0]
				full_mod = '.'.join([bmod] + bparts[1:-1]) if len(bparts) > 2 else bmod
				for k, v in _python_resolve_module_class_members(buf, full_mod, bparts[-1], seen).items():
					out.setdefault(k, v)
	if _top_call:
		buf._python_module_class_members_cache[(mod, class_name)] = out
	return out
def _python_build_scopes(buf, text, gen = None, line_blocks = None, seed_names = None, seed_types = None, seed_classes = None, seed_aliases = None, seed_origins = None, seed_method_params = None, seed_accepts_any = None, seed_module_bases = None, seed_func_origins = None, seed_attr_types = None, seed_class_attr_types = None, seed_func_params = None, seed_func_accepts_any = None, seed_class_bases = None, seed_inherited = None, seed_instance_only = None):
	def _ck():
		if gen is not None and buf._python_edit_generation[0] != gen:
			raise _PythonScanCancelled()
	def _same_block(l1, l2):
		if line_blocks is None or l1 == l2:
			return True
		if not (0 < l1 <= len(line_blocks)) or not (0 < l2 <= len(line_blocks)):
			return False
		_b1 = line_blocks[l1 - 1]
		return _b1 != 0 and _b1 == line_blocks[l2 - 1]
	def _assign_pairs(targets, value):
		pairs = []
		def _pair(t, v):
			if isinstance(t, ast.Starred):
				_pair(t.value, None)
			elif isinstance(t, (ast.Tuple, ast.List)):
				if isinstance(v, (ast.Tuple, ast.List)) and len(v.elts) == len(t.elts):
					for _t2, _v2 in zip(t.elts, v.elts):
						_pair(_t2, _v2)
				else:
					_ev = v if isinstance(v, ast.JoinedStr) or (isinstance(v, ast.Constant) and isinstance(v.value, str)) else None
					for _t2 in t.elts:
						_pair(_t2, _ev)
			else:
				pairs.append((t, v))
		for t in targets:
			_pair(t, value)
		return pairs
	lines = text.split('\n')
	tree = None
	for _ in range(len(lines) + 2):
		_ck()
		try:
			with warnings.catch_warnings():
				warnings.simplefilter('ignore')
				tree = ast.parse('\n'.join(lines))
			break
		except (SyntaxError, SyntaxWarning) as error:
			ln = max(1, min(getattr(error, 'lineno', None) or 1, len(lines)))
			msg = getattr(error, 'msg', '') or ''
			target = ln - 1
			if 'unexpected indent' in msg and ln > 1:
				indent_n = len(lines[ln - 1]) - len(lines[ln - 1].lstrip())
				earlier_same = any(lines[i].strip() and (len(lines[i]) - len(lines[i].lstrip())) == indent_n for i in range(ln - 2, -1, -1))
				if earlier_same:
					for i in range(ln - 2, -1, -1):
						if lines[i].strip():
							if (len(lines[i]) - len(lines[i].lstrip())) < indent_n and not lines[i].rstrip().endswith(':'):
								target = i
							break
			if not lines[target].strip():
				target = ln - 1
			if not lines[target].strip():
				break
			lines[target] = ''
		except Exception:
			return None
	if tree is None:
		return None
	_ck()
	builder = _PythonScopeBuilder()
	builder.scopes[0]['end'] = len(lines)
	try:
		builder.visit(tree)
	except Exception:
		return None
	if seed_names:
		for _sn, _sk in seed_names.items():
			builder.scopes[0]['names'].setdefault(_sn, []).append((0, _sk))
	if seed_aliases:
		for _sa, _sm in seed_aliases.items():
			builder.module_aliases.setdefault(_sa, _sm)
			builder.module_alias_defs.setdefault(_sa, []).append((0, _sm))
	if seed_names:
		for _sn, _sk in seed_names.items():
			if _sk == 'module':
				builder.module_aliases.setdefault(_sn, _sn)
				builder.module_alias_defs.setdefault(_sn, []).append((0, _sn))
	if seed_func_params:
		for _sfp_n, _sfp_v in seed_func_params.items():
			builder.func_params.setdefault(_sfp_n, []).insert(0, (0, set(_sfp_v), 0))
	if seed_func_accepts_any:
		for _sfa_n, _sfa_v in seed_func_accepts_any.items():
			builder.func_accepts_any.setdefault(_sfa_n, []).insert(0, (0, _sfa_v, 0))
	_ck()
	line_to_scope = [None] * (len(lines) + 2)
	for ln in range(1, len(lines) + 1):
		if ln % 500 == 0:
			_ck()
		best_idx = None
		for idx, sc in enumerate(builder.scopes):
			if sc['start'] <= ln <= sc['end']:
				if best_idx is None or sc['start'] >= builder.scopes[best_idx]['start']:
					best_idx = idx
		line_to_scope[ln] = best_idx
	def _scope_for_line(ln):
		if 0 <= ln < len(line_to_scope):
			return line_to_scope[ln]
		return None
	def _scope_for_pos(ln, col):
		winner = None
		winner_start = None
		for idx, sc in enumerate(builder.scopes):
			if sc['start'] <= ln <= sc['end']:
				if sc['start'] == ln and col < sc.get('start_col', 0):
					continue
				_ec = sc.get('end_col')
				if sc['end'] == ln and _ec is not None and col >= _ec:
					continue
				if winner is None or sc['start'] >= winner_start:
					winner = idx
					winner_start = sc['start']
		return winner
	def _def_scope_chain(lineno):
		chain = []
		_si = _scope_for_line(lineno)
		_inner = _si
		while _si is not None:
			_sc = builder.scopes[_si]
			if _sc.get('kind') != 'class' or _si == _inner:
				chain.append(_si)
			_si = _sc['parent']
		if 0 not in chain:
			chain.append(0)
		return chain
	def _rebind_def_scopes(store):
		for _rn, _rdefs in store.items():
			for _ri, _rd in enumerate(_rdefs):
				if len(_rd) > 2:
					_rdefs[_ri] = (_rd[0], _rd[1], _binding_scope_for(_rn, _rd[2]))
	def _binding_scope_of_def(lineno):
		_si = _scope_for_line(lineno)
		if _si is None:
			return 0
		_par = builder.scopes[_si]['parent']
		return _par if _par is not None else 0
	def _binding_scope_for(name, sc_idx):
		if sc_idx is None:
			return sc_idx
		sc = builder.scopes[sc_idx]
		if name in sc.get('globals', {}):
			return 0
		if name in sc.get('nonlocals', {}):
			_p = sc['parent']
			while _p is not None:
				_ps = builder.scopes[_p]
				if _ps.get('kind') == 'function' and name in _ps['names'] and name not in _ps.get('globals', {}) and name not in _ps.get('nonlocals', {}):
					return _p
				_p = _ps['parent']
			return sc_idx
		return sc_idx
	_rebind_def_scopes(builder.func_params)
	_rebind_def_scopes(builder.func_accepts_any)
	_ck()
	def _call_name_kind(name, lineno):
		sidx = _scope_for_line(lineno)
		inner = sidx
		while sidx is not None:
			sc = builder.scopes[sidx]
			if sc.get('kind') == 'class' and sidx != inner:
				sidx = sc['parent']
				continue
			if name in sc['names']:
				best = None
				latest = None
				for dl, kind in sc['names'][name]:
					if latest is None or dl > latest[0]:
						latest = (dl, kind)
					if sidx == inner and dl > lineno:
						continue
					if best is None or dl > best[0]:
						best = (dl, kind)
				if best is None and latest is not None and name in _PYTHON_BUILTIN_NAMES:
					return None
				if best is None and latest is not None and _same_block(latest[0], lineno):
					best = latest
				return best[1] if best is not None else '_local'
			sidx = sc['parent']
		return None
	module_contents = {}
	local_classes = {}
	class_module_origin = {_so: [(0, _sv)] for _so, _sv in seed_origins.items()} if seed_origins else {}
	def _line_def_at(defs, lineno):
		if not defs:
			return None
		_best = None
		for _dl, _dv in defs:
			if _dl <= lineno and (_best is None or _dl >= _best[0]):
				_best = (_dl, _dv)
		if _best is None:
			for _dl, _dv in defs:
				if _same_block(_dl, lineno) and (_best is None or _dl > _best[0]):
					_best = (_dl, _dv)
		return _best[1] if _best is not None else None
	def _class_origin_at(name, lineno):
		return _line_def_at(class_module_origin.get(name), lineno)
	dynamic_class_attrs = {}
	dynamic_class_attr_types = {}
	dynamic_module_attrs = {}
	dynamic_module_attr_types = {}
	dynamic_modclass_attrs = {}
	dynamic_modclass_attr_types = {}
	tree_class_defs = []
	tree_func_defs = []
	tree_assigns = []
	tree_attributes = []
	tree_imports = []
	tree_importfroms = []
	name_positions = []
	global_stmt_positions = []
	def _skip_ws(enc, i):
		while i < len(enc) and enc[i:i + 1] in (b' ', b'\t'):
			i += 1
		return i
	_tw = 0
	for _tn in ast.walk(tree):
		_tw += 1
		if _tw % 2000 == 0:
			_ck()
		if isinstance(_tn, ast.Name):
			name_positions.append((_tn.lineno, _tn.col_offset, _tn.id, isinstance(_tn.ctx, ast.Store)))
		elif isinstance(_tn, ast.arg):
			name_positions.append((_tn.lineno, _tn.col_offset, _tn.arg, True))
		elif isinstance(_tn, ast.Attribute):
			tree_attributes.append(_tn)
		elif isinstance(_tn, ast.Assign):
			tree_assigns.append(_tn)
		elif isinstance(_tn, ast.NamedExpr) and isinstance(_tn.target, ast.Name):
			_tn.targets = [_tn.target]
			tree_assigns.append(_tn)
		elif isinstance(_tn, ast.AnnAssign) and _tn.value is not None and isinstance(_tn.target, ast.Name):
			_tn.targets = [_tn.target]
			tree_assigns.append(_tn)
		elif isinstance(_tn, ast.ClassDef):
			tree_class_defs.append(_tn)
		elif isinstance(_tn, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
			tree_func_defs.append(_tn)
		elif isinstance(_tn, ast.alias):
			if _tn.asname:
				name_positions.append((_tn.end_lineno, _tn.end_col_offset - len(_tn.asname.encode('utf-8')), _tn.asname, True))
			elif _tn.name != '*' and '.' not in _tn.name:
				name_positions.append((_tn.lineno, _tn.col_offset, _tn.name, True))
		elif isinstance(_tn, ast.Import):
			tree_imports.append(_tn)
		elif isinstance(_tn, ast.ImportFrom):
			tree_importfroms.append(_tn)
		elif isinstance(_tn, ast.ExceptHandler):
			if _tn.name and _tn.type is not None and 0 < _tn.type.end_lineno <= len(lines):
				_enc = lines[_tn.type.end_lineno - 1].encode('utf-8')
				_i = _skip_ws(_enc, _tn.type.end_col_offset)
				if _enc[_i:_i + 2] == b'as':
					_i = _skip_ws(_enc, _i + 2)
					_nb = _tn.name.encode('utf-8')
					if _enc[_i:_i + len(_nb)] == _nb:
						name_positions.append((_tn.type.end_lineno, _i, _tn.name, True))
		elif isinstance(_tn, (ast.Global, ast.Nonlocal)):
			if 0 < _tn.lineno <= len(lines):
				_enc = lines[_tn.lineno - 1].encode('utf-8')
				_i = _tn.col_offset + (6 if isinstance(_tn, ast.Global) else 8)
				for _gname in _tn.names:
					while _i < len(_enc) and _enc[_i:_i + 1] in (b' ', b'\t', b','):
						_i += 1
					_nb = _gname.encode('utf-8')
					if _enc[_i:_i + len(_nb)] != _nb:
						break
					name_positions.append((_tn.lineno, _i, _gname, False))
					global_stmt_positions.append((_tn.lineno, _i, _gname, _scope_for_line(_tn.lineno)))
					_i += len(_nb)
	def_name_positions = []
	for _tn in tree_class_defs + tree_func_defs:
		if isinstance(_tn, ast.Lambda) or not (0 < _tn.lineno <= len(lines)):
			continue
		_enc = lines[_tn.lineno - 1].encode('utf-8')
		_i = _tn.col_offset
		if isinstance(_tn, ast.ClassDef):
			_i += 5
		else:
			if _enc[_i:_i + 5] == b'async':
				_i = _skip_ws(_enc, _i + 5)
			_i += 3
		_i = _skip_ws(_enc, _i)
		_nb = _tn.name.encode('utf-8')
		if _enc[_i:_i + len(_nb)] == _nb:
			def_name_positions.append((_tn.lineno, _i, _tn.name, 'class' if isinstance(_tn, ast.ClassDef) else 'func'))
	_class_def_by_name = {}
	for _tn in tree_class_defs:
		if _tn.name not in _class_def_by_name:
			_class_def_by_name[_tn.name] = _tn
	def _flatten_class_body(body, depth = 0):
		out = []
		if depth > 60:
			return out
		for _s in body:
			if isinstance(_s, (ast.Assign, ast.AnnAssign)):
				out.append(_s)
			elif isinstance(_s, (ast.For, ast.AsyncFor, ast.While)):
				out.extend(_flatten_class_body(_s.body, depth + 1))
				out.extend(_flatten_class_body(_s.orelse, depth + 1))
			elif isinstance(_s, ast.If):
				out.extend(_flatten_class_body(_s.body, depth + 1))
				out.extend(_flatten_class_body(_s.orelse, depth + 1))
			elif isinstance(_s, (ast.With, ast.AsyncWith)):
				out.extend(_flatten_class_body(_s.body, depth + 1))
			elif isinstance(_s, ast.Try):
				out.extend(_flatten_class_body(_s.body, depth + 1))
				for _h in _s.handlers:
					out.extend(_flatten_class_body(_h.body, depth + 1))
				out.extend(_flatten_class_body(_s.orelse, depth + 1))
				out.extend(_flatten_class_body(_s.finalbody, depth + 1))
		return out
	def _compute_class_members(node):
		members = _python_inspect_ast_members(node.body)
		for _bstmt in _flatten_class_body(node.body):
			_btgts = _bstmt.targets if isinstance(_bstmt, ast.Assign) else ([_bstmt.target] if isinstance(_bstmt, ast.AnnAssign) else [])
			_bval = _bstmt.value if isinstance(_bstmt, (ast.Assign, ast.AnnAssign)) else None
			if isinstance(_bval, ast.NamedExpr):
				_bval = _bval.value
			_bval = _python_unwrap_descriptor(_bval)
			if not isinstance(_bval, ast.Name):
				continue
			for _btgt in _btgts:
				if isinstance(_btgt, ast.Name) and members.get(_btgt.id) in ('var', None):
					_rk = _call_name_kind(_bval.id, _bstmt.lineno)
					if _rk in ('func', 'class', 'module'):
						members[_btgt.id] = _rk
		for meth in node.body:
			if isinstance(meth, (ast.FunctionDef, ast.AsyncFunctionDef)):
				_fp = meth.args.args[0].arg if (meth.args.args and _python_method_has_implicit_first_param(meth)) else None
				for stmt in ast.walk(meth):
					tgts = stmt.targets if isinstance(stmt, ast.Assign) else ([stmt.target] if isinstance(stmt, (ast.AnnAssign, ast.AugAssign)) else [])
					for tgt, _tval in _assign_pairs(tgts, stmt.value if isinstance(stmt, (ast.Assign, ast.AnnAssign)) else None):
						if _fp and isinstance(tgt, ast.Attribute) and isinstance(tgt.value, ast.Name) and tgt.value.id == _fp:
							_mvk = 'var'
							if isinstance(_tval, ast.Lambda):
								_mvk = 'func'
							elif isinstance(_tval, ast.Attribute) and isinstance(_tval.value, ast.Name) and _tval.value.id == _fp:
								_svk = members.get(_tval.attr)
								if _svk in ('func', 'class', 'module'):
									_mvk = _svk
							elif isinstance(_tval, ast.Name):
								_nvk = _call_name_kind(_tval.id, stmt.lineno)
								if _nvk in ('func', 'class', 'module'):
									_mvk = _nvk
							if _mvk == 'var' and members.get(tgt.attr) in ('func', 'class', 'module'):
								members[tgt.attr] = 'var'
							else:
								members.setdefault(tgt.attr, _mvk)
		return members
	class_def_lines = {}
	class_def_scopes = {}
	local_class_defs = {}
	_class_nested_lines = set()
	for _tn in tree_class_defs:
		for _tsub in _tn.body:
			if isinstance(_tsub, ast.ClassDef):
				_class_nested_lines.add((_tsub.name, _tsub.lineno))
	for _tn in tree_class_defs:
		if (_tn.name, _tn.lineno) in _class_nested_lines:
			continue
		class_def_lines.setdefault(_tn.name, []).append(_tn.lineno)
		class_def_scopes[(_tn.name, _tn.lineno)] = _binding_scope_for(_tn.name, _binding_scope_of_def(_tn.lineno))
	def _class_def_line_at(name, lineno):
		_lns = class_def_lines.get(name)
		if not _lns:
			return None
		for _sidx in _def_scope_chain(lineno):
			_cands = [_cl for _cl in _lns if class_def_scopes.get((name, _cl), 0) == _sidx]
			if not _cands:
				continue
			_best = None
			for _cl in _cands:
				if _cl <= lineno and (_best is None or _cl > _best):
					_best = _cl
			return _best if _best is not None else max(_cands)
		_best = None
		for _cl in _lns:
			if _cl <= lineno and (_best is None or _cl > _best):
				_best = _cl
		if _best is None:
			_best = max(_lns)
		return _best
	for scope in builder.scopes:
		for name, defs in scope['names'].items():
			for _, kind in defs:
				if kind == 'class' and name in _class_def_by_name and name not in local_classes:
					try:
						node = _class_def_by_name[name]
						local_classes[name] = _compute_class_members(node)
					except Exception:
						pass
	_class_first_line = {}
	for _tn in tree_class_defs:
		if _tn.name not in _class_first_line:
			_class_first_line[_tn.name] = _tn.lineno
	def _class_key_at(name, lineno):
		_dl = _class_def_line_at(name, lineno)
		if _dl is None or _dl == _class_first_line.get(name):
			return name
		return name + '\x00' + str(_dl)
	for _tn in tree_class_defs:
		if _tn.name in local_classes and _tn.lineno != _class_first_line.get(_tn.name):
			_rk = _tn.name + '\x00' + str(_tn.lineno)
			if _rk not in local_classes:
				try:
					local_classes[_rk] = _compute_class_members(_tn)
				except Exception:
					local_classes[_rk] = {}
	if seed_classes:
		for _scn, _scm in seed_classes.items():
			local_classes.setdefault(_scn, dict(_scm))
	_ck()
	def _node_class_key(node):
		if node.name in local_classes and node.lineno != _class_first_line.get(node.name):
			return node.name + '\x00' + str(node.lineno)
		return node.name
	class_bases = {}
	module_scope_class_keys = set()
	_nonmodule_scope_class_keys = set()
	_class_body_members = {}
	_self_assigned_attrs = {}
	if seed_instance_only:
		for _sio_c, _sio_v in seed_instance_only.items():
			_self_assigned_attrs.setdefault(_sio_c, set()).update(_sio_v)
	_module_class_bases = []
	for node in tree_class_defs:
		if node.name in local_classes:
			bases = []
			for base in node.bases:
				if isinstance(base, ast.Name):
					bases.append(_class_key_at(base.id, node.lineno))
				elif isinstance(base, ast.Attribute):
					bases.append(base.attr)
					_module_class_bases.append((_node_class_key(node), base))
			class_bases[_node_class_key(node)] = bases
			_class_body_members[_node_class_key(node)] = set(_bm for _bm in _python_inspect_ast_members(node.body) if '.' not in _bm)
			if _binding_scope_for(node.name, _binding_scope_of_def(node.lineno)) == 0:
				module_scope_class_keys.add(_node_class_key(node))
			else:
				_nonmodule_scope_class_keys.add(_node_class_key(node))
	if seed_class_bases:
		for _scb_c, _scb_b in seed_class_bases.items():
			module_scope_class_keys.add(_scb_c)
			if _scb_c not in class_bases:
				class_bases[_scb_c] = list(_scb_b)
	if seed_classes:
		module_scope_class_keys.update(seed_classes)
	module_scope_class_keys -= _nonmodule_scope_class_keys
	def _instance_only_attr(clskey, attr):
		for _ioc in _python_c3_linearize(clskey, class_bases, frozenset()):
			if attr in _class_body_members.get(_ioc, ()):
				return False
			if attr in _self_assigned_attrs.get(_ioc, ()):
				return True
		return False
	local_class_method_params = {}
	local_class_accepts_any = set()
	_class_attr_lambda_params = {}
	for node in tree_class_defs:
		if node.name in local_classes:
			_nk = _node_class_key(node)
			for sub in node.body:
				if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)):
					_mimp = _python_method_has_implicit_first_param(sub)
					_margs = list(sub.args.posonlyargs) + list(sub.args.args) + list(sub.args.kwonlyargs)
					_mp = (set(a.arg for a in (_margs[1:] if _mimp else _margs)) - set(a.arg for a in sub.args.posonlyargs)) | set(a.arg for a in sub.args.kwonlyargs)
					if sub.args.kwarg:
						local_class_accepts_any.add(_nk + '.' + sub.name)
					local_class_method_params[_nk + '.' + sub.name] = _mp
					_sfp = sub.args.args[0].arg if (sub.args.args and _mimp) else None
					if _sfp:
						for _astmt in ast.walk(sub):
							if not isinstance(_astmt, ast.Assign):
								continue
							for _atg in _astmt.targets:
								if isinstance(_atg, ast.Attribute) and isinstance(_atg.value, ast.Name) and _atg.value.id == _sfp:
									_av = _astmt.value
									if isinstance(_av, ast.Lambda):
										_lp = set(a.arg for a in list(_av.args.args) + list(_av.args.kwonlyargs))
										local_class_method_params[_nk + '.' + _atg.attr] = _lp
										if _av.args.kwarg:
											local_class_accepts_any.add(_nk + '.' + _atg.attr)
									elif isinstance(_av, ast.Attribute) and isinstance(_av.value, ast.Name) and _av.value.id == _sfp:
										_class_attr_lambda_params.setdefault(_nk, []).append((_atg.attr, _av.attr))
				for _clstmt in _flatten_class_body(node.body):
					_clval = _clstmt.value if isinstance(_clstmt, (ast.Assign, ast.AnnAssign)) else None
					if isinstance(_clval, ast.NamedExpr):
						_clval = _clval.value
					_clval = _python_unwrap_descriptor(_clval)
					if not isinstance(_clval, ast.Lambda):
						continue
					_cltgts = _clstmt.targets if isinstance(_clstmt, ast.Assign) else [_clstmt.target]
					_clargs = list(_clval.args.posonlyargs) + list(_clval.args.args) + list(_clval.args.kwonlyargs)
					_clp = (set(a.arg for a in (_clargs[1:] if _clargs else _clargs)) - set(a.arg for a in _clval.args.posonlyargs)) | set(a.arg for a in _clval.args.kwonlyargs)
					for _cltgt in _cltgts:
						if not isinstance(_cltgt, ast.Name):
							continue
						local_class_method_params[_nk + '.' + _cltgt.id] = _clp
						if _clval.args.kwarg:
							local_class_accepts_any.add(_nk + '.' + _cltgt.id)
				for _cmstmt in _flatten_class_body(node.body):
					_cmval = _cmstmt.value if isinstance(_cmstmt, (ast.Assign, ast.AnnAssign)) else None
					if isinstance(_cmval, ast.NamedExpr):
						_cmval = _cmval.value
					_cmval = _python_unwrap_descriptor(_cmval)
					if not isinstance(_cmval, ast.Name):
						continue
					_cmsrc = _nk + '.' + _cmval.id
					if _cmsrc not in local_class_method_params:
						continue
					_cmtgts = _cmstmt.targets if isinstance(_cmstmt, ast.Assign) else [_cmstmt.target]
					for _cmtgt in _cmtgts:
						if not isinstance(_cmtgt, ast.Name):
							continue
						local_class_method_params[_nk + '.' + _cmtgt.id] = local_class_method_params[_cmsrc]
						if _cmsrc in local_class_accepts_any:
							local_class_accepts_any.add(_nk + '.' + _cmtgt.id)
				for _cmstmt in _flatten_class_body(node.body):
					_cmval = _cmstmt.value if isinstance(_cmstmt, (ast.Assign, ast.AnnAssign)) else None
					if isinstance(_cmval, ast.NamedExpr):
						_cmval = _cmval.value
					_cmval = _python_unwrap_descriptor(_cmval)
					if not (isinstance(_cmval, ast.Attribute) and isinstance(_cmval.value, ast.Name)):
						continue
					_cmbase = _class_key_at(_cmval.value.id, _cmstmt.lineno)
					_cmsrc = _cmbase + '.' + _cmval.attr
					if _cmbase not in local_classes or _cmsrc not in local_class_method_params:
						continue
					_cmtgts = _cmstmt.targets if isinstance(_cmstmt, ast.Assign) else [_cmstmt.target]
					for _cmtgt in _cmtgts:
						if not isinstance(_cmtgt, ast.Name):
							continue
						local_class_method_params[_nk + '.' + _cmtgt.id] = local_class_method_params[_cmsrc]
						local_classes[_nk][_cmtgt.id] = 'func'
						if _cmsrc in local_class_accepts_any:
							local_class_accepts_any.add(_nk + '.' + _cmtgt.id)
	if seed_method_params:
		for _smk, _smv in seed_method_params.items():
			local_class_method_params.setdefault(_smk, _smv)
	if seed_accepts_any:
		local_class_accepts_any.update(seed_accepts_any)
	class_attr_types = {}
	if seed_class_attr_types:
		for _scat_c, _scat_m in seed_class_attr_types.items():
			class_attr_types.setdefault(_scat_c, {}).update(_scat_m)
	var_attr_types = {}
	def _var_attr_type_at(sc_idx, name, attr, lineno):
		sidx = sc_idx
		inner = sidx
		while sidx is not None:
			sc = builder.scopes[sidx]
			if sc.get('kind') == 'class' and sidx != inner:
				sidx = sc['parent']
				continue
			if name in sc['names']:
				_vat = var_attr_types.get((sidx, name), {}).get(attr)
				if _vat:
					best = None
					for dl, tp in _vat:
						if sidx == inner and dl > lineno:
							continue
						if best is None or dl > best[0]:
							best = (dl, tp)
					if best is not None:
						return True, best[1]
				return False, None
			sidx = sc['parent']
		return False, None
	for _ncnode in tree_class_defs:
		if _ncnode.name not in local_classes:
			continue
		_nckey = _node_class_key(_ncnode)
		for _ncsub in _ncnode.body:
			if isinstance(_ncsub, ast.ClassDef) and _ncsub.name in local_classes:
				class_attr_types.setdefault(_nckey, {})[_ncsub.name] = ('class', _node_class_key(_ncsub))
	_inherited_members = set()
	_inherited_attr_types = set()
	_inherited_method_params = set()
	_direct_attr_assigns = set()
	if seed_inherited:
		_inherited_members.update(seed_inherited.get('members', ()))
		_inherited_attr_types.update(seed_inherited.get('attr_types', ()))
		_inherited_method_params.update(seed_inherited.get('method_params', ()))
	def _python_merge_class_bases():
		for cls in list(class_bases):
			if cls not in local_classes:
				continue
			_filled = set()
			_filled_attrs = set()
			_filled_params = set()
			for base in _python_c3_linearize(cls, class_bases, frozenset())[1:]:
				if base not in local_classes:
					continue
				for k, v in local_classes[base].items():
					if (base, k) in _inherited_members or k in _filled:
						continue
					if k not in local_classes[cls] or (local_classes[cls][k] == 'var' and v != 'var'):
						local_classes[cls][k] = v
						_inherited_members.add((cls, k))
						_filled.add(k)
				for _ak, _av in class_attr_types.get(base, {}).items():
					if (base, _ak) in _inherited_attr_types or _ak in _filled_attrs:
						continue
					if _ak in _self_assigned_attrs.get(cls, ()) or (cls, _ak) in _direct_attr_assigns:
						continue
					if _ak not in class_attr_types.setdefault(cls, {}):
						class_attr_types[cls][_ak] = _av
						_inherited_attr_types.add((cls, _ak))
						_filled_attrs.add(_ak)
				for _mk in list(local_class_method_params):
					if not _mk.startswith(base + '.') or _mk in _inherited_method_params:
						continue
					_meth = _mk[len(base) + 1:]
					if _meth in _filled_params:
						continue
					_ck2 = cls + '.' + _meth
					if _ck2 not in local_class_method_params:
						local_class_method_params[_ck2] = local_class_method_params[_mk]
						if _mk in local_class_accepts_any:
							local_class_accepts_any.add(_ck2)
						_inherited_method_params.add(_ck2)
						_filled_params.add(_meth)
	_python_merge_class_bases()
	for _calp_nk, _calp_pairs in _class_attr_lambda_params.items():
		for _attr_name, _src_meth in _calp_pairs:
			_src_key = _calp_nk + '.' + _src_meth
			if _src_key in local_class_method_params and _calp_nk + '.' + _attr_name not in local_class_method_params:
				local_class_method_params[_calp_nk + '.' + _attr_name] = local_class_method_params[_src_key]
				if _src_key in local_class_accepts_any:
					local_class_accepts_any.add(_calp_nk + '.' + _attr_name)
	_ck()
	for _bname, _bmembers in _PYTHON_BUILTIN_MEMBERS.items():
		local_classes.setdefault(_bname, dict(_bmembers))
	def _name_is_class_at(name, lineno):
		if name not in local_classes:
			return False
		_k = _call_name_kind(name, lineno)
		return _k == 'class' or _k is None
	class_type_maps = {}
	if seed_attr_types:
		for _sat_c, _sat_m in seed_attr_types.items():
			class_type_maps.setdefault(_sat_c, {}).update(_sat_m)
	for node in tree_class_defs:
		if node.name in local_classes:
			class_type_maps[_node_class_key(node)] = {}
	_ck()
	candidate_modules = set()
	for _, imported_name, top_name, _, _ in builder.import_names:
		candidate_modules.add(top_name)
		candidate_modules.add(imported_name)
	for _, top_name in builder.module_literals:
		candidate_modules.add(top_name)
	for _, module_name, imported_name, _orig_name, _ in builder.from_imports:
		if module_name:
			candidate_modules.add(module_name.split('.')[0])
			candidate_modules.add(module_name)
			candidate_modules.add(f'{module_name}.{_orig_name}')
	for _adefs in builder.module_alias_defs.values():
		for _, _sm in _adefs:
			candidate_modules.add(_sm)
	for _sm in builder.module_aliases.values():
		candidate_modules.add(_sm)
	valid_modules = set()
	imported_modules = set()
	for name in candidate_modules:
		spec = _python_find_spec_cached(buf, name)
		if spec is not None:
			valid_modules.add(name)
			imported_modules.add(name)
			members = _python_resolve_module_members(buf, name)
			if members:
				module_contents[name] = members
	_dotted_module_targets = {}
	for name in candidate_modules:
		if name in valid_modules or '.' not in name:
			continue
		_dmt = _python_resolve_dotted_module(buf, name)
		if _dmt is None:
			continue
		_dotted_module_targets[name] = _dmt
		if _dmt not in valid_modules:
			valid_modules.add(_dmt)
			imported_modules.add(_dmt)
			_dmems = _python_resolve_module_members(buf, _dmt)
			if _dmems:
				module_contents[_dmt] = _dmems
	def _real_module_name(name):
		return _dotted_module_targets.get(name, name)
	_ck()
	for scope_idx, imported_name, top_name, used_name, lineno in builder.import_names:
		if used_name == top_name:
			if top_name in valid_modules:
				builder.scopes[scope_idx]['names'].setdefault(used_name, []).append((lineno, 'module'))
		elif imported_name in valid_modules or imported_name in _dotted_module_targets:
			builder.scopes[scope_idx]['names'].setdefault(used_name, []).append((lineno, 'module'))
	for _gsn in builder.global_seed_names:
		if not builder.scopes[0]['names'].get(_gsn):
			builder.scopes[0]['names'].setdefault(_gsn, []).append((1, 'var'))
	for _nlp, _nln in builder.nonlocal_seeds:
		_nlbound = False
		_nlcur = _nlp
		while _nlcur is not None:
			if builder.scopes[_nlcur].get('kind') == 'function' and builder.scopes[_nlcur]['names'].get(_nln):
				_nlbound = True
				break
			_nlcur = builder.scopes[_nlcur]['parent']
		if not _nlbound:
			builder.scopes[_nlp]['names'].setdefault(_nln, []).append((builder.scopes[_nlp]['start'], 'var'))
	for scope_idx, module_name, imported_name, _orig_name, lineno in builder.from_imports:
		module_name = _real_module_name(module_name)
		if not module_name or module_name not in valid_modules:
			continue
		contents = module_contents.get(module_name, {})
		if imported_name == '*':
			for _wname, _wkind in contents.items():
				if '.' not in _wname:
					builder.scopes[scope_idx]['names'].setdefault(_wname, []).append((lineno, _wkind))
		else:
			if _orig_name in contents:
				kind = contents[_orig_name]
				if kind == 'module':
					_fmtgt = contents.get('@modtarget:' + _orig_name)
					if _fmtgt is None:
						_fmtgt = f'{module_name}.{_orig_name}'
					if _fmtgt not in valid_modules and _python_find_spec_cached(buf, _fmtgt) is not None:
						valid_modules.add(_fmtgt)
						_fmmems = _python_resolve_module_members(buf, _fmtgt)
						if _fmmems:
							module_contents[_fmtgt] = _fmmems
					builder.module_alias_defs.setdefault(imported_name, []).append((lineno, _fmtgt))
					if lineno >= builder.module_alias_lines.get(imported_name, 0):
						builder.module_aliases[imported_name] = _fmtgt
						builder.module_alias_lines[imported_name] = lineno
			elif f'{module_name}.{_orig_name}' in valid_modules or _python_find_spec_cached(buf, f'{module_name}.{_orig_name}') is not None:
				kind = 'module'
				builder.module_alias_defs.setdefault(imported_name, []).append((lineno, f'{module_name}.{_orig_name}'))
				if lineno >= builder.module_alias_lines.get(imported_name, 0):
					builder.module_aliases[imported_name] = f'{module_name}.{_orig_name}'
					builder.module_alias_lines[imported_name] = lineno
			else:
				continue
			builder.scopes[scope_idx]['names'].setdefault(imported_name, []).append((lineno, kind))
	for _, module_name, imported_name, _orig_name, _fln0 in builder.from_imports:
		module_name = _real_module_name(module_name)
		if not module_name:
			continue
		mc = module_contents.get(module_name, {})
		if imported_name == '*':
			for _wname, _wkind in mc.items():
				if '.' not in _wname and _wkind == 'class':
					if _wname not in local_classes:
						_wmems = _python_resolve_module_class_members(buf, module_name, _wname)
						if _wmems:
							local_classes[_wname] = _wmems
					if _wname in local_classes:
						class_module_origin.setdefault(_wname, []).append((_fln0, (module_name, _wname)))
		elif mc.get(_orig_name) == 'class':
			if imported_name not in local_classes:
				_imp_mems = _python_resolve_module_class_members(buf, module_name, _orig_name)
				if _imp_mems:
					local_classes[imported_name] = _imp_mems
			if imported_name in local_classes:
				class_module_origin.setdefault(imported_name, []).append((_fln0, (module_name, _orig_name)))
	base_to_module = {}
	for _, imported_name, top_name, used_name, _iln in builder.import_names:
		if used_name == top_name:
			if top_name in valid_modules:
				base_to_module.setdefault(used_name, []).append((_iln, top_name))
		elif imported_name in valid_modules or imported_name in _dotted_module_targets:
			base_to_module.setdefault(used_name, []).append((_iln, _real_module_name(imported_name)))
		elif top_name in valid_modules:
			base_to_module.setdefault(used_name, []).append((_iln, top_name))
	for _alias, _adefs in builder.module_alias_defs.items():
		for _al, _afull in _adefs:
			if _afull in valid_modules or _afull in _dotted_module_targets:
				base_to_module.setdefault(_alias, []).append((_al, _real_module_name(_afull)))
	def _base_module_at(name, lineno):
		return _line_def_at(base_to_module.get(name), lineno)
	for _dsc, _dln, _dname, _dmod, _dbuiltin in builder.dynamic_imports:
		if _dbuiltin and _call_name_kind('__import__', _dln) is not None:
			continue
		if _python_find_spec_cached(buf, _dmod) is not None:
			valid_modules.add(_dmod)
			base_to_module.setdefault(_dname, []).append((_dln, _dmod))
			if _dln >= builder.module_alias_lines.get(_dname, 0):
				builder.module_aliases[_dname] = _dmod
				builder.module_alias_lines[_dname] = _dln
			if _dmod not in module_contents:
				_dmems = _python_resolve_module_members(buf, _dmod)
				if _dmems:
					module_contents[_dmod] = _dmems
					imported_modules.add(_dmod)
			_dnames = builder.scopes[_dsc]['names'].setdefault(_dname, [])
			_dnames[:] = [(_l, _k) for _l, _k in _dnames if not (_l == _dln and _k == 'var')]
			_dnames.append((_dln, 'module'))
	def _resolve_name_kind_scope(scope_idx, name, lineno):
		sidx = scope_idx
		inner = sidx
		while sidx is not None:
			sc = builder.scopes[sidx]
			if sc.get('kind') == 'class' and sidx != inner:
				sidx = sc['parent']
				continue
			if name in sc['names']:
				best = None
				latest = None
				for _dl, _k in sc['names'][name]:
					if latest is None or _dl > latest[0]:
						latest = (_dl, _k)
					if sidx == inner and _dl > lineno:
						continue
					if best is None or _dl > best[0]:
						best = (_dl, _k)
				if best is None and latest is not None and name in _PYTHON_BUILTIN_NAMES:
					return None
				if best is None and latest is not None and _same_block(latest[0], lineno):
					best = latest
				return best[1] if best is not None else None
			sidx = sc['parent']
		return None
	def _pick_scoped_def(defs, lineno, default):
		for _sidx in _def_scope_chain(lineno):
			best = None
			latest = None
			for _d in defs:
				if (_d[2] if len(_d) > 2 else 0) != _sidx:
					continue
				if latest is None or _d[0] > latest[0]:
					latest = _d
				if _d[0] > lineno:
					continue
				if best is None or _d[0] > best[0]:
					best = _d
			if best is None and latest is not None and _same_block(latest[0], lineno):
				best = latest
			if best is not None:
				return best[1]
		return default
	def _func_params_at(name, lineno):
		defs = builder.func_params.get(name)
		if not defs:
			return None
		return _pick_scoped_def(defs, lineno, None)
	def _func_accepts_any_at(name, lineno):
		defs = builder.func_accepts_any.get(name)
		if not defs:
			return False
		return _pick_scoped_def(defs, lineno, False)
	for _asc, _aln, _aname, _asrc in builder.alias_assigns:
		_srckind = _resolve_name_kind_scope(_asc, _asrc, _aln)
		if _srckind is None and _asrc in _PYTHON_BUILTIN_MEMBERS:
			_srckind = 'builtin'
		elif _srckind is None and _asrc in _PYTHON_BUILTIN_NAMES:
			_srckind = 'builtin'
			if _asrc in _PYTHON_BUILTIN_CALLABLE_PARAMS:
				builder.func_params.setdefault(_aname, []).append((_aln, _PYTHON_BUILTIN_CALLABLE_PARAMS[_asrc], _binding_scope_for(_aname, _asc)))
		if _srckind == 'module':
			_asrc_mod = _base_module_at(_asrc, _aln)
			if _asrc_mod is not None:
				_absc = _binding_scope_for(_aname, _asc)
				_anames = builder.scopes[_absc]['names'].setdefault(_aname, [])
				_anames[:] = [(_l, _k) for _l, _k in _anames if not (_l == _aln and _k == 'var')]
				_anames.append((_aln, 'module'))
				base_to_module.setdefault(_aname, []).append((_aln, _asrc_mod))
				builder.module_alias_defs.setdefault(_aname, []).append((_aln, _asrc_mod))
		if _srckind in ('class', 'func', 'builtin'):
			_absc = _binding_scope_for(_aname, _asc)
			_anames = builder.scopes[_absc]['names'].setdefault(_aname, [])
			_anames[:] = [(_l, _k) for _l, _k in _anames if not (_l == _aln and _k == 'var')]
			_anames.append((_aln, _srckind))
			if _srckind in ('func', 'builtin'):
				_src_params = _func_params_at(_asrc, _aln)
				if _src_params is not None:
					builder.func_params.setdefault(_aname, []).append((_aln, _src_params, _absc))
					builder.func_accepts_any.setdefault(_aname, []).append((_aln, _func_accepts_any_at(_asrc, _aln), _absc))
			if _srckind in ('class', 'builtin'):
				_asrc_key = _class_key_at(_asrc, _aln)
				if _asrc_key in local_classes:
					class_def_lines.setdefault(_aname, [])
					if _aln not in class_def_lines[_aname]:
						class_def_lines[_aname].append(_aln)
					class_def_scopes[(_aname, _aln)] = _absc
					_class_first_line.setdefault(_aname, _aln)
					_adst_key = _class_key_at(_aname, _aln)
					if _adst_key not in local_classes:
						local_classes[_adst_key] = local_classes[_asrc_key]
					class_type_maps[_adst_key] = class_type_maps.setdefault(_asrc_key, {})
					_sorig = _class_origin_at(_asrc, _aln)
					if _sorig is not None:
						class_module_origin.setdefault(_aname, []).append((_aln, _sorig))
					for _mk in list(local_class_method_params):
						if _mk.startswith(_asrc_key + '.'):
							_ameth = _mk[len(_asrc_key) + 1:]
							local_class_method_params[_adst_key + '.' + _ameth] = local_class_method_params[_mk]
							if _mk in local_class_accepts_any:
								local_class_accepts_any.add(_adst_key + '.' + _ameth)
	name_module_class = {}
	_attr_alias_func_origins = []
	def _dotted_chain_parts(node):
		attrs = []
		cur = node
		while isinstance(cur, ast.Attribute):
			attrs.append(cur.attr)
			cur = cur.value
		if isinstance(cur, ast.Name):
			attrs.reverse()
			return cur.id, attrs
		return None, None
	def _resolve_local_class_dotted(base, attrs, lineno):
		if not _name_is_class_at(base, lineno):
			return None
		_key = _class_key_at(base, lineno)
		for _i, _attr in enumerate(attrs):
			if local_classes.get(_key, {}).get(_attr) != 'class':
				return None
			_ct = class_attr_types.get(_key, {}).get(_attr)
			if _ct is not None and _ct[0] == 'modclass':
				if _i == len(attrs) - 1:
					return ('class', _ct[1], _ct[2])
				return None
			if _ct is not None and _ct[0] == 'class' and _ct[1] in local_classes:
				_key = _ct[1]
			elif _attr in local_classes:
				_key = _attr
			else:
				return None
			if _i == len(attrs) - 1:
				return ('localclass', _key)
		return None
	def _resolve_dotted_alias(base, attrs, lineno):
		mod = _base_module_at(base, lineno)
		if mod is None:
			return _resolve_local_class_dotted(base, attrs, lineno)
		for _i, _attr in enumerate(attrs):
			_mm = _python_resolve_module_members(buf, mod)
			_kind = _mm.get(_attr)
			_sub = f'{mod}.{_attr}'
			if _kind is None and (_sub in valid_modules or _python_find_spec_cached(buf, _sub) is not None):
				_kind = 'module'
			if _kind == 'module':
				_tgt = _mm.get('@modtarget:' + _attr)
				mod = _tgt if _tgt is not None else _sub
				continue
			if _i == len(attrs) - 1 and _kind in ('class', 'func'):
				return (_kind, mod, _attr)
			return None
		return ('module', mod)
	for _cbnode in tree_class_defs:
		if _cbnode.name not in local_classes:
			continue
		_cbkey = _node_class_key(_cbnode)
		for _cbstmt in _flatten_class_body(_cbnode.body):
			_cbtgts = _cbstmt.targets if isinstance(_cbstmt, ast.Assign) else ([_cbstmt.target] if isinstance(_cbstmt, ast.AnnAssign) else [])
			_cbval = _cbstmt.value if isinstance(_cbstmt, (ast.Assign, ast.AnnAssign)) else None
			if isinstance(_cbval, ast.NamedExpr):
				_cbval = _cbval.value
			_cbval = _python_unwrap_descriptor(_cbval)
			if not isinstance(_cbval, ast.Attribute):
				continue
			_cbbase, _cbattrs = _dotted_chain_parts(_cbval)
			if _cbbase is None or not _cbattrs:
				continue
			_cbr = _resolve_dotted_alias(_cbbase, _cbattrs, _cbstmt.lineno)
			if _cbr is None:
				continue
			for _cbtgt in _cbtgts:
				if not isinstance(_cbtgt, ast.Name):
					continue
				if _cbr[0] == 'localclass':
					local_classes[_cbkey][_cbtgt.id] = 'class'
					class_attr_types.setdefault(_cbkey, {})[_cbtgt.id] = ('class', _cbr[1])
				elif _cbr[0] == 'class':
					local_classes[_cbkey][_cbtgt.id] = 'class'
					class_attr_types.setdefault(_cbkey, {})[_cbtgt.id] = ('modclass', _cbr[1], _cbr[2])
				elif _cbr[0] == 'func':
					local_classes[_cbkey][_cbtgt.id] = 'func'
				elif _cbr[0] == 'module':
					local_classes[_cbkey][_cbtgt.id] = 'module'
	for _daa_sc, _daa_ln, _daa_name, _daa_val in builder.dotted_alias_assigns:
		_daa_base, _daa_attrs = _dotted_chain_parts(_daa_val)
		if _daa_base is None or not _daa_attrs:
			continue
		_dr = _resolve_dotted_alias(_daa_base, _daa_attrs, _daa_ln)
		if _dr is None:
			continue
		_akind = _dr[0]
		_absc = _binding_scope_for(_daa_name, _daa_sc)
		_anames = builder.scopes[_absc]['names'].setdefault(_daa_name, [])
		_anames[:] = [(_l, _k) for _l, _k in _anames if not (_l == _daa_ln and _k == 'var')]
		_anames.append((_daa_ln, 'class' if _akind == 'localclass' else _akind))
		if _akind == 'localclass':
			_asrckey = _dr[1]
			class_def_lines.setdefault(_daa_name, [])
			if _daa_ln not in class_def_lines[_daa_name]:
				class_def_lines[_daa_name].append(_daa_ln)
			class_def_scopes[(_daa_name, _daa_ln)] = _absc
			_class_first_line.setdefault(_daa_name, _daa_ln)
			_akey = _class_key_at(_daa_name, _daa_ln)
			if _akey not in local_classes:
				local_classes[_akey] = local_classes[_asrckey]
			for _mk in list(local_class_method_params):
				if _mk.startswith(_asrckey + '.'):
					_ameth = _mk[len(_asrckey) + 1:]
					if _akey + '.' + _ameth not in local_class_method_params:
						local_class_method_params[_akey + '.' + _ameth] = local_class_method_params[_mk]
						if _mk in local_class_accepts_any:
							local_class_accepts_any.add(_akey + '.' + _ameth)
			_sorig2 = _class_origin_at(_asrckey, _daa_ln)
			if _sorig2 is not None:
				class_module_origin.setdefault(_daa_name, []).append((_daa_ln, _sorig2))
		elif _akind == 'class':
			_amod, _aattr = _dr[1], _dr[2]
			name_module_class.setdefault(_daa_name, []).append((_daa_ln, (_amod, _aattr)))
			class_def_lines.setdefault(_daa_name, [])
			if _daa_ln not in class_def_lines[_daa_name]:
				class_def_lines[_daa_name].append(_daa_ln)
			class_def_scopes[(_daa_name, _daa_ln)] = _absc
			_class_first_line.setdefault(_daa_name, _daa_ln)
			_akey = _class_key_at(_daa_name, _daa_ln)
			if _akey not in local_classes:
				_amems = _python_resolve_module_class_members(buf, _amod, _aattr)
				if _amems:
					local_classes[_akey] = _amems
			class_module_origin.setdefault(_daa_name, []).append((_daa_ln, (_amod, _aattr)))
		elif _akind == 'module':
			_asub = _dr[1]
			valid_modules.add(_asub)
			base_to_module.setdefault(_daa_name, []).append((_daa_ln, _asub))
			builder.module_alias_defs.setdefault(_daa_name, []).append((_daa_ln, _asub))
		elif _akind == 'func':
			_amod, _aattr = _dr[1], _dr[2]
			_attr_alias_func_origins.append((_daa_name, _daa_ln, _amod, _aattr))
	from_func_module = {}
	if seed_func_origins:
		for _sfo_n, _sfo_v in seed_func_origins.items():
			from_func_module.setdefault(_sfo_n, []).append((0, _sfo_v))
	for _, module_name, imported_name, _orig_name, _fln in builder.from_imports:
		module_name = _real_module_name(module_name)
		if module_name and imported_name != '*' and module_name in valid_modules:
			from_func_module.setdefault(imported_name, []).append((_fln, (module_name, _orig_name)))
	for _afo_name, _afo_ln, _afo_mod, _afo_attr in _attr_alias_func_origins:
		from_func_module.setdefault(_afo_name, []).append((_afo_ln, (_afo_mod, _afo_attr)))
	local_def_lines = {}
	for _dln, _dnm, _dk in builder.def_names:
		local_def_lines.setdefault(_dnm, []).append(_dln)
	for _asc, _aln, _aname, _asrc in builder.alias_assigns:
		if _aname in local_classes or _asrc in local_classes:
			local_def_lines.setdefault(_aname, []).append(_aln)
	def _lookup_module_callable(mod_name, key, seen = None):
		if seen is None:
			seen = set()
		if (mod_name, key) in seen:
			return None, None
		seen.add((mod_name, key))
		if mod_name not in valid_modules and _python_find_spec_cached(buf, mod_name) is None:
			return None, None
		fp = _python_resolve_module_func_params(buf, mod_name)
		if key in fp:
			v = fp[key]
			if v is None:
				return True, None
			return True, v
		imports = fp.get('@imports', {})
		_head = key.split('.', 1)[0]
		_tail = key[len(_head) + 1:] if '.' in key else None
		if _head in imports and imports[_head][1] is not None:
			_rmod, _rname = imports[_head]
			return _lookup_module_callable(_rmod, _rname if _tail is None else f'{_rname}.{_tail}', seen)
		return None, None
	def _resolve_through_module(mod_name, rest):
		cur_mod = mod_name
		idx = 0
		while idx < len(rest):
			seg = rest[idx]
			sub_full = cur_mod + '.' + seg
			if sub_full in valid_modules or _python_find_spec_cached(buf, sub_full) is not None:
				cur_mod = sub_full
				idx += 1
				continue
			mems = _python_resolve_module_members(buf, cur_mod)
			_tgt = mems.get('@modtarget:' + seg)
			if _tgt is not None:
				cur_mod = _tgt
				idx += 1
				continue
			if mems.get(seg) == 'class':
				if idx + 1 < len(rest):
					return _lookup_module_callable(cur_mod, seg + '.' + rest[idx + 1])
				return _lookup_module_callable(cur_mod, seg)
			if idx == len(rest) - 1:
				return _lookup_module_callable(cur_mod, seg)
			return None, None
		return None, None
	def _params_for_dotted(dotted, lineno):
		if not dotted:
			return None, None
		root = dotted[0]
		rest = dotted[1:]
		if len(dotted) == 1:
			kind = _call_name_kind(root, lineno)
			_local_line = None
			for _dl in local_def_lines.get(root, []):
				if _dl <= lineno and (_local_line is None or _dl > _local_line):
					_local_line = _dl
			if _local_line is not None and kind not in ('func', 'class', None):
				_local_line = None
			_imp = None
			_imp_line = None
			for _fl, _fv in from_func_module.get(root, []):
				if _fl <= lineno and (_imp_line is None or _fl >= _imp_line):
					_imp_line = _fl
					_imp = _fv
			if _local_line is not None and (_imp_line is None or _local_line >= _imp_line):
				if kind == 'class' and root in local_classes and root in class_def_lines:
					_ckey = _class_key_at(root, lineno)
					if _ckey + '.__init__' in local_class_accepts_any:
						return True, None
					if _ckey + '.__init__' in local_class_method_params:
						return True, local_class_method_params[_ckey + '.__init__']
					for _lcmo_mod, _lcmo_cls in local_class_module_origins.get(_ckey, []):
						found, mp = _python_resolve_module_method(buf, _lcmo_mod, _lcmo_cls, '__init__')
						if found:
							return True, mp
					_corig = _class_origin_at(root, lineno)
					if _corig is not None:
						found, mp = _python_resolve_module_method(buf, _corig[0], _corig[1], '__init__')
						if found:
							return True, mp
					return True, set()
				if kind == 'class' and root in local_classes:
					_ckey = _class_key_at(root, lineno)
					if _ckey + '.__init__' in local_class_accepts_any:
						return True, None
					if _ckey + '.__init__' in local_class_method_params:
						return True, local_class_method_params[_ckey + '.__init__']
					for _lcmo_mod, _lcmo_cls in local_class_module_origins.get(_ckey, []):
						found, mp = _python_resolve_module_method(buf, _lcmo_mod, _lcmo_cls, '__init__')
						if found:
							return True, mp
					_corig = _class_origin_at(root, lineno)
					if _corig is not None:
						found, mp = _python_resolve_module_method(buf, _corig[0], _corig[1], '__init__')
						if found:
							return True, mp
				if _func_accepts_any_at(root, lineno):
					return True, None
				return True, _func_params_at(root, lineno) or set()
			if _imp_line is not None and kind in ('func', 'class', 'module', None):
				return _lookup_module_callable(_imp[0], _imp[1])
			if kind is None and root in _PYTHON_BUILTIN_CALLABLE_NAMES:
				return True, _PYTHON_BUILTIN_CALLABLE_PARAMS.get(root, set())
			if kind in ('func', 'builtin') and root in builder.func_params:
				if _func_accepts_any_at(root, lineno):
					return True, None
				return True, _func_params_at(root, lineno) or set()
			if kind == 'class' and root in local_classes:
				_ckey = _class_key_at(root, lineno)
				if _ckey + '.__init__' in local_class_accepts_any:
					return True, None
				if _ckey + '.__init__' in local_class_method_params:
					return True, local_class_method_params[_ckey + '.__init__']
				for _lcmo_mod, _lcmo_cls in local_class_module_origins.get(_ckey, []):
					found, mp = _python_resolve_module_method(buf, _lcmo_mod, _lcmo_cls, '__init__')
					if found:
						return True, mp
				_corig = _class_origin_at(root, lineno)
				if _corig is not None:
					found, mp = _python_resolve_module_method(buf, _corig[0], _corig[1], '__init__')
					if found:
						return True, mp
			return None, None
		if len(rest) == 1 and _name_is_class_at(root, lineno):
			_ckey = _class_key_at(root, lineno)
			if local_classes.get(_ckey, {}).get(rest[0]) == 'class':
				_cat = class_attr_types.get(_ckey, {}).get(rest[0])
				if _cat is None and rest[0] in local_classes:
					_cat = ('class', rest[0])
				if _cat is not None and _cat[0] == 'class' and _cat[1] in local_classes:
					_tkey = _cat[1]
					if _tkey + '.__init__' in local_class_accepts_any:
						return True, None
					if _tkey + '.__init__' in local_class_method_params:
						return True, local_class_method_params[_tkey + '.__init__']
					for _lcmo_mod, _lcmo_cls in local_class_module_origins.get(_tkey, []):
						found, mp = _python_resolve_module_method(buf, _lcmo_mod, _lcmo_cls, '__init__')
						if found:
							return True, mp
					_torig = _class_origin_at(_tkey, lineno)
					if _torig is not None:
						found, mp = _python_resolve_module_method(buf, _torig[0], _torig[1], '__init__')
						if found:
							return True, mp
					return True, set()
				if _cat is not None and _cat[0] == 'modclass':
					found, mp = _python_resolve_module_method(buf, _cat[1], _cat[2], '__init__')
					if found:
						return True, mp
			_mkey = _ckey + '.' + rest[0]
			if _instance_only_attr(_ckey, rest[0]):
				return None, None
			if _mkey in local_class_accepts_any:
				return True, None
			if _mkey in local_class_method_params:
				return True, local_class_method_params[_mkey]
			for _lcmo_mod, _lcmo_cls in local_class_module_origins.get(_ckey, []):
				found, mp = _python_resolve_module_method(buf, _lcmo_mod, _lcmo_cls, rest[0])
				if found:
					return True, mp
		if _call_name_kind(root, lineno) in ('module', None):
			_rmod = _base_module_at(root, lineno)
			if _rmod is not None:
				return _resolve_through_module(_rmod, rest)
		return None, None
	_ck()
	module_literals = []
	for _ifn in tree_importfroms:
		if _ifn.module and '.' not in _ifn.module and _ifn.module in valid_modules:
			module_literals.append((_ifn.lineno, _ifn.col_offset + 5 + _ifn.level, _ifn.module))
	for _imn in tree_imports:
		for _ial in _imn.names:
			if _ial.asname and '.' not in _ial.name and _ial.name in valid_modules:
				module_literals.append((_ial.lineno, _ial.col_offset, _ial.name))
	import_dotted_lines = [(lineno, col, dotted) for lineno, col, dotted in builder.import_dotted_lines if dotted in valid_modules or dotted in _dotted_module_targets or _python_find_spec_cached(buf, dotted) is not None]
	import_orig_name_tags = []
	_kind_to_tag = {'func': 'hpf', 'class': 'hpx', 'var': 'hpv', 'module': 'hpm'}
	for _oln, _ocol, _oname, _omod in builder.import_orig_names:
		_omod = _real_module_name(_omod)
		if not _omod or _omod not in valid_modules:
			continue
		_okind = None
		if f'{_omod}.{_oname}' in valid_modules or _python_find_spec_cached(buf, f'{_omod}.{_oname}') is not None:
			_okind = 'module'
		else:
			_ocontents = module_contents.get(_omod) or _python_resolve_module_members(buf, _omod)
			_okind = _ocontents.get(_oname)
		_otag = _kind_to_tag.get(_okind)
		if _otag is not None:
			import_orig_name_tags.append((_oln, _ocol, _oname, _otag))
	_from_import_map = {}
	for _, module_name, imported_name, _orig_name, _fln in builder.from_imports:
		module_name = _real_module_name(module_name)
		if module_name and imported_name != '*':
			_from_import_map.setdefault(imported_name, []).append((_fln, module_name))
	_ck()
	scope_var_types = {}
	if seed_types:
		for _stn, _stt in seed_types.items():
			if _stt in local_classes:
				scope_var_types.setdefault(0, {}).setdefault(_stn, []).append((0, _stt))
	_var_type_alias_assigns = []
	container_elem_types = {}
	def _elem_type_name(v, lineno):
		if isinstance(v, ast.Call) and isinstance(v.func, ast.Name):
			_en = v.func.id
			if _en in local_classes and _name_is_class_at(_en, lineno):
				return _class_key_at(_en, lineno)
			if _class_origin_at(_en, lineno) is not None:
				return _en
		if isinstance(v, ast.Call) and isinstance(v.func, ast.Attribute) and isinstance(v.func.value, ast.Name):
			_emod = _base_module_at(v.func.value.id, lineno)
			if _emod is not None and _python_resolve_module_members(buf, _emod).get(v.func.attr) == 'class':
				class_module_origin.setdefault(v.func.attr, []).append((lineno, (_emod, v.func.attr)))
				return v.func.attr
		return None
	for node in tree_assigns:
		for tgt, val in _assign_pairs(node.targets, node.value):
			if not isinstance(tgt, ast.Name) or val is None:
				continue
			type_name = None
			if isinstance(val, ast.Call):
				func = val.func
				mod_name = None
				if isinstance(func, ast.Name):
					type_name = func.id
					mod_name = _line_def_at(_from_import_map.get(type_name), node.lineno)
				elif isinstance(func, ast.Attribute):
					type_name = func.attr
					mod_name = _base_module_at(func.value.id, node.lineno) if isinstance(func.value, ast.Name) else None
				if type_name and type_name not in local_classes and mod_name:
					if _python_resolve_module_members(buf, mod_name).get(type_name) == 'class':
						class_module_origin.setdefault(type_name, []).append((node.lineno, (mod_name, type_name)))
			elif isinstance(val, ast.Constant):
				type_name = type(val.value).__name__
			elif isinstance(val, ast.List):
				type_name = 'list'
			elif isinstance(val, ast.Dict):
				type_name = 'dict'
			elif isinstance(val, ast.Tuple):
				type_name = 'tuple'
			elif isinstance(val, ast.Set):
				type_name = 'set'
			elif isinstance(val, ast.JoinedStr):
				type_name = 'str'
			elif isinstance(val, ast.Name):
				_var_type_alias_assigns.append((node.lineno, tgt.id, val.id))
			if isinstance(val, ast.Call) and isinstance(val.func, ast.Name) and type_name and type_name in local_classes and not _name_is_class_at(type_name, node.lineno):
				type_name = None
			if isinstance(val, ast.Call) and isinstance(val.func, ast.Name) and type_name and type_name in local_classes:
				type_name = _class_key_at(type_name, node.lineno)
			if type_name and (type_name in local_classes or _class_origin_at(type_name, node.lineno) is not None or (type_name in _PYTHON_BUILTIN_MEMBERS and type_name not in local_classes)):
				sc_idx = _binding_scope_for(tgt.id, _scope_for_line(node.lineno))
				if sc_idx is not None:
					scope_var_types.setdefault(sc_idx, {}).setdefault(tgt.id, []).append((node.lineno, type_name))
			elif not isinstance(val, ast.Name):
				sc_idx = _binding_scope_for(tgt.id, _scope_for_line(node.lineno))
				if sc_idx is not None:
					scope_var_types.setdefault(sc_idx, {}).setdefault(tgt.id, []).append((node.lineno, None))
			_cet_elts = None
			if isinstance(val, (ast.List, ast.Tuple, ast.Set)):
				_cet_elts = val.elts
			elif isinstance(val, ast.Dict):
				_cet_elts = [_dv for _dv in val.values if _dv is not None]
			if _cet_elts:
				_cet_name = None
				_cet_ok = True
				for _cet_el in _cet_elts:
					_cet_t = _elem_type_name(_cet_el, node.lineno)
					if _cet_t is None or (_cet_name is not None and _cet_t != _cet_name):
						_cet_ok = False
						break
					_cet_name = _cet_t
				if _cet_ok and _cet_name is not None and (_cet_name in local_classes or _class_origin_at(_cet_name, node.lineno) is not None):
					_cet_sc = _binding_scope_for(tgt.id, _scope_for_line(node.lineno))
					if _cet_sc is not None:
						container_elem_types.setdefault(_cet_sc, {}).setdefault(tgt.id, []).append((node.lineno, _cet_name))
	for _fn in ast.walk(tree):
		if not isinstance(_fn, (ast.For, ast.AsyncFor)) or not isinstance(_fn.target, ast.Name):
			continue
		_fit = None
		if isinstance(_fn.iter, ast.Name):
			_fsc0 = _binding_scope_for(_fn.iter.id, _scope_for_line(_fn.lineno))
			_fcands = container_elem_types.get(_fsc0, {}).get(_fn.iter.id) if _fsc0 is not None else None
			if _fcands:
				_fb = None
				for _fdl, _ftn in _fcands:
					if _fdl <= _fn.lineno and (_fb is None or _fdl > _fb[0]):
						_fb = (_fdl, _ftn)
				if _fb is not None:
					_fit = _fb[1]
		elif isinstance(_fn.iter, (ast.List, ast.Tuple, ast.Set)):
			_fname = None
			_fok = True
			for _fel in _fn.iter.elts:
				_ft = _elem_type_name(_fel, _fn.lineno)
				if _ft is None or (_fname is not None and _ft != _fname):
					_fok = False
					break
				_fname = _ft
			if _fok:
				_fit = _fname
		if _fit is not None and (_fit in local_classes or _class_origin_at(_fit, _fn.lineno) is not None):
			_ftsc = _binding_scope_for(_fn.target.id, _scope_for_line(_fn.lineno))
			if _ftsc is not None:
				scope_var_types.setdefault(_ftsc, {}).setdefault(_fn.target.id, []).append((_fn.lineno, _fit))
	for _valn, _vatgt, _vasrc in sorted(_var_type_alias_assigns):
		_vsc = _scope_for_line(_valn)
		_scur = _vsc
		_vtype = None
		_vfound = False
		while _scur is not None and not _vfound:
			_vscobj = builder.scopes[_scur]
			if _vscobj.get('kind') == 'class' and _scur != _vsc:
				_scur = _vscobj['parent']
				continue
			if _vasrc in _vscobj['names']:
				_svt = scope_var_types.get(_scur, {}).get(_vasrc)
				if _svt:
					_vb = None
					for _vdl, _vtn in _svt:
						if _scur == _vsc and _vdl > _valn:
							continue
						if _vb is None or _vdl > _vb[0]:
							_vb = (_vdl, _vtn)
					if _vb is not None:
						_vtype = _vb[1]
				_vfound = True
				break
			_scur = _vscobj['parent']
		_vtsc = _binding_scope_for(_vatgt, _vsc)
		if _vtsc is not None:
			scope_var_types.setdefault(_vtsc, {}).setdefault(_vatgt, []).append((_valn, _vtype))
	_ck()
	for cls_node in tree_class_defs:
		for meth in cls_node.body:
			if not isinstance(meth, (ast.FunctionDef, ast.AsyncFunctionDef)):
				continue
			_fp = meth.args.args[0].arg if (meth.args.args and _python_method_has_implicit_first_param(meth)) else None
			if not _fp:
				continue
			for stmt in ast.walk(meth):
				if not isinstance(stmt, ast.Assign):
					continue
				for tgt, val in _assign_pairs(stmt.targets, stmt.value):
					if not (isinstance(tgt, ast.Attribute) and isinstance(tgt.value, ast.Name) and tgt.value.id == _fp) or val is None:
						continue
					_self_assigned_attrs.setdefault(_node_class_key(cls_node), set()).add(tgt.attr)
					type_name = None
					if isinstance(val, ast.Call):
						func = val.func
						mod_name = None
						if isinstance(func, ast.Name):
							type_name = func.id
							mod_name = _line_def_at(_from_import_map.get(type_name), stmt.lineno)
							if mod_name is None and not _name_is_class_at(type_name, stmt.lineno):
								type_name = None
						elif isinstance(func, ast.Attribute):
							type_name = func.attr
							mod_name = _base_module_at(func.value.id, stmt.lineno) if isinstance(func.value, ast.Name) else None
						if type_name and type_name not in local_classes and mod_name:
							mems = _python_resolve_module_class_members(buf, mod_name, type_name)
							if mems:
								local_classes[type_name] = mems
								class_module_origin.setdefault(type_name, []).append((stmt.lineno, (mod_name, type_name)))
					elif isinstance(val, ast.Constant):
						type_name = type(val.value).__name__
					elif isinstance(val, ast.List):
						type_name = 'list'
					elif isinstance(val, ast.Dict):
						type_name = 'dict'
					elif isinstance(val, ast.Tuple):
						type_name = 'tuple'
					elif isinstance(val, ast.Set):
						type_name = 'set'
					elif isinstance(val, ast.JoinedStr):
						type_name = 'str'
					if type_name and type_name in local_classes:
						if isinstance(val, ast.Call) and isinstance(val.func, ast.Name):
							type_name = _class_key_at(type_name, stmt.lineno)
						class_type_maps.setdefault(_node_class_key(cls_node), {})[tgt.attr] = type_name
					else:
						class_type_maps.get(_node_class_key(cls_node), {}).pop(tgt.attr, None)
	for cls_node in tree_class_defs:
		if cls_node.name not in local_classes:
			continue
		for stmt in cls_node.body:
			if not isinstance(stmt, ast.Assign):
				continue
			val = stmt.value
			type_name = None
			if isinstance(val, ast.Call):
				func = val.func
				if isinstance(func, ast.Name):
					type_name = func.id
				elif isinstance(func, ast.Attribute):
					type_name = func.attr
			elif isinstance(val, ast.Constant):
				type_name = type(val.value).__name__
			elif isinstance(val, ast.List):
				type_name = 'list'
			elif isinstance(val, ast.Dict):
				type_name = 'dict'
			elif isinstance(val, ast.Tuple):
				type_name = 'tuple'
			elif isinstance(val, ast.Set):
				type_name = 'set'
			elif isinstance(val, ast.JoinedStr):
				type_name = 'str'
			if type_name and type_name in local_classes:
				if isinstance(val, ast.Call) and isinstance(val.func, ast.Name):
					type_name = _class_key_at(type_name, stmt.lineno)
				for tgt in stmt.targets:
					if isinstance(tgt, ast.Name) and tgt.id not in _self_assigned_attrs.get(_node_class_key(cls_node), ()):
						class_type_maps.setdefault(_node_class_key(cls_node), {})[tgt.id] = type_name
	for _saa_cls, _saa_names in _self_assigned_attrs.items():
		for _saa_name in _saa_names:
			if local_classes.get(_saa_cls, {}).get(_saa_name) != 'var':
				continue
			_saa_key = _saa_cls + '.' + _saa_name
			local_class_method_params.pop(_saa_key, None)
			local_class_accepts_any.discard(_saa_key)
	_ck()
	_ck()
	method_fp_ranges = []
	for _cnode in tree_class_defs:
		if _cnode.name in local_classes:
			_cnk = _node_class_key(_cnode)
			for _meth in _cnode.body:
				if isinstance(_meth, (ast.FunctionDef, ast.AsyncFunctionDef)) and _meth.args.args and _python_method_has_implicit_first_param(_meth):
					method_fp_ranges.append((_meth.lineno, getattr(_meth, 'end_lineno', _meth.lineno), _meth.args.args[0].arg, _cnk))
	def _fp_class_at(name, lineno):
		best = None
		for ms, me, fp, cn in method_fp_ranges:
			if ms <= lineno <= me and name == fp and (best is None or ms > best[0]):
				best = (ms, cn)
		return best[1] if best else None
	def _var_type_at(name, lineno, col = None):
		sidx = _scope_for_line(lineno) if col is None else _scope_for_pos(lineno, col)
		inner = sidx
		while sidx is not None:
			sc = builder.scopes[sidx]
			if sc.get('kind') == 'class' and sidx != inner:
				sidx = sc['parent']
				continue
			if name in sc['names']:
				svt = scope_var_types.get(sidx, {})
				if name in svt:
					best = None
					for dl, tn in svt[name]:
						if sidx == inner and dl > lineno:
							continue
						if best is None or dl > best[0]:
							best = (dl, tn)
					if best is not None:
						return best[1]
				return None
			sidx = sc['parent']
		return None
	def _assign_type_name(val, lineno):
		if isinstance(val, ast.Call):
			func = val.func
			if isinstance(func, ast.Name):
				return func.id if _name_is_class_at(func.id, lineno) else None
			if isinstance(func, ast.Attribute):
				return func.attr if func.attr in local_classes else None
			return None
		if isinstance(val, ast.Constant):
			return type(val.value).__name__
		if isinstance(val, ast.List):
			return 'list'
		if isinstance(val, ast.Dict):
			return 'dict'
		if isinstance(val, ast.Tuple):
			return 'tuple'
		if isinstance(val, ast.Set):
			return 'set'
		if isinstance(val, ast.JoinedStr):
			return 'str'
		if isinstance(val, ast.Name) and _name_is_class_at(val.id, lineno):
			return _class_key_at(val.id, lineno)
		return None
	def _literal_type(node):
		if isinstance(node, ast.Constant):
			return type(node.value).__name__
		if isinstance(node, ast.JoinedStr):
			return 'str'
		if isinstance(node, ast.List):
			return 'list'
		if isinstance(node, ast.Dict):
			return 'dict'
		if isinstance(node, ast.Tuple):
			return 'tuple'
		if isinstance(node, ast.Set):
			return 'set'
		return None
	def _module_attr_kind(mod, attr):
		_mm = _python_resolve_module_members(buf, mod)
		_k = _mm.get(attr)
		if _k is not None:
			return _k
		_dk = dynamic_module_attrs.get(mod, {}).get(attr)
		if _dk is not None:
			return _dk
		_sub = f'{mod}.{attr}'
		if _sub in valid_modules:
			return 'module'
		_spec = _python_find_spec_cached(buf, mod)
		if _spec is not None and getattr(_spec, 'submodule_search_locations', None) and _python_find_spec_cached(buf, _sub) is not None:
			return 'module'
		return None
	def _assign_value_kind(val, lineno):
		if val is None:
			return None
		val = _python_unwrap_descriptor(val)
		if isinstance(val, ast.Lambda):
			return 'func'
		if isinstance(val, ast.Call) and builder._dynamic_import_module(val) is not None:
			return 'module'
		if isinstance(val, ast.Name):
			_vk = _call_name_kind(val.id, lineno)
			if _vk in ('func', 'class', 'module'):
				return _vk
			if _vk is None and val.id in _PYTHON_BUILTIN_MEMBERS:
				return 'class'
			if _vk is None and val.id in _PYTHON_BUILTIN_CALLABLE_NAMES:
				return 'func'
			return None
		if isinstance(val, ast.Attribute) and isinstance(val.value, ast.Name):
			_vfpc = _fp_class_at(val.value.id, lineno)
			if _vfpc is not None:
				_vfk = local_classes.get(_vfpc, {}).get(val.attr)
				if _vfk in ('func', 'class', 'module'):
					return _vfk
			if _name_is_class_at(val.value.id, lineno):
				_vck = _class_key_at(val.value.id, lineno)
				_vckk = local_classes.get(_vck, {}).get(val.attr)
				if _vckk in ('func', 'class', 'module'):
					return _vckk
			if _call_name_kind(val.value.id, lineno) in ('module', None):
				_vmod = _base_module_at(val.value.id, lineno)
				if _vmod is not None:
					_vak = _module_attr_kind(_vmod, val.attr)
					if _vak in ('func', 'class', 'module'):
						return _vak
		return None
	def _value_type(val, lineno):
		val = _python_unwrap_descriptor(val)
		_blt = _literal_type(val)
		if _blt is not None and _blt in _PYTHON_BUILTIN_MEMBERS:
			return ('builtin', _blt)
		if isinstance(val, ast.Call):
			_dr = builder._dynamic_import_module(val)
			if _dr is not None:
				return ('module', _dr[0])
			_ft = _value_type(val.func, lineno)
			if _ft is not None:
				if _ft[0] == 'class':
					return ('instance', _ft[1])
				if _ft[0] == 'modclass':
					return ('minstance', _ft[1], _ft[2])
			return None
		if isinstance(val, ast.Name):
			_vo = _class_origin_at(val.id, lineno)
			if _vo is not None and _call_name_kind(val.id, lineno) in (None, 'class'):
				return ('modclass', _vo[0], _vo[1])
			if val.id in local_classes and _call_name_kind(val.id, lineno) in (None, 'class'):
				return ('class', _class_key_at(val.id, lineno))
			if _call_name_kind(val.id, lineno) == 'module':
				_vm = _base_module_at(val.id, lineno)
				if _vm is not None:
					return ('module', _vm)
			_vvt = _var_type_at(val.id, lineno)
			if _vvt is not None:
				if _vvt in _PYTHON_BUILTIN_MEMBERS and _vvt not in local_classes:
					return ('builtin', _vvt)
				_vvo = _class_origin_at(_vvt, lineno)
				if _vvo is not None and _vvt not in local_classes:
					return ('minstance', _vvo[0], _vvo[1])
				if _vvt in local_classes:
					return ('instance', _vvt)
			return None
		if isinstance(val, ast.Attribute) and isinstance(val.value, ast.Name):
			if _call_name_kind(val.value.id, lineno) in ('module', None):
				_vm = _base_module_at(val.value.id, lineno)
				if _vm is not None:
					_vmk = _module_attr_kind(_vm, val.attr)
					if _vmk == 'class':
						return ('modclass', _vm, val.attr)
					if _vmk == 'module':
						_vtgt = _python_resolve_module_members(buf, _vm).get('@modtarget:' + val.attr)
						return ('module', _vtgt if _vtgt is not None else f'{_vm}.{val.attr}')
			return None
		return None
	for _ccnode in tree_class_defs:
		if _ccnode.name not in local_classes:
			continue
		for _cstmt in _flatten_class_body(_ccnode.body):
			_ctgts = _cstmt.targets if isinstance(_cstmt, ast.Assign) else ([_cstmt.target] if isinstance(_cstmt, ast.AnnAssign) else [])
			for _ctgt, _cval in _assign_pairs(_ctgts, _cstmt.value if _ctgts else None):
				if isinstance(_cval, ast.NamedExpr):
					_cval = _cval.value
				_cval = _python_unwrap_descriptor(_cval)
				if not isinstance(_ctgt, ast.Name) or _cval is None:
					continue
				if _ctgt.id in _self_assigned_attrs.get(_node_class_key(_ccnode), ()):
					continue
				_cvt = _value_type(_cval, _cstmt.lineno)
				if _cvt is not None:
					class_attr_types.setdefault(_node_class_key(_ccnode), {})[_ctgt.id] = _cvt
					if _cvt[0] in ('modclass', 'class'):
						local_classes[_node_class_key(_ccnode)][_ctgt.id] = 'class'
	for _ucnode in tree_class_defs:
		if _ucnode.name not in local_classes:
			continue
		for _umeth in _ucnode.body:
			if not isinstance(_umeth, (ast.FunctionDef, ast.AsyncFunctionDef)) or not _umeth.args.args or not _python_method_has_implicit_first_param(_umeth):
				continue
			_ufp = _umeth.args.args[0].arg
			for _ustmt in ast.walk(_umeth):
				_utgts = _ustmt.targets if isinstance(_ustmt, ast.Assign) else ([_ustmt.target] if isinstance(_ustmt, ast.AnnAssign) else [])
				for _utgt, _uval in _assign_pairs(_utgts, _ustmt.value if _utgts else None):
					if not (isinstance(_utgt, ast.Attribute) and isinstance(_utgt.value, ast.Name) and _utgt.value.id == _ufp):
						continue
					_ukind = _assign_value_kind(_uval, _ustmt.lineno)
					_unk = _node_class_key(_ucnode)
					if _ukind is not None and local_classes[_unk].get(_utgt.attr) == 'var':
						local_classes[_unk][_utgt.attr] = _ukind
					_uvt = _value_type(_uval, _ustmt.lineno) if _uval is not None else None
					if _uvt is not None:
						class_attr_types.setdefault(_unk, {})[_utgt.attr] = _uvt
	def _elem_type_at(name, lineno):
		sidx = _scope_for_line(lineno)
		inner = sidx
		while sidx is not None:
			sc = builder.scopes[sidx]
			if sc.get('kind') == 'class' and sidx != inner:
				sidx = sc['parent']
				continue
			_cet = container_elem_types.get(sidx, {}).get(name)
			if _cet:
				_cb = None
				for _cdl, _ctn in _cet:
					if sidx == inner and _cdl > lineno:
						continue
					if _cb is None or _cdl > _cb[0]:
						_cb = (_cdl, _ctn)
				if _cb is not None:
					return _cb[1]
			sidx = sc['parent']
		return None
	def _infer_type(node):
		if isinstance(node, ast.NamedExpr):
			return _infer_type(node.value)
		if isinstance(node, ast.Subscript) and isinstance(node.value, ast.Name):
			_st = _elem_type_at(node.value.id, node.lineno)
			if _st is not None:
				_sorig3 = _class_origin_at(_st, node.lineno)
				if _sorig3 is not None and _st not in local_classes:
					return ('minstance', _sorig3[0], _sorig3[1])
				return ('instance', _st)
		if isinstance(node, ast.Name):
			vt = _var_type_at(node.id, node.lineno)
			if vt is not None:
				if vt in _PYTHON_BUILTIN_MEMBERS and vt not in local_classes:
					return ('builtin', vt)
				_vorig = _class_origin_at(vt, node.lineno)
				if _vorig is not None and vt not in local_classes:
					return ('minstance', _vorig[0], _vorig[1])
				return ('instance', vt)
			fpc = _fp_class_at(node.id, node.lineno)
			if fpc is not None:
				return ('instance', fpc)
			_norig = _class_origin_at(node.id, node.lineno)
			if _norig is not None and _call_name_kind(node.id, node.lineno) == 'class':
				return ('modclass', _norig[0], _norig[1])
			if _name_is_class_at(node.id, node.lineno):
				return ('class', _class_key_at(node.id, node.lineno))
			if _call_name_kind(node.id, node.lineno) == 'module':
				_nmod = _base_module_at(node.id, node.lineno)
				if _nmod is not None:
					return ('module', _nmod)
			return None
		_lt = _literal_type(node)
		if _lt is not None and _lt in local_classes:
			return ('instance', _lt)
		if isinstance(node, ast.Call):
			if isinstance(node.func, ast.Name) and node.func.id == '__import__' and _call_name_kind('__import__', node.lineno) is None and node.args and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
				if node.args[0].value in valid_modules or _python_find_spec_cached(buf, node.args[0].value) is not None:
					if _python_import_fromlist_is_nonempty(node):
						return ('module', node.args[0].value)
					return ('module', node.args[0].value.split('.')[0])
			if isinstance(node.func, ast.Attribute) and node.func.attr == 'import_module' and node.args and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
				if node.args[0].value in valid_modules or _python_find_spec_cached(buf, node.args[0].value) is not None:
					return ('module', node.args[0].value)
			if isinstance(node.func, ast.Name) and node.func.id == 'super' and _call_name_kind('super', node.lineno) is None:
				_sbest = None
				for _ms, _me, _mfp, _mcls in method_fp_ranges:
					if _ms <= node.lineno <= _me and (_sbest is None or _ms > _sbest[0]):
						_sbest = (_ms, _mcls)
				if _sbest is not None:
					return ('instance', _sbest[1])
			rf = _infer_type(node.func)
			if rf is not None and rf[0] == 'class':
				return ('instance', rf[1])
			if rf is not None and rf[0] == 'modclass':
				return ('minstance', rf[1], rf[2])
			if isinstance(node.func, ast.Attribute):
				br = _infer_type(node.func.value)
				if br is not None and br[0] in ('instance', 'class'):
					rt = class_type_maps.get(br[1], {}).get(node.func.attr)
					if rt is None:
						rt = _PYTHON_BUILTIN_METHOD_RETURNS.get(br[1], {}).get(node.func.attr)
					if rt is not None and rt in local_classes:
						return ('instance', rt)
			return None
		if isinstance(node, ast.Attribute):
			r = _infer_type(node.value)
			if r is None:
				return None
			if r[0] == 'instance' and isinstance(node.value, ast.Name) and _fp_class_at(node.value.id, node.lineno) != r[1]:
				_vasc = _binding_scope_for(node.value.id, _scope_for_line(node.lineno))
				if _vasc is not None:
					_vfound, _vtype = _var_attr_type_at(_vasc, node.value.id, node.attr, node.lineno)
					if _vfound:
						return _vtype
			if r[0] == 'module':
				_mk = _module_attr_kind(r[1], node.attr)
				if _mk == 'module':
					_tgt = _python_resolve_module_members(buf, r[1]).get('@modtarget:' + node.attr)
					return ('module', _tgt if _tgt is not None else f'{r[1]}.{node.attr}')
				if _mk == 'class':
					_dmc = dynamic_module_attr_types.get(r[1], {}).get(node.attr)
					if _dmc is not None and _dmc in local_classes:
						return ('class', _dmc)
					return ('modclass', r[1], node.attr)
				_dmt = dynamic_module_attr_types.get(r[1], {}).get(node.attr)
				if _dmt is not None and _dmt in local_classes:
					return ('instance', _dmt)
				return None
			if r[0] in ('modclass', 'minstance'):
				_cat = class_attr_types.get(r[2], {}).get(node.attr)
				if _cat is not None:
					return _cat
				_dt = dynamic_class_attr_types.get(r[2], {}).get(node.attr)
				if _dt is None and r[0] == 'modclass':
					_dt = dynamic_modclass_attr_types.get(r[2], {}).get(node.attr)
				if _dt is not None and _dt in local_classes:
					return ('instance', _dt)
				return None
			if r[0] == 'class' and _instance_only_attr(r[1], node.attr):
				return None
			members = local_classes.get(r[1], {})
			_cat = class_attr_types.get(r[1], {}).get(node.attr)
			if _cat is not None:
				return _cat
			if r[0] == 'instance':
				_dt = dynamic_class_attr_types.get(r[1], {}).get(node.attr)
				if _dt is not None and _dt in local_classes:
					return ('instance', _dt)
			if node.attr not in members:
				return None
			tt = class_type_maps.get(r[1], {}).get(node.attr)
			if tt is not None and tt in local_classes:
				return ('instance', tt)
			if members[node.attr] == 'class' and node.attr in local_classes:
				return ('class', node.attr)
			return None
		return None
	for _an in sorted(tree_assigns, key = lambda _n: (_n.lineno, _n.col_offset)):
		for _atgt, _aval in _assign_pairs(_an.targets, _an.value):
			if not isinstance(_atgt, ast.Attribute):
				continue
			_atn = _assign_type_name(_aval, _an.lineno) if _aval is not None else None
			_adkind = _assign_value_kind(_aval, _an.lineno) or 'var'
			if isinstance(_atgt.value, ast.Name) and _call_name_kind(_atgt.value.id, _an.lineno) == 'class' and _atgt.value.id in local_classes and _class_origin_at(_atgt.value.id, _an.lineno) is None:
				local_classes[_atgt.value.id][_atgt.attr] = _adkind
				if _adkind == 'class':
					_avr = _infer_type(_aval) if _aval is not None else None
					if _avr is not None and _avr[0] in ('class', 'modclass'):
						class_attr_types.setdefault(_atgt.value.id, {})[_atgt.attr] = _avr
				if _atn is not None and _atn in local_classes:
					class_type_maps.setdefault(_atgt.value.id, {})[_atgt.attr] = _atn
				continue
			_br = _infer_type(_atgt.value)
			if _br is None:
				continue
			if _br[0] == 'module':
				dynamic_module_attrs.setdefault(_br[1], {})[_atgt.attr] = _adkind
				if _atn is not None and _atn in local_classes:
					dynamic_module_attr_types.setdefault(_br[1], {})[_atgt.attr] = _atn
			elif _br[0] == 'modclass':
				dynamic_modclass_attrs.setdefault(_br[2], {})[_atgt.attr] = _adkind
				if _atn is not None and _atn in local_classes:
					dynamic_modclass_attr_types.setdefault(_br[2], {})[_atgt.attr] = _atn
			elif _br[0] == 'minstance':
				dynamic_class_attrs.setdefault(_br[2], {})[_atgt.attr] = _adkind
				if _atn is not None and _atn in local_classes:
					dynamic_class_attr_types.setdefault(_br[2], {})[_atgt.attr] = _atn
			elif _br[0] == 'class' and _class_origin_at(_br[1], _an.lineno) is not None:
				_ocls = _class_origin_at(_br[1], _an.lineno)[1]
				dynamic_modclass_attrs.setdefault(_ocls, {})[_atgt.attr] = _adkind
				if _atn is not None and _atn in local_classes:
					dynamic_modclass_attr_types.setdefault(_ocls, {})[_atgt.attr] = _atn
			elif _br[0] == 'class' and _br[1] in local_classes:
				local_classes[_br[1]][_atgt.attr] = _adkind
				_direct_attr_assigns.add((_br[1], _atgt.attr))
				_avt = _value_type(_aval, _an.lineno) if _aval is not None else None
				if _avt is not None:
					class_attr_types.setdefault(_br[1], {})[_atgt.attr] = _avt
					class_type_maps.get(_br[1], {}).pop(_atgt.attr, None)
				elif _atn is not None and _atn in local_classes:
					class_type_maps.setdefault(_br[1], {})[_atgt.attr] = _atn
					class_attr_types.get(_br[1], {}).pop(_atgt.attr, None)
				else:
					class_attr_types.get(_br[1], {}).pop(_atgt.attr, None)
					class_type_maps.get(_br[1], {}).pop(_atgt.attr, None)
			elif _br[0] == 'instance' and _br[1] in local_classes:
				dynamic_class_attrs.setdefault(_br[1], {})[_atgt.attr] = _adkind
				_avt = _value_type(_aval, _an.lineno) if _aval is not None else None
				_is_self_attr = not isinstance(_atgt.value, ast.Name) or _fp_class_at(_atgt.value.id, _an.lineno) == _br[1]
				if not _is_self_attr:
					_vasc = _binding_scope_for(_atgt.value.id, _scope_for_line(_an.lineno))
					if _vasc is not None:
						if _avt is not None:
							_vaval = _avt
						elif _atn is not None and _atn in local_classes:
							_vaval = ('instance', _atn)
						else:
							_vaval = None
						var_attr_types.setdefault((_vasc, _atgt.value.id), {}).setdefault(_atgt.attr, []).append((_an.lineno, _vaval))
				elif _avt is not None:
					class_attr_types.setdefault(_br[1], {})[_atgt.attr] = _avt
					dynamic_class_attr_types.get(_br[1], {}).pop(_atgt.attr, None)
					class_type_maps.get(_br[1], {}).pop(_atgt.attr, None)
					_direct_attr_assigns.add((_br[1], _atgt.attr))
				elif _atn is not None and _atn in local_classes:
					dynamic_class_attr_types.setdefault(_br[1], {})[_atgt.attr] = _atn
					class_attr_types.get(_br[1], {}).pop(_atgt.attr, None)
					class_type_maps.get(_br[1], {}).pop(_atgt.attr, None)
					_direct_attr_assigns.add((_br[1], _atgt.attr))
				else:
					class_attr_types.get(_br[1], {}).pop(_atgt.attr, None)
					dynamic_class_attr_types.get(_br[1], {}).pop(_atgt.attr, None)
					class_type_maps.get(_br[1], {}).pop(_atgt.attr, None)
					_direct_attr_assigns.add((_br[1], _atgt.attr))
	for node in tree_assigns:
		if not isinstance(node.value, ast.Call) or not isinstance(node.value.func, ast.Attribute):
			continue
		for tgt, _tv in _assign_pairs(node.targets, node.value):
			if not isinstance(tgt, ast.Name):
				continue
			_isc = _binding_scope_for(tgt.id, _scope_for_line(node.lineno))
			if _isc is None or scope_var_types.get(_isc, {}).get(tgt.id):
				continue
			_ir = _infer_type(node.value)
			if _ir is not None and _ir[0] == 'instance' and _ir[1] in local_classes:
				scope_var_types.setdefault(_isc, {}).setdefault(tgt.id, []).append((node.lineno, _ir[1]))
	_class_alias_seen = set()
	for _ in range(10):
		_alias_changed = False
		for _asc, _aln, _aname, _asrc in builder.alias_assigns:
			if (_aname, _aln) in _class_alias_seen:
				continue
			_asrc_key = _class_key_at(_asrc, _aln)
			if _asrc_key not in local_classes:
				continue
			_class_alias_seen.add((_aname, _aln))
			class_def_lines.setdefault(_aname, [])
			if _aln not in class_def_lines[_aname]:
				class_def_lines[_aname].append(_aln)
			_class_first_line.setdefault(_aname, _aln)
			_adst_key = _class_key_at(_aname, _aln)
			if _adst_key not in local_classes:
				local_classes[_adst_key] = local_classes[_asrc_key]
			_asrc_orig = _class_origin_at(_asrc, _aln)
			if _asrc_orig is not None:
				class_module_origin.setdefault(_aname, []).append((_aln, _asrc_orig))
			_aln_names = builder.scopes[_binding_scope_for(_aname, _asc)]['names'].setdefault(_aname, [])
			_aln_names[:] = [(_l, _k) for _l, _k in _aln_names if not (_l == _aln and _k == 'var')]
			_aln_names.append((_aln, 'class'))
			local_def_lines.setdefault(_aname, []).append(_aln)
			_alias_changed = True
		if not _alias_changed:
			break
	local_class_module_origins = {}
	for _nmc_name, _nmc_defs in name_module_class.items():
		for _nmc_ln, _nmc_origin in _nmc_defs:
			_nmc_key = _class_key_at(_nmc_name, _nmc_ln)
			local_class_module_origins.setdefault(_nmc_key, [])
			if _nmc_origin not in local_class_module_origins[_nmc_key]:
				local_class_module_origins[_nmc_key].append(_nmc_origin)
	if seed_module_bases:
		for _smb_k, _smb_v in seed_module_bases.items():
			local_class_module_origins.setdefault(_smb_k, [])
			for _smb_o in _smb_v:
				if _smb_o not in local_class_module_origins[_smb_k]:
					local_class_module_origins[_smb_k].append(_smb_o)
	for _mcb_key, _mcb_node in _module_class_bases:
		if _mcb_key not in local_classes:
			continue
		_mcb_r = _infer_type(_mcb_node)
		if _mcb_r is None or _mcb_r[0] != 'modclass':
			continue
		_mcb_mems = _python_resolve_module_class_members(buf, _mcb_r[1], _mcb_r[2])
		for _mcb_mk, _mcb_mv in _mcb_mems.items():
			local_classes[_mcb_key].setdefault(_mcb_mk, _mcb_mv)
		local_class_module_origins.setdefault(_mcb_key, []).append((_mcb_r[1], _mcb_r[2]))
	for _lcmo_node in tree_class_defs:
		if _lcmo_node.name not in local_classes:
			continue
		_lcmo_key = _node_class_key(_lcmo_node)
		for _lcmo_base in _lcmo_node.bases:
			if isinstance(_lcmo_base, ast.Name):
				_lcmo_orig = _class_origin_at(_lcmo_base.id, _lcmo_node.lineno)
				if _lcmo_orig is not None:
					local_class_module_origins.setdefault(_lcmo_key, []).append(_lcmo_orig)
	for _ in range(10):
		_lcmo_changed = False
		for _lcmo_cls, _lcmo_bases in class_bases.items():
			for _lcmo_b in _lcmo_bases:
				for _lcmo_o in local_class_module_origins.get(_lcmo_b, []):
					if _lcmo_o not in local_class_module_origins.get(_lcmo_cls, []):
						local_class_module_origins.setdefault(_lcmo_cls, []).append(_lcmo_o)
						_lcmo_changed = True
		if not _lcmo_changed:
			break
	for _ in range(10):
		_aomo_changed = False
		for _asc, _aln, _aname, _asrc in builder.alias_assigns:
			_asrc_key = _class_key_at(_asrc, _aln)
			_adst_key = _class_key_at(_aname, _aln)
			for _ao in local_class_module_origins.get(_asrc_key, []):
				if _ao not in local_class_module_origins.get(_adst_key, []):
					local_class_module_origins.setdefault(_adst_key, []).append(_ao)
					_aomo_changed = True
		if not _aomo_changed:
			break
	_python_merge_class_bases()
	typed_attrs = []
	_ti = 0
	for node in tree_attributes:
		_ti += 1
		if _ti % 400 == 0:
			_ck()
		r = _infer_type(node.value)
		if r is None:
			continue
		if r[0] == 'module':
			_k = _module_attr_kind(r[1], node.attr)
		elif r[0] in ('modclass', 'minstance'):
			_k = None
			if r[0] == 'minstance':
				_k = dynamic_class_attrs.get(r[2], {}).get(node.attr)
			if _k is None and r[0] == 'modclass':
				_k = dynamic_modclass_attrs.get(r[2], {}).get(node.attr)
			if _k is None:
				_k = _python_resolve_module_member_kind(buf, r[1], r[2], node.attr)
		elif r[0] == 'builtin':
			_k = _PYTHON_BUILTIN_MEMBERS.get(r[1], {}).get(node.attr)
		else:
			_k = None
			if r[0] == 'class' and _instance_only_attr(r[1], node.attr):
				continue
			if r[0] in ('instance', 'class'):
				_k = dynamic_class_attrs.get(r[1], {}).get(node.attr)
			if _k is None:
				_k = local_classes.get(r[1], {}).get(node.attr)
		if _k == 'var' and r[0] != 'builtin':
			_kir = _infer_type(node)
			if _kir is not None and (_kir[0] == 'minstance' or (_kir[0] == 'instance' and _kir[1] not in _PYTHON_BUILTIN_MEMBERS)):
				_k = 'instance'
		if _k is not None:
			typed_attrs.append((node.end_lineno, node.end_col_offset - len(node.attr), node.attr, _k))
	_ck()
	var_module_class = {}
	for _vn in tree_assigns:
		_val = _vn.value
		if not isinstance(_val, ast.Call):
			continue
		_fn = _val.func
		_cmod = None
		_ccls = None
		if isinstance(_fn, ast.Attribute) and isinstance(_fn.value, ast.Name):
			_bmod = _base_module_at(_fn.value.id, _vn.lineno)
			if _bmod is not None and _python_resolve_module_members(buf, _bmod).get(_fn.attr) == 'class':
				_cmod = _bmod
				_ccls = _fn.attr
		elif isinstance(_fn, ast.Name):
			_ffm = _line_def_at(from_func_module.get(_fn.id), _vn.lineno)
			if _ffm is not None and _python_resolve_module_members(buf, _ffm[0]).get(_ffm[1]) == 'class':
				_cmod, _ccls = _ffm
			else:
				_nmc = _line_def_at(name_module_class.get(_fn.id), _vn.lineno)
				if _nmc is not None:
					_cmod, _ccls = _nmc
		if _cmod is None:
			_vit = _infer_type(_val)
			if _vit is not None and _vit[0] == 'minstance':
				_cmod, _ccls = _vit[1], _vit[2]
		if _cmod is None:
			continue
		_vsc = _scope_for_line(_vn.lineno)
		for _t in _vn.targets:
			if isinstance(_t, ast.Name):
				var_module_class.setdefault((_binding_scope_for(_t.id, _vsc), _t.id), []).append((_vn.lineno, _cmod, _ccls))
	def _var_modclass_at(name, lineno, col = None):
		sidx = _scope_for_line(lineno) if col is None else _scope_for_pos(lineno, col)
		inner = sidx
		while sidx is not None:
			sc = builder.scopes[sidx]
			if sc.get('kind') == 'class' and sidx != inner:
				sidx = sc['parent']
				continue
			if name in sc['names']:
				best = None
				for _dl, _cm, _cc in var_module_class.get((sidx, name), []):
					if sidx == inner and _dl > lineno:
						continue
					if best is None or _dl > best[0]:
						best = (_dl, _cm, _cc)
				if best is not None:
					return best[1], best[2]
				return None
			sidx = sc['parent']
		return None
	call_kwargs = {}
	for lineno, func_name, kwarg_name, is_name, dotted, _cnode in builder.pending_calls:
		ok, params = _params_for_dotted(dotted, lineno)
		if not ok and dotted is not None and len(dotted) == 2:
			_mc = _var_modclass_at(dotted[0], lineno)
			if _mc is not None:
				found, mp = _python_resolve_module_method(buf, _mc[0], _mc[1], func_name)
				if found:
					ok, params = True, mp
			if not ok:
				_lcls = _var_type_at(dotted[0], lineno)
				if _lcls is not None:
					_lkey = _lcls + '.' + func_name
					if _lkey in local_class_accepts_any:
						ok, params = True, None
					elif _lkey in local_class_method_params:
						ok, params = True, local_class_method_params[_lkey]
					elif _class_origin_at(_lcls, lineno) is not None:
						_lorig = _class_origin_at(_lcls, lineno)
						found, mp = _python_resolve_module_method(buf, _lorig[0], _lorig[1], func_name)
						if found:
							ok, params = True, mp
					if not ok:
						for _lcmo_mod, _lcmo_cls in local_class_module_origins.get(_lcls, []):
							found, mp = _python_resolve_module_method(buf, _lcmo_mod, _lcmo_cls, func_name)
							if found:
								ok, params = True, mp
								break
		if not ok and isinstance(_cnode.func, ast.Attribute) and isinstance(_cnode.func.value, ast.Call) and isinstance(_cnode.func.value.func, ast.Name) and _cnode.func.value.func.id == 'super' and _call_name_kind('super', lineno) is None:
			_super_cls = None
			for _sms, _sme, _smfp, _smcls in method_fp_ranges:
				if _sms <= lineno <= _sme and (_super_cls is None or _sms > _super_cls[0]):
					_super_cls = (_sms, _smcls)
			if _super_cls is not None:
				for _sbase in class_bases.get(_super_cls[1], []):
					_sbkey = _sbase + '.' + func_name
					if _sbkey in local_class_accepts_any:
						ok, params = True, None
						break
					if _sbkey in local_class_method_params:
						ok, params = True, local_class_method_params[_sbkey]
						break
				if not ok:
					for _scmo_mod, _scmo_cls in local_class_module_origins.get(_super_cls[1], []):
						found, mp = _python_resolve_module_method(buf, _scmo_mod, _scmo_cls, func_name)
						if found:
							ok, params = True, mp
							break
		if not ok and isinstance(_cnode.func, ast.Attribute):
			_rcv = _infer_type(_cnode.func.value)
			if _rcv is not None:
				if _rcv[0] in ('modclass', 'minstance'):
					found, mp = _python_resolve_module_method(buf, _rcv[1], _rcv[2], func_name)
					if found:
						ok, params = True, mp
				elif _rcv[0] == 'module':
					_mok, _mp = _lookup_module_callable(_rcv[1], func_name)
					if _mok:
						ok, params = _mok, _mp
				elif _rcv[0] in ('instance', 'class') and not (_rcv[0] == 'class' and _instance_only_attr(_rcv[1], func_name)):
					if local_classes.get(_rcv[1], {}).get(func_name) == 'class':
						_cat = class_attr_types.get(_rcv[1], {}).get(func_name)
						if _cat is None and func_name in local_classes:
							_cat = ('class', func_name)
						if _cat is not None and _cat[0] == 'class' and _cat[1] in local_classes:
							_tkey = _cat[1]
							if _tkey + '.__init__' in local_class_accepts_any:
								ok, params = True, None
							elif _tkey + '.__init__' in local_class_method_params:
								ok, params = True, local_class_method_params[_tkey + '.__init__']
							else:
								ok, params = True, set()
								for _lcmo_mod, _lcmo_cls in local_class_module_origins.get(_tkey, []):
									found, mp = _python_resolve_module_method(buf, _lcmo_mod, _lcmo_cls, '__init__')
									if found:
										ok, params = True, mp
										break
								else:
									_torig = _class_origin_at(_tkey, lineno)
									if _torig is not None:
										found, mp = _python_resolve_module_method(buf, _torig[0], _torig[1], '__init__')
										if found:
											ok, params = True, mp
						elif _cat is not None and _cat[0] == 'modclass':
							found, mp = _python_resolve_module_method(buf, _cat[1], _cat[2], '__init__')
							if found:
								ok, params = True, mp
					_lkey = _rcv[1] + '.' + func_name
					if not ok and _lkey in local_class_accepts_any:
						ok, params = True, None
					elif not ok and _lkey in local_class_method_params:
						ok, params = True, local_class_method_params[_lkey]
					elif not ok and _class_origin_at(_rcv[1], lineno) is not None:
						_rorig = _class_origin_at(_rcv[1], lineno)
						found, mp = _python_resolve_module_method(buf, _rorig[0], _rorig[1], func_name)
						if found:
							ok, params = True, mp
					if not ok:
						for _lcmo_mod, _lcmo_cls in local_class_module_origins.get(_rcv[1], []):
							found, mp = _python_resolve_module_method(buf, _lcmo_mod, _lcmo_cls, func_name)
							if found:
								ok, params = True, mp
								break
		if ok and (params is None or kwarg_name in params):
			call_kwargs.setdefault(lineno, set()).add(kwarg_name)
	for _cdk_ln, _cdk_cls, _cdk_defln, _cdk_arg in builder.class_def_kwargs:
		if _cdk_arg == 'metaclass':
			call_kwargs.setdefault(_cdk_ln, set()).add(_cdk_arg)
			continue
		_cdk_key = _class_key_at(_cdk_cls, _cdk_defln)
		_cdk_ok = False
		_cdk_params = None
		for _cdk_base in class_bases.get(_cdk_key, []):
			_cdk_mk = _cdk_base + '.__init_subclass__'
			if _cdk_mk in local_class_accepts_any:
				_cdk_ok, _cdk_params = True, None
				break
			if _cdk_mk in local_class_method_params:
				_cdk_ok, _cdk_params = True, local_class_method_params[_cdk_mk]
				break
			for _cdk_mod, _cdk_mcls in local_class_module_origins.get(_cdk_base, []):
				found, mp = _python_resolve_module_method(buf, _cdk_mod, _cdk_mcls, '__init_subclass__')
				if found:
					_cdk_ok, _cdk_params = True, mp
					break
			if _cdk_ok:
				break
		if _cdk_ok and (_cdk_params is None or _cdk_arg in _cdk_params):
			call_kwargs.setdefault(_cdk_ln, set()).add(_cdk_arg)
	def _resolve_kind_in(start_idx, name, lineno):
		sidx = start_idx
		inner = sidx
		while sidx is not None:
			sc = builder.scopes[sidx]
			if sc.get('kind') == 'class' and sidx != inner:
				sidx = sc['parent']
				continue
			if name in sc['names']:
				best = None
				latest = None
				for dl, kind in sc['names'][name]:
					if latest is None or dl > latest[0]:
						latest = (dl, kind)
					if sidx == inner and dl > lineno:
						continue
					if best is None or dl > best[0]:
						best = (dl, kind)
				if best is None and latest is not None and _same_block(latest[0], lineno):
					best = latest
				return best[1] if best is not None else None
			sidx = sc['parent']
		return None
	param_default_tags = []
	for fnode in tree_func_defs:
		args = fnode.args
		param_names = set(a.arg for a in list(args.posonlyargs) + list(args.args) + list(args.kwonlyargs))
		if args.vararg:
			param_names.add(args.vararg.arg)
		if args.kwarg:
			param_names.add(args.kwarg.arg)
		defaults = list(args.defaults) + [d for d in args.kw_defaults if d is not None]
		if not param_names or not defaults:
			continue
		fscope = _scope_for_line(fnode.lineno)
		enclosing = builder.scopes[fscope]['parent'] if fscope is not None else None
		if enclosing is None:
			continue
		for dexpr in defaults:
			for nm in ast.walk(dexpr):
				if isinstance(nm, ast.Name) and nm.id in param_names:
					kind = _resolve_kind_in(enclosing, nm.id, fnode.lineno)
					if kind is not None:
						param_default_tags.append((nm.lineno, nm.col_offset, nm.id, kind))
	_ck()
	literal_attrs = []
	for node in tree_attributes:
		val = node.value
		_lat = None
		if isinstance(val, ast.Constant):
			_lat = type(val.value).__name__
		elif isinstance(val, ast.List):
			_lat = 'list'
		elif isinstance(val, ast.Dict):
			_lat = 'dict'
		elif isinstance(val, ast.Tuple):
			_lat = 'tuple'
		elif isinstance(val, ast.Set):
			_lat = 'set'
		elif isinstance(val, ast.JoinedStr):
			_lat = 'str'
		if _lat and node.attr in _PYTHON_BUILTIN_MEMBERS.get(_lat, {}):
			literal_attrs.append((node.end_lineno, node.end_col_offset - len(node.attr), node.attr, _lat))
	_ck()
	instance_name_positions = set()
	_instance_name_cache = {}
	for _inl, _incol, _inname, _instore in list(name_positions) + [(_pl, _pcol, _pname, False) for _pl, _pcol, _pname, _pkind in param_default_tags]:
		_inkey = (_inname, _inl, _incol)
		_inres = _instance_name_cache.get(_inkey)
		if _inres is None:
			_invt = _var_type_at(_inname, _inl, _incol)
			_inres = (_invt is not None and _invt in local_classes and _invt not in _PYTHON_BUILTIN_MEMBERS) or _var_modclass_at(_inname, _inl, _incol) is not None
			_instance_name_cache[_inkey] = _inres
		if _inres:
			instance_name_positions.add((_inl, _incol))
	_ck()
	global_stmt_kind_positions = {}
	def _gs_best(defs):
		best = None
		for _dl, _dv in defs:
			if _dl <= _gsend and (best is None or _dl > best[0]):
				best = (_dl, _dv)
		if best is None:
			for _dl, _dv in defs:
				if best is None or _dl > best[0]:
					best = (_dl, _dv)
		return best[1] if best is not None else None
	for _gsl, _gscol, _gsname, _gsscope in global_stmt_positions:
		if _gsscope is None:
			continue
		_gstgt = _binding_scope_for(_gsname, _gsscope)
		if _gstgt is None:
			continue
		_gsend = builder.scopes[_gsscope]['end']
		_gskind = _gs_best(builder.scopes[_gstgt]['names'].get(_gsname, ()))
		if _gskind is None:
			continue
		if _gskind == 'var':
			_gsvt = _gs_best(scope_var_types.get(_gstgt, {}).get(_gsname, ()))
			if _gsvt is not None and _gsvt in local_classes and _gsvt not in _PYTHON_BUILTIN_MEMBERS:
				_gskind = 'instance'
			elif _gs_best([(_d[0], (_d[1], _d[2])) for _d in var_module_class.get((_gstgt, _gsname), ())]) is not None:
				_gskind = 'instance'
		global_stmt_kind_positions[(_gsl, _gscol)] = _gskind
	_ck()
	_export_func_params = {}
	for _efp_n, _efp_defs in builder.func_params.items():
		_efp_mod = [_d for _d in _efp_defs if (_d[2] if len(_d) > 2 else 0) == 0]
		if _efp_mod:
			_export_func_params[_efp_n] = max(_efp_mod, key = lambda d: d[0])[1]
	_export_func_accepts_any = {}
	for _efa_n, _efa_defs in builder.func_accepts_any.items():
		_efa_mod = [_d for _d in _efa_defs if (_d[2] if len(_d) > 2 else 0) == 0]
		if _efa_mod:
			_export_func_accepts_any[_efa_n] = max(_efa_mod, key = lambda d: d[0])[1]
	_export_class_bases = {_k: _v for _k, _v in class_bases.items() if _k in module_scope_class_keys}
	_export_instance_only = {}
	for _eio_c, _eio_v in _self_assigned_attrs.items():
		if _eio_c not in module_scope_class_keys:
			continue
		_eio_only = set(_eio_v) - _class_body_members.get(_eio_c, set())
		if _eio_only:
			_export_instance_only[_eio_c] = _eio_only
	_export_inherited = {'members': _inherited_members, 'attr_types': _inherited_attr_types, 'method_params': _inherited_method_params}
	return builder.scopes, call_kwargs, builder.module_alias_defs, local_classes, module_literals, scope_var_types, literal_attrs, def_name_positions, typed_attrs, param_default_tags, builder.kwarg_positions, import_dotted_lines, import_orig_name_tags, class_module_origin, local_class_method_params, local_class_accepts_any, name_positions, local_class_module_origins, from_func_module, class_type_maps, class_attr_types, _export_func_params, _export_func_accepts_any, _export_class_bases, _export_inherited, module_scope_class_keys, _export_instance_only, instance_name_positions, global_stmt_kind_positions
def _python_scan_names(buf, text, gen = None):
	result = _python_build_scopes(buf, text, gen)
	if result is not None:
		scopes, call_kwargs, module_aliases, local_classes, module_literals, scope_var_types, literal_attrs, def_names, typed_attrs, param_default_tags, kwarg_positions, import_dotted_lines, import_orig_name_tags, class_module_origin, local_class_method_params, local_class_accepts_any, name_positions, _lcmo, _ffm, _ctm, _cat, _efp, _efa, _ecb, _ein, _emck, _eio, instance_name_positions, global_stmt_kind_positions = result
		buf._python_scopes = scopes
		buf._python_call_kwargs = call_kwargs
		buf._python_module_literals = module_literals
		buf._python_literal_attrs = literal_attrs
		buf._python_name_positions = name_positions
		buf._python_def_names = def_names
		buf._python_typed_attrs = typed_attrs
		buf._python_param_default_tags = param_default_tags
		buf._python_kwarg_positions = kwarg_positions
		buf._python_import_dotted_lines = import_dotted_lines
		buf._python_import_orig_name_tags = import_orig_name_tags
		buf._python_instance_name_positions = instance_name_positions
		buf._python_global_stmt_kind_positions = global_stmt_kind_positions
		buf._main_queue.put(lambda: buf.ha('python') if buf.hmode == 'python' else None)
def _python_scan_start(buf):
	buf._python_scan_after_id = None
	if buf._python_names_scan_thread is not None and buf._python_names_scan_thread.is_alive():
		buf._python_scan_after_id = buf._own_type.after(10, lambda: _python_scan_start(buf))
		return
	gen = buf._python_edit_generation[0]
	text = buf.type_.get('1.0', 'end')
	def _get_and_scan():
		try:
			_python_scan_names(buf, text, gen)
		except _PythonScanCancelled:
			pass
		except Exception:
			pass
	buf._python_names_scan_thread = threading.Thread(target = _get_and_scan, daemon = True)
	buf._python_names_scan_thread.start()
def _python_resolve_module_func_params(buf, name):
	if name in buf._python_module_func_params_cache:
		return buf._python_module_func_params_cache[name]
	spec = _python_find_spec_cached(buf, name)
	src_path = _python_module_src_path(spec, name)
	if src_path is None:
		buf._python_module_func_params_cache[name] = {}
		return {}
	try:
		with open(src_path, 'r', encoding = 'utf-8') as f:
			src = f.read()
		with warnings.catch_warnings():
			warnings.simplefilter('ignore')
			mod_ast = ast.parse(src)
	except Exception:
		buf._python_module_func_params_cache[name] = {}
		return {}
	out = {}
	_imp = {}
	_stars = []
	for node in mod_ast.body:
		if isinstance(node, ast.ImportFrom):
			_imod = _python_relative_import_target(name, node.level, node.module, bool(getattr(spec, 'submodule_search_locations', None))) if (node.module or node.level) else name
			if _imod:
				for alias in node.names:
					if alias.name != '*':
						_imp[alias.asname or alias.name] = (_imod, alias.name)
					elif _imod != name:
						_stars.append(_imod)
			continue
		if isinstance(node, ast.Import):
			for alias in node.names:
				_imp[alias.asname or alias.name.split('.')[0]] = (alias.name, None)
			continue
		if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
			params = set(a.arg for a in list(node.args.args) + list(node.args.kwonlyargs))
			if node.args.kwarg:
				params = None
			out[node.name] = params
		elif isinstance(node, ast.ClassDef):
			base_refs = []
			for b in node.bases:
				if isinstance(b, ast.Name):
					base_refs.append(b.id)
				elif isinstance(b, ast.Attribute):
					_parts = []
					_cur = b
					while isinstance(_cur, ast.Attribute):
						_parts.append(_cur.attr)
						_cur = _cur.value
					if isinstance(_cur, ast.Name):
						_parts.append(_cur.id)
						_parts.reverse()
						base_refs.append('.'.join(_parts))
			out['@bases:' + node.name] = base_refs
			for sub in node.body:
				if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)):
					margs = list(sub.args.posonlyargs) + list(sub.args.args) + list(sub.args.kwonlyargs)
					mparams = (set(a.arg for a in margs[1:]) - set(a.arg for a in sub.args.posonlyargs)) | set(a.arg for a in sub.args.kwonlyargs)
					if sub.args.kwarg:
						mparams = None
					out[node.name + '.' + sub.name] = mparams
					if sub.name == '__init__':
						out[node.name] = None if mparams is None else set(mparams)
			for sub in node.body:
				if isinstance(sub, ast.Assign) and isinstance(sub.value, ast.Name):
					_src_key = node.name + '.' + sub.value.id
					if _src_key in out:
						for _at in sub.targets:
							if isinstance(_at, ast.Name):
								out[node.name + '.' + _at.id] = out[_src_key]
	out['@imports'] = _imp
	buf._python_module_func_params_cache[name] = out
	for _smod in _stars:
		for _sk, _sv in _python_resolve_module_func_params(buf, _smod).items():
			if _sk != '@imports' and _sk not in out:
				out[_sk] = _sv
	return out
def _python_resolve_module_method(buf, mod, class_name, method, seen = None):
	if seen is None:
		seen = set()
	key = (mod, class_name)
	if key in seen:
		return False, None
	seen.add(key)
	fp = _python_resolve_module_func_params(buf, mod)
	if f'{class_name}.{method}' in fp:
		return True, fp[f'{class_name}.{method}']
	imports = fp.get('@imports', {})
	if '@bases:' + class_name not in fp and class_name in imports and imports[class_name][1] is not None:
		return _python_resolve_module_method(buf, imports[class_name][0], imports[class_name][1], method, seen)
	for base in fp.get('@bases:' + class_name, []):
		bparts = base.split('.')
		if len(bparts) == 1:
			if '@bases:' + base in fp:
				ok, params = _python_resolve_module_method(buf, mod, base, method, seen)
				if ok:
					return True, params
			elif base in imports:
				bmod, bname = imports[base]
				if bname is not None:
					ok, params = _python_resolve_module_method(buf, bmod, bname, method, seen)
					if ok:
						return True, params
		else:
			broot = bparts[0]
			if broot in imports:
				bmod = imports[broot][0]
				full_mod = '.'.join([bmod] + bparts[1:-1]) if len(bparts) > 2 else bmod
				ok, params = _python_resolve_module_method(buf, full_mod, bparts[-1], method, seen)
				if ok:
					return True, params
	return False, None
def _python_resolve_dotted_module(buf, dotted):
	parts = dotted.split('.')
	cur = parts[0]
	if _python_find_spec_cached(buf, cur) is None:
		return None
	for _p in parts[1:]:
		_mm = _python_resolve_module_members(buf, cur)
		_tgt = _mm.get('@modtarget:' + _p)
		if _tgt is not None:
			cur = _tgt
			continue
		_sub = cur + '.' + _p
		if _mm.get(_p) == 'module' or _python_find_spec_cached(buf, _sub) is not None:
			cur = _sub
			continue
		return None
	return cur
