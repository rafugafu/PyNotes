import matplotlib.pyplot as plt
import numpy as np
import re as refind
import easytk
from sympy.abc import *
from sympy import *
import code
import code
import sys
import platform
import io
if platform.system() == 'Linux':
	monospace = 'monospace'
else:
	monospace = 'Courier'
class MathGod:
	def __init__(self):
		pass
	def asin(self, x, *args, **kwargs):
		return asin(x, *args, **kwargs)
	def acos(self, x, *args, **kwargs):
		return acos(x, *args, **kwargs)
	def atan(self, x, *args, **kwargs):
		return atan(x, *args, **kwargs)
	def asinh(self, x, *args, **kwargs):
		return asinh(x, *args, **kwargs)
	def acosh(self, x, *args, **kwargs):
		return acosh(x, *args, **kwargs)
	def atanh(self, x, *args, **kwargs):
		return atanh(x, *args, **kwargs)
	def sinh(self, x, *args, **kwargs):
		return sinh(x, *args, **kwargs)
	def cosh(self, x, *args, **kwargs):
		return cosh(x, *args, **kwargs)
	def tanh(self, x, *args, **kwargs):
		return tanh(x, *args, **kwargs)
	def sin(self, x, *args, **kwargs):
		return sin(x, *args, **kwargs)
	def cos(self, x, *args, **kwargs):
		return cos(x, *args, **kwargs)
	def tan(self, x, *args, **kwargs):
		return tan(x, *args, **kwargs)
	def log(self, x, base = None, *args, **kwargs):
		if base == None:
			return log(x, *args, **kwargs)
		else:
			return log(x, base, *args, **kwargs)
	def solve(self, eq, v, *args, **kwargs):
		return solve(eq, v, *args, **kwargs)
	def derivative(self, f, x, *args, **kwargs):
		return diff(f, x, *args, **kwargs)
	def integral(self, f, x, start = None, end = None, *args, **kwargs):
		if start == None and end == None:
			return integrate(f, x, *args, **kwargs)
		else:
			return integrate(f, (x, start, end), *args, **kwargs)
	def limit(self, f, x, a, *args, **kwargs):
		return limit(f, x, a, *args, **kwargs)
	def summation(self, f, x, start, end, *args, **kwargs):
		return summation(f, (x, start, end), *args, **kwargs)
	def product(self, f, x, start, end, *args, **kwargs):
		return product(f, (x, start, end), *args, **kwargs)
	def interpolate(self, *args, **kwargs):
		return interpolate(*args, **kwargs)
	def plotfunc(self, func, var, start, end, title = 'Plot', label = None, grid = False, x_label = None, y_label = None, xticks = None, yticks = None, linspace = 1000, *args, **kwargs):
		plt.title(title)
		if x_label != None:
			plt.xlabel(x_label)
		if y_label != None:
			plt.ylabel(y_label)
		if xticks != None:
			plt.xticks(xticks)
		if yticks != None:
			plt.yticks(yticks)
		y = list(map(lambda iterator: (func if type(func) == int else func.subs(var, iterator)), np.linspace(start, end, linspace)))
		plt.plot(np.linspace(start, end, linspace), y, label = label, *args, **kwargs)
		if label:
			plt.legend()
		plt.grid(grid)
	def plotfunc3d(self, func, x, y, se1, se2, title = 'Plot', grid = False, x_label = None, y_label = None, z_label = None, linspace = 1000, *args, **kwargs):
		fig = plt.figure()
		ax = fig.add_subplot(111, projection = '3d')
		ax.set_title(title)
		if x_label != None:
			ax.set_xlabel(x_label)
		if y_label != None:
			ax.set_ylabel(y_label)
		if z_label != None:
			ax.set_zlabel(z_label)
		X, Y = np.meshgrid(np.linspace(se1[0], se1[1], linspace), np.linspace(se2[0], se2[1], linspace))
		if not type(func) == int:
			z = lambdify((x, y), func, 'numpy')
			Z = z(X, Y)
		else:
			Z = np.full_like(X, func)
		ax.grid(grid)
		ax.plot_surface(X, Y, Z, cmap = 'gnuplot', *args, **kwargs)
		plt.show()
	def plotlist2d(self, x, y, title = 'Plot', label = None,  grid = False, x_label = None, y_label = None, xticks = None, yticks = None, *args, **kwargs):
		plt.plot(x, y, label = label, *args, **kwargs)
		if label:
			plt.legend()
		plt.grid(grid)
		plt.title(title)
		if x_label != None:
			plt.xlabel(x_label)
		if y_label != None:
			plt.ylabel(y_label)
		if xticks != None:
			plt.xticks(xticks)
		if yticks != None:
			plt.yticks(yticks)
	def piechart(self, *args, **kwargs):
		plt.pie(*args, **kwargs)
		plt.show()
	def barchart(self, *args, **kwargs):
		plt.bar(*args, **kwargs)
		plt.show()
