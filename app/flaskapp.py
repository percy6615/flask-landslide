import os

from dotenv import load_dotenv
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_cache import Cache
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_moment import Moment
from flask_pagedown import PageDown
from werkzeug.middleware.proxy_fix import ProxyFix

from .classification.enet.enet_classify_land import EnetClassifyLandslide

from .classification.keras.keras_classify_land import KerasClassifyLandslide
from .tools.config_tools import config


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
        load_dotenv(override=True)
        self.c = config()
        self.keras_classify = KerasClassifyLandslide()
        self.enet_ground_classify = EnetClassifyLandslide(inputModelName=os.getenv('enet_ground_model_version'))
        self.enet_air_classify = EnetClassifyLandslide(inputModelName=os.getenv('enet_air_model_version'))
        self.app.config['JWT_SECRET_KEY'] = 'this-should-be-change'
        self.cache = Cache(self.app, config={'CACHE_TYPE': 'filesystem', 'CACHE_DIR': self.c.getbasedircache()})
        self.writepid()

    def getApp(self):
        return self.app

    def getCache(self):
        return self.cache

    def getKerasModel(self):
        return self.keras_classify

    def getEnetGroundModel(self):
        return self.enet_ground_classify

    def getEnetAirModel(self):
        return self.enet_air_classify

    def getKeras_sub_folder(self):
        return self.c.getkeras_sub_folder()

    def getEnet_air_sub_folder(self):
        return self.c.getenet_air_sub_folder()

    def getEnet_ground_sub_folder(self):
        return self.c.getenet_ground_sub_folder()

    def getConfig(self):
        return self.c

    def writepid(self):
        with open('PID.file', 'w+') as pidfile:
            pidfile.write(str(os.getpid()))
