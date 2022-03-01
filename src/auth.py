from multiprocessing import dummy
from src.data_store import data_store
from src.error import InputError
import re


def auth_login_v1(email, password):
    storage = data_store.get()

    #sentinel variable I don't know how to do better
    email_exists = False
    u_id = 0

    for i, user in enumerate(storage['users']):
        if user['email'] == email:
            email_exists = True
            u_id = user['id']
    
    #errors
    if not email_exists:
        raise InputError("Email Does Not Exist")
  
    for user in storage['passwords']:
        if user['id'] == u_id and user['password'] != password:
            raise InputError('Password does not match')

    return {
        'auth_user_id': u_id,
    }

def auth_register_v1(email, password, name_first, name_last):
    storage = data_store.get()

    #using regular expressions to check if email is valid
    regex_email = '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}$'
    # \\ is used as \ is an escape character and produces a warning when used on its own
    if not re.fullmatch(regex_email, email):
        raise InputError("Invalid Email")

    #errors
    for user in storage['users']:
        if user['email'] == email:
            raise InputError("Email Duplicate")

    if len(password) < 6:
        raise InputError("Invalid Password")
    
    if not (len(name_first) <= 50 and len(name_first) >= 1):
        raise InputError("Invalid First Name") 

    if not (len(name_last) <= 50 and len(name_last) >= 1):
        raise InputError("Invalid Last Name") 

    #handle creation
    #regular expression to get rid of all non alphanumeric characters
    handle = re.sub(r'\W+', '', name_first).lower() + re.sub(r'\W+', '', name_last).lower()
    handle = handle[:20]
    #-1 would be the case where there are no numbers at the end of the handle
    num_of_same_handle = -1
    while num_of_same_handle + 1 < len(storage['users']):
        same_handle = False
        for user in storage['users']:
            if user['handle'] == handle or user['handle'] == handle + str(num_of_same_handle):
                same_handle = True
                num_of_same_handle += 1
        if not same_handle:
            break
    
    #if not unique add the iteration of the handle to the end of the handle
    if num_of_same_handle >= 0:
        handle += str(num_of_same_handle)
    
    #id creation is based off the last person's id
    new_id = 1
    if len(storage['users']):
        new_id = storage['users'][len(storage['users']) - 1]['id'] + 1

    storage['users'].append({'id': new_id, 'email': email, 'name_first': name_first, 'name_last': name_last, 'handle': handle, 'channels' : []})
    storage['passwords'].append({'id': new_id, 'password': password})
    

    data_store.set(storage)
    return {
        'auth_user_id': new_id,
    }