engine = MathGod()
class interactive_shell:
	def __init__(self):
		self.locals = globals()
		self.shell = code.InteractiveConsole(self.locals)
	def ragoae(self, string):
		output = io.StringIO()
		error = io.StringIO()
		old_stdout = sys.stdout
		old_stderr = sys.stderr
		sys.stderr = error
		sys.stdout = output
		try:
			self.shell.push(string)
		except SystemExit:
			sys.stdout = None
			sys.stderr = None
			self.shell.push('pass')
		sys.stdout = old_stdout
		sys.stderr = old_stderr
		return output.getvalue()
shell = interactive_shell()
def translate(code):
	global plotlist
	global shell
	toreturn = ''
	code = 'clearplot\n' + code
	try:
		for iterator in range(len(code.split('\n'))):
			line = code.split('\n')[iterator]
			line = line.replace('^', '**')
			multiplication = refind.findall(r'(\d+)([a-zA-Z])', line)
			for match in multiplication:
				line = line.replace(match[0] + match[1], match[0] + '*' + match[1])
			translatedline = line
			if not line:
				continue
			if line.strip() == 'clearplot':
				plotlist = ''
				continue
			var = refind.findall(r'^\s*[a-zA-Z_][a-zA-Z0-9_]*\s*=\s*[^=]+', line)
			func = refind.findall(r'\{[ \t]*func[ \t]+[a-zA-Z0-9_]+[ \t]*,[^}]*\}', line)
			eq = refind.findall(r'\{[ \t]*eq[ \t]+[a-zA-Z0-9_]+[ \t]*,[^}]*\}', line)
			integral = refind.findall(r'\{[ \t]*integrate[ \t]+[^}]*\}', line)
			limit = refind.findall(r'\{[ \t]*limit[ \t]+[^}]*\}', line)
			derivative = refind.findall(r'\{[ \t]*derivative[ \t]+[^}]*\}', line)
			solve = refind.findall(r'\{[ \t]*solve[ \t]+[^}]*\}', line)
			plot = refind.findall(r'\{[ \t]*plot[ \t]+[^}]*\}', line)
			plotcoord = refind.findall(r'\{[ \t]*plotlist[ \t]+[^}]*\}', line)
			piechart = refind.findall(r'\{[ \t]*pie[ \t]+[^}]*\}', line)
			barchart = refind.findall(r'\{[ \t]*bar[ \t]+[^}]*\}', line)
			plot3d = refind.findall(r'\{[ \t]*plot3[ \t]+[^}]*\}', line)
			sum = refind.findall(r'\{[ \t]*sum[ \t]+[^}]*\}', line)
			prod = refind.findall(r'\{[ \t]*prod[ \t]+[^}]*\}', line)
			interpolate = refind.findall(r'\{[ \t]*interpolate[ \t]+[^}]*\}', line)
			if solve:
				solve = refind.findall(r'\{[ \t]*solve[ \t]+[^}]*\}', translatedline)
				originalfound = solve[0]
				translatedline = translatedline.replace(originalfound, 'engine.solve(' + solve[0].split('solve ')[1].strip()[:-1].strip() + ')')
			if integral:
				integral = refind.findall(r'\{[ \t]*integrate[ \t]+[^}]*\}', translatedline)
				originalfound = integral[0]
				translatedline = translatedline.replace(originalfound, 'engine.integral(' + integral[0].split('integrate ')[1].strip()[:-1].strip() + ')')
			if limit:
				limit = refind.findall(r'\{[ \t]*limit[ \t]+[^}]*\}', translatedline)
				originalfound = limit[0]
				translatedline = translatedline.replace(originalfound, 'engine.limit(' + limit[0].split('limit ', 1)[1].strip()[:-1].strip() + ')')
			if derivative:
				derivative = refind.findall(r'\{[ \t]*derivative[ \t]+[^}]*\}', translatedline)
				originalfound = derivative[0]
				translatedline = translatedline.replace(originalfound, 'engine.derivative(' + derivative[0].split('derivative ')[1].strip()[:-1].strip() + ')')
			if sum:
				sum = refind.findall(r'\{[ \t]*sum[ \t]+[^}]*\}', translatedline)
				originalfound = sum[0]
				translatedline = translatedline.replace(originalfound, 'engine.summation(' + sum[0].split('sum ')[1].strip()[:-1].strip() + ')')
			if prod:
				prod = refind.findall(r'\{[ \t]*prod[ \t]+[^}]*\}', translatedline)
				originalfound = prod[0]
				translatedline = translatedline.replace(originalfound, 'engine.product(' + prod[0].split('prod ')[1].strip()[:-1].strip() + ')')
			if interpolate:
				interpolate = refind.findall(r'\{[ \t]*interpolate[ \t]+[^}]*\}', translatedline)
				originalfound = interpolate[0]
				translatedline = translatedline.replace(originalfound, 'engine.interpolate(' + interpolate[0].split('interpolate ')[1].strip()[:-1].strip() + ')')
			if func:
				func = refind.findall(r'\{[ \t]*func[ \t]+[a-zA-Z0-9_]+[ \t]*,[^}]*\}', translatedline)
				exec(func[0].split('func ', 1)[1].split(',', 2)[0].strip() + '=lambda ' + func[0].split('func ', 1)[1].split(',', 2)[1].strip().replace(' ', ',') + ':' + func[0].split('func ', 1)[1].split(',', 2)[2].strip()[:-1], globals())
				translatedline = ''
			if eq:
				eq = refind.findall(r'\{[ \t]*eq[ \t]+[a-zA-Z0-9_]+[ \t]*,[^}]*\}', translatedline)
				exec(eq[0].split('eq ', 1)[1].split(',', 1)[0].strip() + '=Eq(' + eq[0].split('eq ', 1)[1].split(',', 1)[1].strip()[:-1].replace('=', ',') + ')', globals())
				translatedline = ''
			if plot:
				plot = refind.findall(r'\{[ \t]*plot[ \t]+[^}]*\}', translatedline)
				oldplotlist = plotlist
				plotlist += ( 'engine.plotfunc(' + plot[0].split('plot ')[1].strip()[:-1] + ')\n')
				try:
					exec(plotlist + 'plt.show()', globals())
				except:
					plotlist = oldplotlist
				else:
					translatedline = ''
			if plotcoord:
				plotcoord = refind.findall(r'\{[ \t]*plotlist[ \t]+[^}]*\}', translatedline)
				oldplotlist = plotlist
				plotlist += ('engine.plotlist2d(' + plotcoord[0].split('plotlist ')[1].strip()[:-1] + ')\n')
				try:
					exec(plotlist + 'plt.show()', globals())
				except:
					plotlist = oldplotlist
				else:
					translatedline = ''
			if piechart:
				piechart = refind.findall(r'\{[ \t]*pie[ \t]+[^}]*\}', line)
				exec('engine.piechart(' + piechart[0].split('pie ')[1].strip()[:-1] + ')')
				translatedline = ''
			if barchart:
				barchart = refind.findall(r'\{[ \t]*bar[ \t]+[^}]*\}', line)
				exec('engine.barchart(' + barchart[0].split('bar ')[1].strip()[:-1] + ')')
				translatedline = ''
			if plot3d:
				plot3d = refind.findall(r'\{[ \t]*plot3[ \t]+[^}]*\}', translatedline)
				exec('engine.plotfunc3d(' + plot3d[0].split('plot3 ')[1].strip()[:-1] + ')')
				translatedline = ''
			if var:
				var = refind.findall(r'^\s*[a-zA-Z_][a-zA-Z0-9_]*\s*=\s*[^=]+', translatedline)
				exec(var[0], globals())
				translatedline = ''
			if translatedline:
				ans = shell.ragoae(translatedline)
				try:
					toreturn += eval(f'pretty({ans}, use_unicode = True)') + '\n\n'
				except:
					toreturn += ans + '\n\n'
	except:
		pass
	return toreturn
