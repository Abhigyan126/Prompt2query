import tkinter as tk
from tkinter import PhotoImage, Entry, Button, Frame, Scrollbar, filedialog, messagebox
from llm_pandas import LLMHandler  # Ensure this module is installed or accessible

class Prompt2QueryApp:
    def __init__(self, root):
        self.root = root
        self.file_path = None  # Store the file path globally within the instance
        self.setup_window()
        self.load_icons()
        self.create_layout()
        self.lh = LLMHandler()  # LLMHandler instance
        self.prompt_count = 0  # Counter for tracking queries
        self.prompts = []  # List to store submitted queries

    def setup_window(self):
        height_ = self.root.winfo_screenheight() - 100
        width_ = self.root.winfo_screenwidth() - 50
        self.root.geometry(f"{width_}x{height_}")
        self.root.title("Prompt2Query")

    def load_icons(self):
        # Load images for buttons and window icon
        try:
            self.icon = PhotoImage(file='Icons/logo.png')
            self.root.iconphoto(True, self.icon)
        except tk.TclError:
            print("Logo image not found. Please ensure 'Icons/logo.png' is in the working directory.")
        try:
            self.icon_up = PhotoImage(file='Icons/up-arrow.png').subsample(20, 20)
        except tk.TclError:
            print("Up-arrow image not found. Please ensure 'Icons/up-arrow.png' is in the working directory.")
            self.icon_up = None  # Set to None to avoid errors
        try:
            self.icon_attach = PhotoImage(file='Icons/attachment.png').subsample(20, 20)
        except tk.TclError:
            print("Attachment image not found. Please ensure 'attachment.png' is in the working directory.")
            self.icon_attach = None

    def create_layout(self):
        self.create_left_frame()
        self.create_right_frame()

    def create_left_frame(self):
        # Frame for displaying history on the left
        self.left_frame = Frame(self.root, bg="lightgrey", width=300)
        self.left_frame.pack(side="left", fill="y")

        history_label = tk.Label(self.left_frame, text="History", font=("Arial", 15, "bold"), bg="lightgrey")
        history_label.pack(pady=20)

        # Scrollable frame for history
        self.history_canvas = tk.Canvas(self.left_frame, bg="lightgrey")
        self.history_scrollbar = Scrollbar(self.left_frame, orient="vertical", command=self.history_canvas.yview)
        self.history_canvas.configure(yscrollcommand=self.history_scrollbar.set)
        self.history_scrollbar.pack(side="right", fill="y")
        self.history_canvas.pack(side="left", fill="both", expand=True)

        self.history_frame = Frame(self.history_canvas, bg="lightgrey")
        self.history_canvas.create_window((0, 0), window=self.history_frame, anchor="nw")
        self.history_frame.bind("<Configure>", lambda e: self.history_canvas.configure(scrollregion=self.history_canvas.bbox("all")))

    def create_right_frame(self):
        # Frame on the right for input/output and displaying results
        self.right_frame = Frame(self.root, bg="white")
        self.right_frame.pack(side="right", fill="both", expand=True)

        self.create_bottom_right_frame()
        self.create_result_display()

    def create_bottom_right_frame(self):
        # Bottom frame for text input and buttons
        self.bottom_right_frame = Frame(self.right_frame, bg="white")
        self.bottom_right_frame.pack(side="bottom", pady=20)

        self.entry = Entry(self.bottom_right_frame, font=("Arial", 20), width=50)
        self.entry.grid(row=0, column=1, padx=5)
        self.entry.bind("<Return>", lambda e: self.submit_text())

        attach_button = Button(self.bottom_right_frame, image=self.icon_attach, width=30, height=28, command=self.attach_file)
        attach_button.grid(row=0, column=0)

        submit_button = Button(self.bottom_right_frame, image=self.icon_up, width=30, height=28, command=self.submit_text)
        submit_button.grid(row=0, column=2, padx=5)

    def create_result_display(self):
        # Text widget for displaying results
        self.result_text = tk.Text(self.right_frame, wrap="word", font=("Arial", 12))
        self.result_text.pack(side="top", fill="both", expand=True)

        # Scrollbar for the result text
        self.result_scrollbar = Scrollbar(self.right_frame, command=self.result_text.yview)
        self.result_scrollbar.pack(side="right", fill="y")
        self.result_text.configure(yscrollcommand=self.result_scrollbar.set)

    def submit_text(self):
        text = self.entry.get()
        if not self.file_path:
            messagebox.showwarning("No File Attached", "Please attach a CSV file before submitting a query.")
            return
        if text.strip():
            self.prompt_count += 1
            self.prompts.append(text)
            self.add_prompt_label(text)
            res = self.get_from_llm_pandas(text)  # Call LLMHandler for query execution
            self.display_result(res)
            self.entry.delete(0, tk.END)
        else:
            messagebox.showwarning("Empty Query", "Please enter a query before submitting.")

    def attach_file(self):
        # Opens file dialog to select a file, saves the path to self.file_path
        self.file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if self.file_path:
            print(f"Attached file: {self.file_path}")
            try:
                self.lh.load_data(self.file_path)
                messagebox.showinfo("File Attached", f"Successfully loaded {self.file_path}")
            except Exception as e:
                messagebox.showerror("File Load Error", f"An error occurred while loading the file: {e}")
                self.file_path = None

    def add_prompt_label(self, text):
        # Adds a button on the left frame for each prompt submitted
        new_prompt_button = Button(self.history_frame, text=f"Prompt {self.prompt_count}: {text}",
                                   font=("Arial", 10), bg="lightblue", anchor="w", width=30)
        new_prompt_button.pack(pady=5, padx=5)
        new_prompt_button.bind("<Button-1>", lambda e, t=text: self.entry.insert(0, t))

    def display_result(self, result):
        # Displays the result in the result_text widget
        self.result_text.insert(tk.END, f"Prompt {self.prompt_count}: {self.prompts[-1]}\n")
        self.result_text.insert(tk.END, f"Result:\n{result}\n{'-'*50}\n")
        self.result_text.see(tk.END)

    def get_from_llm_pandas(self, message):
        # Uses the LLMHandler to generate and execute code based on the message
        try:
            gen_code = self.lh.generate_code(message)
            print(f"Generated code:\n{gen_code}")
            result = self.lh.execute_code(gen_code)
            print("Result:", result)
            return result
        except Exception as e:
            error_msg = f"An error occurred during query execution: {e}"
            print(error_msg)
            messagebox.showerror("Execution Error", error_msg)
            return error_msg

if __name__ == "__main__":
    root = tk.Tk()
    app = Prompt2QueryApp(root)
    root.mainloop()
