import datetime
import requests
import mysql.connector
from flask import jsonify, request
from function.db import get_db
import re

from function.loadconfig import config, isDev

from flask_jwt_extended import create_access_token, set_access_cookies, get_csrf_token

regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'

def main():
    if not isDev:
        return jsonify({
            'success': False,
            'msg': '',
            'data': {}
        })

    DataJ = request.get_json()


    email = DataJ.get("email")
    emailsplit = email.split("@")
    
    if(not re.fullmatch(regex, email)):
        return jsonify({
            'success': False,
            'msg': 'Please fill with valid email form.',
            'data': {}
        }), 200

    if(not emailsplit[1] in ["chula.ac.th", "student.chula.ac.th"]):
        return jsonify({
            'success': False,
            'msg': 'Only chula email allow',
            'data': {}
        }), 200
    UID = emailsplit[0]
    name = "Test"
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
        "role": DataJ.get("role")
    }

    print(ac_token_data)

    access_token = create_access_token(identity=ac_token_data, expires_delta=expires_access)
    ac_token_data['csrf_token'] = get_csrf_token(access_token)
    resp = jsonify({
        'success': True,
        'msg': '',
        'data': ac_token_data
    })
    set_access_cookies(resp, access_token)

    return resp, 200