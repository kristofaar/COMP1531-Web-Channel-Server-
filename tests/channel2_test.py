import re
import pytest
import requests
import json
from src import config

A_ERR = 403
I_ERR = 400
OK = 200

@pytest.fixture
def reg_two_users_and_create_two_channels():
    clear_resp = requests.delete(config.url + 'clear/v1')
    assert clear_resp.status_code == OK
    resp1 = requests.post(config.url + 'auth/register/v2', json={'email': 'teast@test.test', 'password': 'testtesttest', 'name_first': 'test', 'name_last': 'test'})
    assert resp1.status_code == OK
    resp2 = requests.post(config.url + 'auth/register/v2', json={'email': 'lol@lol.lol', 'password': '123abc123abc', 'name_first': 'Jane', 'name_last': 'Austen'})
    assert resp2.status_code == OK
    resp1_data = resp1.json()
    resp2_data = resp2.json()
    resp3 = requests.post(config.url + 'channels/create/v2', json={'token': resp1_data['token'], 'name': 'CoolChannelName', 'is_public': True})
    assert resp3.status_code == OK
    resp4 = requests.post(config.url + 'channels/create/v2', json={'token': resp2_data['token'], 'name': 'NiceChannel', 'is_public': False})
    assert resp4.status_code == OK
    resp3_data = resp3.json()
    resp4_data = resp4.json()
    return {'token1': resp1_data['token'], 'token2': resp2_data['token'], 'u_id1': resp1_data['auth_user_id'], 'u_id2': resp2_data['auth_user_id'], 'ch_id1': resp3_data['channel_id'], 'ch_id2': resp4_data['channel_id']}

#details errors
def test_channel_details_invalid_token(reg_two_users_and_create_two_channels):
    resp = requests.get(config.url + 'channel/details/v2', json={'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c', 'channel_id': reg_two_users_and_create_two_channels['ch_id1']})
    assert resp.status_code == A_ERR

def test_channel_details_expired_token(reg_two_users_and_create_two_channels):
    resp1 = requests.get(config.url + 'auth/logout/v1', json={'token': reg_two_users_and_create_two_channels['token1']})
    assert resp1.status_code == OK
    resp2 = requests.get(config.url + 'channel/details/v2', json={'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1']})
    assert resp2.status_code == A_ERR