def retranslateandprint(string):
	global id
	if not string:
		string = ''
	outputboxes[id].config(state = 'normal')
	outputboxes[id].delete('1.0', 'end')
	outputboxes[id].insert('end', string)
	outputboxes[id].config(height = str(outputboxes[id].index('end-1c')).split('.')[0])
	outputboxes[id].config(state = 'disabled')
	return 'break'
def ha():
	searchs = [r'\yplotlist\y', r'\yeval\y', r'\yRisingFactorial\y', r'\yFallingFactorial\y', r'\ynot\y', r'\yor\y', r'\yand\y', r'\yif\y', r'\yelse\y', r'\yabs\y', r'\yround\y', r'\ybar\y', r'\ypie\y', r'\yTrue\y', r'\yFalse\y', r'\yceiling\y', r'\yfloor\y', r'\ygamma\y', r'\ysolve\y', r'\ysqrt\y', r'\ysin\y', r'\ycos\y', r'\ytan\y', r'\ysum\y', r'\yprod\y', r'\yintegrate\y', r'\yderivative\y', r'\ylimit\y', r'\yplot\y', r'\yplot3\y', r'\yinterpolate\y', r'\yfunc\y', r'\yeq\y', r'\'.+?\'', r'".+?"', r'\d+', r'\yclearplot\y', r'\yPiecewise\y']
	tags = ['plotlist', 'eval', 'ffact', 'rfact', 'not', 'or', 'and', 'if', 'else', 'abs', 'rnd', 'bar', 'pi', 'tr', 'fa', 'cel', 'flr', 'gma', 'slve', 'sqrt', 'sin', 'cos', 'tan', 'sum', 'prod', 'int', 'der', 'lim', 'pl', 'pl3', 'inte', 'func', 'eq', 'quos', 'quod', 'num', 'cp', 'ifother']
	colours = ['bold', 'orange', 'bold', 'bold', 'orange', 'orange', 'orange', 'bold', 'bold', 'orange', 'orange', 'bold', 'bold', 'red', 'red', 'orange', 'orange', 'orange', 'bold', 'orange', 'orange', 'orange', 'orange', 'orange', 'orange', 'bold', 'bold', 'bold', 'bold', 'bold', 'bold', 'orange', 'orange', 'green', 'green', 'blue', 'bold', 'orange']
	for entry in inputentries.items():
		entry = entry[1]
		for tag in tags:
			entry.tag_remove(tag, '1.0', 'end')
		for search in searchs:
			n = '1.0'
			while True:
				count = root.intvar()
				n = entry.search(search, n, nocase = 1, count = count, stopindex = 'end', regexp = True)
				if not n:
					break
				nn = '%s+%dc' % (n, count.get())
				entry.tag_add(tags[searchs.index(search)], n, nn)
				n = nn
			colour = colours[searchs.index(search)]
			if colour == 'bold':
				entry.tag_config(tags[searchs.index(search)], font = (monospace, 12, 'bold'), foreground = 'purple')
			else:
				entry.tag_config(tags[searchs.index(search)], foreground = colour)
