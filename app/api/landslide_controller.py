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
from pyfcm import FCMNotification

from app import keras_classify, keras_version_sub_folder, kerasglobalInMem
from app.tools.image_tools import ImageHandle

errorcount_notify = 500


def send_static_content(path):
    return send_from_directory('public', path)


class PublicPathController(MethodView):
    def get(self, path):
        return send_static_content(path)


class UploadImageToClassifyController(MethodView):
    def post(self):
        file = request.files['filedata']
        filedata = file.read()
        # dotenv_file = dotenv.find_dotenv()
        # dotenv.load_dotenv(dotenv_file)
        # dotenv.set_key(dotenv_file, "test", 'os.environ[]')
        return KerasImageClassifyHandle().handle(filedata, None, file.filename)


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
            # if personclass != kerasfilejsondata[uuid]['personclass'] :
            kerasfilejsondata[uuid]['personclass'] = personclass
            filepath = kerasfilejsondata[uuid]['filepath']
            filename = filepath.split('/')[-1]
            savepath = "./app" + keras_version_sub_folder + "/" + str(personclass) + "/" + filename
            kerasfilejsondata[uuid]['filepath'] = savepath
            os.rename(filepath, savepath)

            kerasfile = json.dumps(kerasfilejsondata, ensure_ascii=False)
            pathlib.Path("./app" + keras_version_sub_folder + "/data.json").write_text(kerasfile, encoding="utf-8")
            error_count = 0
            total_count = len(kerasfilejsondata)
            for kuuid in kerasfilejsondata:
                if kerasfilejsondata[kuuid]['machineclass'] != kerasfilejsondata[kuuid]['personclass']:
                    error_count = error_count + 1
            if error_count >= errorcount_notify or (total_count > errorcount_notify and error_count/total_count > 0.1):
                payload = {"message": "landslid must be retrain"}
                headers = {'Authorization': 'Bearer ' + os.getenv("line_notify_oneoone"), }
                r = requests.post('https://notify-api.line.me/api/notify', payload, headers=headers)
            print(total_count)
            print(error_count)
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
                                          'filepath': savepath, 'phash': str(degree)}
            kerasfilejsondata = json.dumps(kerasfilejsondata, ensure_ascii=False)
            pathlib.Path("./app" + keras_version_sub_folder + "/data.json").write_text(kerasfilejsondata,
                                                                                       encoding="utf-8")
            image.save(savepath, quality=100)
            image.close()

        return str({"uuid": str(my_uuid), 'machineclassname': classify_imageName})


class GetFirebaseTokenController(MethodView):
    def post(self):
        jsondata = request.get_json()
        print(jsondata)
        return {'success': 200}


class FirebaseNotefication():
    def __init__(self):
        pass

    def sendMessage(self):
        device_id = 'cUWHDv6gRpCLlI3MjglGBz:APA91bGfMy6UVEzAD3q81Du4hMY4seRQBmH3C_7LSNz5saKrMaVN7a-PGTT3_cpWftwAHl4kZJWlqESBLL2zzYZrgtUOcGceZZDJMYvpsMoXk1ky-xJragrV-L3azzU-hhOPy815EuoO'
        server_key = os.getenv('firebase_landslide_serverkey')
        push_service = FCMNotification(api_key=server_key)
        registration_id = device_id
        message_title = "PB PerfEval"
        message_body = "test"

        datamsg = {
            "data": message_body
        }
        # click_action="com.precisebiometrics.perfevalmessge.TARGET_NOTIFICATION"
        result = push_service.notify_single_device(registration_id=registration_id, message_title=message_title,
                                                   message_body=message_body, data_message=datamsg)
        print(message_body)
