import json
import pathlib

from .. import kerasVersion_subFolder, getConfig
from ..tools.sync_tool import singleton


@singleton
class KerasGlobalInMem:
    # getInstance

    def __init__(self):
        self.kerasfilejsondata = json.loads(pathlib.Path(kerasVersion_subFolder + "/data.json",
                                                         encoding="utf-8").read_text(
            encoding='utf-8'))  # 解析為陣列
        self.keras_version_record = json.loads(pathlib.Path(getConfig.getVersion_dispatch_record(),
                                                            encoding="utf-8").read_text(
            encoding='utf-8'))
        self.device_token = json.loads(pathlib.Path(getConfig.getdispatch_device_token(),
                                                    encoding="utf-8").read_text(
            encoding='utf-8'))

    def getkerasfilejsondata(self):
        return self.kerasfilejsondata

    def getkeras_version_record(self):
        return self.keras_version_record

    def getDevice_token_record(self):
        return self.device_token
