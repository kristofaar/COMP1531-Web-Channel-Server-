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

