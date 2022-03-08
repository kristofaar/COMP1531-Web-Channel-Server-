from multiprocessing.sharedctypes import Value
from email import message
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
    u_id = auth_register_v1('anemail@email.com', 'verycoolpassword', 'Name', 'Name')['auth_user_id']
    ch_id1 = channels_create_v1(u_id, 'public', True)['channel_id']
    ch_id2 = channels_create_v1(u_id, 'private', False)['channel_id']
    first_channel_details = channel_details_v1(u_id, ch_id1)
    second_channel_details = channel_details_v1(u_id, ch_id2)
    return {'first': first_channel_details, 'second': second_channel_details, 'u_id': u_id, 'ch_id1': ch_id1, 'ch_id2': ch_id2}

# Testing for channel_details  
 
def test_channel_details_check_public_private(one_user_made_two_channels):
    assert one_user_made_two_channels['first']['is_public'] == True
    assert one_user_made_two_channels['second']['is_public']  == False

def test_channel_details_check_name(one_user_made_two_channels):
     assert one_user_made_two_channels['first']['name'] == 'public'
     assert one_user_made_two_channels['second']['name'] == 'private'

def test_channel_details_check_owner(one_user_made_two_channels):
    assert one_user_made_two_channels['first']['owner_members'][0]['u_id'] == one_user_made_two_channels['u_id']
    assert one_user_made_two_channels['second']['owner_members'][0]['u_id'] == one_user_made_two_channels['u_id']

def test_channel_details_check_members(one_user_made_two_channels):
    assert one_user_made_two_channels['first']['all_members'] == [{'email': 'anemail@email.com',  'handle_str': 'namename',  'name_first': 'Name', 'name_last': 'Name',  'u_id': one_user_made_two_channels['u_id']}]
    assert one_user_made_two_channels['second']['all_members'] == [{'email': 'anemail@email.com', 'handle_str': 'namename',  'name_first': 'Name',  'name_last': 'Name', 'u_id': one_user_made_two_channels['u_id']}]


def test_channel_details_invalid_channel_id(one_user_made_two_channels):
    for i in range(3):
        if i != one_user_made_two_channels['ch_id1'] and i != one_user_made_two_channels['ch_id2']:
            with pytest.raises(InputError):
                channel_details_v1(one_user_made_two_channels['u_id'], i)

def test_channel_details_unauthorised_user(one_user_made_two_channels):     # second user tries accessing first user channels
    u_id2 = auth_register_v1('notanemail@email.com', 'verycoolpassword', 'Second', 'User')['auth_user_id']
    ch_id3 = channels_create_v1(2, 'third_channel', True)['channel_id']    # second user makes a channel (third one in storage)
    with pytest.raises(AccessError):
        channel_details_v1(u_id2, one_user_made_two_channels['ch_id1'])
    with pytest.raises(AccessError):
        channel_details_v1(one_user_made_two_channels['u_id'], ch_id3)  # first user tries accessing second user channels    

def test_channel_details_multiple_members(one_user_made_two_channels):
    u_id2 = auth_register_v1('notanemail@email.com', 'verycoolpassword', 'Second', 'User')['auth_user_id']
    channel_join_v1(u_id2, one_user_made_two_channels['ch_id1']) #second user joins channel 1
    assert channel_details_v1(one_user_made_two_channels['u_id'], one_user_made_two_channels['ch_id1'])['all_members'] == [{'email': 'anemail@email.com',  'handle_str': 'namename',  'name_first': 'Name',  'name_last': 'Name', 'u_id': one_user_made_two_channels['u_id']}, {'email': 'notanemail@email.com',  'handle_str': 'seconduser',  'name_first': 'Second',  'name_last': 'User',  'u_id': u_id2}]

def test_channel_details_invalid_user(one_user_made_two_channels):
    with pytest.raises(AccessError):
        channel_details_v1(one_user_made_two_channels['u_id'] + 1, one_user_made_two_channels['ch_id1'])    # second user doesn't exist

# testing channel_join_v1

