from flask import Blueprint, render_template, request
from .modles import User
from .exceptions import *
from .constants import *


auth = Blueprint('auth', __name__)


@auth.route('/user/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template('signin.html')
    elif request.method == 'POST':
        return User().login()


@auth.route('/user/signout')
def signout():
    return User().signout()


@auth.route('/user/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')
    elif request.method == 'POST':
        return User().signup()
