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

gmt_timezone = pytz.timezone('GMT')

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

        Source_files = [v for k, v in request.files.items() if k.startswith("Source")]
        Release_files = [v for k, v in request.files.items() if k.startswith("Release")]
        Additional_files = [v for k, v in request.files.items() if k.startswith("Add")]

        LockOnDue = form["DueDate"] if form['LockOnDue'] == 'true' else None

        # Path = <CSYID>/<LID>/(Addi)
        # Path = <CSYID>/<LID>/Source_(index)_(Source)
        # Path = <CSYID>/<LID>/Release_(index)_(Release)
        
        seleted = [GetGID(conn, cursor, i, form["CSYID"]) if (form["IsGroup"] == 'true') else GetCID(conn, cursor, i, form["CSYID"]) for i in form["Selected"].split(",")]

        GCID = "GID" if (form["IsGroup"] == 'true') else "CID"

        addLab = f"INSERT INTO lab (Lab, Name, Publish, Due, `Lock`, showScoreOnLock, {GCID}, CSYID, Creator) VALUES " + "(%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(addLab, (form["LabNum"], form["LabName"], form["PubDate"], form["DueDate"], LockOnDue, 1 if form["ShowOnLock"] == 'true' else 0, str(seleted).replace(" ", ""), form["CSYID"], Email))
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