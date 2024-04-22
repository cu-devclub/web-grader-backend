from flask import request, jsonify, g

def main():
    try:
        
        #Param
        Email = request.args.get('Email')
        
        # Create a cursor
        cur = g.db.cursor()

        query = """
            SELECT
                CLS.CSYID,
                CLS.ClassName,
                CLS.ClassID,
                CLS.SchoolYear,
                CLS.Thumbnail
            FROM
                class CLS
                INNER JOIN classeditor CET ON CET.CSYID = CLS.CSYID 
            WHERE 
                CET.Email = %s
            ORDER BY
                SchoolYear DESC;
                 """

        # Execute a SELECT statement
        cur.execute(query, (Email))
        # Fetch all rows
        data = cur.fetchall()

        # Close the cursor
        cur.close()

        # Convert the result to the desired structure
        transformed_data = {}

        for row in data:
            csyid, classname, classid, schoolyear, thumbnail = row
            class_info = {
                'ID': csyid,
                'ClassName': classname,
                'ClassID': classid,
                'Thumbnail': thumbnail if thumbnail else None
            }
            if schoolyear not in transformed_data:
                transformed_data[schoolyear] = [class_info]
            else:
                transformed_data[schoolyear].append(class_info)
    
        return jsonify(transformed_data)

    except Exception as e:
        print(e)
        return jsonify({'error': 'An error occurred'}), 500