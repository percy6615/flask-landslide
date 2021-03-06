# utf-8
# from app import singleton

import os
from abc import ABC
from functools import lru_cache
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

# from app.classification import ClassifyInterface
from app.classification import ClassifyInterface

load_dotenv()

@lru_cache()
class KerasClassifyLandslide(ClassifyInterface, ABC):
    def __init__(self,modelName = os.getenv('keras_model_version')):
        super().__init__(modelName)
        ImageFile.LOAD_TRUNCATED_IMAGES = True
        config = tf.compat.v1.ConfigProto()
        config.gpu_options.allow_growth = True
        sess = tf.compat.v1.Session(config=config)
        tf.compat.v1.keras.backend.set_session(sess)
        # self.keras_model = self.create_model()


    def create_model(self, modelName):
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
        result = self.classify_model.predict(img)
        resultarg = np.argmax(result)
        return result, resultarg

    def classifyimagepath(self, img_path=os.path.join(os.path.dirname(__file__), "../../public/2.jpg")):
        img = image.load_img(img_path, target_size=(299, 299))
        return self.classify(img)

    def classifyurl(self, url='http://127.0.0.1/webhooks/public/1.jpg'):
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))
        return self.classifyimagebytes(img)


    def classifyimagebytes(self, imagebytes):
        img = self.load_img(imagebytes)
        return self.classify(img)

# k = KerasClassifyLandslide()
# print(k.classifyurl())
# print(k.classify())
