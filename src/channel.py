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

    # Check auth_user_id is registered 
    check_auth_user_id = next((user for user in users if auth_user_id == user['id']), None)
    if check_auth_user_id == None:
        raise AccessError("Invalid User (Channel Inviter)")

    #search through channels by id until id is matched
    ch = next((channel for channel in channels if channel_id == channel['channel_id_and_name']['id']), None)
    if ch == None:
        raise InputError("Invalid Channel Id")
    
    #Check auth_user_id is a member 
    if auth_user_id not in ch['members']:
        raise AccessError("Authorised user not in channel")

    #search through users until u_id is matched
    add_user = next((user for user in users if u_id == user['id']), None)
    if add_user == None:
        raise InputError("Adding an Invalid User")
    
    #check u_id is not in channel members
    if u_id in ch['members']:
        raise InputError("User already in channel")
    
    #add user to channel
    ch['members'].append(u_id)

    #update user
    add_user['channels'].append({'channel_id': ch['channel_id_and_name']['id'], 'name': ch['channel_id_and_name']['name']})
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

    # Check auth_user_id is registered 
    check_auth_user_id = next((user for user in users if auth_user_id == user['id']), None)
    if check_auth_user_id == None:
        raise AccessError("Invalid User (Channel Inviter)")

    #search through channels by id until id is matched
    ch = next((channel for channel in channels if channel_id == channel['channel_id_and_name']['id']), None)
    if ch == None:
        raise InputError("Invalid Channel Id")

    #check if auth_user_id is a member of the channel queried
    if auth_user_id not in ch['members']:
        raise AccessError("Unauthorised User: User is not in channel")

    #generate lists of users 
    owner_members = []
    all_members = []
    for member in ch['owner']:
        curr_user = next((user for user in users if member == user['id']), None)
        owner_members.append({'u_id': curr_user['id'], 'email': curr_user['email'], 'name_first': curr_user['name_first'], 'name_last': curr_user['name_last'], 'handle_str': curr_user['handle']})
    for member in ch['members']:
        curr_user = next((user for user in users if member == user['id']), None)
        all_members.append({'u_id': curr_user['id'], 'email': curr_user['email'], 'name_first': curr_user['name_first'], 'name_last': curr_user['name_last'], 'handle_str': curr_user['handle']})

    return {'name': ch['channel_id_and_name']['name'],
            'is_public': ch['is_public'],
            'owner_members': owner_members,
            'all_members': all_members}

'''
<Returns information on up to 50 messages within the channel>

Arguments:
    <auth_user_id> (<Integer>)    - <User who is trying to access the messages>
    <channel_id> (<Integer>)    - <Id of channel that the messages are being outputted from>
    <start> (<Integer>)    - <Which index of messages to start outputting

Exceptions:
    InputError  - Occurs when:
        - channel_id does not refer to a valid channel
        - start is greater than the total number of messages in the channel
    AccessError - Occurs when:
        - channel_id is valid and the authorised user is not a member of the channel
        - auth_user_id is not a valid id in the system

Return Value:
    Returns <{messages, start, end}> always, where end is the index of the final message, -1 if up to date.
'''
def channel_messages_v1(auth_user_id, channel_id, start):
    storage = data_store.get()

    #errors
    id_exists = False
    for user in storage['users']:
        if user['id'] == auth_user_id:
            id_exists = True
    
    if not id_exists:
        raise AccessError("ID does not exist")

    channel_exists = False
    temp_channel = {}
    for channel in storage['channels']:
        if channel['channel_id_and_name']['id'] == channel_id:
            channel_exists = True
            temp_channel = channel

    if not channel_exists:
        raise InputError("Channel ID does not exist")
    
    id_exists = False
    for user in temp_channel['members']:
        if user == auth_user_id:
            id_exists = True
    
    if not id_exists:
        raise AccessError("Unauthorised ID")
    
    if start + 1 > len(temp_channel['messages']) and start != 0:
        raise InputError("Start index is greater than number of messages")
    
    ret_messages = []
    for i in range(start, start + 50 if start + 50 < len(temp_channel['messages']) else len(temp_channel['messages'])):
        ret_messages.append(temp_channel['messages'][i])

    return {
        'messages': ret_messages,
        'start': start,
        'end': start + 50 if start + 50 < len(temp_channel['messages']) else -1,
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
        raise AccessError('Unregistered user id')

    # check channel is valid 
    channel = next((channel for channel in channels if channel_id == channel['channel_id_and_name']['id']), None)
    if channel == None:
        raise InputError("Invalid Channel Id")

    # check if already a member 
    member = next((member for member in channel['members'] if auth_user_id == member), None)
    if channel['is_public'] == False and member == None:  # New member but private channel
        raise AccessError('Channel is private and user is not a member')
    elif member != None:  # Existing member 
        raise InputError('User already a channel member')
        
    
    # If conditions met, add new member to channel
    member_list = channel['members']
    member_list.append(auth_user_id)

    #update user
    user['channels'].append({'channel_id': channel['channel_id_and_name']['id'], 'name': channel['channel_id_and_name']['name']})
    data_store.set(storage)

    return {
    }
