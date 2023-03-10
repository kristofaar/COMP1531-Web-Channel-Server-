from src.data_store import data_store
from src.error import InputError
from src.error import AccessError
from src.other import read_token, check_if_valid
from src import config
import re
import hashlib, jwt
import urllib.request
import sys
from PIL import Image
import requests
from pathlib import Path

MIN_NAME_LENGTH = 1
MAX_NAME_LENGTH = 50
MIN_HANDLE_LENGTH = 3
MAX_HANDLE_LENGTH = 20

def users_all_v1(token):
    '''
    Returns a list of all users and their associated details

    Arguments:
        token  (string)    - passes in the unique user token of whoever ran the funtion

    Exceptions:
        AccessError  - Occurs when invalid token was passed in

    Return Value:
        Returns list of users with u_id, email, name_first, name_last, handle_str
    '''
    #staging variables
    storage = data_store.get()
    if not check_if_valid(token):
        raise AccessError(description="Invalid token")
    users = storage['users']
    
    #append user data dictionary to list
    output = []
    for user in users:
        output.append({"u_id": user["id"], 
                       "email": user["email"], 
                       "name_first": user["name_first"],
                       "name_last": user["name_last"],
                       "handle_str": user["handle"]})
    return {"users": output}

def user_profile_v1(token, u_id):
    '''
    For a valid user, returns associated details about the user.

    Arguments:
        token (str) - The user's session token.
        u_id (int)  - The user's user ID.

    Exceptions:
        AccessError - Occurs when token does not refer to a valid session.
        InputError  - Occurs when u_id does not refer to a valid user.

    Return Value:
        Returns information about a user's user_id, email, first name, last name, and handle when given a valid user u_id.
    '''

    store = data_store.get()
    users = store["users"]
    removed_users = store["removed_users"]

    # Check valid token
    if not check_if_valid(token):
        raise AccessError(description="Invalid token")

    for user in users:
        if user["id"] == int(u_id):
            return {'user': 
                {
                "u_id": user["id"], 
                "email": user["email"], 
                "name_first": user["name_first"],
                "name_last": user["name_last"],
                "handle_str": user["handle"]
                }
            }

    for removed_user in removed_users:
        if removed_user["id"] == int(u_id):
            return {'user': 
                {
                "u_id": removed_user["id"], 
                "email": removed_user["email"], 
                "name_first": "Removed",
                "name_last": "user",
                "handle_str": removed_user["handle"]
                }
            }

    # Check valid user ID
    raise InputError(description="Invalid user ID")

def user_profile_setname_v1(token, name_first, name_last):
    '''
    Update the authorised user's first and last name.

    Arguments:
        token (str)       - The user's session token.
        name_first (str)  - The user's first name.
        name_last (str)   - The user's last name.

    Exceptions:
        AccessError - Occurs when token does not refer to a valid session.
        InputError  - Occurs when length of name_first is not between 1 and 50 characters inclusive.
        InputError  - Occurs when length of name_last is not between 1 and 50 characters inclusive.

    Return Value:
        Returns nothing.
    '''

    store = data_store.get()
    users = store["users"]

    # Check valid token
    if not check_if_valid(token):
        raise AccessError(description="Invalid token")

    # Check valid first and last name inputs
    if not MIN_NAME_LENGTH <= len(name_first) <= MAX_NAME_LENGTH:
        raise InputError(description="Invalid first name length")
    if not MIN_NAME_LENGTH <= len(name_last) <= MAX_NAME_LENGTH:
        raise InputError(description="Invalid last name length")

    # Get user ID from token
    u_id = read_token(token)

    for user in users:
        if user["id"] == u_id:
            user["name_first"] = name_first
            user["name_last"] = name_last
    data_store.set(store)
    return {}

