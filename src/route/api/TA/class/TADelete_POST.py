import mysql.connector
from flask import request, jsonify
from re import fullmatch

from function.db import get_db
from function.GetCSYID import GetCSYID
from function.AddClassEditor import AddClassEditor
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request

# @jwt_required()
def main():
    conn = get_db()
    cursor = conn.cursor()
    # verify_jwt_in_request()

    # adder = get_jwt_identity()
    adder = {}
    Data = request.get_json()
    adder["email"] = Data.get("AEmail")

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
            'msg': 'Add TA successfully',
            'data': ''
        })