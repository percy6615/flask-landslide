import logging
from flask import request, render_template
from flask_restful import Resource
# from app.auth import routerCache
from flask.views import MethodView


class Fuck1Controller(MethodView):
    # def __init__(self, *args, **kwargs):
    # super.__init__(*args, **kwargs)

    def post(self):
        # get X-Line-Signature header value
        # signature = request.headers['X-Line-Signature']
        # get request body as text
        body = request.get_data(as_text=True)
        logging.info("Request body: " + body)
        # app.logger.info("Request body: " + body)
        print("Request body: " + body)
        # handle webhook body

    # @routerCache.cached()
    def get(self):
        return render_template('index.html')
