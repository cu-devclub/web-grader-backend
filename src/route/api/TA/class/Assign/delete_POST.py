import mysql.connector
import os
import shutil
from flask import request, jsonify

from function.db import get_db

def delete_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)
        return True
    return False

def delete_directory_if_empty(directory_path):
    if os.path.isdir(directory_path) and not os.listdir(directory_path):
        shutil.rmtree(directory_path)
        return True
    return False

def main():
    try:
        conn = get_db()
        cursor = conn.cursor()

        data = request.get_json()
        LID = data.get('LabID')

        # Retrieve and delete files from the 'submitted' table
        select_sub_query = "SELECT SummitedFile FROM submitted WHERE LID = %s"
        cursor.execute(select_sub_query, (LID,))
        submitted_files = cursor.fetchall()

        for file in submitted_files:
            file_path = file[0]
            delete_file(file_path)
            delete_directory_if_empty(os.path.dirname(file_path))

        # Delete rows from the 'submitted' table
        delete_sub_query = "DELETE FROM submitted WHERE LID = %s"
        cursor.execute(delete_sub_query, (LID,))
        conn.commit()

        # Retrieve and delete files from the 'question' table
        select_qst_query = "SELECT SourcePath, ReleasePath FROM question WHERE LID = %s"
        cursor.execute(select_qst_query, (LID,))
        question_files = cursor.fetchall()

        for source_path, release_path in question_files:
            delete_file(source_path)
            delete_directory_if_empty(os.path.dirname(source_path))
            delete_file(release_path)
            delete_directory_if_empty(os.path.dirname(release_path))

        # Delete rows from the 'question' table
        delete_qst_query = "DELETE FROM question WHERE LID = %s"
        cursor.execute(delete_qst_query, (LID,))
        conn.commit()

        # Retrieve and delete files from the 'addfile' table
        select_addfile_query = "SELECT Path FROM addfile WHERE LID = %s"
        cursor.execute(select_addfile_query, (LID,))
        addfile_files = cursor.fetchall()

        for path in addfile_files:
            file_path = path[0]
            delete_file(file_path)
            delete_directory_if_empty(os.path.dirname(file_path))

        # Delete rows from the 'addfile' table
        delete_addfile_query = "DELETE FROM addfile WHERE LID = %s"
        cursor.execute(delete_addfile_query, (LID,))
        conn.commit()

        # Delete the lab
        delete_lab_query = "DELETE FROM lab WHERE LID = %s"
        cursor.execute(delete_lab_query, (LID,))
        conn.commit()

        return jsonify({
            'success': True,
            'msg': "",
            'data': {}
        }), 200

    except mysql.connector.Error as error:
        conn.rollback()
        print(error)
        return jsonify({
            'success': False,
            'msg': "Please contact admin!",
            'data': "error"
        }), 200
