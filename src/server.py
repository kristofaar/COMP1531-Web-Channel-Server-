import sys
import signal
from json import dumps
from flask import Flask, request
from flask_cors import CORS
from src.error import InputError
from src import config
from src.auth import auth_login_v1, auth_register_v1, auth_logout_v1
from src.data_store import data_store
from src.channels import channels_create_v1,channels_listall_v1,channels_list_v1
from src.channel import channel_details_v1, channel_invite_v1, channel_join_v1, channel_messages_v1
from src.dm import dm_create_v1, dm_list_v1, dm_remove_v1, dm_details_v1, dm_messages_v1
from src.other import clear_v1
from src.message import message_send_v1, message_edit_v1, message_remove_v1, message_senddm_v1
from src.user import users_all_v1
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

datas = []
try:
    datas = pickle.load(open("datastore.p", "rb"))
    storage = data_store.get()
    storage['users'] = datas['users']
    storage['channels'] = datas['channels']
    storage['no_users'] = datas['no_users']
    storage['dms'] = datas['dms']
    storage['session_id'] = datas['session_id']
    data_store.set(storage)
except Exception:
    pass

#persistence
def save():
    storage = data_store.get()
    data = {'users': storage['users'], 'channels': storage['channels'], 'no_users': storage['no_users'], 'dms': storage['dms'], 'session_id': storage['session_id']}
    with open('datastore.p', 'wb+') as FILE:
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

#AUTH FUNCTION WRAPPERS
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

@APP.route('/auth/logout/v1', methods=['POST'])
def logout():
    data = request.get_json()
    auth_logout_v1(data['token'])
    save()
    return dumps({})

#CHANNEL FUNCTION WRAPPERS
@APP.route('/channels/create/v2', methods=['POST'])
def create():
    data = request.get_json()
    details = channels_create_v1(data['token'], data['name'], data['is_public'])
    save()
    return dumps({
        'channel_id': details['channel_id']
    })

@APP.route('/channels/list/v2', methods=['GET'])
def channel_list():
    return channels_list_v1(request.args.get("token"))

@APP.route('/channels/listall/v2', methods=['GET'])
def channel_listall():
    return channels_listall_v1(request.args.get("token"))
    
@APP.route('/channel/details/v2', methods=['GET'])
def details():
    return channel_details_v1(request.args.get("token"), request.args.get("channel_id"))

@APP.route('/channel/join/v2', methods=['POST'])
def join():
    data = request.get_json()
    channel_join_v1(data['token'], data['channel_id'])
    save()
    return dumps({})

@APP.route('/channel/invite/v2', methods=['POST'])
def invite():
    data = request.get_json()
    channel_invite_v1(data['token'], data['channel_id'], data['u_id'])
    save()
    return dumps({})

@APP.route("/channel/messages/v2", methods=['GET'])
def messages():
    return dumps(channel_messages_v1(request.args.get('token'), request.args.get('channel_id'), request.args.get('start')))


#DM FUNCTION WRAPPERS
@APP.route('/dm/create/v1', methods=['POST'])
def dm_create():
    data = request.get_json()
    details = dm_create_v1(data['token'], data['u_ids'])
    save()
    return dumps({
        'dm_id': details['dm_id']
    })

@APP.route('/dm/list/v1', methods=['GET'])
def dm_list():
    return dm_list_v1(request.args.get("token"))

@APP.route("/dm/remove/v1", methods=['DELETE'])
def dm_remove():
    data = request.get_json()
    dm_remove_v1(data['token'], data['dm_id'])
    save()
    return dumps({})

@APP.route('/dm/details/v1', methods=['GET'])
def dm_details():
    return dm_details_v1(request.args.get("token"), request.args.get("dm_id"))

#MESSAGES FUNCTION WRAPPERS
@APP.route("/message/send/v1", methods=['POST'])
def send_message():
    data = request.get_json()
    details = message_send_v1(data['token'], data['channel_id'], data['message'])
    save()
    return dumps({
        'message_id': details['message_id']
    })

@APP.route("/message/edit/v1", methods=['PUT'])
def edit_message():
    data = request.get_json()
    message_edit_v1(data['token'], data['message_id'], data['message'])
    save()
    return dumps({})

@APP.route("/message/remove/v1", methods=['DELETE'])
def remove_message():
    data = request.get_json()
    message_remove_v1(data['token'], data['message_id'])
    save()
    return dumps({})

@APP.route("/message/senddm/v1", methods=['POST'])
def senddm():
    data = request.get_json()
    details = message_senddm_v1(data['token'], data['dm_id'], data['message'])
    save()
    return dumps({
        'message_id': details['message_id']
    })

@APP.route("/clear/v1", methods=['DELETE'])
def clear():
    clear_v1()
    save()
    return dumps({})
    
#USER FUNCTION WRAPPERS
@APP.route('/users/all/v1', methods=['GET'])
def users_all():
    return users_all_v1(request.args.get("token"))

@APP.route("/user/profile/v1", methods=["GET"])
def user_profile():
    return user_profile_v1(request.args.get("token"))

@APP.route("/user/profile/setname/v1", methods=["PUT"])
def user_profile():
    return {}

@APP.route("/user/profile/setemail/v1", methods=["PUT"])
def user_profile():
    return {}

@APP.route("/user/profile/sethandle/v1", methods=["PUT"])
def user_profile():
    return {}


#### NO NEED TO MODIFY BELOW THIS POINT

if __name__ == "__main__":
    signal.signal(signal.SIGINT, quit_gracefully) # For coverage
    APP.run(port=config.port) # Do not edit this port
