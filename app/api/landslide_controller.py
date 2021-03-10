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

from app import keras_classify, kerasVersion_subFolder, kerasGlobalInMem, getConfig, firebaseNotefication, ftpclient
from app.tools.image_tools import ImageHandle

errorcount_notify = 5


# dotenv_file = dotenv.find_dotenv()
# dotenv.load_dotenv(dotenv_file)
# dotenv.set_key(dotenv_file, "test", 'os.environ[]')

def send_static_content(path):
    return send_from_directory('public', path)


def check_ping(hostname="192.168.4.200"):
    response = os.system("ping  -n 1 " + hostname)
    # and then check the response...
    if response == 0:
        pingstatus = True
    else:
        pingstatus = False

    return pingstatus


class PublicPathController(MethodView):
    def get(self, path):
        return send_static_content(path)


class KerasUploadImageToClassifyController(MethodView):
    def post(self):
        print("file" == request.values.get("type"))
        type = request.values.get("type")
        if type is not None and type == "file":
            file = request.files['filedata']
            filedata = file.read()
            return KerasImageClassifyHandle().handle(filedata, None, file.filename)
        elif type is not None and type == "model":
            model = request.files['filedata']
            model.save('./app/classification/keras/keras_model/' + model.filename)
            return {"status": 200}


class ActionServiceController(MethodView):
    def post(self):
        if request.is_json:
            jsondata = request.get_json()
            action = jsondata['action']
            if action == "shutdown":
                func = request.environ.get('werkzeug.server.shutdown')
                func()
            elif action == "ftpupload":
                ftpclient.upload_all(
                    base_local_dir=kerasVersion_subFolder,
                    base_remote_dir=os.getenv("keras_model_version"))
        return {"status": 200}


class KerasUploadImageUrlToClassifyController(MethodView):
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


class KerasClassifyErrorByPersonController(MethodView):
    def post(self):
        if request.is_json:
            jsondata = request.get_json()
            if 'uuid' in jsondata and 'personclassname' in jsondata:
                uuid = jsondata['uuid']
                personclassname = jsondata['personclassname']
                kerasfilejsondata = kerasGlobalInMem.getkerasfilejsondata()
                if uuid in kerasfilejsondata:
                    personclass = keras_classify.defineClassifyStrToInt(personclassname)
                    if personclass != -1:
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
                        notifytf = ((error_count >= errorcount_notify) or (
                                total_count > errorcount_notify and error_count / total_count > 0.1)) and error_count % errorcount_notify < 3
                        if ((error_count >= errorcount_notify) or (
                                total_count > errorcount_notify and error_count / total_count > 0.1)) :
                            payload = {"message": "landslide must be retrain"}
                            headers = {'Authorization': 'Bearer ' + os.getenv("line_notify_oneoone"), }
                            r = requests.post('https://notify-api.line.me/api/notify', payload, headers=headers)
                            # if check_ping():
                            #     ftpclient.upload_all(
                            #         base_local_dir=kerasVersion_subFolder,
                            #         base_remote_dir=os.getenv("keras_model_version"))
                        return {'status': 200}
                    else:
                        return {'status': 401}
                else:
                    return {'status': 402}
            else:
                return {'status': 403}
        else:
            return {'status': 404}


