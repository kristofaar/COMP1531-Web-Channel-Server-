from src.data_store import data_store
from src.error import InputError
from src.error import AccessError

'''
channel_invite_v1 invites a user with ID u_id to join a channel with ID channel_id. Once invited, the user is 
added to the channel immediately. In both public and private channels, all members are able to invite users.

Arguments:
    auth_user_id (int)    - passes in the unique user id of whoever ran the funtion
    channel_id   (int)    - passes in the unique channel id of the channel we are inviting someone to
    u_id         (int)    - passes in the unique user id of who we are inviting into the channel

Exceptions:
    InputError  - Occurs when channel_id does not refer to a valid channel
                - Occurs when u_id does not refer to a valid user
                - Occurs when u_id refers to a user who is already a member of the channel
    AccessError - Occurs when channel_id is valid and the authorised user is not a member of the channel
'''
def channel_invite_v1(auth_user_id, channel_id, u_id):
    #staging variables
    storage = data_store.get()
    channels = storage['channels']
    users = storage['users']

    #search through channels by id until id is matched
    ch = next((channel for channel in channels if channel_id == channel['id']), None)
    if ch == None:
        raise InputError("Invalid Channel Id")
    
    #search through users until u_id is matched
    add_user = next((user for user in users if u_id == user['id']), None)
    if add_user == None:
        raise InputError("Adding an Invalid User")
    
    #check u_id is not in channel members
    if u_id in ch['all_members']:
        raise InputError("User already in channel")
    
    if auth_user_id not in ch['all_members']:
        raise AccessError("Authorised user not in channel")

    #add user to channel
    ch['members'].append(u_id)

    #update user
    add_user['channels'].append({'id': ch['channel_id_and_name']['id'], 'name': ch['channel_id_and_name']['name']})
    data_store.set(storage)

'''
channel_details_v1 provides basic details about the channel given a channel with ID channel_id that the 
authorised user is a member of.

Arguments:
    auth_user_id (int)    - passes in the unique user id of whoever ran the funtion
    channel_id   (int)    - passes in the unique channel id of the channel we are enquiring about

Exceptions:
    InputError  - Occurs when channel_id does not refer to a valid channel
    AccessError - Occurs when channel_id is valid and the authorised user is not a member of the channel

Return Value:
    Returns channel_id, channel name, whether or not the channel is 
    public, the owner members, and all members of the channel.
'''
def channel_details_v1(auth_user_id, channel_id):
    #staging variables
    storage = data_store.get()
    channels = storage['channels']
    users = storage['users']
    #search through channels by id until id is matched
    ch = next((channel for channel in channels if channel_id == channel['id']), None)
    if ch == None:
        raise InputError("Invalid Channel Id")

    #check if auth_user_id is a member of the channel queried
    if auth_user_id not in ch['all_members']:
        raise AccessError("Unauthorised User: User is not in channel")

    #generate lists of users 
    owner_members = []
    all_members = []
    for member in ch['owner_members']:
        curr_user = next((user for user in users if member == user['id']), None)
        owner_members.append(curr_user)
    for member in ch['all_members']:
        curr_user = next((user for user in users if member == user['id']), None)
        all_members.append(curr_user)

    return {'id': channel_id,
            'name': ch['name'],
            'is_public': ch['is_public'],
            'owner_members': owner_members,
            'all_members': all_members}

'''
<Brief description of what the function does>

Arguments:
    <name> (<data type>)    - <description>
    <name> (<data type>)    - <description>
    ...

Exceptions:
    InputError  - Occurs when ...
    AccessError - Occurs when ...

Return Value:
    Returns <return value> on <condition>
    Returns <return value> on <condition>
'''
def channel_messages_v1(auth_user_id, channel_id, start):
    return {
        'messages': [
            {
                'message_id': 1,
                'u_id': 1,
                'message': 'Hello world',
                'time_created': 1582426789,
            }
        ],
        'start': 0,
        'end': 50,
    }

'''<Brief description of what the function does>

Arguments:
    <name> (<data type>)    - <description>
    <name> (<data type>)    - <description>
    ...

Exceptions:
    InputError  - Occurs when ...
    AccessError - Occurs when ...

Return Value:
    Returns <return value> on <condition>
    Returns <return value> on <condition>
'''
def channel_join_v1(auth_user_id, channel_id):
    #staging variables
    storage = data_store.get()
    channels = storage['channels']
    users = storage['users']
    
    # check auth_user_id is valid user 
    user = next((user for user in users if user['id'] == auth_user_id), None)
    if user == None: # User not found
        raise InputError('Unregistered user id')

    # check channel is valid 
    channel = next((channel for channel in channels if channel_id == channel['id']), None)
    if channel == None:
        raise InputError("Invalid Channel Id")

    # check if already a member 
    member = next((member for member in channel['all_members'] if auth_user_id == member), None)
    if member != None:  # Existing member 
        raise InputError('User already a channel member')
    elif channel['is_public'] == False:  # New member but private channel
        raise AccessError('Channel is private and user is not a member')
    
    # If conditions met, add new member to channel
    member_list = channel['all_members']
    member_list.append(auth_user_id)

    return {
    }
