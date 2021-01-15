import json
import os
import pathlib
from datetime import datetime

from flask import Flask, send_from_directory
from flask_bootstrap import Bootstrap
from flask_cache import Cache
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_moment import Moment
from flask_pagedown import PageDown
from pyfcm import FCMNotification
from werkzeug.middleware.proxy_fix import ProxyFix

from .classification.keras.keras_classify_land import KerasClassifyLandslide
from .tools.config import config


class FirebaseNotefication:
    def __init__(self):
        pass

    def sendNotificationMessage(self, device_id="", message_title="", message_body="",
                                api_key=os.getenv('firebase_landslide_serverkey')):
        push_service = FCMNotification(api_key=api_key)
        registration_id = device_id
        datamsg = {
            "data": message_body
        }
        result = push_service.notify_single_device(registration_id=registration_id, message_title=message_title,
                                                   message_body=message_body, data_message=datamsg)
        print(result)

    def sendDataMessage(self, device_id="", message_body=None, api_key=os.getenv('firebase_landslide_serverkey')):
        push_service = FCMNotification(api_key=api_key)
        registration_id = device_id
        datamsg = {
            "data": message_body
        }
        result = push_service.single_device_data_message(registration_id=registration_id, data_message=datamsg)
        return result['success']

    def handle1(self, token="", id=""):
        dtoken_record = kerasGlobalInMem.getDevice_token_record()
        if id in dtoken_record:
            if dtoken_record[id]['modelversion'] != os.getenv('keras_model_version'):
                result = self.sendDataMessage(device_id=token, message_body={"title": "版本更新", "body": "版本更新"})
                if result == 1:
                    dtoken_record[id]['modelversion'] = os.getenv('keras_model_version')
        return dtoken_record

    def handle(self):
        dtoken_record = kerasGlobalInMem.getDevice_token_record()
        for k in dtoken_record:
            if dtoken_record[k]['modelversion'] != os.getenv('keras_model_version'):
                token = dtoken_record[k]['fbtoken']
                result = self.sendDataMessage(device_id=token, message_body={"title": "版本更新", "body": "版本更新"})
                if result == 1:
                    dtoken_record[k]['modelversion'] = os.getenv('keras_model_version')
        return dtoken_record


# @singleton
class FlaskApp:
    def __init__(self):
        self.app = Flask(__name__)
        self.app.wsgi_app = ProxyFix(self.app.wsgi_app, x_for=1, x_host=1, x_proto=1)
        Bootstrap(self.app)
        JWTManager(self.app)
        CORS(self.app)
        Mail(self.app)
        Moment(self.app)
        PageDown(self.app)
        self.c = config()
        self.keras_classify = KerasClassifyLandslide()
        self.app.config['JWT_SECRET_KEY'] = 'this-should-be-change'
        self.cache = Cache(self.app, config={'CACHE_TYPE': 'filesystem', 'CACHE_DIR': self.c.getbasedircache()})

    def getApp(self):
        return self.app

    def getCache(self):
        return self.cache

    def getKerasModel(self):
        return self.keras_classify

    def getKeras_version_sub_folder(self):
        return self.c.getkeras_version_sub_folder()

    def getConfig(self):
        return self.c


flask_app = FlaskApp()
kerasVersion_subFolder = flask_app.getKeras_version_sub_folder()
app = flask_app.getApp()
keras_classify = flask_app.getKerasModel()
getConfig = flask_app.getConfig()
from .model.global_data import KerasGlobalInMem

kerasGlobalInMem = KerasGlobalInMem()
firebaseNotefication = FirebaseNotefication()

from . import api


@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'favicon.ico', mimetype='image/vnd.microsoft.icon')


class PostNewModelVersion:
    def __init__(self):
        pass

    def handle(self):
        mver_record = kerasGlobalInMem.getkeras_version_record()
        sver = os.getenv('keras_model_version')
        if sver not in mver_record:
            mver_record[sver] = {'modelversion': sver, 'time': datetime.now().strftime("%m/%d/%Y, %H:%M:%S")}
            mver_dumps = json.dumps(mver_record, ensure_ascii=False)
            pathlib.Path(getConfig.getVersion_dispatch_record()).write_text(mver_dumps, encoding="utf-8")
        # TODO postfirebase
        firebaseNotefication.handle()


PostNewModelVersion().handle()
