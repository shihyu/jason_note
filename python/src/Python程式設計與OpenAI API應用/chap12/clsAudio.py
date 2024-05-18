import openai
from io import BytesIO
from gtts import gTTS
import pygame
import pyaudio
import wave
import asyncio


class cls_audio:
    def __init__(self, record_file):
        self.record_file = record_file
        self.mess = ""
        self.recording = False

    def set_recording(self, flag):
        self.recording = flag

    async def transcribe_audio(self):
        try:
            pass
        except Exception as e:
            yield str(e)

    def say(self, mess):
        pass

    def record_audio(self):
        self.chunk = 1024
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 44100

        p = pyaudio.PyAudio()

        stream = p.open(format=self.format,
                        channels=self.channels,
                        rate=self.rate,
                        input=True,
                        frames_per_buffer=self.chunk)

        frames = []

        while self.recording:
            data = stream.read(self.chunk)
            frames.append(data)

        stream.stop_stream()
        stream.close()
        p.terminate()

        try:
            wf = wave.open(self.record_file, 'wb')
            wf.setnchannels(self.channels)
            wf.setsampwidth(p.get_sample_size(self.format))
            wf.setframerate(self.rate)
            wf.writeframes(b''.join(frames))
            wf.close()
        except Exception as e:
            print(str(e))
