import os
import pytz
import json
from datetime import datetime
from flask import request, jsonify
from werkzeug.utils import secure_filename

from function.db import get_db
from function.isIPYNB import isIPYNB
from function.loadconfig import UPLOAD_FOLDER, config
from function.isLock import isLock
import function.grader as grader

from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives import serialization
from binascii import unhexlify

gmt_timezone = pytz.timezone('Asia/Bangkok')

def delete_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)
        return True
    return False

from flask_jwt_extended import jwt_required, get_jwt_identity

@jwt_required()
def main():
    Email = get_jwt_identity()['email']
    conn = get_db()
    cursor = conn.cursor()
    
    UID = Email.split('@')[0]
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

        query = """
            SELECT 
                CASE 
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
                    ) 
                    THEN 1 
                    ELSE 0 
                END AS access;
        """
        cursor.execute(query, (Email, QID))
        # Fetch access result
        data = cursor.fetchone()

        if not bool(int(data[0])):
            return jsonify({
                'success': False,
                'msg': "You don't have permission to this question",
                'data': {}
            }), 200

        # Query to select LID, QID, and CSYID from question where QID = %s
        select_query = """
            SELECT 
                q.LID, 
                q.QID, 
                q.CSYID, 
                q.SourcePath, 
                q.MaxScore,
                CASE
                    WHEN CONVERT_TZ(NOW(), '+00:00', '+07:00') >= LAB.Publish THEN 1
                    ELSE 0
                END AS Pub
            FROM 
                question q
                JOIN lab LAB ON q.LID = LAB.LID
            WHERE 
                q.QID = %s
        """
        cursor.execute(select_query, (QID,))
        result = cursor.fetchone()

        if isLock(conn, cursor, result[0]):
            return jsonify({
                'success': False,
                'msg': 'This question is no longer accepting answers.',
                'data': {}
            }), 200
        
        if(not bool(int(result[5]))):
            return jsonify({
                'success': False,
                'msg': 'This question is not available yet.',
                'data': {}
            }), 200


        q_query = "SELECT QID FROM question WHERE LID = %s"
        cursor.execute(q_query, (result[0],))
        q = cursor.fetchall()

        if not result:
            return jsonify({
                'success': False,
                'msg': f'Question with QID {QID} not found.',
                'data': {}
            }), 404

        LID = result[0]
        fQID = q.index((result[1],))+1
        QID = result[1]
        CSYID = result[2]
        Source = result[3]
        MaxScore = result[4]

        # Query to select additional files (addfile) paths related to LID
        select_query = "SELECT Path FROM addfile WHERE LID = %s"
        cursor.execute(select_query, (LID,))
        result = cursor.fetchall()

        addfiles = [row[0] for row in result]

        select_query = "SELECT Lab FROM lab WHERE LID = %s"
        cursor.execute(select_query, (LID,))
        resultLab = cursor.fetchone()
        
        # Path = <CSYID>/<LID>/TurnIn/(filename)

        if uploaded_file.filename == "":
            return jsonify({
                'success': False,
                'msg': 'No file uploaded.',
                'data': {}
            }), 400
        
        filename = secure_filename(uploaded_file.filename)     
        OriginalFileName = filename 
        filename = f"{UID}-L{resultLab[0]}-Q{fQID}{os.path.splitext(uploaded_file.filename)[1]}"

        # Check and create directories if they don't exist
        smtdirec = os.path.join(UPLOAD_FOLDER, str(CSYID), str(LID), 'TurnIn')
        if not os.path.exists(smtdirec):
            os.makedirs(smtdirec)

        filepath = os.path.join(smtdirec, filename)

        uploaded_file.save(filepath)

        encrypted_message_str = None
        with open(filepath, 'r', encoding='utf-8') as file:
            try:
                encrypted_message_str = json.loads(file.read())["metadata"]["BondSan"]
            except Exception as e:
                encrypted_message_str = None



        if encrypted_message_str is not None:
            try:
                private_key = serialization.load_pem_private_key(config["PRIKEY"].encode('utf-8'), password=None)

                # Convert the encrypted message back from hex string
                encrypted_message = unhexlify(encrypted_message_str)

                # Decrypt the message
                decrypted_message = private_key.decrypt(
                    encrypted_message,
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                ).decode("utf-8")
            except Exception as e:
                decrypted_message = ""

        if encrypted_message_str is not None:
            DMS = decrypted_message.split("_")

        if encrypted_message_str is None:
            sus_query = """
                INSERT INTO `suspicious` (`UID`, `LID`, `QID`, `Type`, `Message`, `Timestamp`)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    `Message` = VALUES(Message),
                    `Timestamp` = VALUES(Timestamp)
            """

            cursor.execute(sus_query, (UID, LID, QID, 1, "File that user upload is not contain signature.", upload_time))
            conn.commit()

        elif len(DMS) != 3:
            sus_query = """
                INSERT INTO `suspicious` (`UID`, `LID`, `QID`, `Type`, `Message`, `Timestamp`)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    `Message` = VALUES(Message),
                    `Timestamp` = VALUES(Timestamp)
            """

            cursor.execute(sus_query, (UID, LID, QID, 2, "Signature is not valid.", upload_time))
            conn.commit()

        elif UID == DMS[0] and LID == int(DMS[1]) and QID == int(DMS[2]):
            pass

        elif UID != DMS[0]:
            sus_query = """
                INSERT INTO `suspicious` (`UID`, `LID`, `QID`, `Type`, `Message`, `Timestamp`)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    `Message` = VALUES(Message),
                    `Timestamp` = VALUES(Timestamp)
            """

            cursor.execute(sus_query, (UID, LID, QID, 3, f"Owner of this file is {decrypted_message.split('_')[0]}.", upload_time))
            conn.commit()

        elif LID != int(DMS[1]) or QID != int(DMS[2]):
            sus_query = """
                INSERT INTO `suspicious` (`UID`, `LID`, `QID`, `Type`, `Message`, `Timestamp`)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    `Message` = VALUES(Message),
                    `Timestamp` = VALUES(Timestamp)
            """

            cursor.execute(sus_query, (UID, LID, QID, 4, "This signature is from different question.", upload_time))
            conn.commit()

        else:
            sus_query = """
                INSERT INTO `suspicious` (`UID`, `LID`, `QID`, `Type`, `Message`, `Timestamp`)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    `Message` = VALUES(Message),
                    `Timestamp` = VALUES(Timestamp)
            """

            cursor.execute(sus_query, (UID, LID, QID, 5, "There is problem with signature.", upload_time))
            conn.commit()
            

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

        # Define the insert or update query
        upsert_query = """
            INSERT INTO submitted (UID, LID, QID, SummitedFile, Score, Timestamp, CSYID, OriginalName)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                SummitedFile = VALUES(SummitedFile),
                Score = VALUES(Score),
                Timestamp = VALUES(Timestamp),
                OriginalName = VALUES(OriginalName)
        """

        # Execute the query with the provided values
        cursor.execute(upsert_query, (UID, LID, QID, filepath, Score, upload_time, CSYID, OriginalFileName))
        conn.commit()          

        return jsonify({
            'success': True,
            'msg': "Record inserted successfully",
            'data': {}
        }), 200

    except Exception as e:
        print(e)
        return jsonify({
            'success': False,
            'msg': 'Please contact admin.',
            'data': e
        }), 200
