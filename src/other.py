from src.data_store import data_store
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
    return time_sent