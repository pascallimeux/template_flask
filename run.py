# -*- encoding: utf-8 -*-
#!/bin/env python

from app import app, socketio
from app.image import events as image_events
from app.auth import events as auth_events
from app.config import SERVER_PORT, SERVER_IP, KEYFILE, CERTFILE, SECURE_MODE, LOGGER
import logging

application = app

if __name__ == '__main__':
    #disable logger for flask-socketio
    logging.getLogger('socketio').setLevel(logging.ERROR)
    logging.getLogger('engineio').setLevel(logging.ERROR)
    if SECURE_MODE == 0:
        LOGGER.info("Start application ...")
        socketio.run(app, host=SERVER_IP, port=SERVER_PORT)
    else:
        LOGGER.info("Start application in secure mode ...")
        socketio.run(app, host=SERVER_IP, port=SERVER_PORT, keyfile=KEYFILE, certfile=CERTFILE)
