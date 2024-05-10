import openai
from decouple import config

openai.api_key=config('OPENAI_API_KEY')
print("請稍待 ...")

completion = openai.ChatCompletion.create(
  model="gpt-3.5-turbo",
  messages=[
    {"role": "system", "content": "你會說中文, 是聰明的助理"},
    {"role": "user", "content": "台北那裡最好玩?"}
  ]
)

response=completion.choices[0].message.content
print(response)

