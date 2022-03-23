from src.data_store import data_store
from src.error import InputError
from src.error import AccessError
from src.other import create_token, read_token, check_if_valid
import hashlib
import jwt

SECRET = 'heheHAHA111'


def channel_invite_v1(token, channel_id, u_id):
    '''
channel_invite_v1 invites a user with ID u_id to join a channel with ID channel_id. Once invited, the user is 
added to the channel immediately. In both public and private channels, all members are able to invite users.

Arguments:
    token       (hash)  - passes in the unique user id of whoever ran the funtion
    channel_id  (int)   - passes in the unique channel id of the channel we are inviting someone to
    u_id        (int)   - passes in the unique user id of who we are inviting into the channel

Exceptions:
    InputError  - Occurs when channel_id does not refer to a valid channel
                - Occurs when u_id does not refer to a valid user
                - Occurs when u_id refers to a user who is already a member of the channel
    AccessError - Occurs when channel_id is valid and the authorised user is not a member of the channel
'''
    # check token 
    if not check_if_valid(token):
        raise AccessError("Invalid Token")
        
    # staging variables
    check_if_valid(token)
    storage = data_store.get()
    auth_user_id = read_token(token)

    channels = storage['channels']
    users = storage['users']

    # Check auth_user_id is registered
    check_auth_user_id = next(
        (user for user in users if auth_user_id == user['id']), None)
    if check_auth_user_id == None:
        raise AccessError("Invalid User (Channel Inviter)")

    # search through channels by id until id is matched
    ch = next((channel for channel in channels if channel_id ==
              channel['channel_id_and_name']['channel_id']), None)
    if ch == None:
        raise InputError("Invalid Channel Id")

    # Check auth_user_id is a member
    if auth_user_id not in ch['members']:
        raise AccessError("Authorised user not in channel")

    # search through users until u_id is matched
    add_user = next((user for user in users if u_id == user['id']), None)
    if add_user == None:
        raise InputError("Adding an Invalid User")

    # check u_id is not in channel members
    if u_id in ch['members']:
        raise InputError("User already in channel")

    # add user to channel
    ch['members'].append(u_id)

    # update user
    add_user['channels'].append({'channel_id': ch['channel_id_and_name']
                                ['channel_id'], 'name': ch['channel_id_and_name']['name']})
    data_store.set(storage)
    return {
    }


def channel_details_v1(token, channel_id):
    '''
channel_details_v1 provides basic details about the channel given a channel with ID channel_id that the 
authorised user is a member of.

Arguments:
    token       (hash)  - passes in the unique user id of whoever ran the funtion
    channel_id  (int)   - passes in the unique channel id of the channel we are enquiring about

Exceptions:
    InputError  - Occurs when channel_id does not refer to a valid channel
    AccessError - Occurs when channel_id is valid and the authorised user is not a member of the channel

Return Value:
    Returns channel_id, channel name, whether or not the channel is 
    public, the owner members, and all members of the channel.
'''
    # check token 
    if not check_if_valid(token):
        raise AccessError("Invalid Token")

    # staging variables
    check_if_valid(token)
    storage = data_store.get()
    auth_user_id = read_token(token)

    channels = storage['channels']
    users = storage['users']

    # Check auth_user_id is registered
    check_auth_user_id = next(
        (user for user in users if auth_user_id == user['id']), None)
    if check_auth_user_id == None:
        raise AccessError("Invalid User (Channel Inviter)")

    # search through channels by id until id is matched
    ch = next((channel for channel in channels if channel_id ==
              channel['channel_id_and_name']['channel_id']), None)
    if ch == None:
        raise InputError("Invalid Channel Id")

    # check if auth_user_id is a member of the channel queried
    if auth_user_id not in ch['members']:
        raise AccessError("Unauthorised User: User is not in channel")

    # generate lists of users
    owner_members = []
    all_members = []
    for member in ch['owner']:
        curr_user = next(
            (user for user in users if member == user['id']), None)
        owner_members.append({'u_id': curr_user['id'], 'email': curr_user['email'], 'name_first': curr_user['name_first'],
                             'name_last': curr_user['name_last'], 'handle_str': curr_user['handle']})
    for member in ch['members']:
        curr_user = next(
            (user for user in users if member == user['id']), None)
        all_members.append({'u_id': curr_user['id'], 'email': curr_user['email'], 'name_first': curr_user['name_first'],
                           'name_last': curr_user['name_last'], 'handle_str': curr_user['handle']})

    return {'name': ch['channel_id_and_name']['name'],

            'is_public': ch['is_public'],
            'owner_members': owner_members,
            'all_members': all_members}


