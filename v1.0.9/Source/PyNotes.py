import easytk
import os
import sys
import io
import time
import keyword
import getpass
from runnerpython import ragoae
from runnerpython import ragoae_other
root = easytk.win()
start = time.time()
bfr = True
v = '1.0.9'
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
    answer = root.ask('Warning', 'Do you want to save file before closing ?', options = ('yes', 'no', 'cancel'), icon = 'warning') if filename.cget('text')[-1:] == '*' else False
    if answer != None:
        if answer:
            sv(title)
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
    cw__ = cw.frame(master = cw_)
    cw_.pack(fill = 'both', padx = 10, pady = 10)
    cw__.grid(column = 0, row = 2, sticky = 'w')
    cw.text(master = cw_, text = '1. Changed the icon!').grid(column = 0, row = 0, sticky = 'w')
    cw.text(master = cw_, text = '2. A lot of important stuff').grid(column = 0, row = 1, sticky = 'w')
    cw.text(master = cw__, text = 'IMPORTANT: A system like Elisp (Emacs) will probably come soon!\n(although instead of Lisp, it will probably have a syntax more like Python\'s or it\'s own new way)', relief = 'sunken', padding = (10, 10, 10, 10)).grid(column = 0, row = 0, sticky = 'w')
    cw.button(text = 'Close', command = cw.destroy).pack(side = 'bottom', fill = 'x', padx = 10, pady = 10)
    cw.bind('<Return>', lambda event: cw.destroy())
    cw.sizablefalse()
    cw.show()
def lld():
    fn = root.openfile(('all', 'py', 'txt', 'tex'))
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
    answer = root.ask('Warning', 'Do you want to save file before closing ?', options = ('yes', 'no', 'cancel'), icon = 'warning') if filename.cget('text')[-1:] == '*' else False
    if answer != None:
        if answer:
            sv(title)
        root.destroy()
def ld(nm):
    global type_
    global root
    global m
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
            keypress()
def llld(event = None):
    answer = root.ask('Warning', 'Do you want to save file before closing ?', options = ('yes', 'no', 'cancel'), icon = 'warning') if filename.cget('text')[-1:] == '*' else False
    if answer != None:
        if answer:
            sv(title)
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
    answer = root.ask('Warning', 'Do you want to save file before closing ?', options = ('yes', 'no', 'cancel'), icon = 'warning') if filename.cget('text')[-1:] == '*' else False
    if answer != None:
        if answer:
            sv(title)
        type_.delete('1.0', 'end')
        clt('')
        filename.config(text = 'Untitled')
        filetype.config(text = 'Plain Text (*.*)')
        filesize.config(text = '0 bytes (Unnamed)')
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
    ok = easytk.win()
    ok.title('Search')
    ok.button(text = 'Close search', command = lambda: [type_.tag_remove('found', '1.0', 'end'), ok.destroy()]).grid(padx = 10, pady = 10)
    ok.bind('<Return>', lambda event: [type_.tag_remove('found', '1.0', 'end'), ok.destroy(), root.unbind('<Return>')])
    root.bind('<Return>', lambda event: [type_.tag_remove('found', '1.0', 'end'), ok.destroy(), root.unbind('<Return>')])
    ok.sizablefalse()
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
def bf(opt):
    global bfr
    bfr = opt
def svprf():
    pass
def prf(event = None):
    global bfr
    pr = easytk.win()
    pr.style(root.gettheme())
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
    f = pr.droptype(options = tuple(sorted(pr.getfonts())), master = mf, command = lambda: [pr.sizabletrue(), type_.config(font = (f.get(), 12)), showfont.config(font = (f.get(), 12)), pr.sizablefalse()])
    f.grid(column = 1, row = 1, padx = 10, pady = 10)
    f.insert('end', type_.cget('font'))
    pr.bind('<Return>', lambda event: pr.destroy())
    pr.protocol('WM_DELETE_WINDOW', lambda: [svprf(), pr.destroy()])
    pr.button(text = 'OK', command = pr.destroy).pack(side = 'bottom', fill = 'x', padx = 10, pady = 10)
    pr.sizablefalse()
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
    for k in ('file', 'open', 'map', 'int', 'str', 'print', 'range', 'set', 'input', 'list', 'len', 'self', 'type', 'exec', 'sum', 'iter', 'dir', 'compile', 'eval', 'format', 'locals', 'cls', 'exit', 'dict', 'repr', 'hasattr', 'setattr', 'super', 'isinstance', 'object', 'tuple', 'float'):
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
    if bfr and title and int(time.time() - start) % 10:
        open(os.path.join(os.path.dirname(os.path.splitext(title)[0]), '.' + os.path.basename(os.path.splitext(title)[0]) + 'backpynotes' + os.path.splitext(title)[1]), 'w+').write(type_.get('1.0', 'end'))
    if wordlist and filetype.cget('text') != 'Python File (.py)' and filetype.cget('text') != 'LaTeX File (.tex)': spellcheck()
    filesize.config(text = str(len(io.StringIO(type_.get('1.0', 'end')).read()) - 1) + ' bytes')
    if filetype.cget('text') == 'Python File (.py)': ha('py')
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
        tw = easytk.win()
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
        tw.show()
