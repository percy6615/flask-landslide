import os

from .. import flask_app, keras_classify, keras_subFolder, globalInMem, enet_air_subFolder, enet_air_classify, \
    enet_ground_classify, enet_ground_subFolder

app = flask_app.getApp()
routerCache = flask_app.getCache()

from .landslide_controller import PublicPathController, ActionServiceController, \
    UploadImageToClassifyController, KerasImageClassifyHandle, \
    UploadImageUrlToClassifyController, VersionController, GetFirebaseTokenController, ClassifyErrorByPersonController, \
    EnetAirImageClassifyHandle, EnetGroundImageClassifyHandle

app.add_url_rule('/webhooks/public/<path:path>',
                 view_func=PublicPathController.as_view('PublicPathController'))

app.add_url_rule('/webhooks/action',
                 view_func=ActionServiceController.as_view('ActionServiceController'))

app.add_url_rule('/webhooks/postimage',
                 view_func=UploadImageToClassifyController.as_view('KerasUploadImageToClassifyController'),
                 defaults={'classifyHandle': KerasImageClassifyHandle(),
                           'modelPath': './app/classification/keras/keras_model/'})

app.add_url_rule('/webhooks/postimageurl',
                 view_func=UploadImageUrlToClassifyController.as_view('KerasUploadImageUrlToClassifyController'),
                 defaults={'classifyHandle': KerasImageClassifyHandle()})

app.add_url_rule('/webhooks/kerasversion',
                 view_func=VersionController.as_view('KerasVersionController'),
                 defaults={'sver': os.getenv("keras_model_version")})

app.add_url_rule('/webhooks/posterrorbyperson',
                 view_func=ClassifyErrorByPersonController.as_view('KerasClassifyErrorByPersonController'),
                 defaults={'classify_model': keras_classify, 'subFolder': keras_subFolder,
                           'jsondata': globalInMem.getKerasfilejsondata(), 'modelName': 'keras'})

app.add_url_rule('/webhooks/postfcmtoken',
                 view_func=GetFirebaseTokenController.as_view('KerasGetFirebaseTokenController'),
                 defaults={'sver': os.getenv("keras_model_version")})
######
app.add_url_rule('/webhooks/enetairpostimage',
                 view_func=UploadImageToClassifyController.as_view('EnetAirUploadImageToClassifyController'),
                 defaults={'classifyHandle': EnetAirImageClassifyHandle(),
                           'modelPath': './app/classification/enet/enet_model/'})

app.add_url_rule('/webhooks/enetgroundpostimage',
                 view_func=UploadImageToClassifyController.as_view(
                     'EnetGroundUploadImageToClassifyController'),
                 defaults={'classifyHandle': EnetGroundImageClassifyHandle(),
                           'modelPath': './app/classification/enet/enet_model/'})
######
app.add_url_rule('/webhooks/enetairpostimageurl',
                 view_func=UploadImageUrlToClassifyController.as_view(
                     'EnetAirUploadImageUrlToClassifyController'),
                 defaults={'classifyHandle': EnetAirImageClassifyHandle()})

app.add_url_rule('/webhooks/enetgroundpostimageurl',
                 view_func=UploadImageUrlToClassifyController.as_view(
                     'EnetGroundUploadImageUrlToClassifyController'),
                 defaults={'classifyHandle': EnetGroundImageClassifyHandle()})

#######
app.add_url_rule('/webhooks/enetairversion',
                 view_func=VersionController.as_view('EnetAirVersionController'),
                 defaults={'sver': os.getenv('enet_air_model_version')})

app.add_url_rule('/webhooks/enetgroundversion',
                 view_func=VersionController.as_view('EnetGroundVersionController'),
                 defaults={'sver': os.getenv('enet_ground_model_version')})

#######
app.add_url_rule('/webhooks/enetairposterrorbyperson',
                 view_func=ClassifyErrorByPersonController.as_view('EnetAirClassifyErrorByPersonController'),
                 defaults={'classify_model': enet_air_classify, 'subFolder': enet_air_subFolder,
                           'jsondata': globalInMem.getEnetAirfilejsondata(), 'modelName': 'enetair'})

app.add_url_rule('/webhooks/enetgroundposterrorbyperson',
                 view_func=ClassifyErrorByPersonController.as_view(
                     'EnetGroundClassifyErrorByPersonController'),
                 defaults={'classify_model': enet_ground_classify, 'subFolder': enet_ground_subFolder,
                           'jsondata': globalInMem.getEnetGroundfilejsondata(), 'modelName': 'enetground'})
#######
app.add_url_rule('/webhooks/enetairpostfcmtoken',
                 view_func=GetFirebaseTokenController.as_view('EnetAirGetFirebaseTokenController'),
                 defaults={'sver': os.getenv("enet_air_model_version")})

app.add_url_rule('/webhooks/enetgroundpostfcmtoken',
                 view_func=GetFirebaseTokenController.as_view('EnetGroundGetFirebaseTokenController'),
                 defaults={'sver': os.getenv("enet_ground_model_version")})
