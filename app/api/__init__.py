from .landslide_enet_controller import EnetAirUploadImageToClassifyController, \
    EnetGroundUploadImageToClassifyController, EnetAirUploadImageUrlToClassifyController, \
    EnetGroundUploadImageUrlToClassifyController, EnetAirVersionController, EnetGroundVersionController
from .. import flask_app

app = flask_app.getApp()
routerCache = flask_app.getCache()

from .landslide_controller import PublicPathController, KerasUploadImageToClassifyController, \
    KerasUploadImageUrlToClassifyController, KerasVersionController, KerasClassifyErrorByPersonController, \
    KerasGetFirebaseTokenController, ActionServiceController

app.add_url_rule('/webhooks/public/<path:path>',
                 view_func=PublicPathController.as_view('PublicPathController'))

app.add_url_rule('/webhooks/action',
                 view_func=ActionServiceController.as_view('ActionServiceController'))

app.add_url_rule('/webhooks/postimage',
                 view_func=KerasUploadImageToClassifyController.as_view('KerasUploadImageToClassifyController'))

app.add_url_rule('/webhooks/postimageurl',
                 view_func=KerasUploadImageUrlToClassifyController.as_view('KerasUploadImageUrlToClassifyController'))

app.add_url_rule('/webhooks/kerasversion',
                 view_func=KerasVersionController.as_view('KerasVersionController'))

app.add_url_rule('/webhooks/posterrorbyperson',
                 view_func=KerasClassifyErrorByPersonController.as_view('KerasClassifyErrorByPersonController'))

app.add_url_rule('/webhooks/postfcmtoken',
                 view_func=KerasGetFirebaseTokenController.as_view('KerasGetFirebaseTokenController'))
######
app.add_url_rule('/webhooks/enetairpostimage',
                 view_func=EnetAirUploadImageToClassifyController.as_view('EnetAirUploadImageToClassifyController'))

app.add_url_rule('/webhooks/enetgroundpostimage',
                 view_func=EnetGroundUploadImageToClassifyController.as_view(
                     'EnetGroundUploadImageToClassifyController'))
######
app.add_url_rule('/webhooks/enetairpostimageurl',
                 view_func=EnetAirUploadImageUrlToClassifyController.as_view(
                     'EnetAirUploadImageUrlToClassifyController'))

app.add_url_rule('/webhooks/enetgroundpostimageurl',
                 view_func=EnetGroundUploadImageUrlToClassifyController.as_view(
                     'EnetGroundUploadImageUrlToClassifyController'))

#######
app.add_url_rule('/webhooks/enetairversion',
                 view_func=EnetAirVersionController.as_view('EnetAirVersionController'))

app.add_url_rule('/webhooks/enetgroundversion',
                 view_func=EnetGroundVersionController.as_view('EnetGroundVersionController'))

#######
# app.add_url_rule('/webhooks/enetairposterrorbyperson',
#                  view_func=KerasClassifyErrorByPersonController.as_view('KerasClassifyErrorByPersonController'))
#
# app.add_url_rule('/webhooks/enetgroundposterrorbyperson',
#                  view_func=KerasClassifyErrorByPersonController.as_view('KerasClassifyErrorByPersonController'))
