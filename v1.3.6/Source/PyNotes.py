from encrypter import encryptdecrypt
import easytk
import os
import subprocess
import sys
import io
import time
import math as mathmod
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import keyword
import re
import getpass
import threading
from runnerpython import ragoae
from runnerpython import interactive_shell
from runnerpython import ragoae_other
def ask(title, askinput):
    def yes():
        global returnval
        askwin.destroy()
        returnval = True
    def no():
        global returnval
        askwin.destroy()
        returnval = False
    askwin = easytk.win()
    askwin.title(title)
    askwin.text(text = askinput).pack(side = 'top', anchor = 'n', padx = 10, pady = 10)
    askwin.button(text = 'Yes', command = yes).pack(side = 'left', anchor = 'nw', padx = 10, pady = 10)
    askwin.button(text = 'No', command = no).pack(side = 'right', anchor = 'ne', padx = 10, pady = 10)
    askwin.protocol('WM_DELETE_WINDOW', lambda: None)
    askwin.show()
    return returnval
def faketerm(number):
    termwin = easytk.win()
    term = termwin.textbox(background = 'black', foreground = 'white', font = ('Ubuntu Mono', 12))
    term.insert('end', f'{getpass.getuser()}@PyNotes:~$ ')
    if number == 0:
        command = 'pip3 install tika'
    elif number == 1:
        command = 'pip3 install pdfplumber'
    elif number == 2:
        command = 'pip3 install pyttsx3'
    term.insert('end', command + '\n')
    term.pack(fill = 'both')
    termwin.update()
    try:
        result = subprocess.run(command, shell = True, text = True, capture_output = True)
        item = result.stdout + result.stderr
    except Exception as error:
        item = str(error)
    term.insert('end', item)
    termwin.update()
    time.sleep(2)
    termwin.destroy()
try:
    import tika
    from tika import parser
except:
    ans = ask('Error!', 'The module \'tika\' is not installed. Should PyNotes install it locally?')
    if not ans:
        exit()
    else:
        faketerm(0)
try:
    import pdfplumber
except:
    ans = ask('Error!', 'The module \'pdfplumber\' is not installed. Should PyNotes install it locally?')
    if not ans:
        exit()
    else:
        faketerm(1)
try:
    import pyttsx3 as stt
except:
    ans = ask('Error!', 'The module \'pyttsx3\' is not installed. Should PyNotes install it locally?')
    if not ans:
        exit()
    else:
        faketerm(2)
root = easytk.win()
start = time.time()
v = '1.3.6'
try:
    os.mkdir(f'/home/{getpass.getuser()}/.local/PyNotes/')
except:
    pass
try:
    file = open(f'/home/{getpass.getuser()}/.local/PyNotes/defs', 'r')
except:
    file = open(f'/home/{getpass.getuser()}/.local/PyNotes/defs', 'w+')
    file.write(f'{v}\nFalse\nTkDefaultFont\nice\nenglish.txt')
    file.close()
    file = open(f'/home/{getpass.getuser()}/.local/PyNotes/defs', 'r')
defs = file.read().split('\n')
file.close()
dicts = defs[4].split(',')
if not v == defs[0]:
    root.info('Info', 'PyNotes has been updated!')
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
    cw_.pack(fill = 'both', padx = 10, pady = 10)
    cw.text(master = cw_, text = '1. Added EMAIL to PyNotes! (See Help → Help with Email)\nThere is a spellcheck in the email.\nSee Help → Help with Email → Dictionaries for how to add or remove additional dictionaries.').grid(column = 0, row = 0, sticky = 'w')
    cw.button(text = 'Close', command = cw.destroy).pack(side = 'bottom', fill = 'x', padx = 10, pady = 10)
    cw.bind('<Return>', lambda event: cw.destroy())
    cw.sizablefalse()
    cw.style(root.gettheme())
    cw.show()
def hemail(event = None):
    hew = root.subwin()
    hew.title('Help with Email')
    tabs = hew.tabs()
    mf = hew.frame()
    tabs.add(mf, text = 'Setup')
    tabs.pack(fill = 'both', expand = True, padx = 10, pady = 10)
    hew.text(master = mf, text = 'First change the HMode to Email with Alt-X and \'hmode:em\'.\nThis will enable the tab \'Email\'.\nGo to that tab and give the username and password of your email.\nThen you can type and send any email from PyNotes!').grid(padx = 10, pady = 10)
    dt = hew.frame()
    tabs.add(dt, text = 'Dictionaries')
    hew.text(master = dt, text = 'The email textbox has a spellcheck. The default wordlist for spellchecking is just english, but you can add or remove extra dictionaries to this.\nYou need to find or make a text file that has one word in each line, without any spaces. (It can be any language)\nThen go to Preferences → Email to upload that dictionary.\nONCE YOU HAVE ADDED A DICTIONARY, DO NOT MOVE THE FILE BEFORE REMOVING THE DICTIONARY IN THE PREFERENCES.').grid(padx = 10, pady = 10)
    hew.sizablefalse()
    hew.style(root.gettheme())
    hew.show()
def lld():
    fn = root.openfile(('all', 'py', 'txt', 'tex', 'png', 'pdf', 'epub'))
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
                try:
                    pdf = pdfplumber.open(nm)
                    type_.delete('1.0', 'end')
                    for page in pdf.pages:
                        type_.insert('end', page.extract_text())
                except:
                    try:
                        parsed = parser.from_file(nm, service = 'text')
                        content = parsed['content']
                        type_.delete('1.0', 'end')
                        type_.insert('end', content)
                    except:
                        root.error('Error', error)
                    else:
                        show('open file')
                        clt(nm)
                        filesize.config(text = str(os.path.getsize(nm)) + 'bytes')
                        m.entryconfig(4, state = 'disabled')
                        m.entryconfig(5, state = 'disabled')
                        tabs.tab(2, state = 'hidden')
                        for widget in lf.winfo_children()[1:]:
                            widget.config(state = 'disabled')
                        filetype.config(text = 'EPUB File (*.epub)')
                        keypress()
                else:
                    show('open file')
                    clt(nm)
                    filesize.config(text = str(os.path.getsize(nm)) + 'bytes')
                    m.entryconfig(4, state = 'disabled')
                    m.entryconfig(5, state = 'disabled')
                    tabs.tab(2, state = 'hidden')
                    for widget in lf.winfo_children()[1:]:
                        widget.config(state = 'disabled')
                    filetype.config(text = 'PDF File (*.pdf)')
                    keypress()
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
                m.entryconfig(4, state = 'disabled')
                m.entryconfig(5, state = 'disabled')
                tabs.tab(2, state = 'hidden')
                for widget in lf.winfo_children()[1:]:
                    widget.config(state = 'disabled')
        else:
            show('open file')
            clt(nm)
            filesize.config(text = str(os.path.getsize(nm)) + ' bytes')
            if os.path.splitext(nm)[1] == '.py':
                m.entryconfig(4, state = 'normal')
                m.entryconfig(5, state = 'disabled')
                tabs.tab(2, state = 'hidden')
                for widget in lf.winfo_children()[1:]:
                    widget.config(state = 'disabled')
                filetype.config(text = 'Python File (' + os.path.splitext(nm)[1] + ')')
            elif os.path.splitext(nm)[1] == '.tex':
                m.entryconfig(4, state = 'disabled')
                m.entryconfig(5, state = 'normal')
                tabs.tab(2, state = 'hidden')
                for widget in lf.winfo_children()[1:]:
                    widget.config(state = 'normal')
                filetype.config(text = 'LaTeX File (' + os.path.splitext(nm)[1] + ')')
            else:
                filetype.config(text = 'Plain Text (*.*)')
                m.entryconfig(4, state = 'disabled')
                m.entryconfig(5, state = 'disabled')
                tabs.tab(2, state = 'hidden')
                for widget in lf.winfo_children()[1:]:
                    widget.config(state = 'disabled')
            keypress()
        type_.edit_reset()
