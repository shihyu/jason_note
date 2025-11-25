import google.generativeai as genai

api_key = "<API-KEY>"
genai.configure(api_key=api_key)

model = genai.GenerativeModel(model_name="gemini-2.0-flash") 

chat = model.start_chat(history=[])
prompt1 = "請用50個字說明什麼是Python?"
response1 = chat.send_message(prompt1)
print("AI:", response1.text)
prompt2 = "請用50個字說明為什麼需要寫Python程式?"
response2 = chat.send_message(prompt2)
print("AI:", response2.text)

print("對話歷史======")
for message in chat.history:
    print(message.role, ":", message.parts[0].text)

    