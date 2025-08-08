import tkinter as tk
from tkinter import filedialog as fd
from tkinter import messagebox as mb
import os
import sys
import getpass
os.chdir('/usr/share/PyNotes/')
root = tk.Tk()
image = tk.PhotoImage(file = 'Icon.png')
root.geometry('650x500')
root.iconphoto(False, image)
root.title('PyNotes')
title = ''
def shv(event = None):
	mb.showinfo('Version', '1.0')
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
def sssv():
	global title
	if not title == '':
		ssssv(title)
	else:
		ssv()
def ext():
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
def llld():
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
def ssv():
	fn = fd.asksaveasfilename(initialdir = '/', title = 'Save', filetypes = (('Text Files', '*.txt'), ('All Files', '*.*')))
	sv(fn)
	clt(fn)
def nw():
	answer = mb.askquestion('Warning', 'Are you sure you want to open a new document ?', icon = 'warning')
	if answer == 'yes':
		type_.delete('1.0', 'end')
		clt('')
scrlbr = tk.Scrollbar(root)
scrlbr.pack(side = tk.RIGHT, fill = tk.Y)
type_ = tk.Text(root, yscrollcommand = scrlbr.set, width = 500, height = 500)
type_.pack(fill = tk.BOTH)
scrlbr.config(command = type_.yview)
m = tk.Menu(root)
root.config(m = m)
fm = tk.Menu(m)
hm = tk.Menu(m)
m.add_cascade(label = 'File', menu = fm)
m.add_cascade(label = 'Help', menu = hm)
hm.add_command(label = 'Version', command = shv)
hm.add_command(label = 'Author', command = rafey)
fm.add_command(label = 'New', command = nw)
fm.add_command(label = 'Open', command = llld)
fm.add_separator()
fm.add_command(label = 'Save', command = sssv)
fm.add_command(label = 'Save as', command = ssv)
fm.add_separator()
fm.add_command(label = 'Exit', command = ext)
if len(sys.argv) > 1:
	ld(sys.argv[1])
root.mainloop()
