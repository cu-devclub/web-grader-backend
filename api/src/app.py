# SYS
import os
from tabulate import tabulate
from colorama import Fore, Style
from importlib import import_module

# Flask
from flask_cors import CORS
from flask import app, Flask, Response, g, send_from_directory, send_file, jsonify
from flask_jwt_extended import JWTManager

# Google
from function.google import secret_key

from function.db import get_db, get_dbdict
from function.loadconfig import config, UPLOAD_FOLDER, isDev


# list route file
def tree_route(startpath):
    ListRoute = []
    for root, dirs, files in os.walk(startpath):
        if (not "__pycache__" in root) and len(files) != 0:
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



if not isDev:
    CORS(app, supports_credentials=True, resources={r"/api/*": {"origins": config['DOMAIN']}})
else: 
    CORS(app, supports_credentials=True)

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1" if isDev else "0" # to allow Http traffic for local dev

# setup JWT
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_COOKIE_CSRF_PROTECT'] = True
app.config['JWT_SECRET_KEY'] = config['JWT_SECRET_KEY']
app.config['JWT_COOKIE_SAMESITE'] = "None"
app.config['JWT_COOKIE_SECURE'] = True

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

jwt = JWTManager(app)

# setup google authen
app.secret_key = secret_key

# add route to /
@app.route('/api/')
def index():
    return Response("I'm a teapot so I sent 418 error.", status=418, mimetype='application/json')


@app.before_request
def before_request():
    g.db = get_db()
    g.dbdict = get_dbdict()


@app.teardown_request
def teardown_request(exception=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()
        
    dbdict = g.pop('dbdict', None)
    if dbdict is not None:
        dbdict.close()

@app.route('/api/Thumbnail/<filename>')
def get_image_thumbnail(filename):
    filepath = os.path.join(UPLOAD_FOLDER, 'Thumbnail', filename)
    return send_from_directory(os.path.dirname(filepath), os.path.basename(filepath))

@app.route("/api/image/<filename>", methods=["GET"])
def get_image(filename):
    image_extensions = {'png', 'jpg', 'jpeg', 'gif'}
    file_extension = filename.split('.')[-1]
    
    # Check if the file extension is in the set of allowed image extensions
    if file_extension.lower() in image_extensions:
        return send_file(os.path.join(UPLOAD_FOLDER, 'Thumbnail', filename), mimetype=f"image/{file_extension}")
    else:
        return "Invalid image file format", 400  # Return a 400 Bad Request status for invalid image formats

@jwt.unauthorized_loader
def custom_unauthorized_response(callback):
    return jsonify({
        'success': False,
        'msg':"Unauthorized."
    })

@jwt.invalid_token_loader
def custom_invalid_token_response(callback):
    return jsonify({
        'success': False,
        'msg':"Invalid token."
    })

@jwt.expired_token_loader
def custom_expired_token_response(jwt_header, jwt_payload):
    return jsonify({
        'success': False,
        'msg': "Expired token."
    })

mount_info = []

# loop add route to api server
for i in gbl['list_route']:
    x = i.split("_")
    app.add_url_rule('/'+x[0].replace('route.', '').replace('.', '/'), i, gbl[i].main, methods=x[1].split("-"))
    mount_info.append([Fore.GREEN + x[0], Fore.CYAN + x[1], Fore.YELLOW + x[0].replace('route.', '').replace('.', '/') + Style.RESET_ALL])

print(tabulate(mount_info, headers=['Route', 'Method', "Path"]))

# start api server
if __name__ == "__main__":
    app.run(debug=isDev, host=config['HOST'], port=int(config['PORT']))
    