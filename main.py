import pandas as pd
import io
import numpy as np

# Assuming LLM is some custom class that generates a response
from llm import LLM
llm = LLM()

buffer = io.StringIO()

# Load data
data = pd.read_csv('heart.csv')

# Capture info
data.info(buf=buffer)
info_str = buffer.getvalue()

# Simulated prompt to LLM
result = ''
message = 'use matplotlib to make graph'
prompt = f"your job is to write code without any explanation or comments for the queries asked try to write it in a way that will not genrate any error if you want to access the data its stored in data variable by default here ar the queries: {message}. here is the information about the data which is in data variable : {data}. if you want to print somthing out just sum it to the result. note your code will automatically be run by exec command but you are not limited by anything. solve the query given to you"

# LLM generates text (simulated here)
text = llm.model(prompt)

# Simulate LLM-generated code execution
generated_code = text[9:len(text)-3]
print(generated_code)
# Execute the code
exec(generated_code)
print(result)