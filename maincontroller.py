import subprocess

import flask
import requests
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix

app = flask.Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_host=1, x_proto=1)
cors = CORS(app)


class mem:
    def __init__(self):
        self.ismachine = False

    def getmem(self):
        return self.ismachine

    def setmem(self, machine):
        self.ismachine = machine


inmeme = mem()
if not inmeme.getmem():
    subprocess.Popen('python main.py', shell=True)
    inmeme.setmem(True)

@app.route("/start")
def start():
    if not inmeme.getmem():
        subprocess.Popen('python main.py', shell=True)
        inmeme.setmem(True)
    return {"status": 200}


@app.route("/stop")
def stop():
    if inmeme.getmem():
        url = "http://localhost:8000/webhooks/shutdown"
        requests.post(url,data={"action":"shutdown"})
        inmeme.setmem(False)
    return {"status": 200}


app.run(host='0.0.0.0', debug=False, port=5000, threaded=True)
