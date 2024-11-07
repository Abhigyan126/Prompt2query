import mysql.connector
from llm import LLM
import re

# Initialize LLM and MySQL connection
llm = LLM()
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="jain@123"
)

result_hist = ''
code_hist = ''
# Define the task message for the LLM
message = 'find schema and tables along with attributes for education database'

# Generate the SQL query using the LLM model
def rec(message):
    prompt = f'you are a worker in a factory, Your job is to write clean SQL queries each query should be in one line for MySQL for the task described: {message}.you can use a method by writing REC folllowed by the message you want to tell other worker so he can finish the job you can do this in situation where data is not provided and for the completion of the task side query is required, in situation like where i ask you to do somthing for example insert data into table and you dont have schema information generate a query to first find that information in this case schma like table name etc and its attributes then let the other worker handle rest you can do this by writing a REC ''message to worker'' so the next worker handles th rest of the job, but you need to give the worker result in this case schema so generate code for schema then rec. worker cannot comment or use anything other than rec the moment re is detected job will be forworded to next worker' 
    global result_hist, code_hist
    reply = llm.model(prompt)
    print(reply)

    # Extract the SQL code from the LLM's response
    pattern = re.compile(r'```sql(.*?)```', re.DOTALL)
    matches = pattern.findall(reply)

    if matches:
        # Clean the extracted SQL query
        sql_query = matches[0]
        # Remove single-line comments
        sql_query = re.sub(r'--.*', '', sql_query)
        # Remove multi-line comments
        sql_query = re.sub(r'/\*.*?\*/', '', sql_query, flags=re.DOTALL)
        # Remove backslashes and unnecessary characters
        sql_query = re.sub(r'\\n', '\n', sql_query)
        sql_query = re.sub(r'\\', '', sql_query).strip()
    else:
        print("No SQL code found in the LLM's reply.")
        sql_query = ''

    print(sql_query)

    try:
        # Execute each SQL command in the query
        cursor = mydb.cursor()
        for statement in sql_query.split(';'):
            statement = statement.strip()
            if statement:
                cursor.execute(statement)
                # Commit the transaction if it's a DML statement (e.g., INSERT)
                if statement.lower().startswith(('insert', 'update', 'delete')):
                    mydb.commit()
                    print("Transaction committed.")
                # Fetch results if the query is a SELECT statement
                if statement.lower().startswith('select'):
                    result = cursor.fetchall()
                    for row in result:
                        print(row)
        
        cursor.close()
    except mysql.connector.Error as err:
        print(f"Error: {err}")

    finally:
        mydb.close()
rec(message)