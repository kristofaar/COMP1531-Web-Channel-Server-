from src.data_store import data_store
from src.error import InputError
from src.error import AccessError
from src.other import read_token, check_if_valid
import re
import hashlib, jwt

MIN_QUERY_STR_LENGTH = 1
MAX_QUERY_STR_LENGTH = 1000

def search_v1(token, query_str):
    '''
    Given a query string, return a collection of messages 
    in all of the channels/DMs that the user has joined 
    that contain the query (case-insensitive). 
    There is no expected order for these messages.

    Arguments:
        token (str)       - The user's session token.
        query_str (str)   - The string being searched for.

    Exceptions:
        AccessError - Occurs when token does not refer to a valid session.
        InputError  - Occurs when length of query_str is not between 1 and 1000 characters inclusive.

    Return Value:
        Returns the search results as a list of messages.
    '''

    store = data_store.get()
    users = store['users']
    channels = store["channels"]

    # Check valid token
    if not check_if_valid(token):
        raise AccessError(description="Invalid token")

    # Check valid query string
    if not MIN_QUERY_STR_LENGTH <= len(query_str) <= MAX_QUERY_STR_LENGTH:
        raise InputError(description="Invalid query string length")

    # Store search results as a list of messages
    messages = []

    # Get user ID from token
    u_id = read_token(token)
    user = None
    for i in users:
        if u_id == i['id']:
            user = i

    # Check all channels the user is a part of
    for user_channel in user['channels']:
        for channel in channels:
            if user_channel['channel_id'] == channel['channel_id_and_name']['channel_id']:
                for message in channel["messages"]:
                    lower_query_str = query_str.lower()
                    lower_message = message["message"].lower()
                    if lower_query_str in lower_message:
                        messages.append(message)

    return {
        "messages": messages,
    }
