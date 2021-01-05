# -*- coding: utf-8 -*-
import json
import os
from io import BytesIO
# from urllib import response
import uuid
import requests
from flask import render_template, request, send_from_directory, make_response, jsonify
from flask.views import MethodView
from werkzeug.utils import secure_filename

from app import keras_classify, keras_version_sub_folder, kerasglobalInMem
from PIL import Image, ExifTags
import pathlib

from app.tools.phash_tools import PhashImage


def send_static_content(path):
    return send_from_directory('public', path)


class PublicPathController(MethodView):
    def get(self, path):
        # return {"success":path}
        return send_static_content(path)


class ClassifyLandSlideController(MethodView):
    def post(self):
        filedata = request.files['Filedata']
        print(filedata)


    def get(self):
        strr = keras_classify.classify().encode('utf8').decode('utf8').replace("'", '"')
        jsondata = {'data': strr}
        return str(jsondata)



class PostImageUrlController(MethodView):
    def post(self):
        jsondata = request.get_json()
        url, urlfilename, ext = self.urlhandle(jsondata)
        my_uuid = uuid.uuid4().hex
        getContent = requests.get(url)
        image = Image.open(BytesIO(getContent.content))
        image = self.imageRotate(image)
        phash_classfy = PhashImage()
        degree = phash_classfy.classify_pHash(image)
        hexCodedegree = degree.rstrip()
        kerasfilejsondata = kerasglobalInMem.getkerasfilejsondata()
        isInDataJson = False
        # suspected_image = []
        # for key in kerasfilejsondata:
        #     if kerasfilejsondata[key]['url'] == url or kerasfilejsondata[key]['urlfilename'] == urlfilename:
        #         suspected_image.append(key)
        #         continue
        #
        # for key in suspected_image:
        #     imagecompare = Image.open(kerasfilejsondata[key]['filepath'])
        #     degreecompare = phash_classfy.classify_pHash(imagecompare)
        #     hd = phash_classfy.hamming_distance(degree, degreecompare)
        #     if hd <= 0:
        #         my_uuid = key
        #         isInDataJson = True
        #         break
        for key in kerasfilejsondata:
            hexCodedegreecompare = kerasfilejsondata[key]['phash'].rstrip()
            if len(hexCodedegreecompare) == 18 and len(hexCodedegree) == 18:
                hd = phash_classfy.hamming_distance(hexCodedegreecompare, hexCodedegree)
                if hd <= 0:
                    my_uuid = key
                    isInDataJson = True
                    break

        if isInDataJson:
            classify_imageName = keras_classify.defineClassifyIntToStr(kerasfilejsondata[str(my_uuid)]['personclass'])
        else:
            classify_image = keras_classify.classifyurl(url)
            classify_imageName = str(keras_classify.defineClassifyIntToStr(classify_image))
            # filepath = keras_version_folder + "/" + str(classify_image) + "/" + my_uuid + "." + ext
            savepath = "./app" + keras_version_sub_folder + "/" + str(classify_image) + "/" + my_uuid + "." + ext
            kerasfilejsondata[my_uuid] = {'uuid': my_uuid, 'url': url, 'machineclass': int(classify_image),
                                          'personclass': int(classify_image), 'urlfilename': urlfilename,
                                          'filepath': savepath, 'phash': str(degree)}
            kerasfilejsondata = json.dumps(kerasfilejsondata, ensure_ascii=False)
            pathlib.Path("./app" + keras_version_sub_folder + "/data.json").write_text(kerasfilejsondata,
                                                                                       encoding="utf-8")
            image.save(savepath, quality=100)
            image.close()

        return str({"uuid": str(my_uuid), 'machineclassname': classify_imageName})

    def imageRotate(self, image):
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                break
        if image != None and image._getexif() != None:
            exif = dict(image._getexif().items())
            if exif[orientation] == 3:
                image = image.rotate(180, expand=True)
            elif exif[orientation] == 6:
                image = image.rotate(270, expand=True)
            elif exif[orientation] == 8:
                image = image.rotate(90, expand=True)
        return image

    def urlhandle(self, jsondata):
        url = jsondata['url']
        urlfilename = url.split("/")[-1]
        ext = url.split(".")[-1]
        return url, urlfilename, ext


class KerasVersionController(MethodView):
    def post(self):
        return {'version': os.getenv('keras_model_version')}

    def get(self):
        return {'version': os.getenv('keras_model_version')}
