import tkinter as tk
from tkinter import PhotoImage, Entry, Button, Frame, Scrollbar, filedialog
from llm_pandas import LLMHandler
from datetime import datetime

class Prompt2QueryApp:
    def __init__(self, root):
        self.root = root
        self.setup_window()
        self.load_icons()
        self.create_layout()
        self.lh = LLMHandler()
        self.is_loded_data = False
        self.data_storage = []

    def setup_window(self):
        height_ = self.root.winfo_screenheight() - 100
        width_ = self.root.winfo_screenwidth() - 50
        self.root.geometry(f"{width_}x{height_}")
        self.root.title("Prompt2Query")

    def load_icons(self):
        # Load and set the window icon
        self.icon = PhotoImage(file='Icons/logo.png')
        self.root.iconphoto(True, self.icon)

        # Load icons for buttons
        self.icon_up = PhotoImage(file='Icons/up-arrow.png').subsample(20, 20)
        self.icon_attach = PhotoImage(file='Icons/attachment.png').subsample(20, 20)
        self.save_icon = PhotoImage(file='Icons/save_icon.png').subsample(20, 20)
        self.arrow = PhotoImage(file='Icons/play_red.png').subsample(20, 20)
        self.play_green = PhotoImage(file='Icons/play_green.png').subsample(25, 25)
        self.play_red = PhotoImage(file='Icons/play_red.png').subsample(25, 25)

    def create_layout(self):
        self.create_left_frame()
        self.create_right_frame()

    def create_left_frame(self):
        # Left frame for text output and scrollbar
        self.left_frame = Frame(self.root, bg="white", width=self.root.winfo_width() // 2 - 250)
        self.left_frame.pack(side="left", fill="y")

        # Frame to hold both label and button
        self.label_button_frame = Frame(self.left_frame, bg="white")
        self.label_button_frame.pack(side="top", pady=(5,3), fill="x")

        # Configure the grid layout for the label_button_frame
        self.label_button_frame.grid_columnconfigure(0, weight=1)  # Column for button (left)
        self.label_button_frame.grid_columnconfigure(1, weight=1)  # Column for label (center)
        self.label_button_frame.grid_columnconfigure(2, weight=3)  # Space to the right of label

        # Button on the left-most side
        self.right_button = tk.Button(self.label_button_frame,image=self.play_green , borderwidth=0, highlightthickness=0,command=self.button_execute_manually)
        self.right_button.grid(row=0, column=0, sticky="w", padx=(10, 0))

        # Label in the center
        self.left_label = tk.Label(self.label_button_frame, text="Executed Code", font=("Arial", 16), fg="black", bg="white", anchor="center")
        self.left_label.grid(row=0, column=1, sticky="nsew")

        self.output_text = tk.Text(self.left_frame, bg="black", font=("Arial", 14), wrap="word", height=20, width=50)
        self.output_text.pack(side="left", fill="both", expand=True, padx=(10,0), pady=(0,10))

        # Add scrollbar to text widget
        self.scrollbar = Scrollbar(self.left_frame, command=self.output_text.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.output_text.config(yscrollcommand=self.scrollbar.set)

    # Example command for the button
    def button_execute_manually(self):
        selected_option_value = self.selected_option.get()
        if  selected_option_value == "Pandas":
            query = self.output_text.get("1.0", "end-1c")
            result = self.lh.execute_code(query)
            self.add_label("Query: " + query + "    | " + datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
            self.add_label_ans(result)
        else:
            self.add_label_error("Mode not selected")

        print("Button clicked!")

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

        # Create a container frame for label and dropdown
        self.label_dropdown_frame = Frame(self.top_right_frame, bg="white")
        self.label_dropdown_frame.pack(side="top", fill="x", padx=15, pady=1)

        # Label centered in the grid (Grid position: row 0, column 0, columnspan 2)
        self.top_label = tk.Label(self.label_dropdown_frame, text="Result/ Logs", font=("Arial", 16), fg="black", bg="white", anchor="center")
        self.top_label.grid(row=0, column=0, columnspan=2, padx=1, pady=5, sticky="nsew") 

        # Dropdown on the far right (Grid position: row 0, column 2)
        self.selected_option = tk.StringVar(self.root)
        self.selected_option.set("MODE")
        self.dropdown = tk.OptionMenu(self.label_dropdown_frame, self.selected_option, "Pandas", "SQL")
        self.dropdown.grid(row=0, column=2, padx=1, pady=5, sticky="e")

        # Configure the grid columns for proper layout
        self.label_dropdown_frame.grid_columnconfigure(0, weight=1)  # Column for the label to expand
        self.label_dropdown_frame.grid_columnconfigure(1, weight=1)  # Empty column to balance the layout
        self.label_dropdown_frame.grid_columnconfigure(2, weight=0)  # Column for the dropdown, no expansion


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
        self.entry.grid(row=0, column=2)
        self.entry.bind("<Return>", self.submit_text)


        # Attachment button
        self.attach_button = Button(self.input_frame, image=self.icon_attach, width=30, height=26, command=self.attach_file)
        self.attach_button.grid(row=0, column=1)

        #Save botton functionality not implemented
        self.save_button =  Button(self.input_frame, image=self.save_icon, width=30, height=26, command=self.attach_file)
        self.save_button.grid(row=0, column=0)

        # Submit button for adding labels
        self.submit_button = Button(self.input_frame, image=self.icon_up, width=30, height=26, command=self.submit_text)
        self.submit_button.grid(row=0, column=3)

    def on_frame_configure(self, event): 
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def scroll(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def submit_text(self, event=None):
        selected_option_value = self.selected_option.get()
        if selected_option_value == "Pandas":
            self.pandas_mode()
        elif selected_option_value == "SQL":
            print("sql")
        else:
            self.add_label_error("Select a mode from MODE MENU")
        
    def pandas_mode(self):
        text = self.entry.get()
        if text:
            self.add_label_button("Query: " + text + "    | " + datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
            output = self.get_from_llm_pandas(text)
            if output is None:
                self.add_label_error("ERROR: No output from the model")
                return
            try:
                res = output[0]
                code = output[1]
            except (IndexError, TypeError):
                self.add_label_error("ERROR: Output format is incorrect")
                return
            
            self.data_storage.append({'query': text, 'response': res, 'code': code})

            self.output_text.delete("1.0", "end")
            self.output_text.insert("1.0", f"{code}\n\n")
            if res == "":
                self.add_label_error("RESULT NOT GENERATED")
            else:
                self.add_label(res)
            natural = self.lh.result_to_natural(text, res, code)
            self.add_label_ans(natural)
            self.entry.delete(0, tk.END)

    def attach_file(self):
        file_path = filedialog.askopenfilename(
        title="Select a CSV file",
        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        res = self.lh.load_data(file_path)
        if res:
            self.is_loded_data = True
            self.add_label_ans("File loded sucessfully")
        else:
            self.add_label_error("Failed to load file")

    def add_label_button(self, text):
        frame = tk.Frame(self.label_container, bg="black")
        frame.pack(anchor="w", pady=5, padx=10, fill="x")

        # Capture the current index correctly for each button
        if self.is_loded_data:
            index = len(self.data_storage)  # Get the index for the new query
            button = tk.Button(frame, text="Show Code",image=self.arrow , command=lambda idx=index: self.display_code(idx))
            button.pack(side="left", padx=(0,10))

        label = tk.Label(frame, text=text, bg="black", font=("Arial", 14), anchor="w", justify="left")
        label.pack(side="left")



    def add_label(self, text):
        label = tk.Label(self.label_container, text=text, bg="black", font=("Arial", 14), anchor="w", justify="left")
        label.pack(anchor="w", pady=5, padx=10)
    def add_label_ans(self, text):
        label = tk.Label(self.label_container, text=text, bg="black",fg="lightgreen", font=("Arial", 14), anchor="w", justify="left")
        label.pack(anchor="w", pady=5, padx=10)
    
    def add_label_error(self, text):
        label = tk.Label(self.label_container, text=text, bg="black",fg="red", font=("Arial", 16), anchor="w", justify="left")
        label.pack(anchor="w", pady=5, padx=10)

    def get_from_llm_pandas(self, message):
        if self.is_loded_data == False:
            self.add_label_error("Data not loaded")
        else:
            gen_code = self.lh.generate_code(message)
            print(gen_code)
            result = self.lh.execute_code(gen_code)
            print("gen code executed")
            print(result)
            return [result, gen_code]
    
    def display_code(self, index):
        if index < len(self.data_storage):
            code = self.data_storage[index]['code']
            self.output_text.delete("1.0", "end")
            self.output_text.insert("1.0", f"{code}\n\n")  # Display the code
        else:
            self.add_label_error("Invalid index Error")


if __name__ == "__main__":
    root = tk.Tk()
    app = Prompt2QueryApp(root)
    root.mainloop()
