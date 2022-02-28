import pytest

from src.auth import auth_register_v1, auth_login_v1
from src.channels import channels_create_v1,channels_listall_v1,channels_list_v1
from src.error import InputError
from src.error import AccessError
from src.other import clear_v1

#Error tests
def test_invalid_user_id():
    clear_v1()
    with pytest.raises(AccessError):
        channels_create_v1(0, "name", True)

def test_channel_name_too_long():
    clear_v1()
    with pytest.raises(InputError):
        channels_create_v1(1, "thelengthofthisnameisover20characters", True)

def test_channel_name_too_short():
    clear_v1()
    with pytest.raises(InputError):
        channels_create_v1(1, "", True)
#Working tests
def test_register_and_create_channel():
    clear_v1()
    register_return = auth_register_v1('anemail@email.com', 'verycoolpassword', 'Name', 'Name')
    channel_return = channels_create_v1(1, 'coolname', True)
    assert channel_return == {'channel_id' : 1}

