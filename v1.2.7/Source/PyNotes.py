import easytk
import os
import sys
import io
import time
import keyword
import re
import getpass
from runnerpython import ragoae
from runnerpython import ragoae_other
root = easytk.win()
start = time.time()
v = '1.2.7'
try:
    os.mkdir(f'/home/{getpass.getuser()}/.local/PyNotes/')
except:
    pass
try:
    file = open(f'/home/{getpass.getuser()}/.local/PyNotes/defs', 'r')
except:
    file = open(f'/home/{getpass.getuser()}/.local/PyNotes/defs', 'w+')
    file.write(f'{v}\nFalse\nTkDefaultFont\nice')
    file.close()
    file = open(f'/home/{getpass.getuser()}/.local/PyNotes/defs', 'r')
defs = file.read().split('\n')
file.close()
if not v == defs[0]:
    root.info('Info', 'PyNotes has been updated!\n(Consider checking Help → Help with PyCode if this is your first time)')
    defs[0] = v
    file = open(f'/home/{getpass.getuser()}/.local/PyNotes/defs', 'w+')
    for d in defs:
        file.write(d + '\n')
    file.close()
if defs[1] == 'False':
    bfr = False
elif defs[1] == 'True':
    bfr = True
try:
    wordlist = open('/usr/share/PyNotes/dictionary', 'r').read().split('\n')
except:
    root.error('Error', 'Could not find the dictionary at /usr/share/PyNotes/dictionary')
    if not root.ask('Question', 'Do you want to continue without the spellchecker ?', ('yes', 'no')):
        exit()
        root.destroy()
    else:
        wordlist = list()
try:
    icon = '/usr/share/PyNotes/Icon.png'
    root.seticon(icon)
except:
    root.error('Error', 'Could not find the icon at /usr/share/PyNotes/Icon.png')
    root.destroy()
    exit()
root.title('PyNotes - Untitled')
title = ''
def ss():
    answer = root.ask('Warning', 'Do you want to save file before closing ?', options = ('yes', 'no', 'cancel'), icon = 'warning') if filename.cget('text')[-1:] == '*' and not filename.cget('text') == '*scratch*' else False
    if answer != None:
        if answer:
            sv(title)
        ld('/usr/share/PyNotes/PyNotes.py')
def abt(event = None):
    abw = root.subwin()
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
    cw = root.subwin()
    cw.title(f'Changes in v{v}')
    cw_ = cw.frame()
    cw__ = cw.frame(master = cw_)
    cw_.pack(fill = 'both', padx = 10, pady = 10)
    cw__.grid(column = 0, row = 2, sticky = 'w')
    cw.text(master = cw_, text = '1. PyNotes can now open png images!').grid(column = 0, row = 0, sticky = 'w')
    cw.button(text = 'Close', command = cw.destroy).pack(side = 'bottom', fill = 'x', padx = 10, pady = 10)
    cw.bind('<Return>', lambda event: cw.destroy())
    cw.sizablefalse()
    cw.style(root.gettheme())
    cw.show()
def lld():
    fn = root.openfile(('all', 'py', 'txt', 'tex', 'png'))
    if fn:
        ld(fn)
def ssssv(nm):
    if not nm == '':
        sv(nm)
    clt(nm)
def clt(nt):
    global title
    try:
        if not nt == '':
            root.title('PyNotes' + ' - ' + os.path.basename(nt))
        else:
            root.title('PyNotes - Untitled')
        title = nt
        filename.config(text = os.path.basename(nt))
    except:
        pass
def sssv(event = None):
    global title
    if not title == '':
        ssssv(title)
    else:
        ssv()
def ext(event = None):
    answer = root.ask('Warning', 'Do you want to save file before closing ?', options = ('yes', 'no', 'cancel'), icon = 'warning') if filename.cget('text')[-1:] == '*' and not filename.cget('text') == '*scratch*' else False
    if answer != None:
        if answer:
            sv(title)
        root.destroy()
def ld(nm):
    global type_
    global root
    global m
    global imageload
    if not nm == '':
        nw()
        try:
            file = open(nm, 'r')
            lines = file.readlines()
            type_.delete('1.0', 'end')
            for i in range(len(lines)):
                type_.insert('end', lines[i])
            file.close()
        except Exception as error:
            try:
                imageload = root.image(image = nm, imsize = (1, 1))
            except:
                root.error('Error', error)
            else:
                type_.pack_forget()
                ln.pack_forget()
                tabs.pack_forget()
                imageload.pack(fill = 'both', expand = True)
                show('open image')
                clt(nm)
                filesize.config(text = str(os.path.getsize(nm)) + ' bytes')
                filetype.config(text = 'PNG Image (*.png)')
                imageload.focus_force()
        else:
            try:
                imageload.pack_forget()
            except:
                pass
            else:
                ln.pack(side = 'left', fill = 'y', anchor = 'n')
                type_.pack(fill = 'both', expand = True, anchor = 'n')
                tabs.pack(padx = 10, pady = 10, fill = 'both', expand = True)
            show('open file')
            clt(nm)
            filesize.config(text = str(os.path.getsize(nm)) + ' bytes')
            if os.path.splitext(nm)[1] == '.py':
                m.entryconfig(4, state = 'normal')
                m.entryconfig(5, state = 'disabled')
                filetype.config(text = 'Python File (' + os.path.splitext(nm)[1] + ')')
            elif os.path.splitext(nm)[1] == '.tex':
                m.entryconfig(4, state = 'disabled')
                m.entryconfig(5, state = 'normal')
                filetype.config(text = 'LaTeX File (' + os.path.splitext(nm)[1] + ')')
            else:
                filetype.config(text = 'Plain Text (*.*)')
                m.entryconfig(4, state = 'disabled')
                m.entryconfig(5, state = 'disabled')
            keypress()
