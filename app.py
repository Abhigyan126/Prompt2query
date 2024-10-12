from flask import Flask, request, jsonify
from flask_cors import CORS
from llm_pandas import LLMHandler  # Import your LLMHandler class here
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests

# Initialize the LLMHandler object (adjust as necessary for your app)
lh = LLMHandler()

# Define the route for file upload and query processing
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file provided. Please upload a file.", 400

    file = request.files['file']
    
    if file.filename == '':
        return "No file selected. Please choose a file to upload.", 400

    # Save the uploaded file temporarily
    file_path = os.path.join("/tmp", file.filename)
    file.save(file_path)

    try:
        # Load the file into the LLMHandler
        lh.load_data(file_path)
        return "File uploaded and data loaded successfully."
    except Exception as e:
        return f"An error occurred while loading the file: {str(e)}", 500
    finally:
        os.remove(file_path)  # Remove the file after processing


# Define the route for handling queries
@app.route('/query', methods=['POST'])
def handle_query():
    data = request.get_json()
    query = data.get("query", "")

    if not query:
        return "No query provided", 400

    try:
        # Process the query using LLMHandler
        generated_code = lh.generate_code(query)
        result = lh.execute_code(generated_code)
        
        # Return the result as plain text
        return f"Here is the result of your query: {result}"
    except Exception as e:
        return f"An error occurred: {str(e)}", 500


if __name__ == '__main__':
    app.run(debug=True)
