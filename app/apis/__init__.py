from flask import Blueprint
from flask_restful import Api


from .resources.user import UserListAPI, UserAPI
from .resources.auth import LoginAPI, RefreshTokenAPI

v1 = Blueprint('v1', __name__)
api = Api()
api.init_app(v1)

@v1.route('/')
def show():
    return 'API version 1'

api.add_resource(UserListAPI, '/users')
api.add_resource(UserAPI, '/user/<string:id>')
api.add_resource(LoginAPI, '/login')
api.add_resource(RefreshTokenAPI, '/refresh_token')

