from flask import request, jsonify
from werkzeug.utils import secure_filename
import os

UPLOAD_FOLDER = "files/"

def main():
    uploaded_file = request.files["file"]

    if uploaded_file.filename != "":
        # Securely generate a unique filename
        filename = secure_filename(uploaded_file.filename)
        # Construct the full path to the file
        filepath = os.path.join(UPLOAD_FOLDER,'TurnIn',filename)

        try:
            # Save the file
            uploaded_file.save(filepath)
            # Return a success message
            return jsonify({"message": "File uploaded successfully!"})

        except Exception as e:
            # Handle any exceptions during file saving gracefully
            print("Error saving file: {e}")
            return jsonify({"error": "An error occurred while uploading the file."}), 500