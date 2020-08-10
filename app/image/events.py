import sys
from datetime import datetime
from ..models import Image, MediaType
from flask_login import current_user, login_required
from .views import IMAGE_FORMAT, VIDEO_FORMAT

sys.path.insert(0,'../..')
from app import socketio


@socketio.on('image-save', namespace='/')
@login_required
def handle_image_save(data_image):
    filename = "{}.{}".format(datetime.now().strftime("%Y%m%d%H%M%S"), IMAGE_FORMAT[0])
    media = Image(user=current_user.id, name=filename, data=data_image, mtype=MediaType.IMAGE)
    media.create()
    #with open("/tmp/img/{}".format(filename),'wb') as f:
    #    f.write(data_image)

   
@socketio.on('video-save', namespace='/')
@login_required
def handle_video_save(data_video):
    filename = "{}.{}".format(datetime.now().strftime("%Y%m%d%H%M%S"), VIDEO_FORMAT)
    media = Image(user=current_user.id, name=filename, data=data_video, mtype=MediaType.VIDEO)
    media.create()
    #with open("/tmp/mp4/{}".format(filename),'wb') as f:
    #    f.write(data_video)
