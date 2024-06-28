import os
import base64
from flask import request, jsonify, g

from function.checkPermSubmitDown import checkPermSubmitDown
from function.checkPermQDown import checkPermQDown
from function.checkPermAddDown import checkPermAddDown

def main():
    data = request.get_json()
    fileRequest = data.get('fileRequest')
    Email = data.get("Email")
    # fileRequest = ""
    # 0_<perm>_<ID>        <Additional file>
    # 1_<perm>_<QID>       <Question release>
    # 1_<perm>_<QID>       <Question source>
    # 2_<perm>_<SID>       <Submission>
    # 3_<perm>_<csyid>     <Thumbnail>
    # 
    # <perm>
    # 0 low
    # 1 high

    cur = g.db.cursor()
    
    FRL = fileRequest.strip().split("_")
    
    if len(FRL) != 3:
        return jsonify({
            'success': False,
            'msg': 'fileRequest length is not match.',
            'data': ""
        }), 200
    
    try:
        FRL = [int(i) for i in FRL]
    except:
        return jsonify({
            'success': False,
            'msg': 'fileRequest is not valid',
            'data': ""
        }), 200

    addPath = ""

    if FRL[0] == 0:
        if not checkPermAddDown(FRL[2], Email, cur):
            return jsonify({
                'success': False,
                'msg': 'You do not have access to this file.',
                'data': ""
            }), 200
        query = "SELECT Path FROM addfile WHERE ID = %s"
    elif FRL[0] == 1:
        if FRL[1] == 0:
            if not checkPermQDown(FRL[2], Email, 0, cur):
                return jsonify({
                    'success': False,
                    'msg': 'You do not have access to this file.',
                    'data': ""
                }), 200
            query = "SELECT ReleasePath, LID FROM question WHERE QID = %s"
        elif FRL[1] == 1:
            if not checkPermQDown(FRL[2], Email, 1, cur):
                return jsonify({
                    'success': False,
                    'msg': 'You do not have access to this file.',
                    'data': ""
                }), 200
            query = "SELECT SourcePath, LID FROM question WHERE QID = %s"
        else:
            return jsonify({
                'success': False,
                'msg': 'fileRequest is not valid',
                'data': ""
            }), 200
    elif FRL[0] == 2:
        if not checkPermSubmitDown(FRL[2], Email, cur):
            return jsonify({
                'success': False,
                'msg': 'You do not have access to this file.',
                'data': ""
            }), 200
        query = "SELECT SummitedFile FROM submitted WHERE SID = %s"
    elif FRL[0] == 3:
        query = "SELECT Thumbnail FROM class WHERE CSYID = %s"
        addPath = "files\\UploadFile\\Thumbnail\\"
    else:
        return jsonify({
            'success': False,
            'msg': 'fileRequest is not valid',
            'data': ""
        }), 200

    # Execute a SELECT statement
    cur.execute(query, (FRL[2],))
    # Fetch all rows
    data = cur.fetchall()

    # Close the cursor
    cur.close()

    file_path = addPath + data[0][0]
    filename = data[0][0]
    if FRL[0] == 1:
        prefilename = data[0][0].split("\\")[-1].split("_")
        filename = f'{Email.split("@")[0]}-L{data[0][1]}-Q{int(prefilename[1]) + 1}-{prefilename[2]}'

    file_content = ""
    # Read the file content
    with open(file_path, "rb") as file:
        file_content = file.read()

    # Encode the file content to base64
    encoded_file_content = base64.b64encode(file_content).decode('utf-8')
    
    # Construct response data
    response_data = {
        'success': True,
        'fileContent': encoded_file_content,
        'fileType': "application/octet-stream",  # Adjust as needed
        'downloadFilename': filename
    }
    
    return jsonify(response_data)
