# SYS
import os
from colorama import Fore, Style
from importlib import import_module

# Flask
from flask_cors import CORS
from flask import app, Flask, Response, g, send_from_directory, send_file
from flask_jwt_extended import JWTManager

# Google
from function.google import secret_key

from function.db import get_db
from function.loadconfig import config, UPLOAD_FOLDER

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
for i in list_route:
    gbl[i] = import_module(i)

# init api server
app = Flask(__name__)
CORS(app, supports_credentials=False)

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1" # to allow Http traffic for local dev

# setup JWT
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_COOKIE_CSRF_PROTECT'] = False
app.config['JWT_SECRET_KEY'] = config['JWT_SECRET_KEY']

jwt = JWTManager(app)

# setup google authen
app.secret_key = secret_key

# add route to /
@app.route('/')
def index():
    return Response("I'm a teapot so I sent 418 error.", status=418, mimetype='application/json')


@app.before_request
def before_request():
    g.db = get_db()


@app.teardown_request
def teardown_request(exception=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()



@app.route('/Thumbnail/<filename>')
def get_image_thumbnail(filename):
    filepath = os.path.join(UPLOAD_FOLDER, 'Thumbnail', filename)
    return send_from_directory(os.path.dirname(filepath), os.path.basename(filepath))

@app.route("/image/<filename>", methods=["GET"])
def get_image(filename):
    image_extensions = {'png', 'jpg', 'jpeg', 'gif'}
    file_extension = filename.split('.')[-1]
    
    # Check if the file extension is in the set of allowed image extensions
    if file_extension.lower() in image_extensions:
        return send_file(os.path.join(UPLOAD_FOLDER, 'Thumbnail', filename), mimetype=f"image/{file_extension}")
    else:
        return "Invalid image file format", 400  # Return a 400 Bad Request status for invalid image formats





# loop add route to api server
for i in gbl['list_route']:
    x = i.split("_")
    app.add_url_rule('/'+x[0].replace('route.', '').replace('.', '/'), i, gbl[i].main, methods=x[1].split("-"))
    print(Fore.GREEN + x[0] + "method " + Fore.CYAN + x[1] + Fore.YELLOW + " has been mounted to server as " + Fore.GREEN + x[0].replace('route.', '').replace('.', '/')+ Style.RESET_ALL)

# start api server
if __name__ == "__main__":
    app.run(debug=bool(config['dev']), host=config['HOST'], port=int(config['PORT']))