import json
import pathlib

from .. import keras_subFolder, getConfig, enet_air_subFolder, enet_ground_subFolder
from ..tools.sync_tool import Singletonclass


@Singletonclass.singleton
class GlobalInMem:
    def __init__(self):
        self.kerasfilejsondata = self.load(keras_subFolder + "/data.json")
        self.enetairfilejsondata = self.load(enet_air_subFolder + "/data.json")
        self.enetgroundfilejsondata = self.load(enet_ground_subFolder + "/data.json")
        self.version_record = self.load(getConfig.getVersion_evn_fileName())
        self.device_token = self.load(getConfig.getDispatch_device_token())

    def load(self, filePath):
        return json.loads(pathlib.Path(filePath, encoding="utf-8").read_text(encoding='utf-8'))

    def getKerasfilejsondata(self):
        return self.kerasfilejsondata

    def setKerasfilejsondata(self, data):
        self.kerasfilejsondata = data

    def getEnetAirfilejsondata(self):
        return self.enetairfilejsondata

    def setEnetAirfilejsondata(self, data):
        self.enetairfilejsondata = data

    def getEnetGroundfilejsondata(self):
        return self.enetgroundfilejsondata

    def setEnetGroundfilejsondata(self, data):
        self.enetgroundfilejsondata = data

    def getVersion_record(self):
        return self.version_record

    def getDevice_token_record(self):
        return self.device_token

    def setfilejsondata(self, filejson, data):
        if filejson == 'keras':
            self.kerasfilejsondata = data
        elif filejson == 'enetair':
            self.enetairfilejsondata = data
        elif filejson == 'enetground':
            self.enetgroundfilejsondata = data

    def getfilejsondata(self, filejson):
        if filejson == 'keras':
            return self.kerasfilejsondata
        elif filejson == 'enetair':
            return self.enetairfilejsondata
        elif filejson == 'enetground':
            return self.enetgroundfilejsondata
