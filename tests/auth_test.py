import pytest

from src.auth import auth_register_v1, auth_login_v1
from src.error import InputError
from src.other import clear_v1

#Error tests
def test_register_invalid_email():
    clear_v1()
    with pytest.raises(InputError):
        auth_register_v1('a', 'verycoolpassword', 'Name', 'Name')

def test_register_duplicate_email():
    clear_v1()
    auth_register_v1('anemail@email.com', 'verycoolpassword', 'Name', 'Name')
    with pytest.raises(InputError):
        auth_register_v1('anemail@email.com', 'verycoolpassword', 'Name', 'Name')

def test_register_invalid_password():
    clear_v1()
    with pytest.raises(InputError):
        auth_register_v1('anemail@email.com', 'bad:(', 'Name', 'Name')

def test_register_first_name_too_long():
    clear_v1()
    with pytest.raises(InputError):
        auth_register_v1('anemail@email.com', 'verycoolpassword', 'pneumonoultramicroscopicsilicovolcanoconiosispneumonoultramicroscopicsilicovolcanoconiosispneumonoultramicroscopicsilicovolcanoconiosispneumonoultramicroscopicsilicovolcanoconiosis', 'Name')

def test_register_first_name_none():
    clear_v1()
    with pytest.raises(InputError):
       auth_register_v1('anemail@email.com', 'verycoolpassword', '', 'Name') 

def test_register_last_name_too_long():
    clear_v1()
    with pytest.raises(InputError):
        auth_register_v1('anemail@email.com', 'verycoolpassword', 'Name', 'pneumonoultramicroscopicsilicovolcanoconiosispneumonoultramicroscopicsilicovolcanoconiosispneumonoultramicroscopicsilicovolcanoconiosispneumonoultramicroscopicsilicovolcanoconiosis')

def test_register_last_name_none():
    clear_v1()
    with pytest.raises(InputError):
       auth_register_v1('anemail@email.com', 'verycoolpassword', 'Name', '') 

def test_login_invalid_email():
    clear_v1()
    auth_register_v1('anemail@email.com', 'verycoolpassword', 'Name', 'Name') 
    with pytest.raises(InputError):
        auth_login_v1('bademail@yahoo.com', 'verycoolpassword')

def test_login_incorrect_password():
    clear_v1()
    auth_register_v1('anemail@email.com', 'verycoolpassword', 'Name', 'Name') 
    with pytest.raises(InputError):
        auth_login_v1('anemail@email.com', 'notcoolpassword')