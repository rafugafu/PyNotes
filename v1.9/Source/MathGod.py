import matplotlib.pyplot as plt
import numpy as np
import re as refind
import easytk
from sympy import *
import sympy
import ast
import builtins
import xml.etree.ElementTree as ET
import ziamath as zm
import cairosvg
from PIL import Image, ImageTk, ImageDraw, ImageFont
import code
import sys
import platform
import io
if platform.system() == 'Linux':
	import subprocess
	monospace = 'monospace'
else:
	monospace = 'Courier'
	fd = easytk.fd
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
			self.shell.push('pass')
		sys.stdout = old_stdout
		sys.stderr = old_stderr
		return output.getvalue() + error.getvalue()
shell = interactive_shell()
def _auto_symbols(code_str):
	try:
		tree = ast.parse(code_str)
	except Exception:
		return
	g = globals()
	for node in ast.walk(tree):
		if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load) and node.id not in g and not hasattr(builtins, node.id):
			g[node.id] = Symbol(node.id)
def _gexec(code_str):
	_auto_symbols(code_str)
	exec(code_str, globals())
def _geval(code_str):
	_auto_symbols(code_str)
	return eval(code_str, globals())
_MATH_OPS = {
	'integrate': 'engine.integral',
	'derivative': 'engine.derivative',
	'limit': 'engine.limit',
	'solve': 'engine.solve',
	'sum': 'engine.summation',
	'prod': 'engine.product',
	'interpolate': 'engine.interpolate',
}
def _translate_innermost_brace(m):
	content = m.group(1).strip()
	km = refind.match(r'(\w+)\s+(.*)', content, refind.DOTALL)
	if not km:
		return '{' + content + '}'
	keyword, args = km.group(1), km.group(2).strip()
	if keyword in _MATH_OPS:
		return _MATH_OPS[keyword] + '(' + args + ')'
	return '{' + content + '}'
def expand_braces(line):
	pattern = r'\{([^{}]*)\}'
	prev = None
	while prev != line:
		prev = line
		line = refind.sub(pattern, _translate_innermost_brace, line)
	return line
output_cache = {}
def _render_latex_img(latex_str, size = 24, scale = 1.0):
	math_obj = zm.Math.fromlatex(latex_str, size = size)
	svg_text = math_obj.svg()
	svg_bytes = svg_text.encode('utf-8')
	svg_root = ET.fromstring(svg_text)
	svg_w = float(svg_root.get('width', '500'))
	svg_h = float(svg_root.get('height', '100'))
	if max(svg_w * scale, svg_h * scale) <= 32767:
		png_bytes = cairosvg.svg2png(bytestring = svg_bytes, scale = scale)
		img = Image.open(io.BytesIO(png_bytes))
	else:
		safe_scale = 32767 / max(svg_w, svg_h)
		png_bytes = cairosvg.svg2png(bytestring = svg_bytes, scale = safe_scale)
		img = Image.open(io.BytesIO(png_bytes))
		img = img.resize((max(1, int(svg_w * scale)), max(1, int(svg_h * scale))), Image.LANCZOS)
	if img.mode == 'RGBA':
		bg = Image.new('RGB', img.size, 'white')
		bg.paste(img, mask = img.split()[3])
		return bg
	return img.convert('RGB')
def _render_text_img(text):
	for path in ['/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf', '/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf']:
		try:
			font = ImageFont.truetype(path, 16)
			break
		except:
			font = None
	if font is None:
		try:
			font = ImageFont.load_default(size = 16)
		except:
			font = ImageFont.load_default()
	lines = text.split('\n')
	dummy = Image.new('RGB', (1, 1), 'white')
	draw = ImageDraw.Draw(dummy)
	try:
		line_h = draw.textbbox((0, 0), 'A', font = font)[3] + 4
		max_w = max(draw.textbbox((0, 0), l, font = font)[2] for l in lines) if lines else 10
	except:
		line_h = 20
		max_w = max(len(l) * 9 for l in lines) if lines else 100
	img = Image.new('RGB', (max(1, max_w + 20), max(1, line_h * len(lines) + 10)), 'white')
	draw = ImageDraw.Draw(img)
	for i, line in enumerate(lines):
		draw.text((10, 5 + i * line_h), line, font = font, fill = 'black')
	return img
