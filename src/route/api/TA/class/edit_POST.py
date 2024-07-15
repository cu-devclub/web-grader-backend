import mysql.connector
from flask import request, jsonify

from function.db import get_db
from function.isCET import isCET

from flask_jwt_extended import jwt_required, get_jwt_identity

@jwt_required()
def main():
    Email = get_jwt_identity()['email']
    
    conn = get_db()
    cursor = conn.cursor()
    
    ClassName = request.form.get('ClassName')
    ClassID = request.form.get('ClassID')
    SchoolYear = request.form.get('SchoolYear')
    CSYID = request.form.get('CSYID')

    if not isCET(conn, cursor, Email, CSYID):
        jsonify({
            'success': False,
            'msg': "You don't have permission.",
            'data': {}
        }), 200
    
    try:
        update_class = """ 
            UPDATE class
            SET ClassName = %s,
                ClassID = %s,
                SchoolYear = %s
            WHERE CSYID = %s
            """
        cursor.execute(update_class, (ClassName, ClassID, SchoolYear, CSYID))
        conn.commit()
        return jsonify({"message":"class update successfully","Status": True})
    except mysql.connector.Error as error:
        conn.rollback()
        return jsonify({"message":"An error occurred while delete class.","Status": False})