import json
import pathlib
from abc import ABCMeta

from .. import kerasVersion_subFolder, getConfig
from ..tools.sync_tool import Singletonclass


@Singletonclass.singleton
class GlobalInMem():
    def __init__(self):
        self.kerasfilejsondata = self.load(kerasVersion_subFolder + "/data.json")
        self.version_dispatch_record = self.load(getConfig.getVersion_evn_fileName())
        self.device_token = self.load(getConfig.getDispatch_device_token())

    def load(self, filePath):
        return json.loads(pathlib.Path(filePath, encoding="utf-8").read_text(encoding='utf-8'))

    def getkerasfilejsondata(self):
        return self.kerasfilejsondata

    def getVersion_dispatch_record(self):
        return self.version_dispatch_record

    def getDevice_token_record(self):
        return self.device_token


