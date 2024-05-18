import openai
from decouple import config

openai.api_key=config('OPENAI_API_KEY')

response = openai.Image.create(
  prompt="Frogs and butterflies playing in the forest.",
  n=1,
  size="512x512"
)

image_url = response['data'][0]['url']
print(image_url)

