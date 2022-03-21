from src.data_store import data_store
from src.error import InputError
from src.error import AccessError
from src.other import create_token, read_token, check_if_valid, generate_new_session_id, owner_perms
from datetime import timezone
import datetime
import hashlib, jwt

SECRET = 'heheHAHA111'

def message_send_v1(token, channel_id, message):
    '''
    Send a message from the authorised user to the channel specified by channel_id. 
    Note: Each message should have its own unique ID, i.e. no messages should share an ID with another message, 
    even if that other message is in a different channel.

    Arguments:
        token (String)        - passes in the unique session token of whoever ran the funtion
        channel_id   (int)    - passes in the unique channel id of the channel we are enquiring about
        message (String)      - message being sent

    Exceptions:
        InputError when:
            channel_id does not refer to a valid channel
            length of message is less than 1 or over 1000 characters
        AccessError when:
            token is invalid
            channel_id is valid and the authorised user is not a member of the channel

    Return Value:
        Returns unique message_id.
    '''

    if not check_if_valid(token):
        raise AccessError
    
    #staging variables
    storage = data_store.get()
    auth_user_id = read_token(token)

    channels = storage['channels']
    users = storage['users']
    
    #search through channels by id until id is matched
    ch = next((channel for channel in channels if channel_id == channel['channel_id_and_name']['channel_id']), None)
    if ch == None:
        raise InputError("Invalid Channel Id")

    #check if auth_user_id is a member of the channel queried
    if auth_user_id not in ch['members']:
        raise AccessError("Unauthorised User: User is not in channel")

    if not 1 <= len(message) <= 1000:
        raise InputError("Invalid message length")

    # Getting the current date
    # and time
    datet = datetime.datetime.now(timezone.utc)

    time = datet.replace(tzinfo=timezone.utc)
    time_sent = time.timestamp()

    #using session id generator to create unique message id
    message_id = generate_new_session_id()

    #inserting message
    message_dict = {
        'message_id': message_id,
        'u_id': auth_user_id,
        'message': message,
        'time_sent': time_sent,
    }
    ch['messages'].insert(0, message_dict)
    data_store.set(storage)
    return {
        'message_id': message_id
    }

def message_edit_v1(token, message_id, message):
    '''
    Given a message, update its text with new text. If the new message is an empty string, the message is deleted.

    Arguments:
        token (String)        - passes in the unique session token of whoever ran the funtion
        message_id   (int)    - passes in the unique message id of the message we are enquiring about
        message (String)      - new message

    Exceptions:
        InputError when any of:
      
            length of message is over 1000 characters
            message_id does not refer to a valid message within a channel/DM that the authorised user has joined
        
        AccessError when message_id refers to a valid message in a joined channel/DM and none of the following are true:
        
            the message was sent by the authorised user making this request
            the authorised user has owner permissions in the channel/DM

    Return Value:
        Nothing.
    '''

    if not check_if_valid(token):
        raise AccessError
    
    #staging variables
    storage = data_store.get()
    auth_user_id = read_token(token)

    users = storage['users']
    channels = storage['channels']
    
    #search through channels by id until id is matched
    msg = None
    ch = None
    for user_channel in users['channels']:
        ch = next((channel for channel in channels if user_channel['channel_id'] == channel['channel_id_and_name']['channel_id']), None)
        msg = next((mssg for mssg in ch['messages'] if message_id == mssg['message_id']), None)
        if msg != None:
            break
    
    if not msg:
        raise InputError('Invalid message id')
    
    if msg['u_id'] != auth_user_id and not owner_perms(auth_user_id, ch['channel_id_and_name']['channel_id']):
        raise AccessError("Unauthorised editor")

    if len(message) > 1000:
        raise InputError("Invalid message length")

    #editing message
    if len(message) == 0:
        ch['messages'].remove(msg)
    else:
        msg['message'] = message
    data_store.set(storage)
    return {}

def message_remove_v1(token, message_id):
    '''
    Given a message_id for a message, this message is removed from the channel/DM

    Arguments:
        token (String)        - passes in the unique session token of whoever ran the funtion
        message_id   (int)    - passes in the unique message id of the message we are enquiring about
        message (String)      - new message

    Exceptions:
        InputError when any of:
      
            length of message is over 1000 characters
            message_id does not refer to a valid message within a channel/DM that the authorised user has joined
        
        AccessError when message_id refers to a valid message in a joined channel/DM and none of the following are true:
        
            the message was sent by the authorised user making this request
            the authorised user has owner permissions in the channel/DM

    Return Value:
        Nothing.
    '''

    if not check_if_valid(token):
        raise AccessError
    
    #staging variables
    storage = data_store.get()
    auth_user_id = read_token(token)

    users = storage['users']
    channels = storage['channels']
    
    #search through channels by id until id is matched
    msg = None
    ch = None
    for user_channel in users['channels']:
        ch = next((channel for channel in channels if user_channel['channel_id'] == channel['channel_id_and_name']['channel_id']), None)
        msg = next((mssg for mssg in ch['messages'] if message_id == mssg['message_id']), None)
        if msg != None:
            break
    
    if not msg:
        raise InputError('Invalid message id')
    
    if msg['u_id'] != auth_user_id and not owner_perms(auth_user_id, ch['channel_id_and_name']['channel_id']):
        raise AccessError("Unauthorised editor")

    #deleting message
    ch['messages'].remove(msg)
    data_store.set(storage)
    return {}