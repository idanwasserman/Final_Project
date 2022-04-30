from http.client import BAD_REQUEST, NOT_ACCEPTABLE, NOT_FOUND, UNAUTHORIZED
from flask import make_response

def access_denied_exception(msg):
    return make_response(msg, UNAUTHORIZED)

def empty_field_exception(msg):
    return make_response(msg, NOT_ACCEPTABLE)

def not_found_exception(msg):
    return make_response(msg, NOT_FOUND)

def bad_request_exception(msg):
    return make_response(msg, BAD_REQUEST)
    
def not_accepteable_exception(msg):
    return make_response(msg, NOT_ACCEPTABLE)