def llld(event = None):
    answer = root.ask('Warning', 'Do you want to save file before closing ?', options = ('yes', 'no', 'cancel'), icon = 'warning') if filename.cget('text')[-1:] == '*' and not filename.cget('text') == '*scratch*' else False
    if answer != None:
        if answer:
            sv(title)
        lld()
def sv(nm):
    global root
    if not nm == '':
        if not filetype.cget('text') == 'PNG Image (*.png)':
            try:
                file = open(nm, 'w')
                file.writelines(type_.get(1.0, 'end-1c'))
                file.close()
                clt(nm)
            except:
                pass
            else:
                show('save file')
def ssv(event = None):
    fn = root.savefile()
    if fn:
        sv(fn)
        clt(fn)
def nw(event = None):
    answer = root.ask('Warning', 'Do you want to save file before closing ?', options = ('yes', 'no', 'cancel'), icon = 'warning') if filename.cget('text')[-1:] == '*' and not filename.cget('text') == '*scratch*' else False
    if answer != None:
        try:
            imageload.pack_forget()
        except:
            pass
        else:
            ln.pack(side = 'left', fill = 'y', anchor = 'n')
            type_.pack(fill = 'both', expand = True, anchor = 'n')
            tabs.pack(padx = 10, pady = 10, fill = 'both', expand = True)
        if answer:
            sv(title)
        type_.delete('1.0', 'end')
        clt('')
        filename.config(text = '*scratch*')
        filetype.config(text = 'Plain Text (*.*)')
        filesize.config(text = '0 bytes (Unnamed)')
        show('open new')
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
        show('find and replace string')
def f(event = None):
    ok = root.subwin()
    ok.title('Search')
    ok.button(text = 'Close search', command = lambda: [type_.tag_remove('found', '1.0', 'end'), ok.destroy()]).grid(padx = 10, pady = 10)
    ok.bind('<Return>', lambda event: [type_.tag_remove('found', '1.0', 'end'), ok.destroy(), root.unbind('<Return>')])
    root.bind('<Return>', lambda event: [type_.tag_remove('found', '1.0', 'end'), ok.destroy(), root.unbind('<Return>')])
    ok.sizablefalse()
    ok.style(root.gettheme())
    global type_
    find = root.askstring('Find', 'Text to Find:')
    if find:
        while True:
            try:
                ok.winfo_exists()
            except:
                type_.tag_remove('found', '1.0', 'end')
                break
            else:
                ok.update()
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
        show('find and highlight string')
def bf(opt):
    global bfr
    bfr = opt
def svprf():
    global bfr
    file = open(f'/home/{getpass.getuser()}/.local/PyNotes/defs', 'w+')
    file.write(f'{v}\n{str(bfr)}\n{type_.cget("font")}\n{root.gettheme()}')
    file.close()
def prf(event = None):
    global bfr
    pr = root.subwin()
    pr.title('Preferences')
    tabs = pr.tabs()
    gt = pr.frame()
    tft = pr.frame()
    tabs.add(gt, text = 'General')
    bfc = pr.booleanvar(value = bfr)
    pr.check(master = gt, text = 'Backup file regularly', command = lambda: bf(bfc.get()), var = bfc).grid(column = 0, row = 0)
    tabs.add(tft, text = 'Theme & Font')
    tabs.select(tft)
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
    f = pr.droptype(options = tuple(sorted(pr.getfonts())), master = mf, command = lambda: [pr.sizabletrue(), type_.config(font = (f.get(), 12)), ln.config(font = (f.get(), 12)), showfont.config(font = (f.get(), 12)), pr.sizablefalse()])
    f.grid(column = 1, row = 1, padx = 10, pady = 10)
    f.insert('end', type_.cget('font'))
    pr.bind('<Return>', lambda event: [svprf(), show('change / view preferences'), pr.destroy()])
    pr.button(text = 'OK', command = lambda: [svprf(), show('change / view preferences'), pr.destroy()]).pack(side = 'bottom', fill = 'x', padx = 10, pady = 10)
    pr.protocol('WM_DELETE_WINDOW', lambda: [svprf(), show('change / view preferences'), pr.destroy()])
    pr.sizablefalse()
    pr.style(root.gettheme())
    pr.show()
def spellcheck():
    type_.tag_remove('wrong', '1.0', 'end')
    n = '1.0'
    search = r'\w+'
    while True:
        count = root.intvar()
        n = type_.search(search, n, nocase = 1, count = count, stopindex = 'end', regexp = True)
        if not n: break
        nn = '%s+%dc' % (n, count.get())
        if not type_.get(n, nn).lower() in wordlist and len(type_.get(n, nn)) > 1:
            try:
                int(type_.get(n, nn))
            except:
                type_.tag_add('wrong', n, nn)
        n = nn
    n = '1.0'
    type_.tag_config('wrong', underline = True, underlinefg = 'red')
def hpa():
    type_.tag_remove('hpa', '1.0', 'end')
    for k in keyword.kwlist:
        n = '1.0'
        searchstr = r'\y' + k + r'\y'
        while True:
            n = type_.search(searchstr, n, nocase = 1, stopindex = 'end', regexp = True)
            if not n: break
            nn = '%s+%dc' % (n, len(k))
            type_.tag_add('hpa', n, nn)
            n = nn
        type_.tag_config('hpa', foreground = 'red')
