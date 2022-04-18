from src.data_store import data_store
from src.error import AccessError, InputError
from datetime import timezone
import datetime
import re, hashlib, jwt
SECRET = 'heheHAHA111'

def clear_v1():
    '''Sets data_store to a clean state'''
    store = data_store.get()
    store['users'] = []
    store['channels'] = []
    store['dms'] = []
    store['no_users'] = True
    store['session_id'] = 0
    store['removed_users'] = []
    store['workspace_stats'] = {
        'channels_exist': [{
            'num_channels_exist': 0,
            'time_stamp': get_time()
        }],
        'dms_exist': [{
            'num_dms_exist': 0,
            'time_stamp': get_time()
        }],
        'messages_exist': [{
            'num_messages_exist': 0,
            'time_stamp': get_time()
        }],
        'utilization_rate': 0
    }
    data_store.set(store)
    return {
    }

"""Owner perms checker"""
def owner_perms(u_id, ch_id):
    store = data_store.get()
    ch = None
    for channel in store['channels']:
        if ch_id == channel['channel_id_and_name']['channel_id']:
            ch = channel
    user = None
    for usa in store['users']:
        if usa['id'] == u_id:
            user = usa
    is_owner = None
    for owner in ch['owner']:
        if owner == u_id:
            is_owner = owner
    if is_owner != None or user['global_owner']:
        return True
    else:
        return False
    

"""Session Id functions"""
def generate_new_session_id():
    store = data_store.get()
    store['session_id'] += 1
    data_store.set(store)
    return store['session_id']

#checks if the session id is valid, assumes that u_id exists
def check_if_valid(token):
    store = data_store.get()
    try:
        details = jwt.decode(token, SECRET, algorithms=["HS256"])
    except:
        return False
    if not ("id" in details.keys() and "session_id" in details.keys() and len(details.keys()) == 2):
        return False
    user = None
    for usa in store['users']:
        if details['id'] == usa['id']:
            user = usa
    if user == None:
        return False
    id = None
    for i in user['session_list']:
        if i == details['session_id']:
            id = i
    if id != None:
        return True
    else:
        return False

def read_token(token):
    return jwt.decode(token, SECRET, algorithms=["HS256"])['id']

#gets current timestamp
def get_time():
    # Getting the current date
    # and time
    datet = datetime.datetime.now(timezone.utc)

    time = datet.replace(tzinfo=timezone.utc)
    time_sent = time.timestamp()
    return round(time_sent)

#notifications, channelinvite, messagesend, messageedit, dmcreate, senddm, messageshare, react, sendlatermessage/dm
def notifications_get_v1(token):
    '''Return the user's most recent 20 notifications, ordered from most recent to least recent.

    Arguments:
        token (String)         - The token of auth user whose notifications are to be displayed.

    Exceptions:
        AccessError  - Occurs when: 
            -Token is invalid

    Return Value:
        Returns notifications, dict with shape {channel_id, dm_id, notification_message}.
    '''
    if not check_if_valid(token):
        raise AccessError(description="Invalid Token")

    # staging variables
    storage = data_store.get()
    auth_user_id = read_token(token)
    users = storage['users']
    user = None
    for usa in users:
        if auth_user_id == usa['id']:
            user = usa
    return {
        'notifications': user['notifications']
    }

