import tkinter as tk
from tkinter import ttk, font
from tkinter.scrolledtext import ScrolledText
import openai
import asyncio
from async_tkinter_loop import async_handler, async_mainloop
from decouple import config
from clsAudio import cls_audio
from clsChat import cls_chatgpt

openai.api_key=config('OPENAI_API_KEY')

class AudioRecorderApp:
    def __init__(self, root):
        self.record_file="d:/openai_book/chap12/record.wav"
        self.audio=cls_audio(record_file=self.record_file)
        self.audio.set_recording(False)               
        self.json_file="d:/openai_book/chap12/hist_data.json"
        self.chat=cls_chatgpt(json_file=self.json_file)

        self.root = root
        self.root.title("Audio Recorder")
        self.width=900
        self.height=600
        self.window_center()
        self.window_font()

        self.recording=False       
        
        self.window_layout()
    
    def window_layout(self):
        # 錄音
        self.record_button = ttk.Button(root, text="錄音",
                                       command=async_handler(self.toggle_recording))
        self.record_button.pack(padx=10, pady=10)
        
        self.status_label = ttk.Label(root, text="", background="light yellow")
        self.status_label.pack(padx=10, pady=10)
        
        # 提示輸入
        self.user_text = ScrolledText(root, width=90, height=3, font=self.myfont)        
        self.user_text.pack(padx=10, pady=10)

        self.frame=ttk.Frame(root)
        self.frame.pack(padx=10, pady=10)

        # 提交按鈕
        self.btn_submit = ttk.Button(self.frame, text="提交", width=15, command=async_handler(self.on_submit))
        self.btn_submit.pack(side='left', padx=10)

        # 新對話按鈕
        self.btn_new = ttk.Button(self.frame, text="新對話", width=15,command=self.on_new)
        self.btn_new.pack(side='left', padx=10)

        # 載入對話歷史按鈕
        self.btn_load = ttk.Button(self.frame, text="載入對話歷史", width=15,command=async_handler(self.on_load))
        self.btn_load.pack(side='left', padx=10)

        self.ck_var=tk.IntVar()
        self.ck_say=ttk.Checkbutton(self.frame, text="語音輸出", variable=self.ck_var)        
        self.ck_say.pack(side='left', padx=10)

        # 測試語音
        self.btn_test = ttk.Button(self.frame, text="測試語音", width=15,command=self.on_test)
        self.btn_test.pack(side='left', padx=10)

         # 提示輸入框
        self.result_text = ScrolledText(root, width=90, height=15, font=self.myfont)        
        self.result_text.pack(padx=10, pady=10)
    
    def window_font(self):
        # 設定 ttk 控件字型
        self.style=ttk.Style()
        self.style.configure('.', font=('微軟正黑體', 12))

        # 設定 tk 控件字型
        self.myfont=font.Font(family="微軟正黑體", size=12)
    
    def window_center(self):
        # 視窗位置置中
        self.root.title("Audio Recorder")        
        screen_width=self.root.winfo_screenwidth()
        screen_height=self.root.winfo_screenheight()
        center_x=int(screen_width/2-self.width/2)
        center_y=int(screen_height/2-self.height/2)
        self.root.geometry(f"{self.width}x{self.height}+{center_x}+{center_y}")
        
    async def toggle_recording(self):
        if not self.recording:
            self.recording=True
            self.audio.set_recording(True)
            self.record_button.config(text="停止錄音")
            self.status_label.config(text="錄音中 ...")
            await asyncio.to_thread(self.audio.record_audio)            
            await self.on_transcribe()
        else:
            self.recording=False
            self.audio.set_recording(False)
            self.record_button.config(text="錄音")
            self.status_label.config(text="錄音完成") 
    
    async def on_transcribe(self):
        self.status_label["text"]="翻譯中..."
        self.user_text.delete(1.0, tk.END)    
        async for resp in self.audio.transcribe_audio():
            self.user_text.insert(tk.END, resp)            
            self.root.update()
        self.status_label["text"]=""

        #await self.on_submit()

    async def on_submit(self):      
        self.user_msg = self.user_text.get('1.0', tk.END)

        self.reply_list=[]
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END) 
        self.msg_list=[]
        self.cnt=0
        async for resp in self.chat.ask_gpt(self.user_msg):
            self.cnt += 1            
            self.result_text.insert(tk.END, resp)
            self.reply_list.append(resp)
            root.update()

            self.msg_list.append(resp)

            if self.ck_var.get()==1:
                if (resp=="，" or resp=="。" or resp=="：" 
                    or resp=="。\n\n" or resp=="？" or resp=="!"
                    or resp==":\n\n"):                
                    self.msg=self.msg_list[0:self.cnt]
                    self.msg2="".join(self.msg)
                    await asyncio.to_thread(self.audio.say,self.msg2)
                    self.msg_list=self.msg_list[self.cnt:]
                    self.cnt=0
        
        #print(self.reply_list)
        self.result_text.config(state=tk.DISABLED)
        self.reply_msg="".join(self.reply_list)
        self.chat.save_hist(self.user_msg, self.reply_msg)
    
    def on_test(self):
        self.text="你好，這是測試。"
        self.audio.say(self.text)
    
    def on_clear(self):
        self.user_text.delete('1.0', tk.END)
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        self.result_text.config(state=tk.DISABLED)

    def on_new(self):
        self.on_clear()
        self.chat.reset_hist()
        
    async def on_load(self):
        self.on_clear()
        self.mess=await asyncio.to_thread(self.chat.load_hist)
        self.result_text.config(state=tk.NORMAL)
        self.result_text.insert(1.0, self.mess)
        self.result_text.config(state=tk.DISABLED)    

if __name__ == "__main__":
    root = tk.Tk()
    app = AudioRecorderApp(root)
    async_mainloop(root)
