from flask import request, jsonify, g

def main():
    #ลืม section
        #Param
        class_id = request.args.get('class_id')
        school_year = request.args.get('school_year')

        # Create a cursor
        cur = g.db.cursor()

        query = """
            SELECT
            	QST.LAB,
                QST.Question,
                USR.EmailName,
                USR.Name,
                SMT.TimeStamp,
                SMT.Score,
                QST.MaxScore,
                ASN.DueTime,
                CASE WHEN SMT.TimeStamp IS NOT NULL THEN TRUE ELSE FALSE END As TurnIn,
                CASE WHEN ASN.DueTime <= SMT.TimeStamp THEN TRUE ELSE FALSE END AS Late
            FROM
            	Question QST
                INNER JOIN class CLS 
                INNER JOIN userclass USC ON CLS.ID = USC.IDClass 
                INNER JOIN submitted SMT ON QST.LAB = SMT.LAB AND QST.Question = SMT.Question
                INNER JOIN assign ASN ON QST.LAB = ASN.LAB
                INNER JOIN user USR ON USC.Email = USR.Email
            WHERE
                QST.ClassID = %s
                AND QST.SchoolYear = %s
                AND QST.ClassID = ASN.ClassID AND ASN.ClassID = SMT.ClassID AND SMT.ClassID = CLS.ClassID
            	AND QST.SchoolYear = ASN.SchoolYear AND ASN.SchoolYear = SMT.SchoolYear AND SMT.SchoolYear = CLS.SchoolYear
                AND LEFT(USC.Email, LOCATE('@', USC.Email) - 1) = SMT.StudentID
            ORDER BY
            	USR.EmailName ASC,QST.LAB ASC, QST.Question ASC;
                    """

        # Execute a SELECT statement
        cur.execute(query,(class_id,school_year))
        # Fetch all rows
        data = cur.fetchall()

        transformed_data = {}

        for row in data:
            lab, question, emailname, name, timestamp, score, maxscore, duetime, turn_in, late = row

            # Convert turn_in and late to boolean values
            turn_in_bool = bool(turn_in)
            late_bool = bool(late)

            # Create LAB if it doesn't exist
            if emailname not in transformed_data:
                transformed_data[emailname] = {"EmailName": emailname, "Name": name}

            # Create LAB dictionary if it doesn't exist
            if f'LAB{lab}' not in transformed_data[emailname]:
                transformed_data[emailname][f'LAB{lab}'] = {}

            # Add question data to LAB dictionary
            transformed_data[emailname][f'LAB{lab}'][f'Q{question}'] = {
                'DueTime': duetime,
                'Score': score,
                'Maxscore': maxscore,
                'TimeStamp': timestamp,
                'Late': late_bool,
                'TurnIn': turn_in_bool
            }

        # Convert the dictionary to a list of values
        transformed_data_list = list(transformed_data.values())

        # Close the cursor
        cur.close()

        # Convert the result to the desired structure
        return jsonify(transformed_data_list)