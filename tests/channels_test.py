import pytest

from src.auth import auth_register_v1, auth_login_v1
from src.channels import channels_create_v1,channels_listall_v1,channels_list_v1
from src.error import InputError
from src.error import AccessError
from src.other import clear_v1

@pytest.fixture

def made_one_user():
    clear_v1()
    u_id = auth_register_v1('anemail@email.com', 'verycoolpassword', 'Name', 'Name')['auth_user_id']
    # ch_id1 = channels_create_v1(u_id, 'public', True)['channel_id'] , 'ch_id1': ch_id1
    return {'u_id': u_id}

#Error tests
def test_channel_create_empty_id(made_one_user):
    with pytest.raises(InputError):
        channels_create_v1(None,"name",True)

def test_channel_create_none_name(made_one_user):
    with pytest.raises(InputError):
        channels_create_v1(made_one_user['u_id'],None,True)

def test_channel_create_empty_is_public(made_one_user):
    with pytest.raises(InputError):
        channels_create_v1(made_one_user['u_id'],'name',None) 

def test_channel_create_empty_all(made_one_user):
    with pytest.raises(InputError):
        channels_create_v1(None,None,None)

def test_channel_create_invalid_user_id(made_one_user):
    with pytest.raises(AccessError):
        channels_create_v1(made_one_user['u_id'] + 1, "name", True)

def test_channel_create_channel_name_too_long(made_one_user):
    with pytest.raises(InputError):
        channels_create_v1(made_one_user['u_id'], "thelengthofthisnameisover20characters", True)

def test_channel_create_channel_name_too_short(made_one_user):
    with pytest.raises(InputError):
        channels_create_v1(made_one_user['u_id'], "", True)

def test_channel_list_invalid_user():
    clear_v1()
    with pytest.raises(AccessError):
        channels_list_v1(1)

def test_chanel_list_empty_id():
    clear_v1()
    with pytest.raises(InputError):
        channels_list_v1(None)

def test_channel_listall_invalid_user():
    clear_v1()
    with pytest.raises(AccessError):
        channels_listall_v1(1)

def test_chanel_listall_empty_id():
    clear_v1()
    with pytest.raises(InputError):
        channels_listall_v1(None)
#Working tests
def test_register_and_create_channel(made_one_user):
    channel_return = channels_create_v1(made_one_user['u_id'], 'coolname', True)['channel_id']
    channel_list = channels_list_v1(made_one_user['u_id'])['channels']
    assert channel_return == channel_list[0]['channel_id']

def test_register_and_create_multiple_channels(made_one_user):
    u_id2 = auth_register_v1('random@email.com', 'verycoolpassword', 'Name', 'Name')['auth_user_id'] # second user

    channel_return1 = channels_create_v1(made_one_user['u_id'], 'coolname', True)['channel_id']
    channel_return2 = channels_create_v1(u_id2, 'coolname2', True)['channel_id']
    channel_list1 = channels_list_v1(made_one_user['u_id'])['channels']
    channel_list2 = channels_list_v1(u_id2)['channels']

    assert channel_return1 == channel_list1[0]['channel_id'] and channel_return2 == channel_list2[0]['channel_id']

def test_channels_list(made_one_user):
    channel_return1 = channels_create_v1(made_one_user['u_id'], 'coolname', True)['channel_id']

    channel_list = channels_list_v1(made_one_user['u_id'])
    assert channel_list['channels'] == [{'channel_id': channel_return1, 'name': 'coolname'}]

def test_mutliple_channels_list(made_one_user):
    channel_return1 = channels_create_v1(made_one_user['u_id'], 'coolname', True)['channel_id']
    channel_return2 = channels_create_v1(made_one_user['u_id'], 'coolname2', True)['channel_id']

    channel_list = channels_list_v1(made_one_user['u_id'])
    assert channel_list['channels'] == [{'channel_id': channel_return1, 'name': 'coolname'}, {'channel_id': channel_return2, 'name': 'coolname2'}]

def test_mutliple_users_list(made_one_user):
    u_id2 = auth_register_v1('random@email.com', 'verycoolpassword', 'Name', 'Name')['auth_user_id']

    channel_return1 = channels_create_v1(made_one_user['u_id'], 'coolname', True)['channel_id'] 
    channel_return2 = channels_create_v1(u_id2, 'coolname2', True)['channel_id']

    channel_list = channels_list_v1(made_one_user['u_id'])
    assert channel_list['channels'] == [{'channel_id': channel_return1, 'name': 'coolname'}]

def test_channels_listall(made_one_user):
    channel_return1 = channels_create_v1(made_one_user['u_id'], 'coolname', True)['channel_id']

    channel_list = channels_listall_v1(made_one_user['u_id'])
    assert channel_list['channels'] == [{'channel_id': channel_return1, 'name': 'coolname'}]

def test_mutliple_channels_listall(made_one_user):
    channel_return1 = channels_create_v1(made_one_user['u_id'], 'coolname', True)['channel_id']
    channel_return2 = channels_create_v1(made_one_user['u_id'], 'coolname2', True)['channel_id']

    channel_list = channels_listall_v1(made_one_user['u_id'])
    assert channel_list['channels'] == [{'channel_id': channel_return1, 'name': 'coolname'}, {'channel_id': channel_return2, 'name': 'coolname2'}]

def test_mutliple_users_listall(made_one_user):
    channel_return1 = channels_create_v1(made_one_user['u_id'], 'coolname', True)['channel_id']

    u_id2 = auth_register_v1('random@email.com', 'verycoolpassword', 'Name', 'Name')['auth_user_id'] 
    channel_return2 = channels_create_v1(u_id2, 'coolname2', True)['channel_id']

    channel_list = channels_listall_v1(made_one_user['u_id'])
    assert channel_list['channels'] == [{'channel_id': channel_return1, 'name': 'coolname'}, {'channel_id': channel_return2, 'name': 'coolname2'}]

def test_listall(made_one_user):
    channel_list = channels_listall_v1(made_one_user['u_id'])
    assert channel_list['channels'] == []