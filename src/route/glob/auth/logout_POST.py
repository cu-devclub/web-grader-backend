from flask import jsonify
from flask_jwt_extended import unset_jwt_cookies

def main():
    resp = jsonify({
        'success': True,
        'msg': '',
        'data': {}
    })
    unset_jwt_cookies(resp)
    return resp, 200