def llld(event = None):
    answer = root.ask('Warning', 'Do you want to save file before closing ?', options = ('yes', 'no', 'cancel'), icon = 'warning') if filename.cget('text')[-1:] == '*' and not filename.cget('text') == '*scratch*' else False
    if answer != None:
        if answer:
            sv(title)
        lld()
def sv(nm):
    global root
    if not nm == '':
        if not filetype.cget('text') in ['PNG Image (*.png)', 'PDF File (*.pdf)', 'EPUB File (*.epub)']:
            try:
                file = open(nm, 'w')
                file.writelines(type_.get(1.0, 'end-1c'))
                file.close()
                clt(nm)
            except:
                pass
            else:
                show('save file')
        else:
            root.error('Error!', 'Cannot save files of this type')
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
        type_.edit_reset()
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
        show('replace string')
def f(event = None):
    global type_
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
                if not ok.winfo_exists(): raise Exception
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
        show('find string')
def bf(opt):
    global bfr
    bfr = opt
def svprf():
    global bfr
    file = open(f'/home/{getpass.getuser()}/.local/PyNotes/defs', 'w+')
    file.write(f"{v}\n{str(bfr)}\n{type_.cget('font')}\n{root.gettheme()}\n{','.join(dicts)}")
    file.close()
def prf(event = None):
    global bfr
    def removedict():
        try:
            dicts.remove(dictlist.selection_get())
        except:
            pass
        else:
            dictlist.delete(dictlist.curselection())
        wordlist.clear()
        try:
            for dictionary in dicts:
                if dictionary:
                    wordlist.extend(open(dictionary, 'r').read().split('\n'))
        except Exception as error:
            root.error('Error', error)
    def adddict():
        dicttoadd = pr.openfile(['txt'])
        if dicttoadd:
            dicts.append(dicttoadd)
            dictlist.insert('end', dicttoadd)
        wordlist.clear()
        try:
            for dictionary in dicts:
                if dictionary:
                    wordlist.extend(open(dictionary, 'r').read().split('\n'))
        except Exception as error:
            root.error('Error', error)
    pr = root.subwin()
    pr.title('Preferences')
    tabs = pr.tabs()
    gt = pr.frame()
    tft = pr.frame()
    et = pr.frame()
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
    tabs.add(et, text = 'Email')
    pr.text(master = et, text = 'Dictionaries:').pack(padx = 10, pady = 10, side = 'top', anchor = 'n')
    dictlist = pr.listbox(master = et)
    for dictionary in dicts:
        dictlist.insert('end', dictionary)
    dictlist.pack(fill = 'both', expand = True, padx = 10, pady = 10, anchor = 'center')
    pr.button(master = et, text = 'Remove', command = removedict).pack(fill = 'x', expand = True, padx = 10, pady = 10, side = 'left', anchor = 'sw')
    pr.button(master = et, text = 'Add', command = adddict).pack(fill = 'x', expand = True, padx = 10, pady = 10, side = 'right', anchor = 'se')
    pr.button(text = 'OK', command = lambda: [svprf(), show('change / view preferences'), pr.destroy()]).pack(side = 'bottom', fill = 'x', padx = 10, pady = 10)
    pr.protocol('WM_DELETE_WINDOW', lambda: [svprf(), show('change / view preferences'), pr.destroy()])
    pr.sizablefalse()
    pr.style(root.gettheme())
    pr.show()
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
        start = type_.search(r'\\begin{.+?}', start, nocase = 1, stopindex = 'end', regexp = True)
        if not start:
            break
        end = type_.search(r'\\end{.+?}', start, nocase = 1, stopindex = 'end', regexp = True)
        if not end:
            break
        type_.tag_add('hlb', start, end.split('.')[0] + '.end')
        start = end
    type_.tag_config('hlb', background = 'yellow')
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
        n = type_.search(searchstr, n, nocase = 1, count = count, stopindex = 'end', regexp = True)
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
        hld()
        hle()
        hlf()
        hlg()
def keypress(event = None):
    global bfr
    global ln
    global type_
    global tab
    lines = int(type_.index('end-1c').split('.')[0])
    ln.config(state = 'normal')
    ln.delete('1.0', 'end')
    for i in range(lines):
        ln.insert('end', str(i + 1) + '\n')
    ln.config(state = 'disabled')
    for tag in type_.tag_names():
        if not tag == 'sel': type_.tag_remove(tag, '1.0', 'end')
    if all((not filetype.cget('text') in ['PNG Image (*.png)', 'PDF File (*.pdf)', 'EPUB File (*.epub)'], bfr, title, int(time.time() - start) % 3 == 0)):
        open(os.path.join(os.path.dirname(os.path.splitext(title)[0]), '.' + os.path.basename(os.path.splitext(title)[0]) + 'backpynotes' + os.path.splitext(title)[1]), 'w+').write(type_.get('1.0', 'end'))
        show('backing up ... done')
    filesize.config(text = str(len(io.StringIO(type_.get('1.0', 'end')).read()) - 1) + ' bytes')
    tabs.tab(1, state = 'hidden')
    if filetype.cget('text') == 'Python File (.py)':
        tabs.tab(1, state = 'normal')
        ha('py')
    elif filetype.cget('text') == 'LaTeX File (.tex)':
        ha('latex')
    if title and not filetype.cget('text') in ['PNG Image (*.png)', 'PDF File (*.pdf)', 'EPUB File (*.epub)']:
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
shell = interactive_shell()
def shellexec(command):
    global shell
    output = shell.ragoae(command)
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
        root.error('Error', 'The pdf could not be shown, there could have been an error in your code?')
        return
    else:
        os.system('xdg-open ' + '"' + pdf_ + '"')
