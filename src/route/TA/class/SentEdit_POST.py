import pytz
import json
import datetime
import mysql.connector
from flask import request, jsonify

from function.db import get_db

gmt_timezone = pytz.timezone('GMT')

def main():
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        data = json.loads(request.form.get('Data'))
        
        UID = data['UID']
        Lab = data['Lab']
        Question = data['Question']
        score = data['updatescore']
        CSYID = data['CSYID']
        update_score_time = datetime.now(gmt_timezone)
        
        print(UID,Lab,Question,score,CSYID)
        
        sentin_edit_query = """ 
        INSERT INTO Submitted (UID, Lab, Question, score, CSYID, LastEdit)
        VALUES (%s, %s, %s, %s, %s, %s) AS new
        ON DUPLICATE KEY UPDATE score = new.score, LastEdit = new.LastEdit
        """
        cursor.execute(sentin_edit_query,(UID, Lab, Question, score, CSYID, update_score_time))
        conn.commit()
        return jsonify({"message":"update score successful"}), 500
    except mysql.connector.Error as error:
        conn.rollback()
        return jsonify({"error": f"An error occurred: {error}"}), 500