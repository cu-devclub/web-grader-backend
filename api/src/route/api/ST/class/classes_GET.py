from flask import request, jsonify, g

from flask_jwt_extended import jwt_required, get_jwt_identity

@jwt_required()
def main():
    Email = get_jwt_identity()['email']
    try:
        #Param
        UID = Email.split('@')[0]
        
        # Create a cursor
        cur = g.db.cursor()

        query = """
            SELECT
                SCT.CID,
                CLS.ClassName,
                CLS.ClassID,
                SCT.Section,
                CLS.SchoolYear,
                CLS.Thumbnail,
                CREATOR_USR.Name AS Instructor,
                CLS.CSYID
            FROM
                class CLS
                INNER JOIN section SCT ON SCT.CSYID = CLS.CSYID
                INNER JOIN student STD ON STD.CID = SCT.CID
                INNER JOIN user USR ON USR.UID = STD.UID
                INNER JOIN user CREATOR_USR ON CREATOR_USR.Email = CLS.ClassCreator
            WHERE 
                USR.UID = %s
                AND SCT.Section <> 0
                AND CLS.Archive = 0
            ORDER BY
                CLS.SchoolYear DESC,
                CLS.ClassName ASC;
        """

        # Execute a SELECT statement
        cur.execute(query,(UID))
        # Fetch all rows
        data = cur.fetchall()

        # Close the cursor
        cur.close()

        ### sort by schoolyear
        transformed_data = {}
        for row in data:
            cid, name, class_id, section, school_year, thumbnail, PFS, csyid = row
            class_info = {
                "ClassID": class_id,
                "ClassName": name,
                "ID": csyid,
                "Section": section,
                "Thumbnail": thumbnail,
                "Instructor": PFS
            }
            if school_year not in transformed_data:
                transformed_data[school_year] = [class_info]
            else:
                transformed_data[school_year].append(class_info)

        return jsonify(transformed_data)

    except Exception as e:
        print(e)
        return jsonify({'error': 'An error occurred'}), 500