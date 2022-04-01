import pytest

from src.auth import auth_register_v1, auth_login_v1, auth_passwordreset_request_v1, auth_passwordreset_reset_v1
from src.error import InputError
from src.channels import channels_create_v1
from src.channel import channel_details_v1
from src.other import clear_v1

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

def test_handle_no_alphanumeric():
    clear_v1()
    token = auth_register_v1('anemail@email.com', 'verycoolpassword', 'Name123_!@#', 'Name123!@#')['token']
    ch_id = channels_create_v1(token, 'hi', True)['channel_id']
    assert channel_details_v1(token, ch_id)['all_members'][0]['handle_str'] == 'name123name123'

def test_handle_less_than_20():   # check name over 20 letters
    clear_v1()
    token = auth_register_v1('anemail@email.com', 'verycoolpassword', 'NameIsWayPast', 'TwentyCharacters')['token']
    ch_id = channels_create_v1(token, 'hi', True)['channel_id']
    assert channel_details_v1(token, ch_id)['all_members'][0]['handle_str'] == 'nameiswaypasttwentyc'

# todo

def test_handle_less_than_20_duplicate():    # check if both handles less than 20, ignore number append (next one tests it)
    clear_v1()
    auth_register_v1('blah@email.com', 'verycoolpassword', 'a', 'a')
    auth_register_v1('anemail1@email.com', 'verycoolpassword', 'Name#@', 'nAme!@89')
    auth_register_v1('anemail2@email.com', 'verycoolpassword', 'Name', 'nAme!@89')
    token = auth_register_v1('anemail3@email.com', 'verycoolpassword', '!@&name', 'nAme!@89')['token']
    ch_id = channels_create_v1(token, 'hi', True)['channel_id']
    assert channel_details_v1(token, ch_id)['all_members'][0]['handle_str'] == 'namename891'

def test_handle_append_number(): # check if right number is appended to handle for identical names over 20 characters
    clear_v1()
    auth_register_v1('anemail1@email.com', 'verycoolpassword', 'NameIsWayPast', 'TwentyCharacters')
    auth_register_v1('anemail2@email.com', 'verycoolpassword', 'NameIsWayPast', 'TwentyCharacters')
    token = auth_register_v1('anemail3@email.com', 'verycoolpassword', 'NameIsWayPast', 'TwentyCharacters')['token']
    ch_id = channels_create_v1(token, 'hi', True)['channel_id']
    assert channel_details_v1(token, ch_id)['all_members'][0]['handle_str'] == 'nameiswaypasttwentyc1'

def test_handle_no_alphanumeric_name(): # test for name with no letters/numbers so end up with empty space name? 
    clear_v1()
    token = auth_register_v1('anemail3@email.com', 'verycoolpassword', '$^#^*&', '_!@&)@#')['token']
    ch_id = channels_create_v1(token, 'hi', True)['channel_id']
    assert channel_details_v1(token, ch_id)['all_members'][0]['handle_str'] == ''

def test_handle_no_alphanumeric_name_multiple():
    clear_v1()
    auth_register_v1('anemail1@email.com', 'verycoolpassword', '$^#^*&', '_!@&)@#')
    auth_register_v1('anemail2@email.com', 'verycoolpassword', '$^#^*&', '_!@&)@#')
    token = auth_register_v1('anemail3@email.com', 'verycoolpassword', '$^#^*&', '_!@&)@#')['token']
    ch_id = channels_create_v1(token, 'hi', True)['channel_id']
    assert channel_details_v1(token, ch_id)['all_members'][0]['handle_str'] == '1'

def test_clear_v1_users():
    clear_v1()
    register_return = auth_register_v1('anemail@email.com', 'verycoolpassword', 'Name', 'Name') 
    reg_id1 = register_return['auth_user_id']

    login_return = auth_login_v1('anemail@email.com', 'verycoolpassword')
    log_id1 = login_return['auth_user_id']

    clear_v1() #test that once we clear the data_store, we can add the same exact user without an error
    register_return = auth_register_v1('anemail@email.com', 'verycoolpassword', 'Name', 'Name') 
    reg_id1 = register_return['auth_user_id']

    login_return = auth_login_v1('anemail@email.com', 'verycoolpassword')
    log_id1 = login_return['auth_user_id']

    assert reg_id1 == log_id1

