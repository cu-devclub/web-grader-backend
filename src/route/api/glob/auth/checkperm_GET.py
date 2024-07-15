from flask import jsonify, request, g

from function.db import get_db
from function.isCET import isCET

from flask_jwt_extended import jwt_required, get_jwt_identity

@jwt_required()
def main():
    email = get_jwt_identity()['email']
    csyid = request.args.get('CSYID')

    conn = get_db()
    cursor = conn.cursor()

    return jsonify({
        'success': isCET(conn, cursor, email, csyid),
        'msg': '',
        'data': {}
    }), 200