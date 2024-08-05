from flask import jsonify, request
from function.google import flow

def main():
    # authorization_url, state = flow.authorization_url()
    # return jsonify({
    #     'success': True,
    #     'msg': '',
    #     'data': {
    #         'url': authorization_url,
    #         'state': state
    #     }
    # })
    return jsonify({
        'success': False,
        'msg': 'This route is no loager using.',
        'data': {}
    })