def channel_messages_v1(token, channel_id, start):
    '''
Returns information on up to 50 messages within the channel

Arguments:
    token       (Hash)      - User who is trying to access the messages
    channel_id  (Integer)   - Id of channel that the messages are being outputted from
    start       (Integer)   - Which index of messages to start outputting

Exceptions:
    InputError  - Occurs when:
        - channel_id does not refer to a valid channel
        - start is greater than the total number of messages in the channel
    AccessError - Occurs when:
        - channel_id is valid and the authorised user is not a member of the channel
        - auth_user_id is not a valid id in the system

Return Value:
    Returns {messages, start, end} always, where end is the index of the final message, -1 if up to date.
'''
    # check token 
    if not check_if_valid(token):
        raise AccessError("Invalid Token")

    # Staging variables
    check_if_valid(token)
    storage = data_store.get()
    u_id = read_token(token)

    # errors
    id_exists = False
    auth_user_id = -1
    for user in storage['users']:
        if user['id'] == u_id:
            id_exists = True
            auth_user_id = user['id']

    if not id_exists:
        raise AccessError("ID does not exist")

    # getting channel
    channel_exists = False
    temp_channel = {}
    for channel in storage['channels']:
        if channel['channel_id_and_name']['channel_id'] == channel_id:
            channel_exists = True
            temp_channel = channel

    # errors
    if not channel_exists:
        raise InputError("Channel ID does not exist")

    id_exists = False
    for user in temp_channel['members']:
        if user == auth_user_id:
            id_exists = True

    if not id_exists:
        raise AccessError("Unauthorised ID")

    if start > len(temp_channel['messages']):
        raise InputError("Start index is greater than number of messages")

    # storing 50 messages into ret_messages
    ret_messages = []
    for i in range(start, start + 50 if start + 50 < len(temp_channel['messages']) else len(temp_channel['messages'])):
        ret_messages.append(temp_channel['messages'][i])

    return {
        'messages': ret_messages,
        'start': start,
        'end': start + 50 if start + 50 < len(temp_channel['messages']) else -1,
    }


def channel_join_v1(token, channel_id):
    '''User with id auth_user_id is added into channel with id channel_id if public

Arguments:
    token       (hash)  - hashed id of the user
    channel_id  (int)   - id of the channel
    ...

Exceptions:
    InputError  - Occurs when:
        - channel_id does not refer to a valid channel
        - the authorised user is already a member of the channel

    AccessError - Occurs when:
        - channel_id refers to a channel that is private and the authorised user is not already a channel member and is not a global owner

Return Value:
    Returns {} always
'''
    # check token 
    if not check_if_valid(token):
        raise AccessError("Invalid Token")

    # staging variables
    check_if_valid(token)
    storage = data_store.get()
    auth_user_id = read_token(token)

    channels = storage['channels']
    users = storage['users']

    # check auth_user_id is valid user
    user = next((user for user in users if user['id'] == auth_user_id), None)
    if user == None:  # User not found
        raise AccessError('Unregistered user id')

    # check channel is valid
    channel = next((channel for channel in channels if channel_id ==
                   channel['channel_id_and_name']['channel_id']), None)
    if channel == None:
        raise InputError("Invalid Channel Id")

    # check if already a member
    member = next(
        (member for member in channel['members'] if auth_user_id == member), None)
    # New member but private channel
    if channel['is_public'] == False and member == None and not user['global_owner']:
        raise AccessError('Channel is private and user is not a member')
    elif member != None:  # Existing member
        raise InputError('User already a channel member')

    # If conditions met, add new member to channel
    member_list = channel['members']
    member_list.append(auth_user_id)

    # update user
    user['channels'].append({'channel_id': channel['channel_id_and_name']
                            ['channel_id'], 'name': channel['channel_id_and_name']['name']})
    data_store.set(storage)

    return {
    }


def channel_leave_v1(token, channel_id):
    '''Removes user from channel_id

    Arguments:
        token       (hash)  - hashed id of the user
        channel_id  (int)   - id of the channel
        ...

    Exceptions:
        InputError  - Occurs when:
            - channel_id does not refer to a valid channel

        AccessError - Occurs when:
            - channel_id is valid and the authorised user is not a member of the channel

    Return Value:
        Returns {} always
    '''
    # check token 
    if not check_if_valid(token):
        raise AccessError("Invalid Token")

    # staging variables
    check_if_valid(token)
    storage = data_store.get()
    auth_user_id = read_token(token)

    channels = storage['channels']
    users = storage['users']

    # check auth_user_id is valid user
    user = next((user for user in users if user['id'] == auth_user_id), None)
    if user == None:  # User not found
        raise AccessError('Unregistered user id')

    # check channel is valid
    channel = next((channel for channel in channels if channel_id ==
                   channel['channel_id_and_name']['channel_id']), None)
    if channel == None:
        raise InputError("Invalid Channel Id")

    # check if a member of channel
    member = next(
        (member for member in channel['members'] if auth_user_id == member), None)
    if member is None:
        raise AccessError('User is not a member of the channel')

    # remove user from channel_members
    member_list = channel['members']
    member_list.remove(auth_user_id)

    # remove user from channel owners if they are one
    if auth_user_id in channel['owner']:
        channel['owner'].remove(auth_user_id)
    # remove channel_id from user
    for u_channel in user['channels']:
        if u_channel['channel_id_and_name']['channel_id'] == channel_id:
            user['channels'].remove(u_channel)

    return {
    }


