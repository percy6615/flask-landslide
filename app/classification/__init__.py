from abc import ABCMeta, abstractmethod

import PIL
from PIL import Image


class ClassifyInterface(metaclass=ABCMeta):
    def __init__(self, modelName):
        self.classify_model = self.create_model(modelName)
        if PIL.Image is not None:
            self._PIL_INTERPOLATION_METHODS = {
                'nearest': PIL.Image.NEAREST,
                'bilinear': PIL.Image.BILINEAR,
                'bicubic': PIL.Image.BICUBIC,
            }
            # These methods were only introduced in version 3.4.0 (2016).
            if hasattr(Image, 'HAMMING'):
                self._PIL_INTERPOLATION_METHODS['hamming'] = Image.HAMMING
            if hasattr(Image, 'BOX'):
                self._PIL_INTERPOLATION_METHODS['box'] = Image.BOX
            # This method is new in version 1.1.3 (2013).
            if hasattr(Image, 'LANCZOS'):
                self._PIL_INTERPOLATION_METHODS['lanczos'] = Image.LANCZOS

    @abstractmethod
    def create_model(self, modelName):
        pass

    def defineClassifyIntToStr(self, classnum):
        if classnum == 0:
            classstr = '上邊坡土石坍方'
        elif classnum == 1:
            classstr = '下邊坡土石坍方'
        elif classnum == 2:
            classstr = '大面積土石坍方'
        elif classnum == 3:
            classstr = '無法辨識影像'
        elif classnum == 4:
            classstr = '輕微或無災情'
        else:
            classstr = '無'
        return classstr.encode('utf8').decode('utf8').replace("'", '"')

    def defineClassifyStrToInt(self, classstr):
        if classstr == '上邊坡土石坍方':
            classnum = 0
        elif classstr == '下邊坡土石坍方':
            classnum = 1
        elif classstr == '大面積土石坍方':
            classnum = 2
        elif classstr == '無法辨識影像':
            classnum = 3
        elif classstr == '輕微或無災情':
            classnum = 4
        else:
            classnum = -1
        return classnum

    @abstractmethod
    def classify(self):
        pass

    def load_img(self, img, color_mode='rgb', target_size=(299, 299), interpolation='nearest'):
        if color_mode == 'grayscale':
            if img.mode != 'L':
                img = img.convert('L')
        elif color_mode == 'rgba':
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
        elif color_mode == 'rgb':
            if img.mode != 'RGB':
                img = img.convert('RGB')
        else:
            raise ValueError('color_mode must be "grayscale", "rgb", or "rgba"')
        if target_size is not None:
            width_height_tuple = (target_size[1], target_size[0])
            if img.size != width_height_tuple:
                if interpolation not in self._PIL_INTERPOLATION_METHODS:
                    raise ValueError(
                        'Invalid interpolation method {} specified. Supported '
                        'methods are {}'.format(
                            interpolation,
                            ", ".join(self._PIL_INTERPOLATION_METHODS.keys())))
                resample = self._PIL_INTERPOLATION_METHODS[interpolation]
                img = img.resize(width_height_tuple, resample)
        return img
