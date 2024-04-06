from function.db import get_db
from flask import request, jsonify
import mysql.connector

def main():
    CSYID = request.args.get('CSYID')
    ClassName = request.args.get('ClassName')
    ClassID = request.args.get('ClassID')
    SchoolYear = request.args.get('SchoolYear')

    CLS_data = (ClassName, ClassID, SchoolYear)

    try:
        conn = get_db()
        cursor = conn.cursor()

        insert_class_query = "DELETE FROM class WHERE CSYID = %s;"
        cursor.execute(insert_class_query, (CSYID))

        # Commit the transaction
        conn.commit()
        return jsonify({"Status": True}) 
    except mysql.connector.Error as error:
        conn.rollback()
        return jsonify({"message":"An error occurred while delete class.","Status": False})