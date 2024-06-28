from flask import request, jsonify, g
import pytz
import datetime

from function.isLock import isLock

def main():
    conn = g.db
    cursor = conn.cursor()
    try:
        data = request.get_json()
        LID = data.get('LID')
        
        if LID is None:
            raise ValueError("LID is required")

        # Define the time zone for GMT+7
        tz = pytz.timezone('Asia/Bangkok')
        
        # Get the current time in GMT+7
        current_time = datetime.datetime.now(tz)
        # Prepare update query and data
        if not isLock(conn, cursor, LID):
            query_update = "UPDATE lab SET `Lock` = %s WHERE LID = %s"
            update_data = (current_time, LID)
        else:
            query_update = "UPDATE lab SET `Lock` = NULL WHERE LID = %s"
            update_data = (LID,)

        # Execute update query
        cursor.execute(query_update, update_data)
        conn.commit()

        response = {
            "success": True,
            "msg": "Closed assignment.",
            "data": {}
        }

    except Exception as e:
        response = {
            "success": False,
            "msg": str(e),
            "data": {}
        }
        
    return jsonify(response)
