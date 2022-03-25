from src.data_store import data_store
from src.error import InputError
from src.error import AccessError
from src.other import read_token, check_if_valid
import hashlib, jwt

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
        InputError  - Occurs when u_id does not refer to a valid user.

    Return Value:
        Returns information about a user's user_id, email, first name, last name, and handle when given a valid user u_id.
    '''

    storage = data_store.get()
    users = storage["users"]

    for user in users:
        if u_id == user["u_id"] and read_token(token) is not None:
            return {
                "u_id": user["id"], 
                "email": user["email"], 
                "name_first": user["name_first"],
                "name_last": user["name_last"],
                "handle_str": user["handle"]})
            }

    # If user not in users:
    raise InputError("Invalid user ID")
    return {}
