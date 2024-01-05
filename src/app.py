# SYS
import os
from colorama import Fore, Style
from dotenv import dotenv_values
from importlib import import_module

# Flask
from flask_cors import CORS
from flask import app, Flask, Response
from flask_jwt_extended import JWTManager

# Google
from function.google import secret_key



# import requests
# from pip._vendor import cachecontrol
# from google.oauth2 import id_token
# import google.auth.transport.requests


# list route file
def tree_route(startpath):
    ListRoute = []
    for root, dirs, files in os.walk(startpath):
        level = root.replace(startpath, '').count(os.sep)
        if level == 2 and len(files) != 0:
            for f in files:
                if f.endswith(".py"):
                    ListRoute.append(root.replace('\\', '.').replace('/', '.') + '.' + f.replace('.py', '')) # Windows using \ in file part but linux use / so that why it have to replace both / and \ to .
    return ListRoute

list_route = tree_route('route')

# loop import route
gbl = globals()
print(list_route)
for i in list_route:
    print(i)
    gbl[i] = import_module(i)

# load config
config = dotenv_values("config/.env")

# init api server
app = Flask(__name__)
CORS(app, supports_credentials=True)

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1" # to allow Http traffic for local dev

# setup JWT
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_COOKIE_CSRF_PROTECT'] = True
app.config['JWT_SECRET_KEY'] = config['JWT_SECRET_KEY']

jwt = JWTManager(app)

# setup google authen
app.secret_key = secret_key

# add route to /
@app.route('/')
def index():
    return Response("I'm a teapot so I sent 418 error.", status=418, mimetype='application/json')

# loop add route to api server
for i in gbl['list_route']:
    app.add_url_rule('/'+i.replace('route.', '').replace('.', '/'), i, gbl[i].main, methods=['GET', 'POST'])
    print(Fore.GREEN + i + Fore.YELLOW + " has been mounted to server as " + Style.RESET_ALL)

# start api server
if __name__ == "__main__":
    app.run(debug=bool(config['dev']), host=config['HOST'], port=int(config['PORT']))