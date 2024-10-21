import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import threading
import speech_recognition as sr
from PyQt5.QtCore import QObject, pyqtSignal
import time

class ASR(QObject):
    is_recording = False
    recording = None
    transcribed = pyqtSignal(str)
    def __init__(self):
        super().__init__()

    def record_audio(self, fs=44100):
        self.is_recording = True
        self.recording = []

        def callback(indata, frames, time, status):
            if self.is_recording:
                self.recording.append(indata.copy())
            else:
                raise sd.CallbackStop

        with sd.InputStream(samplerate=fs, channels=1, callback=callback):
            while self.is_recording:
                sd.sleep(1000)

    def start_recording(self):
        if not self.is_recording:
            self.thread = threading.Thread(target=self.record_audio)
            self.thread.start()
            print("Recording started")

    def stop_recording(self, filename):
        self.is_recording = False
        if self.recording:
            recorded_data = np.concatenate(self.recording, axis=0).astype('int16')
            wav.write(filename, 44100, recorded_data)
            print(f"Recording stopped and saved as {filename}")
            self.transcribe_audio(filename)
    
    def transcribe_audio(self, filename):
        recognizer = sr.Recognizer()
        with sr.AudioFile(filename) as source:
            audio = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio, language='zh-CN')
            self.transcribed.emit(text)
            print("Transcription: " + text)
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print(f"Could not request results; {e}")

