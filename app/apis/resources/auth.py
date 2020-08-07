
import sys
from flask_restful import Resource
from flask import request

sys.path.insert(0,'../..')

from app.models import User
from ..jwt import TOKEN_NAME, encode_token, refresh_token
from app.auth.forms import LoginForm

class LoginAPI(Resource):

    def post(self):
        try:
            data = request.get_json()
            loginForm = LoginForm(**data, meta={'csrf': False})
            if loginForm.validate():
                username = loginForm.data['username']
                password = loginForm.data['password']
                if User.objects(username=username):
                    user = User.objects.get(username=username)
                    if user.check_password(password):
                        if user.is_active():
                            user.refresh_last_login()
                            user.save()

                            token = encode_token(str(user.id))
                            responseObject = {
                                'status': 'success',
                                'message': 'Successfully logged in.',
                                TOKEN_NAME: token.decode()
                            }
                            return responseObject, 200

                        else:
                            responseObject = {
                                'status': 'fail',
                                'message': 'User is not active.'
                            }
                            return responseObject, 404
                    else:
                        responseObject = {
                            'status': 'fail',
                            'message': 'Bad password.'
                        }
                        return responseObject, 401
                else:
                    responseObject = {
                        'status': 'fail',
                        'message': 'User does not exist.'
                    }
            else:
                responseObject = {
                    'status': 'fail',
                    'message': 'Bad format for request.'
                }
            return responseObject, 404

        except Exception as e :
            print(e)
            responseObject = {
                'status': 'fail',
                'message': 'Try again'
            }
            return responseObject, 500

class RefreshTokenAPI(Resource):
    
    def get(self):
        token = refresh_token(request)
        responseObject = {
            'status': 'success',
            'message': 'Successfully logged in.',
            TOKEN_NAME: token.decode()
        }
        return responseObject, 200

