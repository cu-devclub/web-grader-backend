import datetime
import requests
import mysql.connector
from flask import jsonify, request

from google.oauth2 import id_token
from pip._vendor import cachecontrol
import google.auth.transport.requests
from flask_jwt_extended import create_access_token, set_access_cookies, create_refresh_token

from function.db import get_db
from function.google import flow, GOOGLE_CLIENT_ID


def main():
    flow.fetch_token(authorization_response=request.json['url'])
    urldict = {x[0] : x[1] for x in [x.split("=") for x in request.json['url'].split("?")[1].split("&") ]}
    if not request.json['state'] == urldict["state"]:
        return jsonify({
            'success': False,
            'msg': 'Authen state does not match',
            'data': {}
        })
    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID,
        clock_skew_in_seconds=9999
    )

    email = id_info.get("email")
    UID = email.split("@")[0]
    name = id_info.get("name")
    # profile = id_info.get("picture")
    role = 1 if ("student" in email.split("@")[1]) else 2

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
            'msg': '',
            'data': {}
        }), 200


    # connection = sqlite3.connect('sql.db')
    # cursor = connection.execute(f"SELECT * from user where email='{email}'")
    # if len(cursor.fetchall()) == 0:
    #     connection.execute(f"INSERT INTO user VALUES ('{name}', '{email}', '{profile}')")
    #     connection.commit()
    # cursor.close()
    # connection.close()

    expires_access = datetime.timedelta(days=30)

    access_token = create_access_token(identity=email, expires_delta=expires_access)
    resp = jsonify({
        'success': True,
        'msg': '',
        'data': {
            "Email": email
        }
    })
    set_access_cookies(resp, access_token)

    return resp, 200