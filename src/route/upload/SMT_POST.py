import os
import pytz
from datetime import datetime
from flask import request, jsonify
from werkzeug.utils import secure_filename

from function.db import get_db
from function.isIPYNB import isIPYNB
from function.loadconfig import UPLOAD_FOLDER
from function.isLock import isLock
import function.grader as grader

gmt_timezone = pytz.timezone('Asia/Bangkok')

def delete_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)
        return True
    return False

def main():
    conn = get_db()
    cursor = conn.cursor()
    
    UID = request.form.get("Email").split('@')[0]
    uploaded_file = request.files["file"]
    QID = request.form.get("QID") 

    upload_time = datetime.now(gmt_timezone)
    
    if not isIPYNB(uploaded_file.filename):
        return jsonify({
            'success': False,
            'msg': 'Upload file must be .ipynb',
            'data': {}
        }), 200
    
    if QID is None:
        return jsonify({
            'success': False,
            'msg': "QID is missing in the request",
            'data': {}
        }), 400

    try:
        # Query to select LID, QID, and CSYID from question where QID = %s
        select_query = "SELECT LID, QID, CSYID, SourcePath, MaxScore FROM question WHERE QID = %s"
        cursor.execute(select_query, (QID,))
        result = cursor.fetchone()

        if isLock(conn, cursor, result[0]):
            return jsonify({
                'success': False,
                'msg': 'This question is no longer accepting answers.',
                'data': {}
            }), 200


        q_query = "SELECT QID FROM question WHERE LID = %s"
        cursor.execute(q_query, (result[0],))
        q = cursor.fetchone()

        if not result:
            return jsonify({
                'success': False,
                'msg': f'Question with QID {QID} not found.',
                'data': {}
            }), 404

        LID = result[0]
        fQID = q.index(result[1])+1
        QID = result[1]
        CSYID = result[2]
        Source = result[3]
        MaxScore = result[4]

        # Query to select additional files (addfile) paths related to LID
        select_query = "SELECT Path FROM addfile WHERE LID = %s"
        cursor.execute(select_query, (LID,))
        result = cursor.fetchall()

        addfiles = [row[0] for row in result]
        
        # Path = <CSYID>/<LID>/TurnIn/(filename)

        if uploaded_file.filename != "":
            filename = secure_filename(uploaded_file.filename)        
            filename = f"{UID}-L{LID}-Q{fQID}-{CSYID}{os.path.splitext(uploaded_file.filename)[1]}"

            # Check and create directories if they don't exist
            smtdirec = os.path.join(UPLOAD_FOLDER, str(CSYID), str(LID), 'TurnIn')
            if not os.path.exists(smtdirec):
                os.makedirs(smtdirec)

            filepath = os.path.join(smtdirec, filename)

            uploaded_file.save(filepath)

            err, data = grader.grade(Source, filepath, addfile=addfiles, validate=False, check_keyword="ok")
            if err:
                return jsonify({
                    'success': False,
                    'msg': f'There is a problem while grading.\n{data}',
                    'data': {}
                }), 200
            
            s, m = 0, 0

            if len(data) == 1:
                s += float(data[0][0])  # Ensure data is converted to float
                m += float(data[0][1])  # Ensure data is converted to float
            else:
                for j in range(len(data)):
                    s += float(data[j][0])  # Ensure data is converted to float
                    m += float(data[j][1])  # Ensure data is converted to float

            # Check if m is zero to avoid division by zero
            if m == 0:
                Score = 0
            else:
                Score = float("{:.2f}".format((s / m) * float(MaxScore)))  # Ensure MaxScore is converted to float

            # Check if a submission already exists for this UID, LID, QID, CSYID
            select_query = """
                SELECT SummitedFile FROM submitted
                WHERE UID = %s AND LID = %s AND QID = %s AND CSYID = %s
            """
            cursor.execute(select_query, (UID, LID, QID, CSYID))
            existing_row = cursor.fetchone()

            if existing_row:
                # Delete the existing file and row
                existing_file = existing_row[0]
                delete_file(existing_file)

                delete_query = """
                    DELETE FROM submitted
                    WHERE UID = %s AND LID = %s AND QID = %s AND CSYID = %s
                """
                cursor.execute(delete_query, (UID, LID, QID, CSYID))
                conn.commit()

            # Insert the new submission record
            insert_query = """
                INSERT INTO submitted (UID, LID, QID, SummitedFile, Score, Timestamp, CSYID)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (UID, LID, QID, filepath, Score, upload_time, CSYID))
            conn.commit()

            return jsonify({
                'success': True,
                'msg': "Record inserted successfully",
                'data': {}
            }), 200
        
        else:
            return jsonify({
                'success': False,
                'msg': 'No file uploaded.',
                'data': {}
            }), 400

    except Exception as e:
        # Handle any exceptions during file saving or database operations
        print(f"Error saving file: {e}")
        return jsonify({"message": "An error occurred while processing the request."}), 500
