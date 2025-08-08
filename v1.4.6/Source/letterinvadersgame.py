import matplotlib.pyplot as plt
import random
import tkinter as tk
import os
import getpass
import platform
WIDTH, HEIGHT = 700, 500
FORT_HEIGHT = 60
FORT_HEIGHTS = range(50, 70)
FORT_SECTIONS = 80
if platform.system() == 'Linux':
	homedir = f'/home/{getpass.getuser()}'
	rootdir = '/usr/share/PyNotes'
else:
	homedir = f'C:/Users/{getpass.getuser()}'
	rootdir = 'C:/Program Files/PyNotes'
WORDS = open(f'{rootdir}/wordlist.txt', 'r').read().split('\n')
INITIAL_FALL_SPEED = 300
SPAWN_INTERVAL = 2000
SPEED_INCREMENT = 25
SPEED_INCREASE_INTERVAL = 20000
COLOR_OF_FORT = 'grey'
class Game:
	def __init__(self):
		self.root = tk.Tk()
		self.accuracies_list = []
		self.root.title('Letter Invaders')
		self.canvas = tk.Canvas(master = self.root, width = WIDTH, height = HEIGHT, bg = 'black')
		self.canvas.pack()
		self.typed = ''
		self.accuracies = 0
		self.accuracies_going = 0
		self.totals = 0
		self.fort_sections = []
		for i in range(FORT_SECTIONS):
			section = self.canvas.create_rectangle(
				i * WIDTH/FORT_SECTIONS,
				HEIGHT - random.choice(FORT_HEIGHTS),
				(i + 1) * (WIDTH / FORT_SECTIONS),
				HEIGHT,
				outline = COLOR_OF_FORT,
				fill = COLOR_OF_FORT)
			self.fort_sections.append(section)
		self.words = {}
		self.score = 0
		try:
			os.mkdir(f'{homedir}/.local/PyNotes/game')
		except:
			pass
		try:
			self.highscore = int(open(f'{homedir}/.local/PyNotes/game/highscore.txt', 'r').read().replace('\n', ''))
		except:
			self.highscore = 0
			open(f'{homedir}/.local/PyNotes/game/highscore.txt', 'w')
		self.round = 0
		self.fall_speed = INITIAL_FALL_SPEED
		self.score_text = self.canvas.create_text(10, 10, anchor = 'nw', text = f'Score: {self.score}', fill = 'white', font = ('Arial', 14))
		self.round_text = self.canvas.create_text(10, 30, anchor = 'nw', text = f'Round {self.round}', fill = 'white', font = ('Arial', 14))
		self.highscore_text = self.canvas.create_text(10, 50, anchor = 'nw', text = f'Highscore: {self.highscore}', fill = 'white', font = ('Arial', 14))
		self.root.bind('<KeyPress>', self.check_letter)
		self.start_new_round()
		self.root.mainloop()
	def spawn_word(self):
		if not self.running or self.round_waiting:
			return
		while True:
			word = random.choice(WORDS)
			if not self.words:
				break
			all_the_starts =  [sublist[1][0][0] for sublist in list(self.words.items())]
			if not word[0] in all_the_starts:
				break
		word_width = len(word) * 5
		self.totals += len(word)
		intact_sections = [i for i, section in enumerate(self.fort_sections) if self.canvas.itemcget(section, 'fill') != 'black']
		if intact_sections and random.random() < 0.9:
			chosen_section = random.choice(intact_sections)
			x = (chosen_section * (WIDTH / FORT_SECTIONS)) + (WIDTH / FORT_SECTIONS) // 2
		else:
			x = random.randint(word_width, WIDTH - word_width)
		x = max(word_width, min(x, WIDTH - word_width))
		word_id = self.canvas.create_text(x, 20, text = word, fill = 'white', font = ('Arial', 16))
		self.words[word_id] = [word, x]
		self.root.after(SPAWN_INTERVAL, self.spawn_word)
	def update_words(self):
		if not self.running:
			return
		for word_id in list(self.words.keys()):
			self.canvas.move(word_id, 0, 5)
			x, y = self.canvas.coords(word_id)
			if y >= HEIGHT - FORT_HEIGHT:
				self.destroy_fort_section(x, len(self.words[word_id][0]))
				self.canvas.delete(word_id)
				del self.words[word_id]
				self.score = max(0, self.score - 10)
				self.canvas.itemconfig(self.score_text, text = f'Score: {self.score}')
				if all(self.canvas.itemcget(section, 'fill') == 'black' for section in self.fort_sections):
					self.game_over()
		self.root.after(self.fall_speed, self.update_words)
	def schedule_round_end(self):
		self.root.after(SPEED_INCREASE_INTERVAL, self.check_round_end)
	def check_round_end(self):
		if self.words:
			self.round_waiting = True
			self.root.after(50, self.check_round_end)
		else:
			self.start_new_round()
	def start_new_round(self):
		self.running = False
		self.round_waiting = True
		self.round += 1
		if not self.round == 1:
			self.accuracy_text = self.canvas.create_text(WIDTH // 2, HEIGHT // 2 - 60, fill = 'white', font = ('Arial', 16))
			accuracy_bonus = 0
			if (self.accuracies / self.totals) * 100 >= 90:
				accuracy_bonus = int((self.accuracies / self.totals) * 1000)
				self.score += accuracy_bonus
			self.accuracies_list.append(int((self.accuracies / self.totals)*100))
			self.canvas.itemconfig(self.score_text, text = f'Score: {self.score}')
			self.canvas.itemconfig(self.highscore_text, text = f'Highscore: {self.highscore}')
			self.canvas.itemconfig(self.accuracy_text, text = f'ACCURACY: {int((self.accuracies / self.totals) * 100)}%\nACCURACY BONUS: {accuracy_bonus}')
		self.canvas.itemconfig(self.round_text, text = f'Round {self.round}')
		self.next_round_text = self.canvas.create_text(WIDTH // 2, HEIGHT // 2, text = 'PRESS ENTER TO BEGIN', fill = 'white', font = ('Arial', 16))
		self.root.bind('<Return>', lambda event: self.begin_new_round())
	def begin_new_round(self):
		self.fall_speed = max(50, self.fall_speed - SPEED_INCREMENT)
		self.running = True
		self.round_waiting = False
		if not self.round == 1:
			self.canvas.delete(self.accuracy_text)
		self.accuracies = 0
		self.totals = 0
		self.canvas.delete(self.next_round_text)
		self.root.unbind('<Return>')
		self.schedule_round_end()
		self.spawn_word()
		self.update_words()
	def check_letter(self, event):
		if not self.running:
			return
		letter = event.char
		for word_id, (word, x) in list(self.words.items()):
			if word.startswith(self.typed + letter):
				self.typed += letter
				new_text = word[len(self.typed):]
				self.canvas.itemconfig(word_id, text = new_text)
				self.score += len(self.typed + letter) * 10
				self.accuracies_going += 1
				self.canvas.itemconfig(self.score_text, text = f'Score: {self.score}')
				if self.score > self.highscore:
					self.highscore = self.score
					self.canvas.itemconfig(self.highscore_text, text = f'Highscore: {self.highscore}')
				if not new_text:
					self.canvas.delete(word_id)
					self.typed = ''
					self.accuracies += self.accuracies_going
					self.accuracies_going = 0
					del self.words[word_id]
				return
			else:
				self.canvas.itemconfig(word_id, text = word)
		self.typed = ''
		self.accuracies = max(0, self.accuracies - self.accuracies_going)
		self.accuracies_going = 0
		if self.score > 0:
			self.score = max(0, self.score - 10)
			self.canvas.itemconfig(self.score_text, text = f'Score: {self.score}')
	def destroy_fort_section(self, x, word_length):
		word_width = word_length * 10
		start_index = max(0, int((x - word_width / 2) // (WIDTH / FORT_SECTIONS)))
		end_index = min(FORT_SECTIONS - 1, int((x + word_width / 2) // (WIDTH / FORT_SECTIONS)))
		for i in range(start_index, end_index + 1):
			self.canvas.itemconfig(self.fort_sections[i], fill = 'black', outline = 'red')
	def game_over(self):
		self.running = False
		self.round_waiting = False
		self.accuracies_list.append(self.accuracies)
		self.canvas.create_text(WIDTH // 2, HEIGHT // 2, text = 'GAME OVER\nPRESS ENTER\nTO SEE YOUR\nACCURACY GRAPH', fill = 'red', font = ('Arial', 24, 'bold'))
		open(f'{homedir}/.local/PyNotes/game/highscore.txt', 'w').write(str(self.highscore))
		self.root.unbind('<KeyPress>')
		def show_graph():
			plt.title('Accuracy Graph')
			plt.xticks(range(1, self.round + 1))
			plt.xlabel('Round')
			plt.ylabel('Accuracy')
			plt.plot(range(1, self.round + 1), self.accuracies_list)
			plt.grid(True)
			plt.show()
		self.root.bind('<Return>', lambda event: show_graph())