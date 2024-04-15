import mysql.connector
from flask import request, jsonify,g

def main():
    try:
        cursor = g.db.cursor()
        CSYID = request.args.get('CSYID')

        query = """ 
            SELECT
                LB.Lab,
                LB.Name,
                SCT.Section,
                ASN.Publish,
                ASN.Due,
                LB.CSYID
            FROM
                Lab LB 
                INNER JOIN assign ASN ON LB.CSYID = ASN.CSYID AND LB.Lab = ASN.Lab 
                INNER JOIN section SCT ON SCT.CSYID = LB.CSYID AND SCT.CID = ASN.CID
            WHERE 
                LB.CSYID = %s
            ORDER BY
	            Publish ASC,Lab DESC;
            """
        cursor.execute(query, (CSYID))

        data = cursor.fetchall()

        assignments = {}

        for row in data:
            lab_number = row[0]  # Accessing the first element in the tuple
            lab_name = row[1]    # Accessing the second element in the tuple
            section_number = row[2]  # Accessing the third element in the tuple
            
            # Convert 'Publish' and 'Due' strings to datetime objects
            publish_date = row[3]
            due_date = row[4]

            # Create the structure if lab_number is not already a key in the assignments dictionary
            if lab_number not in assignments:
                assignments[lab_number] = {
                    'LabName': lab_name,
                    'Section': {}
                }

            # Add section information under the lab
            assignments[lab_number]['Section'][section_number] = {
                'Publish': publish_date,
                'Due': due_date
            }

        # Wrap the assignments dictionary into a 'Assignment' key as you specified
        result = {'Assignment': assignments}

        # Return the result as JSON
        return jsonify(result)
        
    except mysql.connector.Error as error:
        return jsonify({"error": f"An error occurred: {error}"}), 500