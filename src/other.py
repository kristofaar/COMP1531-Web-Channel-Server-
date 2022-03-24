from src.data_store import data_store
import re, hashlib, jwt
SECRET = 'heheHAHA111'

def clear_v1():
    store = data_store.get()
    store['users'] = []
    store['channels'] = []
    store['dms'] = []
    store['no_users'] = True
    store['session_id'] = 0
    data_store.set(store)
    return {
    }

"""Owner perms checker"""
def owner_perms(u_id, ch_id):
    store = data_store.get()
    ch = next((channel for channel in store['channels'] if ch_id == channel['channel_id_and_name']['channel_id']), None)
    if not ch:
        return False
    user = next((user for user in store['users'] if user['id'] == u_id), None)
    if not user:
        return False
    is_owner = next((owner for owner in ch['owner'] if owner == u_id), None)
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

#checks if the token is valid 
def check_if_valid(token):
    store = data_store.get()
    try:
        details = jwt.decode(token, SECRET, algorithms=["HS256"])
    except:
        return False
    if not ("id" in details.keys() and "session_id" in details.keys() and len(details.keys()) == 2):
        return False
    user = next((user for user in store['users'] if details['id'] == user['id']), None)
    if user == None:
        return False
    id = next ((id for id in user['session_list'] if id == details['session_id']), None)
    if id != None:
        return True
    else:
        return False

""" Token functions """
# add a try except as if the token is invalid it might break the whole code
def create_token(auth_user_id):
    '''Create a unique token for a user'''
    token = jwt.encode({'id': auth_user_id}, SECRET, algorithm='HS256')
    return token

def read_token(token):
    return jwt.decode(token, SECRET, algorithms=["HS256"])['id']

