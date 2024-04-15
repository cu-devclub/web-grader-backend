import os
from flask import request, jsonify
from werkzeug.utils import secure_filename

from function.db import get_db
from function.loadconfig import UPLOAD_FOLDER

def main():
    conn = get_db()
    cursor = conn.cursor()
    
    CSYID = request.form.get("CSYID") 
    uploaded_thumbnail = request.files["file"]
    
    if uploaded_thumbnail and uploaded_thumbnail.filename != "":
        filename = secure_filename(uploaded_thumbnail.filename)
        filename = f"{CSYID}{os.path.splitext(uploaded_thumbnail.filename)[1]}"
        
        filepath = os.path.join(UPLOAD_FOLDER, 'Thumbnail', filename)        
        try:
            update_thumbnail = """ 
                UPDATE class
                SET Thumbnail = %s
                WHERE CSYID = %s
                """
            cursor.execute(update_thumbnail, (filename, CSYID))
            conn.commit()
            uploaded_thumbnail.save(filepath)

            return jsonify({"success": True})
        except Exception as e:
            print(f"Error saving file: {e}")
            return jsonify({"success": False, "error": str(e)})
    
    return jsonify({"success": False, "error": "No file provided"})