#message tagging helper
def message_tags_update(message, message_id, channel_id, dm_id, name, tagger):
    '''Updates user's notifications if tagged in a message'''
    storage = data_store.get()
    users = storage['users']
    channels = storage['channels']
    dms = storage['dms']
    channel = None

    if channel_id != -1 and dm_id != -1:
        raise InputError(description='neither channel_id nor dm_id are -1')
    elif dm_id == -1 and channel_id != -1:
        # search through channels by id until id is matched
        channel = next((channel for channel in channels if int(
            channel_id) == channel['channel_id_and_name']['channel_id']), None)
        if channel == None:
            raise InputError(description="Invalid Channel Id")
    elif channel_id == -1 and dm_id != -1:
        channel = next((channel for channel in dms if int(
            dm_id) == channel['dm_id']), None)
        if channel == None:
            raise InputError(description="Invalid dm Id")
    else:
        raise InputError(description="Both channel and dm id are invalid")
    i = 0
    reading = False
    handle = ''
    for i in range(len(message)):
        if reading:
            if not message[i].isalnum():
                reading = False
                for user in users:
                    if handle == user['handle'] and user['id'] in channel['members'] and not message_id in user['tagged_msg']:
                        user['tagged_msg'].append(message_id)
                        user['notifications'].insert(0, {
                            'channel_id': channel_id,
                            'dm_id': dm_id,
                            'notification_message': f"{tagger} tagged you in {name}: {message[:20]}"
                        })
                handle = ''
            else:
                handle += message[i]
        if message[i] == '@':
            reading = True
            continue
    if reading:
        for user in users:
            if handle == user['handle'] and user['id'] in channel['members'] and not message_id in user['tagged_msg']:
                user['tagged_msg'].append(message_id)
                user['notifications'].insert(0, {
                    'channel_id': channel_id,
                    'dm_id': dm_id,
                    'notification_message': f"{tagger} tagged you in {name}: {message[:20]}"
                })

        
    data_store.set(storage)

def standup_sendall(token, channel_id, message):
    '''
    Sends a standup message from the authorised user to the channel specified by channel_id. 
    Note: Each message should have its own unique ID, i.e. no messages should share an ID with another message, 
    even if that other message is in a different channel.

    Arguments:
        token (String)        - passes in the unique session token of whoever ran the funtion
        channel_id   (int)    - passes in the unique channel id of the channel we are enquiring about
        message (String)      - message being sent

    Exceptions:
        InputError when:
            channel_id does not refer to a valid channel
            length of message is less than 1 or over 1000 characters
        AccessError when:
            token is invalid
            channel_id is valid and the authorised user is not a member of the channel

    Return Value:
        Returns unique message_id.
    '''

    if not check_if_valid(token):
        raise AccessError(description="Invalid Token")

    # staging variables
    storage = data_store.get()
    auth_user_id = read_token(token)

    channels = storage['channels']

    # search through channels by id until id is matched
    ch = None
    for channel in channels:
        if int(channel_id) == channel['channel_id_and_name']['channel_id']:
            ch = channel
    if ch == None:
        raise InputError(description="Invalid Channel Id")

    # check if auth_user_id is a member of the channel queried
    if auth_user_id not in ch['members']:
        raise AccessError(
            description="Unauthorised User: User is not in channel")

    if not 1 <= len(message) <= 1000:
        raise InputError(description="Invalid message length")

    time_sent = get_time()

    # using session id generator to create unique message id
    message_id = generate_new_session_id()

    # inserting message
    message_dict = {
        'message_id': message_id,
        'u_id': auth_user_id,
        'message': message,
        'time_sent': time_sent,
        'reacts': [{'react_id': 1, 'u_ids': []}],
        'pinned': False,
    }
    ch['messages'].insert(0, message_dict)

    # stats
    auth_user = None
    for user in storage['users']:
        if user['id'] == auth_user_id:
            auth_user = user
            user['user_stats']['messages_sent'].append({
                'num_messages_sent': user['user_stats']['messages_sent'][len(user['user_stats']['messages_sent']) - 1]['num_messages_sent'] + 1,
                'time_stamp': get_time()
            })
    storage['workspace_stats']['messages_exist'].append({
        'num_messages_exist': storage['workspace_stats']['messages_exist'][len(storage['workspace_stats']['messages_exist']) - 1]['num_messages_exist'] + 1,
        'time_stamp': get_time()
    })
    
    data_store.set(storage)
    return {
        'message_id': message_id
    }
