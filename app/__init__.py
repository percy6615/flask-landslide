import random

from flask import Flask, send_from_directory, Response, send_file
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_cache import Cache
from flask_bootstrap import Bootstrap
import os
from flask_mail import Mail
from flask_moment import Moment
from flask_pagedown import PageDown
from app.model.global_mem_value import GlobalInMem
#from .database.redis_engine import redis_handle
from .tools.sync_tool import singleton

basedirs = os.path.abspath(os.path.dirname(__file__))
basedir = basedirs + '/cache'
globalInMem = GlobalInMem().handleUserList()
globalRegisterUser = globalInMem.getUserList()
globalRegisterGroup = globalInMem.getGroupList()
globalMissionData = globalInMem.getMissionid()

webhook_baseuri = os.getenv('webhook_baseuri')
wra_baseuri = os.getenv('wra_baseuri')
wra_register = os.getenv('wra_register')
image_sign_static = os.getenv('image_sign_static')
image_register_static = os.getenv('image_register_static')


@singleton
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

        self.app.config['JWT_SECRET_KEY'] = 'this-should-be-change'
        self.cache = Cache(self.app, config={'CACHE_TYPE': 'filesystem', 'CACHE_DIR': basedir})

    def getApp(self):
        return self.app

    def getCache(self):
        return self.cache


flask_app = FlaskApp()
app = flask_app.getApp()


@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'favicon.ico', mimetype='image/vnd.microsoft.icon')



from . import api
from . import auth
