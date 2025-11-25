from groq import Groq

api_key = "<API-KEY>"
client = Groq(api_key=api_key)

completion = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{
        "role": "user",
        "content": "請使用繁體中文說明Groq API是什麼?"
        }],
    temperature=1,
    max_completion_tokens=1024,
    top_p=1,
    stream=False,
    stop=None,
)
# 取出 content 的回應內容
content = completion.choices[0].message.content
print(content)
