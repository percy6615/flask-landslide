from flask import Flask, send_from_directory
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_cache import Cache
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask_pagedown import PageDown
from app.model.global_mem_value import GlobalInMem
from .classification.keras.keras_classify_land import KerasClassifyLandslide
from .tools.sync_tool import singleton
from .tools.config import config


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
        self.keras_version_sub_folder = self.c.getkeras_version_sub_folder()
        basedir, basedircache = self.c.getbasedircache()
        self.keras_classify = KerasClassifyLandslide()
        self.app.config['JWT_SECRET_KEY'] = 'this-should-be-change'
        self.cache = Cache(self.app, config={'CACHE_TYPE': 'filesystem', 'CACHE_DIR': basedircache})

    def getApp(self):
        return self.app

    def getCache(self):
        return self.cache

    def getKerasModel(self):
        return self.keras_classify

    def getkeras_version_sub_folder(self):
        return self.keras_version_sub_folder


flask_app = FlaskApp()
keras_version_sub_folder = flask_app.getkeras_version_sub_folder()
app = flask_app.getApp()
keras_classify = flask_app.getKerasModel()

from .model.global_data import KerasGlobalInMem
kerasglobalInMem = KerasGlobalInMem()



@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'favicon.ico', mimetype='image/vnd.microsoft.icon')


from . import api
from . import auth
