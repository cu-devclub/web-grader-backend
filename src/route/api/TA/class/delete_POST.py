import os
import glob
import shutil
import mysql.connector
from flask import request, jsonify

from function.db import get_db
from function.loadconfig import UPLOAD_FOLDER

def main():
    
    CSYID = request.form.get('CSYID')
    
    try:
        conn = get_db()
        cursor = conn.cursor()
        insert_class_query = "DELETE FROM class WHERE CSYID = %s;"
        cursor.execute(insert_class_query, (CSYID))
        conn.commit()

        dir_path = os.path.join(UPLOAD_FOLDER, CSYID)
        csv_path = os.path.join(UPLOAD_FOLDER, 'CSV', f'{CSYID}.csv')
        thumbnail_path_pattern = os.path.join(UPLOAD_FOLDER, 'Thumbnail', f'{CSYID}.*')
        
        # Delete the directory
        if os.path.exists(dir_path) and os.path.isdir(dir_path):
            shutil.rmtree(dir_path)
        
        # Delete the CSV file
        if os.path.exists(csv_path):
            os.remove(csv_path)
        
        # Delete the thumbnail file with any extension
        thumbnail_files = glob.glob(thumbnail_path_pattern)
        for thumbnail_file in thumbnail_files:
            if os.path.exists(thumbnail_file):
                os.remove(thumbnail_file)

        return jsonify({"Status": True}) 
    except mysql.connector.Error as error:
        conn.rollback()
        return jsonify({"message":"An error occurred while delete class.","Status": False})