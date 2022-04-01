from src.data_store import data_store
from src.error import InputError
from src.error import AccessError
from src.other import read_token, check_if_valid
import datetime

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
    return {"time_finish"}

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
    return {"is_active", "time_finish"}

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
    return {}