def hpb():
    type_.tag_remove('hpb', '1.0', 'end')
    for k in ('file', 'open', 'map', 'int', 'str', 'print', 'range', 'set', 'input', 'list', 'len', 'self', 'type', 'exec', 'sum', 'iter', 'dir', 'compile', 'eval', 'format', 'locals', 'cls', 'exit', 'quit', 'dict', 'repr', 'hasattr', 'setattr', 'super', 'isinstance', 'object', 'tuple', 'float'):
        n = '1.0'
        searchstr = r'\y' + k + r'\y'
        while True:
            n = type_.search(searchstr, n, nocase = 1, stopindex = 'end', regexp = True)
            if not n: break
            nn = '%s+%dc' % (n, len(k))
            type_.tag_add('hpb', n, nn)
            n = nn
        type_.tag_config('hpb', foreground = 'magenta')
def hpc():
    type_.tag_remove('hpc', '1.0', 'end')
    n = '1.0'
    searchstr = r'#.+?\n'
    while True:
        count = root.intvar()
        n = type_.search(searchstr, n, nocase = 1, stopindex = 'end', regexp = True, count = count)
        if not n: break
        nn = '%s+%dc' % (n, count.get())
        type_.tag_add('hpc', n, nn)
        n = nn
    type_.tag_config('hpc', foreground = 'green')
def hpd():
    type_.tag_remove('hpd', '1.0', 'end')
    n = '1.0'
    searchstr = r'\'.+?\''
    while True:
        count = root.intvar()
        n = type_.search(searchstr, n, nocase = 1, stopindex = 'end', regexp = True, count = count)
        if not n: break
        nn = '%s+%dc' % (n, count.get())
        type_.tag_add('hpd', n, nn)
        n = nn
    type_.tag_config('hpd', foreground = 'blue')
def hla():
    type_.tag_remove('hla', '1.0', 'end')
    n = '1.0'
    search = r'\$.+?\$'
    while True:
        count = root.intvar()
        n = type_.search(search, n, nocase = 1, count = count, stopindex = 'end', regexp = True)
        if not n: break
        nn = '%s+%dc' % (n, count.get())
        type_.tag_add('hla', n, nn)
        n = nn
    type_.tag_config('hla', foreground = 'red')
def hlb():
    type_.tag_remove('hlb', '1.0', 'end')
    start = '1.0'
    while True:
        start = type_.search(r'\\begin{equation}', start, nocase = 1, stopindex = 'end', regexp = True)
        if not start:
            break
        end = type_.search(r'\\end{equation}', start, nocase = 1, stopindex = 'end', regexp = True)
        if not end:
            break
        type_.tag_add('hlb', start, end + '+14c')
        start = end
    type_.tag_config('hlb', background = 'lightblue')
def hlc():
    type_.tag_remove('hlc', '1.0', 'end')
    start = '1.0'
    while True:
        start = type_.search(r'\\begin{tabular}{.+?}', start, nocase = 1, stopindex = 'end', regexp = True)
        if not start:
            break
        end = type_.search(r'\\end{tabular}', start, nocase = 1, stopindex = 'end', regexp = True)
        if not end:
            break
        type_.tag_add('hlc', start, end + '+13c')
        start = end
    type_.tag_config('hlc', background = 'yellow')
def hld():
    type_.tag_remove('hld', '1.0', 'end')
    n = '1.0'
    search = r'\\(\w+)'
    while True:
        count = root.intvar()
        n = type_.search(search, n, nocase = 1, count = count, stopindex = 'end', regexp = True)
        if not n: break
        nn = '%s+%dc' % (n, count.get())
        type_.tag_add('hld', n, nn)
        n = nn
    n = '1.0'
    search = r'\\(\w+)\{'
    while True:
        count = root.intvar()
        n = type_.search(search, n, nocase = 1, count = count, stopindex = 'end', regexp = True)
        if not n: break
        nn = '%s+%dc' % (n, count.get())
        type_.tag_add('hld', n, nn)
        n = nn
    type_.tag_config('hld', foreground = 'magenta')
def hle():
    type_.tag_remove('hle', '1.0', 'end')
    n = '1.0'
    search = r'\{.+?\}'
    while True:
        count = root.intvar()
        n = type_.search(search, n, nocase = 1, count = count, stopindex = 'end', regexp = True)
        if not n: break
        nn = '%s+%dc' % (n, count.get())
        type_.tag_add('hle', n, nn)
        n = nn
    type_.tag_config('hle', foreground = 'blue')
def hlf():
    type_.tag_remove('hle', '1.0', 'end')
    n = '1.0'
    search = r'\\\\'
    while True:
        count = root.intvar()
        n = type_.search(search, n, nocase = 1, count = count, stopindex = 'end', regexp = True)
        if not n: break
        nn = '%s+%dc' % (n, count.get())
        type_.tag_add('hle', n, nn)
        n = nn
    n = '1.0'
    search = r'&'
    while True:
        count = root.intvar()
        n = type_.search(search, n, nocase = 1, count = count, stopindex = 'end', regexp = True)
        if not n: break
        nn = '%s+%dc' % (n, count.get())
        type_.tag_add('hle', n, nn)
        n = nn
    n = '1.0'
    search = r'\|'
    while True:
        count = root.intvar()
        n = type_.search(search, n, nocase = 1, count = count, stopindex = 'end', regexp = True)
        if not n: break
        nn = '%s+%dc' % (n, count.get())
        type_.tag_add('hle', n, nn)
        n = nn
    type_.tag_config('hle', foreground = 'white', background = 'grey')
def hlg():
    type_.tag_remove('hlg', '1.0', 'end')
    n = '1.0'
    search = r'\[.+?\]'
    while True:
        count = root.intvar()
        n = type_.search(search, n, nocase = 1, count = count, stopindex = 'end', regexp = True)
        if not n: break
        nn = '%s+%dc' % (n, count.get())
        type_.tag_add('hlg', n, nn)
        n = nn
    type_.tag_config('hlg', foreground = 'brown')
