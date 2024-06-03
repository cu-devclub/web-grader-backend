import os
import csv
from flask import request, jsonify
from werkzeug.utils import secure_filename

from function.db import get_db
from function.isCSV import isCSV
from function.AddStudent import AddStudent
from function.loadconfig import UPLOAD_FOLDER
from function.AddUserClass import AddUserClass
from function.CreateSection import CreateSection
from function.CreateGroup import CreateGroup
from function.AddUserGrader import AddUserGrader

def main():
    CSYID = request.form.get("CSYID") 
    uploaded_CSV = request.files["file"]
    filename = secure_filename(uploaded_CSV.filename)
    filename = f"{CSYID}{os.path.splitext(uploaded_CSV.filename)[1]}"

    # check path
    csvdirec = os.path.join(UPLOAD_FOLDER, 'CSV')
    if not os.path.exists(csvdirec):
        os.makedirs(csvdirec)

    filepath = os.path.join(csvdirec, filename)
    
    

    if not isCSV(uploaded_CSV.filename):
        return jsonify({"message": "upload file must be .CSV"}), 500 

    try:
        uploaded_CSV.save(filepath)
        try:
            conn = get_db()
            cursor = conn.cursor()
            
            #clear student in class
            clear1_class = """
            DELETE 
                STD 
            FROM 
                student STD
            WHERE 
                STD.CSYID = %s;
            """
            clear2_class = """
            DELETE 
                GRP
            FROM 
                `group` GRP
            WHERE 
                GRP.CSYID = %s;
            """
            cursor.execute(clear1_class, (CSYID))
            cursor.execute(clear2_class, (CSYID))

            
            #read file and add user
            with open(filepath, newline='', encoding="utf-8") as csvfile:
                reader = csv.reader(csvfile)
                dataTitle = next(reader, None)
                # get index of data that we want
                i_Section = dataTitle.index('Section')
                i_UID = dataTitle.index('ID')
                i_Name = dataTitle.index('Name (English)')
                i_Group = dataTitle.index('Group') if 'Group' in dataTitle else None

                maxSection = 1
                for row in reader:
                    Section = row[i_Section]
                    UID = row[i_UID]
                    Name = row[i_Name]
                    Group = row[i_Group] if i_Group != None else None
                    Group = Group if Group != '' and Group != '-' else None
                    # UID, Name, Section = row
                    Email = UID + "@student.chula.ac.th"
                    if Group != None:
                        CreateGroup(conn, cursor, CSYID, Group)
                    CreateSection(conn, cursor, CSYID, Section)

                    AddUserGrader(conn, cursor, UID, Email, Name)
                    AddUserClass(conn, cursor, UID, CSYID, Section, Group)

                    # AddStudent(conn, cursor, UID, Section, CSYID)
                    if(maxSection < int(Section)):
                        maxSection = int(Section)
                #clear unused section
                delete_student_class = """DELETE SCT FROM section SCT WHERE SCT.CSYID = %s AND SCT.Section > %s"""
                cursor.execute(delete_student_class, (CSYID, maxSection))
            
            conn.commit()
            return jsonify({
                'success': True,
                "message": "File uploaded successfully!"
            })
        except FileNotFoundError:
            print(f"File {filepath} not found.")
            return jsonify({
                'success': False,
                "message": "An error occurred while updating the file."
            })
        except Exception as e:
            print("An error occurred:", e)
            return jsonify({
                'success': False,
                "message": "An error occurred while updating the file."
            })
        
    except Exception as e:
        print(f"Error saving file: {e}")
        return jsonify({
            'success': False,
            "message": "An error occurred while uploading the file."
        })