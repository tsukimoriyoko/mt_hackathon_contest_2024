import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import speech_recognition as sr
# from core.conf import settings

def record_audio(duration, fs=44100):
    print("Recording...")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()
    print("Recording complete")
    return recording

def save_audio(filename, recording, fs):
    wav.write(filename, fs, recording)
    print(f"Audio saved as {filename}")

def transcribe_audio(filename):
    recognizer = sr.Recognizer()
    with sr.AudioFile(filename) as source:
        audio = recognizer.record(source)
    try:
        text = recognizer.recognize_google(audio, language='zh-CN')
        print("Transcription: " + text)
        return text
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print(f"Could not request results; {e}")

# # 录制音频
# duration = 5  # 录制时长，单位秒
# recording = record_audio(duration)
# save_audio("D:\\output.wav", recording, 44100)

# # 进行语音识别
# transcribe_audio("D:\\output.wav")
