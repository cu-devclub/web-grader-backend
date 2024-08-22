import os
import csv
import json
from flask import request, jsonify, g

from function.db import get_db
from function.isCSV import isCSV
from function.loadconfig import UPLOAD_FOLDER
from function.AddUserGrader import AddUserGrader
from function.isCET import isCET

from flask_jwt_extended import jwt_required, get_jwt_identity

@jwt_required()
def main():
    Email = get_jwt_identity()['email']
    connection = get_db()

    CSYID = request.form.get("CSYID")
    uploaded_CSV = request.files["file"]

    if(not isCET(g.db, g.db.cursor(), Email, CSYID)):
        return jsonify({
            'success': False,
            'msg': "You don't have permission",
            'data': {}
        }), 200

    if not CSYID or not Email or not uploaded_CSV:
        return jsonify({'success': False, 'msg': 'Missing data'})

    # Check path and save the uploaded file
    csvdirec = os.path.join(UPLOAD_FOLDER, 'CSV')
    if not os.path.exists(csvdirec):
        os.makedirs(csvdirec)

    filename = uploaded_CSV.filename
    if not isCSV(filename):
        return jsonify({"message": "upload file must be .CSV"}), 500 

    filepath = os.path.join(csvdirec, f"{CSYID}.csv")
    try:
        uploaded_CSV.save(filepath)
    except Exception as e:
        return jsonify({"success": False, "msg": f"Failed to save file: {str(e)}"}), 500 

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM classeditor WHERE Email=%s AND CSYID=%s", (Email, CSYID))
            if cursor.rowcount == 0:
                return jsonify({'success': False, 'msg': 'Email not authorized for this class'})

            # Read CSV file from saved location
            with open(filepath, 'r', encoding='utf-8') as file:
                csv_reader = csv.DictReader(file)


                if 'Group' in csv_reader.fieldnames:
                    # Validate groups in CSV
                    groups = {row['Group'] for row in csv_reader}

                    if ('' in groups or '-' in groups) and ('' in groups and '-' in groups):
                        return jsonify({'success': False, 'msg': 'Invalid group data\nPlease ensure that there are no empty rows in your CSV file.'})

                # Reset csv reader
                file.seek(0)
                csv_reader = csv.DictReader(file)

                # fetch current list of student in class to check who to delete
                cursor.execute("SELECT UID FROM student WHERE CSYID=%s", (CSYID))
                current_student = list(cursor.fetchall())

                # Process CSV and update the database
                for row in csv_reader:
                    student_id = row['ID']
                    if (str(student_id).strip(),) in current_student:
                        current_student.remove((str(student_id).strip(),))
                    section = row['Section']
                    group = row['Group'] if 'Group' in csv_reader.fieldnames else "-"
                    student_Name = row['Name (English)']

                    # Fetch CID for section
                    cursor.execute("SELECT CID FROM section WHERE CSYID=%s AND Section=%s", (CSYID, section))
                    section_data = cursor.fetchone()
                    if section_data:
                        CID = section_data[0]  # Access by index
                    else:
                        cursor.execute("INSERT INTO section (CSYID, Section) VALUES (%s, %s)", (CSYID, section))
                        CID = cursor.lastrowid

                    # Fetch GID for group
                    if group not in ['', '-']:
                        cursor.execute("UPDATE class SET useGroup=%s WHERE CSYID=%s", (1, CSYID))
                        cursor.execute("SELECT GID FROM `group` WHERE CSYID=%s AND `Group`=%s", (CSYID, group))
                        group_data = cursor.fetchone()
                        if group_data:
                            GID = group_data[0]  # Access by index
                        else:
                            cursor.execute("INSERT INTO `group` (CSYID, `Group`) VALUES (%s, %s)", (CSYID, group))
                            GID = cursor.lastrowid
                    else:
                        GID = None
                        cursor.execute("UPDATE class SET useGroup=%s WHERE CSYID=%s", (0, CSYID))

                    # insert user to grader
                    AddUserGrader(connection, cursor, student_id, student_id + f"@{'student.' if student_id.isnumeric() else ''}chula.ac.th", student_Name)

                    # Check if student exists and update or insert
                    cursor.execute("SELECT * FROM student WHERE UID=%s AND CSYID=%s", (student_id, CSYID))
                    student_data = cursor.fetchone()
                    if student_data:
                        if student_data[1] != CID or student_data[4] != GID:  # Adjust index based on column position
                            cursor.execute("UPDATE student SET CID=%s, GID=%s WHERE UID=%s AND CSYID=%s", (CID, GID, student_id, CSYID))
                    else:
                        cursor.execute("INSERT INTO student (CID, UID, CSYID, GID) VALUES (%s, %s, %s, %s)", (CID, student_id, CSYID, GID))

                # remove remain student that doesn't show in new csv
                cursor.executemany("DELETE FROM student WHERE UID=%s AND CSYID=%s", [(i[0], CSYID) for i in current_student])


                connection.commit()
                return jsonify({'success': True, 'msg': 'CSV processed successfully'})
    except Exception as e:
        connection.rollback()
        return jsonify({'success': False, 'msg': str(e)})