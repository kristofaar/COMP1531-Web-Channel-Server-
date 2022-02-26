import pytest

from src.auth import auth_register_v1, auth_login_v1
from src.error import InputError
from src.other import clear_v1
from src.data_store import data_store

#Error tests
def test_register_invalid_email():
    clear_v1()
    with pytest.raises(InputError):
        auth_register_v1('a', 'verycoolpassword', 'Name', 'Name')

def test_register_invalid_email2():
    clear_v1()
    with pytest.raises(InputError):
        auth_register_v1('', 'verycoolpassword', 'Name', 'Name')

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

#Working tests
def test_register_and_login():
    clear_v1()
    register_return = auth_register_v1('anemail@email.com', 'verycoolpassword', 'Name', 'Name') 
    reg_id1 = register_return['auth_user_id']

    login_return = auth_login_v1('anemail@email.com', 'verycoolpassword')
    log_id1 = login_return['auth_user_id']

    assert reg_id1 == log_id1

def test_register_and_login_multiple():
    clear_v1()

    register_return1 = auth_register_v1('anemail@email.com', 'verycoolpassword', 'Name', 'Name') 
    reg_id1 = register_return1['auth_user_id']

    login_return1 = auth_login_v1('anemail@email.com', 'verycoolpassword')
    log_id1 = login_return1['auth_user_id']
     
    register_return2 = auth_register_v1('random@email.com', 'verycoolpassword', 'Name', 'Name') 
    reg_id2 = register_return2['auth_user_id']

    register_return3 = auth_register_v1('gmail@yahoo.com', 'differentpasswordwow', 'Name', 'Name') 
    reg_id3 = register_return3['auth_user_id']

    login_return2 = auth_login_v1('random@email.com', 'verycoolpassword')
    log_id2 = login_return2['auth_user_id']

    login_return3 = auth_login_v1('gmail@yahoo.com', 'differentpasswordwow')
    log_id3 = login_return3['auth_user_id']

    assert reg_id1 == log_id1
    assert reg_id2 == log_id2
    assert reg_id3 == log_id3

#might need tests for handle checking

@pytest.fixture
def clear_and_handle():     # clears, and returns 'users' for access - Didn't end up using it
    clear_v1()
    storage = data_store.get()
    users = storage['users']
    return users

def test_handle_no_alphanumeric():      #DOES NOT WORK FOR NAMES WITH UNDERSCORES ie. Name___123
    clear_v1()
    auth_register_v1('anemail@email.com', 'verycoolpassword', 'Name123!@#', 'Name123!@#')

    storage = data_store.get()
    users = storage['users']

    result = True
    for user in users:
        if not user['handle'].isalnum():  # if not alphanumeric - this was supposed to be for multiple users 
            result = false    

    assert result == True

def test_handle_less_than_20():   # check name over 20 letters
    clear_v1()
    auth_register_v1('anemail@email.com', 'verycoolpassword', 'NameIsWayPast', 'TwentyCharacters')

    storage = data_store.get()
    users = storage['users']
    handle = users[0]['handle']     # checks first user 
    length = len(handle)

    assert length == 20

# todo

def test_handle_less_than_20_duplicate():    # check if both handles less than 20, ignore number append (next one tests it)
    clear_v1()
    auth_register_v1('anemail@email.com', 'verycoolpassword', 'NameIsWayPast', 'TwentyCharacters')
    auth_register_v1('random@email.com', 'verycoolpassword', 'NameIsWayPast', 'TwentyCharacters')
    pass

def test_handle_append_number(): # check if right number is appended to handle for identical names over 20 characters
    clear_v1()
    auth_register_v1('anemail@email.com', 'verycoolpassword', 'NameIsWayPast', 'TwentyCharacters')
    auth_register_v1('random@email.com', 'verycoolpassword', 'NameIsWayPast', 'TwentyCharacters')
    pass

def test_handle_no_alphanumeric_name(): # test for name with no letters/numbers so end up with empty space name? 
    clear_v1()
    auth_register_v1('anemail@email.com', 'verycoolpassword', '!@#$%^123', '!@#$%^123')     # is this even allowed as valid name? 
    pass

def test_handle_multiple_users():   
    clear_v1()
    pass





