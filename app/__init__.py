# inital
from flask import send_from_directory

from .flaskapp import FlaskApp

flask_app = FlaskApp()
kerasVersion_subFolder = flask_app.getKeras_version_sub_folder()
app = flask_app.getApp()
keras_classify = flask_app.getKerasModel()
getConfig = flask_app.getConfig()

# content
from .model.global_data import KerasGlobalInMem

kerasGlobalInMem = KerasGlobalInMem()
from .tools.firebase_tools import FirebaseNotefication

firebaseNotefication = FirebaseNotefication()
firebaseNotefication.postNewModelVersion()
from . import api


@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'favicon.ico', mimetype='image/vnd.microsoft.icon')
