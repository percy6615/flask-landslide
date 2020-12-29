import os

from flask import render_template

from .. import flask_app

app = flask_app.getApp()
routerCache = flask_app.getCache()

from .landslide_controller import LiffPublicPathController,  LiffUploadImageController

app.add_url_rule('/webhooks/uploadimage',
                 view_func=LiffUploadImageController.as_view('LiffUploadImageController'))


app.add_url_rule('/webhooks/public/<path:path>',
                 view_func=LiffPublicPathController.as_view('LiffPublicPathController'))