def runtex(compiler):
    global type_
    global title
    compiler += 'latex '
    if os.path.splitext(title)[1] == '.tex':
        pdf_ = os.path.splitext(title)[0]
    else:
        pdf_ = title
    pdf_ += '.pdf'
    try:
        os.remove(pdf_)
    except:
        pass
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
def termexec(command):
    if command[:2] == 'cd':
        try:
            os.chdir(command[3:])
        except Exception as error:
            return str(error)
        else:
            return ''
    else:
        try:
            result = subprocess.run(command, shell = True, text = True, capture_output = True, timeout = 5)
            item = result.stdout + result.stderr
        except subprocess.TimeoutExpired:
            item = 'error: time expired'
        except Exception as error:
            item = str(error)
        return item
readonlytext = f'{getpass.getuser()}@PyNotes:{os.getcwd()}$ '
readonlyend = '1.' + str(len(f'{getpass.getuser()}@PyNotes:{os.getcwd()}$ '))
def term():
    global readonlytext
    global readonlyend
    readonlytext = f'{getpass.getuser()}@PyNotes:{os.getcwd()}$ '
    readonlyend = '1.' + str(len(f'{getpass.getuser()}@PyNotes:{os.getcwd()}$ '))
    def check_edit():
        term.delete('1.0', readonlyend)
        term.insert('1.0', readonlytext)
        term.see('end')
    def exec():
        global readonlyend
        global readonlytext
        command = term.get(term.index('end-2c').split('.')[0] + '.0', 'end-2c')[len(f'{getpass.getuser()}@PyNotes:{os.getcwd()}$ '):].strip()
        output = None
        if all((not command == 'clear', not command == 'exit')):
            output = termexec(command)
        elif command == 'clear':
            term.delete('1.0', 'end')
        elif command == 'exit':
            tw.destroy()
        if not output == None:
            term.insert('end', output + '\n' + f'{getpass.getuser()}@PyNotes:{os.getcwd()}$ ')
            readonlyend = term.index('end-1c').split('.')[0] + '.' + str(len(f'{getpass.getuser()}@PyNotes:{os.getcwd()}$ '))
            readonlytext += command + '\n' + output + '\n' + f'{getpass.getuser()}@PyNotes:{os.getcwd()}$ '
        else:
            readonlytext = f'{getpass.getuser()}@PyNotes:{os.getcwd()}$ '
            readonlyend = '1.' + str(len(f'{getpass.getuser()}@PyNotes:{os.getcwd()}$ '))
            term.insert('end', readonlytext)
        term.see('end')
    tw = root.subwin()
    tw.title('Terminal')
    term = tw.textbox(background = 'black', foreground = 'white', font = ('Ubuntu Mono', 12), insertbackground = 'white')
    term.insert('end', f'{getpass.getuser()}@PyNotes:{os.getcwd()}$ ')
    term.bind('<KeyPress>', lambda event: check_edit())
    tw.bind('<Return>', lambda event: exec())
    term.pack(fill = 'both')
    tw.update()
    tw.sizablefalse()
    term.focus()
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
    hxh.insert('end', "'exit' or 'e': exit the window (the same as File → Exit)\n'save' or 's': save the current file (the same as File → Save)\n'u' or 'undo': undo the last edit\n'r' or 'redo': redo the last undoed edit\n'termexec:{string}' or 'te:{string}': run the given string as a terminal command\n'write:{string}*{n}' or 'w:{string}*{n}': copy the given text {n} number of times after the cursor position\n'search' or 'f': find a string in the editor (the same as Edit → Find)\n'fr' or 'find-replace' or 'findreplace': find and replace a string in the editor instantly (the same as Edit → Find&Replace)\n'show-source' or 'source-code': show and edit the main source code of PyNotes (/usr/share/PyNotes/main.py) (the same as Options → Source Code)\n'new' or 'n': open a new document (the same as File → New)\n'gotoline' or 'gl' or 'l': go to a specified line\n'pyshell' or 'ps': Open the Python shell if you are in Python mode.\n'o' or 'f' or 'load' or 'find' or 'open': Load a new file into the editor (the same as File → Open)\n't' or 'term' or 'terminal' or 'cmd': Open the terminal (the same as Options → Terminal)\n'prf' or 'preferences': Change the preferences (the same as Options → Preferences)\n'cancel' or 'z': Cancel the command and go back to the editor\n'a' or 'selall' or 'all': select all the text in the editor\n'c' or 'copy': copy the selected text\n'cut': cut the selected text\n'p' or 'paste': paste  the last copied text\n'help' or 'h' or 'list': Open this\n'hmode:{(py/la/norm/em)}': Change the HMode \n'pf' or 'pagenext': Scroll down a page in the editor\n'pb' or 'pageback': Scroll up a page in the editor\n'clear': Clear the editor completely\n'full': Make the window fullscreen\n'max': Maximize the window\n'min': Minimize the window\n'pycode' or 'pc': Open PyCode\n'<Esc>': 'cancel'\n'sp' or 'speak': Speak the text selected out loud".replace('\n', '\n\n'))
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
    elif command == 'pyshell' or command == 'ps':
        if filetype.cget('text') == 'Python File (.py)':
            sf.focus()
            tabs.select(1)
            shellcmd.focus()
    elif command[:8] == 'termexec' or command[:2] == 'te':
        try:
            termexec(command.split(':')[1])
        except:
            show(f'invalid command \'{command}\'')
    elif command[:5] == 'write' or command[:1] == 'w':
        try:
            type_.insert(type_.index('insert'), command.split(':')[1].split('*')[0] * int(command.split('*')[1]))
        except:
            show(f'invalid command \'{command}\'')
    elif command == 'u' or command == 'undo':
        undo()
    elif command == 'r' or command == 'redo':
        redo()
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
    elif command[:5] == 'hmode':
        try:
            ans = command.split(':')[1]
            ans = ans.lower().replace(' ', '')
            if ans == 'python' or ans == 'py':
                m.entryconfig(4, state = 'normal')
                m.entryconfig(5, state = 'disabled')
                tabs.tab(2, state = 'hidden')
                for widget in lf.winfo_children()[1:]:
                    widget.config(state = 'disabled')
                filetype.config(text = 'Python File (.py)')
            elif ans == 'latex' or ans == 'la':
                m.entryconfig(5, state = 'normal')
                m.entryconfig(4, state = 'disabled')
                tabs.tab(2, state = 'hidden')
                for widget in lf.winfo_children()[1:]:
                    widget.config(state = 'enabled')
                filetype.config(text = 'LaTeX File (.tex)')
            elif ans == 'normal' or ans == 'norm':
                m.entryconfig(4, state = 'disabled')
                m.entryconfig(5, state = 'disabled')
                tabs.tab(2, state = 'hidden')
                for widget in lf.winfo_children()[1:]:
                    widget.config(state = 'disabled')
                filetype.config(text = 'Plain Text (*.*)')
            elif ans == 'email' or ans == 'em':
                m.entryconfig(4, state = 'disabled')
                m.entryconfig(5, state = 'disabled')
                filetype.config(text = 'Plain Text (*.*)')
                tabs.tab(2, state = 'normal')
            show('change hmode')
            keypress()
        except:
            show(f'invalid command \'{command}\'')
    else:
        show(text = f'invalid command \'{command}\'')
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
engine = stt.init()
def actualspk(text):
    global engine
    try:
        engine.say(text)
        engine.runAndWait()
    except Exception as error:
        root.error('Error', f'An error occured:{error}')
    else:
        show('speak text')
