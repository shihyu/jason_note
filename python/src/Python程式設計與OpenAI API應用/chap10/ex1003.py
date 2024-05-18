import tkinter as tk
from tkinter import ttk, font
from tkinter.scrolledtext import ScrolledText
import openai
import asyncio
import json
from async_tkinter_loop import async_handler, async_mainloop
from decouple import config

openai.api_key = config('OPENAI_API_KEY')
file_name = "d:/openai_book/chap10/hist_data.json"


def reset_hist():
    open(file_name, "w")


def get_hist():
    hist = []
    hist.append({"role": "system", "content": "你會說中文, 是聰明的助理"})

    try:
        with open(file_name) as f:
            pass
    except Exception as e:
        pass

    return hist


def save_hist(user_msg, reply_msg):
    pass


def load_hist():
    mess = ""
    try:
        pass
    except Exception as e:
        pass

    return mess


async def ask_gpt(user_msg):
    hist = get_hist()
    hist.append({"role": "user", "content": user_msg})
    try:
        responses = await asyncio.to_thread(
            openai.ChatCompletion.create,
            model="gpt-3.5-turbo",
            messages=hist,
            stream=True
        )

        for resp in responses:
            if 'content' in resp['choices'][0]['delta']:
                yield resp['choices'][0]['delta']['content']

    except Exception as e:
        yield str(e)


async def on_submit():
    user_msg = text.get('1.0', tk.END)

    reply_list = []
    result_text.config(state=tk.NORMAL)
    result_text.delete(1.0, tk.END)

    async for resp in ask_gpt(user_msg):
        result_text.insert(tk.END, resp)
        reply_list.append(resp)
        root.update()

    result_text.config(state=tk.DISABLED)

    reply_msg = "".join(reply_list)
    save_hist(user_msg, reply_msg)


def on_clear():
    text.delete('1.0', tk.END)
    result_text.config(state=tk.NORMAL)
    result_text.delete(1.0, tk.END)
    result_text.config(state=tk.DISABLED)


def on_new():
    on_clear()
    reset_hist()


async def on_load():
    on_clear()
    mess = await asyncio.to_thread(load_hist)
    result_text.config(state=tk.NORMAL)
    result_text.insert(1.0, mess)
    result_text.config(state=tk.DISABLED)

# 主視窗
root = tk.Tk()
root.title("OpenAI API 應用程式")

# 視窗位置置中
window_width = 900
window_height = 600
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
center_x = int(screen_width/2-window_width/2)
center_y = int(screen_height/2-window_height/2)
root.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")

# 設定 ttk 控件字型
style = ttk.Style()
style.configure('.', font=('微軟正黑體', 12))

# 設定 tk 控件字型
myfont = font.Font(family="微軟正黑體", size=12)

# Label
lbl_prompt = ttk.Label(root, text="輸入提示 :")
lbl_prompt.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)

# 提示輸入框
text = ScrolledText(root, height=5, width=100, font=myfont)
text.grid(row=5, column=0, padx=10, pady=10, sticky=tk.W+tk.E)

frame = ttk.Frame(root)
frame.grid(row=10, column=0)

# 提交按鈕
btn_submit = ttk.Button(frame, text="提交", width=15,
                        command=async_handler(on_submit))
btn_submit.pack(side='left', padx=10)

# 清除按鈕
btn_clear = ttk.Button(frame, text="清除", width=15, command=on_clear)
btn_clear.pack(side='left', padx=10)

# 新對話
btn_new = ttk.Button(frame, text="新對話", width=15, command=on_new)
btn_new.pack(side='left', padx=10)

# 載入對話歷史
btn_load = ttk.Button(frame, text="載入對話歷史", width=20,
                      command=async_handler(on_load))
btn_load.pack(side='left', padx=10)

# 添加完成顯示文本框
result_text = ScrolledText(root, wrap=tk.WORD, height=20, font=myfont)
result_text.config(state=tk.DISABLED)
result_text.grid(row=99, column=0, pady=10, padx=10, sticky=tk.E+tk.W)

root.rowconfigure(99, weight=1)
root.columnconfigure(0, weight=1)

async_mainloop(root)
