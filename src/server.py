import sys
import signal
from json import dumps
from flask import Flask, request
from flask_mail import Mail, Message
from flask_cors import CORS
from src.error import InputError
from src import config
from src.auth import auth_login_v1, auth_register_v1, auth_logout_v1, auth_passwordreset_request_v1, auth_passwordreset_reset_v1
from src.data_store import data_store
from src.channels import channels_create_v1, channels_listall_v1, channels_list_v1
from src.channel import channel_details_v1, channel_invite_v1, channel_join_v1, channel_messages_v1, channel_leave_v1, channel_addowner_v1, channel_removeowner_v1
from src.dm import dm_create_v1, dm_list_v1, dm_remove_v1, dm_details_v1, dm_leave_v1, dm_messages_v1
from src.other import clear_v1
from src.message import message_send_v1, message_edit_v1, message_remove_v1, message_senddm_v1,  message_sendlater_v1, message_sendlaterdm_v1, message_share_v1, message_react_v1, message_unreact_v1, message_pin_v1, message_unpin_v1
from src.user import users_all_v1, user_profile_v1, user_profile_setname_v1, user_profile_setemail_v1, user_profile_sethandle_v1, user_stats_v1, users_stats_v1
from src.admin import admin_user_remove_v1, admin_userpermission_change_v1
from src.standup import standup_start, standup_send, standup_active
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

# NO NEED TO MODIFY ABOVE THIS POINT, EXCEPT IMPORTS

# Persistence data gathering
datas = []
try:
    datas = pickle.load(open("datastore.p", "rb"))
    storage = data_store.get()
    storage['users'] = datas['users']
    storage['channels'] = datas['channels']
    storage['no_users'] = datas['no_users']
    storage['dms'] = datas['dms']
    storage['session_id'] = datas['session_id']
    storage['removed_users'] = datas['removed_users']
    storage['workspace_stats'] = datas['workspace_stats']
    data_store.set(storage)
except Exception:
    pass


def save():
    '''For persistence, saves current data_store into datastore.p'''
    storage = data_store.get()
    data = {'users': storage['users'], 'channels': storage['channels'], 'no_users': storage['no_users'],
            'dms': storage['dms'], 'session_id': storage['session_id'], 'removed_users': storage['removed_users'],
            'workspace_stats': storage['workspace_stats']}
    with open('datastore.p', 'wb+') as FILE:
        pickle.dump(data, FILE)


# For email for password reset
APP.config['MAIL_SERVER'] = 'smtp.gmail.com'
APP.config['MAIL_PORT'] = 465
APP.config['MAIL_USERNAME'] = 'comp1531f11b.ant@gmail.com'
APP.config['MAIL_PASSWORD'] = 'Comppass123'
APP.config['MAIL_USE_TLS'] = False
APP.config['MAIL_USE_SSL'] = True
mail = Mail(APP)

# AUTH FUNCTION WRAPPERS


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

    details = auth_register_v1(
        data['email'], data['password'], data['name_first'], data['name_last'])
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


@APP.route('/auth/passwordreset/request/v1', methods=['POST'])
def resetrequest():
    data = request.get_json()
    code = str(auth_passwordreset_request_v1(data['email']))
    if code != None:
        msg = Message(
            "Password reset", sender='comp1531f11b.ant@gmail.com', recipients=[data['email']])
        msg.body = f"Hi, your code is: {code}"
        mail.send(msg)
    save()
    return dumps({})


@APP.route('/auth/passwordreset/reset/v1', methods=['POST'])
def resetpass():
    data = request.get_json()
    auth_passwordreset_reset_v1(data['reset_code'], data['new_password'])
    save()
    return dumps({})

# CHANNEL FUNCTION WRAPPERS
@APP.route('/channels/create/v2', methods=['POST'])
def create():
    data = request.get_json()
    details = channels_create_v1(
        data['token'], data['name'], data['is_public'])
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

@APP.route("/channel/leave/v1", methods=['POST'])
def leave():
    data = request.get_json()
    channel_leave_v1(data['token'], data['channel_id'])
    save()
    return dumps({})

@APP.route("/channel/addowner/v1", methods=['POST'])
def addowner():
    data = request.get_json()
    channel_addowner_v1(data['token'], data['channel_id'], data['u_id'])
    save()
    return dumps({})

@APP.route("/channel/removeowner/v1", methods=['POST'])
def removeowner():
    data = request.get_json()
    channel_removeowner_v1(data['token'], data['channel_id'], data['u_id'])
    save()
    return dumps({})

# DM FUNCTION WRAPPERS
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

@APP.route('/dm/leave/v1', methods=['POST'])
def dm_leave():
    data = request.get_json()
    dm_leave_v1(data['token'], data['dm_id'])
    save()
    return dumps({})

@APP.route("/dm/messages/v1", methods=['GET'])
def dm_messages():
    return dumps(dm_messages_v1(request.args.get('token'), request.args.get('dm_id'), request.args.get('start')))

# MESSAGES FUNCTION WRAPPERS
@APP.route("/message/send/v1", methods=['POST'])
def send_message():
    data = request.get_json()
    details = message_send_v1(
        data['token'], data['channel_id'], data['message'])
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

