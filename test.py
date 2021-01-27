import subprocess

import flask
import requests
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix

app = flask.Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_host=1, x_proto=1)
cors = CORS(app)
ismachine = False
@app.route("/start")
def start():
    if not ismachine:
        subprocess.Popen('python main.py', shell=True)
    return {"status":200}

@app.route("/stop")
def stop():
    if not ismachine:
        subprocess.Popen('python main.py', shell=True)
    return {"status":200}

app.run(host='0.0.0.0', debug=False, port=5000, threaded=True)








