from flask import request, jsonify
from function.SaveCsvFile import save_csv_file
from function.SaveThumbnailFile import save_thumbnail_file
from function.db import get_db
import mysql.connector

def main():
    ClassID = request.form.get('ClassID')
    if not ClassID:
        return jsonify({"error": "ClassID is required."}), 400
    
    ClassName = request.form.get('ClassName')
    Section = request.form.get('Section')
    SchoolYear = request.form.get('SchoolYear')
    
    # Handle CSV file
    success_csv, PathToPicture1 = save_csv_file(ClassID, Section, SchoolYear, request.files.get('file1'))

    # Handle Thumbnail file
    success_thumbnail, PathToPicture2 = save_thumbnail_file(request.files.get('file2'))

    if not (success_csv and success_thumbnail):
        return jsonify({"error": "Failed to save one or more files."}), 500

    try:
        # Establish MySQL connection
        conn = get_db()
        cursor = conn.cursor()
        
        update_query = "UPDATE class SET Name = %s, Section = %s, SchoolYear = %s, PathToPicture1 = %s, PathToPicture2 = %s WHERE ClassID = %s"
        cursor.execute(update_query, (ClassName, Section, SchoolYear, PathToPicture1, PathToPicture2, ClassID))

        conn.commit()
        
        return jsonify({"message": "Class updated successfully!"})

    except mysql.connector.Error as error:
        conn.rollback()
        return jsonify({"error": f"An error occurred while updating class: {error}"}), 500

    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()