from flask import request, jsonify, g

def main():
    try:
        
        #Param
        Uid = request.args.get('UID')
        Csyid = request.args.get('CSYID')
        Lab = request.args.get('speclab')

        # Create a cursor
        cur = g.db.cursor()

        query = """
            SELECT
                QST.Lab,
                LB.Name,
                QST.QID,
                QST.Question,
                ASN.Due,
                SMT.Timestamp,
                SMT.Score,
                QST.MaxScore,
                SMT.SummitedFile,
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
                AND QST.Lab = %s
                    """

        # Execute a SELECT statement
        cur.execute(query,(Uid,Csyid,Lab))
        # Fetch all rows
        data = cur.fetchall()

        # Close the cursor
        

        # Convert the result to the desired structure
        transformed_data_list = []
        
        for row in data:
            lab, lab_name, question_id, question, due_time, submission_time, score, max_score, turn_in_file, Late = row
            lab_num = 'Lab' + str(lab)

            # Construct the question key
            question_key = 'Q' + str(question)

            # Check if lab_num already exists in transformed_data_list
            lab_exists = False
            for item in transformed_data_list:
                if item['Lab'] == lab_num:
                    lab_exists = True
                    lab_data = item
                    break

            # If lab_num doesn't exist, create it
            if not lab_exists:
                lab_data = {
                    'Lab': lab_num,
                    'Name': lab_name,
                    'Due': due_time,
                    'Files': [],
                    'Questions': {}
                }
                transformed_data_list.append(lab_data)

            # Initialize the question key if it doesn't exist
            if question_key not in lab_data['Questions']:
                lab_data['Questions'][question_key] = {
                    'ID': question_id,
                    'QuestionNum': question,
                    'Submission': {
                        'Date': submission_time,
                        'FileName': turn_in_file,
                    },
                    'Score': score,
                    'MaxScore': max_score,
                    'Late': bool(Late)
                }

            # Fetch files for the current lab and add them to the lab's 'Files' list
            query_files = """
                SELECT
                    PathToFile
                FROM
                    addfile ADF
                WHERE
                    ADF.CSYID = %s
                    AND ADF.Lab = %s
            """
            cur.execute(query_files, (Csyid, lab))
            files_data = cur.fetchall()
            for file_row in files_data:
                file_path = file_row[0]
                if file_path not in lab_data['Files']:
                    lab_data['Files'].append(file_path)

        # jsonify the transformed data list
        return jsonify(transformed_data_list[0])

    except Exception as e:
        print(e)
        return jsonify({'error': 'An error occurred'}), 500