def hlh():
    type_.tag_remove('hlh', '1.0', 'end')
    n = '1.0'
    searchstr = r'%.+?\n'
    while True:
        count = root.intvar()
        n = type_.search(searchstr, n, nocase = 1, count = count, stopindex = tk.END, regexp = True)
        if not n: break
        nn = '%s+%dc' % (n, count.get())
        type_.tag_add('hlh', n, nn)
        n = nn
    type_.tag_config('hlh', foreground = 'grey')
def ha(ft):
    if ft == 'py':
        hpa()
        hpb()
        hpc()
        hpd()
    elif ft == 'latex':
        hla()
        hlb()
        hlc()
        hld()
        hle()
        hlf()
        hlg()
def keypress(event = None):
    global bfr
    global ln
    global tabs
    lines = int(type_.index('end-1c').split('.')[0])
    ln.config(state = 'normal')
    ln.delete('1.0', 'end')
    for i in range(lines):
        ln.insert('end', str(i + 1) + '\n')
    ln.config(state = 'disabled')
    for tag in type_.tag_names():
        if not tag == 'sel': type_.tag_remove(tag, '1.0', 'end')
    if bfr and title and int(time.time() - start) % 3 == 0:
        open(os.path.join(os.path.dirname(os.path.splitext(title)[0]), '.' + os.path.basename(os.path.splitext(title)[0]) + 'backpynotes' + os.path.splitext(title)[1]), 'w+').write(type_.get('1.0', 'end'))
        show('backing up ... done')
    if wordlist and filetype.cget('text') == 'Plain Text (*.*)': spellcheck()
    filesize.config(text = str(len(io.StringIO(type_.get('1.0', 'end')).read()) - 1) + ' bytes')
    tabs.tab(1, state = 'disabled')
    if filetype.cget('text') == 'Python File (.py)':
        tabs.tab(1, state = 'normal')
        ha('py')
    elif filetype.cget('text') == 'LaTeX File (.tex)': ha('latex')
    if title:
        if type_.get('1.0', 'end').strip() != open(title, 'r').read().strip():
            filename.config(text = os.path.basename(title) + ' *')
            root.title('PyNotes - ' + os.path.basename(title) + ' *')
        else:
            filename.config(text = os.path.basename(title))
            root.title('PyNotes - ' + os.path.basename(title))
def rp():
    sv(title)
    output = ragoae(type_.get('1.0', 'end'))
    if output[0] == False:
        root.info('Output', output[1])
    else:
        root.error('Error', output[1])
def shellexec(command):
    output = ragoae(command)
    if output[0] == False:
        output = '\n'.join(str(item) for item in output[1])
    elif output[0] == True:
        output = 'Error:\n' + output[1]
    return output
def rp2():
    sv(title)
    output = ragoae_other(type_.get('1.0', 'end'))
    if output[0] == False:
        root.info('उत्पादन', output[1])
    else:
        root.error('गलती', output[1])
def f5(event = None):
    if filetype.cget('text') == 'Python File (.py)':
        rp()
    elif filetype.cget('text') == 'LaTeX File (.tex)':
        lp()
    show('run program')
def pdf(title):
	if os.path.splitext(title)[1] == '.tex':
		pdf_ = os.path.splitext(title)[0]
	else:
		pdf_ = title
	pdf_ += '.pdf'
	time.sleep(0.5)
	if not os.path.exists(os.path.abspath(pdf_)):
		mb.showerror('Error', 'The pdf could not be shown, there could have been an error in your code?')
		return
	else:
		os.system('xdg-open ' + '"' + pdf_ + '"')
def runtex(compiler):
	global type_
	global title
	compiler += 'latex '
	os.system(compiler + '"' +  title + '"' + ' > /dev/null 2>&1 &')
	pdf(title)
def lp2(event = None):
	sv(title)
	runtex('pdf')
def lp(event = None):
	sv(title)
	runtex('lua')
def rb():
    root.info('Recover Backup', '1. Go to the directory of the lost file\n2. Press Ctrl-h to show hidden files\n3. You will see something like .filebackpynotes.txt\n4. Copy it into the original lost file.\n(This may not be an exact copy)')
def termexec(string, listbox, window, bar, entry):
    if string == 'clear':
        listbox.delete(0, 'end')
        entry.delete(0, 'end')
        return
    elif string == 'exit':
        window.destroy()
        return
    else:
        bar.config(value = 0)
        bar.grid(column = 1, row = 0)
        bar.lift()
        window.update()
        time.sleep(0.05)
        bar.config(value = 50)
        window.update()
        time.sleep(0.05)
        bar.config(value = 100)
        window.update()
        time.sleep(0.05)
        bar.grid_forget()
        window.sizabletrue()
        os.system(string + '> .termout')
        for item in open('.termout', 'r').read().split('\n'):
            listbox.insert('end', item)
        entry.delete(0, 'end')
        window.sizablefalse()
        os.remove('.termout')
def term():
        tw = root.subwin()
        tw.title('Terminal')
        tf = tw.frame()
        tf.pack(side = 'top', fill = 'x')
        tw.text(master = tf, text = f'{getpass.getuser()}@PyNotes:{os.path.basename(os.getcwd())}/$').grid(column = 0, row = 0, padx = 10, pady = 10)
        in_ = tw.entry(master = tf, width = 20)
        obf = tw.frame()
        scrolly = tw.scroll(master = obf)
        scrolly2 = tw.scroll(master = obf, orient = 'horizontal')
        scrolly.pack(side = 'right', fill = 'y')
        scrolly2.pack(side = 'bottom', fill = 'x')
        out = tw.listbox(master = obf, yscrollcommand = scrolly.set, xscrollcommand = scrolly2.set)
        out.pack(fill = 'both')
        scrolly.config(command = out.yview)
        scrolly2.config(command = out.xview)
        obf.pack(side = 'bottom', fill = 'x')
        cmdprgrs = tw.progressbar(master = tf, length = 145)
        in_.bind('<Return>', lambda event: termexec(in_.get(), out, tw, cmdprgrs, in_))
        in_.focus()
        in_.grid(column = 1, row = 0, padx = 10, pady = 10)
        tw.sizablefalse()
        tw.style(root.gettheme())
        tw.show()
