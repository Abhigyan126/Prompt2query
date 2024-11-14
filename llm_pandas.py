import pandas as pd
import matplotlib as plt
import io
import numpy as np
from llm import LLM

class LLMHandler:
    def __init__(self):
        self.llm = LLM()
        self.buffer = io.StringIO()
        self.data = pd.DataFrame()

    def load_data(self, url):
        try:
            # Load data into self.data and also make it globally accessible as 'data'
            self.data = pd.read_csv(url)
            return True
        except Exception as e:
            return e
    def return_data(self):
        return self.data
    def load_data_var(self, data):
        print("origin", data)
        self.data = data

    def get_data_info(self):
        self.data.info(buf=self.buffer)
        return self.buffer.getvalue()

    def generate_code(self, query, history):
        # Craft the prompt using the query and data information
        prompt = (f"your job is to write code without any explanation or comments for the queries asked. "
                  f"Try to write it in a way that will not generate any error. If you want to access the data, "
                  f"it's stored in the 'data' variable by default. Here is the query: {query} {history}."
                  f"available libraries you can use nupmy as np, pandas as pd, and matplotlib as plt."
                  f"dont display any graph save all the images or graphs in the graphs directory which is alredy created for you, the name for the graph should be its discription in detail, donot print confirmation regarding saving graph"
                  f"stick with the information provided dont assume things and use try and except block with proper error handeling"
                  f"print the answer for query asked"
                  f"Here is the information about the data: {self.get_data_info()}. "
                  f"Solve the query given to you."
                  )
        
        # Get the response from the LLM
        generated_code = self.llm.model(prompt)[9:-3]
        return generated_code

    def execute_code(self, generated_code):
        # Initialize the result variable to capture output
        data = self.data
        result = io.StringIO()

        # Define a custom print function that appends to the result variable
        def custom_print(*args, **kwargs):
            print_output = " ".join(map(str, args)) + "\n"
            result.write(print_output)

        # Temporarily override the built-in print function inside the exec context
        exec_globals = globals().copy()
        exec_globals['print'] = custom_print

        # Pass 'data' to exec_globals to make it accessible inside exec
        exec_globals['data'] = self.data

        # Execute the generated code in this modified environment
        exec(generated_code, exec_globals)

        # Make sure to assign the modified 'data' back to the class instance
        self.data = exec_globals['data']

        # Return the accumulated result as a string
        return result.getvalue()

    def result_to_natural(self, query, res, code):
        prompt = f"your job is to make user understand the result in natural language this maybe for someone non technical keep, please provide inference for the recived result for query in minimum words tell the user what result is not explain the result, here is code: {code}, query: {query}, result: {res}"
        result = self.llm.model(prompt)
        return result

