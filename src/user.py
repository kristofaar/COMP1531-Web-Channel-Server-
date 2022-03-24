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
