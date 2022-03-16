import sys
import signal
from json import dumps
from flask import Flask, request
from flask_cors import CORS
from src.error import InputError
from src import config
from src.auth import auth_login_v1, auth_register_v1
from src.data_store import data_store
import pickle

def quit_gracefully(*args):
    '''For coverage'''
    exit(0)

def defaultHandler(err):
    response = err.get_response()
    print('response', err, err.get_response())
    response.data = dumps({
        "code": err.code,
        "name": "System Error",
        "message": err.get_description(),
    })
    response.content_type = 'application/json'
    return response

APP = Flask(__name__)
CORS(APP)

APP.config['TRAP_HTTP_EXCEPTIONS'] = True
APP.register_error_handler(Exception, defaultHandler)

#### NO NEED TO MODIFY ABOVE THIS POINT, EXCEPT IMPORTS

#data store
data_store = []
try:
    data_store = pickle.load(open("datastore.p", "rb"))
    storage = data_store.get()
    storage['users'] = data_store[0]['users']
    storage['channels'] = data_store[0]['channels']
    storage['no_users'] = data_store[0]['no_users']
    data_store.set(storage)
except Exception:
    pass

def save():
    storage = data_store.get()
    data = {storage['users'], storage['channels'], storage['no_users']}
    with open('datastore.p', 'wb') as FILE:
        pickle.dump(data, FILE)


# Example
@APP.route("/echo", methods=['GET'])
def echo():
    data = request.args.get('data')
    if data == 'echo':
   	    raise InputError(description='Cannot echo "echo"')
    return dumps({
        'data': data
    })

@APP.route("/auth/login/v2", methods=['POST'])
def login():
    data = request.get_json()
    details = auth_login_v1(data['email'], data['password'])
    save()
    return dumps({
        'token': details['token'],
        'auth_user_id': details['auth_user_id']
    })

@APP.route("/auth/register/v2", methods=['POST'])
def register():
    data = request.get_json()
    details = auth_register_v1(data['email'], data['password'], data['name_first'], data['name_last'])
    save()
    return dumps({
        'token': details['token'],
        'auth_user_id': details['auth_user_id']
    })

@APP.route("/channel/messages/v2", methods=['GET'])
def messages():
    return dumps(channel_messages_v1(request.args.get('token'), request.args.get('channel_id'), request.args.get('start')))
    
@APP.route("clear/v1", methods=['DELETE'])
def clear():
    return dumps(clear_v1())
    

#### NO NEED TO MODIFY BELOW THIS POINT

if __name__ == "__main__":
    signal.signal(signal.SIGINT, quit_gracefully) # For coverage
    APP.run(port=config.port) # Do not edit this port
