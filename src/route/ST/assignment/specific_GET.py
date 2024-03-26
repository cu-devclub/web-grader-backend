from flask import request, g, jsonify

def main():
    try:
        
        #Param
        class_id = request.args.get('class_id')
        speclab = request.args.get('speclab')
        school_year = request.args.get('school_year')
        
        # Create a cursor
        cur = g.db.cursor()

        query = """
            SELECT
            	QST.LAB,
                LB.Name,
                QST.ID,
                QST.Question,
                ASN.DueTime,
                SMT.TimeStamp,
                SMT.Score,
                QST.MaxScore,
                SMT.PathToFile AS TurnInFile,
                ADF.PathToFile AS QuestionFile
            FROM
            	question QST
                INNER JOIN assign ASN ON QST.LAB = ASN.LAB
                INNER JOIN submitted SMT ON QST.LAB = SMT.LAB AND QST.Question = SMT.Question
                INNER JOIN addfile ADF ON QST.LAB =ADF.LAB
                INNER JOIN lab LB ON QST.LAB = LB.LAB 
            WHERE
            	QST.ClassID = %s
                AND QST.LAB = %s
                AND QST.SchoolYear = %s
                AND QST.ClassID = ASN.ClassID AND ASN.ClassID = SMT.ClassID AND SMT.ClassID = LB.ClassID
                AND QST.SchoolYear = ASN.SchoolYear AND ASN.SchoolYear = SMT.SchoolYear AND SMT.SchoolYear = LB.SchoolYear
            ORDER BY
            	QST.LAB ASC, QST.Question ASC;
                    """

        # Execute a SELECT statement
        cur.execute(query,(class_id,speclab,school_year))
        # Fetch all rows
        data = cur.fetchall()

        # Close the cursor
        cur.close()

        # Convert the result to the desired structure
        transformed_data_list = []
        
        for row in data:
            lab, lab_name, question_id, question, due_time, submission_time, score, max_score, turn_in_file, question_file = row
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
                    'Files':[],
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
                    'MaxScore': max_score
                }
        
            if question_file not in lab_data['Files']:
                lab_data['Files'].append(question_file)
        
        # jsonify the transformed data list
        return jsonify(transformed_data_list[0])


    except Exception as e:
        print(e)
        return jsonify({'error': 'An error occurred'}), 500