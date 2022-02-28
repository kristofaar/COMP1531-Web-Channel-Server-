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

Return Value:
    Returns <return value> on <condition>
    Returns <return value> on <condition>
'''
def channel_invite_v1(auth_user_id, channel_id, u_id):
    return {
    }

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
    Returns <return value> on <condition>
    Returns <return value> on <condition>
'''
def channel_details_v1(auth_user_id, channel_id):
    #staging variables
    storage = data_store.get()
    return storage['channels'][channel_id]
    return {
        'name': 'Hayden',
        'owner_members': [
            {
                'u_id': 1,
                'email': 'example@gmail.com',
                'name_first': 'Hayden',
                'name_last': 'Jacobs',
                'handle_str': 'haydenjacobs',
            }
        ],
        'all_members': [
            {
                'u_id': 1,
                'email': 'example@gmail.com',
                'name_first': 'Hayden',
                'name_last': 'Jacobs',
                'handle_str': 'haydenjacobs',
            }
        ],
    }

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
    return {
    }
