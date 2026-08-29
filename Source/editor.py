import os
import platform
import subprocess
import shutil
import codecs
import smtplib
import keyword
import re
import threading
import queue
import ast
import warnings
import io
import math as mathmod
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import easytk
import state
from encrypter import encryptdecrypt
from init import homedir, monospace
from buffer import Buffer, DEBOUNCE_TIME
from python_scope_build import _PYTHON_BUILTIN_MEMBERS, _PYTHON_BUILTIN_NAMES
import python_scope_build
import dialogs
import pycode
import speech
import terminal
import utils
import window
try:
	import tika
	from tika import parser
except Exception:
	pass
try:
	import pdfplumber
except Exception:
	pass
try:
	from tklinenums import TkLineNumbers
except Exception:
	pass
try:
	from watchdog.observers import Observer
	from watchdog.events import FileSystemEventHandler
except Exception:
	pass
class Editor(Buffer):
	for code in state.editor_init_functions:
		try:
			exec(code, vars(state), locals())
		except Exception as error:
			error = str(error)
			state.root.error('Error', f'Error in editor init functions:\n{error}')
	class FileChangeHandler(FileSystemEventHandler):
		def __init__(self, outer):
			self.outer = outer
			super().__init__()
		def _handle(self, path):
			if os.path.abspath(path) != self.outer.title:
				return
			if self.outer.file_editing_own:
				return
			if self.outer._file_watch_prompt_pending:
				return
			self.outer._file_watch_prompt_pending = True
			self.outer._main_queue.put(self.outer._file_watch_prompt)
		def on_modified(self, event):
			if event.is_directory:
				return
			self._handle(event.src_path)
		def on_created(self, event):
			if event.is_directory:
				return
			self._handle(event.src_path)
		def on_moved(self, event):
			if event.is_directory:
				return
			self._handle(event.dest_path)
	_SHARED_STATE_ATTRS = frozenset(('unsaved', 'unsavedtext', 'hmode', 'title', 'wanttitle', 'file_editing_own', '_file_watch_prompt_pending', 'imageloaded', 'observer', '_python_scopes', '_python_call_kwargs', '_python_module_literals', '_python_literal_attrs', '_python_name_positions', '_python_def_names', '_python_typed_attrs', '_python_param_default_tags', '_python_kwarg_positions', '_python_import_dotted_lines', '_python_import_orig_name_tags', '_python_instance_name_positions', '_python_global_stmt_kind_positions', '_python_names_scan_thread', '_python_scan_after_id', '_python_edit_generation', '_python_module_spec_cache', '_python_module_members_cache', '_python_module_class_members_cache', '_python_module_func_params_cache', '_ha_running', '_ha_pending'))
	_TK_INTERNAL_ATTRS = frozenset(('_w', '_name', 'children', 'master', 'tk', '_tclCommands', 'widgetName', '_last_child_ids'))
	_PER_PANE_ATTRS = frozenset(('root', 'fileinfo', 'filename', 'filetype', 'filesize', 'mf', 'sf', 'lf', 'latexbold', 'latexitalic', 'latexunderline', 'latexsubscript', 'latexsuperscript', 'latexnumberlist', 'latexbulletlist', 'latexsectionvar', 'latexsection', 'latexparagraph', 'latexequation', 'latexcharvar', 'latexmath', 'ef', 'tabs', 'scrlbr', '_own_type', 'ln', 'active', 'imageload', 'm', 'view_master', 'view_children', '_selectionpoint', 'type_top', 'type_bottom', '_prev_visible_region', '_ha_after_id', '_filesize_after_id', '_unsaved_after_id', '_main_queue', '_hapyshell_running', '_pyshell_last_scan_key', '_pyshell_cached_scope_result', '_pyshell_session_names', '_pyshell_session_types', '_pyshell_session_classes', '_pyshell_session_aliases', '_pyshell_session_origins', '_pyshell_session_method_params', '_pyshell_session_accepts_any', '_pyshell_session_module_bases', '_pyshell_session_func_origins', '_pyshell_session_attr_types', '_pyshell_session_class_attr_types', '_pyshell_session_func_params', '_pyshell_session_func_accepts_any', '_pyshell_session_class_bases', '_pyshell_session_inherited', '_pyshell_session_instance_only', 'shellcmd', 'loginframe', 'email', 'password', 'server', 'port', 'entryframe', 'recipiententry', 'subjectentry', 'buttonframe', 'attachmentslist', 'attachmentslistwidget', 'emailtextbox', '_email_logged_in'))
	def __setattr__(self, name, value):
		if name in Editor._SHARED_STATE_ATTRS and self.__dict__.get('view_master') is not None:
			setattr(self.__dict__['view_master'], name, value)
		else:
			object.__setattr__(self, name, value)
	def __getattr__(self, name):
		if name in Editor._SHARED_STATE_ATTRS:
			master = self.__dict__.get('view_master')
			if master is not None:
				return getattr(master, name)
		raise AttributeError(name)
	@property
	def mainwidget(self):
		if self.view_master is None:
			for child in self.view_children:
				if child.active:
					return child._own_type
		return self._own_type
	@mainwidget.setter
	def mainwidget(self, value):
		pass
	@property
	def type_(self):
		if self.view_master is None:
			for child in self.view_children:
				if child.active:
					return child._own_type
		return self._own_type
	@type_.setter
	def type_(self, value):
		self._own_type = value
	def _group_members(self):
		resolved = self.view_master if self.view_master else self
		return [resolved] + list(resolved.view_children)
	def _focused_pane(self):
		for member in self._group_members():
			if member.active:
				return member
		return self
	@property
	def selectionpoint(self):
		return self._focused_pane()._selectionpoint
	@selectionpoint.setter
	def selectionpoint(self, value):
		self._focused_pane()._selectionpoint = value
	def _make_peer_type(self, master):
		name = 'peertype%d' % id(self)
		master._own_type.peer_create(str(self.mf) + '.' + name)
		peer = easytk.ttk.Text.__new__(easytk.ttk.Text)
		peer.widgetName = 'text'
		peer._tclCommands = None
		peer._setup(self.mf, {'name': name})
		for option in master._own_type.configure():
			if option in ('xscrollcommand', 'yscrollcommand'):
				continue
			try:
				peer.configure(**{option: master._own_type.cget(option)})
			except Exception:
				pass
		return peer
	def _wire_type(self):
		self.scrlbr.config(command = self.type_.yview)
		self.type_.focus_set()
		self.ln = TkLineNumbers(self.mf, self.type_, justify = 'center')
		self.type_.config(yscrollcommand = lambda *args: [self.scrlbr.set(*args), self.ln.redraw()])
		self.ln.pack(side = 'left', fill = 'y')
		self.type_.pack(side = 'right', fill = 'both', expand = True)
		self._bind_type_events()
		self._bind_focus_recursive(self._own_type)
	def _bind_focus_recursive(self, widget, skip_widgets = ()):
		if widget in skip_widgets:
			return
		widget.bind('<FocusIn>', lambda event, buffer = self: window.setactive(state.all_buffers.index(buffer)))
		for child in widget.winfo_children():
			self._bind_focus_recursive(child, skip_widgets)
	def _bind_type_events(self):
		self.type_.bind('<Control-a>', lambda event: self.selall() or 'break')
		self.type_.bind('<Control-n>', lambda event: self.nw() or 'break')
		self.type_.bind('<Control-o>', lambda event: self.llld() or 'break')
		self.type_.bind('<Control-c>', lambda event: self.cp() or 'break')
		self.type_.bind('<Control-v>', lambda event: self.pst() or 'break')
		self.type_.bind('<Control-x>', lambda event: self.cut() or 'break')
		self.type_.bind('<KeyRelease>', lambda event: self.keypress())
		self.type_.bind('<BackSpace>', lambda event: utils.show('delete text'))
		self.type_.bind('<Delete>', lambda event: utils.show('delete text'))
		self.type_.bind('<Return>', lambda event: self.indent())
		self.type_.bind('<Alt-l>', lambda event: self.gl() or 'break')
		self.type_.bind('<Control-p>', lambda event: self.ptf() or 'break')
		self.type_.bind('<Control-P>', lambda event: self.ptb() or 'break')
		self.type_.bind('<Control-f>', lambda event: self.f() or 'break')
		self.type_.bind('<Control-F>', lambda event: self.fr() or 'break')
		self.type_.bind('<Control-h>', lambda event: self.fr() or 'break')
		self.type_.bind('<Control-z>', lambda event: self.undo() or 'break')
		self.type_.bind('<Control-Z>', lambda event: self.redo() or 'break')
		self.type_.bind('<Control-s>', lambda event: self.sssv() or 'break')
		self.type_.bind('<Control-S>', lambda event: self.ssv() or 'break')
		self.type_.bind('<F5>', lambda event: self.f5() or 'break')
		self.type_.bind('<Control-space>', lambda event: self.toggleselpoint() or 'break')
		self.type_.bind('<KeyPress>', self.selkeypress)
	def selkeypress(self, event):
		if not self.selectionpoint:
			return
		if event.keysym in ('BackSpace', 'Delete', 'Return', 'Tab') or (event.char and ord(event.char[0]) >= 32):
			self.removeselpoint()
		else:
			self.type_.after_idle(self.selupdate)
	def _sync_chrome(self):
		master = self.view_master
		if master is None:
			return
		self.fileinfoconfig(filename = master.infos['filename'].cget('text'), filesaved = master.infos['filesaved'].cget('text'), filetype = master.infos['filetype'].cget('text'), filesize = master.infos['filesize'].cget('text'))
		self.tabs.tab(self.sf, state = master.tabs.tab(master.sf, option = 'state'))
		self.tabs.tab(self.ef, state = master.tabs.tab(master.ef, option = 'state'))
		if master.hmode == 'latex':
			self.lfouter.pack(padx = 10, pady = 10, side = 'top', fill = 'x', before = self.fileinfo)
		else:
			self.lfouter.pack_forget()
		if master.imageloaded:
			self.type_.pack_forget()
			self.ln.pack_forget()
			self.tabs.pack_forget()
		else:
			self.ln.pack(side = 'left', fill = 'y', anchor = 'n')
			self.type_.pack(fill = 'both', expand = True, anchor = 'n')
			self.tabs.pack(padx = 10, pady = 10, fill = 'both', expand = True)
	def _cancel_type_after_ids(self):
		for name in ('_main_poll_after_id', '_ha_after_id', '_filesize_after_id', '_setundo_after_id', '_unsaved_after_id', '_python_scan_after_id', '_find_apply_after_id'):
			after_id = getattr(self, name, None)
			if after_id is not None:
				try:
					self._own_type.after_cancel(after_id)
				except Exception:
					pass
				setattr(self, name, None)
		if self._ha_apply_after_id is not None:
			try:
				state.root.after_cancel(self._ha_apply_after_id)
			except Exception:
				pass
			self._ha_apply_after_id = None
	def _cancel_all_after_ids(self):
		self._cancel_type_after_ids()
		for name, widget in (('_type_setview_after_id', self.mf), ('_do_backup_after_id', self.mf), ('_email_login_poll_after_id', self.ef), ('_shell_setview_after_id', self.sf)):
			after_id = getattr(self, name, None)
			if after_id is not None:
				try:
					widget.after_cancel(after_id)
				except Exception:
					pass
				setattr(self, name, None)
	def _connect_to(self, master):
		old_type = self.type_
		old_ln = self.ln
		self._cancel_type_after_ids()
		self.type_ = self._make_peer_type(master)
		self.mainwidget = self.type_
		self._wire_type()
		old_ln.destroy()
		old_type.destroy()
		for name in Editor._SHARED_STATE_ATTRS:
			self.__dict__.pop(name, None)
		self.view_master = master
		master.view_children.append(self)
		self.m = master.m
		self._sync_chrome()
		self._main_poll()
		pycode.pcrun(state.pycode_keybindings_cdt)
	def _disconnect(self):
		if self.view_children:
			window._promote_new_master(self)
			self.view_children = []
			old_type = self.type_
			old_ln = self.ln
			self._cancel_type_after_ids()
			self.type_ = state.root.textbox(master = self.mf, font = (state.defs[2], 12), wrap = 'word', undo = True, autoseparators = True)
			self.mainwidget = self.type_
			self._wire_type()
			old_ln.destroy()
			old_type.destroy()
			self.unsaved = False
			self.unsavedtext = ''
			self.hmode = 'normal'
			self.title = ''
			self._sync_wanttitle()
			self.imageloaded = False
			self.file_editing_own = False
			self._file_watch_prompt_pending = False
			self.observer = None
			self.init_hl_tags()
			self.init_plugin_tags()
			self.type_.edit_reset()
			python_scope_build._python_reset_scan_state(self)
			self.resetfileinfo()
			self.tabs.tab(self.sf, state = 'hidden')
			self.tabs.tab(self.ef, state = 'hidden')
			self.lfouter.pack_forget()
			self._main_poll()
			pycode.pcrun(state.pycode_keybindings_cdt)
		if self.view_master is not None:
			master = self.view_master
			if self in master.view_children:
				master.view_children.remove(self)
			old_type = self.type_
			old_ln = self.ln
			self._cancel_type_after_ids()
			self.type_ = state.root.textbox(master = self.mf, font = (state.defs[2], 12), wrap = 'word', undo = True, autoseparators = True)
			self.mainwidget = self.type_
			self._wire_type()
			old_ln.destroy()
			old_type.destroy()
			self._main_poll()
			self.view_master = None
			self.unsaved = False
			self.unsavedtext = ''
			self.hmode = 'normal'
			self.title = ''
			self._sync_wanttitle()
			self.imageloaded = False
			self.file_editing_own = False
			self._file_watch_prompt_pending = False
			self.observer = None
			self._python_scopes = [{'start': 1, 'end': 1, 'parent': None, 'names': {}}]
			self._python_call_kwargs = {}
			self._python_module_literals = []
			self._python_literal_attrs = []
			self._python_name_positions = []
			self._python_def_names = []
			self._python_typed_attrs = []
			self._python_param_default_tags = []
			self._python_kwarg_positions = []
			self._python_import_dotted_lines = []
			self._python_import_orig_name_tags = []
			self._python_instance_name_positions = set()
			self._python_global_stmt_kind_positions = {}
			self._python_names_scan_thread = None
			self._python_scan_after_id = None
			self._python_edit_generation = [0]
			self._python_module_spec_cache = {}
			self._python_module_members_cache = {}
			self._python_module_class_members_cache = {}
			self._python_module_func_params_cache = {}
			self._ha_running = [False]
			self._ha_pending = [None]
			self.m = state.root.menu()
			for label, menu in state.all_editor_menus.items():
				self.m.add_cascade(label = label, menu = menu)
			self.init_hl_tags()
			self.init_plugin_tags()
			self.type_.edit_reset()
			python_scope_build._python_reset_scan_state(self)
			self.resetfileinfo()
			self.tabs.tab(self.sf, state = 'hidden')
			self.tabs.tab(self.ef, state = 'hidden')
			self.lfouter.pack_forget()
			pycode.pcrun(state.pycode_keybindings_cdt)
	def _detach_before_close(self):
		if self.view_children:
			window._promote_new_master(self)
			self.view_children = []
		if self.view_master is not None:
			master = self.view_master
			if self in master.view_children:
				master.view_children.remove(self)
	def _smart_open(self, path):
		abspath = os.path.abspath(path)
		resolved = self.view_master if self.view_master else self
		if resolved.title == abspath:
			return
		match = window.find_open_editor(abspath)
		self._disconnect()
		if match is not None and match is not self:
			self._connect_to(match)
		else:
			self.ld(path)
	def __init__(self, master, file = None, view_master = None, *args, **kwargs):
		super().__init__(master, *args, **kwargs)
		self.view_master = view_master
		self.view_children = []
		self.fileinfoconfig(filename = 'Untitled', filetype = 'Plain Text (*.*)', filesize = '0 bytes', filesaved = 'Untitled File')
		self.tabs = state.root.tabs(master = self)
		self.mf = state.root.frame(master = self.tabs)
		self.sf = state.root.frame(master = self.tabs)
		self.ef = state.root.frame(master = self.tabs)
		self.lfouter = state.root.frame(master = self)
		self.lfcanvas = easytk.ttk.Canvas(self.lfouter, highlightthickness = 0)
		self.lfscroll = state.root.scroll(master = self.lfouter, orient = 'horizontal', command = self.lfcanvas.xview)
		self.lfcanvas.configure(xscrollcommand = self.lfscroll.set)
		self.lfcanvas.pack(side = 'top', fill = 'x')
		self.lfscroll.pack(side = 'top', fill = 'x')
		self.lf = state.root.frame(master = self.lfcanvas)
		self.lfcanvaswindow = self.lfcanvas.create_window((0, 0), window = self.lf, anchor = 'nw')
		self.lf.bind('<Configure>', lambda event: self.lfcanvas.configure(scrollregion = self.lfcanvas.bbox('all'), height = self.lf.winfo_reqheight()))
		state.root.text(master = self.lf, text = 'LaTeX:').grid(column = 0, row = 0, padx = 10, pady = 10)
		self.latexbold = state.root.button(master = self.lf, text = 'Bold', command = self.boldlatex)
		self.latexbold.grid(column = 1, row = 0, padx = 10, pady = 10)
		self.latexitalic = state.root.button(master = self.lf, text = 'Italic', command = self.italiclatex)
		self.latexitalic.grid(column = 2, row = 0, padx = 10, pady = 10)
		self.latexunderline = state.root.button(master = self.lf, text = 'Underline', command = self.underlinelatex)
		self.latexunderline.grid(column = 3, row = 0, padx = 10, pady = 10)
		self.latexsubscript = state.root.button(master = self.lf, text = 'Subscript', command = self.subscriptlatex)
		self.latexsubscript.grid(column = 4, row = 0, padx = 10, pady = 10)
		self.latexsuperscript = state.root.button(master = self.lf, text = 'Superscript', command = self.superscriptlatex)
		self.latexsuperscript.grid(column = 5, row = 0, padx = 10, pady = 10)
		self.latexnumberlist = state.root.button(master = self.lf, text = 'Numbered List', command = self.numberlistlatex)
		self.latexnumberlist.grid(column = 6, row = 0, padx = 10, pady = 10)
		self.latexbulletlist = state.root.button(master = self.lf, text = 'Bullet List', command = self.bulletlistlatex)
		self.latexbulletlist.grid(column = 7, row = 0, padx = 10, pady = 10)
		self.latexsectionvar = state.root.stringvar(master = self.lf)
		self.latexsection = state.root.dropdown(stringvar = self.latexsectionvar, showdefault = 'Section', options = ['Section', 'Subsection', 'Subsubsection'], master = self.lf, command = self.sectionlatex)
		self.latexsection.grid(column = 8, row = 0, padx = 10, pady = 10)
		self.latexparagraph = state.root.button(master = self.lf, text = 'Paragraph', command = self.paragraphlatex)
		self.latexparagraph.grid(column = 9, row = 0, padx = 10, pady = 10)
		self.latexequation = state.root.button(master = self.lf, text = 'Equation', command = self.equationlatex)
		self.latexequation.grid(column = 10, row = 0, padx = 10, pady = 10)
		self.latexcharvar = state.root.stringvar()
		self.latexmath = state.root.dropdown(master = self.lf, stringvar = self.latexcharvar, showdefault = 'Multiplication', options = ['Multiplication', 'Division', 'Less or equal', 'More or equal', 'Not equal', 'Infinity', 'Summation', 'Integral', 'Pi', 'Theta', 'Alpha Lower', 'Alpha Upper', 'Inline Math'], command = self.mathlatex)
		self.latexmath.grid(column = 11, row = 0, padx = 10, pady = 10)
		self.tabs.add(self.mf, text = 'Editor')
		self.tabs.add(self.sf, text = 'Python Shell', state = 'hidden')
		self.tabs.add(self.ef, text = 'Email', state = 'hidden')
		self.tabs.pack(fill = 'both', expand = True)
		self.scrlbr = state.root.scroll(master = self.mf)
		self.scrlbr.pack(side = 'right', fill = 'y')
		if view_master is None:
			self.type_ = state.root.textbox(master = self.mf, font = (state.defs[2], 12), wrap = 'word', undo = True, autoseparators = True)
		else:
			self.type_ = self._make_peer_type(view_master)
		self.undoset = False
		self.type_.bind('<<Modified>>', lambda event: [setattr(self, 'undoset', False), self.type_.edit_modified(False)])
		self.mainwidget = self.type_
		self._wire_type()
		self.type_top = '1.0'
		self.type_bottom = 'end'
		self._ha_after_id = None
		self._ha_apply_after_id = None
		self._find_apply_after_id = None
		self._filesize_after_id = None
		self._setundo_after_id = None
		self._unsaved_after_id = None
		self._prev_visible_region = None
		self._main_poll_after_id = None
		self._type_setview_after_id = None
		self._email_login_poll_after_id = None
		self._shell_setview_after_id = None
		self._do_backup_after_id = None
		self._main_queue = queue.Queue()
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
		self._selectionpoint = None
		if view_master is None:
			self.unsaved = False
			self.unsavedtext = ''
			self.hmode = 'normal'
			self.title = ''
			self.setwanttitle('Untitled')
			self.imageloaded = False
			self.file_editing_own = False
			self._file_watch_prompt_pending = False
			self._python_scopes = [{'start': 1, 'end': 1, 'parent': None, 'names': {}}]
			self._python_call_kwargs = {}
			self._python_module_literals = []
			self._python_literal_attrs = []
			self._python_name_positions = []
			self._python_def_names = []
			self._python_typed_attrs = []
			self._python_param_default_tags = []
			self._python_kwarg_positions = []
			self._python_import_dotted_lines = []
			self._python_import_orig_name_tags = []
			self._python_instance_name_positions = set()
			self._python_global_stmt_kind_positions = {}
			self._python_names_scan_thread = None
			self._python_scan_after_id = None
			self._python_edit_generation = [0]
			self._python_module_spec_cache = {}
			self._python_module_members_cache = {}
			self._python_module_class_members_cache = {}
			self._python_module_func_params_cache = {}
			self._ha_running = [False]
			self._ha_pending = [None]
			self.m = state.root.menu()
			for label, menu in state.all_editor_menus.items():
				self.m.add_cascade(label = label, menu = menu)
		else:
			self.m = view_master.m
			view_master.view_children.append(self)
		self.shellpy()
		self.init_pythonshell_hl_tags()
		if view_master is None:
			self.init_hl_tags()
			self.init_plugin_tags()
			self.type_.edit_reset()
			python_scope_build._python_reset_scan_state(self)
		self.type_setview()
		self._main_poll()
		if view_master is None:
			self.do_backup()
		self._email_logged_in = False
		self._email_login_setup()
		self._email_login_poll()
		if view_master is None:
			if file:
				self.ld(file)
		else:
			self._sync_chrome()
		self._bind_focus_recursive(self, (self._own_type,) + tuple(self.ef.winfo_children()) + ((self.imageload,) if getattr(self, 'imageload', None) else ()))
		for code in state.editor_init_code:
			try:
				exec(code, vars(state), locals())
			except Exception as error:
				error = str(error)
				state.root.error('Error', f'Error in editor init code:\n{error}')
	def close(self):
		if self._file_watch_prompt_pending:
			utils.show('select \'Discard Changes & Reload\' or \'Ignore\' external changes before closing the editor')
			return False
		is_last_reference = self.view_master is None and not self.view_children
		answer = state.root.ask('Warning', 'Do you want to save file before closing?', options = ('yes', 'no', 'cancel')) if (self.unsaved and is_last_reference) else False
		if answer != None:
			if answer:
				if not self.saveforclose():
					return False
			self._detach_before_close()
			return True
		return False
	def _file_watch_prompt(self):
		answer = state.root.warning('Warning', f'The file "{self.title}" has changed on disk. Should PyNotes discard unsaved changes and reload the file, or overwrite the file on next save?', buttons = ['Ignore', 'Discard Changes & Reload'])
		self._file_watch_prompt_pending = False
		if answer == 'Discard Changes & Reload':
			self.ld(self.title)
	def setselpoint(self, index = None):
		if index is None:
			index = self.type_.index('insert')
		self.selectionpoint = index
		utils.show(f'selection point set at {self.selectionpoint}')
	def removeselpoint(self):
		if self.selectionpoint:
			self.selectionpoint = None
			utils.show('removed selection point')
		else:
			utils.show('no selection point set')
	def toggleselpoint(self):
		if self.selectionpoint:
			self.removeselpoint()
		else:
			self.setselpoint()
	def lld(self):
		if self._file_watch_prompt_pending:
			utils.show('select \'Discard Changes & Reload\' or \'Ignore\' external changes before loading another file')
			return
		fn = dialogs.openfileget((('All Files', '*'), ('Python Files', '*.py'), ('Text Files', '*.txt'), ('LaTeX Files', '*.tex'), ('PNG Images', '*.png'), ('PDF Files', '*.pdf'), ('ePub Files', '*.epub')))
		pycode.pcrunhook('before', 'open-file-current-editor', fn if fn else None)
		if fn:
			utils.show('open file')
			self._smart_open(fn)
			pycode.pcrunhook('after', 'open-file-current-editor', fn)
	def ssssv(self, nm):
		if self.view_master:
			return self.view_master.ssssv(nm)
		if self._file_watch_prompt_pending:
			utils.show('select \'Ignore\' external changes before saving file')
			return False
		if not nm == '':
			return self.sv(nm)
		self.clt(nm)
		return True
	def _sync_wanttitle(self):
		self.setwanttitle(os.path.basename(self.title) + (' *' if self.unsaved else '') if self.title else 'Untitled')
	def clt(self, nt):
		if self.view_master:
			return self.view_master.clt(nt)
		if self is state.active:
			state.pcsettitle = False
		try:
			self.observer.stop()
			self.observer.join()
		except Exception:
			pass
		try:
			if not nt == '':
				self.fileinfoconfig(filename = os.path.basename(nt), filesaved = 'Saved File')
				self.title = os.path.abspath(nt)
			else:
				self.fileinfoconfig(filename = 'Untitled', filesaved = 'Untitled File')
				self.title = ''
			self.unsaved = False
			self._sync_wanttitle()
			for child in self.view_children:
				child.fileinfoconfig(filename = self.infos['filename'].cget('text'), filesaved = self.infos['filesaved'].cget('text'))
		except Exception:
			pass
		else:
			self.file_editing_own = False
			if nt == '':
				return
			self.observer = Observer()
			self.observer.schedule(self.FileChangeHandler(self), os.path.dirname(self.title), recursive = False)
			self.observer.start()
	def sssv(self):
		if self.view_master:
			return self.view_master.sssv()
		if self._file_watch_prompt_pending:
			utils.show('select \'Ignore\' external changes before saving file')
			return
		if not self.title == '':
			pycode.pcrunhook('before', 'save-file')
			self.ssssv(self.title)
			pycode.pcrunhook('after', 'save-file')
		else:
			self.ssv()
	def saveforclose(self):
		if self.view_master:
			return self.view_master.saveforclose()
		if not self.title == '':
			return self.ssssv(self.title)
		else:
			if self.ssv() == False:
				return False
			else:
				return True
	def ld(self, nm):
		if os.path.isdir(nm):
			state.root.error('Error', f'"{nm}" is a directory.')
			return
		if self._file_watch_prompt_pending:
			utils.show('select \'Discard Changes & Reload\' or \'Ignore\' external changes before loading another file')
			return
		if not nm == '':
			self._disconnect()
			try:
				self.imageload.pack_forget()
				self.imageloaded = False
				self.mainwidget = self.type_
			except Exception:
				pass
			else:
				self.hmode = 'normal'
				self.ln.pack(side = 'left', fill = 'y', anchor = 'n')
				self.type_.pack(fill = 'both', expand = True, anchor = 'n')
				self.tabs.pack(padx = 10, pady = 10, fill = 'both', expand = True)
			self.type_.delete('1.0', 'end')
			if os.path.dirname(nm):
				try:
					os.chdir(os.path.dirname(nm))
				except Exception:
					state.root.error('Error', f'The directory \'{os.path.dirname(nm)}\' does not exist.')
					return
				else:
					nm = os.path.basename(nm)
					self.type_.edit_reset()
					python_scope_build._python_reset_scan_state(self)
			if not os.path.exists(nm):
				open(nm, 'w', encoding = 'utf-8')
			try:
				file = open(nm, 'r', encoding = 'utf-8')
				content = file.read()
				self.type_.delete('1.0', 'end')
				self.type_.insert('end', content)
				file.close()
			except Exception as error:
				error = str(error)
				try:
					self.imageload = state.root.image(master = self, image = nm, imsize = (1, 1))
					self._bind_focus_recursive(self.imageload)
					self.imageloaded = True
					self.mainwidget = self.imageload
				except Exception:
					try:
						pdf = pdfplumber.open(nm)
						self.type_.delete('1.0', 'end')
						for page in pdf.pages:
							self.type_.insert('end', page.extract_text())
					except Exception:
						try:
							parsed = parser.from_file(nm, service = 'text')
							content = parsed['content']
							self.type_.delete('1.0', 'end')
							self.type_.insert('end', content)
						except Exception:
							state.root.error('Error', error)
						else:
							self.clt(nm)
							self.fileinfoconfig(filesize = str(os.path.getsize(nm)) + ' bytes', filetype = 'EPUB File (*.epub)')
							self.sethmenu(None)
							self.tabs.tab(self.sf, state = 'hidden')
							self.tabs.tab(self.ef, state = 'hidden')
							self.lfouter.pack_forget()
							self.hmode = 'epub'
							self.keypress()
					else:
						self.clt(nm)
						self.fileinfoconfig(filesize = str(os.path.getsize(nm)) + ' bytes', filetype = 'PDF File (*.pdf)')
						self.sethmenu(None)
						self.tabs.tab(self.sf, state = 'hidden')
						self.tabs.tab(self.ef, state = 'hidden')
						self.lfouter.pack_forget()
						self.hmode = 'pdf'
						self.keypress()
				else:
					self.type_.pack_forget()
					self.ln.pack_forget()
					self.tabs.pack_forget()
					self.imageload.pack(fill = 'both', expand = True)
					self.imageloaded = True
					self.mainwidget = self.imageload
					self.clt(nm)
					self.fileinfoconfig(filesize = str(os.path.getsize(nm)) + ' bytes', filetype = 'PNG Image (*.png)')
					self.hmode = 'png'
					self.imageload.focus_set()
					self.sethmenu(None)
					self.tabs.tab(self.sf, state = 'hidden')
					self.tabs.tab(self.ef, state = 'hidden')
					self.lfouter.pack_forget()
					self.keypress()
			else:
				self.unsavedtext = self.type_.get('1.0', 'end-1c')
				self.clt(nm)
				self.fileinfoconfig(filesize = str(os.path.getsize(nm)) + ' bytes')
				if os.path.splitext(nm)[1] == '.py':
					self.pchmode('python')
				elif os.path.splitext(nm)[1] == '.tex':
					self.pchmode('latex')
				elif os.path.splitext(nm)[1] == '.html':
					self.pchmode('html')
				elif os.path.splitext(nm)[1] == '.md':
					self.pchmode('markdown')
				else:
					self.pchmode('normal')
				self.keypress()
			self.type_.edit_reset()
			python_scope_build._python_reset_scan_state(self)
			for child in self.view_children:
				child._sync_chrome()
	def llld(self):
		if self._file_watch_prompt_pending:
			utils.show('select \'Discard Changes & Reload\' or \'Ignore\' external changes before loading another file')
			return
		is_last_reference = self.view_master is None and not self.view_children
		answer = state.root.ask('Warning', 'Do you want to save file before closing?', options = ('yes', 'no', 'cancel')) if (self.unsaved and is_last_reference) else False
		if answer != None:
			if answer:
				if not self.saveforclose():
					return
			self.lld()
	def sv(self, nm):
		if self.view_master:
			return self.view_master.sv(nm)
		if self._file_watch_prompt_pending:
			utils.show('select \'Ignore\' external changes before saving file')
			return False
		if not nm == '':
			if not self.hmode in ['png', 'pdf', 'epub']:
				try:
					content = self.type_.get('1.0', 'end-1c')
					if content == self.unsavedtext:
						utils.show('no changes to save')
						return True
					if os.path.isdir(nm):
						state.root.error('Error', f'"{os.path.basename(nm)}" is an already existing directory.')
						return False
					if os.path.dirname(nm):
						os.chdir(os.path.dirname(nm))
						nm = os.path.basename(nm)
					self.file_editing_own = True
					try:
						file = open(nm, 'w', encoding = 'utf-8')
						file.write(content)
						file.close()
						self.unsavedtext = content
						utils.show('save file')
						self.clt(nm)
					except Exception as error:
						error = str(error)
						state.root.error('Error', error)
						self.file_editing_own = False
						return False
					else:
						self.file_editing_own = False
						return True
				except Exception as error:
					error = str(error)
					state.root.error('Error', error)
					return False
			else:
				state.root.error('Error!', 'Cannot save files of this type.')
				return False
	def ssv(self):
		if self.view_master:
			return self.view_master.ssv()
		if self._file_watch_prompt_pending:
			utils.show('select \'Ignore\' external changes before saving file')
			return False
		fn = dialogs.saveasfileget(initialfile = self.type_.get('1.0', '1.end').replace('/', ' ').replace('\\', ' '))
		pycode.pcrunhook('before', 'save-as-file', fn if fn else None)
		if fn:
			utils.show('save as file')
			if not self.sv(fn):
				return False
			self.clt(fn)
			pycode.pcrunhook('after', 'save-as-file', fn)
			return True
		else:
			return False
	def nw(self):
		is_last_reference = self.view_master is None and not self.view_children
		answer = state.root.ask('Warning', 'Do you want to save file before closing?', options = ('yes', 'no', 'cancel')) if (self.unsaved and is_last_reference) else False
		if answer != None:
			if answer:
				if not self.saveforclose():
					return
			pycode.pcrunhook('before', 'new-file-current-editor')
			self._disconnect()
			try:
				self.imageload.pack_forget()
				self.imageloaded = False
				self.mainwidget = self.type_
			except Exception:
				pass
			else:
				self.ln.pack(side = 'left', fill = 'y', anchor = 'n')
				self.type_.pack(fill = 'both', expand = True, anchor = 'n')
				self.tabs.pack(padx = 10, pady = 10, fill = 'both', expand = True)
			self.type_.delete('1.0', 'end')
			self.unsavedtext = ''
			self.clt('')
			self.type_.edit_reset()
			python_scope_build._python_reset_scan_state(self)
			self.pchmode('normal')
			self.fileinfoconfig(filesize = '0 bytes')
			utils.show('new file')
			pycode.pcrunhook('after', 'new-file-current-editor')
	def fr(self, dir = 'forward'):
		if dir == 'forward':
			utils.show('find & replace text forward')
		elif dir == 'backward':
			utils.show('find & replace text backward')
		elif dir == 'beginning':
			utils.show('find & replace text from beginning')
		search_anchor = [self.type_.index('insert')]
		def fback(replacetext = None):
			nonlocal i
			if searching[0]:
				return
			self.type_.tag_remove('foundhighlight', '1.0', 'end')
			if not foundlist:
				return
			if replacetext is not None:
				replace_start = foundlist[i][0]
				programmatic_edit[0] = True
				self.type_.delete(foundlist[i][0], foundlist[i][1])
				self.type_.insert(foundlist[i][0], replacetext)
				self.type_.after_idle(clear_programmatic_edit)
				def after_search():
					nonlocal i
					for j in range(len(foundlist) - 1, -1, -1):
						if self.type_.compare(foundlist[j][0], '<', replace_start):
							i = j
							self.type_.tag_add('foundhighlight', foundlist[i][0], foundlist[i][1])
							exec("self.type_.tag_config('foundhighlight'," + state.theme['pynotes:foundhighlight'] + ')')
							self.type_.see(foundlist[i][1])
							self.type_.mark_set('insert', foundlist[i][1])
							return
					close_find()
				pending_action[0] = after_search
				updatef()
			else:
				if i != 0:
					i -= 1
				else:
					i = len(foundlist) - 1
				self.type_.tag_add('foundhighlight', foundlist[i][0], foundlist[i][1])
				exec("self.type_.tag_config('foundhighlight'," + state.theme['pynotes:foundhighlight'] + ')')
				self.type_.see(foundlist[i][1])
				self.type_.mark_set('insert', foundlist[i][1])
			self.keypress()
		def fnext(replacetext = None):
			nonlocal i
			if searching[0]:
				return
			self.type_.tag_remove('foundhighlight', '1.0', 'end')
			if not foundlist:
				return
			if replacetext is not None:
				replace_start = foundlist[i][0]
				programmatic_edit[0] = True
				self.type_.delete(foundlist[i][0], foundlist[i][1])
				self.type_.insert(foundlist[i][0], replacetext)
				self.type_.after_idle(clear_programmatic_edit)
				after_replace = '%s+%dc' % (replace_start, len(replacetext))
				def after_search():
					nonlocal i
					for j in range(len(foundlist)):
						if self.type_.compare(foundlist[j][0], '>=', after_replace):
							i = j
							self.type_.tag_add('foundhighlight', foundlist[i][0], foundlist[i][1])
							exec("self.type_.tag_config('foundhighlight'," + state.theme['pynotes:foundhighlight'] + ')')
							self.type_.see(foundlist[i][1])
							self.type_.mark_set('insert', foundlist[i][1])
							return
					close_find()
				pending_action[0] = after_search
				updatef()
			else:
				if i != len(foundlist) - 1:
					i += 1
				else:
					i = 0
				self.type_.tag_add('foundhighlight', foundlist[i][0], foundlist[i][1])
				exec("self.type_.tag_config('foundhighlight'," + state.theme['pynotes:foundhighlight'] + ')')
				self.type_.see(foundlist[i][1])
				self.type_.mark_set('insert', foundlist[i][1])
			self.keypress()
		def replaceall(replacetext):
			nonlocal i
			if searching[0]:
				return
			self.type_.tag_remove('foundhighlight', '1.0', 'end')
			if not foundlist:
				return
			programmatic_edit[0] = True
			for j in range(len(foundlist) - 1, i - 1, -1):
				self.type_.delete(foundlist[j][0], foundlist[j][1])
				self.type_.insert(foundlist[j][0], replacetext)
			self.type_.after_idle(clear_programmatic_edit)
			close_find()
			self.keypress()
		search_cancel = [None]
		searching = [False]
		pending_action = [None]
		programmatic_edit = [False]
		def clear_programmatic_edit():
			programmatic_edit[0] = False
		def updatef():
			nonlocal i
			nonlocal foundlist
			find = findbox.get()
			useregx = regx.get()
			case = cs.get()
			wholeword = ww.get()
			if search_cancel[0]:
				search_cancel[0].set()
			if self._find_apply_after_id is not None:
				self._own_type.after_cancel(self._find_apply_after_id)
				self._find_apply_after_id = None
			if not find:
				self.type_.tag_remove('found', '1.0', 'end')
				self.type_.tag_remove('foundhighlight', '1.0', 'end')
				foundlist.clear()
				searching[0] = False
				return
			self.type_.tag_remove('found', '1.0', 'end')
			self.type_.tag_remove('foundhighlight', '1.0', 'end')
			text_content = self.type_.get('1.0', 'end')
			cancel = threading.Event()
			search_cancel[0] = cancel
			searching[0] = True
			def do_search():
				try:
					pat = find if useregx else re.escape(find)
					if wholeword:
						pat = r'\b' + pat + r'\b'
					flags = 0 if case else re.IGNORECASE
					compiled = re.compile(pat, flags)
				except Exception:
					self._main_queue.put(lambda: _start_apply([]))
					return
				line_starts = [0]
				pos = 0
				while True:
					pos = text_content.find('\n', pos)
					if pos == -1:
						break
					line_starts.append(pos + 1)
					pos += 1
				def to_tk(offset):
					lo, hi = 0, len(line_starts) - 1
					while lo < hi:
						mid = (lo + hi + 1) // 2
						if line_starts[mid] <= offset:
							lo = mid
						else:
							hi = mid - 1
					return f'{lo + 1}.{offset - line_starts[lo]}'
				tk_results = []
				for m in compiled.finditer(text_content):
					if cancel.is_set():
						return
					if m.start() == m.end():
						continue
					tk_results.append((to_tk(m.start()), to_tk(m.end())))
				if not cancel.is_set():
					self._main_queue.put(lambda: _start_apply(tk_results))
			def _start_apply(tk_results):
				nonlocal i, foundlist
				if cancel.is_set():
					searching[0] = False
					return
				foundlist = []
				i = 0
				if tk_results:
					if dir == 'forward':
						cursor = search_anchor[0]
						for idx in range(len(tk_results)):
							if self.type_.compare(tk_results[idx][0], '>=', cursor):
								i = idx
								break
						else:
							i = 0
					elif dir == 'backward':
						cursor = search_anchor[0]
						for idx in range(len(tk_results) - 1, -1, -1):
							if self.type_.compare(tk_results[idx][0], '<', cursor):
								i = idx
								break
						else:
							i = len(tk_results) - 1
				_apply_batch(tk_results, len(tk_results), 0)
			def _apply_batch(tk_results, n, idx):
				nonlocal i, foundlist
				if cancel.is_set():
					self._find_apply_after_id = None
					searching[0] = False
					return
				end = idx + 500
				if end > n:
					end = n
				for k in range(idx, end):
					st, et = tk_results[k]
					self._own_type.tag_add('found', st, et)
					foundlist.append((st, et))
				if end < n:
					self._find_apply_after_id = self._own_type.after(1, lambda: _apply_batch(tk_results, n, end))
				else:
					self._find_apply_after_id = None
					searching[0] = False
					if foundlist:
						exec("self.type_.tag_config('found'," + state.theme['pynotes:found'] + ')')
					action = pending_action[0]
					pending_action[0] = None
					if action:
						action()
					elif foundlist:
						self.type_.tag_add('foundhighlight', foundlist[i][0], foundlist[i][1])
						exec("self.type_.tag_config('foundhighlight'," + state.theme['pynotes:foundhighlight'] + ')')
						self.type_.see(foundlist[i][1])
						self.type_.mark_set('insert', foundlist[i][1])
			threading.Thread(target = do_search, daemon = True).start()
		def updateff(event = None):
			if not event or event and not event.keysym == 'Return' and not (event.state & 4):
				updatef()
				return
			if not foundlist:
				return
			self.type_.tag_add('foundhighlight', foundlist[i][0], foundlist[i][1])
			exec("self.type_.tag_config('foundhighlight'," + state.theme['pynotes:foundhighlight'] + ')')
			self.type_.see(foundlist[i][1])
			self.type_.mark_set('insert', foundlist[i][1])
		ok = state.root.subwin()
		if dir == 'beginning':
			i = 0
		foundlist = []
		ok.title('Find & Replace')
		ok.text(text = 'Find:').grid(column = 0, row = 0, padx = 10, pady = 10)
		findbox = ok.entry()
		findbox.focus()
		findbox.bind('<KeyRelease>', updateff)
		if not state.emacskeysforsearch:
			findbox.bind(('<Return>' if dir != 'backward' else '<Shift-Return>'), lambda event: fnext())
			findbox.bind(('<Return>' if dir == 'backward' else '<Shift-Return>'), lambda event: fback())
		findbox.grid(column = 1, row = 0, padx = 10, pady = 10, sticky = 'ew')
		ok.text(text = 'Replace:').grid(column = 0, row = 1, padx = 10, pady = 10)
		replacebox = ok.entry()
		if not state.emacskeysforsearch:
			replacebox.bind('<Return>', lambda event: fback(replacebox.get()) if dir == 'backward' else fnext(replacebox.get()))
		replacebox.grid(column = 1, row = 1, padx = 10, pady = 10, sticky = 'ew')
		cs = ok.booleanvar()
		ok.check(text = 'Case Sensitive', variable = cs, command = updateff).grid(column = 0, row = 2, padx = 10, pady = 10, sticky = 'ew')
		regx = ok.booleanvar()
		ok.check(text = 'Use regexp', variable = regx, command = updateff).grid(column = 1, row = 2, padx = 10, pady = 10, sticky = 'ew')
		ww = ok.booleanvar()
		ok.check(text = 'Match Whole Word Only', variable = ww, command = updateff).grid(column = 0, row = 3, columnspan = 2, padx = 10, pady = 10, sticky = 'ew')
		ok.button(text = 'Previous', command = fback).grid(column = 0, row = 4, padx = 10, pady = 10, sticky = 'ew')
		ok.button(text = 'Next', command = fnext).grid(column = 1, row = 4, padx = 10, pady = 10, sticky = 'ew')
		def replace_current():
			nonlocal i
			if searching[0] or not foundlist:
				return
			programmatic_edit[0] = True
			self.type_.delete(foundlist[i][0], foundlist[i][1])
			self.type_.insert(foundlist[i][0], replacebox.get())
			self.type_.after_idle(clear_programmatic_edit)
			saved_i = i
			def after_search():
				nonlocal i
				if not foundlist:
					return
				i = saved_i if saved_i < len(foundlist) else len(foundlist) - 1
				self.type_.tag_add('foundhighlight', foundlist[i][0], foundlist[i][1])
				exec("self.type_.tag_config('foundhighlight'," + state.theme['pynotes:foundhighlight'] + ')')
				self.type_.see(foundlist[i][1])
				self.type_.mark_set('insert', foundlist[i][1])
			pending_action[0] = after_search
			updatef()
		ok.button(text = 'Replace', command = replace_current).grid(column = 0, row = 5, padx = 10, pady = 10, sticky = 'ew')
		ok.button(text = 'Replace and next', command = lambda: fnext(replacebox.get())).grid(column = 1, row = 5, padx = 10, pady = 10, sticky = 'ew')
		ok.button(text = 'Replace all', command = lambda: replaceall(replacebox.get())).grid(column = 0, row = 6, padx = 10, pady = 10, sticky = 'ew')
		def close_find():
			if search_cancel[0]:
				search_cancel[0].set()
			if self._find_apply_after_id is not None:
				self._own_type.after_cancel(self._find_apply_after_id)
				self._find_apply_after_id = None
			self.type_.tag_remove('found', '1.0', 'end')
			self.type_.tag_remove('foundhighlight', '1.0', 'end')
			for member in self._group_members():
				member._own_type.unbind('<<Modified>>', member.findmodbindid)
				del member.findmodbindid
			ok.destroy()
		def on_type_modified(event):
			event.widget.edit_modified(False)
			if programmatic_edit[0]:
				return
			close_find()
		for member in self._group_members():
			member._own_type.edit_modified(False)
		state.root.update()
		for member in self._group_members():
			member.findmodbindid = member._own_type.bind('<<Modified>>', on_type_modified, '+')
		ok.button(text = 'Close', command = close_find).grid(column = 1, row = 6, padx = 10, pady = 10, sticky = 'ew')
		if state.emacskeysforsearch:
			ok.bind('<Alt-Return>', lambda event: fnext())
			ok.bind('^', lambda event: fback())
			ok.bind('<Control-t>', lambda event: fback(replacebox.get()) if dir == 'backward' else fnext(replacebox.get()))
			ok.bind('!', lambda event: replaceall(replacebox.get()))
			ok.bind('<Return>', lambda event: close_find())
			for w in (findbox, replacebox):
				w.bind('^', lambda event: fback() or 'break')
				w.bind('!', lambda event: replaceall(replacebox.get()) or 'break')
		ok.update()
		ok.sizablefalse()
		ok.style(state.root.gettheme())
		ok.bind('<Escape>', lambda event: close_find())
		ok.protocol('WM_DELETE_WINDOW', close_find)
	def f(self, dir = 'forward'):
		if dir == 'forward':
			utils.show('find text forward')
		elif dir == 'backward':
			utils.show('find text backward')
		elif dir == 'beginning':
			utils.show('find text from beginning')
		search_anchor = [self.type_.index('insert')]
		def fback():
			nonlocal i
			self.type_.tag_remove('foundhighlight', '1.0', 'end')
			if not foundlist:
				return
			if i != 0:
				i -= 1
			else:
				i = len(foundlist) - 1
			self.type_.tag_add('foundhighlight', foundlist[i][0], foundlist[i][1])
			exec("self.type_.tag_config('foundhighlight'," + state.theme['pynotes:foundhighlight'] + ')')
			self.type_.see(foundlist[i][1])
			self.type_.mark_set('insert', foundlist[i][1])
			self.keypress()
		def fnext():
			nonlocal i
			self.type_.tag_remove('foundhighlight', '1.0', 'end')
			if not foundlist:
				return
			if i != len(foundlist) - 1:
				i += 1
			else:
				i = 0
			self.type_.tag_add('foundhighlight', foundlist[i][0], foundlist[i][1])
			exec("self.type_.tag_config('foundhighlight'," + state.theme['pynotes:foundhighlight'] + ')')
			self.type_.see(foundlist[i][1])
			self.type_.mark_set('insert', foundlist[i][1])
			self.keypress()
		search_cancel = [None]
		def updatef():
			nonlocal i
			nonlocal foundlist
			find = findbox.get()
			useregx = regx.get()
			case = cs.get()
			wholeword = ww.get()
			if search_cancel[0]:
				search_cancel[0].set()
			if self._find_apply_after_id is not None:
				self._own_type.after_cancel(self._find_apply_after_id)
				self._find_apply_after_id = None
			if not find:
				self.type_.tag_remove('found', '1.0', 'end')
				self.type_.tag_remove('foundhighlight', '1.0', 'end')
				foundlist.clear()
				return
			self.type_.tag_remove('found', '1.0', 'end')
			self.type_.tag_remove('foundhighlight', '1.0', 'end')
			text_content = self.type_.get('1.0', 'end')
			cancel = threading.Event()
			search_cancel[0] = cancel
			def do_search():
				try:
					pat = find if useregx else re.escape(find)
					if wholeword:
						pat = r'\b' + pat + r'\b'
					flags = 0 if case else re.IGNORECASE
					compiled = re.compile(pat, flags)
				except Exception:
					self._main_queue.put(lambda: _start_apply([]))
					return
				line_starts = [0]
				pos = 0
				while True:
					pos = text_content.find('\n', pos)
					if pos == -1:
						break
					line_starts.append(pos + 1)
					pos += 1
				def to_tk(offset):
					lo, hi = 0, len(line_starts) - 1
					while lo < hi:
						mid = (lo + hi + 1) // 2
						if line_starts[mid] <= offset:
							lo = mid
						else:
							hi = mid - 1
					return f'{lo + 1}.{offset - line_starts[lo]}'
				tk_results = []
				for m in compiled.finditer(text_content):
					if cancel.is_set():
						return
					if m.start() == m.end():
						continue
					tk_results.append((to_tk(m.start()), to_tk(m.end())))
				if not cancel.is_set():
					self._main_queue.put(lambda: _start_apply(tk_results))
			def _start_apply(tk_results):
				nonlocal i, foundlist
				if cancel.is_set():
					return
				foundlist = []
				i = 0
				if tk_results:
					if dir == 'forward':
						cursor = search_anchor[0]
						for idx in range(len(tk_results)):
							if self.type_.compare(tk_results[idx][0], '>=', cursor):
								i = idx
								break
						else:
							i = 0
					elif dir == 'backward':
						cursor = search_anchor[0]
						for idx in range(len(tk_results) - 1, -1, -1):
							if self.type_.compare(tk_results[idx][0], '<', cursor):
								i = idx
								break
						else:
							i = len(tk_results) - 1
				_apply_batch(tk_results, len(tk_results), 0)
			def _apply_batch(tk_results, n, idx):
				nonlocal i, foundlist
				if cancel.is_set():
					self._find_apply_after_id = None
					return
				end = idx + 500
				if end > n:
					end = n
				for k in range(idx, end):
					st, et = tk_results[k]
					self._own_type.tag_add('found', st, et)
					foundlist.append((st, et))
				if end < n:
					self._find_apply_after_id = self._own_type.after(1, lambda: _apply_batch(tk_results, n, end))
				else:
					self._find_apply_after_id = None
					if foundlist:
						exec("self.type_.tag_config('found'," + state.theme['pynotes:found'] + ')')
						self.type_.tag_add('foundhighlight', foundlist[i][0], foundlist[i][1])
						exec("self.type_.tag_config('foundhighlight'," + state.theme['pynotes:foundhighlight'] + ')')
						self.type_.see(foundlist[i][1])
						self.type_.mark_set('insert', foundlist[i][1])
			threading.Thread(target = do_search, daemon = True).start()
		def updateff(event = None):
			if not event or event and not event.keysym == 'Return' and not (event.state & 4):
				updatef()
				return
			if not foundlist:
				return
			self.type_.tag_add('foundhighlight', foundlist[i][0], foundlist[i][1])
			exec("self.type_.tag_config('foundhighlight'," + state.theme['pynotes:foundhighlight'] + ')')
			self.type_.see(foundlist[i][1])
			self.type_.mark_set('insert', foundlist[i][1])
		ok = state.root.subwin()
		if dir == 'beginning':
			i = 0
		foundlist = []
		ok.title('Find')
		ok.text(text = 'Find:').grid(column = 0, row = 0, padx = 10, pady = 10)
		findbox = ok.entry()
		findbox.focus()
		findbox.bind('<KeyRelease>', updateff)
		if not state.emacskeysforsearch:
			findbox.bind(('<Return>' if dir != 'backward' else '<Shift-Return>'), lambda event: fnext())
			findbox.bind(('<Return>' if dir == 'backward' else '<Shift-Return>'), lambda event: fback())
		findbox.grid(column = 1, row = 0, padx = 10, pady = 10, sticky = 'ew')
		cs = ok.booleanvar()
		ok.check(text = 'Case Sensitive', variable = cs, command = updateff).grid(column = 0, row = 1, padx = 10, pady = 10, sticky = 'ew')
		regx = ok.booleanvar()
		ok.check(text = 'Use regexp', variable = regx, command = updateff).grid(column = 1, row = 1, padx = 10, pady = 10, sticky = 'ew')
		ww = ok.booleanvar()
		ok.check(text = 'Match Whole Word Only', variable = ww, command = updateff).grid(column = 0, row = 2, columnspan = 2, padx = 10, pady = 10, sticky = 'ew')
		ok.button(text = 'Previous', command = fback).grid(column = 0, row = 3, padx = 10, pady = 10, sticky = 'ew')
		ok.button(text = 'Next', command = fnext).grid(column = 1, row = 3, padx = 10, pady = 10, sticky = 'ew')
		def close_find():
			if search_cancel[0]:
				search_cancel[0].set()
			if self._find_apply_after_id is not None:
				self._own_type.after_cancel(self._find_apply_after_id)
				self._find_apply_after_id = None
			self.type_.tag_remove('found', '1.0', 'end')
			self.type_.tag_remove('foundhighlight', '1.0', 'end')
			for member in self._group_members():
				member._own_type.unbind('<<Modified>>', member.findmodbindid)
				del member.findmodbindid
			ok.destroy()
		def on_type_modified(event):
			event.widget.edit_modified(False)
			close_find()
		for member in self._group_members():
			member._own_type.edit_modified(False)
		state.root.update()
		for member in self._group_members():
			member.findmodbindid = member._own_type.bind('<<Modified>>', on_type_modified)
		ok.button(text = 'Close', command = close_find).grid(column = 1, row = 4, padx = 10, pady = 10, sticky = 'ew')
		if state.emacskeysforsearch:
			ok.bind('<Control-s>', lambda event: fnext())
			ok.bind('<Control-r>', lambda event: fback())
			ok.bind('<Return>', lambda event: close_find())
		ok.update()
		ok.sizablefalse()
		ok.style(state.root.gettheme())
		ok.bind('<Escape>', lambda event: close_find())
		ok.protocol('WM_DELETE_WINDOW', close_find)
	def type_getvisible(self):
		self._own_type.update()
		top = self._own_type.index('@0,0-2l')
		bottom = self._own_type.index(f'@0,{self._own_type.winfo_height()}+2l')
		return (top, bottom)
	def _update_filesize(self):
		size = len(io.StringIO(self.type_.get('1.0', 'end')).read()) - 1
		for member in self._group_members():
			member.fileinfoconfig(filesize = str(size) + ' bytes')
	def trigger_filesize(self):
		if self._filesize_after_id is not None:
			self._own_type.after_cancel(self._filesize_after_id)
		self._filesize_after_id = self._own_type.after(DEBOUNCE_TIME, self._update_filesize)
	def _set_undo_mark(self):
		if not self.undoset:
			self.type_.edit_separator()
			self.undoset = True
	def trigger_undo_set(self):
		if self._setundo_after_id is not None:
			self._own_type.after_cancel(self._setundo_after_id)
		self.setundo_after_id = self._own_type.after(DEBOUNCE_TIME, self._set_undo_mark)
	def _update_unsaved(self):
		if self.title and not self.hmode in ['png', 'pdf', 'epub']:
			if self.type_.get('1.0', 'end-1c') != self.unsavedtext:
				self.unsaved = True
				self._sync_wanttitle()
				for member in self._group_members():
					member.fileinfoconfig(filesaved = 'Unsaved File')
			else:
				self.unsaved = False
				self._sync_wanttitle()
				for member in self._group_members():
					member.fileinfoconfig(filesaved = 'Saved File')
	def trigger_unsaved(self):
		if self._unsaved_after_id is not None:
			self._own_type.after_cancel(self._unsaved_after_id)
		self._unsaved_after_id = self._own_type.after(DEBOUNCE_TIME, self._update_unsaved)
	def trigger_ha(self, ft):
		if self.view_master is not None:
			return self.view_master.trigger_ha(ft)
		if self._ha_after_id is not None:
			self._own_type.after_cancel(self._ha_after_id)
		self._ha_after_id = self._own_type.after(DEBOUNCE_TIME, lambda: self.ha(ft))
	def python_trigger_name_scan(self):
		if self.view_master is not None:
			return self.view_master.python_trigger_name_scan()
		if self._python_scan_after_id is not None:
			self._own_type.after_cancel(self._python_scan_after_id)
		self._python_scan_after_id = self._own_type.after(DEBOUNCE_TIME, lambda: python_scope_build._python_scan_start(self))
	def ha(self, ft):
		if self.view_master is not None:
			return self.view_master.ha(ft)
		if self._ha_running[0]:
			self._ha_pending[0] = ft
			return
		self._ha_running[0] = True
		try:
			snapshots = []
			for member in self._group_members():
				own_type = member._own_type
				top = member.type_top
				bottom = member.type_bottom
				text = own_type.get(top, bottom)
				pre_text = own_type.get('1.0', top)
				snapshots.append((member, own_type, top, bottom, text, pre_text))
			python_scopes = self._python_scopes
			python_call_kwargs = self._python_call_kwargs
			python_module_literals = self._python_module_literals
			python_name_positions = self._python_name_positions
			python_def_names = self._python_def_names
			python_typed_attrs = self._python_typed_attrs
			python_param_default_tags = self._python_param_default_tags
			python_kwarg_positions = self._python_kwarg_positions
			python_import_dotted_lines = self._python_import_dotted_lines
			python_instance_name_positions = self._python_instance_name_positions
			python_global_stmt_kind_positions = self._python_global_stmt_kind_positions
			python_import_orig_name_tags = self._python_import_orig_name_tags
		except Exception:
			self._ha_running[0] = False
			pending = self._ha_pending[0]
			if pending is not None:
				self._ha_pending[0] = None
				self.ha(pending)
			return
		def _build_ops(own_type, top, bottom, text, pre_text):
			ops = []
			try:
				ops.append(('remove_all',))
				if ft == 'python':
					for m in _PYTHON_KW_PAT.finditer(text):
						ops.append(('add', 'hpa', f'{top}+{m.start()}c', f'{top}+{m.end()}c'))
					top_line = int(top.split('.')[0])
					line_scope_candidates = {}
					for line in range(top_line, top_line + len(text.split('\n'))):
						_cands = []
						for k, sc in enumerate(python_scopes):
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
					module_literal_lines = {}
					for lineno, _mcol, name in python_module_literals:
						module_literal_lines.setdefault(lineno, []).append((_mcol, name))
					import_dotted_by_line = {}
					for lineno, dcol, dotted in python_import_dotted_lines:
						import_dotted_by_line.setdefault(lineno, []).append((dcol, dotted))
					import_orig_by_line = {}
					for _oln, _ocol, _oname, _otag in python_import_orig_name_tags:
						import_orig_by_line.setdefault(_oln, []).append((_ocol, _oname, _otag))
					name_pos_by_line = {}
					for _nl, _ncol, _nname, _nstore in python_name_positions:
						name_pos_by_line.setdefault(_nl, []).append((_ncol, _nname, _nstore))
					def_names_by_line = {}
					for _dl, _dcol, _dname, _dkind in python_def_names:
						def_names_by_line.setdefault(_dl, []).append((_dcol, _dname, _dkind))
					python_kind_tags = {'var': 'hpv', 'instance': 'hpi', 'func': 'hpf', 'func_arg': 'hpfa', 'first_param': 'hpb', 'module': 'hpm', 'class': 'hpx', 'builtin': 'hpb'}
					python_literal_attrs = self._python_literal_attrs
					literal_attr_by_line = {}
					for _ln, _col, _attr, _tname in python_literal_attrs:
						literal_attr_by_line.setdefault(_ln, []).append((_col, _attr, _tname))
					typed_attr_by_line = {}
					for _tl, _tcol, _tattr, _tkind in python_typed_attrs:
						typed_attr_by_line.setdefault(_tl, []).append((_tcol, _tattr, _tkind))
					param_default_by_line = {}
					for _pl, _pcol, _pname, _pkind in python_param_default_tags:
						param_default_by_line.setdefault(_pl, []).append((_pcol, _pname, _pkind))
					kwarg_pos_by_line = {}
					for _kl, _kcol, _kname in python_kwarg_positions:
						kwarg_pos_by_line.setdefault(_kl, []).append((_kcol, _kname))
					_active_cache = {}
					def _active_for(abs_line, scope_idx):
						_ckey = (abs_line, scope_idx)
						if _ckey in _active_cache:
							return _active_cache[_ckey]
						active = {}
						prior_kinds = {}
						bound = set()
						innermost_scope = scope_idx
						innermost_parent = python_scopes[innermost_scope]['parent'] if innermost_scope is not None else None
						on_header = innermost_scope is not None and abs_line == python_scopes[innermost_scope]['start']
						_redir_names = set()
						_rsi = innermost_scope
						while _rsi is not None:
							_rsc = python_scopes[_rsi]
							_redir_names |= set(_rsc.get('globals', {}))
							_redir_names |= set(_rsc.get('nonlocals', {}))
							_rsi = _rsc['parent']
						_sidx = scope_idx
						while _sidx is not None:
							sc = python_scopes[_sidx]
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
								if best is None and name not in _PYTHON_BUILTIN_NAMES:
									best = latest
								bound.add(name)
								if best is not None:
									active[name] = best[1]
									if best[0] == abs_line and second_best is not None and second_best[1] != best[1]:
										prior_kinds[name] = second_best[1]
							_sidx = sc['parent']
						_result = (active, prior_kinds)
						_active_cache[_ckey] = _result
						return _result
					offset = 0
					for li, line_str in enumerate(text.split('\n')):
						abs_line = top_line + li
						for _ncol, _nname, _nstore in name_pos_by_line.get(abs_line, []):
							_nkind = python_global_stmt_kind_positions.get((abs_line, _ncol))
							if _nkind is None:
								active, prior_kinds = _active_for(abs_line, _resolve_scope_idx(abs_line, _ncol))
								_nkind = active.get(_nname)
								if _nkind is None:
									if _nname not in _PYTHON_BUILTIN_NAMES:
										continue
									_nkind = 'builtin'
								elif not _nstore and _nname in prior_kinds:
									_nkind = prior_kinds[_nname]
							_ntag = python_kind_tags.get(_nkind)
							if _ntag is None:
								continue
							if _ntag == 'hpv' and (abs_line, _ncol) in python_instance_name_positions:
								_ntag = 'hpi'
							_nccol = _python_bytecol_to_charcol(line_str, _ncol)
							s = f'{top}+{offset + _nccol}c'
							e = f'{top}+{offset + _nccol + len(_nname)}c'
							ops.append(('add', _ntag, s, e))
						for _dcol, _dname, _dkind in def_names_by_line.get(abs_line, []):
							_dccol = _python_bytecol_to_charcol(line_str, _dcol)
							s = f'{top}+{offset + _dccol}c'
							e = f'{top}+{offset + _dccol + len(_dname)}c'
							ops.append(('add', 'hpf' if _dkind == 'func' else 'hpx', s, e))
						for _pcol, _pname, _pkind in param_default_by_line.get(abs_line, []):
							if _pkind == 'var' and (abs_line, _pcol) in python_instance_name_positions:
								_pkind = 'instance'
							_pcol = _python_bytecol_to_charcol(line_str, _pcol)
							_ptag = {'var': 'hpv', 'instance': 'hpi', 'func': 'hpf', 'func_arg': 'hpfa', 'first_param': 'hpb', 'module': 'hpm', 'class': 'hpx'}.get(_pkind)
							if _ptag is not None:
								s = f'{top}+{offset + _pcol}c'
								e = f'{top}+{offset + _pcol + len(_pname)}c'
								ops.append(('add', _ptag, s, e))
						for _mcol, name in module_literal_lines.get(abs_line, []):
							_mccol = _python_bytecol_to_charcol(line_str, _mcol)
							if line_str[_mccol:_mccol + len(name)] != name:
								continue
							ops.append(('add', 'hpm', f'{top}+{offset + _mccol}c', f'{top}+{offset + _mccol + len(name)}c'))
						for dcol, dotted in import_dotted_by_line.get(abs_line, []):
							dcol = _python_bytecol_to_charcol(line_str, dcol)
							if line_str[dcol:dcol + len(dotted)] != dotted:
								continue
							pos = dcol
							for part in dotted.split('.'):
								ops.append(('add', 'hpm', f'{top}+{offset + pos}c', f'{top}+{offset + pos + len(part)}c'))
								pos += len(part) + 1
						for _ocol, _oname, _otag in import_orig_by_line.get(abs_line, []):
							_ocol = _python_bytecol_to_charcol(line_str, _ocol)
							if line_str[_ocol:_ocol + len(_oname)] != _oname:
								continue
							ops.append(('add', _otag, f'{top}+{offset + _ocol}c', f'{top}+{offset + _ocol + len(_oname)}c'))
						for _col, _attr, _tname in literal_attr_by_line.get(abs_line, []):
							_col = _python_bytecol_to_charcol(line_str, _col)
							_kind = _PYTHON_BUILTIN_MEMBERS[_tname].get(_attr)
							if _kind is not None:
								ops.append(('add', 'hpf' if _kind == 'func' else 'hpv', f'{top}+{offset + _col}c', f'{top}+{offset + _col + len(_attr)}c'))
						for _tcol, _tattr, _tkind in typed_attr_by_line.get(abs_line, []):
							_tcol = _python_bytecol_to_charcol(line_str, _tcol)
							_ttag = {'func': 'hpf', 'var': 'hpv', 'instance': 'hpi', 'module': 'hpm', 'class': 'hpx'}.get(_tkind, 'hpx')
							ops.append(('add', _ttag, f'{top}+{offset + _tcol}c', f'{top}+{offset + _tcol + len(_tattr)}c'))
						for _kcol, _kname in kwarg_pos_by_line.get(abs_line, []):
							_kcol = _python_bytecol_to_charcol(line_str, _kcol)
							s = f'{top}+{offset + _kcol}c'
							e = f'{top}+{offset + _kcol + len(_kname)}c'
							ops.append(('clear_other', s, e))
							if _kname in python_call_kwargs.get(abs_line, set()):
								ops.append(('add', 'hpfa', s, e))
						offset += len(line_str) + 1
					for m in _PYTHON_OP_PAT.finditer(text):
						s = f'{top}+{m.start()}c'
						e = f'{top}+{m.end()}c'
						ops.append(('add', 'hpo', s, e))
					pre_n = len(pre_text)
					pre_i = 0
					in_triple = False
					triple_ch = None
					in_single = False
					single_ch = None
					while pre_i < pre_n:
						pch = pre_text[pre_i]
						if pch in ('"', "'") and pre_i + 2 < pre_n and pre_text[pre_i + 1] == pch and pre_text[pre_i + 2] == pch:
							pquote = pre_text[pre_i:pre_i + 3]
							j = pre_i + 3
							found_close = False
							while j < pre_n:
								if pre_text[j] == '\\':
									j += 2
									continue
								if pre_text[j:j + 3] == pquote:
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
								if pre_text[j] == '\\':
									j += 2
									continue
								if pre_text[j] == pquote:
									j += 1
									closed = True
									break
								if pre_text[j] == '\n':
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
							while j < pre_n and pre_text[j] != '\n':
								j += 1
							if j < pre_n:
								j += 1
							pre_i = j
						else:
							pre_i += 1
					n = len(text)
					i = 0
					if in_triple:
						quote = triple_ch * 3
						j = 0
						found_close = False
						while j < n:
							if text[j] == '\\':
								j += 2
								continue
							if text[j:j + 3] == quote:
								j += 3
								found_close = True
								break
							j += 1
						if not found_close:
							j = n
						ops.append(('add', 'hpd', f'{top}+0c', f'{top}+{j}c'))
						i = j
					elif in_single:
						quote = single_ch
						j = 0
						while j < n:
							if text[j] == '\\':
								j += 2
								continue
							if text[j] == quote:
								j += 1
								break
							if text[j] == '\n':
								break
							j += 1
						if j > n:
							j = n
						ops.append(('add', 'hpd', f'{top}+0c', f'{top}+{j}c'))
						i = j
					while i < n:
						ch = text[i]
						if ch in ('"', "'") and i + 2 < n and text[i + 1] == ch and text[i + 2] == ch:
							quote = text[i:i + 3]
							j = i + 3
							found_close = False
							while j < n:
								if text[j] == '\\':
									j += 2
									continue
								if text[j:j + 3] == quote:
									j += 3
									found_close = True
									break
								j += 1
							if not found_close:
								j = n
							ops.append(('add', 'hpd', f'{top}+{i}c', f'{top}+{j}c'))
							i = j
						elif ch in ('"', "'"):
							quote = ch
							j = i + 1
							while j < n:
								if text[j] == '\\':
									j += 2
									continue
								if text[j] == quote:
									j += 1
									break
								if text[j] == '\n':
									break
								j += 1
							ops.append(('add', 'hpd', f'{top}+{i}c', f'{top}+{j}c'))
							i = j
						elif ch == '#':
							j = i + 1
							while j < n and text[j] != '\n':
								j += 1
							if j < n:
								j += 1
							ops.append(('add', 'hpc', f'{top}+{i}c', f'{top}+{j}c'))
							i = j
						else:
							i += 1
				elif ft == 'latex':
					pre_n = len(pre_text)
					pre_i = 0
					in_math = False
					math_close = ''
					while pre_i < pre_n:
						pc = pre_text[pre_i]
						if pc == '\\' and pre_i + 1 < pre_n:
							nc = pre_text[pre_i + 1]
							if not in_math and nc == '[':
								in_math = True
								math_close = '\\]'
								pre_i += 2
								continue
							if not in_math and nc == '(':
								in_math = True
								math_close = '\\)'
								pre_i += 2
								continue
							if in_math and math_close == '\\]' and nc == ']':
								in_math = False
								pre_i += 2
								continue
							if in_math and math_close == '\\)' and nc == ')':
								in_math = False
								pre_i += 2
								continue
							pre_i += 2
							continue
						if pc == '%':
							while pre_i < pre_n and pre_text[pre_i] != '\n':
								pre_i += 1
							continue
						if pc == '$':
							if pre_i + 1 < pre_n and pre_text[pre_i + 1] == '$':
								if in_math and math_close == '$$':
									in_math = False
								elif not in_math:
									in_math = True
									math_close = '$$'
								pre_i += 2
								continue
							else:
								if in_math and math_close == '$':
									in_math = False
								elif not in_math:
									in_math = True
									math_close = '$'
						pre_i += 1
					if in_math:
						j = text.find(math_close)
						if j == -1:
							j = len(text)
						else:
							j += len(math_close)
						ops.append(('add', 'hla', f'{top}+0c', f'{top}+{j}c'))
					for m in _LATEX_MATH_PAT.finditer(text):
						ops.append(('add', 'hla', f'{top}+{m.start()}c', f'{top}+{m.end()}c'))
					pre_n = len(pre_text)
					env_stack = []
					for em in re.finditer(r'\\(begin|end){\s*(\w+\*?)\s*}', pre_text):
						ename = em.group(2)
						if ename == 'document':
							continue
						if em.group(1) == 'begin':
							env_stack.append((ename, em.start()))
						elif env_stack and env_stack[-1][0] == ename:
							env_stack.pop()
					scan_from = 0
					if env_stack:
						outer_name, outer_start = env_stack[0]
						region = own_type.get(f'1.0+{outer_start}c', bottom)
						env_pat = re.compile(r'\\(begin|end){\s*' + re.escape(outer_name) + r'\s*}')
						m0 = env_pat.match(region)
						depth = 1
						search_from = m0.end() if m0 else len(region)
						hl_start_rel = search_from
						nl0 = region.find('\n', hl_start_rel)
						if nl0 != -1:
							hl_start_rel = nl0 + 1
						while depth > 0:
							em2 = env_pat.search(region, search_from)
							if not em2:
								search_from = len(region)
								break
							if em2.group(1) == 'begin':
								depth += 1
							else:
								depth -= 1
							search_from = em2.end()
						end_abs = outer_start + search_from
						hl_start_abs = outer_start + hl_start_rel
						if hl_start_abs < end_abs:
							ops.append(('add', 'hlb', f'1.0+{hl_start_abs}c', f'1.0+{end_abs}c'))
						scan_from = max(0, end_abs - pre_n)
					tn = len(text)
					for begin_m in re.finditer(r'\\begin{\s*(\w+\*?)\s*}', text[scan_from:]):
						if begin_m.group(1) == 'document':
							continue
						env_name = re.escape(begin_m.group(1))
						search_from2 = scan_from + begin_m.end()
						bstart = search_from2
						nl1 = text.find('\n', bstart)
						if nl1 != -1:
							bstart = nl1 + 1
						depth2 = 1
						env_pat2 = re.compile(r'\\(begin|end){\s*' + env_name + r'\s*}')
						bend = tn
						while depth2 > 0:
							em3 = env_pat2.search(text, search_from2)
							if not em3:
								break
							if em3.group(1) == 'begin':
								depth2 += 1
							else:
								depth2 -= 1
							search_from2 = em3.end()
							if depth2 == 0:
								bend = search_from2
						if bstart < bend:
							ops.append(('add', 'hlb', f'{top}+{bstart}c', f'{top}+{bend}c'))
					for m in re.finditer(r'\\[a-zA-Z@]+\*?', text):
						ops.append(('add', 'hld', f'{top}+{m.start()}c', f'{top}+{m.end()}c'))
					for i in range(len(text)):
						if text[i] == '{' and (i == 0 or text[i - 1] != '\\'):
							j = _find_closing_brace(text, i)
							ops.append(('add', 'hle', f'{top}+{i}c', f'{top}+{j}c'))
					for m in re.finditer(r'\\\\|&|\|', text):
						ops.append(('add', 'hlf', f'{top}+{m.start()}c', f'{top}+{m.end()}c'))
					for i in range(len(text)):
						if text[i] == '[' and (i == 0 or text[i - 1] != '\\'):
							j = _find_closing_bracket(text, i)
							ops.append(('add', 'hlg', f'{top}+{i}c', f'{top}+{j}c'))
					for m in _LH_PAT.finditer(text):
						s = f'{top}+{m.start()}c'
						e = f'{top}+{m.end()}c'
						ops.append(('add', 'hlh', s, e))
				elif ft == 'html':
					last_open = pre_text.rfind('<!--')
					last_close = pre_text.rfind('-->')
					if last_open != -1 and last_close < last_open:
						close_pos = text.find('-->')
						j = (close_pos + 3) if close_pos != -1 else len(text)
						ops.append(('add', 'hcmt', f'{top}+0c', f'{top}+{j}c'))
					for m in _HC_PAT.finditer(text):
						s = f'{top}+{m.start()}c'
						e = f'{top}+{m.end()}c'
						ops.append(('add', 'hcmt', s, e))
					hi = 0
					htlen = len(text)
					while hi < htlen:
						if text[hi] != '<' or hi >= htlen - 1:
							hi += 1
							continue
						hj = _find_closing_tag(text, hi)
						htag_inner = text[hi:hj]
						if text[hi + 1] == '!':
							if re.match(r'<!DOCTYPE\b', htag_inner, re.IGNORECASE):
								ops.append(('add', 'hstuff', f'{top}+{hi}c', f'{top}+{hj}c'))
							hi = hj
							continue
						if hj > hi + 1 and (text[hi + 1].isalpha() or text[hi + 1] == '/'):
							ops.append(('add', 'hstuff', f'{top}+{hi}c', f'{top}+{hj}c'))
							htn_m = re.match(r'</?([a-zA-Z][a-zA-Z0-9:-]*)', htag_inner, re.IGNORECASE)
							hattrs_off = htn_m.end() if htn_m else 1
							for ham in _HTML_ATTR_PAT.finditer(htag_inner, hattrs_off):
								ops.append(('add', 'hattr', f'{top}+{hi + ham.start(1)}c', f'{top}+{hi + ham.end(1)}c'))
								ops.append(('add', 'hstr', f'{top}+{hi + ham.start(2)}c', f'{top}+{hi + ham.end(2)}c'))
							for hbm in _HTML_BOOL_ATTR_PAT.finditer(htag_inner, hattrs_off):
								ops.append(('add', 'hattr', f'{top}+{hi + hbm.start()}c', f'{top}+{hi + hbm.end()}c'))
						hi = hj
				elif ft == 'markdown':
					last_open = pre_text.rfind('<!--')
					last_close = pre_text.rfind('-->')
					if last_open != -1 and last_close < last_open:
						close_pos = text.find('-->')
						j = (close_pos + 3) if close_pos != -1 else len(text)
						ops.append(('add', 'hcmt', f'{top}+0c', f'{top}+{j}c'))
					for m in _HC_PAT.finditer(text):
						s = f'{top}+{m.start()}c'
						e = f'{top}+{m.end()}c'
						ops.append(('add', 'hcmt', s, e))
					mhi = 0
					mhtlen = len(text)
					while mhi < mhtlen:
						if text[mhi] != '<' or mhi >= mhtlen - 1:
							mhi += 1
							continue
						mhj = _find_closing_tag(text, mhi)
						mhtag_inner = text[mhi:mhj]
						if text[mhi + 1] == '!':
							if re.match(r'<!DOCTYPE\b', mhtag_inner, re.IGNORECASE):
								ops.append(('add', 'hstuff', f'{top}+{mhi}c', f'{top}+{mhj}c'))
							mhi = mhj
							continue
						if mhj > mhi + 1 and (text[mhi + 1].isalpha() or text[mhi + 1] == '/'):
							ops.append(('add', 'hstuff', f'{top}+{mhi}c', f'{top}+{mhj}c'))
							mhtn_m = re.match(r'</?([a-zA-Z][a-zA-Z0-9:-]*)', mhtag_inner, re.IGNORECASE)
							mhattrs_off = mhtn_m.end() if mhtn_m else 1
							for mham in _HTML_ATTR_PAT.finditer(mhtag_inner, mhattrs_off):
								ops.append(('add', 'hattr', f'{top}+{mhi + mham.start(1)}c', f'{top}+{mhi + mham.end(1)}c'))
								ops.append(('add', 'hstr', f'{top}+{mhi + mham.start(2)}c', f'{top}+{mhi + mham.end(2)}c'))
							for mhbm in _HTML_BOOL_ATTR_PAT.finditer(mhtag_inner, mhattrs_off):
								ops.append(('add', 'hattr', f'{top}+{mhi + mhbm.start()}c', f'{top}+{mhi + mhbm.end()}c'))
						mhi = mhj
					for m in _MDH_PAT.finditer(text):
						level = len(m.group(1))
						s = f'{top}+{m.start()}c'
						e = f'{top}+{m.end()}c'
						for htag in _MD_HTML_TAGS:
							ops.append(('remove', htag, s, e))
						ops.append(('add', f'hmh{level}', s, e))
					for m in _MDB_PAT.finditer(text):
						s = f'{top}+{m.start()}c'
						e = f'{top}+{m.end()}c'
						for htag in _MD_HTML_TAGS:
							ops.append(('remove', htag, s, e))
						ops.append(('add', 'hmb', s, e))
					for m in _MDI_PAT.finditer(text):
						s = f'{top}+{m.start()}c'
						e = f'{top}+{m.end()}c'
						for htag in _MD_HTML_TAGS:
							ops.append(('remove', htag, s, e))
						ops.append(('add', 'hmi', s, e))
					for m in _MDBI_PAT.finditer(text):
						s = f'{top}+{m.start()}c'
						e = f'{top}+{m.end()}c'
						ops.append(('add', 'hmbi', s, e))
					for m in _MDS_PAT.finditer(text):
						s = f'{top}+{m.start()}c'
						e = f'{top}+{m.end()}c'
						for htag in _MD_HTML_TAGS:
							ops.append(('remove', htag, s, e))
						ops.append(('add', 'hms', s, e))
					for m in _MDC_PAT.finditer(text):
						s = f'{top}+{m.start()}c'
						e = f'{top}+{m.end()}c'
						ops.append(('add', 'hmc', s, e))
					for m in _MDL_PAT.finditer(text):
						s = f'{top}+{m.start()}c'
						e = f'{top}+{m.end()}c'
						ops.append(('add', 'hml', s, e))
					for m in _MDQ_PAT.finditer(text):
						s = f'{top}+{m.start()}c'
						e = f'{top}+{m.end()}c'
						for htag in _MD_HTML_TAGS:
							ops.append(('remove', htag, s, e))
						ops.append(('add', 'hmq', s, e))
					pre_n = len(pre_text)
					pre_i = 0
					in_fence = False
					while pre_i < pre_n:
						if (pre_i == 0 or pre_text[pre_i - 1] == '\n') and pre_text[pre_i:pre_i + 3] == '```':
							j = pre_i + 3
							while j < pre_n and pre_text[j] != '\n':
								j += 1
							if j < pre_n:
								j += 1
							k = j
							found_close = False
							while k < pre_n:
								if (k == 0 or pre_text[k - 1] == '\n') and pre_text[k:k + 3] == '```':
									k += 3
									while k < pre_n and pre_text[k] != '\n':
										k += 1
									if k < pre_n:
										k += 1
									found_close = True
									break
								k += 1
							if found_close:
								pre_i = k
							else:
								in_fence = True
								break
						else:
							pre_i += 1
					n = len(text)
					i = 0
					if in_fence:
						j = 0
						found_close = False
						while j < n:
							if (j == 0 or text[j - 1] == '\n') and text[j:j + 3] == '```':
								j += 3
								while j < n and text[j] != '\n':
									j += 1
								if j < n:
									j += 1
								found_close = True
								break
							j += 1
						if not found_close:
							j = n
						ops.append(('add', 'hmf', f'{top}+0c', f'{top}+{j}c'))
						i = j
					while i < n:
						if (i == 0 or text[i - 1] == '\n') and text[i:i + 3] == '```':
							j = i + 3
							while j < n and text[j] != '\n':
								j += 1
							if j < n:
								j += 1
							k = j
							found_close = False
							while k < n:
								if (k == 0 or text[k - 1] == '\n') and text[k:k + 3] == '```':
									k += 3
									while k < n and text[k] != '\n':
										k += 1
									if k < n:
										k += 1
									found_close = True
									break
								k += 1
							if not found_close:
								k = n
							ops.append(('add', 'hmf', f'{top}+{i}c', f'{top}+{k}c'))
							i = k
						else:
							i += 1
			except Exception:
				pass
			return ops
		def _apply_plugin_ops(text, top, ops):
			if ft in state.plugin_hl:
				entry = state.plugin_hl[ft]
				plugin_name = entry.get('plugin', '') if isinstance(entry, dict) else ''
				if isinstance(entry, dict):
					func = entry.get('func', None)
					cond = entry.get('if', True)
					hl = entry.get('hl', '{}')
					else_fn = entry.get('else', None)
					if func is not None:
						try:
							exec(func, vars(state))
						except Exception as error:
							error = str(error)
							msg = f'There was an error in running the function "{func}" before syntax highlighting by the plugin "{plugin_name}":\n{error}'
							state.root.error('Error', msg)
					try:
						cond_result = bool(eval(cond, vars(state)))
					except Exception as error:
						msg = f'There was an error in evaluating the condition "{cond}" for syntax highlighting by the plugin "{plugin_name}":\n{error}'
						state.root.error('Error', msg)
						cond_result = False
					if cond_result:
						try:
							hl_value = eval(hl, vars(state))
						except Exception as error:
							error = str(error)
							msg = f'There was an error in syntax highlighting of the plugin "{plugin_name}":\n{error}'
							state.root.error('Error', msg)
							hl_value = {}
						if callable(hl_value):
							try:
								hl_value(text, top, ops)
							except Exception as error:
								error = str(error)
								msg = f'There was an error in syntax highlighting of the plugin "{plugin_name}":\n{error}'
								state.root.error('Error', msg)
						else:
							for tag, (pat, theme_key) in hl_value.items():
								try:
									for m in pat.finditer(text):
										ops.append(('add', tag, f'{top}+{m.start()}c', f'{top}+{m.end()}c'))
									ops.append(('config', tag, state.theme[theme_key]))
								except Exception as error:
									error = str(error)
									msg = f'There was an error in syntax highlighting of the plugin "{plugin_name}":\n{error}'
									state.root.error('Error', msg)
					elif else_fn is not None:
						try:
							exec(else_fn, vars(state))
						except Exception as error:
							error = str(error)
							msg = f'There was an error in running the else block in the syntax highlighting of the plugin "{plugin_name}":\n{error}'
							state.root.error('Error', msg)
				elif callable(entry):
					try:
						entry(text, top, ops)
					except Exception as error:
						error = str(error)
						msg = f'There was an error in syntax highlighting of the plugin "{plugin_name}":\n{error}'
						state.root.error('Error', msg)
				else:
					for tag, (pat, theme_key) in entry.items():
						try:
							for m in pat.finditer(text):
								ops.append(('add', tag, f'{top}+{m.start()}c', f'{top}+{m.end()}c'))
						except Exception as error:
							error = str(error)
							msg = f'There was an error in syntax highlighting of the plugin "{plugin_name}":\n{error}'
							state.root.error('Error', msg)
		def do_hl():
			results = [(member, own_type, top, bottom, text, _build_ops(own_type, top, bottom, text, pre_text)) for member, own_type, top, bottom, text, pre_text in snapshots]
			self._main_queue.put(lambda: _finish_all(results))
		def _done():
			self._ha_running[0] = False
			pending = self._ha_pending[0]
			if pending is not None:
				self._ha_pending[0] = None
				self.ha(pending)
		def _finish_all(results):
			def _process(i):
				if i >= len(results):
					_done()
					return
				member, own_type, top, bottom, text, ops = results[i]
				_apply_plugin_ops(text, top, ops)
				_finish_one(member, own_type, top, bottom, text, ops, lambda: _process(i + 1))
			_process(0)
		def _finish_one(member, own_type, top, bottom, text, ops, on_done):
			try:
				if own_type.get(top, bottom) != text:
					on_done()
					return
				all_tags = set(own_type.tag_names())
				removable_tags = [tag for tag in all_tags if tag not in state._PYTHON_EDITOR_HL_SKIP_REMOVE_TAGS and (tag not in state.skiptags or member.hmode not in state.skiptags[tag])]
				_HA_CHUNK_SIZE = 4000
				def _apply_chunk(start):
					try:
						end = min(start + _HA_CHUNK_SIZE, len(ops))
						for op in ops[start:end]:
							if op[0] == 'remove_all':
								for tag in removable_tags:
									own_type.tag_remove(tag, top, bottom)
							elif op[0] == 'add':
								for tag in removable_tags:
									if tag != op[1] and not (ft == 'latex' and tag == 'hlb' and op[1] != 'hlb'):
										own_type.tag_remove(tag, op[2], op[3])
								own_type.tag_add(op[1], op[2], op[3])
								if ft == 'latex' and op[1] != 'hlb':
									own_type.tag_raise(op[1], 'hlb')
							elif op[0] == 'remove':
								own_type.tag_remove(op[1], op[2], op[3])
							elif op[0] == 'config':
								exec("own_type.tag_config('" + op[1] + "'," + op[2] + ')')
							elif op[0] == 'clear_other':
								for tag in removable_tags:
									own_type.tag_remove(tag, op[1], op[2])
						own_type.tag_raise('sel')
						if end < len(ops):
							member._ha_apply_after_id = state.root.after(0, lambda: _apply_chunk(end))
						else:
							member._ha_apply_after_id = None
							on_done()
					except Exception as error:
						member._ha_apply_after_id = None
						error = str(error)
						state.root.error('Error!', f'Error:{error}\nInvalid colour settings.\nQuitting syntax highlighting.')
						on_done()
				_apply_chunk(0)
			except Exception as error:
				error = str(error)
				state.root.error('Error!', f'Error:{error}\nInvalid colour settings.\nQuitting syntax highlighting.')
				on_done()
		threading.Thread(target = do_hl, daemon = True).start()
	def init_hl_tags(self):
		[self._own_type.tag_delete(tag) for tag in ('hpa', 'hpb', 'hpv', 'hpi', 'hpf', 'hpx', 'hpfa', 'hpm', 'hpo', 'hpd', 'hpc', 'hla', 'hlb', 'hld', 'hle', 'hlf', 'hlg', 'hlh', 'hstuff', 'hattr', 'hstr', 'hcmt', 'hmh1', 'hmh2', 'hmh3', 'hmh4', 'hmh5', 'hmh6', 'hmb', 'hmi', 'hmbi')]
		exec("self._own_type.tag_config('hpa'," + state.theme['python:keywords'].replace('type_', 'self._own_type') + ')')
		exec("self._own_type.tag_config('hpb'," + state.theme['python:inbuilt'].replace('type_', 'self._own_type') + ')')
		exec("self._own_type.tag_config('hpv'," + state.theme['python:variable_names'].replace('type_', 'self._own_type') + ')')
		exec("self._own_type.tag_config('hpi'," + state.theme['python:class_instances'].replace('type_', 'self._own_type') + ')')
		exec("self._own_type.tag_config('hpf'," + state.theme['python:function_names'].replace('type_', 'self._own_type') + ')')
		exec("self._own_type.tag_config('hpx'," + state.theme['python:class_names'].replace('type_', 'self._own_type') + ')')
		exec("self._own_type.tag_config('hpfa'," + state.theme['python:function_arguments'].replace('type_', 'self._own_type') + ')')
		exec("self._own_type.tag_config('hpm'," + state.theme['python:module_names'].replace('type_', 'self._own_type') + ')')
		exec("self._own_type.tag_config('hpo'," + state.theme['python:operators'].replace('type_', 'self._own_type') + ')')
		exec("self._own_type.tag_config('hpd'," + state.theme['python:strings'].replace('type_', 'self._own_type') + ')')
		exec("self._own_type.tag_config('hpc'," + state.theme['python:comments'].replace('type_', 'self._own_type') + ')')
		exec("self._own_type.tag_config('hla'," + state.theme['latex:inlinemath'].replace('type_', 'self._own_type') + ')')
		exec("self._own_type.tag_config('hlb'," + state.theme['latex:environment'].replace('type_', 'self._own_type') + ')')
		exec("self._own_type.tag_config('hld'," + state.theme['latex:commands'].replace('type_', 'self._own_type') + ')')
		exec("self._own_type.tag_config('hle'," + state.theme['latex:arguments'].replace('type_', 'self._own_type') + ')')
		exec("self._own_type.tag_config('hlf'," + state.theme['latex:operators'].replace('type_', 'self._own_type') + ')')
		exec("self._own_type.tag_config('hlg'," + state.theme['latex:square_brackets'].replace('type_', 'self._own_type') + ')')
		exec("self._own_type.tag_config('hlh'," + state.theme['latex:comments'].replace('type_', 'self._own_type') + ')')
		exec("self._own_type.tag_config('hstuff'," + state.theme['html:tags'].replace('type_', 'self._own_type') + ')')
		exec("self._own_type.tag_config('hattr'," + state.theme['html:attributes'].replace('type_', 'self._own_type') + ')')
		exec("self._own_type.tag_config('hstr'," + state.theme['html:quotes'].replace('type_', 'self._own_type') + ')')
		exec("self._own_type.tag_config('hcmt'," + state.theme['html:comments'].replace('type_', 'self._own_type') + ')')
		exec("self._own_type.tag_config('hmh1'," + state.theme['markdown:headers1'].replace('type_', 'self._own_type') + ')')
		exec("self._own_type.tag_config('hmh2'," + state.theme['markdown:headers2'].replace('type_', 'self._own_type') + ')')
		exec("self._own_type.tag_config('hmh3'," + state.theme['markdown:headers3'].replace('type_', 'self._own_type') + ')')
		exec("self._own_type.tag_config('hmh4'," + state.theme['markdown:headers4'].replace('type_', 'self._own_type') + ')')
		exec("self._own_type.tag_config('hmh5'," + state.theme['markdown:headers5'].replace('type_', 'self._own_type') + ')')
		exec("self._own_type.tag_config('hmh6'," + state.theme['markdown:headers6'].replace('type_', 'self._own_type') + ')')
		exec("self._own_type.tag_config('hmb'," + state.theme['markdown:bold'].replace('type_', 'self._own_type') + ')')
		exec("self._own_type.tag_config('hmi'," + state.theme['markdown:italic'].replace('type_', 'self._own_type') + ')')
		exec("self._own_type.tag_config('hmbi'," + state.theme['markdown:bold_italic'].replace('type_', 'self._own_type') + ')')
		exec("self._own_type.tag_config('hms'," + state.theme['markdown:strike'].replace('type_', 'self._own_type') + ')')
		exec("self._own_type.tag_config('hmc'," + state.theme['markdown:inlinecode'].replace('type_', 'self._own_type') + ')')
		exec("self._own_type.tag_config('hml'," + state.theme['markdown:links'].replace('type_', 'self._own_type') + ')')
		exec("self._own_type.tag_config('hmq'," + state.theme['markdown:blockquotes'].replace('type_', 'self._own_type') + ')')
		exec("self._own_type.tag_config('hmf'," + state.theme['markdown:codeblocks'].replace('type_', 'self._own_type') + ')')
		exec("self._own_type.tag_config('marked'," + state.theme['pynotes:marked'].replace('type_', 'self._own_type') + ')')
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
	def init_plugin_tags(self):
		for ft, entry in state.plugin_hl.items():
			mapping = None
			if isinstance(entry, dict):
				if 'hl' not in entry:
					mapping = entry
			elif not callable(entry):
				mapping = entry
			if mapping is None:
				continue
			for tag, (pat, theme_key) in mapping.items():
				try:
					exec("self._own_type.tag_config('" + tag + "'," + state.theme[theme_key].replace('type_', 'self._own_type') + ')')
				except Exception:
					pass
	def selupdate(self):
		if self.selectionpoint:
			self.type_.tag_remove('sel', '1.0', 'end')
			if self.type_.compare(self.selectionpoint, '<=', 'insert'):
				self.type_.tag_add('sel', self.selectionpoint, 'insert')
			else:
				self.type_.tag_add('sel', 'insert', self.selectionpoint)
	def keypress(self):
		if not self.winfo_exists():
			return
		self.selupdate()
		self._python_edit_generation[0] += 1
		self.ln.redraw()
		self.trigger_filesize()
		self.trigger_undo_set()
		if self.hmode == 'python':
			self.tabs.tab(self.sf, state = 'normal')
			self.python_trigger_name_scan()
		else:
			self.tabs.tab(self.sf, state = 'hidden')
			self.trigger_ha(self.hmode)
		self._sync_wanttitle()
		if self.title:
			if self.hmode in ['png', 'pdf', 'epub']:
				for member in self._group_members():
					member.fileinfoconfig(filename = os.path.basename(self.title), filesaved = 'Read Only File')
			else:
				for member in self._group_members():
					member.fileinfoconfig(filename = os.path.basename(self.title))
		else:
			if (self.view_master or self) is state.active and not state.pcsettitle:
				for member in self._group_members():
					member.fileinfoconfig(filename = 'Untitled', filesaved = 'Untitled File')
			else:
				for member in self._group_members():
					member.fileinfoconfig(filename = 'Untitled')
		self.trigger_unsaved()
		if not self.title:
			if self.type_.get('1.0', 'end-1c'):
				self.unsaved = True
			else:
				self.unsaved = False
	def sethmenu(self, mode):
		try:
			self.m.delete('Python')
		except Exception:
			pass
		try:
			self.m.delete('LaTeX')
		except Exception:
			pass
		if mode == 'python':
			self.m.insert_cascade(self.m.index('Options') + 1, label = 'Python', menu = state.pm)
		elif mode == 'latex':
			self.m.insert_cascade(self.m.index('Options') + 1, label = 'LaTeX', menu = state.lm)
	def pchmode(self, mode):
		if self.view_master:
			return self.view_master.pchmode(mode)
		if self.hmode in ['png', 'pdf', 'epub']:
			return
		pycode.pcrunhook('before', 'change-hmode', mode)
		[self.type_.tag_remove(tag, '1.0', 'end') for tag in ('hpa', 'hpb', 'hpv', 'hpi', 'hpf', 'hpx', 'hpfa', 'hpm', 'hpo', 'hpd', 'hpc', 'hla', 'hlb', 'hld', 'hle', 'hlf', 'hlg', 'hlh', 'hstuff', 'hattr', 'hstr', 'hcmt', 'hmh1', 'hmh2', 'hmh3', 'hmh4', 'hmh5', 'hmh6', 'hmb', 'hmi', 'hmbi')]
		if mode == 'python' or mode == 'py':
			self.sethmenu('python')
			self.tabs.tab(self.sf, state = 'normal')
			self.tabs.tab(self.ef, state = 'hidden')
			self.lfouter.pack_forget()
			self.hmode = 'python'
			self.fileinfoconfig(filetype = 'Python File (*.py)')
			self.python_trigger_name_scan()
		elif mode == 'latex' or mode == 'la':
			self.sethmenu('latex')
			self.tabs.tab(self.sf, state = 'hidden')
			self.tabs.tab(self.ef, state = 'hidden')
			self.lfouter.pack(padx = 10, pady = 10, side = 'top', fill = 'x', before = self.fileinfo)
			self.hmode = 'latex'
			self.fileinfoconfig(filetype = 'LaTeX / TeX File (*.tex)')
		elif mode == 'normal' or mode == 'norm':
			self.sethmenu(None)
			self.tabs.tab(self.sf, state = 'hidden')
			self.tabs.tab(self.ef, state = 'hidden')
			self.lfouter.pack_forget()
			self.hmode = 'normal'
			self.fileinfoconfig(filetype = 'Plain Text (*.*)')
		elif mode == 'email' or mode == 'em':
			self.sethmenu(None)
			self.hmode = 'email'
			self.fileinfoconfig(filetype = 'Plain Text (*.*) (Email)')
			self.tabs.tab(self.sf, state = 'hidden')
			self.tabs.tab(self.ef, state = 'normal')
		elif mode == 'html':
			self.sethmenu(None)
			self.hmode = 'html'
			self.fileinfoconfig(filetype = 'HTML File (*.html)')
			self.tabs.tab(self.sf, state = 'hidden')
			self.tabs.tab(self.ef, state = 'hidden')
			self.lfouter.pack_forget()
		elif mode == 'markdown' or mode == 'md':
			self.sethmenu(None)
			self.tabs.tab(self.sf, state = 'hidden')
			self.tabs.tab(self.ef, state = 'hidden')
			self.lfouter.pack_forget()
			self.hmode = 'markdown'
			self.fileinfoconfig(filetype = 'Markdown File (*.md)')
		elif mode in state.plgnhmodes:
			try:
				self.hmode = mode
				exec(state.plgnhmodes[mode][1], vars(state))
			except Exception as error:
				error = str(error)
				state.root.error('Error!', f'There was an error in switching to the HMode {mode} from the plugin "{os.path.basename(os.path.normpath(state.plgnhmodes[mode][0]))}":\n{error}')
		utils.show(f'{self.hmode} hmode')
		self.keypress()
		for child in self.view_children:
			child._sync_chrome()
		pycode.pcrunhook('after', 'change-hmode', mode)
	def rp(self):
		if not self.title:
			f = open(f'{homedir}/.local/share/PyNotes/tempfiles/tempcode', 'w', encoding = 'utf-8')
			f.write(self.type_.get('1.0', 'end-1c'))
			f.close()
			file = f'{homedir}/.local/share/PyNotes/tempfiles/tempcode'
		else:
			file = self.title
			self.sv(file)
		terminal.term([state.pythonexecutable, file], title = f'*{file} Running*', endmessage = '--- Python code finished, press any key to continue ---')
	def hp(self):
		if not self.title:
			f = open(f'{homedir}/.local/share/PyNotes/tempfiles/tempcode', 'w', encoding = 'utf-8')
			f.write(self.type_.get('1.0', 'end-1c'))
			f.close()
			file = f'{homedir}/.local/share/PyNotes/tempfiles/tempcode'
		else:
			file = self.title
			self.sv(file)
		if platform.system() == 'Linux':
			subprocess.run(['xdg-open', file], cwd = os.path.dirname(file))
		else:
			subprocess.run(['start', file], cwd = os.path.dirname(file))
	def runtex(self, compiler):
		if not self.title:
			f = open(f'{homedir}/.local/share/PyNotes/tempfiles/tempcode', 'w', encoding = 'utf-8')
			f.write(self.type_.get('1.0', 'end-1c'))
			f.close()
			file = f'{homedir}/.local/share/PyNotes/tempfiles/tempcode'
		else:
			file = self.title
			self.sv(file)
		compiler += 'latex'
		if not shutil.which(compiler):
			state.root.error('Error', f'Error in running LaTeX - {compiler} is not installed')
			return
		if os.path.splitext(file)[1] == '.tex':
			pdf_ = os.path.splitext(file)[0]
		else:
			pdf_ = file
		pdf_ += '.pdf'
		try:
			os.remove(pdf_)
		except Exception:
			pass
		terminal.term([compiler, file, f'--output-directory={os.path.dirname(file)}'], title = f'*{file} Compiling*', endmessage = '--- LaTeX compiling finished, press any key to continue ---', blocking = True)
		dialogs.pdf(file)
	def f5(self):
		if self._file_watch_prompt_pending:
			utils.show('select \'Discard Changes & Reload\' or \'Ignore\' external changes before loading another file')
			return
		pycode.pcrunhook('before', 'run-code')
		if self.hmode == 'python':
			self.rp()
		elif self.hmode == 'latex':
			self.runtex('lua')
		elif self.hmode == 'html':
			self.hp()
		else:
			utils.show('hmode not in python / latex / html')
			return
		utils.show(f'run {self.hmode} code')
		pycode.pcrunhook('after', 'run-code')
	def indent(self):
		self.type_.edit_separator()
		if not self.hmode == 'python':
			return
		l = int(self.type_.index('insert').split('.')[0])
		self.type_.insert(f'insert', '\n')
		line = self.type_.get(f'{l}.0', f'{l}.end')
		whitespace = re.match(r'\s*', line).group()
		self.type_.insert(f'{l + 1}.0', whitespace)
		line = re.sub(r'\'[^\'\\]*(?:\\.[^\'\\]*)*\'|"[^"\\]*(?:\\.[^"\\]*)*"', '', line)
		line = re.sub(r'#.*', '', line).strip()
		if state.taborspace:
			indentthing = '    '
		else:
			indentthing = '	'
		if not line:
			return 'break'
		if line[-1] == ':':
			self.type_.insert(f'{l + 1}.0', indentthing)
		self.type_.edit_separator()
		return 'break'
	def gl(self, l = None):
		if l is None:
			l = utils.prompt('Go to line: ')
		if type(l) == str:
			l = l.strip()
		if not l:
			return
		try:
			l = int(l)
		except Exception:
			utils.show(f'cannot go to line number \'{l}\'')
			return
		else:
			utils.show(f'go to line no. {l}')
			self.type_.see(f'{l}.0')
			self.type_.mark_set('insert', f'{l}.0')
			self.type_.tag_add('sel', f'{l}.0', f'{l}.end')
	def selall(self):
		utils.show('select all text')
		self.type_.tag_add('sel', '1.0', 'end')
		return 'break'
	def cp(self):
		try:
			select = self.type_.get('sel.first', 'sel.last')
		except Exception:
			utils.show('no text is selected')
			return
		else:
			pycode.pcrunhook('before', 'copy-text', select)
			utils.show('copy text')
		state.root.clipboard_clear()
		state.root.clipboard_append(select)
		pycode.pcrunhook('after', 'copy-text', select)
	def cut(self):
		try:
			select = self.type_.get('sel.first', 'sel.last')
		except Exception:
			utils.show('no text is selected')
			return
		else:
			pycode.pcrunhook('before', 'cut-text', select)
			utils.show('cut text')
		self.type_.delete('sel.first', 'sel.last')
		state.root.clipboard_clear()
		state.root.clipboard_append(select)
		utils.show('cut text')
		pycode.pcrunhook('after', 'cut-text', select)
	def spk(self):
		try:
			select = self.type_.get('sel.first', 'sel.last')
		except Exception:
			utils.show('no text is selected')
			return
		else:
			utils.show('speak selected text')
			speakthread = threading.Thread(target = speech.actualspk, args = (select,), daemon = True)
			speakthread.start()
	def pst(self):
		try:
			text = state.root.clipboard_get()
		except Exception:
			utils.show('no text is on clipboard')
			return
		else:
			pycode.pcrunhook('before', 'paste-text', text)
			utils.show('paste text')
		self.type_.edit_separator()
		self.type_.insert('insert', text)
		self.type_.edit_separator()
		pycode.pcrunhook('after', 'paste-text', text)
		return 'break'
	def ptb(self):
		if self.type_.yview()[0] == 0.0:
			utils.show('already at beginning')
			return
		pycode.pcrunhook('before', 'previous-page')
		self.type_.yview_scroll(-1, 'pages')
		utils.show('go to previous page')
		pycode.pcrunhook('after', 'previous-page')
	def ptf(self):
		if self.type_.yview()[1] == 1.0:
			utils.show('already at end')
			return
		pycode.pcrunhook('before', 'next-page')
		self.type_.yview_scroll(1, 'pages')
		utils.show('go to next page')
		pycode.pcrunhook('after', 'next-page')
	def undo(self):
		pycode.pcrunhook('before', 'undo')
		try:
			self.type_.edit_undo()
			utils.show('undoed edit')
			pycode.pcrunhook('after', 'undo')
		except Exception:
			utils.show('nothing to undo')
	def redo(self):
		pycode.pcrunhook('before', 'redo')
		try:
			self.type_.edit_redo()
			utils.show('redoed edit')
			pycode.pcrunhook('after', 'redo')
		except Exception:
			utils.show('nothing to redo')
	def _main_poll(self):
		try:
			while True:
				task = self._main_queue.get_nowait()
				task()
		except Exception:
			pass
		self._main_poll_after_id = self._own_type.after(10, self._main_poll)
	def type_setview(self):
		new_region = self.type_getvisible()
		if new_region != self._prev_visible_region:
			self._prev_visible_region = new_region
			self.type_top, self.type_bottom = new_region
			self.trigger_ha(self.hmode)
		else:
			self.type_top, self.type_bottom = new_region
		self._type_setview_after_id = self.mf.after(10, self.type_setview)
	def do_backup(self):
		if all((not self.hmode in ['png', 'pdf', 'epub'], state.bfr, self.title)):
			open(os.path.join(os.path.dirname(os.path.splitext(self.title)[0]), '.' + os.path.basename(os.path.splitext(self.title)[0]) + 'backpynotes' + os.path.splitext(self.title)[1]), 'w+', encoding = 'utf-8').write(self.type_.get('1.0', 'end'))
			utils.show('saved backup')
		self._do_backup_after_id = self.mf.after(10000, self.do_backup)
	def emailsetup(self, saved = None):
		global e
		global p
		global s
		global po
		attachments = []
		def removeattach():
			def actualremoveattachment(attachment):
				del self.attachmentslist[attachment]
				del attachments[attachment]
				self.attachmentslistwidget.config(text = 'Attachments: ' + ' , '.join(self.attachmentslist))
				raw.destroy()
			if self.attachmentslist:
				raw = state.root.subwin()
				for i in range(len(self.attachmentslist)):
					attachment = self.attachmentslist[i]
					raw.button(text = attachment, command = lambda i = i: actualremoveattachment(i)).grid(column = i % 5, row = mathmod.floor(i / 5), sticky = 'ew')
		def attach():
			fn = dialogs.openfileget(prompttext = 'Email Attachment File: ', filetypes = (('All Files', '*')))
			if fn:
				try:
					with open(fn, 'rb') as attachment:
						part = MIMEBase('application', 'octet-stream')
						part.set_payload(attachment.read())
						encoders.encode_base64(part)
						part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(fn)}')
						if not os.path.basename(fn) in self.attachmentslist:
							attachments.append(part)
							self.attachmentslist.append(os.path.basename(fn))
							self.attachmentslistwidget.config(text = 'Attachments: ' + ' , '.join(self.attachmentslist))
				except Exception as error:
					error = str(error)
					state.root.error('Error', error)
		def changeinfo():
			def emailsetupother():
				global e
				global p
				global s
				global po
				self.entryframe.pack(padx = 10, pady = 10, fill = 'x', anchor = 'n', expand = True)
				self.buttonframe.pack(padx = 10, pady = 10, fill = 'x', anchor = 'n', expand = True)
				self.emailtextbox.pack(fill = 'both', expand = True, padx = 10, pady = 10)
				e = self.email.get()
				p = self.password.get()
				s = self.server.get()
				po = self.port.get()
				file = open(f'{homedir}/.pynotesemailconfig', 'w+', encoding = 'utf-8')
				file.write(f'{e}\n{p}\n{s}\n{po}')
				file.close()
				encryptdecrypt(f'{homedir}/.pynotesemailconfig')
				self.loginframe.pack_forget()
			self.entryframe.pack_forget()
			self.buttonframe.pack_forget()
			self.emailtextbox.pack_forget()
			self.loginframe = state.root.frame(master = self.ef)
			self.loginframe.pack(expand = True)
			state.root.text(master = self.loginframe, text = 'Email:').grid(column = 0, row = 0, padx = 10, pady = 10)
			self.email = state.root.entry(master = self.loginframe)
			self.email.grid(column = 1, row = 0, padx = 10, pady = 10)
			state.root.text(master = self.loginframe, text = 'Password:').grid(column = 0, row = 1, padx = 10, pady = 10)
			self.password = state.root.entry(master = self.loginframe, show = '*')
			self.password.grid(column = 1, row = 1, padx = 10, pady = 10)
			state.root.text(master = self.loginframe, text = 'Smtp Server:').grid(column = 0, row = 2, padx = 10, pady = 10)
			self.server = state.root.entry(master = self.loginframe)
			self.server.grid(column = 1, row = 2, padx = 10, pady = 10)
			state.root.text(master = self.loginframe, text = 'Smtp Port:').grid(column = 0, row = 3, padx = 10, pady = 10)
			self.port = state.root.entry(master = self.loginframe)
			self.port.grid(column = 1, row = 3, padx = 10, pady = 10)
			state.root.button(master = self.loginframe, text = 'Done', command = emailsetupother).grid(column = 1, row = 4, padx = 10, pady = 10, sticky = 'e')
			self._bind_focus_recursive(self.loginframe)
		def sendemail():
			global e
			global p
			global s
			global po
			recipients = self.recipiententry.get().split(',')
			subject = self.subjectentry.get()
			if not subject:
				subject = '(No Subject)'
			body = self.emailtextbox.get('1.0', 'end-1c')
			for recipient in recipients:
				if recipient:
					message = MIMEMultipart()
					message['From'] = e
					message['To'] = recipient
					message['Subject'] = subject
					message.attach(MIMEText(body, 'plain'))
					try:
						for attachment in attachments:
							message.attach(attachment)
						with smtplib.SMTP_SSL(s, po) as server:
							server.login(e, p)
							server.sendmail(e, recipient, message.as_string())
					except Exception as error:
						error = str(error)
						state.root.error('Error', error)
						utils.show('email failed')
						return
			self.emailtextbox.delete('1.0', 'end')
			self.recipiententry.delete(0, 'end')
			attachments.clear()
			self.attachmentslist.clear()
			self.attachmentslistwidget.config(text = 'Attachments:')
			self.subjectentry.delete(0, 'end')
			utils.show('email sent')
			state.root.info('Info', 'Email Sent Successfully!')
			return 'break'
		def spellcheck():
			if not state.emailwordlist:
				return
			self.emailtextbox.tag_remove('wrong', '1.0', 'end')
			n = '1.0'
			search = r'\w+'
			while True:
				count = state.root.intvar()
				n = self.emailtextbox.search(search, n, nocase = 1, count = count, stopindex = 'end', regexp = True)
				if not n:
					break
				nn = '%s+%dc' % (n, count.get())
				if not self.emailtextbox.get(n, nn).lower() in state.emailwordlist and len(self.emailtextbox.get(n, nn)) > 1:
					try:
						int(self.emailtextbox.get(n, nn))
					except Exception:
						self.emailtextbox.tag_add('wrong', n, nn)
				n = nn
			n = '1.0'
		if not saved:
			e = self.email.get()
			p = self.password.get()
			s = self.server.get()
			po = self.port.get()
			self.loginframe.pack_forget()
			ans = state.root.ask('', 'Do you want PyNotes to save your email and password?', ['yes', 'no'])
			if ans:
				file = open(f'{homedir}/.pynotesemailconfig', 'w+', encoding = 'utf-8')
				file.write(f'{e}\n{p}\n{s}\n{po}')
				file.close()
				encryptdecrypt(f'{homedir}/.pynotesemailconfig')
		elif saved == 'file':
			encryptdecrypt(f'{homedir}/.pynotesemailconfig')
			file = open(f'{homedir}/.pynotesemailconfig', 'r', encoding = 'utf-8').read().split('\n')
			encryptdecrypt(f'{homedir}/.pynotesemailconfig')
			e = file[0]
			p = file[1]
			s = file[2]
			po = file[3]
		self._email_logged_in = True
		self.entryframe = state.root.frame(master = self.ef)
		self.recipiententry = state.root.entry(master = self.entryframe)
		state.root.text(master = self.entryframe, text = 'Recipients (separate by commas):').grid(column = 0, row = 0, padx = 10, pady = 10, sticky = 'e')
		self.recipiententry.grid(column = 1, row = 0, padx = 10, pady = 10, sticky = 'ew')
		state.root.text(master = self.entryframe, text = 'Subject:').grid(column = 0, row = 1, padx = 10, pady = 10, sticky = 'e')
		self.subjectentry = state.root.entry(master = self.entryframe)
		self.subjectentry.grid(column = 1, row = 1, padx = 10, pady = 10, sticky = 'ew')
		self.entryframe.pack(padx = 10, pady = 10, fill = 'both', anchor = 'n', expand = True)
		self.entryframe.columnconfigure(1, weight = 1)
		self.buttonframe = state.root.frame(master = self.ef)
		self.buttonframe.pack(padx = 10, pady = 10, fill = 'both', anchor = 'n', expand = True)
		state.root.button(master = self.buttonframe, text = 'Send (Ctrl + Enter)', command = sendemail).pack(fill = 'x', expand = True, padx = 10, pady = 10, side = 'left', anchor = 'n')
		state.root.button(master = self.buttonframe, text = 'Attach', command = attach).pack(fill = 'x', expand = True, padx = 10, pady = 10, side = 'right', anchor = 'n')
		state.root.button(master = self.buttonframe, text = 'Change Info', command = changeinfo).pack(fill = 'x', expand = True, padx = 10, pady = 10, side = 'left', anchor = 'n')
		state.root.button(master = self.buttonframe, text = 'Remove Attachment', command = removeattach).pack(fill = 'x', expand = True, padx = 10, pady = 10, side = 'right', anchor = 'n')
		self.attachmentslist = []
		self.attachmentslistwidget = state.root.text(master = self.buttonframe, text = 'Attachments:')
		self.attachmentslistwidget.pack(fill = 'x', expand = True, padx = 10, pady = 10)
		self.emailtextbox = state.root.textbox(master = self.ef, scrolled = True, font = (monospace, 15))
		self.emailtextbox.tag_config('wrong', underline = True, underlinefg = 'red')
		self.emailtextbox.pack(fill = 'both', expand = True, padx = 10, pady = 10)
		self.emailtextbox.bind('<Control-Return>', lambda event: sendemail())
		self.emailtextbox.bind('<KeyRelease>', lambda event: spellcheck())
		self._bind_focus_recursive(self.ef)
	def _email_session_active(self):
		try:
			e, p, s, po
		except Exception:
			return False
		return bool(e and p and s and po)
	def _add_switch_account_loginframe(self):
		self.loginframe = state.root.frame(master = self.ef)
		self.loginframe.pack(expand = True)
		state.root.text(master = self.loginframe, text = 'Email:').grid(column = 0, row = 0, padx = 10, pady = 10)
		self.email = state.root.entry(master = self.loginframe)
		self.email.grid(column = 1, row = 0, padx = 10, pady = 10)
		state.root.text(master = self.loginframe, text = 'Password:').grid(column = 0, row = 1, padx = 10, pady = 10)
		self.password = state.root.entry(master = self.loginframe, show = '*')
		self.password.grid(column = 1, row = 1, padx = 10, pady = 10)
		state.root.text(master = self.loginframe, text = 'Smtp Server:').grid(column = 0, row = 2, padx = 10, pady = 10)
		self.server = state.root.entry(master = self.loginframe)
		self.server.grid(column = 1, row = 2, padx = 10, pady = 10)
		state.root.text(master = self.loginframe, text = 'Smtp Port:').grid(column = 0, row = 3, padx = 10, pady = 10)
		self.port = state.root.entry(master = self.loginframe)
		self.port.grid(column = 1, row = 3, padx = 10, pady = 10)
		state.root.button(master = self.loginframe, text = 'Let\'s Go!', command = self.emailsetup).grid(column = 1, row = 4, padx = 10, pady = 10, sticky = 'e')
		self._bind_focus_recursive(self.loginframe)
	def _email_tab_reload(self):
		for child in self.ef.winfo_children():
			child.destroy()
		self.emailsetup('memory')
		self._add_switch_account_loginframe()
	def _email_login_poll(self):
		if not self._email_logged_in and self._email_session_active():
			self._email_tab_reload()
		self._email_login_poll_after_id = self.ef.after(2000, self._email_login_poll)
	def _email_login_setup(self):
		if self._email_session_active():
			self.emailsetup('memory')
			self._add_switch_account_loginframe()
			return
		try:
			open(f'{homedir}/.pynotesemailconfig', 'r', encoding = 'utf-8')
		except Exception:
			self.loginframe = state.root.frame(master = self.ef)
			self.loginframe.pack(expand = True)
			state.root.text(master = self.loginframe, text = 'Email:').grid(column = 0, row = 0, padx = 10, pady = 10)
			self.email = state.root.entry(master = self.loginframe)
			self.email.grid(column = 1, row = 0, padx = 10, pady = 10)
			state.root.text(master = self.loginframe, text = 'Password:').grid(column = 0, row = 1, padx = 10, pady = 10)
			self.password = state.root.entry(master = self.loginframe, show = '*')
			self.password.grid(column = 1, row = 1, padx = 10, pady = 10)
			state.root.text(master = self.loginframe, text = 'Smtp Server:').grid(column = 0, row = 2, padx = 10, pady = 10)
			self.server = state.root.entry(master = self.loginframe)
			self.server.grid(column = 1, row = 2, padx = 10, pady = 10)
			state.root.text(master = self.loginframe, text = 'Smtp Port:').grid(column = 0, row = 3, padx = 10, pady = 10)
			self.port = state.root.entry(master = self.loginframe)
			self.port.grid(column = 1, row = 3, padx = 10, pady = 10)
			state.root.button(master = self.loginframe, text = 'Let\'s Go!', command = self.emailsetup).grid(column = 1, row = 4, padx = 10, pady = 10, sticky = 'e')
			self._bind_focus_recursive(self.loginframe)
		else:
			try:
				self.emailsetup('file')
			except Exception:
				state.root.error('Error', 'The saved email details are corrupted. Remaking file.')
				os.remove(f'{homedir}/.pynotesemailconfig')
			self._add_switch_account_loginframe()
	def boldlatex(self):
		try:
			select = self.type_.get('sel.first', 'sel.last')
		except Exception:
			return
		self.type_.edit_separator()
		self.type_.delete('sel.first', 'sel.last')
		self.type_.insert('insert', '{\\bf ' + select + '}')
		self.type_.edit_separator()
		utils.show('bold text latex')
		self.keypress()
	def italiclatex(self):
		try:
			select = self.type_.get('sel.first', 'sel.last')
		except Exception:
			return
		self.type_.edit_separator()
		self.type_.delete('sel.first', 'sel.last')
		self.type_.insert('insert', '\\textit{' + select + '}')
		self.type_.edit_separator()
		utils.show('italic text latex')
		self.keypress()
	def underlinelatex(self):
		try:
			select = self.type_.get('sel.first', 'sel.last')
		except Exception:
			return
		self.type_.edit_separator()
		self.type_.delete('sel.first', 'sel.last')
		self.type_.insert('insert', '\\underline{' + select + '}')
		self.type_.edit_separator()
		utils.show('underline text latex')
		self.keypress()
	def subscriptlatex(self):
		try:
			select = self.type_.get('sel.first', 'sel.last')
		except Exception:
			return
		self.type_.edit_separator()
		self.type_.delete('sel.first', 'sel.last')
		self.type_.insert('insert', '_{' + select + '}')
		self.type_.edit_separator()
		utils.show('subscript text latex')
		self.keypress()
	def superscriptlatex(self):
		try:
			select = self.type_.get('sel.first', 'sel.last')
		except Exception:
			return
		self.type_.edit_separator()
		self.type_.delete('sel.first', 'sel.last')
		self.type_.insert('insert', '^{' + select + '}')
		self.type_.edit_separator()
		utils.show('superscript text latex')
		self.keypress()
	def numberlistlatex(self):
		self.type_.edit_separator()
		try:
			select = self.type_.get('sel.first', 'sel.last')
		except Exception:
			self.type_.insert('insert', '\n\\begin{enumerate}\n\n\\end{enumerate}\n')
		else:
			tryfind = re.findall(r'\\begin{enumerate}.+\\end{enumerate}', select, re.DOTALL)
			if not tryfind:
				select = '\\item ' + select.replace('\n', '\n\\item ').replace('\\item \\item ', '\\item ')
				self.type_.delete('sel.first', 'sel.last')
				self.type_.insert('insert', '\n\\begin{enumerate}\n' + select + '\n\\end{enumerate}\n')
			else:
				keeptext = tryfind[0][len('\\begin{enumerate}'):][:-len('\\end{enumerate}')].replace('\\item ', '')
				self.type_.delete('sel.first', 'sel.last')
				self.type_.insert('insert', keeptext)
		self.type_.edit_separator()
		utils.show('numbered list latex')
		self.keypress()
	def bulletlistlatex(self):
		self.type_.edit_separator()
		try:
			select = self.type_.get('sel.first', 'sel.last')
		except Exception:
			self.type_.insert('insert', '\n\\begin{itemize}\n\n\\end{itemize}\n').replace('\\item \\item ', '\\item ')
		else:
			tryfind = re.findall(r'\\begin{itemize}.+\\end{itemize}', select, re.DOTALL)
			if not tryfind:
				select = '\\item ' + select.replace('\n', '\n\\item ').replace('\\item \\item ', '\\item ')
				self.type_.delete('sel.first', 'sel.last')
				self.type_.insert('insert', '\n\\begin{itemize}\n' + select + '\n\\end{itemize}\n')
			else:
				keeptext = tryfind[0][len('\\begin{itemize}'):][:-len('\\end{itemize}')].replace('\\item ', '')
				self.type_.delete('sel.first', 'sel.last')
				self.type_.insert('insert', keeptext)
		self.type_.edit_separator()
		utils.show('bulleted list latex')
		self.keypress()
	def paragraphlatex(self):
		self.type_.edit_separator()
		self.type_.insert('insert', '\\par\n')
		utils.show('new paragraph latex')
		self.keypress()
	def equationlatex(self):
		self.type_.edit_separator()
		try:
			select = self.type_.get('sel.first', 'sel.last')
		except Exception:
			self.type_.insert('insert', '\n\\begin{equation}\n\\begin{split}\n\n\\end{split}\n\\end{equation}\n')
		else:
			tryfind = re.findall(r'\\begin{equation}.+\\end{equation}', select, re.DOTALL)
			if not tryfind:
				select = select.replace('\n', '\\\\\n').replace('\\\\\\\\', '\\\\')
				self.type_.delete('sel.first', 'sel.last')
				self.type_.insert('insert', '\n\\begin{equation}\n' + select + '\n\\end{equation}\n')
			else:
				keeptext = tryfind[0][len('\\begin{equation}'):][:-len('\\end{equation}')].replace('\\', '')
				self.type_.delete('sel.first', 'sel.last')
				self.type_.insert('insert', keeptext)
		self.type_.edit_separator()
		utils.show('equation latex')
		self.keypress()
	def sectionlatex(self, typeofsection):
		self.type_.edit_separator()
		typeofsection = typeofsection.lower()
		secname = 'Section'
		if secname:
			self.type_.insert('insert', f'\n\\{typeofsection}' + '{' + secname + '}\n')
		self.type_.edit_separator()
		utils.show(f'new {typeofsection} latex')
		self.keypress()
	def mathlatex(self, whichchar):
		self.type_.edit_separator()
		original = ['Multiplication', 'Division', 'Less or equal', 'More or equal', 'Not equal', 'Infinity', 'Summation', 'Integral', 'Pi', 'Theta', 'Alpha Lower', 'Alpha Upper', 'Inline Math']
		replaces = ['\\times', '\\div', '\\leq', '\\meq', '\\neq', '\\infty', '\\sum', '\\int', '\\pi', '\\theta', '\\alpha', '\\Alpha', '$$']
		whichchar = replaces[original.index(whichchar)]
		self.type_.insert('insert', whichchar)
		self.type_.edit_separator()
		utils.show('insert math latex')
		self.keypress()
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
				if 'wrapcont' in self.shellcmd.tag_names(f'{_rl}.0'):
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
			self.shellcmd.tag_config('prompt', foreground = 'green', font = (monospace, 14, 'bold'))
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
			widget = terminal.Terminal(self.sf, [state.pythonexecutable], None, nocolor = True)
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
		self._shellbuttons = state.root.frame(master = self.sf)
		clearshell = state.root.button(master = self._shellbuttons, text = 'Clear Shell', command = cs)
		killshell = state.root.button(master = self._shellbuttons, text = 'Restart Shell', command = ks)
		self._shellbuttons.pack(side = 'bottom', fill = 'x')
		clearshell.pack(anchor = 'sw', side = 'left', padx = 10, pady = 10)
		killshell.pack(anchor = 'sw', side = 'left', padx = 10, pady = 10)
		self.shellcmd = _make_shellcmd()
		def shell_setview():
			self.hapyshell()
			self._shell_setview_after_id = self.sf.after(50, shell_setview)
		self._shell_setview_after_id = self.sf.after(50, shell_setview)
