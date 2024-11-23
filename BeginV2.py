import customtkinter as ctk
from tkinter import PhotoImage, filedialog, Toplevel
from llm_pandas import LLMHandler
from sql_llm import LLMMySQLHandler
from llm import LLM
from datetime import datetime
from PIL import Image, ImageTk
import json 
import os

# Set default appearance and color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

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
        self.dir_path = "graphs"
        if not os.path.exists(self.dir_path):
            os.makedirs(self.dir_path)

    def load_icons(self):
        self.icon = PhotoImage(file='Icons/logo.png')
        self.root.iconphoto(True, self.icon)
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
        # Create main container
        self.main_container = ctk.CTkFrame(self.root)
        self.main_container.pack(fill="both", expand=True, padx=10, pady=10)

        # Create left and right frames
        self.create_left_frame()
        self.create_right_frame()

    def create_left_frame(self):
        self.left_frame = ctk.CTkFrame(self.main_container)
        self.left_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))

        # Top controls frame
        self.controls_frame = ctk.CTkFrame(self.left_frame)
        self.controls_frame.pack(fill="x", padx=5, pady=5)

        self.execute_button = ctk.CTkButton(
            self.controls_frame,
            image=self.play_green,
            text="",
            width=30,
            command=self.button_execute_manually
        )
        self.execute_button.pack(side="left", padx=5)

        self.left_label = ctk.CTkLabel(
            self.controls_frame,
            text="Executed Code",
            font=("Arial", 16)
        )
        self.left_label.pack(side="left", expand=True)

        # Output text area
        self.output_text = ctk.CTkTextbox(
            self.left_frame,
            font=("Arial", 14),
            wrap="word"
        )
        self.output_text.pack(fill="both", expand=True, padx=5, pady=5)

    def create_right_frame(self):
        self.right_frame = ctk.CTkFrame(self.main_container)
        self.right_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))

        self.create_top_right_frame()
        self.create_bottom_right_frame()

    def create_top_right_frame(self):
        # Header frame
        self.header_frame = ctk.CTkFrame(self.right_frame)
        self.header_frame.pack(fill="x", padx=5, pady=5)

        self.top_label = ctk.CTkLabel(
            self.header_frame,
            text="Result/ Logs",
            font=("Arial", 16)
        )
        self.top_label.pack(side="left", padx=5)

        # Control buttons
        self.config_button = ctk.CTkButton(
            self.header_frame,
            image=self.configure_icon,
            text="",
            width=30,
            command=self.config
        )
        self.config_button.pack(side="right", padx=2)

        self.load_rollback_button = ctk.CTkButton(
            self.header_frame,
            image=self.loadrollback,
            text="",
            width=30,
            command=self.perform_load_rollback
        )
        self.load_rollback_button.pack(side="right", padx=2)

        self.rollback_button = ctk.CTkButton(
            self.header_frame,
            image=self.rollback_icon,
            text="",
            width=30,
            command=self.perform_rollback,
            state="disabled"
        )
        self.rollback_button.pack(side="right", padx=2)

        # Mode selection
        self.mode_menu = ctk.CTkOptionMenu(
            self.header_frame,
            values=["Pandas", "SQL", "Default"],
            command=self.mode_callback
        )
        self.mode_menu.pack(side="right", padx=5)
        self.mode_menu.set("MODE")

        # Scrollable frame for results
        self.scroll_frame = ctk.CTkScrollableFrame(self.right_frame)
        self.scroll_frame.pack(fill="both", expand=True, padx=5, pady=5)

    def create_bottom_right_frame(self):
        self.bottom_frame = ctk.CTkFrame(self.right_frame)
        self.bottom_frame.pack(fill="x", padx=5, pady=5)

        # Input controls
        self.save_button = ctk.CTkButton(
            self.bottom_frame,
            image=self.save_icon,
            text="",
            width=30,
            command=self.save_data
        )
        self.save_button.pack(side="left", padx=2)

        self.attach_button = ctk.CTkButton(
            self.bottom_frame,
            image=self.icon_attach,
            text="",
            width=30,
            command=self.attach_file
        )
        self.attach_button.pack(side="left", padx=2)

        self.entry = ctk.CTkEntry(
            self.bottom_frame,
            font=("Arial", 16),
            placeholder_text="Enter your query here..."
        )
        self.entry.pack(side="left", fill="x", expand=True, padx=5)
        self.entry.bind("<Return>", self.submit_text)

        self.submit_button = ctk.CTkButton(
            self.bottom_frame,
            image=self.icon_up,
            text="",
            width=30,
            command=self.submit_text
        )
        self.submit_button.pack(side="right", padx=2)

    def add_label(self, text, color="white"):
        frame = ctk.CTkFrame(self.scroll_frame)
        frame.pack(fill="x", padx=5, pady=2)

        var = ctk.BooleanVar()
        checkbox = ctk.CTkCheckBox(
            frame,
            text="",
            variable=var,
            command=lambda: self.toggle_history(text, var),
            width=20
        )
        checkbox.pack(side="left", padx=5)

        label = ctk.CTkLabel(
            frame,
            text=text,
            font=("Arial", 14),
            text_color=color,
            wraplength=500
        )
        label.pack(side="left", fill="x", expand=True, padx=5)

    def add_label_button(self, text):
        frame = ctk.CTkFrame(self.scroll_frame)
        frame.pack(fill="x", padx=5, pady=2)

        if self.is_loded_data:
            index = len(self.data_storage)
            button = ctk.CTkButton(
                frame,
                image=self.arrow,
                text="Show Code",
                width=30,
                command=lambda idx=index: self.display_code(idx)
            )
            button.pack(side="left", padx=5)

        label = ctk.CTkLabel(
            frame,
            text=text,
            font=("Arial", 14)
        )
        label.pack(side="left", fill="x", expand=True, padx=5)

    def add_label_ans(self, text):
        self.add_label(text, "lightgreen")

    def add_label_error(self, text):
        self.add_label(text, "red")

    def add_label_image(self, image):
        frame = ctk.CTkFrame(self.scroll_frame)
        frame.pack(fill="x", padx=5, pady=2)
        
        label = ctk.CTkLabel(frame, image=image, text="")
        label.pack(padx=5, pady=5)

    def mode_callback(self, choice):
        print(f"Mode selected: {choice}")

    def submit_text(self, event=None):
        mode = self.mode_menu.get()
        if mode == "Pandas":
            self.pandas_mode()
        elif mode == "SQL":
            self.sql_mode()
        elif mode == "Default":
            self.default_mode()
        else:
            self.add_label_error("Select a mode from MODE MENU")

    # The following methods remain largely unchanged from the original code
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
            self.entry.delete(0, "end")

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
            self.entry.delete(0, "end")

    def default_mode(self):
        text = self.entry.get()
        output = self.llm.model(f"{text}, this is history of previous conversation: {self.history}")
        self.add_label_ans(output)
        self.entry.delete(0, "end")

    def get_from_llm_pandas(self, message):
        if not self.is_loded_data:
            self.add_label_error("Data not loaded")
            return None
        gen_code = self.lh.generate_code(message, history=self.history)
        result = self.lh.execute_code(gen_code)
        return [result, gen_code]

    def get_from_ll_sql(self, message):
        gen_sql = self.sh.generate_sql(message, self.history)
        result = self.sh.execute_sql(gen_sql)
        return [result, gen_sql]

    def button_execute_manually(self):
        mode = self.mode_menu.get()
        if mode == "Pandas":
            query = self.output_text.get("1.0", "end-1c")
            result = self.lh.execute_code(query)
            self.add_label("Query: " + query + "    | " + datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
            self.add_label_ans(result)
        elif mode == "SQL":
            query = self.output_text.get("1.0", "end-1c")
            output = self.get_from_ll_sql(query)
            result, _ = output
            self.add_label("Query: " + query + "    | " + datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
            self.add_label_ans(result)
        else:
            self.add_label_error("Mode not selected")

    def save_data(self):
        # Implement save functionality
        pass

    def attach_file(self):
        file_path = filedialog.askopenfilename(
            title="Select a CSV file",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if file_path:
            res = self.lh.load_data(file_path)
            if res:
                self.is_loded_data = True
                self.add_label_ans("File loaded successfully")
            else:
                self.add_label_error("Failed to load file")

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
        print("Current history:", self.history)

    def add_graph(self):
        image_store = self.load_png_images_and_delete(self.dir_path)
        if image_store:
            for description, single_image in image_store.items():
                description = description.replace(".png", "")
                self.add_label(description)
                self.add_label_image(single_image)

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

    def perform_rollback(self):
        self.lh.load_data_var(self.rollbackdata)
        print(self.rollbackdata.head())
        self.add_label_ans("Rollback performed successfully")

    def perform_load_rollback(self):
        self.rollbackdata = self.lh.return_data()
        self.rollback_button.configure(state="normal")
        self.add_label_ans("Rollback data loaded")

    def config(self):
        # Create new window using CTk
        self.new_window = ctk.CTkToplevel(self.root)
        self.new_window.title("Database Configuration")
        self.new_window.geometry("400x300")

        # Create main frame
        config_frame = ctk.CTkFrame(self.new_window)
        config_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Load existing credentials
        credentials = {}
        if os.path.exists("db_credentials.json"):
            try:
                with open("db_credentials.json", "r") as file:
                    credentials = json.load(file)
            except json.JSONDecodeError:
                print("Error decoding credentials file")

        # Host entry
        host_label = ctk.CTkLabel(config_frame, text="Host:")
        host_label.pack(pady=(0, 5))
        self.host_entry = ctk.CTkEntry(config_frame)
        self.host_entry.insert(0, credentials.get("host", ""))
        self.host_entry.pack(pady=(0, 10), fill="x")

        # User entry
        user_label = ctk.CTkLabel(config_frame, text="User:")
        user_label.pack(pady=(0, 5))
        self.user_entry = ctk.CTkEntry(config_frame)
        self.user_entry.insert(0, credentials.get("user", ""))
        self.user_entry.pack(pady=(0, 10), fill="x")

        # Password entry
        password_label = ctk.CTkLabel(config_frame, text="Password:")
        password_label.pack(pady=(0, 5))
        self.password_entry = ctk.CTkEntry(config_frame, show="*")
        self.password_entry.insert(0, credentials.get("password", ""))
        self.password_entry.pack(pady=(0, 10), fill="x")

        # Save and Connect button
        save_button = ctk.CTkButton(
            config_frame,
            text="Save and Connect",
            image=self.floppydisk,
            command=self.manage_connect
        )
        save_button.pack(pady=20)

    def manage_connect(self):
        try:
            host = self.host_entry.get()
            user = self.user_entry.get()
            password = self.password_entry.get()
            
            # Save credentials to file
            credentials = {
                "host": host,
                "user": user,
                "password": password
            }
            with open("db_credentials.json", "w") as file:
                json.dump(credentials, file)

            # Attempt connection
            self.sh.connect(host=host, password=password, user=user)
            self.connect_state = True
            
            # Close config window and show success message
            self.new_window.destroy()
            self.add_label_ans(f"Successfully connected to database as {user}")
        except Exception as e:
            self.add_label_error(f'Error connecting to database: {str(e)}')

    def fill_manage_connect(self):
        try:
            with open("db_credentials.json", "r") as file:
                credentials = json.load(file)
            
            # Attempt automatic connection
            self.sh.connect(
                host=credentials.get("host"),
                user=credentials.get("user"),
                password=credentials.get("password")
            )
            self.connect_state = True            
            self.add_label_ans(f"Connected to SQL as {credentials.get('user')}")
        except FileNotFoundError:
            self.add_label_error("No saved credentials found. Please configure database connection.")
        except json.JSONDecodeError:
            self.add_label_error("Error reading credentials file. Please reconfigure database connection.")
        except Exception as e:
            self.add_label_error(f"Could not connect to SQL server: {str(e)}")

if __name__ == "__main__":
    root = ctk.CTk()
    app = Prompt2QueryApp(root)
    root.mainloop()
