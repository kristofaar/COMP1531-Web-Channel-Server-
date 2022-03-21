import pytest
import requests
import json
from src import config

A_ERR = 403
I_ERR = 400
OK = 200
'''
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

#send errors
def test_message_send_invalid_token(reg_two_users_and_create_two_channels):
    resp = requests.post(config.url + 'message/send/v1', json={'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c', 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'message': 'hi'})
    assert resp.status_code == A_ERR

def test_message_send_expired_token(reg_two_users_and_create_two_channels):
    resp1 = requests.post(config.url + 'auth/logout/v1', json={'token': reg_two_users_and_create_two_channels['token1']})
    assert resp1.status_code == OK
    resp = requests.post(config.url + 'message/send/v1', json={'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'message': 'hi'})
    assert resp.status_code == A_ERR

def test_message_send_unauthorised(reg_two_users_and_create_two_channels):
    resp = requests.post(config.url + 'message/send/v1', json={'token': reg_two_users_and_create_two_channels['token2'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'message': 'hi'})
    assert resp.status_code == A_ERR

def test_message_send_invalid_channel(reg_two_users_and_create_two_channels):
    resp = requests.post(config.url + 'message/send/v1', json={'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': 123312321345, 'message': 'hi'})
    assert resp.status_code == I_ERR

def test_message_send_bad_length(reg_two_users_and_create_two_channels):
    resp1 = requests.post(config.url + 'message/send/v1', json={'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'message': ''})
    assert resp1.status_code == I_ERR
    msg = 'a'
    for i in range(1000):
        msg += 'a'
    resp2 = requests.post(config.url + 'message/send/v1', json={'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'message': msg})
    assert resp2.status_code == I_ERR

#send working
def test_one_user_two_messages(reg_two_users_and_create_two_channels):
    resp1 = requests.post(config.url + 'message/send/v1', json={'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'message': 'hi'})
    assert resp1.status_code == OK
    resp1_data = resp1.json()
    resp2 = requests.post(config.url + 'message/send/v1', json={'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'message': 'cool'})
    assert resp2.status_code == OK
    resp2_data = resp2.json()
    resp3 = requests.get(config.url + 'channel/messages/v2', json={'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'start': 0})
    assert resp3.status_code == OK
    resp3_data = resp3.json()
    assert resp3_data['start'] == 0
    assert resp3_data['end'] == -1
    assert resp1_data['message_id'] == resp3_data['messages'][1]['message_id'] #hi
    assert resp2_data['message_id'] == resp3_data['messages'][0]['message_id'] #cool
    assert resp3_data['messages'][0]['message_id'] != resp3_data['messages'][1]['message_id']
    assert resp3_data['messages'][0]['u_id'] == reg_two_users_and_create_two_channels['u_id1']
    assert resp3_data['messages'][1]['u_id'] == reg_two_users_and_create_two_channels['u_id1']
    assert resp3_data['messages'][0]['message'] == 'cool'
    assert resp3_data['messages'][1]['message'] == 'hi'
    assert resp3_data['messages'][0]['time_sent'] >= resp3_data['messages'][1]['time_sent']

def test_two_users_one_message(reg_two_users_and_create_two_channels):
    resp1 = requests.post(config.url + 'message/send/v1', json={'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'message': 'hi'})
    assert resp1.status_code == OK
    resp2 = requests.post(config.url + 'message/send/v1', json={'token': reg_two_users_and_create_two_channels['token2'], 'channel_id': reg_two_users_and_create_two_channels['ch_id2'], 'message': 'cool'})
    assert resp2.status_code == OK
    resp3 = requests.get(config.url + 'channel/messages/v2', json={'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'start': 0})
    assert resp3.status_code == OK
    resp3_data = resp3.json()
    resp4 = requests.get(config.url + 'channel/messages/v2', json={'token': reg_two_users_and_create_two_channels['token2'], 'channel_id': reg_two_users_and_create_two_channels['ch_id2'], 'start': 0})
    assert resp4.status_code == OK
    resp4_data = resp3.json()
    assert resp3_data['start'] == 0
    assert resp3_data['end'] == -1
    assert resp4_data['start'] == 0
    assert resp4_data['end'] == -1
    assert resp3_data['messages'][0]['message_id'] != resp4_data['messages'][0]['message_id']
    assert resp3_data['messages'][0]['u_id'] == reg_two_users_and_create_two_channels['u_id1']
    assert resp4_data['messages'][0]['u_id'] == reg_two_users_and_create_two_channels['u_id2']
    assert resp4_data['messages'][0]['message'] == 'cool'
    assert resp3_data['messages'][0]['message'] == 'hi'
    assert resp4_data['messages'][0]['time_sent'] >= resp3_data['messages'][0]['time_sent']

#edit errors
def test_message_edit_invalid_token(reg_two_users_and_create_two_channels):
    resp = requests.put(config.url + 'message/edit/v1', json={'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c', 'message_id': 0, 'message': 'hi'})
    assert resp.status_code == A_ERR

def test_message_edit_expired_token(reg_two_users_and_create_two_channels):
    resp1 = requests.post(config.url + 'auth/logout/v1', json={'token': reg_two_users_and_create_two_channels['token1']})
    assert resp1.status_code == OK
    resp = requests.put(config.url + 'message/edit/v1', json={'token': reg_two_users_and_create_two_channels['token1'], 'message_id': 0, 'message': 'hi'})
    assert resp.status_code == A_ERR

def test_message_edit_unauthorised(reg_two_users_and_create_two_channels):
    resp1 = requests.post(config.url + 'message/send/v1', json={'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'message': 'hi'})
    assert resp1.status_code == OK
    resp1_data = resp1.json()
    resp2 = requests.put(config.url + 'message/edit/v1', json={'token': reg_two_users_and_create_two_channels['token2'], 'message_id': resp1_data['message_id'], 'message': 'hi1'})
    assert resp2.status_code == A_ERR

def test_message_edit_invalid_id(reg_two_users_and_create_two_channels):
    resp = requests.put(config.url + 'message/edit/v1', json={'token': reg_two_users_and_create_two_channels['token1'], 'message_id': 123312321345, 'message': 'hi'})
    assert resp.status_code == I_ERR

def test_message_edit_bad_length(reg_two_users_and_create_two_channels):
    resp1 = requests.post(config.url + 'message/send/v1', json={'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'message': 'hi'})
    assert resp1.status_code == OK
    resp1_data = resp1.json()
    msg = 'a'
    for i in range(1000):
        msg += 'a'
    resp2 = requests.put(config.url + 'message/edit/v1', json={'token': reg_two_users_and_create_two_channels['token1'], 'message_id': resp1_data['message_id'], 'message': msg})
    assert resp2.status_code == I_ERR

#edit working
def test_message_edit_basic(reg_two_users_and_create_two_channels):
    resp1 = requests.post(config.url + 'message/send/v1', json={'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'message': 'hi'})
    assert resp1.status_code == OK
    resp1_data = resp1.json()
    resp2 = requests.put(config.url + 'message/edit/v1', json={'token': reg_two_users_and_create_two_channels['token1'], 'message_id': resp1_data['message_id'], 'message': 'lol'})
    assert resp2.status_code == OK
    resp3 = requests.get(config.url + 'channel/messages/v2', json={'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'start': 0})
    assert resp3.status_code == OK
    resp_data = resp3.json()
    assert resp_data['messages'][0]['message'] == 'lol'

def test_message_edit_owner(reg_two_users_and_create_two_channels):
    resp0 = requests.post(config.url + 'channel/join/v2', json={'token':reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id2']})
    assert resp0.status_code == OK
    resp1 = requests.post(config.url + 'message/send/v1', json={'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id2'], 'message': 'hi'})
    assert resp1.status_code == OK
    resp1_data = resp1.json()
    resp2 = requests.put(config.url + 'message/edit/v1', json={'token': reg_two_users_and_create_two_channels['token2'], 'message_id': resp1_data['message_id'], 'message': 'lol'})
    assert resp2.status_code == OK
    resp3 = requests.get(config.url + 'channel/messages/v2', json={'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id2'], 'start': 0})
    assert resp3.status_code == OK
    resp_data = resp3.json()
    assert resp_data['messages'][0]['message'] == 'lol'

def test_message_edit_global_owner(reg_two_users_and_create_two_channels):
    resp0 = requests.post(config.url + 'channel/join/v2', json={'token':reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id2']})
    assert resp0.status_code == OK
    resp1 = requests.post(config.url + 'message/send/v1', json={'token': reg_two_users_and_create_two_channels['token2'], 'channel_id': reg_two_users_and_create_two_channels['ch_id2'], 'message': 'hi'})
    assert resp1.status_code == OK
    resp1_data = resp1.json()
    resp2 = requests.put(config.url + 'message/edit/v1', json={'token': reg_two_users_and_create_two_channels['token1'], 'message_id': resp1_data['message_id'], 'message': 'lol'})
    assert resp2.status_code == OK
    resp3 = requests.get(config.url + 'channel/messages/v2', json={'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id2'], 'start': 0})
    assert resp3.status_code == OK
    resp_data = resp3.json()
    assert resp_data['messages'][0]['message'] == 'lol'

#remove errors
def test_message_remove_invalid_token(reg_two_users_and_create_two_channels):
    resp = requests.delete(config.url + 'message/remove/v1', json={'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c', 'message_id': 0})
    assert resp.status_code == A_ERR

def test_message_remove_expired_token(reg_two_users_and_create_two_channels):
    resp1 = requests.post(config.url + 'auth/logout/v1', json={'token': reg_two_users_and_create_two_channels['token1']})
    assert resp1.status_code == OK
    resp = requests.delete(config.url + 'message/remove/v1', json={'token': reg_two_users_and_create_two_channels['token1'], 'message_id': 0})
    assert resp.status_code == A_ERR

def test_message_remove_unauthorised(reg_two_users_and_create_two_channels):
    resp1 = requests.post(config.url + 'message/send/v1', json={'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1']})
    assert resp1.status_code == OK
    resp1_data = resp1.json()
    resp2 = requests.delete(config.url + 'message/remove/v1', json={'token': reg_two_users_and_create_two_channels['token2'], 'message_id': resp1_data['message_id']})
    assert resp2.status_code == A_ERR

def test_message_remove_invalid_id(reg_two_users_and_create_two_channels):
    resp = requests.delete(config.url + 'message/remove/v1', json={'token': reg_two_users_and_create_two_channels['token1'], 'message_id': 123312321345})
    assert resp.status_code == I_ERR

#remove working
def test_message_remove_basic(reg_two_users_and_create_two_channels):
    resp1 = requests.post(config.url + 'message/send/v1', json={'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'message': 'hi'})
    assert resp1.status_code == OK
    resp1_data = resp1.json()
    resp2 = requests.delete(config.url + 'message/remove/v1', json={'token': reg_two_users_and_create_two_channels['token1'], 'message_id': resp1_data['message_id']})
    assert resp2.status_code == OK
    resp3 = requests.get(config.url + 'channel/messages/v2', json={'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'start': 0})
    assert resp3.status_code == OK
    resp_data = resp3.json()
    assert len(resp_data['messages']) == 0

def test_message_remove_owner(reg_two_users_and_create_two_channels):
    resp0 = requests.post(config.url + 'channel/join/v2', json={'token':reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id2']})
    assert resp0.status_code == OK
    resp1 = requests.post(config.url + 'message/send/v1', json={'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id2'], 'message': 'hi'})
    assert resp1.status_code == OK
    resp1_data = resp1.json()
    resp2 = requests.delete(config.url + 'message/remove/v1', json={'token': reg_two_users_and_create_two_channels['token2'], 'message_id': resp1_data['message_id']})
    assert resp2.status_code == OK
    resp3 = requests.get(config.url + 'channel/messages/v2', json={'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id2'], 'start': 0})
    assert resp3.status_code == OK
    resp_data = resp3.json()
    assert len(resp_data['messages']) == 0

def test_message_remove_global_owner(reg_two_users_and_create_two_channels):
    resp0 = requests.post(config.url + 'channel/join/v2', json={'token':reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id2']})
    assert resp0.status_code == OK
    resp1 = requests.post(config.url + 'message/send/v1', json={'token': reg_two_users_and_create_two_channels['token2'], 'channel_id': reg_two_users_and_create_two_channels['ch_id2'], 'message': 'hi'})
    assert resp1.status_code == OK
    resp1_data = resp1.json()
    resp2 = requests.delete(config.url + 'message/remove/v1', json={'token': reg_two_users_and_create_two_channels['token1'], 'message_id': resp1_data['message_id']})
    assert resp2.status_code == OK
    resp3 = requests.get(config.url + 'channel/messages/v2', json={'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id2'], 'start': 0})
    assert resp3.status_code == OK
    resp_data = resp3.json()
    assert len(resp_data['messages']) == 0
    '''