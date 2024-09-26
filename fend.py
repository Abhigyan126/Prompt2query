import tkinter as tk

root = tk.Tk()
height = root.winfo_screenheight() - 50
width = root.winfo_screenwidth() - 50

root.geometry(f"{width}x{height}")

# Left frame
left_frame = tk.Frame(root, bg="lightgrey", width=400)
left_frame.pack(side="left", fill="y")

# Right frame
right_frame = tk.Frame(root, bg="grey")
right_frame.pack(side="right", fill="both", expand=True)

# Canvas for scrolling
canvas = tk.Canvas(right_frame, bg="white", height=height * 0.90)
canvas.pack(side="top", fill="both", expand=True)

# Scrollbar
scrollbar = tk.Scrollbar(right_frame, orient="vertical", command=canvas.yview)
scrollbar.pack(side="right", fill="y")

# Configure the canvas and scrollbar
canvas.configure(yscrollcommand=scrollbar.set)
canvas.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

# Frame inside the canvas
top_frame = tk.Frame(canvas, bg="white")
canvas.create_window((0, 0), window=top_frame, anchor="nw")

# Input frame
input_frame = tk.Frame(right_frame, bg="white", height=height*0.1)
input_frame.pack(side="bottom", fill="x", padx=10, pady=10)

# Text area
input_text_box = tk.Text(input_frame, height=3, width=120)
input_text_box.pack(side="left", padx=10, pady=5)
input_text_box.config(state="normal")

# Display top frame
def display_input():
    user_input = input_text_box.get("1.0", tk.END).strip()
    if user_input:
        # Create a new Label inside the top_frame
        output_label = tk.Label(top_frame, text=user_input, bg="white", anchor="w", pady=10)
        output_label.pack(pady=5, fill="x")
        input_text_box.delete("1.0", tk.END)

    # Update the canvas scroll region after adding a new label
    canvas.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))

# Button
send_button = tk.Button(input_frame, text="Enter", width=10, foreground="green", command=display_input)
send_button.pack(side="right", padx=10, pady=5)

root.mainloop()
