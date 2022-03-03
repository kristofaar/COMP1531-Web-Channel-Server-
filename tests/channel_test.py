from multiprocessing.sharedctypes import Value
from email import message
import pytest

from src.channels import channels_create_v1,channels_listall_v1,channels_list_v1
from src.channel import channel_details_v1, channel_invite_v1, channel_join_v1, channel_messages_v1
from src.auth import auth_register_v1, auth_login_v1
from src.error import InputError
from src.error import AccessError
from src.other import clear_v1
from src.data_store import data_store

#Error tests
'''
def test_invalid_user_id():
    clear_v1()
    with pytest.raises(InputError):
        channel_invite_v1(0, 1, 1)

def test_invalid_channel_id():
    clear_v1()
    with pytest.raises(AccessError):
        channel_invite_v1(1,0,1)

def test_invalid_user_id():
    clear_v1()
    with pytest.raises(InputError):
        channel_invite_v1(1,1,0)
'''
#Working tests

@pytest.fixture
def one_user_made_two_channels():   # one public and one private, returns both 
    clear_v1()
    auth_register_v1('anemail@email.com', 'verycoolpassword', 'Name', 'Name')
    channels_create_v1(1, 'public', True)
    channels_create_v1(1, 'private', False)
    first_channel_details = channel_details_v1(1, 1)
    second_channel_details = channel_details_v1(1, 2)
    return {'first': first_channel_details, 'second': second_channel_details}

def test_channel_details_check_id(one_user_made_two_channels):
    assert one_user_made_two_channels['first']['id'] == 1
    assert one_user_made_two_channels['second']['id'] == 2

def test_channel_details_check_public_private(one_user_made_two_channels):
    assert one_user_made_two_channels['first']['is_public'] == True
    assert one_user_made_two_channels['second']['is_public']  == False

def test_channel_details_check_name(one_user_made_two_channels):
     assert one_user_made_two_channels['first']['name'] == 'public'
     assert one_user_made_two_channels['second']['name'] == 'private'

def test_channel_details_check_owner(one_user_made_two_channels):
    assert one_user_made_two_channels['first']['owner'][0]['id'] == 1
    assert one_user_made_two_channels['second']['owner'][0]['id'] == 1

def test_channel_details_check_members(one_user_made_two_channels):
    assert one_user_made_two_channels['first']['members'] == [{'channels': [{'id': 1, 'name': 'public'}, {'id': 2, 'name': 'private'}],  'email': 'anemail@email.com',  'handle': 'namename',  'id': 1,  'name_first': 'Name',  'name_last': 'Name'}]
    assert one_user_made_two_channels['second']['members'] == [{'channels': [{'id': 1, 'name': 'public'}, {'id': 2, 'name': 'private'}],  'email': 'anemail@email.com',  'handle': 'namename',  'id': 1,  'name_first': 'Name', 'name_last': 'Name'}]

def test_channel_details_invalid_channel_id(one_user_made_two_channels):
    with pytest.raises(InputError):
        channel_details_v1(1, 5)

def test_channel_details_unauthorised_user(one_user_made_two_channels):     # second user tries accessing first user channels
    auth_register_v1('notanemail@email.com', 'verycoolpassword', 'Second', 'User')
    channels_create_v1(2, 'third_channel', True)    # second user makes a channel (third one in storage)
    with pytest.raises(AccessError):
        channel_details_v1(2, 1)
    with pytest.raises(AccessError):
        channel_details_v1(1,3)             # first user tries accessing second user channels    

# testing channel_join_v1, relies on channel_details working properly
# Most if at all don't work currently, channel_join incomplete

def test_channel_join_new_member_join_valid_channel(one_user_made_two_channels):        
    auth_register_v1('notanemail@email.com', 'verycoolpassword', 'Second', 'User') 
    channel_join_v1(2, 1)   # second user joins channel 1 made by first user
    first_channel_details = channel_details_v1(1, 1)
    members = first_channel_details['members']
    assert members[1]['id'] == 2    # check if second user is member of channel 1 now

def test_channel_join_invalid_user_join_valid_channel(one_user_made_two_channels):
    with pytest.raises(InputError):
        channel_join_v1(2, 1)   # second user not registered yet

def test_channel_join_new_member_joins_invalid_channel(one_user_made_two_channels):     
    auth_register_v1('notanemail@email.com', 'verycoolpassword', 'Second', 'User') 
    with pytest.raises(InputError):
        channel_join_v1(2, 3)       # second user tries joining channel 3 (doesn't exist, only 1 and 2)

def test_channel_join_already_a_member(one_user_made_two_channels):
    auth_register_v1('notanemail@email.com', 'verycoolpassword', 'Second', 'User') 
    channel_join_v1(2, 1)   
    with pytest.raises(InputError):
        channel_join_v1(2, 1)   # second user tries joining channel 1 again

def test_channel_join_new_member_joins_private_channel(one_user_made_two_channels):    
    auth_register_v1('notanemail@email.com', 'verycoolpassword', 'Second', 'User') 
    with pytest.raises(AccessError):
        channel_join_v1(2, 2)   # second user tries joining channel 2, which is private
    
