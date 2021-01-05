import os
import pathlib


class config():
    def __init__(self):
        self.keras_version_sub_folder = '/classification/keras/image/' + os.getenv('keras_model_version')

        if not os.path.exists("./app" + self.keras_version_sub_folder):
            for sub in range(5):
                pathlib.Path("./app" + self.keras_version_sub_folder + "/" + str(sub)).mkdir(parents=True,
                                                                                             exist_ok=True)

        if not os.path.exists("./app" + self.keras_version_sub_folder + "/data.json"):
            pathlib.Path("./app" + self.keras_version_sub_folder + "/data.json").write_text(str({}), encoding="utf-8")
        self.basedirs = os.path.abspath(os.path.dirname(__file__))
        self.basedircache = self.basedirs + '/cache'

    def getkeras_version_sub_folder(self):
        return self.keras_version_sub_folder

    def getbasedircache(self):
        return self.basedirs, self.basedircache
