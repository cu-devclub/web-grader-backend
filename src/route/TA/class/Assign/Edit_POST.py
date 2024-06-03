import os
import pytz
import json
from datetime import datetime
from flask import request, jsonify

from function.db import get_db
from function.GetCID import GetCID
from function.GetGID import GetGID
from function.loadconfig import UPLOAD_FOLDER

gmt_timezone = pytz.timezone('GMT')

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
            # Update existing question
            current_qid, current_source_path, current_release_path = existing_questions[i]
            
            # Check if source path has changed and remove old file if needed
            if source_path and current_source_path and source_path != current_source_path:
                if os.path.exists(current_source_path):
                    os.remove(current_source_path)
                source_files[str(i)].save(source_path)
            else:
                source_path = current_source_path

            # Check if release path has changed and remove old file if needed
            if release_path and current_release_path and release_path != current_release_path:
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
        else:
            print(source_path)
            print(release_path)
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


def main():
    conn = get_db()
    cursor = conn.cursor()

    form = request.form

    try:
        Source_files = {k.replace("Source", ""):v for k, v in request.files.items() if k.startswith("Source")}
        Release_files = {k.replace("Release", ""):v for k, v in request.files.items() if k.startswith("Release")}
        Additional_files = [v for k, v in request.files.items() if k.startswith("Add")]

        # Path = <CSYID>/<LID>/(Addi)
        # Path = <CSYID>/<LID>/Source_(index)_(Source)
        # Path = <CSYID>/<LID>/Release_(index)_(Release)
        
        seleted = [GetGID(conn, cursor, i, form["CSYID"]) if form["IsGroup"] else GetCID(conn, cursor, i, form["CSYID"]) for i in form["Selected"].split(",")]

        # addLab = f"INSERT INTO lab (Lab, Name, Publish, Due, {"GID" if form["IsGroup"] else "CID"}, CSYID, Creator) VALUES " + "(%s, %s, %s, %s, %s, %s, %s)"
        setLab = """
            UPDATE 
                lab
            SET 
                Lab = %s,
                Name = %s,
                Publish = %s,
                Due = %s,
                """ + f"{"GID" if form["IsGroup"] else "CID"}" + """ = %s
            WHERE 
                LID = %s;
        """
        cursor.execute(setLab, (form["LabNum"], form["LabName"], form["PubDate"], form["DueDate"], str(seleted).replace(" ", ""), form["LID"]))
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


    # try:
    #     conn = get_db()
    #     cursor = conn.cursor()
        
    #     Creator = request.form.get('Creator') #no change
    #     CSYID = request.form.get('CSYID') #no change
    #     Create_time = datetime.now(gmt_timezone) #no change
        
    #     oldLabNum = request.form.get('oldlabNum')
        
        
    #     LabNum = request.form.get('labNum')
    #     LabName = request.form.get('labName')
    #     Question = json.loads(request.form.get('Question'))
    #     submittedDates = json.loads(request.form.get('submittedDates'))
        

    #     #check lab exist
    #     select_lab_query = "SELECT Lab,Name,CSYID FROM lab WHERE Lab = %s AND CSYID = %s"
    #     cursor.execute(select_lab_query, (LabNum, CSYID))
    #     exist_lab = cursor.fetchone()
    #     print(exist_lab)
        
    #     #update lab
    #     print("askdcpoaskcdpasokdcpoasdkcpasdokcpasdokcasdodckdaspodck")
    #     update_lab_query = """ UPDATE lab SET Lab = %s,Name = %s WHERE Lab = %s AND CSYID = %s """
        
    #     cursor.execute(update_lab_query, (LabNum, LabName, oldLabNum, CSYID))
    #     print("askdcpoaskcdpasokdcpoasdkcpasdokcpasdokcasdodckdaspodck")
    #     #update Question
    #     try:
    #         for question_data in Question:
    #             question_id = question_data['id']
    #             score = question_data['score']
    #             # Insert question data into the database
    #             insert_question_query = """ 
    #                 INSERT INTO question (Creator, Lab, Question, MaxScore, LastEdit, CSYID)
    #                 VALUES (%s, %s, %s, %s, %s, %s) AS new
    #                 ON DUPLICATE KEY UPDATE MaxScore = new.MaxScore,LastEdit = new.LastEdit
    #             """
    #             cursor.execute(insert_question_query, (Creator, LabNum, question_id, score, Create_time, CSYID))
    #             maxQuestion = question_id
        
    #     except mysql.connector.Error as error:
    #         conn.rollback()
    #         return jsonify({"error": f"An error occurred: {error}","Status":False}), 500
    #     #delete unuse Question
    #     try:
    #         delete_question_query = """ 
    #                 DELETE QST FROM question QST WHERE QST.Lab = %s AND QST.CSYID = %s AND QST.Question > %s
    #             """
    #         cursor.execute(delete_question_query, (LabNum, CSYID, maxQuestion))
                
    #     except mysql.connector.Error as error:
    #             conn.rollback()
    #             return jsonify({"error": f"An error occurred: {error}","Status":False}), 500
    #     #delete old assign
    #     try:
    #         delete_assign_query = """ 
    #                 DELETE ASN FROM assign ASN WHERE ASN.Lab = %s AND ASN.CSYID = %s
    #             """
    #         cursor.execute(delete_assign_query, (LabNum, CSYID))
            
    #     except mysql.connector.Error as error:
    #         conn.rollback()
    #         return jsonify({"error": f"An error occurred: {error}","Status":False}), 500
        
    #     #assign to section
    #     try:
    #         for section, dates in submittedDates.items():
    #             Publish = dates['publishDate']
    #             Due = dates['dueDate']
    #             CID = GetCID(conn,cursor,section,CSYID)
    #             insert_assignTo = """ INSERT INTO assign (Lab,Publish,Due,CID,CSYID) VALUES(%s,%s,%s,%s,%s) """
    #             cursor.execute(insert_assignTo,(LabNum,Publish,Due,CID,CSYID))
    #     except mysql.connector.Error as error:
    #         conn.rollback()
    #         return jsonify({"error": f"An error occurred: {error}","Status":False}), 500
    #     conn.commit()
    #     return jsonify({"message":"create success","Status":True}), 200
        
    # except mysql.connector.Error as error:
    #     conn.rollback()
    #     return jsonify({"error": f"An error occurred: {error}","Status":False}), 500