def channel_addowner_v1(token, channel_id, u_id):
    '''Make user with user id u_id an owner of the channel.

    Arguments:
        token       (hash)  - hashed id of the user
        channel_id  (int)   - id of the channel
        u_id        (int)   - id of any user
        ...

    Exceptions:
        InputError  - Occurs when:
            - channel_id does not refer to a valid channel
            - u_id does not refer to a valid user
            - u_id refers to a user who is not a member of the channel
            - u_id refers to a user who is already an owner of the channel

        AccessError - Occurs when:
            - channel_id is valid and the authorised user does not have owner permissions in the channel

    Return Value:
        Returns {} always
    '''
    # check token 
    if not check_if_valid(token):
        raise AccessError("Invalid Token")

    # staging variables
    check_if_valid(token)
    storage = data_store.get()
    auth_user_id = read_token(token)

    channels = storage['channels']
    users = storage['users']

    # check auth_user_id is valid user
    a_user = next((user for user in users if user['id'] == auth_user_id), None)
    if a_user == None:  # User not found
        raise InputError(description='Unregistered user id')

    # check channel is valid
    channel = next((channel for channel in channels if channel_id ==
                   channel['channel_id_and_name']['channel_id']), None)
    if channel == None:
        raise InputError(description="Invalid Channel Id")

    # check if auth_user_id is member of channel and a global owner
    member = next(
        (member for member in channel['members'] if auth_user_id == member), None)
    if member is None and a_user['global_owner']:
        raise AccessError(
            description='Authorised user is global user but not member of channel')

    # check if auth_user_id an owner of channel
    owner = next(
        (owner for owner in channel['owner'] if auth_user_id == owner), None)
    if owner is None:
        raise InputError(
            description='Authorised user is not an owner of the channel')

    # check if u_id is valid user
    u_user = next((user for user in users if user['id'] == u_id), None)
    if u_user == None:  # User not found
        raise InputError(description='Unregistered user id')

    # check if u_id already an owner of channel
    u_owner = next(
        (owner for owner in channel['owner'] if u_id == owner), None)
    if u_owner is not None:
        raise InputError(
            description='User getting added is already owner of the channel')

    # check if u_id a member of channel
    member = next(
        (member for member in channel['members'] if u_id == member), None)
    if u_id is None:
        raise InputError(
            description='User getting added is not a member of channel')

    # adds u_id to channel owner list now 
    channel['owner'].append(u_id)
    return {}


def channel_removeowner_v1(token, channel_id, u_id):
    '''U_id no longer an owner of channel.

    Arguments:
        token       (hash)  - hashed id of the user
        channel_id  (int)   - id of the channel
        u_id        (int)   - id of any user
        ...

    Exceptions:
        InputError  - Occurs when:
            - channel_id does not refer to a valid channel
            - u_id does not refer to a valid user
            - u_id refers to a user who is not an owner of the channel
            - u_id refers to a user who is currently the only owner of the channel

        AccessError - Occurs when:
            - channel_id is valid and the authorised user does not have owner permissions in the channel

    Return Value:
        Returns {} always
    '''
    # check token 
    if not check_if_valid(token):
        raise AccessError("Invalid Token")
        
    # staging variables
    check_if_valid(token)
    storage = data_store.get()
    auth_user_id = read_token(token)

    channels = storage['channels']
    users = storage['users']

    # check auth_user_id is valid user
    a_user = next((user for user in users if user['id'] == auth_user_id), None)
    if a_user == None:  # User not found
        raise InputError(description='Unregistered user id')

    # check channel is valid
    channel = next((channel for channel in channels if channel_id ==
                   channel['channel_id_and_name']['channel_id']), None)
    if channel == None:
        raise InputError(description="Invalid Channel Id")

    # check if auth_user_id is member of channel and a global owner
    member = next(
        (member for member in channel['members'] if auth_user_id == member), None)
    if member is None and a_user['global_owner']:
        raise AccessError(
            description='Authorised user is global user but not member of channel')

    # check if auth_user_id an owner of channel
    owner = next(
        (owner for owner in channel['owner'] if auth_user_id == owner), None)
    if owner is None:
        raise InputError(
            description='Authorised user is not an owner of the channel')

    # check if u_id is valid user
    u_user = next((user for user in users if user['id'] == u_id), None)
    if u_user is None:  # User not found
        raise InputError(description='Unregistered user id')

    # check if u_id not an owner of channel
    u_owner = next(
        (owner for owner in channel['owner'] if u_id == owner), None)
    if u_owner is None:
        raise InputError(
            description='User getting removed is not an owner of the channel')

    # check if u_id only owner of channel
    if len(channel['owner']) == 1:
        raise InputError(
            description='User getting removed is the only owner of channel')

    # removing u_id from channel owners and members list 
    channel['owner'].remove(u_id)
    channel['members'].remove(u_id)

    return {}
