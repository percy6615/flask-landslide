# -*- coding: utf-8 -*-
import json
import os
import pathlib
# from urllib import response
import uuid
from io import BytesIO

import requests
from PIL import Image
from flask import request, send_from_directory
from flask.views import MethodView

from app import keras_classify, keras_version_sub_folder, kerasglobalInMem
from app.tools.image_tools import ImageHandle


def send_static_content(path):
    return send_from_directory('public', path)


class PublicPathController(MethodView):
    def get(self, path):
        return send_static_content(path)


class UploadImageToClassifyController(MethodView):
    def post(self):
        file = request.files['filedata']
        filedata = file.read()
        return KerasImageClassifyHandle().handle(filedata, None, file.filename)

    def get(self):
        pass


class UploadImageUrlToClassifyController(MethodView):
    def post(self):
        jsondata = request.get_json()
        url = jsondata['url']
        urlfilename = url.split("/")[-1]
        getContent = requests.get(url)
        return KerasImageClassifyHandle().handle(getContent.content, url, urlfilename)


class ClassifyErrorByPersonController(MethodView):
    def post(self):
        jsondata = request.get_json()
        uuid = jsondata['uuid']
        personclassname = jsondata['personclassname']
        kerasfilejsondata = kerasglobalInMem.getkerasfilejsondata()
        if uuid in kerasfilejsondata:
            personclass = keras_classify.defineClassifyStrToInt(personclassname)
            kerasfilejsondata[uuid]['personclass'] = personclass
            machinefilepath = kerasfilejsondata[uuid]['machinefilepath']
            filename=machinefilepath.split('/')[-1]
            savepath = "./app" + keras_version_sub_folder + "/" + str(personclass)+"/"+filename
            kerasfilejsondata = json.dumps(kerasfilejsondata, ensure_ascii=False)
            pathlib.Path("./app" + keras_version_sub_folder + "/data.json").write_text(kerasfilejsondata,
                                                                                       encoding="utf-8")
        return {'success': 200}


class KerasVersionController(MethodView):
    def post(self):
        return {'version': os.getenv('keras_model_version')}

    def get(self):
        return {'version': os.getenv('keras_model_version')}


class KerasImageClassifyHandle():
    def __init__(self):
        pass

    def handle(self, content, url, urlfilename):
        image_handle = ImageHandle()
        my_uuid = uuid.uuid4().hex
        image = Image.open(BytesIO(content))
        image = image_handle.imageRotate(image)
        ext = image.format.lower()
        if ext == 'jpeg':
            ext = 'jpg'

        degree = image_handle.classify_pHash(image)
        kerasfilejsondata = kerasglobalInMem.getkerasfilejsondata()
        isInDataJson = False

        for key in kerasfilejsondata:
            degreecompare = kerasfilejsondata[key]['phash']
            if len(degreecompare) == 18 and len(degree) == 18:
                hd = image_handle.hamming_distance(degreecompare, degree)
                if hd <= 0:
                    my_uuid = key
                    isInDataJson = True
                    break

        if isInDataJson:
            classify_imageName = keras_classify.defineClassifyIntToStr(kerasfilejsondata[str(my_uuid)]['personclass'])
        else:
            classify_image = keras_classify.classifyimagebytes(image)
            classify_imageName = str(keras_classify.defineClassifyIntToStr(classify_image))
            # filepath = keras_version_folder + "/" + str(classify_image) + "/" + my_uuid + "." + ext
            savepath = "./app" + keras_version_sub_folder + "/" + str(classify_image) + "/" + my_uuid + "." + ext
            kerasfilejsondata[my_uuid] = {'uuid': my_uuid, 'url': url, 'machineclass': int(classify_image),
                                          'personclass': int(classify_image), 'urlfilename': urlfilename,
                                          'machinefilepath': savepath, 'personfilepath': None, 'phash': str(degree)}
            kerasfilejsondata = json.dumps(kerasfilejsondata, ensure_ascii=False)
            pathlib.Path("./app" + keras_version_sub_folder + "/data.json").write_text(kerasfilejsondata,
                                                                                       encoding="utf-8")
            image.save(savepath, quality=100)
            image.close()

        return str({"uuid": str(my_uuid), 'machineclassname': classify_imageName})


path = './app/classification/keras/image/landslide_5class_v0.0.2.h5/2/3e4aa2074384468bb29b59a5471e68cb.jpg'
filename = path.split(keras_version_sub_folder)[-1]
print(filename)
