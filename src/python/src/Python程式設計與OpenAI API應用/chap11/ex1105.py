import openai
import tkinter as tk
from tkinter import ttk, font
from tkinter.scrolledtext import ScrolledText
from decouple import config
import asyncio
from async_tkinter_loop import async_handler, async_mainloop
import requests
from PIL import Image, ImageTk
from io import BytesIO
from time import perf_counter
from os.path import exists


openai.api_key = config('OPENAI_API_KEY')

file_src = "d:/openai_book/chap11/image.png"
file_dst = "d:/openai_book/chap11/image2.png"


def save_image(image_url, file_name):
    pass


def openai_image(user_prompt):
    response = openai.Image.create(
        prompt=user_prompt,
        n=1,
        size="512x512"
    )
    image_url = response['data'][0]['url']
    print(image_url)
    save_image(image_url, file_src)


def openai_variation(file_src):
    response = openai.Image.create_variation(
        image=open(file_src, "rb"),
        n=1,
        size="512x512"
    )
    image_url = response['data'][0]['url']
    save_image(image_url, file_dst)


async def on_submit():
    pass


async def on_variation():
    start = perf_counter()
    print(file_src)
    if not exists(file_src):
        lbl_mess["text"] = "圖像來源檔不存在."
        return
    else:
        lbl_mess["text"] = "圖像變形中..."

    await asyncio.to_thread(
        openai_variation,
        file_src)

    lbl_mess["text"] = "圖像變形完成."
    show_image(file_dst, pos=2)

    elapsed = perf_counter() - start
    print(f"elapsed: {elapsed:.2f} sec")


def on_clear():
    text.delete('1.0', tk.END)
    lbl_mess["text"] = ""
    lbl_image["image"] = ""
    lbl_image2["image"] = ""


def show_image(file_name, pos):
    pass


# 主視窗
root = tk.Tk()
root.title("OpenAI API 應用程式")

# 視窗位置置中
window_width = 900
window_height = 550
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
lbl_prompt.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky=tk.W)

# 提示輸入框
text = ScrolledText(root, height=3, font=myfont)
text.grid(row=5, column=0, columnspan=2, padx=10, pady=10, sticky=tk.W+tk.E)

frame = ttk.Frame(root)
frame.grid(row=10, column=0, columnspan=2)

# 提交按鈕
btn_submit = ttk.Button(frame, text="提交", width=15,
                        command=async_handler(on_submit))
btn_submit.pack(side='left', padx=10)

# 清除按鈕
btn_clear = ttk.Button(frame, text="清除", width=15, command=on_clear)
btn_clear.pack(side='left', padx=10)

# 圖像變形鈕
btn_var = ttk.Button(frame, text="圖像變形", width=20,
                     command=async_handler(on_variation))
btn_var.pack(side='left', padx=10)

# 訊息
lbl_mess = ttk.Label(root, text="訊息", background='light yellow')
lbl_mess.grid(row=20, column=0, columnspan=2,
              padx=10, pady=10, sticky=tk.E+tk.W)

# 顯示圖像_1
lbl_image = ttk.Label(root, width=32, background='snow3')
lbl_image.grid(row=99, column=0, padx=10, pady=10, sticky=tk.S+tk.N)

# 顯示圖像_2
lbl_image2 = ttk.Label(root, width=32, background='snow3')
lbl_image2.grid(row=99, column=1, padx=10, pady=10, sticky=tk.S+tk.N)

root.rowconfigure(99, weight=1)
root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=1)

async_mainloop(root)
