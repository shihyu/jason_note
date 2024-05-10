import openai
from decouple import config
import json

openai.api_key = config('OPENAI_API_KEY')
file_name = "chap09/hist_data.json"


def reset_hist():
    open(file_name, "w")


def get_hist():
    hist = []
    hist.append({"role": "system", "content": "你會說中文, 是聰明的助理"})

    try:
        pass
    except Exception as e:
        pass

    return hist


def save_hist(user_msg, reply_msg):
    pass


def ask_gpt(user_msg):
    hist = get_hist()
    hist.append({"role": "user", "content": user_msg})

    try:
        pass
    except Exception as e:
        print(f"Error:{e.error.messages}")


def main():
    reset_hist()
    print("具對話記錄串流聊天程式, 輸入 'quit' 離開")

    while True:
        user_msg = input("User: ")

        if user_msg.lower() == "quit":
            break

        reply_list = []
        print("AI: ", end="")
        for resp in ask_gpt(user_msg):
            print(resp, end="")
            reply_list.append(resp)

        print("")

        reply_msg = "".join(reply_list)
        save_hist(user_msg, reply_msg)

    print("\n對話歷史如下：")
    hist = get_hist()[1:]
    print(hist)


if __name__ == "__main__":
    main()
