from datetime import datetime
from flask import request, jsonify, g

from function.isSTD import isSTD
from function.isLock import isLock

from flask_jwt_extended import jwt_required, get_jwt_identity

@jwt_required()
def main():
    Email = get_jwt_identity()['email']
    try:
        
        #Param
        student_id = Email.split('@')[0]
        class_id = request.args.get('CID')
        
        # Create a cursor
        cur = g.db.cursor()

        if(not isSTD(g.db, cur, Email, class_id)):
            return jsonify({
                'success': False,
                'msg': "You don't have permission",
                'data': {}
            }), 200

        query = """
        SELECT 
            LAB.LID, 
            LAB.Lab, 
            LAB.Name, 
            LAB.Publish, 
            LAB.Due,
            CASE 
                WHEN LAB.showScoreOnLock = 1 AND (LAB.Lock IS NULL OR CONVERT_TZ(NOW(), '+00:00', '+07:00') < LAB.Lock) THEN 0
                ELSE COALESCE(SUM(SMT.Score), 0)
            END AS Score,
            COALESCE(QST.MaxScore, 0) AS MaxScore,
            CASE 
                WHEN SMT.LatestTimestamp IS NOT NULL THEN TRUE
                ELSE FALSE
            END AS TurnIn,
            CASE 
                WHEN LAB.Due <= IFNULL(SMT.LatestTimestamp, CONVERT_TZ(NOW(), '+00:00', '+07:00')) THEN TRUE
                ELSE FALSE
            END AS Late,
            LAB.showScoreOnLock
        FROM 
            lab AS LAB
        JOIN 
            student AS STD 
        ON 
            (JSON_CONTAINS(LAB.CID, CAST(STD.CID AS JSON), '$') 
            OR JSON_CONTAINS(LAB.GID, CAST(STD.GID AS JSON), '$'))
            AND STD.UID = %s
        LEFT JOIN 
            (SELECT
                UID,
                LID, 
                MAX(Timestamp) AS LatestTimestamp, 
                SUM(Score) AS Score
            FROM 
                submitted
            GROUP BY 
                LID, UID
            ) AS SMT
        ON 
            LAB.LID = SMT.LID AND SMT.UID = STD.UID
        LEFT JOIN 
            (SELECT 
                LID, 
                SUM(CAST(MaxScore AS DECIMAL(10, 2))) AS MaxScore
            FROM 
                question
            GROUP BY 
                LID
            ) AS QST
        ON 
            LAB.LID = QST.LID
        WHERE 
            LAB.CSYID = %s
            AND CONVERT_TZ(NOW(), '+00:00', '+07:00') >= LAB.Publish
        GROUP BY 
            LAB.LID, LAB.Lab, LAB.Name, LAB.Publish, LAB.Due
        ORDER BY 
            LAB.Publish;
        """

        # Execute a SELECT statement
        cur.execute(query, (student_id, class_id))
        # Fetch all rows
        data = cur.fetchall()

        AllLab = []

        # Convert the result to the desired structure
        for row in data:
            AllLab.append({
                "LID": row[0], 
                "Lab": row[1], 
                "Name": row[2], 
                "Publish": datetime.strptime(str(row[3]), "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M"), 
                "Due": datetime.strptime(str(row[4]), "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M"),
                "Score": int(row[5]),
                "MaxScore": int(row[6]),
                "TurnIn": bool(row[7]),
                "Late": bool(row[8]),
                "hideScore": bool(int(row[9])) and not isLock(g.db, cur, row[0])
            })

        # Close the cursor
        cur.close()

        return jsonify({
            'success': True,
            'msg': '',
            'data': AllLab
        }), 200



    except Exception as e:
        print(e)
        return jsonify({
            'success': False,
            'msg': 'Please contact admin',
            'data': e
        }), 200