class KerasVersionController(MethodView):
    def post(self):
        try:
            if request.is_json:
                jsondata = request.get_json()
                if 'id' in jsondata:
                    sver = os.getenv('keras_model_version')
                    id = jsondata['id']
                    dtoken_record = kerasGlobalInMem.getDevice_token_record()
                    ver_record = kerasGlobalInMem.getkeras_version_record()
                    is_updatefile = True
                    if id in dtoken_record:
                        uver = dtoken_record[id]['modelversion']
                        if uver is not None:
                            if uver != sver:
                                if uver in ver_record and sver in ver_record:
                                    utime = datetime.strptime(ver_record[uver]["time"], '%m/%d/%Y, %H:%M:%S')
                                    stime = datetime.strptime(ver_record[sver]["time"], '%m/%d/%Y, %H:%M:%S')
                                    if utime < stime:
                                        dtoken_record[id]['modelversion'] = sver
                                    else:
                                        is_updatefile = False
                            else:
                                is_updatefile = False
                        else:
                            dtoken_record[id]['modelversion'] = sver
                    else:
                        dtoken_record[id] = {'id': id, 'modelversion': sver, 'fbtoken': None}

                    if is_updatefile:
                        dtoken_dumps = json.dumps(dtoken_record, ensure_ascii=False)
                        pathlib.Path(getConfig.getdispatch_device_token()).write_text(dtoken_dumps, encoding="utf-8")
                return {'version': os.getenv('keras_model_version')}
            else:
                {'status': 400}
        except (ValueError, KeyError, TypeError):
            # Not valid information, bail out and return an error
            return {'error': 400}

    def get(self):
        # path = "./app/classification/keras/image/landslide_v20210112.h5/"
        # for root, dirs, files in os.walk(path):
        #     print("  路徑：", root)
        #     print("  目錄：", dirs)
        #     print("  檔案：", files)
        return {'version': os.getenv('keras_model_version')}


class KerasImageClassifyHandle:
    def __init__(self):
        pass

    def handle(self, content, url, urlfilename):
        image_handle = ImageHandle()
        my_uuid = uuid.uuid4().hex
        image = Image.open(BytesIO(content))
        image = image_handle.imageRotate(image)
        if image.format is None:
            ext = urlfilename.split(".")[-1].lower()
        else:
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
            resultpercentList, resultclass = keras_classify.classifyimagebytes(image)
            maxvalue = np.max(resultpercentList)
            classify_imageName = str(keras_classify.defineClassifyIntToStr(resultclass))
            # filepath = keras_version_folder + "/" + str(classify_image) + "/" + my_uuid + "." + ext
            savepath = kerasVersion_subFolder + "/" + str(resultclass) + "/" + my_uuid + "." + ext
            kerasfilejsondata[my_uuid] = {'uuid': my_uuid, 'url': url, 'machineclass': int(resultclass),
                                          'personclass': int(resultclass), 'urlfilename': urlfilename,
                                          'filepath': savepath, 'phash': str(degree), 'percent': float(maxvalue)}
            kerasfilejsondata = json.dumps(kerasfilejsondata, ensure_ascii=False)
            pathlib.Path(kerasVersion_subFolder + "/data.json").write_text(kerasfilejsondata,
                                                                           encoding="utf-8")
            image.save(savepath, quality=100)
            image.close()

        return str({"uuid": str(my_uuid), 'machineclassname': classify_imageName, 'percent': maxvalue})


class KerasGetFirebaseTokenController(MethodView):
    def post(self):
        if request.is_json:
            dtoken_record = kerasGlobalInMem.getDevice_token_record()
            jsondata = request.get_json()
            if 'id' in jsondata and 'fbtoken' in jsondata:
                id = jsondata['id']
                fbtoken = jsondata['fbtoken']
                isupdate_file = True
                if id in dtoken_record:
                    if dtoken_record[id]['fbtoken'] != fbtoken:
                        dtoken_record[id]['fbtoken'] = fbtoken
                    else:
                        isupdate_file = False
                else:
                    dtoken_record[id] = {'id': id, 'modelversion': os.getenv('keras_model_version'), 'fbtoken': fbtoken}
                if isupdate_file:
                    # TODO firebase post
                    dtoken_record = firebaseNotefication.handle1(token=fbtoken, id=id)
                    dtoken_dumps = json.dumps(dtoken_record, ensure_ascii=False)
                    pathlib.Path(getConfig.getdispatch_device_token()).write_text(dtoken_dumps, encoding="utf-8")
                return {'status': 200}
            else:
                return {'status': 400}
        else:
            return {'status': 400}


class EnetClassifyController(MethodView):
    def post(self):
        return {}
    def get(self):
        return {}