from abc import ABCMeta, abstractmethod


class ClassifyInterface(metaclass=ABCMeta):
    def __init__(self):
        self.classify_model = self.create_model()
    @abstractmethod
    def create_model(self):
        pass

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