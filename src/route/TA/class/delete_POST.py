import mysql.connector
from flask import request, jsonify

from function.db import get_db

def main():
    
    CSYID = request.form.get('CSYID')
    
    try:
        conn = get_db()
        cursor = conn.cursor()
        insert_class_query = "DELETE FROM class WHERE CSYID = %s;"
        cursor.execute(insert_class_query, (CSYID))
        conn.commit()
        return jsonify({"Status": True}) 
    except mysql.connector.Error as error:
        conn.rollback()
        return jsonify({"message":"An error occurred while delete class.","Status": False})