def spk(event = None):
    try:
        select = type_.get('sel.first', 'sel.last')
    except:
        return
    else:
        speakthread = threading.Thread(target = actualspk, args = (select,))
        speakthread.start()
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
def say(string):
    root.info('Print PyCode', string)
def ask(string):
    ans = root.askstring('Input PyCode', string)
    exec(f'answer = \'{ans}\'', globals())
def pcrun(code):
    code = code.split('\n')
    variables = list()
    for line in code:
        if not re.findall(r'.+?=.+?', line):
            line_ = line
            if variables:
                for var in variables:
                    varreplaces = re.findall(r'(?<!\')' + var[0] + r'(?!\')', line_)
                    if varreplaces:
                        for found in varreplaces:
                            line_ = line_.replace(found, var[1])
            try:
                exec(line_, globals())
            except Exception as error:
                root.error('Error', f'Error in PyCode: {error}')
        else:
            variables.append((line.split('=')[0], line.split('=')[1]))
def pcread():
    global root
    pycodecommands = ['wait', 'quit', 'say', 'command', 'selall', 'copy', 'paste', 'ask', 'cut', 'term', 'cmd', 'undo', 'redo', 'termexec']
    pythoncommands = ['time.sleep', 'root.destroy()', 'say', 'cmd()', 'selall()', 'cp()', 'pst()', 'ask', 'cut()', 'term()', 'cmdrun', 'undo()', 'redo()', 'termexec']
    def pycodeindex(pycodecode):
        if pycodecode in pycodecommands:
            return pythoncommands[pycodecommands.index(pycodecode)]
        elif pycodecode.split(' ', 1)[0] in pycodecommands:
            func = pycodecode.split(' ', 1)[0]
            giveninput = pycodecode.split(' ', 1)[1]
            return pythoncommands[pycodecommands.index(func)] + f'({giveninput})'
    try:
        code = open(f'/home/{getpass.getuser()}/.pynotes', 'r').read().replace('\n', '').split(';')
    except:
        return
    cdt = ''
    startupcdt = ''
    for line_ in code:
        line = line_.strip() + ';'
        if line_:
            ks = re.findall(r'<.+?>→<.+?>;', line)
            v = re.findall(r'\[.+?\]:→\[.+?\];', line)
            f = re.findall(r'\(.+?\)→:\(.+?\);', line)
            s = re.findall(r'\|.+?\|', line)
            if all((not ks, not v, not f)):
                ks = re.findall(r'<.+?> +→ +<.+?>;', line)
                v = re.findall(r'\[.+?\] +:→ +\[.+?\];', line)
                f = re.findall(r'\(.+?\) +→: +\(.+?\);', line)
            if ks and len(ks) == 1:
                ks = ks[0].strip()[:-1]
                wholenewwords.append(ks.split('→')[0].strip())
                cdt += f"root.bind('<{ks.split('→')[0].strip()[1:][:-1].strip()}>', lambda event: pcrun(\"{pycodeindex(ks.split('→')[1].strip()[:-1][1:].strip())}\"))" + '\n'
            elif v and len(v) == 1:
                v = v[0].strip()[:-1]
                cdt += v.split(':→')[0].strip()[:-1][1:].strip() + '=' + v.split(':→')[1].strip()[:-1][1:].strip() + '\n'
            elif f and len(f) == 1:
                f = f[0].strip()[:-1]
                func_name = f.split('→:')[0].strip()[:-1][1:].strip()
                cdt += f'def {func_name}(): '
                to_do = f.split('→:')[1].strip()[:-1][1:].strip().split(',')
                for i in range(len(to_do)):
                    if to_do[i]:
                        to_do[i] = pycodeindex(to_do[i].strip())
                    else:
                        to_do[i] = ''
                to_do = r'\n'.join(to_do)
                cdt += f'exec("{to_do}")' + '\n'
                pycodecommands.append(func_name)
                pythoncommands.append(func_name + '()')
            elif s and len(s) == 1:
                s = s[0].strip()
                startupcdt += f'{pycodeindex(s[1:-1])}' + '\n'
            else:
                root.error('Error in PyCode', f'Invalid Syntax: {line}')
    file = open(f'/home/{getpass.getuser()}/.pynotesstartup', 'w+')
    file.write(startupcdt)
    file.close()
    pcrun(cdt)
