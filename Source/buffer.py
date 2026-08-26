import easytk
import state
DEBOUNCE_TIME = 300
class Buffer(easytk.ttk.Frame):
	for code in state.buffer_init_functions:
		try:
			exec(code, vars(state), locals())
		except Exception as error:
			error = str(error)
			state.root.error('Error', f'Error in buffer init functions:\n{error}')
	def __init__(self, master, *args, **kwargs):
		super().__init__(master, *args, **kwargs)
		self.active = False
		_, self.infos, self.fileinforelief, self.fileinfocolumn, self.fileinfoconfig = (setattr(self, 'fileinfo', state.root.frame(master = self)) or self.fileinfo).pack(padx = 10, pady = 10, fill = 'x'), {}, 0, 0, lambda relief = None, **infoconfigs: [(self.infos[info].config(text = value) if info in self.infos else (self.infos.update({info: state.root.text(master = self.fileinfo, text = value, padding = (5, 5, 5, 5), relief = relief or {0: 'sunken', 1: 'raised'}[setattr(self, 'fileinforelief', not self.fileinforelief) or self.fileinforelief])}) or self.infos[info]).grid(column = (setattr(self, 'fileinfocolumn', self.fileinfocolumn + 1) or self.fileinfocolumn), row = 0)) for info, value in infoconfigs.items()]
		self.wanttitle = ''
		for code in state.buffer_init_code:
			try:
				exec(code, vars(state), locals())
			except Exception as error:
				error = str(error)
				state.root.error('Error', f'Error in buffer init code:\n{error}')
	def setwanttitle(self, title):
		import window
		self.wanttitle = title
		window.settitle()
def saveforclose():
	for buffer in state.all_buffers:
		if hasattr(buffer, 'saveforclose') and not buffer.saveforclose():
			return False
	return True
