from datetime import datetime
from flask import request, jsonify, g

from function.isLock import isLock

def main():
    try:
        
        # Params
        LID = request.args.get('LID')
        Email = request.args.get('Email')  # change this to jwt later

        # Create a cursor
        cur = g.db.cursor()

        # Check access
        query = """
            SELECT 
                CASE 
                    WHEN EXISTS (
                        SELECT 1
                        FROM user u
                        JOIN student s ON u.UID = s.UID
                        JOIN lab l ON s.CSYID = l.CSYID
                        WHERE u.Email = %s AND l.LID = %s
                        AND (
                            JSON_CONTAINS(l.CID, CAST(s.CID AS JSON), '$')
                            OR JSON_CONTAINS(l.GID, CAST(s.GID AS JSON), '$')
                        )
                    ) 
                    THEN 1 
                    ELSE 0 
                END AS access;
        """
        cur.execute(query, (Email, LID))
        # Fetch access result
        data = cur.fetchone()

        if not bool(int(data[0])):
            return jsonify({
                'success': False,
                'msg': "You don't have permission to this lab",
                'data': {}
            }), 200
        
        # Fetch lab info
        cur.execute("""
            SELECT 
                l.Lab, l.Name, l.Publish, l.Due,
                CASE 
                    WHEN l.Due <= IFNULL(s.LatestTimestamp, CONVERT_TZ(NOW(), '+00:00', '+07:00')) THEN 1
                    ELSE 0
                END AS Late
            FROM lab l
            LEFT JOIN (
                SELECT LID, MAX(Timestamp) AS LatestTimestamp
                FROM submitted
                GROUP BY LID
            ) s ON l.LID = s.LID
            WHERE l.LID = %s
        """, (LID,))
        lab_info_row = cur.fetchone()
        lab_info = {
            "Lock": isLock(g.db, cur, LID),
            "Lab": lab_info_row[0],
            "Name": lab_info_row[1],
            "Publish": datetime.strptime(str(lab_info_row[2]), "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M"),
            "Due": datetime.strptime(str(lab_info_row[3]), "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M"),
            "Late": bool(int(lab_info_row[4]))
        }

        # Fetch questions and submission information
        cur.execute("""
            SELECT q.QID, COALESCE(s.SID, -1) AS SID, COALESCE(s.Score, 0) AS Score, q.MaxScore,
                   COALESCE(s.SummitedFile, '') AS Filename, COALESCE(s.Timestamp, '') AS Timestamp
            FROM question q
            LEFT JOIN submitted s ON q.QID = s.QID AND q.LID = s.LID
            WHERE q.LID = %s
            ORDER BY q.QID
        """, (LID,))
        questions = cur.fetchall()

        questions_list = []
        for q in questions:
            filename = q[4].split('/')[-1] if q[4] else ""
            timestamp = datetime.strptime(str(q[5]), "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M") if q[5] else ""
            late = 1 if timestamp and datetime.strptime(timestamp, "%d/%m/%Y %H:%M") > datetime.strptime(lab_info["Due"], "%d/%m/%Y %H:%M") else 0
            if not timestamp:
                late = -1
            questions_list.append({
                "QID": q[0],
                "SMT": {
                    "SID": q[1],
                    "Filename": filename.split("\\")[-1],
                    "Date": timestamp,
                    "Late": late
                },
                "Score": q[2],
                "Max": int(q[3])
            })

        # Fetch addfile information
        cur.execute("""
            SELECT ID
            FROM addfile
            WHERE LID = %s
        """, (LID,))
        add_files = cur.fetchall()
        add_files_list = [af[0] for af in add_files]

        # Format the JSON response
        result = {
            "Info": lab_info,
            "Question": questions_list,
            "AddFile": add_files_list
        }

        return jsonify({
            'success': True,
            'msg': "",
            'data': result
        }), 200

    except Exception as e:
        print(e)
        return jsonify({
            'success': False,
            'msg': "Please contact admin!",
            'data': {}
        }), 200
