import pocketsphinx
import whisper

def record_voice():
    chunk = 1024
    FORMAT = pyaudio.paInt16
    channels = 1
    rate = 44100
    y = 100

    audio = pyaudio.PyAudio()