from src.data_store import data_store
from src.error import InputError
from src.error import AccessError
from src.other import create_token, read_token
import hashlib, jwt

def dm_create_v1(token, u_ids):
    '''
    Creates a new dm between the current user and the users inputed

    Arguments:
        token  (string)    - passes in the unique user token of whoever ran the funtion
        u_ids  (list)      - a list of user ids which can be used to indentify the users

    Exceptions:
        InputError  - Occurs when any u_id in u_ids does not refer to a valid user
        InputError  - Occurs when there are duplicate 'u_id's in u_ids

    Return Value:
        Returns dm_id on sucessful dm creation
    '''
    pass

def dm_list_v1():
    pass

def dm_remove_v1():
    pass

def dm_details_v1(token, dm_id):
    '''
returns name of dm and members of associated dm

Arguments:
    token        (str)    - passes in the unique token of whoever ran the funtion
    dm_id        (int)    - passes in the unique dm id of the dm we are enquiring about

Exceptions:
    InputError  - Occurs when dm_id does not refer to a valid dm
    AccessError - Occurs when dm_id is valid and the authorised user is not a member of the dm

Return Value:
    Returns name of the dm, and the members of the dm
    '''

    #staging variables
    storage = data_store.get()
    auth_user_id = read_token(token)

    dms = storage['dms']
    uesrs = storage['users']

    # Check auth_user_id is registered 
    check_auth_user_id = next((user for user in users if auth_user_id == user['id']), None)
    if check_auth_user_id == None:
        raise AccessError("Invalid User")

    #search through dms by id until id is matched
    dm = next((dm for dm in dms if dm_id == dm['dm']['dm_id']), None)
    if dm == None:
        raise InputError("Invalid dm id")

    #check if auth_user_id is a member of the dm queried
    if auth_user_id not in dm['members']:
        raise AccessError("Unauthorised User: User is not in dm")

    #generate lists of dm members
    dm_members = []
    for member in dm['member']:
        curr_user = next((user for user in users if member == user['id']), None)
        members.append(user)

    return {"name": dm_name, "members": dm_members}

def dm_leave_v1():
    pass

def dm_messages_v1():
    pass
