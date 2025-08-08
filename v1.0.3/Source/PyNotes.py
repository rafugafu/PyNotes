import tkinter as tk
from tkinter import filedialog as fd
from tkinter import messagebox as mb
from tkinter import simpledialog as sd
import os
import sys
import getpass
root = tk.Tk()
image = tk.PhotoImage(file = '/usr/share/PyNotes/Icon.png')
root.geometry('650x500')
root.iconphoto(False, image)
root.title('PyNotes')
title = ''
def ScorPyon():
	old = os.getcwd()
	try:
		os.chdir('/usr/share/ScorPyon/')
	except:
		return False
	else:
		os.chdir(old)
		return True
def ss(event = None):
	answer = mb.askquestion('Warning', 'Are you sure you want to close this document ?', icon = 'warning')
	if answer == 'yes':
		if not ScorPyon():
			ld('/usr/share/PyNotes/PyNotes.py')
		elif mb.askquestion('Question', 'ScorPyon is installed on this system. Do you want to open the python file in ScorPyon ?', icon = 'info') == 'yes':
			os.system('ScorPyon /usr/share/PyNotes/PyNotes.py')
		else:
			ld('/usr/share/PyNotes/PyNotes.py')
def shv(event = None):
	mb.showinfo('Version', '1.0.3')
def rafey(event = None):
	mb.showinfo('Author', 'Rafey <https://github.com/rafugafu>')
def lld():
	fn = fd.askopenfilename(initialdir = f'/home/{getpass.getuser()}/', title = 'Open', filetypes = (('Text Files', '*.txt'), ('All Files', '*.*')))
	ld(fn)
def ssssv(nm):
	if not nm == '':
		file = open(nm, 'w')
		file.writelines(type_.get(1.0, 'end'))
		file.close()
	clt(nm)
def clt(nt):
	global title
	try:
		if not nt == '':
			root.title('PyNotes' + ' - ' + nt)
		else:
			root.title('PyNotes')
		title = nt
	except:
		pass
def sssv(event = None):
	global title
	if not title == '':
		ssssv(title)
	else:
		ssv()
def ext(event = None):
	global root
	answer = mb.askquestion('Warning', 'Are you sure you want to exit ?', icon = 'warning')
	if answer == 'yes':
		root.destroy()
def ld(nm):
	global type_
	global root
	if not nm == '':
		try:
			file = open(nm, 'r')
			lines = file.readlines()
			type_.delete('1.0', 'end')
			for i in range(len(lines)):
				type_.insert(tk.END, lines[i])
			file.close()
		except:
			pass
	clt(nm)
def llld(event = None):
	answer = mb.askquestion('Warning', 'Are you sure you want to close this document ?', icon = 'warning')
	if answer == 'yes':
		lld()
def sv(nm):
	global root
	if not nm == '':
		try:
			file = open(nm, 'w')
			file.writelines(type_.get(1.0, 'end'))
			file.close()
			clt(nm)
		except:
			pass
def ssv(event = None):
	fn = fd.asksaveasfilename(initialdir = '/', title = 'Save', filetypes = (('Text Files', '*.txt'), ('All Files', '*.*')))
	sv(fn)
	clt(fn)
def nw(event = None):
	answer = mb.askquestion('Warning', 'Are you sure you want to open a new document ?', icon = 'warning')
	if answer == 'yes':
		type_.delete('1.0', 'end')
		clt('')
def fr(event = None):
	global type_
	find = sd.askstring('Find & Replace', prompt = 'Text to Find:')
	replace = sd.askstring('Find & Replace', prompt = 'Replace with:')
	if find != '' and find != None and replace != None:
		n = '1.0'
		search = r'\y' + find + r'\y'
		while True:
			n = type_.search(search, n, nocase = 1, stopindex = 'end', regexp = True)
			if not n: break
			nn = '%s+%dc' % (n, len(find))
			type_.delete(n, nn)
			type_.insert(n, replace)
			n = nn
def f(event = None):
	global type_
	find = sd.askstring('Find', prompt = 'Text to Find:')
	if find != '' and find != None:
		type_.tag_remove('found', '1.0', 'end')
		n = '1.0'
		search = r'\y' + find + r'\y'
		while True:
			n = type_.search(search, n, nocase = 1, stopindex = 'end', regexp = True)
			if not n: break
			nn = '%s+%dc' % (n, len(find))
			type_.tag_add('found', n, nn)
			n = nn
		type_.tag_config('found', foreground = 'white', background = 'black')
	if find == '':
		type_.tag_remove('found', '1.0', 'end')
scrlbr = tk.Scrollbar(root)
scrlbr.pack(side = tk.RIGHT, fill = tk.Y)
type_ = tk.Text(root, yscrollcommand = scrlbr.set, width = 500, height = 500)
type_.pack(fill = tk.BOTH)
scrlbr.config(command = type_.yview)
m = tk.Menu(root)
root.config(m = m)
fm = tk.Menu(m)
em = tk.Menu(m)
om = tk.Menu(m)
hm = tk.Menu(m)
m.add_cascade(label = 'File', menu = fm)
m.add_cascade(label = 'Edit', menu = em)
m.add_cascade(label = 'Options', menu = om)
m.add_cascade(label = 'Help', menu = hm)
em.add_command(label = 'Find -> Ctrl + F', command = f)
root.bind('<Control-f>', f)
em.add_command(label = 'Find & Replace -> Ctrl + Shift + F', command = fr)
root.bind('<Control-F>', fr)
hm.add_command(label = 'Version', command = shv)
hm.add_command(label = 'Author', command = rafey)
fm.add_command(label = 'New -> Ctrl + N', command = nw)
root.bind('<Control-n>', nw)
fm.add_command(label = 'Open -> Ctrl + L', command = llld)
root.bind('<Control-l>', llld)
fm.add_separator()
fm.add_command(label = 'Save -> Ctrl + S', command = sssv)
root.bind('<Control-s>', sssv)
fm.add_command(label = 'Save as -> Ctrl + Shift + S', command = ssv)
root.bind('<Control-S>', ssv)
fm.add_separator()
fm.add_command(label = 'Exit -> Ctrl + Q', command = ext)
root.bind('<Control-q>', ext)
om.add_command(label = 'Open PyNotes Source -> Ctrl + O', command = ss)
root.bind('<Control-o>', ss)
if len(sys.argv) > 1:
	ld(sys.argv[1])
root.mainloop()
