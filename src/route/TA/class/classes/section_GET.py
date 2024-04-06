from flask import request, jsonify, g

def main():
    try:
        #Param
        UID = request.args.get('UID')

        # Create a cursor
        cur = g.db.cursor()

        query = """
            SELECT DISTINCT
                SCT.CID,
                CLS.ClassName,
                CLS.ClassID,
                SCT.Section,
                CLS.SchoolYear,
                CLS.Thumbnail,
                CLS.ClassCreator,
                2 as ClassRole,
                CLS.CSYID
            FROM
                User USR
                INNER JOIN classeditor CET
                LEFT JOIN class CLS ON CET.CSYID = CLS.CSYID 
                INNER JOIN section SCT ON SCT.CSYID = CLS.CSYID
                LEFT JOIN student STD ON STD.CID = SCT.CID 
            WHERE
                USR.UID = %s
                AND USR.Email IN (CET.Email)
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

        # Convert the result to the desired structure
        transformed_data = []
        for row in data:
            cid, name, class_id, section, school_year, thumbnail, classcreator, classrole, csyid = row
            transformed_data.append({
                "ClassID": class_id,
                "ClassName": name,
                "ID": csyid,
                "SchoolYear": school_year,
                "Section": section,
                "Thumbnail": thumbnail
            })

        return jsonify(transformed_data)

    except Exception as e:
        print(e)
        return jsonify({'error': 'An error occurred'}), 500