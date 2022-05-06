import uuid
import pymongo
from . import db, invoker
from flask import jsonify, make_response
from .exceptions import *
from .constants import *
from ml.model import predict_sqli


def get_all_instances(args):
    # get size and page from args
    size = int(get_argument(SIZE, args, 10))
    if size <= 0:
        return not_accepteable_exception("Size cannot be lees than 1")
    page = int(get_argument(PAGE, args, 0))
    if page < 0:
        return not_accepteable_exception("Page cannot be lees than 0")

    # get all instances
    try:
        cursor = db.project_tb.find().sort(ID, pymongo.ASCENDING).skip(size * page).limit(size)
        instances = []
        for doc in cursor:
            instance = document_to_instance(doc)
            if instance != None:
                instances.append(instance)

    except Exception as e:
        return bad_request_exception(f"get_all_instances(args) caught exception: {e}")

    return make_response({"instances": instances})


def get_all_instances_by_type(type, args):
    # get size and page from args
    size = int(get_argument(SIZE, args, 10))
    if size <= 0:
        return not_accepteable_exception("Size cannot be lees than 1")
    page = int(get_argument(PAGE, args, 0))
    if page < 0:
        return not_accepteable_exception("Page cannot be lees than 0")

    # check type
    if type is None or len(type) == 0 or type not in VALID_TYPES:
        return empty_field_exception(f"The type |{type}| is invalid")

    # get all instances by type from db
    try:
        my_query = { TYPE: type }
        cursor = db.project_tb.find(my_query).sort(ID, pymongo.ASCENDING).skip(size * page).limit(size)
        instances = [document_to_instance(doc) for doc in cursor]
        return make_response({"instances": instances})

    except Exception as e:
        return bad_request_exception({
            TYPE: type,
            "args": args,
            RESULT: f"Something went wrong in get_all_instances_by_type(type, args): {e}"
        })


def get_all_instances_by_attribute(attKey, value, args):
    # get size and page from args
    size = int(get_argument(SIZE, args, 10))
    if size <= 0:
        return not_accepteable_exception("Size cannot be lees than 1")
    page = int(get_argument(PAGE, args, 0))
    if page < 0:
        return not_accepteable_exception("Page cannot be lees than 0")

    # check attKey and attVal
    if attKey is None or len(attKey) == 0:
        return empty_field_exception(f"attKey is missing")
    if value is None or len(value) == 0:
        return empty_field_exception(f"attVal is missing")

    # get all instances by attribute
    key = ATTRIBUTES + '.' + attKey
    my_query = {key: value}
    try:
        cursor = db.project_tb.find(my_query)
        instances = [document_to_instance(doc) for doc in cursor]
        return instances
        
    except Exception as e:
        return bad_request_exception({
            "attKey": attKey, "attVal": value, "args": args,
            RESULT: f"Something went wrong in get_all_instances_by_attribute(attKey, value, args): {e}"
        })        


def create_instance(json):
    # check json and get instance to create
    if INSTANCE not in json:
        return empty_field_exception("JSON does not contain new instance to create")
    instance = json[INSTANCE]
    validity_result = check_instance_validity(instance)
    if validity_result != None:
        return validity_result

    # inject more attributes to instance
    instance[ID] = str(uuid.uuid4())
    instance[PARENT] = None
    instance[CHILDREN] = []

    # insert instance to database
    result = db.project_tb.insert_one(instance)
    msg = jsonify({
        RESULT: str(result.inserted_id),
        INSTANCE: instance
    })
    return make_response(msg)


def delete_all_instances():
    db.project_tb.delete_many({})
    return make_response("Deleted all instances from database")


def get_instance(id):
    if id is None or len(id) == 0:
        return not_accepteable_exception("Cannot get instance with empty id")

    # get instance from database
    instance = get_instance_from_db(id)
    if instance == None:
        return not_found_exception(f"Could not find instance with id: {id}")
    return make_response(instance)


def update_instance(id, json):
    # check if attributes to update are in the Json
    if ATTRIBUTES not in json:
        return empty_field_exception("JSON does not contain attributes to update")
    attributes_to_update = json[ATTRIBUTES]

    # get the instance from db and update
    try:
        doc_to_update = { ID: id }
        new_values = { SET_OPERATOR: { ATTRIBUTES: attributes_to_update }}
        result = db.project_tb.update_one(doc_to_update, new_values)
        count = result.modified_count 
        return make_response(jsonify({"modified_count": count}))

    except Exception as e:
        return bad_request_exception(f"Update instance caught an exception - {e}") 


def delete_instance(id):
    result = db.project_tb.find_one_and_delete({ID: id})
    return make_response({RESULT: jsonify(result)})


def get_instance_children(id, args):
    try:
        # get size and page
        size = int(get_argument(SIZE, args, 10))
        if size <= 0:
            return not_accepteable_exception("Size cannot be lees than 1")
        page = int(get_argument(PAGE, args, 0))
        if page < 0:
            return not_accepteable_exception("Page cannot be lees than 0")

        # get parent instance
        parent = get_instance_from_db(id)
        if parent == None:
            return not_found_exception(f"Could not find instance with id: {id}") 

        # get instance's chidren
        children = []
        cursor = db.project_tb.find({ ID: { IN_OPERATOR: parent[CHILDREN] }})
        for doc in cursor:
            child = document_to_instance(doc)
            if child is not None:
                children.append(child)
        return make_response({ CHILDREN: children })


    except Exception as e:
        return bad_request_exception(f"Something went wrong in get_instance_children(id, args): {e}")


