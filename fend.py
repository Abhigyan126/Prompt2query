import tkinter as tk
from tkinter import PhotoImage, Entry, Button, Frame, Scrollbar
from llm_pandas import LLMHandler

class Prompt2QueryApp:
    def __init__(self, root):
        self.root = root
        self.setup_window()
        self.load_icons()
        self.create_layout()
        self.lh = LLMHandler()

    def setup_window(self):
        height_ = self.root.winfo_screenheight() - 100
        width_ = self.root.winfo_screenwidth() - 50
        self.root.geometry(f"{width_}x{height_}")
        self.root.title("Prompt2Query")

    def load_icons(self):
        # Load and set the window icon
        self.icon = PhotoImage(file='logo.png')
        self.root.iconphoto(True, self.icon)

        # Load icons for buttons
        self.icon_up = PhotoImage(file='up-arrow.png').subsample(20, 20)
        self.icon_attach = PhotoImage(file='attachment.png').subsample(20, 20)

    def create_layout(self):
        self.create_left_frame()
        self.create_right_frame()

    def create_left_frame(self):
        # Left frame for text output and scrollbar
        self.left_frame = Frame(self.root, bg="white", width=self.root.winfo_width() // 2 - 250)
        self.left_frame.pack(side="left", fill="y")

        self.output_text = tk.Text(self.left_frame, bg="black", font=("Arial", 14), wrap="word", height=20, width=50)
        self.output_text.pack(side="left", fill="both", expand=True)

        # Add scrollbar to text widget
        self.scrollbar = Scrollbar(self.left_frame, command=self.output_text.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.output_text.config(yscrollcommand=self.scrollbar.set)

    def create_right_frame(self):
        # Right frame for input and dynamic label display
        self.right_frame = Frame(self.root, bg="white")
        self.right_frame.pack(side="right", fill="both", expand=True)

        self.create_top_right_frame()
        self.create_bottom_right_frame()

    def create_top_right_frame(self):
        # Top right frame with scrolling label container
        self.top_right_frame = Frame(self.right_frame, bg="white")
        self.top_right_frame.pack(side="top", fill="both", expand=True)

        self.label_frame = Frame(self.top_right_frame)
        self.label_frame.pack(side="left", fill="both", expand=True)

        # Create canvas for scrolling labels
        self.canvas = tk.Canvas(self.label_frame)
        self.canvas.pack(side="left", fill="both", expand=True)

        # Scrollbar for the label container
        self.label_scrollbar = Scrollbar(self.label_frame, orient="vertical", command=self.canvas.yview)
        self.label_scrollbar.pack(side="right", fill="y")
        self.canvas.config(yscrollcommand=self.label_scrollbar.set)

        # Container frame inside the canvas
        self.label_container = Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.label_container, anchor="nw")

        # Configure canvas scroll area
        self.label_container.bind("<Configure>", self.on_frame_configure)

        # Mouse wheel scrolling
        self.canvas.bind_all("<MouseWheel>", self.scroll)

    def create_bottom_right_frame(self):
        # Bottom right frame for input and buttons
        self.bottom_right_frame = Frame(self.right_frame, bg="white")
        self.bottom_right_frame.pack(side="bottom", fill="x")

        self.input_frame = Frame(self.bottom_right_frame, bg="white")
        self.input_frame.pack(side="top", pady=10)

        # Entry widget for input
        self.entry = Entry(self.input_frame, font=("Arial", 20), width=50, bg="black")
        self.entry.grid(row=0, column=1)

        # Attachment button
        self.attach_button = Button(self.input_frame, image=self.icon_attach, width=30, height=28, command=self.attach_file)
        self.attach_button.grid(row=0, column=0)

        # Submit button for adding labels
        self.submit_button = Button(self.input_frame, image=self.icon_up, width=30, height=28, command=self.submit_text)
        self.submit_button.grid(row=0, column=2)

    def on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def scroll(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def submit_text(self):
        text = self.entry.get()
        if text:
            self.add_label("Query: " + text)
            res = self.get_from_llm_pandas(text)
            if res == "":
                res = "RESULT NOT GENERATED"
            print(res)
            self.add_label_ans(res)
            self.entry.delete(0, tk.END)

    def attach_file(self):
        print("Open CSV")

    def add_label(self, text):
        label = tk.Label(self.label_container, text=text, bg="black", font=("Arial", 14), anchor="w", justify="left")
        label.pack(anchor="w", pady=5, padx=10)
    def add_label_ans(self, text):
        label = tk.Label(self.label_container, text=text, bg="black",fg="green", font=("Arial", 14), anchor="w", justify="left")
        label.pack(anchor="w", pady=5, padx=10)

    def get_from_llm_pandas(self, message):
        self.lh.load_data('heart.csv')
        gen_code = self.lh.generate_code(message)
        print(gen_code)
        result = self.lh.execute_code(gen_code)
        print("gen code executed")
        print(result)
        return result

if __name__ == "__main__":
    root = tk.Tk()
    app = Prompt2QueryApp(root)
    root.mainloop()
