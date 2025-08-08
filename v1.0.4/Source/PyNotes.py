import easytk
import os
import sys
root = easytk.win()
root.geometry('650x500')
root.minsize(650, 500)
v = '1.0.4'
wordlist = open('/usr/share/PyNotes/dictionary', 'r').read().split('\n')
try:
	icon = '/usr/share/PyNotes/Icon.png'
	root.seticon(icon)
except:
	root.error('Error', 'Could not find the icon at /usr/share/PyNotes/Icon.png')
	root.destroy()
	exit()
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
	answer = root.ask('Warning', 'Are you sure you want to close this document ?', options = ('ok', 'cancel'), icon = 'warning')
	if answer:
		if not ScorPyon():
			ld('/usr/share/PyNotes/PyNotes.py')
		elif root.ask('Question', 'ScorPyon is installed on this system. Do you want to open the python file in ScorPyon ?', options = ('yes', 'no'), icon = 'info'):
			os.system('ScorPyon /usr/share/PyNotes/PyNotes.py')
		else:
			ld('/usr/share/PyNotes/PyNotes.py')
def abt(event = None):
	abw = easytk.win()
	abw.title('About PyNotes')
	abw_ = abw.frame()
	abw_.pack(fill = 'both', padx = 10, pady = 10)
	abw.text(master = abw_, text = f'PyNotes v{v}', font = ('TkDefaultFont', 20)).grid(column = 0, row = 0, sticky = 'w')
	abw.text(master = abw_, text = 'Rafey <https://github.com/rafugafu>', font = ('TkDefaultFont', 15)).grid(column = 0, row = 1, sticky = 'w')
	abw.text(master = abw_, text = 'PyNotes is a text editor made in Python', font = ('TkDefaultFont', 12)).grid(column = 0, row = 2, sticky = 'w')
	abw.button(text = 'Close', command = abw.destroy).pack(side = 'bottom', fill = 'x', padx = 10, pady = 10)
	abw.bind('<Return>', lambda event: abw.destroy())
	abw.sizablefalse()
	abw.show()
def changes(event = None):
	cw = easytk.win()
	cw.title(f'Changes in v{v}')
	cw_ = cw.frame()
	cw_.pack(fill = 'both', padx = 10, pady = 10)
	cw.text(master = cw_, text = '1. Added a basic spell checker!').grid(column = 0, row = 0, sticky = 'w')
	cw.text(master = cw_, text = '2. Rewrote the whole program in easytk!').grid(column = 0, row = 1, sticky = 'w')
	cw.text(master = cw_, text = '3. Added Preferences!').grid(column = 0, row = 2, sticky = 'w')
	cw.button(text = 'Close', command = cw.destroy).pack(side = 'bottom', fill = 'x', padx = 10, pady = 10)
	cw.bind('<Return>', lambda event: cw.destroy())
	cw.sizablefalse()
	cw.show()
def lld():
	fn = root.openfile(('all', 'txt'))
	if fn:
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
	answer = root.ask('Warning', 'Are you sure you want to exit ?', options = ('ok', 'cancel'), icon = 'warning')
	if answer:
		root.destroy()
		exit()
def ld(nm):
	global type_
	global root
	if not nm == '':
		try:
			file = open(nm, 'r')
			lines = file.readlines()
			type_.delete('1.0', 'end')
			for i in range(len(lines)):
				type_.insert('end', lines[i])
			file.close()
		except Exception as error:
			root.error('Error', error)
		else:
			clt(nm)
def llld(event = None):
	answer = root.ask('Warning', 'Are you sure you want to close this document ?', options = ('ok', 'cancel'), icon = 'warning')
	if answer:
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
	fn = root.savefile()
	if fn:
		sv(fn)
		clt(fn)
def nw(event = None):
	answer = root.ask('Warning', 'Are you sure you want to open a new document ?', options = ('ok', 'cancel'), icon = 'warning')
	if answer:
		type_.delete('1.0', 'end')
		clt('')
