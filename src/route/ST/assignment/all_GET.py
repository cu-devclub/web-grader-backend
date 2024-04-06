from flask import request, jsonify, g

def main():
    try:
        
        #Param
        class_id = request.args.get('CID')
        
        # Create a cursor
        cur = g.db.cursor()

        query = """
            SELECT
            	QST.Lab,
                QST.Question,
                LB.Name,
                ASN.Due,
                SMT.Timestamp,
                QST.MaxScore,
                SMT.Score,
                CASE WHEN SMT.Timestamp IS NOT NULL THEN TRUE ELSE FALSE END As TurnIn,
                CASE WHEN ASN.Due <= SMT.Timestamp THEN TRUE ELSE FALSE END AS Late
            FROM
            	question QST
                INNER JOIN lab LB ON QST.CSYID = LB.CSYID AND QST.Lab = LB.lab
                INNER JOIN section SCT ON SCT.CSYID = QST.CSYID
                INNER JOIN assign ASN ON SCT.CID = ASN.CID AND QST.Lab = ASN.Lab
                INNER JOIN student STD ON STD.UID = %s AND STD.CID = ASN.CID
                LEFT JOIN submitted SMT ON QST.CSYID = SMT.CSYID AND QST.Lab = SMT.Lab AND QST.Question = SMT.Question AND SMT.UID = STD.UID
            WHERE
            	QST.CSYID = %s
                 """

        # Execute a SELECT statement
        cur.execute(query, (class_id))
        # Fetch all rows
        data = cur.fetchall()

        # Close the cursor
        cur.close()

        # Convert the result to the desired structure
        transformed_data = {}
        for row in data:
            lab, question, name, due_time, timestamp, Maxscore, score, turn_in, late = row
            lab = 'Lab'+str(lab)
            question = 'Q'+str(question)
        
            if lab not in transformed_data:
                transformed_data[lab] = {
                    'Name':name,
                    'Due':due_time,
                }
        
            if question not in transformed_data[lab]:
                transformed_data[lab][question]={
                    'IsTurnIn':bool(turn_in),
                    'IsLate':bool(late)
                    
                }

        return jsonify({'Assignment': transformed_data})

    except Exception as e:
        print(e)
        return jsonify({'error': 'An error occurred'}), 500