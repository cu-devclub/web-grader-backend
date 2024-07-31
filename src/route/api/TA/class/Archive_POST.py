import os
import glob
import shutil
import mysql.connector
from flask import request, jsonify

from function.db import get_db
from function.loadconfig import UPLOAD_FOLDER
from function.isCET import isCET
from function.isArchive import isArchive

from flask_jwt_extended import jwt_required, get_jwt_identity

@jwt_required()
def main():
    Email = get_jwt_identity()['email']
    CSYID = request.form.get('CSYID')
    
    
    try:
        conn = get_db()
        cursor = conn.cursor()

        if not isCET(conn, cursor, Email, CSYID):
            jsonify({
                'success': False,
                'msg': "You don't have permission.",
                'data': {}
            }), 200



        msg = ""
        if isArchive(conn, cursor, CSYID):
            query_update = "UPDATE class SET `Archive` = 0 WHERE CSYID = %s"
            msg = " unarchived."
        else:
            query_update = "UPDATE class SET `Archive` = 1 WHERE CSYID = %s"
            msg = " archived."

        cursor.execute(query_update, (CSYID,))
        conn.commit()    

        response = {
            "success": True,
            "msg": "Class" + msg,
            "data": {}
        }

    except Exception as e:
        conn.rollback()
        response = {
            "success": False,
            "msg": str(e),
            "data": {}
        }
        
    return jsonify(response)