import json
import pathlib

from .. import keras_version_sub_folder
from ..tools.sync_tool import singleton


@singleton
class KerasGlobalInMem:
    # getInstance

    def __init__(self):
        self.kerasfiledata = pathlib.Path("./app" + keras_version_sub_folder + "/data.json",
                                          encoding="utf-8").read_text(
            encoding='utf-8')

        self.kerasfilejsondata = json.loads(self.kerasfiledata)  # 解析為陣列

    def getkerasfiledata(self):
        return self.kerasfiledata

    def getkerasfilejsondata(self):
        return self.kerasfilejsondata
