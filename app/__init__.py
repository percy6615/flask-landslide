# inital
from flask import send_from_directory

from ftp.ftplibclientuploadall import FTPClientToDocker
from .flaskapp import FlaskApp

flask_app = FlaskApp()
keras_subFolder = flask_app.getKeras_sub_folder()
enet_air_subFolder =flask_app.getEnet_air_sub_folder()
enet_ground_subFolder =flask_app.getEnet_ground_sub_folder()
app = flask_app.getApp()
keras_classify = flask_app.getKerasModel()
enet_ground_classify = flask_app.getEnetGroundModel()
enet_Air_classify = flask_app.getEnetAirModel()
getConfig = flask_app.getConfig()

# content
from .model.global_data import GlobalInMem

globalInMem = GlobalInMem()
from .tools.firebase_tools import FirebaseNotefication

firebaseNotefication = FirebaseNotefication()
firebaseNotefication.postNewModelVersion()
ftpclient = FTPClientToDocker()
from . import api


@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'favicon.ico', mimetype='image/vnd.microsoft.icon')
