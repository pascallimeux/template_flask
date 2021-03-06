
import os
import logging
import coloredlogs
from datetime import timedelta
from dotenv import load_dotenv
load_dotenv()

path = os.path.dirname(__file__)
project_path = os.path.abspath(os.path.join(path, os.pardir))

SERVER_PORT = int(os.getenv('SERVER_PORT', 5000))
SERVER_IP   = os.getenv('SERVER_IP', '0.0.0.0')

SECUREMODE = os.getenv('SECURE_MODE', 1)
SECURE_MODE = True
PROTOCOL = "https"
if SECUREMODE == '0':
    SECURE_MODE = False
    PROTOCOL = "http"

KEYFILE     = "{}/{}".format(project_path, os.getenv('KEYFILE','server.key'))
CERTFILE    = "{}/{}".format(project_path, os.getenv('CERTFILE','server.crt'))
mongohost  = os.getenv('MONGODBHOST', 'mongodb://localhost:27017/mydb')
loglevel   = os.getenv('LOGLEVEL', 'DEBUG')
secretkey  = "GWRiUGSgio06MEIKVy50xiZ8"

class Config():
    MONGODB_HOST = mongohost
    LOG_LEVEL = loglevel
    SECRET_KEY = secretkey
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
    LOGGER.info(" * LOGGER level: %s" % (loglevel))
    LOGGER.info(" * DB host:      %s" % (mongohost))
    LOGGER.info(" * SERVER url:   %s://%s:%s" % (PROTOCOL, SERVER_IP, SERVER_PORT))
    if SECURE_MODE:
        LOGGER.info(" * KEYFILE:      %s" % (KEYFILE))
        LOGGER.info(" * CERTFILE:     %s" % (CERTFILE))

config = Config()

LOGGER = logging.getLogger()
LOG_FORMAT = '%(asctime)s - %(module)-15s:%(lineno)-4s - %(levelname)-8s - %(message)s'
coloredlogs.install(level=config.LOG_LEVEL, fmt=LOG_FORMAT, logger=LOGGER)