def gl(event = None):
    l = root.askstring('Go to line', 'Go to line no. :')
    if not l:
        return
    try:
        l = int(l)
    except:
        root.error('Error', f'Cannot go to line number {l}')
        return
    else:
        type_.see(f'{l}.0')
        type_.mark_set('insert', f'{l}.0')
        type_.tag_add('sel', f'{l}.0', f'{l}.end')
def hx():
    root.info('Help with Ctrl-X', "'exit' or 'e': exit the window (the same as File -> Exit)\n'save' or 's': save the current file (the same as File -> Save)\n'search' or 'f': find a string in the editor (the same as Edit -> Find)\n'fr' or 'find-replace' or 'findreplace': find and replace a string in the editor instantly (the same as Edit -> Find&Replace)\n'show-source' or 'source-code': show and edit the main source code of PyNotes (/usr/share/PyNotes/main.py) (the same as Options -> Source Code)(this does not have a shortcut like 'sc' because it is used very rarely)\n'new' or 'n': open a new document (the same as File -> New)\n'o' or 'f' or 'load' or 'find' of 'open' or 'l': Load anew file into the editor (the same as File -> Open)\n't' or 'term' or 'terminal' or 'cmd': Open the small terminal (the same as Options -> Terminal)\n'prf' or 'p' or 'preferences': Change the preferences (the same as Options -> Preferences)\n'cancel' or 'c': Cancel the command and go back to the editor\n'help' or 'h' or 'list': Open this\nother: return \"command '{other}' undefined\"".replace('\n', '\n\n'))
def cmdrun(command):
    type_.focus_set()
    cmdentry.delete('1.0', 'end')
    cmdlabel.config(text = '')
    cmdentry.config(state = 'disabled')
    type_.config(state = 'normal')
    cmdentry.unbind('<Return>')
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
    elif command == 'open' or command == 'find' or command == 'o' or command == 'f' or command == 'l' or command == 'load':
        llld()
    elif command == 'terminal' or command == 'cmd' or command == 'term' or command == 't':
        term()
    elif command == 'prf' or command == 'p' or command == 'preferences':
        prf()
    elif command == 'cancel' or command == 'c':
        pass
    elif command == 'help' or command == 'h' or command == 'list':
        hx()
    else:
        cmdentry.config(state = 'normal')
        cmdentry.insert('end', f'command \'{command}\' undefined')
        cmdentry.config(state = 'disabled')
def cmd(event = None):
    cmdentry.config(state = 'normal')
    cmdentry.delete('1.0', 'end')
    cmdentry.focus_set()
    type_.config(state = 'disabled')
    cmdlabel.config(text = 'C-x-')
    cmdentry.bind('<Return>', lambda event: cmdrun(cmdentry.get('1.0', 'end')[:-1]))
mf = root.frame()
mf.pack(padx = 10, pady = 10, fill = 'both')
scrlbr = root.scroll(master = mf)
scrlbr.pack(side = 'right', fill = 'y')
type_ = root.textbox(master = mf, yscrollcommand = scrlbr.set, width = 100, height = 50)
type_.pack(fill = 'both')
type_.focus()
scrlbr.config(command = type_.yview)
fileinfo = root.frame()
cmdlabel = root.text()
cmdlabel.pack(side = 'left', padx = 10, pady = 10, anchor = 'n')
cmdentry = root.textbox(state = 'disabled', height = 1)
cmdentry.pack(padx = 10, pady = 10, fill = 'x')
fileinfo.pack(padx = 10, pady = 10, fill = 'both')
filename = root.text(master = fileinfo, text = 'Untitled', padding = (5, 5, 5, 5), relief = 'raised')
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
pm.add_command(label = 'Run -> F5', command = rp)
pm.add_command(label = 'Run with अजगर', command = rp2)
lm.add_command(label = 'Run LuaLaTeX -> F5', command = lp)
root.bind('<F5>', f5)
lm.add_command(label = 'Run PdfLaTeX', command = lp2)
m.add_cascade(label = 'Help', menu = hm)
em.add_command(label = 'Find -> Ctrl + F', command = f)
root.bind('<Control-f>', f)
em.add_command(label = 'Find & Replace -> Ctrl + Shift + F', command = fr)
root.bind('<Control-F>', fr)
hm.add_command(label = 'About', command = abt)
hm.add_command(label = f'What\'s new in {v}?', command = changes)
hm.add_command(label = 'Help with Ctrl-X -> Ctrl + X - h', command = hx)
hm.add_separator()
hm.add_command(label = 'Recover backup', command = rb)
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
om.add_command(label = 'Preferences -> Ctrl + P', command = prf)
root.bind('<Control-p>', prf)
om.add_command(label = 'Source Code', command = ss)
om.add_separator()
om.add_command(label = 'Go to line -> Alt + L', command = gl)
root.bind('<Alt-l>', gl)
om.add_separator()
om.add_command(label = 'Command -> Ctrl + X', command = cmd)
root.bind('<Control-x>', cmd)
om.add_command(label = 'Terminal (Beta)', command = term)
root.bind('<KeyRelease>', keypress)
root.protocol('WM_DELETE_WINDOW', ext)
if len(sys.argv) > 1:
    ld(sys.argv[1])
root.show()