def gl(event = None):
    l = root.askstring('Go to line', 'Go to line no. :')
    if not l:
        return
    try:
        l = int(l)
    except:
        root.error('Error', f'Cannot go to line number \'{l}\'')
        return
    else:
        type_.see(f'{l}.0')
        type_.mark_set('insert', f'{l}.0')
        type_.tag_add('sel', f'{l}.0', f'{l}.end')
def hx():
    hxw = root.subwin()
    hxw.title('Help with commands')
    hxs = hxw.scroll()
    hxs.pack(side = 'right', fill = 'y')
    hxh = hxw.textbox(wrap = 'word', yscrollcommand = hxs.set)
    hxs.config(command = hxh.yview)
    hxh.pack(fill = 'both', padx = 10, pady = 10)
    hxh.insert('end', "'exit' or 'e': exit the window (the same as File → Exit)\n'save' or 's': save the current file (the same as File → Save)\n'search' or 'f': find a string in the editor (the same as Edit → Find)\n'fr' or 'find-replace' or 'findreplace': find and replace a string in the editor instantly (the same as Edit → Find&Replace)\n'show-source' or 'source-code': show and edit the main source code of PyNotes (/usr/share/PyNotes/main.py) (the same as Options → Source Code)(this does not have a shortcut like 'sc' because it is used very rarely)\n'new' or 'n': open a new document (the same as File → New)\n'gotoline' or 'gl' or 'l': go to a specified line\n'o' or 'f' or 'load' or 'find' or 'open': Load a new file into the editor (the same as File → Open)\n't' or 'term' or 'terminal' or 'cmd': Open the small terminal (the same as Options → Terminal)\n'prf' or 'preferences': Change the preferences (the same as Options → Preferences)\n'cancel' or 'z': Cancel the command and go back to the editor\n'a' or 'selall' or 'all': select all the text in the editor\n'c' or 'copy': copy the selected text\n'cut': cut (kill) the selected text\n'p' or 'paste': paste (yank) the last copied text\n'help' or 'h' or 'list': Open this\n'hmode': Change the HMode (Major Mode)\n'pf' or 'pagenext': Scroll down a page in the editor\n'pb' or 'pageback': Scroll up a page in the editor\n'clear': Clear the editor completely\n'full': Make the window fullscreen\n'max': Maximize the window\n'min': Minimize the window\n'pycode' or 'pc': Open PyCode (Elisp)\n'<Esc>': 'cancel'\n'sp' or 'speak': Speak the text selected out loud".replace('\n', '\n\n'))
    hxh.config(state = 'disabled')
    hxw.sizablefalse()
    hxw.style(root.gettheme())
    hxw.show()
def cmdrun(command):
    type_.focus_set()
    cmdentry.delete('1.0', 'end')
    cmdlabel.config(text = '')
    cmdentry.config(state = 'disabled')
    type_.config(state = 'normal')
    cmdentry.unbind('<Return>')
    cmdentry.unbind('<Escape>')
    if command == 'exit' or command == 'e':
        ext()
    elif command == 'save' or command == 's':
        sssv()
    elif command == 'search' or command == 'f':
        f()
    elif command == 'find-replace' or command == 'findreplace' or command == 'fr':
        fr()
    elif command == 'show-source' or command == 'source-code':
        ss()
    elif command == 'new' or command == 'n':
        nw()
    elif command == 'l' or command == 'gl' or command == 'gotoline':
        gl()
    elif command == 'open' or command == 'find' or command == 'o' or command == 'f' or command == 'load':
        llld()
    elif command == 'terminal' or command == 'cmd' or command == 'term' or command == 't':
        term()
    elif command == 'prf' or command == 'preferences':
        prf()
    elif command == 'cancel' or command == 'z':
        pass
    elif command == '':
        pass
    elif command == 'help' or command == 'h' or command == 'list':
        hx()
    elif command == 'a' or command == 'selall' or command == 'all':
        selall()
    elif command == 'copy' or command == 'c':
        cp()
    elif command == 'cut':
        cut()
    elif command == 'pf' or command == 'pagenext':
        ptf()
    elif command == 'pb' or command == 'pageback':
        ptb()
    elif command == 'paste' or command == 'p':
        pst()
    elif command == 'sp' or command == 'speak':
        spk()
    elif command == 'full':
        root.attributes('-fullscreen', True)
    elif command == 'max':
        root.attributes('-zoomed', True)
    elif command == 'min':
        root.iconify()
    elif command == 'clear':
        if root.ask('Warning', 'Do you really want to clear the editor?', options = ('ok', 'cancel'), icon = 'warning'):
            type_.delete('1.0', 'end')
            show('cleared')
    elif command == 'pycode' or command == 'pc':
        pc()
    elif command == 'hmode':
        ans = root.askstring('Change hmode', 'HMode (python / latex / normal):')
        if not ans:
            return
        ans = ans.lower().replace(' ', '')
        if ans == 'python' or ans == 'py':
            m.entryconfig(4, state = 'normal')
            m.entryconfig(5, state = 'disabled')
            filetype.config(text = 'Python File (.py)')
        elif ans == 'latex' or ans == 'la':
            m.entryconfig(5, state = 'normal')
            m.entryconfig(4, state = 'disabled')
            filetype.config(text = 'LaTeX File (.tex)')
        elif ans == 'normal' or ans == 'norm':
            m.entryconfig(4, state = 'disabled')
            m.entryconfig(5, state = 'disabled')
            filetype.config(text = 'Plain Text (*.*)')
        show('change hmode')
        keypress()
    else:
        show(text = f'command \'{command}\' undefined')