def setid(x):
	global id
	id = x
def newcell():
	global innum
	global row
	text = root.text(text = f'In[{innum}]:')
	text.grid(column = 0, row = row, padx = 10, pady = 10, sticky = 'ne')
	outtext = root.text(text = f'Out[{innum}]:')
	outtext.grid(column = 0, row = row + 1, padx = 10, pady = 10, sticky = 'ne')
	output = root.textbox(state = 'disabled', height = 1, font = (monospace, 12))
	output.grid(sticky = 'new', column = 1, row = row + 1, padx = 10, pady = 10)
	inputtexts[innum] = text
	outputtexts[innum] = outtext
	outputboxes[innum] = output
	entry = root.textbox(height = 1, font = (monospace, 12))
	entry.bind('<KeyRelease>', lambda event: [ha(), entry.config(height = str(entry.index('end')).split('.')[0])])
	entry.bind('<Control-Return>', lambda event: retranslateandprint(translate(entry.get('1.0', 'end-1c'))))
	entry.bind('<FocusIn>', lambda event, id = innum: setid(id))
	entry.grid(column = 1, row = row, padx = 10, pady = 10, sticky = 'new')
	root.rowconfigure(row, weight = 1)
	root.rowconfigure(row + 1, weight = 1)
	root.columnconfigure(1, weight = 1)
	inputentries[innum] = entry
	innum += 1
	row += 2
