import google.generativeai as genai

api_key = "<API-KEY>"
genai.configure(api_key=api_key)

model = genai.GenerativeModel(model_name="gemini-2.0-flash") 

try:
    prompt = "請問什麼是Google Gemini?"
    response = model.generate_content(prompt)
    reply_msg = response.text
    print(reply_msg)
except Exception as e:
    print("錯誤：", e)
    