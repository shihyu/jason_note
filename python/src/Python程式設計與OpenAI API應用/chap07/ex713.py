import tkinter as tk
from tkinter import ttk

root = tk.Tk()
root.title("tkinter demo")
root.geometry('640x500+300+100')

# Label
lbl_title = ttk.Label(
    root,
    text="Please take the survey",
    font=('Arial 16 bold'),
    background='blue',
    foreground='#FFFFFF'
)
lbl_title.pack()

# Frame
frame1 = ttk.Frame(root)
frame1.pack(padx=10, pady=10)

# Label
lbl_name = ttk.Label(frame1, text="What is your name?")
lbl_name.pack(side='left')

# Entry
et_name = ttk.Entry(frame1)
et_name.pack(side='left', padx=10)

# Frame
frame2 = ttk.Frame(root)
frame2.pack(padx=10, pady=10)

# Label
lbl_num = ttk.Label(frame2, text='How many apples do you eat per day?')
lbl_num.pack(side='left')

# Spinbox
sp_num = ttk.Spinbox(frame2, from_=0, to=10, increment=1)
sp_num.set(0)
sp_num.pack(side='left', padx=10)

# Frame
frame3 = ttk.Frame(root)
frame3.pack(padx=10, pady=10)

# Label
lbl_color = ttk.Label(frame3, text='What is the best color for a apple?')
lbl_color.pack(side='left')

# Listbox
list_color = tk.Listbox(frame3, height=4)
color_choices = ('Any', 'Red', 'Green', 'Yellow')
color_var = tk.Variable(value=color_choices)
list_color = tk.Listbox(frame3, height=4,
                        listvariable=color_var,
                        selectmode=tk.EXTENDED)
list_color.pack(side='left', padx=10)

# Frame
frame4 = ttk.Frame(root)
frame4.pack(padx=10, pady=10)

# LabelFrame
frame_radio = ttk.LabelFrame(frame4, text='Do you like Rome Apple?')
frame_radio.pack(side='left')

# Radiobutton
var = tk.IntVar()
radio1 = ttk.Radiobutton(frame_radio, variable=var, value=1, text='Yes')
radio1.pack(side='left')
radio2 = ttk.Radiobutton(frame_radio, variable=var, value=2, text='No')
radio2.pack(side='left')
var.set(1)

# LabelFrame
frame_check = ttk.LabelFrame(frame4, text='Choose your favorite apple type:')
frame_check.pack(side='left', padx=10)

# Checkbutton
types = {0: "Rome Apple", 1: "Gala Apple", 2: "Fuji Apple"}
var_check = {}
for i in range(len(types)):
    var_check[i] = tk.BooleanVar()
    ttk.Checkbutton(
        frame_check, variable=var_check[i], text=types[i]).pack(side='left')

# Label
lbl_remark = ttk.Label(root, text='Write a remark about apples')
lbl_remark.pack()

# Text
txt_remark = tk.Text(root, height=3)
txt_remark.pack(padx=10, pady=10)

# Button
btn_submit = tk.Button(root, text='Submit Survey')
btn_submit.pack(pady=10)

# Label
lbl_output = ttk.Label(root, text='result:', anchor='w',
                       justify='left', background='light blue')
lbl_output.pack()


def on_submit():
    pass


# Button command
btn_submit.config(command=on_submit)

root.mainloop()
