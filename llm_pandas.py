import pandas as pd
import matplotlib as plt
import io
import re
import numpy as np
from llm import LLM

class LLMHandler:
    def __init__(self):
        self.llm = LLM()
        self.buffer = io.StringIO()
        self.data = pd.DataFrame()
        self.full_plan = ""

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
    
    def generate_code_old(self, query):
        # Craft the prompt using the query and data information
        prompt = (f"your job is to write code without any explanation or comments for the queries asked. "
                  f"Try to write it in a way that will not generate any error. assume data in pandas dataframe, "
                  f"it's stored in the 'data' variable by default. Here is the query: {query}. "
                  f"dont display any graph save all the images or graphs in the graphs directory which is alredy created for you, the name for the graph should be its discription in detail, donot print confirmation regarding saving graph"
                  f"stick with the information provided dont assume things and use try and except block with proper error handeling"
                  f"print the answer for query asked"
                  f"Here is the information about the data: {self.get_data_info()}. "
                  f"Solve the query given to you.")

        generated_code = self.llm.model(prompt)
        pattern = r"```(?:\w+)?\n(.*?)```"
        generated_code = re.findall(pattern, generated_code, re.DOTALL)
        generated_code = "\n".join(generated_code)
        return generated_code

    def generate_code(self, query, history):
        # Craft the prompt using the query and data information
        history = "".join(history)
        prompt = (f"your job is to write code without any explanation or comments for the queries asked. "
                  f"Try to write it in a way that will not generate any error. If you want to access the data, "
                  f"it's stored in the 'data' variable by default. Here is the query: {query} {history}."
                  f"Only makes graphs if they are necessary or asked in queries. try to use the same data variable to hold new data "
                  f"dont display any graph save all the images or graphs in the graphs directory which is alredy created for you, the name for the graph should be its discription in detail, donot print confirmation regarding saving graph"
                  f"stick with the information provided dont assume things and use try and except block with proper error handeling"
                  f"print the answer for query asked"
                  f"Here is the information about the data: {self.get_data_info()}. "
                  f"Solve the query given to you."
                  )
        
        # Get the response from the LLM
        generated_code = self.llm.model(prompt)
        pattern = r"```(?:\w+)?\n(.*?)```"
        generated_code = re.findall(pattern, generated_code, re.DOTALL)
        generated_code = "\n".join(generated_code)
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
    
    def REgenerate_plan(self, query):
        # Ask the AI to create a detailed plan with phases
        prompt = (f"Your job is to create a detailed plan to solve the following query in phases. "
                  f"Each phase should depend on the results of the previous phase. "
                  f"Here is the query: {query}. if you want to use data its in data variable pandas dataframe"
                  f"this plan will be for other ai agen no need to perform things that are visually appling like rename etc . make sure the plan does what it wants in less phase"
                  f"dont plan for things that are alredy provided like datatype and rest"
                  f"Here is the information about the data: {self.get_data_info()} and here is sample {self.data.head()}. "
                  f"avoid mentioning the phase to run by getting column name this causes plobrem if they are not exactly same, encorage use of index"
                  f"Break down the problem logically, and ensure all dependencies are clear.")
    
        self.full_plan = self.llm.model(prompt)
        return self.full_plan
    
    def REgenerate_code(self, current_phase, previous_result, history):
        # Provide the AI with the current phase, full plan, and history
        prompt = (f"Your job is to generate error-free code for the current phase of execution. "
                  f"Here is the current phase number: {current_phase}. "
                  f"Here is the full plan:\n{self.full_plan}. "
                  f"Here is the history of previous phases (queries and results): {history}. "
                  f"Here is the result from the previous phase: {previous_result}. "
                  f"you can find the data in data variable pandas dataframe. you can only use this variable so alter the same data dont create new variabl like cleaned_data etc."
                  f"Here is the information about the data: {self.get_data_info()}, here is samples {self.data.head()}. "
                  f"avoid calling the column by names call if possible, and that means not getting indexes"
                  f"if the current phase is more than the phase listed in plan or if you think the results obtained by previous hase execution contains the right answer print the humanised conclusion and comment satisfied in either case."
                  f"Generate code to execute this phase, and include print statements to display the results.")
        
        # Get the response from the LLM
        generated_code = self.llm.model(prompt)
        pattern = r"```(?:\w+)?\n(.*?)```"
        generated_code = re.findall(pattern, generated_code, re.DOTALL)
        print(current_phase,generated_code)
        return "\n".join(generated_code)
    
    def REexecute_code(self, generated_code):
        # Initialize the result variable to capture output
        data = self.data
        result = io.StringIO()

        # Define a custom print function to capture output
        def custom_print(*args, **kwargs):
            print_output = " ".join(map(str, args)) + "\n"
            result.write(print_output)

        # Temporarily override the built-in print function inside the exec context
        exec_globals = globals().copy()
        exec_globals['print'] = custom_print
        exec_globals['data'] = self.data

        # Execute the generated code in this modified environment
        exec(generated_code, exec_globals)

        # Update the internal data object if modified
        self.data = exec_globals['data']

        # Return the accumulated result
        execution_result = result.getvalue()

        # Check for a satisfaction signal
        
        comments = [line.strip() for line in generated_code.splitlines() if line.strip().startswith("#")]
        is_satisfied = any("satisfied" in comment.lower() for comment in comments)

        return execution_result, is_satisfied
    


    def result_to_natural(self, query, res, code):
        prompt = f"your job is to make user understand the result in natural language this maybe for someone non technical keep, please provide inference for the recived result for query in minimum words tell the user what result is not explain the result, here is code: {code}, query: {query}, result: {res}"
        result = self.llm.model(prompt)
        return result

