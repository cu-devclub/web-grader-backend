from flask import request, jsonify, g

def main():
    try:
        
        #Param
        student_id = request.args.get('SID')
        class_id = request.args.get('CID')
        
        # Create a cursor
        cur = g.db.cursor()

        query = """
        SELECT 
            LAB.LID, 
            LAB.Lab, 
            LAB.Name, 
            LAB.Publish, 
            LAB.Due,
            COALESCE(SMT.Score, 0) AS Score,
            COALESCE(QST.MaxScore, 0) AS MaxScore,
            CASE 
                WHEN LAB.Due <= SMT.LatestTimestamp THEN TRUE
                ELSE FALSE
            END AS Late,
            CASE 
                WHEN SMT.LatestTimestamp IS NOT NULL THEN TRUE
                ELSE FALSE
            END AS TurnIn
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
                LID, 
                MAX(Timestamp) AS LatestTimestamp, 
                SUM(Score) AS Score
            FROM 
                submitted
            GROUP BY 
                LID
            ) AS SMT
        ON 
            LAB.LID = SMT.LID
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
        GROUP BY 
            LAB.LID, LAB.Lab, LAB.Name, LAB.Publish, LAB.Due
        ORDER BY 
            LAB.Publish;
        """

        # Execute a SELECT statement
        cur.execute(query, (student_id, class_id))
        # Fetch all rows
        data = cur.fetchall()

        # Close the cursor
        cur.close()


        AllLab = []

        # Convert the result to the desired structure
        for row in data:
            AllLab.append({
                "LID": row[0], 
                "Lab": row[1], 
                "Name": row[2], 
                "Publish": row[3], 
                "Due": row[4],
                "Score": int(row[5]),
                "MaxScore": int(row[6]),
                "TurnIn": bool(row[7]),
                "Late": bool(row[8])
            })



            # lab, question, name, due_time, timestamp, Maxscore, score, turn_in, late = row
            # lab = 'Lab'+str(lab)
            # question = 'Q'+str(question)
        
            # if lab not in transformed_data:
            #     transformed_data[lab] = {
            #         'Name':name,
            #         'Due':due_time,
            #         'Maxscore' :int(Maxscore) if Maxscore else 0,
            #         'Score' : int(score) if score else 0
            #     }
        
            # if question not in transformed_data[lab]:
            #     transformed_data[lab][question]={
            #         'IsTurnIn':bool(turn_in),
            #         'IsLate':bool(late)
                    
            #     }

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



    #     query = """
    #         SELECT
    #             QST.Lab,
    #             QST.Question,
    #             LB.Name,
    #             ASN.Due,
    #             SMT.Timestamp,
    #             MaxScores.MaxScore AS Lab_MaxScore,
    #             Scores.Score AS Lab_Score,
    #             CASE WHEN SMT.Timestamp IS NOT NULL THEN TRUE ELSE FALSE END AS TurnIn,
    #             CASE WHEN ASN.Due <= SMT.Timestamp THEN TRUE ELSE FALSE END AS Late
    #         FROM
    #             question QST
    #             INNER JOIN lab LB ON QST.CSYID = LB.CSYID AND QST.Lab = LB.lab
    #             INNER JOIN section SCT ON SCT.CSYID = QST.CSYID
    #             INNER JOIN assign ASN ON SCT.CID = ASN.CID AND QST.Lab = ASN.Lab
    #             INNER JOIN student STD ON STD.UID = %s AND STD.CID = ASN.CID
    #             LEFT JOIN submitted SMT ON QST.CSYID = SMT.CSYID AND QST.Lab = SMT.Lab AND QST.Question = SMT.Question AND SMT.UID = STD.UID
    #             LEFT JOIN (
    #                 SELECT Lab, SUM(MaxScore) AS MaxScore
    #                 FROM question
    #                 WHERE CSYID = %s
    #                 GROUP BY Lab
    #             ) AS MaxScores ON QST.Lab = MaxScores.Lab 
    #             LEFT JOIN (
    #                 SELECT Lab, SUM(Score) AS Score
    #                 FROM submitted
    #                 WHERE CSYID = %s AND UID = %s
    #                 GROUP BY Lab
    #             ) AS Scores ON QST.Lab = Scores.Lab
    #         WHERE
    #             QST.CSYID = %s;

    #              """

    #     # Execute a SELECT statement
    #     cur.execute(query, (student_id,class_id,class_id, student_id, class_id))
    #     # Fetch all rows
    #     data = cur.fetchall()

    #     # Close the cursor
    #     cur.close()

    #     # Convert the result to the desired structure
    #     transformed_data = {}
    #     for row in data:
    #         lab, question, name, due_time, timestamp, Maxscore, score, turn_in, late = row
    #         lab = 'Lab'+str(lab)
    #         question = 'Q'+str(question)
        
    #         if lab not in transformed_data:
    #             transformed_data[lab] = {
    #                 'Name':name,
    #                 'Due':due_time,
    #                 'Maxscore' :int(Maxscore) if Maxscore else 0,
    #                 'Score' : int(score) if score else 0
    #             }
        
    #         if question not in transformed_data[lab]:
    #             transformed_data[lab][question]={
    #                 'IsTurnIn':bool(turn_in),
    #                 'IsLate':bool(late)
                    
    #             }

    #     return jsonify({'Assignment': transformed_data})

    # except Exception as e:
    #     print(e)
    #     return jsonify({'error': 'An error occurred'}), 500