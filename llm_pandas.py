import pandas as pd
import matplotlib as plt
import io
import numpy as np
from llm import LLM

class LLMHandler:
    def __init__(self):
        self.llm = LLM()
        self.buffer = io.StringIO()

    def load_data(self, url):
        # Load data into self.data and also make it globally accessible as 'data'
        self.data = pd.read_csv(url)
        globals()['data'] = self.data  # Set 'data' in the global namespace

    def get_data_info(self):
        self.data.info(buf=self.buffer)
        return self.buffer.getvalue()

    def generate_code(self, query):
        # Craft the prompt using the query and data information
        prompt = (f"your job is to write code without any explanation or comments for the queries asked. "
                  f"Try to write it in a way that will not generate any error. If you want to access the data, "
                  f"it's stored in the 'data' variable by default. Here is the query: {query}. "
                  f"print the answer for query asked"
                  f"Here is the information about the data: {self.get_data_info()}. "
                  f"Solve the query given to you.")
        
        # Get the response from the LLM
        generated_code = self.llm.model(prompt)[9:-3]
        return generated_code

    def execute_code(self, generated_code):
        # Initialize the result variable to capture output
        result = io.StringIO()

        # Define a custom print function that appends to the result variable
        def custom_print(*args, **kwargs):
            print_output = " ".join(map(str, args)) + "\n"
            result.write(print_output)

        # Temporarily override the built-in print function inside the exec context
        exec_globals = globals().copy()
        exec_globals['print'] = custom_print
        
        # Execute the generated code in this modified environment
        exec(generated_code, exec_globals)

        # Return the accumulated result as a string
        return result.getvalue()