def selall(event = None):
    show(text = 'select all')
    type_.tag_add('sel', '1.0', 'end')
    return 'break'
def show(text):
    cmdentry.config(state = 'normal')
    cmdentry.delete('1.0', 'end')
    cmdentry.insert('end', text)
    cmdentry.config(state = 'disabled')
def cp(event = None):
    global root
    try:
        select = type_.get('sel.first', 'sel.last')
    except:
        return
    root.clipboard_clear()
    root.clipboard_append(select)
    show(text = 'copy text')
def cut(event = None):
    try:
        select = type_.get('sel.first', 'sel.last')
    except:
        return
    type_.delete('sel.first', 'sel.last')
    root.clipboard_clear()
    root.clipboard_append(select)
    show(text = 'cut text')
def spk(event = None):
    try:
        select = type_.get('sel.first', 'sel.last')
    except:
        return
    try:
        import pyttsx3 as stt
    except:
        root.error('Error', 'The module \'pyttsx3\' is not installed. Use "pip3 install pyttsx3" to install it before using the speech to text engine.')
    else:
        try:
            engine = stt.init()
            voices = engine.getProperty('voices')
            engine.setProperty('rate', 150)
            engine.say(select)
            engine.runAndWait()
        except Exception as error:
            root.error('Error', f'The following error occured:{error}')
        else:
            show('speak text')
def pst(event = None):
    global root
    try:
        text = root.clipboard_get()
    except:
        return
    type_.insert('insert', text)
    show(text = 'paste text')
    return 'break'
def cmd(event = None):
    cmdentry.config(state = 'normal')
    cmdentry.delete('1.0', 'end')
    cmdentry.focus_set()
    type_.config(state = 'disabled')
    cmdlabel.config(text = 'M-x-')
    cmdentry.bind('<Return>', lambda event: cmdrun(cmdentry.get('1.0', 'end')[:-1]))
    cmdentry.bind('<Escape>', lambda event: cmdrun('cancel'))
def ptf(event = None):
    type_.yview_scroll(1, 'pages')
def ptb(event = None):
    type_.yview_scroll(-1, 'pages')
def pcdone(nc):
    open(f'/home/{getpass.getuser()}/.pynotes', 'w+').write(nc)
    pcread()
def print(string):
    root.info('Print PyCode', string)
def input(string):
    return root.askstring('Input PyCode', string)
def pcrun(code):
    code = code.split('\n')
    variables = list()
    for line in code:
        if not re.findall(r'.+?=.+?', line):
            line_ = line
            if variables:
                for var in variables:
                    line_ = line_.replace(var[0], var[1])
            try:
                exec(line_)
            except Exception as error:
                root.error('Error', f'Error in PyCode: {error}')
        else:
            variables.append((line.split('=')[0], line.split('=')[1]))
def pcread():
    global wholenewbinds
    global root
    try:
        code = open(f'/home/{getpass.getuser()}/.pynotes', 'r').read().replace('\n', '').split(';')
    except:
        return
    cdt = ''
    for line in code:
        line = line.replace(' ', '') + ';'
        if line:
            ks = re.findall(r'<.+?>→<.+?>;', line)
            v = re.findall(r'\[.+?\]:→\[.+?\];', line)
            if ks and len(ks) == 1:
                ks = ks[0][:-1]
                wholenewwords.append(ks.split('→')[0])
                cdt += f"root.bind('{ks.split('→')[0]}', lambda event: pcrun(\"{ks.split('→')[1][:-1][1:]}\"))" + '\n'
            elif ks and len(ks) != 1:
                root.error('Error', f'Error in PyCode: line {ks} has too many arguments.')
            elif v and len(v) == 1:
                v = v[0][:-1]
                cdt += v.split(':→')[0][:-1][1:] + '=' + v.split(':→')[1][:-1][1:] + '\n'
            elif v and len(v) != 1:
                root.error('Error', f'Error in PyCode: line {v} has too many arguments.')
    pcrun(cdt)
def edit(widget, editfrom):
    if editfrom == '=':
        widget.insert('insert', '→')
        return 'break'
    elif editfrom == '<':
        widget.insert('insert', '>')
        widget.mark_set('insert', 'insert-1c')
    elif editfrom == ';':
        widget.insert('insert', ';\n')
        widget.mark_set('insert', 'insert+1c')
        return 'break'
    elif editfrom == '(':
        widget.insert('insert', ')')
        widget.mark_set('insert', 'insert-1c')
    elif editfrom == '[':
        widget.insert('insert', ']')
        widget.mark_set('insert', 'insert-1c')
    elif editfrom == "'":
        widget.insert('insert', "'")
        widget.mark_set('insert', 'insert-1c')
    elif editfrom == '"':
        widget.insert('insert', '"')
        widget.mark_set('insert', 'insert-1c')
