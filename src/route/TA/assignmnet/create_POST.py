from flask import request, jsonify
from function.db import get_db
import mysql.connector

def main():
    
    
    Lab = ''
    Name = ''
    ClassID = ''
    SchoolYear = ''
    Publish = ''
    Due = ''
    AssignTo = ''
    Creator = ''
    MaxScore = []
    File = []
    
    
    ASN_data = (Lab, AssignTo, Publish, Due, ClassID, SchoolYear)
    
    
    try:
        # Establish MySQL connection
        conn = get_db()
        cursor = conn.cursor()
        
        # Loop นับจำนวน Question จาก score แล้ว Insert all
        for QSTNum, MS in enumerate(MaxScore):
            Question = QSTNum+1
            MScore = MS
            QST_data = (Creator, Lab, Question, Name, MScore, ClassID, SchoolYear)

            insert_question_query = "INSERT INTO question (Creator, LAB, Question, Name, MaxScore, ClassID, SchoolYear) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(insert_question_query, QST_data)
        
        # File path แจก all
        for filepath in File:
            eachFile = filepath
            
            File_data = (Lab, eachFile, ClassID, SchoolYear)
            insert_file_query = "INSERT INTO file_paths (LAB, PathToFile, ClassID, SchoolYear) VALUES (%s, %s, %s, %s)"
            try:
                cursor.execute(insert_file_query, File_data)
            except mysql.connector.Error as error:
                print("Error inserting file path '{eachFile}': {error}")
        
        # Assignment Data Insert
        insert_assign_query = "INSERT INTO assign (LAB, AssignTo, PublishTime, DueTime, ClassID, SchoolYear) VALUES (%s, %s, %s, %s, %s, %s)"
        cursor.execute(insert_assign_query, ASN_data)

        # Commit the transaction
        conn.commit()
        
        return jsonify({"message": "Data inserted successfully!"})

    except mysql.connector.Error as error:
        # Rollback transaction in case of an error
        conn.rollback()
        return jsonify({"error": f"An error occurred while inserting data: {error}"}), 500

    finally:
        # Close the cursor and MySQL connection
        if 'cursor' in locals() and cursor:
            cursor.close()