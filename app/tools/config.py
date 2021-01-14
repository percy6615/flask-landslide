import os
import pathlib


class config():
    def __init__(self):
        self.keras_version_sub_folder = './app/classification/keras/image/' + str(os.getenv('keras_model_version'))
        self.keras_version_dispatch_record = 'env.json'
        self.keras_version_dispatch_device_token = 'device_token.json'
        if not os.path.exists(self.keras_version_sub_folder):
            for sub in range(5):
                pathlib.Path(self.keras_version_sub_folder + "/" + str(sub)).mkdir(parents=True,
                                                                                   exist_ok=True)

        if not os.path.exists(self.keras_version_sub_folder + "/data.json"):
            pathlib.Path(self.keras_version_sub_folder + "/data.json").write_text(str({}), encoding="utf-8")
        if not os.path.exists(self.keras_version_dispatch_record):
            pathlib.Path(self.keras_version_dispatch_record).write_text(str({}), encoding="utf-8")
        if not os.path.exists(self.keras_version_dispatch_device_token):
            pathlib.Path(self.keras_version_dispatch_device_token).write_text(str({}), encoding="utf-8")
        self.basedirs = os.path.abspath(os.path.dirname(__file__))
        self.basedircache = self.basedirs + '/cache'

    def getkeras_version_sub_folder(self):
        return self.keras_version_sub_folder

    def getbasedircache(self):
        return self.basedircache

    def getVersion_dispatch_record(self):
        return self.keras_version_dispatch_record

    def getdispatch_device_token(self):
        return self.keras_version_dispatch_device_token
