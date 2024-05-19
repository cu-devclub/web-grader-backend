from flask import jsonify, request
from function.google import flow
# import datetime
# from flask_jwt_extended import create_access_token, set_access_cookies

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



# pre write for cunet
    # expires_access = datetime.timedelta(days=30)
    
    # data = request.get_json()

    # ac_token_data = {
    #     "uid": data.get("username"),
    #     "type": 0
    # }

    # access_token = create_access_token(identity=ac_token_data, expires_delta=expires_access)
    # resp = jsonify({
    #     'success': True,
    #     'msg': '',
    #     'data': ac_token_data
    # })
    # set_access_cookies(resp, access_token)

    # return resp, 200