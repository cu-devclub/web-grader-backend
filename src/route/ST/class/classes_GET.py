from flask import request, jsonify, g

def main():
    try:
        #Param
        UID = request.args.get('UID')
        
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
                CLS.ClassCreator,
                1 as ClassRole,
                CLS.CSYID
            FROM
                class CLS
                INNER JOIN section SCT ON SCT.CSYID = CLS.CSYID
                INNER JOIN student STD ON STD.CID = SCT.CID
                INNER JOIN user USR ON USR.UID = STD.UID
                LEFT JOIN classeditor CET ON CET.CSYID = CLS.CSYID AND CET.Email = USR.Email
            WHERE 
                USR.UID = %s
                AND Section <> 0
            ORDER BY
                SchoolYear DESC,ClassName ASC;
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
            cid, name, class_id, section, school_year, thumbnail, classcreator, classrole, csyid = row
            class_info = {
                "ClassID": class_id,
                "ClassName": name,
                "ID": csyid,
                "Section": section,
                "Thumbnail": thumbnail
            }
            if school_year not in transformed_data:
                transformed_data[school_year] = [class_info]
            else:
                transformed_data[school_year].append(class_info)

        return jsonify(transformed_data)

    except Exception as e:
        print(e)
        return jsonify({'error': 'An error occurred'}), 500