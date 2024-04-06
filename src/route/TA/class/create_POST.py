from function.db import get_db
from flask import request, jsonify
import mysql.connector
from function.AddUserClass import AddUserClass

def main():
    DataJ = request.get_json()

    ClassName = DataJ.get('ClassName')
    ClassID = DataJ.get('ClassID')
    SchoolYear = DataJ.get('SchoolYear')
    Creator = DataJ.get('Creator')
    Section = '0'
    
    # Prepare data for database insertion
    CLS_data = (ClassName, ClassID, SchoolYear, Creator)

    
    try:
        # Establish MySQL connection
        conn = get_db()
        cursor = conn.cursor()
            
        # Insert data into the class table
        insert_class_query = "INSERT INTO class (ClassName, ClassID, SchoolYear, ClassCreator) VALUES (%s, %s, %s, %s)"
        cursor.execute(insert_class_query, CLS_data)
        
        # Commit the transaction
        conn.commit()
        
        if AddClassEditor(conn,cursor,Creator,GetCSYID(conn,cursor,ClassID,SchoolYear)):
            return jsonify({"Status": True})
        else:
            return jsonify({"Status": False})

    except mysql.connector.Error as error:
        # Rollback transaction in case of an error
        conn.rollback()
        return jsonify({"Status": False})

    finally:
        # Close the cursor and MySQL connection
        if 'cursor' in locals() and cursor:
            cursor.close()