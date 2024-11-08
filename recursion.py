import pandas as pd
import io
import numpy as np
import time

# Assuming LLM is some custom class that generates a response
from llm import LLM
llm = LLM()

buffer = io.StringIO()

# Load data
data = pd.read_csv('heart.csv')

# Capture info
data.info(buf=buffer)
info_str = buffer.getvalue()

# Initialize history and result
history = ''
result = ''
count_rec = 0
max_recursions = 3

def rec(message):
    global history, result, count_rec, max_recursions
    
    prompt = (f"Your job is to write code without any explanation or comments for the queries asked."
              f"Try to write it in a way that will not generate any error. If you want to access the data, it's stored in the data variable by default. "
              f"Here are the queries: {message}. Here is the information about the data, which is in the data variable: {info_str}. "
              f"If you want to print something out, just append it to the result i will run the code and word to word copy paste with my rest code so when you call same function it will be like taking to the future"
              f"Solve the query given to you. If necessary, you can call the recursive function by generating "
              f"the code with the following signature: rec(updated_prompt) at the end of the code so when exec is run this function is called, "
    )
    count_rec += 1
    print(f"Recursion Count: {count_rec}")
    
    # Generate code from LLM
    text = llm.model(prompt)
    
    # Extract generated code from text
    generated_code = text[9:len(text)-3]
    
    # Log the generated code
    history += f"\nGenerated Code:\n{generated_code}\n"
    print(history)
    time.sleep(10)
    
    try:
        # Execute the generated code
        exec(generated_code)
    except Exception as e:
        # Capture any errors and log them
        error_message = f"Error: {str(e)}"
        print(error_message)
        result += error_message
        history += f"\nResult:\n{error_message}\n"
        
        # Force a recursion in case of an error, limit the number of recursions
        if count_rec < max_recursions:
            updated_prompt = (f"{message}. It seems there was an error ('{str(e)}'). Re-attempt by refining your code, "
                              "and ensure it handles the data correctly.")
            rec(updated_prompt)
        else:
            history += "\nMax recursion limit reached. No further analysis will be attempted.\n"
    else:
        # Log successful result
        history += f"\nResult:\n{result}\n"
        

# Initial prompt
message = ('perform in-depth analysis, figure out everything yourself, print the results you find, and recurse until you feel satisfied. '
           'Ensure to try recursion at least once if needed, especially in case of any errors.')

# Start the process
rec(message)
print(f"Final result: {result}")
