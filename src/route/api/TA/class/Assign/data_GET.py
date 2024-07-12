from function.db import get_db
from flask import request, jsonify

from function.isLock import isLock

def main():
    conn = get_db()
    cursor = conn.cursor()
    
    LID = request.args.get("LID")

    try:
        # Retrieve lab details
        query = """ 
            SELECT
                LB.Lab,
                LB.Name,
                LB.Publish,
                LB.Due,
                LB.CID,
                LB.GID,
                LB.CSYID,
                CASE
                    WHEN LB.Due = LB.Lock THEN 1
                    ELSE 0
                END AS LOD
            FROM
                lab LB
            WHERE 
                LB.LID = %s
            """
        cursor.execute(query, (LID,))
        data = cursor.fetchone()

        isGroup = data[4] is None
        newD5 = data[5] if isGroup else data[4]
        CSYID = data[6]

        if isGroup:
            query = """
            SELECT 
                GRP.GID,
                GRP.Group 
            FROM 
                `group` GRP 
            WHERE 
                GRP.CSYID = %s"""
        else:
            query = """
            SELECT 
                SCT.CID,
                SCT.Section 
            FROM 
                section SCT 
            WHERE 
                SCT.CSYID = %s
            """

        cursor.execute(query, (CSYID,))
        data2 = cursor.fetchall()

        PreSelectList = {}
        for i in data2:
            PreSelectList[i[0]] = i[1]

        # Retrieve question details
        query = """
            SELECT
                QST.QID,
                QST.MaxScore
            FROM 
                question QST 
            WHERE 
                QST.LID = %s
            ORDER BY 
                QST.QID ASC;
            """
        
        cursor.execute(query, (LID,))
        questions = cursor.fetchall()
        
        # Retrieve addfile details
        query = """
            SELECT
                AF.ID
            FROM
                addfile AF
            WHERE
                AF.LID = %s
            """
        cursor.execute(query, (LID,))
        addfiles = cursor.fetchall()
        
        return jsonify({
            'success': True,
            'msg': '',
            'data': {
                'LabNum': data[0],
                'LabName': data[1],
                "PubDate": data[2].strftime("%Y-%m-%dT%H:%M:%S"),
                "DueDate": data[3].strftime("%Y-%m-%dT%H:%M:%S"),
                "LOD": bool(data[7]),
                "Lock": isLock(conn, cursor, LID),
                "IsGroup": isGroup,
                "Selected": [PreSelectList[int(i)] for i in [i for i in newD5.strip("[] ").split(",")]],
                # "Selected": [],
                "SelectList": list(PreSelectList.values()),
                "Question": [{"id": i+1, "QID": questions[i][0], "score": int(questions[i][1])} for i in range(len(questions))],
                "addfile": [file[0] for file in addfiles]
            }
        }), 200
    
    except Exception as e:
        print(e)
        conn.rollback()
        return jsonify({
            'success': False,
            'msg': 'Please contact admin',
            'data': str(e)
        }), 500

