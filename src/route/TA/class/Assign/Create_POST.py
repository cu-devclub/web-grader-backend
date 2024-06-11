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

def main():
    conn = get_db()
    cursor = conn.cursor()

    form = request.form

    try:

        Source_files = [v for k, v in request.files.items() if k.startswith("Source")]
        Release_files = [v for k, v in request.files.items() if k.startswith("Release")]
        Additional_files = [v for k, v in request.files.items() if k.startswith("Add")]

        # Path = <CSYID>/<LID>/(Addi)
        # Path = <CSYID>/<LID>/Source_(index)_(Source)
        # Path = <CSYID>/<LID>/Release_(index)_(Release)
        
        seleted = [GetGID(conn, cursor, i, form["CSYID"]) if (form["IsGroup"] == 'true') else GetCID(conn, cursor, i, form["CSYID"]) for i in form["Selected"].split(",")]

        GCID = "GID" if (form["IsGroup"] == 'true') else "CID"

        addLab = f"INSERT INTO lab (Lab, Name, Publish, Due, {GCID}, CSYID, Creator) VALUES " + "(%s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(addLab, (form["LabNum"], form["LabName"], form["PubDate"], form["DueDate"], str(seleted).replace(" ", ""), form["CSYID"], form["Creator"]))
        conn.commit()

        LID = str(cursor.lastrowid)


        # check path
        AddDirec = os.path.join(UPLOAD_FOLDER, form["CSYID"], LID)
        if not os.path.exists(AddDirec):
            os.makedirs(AddDirec)

        for i in Additional_files:
            AddPath = os.path.join(AddDirec, i.filename)
            i.save(AddPath)
            addFile = "INSERT INTO addfile (LID, Path, CSYID) VALUES (%s, %s, %s)"
            cursor.execute(addFile, (LID, AddPath, form["CSYID"]))
            conn.commit()


        # addASG = f"INSERT INTO assign (LID, {"GID" if form["IsGroup"] else "CID"}, CSYID) VALUES " + "(%s, %s, %s)"

        # seleted = [GetGID(conn, cursor, i, form["CSYID"]) if form["IsGroup"] else GetCID(conn, cursor, i, form["CSYID"]) for i in form["Selected"].split(",")]
        # # for i in form["Selected"].split(","):
        # cursor.execute(addASG, (LID, str(seleted).replace(" ", ""), form["CSYID"]))
        # conn.commit()


        Question = json.loads(request.form.get('Question'))

        for i in range(int(form["QNum"])):
            PathS = os.path.join(AddDirec, (f"Source_{i}_" + Source_files[i].filename))
            PathR = os.path.join(AddDirec, (f"Release_{i}_" + Release_files[i].filename))
            Source_files[i].save(PathS)
            Release_files[i].save(PathR)
            Qry = "INSERT INTO question (LID, SourcePath, ReleasePath, MaxScore, LastEdit, CSYID) VALUES (%s, %s, %s, %s, %s, %s)"
            cursor.execute(Qry, (LID, PathS, PathR, Question[i-1]["score"], datetime.now(gmt_timezone), form["CSYID"]))
            conn.commit()
        
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
        
    #     Creator = request.form.get('Creator')
    #     LabNum = request.form.get('labNum')
    #     LabName = request.form.get('labName')
    #     CSYID = request.form.get('CSYID')
    #     Question = json.loads(request.form.get('Question'))
    #     submittedDates = json.loads(request.form.get('submittedDates'))
    #     Create_time = datetime.now(gmt_timezone)
        
    #     #check if lab already exist
    #     select_lab_query = "SELECT Lab,Name,CSYID FROM lab WHERE Lab = %s AND CSYID = %s"
    #     cursor.execute(select_lab_query, (LabNum, CSYID))
    #     exist_lab = cursor.fetchone()

    #     if exist_lab:
    #         return jsonify({"message": "Lab already exists. Please select a different Lab number.","Status":1}), 500
    #     else:
    #         #create Lab first
    #         insert_lab_query = "INSERT INTO lab (Lab, Name, CSYID) VALUES (%s, %s, %s)"
    #         cursor.execute(insert_lab_query, (LabNum, LabName, CSYID))

    #         #create Question
    #         for question_data in Question:
    #             try:
    #                 question_id = question_data['id']
    #                 score = question_data['score']
    #                 # Insert question data into the database
    #                 insert_question_query = "INSERT INTO question (Creator, Lab, Question, MaxScore, LastEdit, CSYID) VALUES (%s, %s, %s, %s, %s, %s)"
    #                 cursor.execute(insert_question_query, (Creator, LabNum, question_id, score, Create_time, CSYID))
    #             except mysql.connector.Error as error:
    #                 conn.rollback()
    #                 return jsonify({"error": f"An error occurred: {error}","Status":False}), 500

    #         #assign to section
    #         for section, dates in submittedDates.items():
    #             Publish = dates['publishDate']
    #             Due = dates['dueDate']
    #             CID = GetCID(conn,cursor,section,CSYID)
    #             insert_assignTo = """ INSERT INTO assign (Lab,Publish,Due,CID,CSYID) VALUES(%s,%s,%s,%s,%s) """
    #             cursor.execute(insert_assignTo,(LabNum,Publish,Due,CID,CSYID))

    #         conn.commit()
    #         return jsonify({"message":"create success","Status":True}), 500
        
    # except mysql.connector.Error as error:
    #     conn.rollback()
    #     return jsonify({"error": f"An error occurred: {error}","Status":False}), 500