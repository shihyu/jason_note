import google.generativeai as genai

api_key = "<API-KEY>"
genai.configure(api_key=api_key)

# 查詢可用的模型
print("可用的模型：")
for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"- {model.name}")

    