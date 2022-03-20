from multiprocessing import dummy
from src.data_store import data_store
from src.other import generate_new_session_id, check_if_valid, read_token
from src.error import InputError, AccessError
import re, hashlib, jwt

SECRET = 'heheHAHA111'

def auth_login_v1(email, password):
    '''Given a correct email and associated password returns the user's id.

    Arguments:
        email (String)       - The user's email, must be unique.
        password (String)    - Password must be greater or equal to 6 characters long.

    Exceptions:
        InputError  - Occurs when: 
            -email entered does not belong to a user
            -password is not correct
    Return Value:
        Returns auth_user_id always.
    '''

    storage = data_store.get()

    #sentinel variable 
    login_error = False
    u_id = 0
    for user in storage['users']:
        if user['email'] == email and user['password'] == hashlib.sha256(password.encode()).hexdigest():
            login_error = True
            u_id = user['id']
            session_id = generate_new_session_id()
            user['session_list'].append(session_id)
            print(session_id)
    
    #errors
    if not login_error:
        raise InputError("Email/Password Does Not Exist")
    
    return {
        'token': jwt.encode({'id': u_id, 'session_id': session_id}, SECRET, algorithm='HS256'),
        'auth_user_id': u_id,
    }



def auth_register_v1(email, password, name_first, name_last):
    '''Registers a user storing their email, password, name_first, name_last. Creates a unique id and handle which is also stored.
    That user can now interact with with other functions.

    Arguments:
        email (String)         - The user's email, must be unique.
        password (String)      - Password must be greater or equal to 6 characters long.
        name_first (String)    - Must be between 1 and 50 characters.
        name_last (String)     - Must be between 1 and 50 characters.   

    Exceptions:
        InputError  - Occurs when: 
            -email entered is not a valid email
            -email address is already being used by another user
            -length of password is less than 6 characters
            -length of name_first is not between 1 and 50 characters inclusive
            -length of name_last is not between 1 and 50 characters inclusive

    Return Value:
        Returns auth_user_id always.
    '''
    
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
    handle = re.sub(r'[^a-zA-Z0-9]', '', name_first).lower() + re.sub(r'[^a-zA-Z0-9]', '', name_last).lower()
    handle = handle[:20]
    #-1 would be the case where there are no numbers at the end of the handle
    num_of_same_handle = -1
    while num_of_same_handle + 1 < len(storage['users']):
        same_handle = False
        temp_handle = handle if num_of_same_handle == -1 else handle + str(num_of_same_handle)
        for user in storage['users']:
            if user['handle'] == temp_handle:
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
    
    is_first = False
    if storage['no_users']:
        storage['no_users'] = False
        is_first = True
    
    session_id = generate_new_session_id()

    storage['users'].append({'id': new_id, 'email': email, 'name_first': name_first, 'name_last': name_last, 'handle': handle, 
                            'channels' : [], 'global_owner': is_first, 'password': hashlib.sha256(password.encode()).hexdigest(), 'session_list': [session_id]})
    
    data_store.set(storage)
    return {
        'token': jwt.encode({'id': new_id, 'session_id': session_id}, SECRET, algorithm='HS256'),
        'auth_user_id': new_id,
    }

def auth_logout_v1(token):
    '''Invalidates a token.

    Arguments:
        token (String)         - A user's session token. 

    Exceptions:
        AccessError  - Occurs when: 
            -Token is invalid

    Return Value:
        Nothing.
    '''
    storage = data_store.get()
    if not check_if_valid(token):
        raise AccessError("Invalid Token")
    details = jwt.decode(token, SECRET, algorithms=["HS256"])
    for user in storage['users']:
        if (details['session_id'] in user['session_list']):
            user['session_list'].remove(details['session_id'])
    data_store.set(storage)
    return {}
