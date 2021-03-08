# import json
# from PIL import Image
# import torch
# from torchvision import transforms
#
# from efficientnet_pytorch import EfficientNet
# model = EfficientNet.from_pretrained('efficientnet-b0')
#
# # Preprocess image
# tfms = transforms.Compose([transforms.Resize(224), transforms.ToTensor(),
#     transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),])
# img = tfms(Image.open('img.jpg')).unsqueeze(0)
# print(img.shape) # torch.Size([1, 3, 224, 224])
#
# # Load ImageNet class names
# labels_map = json.load(open('labels_map.txt'))
# labels_map = [labels_map[str(i)] for i in range(1000)]
#
# # Classify
# model.eval()
# with torch.no_grad():
#     outputs = model(img)
#
# # Print predictions
# print('-----')
# for idx in torch.topk(outputs, k=5).indices.squeeze(0).tolist():
#     prob = torch.softmax(outputs, dim=1)[0, idx].item()
#     print('{label:<75} ({p:.2f}%)'.format(label=labels_map[idx], p=prob*100))
import json
import os

import torch
from PIL import Image
from efficientnet_pytorch import EfficientNet
from torchvision import transforms

basedirs = os.path.abspath(os.path.dirname(__file__))
weight_path = basedirs + '/enet_model/' + 'net_059.pth'
device = torch.device("cpu")

model = EfficientNet.from_pretrained(model_name='efficientnet-b7')
model._fc.out_features = 5
model.to(device)
model.load_state_dict(torch.load(weight_path, map_location=torch.device('cpu')))
model = model.to(device)

# Preprocess image
tfms = transforms.Compose([transforms.Resize(224), transforms.ToTensor(),
                           transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]), ])
img = tfms(Image.open('img1.jpg')).unsqueeze(0)
print(img.shape)  # torch.Size([1, 3, 224, 224])


# Load ImageNet class names
labels_map = json.load(open('labels_map.txt'))
labels_map = [labels_map[str(i)] for i in range(5)]

# Classify
model.eval()
with torch.no_grad():
    outputs = model(img)
    _, predicted = torch.max(outputs.data, 1)
    print(predicted)
# Print predictions
print('-----')
for idx in torch.topk(outputs, k=5).indices.squeeze(0).tolist():
    prob = torch.softmax(outputs, dim=1)[0, idx].item()
    # print('{label:<75} ({p:.2f}%)'.format(label=labels_map[idx], p=prob*100))
    print('({p:.2f}%)'.format( p=prob * 100))
    print(idx)
