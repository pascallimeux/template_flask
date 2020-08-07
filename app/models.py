import io
import json
from flask_mongoengine import MongoEngine
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from enum import IntEnum
import qrcode
from base64 import b64encode

from .config import Config

db = MongoEngine()

class UserRole(IntEnum):
    GUEST = 1
    USER = 2
    ADMIN = 3

class MediaType(IntEnum):
    IMAGE = 1
    VIDEO = 2

class User(db.Document):
    username = db.StringField(requierd=True, unique=True)
    email = db.EmailField(requierd=True, unique=True)
    password = db.StringField(requierd=True)
    firstname =  db.StringField()
    lastname = db.StringField()
    role = db.IntField(default=UserRole.GUEST)
    active = db.BooleanField(default=True)
    connected = db.BooleanField(default=False)
    created_at = db.DateTimeField(requierd=True)
    last_login = db.DateTimeField()


    def is_admin(self):
        return self.role == UserRole.ADMIN
        
    def refresh_last_login(self):
        self.last_login = datetime.now()
        self.save()

    def set_password(self, password):
        """Create hashed password."""
        self.password = generate_password_hash(password, method='sha256')

    def check_password(self, password):
        """Check hashed password."""
        return check_password_hash(self.password, password)

    def is_active(self):
        return self.active

    def get_id(self):
        """Return the id to satisfy Flask-Login's requirements."""
        return str(self.id)

    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return self.authenticated

    def is_anonymous(self):
        """False, as anonymous users aren't supported."""
        return False

    def __repr__(self):
        return f"User({self.id}, {self.username}, {self.email})"

    def create(self):
        self.set_password(self.password)
        self.created_at = datetime.now()
        return self.save()
    
    def connect(self, state):
        self.connected = state
        return self.save()

    def get_qrcode(self):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )

        qr.add_data(self.toJson())
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        buffer = io.BytesIO()
        img.save(buffer, format='png')
        byteArr = buffer.getvalue()
        b64 = b64encode(byteArr).decode("utf-8")
        return b64

    def toJson(self):
        json_value = {
                'ID': str(self.id),
                'Username': self.username, 
                'Firstname': self.firstname,
                'Lastname': self.lastname,
                'Email': self.email,
                'Role': UserRole(self.role).name.capitalize(),
                'Active': self.active,
                'Created at': self.created_at.strftime('%y/%m/%d %H:%M'),
                'Last login at': self.last_login.strftime('%y/%m/%d %H:%M')}
        value = json.dumps(json_value, indent=2)
        return value


class Image(db.Document):
    name = db.StringField(requierd=True, unique=True)
    data = db.BinaryField(requierd=True)
    mtype = db.IntField(requierd=True)
    size = db.IntField(requierd=True)
    recorded_at = db.DateTimeField(requierd=True)
    user = db.ReferenceField(document_type=User, required=True)
    
    def create(self):
        self.size = len(self.data)
        self.recorded_at = datetime.now()
        self.save()

def init_db(username, password):
    db.connection.drop_database('mydb')

    admin = User(   username=username, 
                    firstname=username, 
                    lastname=username, 
                    email=username + "@orange.com", 
                    password=password,
                    role=int(UserRole.ADMIN))
   
    admin.create()
    print( "account created: login({}), password({}).".format(username, password))


class Visitor(db.Document):
    browser = db.StringField(requierd=True)
    language = db.StringField()
    platform = db.StringField(requierd=True)
    agent_name = db.StringField(requierd=True)
    agent_version = db.StringField(requierd=True)
    ip_address = db.StringField(requierd=True)
    visited_at = db.DateTimeField(requierd=True)
    user = db.ReferenceField(document_type=User)

    def create(self, request):
        user_agent = request.user_agent
        if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
            remote_addr = request.environ['REMOTE_ADDR']
        else:
            remote_addr = request.environ['HTTP_X_FORWARDED_FOR'] # if behind a proxy
        self.browser = user_agent.browser
        self.language = user_agent.language
        self.platform = user_agent.platform
        self.agent_name = user_agent.string
        self.agent_version = user_agent.version
        self.ip_address = remote_addr
        self.visited_at = datetime.now()
        self.save()
            