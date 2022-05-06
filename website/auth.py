from flask import Blueprint
from .modles import User
from .exceptions import *
from .constants import *


auth = Blueprint('auth', __name__)


@auth.route('/user/login', methods=['POST'])
def login():
    return User().login()


@auth.route('/user/signout')
def signout():
    return User().signout()


@auth.route('/user/signup', methods=['POST'])
def signup():
    return User().signup()

