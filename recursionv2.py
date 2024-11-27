import pandas as pd
import io
import re
import numpy as np
from llm import LLM  # Assumes you have an LLM class

class PandasRecursionHandler:
    def __init__(self):
        self.llm = LLM()
        self.buffer = io.StringIO()
        self.data = pd.DataFrame()
        self.phase_counter = 1
        self.max_phases = 10
        self.history = [] 
        self.full_plan = ""

    def load_data(self, url):
        try:
            self.data = pd.read_csv(url)
            print(self.data.head())
            return True
        except Exception as e:
            return e

    def get_data_info(self):
        self.data.info(buf=self.buffer)
        return self.buffer.getvalue()

    def generate_plan(self, query):
        # Ask the AI to create a detailed plan with phases
        prompt = (f"Your job is to create a detailed plan to solve the following query in phases. "
                  f"Each phase should depend on the results of the previous phase. "
                  f"Here is the query: {query}. if you want to use data its in data variable pandas dataframe"
                  f"this plan will be for other ai agen no need to perform things that are visually appling like rename etc . make sure the plan does what it wants in less phase"
                  f"dont plan for things that are alredy provided like datatype and rest"
                  f"Here is the information about the data: {self.get_data_info()} and here is sample {self.data.head()}. "
                  f"avoid mentioning the phase to run by getting column name this causes plobrem if they are not exactly same, encorage use of index"
                  f"Break down the problem logically, and ensure all dependencies are clear.")
    
        plan = self.llm.model(prompt)
        return plan

    def generate_code(self, current_phase, previous_result):
        # Provide the AI with the current phase, full plan, and history
        prompt = (f"Your job is to generate error-free code for the current phase of execution. "
                  f"Here is the current phase number: {current_phase}. "
                  f"Here is the full plan:\n{self.full_plan}. "
                  f"Here is the history of previous phases (queries and results): {self.history}. "
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
        print(self.phase_counter,generated_code)
        return "\n".join(generated_code)

    def execute_code(self, generated_code):
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
    def run(self, query):
        # Generate a phase-wise plan
        self.full_plan = self.generate_plan(query)
        print(f"Plan Generated:\n{self.full_plan}\n")
        
        previous_result = ""
        
        while self.phase_counter <= self.max_phases:
            print(f"Executing Phase {self.phase_counter}")
            current_phase_query = f"Phase {self.phase_counter}: {query}"

            try:
                # Generate code for the current phase
                generated_code = self.generate_code(self.phase_counter, previous_result)
                
                # Execute the generated code and capture the result
                phase_result, is_satisfied = self.execute_code(generated_code)
                print(f"Result of Phase {self.phase_counter}:\n{phase_result}\n")

                # Log the phase history
                self.history.append({
                    "phase": self.phase_counter,
                    "query": current_phase_query,
                    "code": generated_code,
                    "result": phase_result
                })

                # Check if AI indicates completion
                if is_satisfied:
                    print(f"AI is satisfied after Phase {self.phase_counter}. Stopping execution.")
                    break

                # Pass result to the next phase
                previous_result = phase_result

            except Exception as e:
                self.phase_counter += 1
                print(f"Error in Phase {self.phase_counter}: {e}")
                break

            # Increment the phase counter
            self.phase_counter += 1

        if self.phase_counter > self.max_phases:
            print("Maximum phases reached without resolution.")

if __name__ == "__main__":
    # Example usage
    handler = PandasRecursionHandler()

    # Load example data
    url = "/Users/abhigyan/Downloads/project/Prompt2query/airtravel.csv"  # Replace with your CSV URL
    if handler.load_data(url):
        print("Data loaded successfully.")
    else:
        print("Failed to load data.")

    # Example query
    query = "Analyze monthly air travel trends and determine peak months."
    handler.run(query)
