from flask import request, g, jsonify

def main():
    try:
        #Param
        EmailR = request.args.get('Email')
        
        # Create a cursor
        cur = g.db.cursor()

        query = """
            SELECT
            	CLS.ID,
            	CLS.Name,
                CLS.ClassID,
                CLS.Section,
                CLS.SchoolYear,
                CLS.Thumbnail
            FROM
            	class CLS
                INNER JOIN userclass USC ON USC.IDClass = CLS.ID
            WHERE
                USC.EMAIL = %s
            ORDER BY
	            CLS.SchoolYear DESC;
        """

        # Execute a SELECT statement
        cur.execute(query,(EmailR))
        # Fetch all rows
        data = cur.fetchall()

        # Close the cursor
        cur.close()

        # Convert the result to the desired structure
        transformed_data = []
        for row in data:
            id, name, class_id, section, school_year, thumbnail = row
            transformed_data.append({
                "ClassID": class_id,
                "ClassName": name,
                "ID": id,
                "SchoolYear": school_year,
                "Section": section,
                "Thumbnail": thumbnail
            })
            
        return jsonify(transformed_data)

    except Exception as e:
        print(e)
        return jsonify({'error': 'An error occurred'}), 500