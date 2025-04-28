import easytk
import chess
import chess.engine
import copy
import platform
root = easytk.win(style = False)
root.title('ChessPy')
class Board:
	def __init__(self):
		self.positions = {
			'a': ['WR', 'WP', None, None, None, None, 'BP', 'BR'],
			'b': ['WN', 'WP', None, None, None, None, 'BP', 'BN'],
			'c': ['WB', 'WP', None, None, None, None, 'BP', 'BB'],
			'd': ['WQ', 'WP', None, None, None, None, 'BP', 'BQ'],
			'e': ['WK', 'WP', None, None, None, None, 'BP', 'BK'],
			'f': ['WB', 'WP', None, None, None, None, 'BP', 'BB'],
			'g': ['WN', 'WP', None, None, None, None, 'BP', 'BN'],
			'h': ['WR', 'WP', None, None, None, None, 'BP', 'BR']
		}
		self.wm = True
		self.moves = []
		self.pawnmoveswhite = None
		self.pawnmovesblack = None
		self.kingmoveswhite = False
		self.rookmoves1white = False
		self.rookmoves2white = False
		self.kingmovesblack = False
		self.rookmoves1black = False
		self.rookmoves2black = False
	def correspond(self, inpt):
		num = range(26)
		alph = (
			'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i',
			'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r',
			's', 't', 'u', 'v', 'w', 'x', 'y', 'z'
			)
		if type(inpt) == str:
			return num[alph.index(inpt)]
		elif type(inpt) == int:
			return alph[num.index(inpt)]
	def legal(self, s1, s2, checkcall = False):
		column1, row1, column2, row2 = s1[0], int(s1[1]) - 1, s2[0], int(s2[1]) - 1
		p1 = self.positions[column1][row1]
		p2 = self.positions[column2][row2]
		if p1 and not p1[0] == ('W', 'B')[int(self.wm)]:
			pass
		else:
			return False
		if s1 == s2:
			return False
		if not checkcall:
			oldpositions = copy.deepcopy(self.positions)
			self.wm = not self.wm
			column1, row1, column2, row2 = s1[0], int(s1[1]) - 1, s2[0], int(s2[1]) - 1
			p1 = self.positions[column1][row1]
			self.positions[column2][row2] = p1
			self.positions[column1][row1] = None
			if self.wm:
				colour = 'B'
			else:
				colour = 'W'
			king = colour + 'K'
			for col in 'abcdefgh':
				if king in self.positions[col]:
					kingpos = col + str(self.positions[col].index(king) + 1)
			for col in 'abcdefgh':
				fullcol = self.positions[col]
				for row in range(8):
					if fullcol[row] and not fullcol[row][0] == colour:
						try:
							if self.legal(col + str(row + 1), kingpos, True):
								self.wm = not self.wm
								self.positions = copy.deepcopy(oldpositions)
								return False
						except:
							pass
			self.wm = not self.wm
			self.positions = copy.deepcopy(oldpositions)
		colour1 = p1[0]
		p1 = p1[1]
		if p2:
			colour2 = p2[0]
			if colour1 == colour2:
				return False
		if p1 == 'R':
			if column1 == column2:
				fullcol = self.positions[column1]
				if row1 - row2 < 0:
					increment = 1
				else:
					increment = -1
				n = row1
				for i in range(abs(row1 - row2) - 1):
					n += increment
					if not fullcol[n] == None:
						return False
				return True
			if row1 == row2:
				fullrow = list()
				for col in 'abcdefgh':
					fullrow.append(self.positions[col][row1])
				if self.correspond(column1) - self.correspond(column2) < 0:
					increment = 1
				else:
					increment = -1
				n = self.correspond(column1)
				for i in range(abs(self.correspond(column1) - self.correspond(column2)) - 1):
					n += increment
					try:
						if not fullrow[n] == None:
							return False
					except:
						return False
				return True
		elif p1 == 'N':
			if abs(self.correspond(column1) - self.correspond(column2)) == 2 and abs(row1 - row2) == 1:
				return True
			if abs(row1 - row2) == 2 and abs(self.correspond(column1) - self.correspond(column2)) == 1:
				return True
		elif p1 == 'B':
			dc = abs(self.correspond(column1) - self.correspond(column2))
			dr = abs(row1 - row2)
			if not dc == dr:
				return False
			if row1 - row2 < 0:
				incrementvert = 1
			else:
				incrementvert = -1
			if self.correspond(column1) - self.correspond(column2) < 0:
				incrementhoriz = 1
			else:
				incrementhoriz = -1
			nh = self.correspond(column1)
			nv = row1
			for i in range(dc - 1):
				nh += incrementhoriz
				nv += incrementvert
				if not self.positions[self.correspond(nh)][nv] == None:
					return False
			return True
		elif p1 == 'Q':
			if column1 == column2:
				fullcol = self.positions[column1]
				if row1 - row2 < 0:
					increment = 1
				else:
					increment = -1
				n = row1
				for i in range(abs(row1 - row2) - 1):
					n += increment
					if not fullcol[n] == None:
						return False
				return True
			if row1 == row2:
				fullrow = list()
				for col in 'abcdefgh':
					fullrow.append(self.positions[col][row1])
				if self.correspond(column1) - self.correspond(column2) < 0:
					increment = 1
				else:
					increment = -1
				n = self.correspond(column1)
				for i in range(abs(self.correspond(column1) - self.correspond(column2)) - 1):
					n += increment
					if not fullrow[n] == None:
						return False
				return True
			dc = abs(self.correspond(column1) - self.correspond(column2))
			dr = abs(row1 - row2)
			if not dc == dr:
				return False
			if row1 - row2 < 0:
				incrementvert = 1
			else:
				incrementvert = -1
			if self.correspond(column1) - self.correspond(column2) < 0:
				incrementhoriz = 1
			else:
				incrementhoriz = -1
			nh = self.correspond(column1)
			nv = row1
			for i in range(dc - 1):
				nh += incrementhoriz
				nv += incrementvert
				if not self.positions[self.correspond(nh)][nv] == None:
					return False
			return True
		elif p1 == 'K':
			fullrow = list()
			for col in 'abcdefgh':
				fullrow.append(self.positions[col][row1])
			if any(
				(
				all((abs(self.correspond(column1) - self.correspond(column2)) == 1,
				row1 == row2)),
				all((abs(row1 - row2) == 1,
				column1 == column2)),
				all((abs(row1 - row2) == 1,
				abs(self.correspond(column1) - self.correspond(column2)) == 1)),
				)):
				return True
			elif colour1 == 'W':
				if self.kingmoveswhite == False and column1 == 'e' and row1 == 0:
					if row1 == row2:
						if column2 == 'g':
							if self.rookmoves2white == False and fullrow[self.correspond(column1) + 1] == None:
								if self.legal('e1', 'f1'):
									return 'O-OW'
						elif column2 == 'c':
							if all((
								self.rookmoves1white == False,
								fullrow[self.correspond(column1) - 1] == None,
								fullrow[self.correspond(column1) - 3] == None,
								self.legal('e1', 'd1')
								)):
								return 'O-O-OW'
			elif colour1 == 'B':
				if self.kingmovesblack == False and column1 == 'e' and row1 == 7:
					if row1 == row2:
						if column2 == 'g':
							if self.rookmoves2black == False and fullrow[self.correspond(column1) + 1] == None:
								if self.legal('e8', 'f8'):
									return 'O-OB'
						elif column2 == 'c':
							if all((
								self.rookmoves1black == False,
								fullrow[self.correspond(column1) - 1] == None,
								fullrow[self.correspond(column1) - 2] == None,
								self.legal('e8', 'd8')
								)):
								return 'O-O-OB'
		elif p1 == 'P':
			if all((
				colour1 == 'W', row2 - row1 == 1,
				column1 == column2,
				self.positions[column1][row2] == None
				)):
				return True
			elif all((
				colour1 == 'B', row1 - row2 == 1,
				column1 == column2,
				self.positions[column1][row2] == None
				)):
				return True
			if all((
				colour1 == 'W', row1 == 1,
				column1 == column2,
				self.positions[column1][row2] == None,
				)):
				if all((
				row2 - row1 == 2,
				self.positions[column1][row2 - 1] == None
				)):
					return True
			elif all((
				colour1 == 'B', row1 == 6,
				column1 == column2,
				self.positions[column1][row2] == None,
				)):
				if all((
				row1 - row2 == 2,
				self.positions[column1][row2 + 1] == None
				)):
					return True
			elif all((
				colour1 == 'W', row2 - row1 == 1,
				abs(self.correspond(column1) - self.correspond(column2)) == 1,
				self.positions[column2][row2]
				)):
				if not colour1 == self.positions[column2][row2][0]:
					return True
			elif all((
				colour1 == 'B', row1 - row2 == 1,
				abs(self.correspond(column1) - self.correspond(column2)) == 1,
				self.positions[column2][row2]
				)):
				if not colour1 == self.positions[column2][row2][0]:
					return True
			elif all((
				colour1 == 'W',
				self.pawnmovesblack == column2,
				row2 == 5
			)):
				self.positions[column2][4] = None
				return True
			elif all((
				colour1 == 'B',
				self.pawnmoveswhite == column2,
				row2 == 2
			)):
				self.positions[column2][3] = None
				return True
	def getlegalmoves(self, piece, square, colour):
		moves = []
		if piece == 'R':
			column = square[0]
			fullcol = self.positions[column]
			row = int(square[1]) - 1
			fullrow = []
			for i in range(8):
				fullrow.append(self.positions[self.correspond(i)][row])
			for i in range(2):
				increment = (-1, 1)[i]
				while not row == (0, 7)[i]:
					row += increment
					if fullcol[row]:
						break
					else:
						moves.append(column + str(row + 1))
			for i in range(2):
				increment = (-1, 1)[i]
				while not row == (0, 7)[i]:
					column = self.correspond(self.correspond(column) + 1)
					if fullrow[self.correspond(column)]:
						break
					else:
						moves.append(column + str(row + 1))
		return moves
	def move(self, s1, s2):
		legalval = self.legal(s1, s2)
		if legalval == True:
			column1, row1, column2, row2 = s1[0], int(s1[1]) - 1, s2[0], int(s2[1]) - 1
			p1 = self.positions[column1][row1]
			if p1 and p1[1] == 'P':
				if p1[0] == 'W':
					if row2 == 7:
						while True:
							promotion = str(root.askstring('Promote Your Pawn', 'Type q/r/b/n:'))
							if promotion.lower().strip() in ('q', 'r', 'b', 'n'):
								break
						p1 = 'W' + promotion.upper()
				else:
					if row2 == 0:
						while True:
							promotion = str(root.askstring('Promote Your Pawn', 'Type q/r/b/n:'))
							if promotion.lower().strip() in ('q', 'r', 'b', 'n'):
								break
						p1 = 'B' + promotion.upper()
			self.positions[column2][row2] = p1
			self.positions[column1][row1] = None
			if not self.wm:
				self.moves[len(self.moves) - 1] = ((self.lastwhitemove, s1 + ' ' + s2))
			else:
				self.lastwhitemove = s1 + ' ' + s2
				self.moves.append((s1 + ' ' + s2, '...'))
			if p1:
				if p1[0] == 'W':
					self.pawnmoveswhite = None
				else:
					self.pawnmovesblack = None
				if p1[1] == 'P':
					if p1[0] == 'W' and row1 == 1 and row2 == 3:
						self.pawnmoveswhite = column1
					elif p1[0] == 'B' and row1 == 6 and row2 == 4:
						self.pawnmovesblack = column1
			if p1 == 'WR' and column1 == 'a':
				self.rookmoves1white = True
			elif p1 == 'WR' and column1 == 'h':
				self.rookmoves2white = True
			elif p1 == 'BR' and column1 == 'a':
				self.rookmoves1black = True
			elif p1 == 'BR' and column1 == 'h':
				self.rookmoves2black = True
			elif p1 == 'WK':
				self.kingmoveswhite = True
			elif p1 == 'BK':
				self.kingmovesblack = True
		elif legalval == 'O-OW':
			self.positions['e'][0] = None
			self.positions['g'][0] = 'WK'
			self.positions['h'][0] = None
			self.positions['f'][0] = 'WR'
		elif legalval == 'O-OB':
			self.positions['e'][7] = None
			self.positions['g'][7] = 'BK'
			self.positions['h'][7] = None
			self.positions['f'][7] = 'BR'
		elif legalval == 'O-O-OW':
			self.positions['e'][0] = None
			self.positions['c'][0] = 'WK'
			self.positions['a'][0] = None
			self.positions['d'][0] = 'WR'
		elif legalval == 'O-O-OB':
			self.positions['e'][7] = None
			self.positions['c'][7] = 'BK'
			self.positions['a'][7] = None
			self.positions['d'][7] = 'WR'
		if legalval:
			self.wm = not self.wm
