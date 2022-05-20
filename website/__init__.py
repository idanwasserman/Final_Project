from functools import wraps
from flask import redirect, session
from website.constants import LOGGED_IN
from .config import *
from .invoker import Invoker
from pymongo import MongoClient
from website.command import get_commands_dict
# from flask_login import LoginManager


# Database
client = MongoClient(
                    host=host,
                    port=port, 
                    username=username, 
                    password=password,
                    authSource=authSource)
db = client[CLIENT_NAME] 

# Invoker
invoker = Invoker()
for command_name, command in get_commands_dict().items():
    invoker.register(command_name=command_name, command=command)

# Decoartors
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if LOGGED_IN in session:
            return f(*args, **kwargs)
        else:
            return redirect('/user/login')
    return wrap


def create_app():
    from flask import Flask

    app = Flask(__name__)
    app.secret_key = b'\xc0\xcb\xd2h\xfc\xb6\x80\xa7!9@\x92\xcd\xf7\xa9\x1e'

    from .views import views
    from .auth import auth
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    # login_manager = LoginManager()
    # login_manager.login_view = 'auth.login'
    # login_manager.init_app(app)


    return app