def edit(widget, editfrom):
    if editfrom == '=':
        widget.insert('insert', '→')
        return 'break'
    elif editfrom == '|':
        widget.insert('insert', '|')
        widget.mark_set('insert', 'insert-1c')
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
    codeedit.bind('|', lambda event: edit(codeedit, '|'))
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
    hptabs.add(vt, text = 'Variables')
    ft = hpwin.frame()
    hptabs.add(ft, text = 'Functions')
    st = hpwin.frame()
    hptabs.add(st, text = 'Startup Code')
    hpwin.text(master = kst, text = 'You can bind or rebind keyboard shortcuts to do various things with PyCode.\nIf you want to make a keyboard shortcut where you have to press and hold 2 keys,\n(eg. Control or Alt + something else), you will have to put a dash between them.\nControl and Alt keys, when used, can never be after a normal letter.\nYou can never repeat Control or Alt keys in the same keyboard shortcut.\nThere always has to be one and only one letter in each keyboard shortcut.\nThere is no such thing as "Shift" like Control and Alt.\nIf you want to have Shift, just make the letter capital.\nYou can bind keys to these functions:').grid(column = 0, row = 0)
    code = hpwin.style()
    code.configure('CodeStyle.TLabel', background = 'white', padding = (7, 7, 7, 7), relief = 'sunken')
    hpwin.text(master = kst, text = 'termexec \'{input}\': run the input as a terminal command, wait {input}: freeze PyNotes for the given number of seconds, quit: force quit PyNotes, say \'{input}\': display a messagebox with the text, command: type a command (the same as Alt+X), selall: select all the text in the editor, copy: copy the selected text, paste: paste some copied text, undo: undo the last edit, redo: redo the last undoed edit, ask \'{input}\': ask a prompt with the input, cut: copy and delete the selected text, term: open the terminal, cmd \'{input}\': run the input command as if you had pressed Alt+X and typed it'.replace(', ', '\n'), style = 'CodeStyle.TLabel').grid(column = 0, row = 1)
    hpwin.text(master = kst, text = 'Remember, inputs in these should always be inside quotes, and single quotes only!\nWhen you ask something, the output is saved to the variable \'answer\'.\nIf you have already defined a variable named \'answer\', the variable will not change.\nAlso lines of code should always end with a ";".\nHere are a few examples:').grid(column = 0, row = 2)
    hpwin.text(master = kst, text = '<Control-q> → <quit>;', style = 'CodeStyle.TLabel').grid(column = 0, row = 3)
    hpwin.text(master = kst, text = '<Control-t> → <say \'Hello!\'>;', style = 'CodeStyle.TLabel').grid(column = 0, row = 4)
    hpwin.text(master = vt, text = 'If you want to keep using a long string in PyCode again and again, it will become easier to use a variable.\nThis is how to define a variable called "something" with the value "something else":').grid(column = 0, row = 0)
    hpwin.text(master = vt, text = '[something] :→ [\'something else\'];', style = 'CodeStyle.TLabel').grid(column = 0, row = 1)
    hpwin.text(master = vt, text = 'This can be used later like this:').grid(column = 0, row = 2)
    hpwin.text(master = vt, text = '<Control-q> → <say something>;', style = 'CodeStyle.TLabel').grid(column = 0, row = 3)
    hpwin.text(master = vt, text = 'Variables can only be used to do this, and cannot be changed later in the code.').grid(column = 0, row = 4)
    hpwin.text(master = ft, text = 'Functions are shortcuts which can run multiple lines of code.\nThey can be used to bind multiple lines of code to a single keyboard shortcut.\nHere is how to define a function named \'something\' which will ask something and then quit after one second:').grid(column = 0, row = 0)
    hpwin.text(master = ft, text = '(something) →: (ask \'What is your name?\', wait 1, quit,);', style = 'CodeStyle.TLabel').grid(column = 0, row = 1)
    hpwin.text(master = ft, text = 'This can be used later like this:').grid(column = 0, row = 2)
    hpwin.text(master = ft, text = '<Control-q> → <something>;', style = 'CodeStyle.TLabel').grid(column = 0, row = 3)
    hpwin.text(master = st, text = 'Startup code runs automatically every time PyNotes starts.\nThis means you do not need to bind it to a key.\nFor example, if you want to start PyNotes with the text \'Hello!\'\ninstead of the Zen of Python, you can type this:').grid(column = 0, row = 0)
    hpwin.text(master = st, text = '(startup) →: (cmd \'n\', cmd \'write:Hello!*1\');\n|startup|;', style = 'CodeStyle.TLabel').grid(column = 0, row = 1)
    hpwin.sizablefalse()
    hpwin.style(root.gettheme())
    hpwin.show()
def syncscroll(*args):
    ln.yview_moveto(args[0])
    scrlbr.set(*args)
def undo():
    try:
        type_.edit_undo()
    except:
        show('Nothing to UNDO')
def redo():
    try:
        type_.edit_redo()
    except:
        show('Nothing to REDO')
tabs = root.tabs()
mf = root.frame()
sf = root.frame()
lf = root.frame()
ef = root.frame()
def boldlatex():
    try:
        select = type_.get('sel.first', 'sel.last')
    except:
        return
    type_.delete('sel.first', 'sel.last')
    type_.insert('insert', '{\\bf ' + select + '}')
    show('bold text latex')
    keypress()
def italiclatex():
    try:
        select = type_.get('sel.first', 'sel.last')
    except:
        return
    type_.delete('sel.first', 'sel.last')
    type_.insert('insert', '\\textit{' + select + '}')
    show('italic text latex')
    keypress()
def underlinelatex():
    try:
        select = type_.get('sel.first', 'sel.last')
    except:
        return
    type_.delete('sel.first', 'sel.last')
    type_.insert('insert', '\\underline{' + select + '}')
    show('underline text latex')
    keypress()
def subscriptlatex():
    try:
        select = type_.get('sel.first', 'sel.last')
    except:
        return
    type_.delete('sel.first', 'sel.last')
    type_.insert('insert', '_{' + select + '}')
    show('subscript text latex')
    keypress()
def superscriptlatex():
    try:
        select = type_.get('sel.first', 'sel.last')
    except:
        return
    type_.delete('sel.first', 'sel.last')
    type_.insert('insert', '^{' + select + '}')
    show('superscript text latex')
    keypress()
def numberlistlatex():
    try:
        select = type_.get('sel.first', 'sel.last')
    except:
        type_.insert('insert', '\n\\begin{enumerate}\n\n\\end{enumerate}\n')
    else:
        tryfind = re.findall(r'\\begin{enumerate}.+\\end{enumerate}', select, re.DOTALL)
        if not tryfind:
            select = '\\item ' + select.replace('\n', '\n\\item ').replace('\\item \\item ', '\\item ')
            type_.delete('sel.first', 'sel.last')
            type_.insert('insert', '\n\\begin{enumerate}\n' + select + '\n\\end{enumerate}\n')
        else:
            keeptext = tryfind[0][len('\\begin{enumerate}'):][:-len('\\end{enumerate}')].replace('\\item ', '')
            type_.delete('sel.first', 'sel.last')
            type_.insert('insert', keeptext)
    show('numbered list latex')
    keypress()
def bulletlistlatex():
    try:
        select = type_.get('sel.first', 'sel.last')
    except:
        type_.insert('insert', '\n\\begin{itemize}\n\n\\end{itemize}\n').replace('\\item \\item ', '\\item ')
    else:
        tryfind = re.findall(r'\\begin{itemize}.+\\end{itemize}', select, re.DOTALL)
        if not tryfind:
            select = '\\item ' + select.replace('\n', '\n\\item ').replace('\\item \\item ', '\\item ')
            type_.delete('sel.first', 'sel.last')
            type_.insert('insert', '\n\\begin{itemize}\n' + select + '\n\\end{itemize}\n')
        else:
            keeptext = tryfind[0][len('\\begin{itemize}'):][:-len('\\end{itemize}')].replace('\\item ', '')
            type_.delete('sel.first', 'sel.last')
            type_.insert('insert', keeptext)
    show('bulleted list latex')
    keypress()
def paragraphlatex():
    type_.insert('insert', '\\par\n')
    show('new paragraph latex')
    keypress()
