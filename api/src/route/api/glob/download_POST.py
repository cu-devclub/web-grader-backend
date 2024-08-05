import os
import base64
import json
from flask import request, jsonify, g

from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization

from function.checkPermSubmitDown import checkPermSubmitDown
from function.checkPermQDown import checkPermQDown
from function.checkPermAddDown import checkPermAddDown
from function.loadconfig import UPLOAD_FOLDER, config

from flask_jwt_extended import jwt_required, get_jwt_identity

@jwt_required()
def main():
    Email = get_jwt_identity()['email']

    data = request.get_json()
    fileRequest = data.get('fileRequest')
    
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

    editBefore = True

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
            if checkPermQDown(FRL[2], Email, 1, cur):
                editBefore = False
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
        addPath = os.path.join(UPLOAD_FOLDER, "Thumbnail")
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

    if FRL[0] == 1:
        select_query = "SELECT Lab FROM lab WHERE LID = %s"
        cur.execute(select_query, (data[0][1],))
        resultLab = cur.fetchone()

    # Close the cursor
    cur.close()

    file_path = os.path.join(addPath, data[0][0])
    filename = data[0][0]
    
    if FRL[0] == 1:
        prefilename = os.path.split(data[0][0])[-1].split("_")
        if FRL[1] == 0:
            filename = f'{Email.split("@")[0]}-L{resultLab[0]}-Q{int(prefilename[1]) + 1}-{"_".join(prefilename[2:])}'
        if FRL[1] == 1:
            filename = "_".join(prefilename[2:])

    file_content = ""
    # Read the file content
    with open(file_path, "rb") as file:
        file_content = file.read()

    if FRL[0] == 1 and editBefore:
        nb_edit = json.loads(file_content)
        public_key = serialization.load_pem_public_key(config["PUBKEY"].encode('utf-8'))
        encrypted = public_key.encrypt(
            bytes(f"{Email.split('@')[0]}_{data[0][1]}_{FRL[2]}", 'utf-8'),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        nb_edit["metadata"]["BondSan"] = encrypted.hex()
        file_content = bytes(json.dumps(nb_edit), 'utf-8')

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
