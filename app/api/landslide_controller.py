# -*- coding: utf-8 -*-
import os
# from urllib import response
from abc import ABC
from datetime import datetime
from functools import lru_cache

from flask import request, send_from_directory
from flask.views import MethodView

from app import keras_classify, keras_subFolder, globalInMem, ftpclient, \
    enet_ground_classify, enet_ground_subFolder, enet_air_classify, enet_air_subFolder
from app.model.classifyhandle import ImageClassifyHandle
from app.tools.classifyTools import ClassifyTools
# dotenv_file = dotenv.find_dotenv()
# dotenv.load_dotenv(dotenv_file)
# dotenv.set_key(dotenv_file, "test", 'os.environ[]')
from app.tools.decorators_tool import is_json


def send_static_content(path):
    return send_from_directory('public', path)


def check_ping(hostname="192.168.4.200"):
    response = os.system("ping  -n 1 " + hostname)
    # and then check the response...
    if response == 0:
        pingstatus = True
    else:
        pingstatus = False

    return pingstatus


class PublicPathController(MethodView):
    def get(self, path):
        return send_static_content(path)


class ActionServiceController(MethodView):
    def post(self):
        if request.is_json:
            jsondata = request.get_json()
            action = jsondata['action']
            if action == "shutdown":
                func = request.environ.get('werkzeug.server.shutdown')
                func()
            elif action == "ftpupload":
                ftpclient.upload_all(
                    base_local_dir=keras_subFolder,
                    base_remote_dir=os.getenv("keras_model_version"))
        return {"status": 200}


class UploadImageToClassifyController(MethodView):
    def post(self, classifyHandle, modelPath):
        return ClassifyTools().UploadImageToClassify(handle=classifyHandle,
                                                     modelPath=modelPath)


class UploadImageUrlToClassifyController(MethodView):
    def post(self, classifyHandle):
        now = datetime.now()
        print("now =", now)
        return ClassifyTools().UploadImageUrlToClassify(handle=classifyHandle)


class ClassifyErrorByPersonController(MethodView):
    def post(self, classify_model, subFolder, jsondata,modelName):
        responsestr, filejsondata = ClassifyTools().errorByPerson(classify_model=classify_model,
                                                                  subFolder=subFolder,
                                                                  filejsondata=jsondata)
        if filejsondata is not None:
            # globalInMem.setKerasfilejsondata(filejsondata)
            globalInMem.setfilejsondata( modelName, filejsondata)
        return responsestr


class VersionController(MethodView):
    def post(self, sver):
        if type(sver) == str:
            tf, obj = is_json(sver)
            if tf:
                sver = obj['model_name']

        return ClassifyTools().verion(sver)

    def get(self, sver):
        # path = "./app/classification/keras/image/landslide_v20210112.h5/"
        # for root, dirs, files in os.walk(path):
        #     print("  路徑：", root)
        #     print("  目錄：", dirs)
        #     print("  檔案：", files)
        if type(sver) == str:
            tf, obj = is_json(sver)
            if tf:
                sver = obj['model_name']
        return {'version': sver}


class GetFirebaseTokenController(MethodView):
    def post(self, sver=os.getenv('keras_model_version')):
        return ClassifyTools().getfirebasetoken(sver)



class EnetAirImageClassifyHandle(ImageClassifyHandle, ABC):
    def __init__(self):
        pass

    @lru_cache()
    def handle(self, content, url, urlfilename):
        prediction, jsonfiledata = super().handle(content, url, urlfilename, enet_air_classify, enet_air_subFolder,
                                                  globalInMem.getEnetAirfilejsondata())
        globalInMem.setEnetAirfilejsondata(jsonfiledata)
        return prediction



class EnetGroundImageClassifyHandle(ImageClassifyHandle, ABC):
    def __init__(self):
        pass

    @lru_cache()
    def handle(self, content, url, urlfilename):
        prediction, jsonfiledata = super().handle(content, url, urlfilename, enet_ground_classify,
                                                  enet_ground_subFolder,
                                                  globalInMem.getEnetGroundfilejsondata())
        globalInMem.setEnetGroundfilejsondata(jsonfiledata)
        return prediction



class KerasImageClassifyHandle(ImageClassifyHandle, ABC):
    def __init__(self):
        pass

    @lru_cache()
    def handle(self, content, url, urlfilename):
        prediction, jsonfiledata = super().handle(content, url, urlfilename, keras_classify, keras_subFolder,
                                                  globalInMem.getKerasfilejsondata())
        globalInMem.setKerasfilejsondata(jsonfiledata)
        return prediction
