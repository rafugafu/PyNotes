import io
import re
import wave
import threading
import easytk
import state
try:
	import sounddevice as sd
except Exception:
	pass
try:
	import speech_recognition as sr
except Exception:
	pass
try:
	import numpy as np
except Exception:
	pass
import editor
import utils
def actualspk(text):
	try:
		state.engine.say(text)
		state.engine.runAndWait()
	except Exception as error:
		error = str(error)
		state.root.error('Error', f'An error occured:{error}')
def st():
	utils.show('open speech-to-text')
	global recording
	global audio
	recording = False
	audio = []
	def record():
		global recording
		global audio
		def callback(indata, frames, time, status):
			audio.append(indata.copy())
		with sd.InputStream(callback = callback, channels = channels, dtype = dtype, samplerate = samplerate):
			recording = True
			while recording:
				sd.sleep(1000)
	def stop():
		global recording
		global audio
		audio = np.concatenate(audio, axis = 0)
		file = io.BytesIO()
		with wave.open(file, 'wb') as wf:
			wf.setnchannels(1)
			wf.setsampwidth(2)
			wf.setframerate(16000)
			wf.writeframes(audio.tobytes())
		file.seek(0)
		recognizer = sr.Recognizer()
		with sr.AudioFile(file) as source:
			audio_ = recognizer.record(source)
		try:
			text = recognizer.recognize_google(audio_)
		except Exception as e:
			text = f'Error:\n{e}'
		audio = []
		text = re.sub(r'\bfull stop\b', '.', re.sub(r'\bFull Stop\b', '.', re.sub(r'\bfull Stop\b', '.', re.sub(r'\bFull stop\b', '.', re.sub(r'\bComma\b', ',', re.sub(r'\bcomma\b', ',', re.sub(r'\bColon\b', ':', re.sub(r'\bcolon\b', ':', re.sub(r'\bsemi colon\b', ';', re.sub(r'\bSemi Colon\b', ';', re.sub(r'\bsemi Colon\b', ';', re.sub(r'\bSemi colon\b', ';', re.sub(r'\bExclamation Mark\b', '!', re.sub(r'\bexclamation mark', '!', re.sub(r'\bExclamation mark\b', '!', re.sub(r'\bexclamation Mark\b', '!', re.sub(r'\bsemicolon\b', ';', re.sub(r'\bSemicolon\b', ';', re.sub(r'\bNew Line\b', '\n', re.sub(r'\bnew line\b', '\n', re.sub(r'\bNew line\b', '\n', re.sub(r'\bnew Line\b', '\n', re.sub(r'\bnewline\b', '\n', re.sub(r'\bNewline\b', '\n', text))))))))))))))))))))))))
		return text
	samplerate = 16000
	channels = 1
	dtype = np.int16
	dwin = easytk.win()
	dwin.title('Control')
	bframe = dwin.frame()
	bframe.pack(side = 'top', expand = True)
	dwin.button(master = bframe, text = 'Start Recording', command = lambda: threading.Thread(target = record, daemon = True).start()).grid(column = 0, row = 0, padx = 10, pady = 10, sticky = 'w')
	dwin.button(master = bframe, text = 'Stop Recording', command = lambda: [output.delete('1.0', 'end'), output.insert('end', stop())]).grid(column = 1, row = 0, padx = 10, pady = 10, sticky = 'e')
	oframe = dwin.frame()
	output = dwin.textbox(master = oframe)
	output.pack(fill = 'both', expand = True)
	dwin.button(master = oframe, text = 'Write to Active Editor', command = lambda: [state.active.type_.edit_separator(), state.active.type_.insert('insert', output.get('1.0', 'end-1c')), state.active.type_.edit_separator(), dwin.destroy()] if isinstance(state.active, editor.Editor) else utils.show('cannot write to current buffer')).pack(side = 'bottom', fill = 'x', expand = True)
	oframe.pack(side = 'bottom', fill = 'both', expand = True)
	dwin.sizablefalse()
