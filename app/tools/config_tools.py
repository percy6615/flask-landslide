import json
import os
import pathlib


def createFolder(folderPath):
    if not os.path.exists(folderPath):
        pathlib.Path(folderPath).write_text(str({}), encoding="utf-8")


class config():
    def __init__(self):
        self.keras_sub_folder = './app/classification/keras/image/' + str(os.getenv('keras_model_version'))
        obj_air = json.loads(os.getenv('enet_air_model_version'))
        self.enet_air_sub_folder = './app/classification/enet/image/' + str(obj_air['model_name'])

        obj_ground = json.loads(os.getenv('enet_ground_model_version'))
        self.enet_ground_sub_folder = './app/classification/enet/image_ground/' + str(obj_ground['model_name'])

        if not os.path.exists(self.keras_sub_folder):
            for sub in range(5):
                pathlib.Path(self.keras_sub_folder + "/" + str(sub)).mkdir(parents=True,
                                                                           exist_ok=True)
        if not os.path.exists(self.enet_air_sub_folder):
            for sub in range(5):
                pathlib.Path(self.enet_air_sub_folder + "/" + str(sub)).mkdir(parents=True,
                                                                              exist_ok=True)

        if not os.path.exists(self.enet_ground_sub_folder):
            for sub in range(5):
                pathlib.Path(self.enet_ground_sub_folder + "/" + str(sub)).mkdir(parents=True,
                                                                                 exist_ok=True)

        createFolder(self.keras_sub_folder + "/data.json")
        createFolder(self.enet_air_sub_folder + "/data.json")
        createFolder(self.enet_ground_sub_folder + "/data.json")

        self.version_env_fileName = 'env.json'
        self.version_dispatch_device_token = 'device_token.json'
        createFolder(self.version_env_fileName)
        createFolder(self.version_dispatch_device_token)
        self.basedirs = os.path.abspath(os.path.dirname(__file__))
        self.basedircache = self.basedirs + '/cache'


    def getkeras_sub_folder(self):
        return self.keras_sub_folder

    def getenet_air_sub_folder(self):
        return self.enet_air_sub_folder

    def getenet_ground_sub_folder(self):
        return self.enet_ground_sub_folder

    def getbasedircache(self):
        return self.basedircache

    def getVersion_evn_fileName(self):
        return self.version_env_fileName

    def getDispatch_device_token(self):
        return self.version_dispatch_device_token

