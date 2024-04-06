from function.db import get_db
from flask import jsonify

def DeleteUserSummit(conn,cursor):
    try:
        conn = get_db()

    except Exception as e:
        return jsonify({"error": str(e)}), 500  