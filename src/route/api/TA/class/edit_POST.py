import mysql.connector
from flask import request, jsonify

from function.db import get_db

def main():
    
    conn = get_db()
    cursor = conn.cursor()
    
    Section = request.form.get('Section')
    
    ClassName = request.form.get('ClassName')
    ClassID = request.form.get('ClassID')
    SchoolYear = request.form.get('SchoolYear')
    CSYID = request.form.get('CSYID')
    
    print('Data:',ClassName, ClassID, SchoolYear, CSYID)
    """ csvfile = request.files.get['file1']
    thumbnailfile = request.files.get['file2'] """
    """ Thumbnail = %s thumbnailfile.filename"""
    try:
        update_class = """ 
            UPDATE class
            SET ClassName = %s,
                ClassID = %s,
                SchoolYear = %s
            WHERE CSYID = %s
            """
        cursor.execute(update_class, (ClassName, ClassID, SchoolYear, CSYID))
        conn.commit()
        return jsonify({"message":"class update successfully","Status": True})
    except mysql.connector.Error as error:
        conn.rollback()
        return jsonify({"message":"An error occurred while delete class.","Status": False})