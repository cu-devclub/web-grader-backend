import mysql.connector
from flask import request, jsonify

from function.db import get_db

def main():
    try:
        conn = get_db()
        cursor = conn.cursor()

        LabNum = request.form.get('oldlabNum')
        CSYID = request.form.get('CSYID')

        #just delete lab
        
        delete_lab_query = "DELETE FROM lab WHERE LB.Lab = %s AND LB.CSYID = %s"
        cursor.execute(delete_lab_query, (LabNum, CSYID))        
        conn.commit()
        return jsonify({"message":"delete success","Status":True}), 500
        
    except mysql.connector.Error as error:
        conn.rollback()
        return jsonify({"error": f"An error occurred: {error}","Status":False}), 500