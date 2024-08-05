import datetime
import requests
import mysql.connector
from flask import jsonify, request, Response

from google.oauth2 import id_token
from pip._vendor import cachecontrol
import google.auth.transport.requests
from flask_jwt_extended import create_access_token, set_access_cookies, get_csrf_token

from function.db import get_db
from function.google import flow, GOOGLE_CLIENT_ID


def main():
    urldict = {x[0] : x[1] for x in [x.split("=") for x in request.json['url'].split("?")[1].split("&") ]}
    # if not request.json['state'] == urldict["state"]:
    #     return jsonify({
    #         'success': False,
    #         'msg': 'Authen state does not match',
    #         'data': {}
    #     })
    try:
        flow.fetch_token(authorization_response=request.json['url'])
    except Exception as e:
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