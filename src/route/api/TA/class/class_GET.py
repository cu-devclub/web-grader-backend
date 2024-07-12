from flask import request, jsonify, g
from flask_jwt_extended import jwt_required

# @jwt_required()
def main():
    try:
        
        #Param
        CSYID = request.args.get('CSYID')
        
        # Create a cursor
        cur = g.db.cursor()

        query = """
            SELECT
                CLS.ClassName,
                CLS.ClassID,
                CLS.SchoolYear,
                CLS.Thumbnail,
                USR.Name
            FROM
                class CLS
                INNER JOIN classeditor CET ON CET.CSYID = CLS.CSYID 
                INNER JOIN user USR ON USR.Email = CET.Email 
            WHERE 
                CLS.CSYID = %s
        """

        # Execute a SELECT statement
        cur.execute(query, (CSYID))
        # Fetch all rows
        data = cur.fetchall()

        # Close the cursor
        cur.close()

        # Convert the result to the desired structure
        transformed_data = {}

        CNA, CID, CSY, CTN, PFS = data[0]

        return jsonify(
            {
                "ClassName": CNA,
                "ClassID": CID,
                "ClassYear": CSY,
                "Thumbnail": CTN,
                "Instructor": PFS
            }
        )

        # for row in data:
        #     csyid, classname, classid, schoolyear, thumbnail = row
        #     class_info = {
        #         'ID': csyid,
        #         'ClassName': classname,
        #         'ClassID': classid,
        #         'Thumbnail': thumbnail if thumbnail else None
        #     }
        #     if schoolyear not in transformed_data:
        #         transformed_data[schoolyear] = [class_info]
        #     else:
        #         transformed_data[schoolyear].append(class_info)
    
        # return jsonify(transformed_data)

    except Exception as e:
        print(e)
        return jsonify({'error': 'An error occurred'}), 500