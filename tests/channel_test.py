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

def test_channel_list_details_public_private():
    clear_v1()
    auth_register_v1('anemail@email.com', 'verycoolpassword', 'Name', 'Name')
    channels_create_v1(1, 'public', True)
    channels_create_v1(1, 'private', False)

    storage = data_store.get()
    users = storage['users']
    channels = storage['channels']
    for channel in channels:
        if channel['name'] == 'public':
            assert channel['is_public'] == True
        elif channel['name'] == 'private':
            assert channel['is_public'] == False