def test_channel_join_new_member_join_valid_channel(one_user_made_two_channels):        
    u_id2 = auth_register_v1('notanemail@email.com', 'verycoolpassword', 'Second', 'User')['auth_user_id']
    channel_join_v1(u_id2, one_user_made_two_channels['ch_id1'])   # second user joins channel 1 made by first user
    first_channel_details = channel_details_v1(one_user_made_two_channels['u_id'], one_user_made_two_channels['ch_id1'])
    members = first_channel_details['all_members']
    assert members[1]['u_id'] == u_id2    # check if second user is member of channel 1 now

def test_channel_join_invalid_user_join_valid_channel(one_user_made_two_channels):
    with pytest.raises(AccessError):
        channel_join_v1(one_user_made_two_channels['u_id'] + 1, one_user_made_two_channels['ch_id1'])   # second user not registered yet

def test_channel_join_new_member_joins_invalid_channel(one_user_made_two_channels):     
    u_id2 = auth_register_v1('notanemail@email.com', 'verycoolpassword', 'Second', 'User')['auth_user_id'] 
    for i in range(3):
        if i != one_user_made_two_channels['ch_id1'] and i != one_user_made_two_channels['ch_id2']:
            with pytest.raises(InputError):
                channel_join_v1(u_id2, i)       # second user tries joining channel 3 (doesn't exist, only 1 and 2)

def test_channel_join_already_a_member(one_user_made_two_channels):
    u_id2 = auth_register_v1('notanemail@email.com', 'verycoolpassword', 'Second', 'User')['auth_user_id']
    channel_join_v1(u_id2, one_user_made_two_channels['ch_id1'])   
    with pytest.raises(InputError):
        channel_join_v1(u_id2, one_user_made_two_channels['ch_id1'])   # second user tries joining channel 1 again

def test_channel_join_new_member_joins_private_channel(one_user_made_two_channels):    
    u_id2 = auth_register_v1('notanemail@email.com', 'verycoolpassword', 'Second', 'User')['auth_user_id']
    with pytest.raises(AccessError):
        channel_join_v1(u_id2, one_user_made_two_channels['ch_id2'])   # second user tries joining channel 2, which is private
    

# testing channel_invite_v1


def test_channel_invite_member(one_user_made_two_channels):
    u_id2 = auth_register_v1('notanemail@email.com', 'verycoolpassword', 'Second', 'User')['auth_user_id']
    channel_invite_v1(one_user_made_two_channels['u_id'], one_user_made_two_channels['ch_id1'], u_id2) # invite second user to channel 1

    assert channel_details_v1(one_user_made_two_channels['u_id'], one_user_made_two_channels['ch_id1'])['all_members'] == [{'email': 'anemail@email.com',  'handle_str': 'namename',  'name_first': 'Name',  'name_last': 'Name',  'u_id': one_user_made_two_channels['u_id']}, {'email': 'notanemail@email.com',  'handle_str': 'seconduser',  'name_first': 'Second',  'name_last': 'User',  'u_id': u_id2}]

# def test_channel_invite_public/private? Check if invited to both public and private or dw about it?

def test_channel_invite_invalid_channel(one_user_made_two_channels): 
    u_id2 = auth_register_v1('notanemail@email.com', 'verycoolpassword', 'Second', 'User')['auth_user_id']
    for i in range(3):
        if i != one_user_made_two_channels['ch_id1'] and i != one_user_made_two_channels['ch_id2']:
            with pytest.raises(InputError):
                channel_invite_v1(one_user_made_two_channels['u_id'], i, u_id2)    # one user invites second user to 3rd channel (doesn't exist)

def test_channel_invite_invalid_inviter_id(one_user_made_two_channels):   #invalid auth_user_id (one inviting)
    with pytest.raises(AccessError):
        channel_invite_v1(one_user_made_two_channels['u_id'] + 1, one_user_made_two_channels['ch_id1'], one_user_made_two_channels['u_id'])    # second user (not registered) invites first user 
        
def test_channel_invite_invalid_invitee_id(one_user_made_two_channels):   #invalid u_id (one getting invited)
    with pytest.raises(InputError):
        channel_invite_v1(one_user_made_two_channels['u_id'], one_user_made_two_channels['ch_id1'], one_user_made_two_channels['u_id'] + 1)    # first user invites second user (not registered)

