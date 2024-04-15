import os
import csv
from flask import request, jsonify
from werkzeug.utils import secure_filename

from function.db import get_db
from function.isCSV import isCSV
from function.loadconfig import UPLOAD_FOLDER
from function.AddUserClass import AddUserClass
from function.CreateSection import CreateSection
from function.AddUserGrader import AddUserGrader

def main():
    CSYID = request.form.get("CSYID") 
    uploaded_CSV = request.files["file"]
    filename = secure_filename(uploaded_CSV.filename)
    filename = f"{CSYID}{os.path.splitext(uploaded_CSV.filename)[1]}"
    filepath = os.path.join(UPLOAD_FOLDER,'CSV',filename)
    
    if not isCSV(uploaded_CSV.filename):
        return jsonify({"message": "upload file must be .CSV"}), 500 

    try:
        uploaded_CSV.save(filepath)
        try:
            conn = get_db()
            cursor = conn.cursor()
            
            #clear student in class
            delete_student_class = """DELETE STD FROM student STD INNER JOIN section SCT ON STD.CID = SCT.CID WHERE SCT.CSYID = %s"""
            cursor.execute(delete_student_class, (CSYID,))

            
            #read file and add user
            with open(filepath, newline='') as csvfile:
                reader = csv.reader(csvfile)
                next(reader, None)
                maxSection = 1
                for row in reader:
                    print(row)
                    UID, Name, Section = row
                    Email = UID + "@student.chula.ac.th"
                    AddUserGrader(conn, cursor, UID, Email, Name)
                    print('AUG<<<<<<<<<<<<<<<<<<<<<<<<')
                    CreateSection(conn, cursor, CSYID, Section)
                    print('CST<<<<<<<<<<<<<<<<<<<<<<<<')
                    AddUserClass(conn, cursor, UID, CSYID, Section)
                    print('AUC<<<<<<<<<<<<<<<<<<<<<<<<')
                    if(maxSection < int(Section)):maxSection = int(Section)
                #clear unused section
                delete_student_class = """DELETE SCT FROM section SCT WHERE SCT.CSYID = %s AND SCT.Section > %s"""
                cursor.execute(delete_student_class, (CSYID,maxSection))
            
            conn.commit()
            return jsonify({"message": "File uploaded successfully!"})
        except FileNotFoundError:
            print(f"File {filepath} not found.")
            return jsonify({"message": "An error occurred while updating the file."}), 500
        except Exception as e:
            print("An error occurred:", e)
            return jsonify({"message": "An error occurred while updating the file."}), 500
        
    except Exception as e:
        print("Error saving file: {e}")
        return jsonify({"message": "An error occurred while uploading the file."}), 500