import json
import os
import pathlib
from datetime import datetime
from functools import lru_cache

import requests
from flask import request

from app import globalInMem, getConfig, keras_classify, keras_subFolder, firebaseNotefication
from app.tools.decorators_tool import is_json


class ClassifyTools:
    def __init__(self):
        pass

    # @lru_cache
    def UploadImageToClassify(self, handle, modelPath='./app/classification/enet/enet_model/'):
        type = request.values.get("type")
        if type is None:
            type = "file"
        if type is not None and type == "file":
            file = request.files['file']
            filedata = file.read()
            return handle.handle(filedata, None, file.filename)
        elif type is not None and type == "model":
            model = request.files['file']
            model.save(modelPath + model.filename)
            return {"status": 200}

    # @lru_cache
    def UploadImageUrlToClassify(self, handle):
        if request.is_json:
            jsondata = request.get_json()
            if 'url' in jsondata:
                url = jsondata['url']
                urlfilename = url.split("/")[-1]
                getContent = requests.get(url)
                return handle.handle(getContent.content, url, urlfilename)
            else:
                return {'status': 400}
        else:
            return {'status': 400}

    # @lru_cache
    def verion(self, sver):
        try:
            if request.is_json:
                jsondata = request.get_json()
                if 'id' in jsondata:
                    # sver = os.getenv('keras_model_version')
                    id = jsondata['id']
                    dtoken_record = globalInMem.getDevice_token_record()
                    ver_record = globalInMem.getVersion_record()
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
                        pathlib.Path(getConfig.getDispatch_device_token()).write_text(dtoken_dumps, encoding="utf-8")
                return {'version': sver}
            else:
                {'status': 400}
        except (ValueError, KeyError, TypeError):
            # Not valid information, bail out and return an error
            return {'error': 400}

    # @lru_cache
    def errorByPerson(self, classify_model=keras_classify, subFolder=keras_subFolder,
                      filejsondata=globalInMem.getKerasfilejsondata()):
        if request.is_json:
            jsondata = request.get_json()
            if 'uuid' in jsondata and 'personclassname' in jsondata:
                uuid = jsondata['uuid']
                personclassname = jsondata['personclassname']

                if uuid in filejsondata:
                    personclass = classify_model.defineClassifyStrToInt(personclassname)
                    if personclass != -1:
                        # if personclass != kerasfilejsondata[uuid]['personclass'] :
                        filejsondata[uuid]['personclass'] = personclass
                        filepath = filejsondata[uuid]['filepath']
                        filename = filepath.split('/')[-1]
                        savepath = subFolder + "/" + str(personclass) + "/" + filename
                        filejsondata[uuid]['filepath'] = savepath
                        os.rename(filepath, savepath)
                        filedata = json.dumps(filejsondata, ensure_ascii=False)
                        pathlib.Path(subFolder + "/data.json").write_text(filedata, encoding="utf-8")
                        error_count = 0
                        total_count = len(filejsondata)
                        errorcount_notify = int(os.getenv('errorcount_notify'))
                        for kuuid in filejsondata:
                            if filejsondata[kuuid]['machineclass'] != filejsondata[kuuid]['personclass']:
                                error_count = error_count + 1
                        notifytf = ((error_count >= errorcount_notify) or (
                                total_count > errorcount_notify and error_count / total_count > 0.1)) and error_count % errorcount_notify < 3
                        if ((error_count >= errorcount_notify) or (
                                total_count > errorcount_notify and error_count / total_count > 0.1)):
                            payload = {"message": "landslide must be retrain " + subFolder}
                            headers = {'Authorization': 'Bearer ' + os.getenv("line_notify_oneoone"), }
                            r = requests.post('https://notify-api.line.me/api/notify', payload, headers=headers)
                            # if check_ping():
                            #     ftpclient.upload_all(
                            #         base_local_dir=kerasVersion_subFolder,
                            #         base_remote_dir=os.getenv("keras_model_version"))
                        return {'status': 200}, filejsondata
                    else:
                        return {'status': 401}, None
                else:
                    return {'status': 402}, None
            else:
                return {'status': 403}, None
        else:
            return {'status': 404}, None

    # @lru_cache
    def getfirebasetoken(self,sver):
        if type(sver) == str:
            tf, obj = is_json(sver)
            if tf:
                sver = obj['model_name']

        if request.is_json:
            dtoken_record = globalInMem.getDevice_token_record()
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
                    dtoken_record[id] = {'id': id, 'modelversion': sver, 'fbtoken': fbtoken}
                if isupdate_file:
                    # TODO firebase post
                    dtoken_record = firebaseNotefication.handleByArg(token=fbtoken, id=id)
                    dtoken_dumps = json.dumps(dtoken_record, ensure_ascii=False)
                    pathlib.Path(getConfig.getDispatch_device_token()).write_text(dtoken_dumps, encoding="utf-8")
                return {'status': 200}
            else:
                return {'status': 400}
        else:
            return {'status': 400}
