from src.data_store import data_store
from src.error import InputError
from src.error import AccessError
from src.other import read_token, check_if_valid
import hashlib, jwt

MIN_NAME_LENGTH = 1
MAX_NAME_LENGTH = 50

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
        raise AccessError("Invalid token")
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

    storage = data_store.get()
    users = storage["users"]

    # Check valid token
    if not check_if_valid(token):
        raise AccessError(description="Invalid token")

    user_exists = False
    for user in users:
        if u_id == user["u_id"]:
            user_exists = True
            return {
                "u_id": user["id"], 
                "email": user["email"], 
                "name_first": user["name_first"],
                "name_last": user["name_last"],
                "handle_str": user["handle"]})
            }

    # Check valid user ID
    if not user_exists:
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

    storage = data_store.get()
    users = storage["users"]
    channels = storage["channels"]

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
        if u_id == user["u_id"]:
            user["name_first"] = name_first
            user["name_last"] = name_last

    return {}
