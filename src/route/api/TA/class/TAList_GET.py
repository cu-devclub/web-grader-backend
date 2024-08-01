import mysql.connector
from flask import request, jsonify, g

from function.isCET import isCET

from flask_jwt_extended import jwt_required, get_jwt_identity

@jwt_required()
def main():
    Email = get_jwt_identity()['email']
    try:
        cursor = g.db.cursor()
        CSYID = request.args.get('CSYID')

        if not isCET(g.db, cursor, Email, CSYID):
            jsonify({
                'success': False,
                'msg': "You don't have permission.",
                'data': {}
            }), 200
        
        query = """
            SELECT
                CET.Email,
                USR.Name
            FROM
                classeditor CET
                LEFT JOIN user USR ON CET.Email = USR.Email
            WHERE
                CET.CSYID = %s
        """

        cursor.execute(query, (CSYID))
        data = cursor.fetchall()
        
        query = """
            SELECT
                CLS.ClassCreator
            FROM
                class CLS
            WHERE
                CLS.CSYID = %s
        """

        cursor.execute(query, (CSYID))
        ClassCreator = cursor.fetchall()[0][0]

        return jsonify({
            'success': True,
            'msg': '',
            'data': [data, ClassCreator]
        }), 200
        
    except mysql.connector.Error as error:
        return jsonify({
            'success': False,
            'msg': f"An error occurred: {error}",
            'data': {}
        }), 200