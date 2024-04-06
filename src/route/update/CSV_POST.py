from flask import request, jsonify
from werkzeug.utils import secure_filename
import os
from function.db import get_db
import csv
from function.AddUserClass import AddUserClass
from function.AddUserGrader import AddUserGrader

UPLOAD_FOLDER = "files/"

def main(ClassID, SchoolYear):
    ClassID = request.form.get('ClassID')
    SchoolYear = request.form.get('SchoolYear')
    
    SYFile = SchoolYear.replace("/", "T")
    filename = ClassID + "-" + SYFile + ".csv"

    file_path = os.path.join(UPLOAD_FOLDER,'CSV',filename)
    try:
        dbAUG = get_db()
        cursor = dbAUG.cursor()    
        with open(file_path, newline='') as csvfile:
            reader = csv.reader(csvfile)
            # Skip the header row if it exists
            next(reader, None)
            for row in reader:
                print(row)
                SID, Name, Section = row
                Email = SID + "@student.chula.ac.th"
                AddUserGrader(SID, Email, Name)
                AddUserClass(Email, ClassID, SchoolYear, Section)
                AddUserGrader(dbAUG, cursor, SID, Email, Name)
                AddUserClass(dbAUG, cursor, Email, ClassID, SchoolYear, Section)
    except FileNotFoundError:
        print(f"File {file_path} not found.")
    except Exception as e:
        print("An error occurred:", e)