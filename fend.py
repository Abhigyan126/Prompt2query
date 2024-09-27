import tkinter as tk
from tkinter import PhotoImage, Entry, Button, Text, Scrollbar, Frame

root = tk.Tk()
height_ = root.winfo_screenheight() - 100
width_ = root.winfo_screenwidth() - 50

root.geometry(f"{width_}x{height_}")
root.title("Prompt2Query")

# icon
icon = PhotoImage(file='logo.png')
root.iconphoto(True, icon)

# icon-up
up = PhotoImage(file='up-arrow.png')
resized_up = up.subsample(20, 20)

# icon-attachment
attach = PhotoImage(file='attachment.png')
resized_attach = attach.subsample(20, 20)

# Create the left frame
left_frame = tk.Frame(root, bg="lightgrey", width=width_ // 2 - 250)
left_frame.pack(side="left", fill="y")

# Create the output text box with a fixed height and scrollbar
output_text = tk.Text(left_frame, bg="white", font=("Arial", 14), wrap="word", height=20, width=50)
output_text.pack(side="left", fill="both", expand=True)

# Add a vertical scrollbar to the text box
scrollbar = tk.Scrollbar(left_frame, command=output_text.yview)
scrollbar.pack(side="right", fill="y")
output_text.config(yscrollcommand=scrollbar.set)

# Right frame
right_frame = tk.Frame(root, bg="grey")
right_frame.pack(side="right", fill="both", expand=True)

# Top right frame (90% of height)
top_right_frame = tk.Frame(right_frame, bg="red", height=height_*0.90)
top_right_frame.pack(side="top", fill="both", expand=True)

# Frame for the Text widget and scrollbar
output_frame = Frame(top_right_frame)
output_frame.pack(fill="both", expand=True)

# Text widget for displaying output (non-editable)
output_text = Text(output_frame, bg="white", font=("Ariel", 14), wrap='word', state='disabled')
output_text.pack(side="left", fill="both", expand=True)

# Scrollbar for the Text widget
scrollbar = Scrollbar(output_frame, command=output_text.yview)
scrollbar.pack(side="right", fill="y")

# Configure the Text widget to use the scrollbar
output_text.config(yscrollcommand=scrollbar.set)

# Function to update the Text widget
def update_text(text):
    output_text.config(state='normal')
    output_text.insert(tk.END, text + "\n")
    output_text.config(state='disabled')
    output_text.see(tk.END)

# Bottom right frame (height same as buttons)
bottom_right_frame = tk.Frame(right_frame, bg="blue")
bottom_right_frame.pack(side="bottom", fill="x")  # Fill in the x direction only

# Frame to hold Entry and Buttons in bottom_right_frame
input_frame = tk.Frame(bottom_right_frame, bg="blue")
input_frame.pack(side="top", pady=10)  # Pack input_frame to keep it at the top

# Entry widget
entry = Entry(input_frame, font=("Ariel", 20), width=50)
entry.grid(row=0, column=1)

# Attachment button
button = Button(input_frame, image=resized_attach, width=30, height=28, command=lambda: print("Open CSV"))
button.grid(row=0, column=0)

# Function to handle displaying text
def submit_text():
    text = entry.get()
    if text: 
        update_text(text)
        entry.delete(0, tk.END)

# Submit button
submit_button = Button(input_frame, image=resized_up, width=30, height=28, command=submit_text)
submit_button.grid(row=0, column=2)

# Adjust the bottom_right_frame to have the same height as the input_frame
bottom_right_frame.update_idletasks()
bottom_right_frame_height = input_frame.winfo_height()
bottom_right_frame.config(height=bottom_right_frame_height)


print(width_, height_)
root.mainloop()
