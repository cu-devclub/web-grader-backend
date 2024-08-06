import datetime
import mysql.connector
from flask import jsonify, request
from function.loadconfig import config
from datetime import datetime, timedelta
import pytz
import base64

from google.oauth2 import id_token
from pip._vendor import cachecontrol
import google.auth.transport.requests
from flask_jwt_extended import create_access_token, set_access_cookies, get_csrf_token

from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives import serialization

from function.db import get_db
from function.google import flow, GOOGLE_CLIENT_ID

from urllib.parse import urlparse, parse_qs


def main():
    # https://sci.cugrader.com/callback?credential=Q%07nsb%a2Ro%18%ea%3Cx%18}%a4%dc#3L-%bb%9f%d1%96%9b%9f%8e%01%a4%a3%8e%d9&%ebMk%a9%b6I+%f0%a3%93%9a%06W%bd%fa!%07%83i9%e0%ab%ac%85%bf%9cO%98%b3%92%a2%89%bc1%02A%8d%d7%d3%%ba%c6%9d%14%93q%9d%fa3WL=i%ec%82%11SWn%85z%fc%cc%c0-8%01%a1%18%9b%b6%d3%ee%86DI%c6u%a8%db%f7|\%f8%car%c8%19%96~3%eb'%f1%ab%80%b3%0Cy)%17%f2%9dy%3C%f1Q%b6%ae%84Q%9b%7Fs%ca1&%e3o%b5e5%c1%d3H%87%85%0F^%0BX%3C%f9%91%e9(%1E%ea%d4%8d%d5'%f4%f85%b1w%b9r%c0R%d3LB%1B%ce%1C%a0%99%d3%fe%d6p%bb2%f5%1D%e25%b19Y%8c%ff%7F%e7S%81%ac%dfg%e00%a5_%ed%bf%87%8cN1%c1%a8%e4%22,%c2T{%eesmM%19%e1%b0c{U%c9%99%04%91h%be%d4%d9((H%e8%92%a6
    # urldict = {x[0] : x[1] for x in [x.split("=") for x in request.json['url'].split("?")[1].split("&") ]}
    # cred = urldict['credential']
    parsed_url = urlparse(request.json['url'])
    query_params = parse_qs(parsed_url.query)
    cred = query_params.get('credential', [None])[0]
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

    if cred is not None:
        try:
            private_key = serialization.load_pem_private_key(config["PRIKEY"].encode('utf-8'), password=None)
            encrypted_message = base64.urlsafe_b64decode(cred)
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
            'data': {
                "x": [decrypted_message, DMS, cred]
            }
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

    expires_access = timedelta(days=30)


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