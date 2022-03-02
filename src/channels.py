from multiprocessing import dummy
from src.data_store import data_store
from src.error import InputError
from src.error import AccessError

'''channels_list_v1 provides a list of all the channels that the user is a part of

Arguments:
    auth_user_id     (int)  - passes in the unique user id of whoever ran the funtion
    ...

Exceptions:
    N/A

Return Value:
    Returns channel id when successful
    Returns channel name when successful
'''
def channels_list_v1(auth_user_id):
    return {
        'channels': [
        	{
        		'channel_id': 1,
        		'name': 'My Channel',
        	}
        ],
    }

def channels_listall_v1(auth_user_id):
    return {
        'channels': [
        	{
        		'channel_id': 1,
        		'name': 'My Channel',
        	}
        ],
    }

'''
Channels_create_v1 creates a new channel with the given name and public status>

Arguments:
    auth_user_id    (int)       - passes in the unique user id of whoever ran the funtion
    name            (string)    - Gives a name to the channel that is to be created
    is_public       (boolean)   - Sets who can and cant see the new channel 
    ...

Exceptions:
    AccessError - Occurrs when the user id provided is not valid    
    InputError  - Occurs when length of name is less than 1 or more than 20 characters

Return Value:
    Returns channel_id after creating the channel
'''
def channels_create_v1(auth_user_id, name, is_public):
    #staging variables
    storage = data_store.get()
    users = storage['users']
    channels = storage['channels']
    ch_id = 0
    #look through users to see if the given id matches any of their ids
    curr_user = next((user for user in users if auth_user_id == user['id']), None)
    if 20 < len(name):
        raise InputError("Channel Name Is Too Long")
    if 1 > len(name):
        raise InputError("Channel Name Is Too Short")
    #if the given id is not found in users then spit out error message
    if curr_user == None:
        raise AccessError("Invalid User Id ")

    #generate channel id based on its position in the list
    ch_id = len(channels) + 1

    #updating the data store
    channels.append({'channel_id_and_name' :{'id' : ch_id, 'name' : name}, 'is_public' : is_public, 
    'owner' : [auth_user_id], 'members' : [auth_user_id], 'messages' : []})


    #updating user
    curr_user['channels'].append(ch_id)
    data_store.set(storage)
    return{
        'channel_id' : ch_id
    }
    
