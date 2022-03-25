from multiprocessing import dummy
from src import auth
from src.data_store import data_store
from src.error import InputError, AccessError
from src.other import create_token, read_token, check_if_valid


def admin_user_remove_v1(token, u_id):
    '''Given a user by their u_id, remove them from the Seams. 

    Arguments:
        token (String)          - The user's email, must be unique.
        u_id (Integer)          - Password must be greater or equal to 6 characters long. 

    Exceptions:
        InputError  - Occurs when: 
            -u_id does not refer to a valid user
            -u_id refers to a user who is the only global owner

        AccessError - Occurs when:
            -the authorised user is not a global owner

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
    u_user = next((user for user in users if u_id == user['id']), None)
    if u_user == None:
        raise InputError(description="Invalid User Id")

    # check u_id the only global owner
    other_owner = next((user for user in users if user['global_owner'] and user['id'] != auth_user_id), None)
        
    if not other_owner:
        raise InputError(description='User is the only global owner')

    # remove user from channels
    for channel in u_user['channels']:
        channel['members'].remove(u_id)
        if u_id in channel['owner']:
            channel['owner'].remove(u_id)
        # replace channel messages to 'Removed user'
        for message in channel['messages']:
            message['message'] = 'Removed user'

    # remove user from dms
    for dm in storage['dms']:
        user_in_dm = False
        dm_names_list = dm['name'].split(', ')
        if u_id in dm['owner']:
            user_in_dm = True
            dm['owner'].remove(u_id)
        elif u_user['handle'] in dm_names_list:
            user_in_dm = True
            dm_names_list.remove(u_user['handle'])
            dm['name'] = ', '.join(dm_names_list)
        # change messages to 'Removed user'
        if user_in_dm:
            for message in dm['messages']:
                if message['u_id'] == u_id:
                    message['message'] = 'Removed user'

    # move user to removed users list
    removed_users = storage['removed_users']
    removed_users.append(
        {'user_id': u_id, 'email': u_user['email'], 'first_name': 'Removed', 'last name': 'user', 'handle': u_user['handle']})

    # remove user from users list
    users.remove(u_user)

    data_store.set(storage)

    return {}

def admin_userpermission_change_v1(token, u_id, permission_id):
    return {}