def render_output(label, items):
	if not items:
		label.config(image = '', text = '')
		return
	images = []
	for type_, content in items:
		if type_ == 'latex':
			try:
				images.append(_render_latex_img(content))
			except:
				images.append(_render_text_img(content))
		else:
			images.append(_render_text_img(content))
	total_h = sum(img.height for img in images) + 10 * (len(images) - 1)
	max_w = max(img.width for img in images)
	combined = Image.new('RGB', (max(1, max_w), max(1, total_h)), 'white')
	y = 0
	for img in images:
		combined.paste(img, (0, y))
		y += img.height + 10
	available_w = max(100, root.getgeo()[0] - 420)
	if combined.width > available_w:
		ratio = available_w / combined.width
		combined = combined.resize((available_w, max(1, int(combined.height * ratio))), Image.LANCZOS)
	photo = ImageTk.PhotoImage(combined)
	root.imgs.append(photo)
	label.config(image = root.imgs[-1], text = '')
def translate(code_str):
	global plotlist
	global shell
	items = []
	code_str = 'clearplot\n' + code_str
	try:
		for line in code_str.split('\n'):
			line = line.replace('^', '**')
			multiplication = refind.findall(r'(\d+)([a-zA-Z])', line)
			for match in multiplication:
				line = line.replace(match[0] + match[1], match[0] + '*' + match[1])
			translatedline = expand_braces(line)
			if not translatedline:
				continue
			if translatedline.strip() == 'clearplot':
				plotlist = ''
				continue
			func = refind.findall(r'\{[ \t]*func[ \t]+[a-zA-Z0-9_]+[ \t]*,[^}]*\}', translatedline)
			eq = refind.findall(r'\{[ \t]*eq[ \t]+[a-zA-Z0-9_]+[ \t]*,[^}]*\}', translatedline)
			plot = refind.findall(r'\{[ \t]*plot[ \t]+[^}]*\}', translatedline)
			plotcoord = refind.findall(r'\{[ \t]*plotlist[ \t]+[^}]*\}', translatedline)
			piechart = refind.findall(r'\{[ \t]*pie[ \t]+[^}]*\}', translatedline)
			barchart = refind.findall(r'\{[ \t]*bar[ \t]+[^}]*\}', translatedline)
			plot3d = refind.findall(r'\{[ \t]*plot3[ \t]+[^}]*\}', translatedline)
			if func:
				func = refind.findall(r'\{[ \t]*func[ \t]+[a-zA-Z0-9_]+[ \t]*,[^}]*\}', translatedline)
				funcfunc = func[0].split('func ', 1)[1].split(',', 2)[2].strip()[:-1]
				_gexec(func[0].split('func ', 1)[1].split(',', 2)[0].strip() + '=lambda ' + func[0].split('func ', 1)[1].split(',', 2)[1].strip().replace(' ', ',') + ':' + funcfunc)
				translatedline = 'print("' + str(sympify(funcfunc)) + '")'
			if eq:
				eq = refind.findall(r'\{[ \t]*eq[ \t]+[a-zA-Z0-9_]+[ \t]*,[^}]*\}', translatedline)
				eqname = eq[0].split('eq ', 1)[1].split(',', 1)[0].strip()
				_gexec(eqname + '=Eq(' + eq[0].split('eq ', 1)[1].split(',', 1)[1].strip()[:-1].replace('=', ',') + ')')
				translatedline = 'print("' + eqname + '")'
			if plot:
				plot = refind.findall(r'\{[ \t]*plot[ \t]+[^}]*\}', translatedline)
				oldplotlist = plotlist
				plotlist += ('engine.plotfunc(' + plot[0].split('plot ')[1].strip()[:-1] + ')\n')
				try:
					_gexec(plotlist + 'plt.show()')
				except:
					plotlist = oldplotlist
				else:
					plotlabel = plot[0].split('plot ')[1].strip()[:-1].split(',')[0].strip()
					translatedline = 'print("' + plotlabel + '")'
			if plotcoord:
				plotcoord = refind.findall(r'\{[ \t]*plotlist[ \t]+[^}]*\}', translatedline)
				oldplotlist = plotlist
				plotlist += ('engine.plotlist2d(' + plotcoord[0].split('plotlist ')[1].strip()[:-1] + ')\n')
				try:
					_gexec(plotlist + 'plt.show()')
				except:
					plotlist = oldplotlist
				else:
					translatedline = ''
			if piechart:
				piechart = refind.findall(r'\{[ \t]*pie[ \t]+[^}]*\}', translatedline)
				_gexec('engine.piechart(' + piechart[0].split('pie ')[1].strip()[:-1] + ')')
				translatedline = 'print("' + piechart[0].split('pie ')[1].strip()[:-1] + '")'
			if barchart:
				barchart = refind.findall(r'\{[ \t]*bar[ \t]+[^}]*\}', translatedline)
				_gexec('engine.barchart(' + barchart[0].split('bar ')[1].strip()[:-1] + ')')
				printout = barchart[0].split('bar ')[1].strip()[:-1].split(',')
				printout = ','.join(printout[int(len(printout)/2):]).strip()
				translatedline = 'print("' + printout + '")'
			if plot3d:
				plot3d = refind.findall(r'\{[ \t]*plot3[ \t]+[^}]*\}', translatedline)
				_gexec('engine.plotfunc3d(' + plot3d[0].split('plot3 ')[1].strip()[:-1] + ')')
				plot3dlabel = plot3d[0].split('plot3 ')[1].strip()[:-1].split(',')[0].strip()
				translatedline = 'print("' + plot3dlabel + '")'
			var = refind.findall(r'^\s*[a-zA-Z_][a-zA-Z0-9_]*\s*=\s*[^=]+', translatedline)
			if var:
				_gexec(var[0])
				rhs = var[0].split('=', 1)[1].strip()
				translatedline = 'print("' + rhs + '")'
			if translatedline:
				_auto_symbols(translatedline)
				ans = shell.ragoae(translatedline).strip()
				if ans:
					try:
						latex_str = _geval('latex(' + ans + ')')
						items.append(('latex', latex_str))
					except Exception:
						items.append(('text', ans))
	except Exception as error:
		items.append(('text', 'Error: ' + str(error)))
	return items
