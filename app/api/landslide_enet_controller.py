import json
import os
from abc import ABC

from flask.views import MethodView

from app import globalInMem, enet_Air_classify, enet_air_subFolder, enet_ground_classify, enet_ground_subFolder
from app.model.classifyhandle import ImageClassifyHandle
from app.tools.classifyTools import ClassifyTools


class EnetAirUploadImageToClassifyController(MethodView):
    def post(self):
        return ClassifyTools().UploadImageToClassify(handle=EnetAirImageClassifyHandle(),
                                                     modelPath='./app/classification/keras/enet_model/')


class EnetGroundUploadImageToClassifyController(MethodView):
    def post(self):
        return ClassifyTools().UploadImageToClassify(handle=EnetGroundImageClassifyHandle(),
                                                     modelPath='./app/classification/enet/enet_model/')


class EnetAirImageClassifyHandle(ImageClassifyHandle, ABC):
    def __init__(self):
        pass

    def handle(self, content, url, urlfilename):
        prediction, jsonfiledata = super().handle(content, url, urlfilename, enet_Air_classify, enet_air_subFolder,
                                                  globalInMem.getEnetAirfilejsondata())
        globalInMem.setEnetAirfilejsondata(jsonfiledata)
        return prediction


class EnetGroundImageClassifyHandle(ImageClassifyHandle, ABC):
    def __init__(self):
        pass

    def handle(self, content, url, urlfilename):
        prediction, jsonfiledata = super().handle(content, url, urlfilename, enet_ground_classify,
                                                  enet_ground_subFolder,
                                                  globalInMem.getEnetGroundfilejsondata())
        globalInMem.setEnetGroundfilejsondata(jsonfiledata)
        return prediction


class EnetAirUploadImageUrlToClassifyController(MethodView):
    def post(self):
        return ClassifyTools().UploadImageUrlToClassify(handle=EnetAirImageClassifyHandle())


class EnetGroundUploadImageUrlToClassifyController(MethodView):
    def post(self):
        return ClassifyTools().UploadImageUrlToClassify(handle=EnetGroundImageClassifyHandle())


class EnetAirVersionController(MethodView):
    def post(self):
        obj_air = json.loads(os.getenv('enet_air_model_version'))
        return ClassifyTools().verion(str(obj_air['model_name']))

    def get(self):
        return {'version': os.getenv('enet_air_model_version')}


class EnetGroundVersionController(MethodView):
    def post(self):
        obj_air = json.loads(os.getenv('enet_ground_model_version'))
        return ClassifyTools().verion(str(obj_air['model_name']))

    def get(self):
        return {'version': os.getenv('enet_ground_model_version')}



