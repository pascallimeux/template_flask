import io

import sys
from flask_login import current_user
from ..models import User
from ..config import LOGGER

sys.path.insert(0,'../..')
from app import socketio


@socketio.on('connect', namespace='/')
def handle_connected():
    if current_user.is_authenticated:
        try:
            user = User.objects.get(id=str(current_user.id))
            user.connect(True)
        except Exception as e:
            LOGGER.error (e)
    
@socketio.on('disconnect', namespace='/')
def handle_disconnect():
    if current_user.is_authenticated:
        try:
            user = User.objects.get(id=str(current_user.id))
            user.connect(False)
        except Exception as e:
            LOGGER.error (e)

