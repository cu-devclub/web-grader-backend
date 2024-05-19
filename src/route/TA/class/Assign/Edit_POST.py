import pytz
import json
from datetime import datetime
import mysql.connector
from flask import request, jsonify

from function.db import get_db
from function.GetCID import GetCID

gmt_timezone = pytz.timezone('GMT')

def main():
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        Creator = request.form.get('Creator') #no change
        CSYID = request.form.get('CSYID') #no change
        Create_time = datetime.now(gmt_timezone) #no change
        
        oldLabNum = request.form.get('oldlabNum')
        
        
        LabNum = request.form.get('labNum')
        LabName = request.form.get('labName')
        Question = json.loads(request.form.get('Question'))
        submittedDates = json.loads(request.form.get('submittedDates'))
        

        #check lab exist
        select_lab_query = "SELECT Lab,Name,CSYID FROM lab WHERE Lab = %s AND CSYID = %s"
        cursor.execute(select_lab_query, (LabNum, CSYID))
        exist_lab = cursor.fetchone()
        print(exist_lab)
        
        #update lab
        print("askdcpoaskcdpasokdcpoasdkcpasdokcpasdokcasdodckdaspodck")
        update_lab_query = """ UPDATE lab SET Lab = %s,Name = %s WHERE Lab = %s AND CSYID = %s """
        
        cursor.execute(update_lab_query, (LabNum, LabName, oldLabNum, CSYID))
        print("askdcpoaskcdpasokdcpoasdkcpasdokcpasdokcasdodckdaspodck")
        #update Question
        try:
            for question_data in Question:
                question_id = question_data['id']
                score = question_data['score']
                # Insert question data into the database
                insert_question_query = """ 
                    INSERT INTO question (Creator, Lab, Question, MaxScore, LastEdit, CSYID)
                    VALUES (%s, %s, %s, %s, %s, %s) AS new
                    ON DUPLICATE KEY UPDATE MaxScore = new.MaxScore,LastEdit = new.LastEdit
                """
                cursor.execute(insert_question_query, (Creator, LabNum, question_id, score, Create_time, CSYID))
                maxQuestion = question_id
        
        except mysql.connector.Error as error:
            conn.rollback()
            return jsonify({"error": f"An error occurred: {error}","Status":False}), 500
        #delete unuse Question
        try:
            delete_question_query = """ 
                    DELETE QST FROM question QST WHERE QST.Lab = %s AND QST.CSYID = %s AND QST.Question > %s
                """
            cursor.execute(delete_question_query, (LabNum, CSYID, maxQuestion))
                
        except mysql.connector.Error as error:
                conn.rollback()
                return jsonify({"error": f"An error occurred: {error}","Status":False}), 500
        #delete old assign
        try:
            delete_assign_query = """ 
                    DELETE ASN FROM assign ASN WHERE ASN.Lab = %s AND ASN.CSYID = %s
                """
            cursor.execute(delete_assign_query, (LabNum, CSYID))
            
        except mysql.connector.Error as error:
            conn.rollback()
            return jsonify({"error": f"An error occurred: {error}","Status":False}), 500
        
        #assign to section
        try:
            for section, dates in submittedDates.items():
                Publish = dates['publishDate']
                Due = dates['dueDate']
                CID = GetCID(conn,cursor,section,CSYID)
                insert_assignTo = """ INSERT INTO assign (Lab,Publish,Due,CID,CSYID) VALUES(%s,%s,%s,%s,%s) """
                cursor.execute(insert_assignTo,(LabNum,Publish,Due,CID,CSYID))
        except mysql.connector.Error as error:
            conn.rollback()
            return jsonify({"error": f"An error occurred: {error}","Status":False}), 500
        conn.commit()
        return jsonify({"message":"create success","Status":True}), 200
        
    except mysql.connector.Error as error:
        conn.rollback()
        return jsonify({"error": f"An error occurred: {error}","Status":False}), 500