import pytz
import json
import mysql.connector
from datetime import datetime
from flask import request, jsonify

from function.db import get_db
from function.GetCID import GetCID

gmt_timezone = pytz.timezone('GMT')

def main():
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        Creator = request.form.get('Creator')
        LabNum = request.form.get('labNum')
        LabName = request.form.get('labName')
        CSYID = request.form.get('CSYID')
        Question = json.loads(request.form.get('Question'))
        submittedDates = json.loads(request.form.get('submittedDates'))
        Create_time = datetime.now(gmt_timezone)
        
        #check if lab already exist
        select_lab_query = "SELECT Lab,Name,CSYID FROM lab WHERE Lab = %s AND CSYID = %s"
        cursor.execute(select_lab_query, (LabNum, CSYID))
        exist_lab = cursor.fetchone()

        if exist_lab:
            return jsonify({"message": "Lab already exists. Please select a different Lab number.","Status":1}), 500
        else:
            #create Lab first
            insert_lab_query = "INSERT INTO lab (Lab, Name, CSYID) VALUES (%s, %s, %s)"
            cursor.execute(insert_lab_query, (LabNum, LabName, CSYID))

            #create Question
            for question_data in Question:
                try:
                    question_id = question_data['id']
                    score = question_data['score']
                    # Insert question data into the database
                    insert_question_query = "INSERT INTO question (Creator, Lab, Question, MaxScore, LastEdit, CSYID) VALUES (%s, %s, %s, %s, %s, %s)"
                    cursor.execute(insert_question_query, (Creator, LabNum, question_id, score, Create_time, CSYID))
                except mysql.connector.Error as error:
                    conn.rollback()
                    return jsonify({"error": f"An error occurred: {error}","Status":False}), 500

            #assign to section
            for section, dates in submittedDates.items():
                Publish = dates['publishDate']
                Due = dates['dueDate']
                CID = GetCID(conn,cursor,section,CSYID)
                insert_assignTo = """ INSERT INTO assign (Lab,Publish,Due,CID,CSYID) VALUES(%s,%s,%s,%s,%s) """
                cursor.execute(insert_assignTo,(LabNum,Publish,Due,CID,CSYID))

            conn.commit()
            return jsonify({"message":"create success","Status":True}), 500
        
    except mysql.connector.Error as error:
        conn.rollback()
        return jsonify({"error": f"An error occurred: {error}","Status":False}), 500