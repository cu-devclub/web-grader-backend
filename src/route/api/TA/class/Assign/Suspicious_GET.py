from flask import request, jsonify, g
from function.isCET import isCET
import mysql.connector
from flask_jwt_extended import jwt_required, get_jwt_identity

@jwt_required()
def main():
    Email = get_jwt_identity()['email']

    conn = g.db
    cursor = conn.cursor()

    LID = request.args.get('LID')
    if not LID:
        return jsonify({
            'success': False,
            'msg': 'LID is required',
            'data': {}
        }), 400

    query = """ 
        SELECT
            LB.CSYID
        FROM
            lab LB
        WHERE 
            LB.LID = %s
        """
    cursor.execute(query, (LID,))
    data = cursor.fetchone()
    
    if data == None:
        jsonify({
            'success': False,
            'msg': "Lab not found",
            'data': {}
        }), 200

    if not isCET(conn, cursor, Email, data[0]):
        jsonify({
            'success': False,
            'msg': "You don't have permission.",
            'data': {}
        }), 200

    try:
        # Select QID from question table
        cursor.execute("SELECT QID FROM question WHERE LID = %s ORDER BY QID", (LID,))
        question_rows = cursor.fetchall()
        question_ids = [row[0] for row in question_rows]

        if not question_ids:
            return jsonify({'success': False, 'msg': 'No questions found for the given LID', 'data': {}}), 404

        # Select data from suspicious table
        cursor.execute("SELECT UID, QID, Type, Message, Timestamp FROM suspicious WHERE LID = %s", (LID,))
        suspicious_rows = cursor.fetchall()

        suspicious_data = []
        for row in suspicious_rows:
            suspicious_data.append({
                'UID': row[0],
                'QID': question_ids.index(int(row[1])) + 1 if int(row[1]) in question_ids else 0,
                'Type': row[2],
                'Reason': row[3],
                'Timestamp': row[4].strftime('%d/%m/%Y %H:%M')
            })

        data = {
            'Q': list(range(1, len(question_ids) + 1)),
            'Type': [1, 2, 3, 4, 5],
            'Sus': suspicious_data
        }

        return jsonify({'success': True, 'msg': '', 'data': data})

    except mysql.connector.Error as err:
        return jsonify({'success': False, 'msg': str(err), 'data': {}}), 500