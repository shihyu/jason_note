import asyncio
import tkinter as tk
from tkinter import ttk
from async_tkinter_loop import async_handler, async_mainloop

async def counter():
    i = 0
    while True:
        i += 1
        if i==11:
            break
        label.config(text=str(i))
        await asyncio.sleep(1.0)


root = tk.Tk()
root.title("async tkinter demo")
root.geometry('320x200+100+100')

label = ttk.Label(root)
label.pack(padx=10, pady=10)

btn = tk.Button(root, text="Start", width=10,command=async_handler(counter))
btn.pack(padx=10, pady=10)

async_mainloop(root)