def test_channel_details_unauthorised(reg_two_users_and_create_two_channels):
    resp = requests.get(config.url + 'channel/details/v2', json={'token': reg_two_users_and_create_two_channels['token2'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1']})
    assert resp.status_code == A_ERR

def test_channel_details_invalid_channel(reg_two_users_and_create_two_channels):
    resp = requests.get(config.url + 'channel/details/v2', json={'token': reg_two_users_and_create_two_channels['token2'], 'channel_id': 123789})
    assert resp.status_code == I_ERR

#details working
def test_channel_details(reg_two_users_and_create_two_channels):
    resp = requests.get(config.url + 'channel/details/v2', json={'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1']})
    assert resp.status_code == OK
    resp_data = resp.json()
    assert resp_data['name'] == 'CoolChannelName'
    assert resp_data['is_public'] == True
    assert resp_data['owner_members'][0]['u_id'] == reg_two_users_and_create_two_channels['u_id1']
    assert resp_data['all_members'][0]['u_id'] == reg_two_users_and_create_two_channels['u_id1']

#join errors
def test_channel_join_invalid_token(reg_two_users_and_create_two_channels):
    resp = requests.post(config.url + 'channel/post/v2', json={'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c', 'channel_id': reg_two_users_and_create_two_channels['ch_id1']})
    assert resp.status_code == A_ERR

def test_channel_join_expired_token(reg_two_users_and_create_two_channels):
    resp1 = requests.post(config.url + 'auth/logout/v1', json={'token': reg_two_users_and_create_two_channels['token1']})
    assert resp1.status_code == OK
    resp2 = requests.post(config.url + 'channel/join/v2', json={'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1']})
    assert resp2.status_code == A_ERR

def test_channel_join_unauthorised(reg_two_users_and_create_two_channels):
    resp1 = requests.post(config.url + 'channels/create/v2', json={'token': reg_two_users_and_create_two_channels['token1'], 'name': 'CoolChannelName', 'is_public': False})
    assert resp1.status_code == OK
    resp1_data = resp1.json()
    resp2 = requests.post(config.url + 'channel/join/v2', json={'token': reg_two_users_and_create_two_channels['token2'], 'channel_id': resp1_data['channel_id']})
    assert resp2.status_code == A_ERR

def test_channel_join_invalid(reg_two_users_and_create_two_channels):
    resp = requests.post(config.url + 'channel/join/v2', json={'token': reg_two_users_and_create_two_channels['token2'], 'channel_id': 123789})
    assert resp.status_code == I_ERR

def test_channel_join_already_member(reg_two_users_and_create_two_channels):
    resp = requests.post(config.url + 'channel/join/v2', json={'token':reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1']})
    assert resp.status_code == I_ERR

#join working
def test_channel_join_global_owner(reg_two_users_and_create_two_channels):
    resp1 = requests.post(config.url + 'channel/join/v2', json={'token':reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id2']})
    assert resp1.status_code == OK
    resp2 = requests.get(config.url + 'channel/details/v2', json={'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id2']})
    assert resp2.status_code == OK
    resp_data = resp2.json()
    assert resp_data['all_members'][1]['u_id'] == reg_two_users_and_create_two_channels['u_id1']

def test_channel_join_normal(reg_two_users_and_create_two_channels):
    resp1 = requests.post(config.url + 'channels/create/v2', json={'token': reg_two_users_and_create_two_channels['token1'], 'name': 'NiceChannel222', 'is_public': True})
    assert resp1.status_code == OK
    resp1_data = resp1.json()
    resp2 = requests.post(config.url + 'channel/join/v2', json={'token':reg_two_users_and_create_two_channels['token2'], 'channel_id': resp1_data['channel_id']})
    assert resp2.status_code == OK
    resp3 = requests.get(config.url + 'channel/details/v2', json={'token': reg_two_users_and_create_two_channels['token2'], 'channel_id': resp1_data['channel_id']})
    assert resp3.status_code == OK
    resp3_data = resp3.json()
    assert resp3_data['all_members'][1]['u_id'] == reg_two_users_and_create_two_channels['u_id2']

#invite errors
def test_channel_invite_invalid_token(reg_two_users_and_create_two_channels):
    resp = requests.post(config.url + 'channel/invite/v2', json={'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c', 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'u_id': reg_two_users_and_create_two_channels['u_id2']})
    assert resp.status_code == A_ERR

def test_channel_invite_expired_token(reg_two_users_and_create_two_channels):
    resp1 = requests.post(config.url + 'auth/logout/v1', json={'token': reg_two_users_and_create_two_channels['token1']})
    assert resp1.status_code == OK
    resp2 = requests.post(config.url + 'channel/invite/v2', json={'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'u_id': reg_two_users_and_create_two_channels['u_id2']})
    assert resp2.status_code == A_ERR

def test_channel_invite_unauthorised(reg_two_users_and_create_two_channels):
    resp = requests.post(config.url + 'channel/invite/v2', json={'token': reg_two_users_and_create_two_channels['token2'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'u_id': reg_two_users_and_create_two_channels['u_id2']})
    assert resp.status_code == A_ERR

def test_channel_invite_invalid_channel(reg_two_users_and_create_two_channels):
    resp = requests.post(config.url + 'channel/invite/v2', json={'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': 6213732198, 'u_id': reg_two_users_and_create_two_channels['u_id2']})
    assert resp.status_code == I_ERR

def test_channel_invite_invalid_id(reg_two_users_and_create_two_channels):
    resp = requests.post(config.url + 'channel/invite/v2', json={'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'u_id': 21376321})
    assert resp.status_code == I_ERR

def test_channel_invite_already_in(reg_two_users_and_create_two_channels):
    resp = requests.post(config.url + 'channel/invite/v2', json={'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'u_id': reg_two_users_and_create_two_channels['u_id1']})
    assert resp.status_code == I_ERR

#invite working
def test_channel_invite(reg_two_users_and_create_two_channels):
    resp1 = requests.post(config.url + 'channel/invite/v2', json={'token':reg_two_users_and_create_two_channels['token2'], 'channel_id': reg_two_users_and_create_two_channels['ch_id2'], 'u_id': reg_two_users_and_create_two_channels['u_id1']})
    assert resp1.status_code == OK
    resp2 = requests.get(config.url + 'channel/details/v2', json={'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id2']})
    assert resp2.status_code == OK
    resp_data = resp2.json()
    assert resp_data['all_members'][1]['u_id'] == reg_two_users_and_create_two_channels['u_id1']

#messages errors
def test_channel_messages_invalid_token(reg_two_users_and_create_two_channels):
    resp = requests.get(config.url + 'channel/messages/v2', json={'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c', 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'start': 0})
    assert resp.status_code == A_ERR

def test_channel_messages_expired_token(reg_two_users_and_create_two_channels):
    resp1 = requests.post(config.url + 'auth/logout/v1', json={'token': reg_two_users_and_create_two_channels['token1']})
    assert resp1.status_code == OK
    resp2 = requests.get(config.url + 'channel/messages/v2', json={'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'start': 0})
    assert resp2.status_code == A_ERR

def test_channel_messages_unauthorised(reg_two_users_and_create_two_channels):
    resp = requests.get(config.url + 'channel/messages/v2', json={'token': reg_two_users_and_create_two_channels['token2'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'start': 0})
    assert resp.status_code == A_ERR

def test_channel_messages_invalid_channel(reg_two_users_and_create_two_channels):
    resp = requests.get(config.url + 'channel/messages/v2', json={'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': 6213732198, 'start': 0})
    assert resp.status_code == I_ERR

def test_channel_messages_big_start(reg_two_users_and_create_two_channels):
    resp = requests.get(config.url + 'channel/messages/v2', json={'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'start': 1})
    assert resp.status_code == I_ERR

#messages working
def test_channel_messages_empty(reg_two_users_and_create_two_channels):
    resp = requests.get(config.url + 'channel/messages/v2', json={'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'start': 0})
    assert resp.status_code == OK
    resp_data = resp.json()
    assert resp_data['start'] == 0
    assert resp_data['end'] == -1
    assert resp_data['messages'] == []

def test_channel_small_messages(reg_two_users_and_create_two_channels):
    for i in range(2):
        resp = requests.post(config.url + 'message/send/v1', json={'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'message': str(i)})
        assert resp.status_code == OK
    resp = requests.get(config.url + 'channel/messages/v2', json={'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'start': 0})
    assert resp.status_code == OK
    resp_data = resp.json()
    assert resp_data['start'] == 0
    assert resp_data['end'] == -1
    for i in range(2):
        assert resp_data['messages'][i]['message'] == str(1 - i)

def test_channel_big_messages(reg_two_users_and_create_two_channels):
    for i in range(150):
        resp = requests.post(config.url + 'message/send/v1', json={'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'message': str(i)})
        assert resp.status_code == OK
    resp = requests.get(config.url + 'channel/messages/v2', json={'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'start': 0})
    assert resp.status_code == OK
    resp_data = resp.json()
    assert resp_data['start'] == 0
    assert resp_data['end'] == 50
    for i in range(50):
        assert resp_data['messages'][i]['message'] == str(149 - i)
    resp = requests.get(config.url + 'channel/messages/v2', json={'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'start': 100})
    assert resp.status_code == OK
    resp_data = resp.json()
    assert resp_data['start'] == 100
    assert resp_data['end'] == -1
    for i in range(50):
        assert resp_data['messages'][i]['message'] == str(49 - i)

#leave errors
def test_channel_leave_invalid_token(reg_two_users_and_create_two_channels):
    resp = requests.post(config.url + 'channel/leave/v1', json={'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c', 'channel_id': reg_two_users_and_create_two_channels['ch_id1']})
    assert resp.status_code == A_ERR

def test_channel_leave_expired_token(reg_two_users_and_create_two_channels):
    resp1 = requests.post(config.url + 'auth/logout/v1', json={'token': reg_two_users_and_create_two_channels['token1']})
    assert resp1.status_code == OK
    resp2 = requests.post(config.url + 'channel/leave/v1', json={'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1']})
    assert resp2.status_code == A_ERR

def test_channel_messages_unauthorised(reg_two_users_and_create_two_channels):
    resp = requests.post(config.url + 'channel/leave/v1', json={'token': reg_two_users_and_create_two_channels['token2'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1']})
    assert resp.status_code == A_ERR

def test_channel_messages_invalid_channel(reg_two_users_and_create_two_channels):
    resp = requests.post(config.url + 'channel/messages/v2', json={'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': 6213732198})
    assert resp.status_code == I_ERR

#leave working
def test_channel_leave(reg_two_users_and_create_two_channels):
    resp1 = requests.post(config.url + 'channel/join/v2', json={'token': reg_two_users_and_create_two_channels['token2'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1']})
    assert resp1.status_code == OK
    resp2 = requests.post(config.url + 'channel/leave/v1', json={'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1']})
    assert resp2.status_code == OK
    resp3 = requests.get(config.url + 'channel/details/v2', json={'token': reg_two_users_and_create_two_channels['token2'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1']})
    assert resp3.status_code == OK
    resp4 = requests.get(config.url + 'channel/details/v2', json={'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1']})
    assert resp4.status_code == A_ERR

#addowner errors
def test_channel_addowner_invalid_token(reg_two_users_and_create_two_channels):
    resp = requests.post(config.url + 'channel/addowner/v1', json={'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c', 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'u_id': reg_two_users_and_create_two_channels['u_id1']})
    assert resp.status_code == A_ERR

def test_channel_addowner_expired_token(reg_two_users_and_create_two_channels):
    resp1 = requests.post(config.url + 'auth/logout/v1', json={'token': reg_two_users_and_create_two_channels['token1']})
    assert resp1.status_code == OK
    resp2 = requests.post(config.url + 'channel/addowner/v1', json={'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'u_id': reg_two_users_and_create_two_channels['u_id1']})
    assert resp2.status_code == A_ERR

def test_channel_addowner_unauthorised(reg_two_users_and_create_two_channels):
    resp1 = requests.post(config.url + 'channel/join/v2', json={'token': reg_two_users_and_create_two_channels['token2'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1']})
    assert resp1.status_code == OK
    resp2 = requests.post(config.url + 'channel/addowner/v1', json={'token': reg_two_users_and_create_two_channels['token2'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'u_id': reg_two_users_and_create_two_channels['u_id2']})
    assert resp2.status_code == A_ERR

def test_channel_addowner_invalid_channel(reg_two_users_and_create_two_channels):
    resp = requests.post(config.url + 'channel/addowner/v1', json={'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': 6213732198, 'u_id': reg_two_users_and_create_two_channels['u_id1']})
    assert resp.status_code == I_ERR

def test_channel_addowner_invalid_id(reg_two_users_and_create_two_channels):
    resp = requests.post(config.url + 'channel/addowner/v1', json={'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'u_id': 21376321})
    assert resp.status_code == I_ERR

def test_channel_addowner_already_owner(reg_two_users_and_create_two_channels):
    resp = requests.post(config.url + 'channel/addowner/v1', json={'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'u_id': reg_two_users_and_create_two_channels['u_id1']})
    assert resp.status_code == I_ERR

def test_channel_addowner_not_a_member(reg_two_users_and_create_two_channels):
    resp = requests.post(config.url + 'channel/addowner/v1', json={'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'u_id': reg_two_users_and_create_two_channels['u_id2']})
    assert resp.status_code == I_ERR

#addowner working
def test_channel_addowner(reg_two_users_and_create_two_channels):
    resp1 = requests.post(config.url + 'channel/join/v2', json={'token': reg_two_users_and_create_two_channels['token2'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1']})
    assert resp1.status_code == OK
    resp2 = requests.post(config.url + 'channel/addowner/v1', json={'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'u_id': reg_two_users_and_create_two_channels['u_id2']})
    assert resp2.status_code == OK
    resp3 = requests.get(config.url + 'channel/details/v2', json={'token': reg_two_users_and_create_two_channels['token2'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1']})
    assert resp3.status_code == OK
    resp_data = resp3.json()
    assert resp_data['owner_members'][1]['u_id'] == reg_two_users_and_create_two_channels['u_id2']

#removeowner errors
def test_channel_removeowner_invalid_token(reg_two_users_and_create_two_channels):
    resp = requests.post(config.url + 'channel/removeowner/v1', json={'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c', 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'u_id': reg_two_users_and_create_two_channels['u_id1']})
    assert resp.status_code == A_ERR

def test_channel_removeowner_expired_token(reg_two_users_and_create_two_channels):
    resp1 = requests.post(config.url + 'auth/logout/v1', json={'token': reg_two_users_and_create_two_channels['token1']})
    assert resp1.status_code == OK
    resp2 = requests.post(config.url + 'channel/removeowner/v1', json={'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'u_id': reg_two_users_and_create_two_channels['u_id1']})
    assert resp2.status_code == A_ERR

def test_channel_removeowner_unauthorised(reg_two_users_and_create_two_channels):
    resp1 = requests.post(config.url + 'channel/join/v2', json={'token': reg_two_users_and_create_two_channels['token2'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1']})
    assert resp1.status_code == OK
    resp2 = requests.post(config.url + 'channel/removeowner/v1', json={'token': reg_two_users_and_create_two_channels['token2'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'u_id': reg_two_users_and_create_two_channels['u_id1']})
    assert resp2.status_code == A_ERR

def test_channel_removeowner_invalid_channel(reg_two_users_and_create_two_channels):
    resp = requests.post(config.url + 'channel/removeowner/v1', json={'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': 6213732198, 'u_id': reg_two_users_and_create_two_channels['u_id1']})
    assert resp.status_code == I_ERR

def test_channel_removeowner_invalid_id(reg_two_users_and_create_two_channels):
    resp = requests.post(config.url + 'channel/removeowner/v1', json={'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'u_id': 21376321})
    assert resp.status_code == I_ERR

def test_channel_removeowner_not_owner(reg_two_users_and_create_two_channels):
    resp1 = requests.post(config.url + 'channel/join/v2', json={'token': reg_two_users_and_create_two_channels['token2'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1']})
    assert resp1.status_code == OK
    resp2 = requests.post(config.url + 'channel/removeowner/v1', json={'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'u_id': reg_two_users_and_create_two_channels['u_id2']})
    assert resp2.status_code == I_ERR

def test_channel_removeowner_only_owner(reg_two_users_and_create_two_channels):
    resp = requests.post(config.url + 'channel/removeowner/v1', json={'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'u_id': reg_two_users_and_create_two_channels['u_id1']})
    assert resp.status_code == I_ERR

#addowner working
def test_channel_removeowner(reg_two_users_and_create_two_channels):
    resp1 = requests.post(config.url + 'channel/join/v2', json={'token': reg_two_users_and_create_two_channels['token2'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1']})
    assert resp1.status_code == OK
    resp2 = requests.post(config.url + 'channel/addowner/v1', json={'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'u_id': reg_two_users_and_create_two_channels['u_id2']})
    assert resp2.status_code == OK
    resp3 = requests.get(config.url + 'channel/details/v2', json={'token': reg_two_users_and_create_two_channels['token2'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1']})
    assert resp3.status_code == OK
    resp3_data = resp3.json()
    assert resp3_data['owner_members'][1]['u_id'] == reg_two_users_and_create_two_channels['u_id2']
    resp4 = requests.post(config.url + 'channel/removeowner/v1', json={'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'u_id': reg_two_users_and_create_two_channels['u_id2']})
    assert resp4.status_code == OK
    resp5 = requests.get(config.url + 'channel/details/v2', json={'token': reg_two_users_and_create_two_channels['token2'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1']})
    assert resp5.status_code == OK
    resp5_data = resp5.json()
    assert len(resp5_data['owner_members']) == 1
    assert len(resp5_data['all_members']) == 2