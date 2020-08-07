# To generate a new secret key:
# >>> import random, string
# >>> "".join([random.choice(string.printable) for _ in range(24)])
import os
import logging
import coloredlogs
from datetime import timedelta

SERVER_PORT = 5000
SERVER_IP   = '0.0.0.0'
KEYFILE     = 'cert/server.key'
CERTFILE    = 'cert/server.crt'
SECURE_MODE = os.getenv('SECURE_MODE', 0)


class Config():
    MONGODB_HOST = os.getenv('MONGODBHOST', 'mongodb://localhost:27017/mydb')
    LOG_LEVEL = os.getenv('LOGLEVEL', 'DEBUG')
    
    SECRET_KEY = "+K[HC#<ufx0bR$x9S-0<^TINC"
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_DURATION = timedelta(days=1)
    CSRF_ENABLED = True

    STATIC_FOLDER = 'static'
    TEMPLATES_FOLDER = 'templates'

    MAIL_SERVER = "aspmx.l.google.com"
    MAIL_PORT = 25
    MAIL_USE_TLS = False
    MAIL_USE_SSL = False
    MAIL_USERNAME = False
    MAIL_PASSWORD = False

    MAIL_DEBUG = True
    MAIL_SUPPRESS_SEND = False

    MAIL_DEFAULT_SENDER = ('Flask Mailer', 'badAddress@gmail.com')
    MAIL_MAX_EMAILS = None
    MAIL_ASCII_ATTACHMENTS = False

def display_config():
    '''
    Sent configuration to logger
    '''
    LOGGER.info(" * Logger level: %s, " % (LOG_LEVEL))
    LOGGER.info(" * DB host:      %s, " % (MONGODB_HOST))

config = Config()

LOGGER = logging.getLogger()
LOG_FORMAT = '%(asctime)s - %(module)-15s:%(lineno)-4s - %(levelname)-8s - %(message)s'
coloredlogs.install(level=config.LOG_LEVEL, fmt=LOG_FORMAT, logger=LOGGER)

