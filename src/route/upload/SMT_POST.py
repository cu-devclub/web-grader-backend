import os
import pytz
from datetime import datetime
from flask import request, jsonify
from werkzeug.utils import secure_filename

from function.db import get_db
from function.isIPYNB import isIPYNB
from function.loadconfig import UPLOAD_FOLDER

gmt_timezone = pytz.timezone('GMT')

def main():
    
    UID = request.form.get("UID")
    CSYID = request.form.get("CSYID")
    Lab = request.form.get("Lab")
    Question = request.form.get("Question")    
    uploaded_file = request.files["file"]

    upload_time = datetime.now(gmt_timezone)
    
    if not isIPYNB(uploaded_file.filename):
        return jsonify({"message": "upload file must be .ipynb"}), 500 
    
    if uploaded_file.filename != "":
        filename = secure_filename(uploaded_file.filename)        
        filename = f"{UID}-L{Lab}Q{Question}-{CSYID}{os.path.splitext(uploaded_file.filename)[1]}"
        filepath = os.path.join(UPLOAD_FOLDER,'TurnIn',filename)

        try:
            uploaded_file.save(filepath)
            ###test score
            score=10
            
            try:
                conn = get_db()
                cursor = conn.cursor()

                Insert_TurnIn = """ INSERT INTO submitted (UID, Lab, Question, TurnInFile, score, Timestamp, CSYID)
                    VALUES (%s, %s, %s, %s, %s, %s, %s) AS new
                    ON DUPLICATE KEY UPDATE TurnInFile = new.TurnInFile,Timestamp = new.Timestamp,score = new.score; """
                cursor.execute(Insert_TurnIn,(UID,Lab,Question,uploaded_file.filename,score,upload_time,CSYID))
                conn.commit()
                
            except Exception as e:
                conn.rollback()
                print("Error update score: {e}")
                return jsonify({"message": "An error occurred while updating score."}), 500
            
            return jsonify({"message": "File uploaded successfully!","At":upload_time.strftime("%Y-%m-%d %H:%M:%S"),"FileName":uploaded_file.filename,"Score":score})

        except Exception as e:
            # Handle any exceptions during file saving gracefully
            print("Error saving file: {e}")
            return jsonify({"message": "An error occurred while uploading the file."}), 500