import mysql.connector
from flask import request, jsonify

from function.db import get_db
from function.GetCSYID import GetCSYID
from function.AddClassEditor import AddClassEditor

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
        conn.commit()
        
        if AddClassEditor(conn,cursor,Creator,GetCSYID(conn,cursor,ClassID,SchoolYear)):
            return jsonify({"Status": True})
        else:
            return jsonify({"Status": False})
    except mysql.connector.Error as error:
        conn.rollback()
        return jsonify({"Status": False})