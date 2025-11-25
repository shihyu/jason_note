from scrapegraphai.graphs import SpeechGraph
import os

# 設定 OpenAI API 金鑰
os.environ["OPENAI_API_KEY"] = "<OPENAI_API_KEY>"
# 輸出 MP3 檔案的路徑
FILE_NAME = "fchart_summary.mp3"
curr_dir = os.path.dirname(os.path.realpath(__file__))
output_path = os.path.join(curr_dir, FILE_NAME)

graph_config = {
    "llm": {
        "api_key": os.getenv("OPENAI_API_KEY"),
        "model": "openai/gpt-4o-mini",  
        "temperature": 0.7,
    },
    # Text-to-speech (TTS) 模型
    "tts_model": {
        "api_key": os.getenv("OPENAI_API_KEY"),
        "model": "tts-1",
        "voice": "alloy",  # 聲音樣式
    },
    "output_path": output_path,
}

speech_graph = SpeechGraph(
    prompt="""
    請摘要這個 fChart 教學工具網站的內容,
    然後轉為中文的語音講解：
    - 提取重點概念
    - 加入講解說明
    - 適合語音播放的格式
    """,
    source="https://fchart.github.io/",
    config=graph_config,
)

result = speech_graph.run()
print(result)
