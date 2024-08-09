from flask import jsonify, g, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from function.loadconfig import isDev
from function.db import get_db


import pytz
from datetime import datetime

gmt_timezone = pytz.timezone('Asia/Bangkok')

@jwt_required()
def main():
    email = get_jwt_identity()['email']

    conn = get_db()
    cur = conn.cursor()

    if not isDev:
        # log ip
        UID = email.split("@")[0]
        query = "INSERT INTO `iplog` (`IP`, `UID`, `Timestamp`) VALUES (%s,%s,%s)"
        cur.execute(query, (f"{request.headers.get('X-Real-IP')} ; {request.headers.get('X-Forwarded-For')}", UID, datetime.now(gmt_timezone)))
        conn.commit()

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