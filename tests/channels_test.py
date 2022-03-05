import pytest

from src.auth import auth_register_v1, auth_login_v1
from src.channels import channels_create_v1,channels_listall_v1,channels_list_v1
from src.error import InputError
from src.error import AccessError
from src.other import clear_v1

@pytest.fixture

def made_one_user():
    clear_v1()
    auth_register_v1('anemail@email.com', 'verycoolpassword', 'Name', 'Name')

#Error tests
def test_channel_create_empty_id(made_one_user):
    with pytest.raises(InputError):
        channels_create_v1(None,"name",True)

def test_channel_create_none_name(made_one_user):
    with pytest.raises(InputError):
        channels_create_v1(1,None,True)

def test_channel_create_empty_is_public(made_one_user):
    with pytest.raises(InputError):
        channels_create_v1(1,'name',None) 

def test_channel_create_empty_all(made_one_user):
    with pytest.raises(InputError):
        channels_create_v1(None,None,None)

def test_channel_create_invalid_user_id(made_one_user):
    with pytest.raises(AccessError):
        channels_create_v1(0, "name", True)

def test_channel_create_channel_name_too_long(made_one_user):
    with pytest.raises(InputError):
        channels_create_v1(1, "thelengthofthisnameisover20characters", True)

def test_channel_create_channel_name_too_short(made_one_user):
    with pytest.raises(InputError):
        channels_create_v1(1, "", True)

def test_channel_list_invalid_user(made_one_user):
    with pytest.raises(AccessError):
        channels_list_v1(2) # no second user

#Working tests
def test_register_and_create_channel(made_one_user):
    channel_return = channels_create_v1(1, 'coolname', True)

    assert channel_return == {'channel_id' : 1}

def test_register_and_create_multiple_channels(made_one_user):
    auth_register_v1('random@email.com', 'verycoolpassword', 'Name', 'Name') # second user

    channel_return1 = channels_create_v1(1, 'coolname', True) 
    channel_return2 = channels_create_v1(2, 'coolname2', True)

    assert channel_return1 == {'channel_id' : 1} and channel_return2 == {'channel_id' : 2}

def test_channels_list(made_one_user):
    channel_return1 = channels_create_v1(1, 'coolname', True)

    channel_list = channels_list_v1(1)
    assert channel_list == {'channels': [{'channel_id': 1, 'name': 'coolname'}]}

def test_mutliple_channels_list(made_one_user):
    channel_return1 = channels_create_v1(1, 'coolname', True)
    channel_return2 = channels_create_v1(1, 'coolname2', True)

    channel_list = channels_list_v1(1)
    assert channel_list == {'channels': [{'channel_id': 1, 'name': 'coolname'}, {'channel_id': 2, 'name': 'coolname2'}]}

def test_mutliple_users_list(made_one_user):
    auth_register_v1('random@email.com', 'verycoolpassword', 'Name', 'Name')

    channel_return1 = channels_create_v1(1, 'coolname', True) 
    channel_return2 = channels_create_v1(2, 'coolname2', True)

    channel_list = channels_list_v1(1)
    assert channel_list == {'channels': [{'channel_id': 1, 'name': 'coolname'}]}

def test_channels_listall(made_one_user):
    channel_return1 = channels_create_v1(1, 'coolname', True)

    channel_list = channels_listall_v1(1)
    assert channel_list == {'channels': [{'channel_id': 1, 'name': 'coolname'}]}

def test_mutliple_channels_listall(made_one_user):
    channel_return1 = channels_create_v1(1, 'coolname', True)
    channel_return2 = channels_create_v1(1, 'coolname2', True)

    channel_list = channels_listall_v1(1)
    assert channel_list == {'channels': [{'channel_id': 1, 'name': 'coolname'}, {'channel_id': 2, 'name': 'coolname2'}]}

def test_mutliple_users_listall(made_one_user):
    channel_return1 = channels_create_v1(1, 'coolname', True)

    auth_register_v1('random@email.com', 'verycoolpassword', 'Name', 'Name') 
    channel_return2 = channels_create_v1(2, 'coolname2', True)

    channel_list = channels_listall_v1(1)
    assert channel_list == {'channels': [{'channel_id': 1, 'name': 'coolname'}, {'channel_id': 2, 'name': 'coolname2'}]}