def retranslateandprint(items):
	global id
	if not items:
		items = []
	output_cache[id] = '\x1e'.join(t + '\x1f' + c for t, c in items)
	render_output(outputboxes[id], items)
	return 'break'
_SYMPY_HIGHLIGHT_COVERED = {'plotlist', 'eval', 'RisingFactorial', 'FallingFactorial', 'not', 'or', 'and', 'if', 'else', 'abs', 'round', 'bar', 'pie', 'True', 'False', 'ceiling', 'floor', 'gamma', 'solve', 'sqrt', 'sin', 'cos', 'tan', 'sum', 'prod', 'integrate', 'derivative', 'limit', 'plot', 'plot3', 'interpolate', 'func', 'eq', 'clearplot', 'Piecewise'}
_SYMPY_HIGHLIGHT_NAMES = sorted((name for name in dir(sympy) if len(name) > 1 and name.isidentifier() and name[0].isalpha() and not name.startswith('_') and name not in _SYMPY_HIGHLIGHT_COVERED and callable(getattr(sympy, name, None))), key = len, reverse = True)
_SYMPY_HIGHLIGHT_PATTERN = r'\y(' + '|'.join(_SYMPY_HIGHLIGHT_NAMES) + r')\y'
def ha(entry = None):
	searchs = [r'\yplotlist\y', r'\yeval\y', r'\yRisingFactorial\y', r'\yFallingFactorial\y', r'\ynot\y', r'\yor\y', r'\yand\y', r'\yif\y', r'\yelse\y', r'\yabs\y', r'\yround\y', r'\ybar\y', r'\ypie\y', r'\yTrue\y', r'\yFalse\y', r'\yceiling\y', r'\yfloor\y', r'\ygamma\y', r'\ysolve\y', r'\ysqrt\y', r'\ysin\y', r'\ycos\y', r'\ytan\y', r'\ysum\y', r'\yprod\y', r'\yintegrate\y', r'\yderivative\y', r'\ylimit\y', r'\yplot\y', r'\yplot3\y', r'\yinterpolate\y', r'\yfunc\y', r'\yeq\y', r'\'.+?\'', r'".+?"', r'\d+', r'\yclearplot\y', r'\yPiecewise\y', r'\^\-?[A-Za-z0-9.]+', r'_[A-Za-z0-9]+']
	tags = ['plotlist', 'eval', 'ffact', 'rfact', 'not', 'or', 'and', 'if', 'else', 'abs', 'rnd', 'bar', 'pi', 'tr', 'fa', 'cel', 'flr', 'gma', 'slve', 'sqrt', 'sin', 'cos', 'tan', 'sum', 'prod', 'int', 'der', 'lim', 'pl', 'pl3', 'inte', 'func', 'eq', 'quos', 'quod', 'num', 'cp', 'ifother', 'power', 'subscript']
	effects = ['bold', 'orange', 'bold', 'bold', 'orange', 'orange', 'orange', 'bold', 'bold', 'orange', 'orange', 'bold', 'bold', 'red', 'red', 'orange', 'orange', 'orange', 'bold', 'orange', 'orange', 'orange', 'orange', 'orange', 'orange', 'bold', 'bold', 'bold', 'bold', 'bold', 'bold', 'orange', 'orange', 'green', 'green', 'blue', 'bold', 'orange', 'up', 'down']
	searchs = searchs + [_SYMPY_HIGHLIGHT_PATTERN]
	tags = tags + ['sympyfunc']
	effects = effects + ['orange']
	if entry is None:
		entries = list(inputentries.values())
	else:
		entries = [entry]
	for entry in entries:
		for tag in tags:
			entry.tag_remove(tag, '1.0', 'end')
		for search in searchs:
			n = '1.0'
			while True:
				count = root.intvar()
				n = entry.search(search, n, count = count, stopindex = 'end', regexp = True)
				if not n:
					break
				nn = '%s+%dc' % (n, count.get())
				if effects[searchs.index(search)] in ('up', 'down'):
					entry.tag_add('sym', n, n + '+1c')
					n += '+1c'
				entry.tag_add(tags[searchs.index(search)], n, nn)
				n = nn
			effect = effects[searchs.index(search)]
			if effect == 'bold':
				entry.tag_config(tags[searchs.index(search)], font = (monospace, 12, 'bold'), foreground = 'purple')
			elif effect == 'up':
				entry.tag_config(tags[searchs.index(search)], offset = 7, font = (monospace, 10, 'italic'))
			elif effect == 'down':
				entry.tag_config(tags[searchs.index(search)], offset = -7, font = (monospace, 10, 'italic'))
			else:
				entry.tag_config(tags[searchs.index(search)], foreground = effect)
		entry.tag_remove('power_2', '1.0', 'end')
		entry.tag_remove('subscript_2', '1.0', 'end')
		text = entry.get('1.0', 'end-1c')
		i = 0
		while i < len(text):
			if text[i] in '^_' and i + 1 < len(text) and text[i + 1] == '(':
				depth = 0
				j = i + 1
				while j < len(text):
					if text[j] == '(':
						depth += 1
					elif text[j] == ')':
						depth -= 1
						if depth == 0:
							break
					j += 1
				entry.tag_add('sym', '1.0+%dc' % i, '1.0+%dc' % (i + 1))
				entry.tag_add('power_2' if text[i] == '^' else 'subscript_2', '1.0+%dc' % (i + 1), '1.0+%dc' % (j + 1))
				i = j + 1
			else:
				i += 1
		entry.tag_config('power_2', offset = 7, font = (monospace, 10, 'italic'))
		entry.tag_config('subscript_2', offset = -7, font = (monospace, 10, 'italic'))
		entry.tag_config('sym', foreground = 'white', background = 'white')
