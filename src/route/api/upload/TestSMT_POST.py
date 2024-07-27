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

    Email = request.form.get("Email")
    UID = Email.split('@')[0]
    uploaded_file = request.files.get("file")
    QID = request.form.get("QID")

    upload_time = datetime.now(gmt_timezone)
    
    if not uploaded_file or not isIPYNB(uploaded_file.filename):
        return jsonify({
            'success': False,
            'msg': 'Upload file must be .ipynb',
            'data': {}
        }), 500

    if not QID:
        return jsonify({
            'success': False,
            'msg': "QID is missing in the request",
            'data': {}
        }), 500

    try:
        # Use prepared statements to prevent SQL injection
        query = """
            SELECT CASE 
                    WHEN EXISTS (
                        SELECT 1
                        FROM user u
                        JOIN student s ON u.UID = s.UID
                        JOIN lab l ON s.CSYID = l.CSYID
                        JOIN question q on q.LID = l.LID
                        WHERE u.Email = %s AND q.QID = %s
                        AND (
                            JSON_CONTAINS(l.CID, CAST(s.CID AS JSON), '$')
                            OR JSON_CONTAINS(l.GID, CAST(s.GID AS JSON), '$')
                        )
                    ) THEN 1 ELSE 0 
                   END AS access;
        """
        cursor.execute(query, (Email, QID))
        data = cursor.fetchone()

        if not data or not bool(int(data[0])):
            return jsonify({
                'success': False,
                'msg': "You don't have permission to this question",
                'data': {}
            }), 500

        select_query = """
            SELECT LID, QID, CSYID, SourcePath, MaxScore 
            FROM question 
            WHERE QID = %s
        """
        cursor.execute(select_query, (QID,))
        result = cursor.fetchone()

        if not result:
            return jsonify({
                'success': False,
                'msg': f'Question with QID {QID} not found.',
                'data': {}
            }), 500

        LID, QID, CSYID, Source, MaxScore = result

        if isLock(conn, cursor, LID):
            return jsonify({
                'success': False,
                'msg': 'This question is no longer accepting answers.',
                'data': {}
            }), 500

        q_query = "SELECT QID FROM question WHERE LID = %s"
        cursor.execute(q_query, (LID,))
        q = cursor.fetchall()

        fQID = q.index((QID,)) + 1

        addfiles_query = "SELECT Path FROM addfile WHERE LID = %s"
        cursor.execute(addfiles_query, (LID,))
        addfiles = [row[0] for row in cursor.fetchall()]

        lab_query = "SELECT Lab FROM lab WHERE LID = %s"
        cursor.execute(lab_query, (LID,))
        resultLab = cursor.fetchone()

        if not resultLab:
            return jsonify({
                'success': False,
                'msg': 'Lab information not found.',
                'data': {}
            }), 500

        if uploaded_file.filename != "":
            filename = secure_filename(uploaded_file.filename)
            OriginalFileName = filename
            filename = f"{UID}-L{resultLab[0]}-Q{fQID}{os.path.splitext(uploaded_file.filename)[1]}"

            smtdirec = os.path.join(UPLOAD_FOLDER, str(CSYID), str(LID), 'TurnIn')
            os.makedirs(smtdirec, exist_ok=True)

            filepath = os.path.join(smtdirec, filename)
            uploaded_file.save(filepath)

            err, data = grader.grade(Source, filepath, addfile=addfiles, validate=False, check_keyword="ok")
            if err:
                return jsonify({
                    'success': False,
                    'msg': f'There is a problem while grading.\n{data}',
                    'data': {}
                }), 500

            s, m = 0, 0
            for score, max_score in data:
                s += float(score)
                m += float(max_score)

            Score = float("{:.2f}".format((s / m) * float(MaxScore))) if m != 0 else 0

            select_query = """
                SELECT SummitedFile 
                FROM submitted 
                WHERE UID = %s AND LID = %s AND QID = %s AND CSYID = %s
            """
            cursor.execute(select_query, (UID, LID, QID, CSYID))
            existing_row = cursor.fetchone()

            if existing_row:
                existing_file = existing_row[0]
                delete_file(existing_file)

                delete_query = """
                    DELETE FROM submitted 
                    WHERE UID = %s AND LID = %s AND QID = %s AND CSYID = %s
                """
                cursor.execute(delete_query, (UID, LID, QID, CSYID))
                conn.commit()

            insert_query = """
                INSERT IGNORE INTO submitted (UID, LID, QID, SummitedFile, Score, Timestamp, CSYID, OriginalName)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (UID, LID, QID, filepath, Score, upload_time, CSYID, OriginalFileName))
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
            }), 500

    except Exception as e:
        print(f"Error saving file: {e}")
        return jsonify({
            'success': False,
            'msg': 'An error occurred while processing the request.',
            'data': {}
        }), 500