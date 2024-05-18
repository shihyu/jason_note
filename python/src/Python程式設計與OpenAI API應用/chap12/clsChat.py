import openai
import json
import asyncio


class cls_chatgpt():
    def __init__(self, json_file):
        self.json_file = json_file
        self.recording = False

    async def ask_gpt(self, user_msg):
        self.hist = self.get_hist()
        self.hist.append({"role": "user", "content": user_msg})
        try:
            responses = await asyncio.to_thread(
                openai.ChatCompletion.create,
                model="gpt-3.5-turbo",
                messages=self.hist,
                stream=True
            )

            for resp in responses:
                if 'content' in resp['choices'][0]['delta']:
                    yield resp['choices'][0]['delta']['content']

        except Exception as e:
            yield str(e)

    def reset_hist(self):
        open(self.json_file, "w")

    def get_hist(self):
        self.hist = []
        self.hist.append({"role": "system", "content": "你會說中文, 是聰明的助理"})
        try:
            pass
        except Exception as e:
            pass

        return self.hist

    def save_hist(self, user_msg, reply_msg):
        pass

    def load_hist(self):
        self.mess = ""
        try:
            pass
        except Exception as e:
            pass

        return self.mess
