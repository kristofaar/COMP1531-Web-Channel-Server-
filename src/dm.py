from src.data_store import data_store
from src.error import InputError
from src.error import AccessError
from src.other import read_token, check_if_valid
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
    #staging variables
    storage = data_store.get()
    if not check_if_valid(token):
        raise AccessError(description="Invalid token")
    user_id = read_token(token)
    users = storage['users']
    dm = storage['dms']
    
    u_ids.append(user_id)
    u_ids.sort()
    handles = []

    #checks for duplicate in u_ids
    if len(u_ids) != len(set(u_ids)):
        raise InputError(description="U_ids Contains Duplicate(s)")
    
    #id creation is based off the last dm id
    dm_id = 1
    if len(dm):
       dm_id = dm[len(dm) - 1]['dm_id'] + 1

    #adds handle to list of handles
    for u_id in u_ids:
        match_user = next((user for user in users if u_id == user['id']), None)
        if match_user == None:
            raise InputError(description="Invalid User Id(s) In U_id")
        handles.append(match_user['handle'])

    #creates dm name by concatenating handles
    handles.sort()
    name = ', '.join(handles) 

    
    #updating the data store
    dm.append({'dm_id': dm_id, 'name' : name, 'owner': [user_id], 'members': u_ids, 'messages': []})
    
    #updating users
    for u_id in u_ids:
        curr_user = next((user for user in users if u_id == user['id']),None)
        curr_user['dms'].append({'dm_id' : dm_id, 'name' : name})
    data_store.set(storage)
    return{
        'dm_id' : dm_id
    }

def dm_list_v1(token):
    '''
    Provides a list of all the dms that the user is a part of

    Arguments:
        token     (string)  - passes in the unique user token of whoever ran the funtion
    
    Exceptions:
        AccessError - Occurrs when the user id provided is not valid

    Return Value:
        Returns a dictionary of dm_ids and dm names when successful
    '''
    #staging variables
    storage = data_store.get()
    if not check_if_valid(token):
        raise AccessError(description="Invalid token")
    user_id = read_token(token)
    users = storage['users']

    #iterate through users until a user with the corresponding id is found
    curr_user = next((user for user in users if user_id == user['id']), None)    
    return {
        'dms': curr_user['dms']
    }

def dm_remove_v1(token, dm_id):
    '''
    Remove an existing DM, so all members are no longer in the DM. This can only be done by the original creator of the DM.

    Arguments:
        token     (string)  - passes in the unique user token of whoever ran the funtion.
        dm_id     (int)     - asses in the unique channel id of the dm we are removing.
    
    Exceptions:
        AccessError - Occurrs when the dm_id provided is valid but the user is not the creator.
        AccessError - Occurrs when the dm_id provided is valid but the user is not in the dm.
        InputError  - Occurrs when the dm_id provided is not valid.

    Return Value:
        NULL
    '''
    #staging variables
    storage = data_store.get()
    
    if not check_if_valid(token):
        raise AccessError(description="Invalid token")
    user_id = read_token(token)
    dms = storage['dms']
    users = storage['users']

    #check if the dm_id is valid
    curr_dm = next((dm for dm in dms if int(dm_id) == dm['dm_id']), None)
    if curr_dm == None:
        raise InputError(description="Invalid Dm_id")
    
    #check if the user is in dm
    if user_id not in curr_dm['members']:
        raise AccessError(description="User Is Not In Dm")
    #check if the user is the owner
    if user_id not in curr_dm['owner']:
        raise AccessError(description="User Is Not Creator")
    
    

    #updating user and dms
    for members in curr_dm['members']:
        curr_user = next((user for user in users if members == user['id']), None)
        curr_user['dms'].remove({'dm_id': curr_dm['dm_id'], 'name': curr_dm['name']})
    dms.remove(curr_dm)
    data_store.set(storage)
    return{}

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
    
    if not check_if_valid(token):
        raise AccessError(description="Invalid token")
    auth_user_id = read_token(token)
    dms = storage['dms']
    users = storage['users']

    #search through dms by id until id is matched
    curr_dm = next((dm for dm in dms if int(dm_id) == dm['dm_id']), None)
    if curr_dm == None:
        raise InputError(description="Invalid dm id")
    dm_name = curr_dm['name']

    #check if auth_user_id is a member of the dm queried
    if int(auth_user_id) not in curr_dm['members']:
        raise AccessError(description="Unauthorised User: User is not in dm")

    #generate lists of dm members
    dm_members = []
    for member in curr_dm['members']:
        curr_user = next(user for user in users if member == user['id'])
        dm_members.append({'u_id': curr_user['id'], 
                           'email': curr_user['email'], 
                           'name_first': curr_user['name_first'], 
                           'name_last': curr_user['name_last'], 
                           'handle_str': curr_user['handle']})

    return {"name": dm_name, "members": dm_members}

