from flask import jsonify
from function.google import flow

def main():
    authorization_url, state = flow.authorization_url()
    return jsonify({
        'success': True,
        'msg': '',
        'data': {
            'url': authorization_url,
            'state': state
        }
    })