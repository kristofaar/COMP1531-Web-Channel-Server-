from multiprocessing import dummy
from src.data_store import data_store
from src.error import InputError
from src.error import AccessError
from src.other import create_token, read_token, check_if_valid

def channels_list_v1(token):
    '''
    Provides a list of all the channels that the user is a part of

    Arguments:
        token     (string)  - passes in the unique user token of whoever ran the funtion
    
    Exceptions:
        AccessError - Occurrs when the user id provided is not valid

    Return Value:
        Returns a dictionary of channel ids and channel names when successful
    '''
    storage = data_store.get()
    if not check_if_valid(token):
        raise AccessError("Invalid token")
    user_id = read_token(token)
    users = storage['users']
    

            
    #iterate through users until a user with the corresponding id is found
    curr_user = next(user for user in users if user_id == user['id'])

    return {
        'channels': curr_user['channels']
    }


def channels_listall_v1(token):
    '''
    Provides a list of all channels, including private channels

    Arguments:
        token     (string)  - passes in the unique user token of whoever ran the funtion
        
    Exceptions:
        N/A

    Return Value:
        Returns a dictionary of channel ids and channel names when successful
    '''
    channel_list = []
    storage = data_store.get()
    if not check_if_valid(token):
        raise AccessError("Invalid token")

    #add all the channels that have been created to a list 
    for channel in storage['channels']:
        channel_list.append(channel['channel_id_and_name'])
    return {
        'channels': channel_list
    }

def channels_create_v1(token, name, is_public):
    '''
    Creates a new channel with the given name and public status

    Arguments:
        token           (string)   - passes in the unique user token of whoever ran the funtion
        name            (string)    - Gives a name to the channel that is to be created
        is_public       (boolean)   - Sets who can and cant see the new channel 
        ...

    Exceptions:
        AccessError - Occurrs when the user id provided is not valid    
        InputError  - Occurs when length of name is less than 1 or more than 20 characters

    Return Value:
        Returns channel_id after creating the channel
    '''
    #staging variables
    storage = data_store.get()
    if not check_if_valid(token):
        raise AccessError("Invalid token")
    user_id = read_token(token)
    users = storage['users']
    channels = storage['channels']
   
    #look through users to see if the given id matches any of their ids
    curr_user = next(user for user in users if user_id == user['id'])
    if 1 > len(name):
        raise InputError("Channel Name Is Too Short")
    if len(name) > 20:
        raise InputError("Channel Name Is Too Long")
    
    #id creation is based off the last channel's id
    ch_id = 1
    if len(storage['channels']):
        ch_id = storage['channels'][len(storage['channels']) - 1]['channel_id_and_name']['channel_id'] + 1

    #updating the data store
    channels.append({'channel_id_and_name' :{'channel_id' : ch_id, 'name' : name}, 'is_public' : is_public, 
    'owner' : [user_id], 'members' : [user_id], 'messages' : []})

    #updating user
    curr_user['channels'].append({'channel_id' : ch_id, 'name' : name})
    data_store.set(storage)
    return{
        'channel_id' : ch_id
    }
    
