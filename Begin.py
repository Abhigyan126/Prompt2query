import tkinter as tk
from tkinter import PhotoImage, Entry, Button, Frame, Scrollbar, filedialog, Toplevel
from llm_pandas import LLMHandler
from sql_llm import LLMMySQLHandler
from llm import LLM
from datetime import datetime
from PIL import Image, ImageTk
import json 
import os


class Prompt2QueryApp:
    def __init__(self, root):
        self.root = root
        self.setup_window()
        self.load_icons()
        self.create_layout()
        self.lh = LLMHandler()
        self.sh = LLMMySQLHandler()
        self.connect_state = False
        self.is_loded_data = False
        self.llm = LLM()
        self.data_storage = []
        self.image_references = []
        self.history = []
        self.rollbackdata = []
        self.fill_manage_connect()


    def setup_window(self):
        height_ = self.root.winfo_screenheight() - 100
        width_ = self.root.winfo_screenwidth() - 50
        self.root.geometry(f"{width_}x{height_}")
        self.root.title("Prompt2Query")
        #make dir for images
        self.dir_path = "graphs"
        if not os.path.exists(self.dir_path):
            os.makedirs(self.dir_path)

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
        self.rollback_icon = PhotoImage(file='Icons/reload.png').subsample(15, 15)
        self.loadrollback = PhotoImage(file='Icons/insert_rollback.png').subsample(15, 15)
        self.configure_icon = PhotoImage(file='Icons/gear.png').subsample(15, 15)
        self.floppydisk = PhotoImage(file='Icons/floppy-disk.png').subsample(15, 15)

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
        self.right_button = tk.Button(self.label_button_frame,image=self.play_green , borderwidth=0.1, highlightthickness=0.1,command=self.button_execute_manually)
        self.right_button.grid(row=0, column=0, sticky="w", padx=(10, 0))

        # Label in the center
        self.left_label = tk.Label(self.label_button_frame, text="Executed Code", font=("Arial", 16), fg="black", bg="white", anchor="center")
        self.left_label.grid(row=0, column=1, sticky="nsew")

        self.output_text = tk.Text(self.left_frame, bg="black", font=("Arial", 14), wrap="word", height=20, width=50, fg="white")
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
        elif selected_option_value == "SQL":
            query = self.output_text.get("1.0", "end-1c")
            output = self.get_from_ll_sql(query)
            result, _ = output
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
        self.top_label.grid(row=0, column=0, columnspan=4, padx=1, sticky="nsew") 

        #Button for Configure
        self.rollback_button = Button(self.label_dropdown_frame, image=self.configure_icon, borderwidth=0.1, highlightthickness=0.1, command=self.config)
        self.rollback_button.grid(row=0, column=2, padx=2, sticky='w')

        #Button for LoadRollback pandas
        self.load_rollback_button = Button(self.label_dropdown_frame, image=self.loadrollback, borderwidth=0.1, highlightthickness=0.1, command=self.perform_load_rollback)
        self.load_rollback_button.grid(row=0, column=3, padx=2)

        #Button for Rollback Pandas
        self.rollback_button = Button(self.label_dropdown_frame, image=self.rollback_icon, borderwidth=0.1, highlightthickness=0.1, command=self.perform_rollback, state='disabled')
        self.rollback_button.grid(row=0, column=4, padx=5)

        # Dropdown on the far right (Grid position: row 0, column 2)
        self.selected_option = tk.StringVar(self.root)
        self.selected_option.set("MODE")
        self.dropdown = tk.OptionMenu(self.label_dropdown_frame, self.selected_option, "Pandas", "SQL", "Default")
        self.dropdown.grid(row=0, column=5, padx=1, pady=5, sticky="e")

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
        self.entry = Entry(self.input_frame, font=("Arial", 20), width=50, bg="black", fg="white")
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
            self.sql_mode()
        elif selected_option_value == "Default":
            self.default_mode()
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
            self.add_graph()
            self.add_label_ans(natural)
            self.entry.delete(0, tk.END)

    def default_mode(self):
        text = self.entry.get()
        output = self.llm.model(f"{text}, this is histry of previous conversation: {self.history}")
        self.add_label_ans(output)

    def sql_mode(self):
        text = self.entry.get()
        if text and self.connect_state:
                self.add_label_button("Query: " + text + "    | " + datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
                output = self.get_from_ll_sql(text)
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
        if self.is_loded_data:
            index = len(self.data_storage)
            button = tk.Button(frame, text="Show Code",image=self.arrow , command=lambda idx=index: self.display_code(idx))
            button.pack(side="left", padx=(0,10))

        label = tk.Label(frame, text=text, bg="black", font=("Arial", 14), anchor="w", justify="left", fg="white")
        label.pack(side="left")
        self.on_frame_configure(None)


    #Display_Graphs
    def add_graph(self):
        image_store = self.load_png_images_and_delete(self.dir_path)
        if image_store:
            for description, single_image in image_store.items():
                description = description.replace(".png", "") 
                self.add_label(description)
                self.add_label_image(single_image)
                self.on_frame_configure(None)

    def add_label(self, text):
        frame = tk.Frame(self.label_container, bg="black")
        var = tk.BooleanVar()
        checkbox = tk.Checkbutton(frame, variable=var, command=lambda: self.toggle_history(text, var), bg="black")
        checkbox.pack(side="left", padx=(5, 10), anchor="ne")
        label = tk.Label(frame, text=text, bg="black", font=("Arial", 14), anchor="w", justify="left", fg="white", wraplength=500)
        label.pack(side="left", anchor="w", padx=10)
        frame.pack(anchor="w", pady=5, padx=10, fill="x")
        self.on_frame_configure(None)

    def add_label_ans(self, text):
        frame1 = tk.Frame(self.label_container, bg="black")
        var = tk.BooleanVar()
        checkbox = tk.Checkbutton(frame1, variable=var, command=lambda: self.toggle_history(text, var), bg="black")
        checkbox.pack(side="left", padx=(5, 10), anchor="ne")
        label = tk.Label(frame1, text=text, bg="black", fg="lightgreen", font=("Arial", 14), anchor="w", justify="left", wraplength=500)
        label.pack(side="left", anchor="w", padx=10)
        frame1.pack(anchor="w", pady=5, padx=10, fill="x")
        self.on_frame_configure(None)

    def add_label_error(self, text):
        frame2 = tk.Frame(self.label_container, bg="black")
        var = tk.BooleanVar()
        checkbox = tk.Checkbutton(frame2, variable=var, command=lambda: self.toggle_history(text, var), bg="black")
        checkbox.pack(side="left", padx=(5, 10), anchor="ne")
        label = tk.Label(frame2, text=text, bg="black", fg="red", font=("Arial", 16), anchor="w", justify="left", wraplength=500)
        label.pack(side="left", anchor="w", padx=10)  # Using pack for the label
        frame2.pack(anchor="w", pady=5, padx=10, fill="x")  # Using pack for the frame
        self.on_frame_configure(None)

    
    def add_label_image(self, image):
        label = tk.Label(self.label_container, image=image,anchor="w",bg="black", justify="left")
        label.pack(anchor="w", pady=5, padx=10)
        self.on_frame_configure(None)


    def get_from_llm_pandas(self, message):
        if self.is_loded_data == False:
            self.add_label_error("Data not loaded")
        else:
            gen_code = self.lh.generate_code(message, history=self.history)
            print(gen_code)
            result = self.lh.execute_code(gen_code)
            print("gen code executed")
            print(result)
            return [result, gen_code]

    def get_from_ll_sql(self, message):
        gen_sql = self.sh.generate_sql(message, self.history)
        print("Generated sql: ", gen_sql)
        result = self.sh.execute_sql(gen_sql)
        print("Generated Result: ",result)
        return [result, gen_sql]
    
    def display_code(self, index):
        if index < len(self.data_storage):
            code = self.data_storage[index]['code']
            self.output_text.delete("1.0", "end")
            self.output_text.insert("1.0", f"{code}\n\n")
        else:
            self.add_label_error("Invalid index Error")
    
    def toggle_history(self, label_text, var):
        if var.get():
            self.history.append(label_text)
        else:
            self.history.remove(label_text)
        print("Current history:", self.history)  # This prints the updated history list
        
    def load_png_images_and_delete(self, directory):
            image_data = {}
            for filename in os.listdir(directory):
                if filename.endswith('.png'):
                    file_path = os.path.join(directory, filename)
                    try:
                        img = Image.open(file_path)
                        img.thumbnail((600, 600))
                        tk_image = ImageTk.PhotoImage(img)
                        image_data[filename] = tk_image
                        self.image_references.append(tk_image)
                        os.remove(file_path)
                    except Exception as e:
                        print(f"Error loading {filename}: {e}")

            return image_data
    #Function to perform rollback
    def perform_rollback(self):
        self.lh.load_data_var(self.rollbackdata)
        print(self.rollbackdata.head())
    #Function to perform load_rollback
    def perform_load_rollback(self):
        self.rollbackdata = self.lh.return_data()
        self.rollback_button.config(state='active')

    #Function to open config pannel
    def config(self):
        print("Configuring Database Connection...")

        # Create new window
        self.new_window = Toplevel(self.root)
        self.new_window.title("Config")

        # Set up frame for connection
        frame_for_connect = tk.Frame(self.new_window, bg="#eae8e0", borderwidth=5, width=300, height=200)
        frame_for_connect.pack(padx=20, pady=20)

        # Load credentials if the file exists
        credentials = {}
        if os.path.exists("db_credentials.json"):
            with open("db_credentials.json", "r") as file:
                try:
                    credentials = json.load(file)
                except json.JSONDecodeError:
                    print("Error decoding credentials file. Please check the file format.")

        # Host entry
        tk.Label(frame_for_connect, text="Host:", bg="#eae8e0", fg='#6F4E37', anchor='w').grid(row=0, column=0, sticky='w')
        self.host_entry = tk.Entry(frame_for_connect, bg="#eae8e0", fg='#6F4E37')
        self.host_entry.insert(0, credentials.get("host", ""))
        self.host_entry.grid(row=0, column=1)

        # User entry
        tk.Label(frame_for_connect, text="User:", bg="#eae8e0", fg='#6F4E37', anchor='w').grid(row=1, column=0, sticky='w')
        self.user_entry = tk.Entry(frame_for_connect, bg="#eae8e0", fg='#6F4E37')
        self.user_entry.insert(0, credentials.get("user", ""))
        self.user_entry.grid(row=1, column=1)

        # Password entry
        tk.Label(frame_for_connect, text="Password:", bg="#eae8e0", fg='#6F4E37', anchor='w').grid(row=2, column=0, sticky='w')
        self.password_entry = tk.Entry(frame_for_connect, show="*", bg="#eae8e0", fg='#6F4E37')
        self.password_entry.insert(0, credentials.get("password", ""))
        self.password_entry.grid(row=2, column=1)

        # Save and Connect button
        save_button = tk.Button(frame_for_connect, image=self.floppydisk, bg='#eae8e0', command=self.manage_connect)
        save_button.grid(row=3, column=0, columnspan=2, pady=10)
    
    #Function to manage connect
    def manage_connect(self):
        try:
            host = self.host_entry.get()
            user = self.user_entry.get()
            password = self.password_entry.get()
            #dump to file
            credentials = {"host": host, "user": user, "password": password}
            with open("db_credentials.json", "w") as file:
                json.dump(credentials, file)
            self.sh.connect(host=host, password=password, user=user)
            self.connect_state = True
        except Exception as e:
            self.add_label_error(f'Error connecting, Error: {e}')
    def fill_manage_connect(self):
        try:
            with open("db_credentials.json", "r") as file:
                credentials = json.load(file)
            # Automatically connect using the loaded credentials
            self.sh.connect(
            host=credentials.get("host"),
            user=credentials.get("user"),
            password=credentials.get("password")
                )
            self.connect_state = True            
            self.add_label_ans(f"Connected to SQL as {credentials.get('user')}")
        except FileNotFoundError:
            self.add_label_error("Credential file not found. Please enter details manually.")
        except json.JSONDecodeError:
            self.add_label_error("Error decoding credentials file. Please check the file format.")
        except Exception as e:
            print(e)
            self.add_label_error("Could not connect to SQL server")
        

if __name__ == "__main__":
    root = tk.Tk()
    app = Prompt2QueryApp(root)
    root.mainloop()
