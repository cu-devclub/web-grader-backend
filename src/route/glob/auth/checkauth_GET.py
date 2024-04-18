from flask import jsonify, g
from flask_jwt_extended import jwt_required, get_jwt_identity

@jwt_required()
def main():
    email = get_jwt_identity()


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
    cur.execute(query,(email))
    # Fetch all rows
    data = cur.fetchall()

    cur.close()

    if len(data) != 1:
        return {}, 500
    else:
        transformed_data = {}
        Ename, Email, Name, Role = data[0]
        transformed_data = {
            'Name': Name,
            'Email': Email,
            'ID': Ename,
            'Role': Role
        }

        return jsonify({
            'success': True,
            'msg': '',
            'data': transformed_data
        }), 200