from flask import request, jsonify, g

def main():
    try:
        
        #Param
        LID = request.args.get('LID')
        Email = request.args.get('Email') # change this to jwt later

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
        cur.execute(query,(Email, LID))
        # Fetch all rows
        data = cur.fetchall()

        if(not bool(int(data[0][0]))):
            return jsonify({
                'success': False,
                'msg': "You don't have permission to this lab",
                'data': {}
            }), 200
        
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
            "Lab": lab_info_row[0],
            "Name": lab_info_row[1],
            "Publish": lab_info_row[2],
            "Due": lab_info_row[3],
            "Late": bool(int(lab_info_row[4]))
        }

        # Query questions and submitted information
        cur.execute("""
            SELECT q.QID, COALESCE(s.SID, 0) AS SID, COALESCE(s.Score, 0) AS Score, q.MaxScore
            FROM question q
            LEFT JOIN submitted s ON q.QID = s.QID AND q.LID = s.LID
            WHERE q.LID = %s
            ORDER BY q.QID
        """, (LID,))
        questions = cur.fetchall()
        questions_list = [
            {
                "QID": q[0],
                "SMT": q[1],
                "Score": q[2],
                "Max": q[3]
            } for q in questions
        ]

        # Query addfile information
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