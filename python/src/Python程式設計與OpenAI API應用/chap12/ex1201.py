import openai
from decouple import config

openai.api_key = config("OPENAI_API_KEY")

audio_file = open("d:/openai_book/chap12/audio.mp3", "rb")
transcript = openai.Audio.transcribe("whisper-1", audio_file)

message_text=transcript["text"]
print(message_text)






