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
from werkzeug.middleware.proxy_fix import ProxyFix

from .classification.keras.keras_classify_land import KerasClassifyLandslide
from .tools.config import config
from .tools.sync_tool import singleton


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

from . import api


@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'favicon.ico', mimetype='image/vnd.microsoft.icon')


class PostNewModelVersion():
    def __init__(self):
        pass

    def handle(self):
        model_version_record = kerasGlobalInMem.getkeras_version_record()
        firebase_token_record = kerasGlobalInMem.getDevice_token_record()
        keras_model_version = os.getenv('keras_model_version')
        if keras_model_version not in model_version_record:
            model_version_record[keras_model_version] = {'modelversion': keras_model_version,
                                                         'time': datetime.now().strftime("%m/%d/%Y, %H:%M:%S")}
            model_version_dumps = json.dumps(model_version_record, ensure_ascii=False)
            pathlib.Path(getConfig.getVersion_dispatch_record()).write_text(model_version_dumps,
                                                                            encoding="utf-8")
        for k in firebase_token_record:
            print(firebase_token_record[k])
PostNewModelVersion().handle()