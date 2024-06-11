import os
import base64
from flask import request, jsonify

def main():
    data = request.get_json()
    filename = data.get('filename')
    
    file_path = os.path.join('files', filename)

    # Ensure the file exists
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404

    # Read the file content
    with open(file_path, 'rb') as file:
        file_content = file.read()

    # Encode the file content to base64
    encoded_file_content = base64.b64encode(file_content).decode('utf-8')
    
    # Construct response data
    response_data = {
        'fileContent': encoded_file_content,
        'fileType': 'application/octet-stream',  # Adjust as needed
        'downloadFilename': 'test.ipynb',
        'additionalInfo': {
            'message': 'Here is your file with additional JSON data.'
        }
    }
    
    return jsonify(response_data)