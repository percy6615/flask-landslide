import json
import os
from torch import nn
import torch
from PIL import Image
from efficientnet_pytorch import EfficientNet
from torchvision import transforms

basedirs = os.path.abspath(os.path.dirname(__file__))
weight_path = basedirs + '/enet_model/' + 'landslide_ground_v20210310.pth'
device = torch.device("cpu")

# model = EfficientNet.from_name(model_name='efficientnet-b3')
model = EfficientNet.from_pretrained( model_name='efficientnet-b3', weights_path=weight_path, advprop=False,
                        in_channels=3, num_classes=5 )
feature = model._fc.in_features
# model._fc.out_features = 5
model._fc = nn.Linear(in_features=feature,out_features=5,bias=True)

model.to(device)
model.load_state_dict(torch.load(weight_path, map_location=torch.device("cuda:0" if torch.cuda.is_available() else "cpu")))
model = model.to(device)

# Preprocess image
tfms = transforms.Compose([transforms.Resize(224), transforms.ToTensor(),
                           transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]), ])
img = tfms(Image.open('../../public/2.jpg')).unsqueeze(0)
print(img.shape)  # torch.Size([1, 3, 224, 224])


# Load ImageNet class names
labels_map = json.load(open('labels_map.txt'))
labels_map = [labels_map[str(i)] for i in range(5)]

# Classify
model.eval()
with torch.no_grad():
    outputs = model(img)
    _, predicted = torch.max(outputs.data, 1)
    print(predicted.item())
## Print predictions
#     print('-----')
    arr = []
    for idx in torch.topk(outputs, k=5).indices.squeeze(0).tolist():
        prob = torch.softmax(outputs, dim=1)[0, idx].item()
        # print('{label:<75} ({p:.2f}%)'.format(label=labels_map[idx], p=prob*100))
        print('({p:.2f}%)'.format( p=prob * 100))
        print(idx)
        arr.append(prob * 100)
    # sum = 0
    # for a in arr:
    #     sum = sum+a
    # print(arr[0]/sum)