def equationlatex():
    try:
        select = type_.get('sel.first', 'sel.last')
    except:
        type_.insert('insert', '\n\\begin{equation}\n\\begin{split}\n\n\\end{split}\n\\end{equation}\n')
    else:
        tryfind = re.findall(r'\\begin{equation}.+\\end{equation}', select, re.DOTALL)
        if not tryfind:
            select = select.replace('\n', '\\\\\n').replace('\\\\\\\\', '\\\\')
            type_.delete('sel.first', 'sel.last')
            type_.insert('insert', '\n\\begin{equation}\n' + select + '\n\\end{equation}\n')
        else:
            keeptext = tryfind[0][len('\\begin{equation}'):][:-len('\\end{equation}')].replace('\\', '')
            type_.delete('sel.first', 'sel.last')
            type_.insert('insert', keeptext)
    show('equation latex')
    keypress()
def sectionlatex(typeofsection):
    typeofsection = typeofsection.lower()
    secname = 'Section'
    if secname:
        type_.insert('insert', f'\n\\{typeofsection}' + '{' + secname + '}\n')
    show(f'new {typeofsection} latex')
    keypress()
def mathlatex(whichchar):
    original = ['Multiplication', 'Division', 'Less or equal', 'More or equal', 'Not equal', 'Infinity', 'Summation', 'Integral', 'Pi', 'Theta', 'Alpha Lower', 'Alpha Upper', 'Inline Math']
    replaces = ['\\times', '\\div', '\\leq', '\\meq', '\\neq', '\\infty', '\\sum', '\\int', '\\pi', '\\theta', '\\alpha', '\\Alpha', '$$']
    whichchar = replaces[original.index(whichchar)]
    type_.insert('insert', whichchar)
    show('insert math latex')
    keypress()
root.text(master = lf, text = 'LaTeX:').grid(column = 0, row = 0, padx = 10, pady = 10)
bold = root.button(master = lf, text = 'Bold', command = boldlatex)
bold.grid(column = 1, row = 0, padx = 10, pady = 10)
italic = root.button(master = lf, text = 'Italic', command = italiclatex)
italic.grid(column = 2, row = 0, padx = 10, pady = 10)
underline = root.button(master = lf, text = 'Underline', command = underlinelatex)
underline.grid(column = 3, row = 0, padx = 10, pady = 10)
subscript = root.button(master = lf, text = 'Subscript', command = subscriptlatex)
subscript.grid(column = 4, row = 0, padx = 10, pady = 10)
superscript = root.button(master = lf, text = 'Superscript', command = superscriptlatex)
superscript.grid(column = 5, row = 0, padx = 10, pady = 10)
numberlist = root.button(master = lf, text = 'Numbered List', command = numberlistlatex)
numberlist.grid(column = 6, row = 0, padx = 10, pady = 10)
bulletlist = root.button(master = lf, text = 'Bullet List', command = bulletlistlatex)
bulletlist.grid(column = 7, row = 0, padx = 10, pady = 10)
sectionvar = root.stringvar(master = lf)
section = root.dropdown(stringvar = sectionvar, showdefault = 'Section', options = ['Section', 'Subsection', 'Subsubsection'], master = lf, command = sectionlatex)
section.grid(column = 8, row = 0, padx = 10, pady = 10)
paragraph = root.button(master = lf, text = 'Paragraph', command = paragraphlatex)
paragraph.grid(column = 9, row = 0, padx = 10, pady = 10)
equation = root.button(master = lf, text = 'Equation', command = equationlatex)
equation.grid(column = 10, row = 0, padx = 10, pady = 10)
charvar = root.stringvar()
math = root.dropdown(master = lf, stringvar = charvar, showdefault = 'Multiplication', options = ['Multiplication', 'Division', 'Less or equal', 'More or equal', 'Not equal', 'Infinity', 'Summation', 'Integral', 'Pi', 'Theta', 'Alpha Lower', 'Alpha Upper', 'Inline Math'], command = mathlatex)
math.grid(column = 11, row = 0, padx = 10, pady = 10)
lf.pack(padx = 10, pady = 10, side = 'top', fill = 'x')
for widget in lf.winfo_children()[1:]:
    widget.config(state = 'disabled')
