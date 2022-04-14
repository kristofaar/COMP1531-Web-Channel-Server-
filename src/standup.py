from src.data_store import data_store
from src.error import InputError
from src.error import AccessError
from src.other import read_token, check_if_valid
import datetime
from datetime import timezone
import threading
import time
from src.message import message_send_v1

def standup_start(token, channel_id, length):
    '''
    Starts the standup period for a channel.

    Arguments:
        token       (str) - passes in the unique token of whoever ran the function
        channel_id  (int) - passes in the unique id of the channel user is starting a standup in
        length      (int) - length of the standup in seconds

    Exceptions:
        InputError  - when the channel_id does not refer to a valid channel
                    - when the length is a negative number
                    - an active standup is currently running in the channel
        AccessError - channel_id is valid and the authorised user is not a member of the channel

    Return Value:
        Returns time the standup finishes as a unix timestamp integer
    '''
    #staging variables
    storage = data_store.get()
    
    if not check_if_valid(token):
        raise AccessError(description="Invalid token")

    channels = storage['channels']

    # search through channels by id until id is matched
    ch = next((channel for channel in channels if int(channel_id) ==
              channel['channel_id_and_name']['channel_id']), None)
    if ch == None:
        raise InputError(description="Invalid Channel Id")

    if int(length) < 0:
        raise InputError(description="Length is a negative number")

    if standup_active(token, channel_id)['is_active']:
        raise InputError(description="An active standup is currently running in this channel")

    #fetch current time
    dt = datetime.datetime.now(timezone.utc)
    utc_time = dt.replace(tzinfo=timezone.utc)
    utc_timestamp = int(utc_time.timestamp())
    
    time_finish = utc_timestamp + int(length)
    ch['standup_time'] = time_finish
    data_store.set(storage)

    def thread_standup(channel_id, length):
        time.sleep(length)
        #print(ch['standup_message'])
        if ch['standup_message']:
            message_send_v1(token, channel_id, ch['standup_message'])
        #print(ch["messages"])
        ch["standup_time"] = 0
        ch["standup_message"] = ""
        data_store.set(storage)

    x = threading.Thread(target=thread_standup, args=(channel_id, length,))
    x.start()
    
    return {"time_finish": time_finish}

def standup_active(token, channel_id):
    '''
    Checks whether there is an active standup in a channel.

    Arguments:
        token       (str) - passes in the unique token of whoever ran the function
        channel_id  (int) - passes in the unique id of the channel user is checking for standup in

    Exceptions:
        InputError  - when the channel_id does not refer to a valid channel
        AccessError - channel_id is valid and the authorised user is not a member of the channel

    Return Value:
        Returns whether or not there is an active standup in the channel and when the standup will finish
    '''
    #staging variables
    storage = data_store.get()

    if not check_if_valid(token):
        raise AccessError(description="Invalid token")
    auth_user_id = read_token(token)

    channels = storage['channels']

    # search through channels by id until id is matched
    ch = next((channel for channel in channels if int(channel_id) ==
              channel['channel_id_and_name']['channel_id']), None)
    if ch == None:
        raise InputError(description="Invalid Channel Id")

    if auth_user_id not in ch["members"]:
        raise AccessError(description="Authorised user is not a member of the channel")
        
    dt = datetime.datetime.now(timezone.utc)
    utc_time = dt.replace(tzinfo=timezone.utc)
    utc_timestamp = utc_time.timestamp()

    if utc_timestamp < ch["standup_time"]:
        is_active = True
        time_finish = ch["standup_time"]
    else:
        is_active = False
        time_finish = None

    return {"is_active": is_active, "time_finish": time_finish}

def standup_send(token, channel_id, message):
    '''
    Sends a message to be buffered in the standup queue, assuming a standup is active.

    Arguments:
        token       (str) - passes in the unique token of whoever ran the function
        channel_id  (int) - passes in the unique id of the channel user is starting a standup in
        message     (str) - passes in the message to be added to the standup queue

    Exceptions:
        InputError  - when the channel_id does not refer to a valid channel
                    - length of message is over 1000 characters
                    - an active standup is currently running in the channel
        AccessError - channel_id is valid and the authorised user is not a member of the channel

    Return Value:
        None
    '''
    #staging variables
    storage = data_store.get()
    
    if not check_if_valid(token):
        raise AccessError(description="Invalid token")
    auth_user_id = read_token(token)

    channels = storage['channels']
    users = storage['users']

    # find auth_user
    a_user = None
    for usa in users:
        if usa['id'] == auth_user_id:
            a_user = usa

    # search through channels by id until id is matched
    ch = next((channel for channel in channels if int(channel_id) ==
              channel['channel_id_and_name']['channel_id']), None)
    if ch == None:
        raise InputError(description="Invalid Channel Id")

    if len(message) > 1000:
        raise InputError(description="Length of message is over 1000 characters")

    if ch["standup_time"] == 0:
        raise InputError(description="An active standup is not currently running in the channel")

    if auth_user_id not in ch["members"]:
        raise AccessError(description="Authorised user is not a member of the channel")
    
    ch["standup_message"] += (a_user["handle"]+": "+message+"\n")
    data_store.set(storage)
    return {}