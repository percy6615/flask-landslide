# -*- coding: utf-8 -*-
import json
import os
import pathlib
# from urllib import response
import uuid
from datetime import datetime
from io import BytesIO

import numpy as np
import requests
from PIL import Image
from flask import request, send_from_directory
from flask.views import MethodView
from pyfcm import FCMNotification

from app import keras_classify, kerasVersion_subFolder, kerasGlobalInMem, getConfig
from app.tools.image_tools import ImageHandle

errorcount_notify = 500


# dotenv_file = dotenv.find_dotenv()
# dotenv.load_dotenv(dotenv_file)
# dotenv.set_key(dotenv_file, "test", 'os.environ[]')

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


class UploadImageUrlToClassifyController(MethodView):
    def post(self):
        if request.is_json:
            jsondata = request.get_json()
            if 'url' in jsondata:
                url = jsondata['url']
                urlfilename = url.split("/")[-1]
                getContent = requests.get(url)
                return KerasImageClassifyHandle().handle(getContent.content, url, urlfilename)
            else:
                return {'status': 400}
        else:
            return {'status': 400}


class ClassifyErrorByPersonController(MethodView):
    def post(self):
        if request.is_json:
            jsondata = request.get_json()
            if 'uuid' in jsondata and 'personclassname' in jsondata:
                uuid = jsondata['uuid']
                personclassname = jsondata['personclassname']
                kerasfilejsondata = kerasGlobalInMem.getkerasfilejsondata()
                if uuid in kerasfilejsondata:
                    personclass = keras_classify.defineClassifyStrToInt(personclassname)
                    # if personclass != kerasfilejsondata[uuid]['personclass'] :
                    kerasfilejsondata[uuid]['personclass'] = personclass
                    filepath = kerasfilejsondata[uuid]['filepath']
                    filename = filepath.split('/')[-1]
                    savepath = kerasVersion_subFolder + "/" + str(personclass) + "/" + filename
                    kerasfilejsondata[uuid]['filepath'] = savepath
                    os.rename(filepath, savepath)
                    kerasfile = json.dumps(kerasfilejsondata, ensure_ascii=False)
                    pathlib.Path(kerasVersion_subFolder + "/data.json").write_text(kerasfile, encoding="utf-8")
                    error_count = 0
                    total_count = len(kerasfilejsondata)
                    for kuuid in kerasfilejsondata:
                        if kerasfilejsondata[kuuid]['machineclass'] != kerasfilejsondata[kuuid]['personclass']:
                            error_count = error_count + 1
                    if (error_count >= errorcount_notify) or (
                            total_count > errorcount_notify and error_count / total_count > 0.1):
                        payload = {"message": "landslid must be retrain"}
                        headers = {'Authorization': 'Bearer ' + os.getenv("line_notify_oneoone"), }
                        r = requests.post('https://notify-api.line.me/api/notify', payload, headers=headers)
                return {'status': 200}
            else:
                return {'status': 400}
        else:
            return {'status': 400}


class KerasVersionController(MethodView):
    def post(self):
        try:
            if request.is_json:
                jsondata = request.get_json()
                if 'id' in jsondata:
                    now_version = os.getenv('keras_model_version')
                    id = jsondata['id']
                    firebase_token_record = kerasGlobalInMem.getDevice_token_record()
                    keras_version_record = kerasGlobalInMem.getkeras_version_record()
                    is_updatefile = True
                    if id in firebase_token_record:
                        user_version = firebase_token_record[id]['modelversion']
                        if user_version is not None:
                            if user_version != now_version:
                                if user_version in keras_version_record:
                                    user_modeltime = keras_version_record[user_version]["time"]
                                    sys_modeltime = keras_version_record[now_version]["time"]
                                    user_modeltime_obj = datetime.strptime(user_modeltime, '%m/%d/%Y, %H:%M:%S')
                                    sys_modeltime_obj = datetime.strptime(sys_modeltime, '%m/%d/%Y, %H:%M:%S')
                                    if user_modeltime_obj <= sys_modeltime_obj:
                                        firebase_token_record[id]['modelversion'] = now_version
                                        pass
                                    else:
                                        is_updatefile = False
                            else:
                                is_updatefile = False
                        else:
                            firebase_token_record[id]['modelversion'] = now_version
                    else:
                        firebase_token_record[id] = {'id': id, 'modelversion': now_version,
                                                     'fbtoken': None}

                    if is_updatefile:
                        firebase_token_dumps = json.dumps(firebase_token_record, ensure_ascii=False)
                        pathlib.Path(getConfig.getdispatch_device_token()).write_text(firebase_token_dumps,
                                                                                      encoding="utf-8")
                return {'version': os.getenv('keras_model_version')}
            else:
                {'status': 400}
        except (ValueError, KeyError, TypeError):
            # Not valid information, bail out and return an error
            return {'error': 400}

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
        kerasfilejsondata = kerasGlobalInMem.getkerasfilejsondata()
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
            maxvalue = kerasfilejsondata[str(my_uuid)]['percent']
        else:
            result, resultarg = keras_classify.classifyimagebytes(image)
            maxvalue = np.max(result)
            classify_imageName = str(keras_classify.defineClassifyIntToStr(resultarg))
            # filepath = keras_version_folder + "/" + str(classify_image) + "/" + my_uuid + "." + ext
            savepath = kerasVersion_subFolder + "/" + str(resultarg) + "/" + my_uuid + "." + ext
            kerasfilejsondata[my_uuid] = {'uuid': my_uuid, 'url': url, 'machineclass': int(resultarg),
                                          'personclass': int(resultarg), 'urlfilename': urlfilename,
                                          'filepath': savepath, 'phash': str(degree), 'percent': float(maxvalue)}
            kerasfilejsondata = json.dumps(kerasfilejsondata, ensure_ascii=False)
            pathlib.Path(kerasVersion_subFolder + "/data.json").write_text(kerasfilejsondata,
                                                                           encoding="utf-8")
            image.save(savepath, quality=100)
            image.close()

        return str({"uuid": str(my_uuid), 'machineclassname': classify_imageName, 'percent': maxvalue})


class GetFirebaseTokenController(MethodView):
    def post(self):
        if request.is_json:
            firebase_token_record = kerasGlobalInMem.getDevice_token_record()
            jsondata = request.get_json()
            if 'id' in jsondata and 'fbtoken' in jsondata:
                id = jsondata['id']
                fbtoken = jsondata['fbtoken']
                firebase_token_record[id]['fbtoken'] = fbtoken
                firebase_token_dumps = json.dumps(firebase_token_record, ensure_ascii=False)
                pathlib.Path(getConfig.getdispatch_device_token()).write_text(firebase_token_dumps,
                                                                              encoding="utf-8")
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
