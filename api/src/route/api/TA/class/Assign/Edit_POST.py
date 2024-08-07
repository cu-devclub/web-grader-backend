import os
import pytz
import json
from datetime import datetime
from flask import request, jsonify

from function.db import get_db
from function.GetCID import GetCID
from function.GetGID import GetGID
from function.loadconfig import UPLOAD_FOLDER
from function.isCET import isCET
import function.grader as grader

gmt_timezone = pytz.timezone('Asia/Bangkok')

def update_database(conn, cursor, questions, qnum, source_files, release_files, lid, base_path, CSYID):
    # Fetch existing questions for the given LID, sorted by QID
    cursor.execute('SELECT QID, SourcePath, ReleasePath FROM question WHERE LID = %s ORDER BY QID', (lid))
    existing_questions = cursor.fetchall()
    existing_qnum = len(existing_questions)
    
    # Create the base path if it doesn't exist
    os.makedirs(base_path, exist_ok=True)
    
    # Update or insert questions
    for i in range(qnum):
        question = questions[i]
        qid = question['id']
        max_score = question['score']
        
        # Determine the SourcePath and ReleasePath
        source_path = None
        release_path = None
        
        if str(i) in source_files:
            source_filename = f"Source_{i}_" + source_files[str(i)].filename
            source_path = os.path.join(base_path, source_filename)
        
        if str(i) in release_files:
            release_filename = f"Release_{i}_" + release_files[str(i)].filename
            release_path = os.path.join(base_path, release_filename)
        
        if i < existing_qnum:
            isSourceUpdate = False

            # Update existing question
            current_qid, current_source_path, current_release_path = existing_questions[i]
            
            # Check if source path has changed and remove old file if needed
            if source_path:
                isSourceUpdate = True
                if os.path.exists(current_source_path):
                    os.remove(current_source_path)
                source_files[str(i)].save(source_path)
            else:
                source_path = current_source_path

            # Check if release path has changed and remove old file if needed
            if release_path:
                if os.path.exists(current_release_path):
                    os.remove(current_release_path)
                release_files[str(i)].save(release_path)
            else:
                release_path = current_release_path
                
            cursor.execute('''
                UPDATE question
                SET MaxScore = %s, SourcePath = %s, ReleasePath = %s
                WHERE QID = %s AND LID = %s
            ''', (max_score, source_path, release_path, current_qid, lid))

            if isSourceUpdate:
                select_query = "SELECT Path FROM addfile WHERE LID = %s"
                cursor.execute(select_query, (lid,))
                result = cursor.fetchall()

                addfiles = [row[0] for row in result]

                select_query = """
                    SELECT 
                        `SID`, 
                        `SummitedFile` 
                    FROM 
                        `submitted` 
                    WHERE
                        QID = %s AND LID = %s
                """
                cursor.execute(select_query, (current_qid, lid))
                result = cursor.fetchall()

                for SID, filepath in result:
                    err, data = grader.grade(source_path, filepath, addfile=addfiles, validate=False, check_keyword="ok")
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
                        Score = float("{:.2f}".format((s / m) * float(max_score)))  # Ensure MaxScore is converted to float

                    # Define the insert or update query
                    upsert_query = """
                        UPDATE 
                            `submitted` 
                        SET 
                            `Score` = %s 
                        WHERE 
                            `SID` = %s
                    """

                    # Execute the query with the provided values
                    cursor.execute(upsert_query, (Score, SID))
                    conn.commit()

        else:
            # Ensure source_path and release_path are not None before inserting
            if source_path is None or release_path is None:
                raise ValueError(f"Cannot insert new question with QID {qid}: SourcePath or ReleasePath is None.")
            
            # Save new files
            source_files[str(i)].save(source_path)
            release_files[str(i)].save(release_path)
            
            # Insert new question
            cursor.execute('''
                INSERT INTO question (LID, SourcePath, ReleasePath, MaxScore, LastEdit, CSYID)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (lid, source_path, release_path, str(max_score), datetime.now(gmt_timezone), CSYID))
    
    # Delete excess questions
    if existing_qnum > qnum:
        excess_qids = [qid for qid, _, _ in existing_questions[qnum:]]
        cursor.execute(f'DELETE FROM question WHERE QID IN ({",".join(["%s"]*len(excess_qids))})', excess_qids)
    
    conn.commit()


from flask_jwt_extended import jwt_required, get_jwt_identity

@jwt_required()
def main():
    Email = get_jwt_identity()['email']
    conn = get_db()
    cursor = conn.cursor()

    form = request.form

    if not isCET(conn, cursor, Email, form["CSYID"]):
        jsonify({
            'success': False,
            'msg': "You don't have permission.",
            'data': {}
        }), 200

    try:
        Source_files = {k.replace("Source", ""):v for k, v in request.files.items() if k.startswith("Source")}
        Release_files = {k.replace("Release", ""):v for k, v in request.files.items() if k.startswith("Release")}
        Additional_files = [v for k, v in request.files.items() if k.startswith("Add")]

        # Path = <CSYID>/<LID>/(Addi)
        # Path = <CSYID>/<LID>/Source_(index)_(Source)
        # Path = <CSYID>/<LID>/Release_(index)_(Release)
        
        seleted = [GetGID(conn, cursor, i, form["CSYID"]) if (form["IsGroup"] == 'true') else GetCID(conn, cursor, i, form["CSYID"]) for i in form["Selected"].split(",")]

        GCID = "GID" if (form["IsGroup"] == 'true') else "CID"
        setLab = """
            UPDATE 
                lab
            SET 
                Lab = %s,
                Name = %s,
                Publish = %s,
                Due = %s,
                `Lock` = %s,
                showScoreOnLock = %s,
                """ + GCID + """ = %s
            WHERE 
                LID = %s;
        """
        cursor.execute(setLab, (form["LabNum"], form["LabName"], form["PubDate"], form["DueDate"], form["DueDate"] if form["LOD"] == 'true' else None, 1 if form["ShowOnLock"] == 'true' else 0, str(seleted).replace(" ", ""), form["LID"]))
        conn.commit()

        LID = form["LID"]


        # check path
        AddDirec = os.path.join(UPLOAD_FOLDER, form["CSYID"], LID)
        if not os.path.exists(AddDirec):
            os.makedirs(AddDirec)


        query = """
        SELECT
            ADF.Path
        FROM 
            addfile ADF
        WHERE 
            ADF.LID = %s
        """
        cursor.execute(query, (LID))
        data = cursor.fetchall()

        for i in data:
            os.remove(i[0])

        query = """
        DELETE
        FROM 
            addfile ADF
        WHERE 
            ADF.LID = %s
        """
        cursor.execute(query, (LID))
        conn.commit()


        for i in Additional_files:
            AddPath = os.path.join(AddDirec, i.filename)
            i.save(AddPath)
            addFile = "INSERT INTO addfile (LID, Path, CSYID) VALUES (%s, %s, %s)"
            cursor.execute(addFile, (LID, AddPath, form["CSYID"]))
            conn.commit()

        Question = json.loads(request.form.get('Question'))

        update_database(conn, cursor, Question, int(form["QNum"]), Source_files, Release_files, str(LID), os.path.join(UPLOAD_FOLDER, str(form["CSYID"]), str(LID)), form["CSYID"])
        
        return jsonify({
            'success': True,
            'msg': '',
            'data': ''
        }), 200
    
    except Exception as e:
        print(e)
        conn.rollback()
        return jsonify({
            'success': False,
            'msg': 'Please contact admin',
            'data': e
        }), 200