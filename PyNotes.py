import tkinter as tk
from tkinter import filedialog as fd
from tkinter import messagebox as mb
import os
root = tk.Tk()
root.geometry('500x365')
root.title('PyNotes')
title = ''
def lld():
	fn = fd.askopenfilename(initialdir = '/', title = 'Open', filetypes = (('Text Files', '*.txt'), ('All Files', '*.*')))
	ld(fn)
def ssssv(nm):
	if not nm == '':
		file = open(nm, 'w')
		file.writelines(type.get(1.0, 'end'))
		file.close()
	clt(nm)
def clt(nt):
	global title
	if not nt == '':
		root.title('PyNotes' + ' - ' + nt)
	else:
		root.title('PyNotes')
	title = nt
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
	global type
	global root
	if not nm == '':
		file = open(nm, 'r')
		lines = file.readlines()
		type.delete('1.0', 'end')
		for i in range(len(lines)):
			type.insert(tk.END, lines[i])
		file.close()
	clt(nm)
def llld():
	answer = mb.askquestion('Warning', 'Are you sure you want to close this document ?', icon = 'warning')
	if answer == 'yes':
		lld()
def sv(nm):
	global root
	if not nm == '':
		file = open(nm, 'w')
		file.writelines(type.get(1.0, 'end'))
		file.close()
		clt(nm)
def ssv():
	fn = fd.asksaveasfilename(initialdir = '/', title = 'Save', filetypes = (('Text Files', '*.txt'), ('All Files', '*.*')))
	sv(fn)
	clt(fn)
def nw():
	answer = mb.askquestion('Warning', 'Are you sure you want to open a new document ?', icon = 'warning')
	if answer == 'yes':
		type.delete('1.0', 'end')
		clt('')
scrlbr = tk.Scrollbar(root)
scrlbr.pack(side = tk.RIGHT, fill = tk.Y)
type = tk.Text(root, yscrollcommand = scrlbr.set)
type.pack(fill = tk.BOTH)
scrlbr.config(command = type.yview)
m = tk.Menu(root)
root.config(m = m)
fm = tk.Menu(m)
m.add_cascade(label = 'File', menu = fm)
fm.add_command(label = 'New', command = nw)
fm.add_command(label = 'Open', command = llld)
fm.add_separator()
fm.add_command(label = 'Save', command = sssv)
fm.add_command(label = 'Save as', command = ssv)
fm.add_separator()
fm.add_command(label = 'Exit', command = ext)
root.mainloop()