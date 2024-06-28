import io
import os
import csv
import json
from flask import request, jsonify
from werkzeug.utils import secure_filename

from function.db import get_db
from function.isCSV import isCSV
from function.loadconfig import UPLOAD_FOLDER
from function.AddUserGrader import AddUserGrader

def main():
    connection = get_db()

    CSYID = request.form.get("CSYID")
    Email = request.form.get("Email")
    uploaded_CSV = request.files["file"]

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
                    if ('' in groups or '-' in groups) and not ('' in groups and '-' in groups):
                        return jsonify({'success': False, 'msg': 'Invalid group data'})

                # Reset csv reader
                file.seek(0)
                csv_reader = csv.DictReader(file)

                # Process CSV and update the database
                for row in csv_reader:
                    student_id = row['ID']
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
                        cursor.execute("SELECT GID FROM `group` WHERE CSYID=%s AND `Group`=%s", (CSYID, group))
                        group_data = cursor.fetchone()
                        if group_data:
                            GID = group_data[0]  # Access by index
                        else:
                            cursor.execute("INSERT INTO `group` (CSYID, `Group`) VALUES (%s, %s)", (CSYID, group))
                            GID = cursor.lastrowid
                    else:
                        GID = None

                    # insert user to grader
                    AddUserGrader(connection, cursor, student_id, student_id + "@student.chula.ac.th", student_Name)

                    # Check if student exists and update or insert
                    cursor.execute("SELECT * FROM student WHERE UID=%s AND CSYID=%s", (student_id, CSYID))
                    student_data = cursor.fetchone()
                    if student_data:
                        if student_data[1] != CID or student_data[4] != GID:  # Adjust index based on column position
                            cursor.execute("UPDATE student SET CID=%s, GID=%s WHERE UID=%s AND CSYID=%s", (CID, GID, student_id, CSYID))
                            
                            # Delete submitted records where LID not in student's CID or GID
                            cursor.execute("""
                                SELECT LID FROM lab WHERE CSYID=%s AND (
                                    JSON_CONTAINS(CID, %s, '$') = 0 OR JSON_CONTAINS(GID, %s, '$') = 0
                                )
                            """, (CSYID, json.dumps([CID]), json.dumps([GID])))
                            lab_ids = cursor.fetchall()
                            if lab_ids:
                                lab_ids = [lid[0] for lid in lab_ids]  # Extract LID values

                                # Step 1: Retrieve the SubmittedFile paths
                                query = "SELECT SummitedFile FROM submitted WHERE UID=%s AND LID=%s"
                                file_paths = []
                                for lid in lab_ids:
                                    cursor.execute(query, (student_id, lid))
                                    result = cursor.fetchone()
                                    if result:
                                        file_paths.append(result[0])

                                # Step 2: Delete the files from the directory
                                for file_path in file_paths:
                                    if os.path.exists(file_path):
                                        os.remove(file_path)

                                # Step 3: Delete the records from the database
                                cursor.executemany("DELETE FROM submitted WHERE UID=%s AND LID=%s", [(student_id, lid) for lid in lab_ids])
                    else:
                        cursor.execute("INSERT INTO student (CID, UID, CSYID, GID) VALUES (%s, %s, %s, %s)", (CID, student_id, CSYID, GID))

                connection.commit()
                return jsonify({'success': True, 'msg': 'CSV processed successfully'})
    except Exception as e:
        connection.rollback()
        return jsonify({'success': False, 'msg': str(e)})