from flask import Blueprint, jsonify, make_response, request
from . import db
from .services import *

views = Blueprint('views', __name__)


@views.route('/', methods=['GET'])
def home():
    return "Home page"


@views.route('/instances', methods=['GET', 'POST', 'DELETE'])
def api_instances():
    if request.method == 'GET': # get all instances
        return get_all_instances(request.args)

    elif request.method == 'POST': # create instance
        return create_instance(request.json)
        
    elif request.method == 'DELETE': # delete all instances
        return delete_all_instances()


@views.route('/instances/search/byType/<type>', methods=['GET'])
def api_instances_search_by_type(type):
    if request.method == 'GET': # get all instances
        return get_all_instances(type, request.args)

    else:
        return bad_request_exception("Not a GET method")


@views.route('/instances/<id>', methods=['GET', 'PUT', 'DELETE'])
def api_each_instance(id):
    if request.method == 'GET':
        return get_instance(id)

    elif request.method == 'PUT': # update instance
        return update_instance(id, request.json)

    elif request.method == 'DELETE': # delete instance
        return delete_instance(id)


@views.route('/instances/<id>/children', methods=['GET', 'PUT'])
def api_instances_children(id):
    if request.method == 'GET': # get instance children
        return get_instance_children(id, request.args)

    elif request.method == 'PUT': # bind instance to child
        return bind_instance_to_child(id, request.json)
        
    else:
        return bad_request_exception("Not a GET/PUT method")


@views.route('/instances/<id>/parent', methods=['GET'])
def api_instances_parent(id):
    if request.method == 'GET': # get instance parent
        return get_instance_parent(id)
        
    else:
        return bad_request_exception("Not a GET method")


@views.route('/activities', methods=['POST'])
def api_activities():
    if request.method == 'POST': # invoke activity
        return invoke_activity(request.json)
        
    else:
        return bad_request_exception("Not a POST method")