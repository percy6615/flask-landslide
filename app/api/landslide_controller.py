# -*- coding: utf-8 -*-
import json
import os
import random

import requests
from flask import render_template, request, send_from_directory, make_response, jsonify
from flask.views import MethodView
from werkzeug.utils import secure_filename

from app import webhook_baseuri, globalRegisterUser, wra_baseuri, image_sign_static
from app.database.mysql_engine import MySQLs
from PIL import Image, ExifTags






def send_static_content(path):
    return send_from_directory('public', path)


class LiffPublicPathController(MethodView):
    def get(self, path):
        # return {"success":path}
        return send_static_content(path)



class LiffUploadImageController(MethodView):
    def post(self):
        missionID = request.args.get('mission_id')
        print('updateimage'+missionID)
        static_tmp_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'images', 'disasterpics')
        filedata = request.files['Filedata']
        if filedata is not None:
            ext = filedata.filename.split('.')[1]
            filedata.save(os.path.join(static_tmp_path, secure_filename(missionID + "." + ext)))
            image = Image.open(os.path.join(static_tmp_path, secure_filename(missionID + "." + ext)))
            for orientation in ExifTags.TAGS.keys():
                if ExifTags.TAGS[orientation] == 'Orientation':
                    break
            if image!=None and image._getexif()!=None:
                exif = dict(image._getexif().items())
                if exif[orientation] == 3:
                    image = image.rotate(180, expand=True)
                elif exif[orientation] == 6:
                    image = image.rotate(270, expand=True)
                elif exif[orientation] == 8:
                    image = image.rotate(90, expand=True)
            image.save(os.path.join(static_tmp_path, secure_filename(missionID + "." + ext)))
            image.close()
        return {"success": "200"}




def isUserRegister(user_id):
    if user_id in globalRegisterUser:
        if globalRegisterUser[user_id]['webflag'] == 1:
            return True
    return False



