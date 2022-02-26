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
            u_id = i
    
    #errors
    if not email_exists:
        raise InputError("Email Does Not Exist")
  
    if password != storage['passwords'][u_id]:
        print(storage['passwords'])
        raise InputError("Incorrect Password")

    #the auth_user_id starts from 1 not zero
    return {
        'auth_user_id': u_id + 1,
    }

def auth_register_v1(email, password, name_first, name_last):
    storage = data_store.get()

    #using regular expressions to check if email is valid
    regex_email = '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'
    if not re.fullmatch(regex_email, email):
        raise InputError("Invalid Email")

    #each user will have the following objects in this order: id, email, name_first, name_last, handle
    for user in storage['users']:
        if user['email'] == email:
            raise InputError("Email Duplicate")

    if len(password) < 6:
        raise InputError("Invalid Password")
    
    if not (len(name_first) <= 50 and len(name_first) >= 1):
        raise InputError("Invalid First Name") 

    if not (len(name_last) <= 50 and len(name_last) >= 1):
        raise InputError("Invalid Last Name") 

    #regular expression to get rid of all non alphanumeric characters
    handle = re.sub(r'\W+', '', name_first).lower() + re.sub(r'\W+', '', name_last).lower()
    handle = handle[:20]

    num_of_same_handle = 0
    for user in storage['users']:
        if user['handle'][:20] == handle:
            num_of_same_handle += 1
    
    #if not unique add the iteration of the handle to the end of the handle
    if num_of_same_handle:
        handle += str(num_of_same_handle - 1)
    
    new_id = len(storage['users']) + 1

    storage['users'].append({'id': new_id, 'email': email, 'name_first': name_first, 'name_last': name_last, 'handle': handle})
    storage['passwords'].append(password)
    data_store.set(storage)
    return {
        'auth_user_id': new_id,
    }
