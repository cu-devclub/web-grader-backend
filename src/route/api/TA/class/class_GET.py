from flask import request, jsonify, g
from flask_jwt_extended import jwt_required

from function.isCET import isCET

from flask_jwt_extended import jwt_required, get_jwt_identity

@jwt_required()
def main():
    Email = get_jwt_identity()['email']
    try:
        
        #Param
        CSYID = request.args.get('CSYID')

        if not isCET(g.db, g.db.cursor(), Email, CSYID):
            jsonify({
                'success': False,
                'msg': "You don't have permission.",
                'data': {}
            }), 200
        
        # Create a cursor
        cur = g.db.cursor()

        query = """
            SELECT
                CLS.ClassName,
                CLS.ClassID,
                CLS.SchoolYear,
                CLS.Thumbnail,
                USR.Name,
                CLS.Archive
            FROM
                class CLS
                INNER JOIN user USR ON USR.Email = CLS.ClassCreator
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

        CNA, CID, CSY, CTN, PFS, ACH = data[0]

        return jsonify(
            {
                "ClassName": CNA,
                "ClassID": CID,
                "ClassYear": CSY,
                "Thumbnail": CTN,
                "Instructor": PFS,
                "Archive": bool(ACH)
            }
        )

    except Exception as e:
        print(e)
        return jsonify({'error': 'An error occurred'}), 500