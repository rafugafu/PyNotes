import tkinter as tk
from tkinter import ttk
import os
import sys
import shutil
import zipfile
import urllib.request
import io
from tkinter import messagebox as mb
import ctypes
import time
def start():
	update = False
	try:
		shutil.rmtree('C:/Program Files/PyNotes')
	except:
		pass
	else:
		update = True
	button.grid_forget()
	ver = versionno.get()
	if ver == 'Latest':
		ver = 'latest'
	else:
		ver = customversionno.get()
	try:
		status.config(text = 'Downloading PyNotes')
		if ver == 'latest':
			dl_url = 'https://github.com/rafugafu/PyNotes/releases/latest/download/Data-Windows.zip'
		else:
			dl_url = f'https://github.com/rafugafu/PyNotes/releases/download/v{ver}/Data-Windows.zip'
		with urllib.request.urlopen(dl_url) as response:
			archive_bytes = io.BytesIO(response.read())
		pbar['value'] = 20
		status.config(text = 'Extracting PyNotes')
		root.update()
		with zipfile.ZipFile(archive_bytes) as archive:
			for member in archive.infolist():
				if member.is_dir():
					continue
				relative_path = member.filename.split('/', 1)[1]
				target_path = os.path.join('C:/Program Files/PyNotes', relative_path)
				os.makedirs(os.path.dirname(target_path), exist_ok = True)
				with archive.open(member) as source, open(target_path, 'wb') as target:
					shutil.copyfileobj(source, target)
		pbar['value'] = 60
		if not update == True:
			status.config(text = 'Adding to PATH')
			root.update()
			os.system('setx PATH "%PATH%;C:/Program Files/PyNotes" /M')
			pbar['value'] = 80
			status.config(text = 'Adding shortcut to Start Menu')
			root.update()
			os.chdir('C:/Program Files/PyNotes')
			os.system('"start menu shortcut.bat"')
		pbar['value'] = 100
		root.update()
	except Exception as e:
		mb.showerror('Error', f'There was an error:\n{e}')
	button.config(text = 'Finish', command = root.destroy)
	button.grid(column = 0, row = 6, padx = 10, pady = 10, sticky = 'ew')
	status.config(text = 'Done!')
if ctypes.windll.shell32.IsUserAnAdmin() == 0:
	ctypes.windll.shell32.ShellExecuteW(None, 'runas', sys.executable, f'"{__file__}"', None, 1)
	exit()
else:
	root = tk.Tk()
	root.geometry('300x300')
	root.title('PyNotes Installation')
	ttk.Label(master = root, text = 'PyNotes for Windows').grid(column = 0, row = 0, padx = 10, pady = 10, sticky = 'ew')
	pbar = ttk.Progressbar()
	pbar.grid(column = 0, row = 1, padx = 10, pady = 10, sticky = 'ew')
	status = ttk.Label(master = root, text = 'Waiting...')
	status.grid(column = 0, row = 2, padx = 10, pady = 10, sticky = 'ew')
	ttk.Label(master = root, text = 'Version number (1.4.1 and onwards):').grid(column = 0, row = 3, padx = 10, pady = 10, sticky = 'ew')
	versionno = tk.StringVar()
	customversionno = tk.StringVar()
	ttk.OptionMenu(root, versionno, 'Latest', *['Latest', 'Custom'], command = lambda option: customver.grid_forget() if option == 'Latest' else [customver.grid(column = 0, row = 5, padx = 10, pady = 10, sticky = 'ew'), versionno.set('Custom')]).grid(column = 0, row = 4, padx = 10, pady = 10, sticky = 'ew')
	customver = tk.Entry(fg = 'grey')
	customver.insert('end', 'eg. 1.4.2')
	customver.bind('<FocusIn>', lambda event: [customver.delete('0', 'end'), customver.config(fg = 'black'), versionno.set('')])
	customver.bind('<FocusOut>', lambda event: [customversionno.set(customver.get()), customver.delete('0', 'end'), customver.insert('end', 'eg. 1.4.2'), customver.config(fg = 'grey'), versionno.set('Custom')])
	customver.bind('<KeyRelease>', lambda event: versionno.set(customver.get()))
	button = ttk.Button(master = root, text = 'Start', command = start)
	button.grid(column = 0, row = 6, padx = 10, pady = 10, sticky = 'ew')
	root.columnconfigure(1, weight = 1)
	root.mainloop()