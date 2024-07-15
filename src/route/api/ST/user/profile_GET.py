from flask import request, jsonify, g

from flask_jwt_extended import jwt_required, get_jwt_identity

@jwt_required()
def main():
    EmailR = get_jwt_identity()['email']
    try:
        
        # Create a cursor
        cur = g.db.cursor()

        query = """
            SELECT
                USR.UID,
                USR.Email,
                USR.Name,
                USR.Role
            FROM
                user USR
            WHERE 
                Email= %s
        """

        # Execute a SELECT statement
        cur.execute(query,(EmailR))
        # Fetch all rows
        data = cur.fetchall()

        # Close the cursor
        cur.close()

        # Convert the result to the desired structure
        transformed_data = {}
        for row in data:
            Ename, Email, Name, Role = row
            transformed_data = {
                    'Name': Name,
                    'Email': Email,
                    'ID': Ename,
                    'Role': Role
                }
            
        return jsonify(transformed_data)

    except Exception as e:
        print(e)
        return jsonify({'error': 'An error occurred'}), 500