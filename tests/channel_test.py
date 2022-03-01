import pytest

from src.channels import channels_create_v1,channels_listall_v1,channels_list_v1
from src.channel import channel_details_v1, channel_invite_v1, channel_join_v1, channel_messages_v1
from src.auth import auth_register_v1, auth_login_v1
from src.error import InputError
from src.error import AccessError
from src.other import clear_v1

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
    assert one_user_made_two_channels['first']['owner_members'][0]['id'] == 1
    assert one_user_made_two_channels['second']['owner_members'][0]['id'] == 1

def test_channel_details_check_members(one_user_made_two_channels):
    assert one_user_made_two_channels['first']['all_members'] == [{'email': 'anemail@email.com',
                                                                   'handle': 'namename',
                                                                   'id': 1,
                                                                   'name_first': 'Name',
                                                                   'name_last': 'Name'}]
    assert one_user_made_two_channels['second']['all_members'] == [{'email': 'anemail@email.com',
                                                                   'handle': 'namename',
                                                                   'id': 1,
                                                                   'name_first': 'Name',
                                                                   'name_last': 'Name'}]

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

#def two_users_each_make_channel():
    
