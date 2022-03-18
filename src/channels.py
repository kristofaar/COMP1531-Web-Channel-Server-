from multiprocessing import dummy
from src.data_store import data_store
from src.error import InputError
from src.error import AccessError
from src.other import create_token, read_token

def channels_list_v1(auth_user_id):
    '''
    Provides a list of all the channels that the user is a part of

    Arguments:
        auth_user_id     (int)  - passes in the unique user id of whoever ran the funtion
    
    Exceptions:
        AccessError - Occurrs when the user id provided is not valid

    Return Value:
        Returns a dictionary of channel ids and channel names when successful
    '''
    storage = data_store.get()
    users = storage['users']
    

    if auth_user_id == None:
        raise InputError("User Id Entered Is Null")
        
    #iterate through users until a user with the corresponding id is found
    curr_user = next((user for user in users if auth_user_id == user['id']), None)
    #if no user has the given id raise an error
    if curr_user == None:
        raise AccessError("Invalid User Id ")

    return {
        'channels': curr_user['channels']
    }


def channels_listall_v1(auth_user_id):
    '''
    Provides a list of all channels, including private channels

    Arguments:
        auth_user_id     (int)  - passes in the unique user id of whoever ran the funtion
        
    Exceptions:
        N/A

    Return Value:
        Returns a dictionary of channel ids and channel names when successful
    '''
    channel_list = []
    storage = data_store.get()
    users = storage['users']
    

    if auth_user_id == None:
        raise InputError("User Id Entered Is Null")

    #iterate through users until a user with the corresponding id is found
    curr_user = next((user for user in users if auth_user_id == user['id']), None)

    #if no user has the given id raise an error
    if curr_user == None:
        raise AccessError("Invalid User Id ")
    
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
        token           (string)\   - passes in the unique user token of whoever ran the funtion
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
    user_id = read_token(token)
    users = storage['users']
    channels = storage['channels']
   
    #look through users to see if the given id matches any of their ids
    curr_user = next((user for user in users if user_id == user['id']), None)
    #if the given id is not found in users then spit out error message
    if curr_user == None:
        raise AccessError("Invalid User Id ")
    if 1 > len(name) > 20:
        raise InputError("Channel Name Is Invalid")
    
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
    
