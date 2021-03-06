from flask import Blueprint, jsonify, make_response, render_template, request
from . import db, login_required
from .services import *


views = Blueprint('views', __name__)


@views.route('/')
def home():
    return render_template('home.html') 

@views.route('/about/')
def about():
    return render_template('about.html')

@views.route('/testCode/', methods=['GET', 'POST'])
@login_required
def testCode():
    if request.method == 'GET':
        return render_template('testCode.html')
    elif request.method == 'POST':
        result_msg = predict(request.form)[0].get_json()[OUTPUT]
        isRisk = 0
        if "HIGH" in result_msg:
            isRisk = 2
        elif "LOW" in result_msg:
            isRisk = 1
        # prediction = predict(request.form)
        # response = prediction[0]
        # result_msg = response.get_json()[OUTPUT]
        output = f"Result: { result_msg }"
        return render_template("testCode.html", msg=output, risk = isRisk)

@views.route('/dashboard/')
@login_required
def dashboard():
    return render_template('dashboard.html')


@views.route('/mongoSQLI')
def mongoSQLI():
    return render_template('mongoSQLI.html')


@views.route('/redisSQLI')
def redisSQLI():
    return render_template('redisSQLI.html')


@views.route('/instances/', methods=['GET', 'POST', 'DELETE'])
def api_instances():
    if request.method == 'GET': # get all instances
        return get_all_instances(request.args)

    elif request.method == 'POST': # create instance
        return create_instance(request.json)
        
    elif request.method == 'DELETE': # delete all instances
        return delete_all_instances()


@views.route('/instances/search/byType/<type>/', methods=['GET'])
def api_instances_search_by_type(type):
    if request.method == 'GET': # get all instances
        return get_all_instances_by_type(type, request.args)

    else:
        return bad_request_exception("Not a GET method")


@views.route('/instances/search/byAtt/<attKey>/<attVal>/', methods=['GET'])
def api_instances_search_by_att(attKey, attVal):
    if request.method == 'GET': # get all instances that contains (attKey: attVal) in attributes
        return get_all_instances_by_attribute(attKey, attVal, request.args)

    else:
        return bad_request_exception("Not a GET method")


@views.route('/instances/<id>/', methods=['GET', 'PUT', 'DELETE'])
def api_each_instance(id):
    if request.method == 'GET':
        return get_instance(id)

    elif request.method == 'PUT': # update instance
        return update_instance(id, request.json)

    elif request.method == 'DELETE': # delete instance
        return delete_instance(id)


@views.route('/instances/<id>/children/', methods=['GET', 'PUT'])
def api_instances_children(id):
    if request.method == 'GET': # get instance children
        return get_instance_children(id, request.args)

    elif request.method == 'PUT': # bind instance to child
        return bind_instance_to_child(id, request.json)
        
    else:
        return bad_request_exception("Not a GET/PUT method")


@views.route('/instances/<id>/parent/', methods=['GET'])
def api_instances_parent(id):
    if request.method == 'GET': # get instance parent
        return get_instance_parent(id)
        
    else:
        return bad_request_exception("Not a GET method")


@views.route('/activities/', methods=['POST'])
def api_activities():
    if request.method == 'POST': # invoke activity
        return invoke_activity(request.json)
        
    else:
        return bad_request_exception("Not a POST method")


@views.route('/history/')
@login_required
def history():
    user_history = get_user_history()
    return render_template('history.html', data=user_history[HISTORY])