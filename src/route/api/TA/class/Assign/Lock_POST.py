from flask import request, jsonify, g
import pytz
import datetime

from function.isLock import isLock
from function.isCET import isCET

from flask_jwt_extended import jwt_required, get_jwt_identity

@jwt_required()
def main():
    Email = get_jwt_identity()['email']
    conn = g.db
    cursor = conn.cursor()
    try:
        form = request.get_json()
        LID = form.get('LID')

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
        
        if LID is None:
            raise ValueError("LID is required")

        # Define the time zone for GMT+7
        tz = pytz.timezone('Asia/Bangkok')
        
        # Get the current time in GMT+7
        current_time = datetime.datetime.now(tz)


        msg = ""
        # Prepare update query and data
        if not isLock(conn, cursor, LID):
            query_update = "UPDATE lab SET `Lock` = %s WHERE LID = %s"
            update_data = (current_time, LID)
            msg = " closed."
        else:
            query_update = "UPDATE lab SET `Lock` = NULL WHERE LID = %s"
            update_data = (LID,)
            msg = " opened."

        # Execute update query
        cursor.execute(query_update, update_data)
        conn.commit()

        response = {
            "success": True,
            "msg": "Assignment" + msg,
            "data": {}
        }

    except Exception as e:
        response = {
            "success": False,
            "msg": str(e),
            "data": {}
        }
        
    return jsonify(response)