def test_channel_details_multiple_members(one_user_made_two_channels):
    auth_register_v1('notanemail@email.com', 'verycoolpassword', 'Second', 'User') 
    channel_join_v1(2, 1) #second user joins channel 1
    assert channel_details_v1(1,1)['members'] == [{'channels': [{'id': 1, 'name': 'public'}, {'id': 2, 'name': 'private'}],  'email': 'anemail@email.com',  'handle': 'namename',  'id': 1,  'name_first': 'Name',  'name_last': 'Name'}, {'channels': [{'id': 1, 'name': 'public'}],  'email': 'notanemail@email.com',  'handle': 'seconduser',  'id': 2,  'name_first': 'Second',  'name_last': 'User'}]

def test_channel_invite_member(one_user_made_two_channels):
    auth_register_v1('notanemail@email.com', 'verycoolpassword', 'Second', 'User') 
    channel_invite_v1(1,1,2) # invite second user to channel 1
    assert channel_details_v1(1,1)['members'] == [{'channels': [{'id': 1, 'name': 'public'}, {'id': 2, 'name': 'private'}],  'email': 'anemail@email.com',  'handle': 'namename',  'id': 1,  'name_first': 'Name',  'name_last': 'Name'}, {'channels': [{'id': 1, 'name': 'public'}],  'email': 'notanemail@email.com',  'handle': 'seconduser',  'id': 2,  'name_first': 'Second',  'name_last': 'User'}]

def test_channel_messages_invalid_channel_id():
    clear_v1()
    auth_register_v1('anemail@email.com', 'verycoolpassword', 'Name', 'Name')
    channels_create_v1(1, 'channelName', True)
    with pytest.raises(InputError):
        channel_messages_v1(1, 3, 0)

def test_channel_messages_invalid_channel_id_empty():
    clear_v1()
    auth_register_v1('anemail@email.com', 'verycoolpassword', 'Name', 'Name')
    with pytest.raises(InputError):
        channel_messages_v1(1, 3, 0)

'''def test_channel_messages_invalid_start():
    clear_v1()
    auth_register_v1('anemail@email.com', 'verycoolpassword', 'Name', 'Name')
    channels_create_v1(1, 'channelName', True)
    storage = data_store.get()
    storage['channels'][0]['messages'].append({'message_id': 1, 'u_id': 1, 'message': 'HIIII', 'time_sent': 1615975803.787904})
    with pytest.raises(InputError):
        channel_messages_v1(1, 1, 1)'''

def test_channel_messages_unauthorised_user():
    clear_v1()
    auth_register_v1('anemail@email.com', 'verycoolpassword', 'Name', 'Name')
    auth_register_v1('anemail1@email.com', 'verycoolpassword', 'Name', 'Name')
    channels_create_v1(1, 'channelName', True)
    with pytest.raises(AccessError):
        channel_messages_v1(2, 1, 0)

def test_channel_messages_invalid_user():
    clear_v1()
    auth_register_v1('anemail@email.com', 'verycoolpassword', 'Name', 'Name')
    channels_create_v1(1, 'channelName', True)
    with pytest.raises(AccessError):
        channel_messages_v1(2, 1, 0)

def test_channel_messages_double_error1():
    clear_v1()
    auth_register_v1('anemail@email.com', 'verycoolpassword', 'Name', 'Name')
    channels_create_v1(1, 'channelName', True)
    with pytest.raises(AccessError):
        channel_messages_v1(2, 1, 3)

def test_channel_messages_double_error1():
    clear_v1()
    auth_register_v1('anemail@email.com', 'verycoolpassword', 'Name', 'Name')
    channels_create_v1(1, 'channelName', True)
    with pytest.raises(AccessError):
        channel_messages_v1(2, 2, 3)


#Working tests

def test_channel_messages_empty():
    clear_v1()
    auth_register_v1('anemail@email.com', 'verycoolpassword', 'Name', 'Name')
    channels_create_v1(1, 'channelName', True)
    assert channel_messages_v1(1, 1, 0) == {'messages': [], 'start': 0, 'end': -1}

'''def test_channel_messages_twenty():
    clear_v1()
    auth_register_v1('anemail@email.com', 'verycoolpassword', 'Name', 'Name')
    channels_create_v1(1, 'channelName', True)
    storage = data_store.get()

    for i in range(20):
        storage['channels'][0]['messages'].append(i)
    assert channel_messages_v1(1, 1, 0) == {'messages': list(range(20)), 'start': 0, 'end': -1}

def test_channel_messages_sixty():
    clear_v1()
    auth_register_v1('anemail@email.com', 'verycoolpassword', 'Name', 'Name')
    channels_create_v1(1, 'channelName', True)
    storage = data_store.get()

    for i in range(60):
        storage['channels'][0]['messages'].append(i)
    assert channel_messages_v1(1, 1, 0) == {'messages': list(range(50)), 'start': 0, 'end': 50}

def test_channel_messages_sixty_start_15():
    clear_v1()
    auth_register_v1('anemail@email.com', 'verycoolpassword', 'Name', 'Name')
    channels_create_v1(1, 'channelName', True)
    storage = data_store.get()

    for i in range(60):
        storage['channels'][0]['messages'].append(i)
    assert channel_messages_v1(1, 1, 15) == {'messages': list(range(15, 60)), 'start': 15, 'end': -1}'''
