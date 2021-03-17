


import json
import os
from abc import ABC
from functools import lru_cache
from io import BytesIO

import requests
import torch
from PIL import Image
from dotenv import load_dotenv
from efficientnet_pytorch import EfficientNet
from tensorflow_estimator.python.estimator.api._v1.estimator import inputs

from torchvision import transforms

from app.classification import ClassifyInterface

load_dotenv()


class EnetClassifyLandslide(ClassifyInterface, ABC):
    # class EnetClassifyLandslide():
    def __init__(self, inputModelName=os.getenv('enet_air_model_version')):
        super().__init__(inputModelName)
        # self.classify_model = self.create_model()


    def create_model(self, modelName):
        obj = json.loads(modelName)
        basedirs = os.path.abspath(os.path.dirname(__file__))
        weight_path = basedirs + '/enet_model/' + obj['model_name']
        device = torch.device( "cpu")
        # device = torch.device( "cpu")
        # model = EfficientNet.from_name(model_name=obj['network_name'])
        model = EfficientNet.from_pretrained(model_name='efficientnet-b3', weights_path=weight_path, advprop=False,
                                             in_channels=3, num_classes=5)
        # model._fc.out_features = self.classify_num
        # model.to(device)
        feature = model._fc.in_features
        # model._fc.out_features = 5
        model._fc = torch.nn.Linear(in_features=feature, out_features=5, bias=True)
        model.load_state_dict(
            torch.load(weight_path, map_location=torch.device("cuda:0" if torch.cuda.is_available() else "cpu")))
        model = model.to(device)
        return model

    # @lru_cache()
    def classify(self, img):
        # # Classify
        self.classify_model.eval()
        # device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        # device = torch.device("cuda:0")
        with torch.no_grad():
            outputs = self.classify_model(img)
            # outputs.to(device)
            _, predicted = torch.max(outputs.data, 1)
            resultpercentList = []
            sum = 0
            for idx in torch.topk(outputs, k=5).indices.squeeze(0).tolist():
                prob = torch.softmax(outputs, dim=1)[0, idx].item()
                resultpercentList.append(prob)
            # for a in resultpercentList:
            #     sum = sum + a
        return resultpercentList, predicted.item()
        # return [resultpercentList[0]/sum], predicted.item()

    # @lru_cache()
    def classifyimagepath(self, img_path=os.path.join(os.path.dirname(__file__), "../../public/1.jpg")):
        tfms = transforms.Compose([transforms.Resize(224), transforms.ToTensor(),
                                   transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]), ])
        img = tfms(Image.open(img_path)).unsqueeze(0)
        return self.classify(img)

    # @lru_cache()
    def classifyurl(self, url='http://127.0.0.1/webhooks/public/1.png'):
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))
        return self.classifyimagebytes(img)

    # @lru_cache()
    def classifyimagebytes(self, imagebytes):
        tfms = transforms.Compose([transforms.Resize(224), transforms.ToTensor(),
                                   transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]), ])
        img = tfms(imagebytes).unsqueeze(0)
        return self.classify(img)
