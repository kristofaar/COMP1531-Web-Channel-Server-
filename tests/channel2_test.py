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
    return {'token1': resp1_data['token'], 'token2': resp2_data['token'], 'u_id1': resp1_data['auth_user_id'], 'u_id2': resp2_data['auth_user_id'], 'ch_id1': resp3_data['channel_id'], 'ch_id2': resp4_data['channel_id'],}

#details errors
def test_channel_details_invalid_token(reg_two_users_and_create_two_channels):
    resp = requests.get(config.url + 'channel/details/v2', json={'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c', 'channel_id': reg_two_users_and_create_two_channels['ch_id1']})
    assert resp.status_code == A_ERR

def test_channel_details_expired_token(reg_two_users_and_create_two_channels):
    resp1 = requests.post(config.url + 'auth/logout/v1', json={'token': reg_two_users_and_create_two_channels['token1']})
    assert resp1.status_code == OK
    resp2 = requests.post(config.url + 'channel/details/v2', json={'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1']})
    assert resp2.status_code == A_ERR

def test_channel_details_unauthorised(reg_two_users_and_create_two_channels):
    resp = requests.post(config.url + 'channel/details/v2', json={'token': reg_two_users_and_create_two_channels['token2'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1']})
    assert resp.status_code == A_ERR

def test_channel_details_invalid_channel(reg_two_users_and_create_two_channels):
    resp = requests.post(config.url + 'channel/details/v2', json={'token': reg_two_users_and_create_two_channels['token2'], 'channel_id': 123789})
    assert resp.status_code == I_ERR

#details working
    resp = requests.post(config.url + 'channel/details/v2', json={'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1']})
    assert resp.status_code == OK
    resp_data = resp.json()
    assert resp_data['name'] == 'CoolChannelName'
    assert resp_data['is_public'] == True
    assert resp_data['owner_members'][0]['u_id'] == reg_two_users_and_create_two_channels['u_id1']
    assert resp_data['all_members'][0]['u_id'] == reg_two_users_and_create_two_channels['u_id1']