def _init_hl_tags():
	for buffer in state.all_buffers:
		if isinstance(buffer, Editor):
			buffer.init_hl_tags()
def _init_pythonshell_hl_tags():
	for buffer in state.all_buffers:
		if isinstance(buffer, Editor):
			buffer.init_pythonshell_hl_tags()
def _init_plugin_tags():
	for buffer in state.all_buffers:
		if isinstance(buffer, Editor):
			buffer.init_plugin_tags()
def _find_closing_brace(text, start):
	depth = 1
	i = start + 1
	while i < len(text) and depth > 0:
		if text[i] == '\\' and i + 1 < len(text):
			i += 2
			continue
		if text[i] == '{':
			depth += 1
		elif text[i] == '}':
			depth -= 1
		i += 1
	return i if depth == 0 else len(text)
def _find_closing_bracket(text, start):
	depth = 1
	i = start + 1
	while i < len(text) and depth > 0:
		if text[i] == '\\' and i + 1 < len(text):
			i += 2
			continue
		if text[i] == '[':
			depth += 1
		elif text[i] == ']':
			depth -= 1
		i += 1
	return i if depth == 0 else len(text)
def _find_closing_tag(text, start):
	i = start + 1
	in_quote = None
	while i < len(text):
		if text[i] == '\\' and i + 1 < len(text) and in_quote:
			i += 2
			continue
		if in_quote:
			if text[i] == in_quote:
				in_quote = None
		else:
			if text[i] in ('"', '\''):
				in_quote = text[i]
			elif text[i] == '>':
				return i + 1
		i += 1
	return len(text)
