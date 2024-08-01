from flask import request, jsonify, g
from flask_jwt_extended import jwt_required

from flask_jwt_extended import jwt_required, get_jwt_identity

@jwt_required()
def main():
    Email = get_jwt_identity()['email']
    try:
        # Create a cursor
        cur = g.db.cursor()

        query = """
            SELECT
                CLS.CSYID,
                CLS.ClassName,
                CLS.ClassID,
                CLS.SchoolYear,
                CLS.Thumbnail,
                CREATOR_USR.Name AS Instructor,
                CLS.Archive
            FROM
                class CLS
                INNER JOIN classeditor CET ON CET.CSYID = CLS.CSYID
                INNER JOIN user CREATOR_USR ON CREATOR_USR.Email = CLS.ClassCreator
            WHERE 
                CET.Email = %s
            ORDER BY
                CLS.SchoolYear DESC;
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
            csyid, classname, classid, schoolyear, thumbnail, PFS, Archive = row
            class_info = {
                'ID': csyid,
                'ClassName': classname,
                'ClassID': classid,
                'Thumbnail': thumbnail if thumbnail else None,
                'Archive': bool(Archive),
                'Instructor': PFS
            }
            if schoolyear not in transformed_data:
                transformed_data[schoolyear] = [class_info]
            else:
                transformed_data[schoolyear].append(class_info)
    
        return jsonify(transformed_data)

    except Exception as e:
        print(e)
        return jsonify({'error': 'An error occurred'}), 500