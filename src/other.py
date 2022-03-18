from src.data_store import data_store
import re, hashlib, jwt
SECRET = 'heheHAHA111'

def clear_v1():
    store = data_store.get()
    store['users'] = []
    store['channels'] = []
    store['no_users'] = True
    store['session_id'] = 0
    data_store.set(store)
    return {
    }

"""Session Id functions"""
def generate_new_session_id():
    store = data_store.get()
    store['session_id'] += 1
    data_store.set(store)
    return store['session_id']

#checks if the session id is valid, assumes that u_id exists
def check_if_valid_session(token):
    store = data_store.get()
    details = jwt.decode(token, SECRET, algorithms=["HS256"])
    user = next((user for user in store['user'] if details['id'] == user['id']), None)
    id = next ((id for id in user['session_id'] if id == details['session_id']), None)
    if id != None:
        return True
    else:
        return False

""" Token functions """

def create_token(auth_user_id):
    '''Create a unique token for a user'''
    token = jwt.encode({'id': auth_user_id}, SECRET, algorithm='HS256')
    return token

def read_token(token):
    return jwt.decode(token, SECRET, algorithms=["HS256"])['id']