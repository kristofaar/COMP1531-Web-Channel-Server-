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

#create errors
def test_channels_create_invalid_token(reg_two_users_and_create_two_channels):
    resp = requests.post(config.url + 'channels/create/v2', json={'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c', 'name': '123', 'is_public': True})
    assert resp.status_code == A_ERR

def test_channels_create_expired_token(reg_two_users_and_create_two_channels):
    resp1 = requests.post(config.url + 'auth/logout/v1', json={'token': reg_two_users_and_create_two_channels['token1']})
    assert resp1.status_code == OK
    resp2 = requests.post(config.url + 'channels/create/v2', json={'token': reg_two_users_and_create_two_channels['token1'], 'name': '123', 'is_public': True})
    assert resp2.status_code == A_ERR

def test_channels_create_invalid_length(reg_two_users_and_create_two_channels):
    resp1 = requests.post(config.url + 'channels/create/v2', json={'token': reg_two_users_and_create_two_channels['token1'], 'name': '', 'is_public': True})
    assert resp1.status_code == I_ERR
    resp2 = requests.post(config.url + 'channels/create/v2', json={'token': reg_two_users_and_create_two_channels['token1'], 'name': 'ds87dsa7g78dsag78dsga8gdsjkhsdjkhjkdsahjkasdhsdsaddsadsa', 'is_public': True})
    assert resp2.status_code == I_ERR

#create working
def test_channels_create(reg_two_users_and_create_two_channels):
    resp1 = requests.post(config.url + 'channels/create/v2', json={'token': reg_two_users_and_create_two_channels['token1'], 'name': 'AnodaCoolChannel', 'is_public': True})
    assert resp1.status_code == OK
    resp2 = requests.get(config.url + 'channels/list/v2', json={'token': reg_two_users_and_create_two_channels['token1']})
    assert resp2.status_code == OK
    resp1_data = resp1.json()
    resp2_data = resp2.json()
    assert resp2_data['channels'][1]['channel_id'] == resp1_data['channel_id']
    assert resp2_data['channels'][1]['name'] == 'AnodaCoolChannel'

#list errors
def test_channels_list_invalid_token(reg_two_users_and_create_two_channels):
    resp = requests.get(config.url + 'channels/list/v2', json={'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c'})
    assert resp.status_code == A_ERR

def test_channels_list_expired_token(reg_two_users_and_create_two_channels):
    resp1 = requests.post(config.url + 'auth/logout/v1', json={'token': reg_two_users_and_create_two_channels['token1']})
    assert resp1.status_code == OK
    resp2 = requests.post(config.url + 'channels/list/v2', json={'token': reg_two_users_and_create_two_channels['token1']})
    assert resp2.status_code == A_ERR

#list working
def test_channels_list(reg_two_users_and_create_two_channels):
    resp1 = requests.post(config.url + 'channels/create/v2', json={'token': reg_two_users_and_create_two_channels['token1'], 'name': 'AnodaCoolChannel', 'is_public': True})
    assert resp1.status_code == OK
    resp2 = requests.get(config.url + 'channels/list/v2', json={'token': reg_two_users_and_create_two_channels['token1']})
    assert resp2.status_code == OK
    resp1_data = resp1.json()
    resp2_data = resp2.json()
    assert resp2_data['channels'][0]['channel_id'] == reg_two_users_and_create_two_channels['ch_id1']
    assert resp2_data['channels'][0]['name'] == 'CoolChannelName'
    assert resp2_data['channels'][1]['channel_id'] == resp1_data['channel_id']
    assert resp2_data['channels'][1]['name'] == 'AnodaCoolChannel'

#listall errors
def test_channels_listall_invalid_token(reg_two_users_and_create_two_channels):
    resp = requests.get(config.url + 'channels/listall/v2', json={'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c'})
    assert resp.status_code == A_ERR

def test_channels_listall_expired_token(reg_two_users_and_create_two_channels):
    resp1 = requests.post(config.url + 'auth/logout/v1', json={'token': reg_two_users_and_create_two_channels['token1']})
    assert resp1.status_code == OK
    resp2 = requests.post(config.url + 'channels/listall/v2', json={'token': reg_two_users_and_create_two_channels['token1']})
    assert resp2.status_code == A_ERR

#listall working
def test_channels_listall(reg_two_users_and_create_two_channels):
    resp1 = requests.get(config.url + 'channels/list/v2', json={'token': reg_two_users_and_create_two_channels['token1']})
    assert resp1.status_code == OK
    resp1_data = resp1.json()
    assert resp1_data['channels'][0]['channel_id'] == reg_two_users_and_create_two_channels['ch_id1']
    assert resp1_data['channels'][0]['name'] == 'CoolChannelName'
    assert resp1_data['channels'][1]['channel_id'] == reg_two_users_and_create_two_channels['ch_id2']
    assert resp1_data['channels'][1]['name'] == 'NiceChannel'
    '''