from flask_login import login_required, current_user
from functools import wraps
from flask import abort, _request_ctx_stack, current_app, has_request_context

def admin_required(func):
    @wraps(func)
    def wrapped_fct(*args, **kwargs):
        if not current_user:
            abort(401)
        if not current_user.is_admin():
            abort(403)
        return func(*args, **kwargs)

    return wrapped_fct


def owner_required(func):
    @wraps(func)
    def wrapped_fct(*args, **kwargs):
        if not current_user:
            abort(401)
        #all_args = kwargs.copy()
        if _is_owner(current_user, kwargs):
            return func(*args, **kwargs)
        abort(403)

    return wrapped_fct


def owner_or_admin_required(func):
    @wraps(func)
    def wrapped_fct(*args, **kwargs):
        if not current_user:
            abort(401)
        if _is_admin(current_user) or _is_owner(current_user, kwargs):
            return func(*args, **kwargs)
        abort(403)

    return wrapped_fct


def _get_user():
    if has_request_context() and not hasattr(_request_ctx_stack.top, 'user'):
        current_app.login_manager._load_user()
    return getattr(_request_ctx_stack.top, 'user', None)

def _is_admin(user):
    return user.is_admin()

def _is_owner(user, args):
    if 'userid' in args:
        userid = args['userid']
        return  str(user.id) == userid
    return False
