import datetime
import json
import os
import pathlib

from pyfcm import FCMNotification

from app import globalInMem, getConfig


class FirebaseNotefication:
    def __init__(self):
        pass

    def sendNotificationMessage(self, device_id="", message_title="", message_body="",
                                api_key=os.getenv('firebase_landslide_serverkey')):
        push_service = FCMNotification(api_key=api_key)
        registration_id = device_id
        datamsg = {
            "data": message_body
        }
        result = push_service.notify_single_device(registration_id=registration_id, message_title=message_title,
                                                   message_body=message_body, data_message=datamsg)
        print(result)

    def sendDataMessage(self, device_id="", message_body=None, api_key=os.getenv('firebase_landslide_serverkey')):
        push_service = FCMNotification(api_key=api_key)
        registration_id = device_id
        datamsg = {
            "data": message_body
        }
        if registration_id == "" or registration_id is None:
            return 0
        else:
            result = push_service.single_device_data_message(registration_id=registration_id, data_message=datamsg)
            return result['success']

    def handleByArg(self, token="", id=""):
        dtoken_record = globalInMem.getDevice_token_record()
        if id in dtoken_record:
            if dtoken_record[id]['modelversion'] != os.getenv('keras_model_version'):
                result = self.sendDataMessage(device_id=token, message_body={"title": "版本更新", "body": "版本更新"})
                if result == 1:
                    dtoken_record[id]['modelversion'] = os.getenv('keras_model_version')
        return dtoken_record

    def handle(self):
        dtoken_record = globalInMem.getDevice_token_record()
        for k in dtoken_record:
            if dtoken_record[k]['modelversion'] != os.getenv('keras_model_version'):
                token = dtoken_record[k]['fbtoken']
                result = self.sendDataMessage(device_id=token, message_body={"title": "版本更新", "body": "版本更新"})
                if result == 1:
                    dtoken_record[k]['modelversion'] = os.getenv('keras_model_version')
        return dtoken_record

    def postNewModelVersion(self):
        mver_record = globalInMem.getVersion_record()
        sver = os.getenv('keras_model_version')
        if sver not in mver_record:
            mver_record[sver] = {'modelversion': sver, 'time': datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")}
            mver_dumps = json.dumps(mver_record, ensure_ascii=False)
            pathlib.Path(getConfig.getVersion_evn_fileName()).write_text(mver_dumps, encoding="utf-8")
        # TODO postfirebase
        self.handle()
