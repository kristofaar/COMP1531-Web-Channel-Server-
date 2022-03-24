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
    resp1 = requests.post(config.url + 'auth/register/v2', json={'email': '1@test.test', 'password': '1testtest', 'name_first': 'first_test', 'name_last': 'first_test'})
    assert resp1.status_code == OK
    resp2 = requests.post(config.url + 'auth/register/v2', json={'email': '2@lol.lol', 'password': '2abcabc', 'name_first': 'Second_Jane', 'name_last': 'Second_Austen'})
    assert resp2.status_code == OK
    resp1_data = resp1.json()
    resp2_data = resp2.json()
    resp3 = requests.post(config.url + 'dm/create/v1', json={'token': resp1_data['token'], 'u_ids': [resp2_data['auth_user_id']]})
    assert resp3.status_code == OK
    resp3_data = resp3.json()
    return {'token1': resp1_data['token'], 'token2': resp2_data['token'], 
    'u_id1': resp1_data['auth_user_id'], 'u_id2': resp2_data['auth_user_id'], 
    'dm_id': resp3_data['dm_id']}
@pytest.fixture
def reg_another_two_users_and_dm():
    reg1 = requests.post(config.url + 'auth/register/v2', json={'email': '3@test.test', 'password': '3testtest', 'name_first': 'third_name', 'name_last': 'third_last_name'})
    assert reg1.status_code == OK
    reg2 = requests.post(config.url + 'auth/register/v2', json={'email': '4@lol.lol', 'password': '4abcabc', 'name_first': 'Fourth_boi', 'name_last': 'Fourth_last'})
    assert reg2.status_code == OK
    reg1_data = reg1.json()
    reg2_data = reg2.json()
    dmcreate = requests.post(config.url + 'dm/create/v1', json={'token': reg1_data['token'], 'u_ids': [reg2_data['auth_user_id']]})
    assert dmcreate.status_code == OK
    dmcreate_data = dmcreate.json()
    dmdet = requests.get(config.url + 'dm/details/v1', params={'token': reg1_data['token'], 'dm_id': dmcreate_data['dm_id']})
    dmdet_data = dmdet.json()
    return {'token1': reg1_data['token'], 'token2': reg2_data['token'], 
    'u_id1': reg1_data['auth_user_id'], 'u_id2': reg2_data['auth_user_id'], 
    'dm_id': dmcreate_data['dm_id'], 'dm_name': dmdet_data['name']}

#create errors
def test_dm_create_invalid_token(reg_two_users_and_create_dm):
    resp = requests.post(config.url + 'dm/create/v1', json={'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c', 'u_ids': [reg_two_users_and_create_dm['u_id2']]})
    assert resp.status_code == A_ERR

def test_dm_create_expired_token(reg_two_users_and_create_dm):
    resp1 = requests.post(config.url + 'auth/logout/v1', json={'token': reg_two_users_and_create_dm['token1']})
    assert resp1.status_code == OK
    resp2 = requests.post(config.url + 'dm/create/v1', json={'token': reg_two_users_and_create_dm['token1'], 'u_ids': [reg_two_users_and_create_dm['u_id2']]})
    assert resp2.status_code == A_ERR

#list errors

#remove errors

#detail errors

#test working create
def test_dm_create_basic(reg_two_users_and_create_dm):
    resp2 = requests.get(config.url + 'dm/list/v1', params={'token': reg_two_users_and_create_dm['token1']})
    assert resp2.status_code == OK
    resp2_data = resp2.json()
    assert resp2_data['dms'][0]['dm_id'] == reg_two_users_and_create_dm['dm_id']
    #need to get a case for handles working
    #assert resp2_data['dm'][0]['name'] == ''

#test working dm list
def test_dm_list_basic(reg_another_two_users_and_dm):
    dmlist = requests.get(config.url + 'dm/list/v1', params={'token': reg_another_two_users_and_dm['token1']})
    assert dmlist.status_code == OK
    dmlist_data = dmlist.json()
    assert dmlist_data['dms'] == [{'dm_id': reg_another_two_users_and_dm['dm_id'], 'name': reg_another_two_users_and_dm['dm_name']}]

def test_dm_list_multiple(reg_two_users_and_create_dm, reg_another_two_users_and_dm):
    dmcreate = requests.post(config.url + 'dm/create/v1', json={'token': reg_two_users_and_create_dm['token1'], 'u_ids': [reg_another_two_users_and_dm['u_id2']]})
    assert dmcreate.status_code == OK
    dmcreate_data = dmcreate.json()

    dmlist = requests.get(config.url + 'dm/list/v1', params={'token': reg_two_users_and_create_dm['token1']})
    assert dmlist.status_code == OK
    dmlist_data = dmlist.json()

    dmdet1 = requests.get(config.url + 'dm/details/v1', params={'token': reg_two_users_and_create_dm['token1'], 'dm_id': reg_two_users_and_create_dm['dm_id']})
    assert dmdet1.status_code == OK
    dmdet1_data = dmdet1.json()
    
    dmdet2 = requests.get(config.url + 'dm/details/v1', params={'token': reg_two_users_and_create_dm['token1'], 'dm_id': dmcreate_data['dm_id']})
    assert dmdet2.status_code == OK
    dmdet2_data = dmdet2.json()

    assert dmlist_data['dms'] == [{'dm_id': reg_two_users_and_create_dm['dm_id'], 'name': dmdet1_data['name']},{'dm_id': dmcreate_data['dm_id'], 'name': dmdet2_data['name']}]

#test working dm remove

def test_dm_remove_basic(reg_two_users_and_create_dm):
    remove = requests.delete(config.url + 'dm/remove/v1', json={'token': reg_two_users_and_create_dm['token1'], 'dm_id': reg_two_users_and_create_dm['dm_id']})
    dmlist = requests.get(config.url + 'dm/list/v1', params={'token': reg_two_users_and_create_dm['token1']})
    assert dmlist.status_code == OK
    dmlist_data = dmlist.json()
    assert dmlist_data['dms'] == []

#test working dm details
def test_dm_details_basic(reg_two_users_and_create_dm):
    resp = requests.get(config.url + 'dm/details/v1', params={'token': reg_two_users_and_create_dm['token1'], 'dm_id': reg_two_users_and_create_dm['dm_id']})
    assert resp.status_code == OK
    resp_data = resp.json()
    #assert resp_data['name'] == 
    assert resp_data['members'][0]['u_id'] == reg_two_users_and_create_dm['u_id1']
    assert resp_data['members'][1]['u_id'] == reg_two_users_and_create_dm['u_id2']