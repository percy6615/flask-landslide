import json
import pathlib
import uuid
from abc import ABCMeta
from io import BytesIO

import numpy as np
from PIL import Image

from app.tools.image_tools import ImageHandle


class ImageClassifyHandle(metaclass=ABCMeta):
    def __init__(self):
        pass

    def handle(self, content, url, urlfilename, classify_model, subFolder, filejsondata):
        image_handle = ImageHandle()
        my_uuid = uuid.uuid4().hex
        image = Image.open(BytesIO(content))
        image = image_handle.imageRotate(image)
        if image.format is None:
            ext = urlfilename.split(".")[-1].lower()
        else:
            ext = image.format.lower()
        if ext == 'jpeg':
            ext = 'jpg'

        degree = image_handle.classify_pHash(image)
        # filejsondata = globalInMem.getKerasfilejsondata()
        isInDataJson = False

        for key in filejsondata:
            degreecompare = filejsondata[key]['phash']
            if len(degreecompare) == 18 and len(degree) == 18:
                hd = image_handle.hamming_distance(degreecompare, degree)
                if hd <= 0:
                    my_uuid = key
                    isInDataJson = True
                    break

        if isInDataJson:
            classify_imageName = classify_model.defineClassifyIntToStr(filejsondata[str(my_uuid)]['personclass'])
            maxvalue = filejsondata[str(my_uuid)]['percent']
        else:
            resultpercentList, resultclass = classify_model.classifyimagebytes(image)
            maxvalue = np.max(resultpercentList)
            classify_imageName = str(classify_model.defineClassifyIntToStr(resultclass))
            # filepath = keras_version_folder + "/" + str(classify_image) + "/" + my_uuid + "." + ext
            savepath = subFolder + "/" + str(resultclass) + "/" + my_uuid + "." + ext
            filejsondata[my_uuid] = {'uuid': my_uuid, 'url': url, 'machineclass': int(resultclass),
                                     'personclass': int(resultclass), 'urlfilename': urlfilename,
                                     'filepath': savepath, 'phash': str(degree), 'percent': float(maxvalue)}
            filejsondatastr = json.dumps(filejsondata, ensure_ascii=False)
            pathlib.Path(subFolder + "/data.json").write_text(filejsondatastr,
                                                              encoding="utf-8")
            image.save(savepath, quality=100)
            image.close()

        return str({"uuid": str(my_uuid), 'machineclassname': classify_imageName, 'percent': maxvalue}), filejsondata
