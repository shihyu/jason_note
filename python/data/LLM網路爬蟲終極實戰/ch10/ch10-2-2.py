from openai import OpenAI

api_key = "<API-KEY>"
reply_msg = ""
client = OpenAI(api_key=api_key)

while True:
    input_msg = input("你: ")
    response = client.chat.completions.create(
      model = "gpt-4o-mini",      
      messages = [
            {"role": "system", "content": "你是一位客服機器人"},
            {"role": "assistant", "content": reply_msg},
            {"role": "user", "content": input_msg}
                 ]
    )
    reply_msg = response.choices[0].message.content
    print(reply_msg)
    