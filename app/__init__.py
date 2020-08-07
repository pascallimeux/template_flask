
import click
import json
import os
import io
from flask import Flask, render_template, url_for, request, abort, redirect, flash, session, send_file
from flask_login import login_required, LoginManager, login_user, logout_user, current_user
from flask_socketio import SocketIO
from flask_cors import CORS
#from flask_mail import Message, Mail
from base64 import b64encode

from . import config
from .config import LOGGER
from .models import init_db, db, User, Image, UserRole
from .home import home as home_blueprint
from .auth import auth as auth_blueprint
from .user import user as user_blueprint
from .image import image as image_blueprint
from .admin import admin as admin_blueprint
from .apis import v1

socketio = SocketIO(cors_allowed_origins="*", engineio_logger=False)

def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/*":{"origins":"*"}})
    
    login_manager = LoginManager()

    # Read config in first
    app.config.from_object('app.config.Config')
    #app.debug = True
    
    
    db.init_app(app)
    login_manager.init_app(app)
    #mail = Mail(app)
    
    # flask web
    app.register_blueprint(home_blueprint)
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(user_blueprint)
    app.register_blueprint(image_blueprint)
    app.register_blueprint(admin_blueprint)

    # flask restful
    app.register_blueprint(v1, url_prefix='/api/v1')

    # flask sockerio
    socketio.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        try:
            user = User.objects.get(id=id)
        except Exception as e:
            LOGGER.error(e)
            return None
        return user

    @app.errorhandler(403)
    def unauthenticated(e=None):
        LOGGER.info(f"Unauthenticated access: {request.url}")
        return render_template("errors/401.html", error=e), 401

    @app.errorhandler(403)
    def forbidden(e=None):
        LOGGER.info(f"Forbidden access: {request.url}")
        return render_template("errors/403.html", error=e), 403

    @app.errorhandler(404)
    def page_not_found(e=None):
        LOGGER.info(f"Page not found: {request.url}")
        return render_template("errors/404.html", error=e), 404

    @app.errorhandler(500)
    def server_error(e=None):
        app.logger.error(f"Server error: {request.url}")
        return render_template("errors/500.html", error=e), 500
    
    return app


app = create_app()


# use from command line to init DB with one account
@app.cli.command("initdb")
@click.argument("password")
def create_user(password='admin'):
    """Initialize the database."""
    init_db('admin', password)
