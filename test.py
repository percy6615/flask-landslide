import json
import sys

import requests
from pyfcm import FCMNotification


class FirebaseNotefication():
    def __init__(self):
        pass
    def sendMessage(self):
        device_id = 'do6KLMGRSC-4NKCfQ6TZmK:APA91bHXKdnrQGt_yhDOiKqSJTswjJ5Ix4-S1lGz0Ta7MtKYc83BmnqcsLMu_0MH0hmvEjDAJOD_SbpKWAMqpb4xe_rCe4-2tjFfTzQKa4_DLcCo_W1BAyPqwL6uCKXGM3H6BDja6A6z'
        # server_key = "AAAAF_CeRXo:APA91bEmQ5ZNzRR3SD2gtFjsRBzAtDWUzjgMz-xzKhA2I4g8opzD4yp-FzGagxuIbvJNmzszwhLGtP9T9o_uonUldG9dieosivpjMyTGKJYXsLueAKQf8vdCZkM5PzU_Zqjhh4J9yS3l" landslide
        server_key = 'AAAAJVFc-vE:APA91bHg4TQ6PfZpfgmJpTTe3jtBk3okrYqG2_7A5MsMYEyi8zVh7dq5WK0EBDTrqjE-ILUnSpdfeKvWFampG37L_ETqIUv1yIgsElvkBvgX2n211jV0F_wa0211Qj2onR3aSMql12gF'
        push_service = FCMNotification(api_key=server_key)
        registration_id = device_id
        message_title = "PB PerfEval"
        message_body = "test"

        # datamsg = {
        #     "data": {"my_custom_key": "my_custom_value",
        #                 "my_custom_key2": True}
        # }

        datamsg = {
            "data": message_body
        }
        # click_action="com.precisebiometrics.perfevalmessge.TARGET_NOTIFICATION"
        result = push_service.notify_single_device(registration_id=registration_id, message_title=message_title,
                                                   message_body=message_body, data_message=datamsg)
        # payload = {
        #     'action': 'testing',
        #     'test number': 1,
        #     'question': "what do you do with a klondike bar?",
        # }
        # result = push_service.single_device_data_message(registration_id=registration_id, data_message=datamsg)
        print(result['success'])
FirebaseNotefication().sendMessage()
# payload = { "message": "重新訓練搂" }
# headers = {'Authorization': 'Bearer ' + 'YozK8iigJixZArjVZ41ZR4ANlvfZaeOsG8zcbcaYSpz',}
# r = requests.post('https://notify-api.line.me/api/notify', payload, headers=headers)
# print(r.content)

# import numpy as np
# list_data =[13, 14, 15, 16]
# numpyArray = np.array(list_data)
# print(np.max(numpyArray))

# from datetime import datetime
# time = "01/14/2021, 13:21:50"
# time1 = "01/15/2021, 13:21:50"
# date_time_obj = datetime.strptime(time, '%m/%d/%Y, %H:%M:%S')
# date_time_obj1 = datetime.strptime(time1, '%m/%d/%Y, %H:%M:%S')
# print(date_time_obj>date_time_obj1)

class Animal:
    def __init__(self, animal_list):
        self.animal_name = animal_list

    def __getitem__(self):
        return 1

a = Animal([1,2,3])
print(a)

matrix = dict()