def bind_instance_to_child(id, json):
    # get the parent
    parent = get_instance_from_db(id)
    if parent is None:
        return not_found_exception(f"Could not find instance (parent) with id: {id}")

    # get the child
    if ID not in json:
        return empty_field_exception("JSON does not contain ID to bind to instance")
    child = get_instance_from_db(json[ID])
    if child is None:
        return not_found_exception(f"Could not find instance (child) with id: {json[ID]}")

    # update parent
    try:
        if child[ID] not in parent[CHILDREN]:
            parent[CHILDREN].append(child[ID])
            doc_to_update = { ID: parent[ID] }
            new_values = { SET_OPERATOR: { CHILDREN: parent[CHILDREN] }}
            result = db.project_tb.update_one(doc_to_update, new_values)

    except Exception as e:
        return bad_request_exception(
            f"bind_instance_to_child(id, json) caught exc when tried to update {PARENT}: {e} , parent: {parent}")

    # update child
    try:
        if child[PARENT] != parent[ID]:
            doc_to_update = { ID: child[ID] }
            new_values = { SET_OPERATOR: { PARENT: parent[ID] }}
            result = db.project_tb.update_one(doc_to_update, new_values)
            count_child = result.modified_count
        else:
            count_child = 0
            
    except Exception as e:
        return bad_request_exception(
            f"bind_instance_to_child(id, json) caught exc when tried to update {CHILD}: {e}")

    return make_response("binded successfully")


def get_instance_parent(id):
    # get the child
    child = get_instance_from_db(id)
    if child is None:
        return not_found_exception(f"Could not find instance with id: {id}") 

    # get child's parent id
    parent_id = child[PARENT]
    if parent_id is None:
        return not_found_exception(f"Instance with id: {id}, does not have a parent instance")

    # get the parent
    parent = get_instance_from_db(parent_id)
    if parent is None:
        return not_found_exception(f"Could not find parent with id: {parent_id}")
    return make_response({CHILD: child, PARENT: parent}, 200)


def check_instance_validity(instance):
    # check instance's type
    if TYPE not in instance:
        return empty_field_exception(f"Instance must contain {TYPE}")
    elif len(instance[TYPE]) == 0:
        return empty_field_exception(f"Instance's {TYPE} cannot be empty string")
    elif instance[TYPE] not in VALID_TYPES:
        return empty_field_exception(f"Instance's {TYPE} is not valid")

    # check instance's attributes
    if ATTRIBUTES not in instance:
        return empty_field_exception(f"Instance must contain {ATTRIBUTES}")
    elif type(instance[ATTRIBUTES]) is not dict:
        return empty_field_exception(f"Instance's {ATTRIBUTES} should be a dictionary")
    elif not instance[ATTRIBUTES]:
        return empty_field_exception(f"Instance's {ATTRIBUTES} cannot be empty")

    return None # instance is valid

    
def get_argument(arg, args, def_value):
    if arg in args:
        return args[arg]
    else:
        return def_value


def get_instance_from_db(id):
    try:
        return document_to_instance(db.project_tb.find({ID: id})[0])

    except:
        return None
    
    
def document_to_instance(doc):
    try:
        return {
            ID: doc[ID],
            TYPE: doc[TYPE], 
            ATTRIBUTES: doc[ATTRIBUTES],
            PARENT: doc[PARENT],
            CHILDREN: doc[CHILDREN]
        }
    except:
        return None


def invoke_activity(json):
    # check Json contains instance
    if INSTANCE not in json:
        return bad_request_exception(f"invoke_activity(json) does not contain {INSTANCE} in Json")
    instance = json[INSTANCE]

    # check instance's type
    try:
        if instance[TYPE] != ACTIVITY:
            return bad_request_exception(f"invoke_activity(json) {INSTANCE} is not of type {ACTIVITY}")
    except Exception as e:
        return bad_request_exception(f"invoke_activity(json) instance's type is invalid - {e}")

    # check instance has activity attributes
    if ATTRIBUTES not in instance:
        return bad_request_exception(f"invoke_activity(json) {INSTANCE} has no {ATTRIBUTES}")

    # invoke activity
    # return make_response({
    #     "dir": str(dir(invoker))
    # })
    try:
        return invoker.execute(instance[ATTRIBUTES])
    except Exception as e:
        return bad_request_exception(f"invoke_activity(json) caught exception: {e}")


def predict(form):
    if form is None:
        return jsonify({ERROR: 'form is None'}), 400

    if TEXT not in form:
        return jsonify({ERROR: f'{TEXT} not in form'}), 400

    input = form[TEXT]
    try:
        output = predict_sqli(input)
        return jsonify({OUTPUT: output}), 200

    except Exception as e:
        return jsonify({ERROR: f"predict(form): caught exception - {e}"}), 400