import platform
import time
import shutil
from tkinter import messagebox as mb
import getpass
import urllib.request
import urllib.error
import os
import tkinter as tk
try:
	import ttkbootstrap
except:
	from tkinter import ttk
	try:
		import ttkthemes
	except:
		root = tk.Tk()
		ttk.Style().theme_use('clam')
	else:
		root = ttkthemes.ThemedTk(theme = 'breeze')
else:
	import ttkbootstrap as ttk
	root = ttk.Window(themename = 'pulse')
if platform.system() == 'Linux':
	homedir = f'/home/{getpass.getuser()}'
else:
	homedir = f'C:/Users/{getpass.getuser()}'
def download(url, filename):
	urllib.request.urlretrieve(url, filename)
root.geometry('400x400')
root.title('PyNotes Plugin Installer')
infotext = ttk.Label(root, text = 'Downloading list of plugins', font = ('TkDefaultFont', 15))
infotext.pack(anchor = 'nw', padx = 10, pady = 10)
selectframe = ttk.Frame(master = root)
selectframe.pack(fill = 'both', expand = True)
pb = ttk.Progressbar()
root.update()
listurl = 'https://raw.githubusercontent.com/rafugafu/PyNotes/main/Plugins/list'
try:
	with urllib.request.urlopen(listurl) as requested:
		listplugins = requested.read().decode()
except Exception as e:
	mb.showerror('Error', f'There was an error in downloading the list of plugins:\n{e}')
	root.destroy()
	exit()
def done():
	installing = [plugincheck[0] for plugincheck in pluginchecks if plugincheck[1].get()]
	if not installing:
		mb.showinfo('Info', 'Select plugins to install')
		return
	if not mb.askokcancel('Installing', f'These plugins will be installed:\n\n{"\n".join(f'"{x}"' for x in installing)}\n\nContinue?'):
		return
	donebutton.config(state = 'disabled')
	[plugincheck[2].config(state = 'disabled') for plugincheck in pluginchecks]
	pb.pack(anchor = 'nw', padx = 10, pady = 10)
	increment = 100 / len(installing)
	for plugin in installing:
		infotext.config(text = f'Installing plugin "{plugin}"')
		root.update()
		try:
			url = f'https://raw.githubusercontent.com/rafugafu/PyNotes/main/Plugins/{plugin.replace(" ", "%20")}.zip'
			filename = f'{plugin}.zip'
			download(url, filename)
			os.makedirs(f'{homedir}/.local/share/PyNotes/add-ons', exist_ok = True)
			shutil.unpack_archive(filename, f'{homedir}/.local/share/PyNotes/add-ons')
			os.remove(filename)
		except Exception as e:
			mb.showerror('Error', f'There was an error in downloading and installing the plugin:\n{e}')
		pb['value'] += increment
		root.update()
	infotext.config(text = 'Done!')
pluginchecks = []
row = 0
infotext.config(text = 'Select the plugins to (re)install or update:')
root.update()
for plugin in listplugins.strip().split('\n'):
	bv = tk.BooleanVar()
	pluginchecks.append((plugin, bv, ttk.Checkbutton(selectframe, text = plugin, variable = bv)))
	pluginchecks[-1][2].grid(column = 0, row = row, padx = 10, pady = 10, sticky = 'w')
	row += 1
	root.update()
	time.sleep(0.1)
donebutton = ttk.Button(selectframe, text = 'Done', command = done)
donebutton.grid(column = 0, row = row)
root.mainloop()