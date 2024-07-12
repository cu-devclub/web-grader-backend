import mysql.connector
from flask import request, jsonify, g

def main():
    try:
        cursor = g.db.cursor()
        CSYID = request.args.get('CSYID')
        
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