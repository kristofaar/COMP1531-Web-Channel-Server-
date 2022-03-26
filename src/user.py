from src.data_store import data_store
from src.error import InputError
from src.error import AccessError
from src.other import read_token, check_if_valid
import re
import hashlib, jwt

MIN_NAME_LENGTH = 1
MAX_NAME_LENGTH = 50
MIN_HANDLE_LENGTH = 3
MAX_HANDLE_LENGTH = 20

def users_all_v1(token):
    '''
    Returns a list of all users and their associated details

    Arguments:
        token  (string)    - passes in the unique user token of whoever ran the funtion

    Exceptions:
        AccessError  - Occurs when invalid token was passed in

    Return Value:
        Returns list of users with u_id, email, name_first, name_last, handle_str
    '''
    #staging variables
    storage = data_store.get()
    if not check_if_valid(token):
        raise AccessError(description="Invalid token")
    users = storage['users']
    
    #append user data dictionary to list
    output = []
    for user in users:
        output.append({"u_id": user["id"], 
                       "email": user["email"], 
                       "name_first": user["name_first"],
                       "name_last": user["name_last"],
                       "handle_str": user["handle"]})
    return {"users": output}

def user_profile_v1(token, u_id):
    '''
    For a valid user, returns associated details about the user.

    Arguments:
        token (str) - The user's session token.
        u_id (int)  - The user's user ID.

    Exceptions:
        AccessError - Occurs when token does not refer to a valid session.
        InputError  - Occurs when u_id does not refer to a valid user.

    Return Value:
        Returns information about a user's user_id, email, first name, last name, and handle when given a valid user u_id.
    '''

    store = data_store.get()
    users = store["users"]
    removed_users = store["removed_users"]

    # Check valid token
    if not check_if_valid(token):
        raise AccessError(description="Invalid token")

    for user in users:
        if user["id"] == int(u_id):
            return {'user': 
                {
                "u_id": user["id"], 
                "email": user["email"], 
                "name_first": user["name_first"],
                "name_last": user["name_last"],
                "handle_str": user["handle"]
                }
            }

    for removed_user in removed_users:
        if removed_user["id"] == int(u_id):
            return {'user': 
                {
                "u_id": removed_user["id"], 
                "email": removed_user["email"], 
                "name_first": "Removed",
                "name_last": "user",
                "handle_str": removed_user["handle"]
                }
            }

    # Check valid user ID
    raise InputError(description="Invalid user ID")

def user_profile_setname_v1(token, name_first, name_last):
    '''
    Update the authorised user's first and last name.

    Arguments:
        token (str)       - The user's session token.
        name_first (str)  - The user's first name.
        name_last (str)   - The user's last name.

    Exceptions:
        AccessError - Occurs when token does not refer to a valid session.
        InputError  - Occurs when length of name_first is not between 1 and 50 characters inclusive.
        InputError  - Occurs when length of name_last is not between 1 and 50 characters inclusive.

    Return Value:
        Returns nothing.
    '''

    store = data_store.get()
    users = store["users"]

    # Check valid token
    if not check_if_valid(token):
        raise AccessError(description="Invalid token")

    # Check valid first and last name inputs
    if not MIN_NAME_LENGTH <= len(name_first) <= MAX_NAME_LENGTH:
        raise InputError(description="Invalid first name length")
    if not MIN_NAME_LENGTH <= len(name_last) <= MAX_NAME_LENGTH:
        raise InputError(description="Invalid last name length")

    # Get user ID from token
    u_id = read_token(token)

    for user in users:
        if user["id"] == u_id:
            user["name_first"] = name_first
            user["name_last"] = name_last
    data_store.set(store)
    return {}

def user_profile_setemail_v1(token, email):
    '''
    Update the authorised user's email address.

    Arguments:
        token (str)  - The user's session token.
        email (str)  - The user's email.

    Exceptions:
        AccessError - Occurs when token does not refer to a valid session.
        InputError  - Occurs when email entered is not in correct format (section 6.4).
        InputError  - Occurs when email address is already being used by another user.

    Return Value:
        Returns nothing.
    '''

    store = data_store.get()
    users = store["users"]

    # Check valid token
    if not check_if_valid(token):
        raise AccessError(description="Invalid token")

    # Check valid email
    if not re.search(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$', email):
        raise InputError(description="Invalid email")

    # Check duplicate email
    for user in users:
        if user["email"] == email:
            raise InputError(description="User email already exists")

    # Get user ID from token
    u_id = read_token(token)

    for user in users:
        if user["id"] == u_id:
            user["email"] = email
    data_store.set(store)
    return {}

def user_profile_sethandle_v1(token, handle_str):
    '''
    Update the authorised user's handle (i.e. display name).

    Arguments:
        token (str)       - The user's session token.
        handle_str (str)  - The user's display name.

    Exceptions:
        AccessError - Occurs when token does not refer to a valid session.
        InputError  - Occurs when length of handle_str is not between 3 and 20 characters inclusive.
        InputError  - Occurs when handle_str contains characters that are not alphanumeric.
        InputError  - Occurs when the handle is already being used by another user.

    Return Value:
        Returns nothing.
    '''

    store = data_store.get()
    users = store["users"]

    # Check valid token
    if not check_if_valid(token):
        raise AccessError(description="Invalid token")

    # Check valid handle length
    if not MIN_HANDLE_LENGTH <= len(handle_str) <= MAX_HANDLE_LENGTH:
        raise InputError(description="Invalid handle length")

    # Check valid handle input
    if not handle_str.isalnum():
        raise InputError(description="Invalid handle input")
    
    # Check duplicate handle
    for user in users:
        if user["handle"] == handle_str:
            raise InputError(description="User handle already exists")

    # Get user ID from token
    u_id = read_token(token)

    for user in users:
        if user["id"] == u_id:
            user["handle"] = handle_str
    data_store.set(store)
    return {}
