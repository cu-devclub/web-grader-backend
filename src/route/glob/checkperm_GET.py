from flask import jsonify, request, g

from function.db import get_db

def main():
    try:
        # Extract parameters from request
        email = request.args.get('Email')
        csyid = request.args.get('CSYID')

        # Connect to MySQL database
        conn = get_db()
        cursor = conn.cursor()

        # Query to check if Email and CSYID exist in classeditor table
        query = "SELECT * FROM classeditor WHERE Email = %s AND CSYID = %s"
        cursor.execute(query, (email, csyid))
        result = cursor.fetchone()

        if result:
            # If a row is found, return success
            return jsonify({
                'success': True,
                'msg': '',
                'data': {}
            }), 200
        else:
            # If no row is found, return failure
            return jsonify({
                'success': False,
                'msg': '',
                'data': {}
            }), 200
    except Exception as error:
        print(error)
        return jsonify({
            'success': False,
            'msg': 'Database error occurred.',
            'data': {}
        }), 500