def delete():
	global row
	try:
		inputentries[id].grid_forget()
		inputtexts[id].grid_forget()
		outputtexts[id].grid_forget()
		outputboxes[id].grid_forget()
		del inputentries[id]
		del inputtexts[id]
		del outputboxes[id]
		del outputtexts[id]
		row -= 2
	except:
		pass
def save():
	path = root.savefile()
	if not path:
		return
	try:
		file = open(path, 'w')
	except:
		root.error('Error!', 'Unwritable File!')
		return
	file.write('`~!'.join([
		'`|!'.join([inputentries[k].get('1.0', 'end-1c') for k in inputentries.keys()]),
		'`|!'.join([inputtexts[k].cget('text') for k in inputtexts.keys()]),
		'`|!'.join([outputboxes[k].get('1.0', 'end-1c') for k in outputboxes.keys()]),
		'`|!'.join([outputtexts[k].cget('text') for k in outputtexts.keys()]),
		plotlist
	]))
	file.close()
def load():
	global inputentries
	global inputtexts
	global outputboxes
	global outputtexts
	global id
	global plotlist
	global row
	global innum
	ask = root.ask('WARNING', 'Discard current notebook?', ('yes', 'no'))
	if not ask:
		return
	path = root.openfile(['all'])
	if not path:
		return
	try:
		file = open(path, 'r')
	except:
		root.error('Error!', 'Unreadable File!')
		return
	row = 1
	id = 1
	innum = 1
	inputentries_, inputtexts_, outputboxes_, outputtexts_, plotlist = file.read().split('`~!')
	inputentries_ = inputentries_.split('`|!')
	inputtexts_ = inputtexts_.split('`|!')
	outputboxes_ = outputboxes_.split('`|!')
	outputtexts_ = outputtexts_.split('`|!')
	file.close()
	for i in range(len(inputentries_)):
		newcell()
		inputentries[i + 1].insert('end', inputentries_[i])
		inputentries[i + 1].config(height = str(inputentries[i + 1].index('end-1c')).split('.')[0])
		inputtexts[i + 1].config(text = inputtexts_[i])
		outputboxes[i + 1].config(state = 'normal')
		outputboxes[i + 1].insert('end', outputboxes_[i])
		outputboxes[i + 1].config(height = str(outputboxes[i + 1].index('end-1c')).split('.')[0])
		outputboxes[i + 1].config(state = 'disabled')
		outputtexts[i + 1].config(text = outputtexts_[i])
	ha()
plotlist = ''
innum = 1
id = 1
row = 1
root = easytk.win()
root.title('MathGod')
if platform.system()  == 'Linux':
	root.attributes('-zoomed', True)
else:
	root.state('zoomed')
root.update()
root.button(text = '+', command = newcell).grid(sticky = 'w', column = 0, row = 0, padx = 10, pady = 10)
root.button(text = '-', command = delete).grid(sticky = 'w', column = 1, row = 0, padx = 10, pady = 10)
root.button(text = 'Save', command = save).grid(sticky = 'w', column = 2, row = 0, padx = 10, pady = 10)
root.button(text = 'Load', command = load).grid(sticky = 'w', column = 3, row = 0, padx = 10, pady = 10)
inputentries = {}
inputtexts = {}
outputboxes = {}
outputtexts = {}
newcell()
root.show()