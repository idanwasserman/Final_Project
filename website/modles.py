import uuid
from flask import Flask, jsonify, redirect, request, session
from passlib.hash import pbkdf2_sha256
from .constants import *
from . import db


class User():

    def start_session(self, user):
        del user[PASSWORD]
        session[LOGGED_IN] = True
        session[USER] = user

        return jsonify(user), 200


    def signup(self):
        # Extract info from request.form
        username = request.form.get(USERNAME)
        email = request.form.get(EMAIL)
        password1 = request.form.get(PASSWORD + '1')
        password2 = request.form.get(PASSWORD + '2')

        # Check if email exists in users
        if email is None or len(email) == 0:
            return jsonify({ ERROR: "Email cannot be empty string!"}), 400
        existing_user = db.users.find_one({ EMAIL: email})
        if existing_user:
            return jsonify({ ERROR: "Email address already in use!"}), 400

        # Check username and passwords
        if username is None or len(username) == 0:
            return jsonify({ ERROR: "Username cannot be empty string!"}), 400

        if len(password1) < 4:
            return jsonify({ ERROR: "Password needs to be at least 4 characters!"}), 400
        if password1 != password2:
            return jsonify({ ERROR: "Passwords don't match!"}), 400

        # Create the user object
        user = {
            ID: uuid.uuid4().hex,
            USERNAME: username,
            EMAIL: email,
            PASSWORD: password1           
        }

        # Encrypt the password
        user[PASSWORD] = pbkdf2_sha256.encrypt(user[PASSWORD])

        if db.users.insert_one(user):
            return self.start_session(user)

        return jsonify({ ERROR: "Signup failed!"}), 400


    def signout(self):
        session.clear()
        return redirect('/')


    def login(self):
        # Extract info from request.form
        password = request.form.get(PASSWORD)
        email = request.form.get(EMAIL)

        if email is None or len(email) == 0:
            return jsonify({ ERROR: "Email cannot be empty string!"}), 400
        if password is None or len(password) == 0:
            return jsonify({ ERROR: "Password cannot be empty string!"}), 400

        # Get user if exist in db
        doc = db.users.find_one({ EMAIL: email })
        if doc is None:
            return jsonify({ ERROR: "Account doesn't exist!"}), 400

        # Check password
        user = get_user(doc)
        if pbkdf2_sha256.verify(password, user[PASSWORD]):
            return self.start_session(user)
        else:
            return jsonify({ ERROR: "Wrong password!" }), 400        


def get_user(doc):
    user = {}
    user[ID] = doc[ID]
    user[EMAIL] = doc[EMAIL]
    user[PASSWORD] = doc[PASSWORD]
    user[USERNAME] = doc[USERNAME]
    return user