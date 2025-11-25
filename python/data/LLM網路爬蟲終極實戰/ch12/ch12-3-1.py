from scrapegraphai.graphs import SpeechGraph
import os

# 設定 OpenAI API 金鑰
os.environ["OPENAI_API_KEY"] = "<OPENAI_API_KEY>"
# 輸出 MP3 檔案的路徑
FILE_NAME = "news_summary.mp3"
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
    prompt="Make a detailed audio summary of the news titles.",
    source="https://news.ycombinator.com/",
    config=graph_config,
)

result = speech_graph.run()
print(result)
