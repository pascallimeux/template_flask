from functools import wraps
from datetime import datetime, timedelta
from flask import request, jsonify, abort
import jwt
from ..config import Config
from ..models import User

TOKEN_NAME = 'access_token'
TOKEN_DURATION = timedelta(minutes=10)
TOKEN_REFRESH_DURATION = timedelta(minutes=5)
JWT_ALGO = 'HS256'


def token_required(func):
    @wraps(func)
    def wrapped_fct(*args, **kwargs):
        token = None
        auth_headers = request.headers.get('Authorization', '').split()
        if len(auth_headers) == 2 and auth_headers[0] == 'Bearer':
            token = auth_headers[1]
        else:
            abort(401, {'message': 'a valid token is missing'})
        try:
            data = decode_token(token)
            current_user = User.objects.get(id=data['user_id'])
        except Exception as e:
            abort(401, {'message': 'token is invalid'})
        return func(current_user, *args, **kwargs)

    return wrapped_fct



def refresh_token(request):
    """
    Refresh a token
    :param request
    :return: string
    """
    token = None
    auth_headers = request.headers.get('Authorization', '').split()
    if len(auth_headers) == 2 and auth_headers[0] == 'Bearer':
        token = auth_headers[1]
    else:
        abort(401, {'message': 'a valid token is missing'})
    try:
        data = jwt.decode(
            token, 
            Config.SECRET_KEY, 
            leeway=TOKEN_REFRESH_DURATION, 
            algorithms=JWT_ALGO)
        new_token = encode_token(data['sub']['user_id'])
        return new_token
    except Exception as e:
        abort(401, {'message': 'token is invalid'})



def encode_token(userid):
    """
    Generates the Auth Token
    :param userid
    :return: string
    """
    payload = {
        'exp': datetime.utcnow() + TOKEN_DURATION,
        'iat': datetime.utcnow(),
        'sub': {"user_id": userid}
    }
    return jwt.encode(
        payload,
        Config.SECRET_KEY,
        algorithm=JWT_ALGO
    )


def decode_token(token):
    """
    Decodes the auth token
    :param token
    :return: integer|string
    """
    try:
        payload = jwt.decode(token, Config.SECRET_KEY)
        return payload['sub']
    except jwt.ExpiredSignatureError:
        return Raise ('Signature expired. Please log in again.')
    except jwt.InvalidTokenError:
        return Raise ('Invalid token. Please log in again.')
