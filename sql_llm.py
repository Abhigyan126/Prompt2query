import mysql.connector
from llm import LLM
import re

class LLMMySQLHandler:
    def __init__(self):
        # Initialize LLM and MySQL connection
        self.llm = LLM()
        self.mydb = None
        self.cursor = None
    def connect(self, host="localhost", user="root", password="jain@123"):
        self.mydb = mysql.connector.connect(
            host=host,
            user=user,
            password=password
        )
        self.cursor = self.mydb.cursor()

    def generate_sql(self, task_message, history):
        # Craft the prompt for the LLM
        prompt = (f"Your job is to write clean SQL queries for MySQL based on the task description. At start of every qery there should be use database name command to select database"
                  f"If the task is not related to SQL, return a comment saying 'Not SQL.' "
                  f"dont ask question use what you have"
                  f"here attached is histry of previous conversation: {history}"
                  f"Here is the task: {task_message}")
        
        # Get the response from the LLM
        reply = self.llm.model(prompt)
        print("reply from llm sql: ", reply)
        
        # Extract the SQL code from the LLM's response using regex
        pattern = re.compile(r'```sql(.*?)```', re.DOTALL)
        matches = pattern.findall(reply)
        
        if matches:
            # Clean the extracted SQL query
            sql_query = matches[0]
            sql_query = re.sub(r'--.*', '', sql_query)  # Remove single-line comments
            sql_query = re.sub(r'/\*.*?\*/', '', sql_query, flags=re.DOTALL)  # Remove multi-line comments
            sql_query = re.sub(r'\\n', '\n', sql_query)  # Replace escaped newlines with real ones
            sql_query = re.sub(r'\\', '', sql_query).strip()  # Remove unnecessary backslashes
            return sql_query
        else:
            return "No SQL code found in the LLM's reply."

    def execute_sql(self, sql_query):
        results = []
        try:
            if not self.mydb.is_connected():
                self.connect()
            # Split and execute each SQL statement
            for statement in sql_query.split(';'):
                statement = statement.strip()
                if statement:
                    self.cursor.execute(statement)
                    # Commit DML (INSERT, UPDATE, DELETE) transactions
                    if statement.lower().startswith(('insert', 'update', 'delete')):
                        self.mydb.commit()
                    # Fetch and store results for SELECT queries
                    elif statement.lower().startswith('select'):
                        result = self.cursor.fetchall()
                        results.extend(result)
                    # Handle commands like USE or SHOW without fetching or committing
                    elif statement.lower().startswith(('use', 'show', 'describe')):
                        result = self.cursor.fetchall()
                        results.extend(result)
        except mysql.connector.Error as err:
            print(f"Error: {err}")
        return results