def dm_leave_v1(token, dm_id):
    '''
    Given a DM ID, the user is removed as a member of this DM

    Arguments:
        token        (str)    - passes in the unique token of whoever ran the funtion
        dm_id        (int)    - passes in the unique dm id of the dm we are enquiring about

    Exceptions:
        InputError  - Occurs when dm_id does not refer to a valid dm
        AccessError - Occurs when dm_id is valid and the authorised user is not a member of the dm

    Return Value:
        Returns name of the dm, and the members of the dm
    '''
    storage = data_store.get()
    
    if not check_if_valid(token):
        raise AccessError(description="Invalid token")
    user_id = read_token(token)
    dms = storage['dms']
    users = storage['users']
    
    #check if the user is the owner
    curr_dm = next((dm for dm in dms if int(dm_id) == dm['dm_id']), None)
    if curr_dm == None:
        raise InputError(description="Invalid dm id")

    if int(user_id) not in curr_dm['members']:
        raise AccessError(description="Unauthorised User: User is not in dm")

    curr_user = next((user for user in users if user_id == user['id']), None)
    curr_user['dms'].remove({'dm_id' : curr_dm['dm_id'], 'name' : curr_dm['name']})
    curr_dm['members'].remove(user_id)
    data_store.set(storage)
    return{}

def dm_messages_v1(token, dm_id, start):

    '''
Returns information on up to 50 messages within the dm

Arguments:
    token                     - User who is trying to access the messages
    dm_id      (Integer)      - Id of dm that the messages are being outputted from
    start      (Integer)      - Which index of messages to start outputting

Exceptions:
    InputError  - Occurs when:
        - dm_id does not refer to a valid dm
        - start is greater than the total number of messages in the dm
    AccessError - Occurs when:
        - dm_id is valid and the authorised user is not a member of the dm
        - auth_user_id is not a valid id in the system

Return Value:
    Returns {messages, start, end} always, where end is the index of the final message, -1 if up to date.
'''

    storage = data_store.get()
    if not check_if_valid(token):
        raise AccessError(description="Invalid token")
    auth_user_id = read_token(token)

    #getting channel
    dm_exists = False
    temp_dm = {}
    for dm in storage['dms']:
        if dm['dm_id'] == int(dm_id):
            dm_exists = True
            temp_dm = dm

    #errors
    if not dm_exists:
        raise InputError(description="Channel ID does not exist")
    
    id_exists = False
    for user in temp_dm['members']:
        if user == auth_user_id:
            id_exists = True
    
    if not id_exists:
        raise AccessError(description="Unauthorised ID")
    
    if int(start) > len(temp_dm['messages']):
        raise InputError(description="Start index is greater than number of messages")
    
    #storing 50 messages into ret_messages
    ret_messages = []
    for i in range(int(start), int(start) + 50 if int(start) + 50 < len(temp_dm['messages']) else len(temp_dm['messages'])):
        ret_messages.append(temp_dm['messages'][i])

    return {
        'messages': ret_messages,
        'start': int(start),
        'end': int(start) + 50 if int(start) + 50 < len(temp_dm['messages']) else -1,
    }
