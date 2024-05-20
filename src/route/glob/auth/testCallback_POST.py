import datetime
import requests
import mysql.connector
from flask import jsonify, request
from function.db import get_db


def main():
    DataJ = request.get_json()


    email = DataJ.get("email")
    emailsplit = email.split("@")
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

    resp = jsonify({
        'success': True,
        'msg': '',
        'data': ''
    })
    return resp, 200