root.separator(way = 'vertical').pack(fill = 'x', padx = 10, pady = 10)
tabs.add(mf, text = 'Editor')
tabs.add(sf, text = 'Python Shell', state = 'hidden')
tabs.add(ef, text = 'Email', state = 'hidden')
tabs.pack(padx = 10, pady = 10, fill = 'both', expand = True)
scrlbr = root.scroll(master = mf)
scrlbr.pack(side = 'right', fill = 'y')
ln = root.textbox(master = mf, width = 4, state = 'disabled', font = defs[2], yscrollcommand = lambda *args: ln.yview_moveto(type_.yview()[0]), wrap = 'none')
ln.pack(side = 'left', fill = 'y', anchor = 'n')
type_ = root.textbox(master = mf, undo = True, yscrollcommand = syncscroll, font = defs[2], wrap = 'word')
type_.pack(fill = 'both', expand = True, anchor = 'n')
type_.insert('end',
"The Zen of Python, by Tim Peters\n\nBeautiful is better than ugly.\nExplicit is better than implicit.\nSimple is better than complex.\nComplex is better than complicated.\nFlat is better than nested.\nSparse is better than dense.\nReadability counts.\nSpecial cases aren't special enough to break the rules.\nAlthough practicality beats purity.\nErrors should never pass silently.\nUnless explicitly silenced.\nIn the face of ambiguity, refuse the temptation to guess.\nThere should be one-- and preferably only one --obvious way to do it.\nAlthough that way may not be obvious at first unless you're Dutch.\nNow is better than never.\nAlthough never is often better than *right* now.\nIf the implementation is hard to explain, it's a bad idea.\nIf the implementation is easy to explain, it may be a good idea.\nNamespaces are one honking great idea -- let's do more of those!")
scrlbr.config(command = type_.yview)
type_.focus_set()
fileinfo = root.frame()
cmdlabel = root.text()
cmdlabel.pack(side = 'left', padx = 10, pady = 10, anchor = 's')
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
em.add_command(label = 'Undo → Ctrl + Z / Alt + X - u', command = undo)
em.add_command(label = 'Redo → Ctrl + Shift + Z / Alt + X - r', command = redo)
root.bind('<Control-z>', lambda event: undo())
root.bind('<Control-Z>', lambda event: redo())
em.add_separator()
em.add_command(label = 'Copy → Ctrl + C / Alt + X - c', command = cp)
em.add_command(label = 'Paste → Ctrl + V / Alt + X - p', command = pst)
em.add_command(label = 'Cut → Ctrl + X / Alt + X - cut', command = cut)
em.add_command(label = 'Select All → Ctrl + A / Alt + X - a', command = selall)
hm.add_command(label = 'About', command = abt)
hm.add_command(label = f'What\'s new in {v}?', command = changes)
hm.add_command(label = 'Help with Alt-X → Alt + X - h', command = hx)
hm.add_separator()
hm.add_command(label = 'Help with Email', command = hemail)
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
em.add_command(label = 'Find → Ctrl + F', command = f)
root.bind('<Control-f>', f)
em.add_command(label = 'Find & Replace → Ctrl + Shift + F', command = fr)
root.bind('<Control-F>', fr)
readonlytextforshellpy = '>>> '
readonlyendforshellpy = '1.' + str(len('>>> '))
continuation = False
continuationcodeforshellpy = ''
def shellpy():
    global shellcmd
    global readonlytextforshellpy
    global readonlyendforshellpy
    readonlytextforshellpy = f'Python {sys.version} ({sys.executable})'.replace('\n', '') + '\n>>> '
    readonlyendforshellpy = '2.' + str(len('>>> '))
    def check_edit():
        shellcmd.delete('1.0', readonlyendforshellpy)
        shellcmd.insert('1.0', readonlytextforshellpy)
        shellcmd.see('end')
    def exec(event):
        global readonlyendforshellpy
        global readonlytextforshellpy
        global continuation
        global continuationcodeforshellpy
        shellcmd.update()
        command = shellcmd.get(shellcmd.index('end-1c').split('.')[0] + '.0', 'end-1c')[len('>>> '):].strip()
        if all((continuation == False, not command[-1:] == ':')):
            output = shellexec(command)
            shellcmd.insert('end', '\n' + output + '\n' + '>>> ')
            readonlyendforshellpy = shellcmd.index('end-1c').split('.')[0] + '.' + str(len('>>> '))
            readonlytextforshellpy += command + '\n' + output + '\n' + '>>> '
            shellcmd.see('end')
        else:
            continuation = True
            if not command == '':
                command = shellcmd.get(shellcmd.index('end-1c').split('.')[0] + '.0', 'end-1c')[len('... '):].rstrip()
                shellcmd.insert('end', '\n... ')
                readonlyendforshellpy = shellcmd.index('end-1c').split('.')[0] + '.' + str(len('... '))
                readonlytextforshellpy += command + '\n... '
                continuationcodeforshellpy += command + '\n'
                shellcmd.see('end')
            else:
                continuation = False
                output = shellexec(continuationcodeforshellpy)
                shellcmd.insert('end', '\n' + output + '\n' + '>>> ')
                readonlyendforshellpy = shellcmd.index('end-1c').split('.')[0] + '.' + str(len('>>> '))
                readonlytextforshellpy += command + '\n' + output + '\n' + '>>> '
                shellcmd.see('end')
                continuationcodeforshellpy = ''
                shellcmd.see('end')
        return 'break'
    shellcmd = root.textbox(master = sf, font = ('Ubuntu Mono', 12))
    shellcmd.insert('end', f'Python {sys.version} ({sys.executable})'.replace('\n', '') + '\n>>> ')
    shellcmd.bind('<KeyPress>', lambda event: check_edit())
    shellcmd.bind('<Return>', exec)
    shellcmd.pack(fill = 'both')