def test_channel_invite_already_member(one_user_made_two_channels):
    u_id2 = auth_register_v1('notanemail@email.com', 'verycoolpassword', 'Second', 'User')['auth_user_id']
    channel_join_v1(u_id2, one_user_made_two_channels['ch_id1']) # second user joins first channel
    with pytest.raises(InputError):
        channel_invite_v1(one_user_made_two_channels['u_id'], one_user_made_two_channels['ch_id1'], u_id2)    # one user invites second user to first channel (already member)

def test_channel_invite_not_a_member(one_user_made_two_channels):
    u_id2 = auth_register_v1('notanemail@email.com', 'verycoolpassword', 'Second', 'User')['auth_user_id']
    u_id3 = auth_register_v1('anotheremail@email.com', 'verycoolpassword', 'Third', 'User')['auth_user_id']
    with pytest.raises(AccessError):
        channel_invite_v1(u_id2, one_user_made_two_channels['ch_id1'], u_id3)    # third user invited to first channel by second user (not a member)


# testing channel_messages


def test_channel_messages_invalid_channel_id():
    clear_v1()
    u_id = auth_register_v1('anemail@email.com', 'verycoolpassword', 'Name', 'Name')['auth_user_id']
    ch_id = channels_create_v1(u_id, 'channelName', True)['channel_id']
    with pytest.raises(InputError):
        channel_messages_v1(u_id, ch_id + 1, 0)

def test_channel_messages_invalid_channel_id_empty():
    clear_v1()
    u_id = auth_register_v1('anemail@email.com', 'verycoolpassword', 'Name', 'Name')['auth_user_id']
    with pytest.raises(InputError):
        channel_messages_v1(u_id, 3, 0)

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
    u_id1 = auth_register_v1('anemail@email.com', 'verycoolpassword', 'Name', 'Name')['auth_user_id']
    u_id2 = auth_register_v1('anemail1@email.com', 'verycoolpassword', 'Name', 'Name')['auth_user_id']
    ch_id = channels_create_v1(u_id1, 'channelName', True)['channel_id']
    with pytest.raises(AccessError):
        channel_messages_v1(u_id2, ch_id, 0)

def test_channel_messages_invalid_user():
    clear_v1()
    u_id = auth_register_v1('anemail@email.com', 'verycoolpassword', 'Name', 'Name')['auth_user_id']
    ch_id = channels_create_v1(u_id, 'channelName', True)['channel_id']
    with pytest.raises(AccessError):
        channel_messages_v1(u_id + 1, ch_id, 0)

def test_channel_messages_invalid_start():
    clear_v1()
    u_id = auth_register_v1('anemail@email.com', 'verycoolpassword', 'Name', 'Name')['auth_user_id']
    ch_id = channels_create_v1(u_id, 'channelName', True)['channel_id']
    with pytest.raises(InputError):
        channel_messages_v1(u_id, ch_id, 3)

def test_channel_messages_double_error1():
    clear_v1()
    u_id = auth_register_v1('anemail@email.com', 'verycoolpassword', 'Name', 'Name')['auth_user_id']
    ch_id = channels_create_v1(u_id, 'channelName', True)['channel_id']
    with pytest.raises(AccessError):
        channel_messages_v1(u_id + 1, ch_id, 3)

def test_channel_messages_double_error1():
    clear_v1()
    u_id = auth_register_v1('anemail@email.com', 'verycoolpassword', 'Name', 'Name')['auth_user_id']
    ch_id = channels_create_v1(u_id, 'channelName', True)['channel_id']
    with pytest.raises(AccessError):
        channel_messages_v1(u_id + 1, ch_id + 1, 3)


#Working tests

def test_channel_messages_empty():
    clear_v1()
    u_id = auth_register_v1('anemail@email.com', 'verycoolpassword', 'Name', 'Name')['auth_user_id']
    ch_id = channels_create_v1(u_id, 'channelName', True)['channel_id']
    assert channel_messages_v1(u_id, ch_id, 0) == {'messages': [], 'start': 0, 'end': -1}

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