def user_profile_setemail_v1(token, email):
    '''
    Update the authorised user's email address.

    Arguments:
        token (str)  - The user's session token.
        email (str)  - The user's email.

    Exceptions:
        AccessError - Occurs when token does not refer to a valid session.
        InputError  - Occurs when email entered is not in correct format (section 6.4).
        InputError  - Occurs when email address is already being used by another user.

    Return Value:
        Returns nothing.
    '''

    store = data_store.get()
    users = store["users"]

    # Check valid token
    if not check_if_valid(token):
        raise AccessError(description="Invalid token")

    # Check valid email
    if not re.search(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$', email):
        raise InputError(description="Invalid email")

    # Check duplicate email
    for user in users:
        if user["email"] == email:
            raise InputError(description="User email already exists")

    # Get user ID from token
    u_id = read_token(token)

    for user in users:
        if user["id"] == u_id:
            user["email"] = email
    data_store.set(store)
    return {}

def user_profile_sethandle_v1(token, handle_str):
    '''
    Update the authorised user's handle (i.e. display name).

    Arguments:
        token (str)       - The user's session token.
        handle_str (str)  - The user's display name.

    Exceptions:
        AccessError - Occurs when token does not refer to a valid session.
        InputError  - Occurs when length of handle_str is not between 3 and 20 characters inclusive.
        InputError  - Occurs when handle_str contains characters that are not alphanumeric.
        InputError  - Occurs when the handle is already being used by another user.

    Return Value:
        Returns nothing.
    '''

    store = data_store.get()
    users = store["users"]

    # Check valid token
    if not check_if_valid(token):
        raise AccessError(description="Invalid token")

    # Check valid handle length
    if not MIN_HANDLE_LENGTH <= len(handle_str) <= MAX_HANDLE_LENGTH:
        raise InputError(description="Invalid handle length")

    # Check valid handle input
    if not handle_str.isalnum():
        raise InputError(description="Invalid handle input")
    
    # Check duplicate handle
    for user in users:
        if user["handle"] == handle_str:
            raise InputError(description="User handle already exists")

    # Get user ID from token
    u_id = read_token(token)

    for user in users:
        if user["id"] == u_id:
            user["handle"] = handle_str
    data_store.set(store)
    return {}

#functions to change: messageshare, messagesendlater, messagesendlaterdm, standup
def user_stats_v1(token):
    '''
    Fetches the required statistics about this user's use of UNSW Seams.

    Arguments:
        token (str)       - The user's session token.

    Exceptions:
        AccessError - Occurs when token does not refer to a valid session.

    Return Value:
        user_stats        - Dictionary of shape {
                            channels_joined: [{num_channels_joined, time_stamp}],
                            dms_joined: [{num_dms_joined, time_stamp}], 
                            messages_sent: [{num_messages_sent, time_stamp}], 
                            involvement_rate 
                            }.
    '''
    store = data_store.get()
    users = store["users"]
    channels = store['channels']
    dms = store['dms']

    # Check valid token
    if not check_if_valid(token):
        raise AccessError(description="Invalid token")

    # Get user ID from token
    u_id = read_token(token)

    user = None
    for usa in users:
        if usa['id'] == u_id:
            user = usa
    
    ch_joined = user['user_stats']['channels_joined'][len(user['user_stats']['channels_joined']) - 1]['num_channels_joined']
    dm_joined = user['user_stats']['dms_joined'][len(user['user_stats']['dms_joined']) - 1]['num_dms_joined']
    msg_sent = user['user_stats']['messages_sent'][len(user['user_stats']['messages_sent']) - 1]['num_messages_sent']
    tot_msg_sent = 0
    for channel in channels:
        tot_msg_sent += len(channel['messages'])
    for dm in dms:
        tot_msg_sent += len(dm['messages'])
    if len(channels) + len(dms) + tot_msg_sent == 0:
        user['user_stats']['involvement_rate'] = 0
    else:
        user['user_stats']['involvement_rate'] = (ch_joined + dm_joined + msg_sent) / (len(channels) + len(dms) + tot_msg_sent)
    
    if user['user_stats']['involvement_rate'] > 1:
        user['user_stats']['involvement_rate'] = 1
    data_store.set(store)
    return user['user_stats']

def users_stats_v1(token):
    '''
    Fetches the required statistics about the use of UNSW Seams.

    Arguments:
        token (str)       - The user's session token.

    Exceptions:
        AccessError - Occurs when token does not refer to a valid session.

    Return Value:
        workspace_stats     - Dictionary of shape Dictionary of shape {
                              channels_exist: [{num_channels_exist, time_stamp}], 
                              dms_exist: [{num_dms_exist, time_stamp}], 
                              messages_exist: [{num_messages_exist, time_stamp}], 
                              utilization_rate 
                              }
    '''
    store = data_store.get()
    users = store["users"]
    workspace_stats = store['workspace_stats']

    # Check valid token
    if not check_if_valid(token):
        raise AccessError(description="Invalid token")
    
    num_users_who_have_joined_at_least_one_channel_or_dm = 0
    for user in users:
        if user['channels'] != [] or user['dms'] != []:
            num_users_who_have_joined_at_least_one_channel_or_dm += 1
    
    workspace_stats['utilization_rate'] = num_users_who_have_joined_at_least_one_channel_or_dm / len(users)

    data_store.set(store)
    return workspace_stats

def user_profile_uploadphoto_v1(token, img_url, x_start, y_start, x_end, y_end):
    store = data_store.get()
    users = store["users"]

    # Check valid token
    if not check_if_valid(token):
        raise AccessError(description="Invalid token")

    # Check valid HTTP status of img_url
    if requests.head(img_url).status_code != 200:
        raise InputError(description="img_url returns an HTTP status other than 200")

    # Check valid image format
    image_formats = ("image/jpeg", "image/jpg")
    if requests.head(img_url).headers["content-type"] not in image_formats:
        raise InputError(description="Invalid image format")

    # Get user ID from token and user from user ID
    u_id = read_token(token)
    user = None
    for i in users:
        if u_id == i["id"]:
            user = i

    # Specify file path for fetching image
    file_path = "static/" + str(u_id) + "_PFP.jpg"

    # Fetch image via URL
    urllib.request.urlretrieve(img_url, file_path)

    # Open the image to crop
    image_object = Image.open(file_path)
    width, height = image_object.size

    # Check valid dimensions
    if not (0 <= x_start < width) or not (0 <= x_end < width):
        raise InputError(description="Invalid width dimensions")
    if not (0 <= y_start < height) or not (0 <= y_end < height):
        raise InputError(description="Invalid height dimensions")
    if x_end <= x_start or y_end <= y_start:
        raise InputError(description="Invalid dimension input(s)")

    # Crop the image
    cropped = image_object.crop((x_start, y_start, x_end, y_end))
    cropped.save(file_path)

    # Set the user's profile image URL as the cropped image URL
    user["profile_img_url"] = config.url + file_path

    return {}
