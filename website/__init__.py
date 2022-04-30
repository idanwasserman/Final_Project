from .config import *
from .invoker import Invoker
from pymongo import MongoClient
from website.command import get_commands_dict


client = MongoClient(
                    host=host,
                    port=port, 
                    username=username, 
                    password=password,
                    authSource=authSource)
db = client[CLIENT_NAME] 

invoker = Invoker()
for command_name, command in get_commands_dict().items():
    invoker.register(command_name=command_name, command=command)


def create_app():
    from flask import Flask

    app = Flask(__name__)

    from .views import views
    app.register_blueprint(views, url_prefix='/')
    return app

