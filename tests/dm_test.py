import pytest
import requests
import json
from src import config


A_ERR = 403
I_ERR = 400
OK = 200

@pytest.fixture
def reg_two_users_and_create_dm():
    clear_resp = requests.delete(config.url + 'clear/v1')
    assert clear_resp.status_code == OK
    resp1 = requests.post(config.url + 'auth/register/v2', json={'email': 'teast@test.test', 'password': 'testtesttest', 'name_first': 'test', 'name_last': 'test'})
    assert resp1.status_code == OK
    resp2 = requests.post(config.url + 'auth/register/v2', json={'email': 'lol@lol.lol', 'password': '123abc123abc', 'name_first': 'Jane', 'name_last': 'Austen'})
    assert resp2.status_code == OK
    resp1_data = resp1.json()
    resp2_data = resp2.json()
    resp3 = requests.post(config.url + 'dm/create/v1', json={'token': resp1_data['token'], 'u_ids': [resp2_data['auth_user_id']]})
    assert resp3.status_code == OK
    resp3_data = resp3.json()
    return {'token1': resp1_data['token'], 'token2': resp2_data['token'], 'u_id1': resp1_data['auth_user_id'], 'u_id2': resp2_data['auth_user_id'], 'dm_id': resp3_data['dm_id']}

#create errors
def test_dm_create_invalid_token(reg_two_users_and_create_dm):
    resp = requests.post(config.url + 'dm/create/v1', json={'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c', 'u_ids': [reg_two_users_and_create_dm['u_id2']]})
    assert resp.status_code == A_ERR

def test_dm_create_expired_token(reg_two_users_and_create_dm):
    resp1 = requests.post(config.url + 'auth/logout/v1', json={'token': reg_two_users_and_create_dm['token1']})
    assert resp1.status_code == OK
    resp2 = requests.post(config.url + 'dm/create/v1', json={'token': reg_two_users_and_create_dm['token1'], 'u_ids': [reg_two_users_and_create_dm['u_id2']]})
    assert resp2.status_code == A_ERR


#test working create
def test_dm_create(reg_two_users_and_create_dm):
    resp1 = requests.post(config.url + 'dm/create/v1', json={'token': reg_two_users_and_create_dm['token1'], 'u_ids': [reg_two_users_and_create_dm['u_id2']]})
    assert resp1.status_code == OK
    resp2 = requests.get(config.url + 'dm/list/v1', params={'token': reg_two_users_and_create_dm['token1']})
    assert resp2.status_code == OK
    resp1_data = resp1.json()
    resp2_data = resp2.json()
    assert resp2_data['dms'][1]['dm_id'] == resp1_data['dm_id']
    #need to get a case for handles working
    #assert resp2_data['dm'][0]['name'] == ''

#test working dm list
def test_dm_list(reg_two_users_and_create_dm):
    resp1 = requests.post(config.url + 'dm/create/v1', json={'token': reg_two_users_and_create_dm['token1'], 'u_ids': [reg_two_users_and_create_dm['u_id2']]})
    assert resp1.status_code == OK
    resp2 = requests.get(config.url + 'dm/list/v1', params={'token': reg_two_users_and_create_dm['token1']})
    assert resp2.status_code == OK
    
    resp2_data = resp2.json()
    assert resp2_data['dms'][0]['dm_id'] == reg_two_users_and_create_dm['dm_id']
    #assert resp2_data['dm'][0]['name'] == '' 

def test_dm_details(reg_two_users_and_create_dm):
    resp = requests.get(config.url + 'dm/details/v1', params={'token': reg_two_users_and_create_dm['token1'], 'dm_id': reg_two_users_and_create_dm['dm_id']})
    assert resp.status_code == OK
    resp_data = resp.json()
    #assert resp_data['name'] == 
    assert resp_data['members'][0]['u_id'] == reg_two_users_and_create_dm['u_id1']
    assert resp_data['members'][1]['u_id'] == reg_two_users_and_create_dm['u_id2']