def fr(event = None):
	global type_
	find = root.askstring('Find & Replace', 'Text to Find:')
	replace = root.askstring('Find & Replace', 'Replace with:')
	if find and replace:
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
	find = root.askstring('Find', 'Text to Find:')
	if find:
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
def prf(event = None):
	pr = easytk.win()
	pr.style(root.gettheme())
	pr.title('Preferences')
	tabs = pr.tabs()
	tft = pr.frame()
	tabs.add(tft, text = 'Theme & Font')
	tabs.pack(side = 'top', fill = 'x', padx = 10, pady = 10)
	mf = root.frame(master = tft)
	mf.grid(column = 0, row = 0)
	pr.text(text = 'UI Theme', master = mf).grid(column = 0, row = 0, padx = 10, pady = 10)
	sts = pr.droptype(options = tuple(sorted(pr.style().get_themes())), command = lambda: [pr.sizabletrue(), pr.style(sts.get()), root.style(sts.get()), pr.sizablefalse()], master = mf)
	sts.grid(column = 1, row = 0, padx = 10, pady = 10)
	sts.insert('end', root.style().current_theme)
	pr.text(text = 'Editor Font', master = mf).grid(column = 0, row = 1, padx = 10, pady = 10)
	showfont = pr.textbox(master = tft, font = type_.cget('font'), height = 10)
	showfont.insert('end', 'The quick brown fox jumped over the lazy dogs\nAaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz\n1234567890\n?.,<>;:\'"{}[]\\|\n!@#$%^&*()-_+=')
	showfont.grid(column = 0, row = 1)
	f = pr.droptype(options = tuple(sorted(pr.getfonts())), master = mf, command = lambda: [pr.sizabletrue(), type_.config(font = (f.get(), 12)), showfont.config(font = (f.get(), 12)), pr.sizablefalse()])
	f.grid(column = 1, row = 1, padx = 10, pady = 10)
	f.insert('end', type_.cget('font'))
	pr.bind('<Return>', lambda event: pr.destroy())
	pr.button(text = 'OK', command = pr.destroy).pack(side = 'bottom', fill = 'x', padx = 10, pady = 10)
	pr.sizablefalse()
	pr.show()
def spellcheck(event = None):
	type_.tag_remove('wrong', '1.0', 'end')
	n = '1.0'
	search = r'\w+'
	while True:
		count = root.intvar()
		n = type_.search(search, n, nocase = 1, count = count, stopindex = 'end', regexp = True)
		if not n: break
		nn = '%s+%dc' % (n, count.get())
		if not type_.get(n, nn) in wordlist and len(type_.get(n, nn)) > 1:
			try:
				int(type_.get(n, nn))
			except:
				type_.tag_add('wrong', n, nn)
		n = nn
	n = '1.0'
	type_.tag_config('wrong', underline = True, underlinefg = 'red', foreground = 'brown')
scrlbr = root.scroll()
scrlbr.pack(side = 'right', fill = 'y')
type_ = root.textbox(yscrollcommand = scrlbr.set, width = 500, height = 500)
type_.pack(fill = 'both')
type_.focus()
scrlbr.config(command = type_.yview)
m = root.menu()
root.config(m = m)
fm = root.menu()
em = root.menu()
om = root.menu()
hm = root.menu()
m.add_cascade(label = 'File', menu = fm)
m.add_cascade(label = 'Edit', menu = em)
m.add_cascade(label = 'Options', menu = om)
m.add_cascade(label = 'Help', menu = hm)
em.add_command(label = 'Find -> Ctrl + F', command = f)
root.bind('<Control-f>', f)
em.add_command(label = 'Find & Replace -> Ctrl + Shift + F', command = fr)
root.bind('<Control-F>', fr)
hm.add_command(label = 'About', command = abt)
hm.add_command(label = f'What\'s new in {v}?', command = changes)
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
fm.add_command(label = 'Quit -> Ctrl + W', command = ext)
root.bind('<Control-w>', ext)
root.bind('<Control-W>', ext)
om.add_command(label = 'Preferences -> Ctrl + P', command = prf)
root.bind('<Control-p>', prf)
om.add_command(label = 'Open Source -> Ctrl + O', command = ss)
root.bind('<Control-o>', ss)
m.add_separator()
m.add_command(label = 'new', command = nw)
m.add_command(label = 'open', command = llld)
m.add_command(label = 'save', command = sssv)
m.add_command(label = 'save as', command = ssv)
m.add_command(label = 'exit', command = ext)
root.bind('<KeyRelease>', spellcheck)
root.protocol('WM_DELETE_WINDOW', ext)
if len(sys.argv) > 1:
	ld(sys.argv[1])
root.show()