def schedule_ha(entry):
	if getattr(entry, '_ha_after', None):
		root.after_cancel(entry._ha_after)
	entry._ha_after = root.after(150, lambda: ha(entry))
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
	output = root.text()
	output.grid(sticky = 'new', column = 1, row = row + 1, padx = 10, pady = 10)
	inputtexts[innum] = text
	outputtexts[innum] = outtext
	outputboxes[innum] = output
	output_cache[innum] = ''
	entry = root.textbox(height = 1, font = (monospace, 12))
	entry.bind('<KeyRelease>', lambda event, entry = entry: [schedule_ha(entry), entry.config(height = str(entry.index('end')).split('.')[0])])
	entry.bind('<Control-Return>', lambda event: retranslateandprint(translate(entry.get('1.0', 'end-1c'))))
	entry.bind('<FocusIn>', lambda event, id = innum: setid(id))
	entry.grid(column = 1, row = row, padx = 10, pady = 10, sticky = 'new')
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
		if id in output_cache:
			del output_cache[id]
		row -= 2
	except:
		pass
def save():
	if platform.system() == 'Linux':
		path = subprocess.run(['zenity', '--file-selection', '--filename=./', '--save', '--confirm-overwrite', '--title=Save As', '--file-filter=All Files | *'], capture_output = True, text = True).stdout.strip()
	else:
		path = fd.asksaveasfilename()
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
		'`|!'.join([output_cache.get(k, '') for k in outputboxes.keys()]),
		'`|!'.join([outputtexts[k].cget('text') for k in outputtexts.keys()]),
		plotlist
	]))
	file.close()