def clicked(square, number):
	global clicks
	if clicks == []:
		if board.positions[square[0]][int(square[1]) - 1]:
			clicks.append((square, number))
			squares[number].configure(style = 'Clicked.TButton')
	else:
		if colour == None:
			board.move(clicks[0][0], square)
			refresh()
			clicks = []
		else:
			if board.legal(clicks[0][0], square):
				engineboard.push(chess.Move.from_uci(clicks[0][0] + square))
				board.move(clicks[0][0], square)
				refresh()
				playengine()
			refresh()
			clicks = []
def refresh():
	global squares
	squares = []
	showmove.config(
		text =
		'White to move' if board.wm else 'Black to move'
		)
	moveswhite.focus_set() if board.wm else movesblack.focus_set()
	moveswhite.delete('0', 'end')
	movesblack.delete('0', 'end')
	for i in range(len(board.moves)):
		moveswhite.insert('end', str(i + 1) + '. ' + board.moves[i][0])
		movesblack.insert('end', str(i + 1) + '. ' + board.moves[i][1])
		moveswhite.see(i)
		movesblack.see(i)
	for col in 'abcdefgh':
		for row in range(8):
			p = board.positions[col][row]
			style = 'White.TButton' if not (row + ord(col)) % 2 else 'Black.TButton'
			b = root.button(text = p, style = style)
			exec(f'b.configure(command = lambda: clicked("{col + str(row + 1)}", {len(squares)}))')
			b.grid(column = board.correspond(col), row = 8 - row, sticky = 'nsew')
			root.grid_columnconfigure(board.correspond(col), weight = 1)
			root.grid_rowconfigure(8 - row, weight = 1)
			squares.append(b)
	root.update()
