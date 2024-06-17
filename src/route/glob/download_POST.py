import os
import base64
from flask import request, jsonify, g

def main():
    data = request.get_json()
    fileRequest = data.get('fileRequest')
    # fileRequest = ""
    # 0_<perm>_<ID>        <Additional file>
    # 1_<perm>_<QID>       <Question release>
    # 1_<perm>_<QID>       <Question source>
    # 2_<perm>_<SID>       <Submition>
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
        query = "SELECT Path FROM addfile WHERE ID = %s"
    elif FRL[0] == 1:
        if FRL[1] == 0:
            query = "SELECT ReleasePath FROM question WHERE QID = %s"
        elif FRL[1] == 1:
            query = "SELECT SourcePath FROM question WHERE QID = %s"
        else:
            return jsonify({
            'success': False,
            'msg': 'fileRequest is not valid',
            'data': ""
        }), 200
    elif FRL[0] == 2:
        query = "SELECT Path FROM submitted WHERE SID = %s"
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
    cur.execute(query, FRL[2])
    # Fetch all rows
    data = cur.fetchall()

    # Close the cursor
    cur.close()

    file_path = addPath + data[0][0]
    # Read the file content
    with open(file_path, 'rb') as file:
        file_content = file.read()

    # Encode the file content to base64
    encoded_file_content = base64.b64encode(file_content).decode('utf-8')
    
    # Construct response data
    response_data = {
        'fileContent': encoded_file_content,
        'fileType': 'application/octet-stream',  # Adjust as needed
        'downloadFilename': data[0][0],
        'additionalInfo': {
            'message': 'Here is your file with additional JSON data.'
        }
    }
    
    return jsonify(response_data)