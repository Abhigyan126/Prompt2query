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
        try:
            # Load data into self.data and also make it globally accessible as 'data'
            self.data = pd.read_csv(url)
            globals()['data'] = self.data  # Set 'data' in the global namespace
            return True
        except e:
            return e

    def get_data_info(self):
        self.data.info(buf=self.buffer)
        return self.buffer.getvalue()

    def generate_code(self, query):
        # Craft the prompt using the query and data information
        prompt = (f"your job is to write code without any explanation or comments for the queries asked. "
                  f"Try to write it in a way that will not generate any error. If you want to access the data, "
                  f"it's stored in the 'data' variable by default. Here is the query: {query}. "
                  f"available libraries you can use nupmy as np, pandas as pd, and matplotlib as plt."
                  f"stick with the information provided dont assume things and use try and except block with proper error handeling"
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
    def result_to_natural(self, query, res, code):
        prompt = f"your job is to make user understand the result in natural language this maybe for someone non technical keep, please provide inference for the recived result for query in minimum words tell the user what result is not explain the result, here is code: {code}, query: {query}, result: {res}"
        result = self.llm.model(prompt)
        return result

