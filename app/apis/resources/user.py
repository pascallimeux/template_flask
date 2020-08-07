
from flask_restful import Resource
from flask import Response, request, abort

import sys
sys.path.append('../../..')

from app.models import User, UserRole
from app.user.forms import UserForm
from ..jwt import token_required

class UserListAPI(Resource):

    @token_required
    def get(self, current_user):
        '''List all users'''
        users = User.objects().to_json()
        return Response(users, mimetype="application/json", status=200)

    @token_required
    def post(self, current_user):
        '''Create a user'''
        data = request.get_json()
        userForm = UserForm(**data, meta={'csrf': False})
        if userForm.validate():
            post_user = User(**data).create()
        else:
            abort(404,userForm.errors)
        return Response(post_user.to_json(), mimetype="application/json", status=201)


class UserAPI(Resource):

    @token_required
    def get(self, current_user, id):
        '''Fetch a user given its identifier'''
        user = User.objects.get_or_404(id=id)
        return Response(user.to_json(), mimetype="application/json", status=200)

    @token_required
    def put(self, current_user, id):
        '''Update a user given its identifier'''
        data = request.get_json()
        put_user = User.objects(id=id).update(**data)
        return Response(put_user.to_json(), mimetype="application/json", status=200)

    @token_required
    def delete(self, current_user, id):
        '''Delete a user given its identifier'''
        user = User.objects.get_or_404(id=id)
        user.delete()
        return None, 202