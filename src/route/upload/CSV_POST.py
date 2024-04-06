from flask import request, jsonify
from werkzeug.utils import secure_filename
import os
from route.update.CSV_POST import main as UpdateStudentCSV

UPLOAD_FOLDER = "files/"

def main():
    ClassID = request.form.get("ClassID")
    SchoolYear = request.form.get("SchoolYear")
    SYFile = SchoolYear.replace("/", "T")
    uploaded_file = request.files["file"]
    if uploaded_file.filename != "":
        filename = secure_filename(uploaded_file.filename)
                    
        filename = f"{ClassID}-{SYFile}{os.path.splitext(uploaded_file.filename)[1]}"
        filepath = os.path.join(UPLOAD_FOLDER,'CSV',filename)
        
        try:
            # Save the file
            uploaded_file.save(filepath)
            # Return a success message
            UpdateStudentCSV(ClassID, SchoolYear)
            return jsonify({"Status": True})
        except Exception as e:
            # Handle any exceptions during file saving gracefully
            print("Error saving file: {e}")
            return jsonify({"Status": False}), 500
    return jsonify({'Status': False}), 400