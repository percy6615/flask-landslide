import os

from flask import render_template

from .. import flask_app

app = flask_app.getApp()
routerCache = flask_app.getCache()

from .landslide_controller import PublicPathController,  ClassifyLandSlideController, \
    PostImageUrlController, KerasVersionController



app.add_url_rule('/webhooks/classify',
                 view_func=ClassifyLandSlideController.as_view('ClassifyLandSlideController'))

app.add_url_rule('/webhooks/public/<path:path>',
                 view_func=PublicPathController.as_view('PublicPathController'))

app.add_url_rule('/webhooks/postimageurl',
                 view_func=PostImageUrlController.as_view('PostImageUrlController'))

app.add_url_rule('/webhooks/kerasversion',
                 view_func=KerasVersionController.as_view('KerasVersionController'))