def playengine():
	move = engine.play(engineboard, chess.engine.Limit(time = 0.1))
	s1 = str(move.move)[:2]
	s2 = str(move.move)[2:]
	engineboard.push(move.move)
	board.move(s1, s2)
board = Board()
s = root.style()
s.configure('Black.TButton', background = 'darkblue', foreground = 'white')
s.configure('White.TButton', background = 'white', foreground = 'black')
s.configure('Clicked.TButton', background = 'red', foreground = 'white')
s.configure('Custom.TLabel', background = 'white')
squares = list()
clicks = list()
infowin = root.subwin()
infowin.title('Info')
showmove = infowin.text(text = 'White to move', style = 'Custom.TLabel', font = 'TkDefaultFont 15')
showmove.pack(side = 'top', padx = 10, pady = 10, fill = 'x')
infowin.separator(way = 'horizontal').pack(fill = 'x')
moveswhite = infowin.listbox()
moveswhite.pack(side = 'left', padx = 10, pady = 10, fill = 'both')
movesblack = infowin.listbox()
movesblack.pack(side = 'right', padx = 10, pady = 10, fill = 'both')
infowin.protocol('WM_DELETE_WINDOW', lambda: None)
infowin.sizablefalse()
twop = root.ask('', 'Do you want to play two player mode?', ('yes', 'no'))
colour = None
if not twop:
	engineboard = chess.Board()
	colour = root.ask('', 'Do you want to play white?', ('yes', 'no'))
	root.info('Info', 'You will now be asked to give a path to a chess engine.')
	path = root.openfile(types = ['all'])
	if not path:
		root.destroy()
		exit()
	try:
		engine = chess.engine.SimpleEngine.popen_uci(path)
	except:
		root.error('Error!', 'Invalid Chess Engine.')
		root.destroy()
		exit()
	if not colour:
		playengine()
refresh()
if platform.system() == 'Linux':
	root.attributes('-zoomed', True)
else:
	root.state('zoomed')
root.show()