@APP.route("/message/react/v1", methods=['POST'])
def react():
    data = request.get_json()
    return dumps(message_react_v1(data['token'], data['message_id'], data['react_id']))

@APP.route("/message/unreact/v1", methods=['POST'])
def unreact():
    data = request.get_json()
    return dumps(message_unreact_v1(data['token'], data['message_id'], data['react_id']))

@APP.route("/message/sendlater/v1", methods=['POST'])
def sendlater():
    data = request.get_json()
    details = message_sendlater_v1(
        data['token'], data['channel_id'], data['message'], data['time_sent'])
    save()
    return dumps({
        'message_id': details['message_id']
    })

@APP.route("/message/pin/v1", methods=['POST'])
def pin():
    data = request.get_json()
    return dumps(message_pin_v1(data['token'], data['message_id']))

@APP.route("/message/unpin/v1", methods=['POST'])
def unpin():
    data = request.get_json()
    return dumps(message_unpin_v1(data['token'], data['message_id']))

@APP.route("/message/sendlaterdm/v1", methods=['POST'])
def sendlaterdm():
    data = request.get_json()
    details = message_sendlaterdm_v1(
        data['token'], data['dm_id'], data['message'], data['time_sent'])
    save()
    return dumps({
        'message_id': details['message_id']
    })


@APP.route("/message/share/v1", methods=['POST'])
def share():
    data = request.get_json()
    details = message_share_v1(
        data['token'], data['og_message_id'], data['message'], data['channel_id'], data['dm_id'])
    save()
    return dumps({
        'shared_message_id': details['shared_message_id']
    })


@APP.route("/clear/v1", methods=['DELETE'])
def clear():
    clear_v1()
    save()
    return dumps({})



# USER FUNCTION WRAPPERS
@APP.route('/users/all/v1', methods=['GET'])
def users_all():
    users = users_all_v1(request.args.get("token"))['users']
    return dumps({
        'users': users
    })


@APP.route("/user/profile/v1", methods=["GET"])
def user_profile():
    user = user_profile_v1(request.args.get(
        "token"), request.args.get("u_id"))['user']
    return dumps({
        'user': user
    })


@APP.route("/user/profile/setname/v1", methods=["PUT"])
def user_setname():
    data = request.get_json()
    user_profile_setname_v1(
        data['token'], data['name_first'], data['name_last'])
    save()
    return dumps({})


@APP.route("/user/profile/setemail/v1", methods=["PUT"])
def user_setemail():
    data = request.get_json()
    user_profile_setemail_v1(data['token'], data['email'])
    save()
    return dumps({})


@APP.route("/user/profile/sethandle/v1", methods=["PUT"])
def user_sethandle():
    data = request.get_json()
    user_profile_sethandle_v1(data['token'], data['handle_str'])
    save()
    return dumps({})


@APP.route("/user/stats/v1", methods=["GET"])
def user_stats():
    return dumps({
        'user_stats': user_stats_v1(request.args.get("token"))
    })


@APP.route("/users/stats/v1", methods=["GET"])
def users_stats():
    return dumps({
        'workspace_stats': users_stats_v1(request.args.get("token"))
    })

<<<<<<< HEAD
#ADMIN WRAPPER FUNCTIONS
=======

# ADMIN WRAPPER FUNCTIONS
>>>>>>> 95a90e37190c22b770cc982af242bda73b856af6
@APP.route('/admin/user/remove/v1', methods=['DELETE'])
def admin_remove():
    data = request.get_json()
    admin_user_remove_v1(data['token'], data['u_id'])
    save()
    return dumps({})


@APP.route('/admin/userpermission/change/v1', methods=['POST'])
def admin_perm_change():
    data = request.get_json()
    admin_userpermission_change_v1(
        data['token'], data['u_id'], data['permission_id'])
    save()
    return dumps({})

# STANDUP FUNCTION WRAPPERS


@APP.route('/standup/start/v1', methods=['POST'])
def start_standup():
    data = request.get_json()
    time_finish = standup_start(data['token'], data['channel_id'], data['length'])[
        'time_finish']
    save()
    return dumps({'time_finish': time_finish})


@APP.route('/standup/active/v1', methods=['GET'])
def active_standup():
    standup_details = standup_active(request.args.get(
        'token'), request.args.get('channel_id'))
    return dumps({'is_active': standup_details['is_active'], 'time_finish': standup_details['time_finish']})


@APP.route('/standup/send/v1', methods=['POST'])
def send_standup():
    data = request.get_json()
    standup_send(data['token'], data['channel_id'], data['message'])
    return dumps({})

#CLEAR FUNCTION WRAPPER
@APP.route("/clear/v1", methods=['DELETE'])
def clear():
    clear_v1()
    save()
    return dumps({})
# NO NEED TO MODIFY BELOW THIS POINT

if __name__ == "__main__":
    signal.signal(signal.SIGINT, quit_gracefully)  # For coverage
    APP.run(port=config.port)  # Do not edit this port
