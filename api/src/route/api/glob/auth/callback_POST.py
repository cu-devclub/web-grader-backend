import datetime
import mysql.connector
from flask import jsonify, request
from function.loadconfig import config
from binascii import unhexlify
from datetime import datetime
import pytz

from google.oauth2 import id_token
from pip._vendor import cachecontrol
import google.auth.transport.requests
from flask_jwt_extended import create_access_token, set_access_cookies, get_csrf_token

from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives import serialization

from function.db import get_db
from function.google import flow, GOOGLE_CLIENT_ID


def main():
    urldict = {x[0] : x[1] for x in [x.split("=") for x in request.json['url'].split("?")[1].split("&") ]}
    # logging.print(request.json['state'], "from client")
    # logging.print(urldict["state"], "from google")
    # if not request.json['state'] == urldict["state"]:
    #     return jsonify({
    #         'success': False,
    #         'msg': 'Authen state does not match',
    #         'data': {}
    #     })
    # try:
    #     flow.fetch_token(authorization_response=request.json['url'])
    # except Exception as e:
    #     logging.print(e, "google response")
    #     return jsonify({
    #         'success': False,
    #         'msg': 'There is problem with google.',
    #         'data': {}
    #     })
    # credentials = flow.credentials
    # request_session = requests.session()
    # cached_session = cachecontrol.CacheControl(request_session)
    # token_request = google.auth.transport.requests.Request(session=cached_session)

    # id_info = id_token.verify_oauth2_token(
    #     id_token=credentials._id_token,
    #     request=token_request,
    #     audience=GOOGLE_CLIENT_ID,
    #     clock_skew_in_seconds=9999
    # )

    # cred = request.json['credential']

    cred = urldict['credential']

    if cred is not None:
        try:
            private_key = serialization.load_pem_private_key(config["PRIKEY"].encode('utf-8'), password=None)
            encrypted_message = unhexlify(cred)
            decrypted_message = private_key.decrypt(
                encrypted_message,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            ).decode("utf-8")
        except Exception as e:
            decrypted_message = ""

        if cred is not None:
            DMS = decrypted_message.split("_")
    
    if len(DMS) != 3:
        return jsonify({
            'success': False,
            'msg': 'Credentials is not valid.',
            'data': {}
        }), 200

    id_info = {
        "email": DMS[0],
        "name": DMS[1],
        "time": DMS[2]
    }

    time_zone='Asia/Bangkok'
    time_format = "%Y-%m-%d %H:%M:%S"

    input_time = datetime.strptime(id_info["time"], time_format)
    tz = pytz.timezone(time_zone)
    input_time = tz.localize(input_time)
    current_time = datetime.now(tz)
    time_diff = (current_time - input_time).total_seconds()

    if(time_diff > 60):
        return jsonify({
            'success': False,
            'msg': 'Credentials is expired.',
            'data': {}
        }), 200

    email = id_info.get("email")
    emailsplit = email.split("@")
    if(not emailsplit[1] in ["chula.ac.th", "student.chula.ac.th"]):
        return jsonify({
            'success': False,
            'msg': 'Only chula email allow',
            'data': {}
        }), 200
    UID = emailsplit[0]
    name = id_info.get("name")
    role = 1 if ("student" in emailsplit[1]) else 2

    USR_data = (email, UID, name, role)

    try:
        conn = get_db()
        cursor = conn.cursor()

        insert_user_query = "INSERT IGNORE INTO user (Email, UID, Name, Role) VALUES (%s, %s, %s, %s)"
        cursor.execute(insert_user_query, USR_data)
        conn.commit()
    except mysql.connector.Error as error:
        conn.rollback()
        return jsonify({
            'success': False,
            'msg': 'Database error.\nPlease contact admin.',
            'data': {}
        }), 200

    expires_access = datetime.timedelta(days=30)


    ac_token_data = {
        "email": email,
        "uid": UID,
        "role": role
    }

    access_token = create_access_token(identity=ac_token_data, expires_delta=expires_access)
    ac_token_data['csrf_token'] = get_csrf_token(access_token)
    resp = jsonify({
        'success': True,
        'msg': '',
        'data': ac_token_data
    })
    set_access_cookies(resp, access_token)

    return resp, 200