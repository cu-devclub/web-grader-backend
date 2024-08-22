from flask import request, jsonify, g

from function.db import get_db
from function.isCET import isCET

from flask_jwt_extended import jwt_required, get_jwt_identity

@jwt_required()
def main():
    try:
        Email = get_jwt_identity()['email']
        conn = get_db()
        cur = conn.cursor()
        Data = request.get_json()
        UID = Data.get("SID")
        CSYID = Data.get("CSYID")

        cur.execute("SELECT CSYID FROM class WHERE CSYID=%s", (CSYID))
        if(len(cur.fetchall()) == 0):
            return jsonify({
                'success': False,
                'msg': "Class not found.",
                'data': {}
            })

        if(not isCET(g.db, g.db.cursor(), Email, CSYID)):
            return jsonify({
                'success': False,
                'msg': "You don't have permission",
                'data': {}
            }), 200

        cur.execute("SELECT UID FROM student WHERE UID=%s AND CSYID=%s", (UID, CSYID))
        if(len(cur.fetchall()) == 0):
            return jsonify({
                'success': False,
                'msg': "Student not found.",
                'data': {}
            })

        cur.execute("DELETE FROM student WHERE UID=%s AND CSYID=%s", (UID, CSYID))
        conn.commit()
        
        return jsonify({
            'success': True,
            'msg': "Student removed successfully.",
            'data': {}
        })
    
    except Exception as e:
        conn.rollback()
        return jsonify({
            'success': False,
            'msg': "There is problem on server side. please contact admin.",
            'data': {
                'Error': str(e)
            }
        })