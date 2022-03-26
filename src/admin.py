from multiprocessing import dummy
from src import auth
from src.data_store import data_store
from src.error import InputError, AccessError
from src.other import read_token, check_if_valid

OWNER = 1
MEMBER = 2

def admin_user_remove_v1(token, u_id):
    '''Given a user by their u_id, remove them from the Seams. 

    Arguments:
        token (String)          - User's token.
        u_id (Integer)          - User being removed. 

    Exceptions:
        InputError  - Occurs when: 
            -u_id does not refer to a valid user
            -u_id refers to a user who is the only global owner

        AccessError - Occurs when:
            -the authorised user is not a global owner

    Return Value:
        Nothing.
    '''
    # check token
    if not check_if_valid(token):
        raise AccessError("Invalid Token")

    # staging variables
    storage = data_store.get()
    auth_user_id = read_token(token)
    users = storage['users']
    channels = storage['channels']

    # check token user is global owner
    auth_user = next(
        (user for user in users if auth_user_id == user['id']), None)
    if not auth_user['global_owner']:
        raise AccessError(description='Authorised user is not a global owner')

    # check u_id valid
    u_user = next((user for user in users if int(u_id) == user['id']), None)
    if u_user == None:
        raise InputError(description="Invalid User Id")

    # check u_id the only global owner
    other_owner = next((user for user in users if user['global_owner'] and user['id'] != auth_user_id), None)
        
    if int(u_id) == auth_user_id and not other_owner:
        raise InputError(description='User is the only global owner')

    # remove user from channels
    for channel in channels:
        if int(u_id) in channel['members']:
            channel['members'].remove(int(u_id))
        if int(u_id) in channel['owner']:
            channel['owner'].remove(int(u_id))
        for message in channel['messages']:
            if message['u_id'] == int(u_id):
                message['message'] = "Removed user"

    # remove user from dms
    for dm in storage['dms']:
        if int(u_id) in dm['owner']:
            dm['owner'].remove(int(u_id))
        if int(u_id) in dm['members']:
            dm['members'].remove(int(u_id))
        for message in dm['messages']:
            if message['u_id'] == int(u_id):
                message['message'] = "Removed user"
    
    #remove user from users
    users.remove(u_user)

    # move user to removed users list
    storage['removed_users'].append(u_user)

    data_store.set(storage)
    return {}

def admin_userpermission_change_v1(token, u_id, permission_id):
    '''Given a user by their u_id, remove them from the Seams. 

    Arguments:
        token (String)          - Admin token.
        u_id (Integer)          - User being changed.
        permission_id (Integer) - Id of perm

    Exceptions:
        InputError when any of:
      
            u_id does not refer to a valid user
            u_id refers to a user who is the only global owner and they are being demoted to a user
            permission_id is invalid
            the user already has the permissions level of permission_id
      
        AccessError when:
      
            the authorised user is not a global owner

    Return Value:
        Returns empty list
    '''
    # check token
    if not check_if_valid(token):
        raise AccessError("Invalid Token")
    
    # staging variables
    storage = data_store.get()
    auth_user_id = read_token(token)
    users = storage['users']

    # check token user is global owner
    auth_user = next(
        (user for user in users if auth_user_id == user['id']), None)
    if not auth_user['global_owner']:
        raise AccessError(description='Authorised user is not a global owner')

    # check u_id valid
    u_user = next((user for user in users if int(u_id) == user['id']), None)
    if u_user == None:
        raise InputError(description="Invalid User Id")

    # check u_id the only global owner
    other_owner = next((user for user in users if user['global_owner'] and user['id'] != auth_user_id), None)
        
    if int(u_id) == auth_user_id and not other_owner and permission_id == MEMBER:
        raise InputError(description='User is the only global owner')
    
    if permission_id not in [OWNER, MEMBER]:
        raise InputError(description='Invalid perm id')
    
    if (u_user['global_owner'] and permission_id == OWNER) or (permission_id == MEMBER and not u_user['global_owner']):
        raise InputError(description='Already that permission')
    
    if permission_id == OWNER:
        u_user['global_owner'] = True
    else:
        u_user['global_owner'] = False
    data_store.set(storage)
    return {}