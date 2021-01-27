import os

from flask import render_template

from .. import flask_app

app = flask_app.getApp()
routerCache = flask_app.getCache()

from .landslide_controller import PublicPathController, UploadImageToClassifyController, \
    UploadImageUrlToClassifyController, KerasVersionController, ClassifyErrorByPersonController, \
    GetFirebaseTokenController, ShutdownServiceController

app.add_url_rule('/webhooks/postimage',
                 view_func=UploadImageToClassifyController.as_view('ClassifyLandSlideController'))

app.add_url_rule('/webhooks/public/<path:path>',
                 view_func=PublicPathController.as_view('PublicPathController'))

app.add_url_rule('/webhooks/postimageurl',
                 view_func=UploadImageUrlToClassifyController.as_view('PostImageUrlController'))

app.add_url_rule('/webhooks/kerasversion',
                 view_func=KerasVersionController.as_view('KerasVersionController'))

app.add_url_rule('/webhooks/posterrorbyperson',
                 view_func=ClassifyErrorByPersonController.as_view('ClassifyErrorByPersonController'))

app.add_url_rule('/webhooks/postfcmtoken',
                 view_func=GetFirebaseTokenController.as_view('GetFirebaseTokenController'))

app.add_url_rule('/webhooks/shutdown',
                 view_func=ShutdownServiceController.as_view('ShutdownServiceController'))