def _python_bytecol_to_charcol(line_str, bytecol):
	if bytecol <= 0:
		return bytecol
	encoded = line_str.encode('utf-8')
	if bytecol >= len(encoded):
		return len(line_str)
	return len(encoded[:bytecol].decode('utf-8', 'ignore'))
_PYTHON_KW_PAT = re.compile(r'(?<!\.)\b(?:' + '|'.join(re.escape(k) for k in keyword.kwlist) + r')\b')
_PYTHON_OP_PAT = re.compile(r'\*\*=|//=|<<=|>>=|:=|==|!=|<=|>=|\+=|-=|\*=|/=|%=|&=|\|=|\^=|@=|->|\*\*|//|<<|>>|[+\-*/%@&|^~=<>]')
_LH_PAT = re.compile(r'(?<!\\)%[^\n]*(?:\n|$)')
_LATEX_MATH_PAT = re.compile(r'\$\$[\s\S]*?\$\$|\\\[[\s\S]*?\\\]|\\\([\s\S]*?\\\)|\$(?!\$)(?:[^$\\]|\\.)*?\$(?!\$)')
_HC_PAT = re.compile(r'<!--.*?-->', re.DOTALL)
_HTML_ATTR_PAT = re.compile(r'\s([\w:-]+)\s*=\s*("(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\'|[^\s"\'=<>]+)', re.IGNORECASE)
_HTML_BOOL_ATTR_PAT = re.compile(r'\b(?:async|autofocus|autoplay|checked|controls|default|defer|disabled|formnovalidate|hidden|ismap|loop|multiple|muted|nomodule|novalidate|open|readonly|required|reversed|selected)\b', re.IGNORECASE)
_MDH_PAT = re.compile(r'(?m)^(#{1,6})(?:[ \t].*)?$')
_MDBI_PAT = re.compile(r'(?<!\\)\*\*\*(?:\\.|[^*\n])+?\*\*\*|(?<!\\)___(?:\\.|[^_\n])+?___|(?<!\\)\*\*_(?:\\.|[^_\n])+?_\*\*|(?<!\\)__\*(?:\\.|[^*\n])+?\*__|(?<!\\)\*__(?:\\.|[^_\n])+?__\*|(?<!\\)_\*\*(?:\\.|[^*\n])+?\*\*_')
_MDB_PAT = re.compile(r'(?<!\\)\*\*(?:\\.|[^*\n])+?\*\*|(?<!\\)__(?:\\.|[^_\n])+?__')
_MDI_PAT = re.compile(r'(?<!\\)(?<!\*)\*(?:\\.|[^*\n])+?\*(?!\*)|(?<!\\)(?<!_)_(?:\\.|[^_\n])+?_(?!_)')
_MDS_PAT = re.compile(r'(?<!\\)~~(?:\\.|[^~\n])+?~~')
_MDC_PAT = re.compile(r'(?<!\\)`(?:\\.|[^`\n])+?`')
_MDL_PAT = re.compile(r'(?<!\\)\[(?:\\.|[^\]\n])*\]\((?:\\.|[^)\n])*\)')
_MDQ_PAT = re.compile(r'(?m)^>.*$')
_MD_HTML_TAGS = ('hstuff', 'hattr', 'hstr', 'hcmt')
