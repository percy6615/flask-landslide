# utf-8
# from app import singleton

import os
from io import BytesIO

import PIL
import numpy as np
import requests
import tensorflow as tf
from PIL import Image, ImageFile
from dotenv import load_dotenv
from keras.applications import xception
from keras.layers import Dense, GlobalAveragePooling2D, Dropout
from keras.models import Model
from keras.preprocessing import image

load_dotenv()


class KerasClassifyLandslide:
    def __init__(self):
        ImageFile.LOAD_TRUNCATED_IMAGES = True
        config = tf.compat.v1.ConfigProto()
        config.gpu_options.allow_growth = True
        sess = tf.compat.v1.Session(config=config)
        tf.compat.v1.keras.backend.set_session(sess)
        self.keras_model = self.create_model()
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

    def create_model(self, modelName=os.getenv('keras_model_version')):
        baseModel = xception.Xception(include_top=False, input_shape=(299, 299, 3))
        basedirs = os.path.abspath(os.path.dirname(__file__))
        nn_input = baseModel.input
        # New Layers which will be trained on our data set and will be stacked over the Xception Model
        x = baseModel.output
        x = GlobalAveragePooling2D()(x)
        x = Dense(2048, activation='relu')(x)
        x = Dropout(0.5)(x)
        x = Dense(1024, activation='relu')(x)
        x = Dropout(0.5)(x)
        x = Dense(512, activation='relu')(x)
        x = Dropout(0.5)(x)
        x = Dense(256, activation='relu')(x)
        x = Dropout(0.5)(x)
        output = Dense(5, activation='softmax')(x)
        model = Model(nn_input, output)
        model.compile(optimizer='adadelta', loss='categorical_crossentropy', metrics=['accuracy'])
        model.load_weights(basedirs + '/keras_model/' + modelName)
        return model

    def classify(self, img):
        img = image.img_to_array(img)
        img /= 255.0
        img = np.expand_dims(img, axis=0)
        result = self.keras_model.predict(img)
        resultarg = np.argmax(result)
        return result, resultarg

    def classifyimagepath(self, img_path=os.path.join(os.path.dirname(__file__), "../../public/2.jpg")):
        img = image.load_img(img_path, target_size=(299, 299))
        return self.classify(img)

    def defineClassifyIntToStr(self, classnum):
        if classnum == 0:
            classstr = '上邊坡'
        elif classnum == 1:
            classstr = '下邊坡'
        elif classnum == 2:
            classstr = '大面積'
        elif classnum == 3:
            classstr = '無法辨識'
        elif classnum == 4:
            classstr = '無災情'
        else:
            classstr = '無'
        return classstr.encode('utf8').decode('utf8').replace("'", '"')

    def defineClassifyStrToInt(self, classstr):
        if classstr == '上邊坡':
            classnum = 0
        elif classstr == '下邊坡':
            classnum = 1
        elif classstr == '大面積':
            classnum = 2
        elif classstr == '無法辨識':
            classnum = 3
        elif classstr == '無災情':
            classnum = 4
        else:
            classnum = -1
        return classnum

    def classifyurl(self, url='http://127.0.0.1:8000/webhooks/public/1609729025695.png'):
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))
        img = self.load_img(img)
        return self.classify(img)

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

    def classifyimagebytes(self, imagebytes):
        img = self.load_img(imagebytes)
        return self.classify(img)

# k = KerasClassifyLandslide()
# print(k.classifyurl())
# print(k.classify())
