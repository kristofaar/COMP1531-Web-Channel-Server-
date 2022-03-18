from src.data_store import data_store
import re, hashlib, jwt
SECRET = 'heheHAHA111'

def clear_v1():
    store = data_store.get()
    store['users'] = []
    store['passwords'] = []
    store['channels'] = []
    store['no_users'] = True
    data_store.set(store)
    return {
    }

""" Token functions """

def create_token(auth_user_id):
    '''Create a unique token for a user'''
    token = jwt.encode({'id': auth_user_id}, SECRET, algorithm='HS256')
    return token

def read_token(token):
    return jwt.decode(token, SECRET, algorithms=["HS256"])['id']