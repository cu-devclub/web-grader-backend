import os
from flask import request, jsonify, g
from werkzeug.utils import secure_filename

from function.db import get_db
from function.isPicture import isPicture
from function.loadconfig import UPLOAD_FOLDER
from function.isCET import isCET

from flask_jwt_extended import jwt_required, get_jwt_identity

@jwt_required()
def main():
    Email = get_jwt_identity()['email']
    conn = get_db()
    cursor = conn.cursor()
    
    CSYID = request.form.get("CSYID") 
    uploaded_thumbnail = request.files["file"]

    if(not isCET(g.db, g.db.cursor(), Email, CSYID)):
        return jsonify({
            'success': False,
            'msg': "You don't have permission",
            'data': {}
        }), 200
    
    if uploaded_thumbnail and uploaded_thumbnail.filename != "":
        filename = secure_filename(uploaded_thumbnail.filename)

        if(not isPicture(filename)):
            return jsonify({
                "success": False,
                "msg": "Thumbnail must be png, jpg, jpeg or gif."
            })


        filename = f"{CSYID}{os.path.splitext(uploaded_thumbnail.filename)[1]}"

        # check path
        thndirec = os.path.join(UPLOAD_FOLDER, 'Thumbnail')
        if not os.path.exists(thndirec):
            os.makedirs(thndirec)
        
        filepath = os.path.join(thndirec, filename)        
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
            return jsonify({"success": False, "msg": str(e)})
    
    return jsonify({"success": False, "msg": "No file provided"})