def pc(event = None):
    global defs
    global wholenewwords
    for binded in wholenewwords:
        root.unbind(binded)
    wholenewwords.clear()
    pcwin = root.subwin()
    pcwin.title(f'PyCode - PyNotes')
    pcwin.style(defs[3])
    done = pcwin.button(text = 'Done', command = lambda: [pcdone(codeedit.get('1.0', 'end')), pcwin.destroy()])
    done.pack(side = 'bottom', fill = 'x')
    scrolly = pcwin.scroll()
    scrolly.pack(side = 'right', fill = 'y')
    codeedit = pcwin.textbox(yscrollcommand = scrolly.set, font = defs[2], wrap = 'word')
    codeedit.pack(side = 'left', fill = 'both')
    codeedit.focus_set()
    codeedit.bind('=', lambda event: edit(codeedit, '='))
    codeedit.bind('<less>', lambda event: edit(codeedit, '<'))
    codeedit.bind('<semicolon>', lambda event: edit(codeedit, ';'))
    codeedit.bind('(', lambda event: edit(codeedit, '('))
    codeedit.bind('[', lambda event: edit(codeedit, '['))
    codeedit.bind('<quoteright>', lambda event: edit(codeedit, "'"))
    codeedit.bind('<quotedbl>', lambda event: edit(codeedit, '"'))
    scrolly.config(command = codeedit.yview)
    try:
        open(f'/home/{getpass.getuser()}/.pynotes', 'r')
    except:
        open(f'/home/{getpass.getuser()}/.pynotes', 'w+')
    codeedit.insert('end', open(f'/home/{getpass.getuser()}/.pynotes', 'r').read())
    pcwin.style(root.gettheme())
    pcwin.show()
def helppycode():
    hpwin = root.subwin()
    hpwin.title('Help with PyCode')
    hptabs = hpwin.tabs()
    hptabs.pack(side = 'top', fill = 'both', padx = 10, pady = 10)
    kst = hpwin.frame()
    hptabs.add(kst, text = 'Keyboard Shortuts')
    vt = hpwin.frame()
    hptabs.add(vt, text = 'Defining Variables')
    hpwin.text(master = kst, text = 'To learn how to use PyCode,\nit would really help to know a bit of Tkinter and Python\nThis mainly uses the tkinter.Tk.bind function,\nso all the keys are typed the same way. For example,\nif you want to bind Control + q to close the window,\nyou would have to type:\n').grid(column = 0, row = 0)
    code = hpwin.style()
    code.configure('CodeStyle.TLabel', background = 'white', padding = (7, 7, 7, 7), relief = 'sunken')
    hpwin.text(master = kst, text = '<Control-q> → <root.destroy()>;', style = 'CodeStyle.TLabel').grid(column = 0, row = 1)
    hpwin.text(master = kst, text = '\n(You just have to type \'=\' to get \'→\' in the PyCode window)\nThe same way, Alt would be <Alt>, and so on.\nIf you want to bind anything and do not know how to type it,\njust search for how to bind a tkinter window to that key.\nIn this case, it would look something like this:\n').grid(column = 0, row = 2)
    hpwin.text(master = kst, text = 'root.bind("<Control-q>", lambda event: root.destroy())', style = 'CodeStyle.TLabel').grid(column = 0, row = 3)
    hpwin.text(master = kst, text = '\nThe lambda and the rest of the function will automatically\nbe typed for you. If you try to type it in like this, it will give an error.\n\n(IMPORTANT: Never forget to type the semicolon at the end of a line.\nOtherwise something may go wrong.)').grid(column = 0, row = 4)
    hpwin.text(master = vt, text = 'The syntax of defining variables has nothing to do with Tkinter or Python,\nunlike making keyboard shortcuts. This is a very simple thing.\nFor example, if you want to define a variable\n "something" with the value "somethingelse", you can type this:\n').grid(column = 0, row = 0)
    hpwin.text(master = vt, text = '[something] :→ ["something else"]', style = 'CodeStyle.TLabel').grid(column = 0, row = 1)
    hpwin.text(master = vt, text = '\nThen you can use this like this:\n').grid(column = 0, row = 2)
    hpwin.text(master = vt, text = '<Control-q> → <print(something)>', style = 'CodeStyle.TLabel').grid(column = 0, row = 3)
    hpwin.sizablefalse()
    hpwin.style(root.gettheme())
    hpwin.show()
def syncscroll(*args):
    ln.yview_moveto(args[0])
    scrlbr.set(*args)
