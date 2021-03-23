import cv2
import numpy as np
from PIL import ExifTags


class ImageHandle():
    def __init__(self):
        self.ddd = ''

    def getHash(self, image):
        avreage = np.mean(image)
        hash = []
        for i in range(image.shape[0]):
            for j in range(image.shape[1]):
                if image[i, j] > avreage:
                    hash.append(1)
                else:
                    hash.append(0)
        return hash

    def magic(self, numList):  # [1,2,3]
        s = map(str, numList)  # ['1','2','3']
        s = ''.join(s)  # '123'
        return s

    def classify_pHash(self, img1):
        gray1 = cv2.cvtColor(np.asarray(img1), cv2.COLOR_BGR2GRAY)
        gray1 = cv2.resize(gray1, (32, 32))
        # 将灰度图转为浮点型，再进行dct变换
        dct1 = cv2.dct(np.float32(gray1))
        # 取左上角的8*8，这些代表图片的最低频率
        # 这个操作等价于c++中利用opencv实现的掩码操作
        # 在python中进行掩码操作，可以直接这样取出图像矩阵的某一部分
        dct1_roi = dct1[0:8, 0:8]
        hash1 = self.getHash(dct1_roi)
        # print(hash1)
        # decimal_value = 0
        hash1 = self.magic(hash1)
        hash1 = hex(int(hash1, 2))
        return hash1.rstrip()

    def hamming_distance(self, hash1, hash2):
        num = 0
        for index in range(len(hash1)):
            if hash1[index] != hash2[index]:
                num += 1
        return num

    def imageRotate(self, image):
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                break
        if image is not None and image._getexif() is not None:
            exif = dict(image._getexif().items())
            if orientation not in exif:
                pass
            elif exif[orientation] == 3:
                image = image.rotate(180, expand=True)
            elif exif[orientation] == 6:
                image = image.rotate(270, expand=True)
            elif exif[orientation] == 8:
                image = image.rotate(90, expand=True)
        return image