shellpy()
def emailsetup(saved = None):
    global e
    global p
    global s
    global po
    attachments = []
    def removeattach():
        def actualremoveattachment(attachment):
            del attachmentslist[attachment]
            del attachments[attachment]
            attachmentslistwidget.config(text = 'Attachments: ' + ' , '.join(attachmentslist))
            raw.destroy()
        if attachmentslist:
            raw = root.subwin()
            for i in range(len(attachmentslist)):
                attachment = attachmentslist[i]
                raw.button(text = attachment, command = lambda i = i: actualremoveattachment(i)).grid(column = i % 5, row = mathmod.floor(i / 5), sticky = 'ew')
            raw.show()
    def attach():
        fn = root.openfile(['all'])
        if fn:
            try:
                with open(fn, 'rb') as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(fn)}')
                    if not os.path.basename(fn) in attachmentslist:
                        attachments.append(part)
                        attachmentslist.append(os.path.basename(fn))
                        attachmentslistwidget.config(text = 'Attachments: ' + ' , '.join(attachmentslist))
            except Exception as error:
                root.error('Error', str(error))
    def changeinfo():
        def emailsetupother():
            global e
            global p
            global s
            global po
            entryframe.pack(padx = 10, pady = 10, fill = 'x', anchor = 'n', expand = True)
            buttonframe.pack(padx = 10, pady = 10, fill = 'x', anchor = 'n', expand = True)
            emailtextbox.pack(fill = 'both', expand = True, padx = 10, pady = 10)
            e = email.get()
            p = password.get()
            s = server.get()
            po = port.get()
            file = open(f'/home/{getpass.getuser()}/.pynotesemailconfig', 'w+')
            file.write(f'{e}\n{p}\n{s}\n{po}')
            file.close()
            encryptdecrypt(f'/home/{getpass.getuser()}/.pynotesemailconfig')
            loginframe.pack_forget()
        entryframe.pack_forget()
        buttonframe.pack_forget()
        emailtextbox.pack_forget()
        loginframe = root.frame(master = ef)
        loginframe.pack(expand = True)
        root.text(master = loginframe, text = 'Email:').grid(column = 0, row = 0, padx = 10, pady = 10)
        email = root.entry(master = loginframe)
        email.grid(column = 1, row = 0, padx = 10, pady = 10)
        root.text(master = loginframe, text = 'Password:').grid(column = 0, row = 1, padx = 10, pady = 10)
        password = root.entry(master = loginframe, show = '*')
        password.grid(column = 1, row = 1, padx = 10, pady = 10)
        root.text(master = loginframe, text = 'Smtp Server:').grid(column = 0, row = 2, padx = 10, pady = 10)
        server = root.entry(master = loginframe)
        server.grid(column = 1, row = 2, padx = 10, pady = 10)
        root.text(master = loginframe, text = 'Smtp Port:').grid(column = 0, row = 3, padx = 10, pady = 10)
        port = root.entry(master = loginframe)
        port.grid(column = 1, row = 3, padx = 10, pady = 10)
        root.button(master = loginframe, text = 'Done', command = emailsetupother).grid(column = 1, row = 4, padx = 10, pady = 10, sticky = 'e')
    def sendemail(event = None):
        global e
        global p
        global s
        global po
        recipients = recipiententry.get().split(',')
        subject = subjectentry.get()
        if not subject:
            subject = '(No Subject)'
        for recipient in recipients:
            if recipient:
                message = MIMEMultipart()
                message['From'] = e
                message['To'] = recipient
                message['Subject'] = subject
                message.attach(MIMEText(emailtextbox.get('1.0', 'end-1c'), 'plain'))
                try:
                    for attachment in attachments:
                        message.attach(attachment)
                    with smtplib.SMTP_SSL(s, po) as server:
                        server.login(e, p)
                        server.sendmail(e, recipient, message.as_string())
                except Exception as error:
                    root.error('Error', str(error))
                    show('email failed')
                    return
                else:
                    emailtextbox.delete('1.0', 'end')
                    recipiententry.delete(0, 'end')
                    recipiententry.delete(0, 'end')
                    attachments.clear()
                    attachmentslist.clear()
                    attachmentslistwidget.config(text = 'Attachments:')
                    subjectentry.delete(0, 'end')
        show('email sent')
        root.info('Info', 'Email Successfully Sent!')
        return 'break'
    def spellcheck():
        emailtextbox.tag_remove('wrong', '1.0', 'end')
        n = '1.0'
        search = r'\w+'
        while True:
            count = root.intvar()
            n = emailtextbox.search(search, n, nocase = 1, count = count, stopindex = 'end', regexp = True)
            if not n: break
            nn = '%s+%dc' % (n, count.get())
            if not emailtextbox.get(n, nn).lower() in wordlist and len(emailtextbox.get(n, nn)) > 1:
                try:
                    int(emailtextbox.get(n, nn))
                except:
                    emailtextbox.tag_add('wrong', n, nn)
            n = nn
        n = '1.0'
        emailtextbox.tag_config('wrong', underline = True, underlinefg = 'red')
    if not saved:
        e = email.get()
        p = password.get()
        s = server.get()
        po = port.get()
        loginframe.pack_forget()
        ans = root.ask('', 'Do you want PyNotes to save your email and password?', ['yes', 'no'])
        if ans:
            file = open(f'/home/{getpass.getuser()}/.pynotesemailconfig', 'w+')
            file.write(f'{e}\n{p}\n{s}\n{po}')
            file.close()
            encryptdecrypt(f'/home/{getpass.getuser()}/.pynotesemailconfig')
    else:
        encryptdecrypt(f'/home/{getpass.getuser()}/.pynotesemailconfig')
        file = open(f'/home/{getpass.getuser()}/.pynotesemailconfig', 'r').read().split('\n')
        encryptdecrypt(f'/home/{getpass.getuser()}/.pynotesemailconfig')
        e = file[0]
        p = file[1]
        s = file[2]
        po = file[3]
    entryframe = root.frame(master = ef)
    recipiententry = root.entry(master = entryframe)
    root.text(master = entryframe, text = 'Recipients (separate by commas):').grid(column = 0, row = 0, padx = 10, pady = 10, sticky = 'e')
    recipiententry.grid(column = 1, row = 0, padx = 10, pady = 10, sticky = 'ew')
    root.text(master = entryframe, text = 'Subject:').grid(column = 0, row = 1, padx = 10, pady = 10, sticky = 'e')
    subjectentry = root.entry(master = entryframe)
    subjectentry.grid(column = 1, row = 1, padx = 10, pady = 10, sticky = 'ew')
    entryframe.pack(padx = 10, pady = 10, fill = 'both', anchor = 'n', expand = True)
    entryframe.columnconfigure(1, weight = 1)
    buttonframe = root.frame(master = ef)
    buttonframe.pack(padx = 10, pady = 10, fill = 'both', anchor = 'n', expand = True)
    root.button(master = buttonframe, text = 'Send (Ctrl + Enter)', command = sendemail).pack(fill = 'x', expand = True, padx = 10, pady = 10, side = 'left', anchor = 'n')
    root.button(master = buttonframe, text = 'Attach', command = attach).pack(fill = 'x', expand = True, padx = 10, pady = 10, side = 'right', anchor = 'n')
    root.button(master = buttonframe, text = 'Change Info', command = changeinfo).pack(fill = 'x', expand = True, padx = 10, pady = 10, side = 'left', anchor = 'n')
    root.button(master = buttonframe, text = 'Remove Attachment', command = removeattach).pack(fill = 'x', expand = True, padx = 10, pady = 10, side = 'right', anchor = 'n')
    attachmentslist = []
    attachmentslistwidget = root.text(master = buttonframe, text = 'Attachments:')
    attachmentslistwidget.pack(fill = 'x', expand = True, padx = 10, pady = 10)
    emailtextbox = root.textbox(master = ef, scrolled = True, font = ('Ubuntu Mono', 15))
    emailtextbox.pack(fill = 'both', expand = True, padx = 10, pady = 10)
    emailtextbox.bind('<Control-Return>', sendemail)
    emailtextbox.bind('<KeyRelease>', lambda event: spellcheck() if wordlist else None)
wordlist = []
try:
    for dictionary in dicts:
        if dictionary:
            wordlist.extend(open(dictionary, 'r').read().split('\n'))
except Exception as error:
    root.error('Error', error)
try:
    open(f'/home/{getpass.getuser()}/.pynotesemailconfig', 'r')
except:
    loginframe = root.frame(master = ef)
    loginframe.pack(expand = True)
    root.text(master = loginframe, text = 'Email:').grid(column = 0, row = 0, padx = 10, pady = 10)
    email = root.entry(master = loginframe)
    email.grid(column = 1, row = 0, padx = 10, pady = 10)
    root.text(master = loginframe, text = 'Password:').grid(column = 0, row = 1, padx = 10, pady = 10)
    password = root.entry(master = loginframe, show = '*')
    password.grid(column = 1, row = 1, padx = 10, pady = 10)
    root.text(master = loginframe, text = 'Smtp Server:').grid(column = 0, row = 2, padx = 10, pady = 10)
    server = root.entry(master = loginframe)
    server.grid(column = 1, row = 2, padx = 10, pady = 10)
    root.text(master = loginframe, text = 'Smtp Port:').grid(column = 0, row = 3, padx = 10, pady = 10)
    port = root.entry(master = loginframe)
    port.grid(column = 1, row = 3, padx = 10, pady = 10)
    root.button(master = loginframe, text = 'Let\'s Go!', command = emailsetup).grid(column = 1, row = 4, padx = 10, pady = 10, sticky = 'e')
else:
    emailsetup('saved')
root.bind('<Alt-x>', cmd)
type_.bind('<Control-a>', selall)
type_.bind('<Control-c>', cp)
type_.bind('<Control-v>', pst)
type_.bind('<Control-x>', cut)
om.add_command(label = 'Terminal → Alt + X - t', command = term)
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
try:
    file = open(f'/home/{getpass.getuser()}/.pynotesstartup', 'r').read().split('\n')
except:
    pass
else:
    for line in file:
        try:
            exec(line, globals())
        except Exception as error:
            root.error('Error', f'Error in PyCode: {error}')
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
type_.edit_reset()
root.show()