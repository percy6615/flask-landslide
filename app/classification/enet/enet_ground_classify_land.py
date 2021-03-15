# import json
# import os
#
# import torch
# from PIL import Image
# from efficientnet_pytorch import EfficientNet
# from torchvision import transforms
#
# basedirs = os.path.abspath(os.path.dirname(__file__))
# weight_path = basedirs + '/enet_model/' + 'landslide_ground_v20210310.pth'
# device = torch.device("cpu")
#
# model = EfficientNet.from_name(model_name='efficientnet-b3')
# model._fc.out_features = 5
# model.to(device)
# model.load_state_dict(torch.load(weight_path, map_location=torch.device("cuda:0" if torch.cuda.is_available() else "cpu")))
# model = model.to(device)
#
# # Preprocess image
# tfms = transforms.Compose([transforms.Resize(224), transforms.ToTensor(),
#                            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]), ])
# img = tfms(Image.open('image_ground/img4.png')).unsqueeze(0)
# print(img.shape)  # torch.Size([1, 3, 224, 224])
#
#
# # Load ImageNet class names
# labels_map = json.load(open('labels_map.txt'))
# labels_map = [labels_map[str(i)] for i in range(5)]
#
# # Classify
# model.eval()
# with torch.no_grad():
#     outputs = model(img)
#     _, predicted = torch.max(outputs.data, 1)
#     print(predicted.item())
# ## Print predictions
# #     print('-----')
#     for idx in torch.topk(outputs, k=5).indices.squeeze(0).tolist():
#         prob = torch.softmax(outputs, dim=1)[0, idx].item()
#         # print('{label:<75} ({p:.2f}%)'.format(label=labels_map[idx], p=prob*100))
#         print('({p:.2f}%)'.format( p=prob * 100))
#         print(idx)


import json
import os
from abc import ABC
from io import BytesIO

import requests
import torch
from PIL import Image
from dotenv import load_dotenv
from efficientnet_pytorch import EfficientNet
from torchvision import transforms

from app.classification import ClassifyInterface

load_dotenv()


class EnetClassifyLandslide(ClassifyInterface, ABC):
    # class EnetClassifyLandslide():
    def __init__(self, inputModelName=""):
        super().__init__()
        # self.classify_model = self.create_model()

    def create_model(self, modelName=os.getenv('enet_ground_model_version')):
        obj = json.loads(modelName)
        basedirs = os.path.abspath(os.path.dirname(__file__))
        weight_path = basedirs + '/enet_model/' + obj['model_name']
        device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        model = EfficientNet.from_name(model_name=obj['network_name'])
        model._fc.out_features = 5
        model.to(device)
        model.load_state_dict(torch.load(weight_path, map_location=torch.device('cpu')))
        model = model.to(device)

        return model

    def classify(self, img):
        # # Classify
        self.classify_model.eval()
        with torch.no_grad():
            outputs = self.classify_model(img)
            _, predicted = torch.max(outputs.data, 1)
            resultpercentList = []
            for idx in torch.topk(outputs, k=1).indices.squeeze(0).tolist():
                prob = torch.softmax(outputs, dim=1)[0, idx].item()
                resultpercentList.append(prob)
        return resultpercentList, predicted.item()

    def classifyimagepath(self, img_path=os.path.join(os.path.dirname(__file__), "../../public/1.jpg")):
        tfms = transforms.Compose([transforms.Resize(224), transforms.ToTensor(),
                                   transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]), ])
        img = tfms(self.load_img(Image.open(img_path), target_size=(224, 224))).unsqueeze(0)
        return self.classify(img)

    def classifyurl(self, url='http://127.0.0.1/webhooks/public/1.png'):
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))
        return self.classifyimagebytes(img)

    def classifyimagebytes(self, imagebytes):
        tfms = transforms.Compose([transforms.Resize(224), transforms.ToTensor(),
                                   transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]), ])
        img = tfms(self.load_img(imagebytes, target_size=(224, 224))).unsqueeze(0)
        return self.classify(img)
