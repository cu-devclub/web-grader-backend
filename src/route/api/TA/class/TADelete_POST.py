from flask import request, jsonify
from re import fullmatch

from function.db import get_db
from function.isCET import isCET
from flask_jwt_extended import jwt_required, get_jwt_identity

@jwt_required()
def main():
    conn = get_db()
    cursor = conn.cursor()\

    adder = get_jwt_identity()
    Data = request.get_json()

    if not isCET(conn, cursor, adder['email'], Data.get("CSYID")):
        jsonify({
            'success': False,
            'msg': "You don't have permission.",
            'data': {}
        }), 200

    # check mail
    if(not fullmatch(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b', Data.get("Email"))):
        return jsonify({
            'success': False,
            'msg': 'Email is invalid',
            'data': ''
        })

    # check if adder is admin of that class
    query = """
        SELECT
            CET.Email
        FROM
            classeditor CET
        WHERE
            CET.CSYID = %s AND
            CET.Email = %s
    """

    cursor.execute(query, (Data.get("CSYID"), adder.get("email")))
    data = cursor.fetchall()

    if(len(data) != 1):
        return jsonify({
            'success': False,
            'msg': 'Permission denied',
            'data': ''
        })
    
    # check is TA exist
    # check duplicate
    query = """
        SELECT
            CET.Email
        FROM
            classeditor CET
        WHERE
            CET.CSYID = %s AND
            CET.Email = %s
    """

    cursor.execute(query, (Data.get("CSYID"), Data.get("Email")))
    data = cursor.fetchall()

    if(not len(data) > 0):
        return jsonify({
            'success': False,
            'msg': 'This TA is not in this class.',
            'data': ''
        })

    try:
        #add TA
        query = """DELETE FROM classeditor WHERE Email = %s AND CSYID = %s"""
        cursor.execute(query, (Data.get("Email"), Data.get("CSYID")))
        conn.commit()
    except Exception as e:
        conn.rollback() 
        return jsonify({
            'success': False,
            'msg': f'Please contact admin.\n{e}',
            'data': ''
        })
    
    return jsonify({
            'success': True,
            'msg': 'TA deleted successfully.',
            'data': ''
        })