def load():
	global inputentries
	global inputtexts
	global outputboxes
	global outputtexts
	global output_cache
	global id
	global plotlist
	global row
	global innum
	ask = root.ask('WARNING', 'Discard current notebook?', ('yes', 'no'))
	if not ask:
		return
	if platform.system() == 'Linux':
		path = subprocess.run(['zenity', '--file-selection', '--filename=./', '--title=Open File', '--file-filter=All Files | *.*'], capture_output = True, text = True).stdout.strip()
	else:
		path = fd.askopenfilename(title = 'Open File', filetypes = (('All Files', '*.*')))
	if not path:
		return
	try:
		file = open(path, 'r')
	except:
		root.error('Error!', 'Unreadable File!')
		return
	try:
		inputentries_, inputtexts_, outputboxes_, outputtexts_, plotlist = file.read().split('`~!')
		inputentries_ = inputentries_.split('`|!')
		inputtexts_ = inputtexts_.split('`|!')
		outputboxes_ = outputboxes_.split('`|!')
		outputtexts_ = outputtexts_.split('`|!')
	except:
		root.error('Error!', 'Not a saved MathGod file!')
		return
	for k in list(inputentries.keys()):
		inputentries[k].grid_forget()
		inputtexts[k].grid_forget()
		outputtexts[k].grid_forget()
		outputboxes[k].grid_forget()
	inputentries = {}
	inputtexts = {}
	outputboxes = {}
	outputtexts = {}
	output_cache = {}
	row = 1
	id = 1
	innum = 1
	file.close()
	for i in range(len(inputentries_)):
		newcell()
		inputentries[i + 1].insert('end', inputentries_[i])
		inputentries[i + 1].config(height = str(inputentries[i + 1].index('end-1c')).split('.')[0])
		inputtexts[i + 1].config(text = inputtexts_[i])
		output_cache[i + 1] = outputboxes_[i]
		loaded_items = []
		for part in outputboxes_[i].split('\x1e'):
			if '\x1f' in part:
				tc = part.split('\x1f', 1)
				loaded_items.append((tc[0], tc[1]))
			elif part:
				loaded_items.append(('text', part))
		render_output(outputboxes[i + 1], loaded_items)
		outputtexts[i + 1].config(text = outputtexts_[i])
	ha()
plotlist = ''
innum = 1
id = 1
row = 1
root = easytk.win()
root.title('MathGod')
root.update()
root.geometry(f'{root.winfo_screenwidth()}x{root.winfo_screenheight()}')
if platform.system() == 'Linux':
	root.attributes('-zoomed', True)
else:
	root.state('zoomed')
root.update()
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
