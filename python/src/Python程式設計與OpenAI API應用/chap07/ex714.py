import tkinter as tk
from tkinter import ttk

root = tk.Tk()
root.title("tkinter demo")
root.geometry('640x600+300+100')

# Label (0,0)
lbl_title = ttk.Label(
    root,
    text="Please take the survey",
    font=('Arial 16 bold'),
    background='blue',
    foreground='#FFFFFF'
)
lbl_title.grid(row=0, column=0, columnspan=2, padx=10)

# Label (1,0)
lbl_name = ttk.Label(root, text="What is your name?")
lbl_name.grid(row=1, column=0, pady=10, sticky=tk.E)

# Entry (1,1)
et_name = ttk.Entry(root)
et_name.grid(row=1, column=1, sticky=tk.W+tk.E, padx=10)

# Label (2,0)
lbl_num = ttk.Label(root, text='How many apples do you eat per day?')
lbl_num.grid(row=2, column=0, sticky=tk.E, pady=10, padx=10)

# Spinbox (2,1)
sp_num = ttk.Spinbox(root, from_=0, to=10, increment=1)
sp_num.set(0)
sp_num.grid(row=2, column=1, sticky=(tk.W+tk.E), padx=10)

# Label (3,0)
lbl_color = ttk.Label(root, text='What is the best color for a apple?')
lbl_color.grid(row=3, column=0, sticky=tk.E, pady=10)

# Listbox (3,1)
list_color = tk.Listbox(root, height=4)
color_choices = ('Any', 'Red', 'Green', 'Yellow')
color_var = tk.Variable(value=color_choices)
list_color = tk.Listbox(root, height=4,
                        listvariable=color_var,
                        selectmode=tk.EXTENDED)
list_color.grid(row=3, column=1, sticky=tk.W+tk.E, padx=10)


# LabelFrame (4,0)
frame_radio = ttk.LabelFrame(root, text='Do you eat Rome Apple?')
frame_radio.grid(row=4, column=0, sticky=tk.E, pady=10, padx=10)

# Radiobutton
var = tk.IntVar()
radio1 = ttk.Radiobutton(frame_radio, variable=var, value=1, text='Yes')
radio1.pack(side='left')
radio2 = ttk.Radiobutton(frame_radio, variable=var, value=2, text='No')
radio2.pack(side='left')
var.set(1)


# LabelFrame (4,1)
frame_check = ttk.LabelFrame(root, text='Choose your favorite apple type:')
frame_check.grid(row=4, column=1, sticky=tk.W, padx=10, pady=10)

# Checkbutton
types = {0: "Rome Apple", 1: "Gala Apple", 2: "Fuji Apple"}
var_check = {}
for i in range(len(types)):
    var_check[i] = tk.BooleanVar()
    ttk.Checkbutton(
        frame_check, variable=var_check[i], text=types[i]).pack(side='left')

# Label (7,0)
lbl_remark = ttk.Label(root, text='Write a remark about apples')
lbl_remark.grid(row=7, column=0, columnspan=2, sticky=tk.W, padx=10)

# Text (8, 0)
txt_remark = tk.Text(root, height=3)
txt_remark.grid(row=8, column=0, columnspan=2, sticky=tk.W+tk.E, padx=10)

# Button (99, 0)
btn_submit = ttk.Button(root, text='Submit Survey')
btn_submit.grid(row=99, column=0, columnspan=2,
                sticky=tk.E+tk.W, pady=10, padx=10)

# Label (100,0)
lbl_output = ttk.Label(root, text='result:', anchor='w',
                       justify='left', background='light blue')
lbl_output.grid(row=100, columnspan=2, sticky='nswe', pady=10, padx=10)


def on_submit():
    pass


# Button command
btn_submit.config(command=on_submit)

# col=1 縮放比例
root.columnconfigure(1, weight=1)

# row=100 縮放比例
root.rowconfigure(100, weight=1)

root.mainloop()
