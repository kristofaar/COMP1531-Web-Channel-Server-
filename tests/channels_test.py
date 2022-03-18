import pytest

from src.auth import auth_register_v1, auth_login_v1
from src.channels import channels_create_v1,channels_listall_v1,channels_list_v1
from src.error import InputError
from src.error import AccessError
from src.other import clear_v1

@pytest.fixture

def made_one_user():
    clear_v1()
    token = auth_register_v1('anemail@email.com', 'verycoolpassword', 'Name', 'Name')['token']
    # ch_id1 = channels_create_v1(u_id, 'public', True)['channel_id'] , 'ch_id1': ch_id1
    return {'token': token}

#Error tests
def test_channel_create_empty_id(made_one_user):
    with pytest.raises(InputError):
        channels_create_v1(None,"name",True)

def test_channel_create_none_name(made_one_user):
    with pytest.raises(InputError):
        channels_create_v1(made_one_user['token'],None,True)

def test_channel_create_empty_is_public(made_one_user):
    with pytest.raises(InputError):
        channels_create_v1(made_one_user['token'],'name',None) 

def test_channel_create_empty_all(made_one_user):
    with pytest.raises(InputError):
        channels_create_v1(None,None,None)
'''
def test_channel_create_invalid_user_id(made_one_user):
    with pytest.raises(AccessError):
        channels_create_v1(made_one_user['u_id'] + 1, "name", True)
'''
def test_channel_create_channel_name_too_long(made_one_user):
    with pytest.raises(InputError):
        channels_create_v1(made_one_user['token'], "thelengthofthisnameisover20characters", True)

def test_channel_create_channel_name_too_short(made_one_user):
    with pytest.raises(InputError):
        channels_create_v1(made_one_user['token'], "", True)

def test_channel_list_invalid_user():
    clear_v1()
    with pytest.raises(AccessError):
        channels_list_v1('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c')

def test_chanel_list_empty_id():
    clear_v1()
    with pytest.raises(InputError):
        channels_list_v1(None)

def test_channel_listall_invalid_user():
    clear_v1()
    with pytest.raises(AccessError):
        channels_listall_v1('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c')

def test_chanel_listall_empty_id():
    clear_v1()
    with pytest.raises(InputError):
        channels_listall_v1(None)
#Working tests
def test_register_and_create_channel(made_one_user):
    channel_return = channels_create_v1(made_one_user['token'], 'coolname', True)['channel_id']
    channel_list = channels_list_v1(made_one_user['token'])['channels']
    assert channel_return == channel_list[0]['channel_id']

def test_register_and_create_multiple_channels(made_one_user):
    token2 = auth_register_v1('random@email.com', 'verycoolpassword', 'Name', 'Name')['token'] # second user

    channel_return1 = channels_create_v1(made_one_user['token'], 'coolname', True)['channel_id']
    channel_return2 = channels_create_v1(token2, 'coolname2', True)['channel_id']
    channel_list1 = channels_list_v1(made_one_user['token'])['channels']
    channel_list2 = channels_list_v1(token2)['channels']

    assert channel_return1 == channel_list1[0]['channel_id'] and channel_return2 == channel_list2[0]['channel_id']

def test_channels_list(made_one_user):
    channel_return1 = channels_create_v1(made_one_user['token'], 'coolname', True)['channel_id']

    channel_list = channels_list_v1(made_one_user['token'])
    assert channel_list['channels'] == [{'channel_id': channel_return1, 'name': 'coolname'}]

def test_mutliple_channels_list(made_one_user):
    channel_return1 = channels_create_v1(made_one_user['token'], 'coolname', True)['channel_id']
    channel_return2 = channels_create_v1(made_one_user['token'], 'coolname2', True)['channel_id']

    channel_list = channels_list_v1(made_one_user['token'])
    assert channel_list['channels'] == [{'channel_id': channel_return1, 'name': 'coolname'}, {'channel_id': channel_return2, 'name': 'coolname2'}]

def test_mutliple_users_list(made_one_user):
    channel_return1 = channels_create_v1(made_one_user['token'], 'coolname', True)['channel_id'] 

    channel_list = channels_list_v1(made_one_user['token'])
    assert channel_list['channels'] == [{'channel_id': channel_return1, 'name': 'coolname'}]

def test_channels_listall(made_one_user):
    channel_return1 = channels_create_v1(made_one_user['token'], 'coolname', True)['channel_id']

    channel_list = channels_listall_v1(made_one_user['token'])
    assert channel_list['channels'] == [{'channel_id': channel_return1, 'name': 'coolname'}]

def test_mutliple_channels_listall(made_one_user):
    channel_return1 = channels_create_v1(made_one_user['token'], 'coolname', True)['channel_id']
    channel_return2 = channels_create_v1(made_one_user['token'], 'coolname2', True)['channel_id']

    channel_list = channels_listall_v1(made_one_user['token'])
    assert channel_list['channels'] == [{'channel_id': channel_return1, 'name': 'coolname'}, {'channel_id': channel_return2, 'name': 'coolname2'}]

def test_mutliple_users_listall(made_one_user):
    channel_return1 = channels_create_v1(made_one_user['token'], 'coolname', True)['channel_id']

    token2 = auth_register_v1('random@email.com', 'verycoolpassword', 'Name', 'Name')['token'] 
    channel_return2 = channels_create_v1(token2, 'coolname2', True)['channel_id']

    channel_list = channels_listall_v1(made_one_user['token'])
    assert channel_list['channels'] == [{'channel_id': channel_return1, 'name': 'coolname'}, {'channel_id': channel_return2, 'name': 'coolname2'}]

def test_listall(made_one_user):
    channel_list = channels_listall_v1(made_one_user['token'])
    assert channel_list['channels'] == []

def test_clear_v1_channels(made_one_user):
    channel_return = channels_create_v1(made_one_user['token'], 'coolname', True)['channel_id']
    channel_list = channels_list_v1(made_one_user['token'])['channels']

    clear_v1()
    channel_return = channels_create_v1(made_one_user['token'], 'coolname', True)['channel_id']
    channel_list = channels_list_v1(made_one_user['token'])['channels']
    assert channel_return == channel_list[0]['channel_id']