tabs = root.tabs()
mf = root.frame()
sf = root.frame()
tabs.add(mf, text = 'Editor')
tabs.add(sf, text = 'Shell', state = 'disabled')
tabs.pack(padx = 10, pady = 10, fill = 'both', expand = True)
scrlbr = root.scroll(master = mf)
scrlbr.pack(side = 'right', fill = 'y')
ln = root.textbox(master = mf, width = 4, state = 'disabled', font = defs[2], yscrollcommand = lambda *args: ln.yview_moveto(type_.yview()[0]), wrap = 'none')
ln.pack(side = 'left', fill = 'y', anchor = 'n')
type_ = root.textbox(master = mf, yscrollcommand = syncscroll, font = defs[2], wrap = 'word')
type_.pack(fill = 'both', expand = True, anchor = 'n')
type_.insert('end',
"The Zen of Python, by Tim Peters\n\nBeautiful is better than ugly.\nExplicit is better than implicit.\nSimple is better than complex.\nComplex is better than complicated.\nFlat is better than nested.\nSparse is better than dense.\nReadability counts.\nSpecial cases aren't special enough to break the rules.\nAlthough practicality beats purity.\nErrors should never pass silently.\nUnless explicitly silenced.\nIn the face of ambiguity, refuse the temptation to guess.\nThere should be one-- and preferably only one --obvious way to do it.\nAlthough that way may not be obvious at first unless you're Dutch.\nNow is better than never.\nAlthough never is often better than *right* now.\nIf the implementation is hard to explain, it's a bad idea.\nIf the implementation is easy to explain, it may be a good idea.\nNamespaces are one honking great idea -- let's do more of those!")
scrlbr.config(command = type_.yview)
type_.focus_set()
fileinfo = root.frame()
cmdlabel = root.text()
cmdlabel.pack(side = 'left', padx = 10, pady = 10, anchor = 'n')
cmdentry = root.textbox(state = 'disabled', height = 1)
cmdentry.pack(padx = 10, pady = 10, fill = 'x', side = 'bottom')
fileinfo.pack(padx = 10, pady = 10, fill = 'both', side = 'bottom')
filename = root.text(master = fileinfo, text = 'The Zen of Python', padding = (5, 5, 5, 5), relief = 'raised')
filename.grid(column = 0, row = 0)
filetype = root.text(master = fileinfo, text = 'Plain Text (*.*)', padding = (5, 5, 5, 5), relief = 'sunken')
filetype.grid(column = 1, row = 0)
filesize = root.text(master = fileinfo, text = '0 bytes (Unnamed)', padding = (5, 5, 5, 5), relief = 'raised')
filesize.grid(column = 2, row = 0)
m = root.menu()
root.config(m = m)
fm = root.menu()
em = root.menu()
om = root.menu()
pm = root.menu()
lm = root.menu()
hm = root.menu()
m.add_cascade(label = 'File', menu = fm)
m.add_cascade(label = 'Edit', menu = em)
m.add_cascade(label = 'Options', menu = om)
m.add_cascade(label = 'Python', menu = pm, state = 'disabled')
m.add_cascade(label = 'LaTeX', menu = lm, state = 'disabled')
pm.add_command(label = 'Run → F5', command = rp)
pm.add_command(label = 'Run with अजगर', command = rp2)
lm.add_command(label = 'Run LuaLaTeX → F5', command = lp)
root.bind('<F5>', f5)
lm.add_command(label = 'Run PdfLaTeX', command = lp2)
m.add_cascade(label = 'Help', menu = hm)
em.add_command(label = 'Find → Ctrl + F', command = f)
root.bind('<Control-f>', f)
em.add_command(label = 'Find & Replace → Ctrl + Shift + F', command = fr)
root.bind('<Control-F>', fr)
hm.add_command(label = 'About', command = abt)
hm.add_command(label = f'What\'s new in {v}?', command = changes)
hm.add_command(label = 'Help with Alt-X → Alt + X - h', command = hx)
hm.add_separator()
hm.add_command(label = 'Recover backup', command = rb)
fm.add_command(label = 'New → Ctrl + N', command = nw)
root.bind('<Control-n>', nw)
fm.add_command(label = 'Open → Ctrl + L', command = llld)
root.bind('<Control-l>', llld)
fm.add_separator()
fm.add_command(label = 'Save → Ctrl + S', command = sssv)
root.bind('<Control-s>', sssv)
fm.add_command(label = 'Save as → Ctrl + Shift + S', command = ssv)
root.bind('<Control-S>', ssv)
fm.add_separator()
fm.add_command(label = 'Quit → Ctrl + W', command = ext)
root.bind('<Control-w>', ext)
om.add_command(label = 'Preferences → Ctrl + P', command = prf)
root.bind('<Control-p>', prf)
om.add_command(label = 'Source Code', command = ss)
om.add_separator()
om.add_command(label = 'Go to line → Alt + L / Alt + X - l', command = gl)
root.bind('<Alt-l>', gl)
om.add_command(label = 'Page turn → Ctrl + P / Alt + X - pf', command = ptf)
root.bind('<Control-p>', ptf)
om.add_command(label = 'Page turn (back) → Ctrl + Shift + P / Alt + X - pb', command = ptb)
root.bind('<Control-P>', ptb)
om.add_separator()
om.add_command(label = 'Command → Alt + X', command = cmd)
om.add_command(label = 'PyCode → Alt + X - pc', command = pc)
em.add_separator()
em.add_command(label = 'Select All → Ctrl + A / Alt + X - a', command = selall)
em.add_command(label = 'Copy → Ctrl + C / Alt + X - c', command = cp)
em.add_command(label = 'Paste → Ctrl + V / Alt + X - p', command = pst)
em.add_command(label = 'Cut → Ctrl + X / Alt + X - cut', command = cut)
root.text(master = sf, text = '>>>').grid(column = 0, row = 0, padx = 5, pady = 5)
shellcmd = root.textbox(master = sf)
shellcmd.grid(column = 1, row = 0, padx = 5, pady = 5, sticky = 'nsew')
shellout = root.listbox(master = sf)
shellout.grid(column = 1, row = 1, padx = 5, pady = 5, sticky = 'nsew')
sf.grid_rowconfigure(0, weight = 1)
sf.grid_columnconfigure(1, weight = 1)
sf.grid_rowconfigure(1, weight = 1)
root.button(master = sf, text = 'Exec', command = lambda: [shellout.insert('end', line) for line in shellexec(shellcmd.get('1.0', 'end')).split('\n')] + [shellcmd.delete('1.0', 'end'), shellout.insert('end', '\n'), shellout.see('end')]).grid(column = 1, row = 2, padx = 5, pady = 5)
root.bind('<Alt-x>', cmd)
type_.bind('<Control-a>', selall)
type_.bind('<Control-c>', cp)
type_.bind('<Control-v>', pst)
type_.bind('<Control-x>', cut)
om.add_command(label = 'Terminal (Beta)', command = term)
om.add_separator()
om.add_command(label = 'Speak Text → Alt + X - sp', command = spk)
type_.bind('<KeyRelease>', keypress)
type_.bind('<BackSpace>', lambda event: show('delete text'))
type_.bind('<Delete>', lambda event: show('delete text'))
root.protocol('WM_DELETE_WINDOW', ext)
hm.add_separator()
hm.add_command(label = 'Help with PyCode', command = helppycode)
wholenewwords = list()
pcread()
keypress()
if len(sys.argv) > 1:
    if not sys.argv[1] == '--version':
        ld(sys.argv[1])
        if len(sys.argv) > 2:
            for file in sys.argv[2:]:
                os.system(f'PyNotes "{file}"')
    else:
        os.system(f'echo {v}')
        root.destroy()
        exit()
cmdrun('max')
root.update()
root.style(defs[3])
root.show()
