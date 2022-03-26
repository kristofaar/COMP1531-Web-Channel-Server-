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
    reg1 = requests.post(config.url + 'auth/register/v2', json={'email': '1@test.test', 'password': '1testtest', 'name_first': 'first_test', 'name_last': 'first_test'})
    assert reg1.status_code == OK
    reg2 = requests.post(config.url + 'auth/register/v2', json={'email': '2@lol.lol', 'password': '2abcabc', 'name_first': 'Second_Jane', 'name_last': 'Second_Austen'})
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

def test_dm_create_duplicate_invited_users(reg_two_users_and_create_dm):
    u_ids = [reg_two_users_and_create_dm['u_id2'], reg_two_users_and_create_dm['u_id2']]
    resp2 = requests.post(config.url + 'dm/create/v1', json={'token': reg_two_users_and_create_dm['token1'], 'u_ids': u_ids})
    assert resp2.status_code == I_ERR

def test_dm_create_invalid_invited_user(reg_two_users_and_create_dm):
    u_ids = [-8932748923]
    resp2 = requests.post(config.url + 'dm/create/v1', json={'token': reg_two_users_and_create_dm['token1'], 'u_ids': u_ids})
    assert resp2.status_code == I_ERR

#list errors
def test_dm_list_invalid_token(reg_two_users_and_create_dm):
    dmlist = requests.get(config.url + 'dm/list/v1', params={'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c'})
    assert dmlist.status_code == A_ERR

#remove errors
def test_dm_remove_invalid_token(reg_two_users_and_create_dm):
    remove = requests.delete(config.url + 'dm/remove/v1', json={'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c',
                                                                'dm_id': reg_two_users_and_create_dm['dm_id']})
    assert remove.status_code == A_ERR
def test_non_creator_remove(reg_two_users_and_create_dm):
    remove = requests.delete(config.url + 'dm/remove/v1', json={'token': reg_two_users_and_create_dm['token2'], 'dm_id': reg_two_users_and_create_dm['dm_id']})
    assert remove.status_code == A_ERR

def test_not_in_dm_remove(reg_two_users_and_create_dm, reg_another_two_users_and_dm):
    remove = requests.delete(config.url + 'dm/remove/v1', json={'token': reg_another_two_users_and_dm['token1'], 'dm_id': reg_two_users_and_create_dm['dm_id']})
    assert remove.status_code == A_ERR
    
def test_invalid_dm_id(reg_two_users_and_create_dm):
    remove = requests.delete(config.url + 'dm/remove/v1', json={'token': reg_two_users_and_create_dm['token1'], 'dm_id': -9128349012})
    assert remove.status_code == I_ERR
#detail errors

#dm leave errors
def test_leave_invalid_token(reg_two_users_and_create_dm):
    leave = requests.post(config.url + 'dm/leave/v1', json={'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c' , 'dm_id': reg_two_users_and_create_dm['dm_id']})
    assert leave.status_code == A_ERR
def test_leave_invalid_dm_id(reg_two_users_and_create_dm):
    leave = requests.post(config.url + 'dm/leave/v1', json={'token': reg_two_users_and_create_dm['token2'], 'dm_id': -129831941})
    assert leave.status_code == I_ERR

def test_leave_unauthorised_user(reg_two_users_and_create_dm, reg_another_two_users_and_dm):
    leave = requests.post(config.url + 'dm/leave/v1', json={'token': reg_another_two_users_and_dm['token1'], 'dm_id': reg_two_users_and_create_dm['dm_id']})
    assert leave.status_code == A_ERR

#test working create
def test_dm_create_basic(reg_two_users_and_create_dm):
    resp2 = requests.get(config.url + 'dm/list/v1', params={'token': reg_two_users_and_create_dm['token1']})
    assert resp2.status_code == OK
    resp2_data = resp2.json()
    assert resp2_data['dms'][0]['dm_id'] == reg_two_users_and_create_dm['dm_id']

#test working dm list
def test_dm_list_basic(reg_two_users_and_create_dm):
    dmlist = requests.get(config.url + 'dm/list/v1', params={'token': reg_two_users_and_create_dm['token1']})
    assert dmlist.status_code == OK
    dmlist_data = dmlist.json()
    assert dmlist_data['dms'] == [{'dm_id': reg_two_users_and_create_dm['dm_id'], 'name': reg_two_users_and_create_dm['dm_name']}]

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
    assert remove.status_code == OK
    dmlist = requests.get(config.url + 'dm/list/v1', params={'token': reg_two_users_and_create_dm['token1']})
    assert dmlist.status_code == OK
    dmlist_data = dmlist.json()
    assert dmlist_data['dms'] == []

def test_dm_remove_multiple_people_in_dm(reg_two_users_and_create_dm, reg_another_two_users_and_dm):
    dmcreate = requests.post(config.url + 'dm/create/v1', json={'token': reg_two_users_and_create_dm['token1'], 'u_ids': [reg_another_two_users_and_dm['u_id1'], reg_two_users_and_create_dm['u_id2']]})
    assert dmcreate.status_code == OK
    dmcreate_data = dmcreate.json()
    print(dmcreate_data['dm_id'])
    remove = requests.delete(config.url + 'dm/remove/v1', json={'token': reg_two_users_and_create_dm['token1'], 'dm_id': dmcreate_data['dm_id']})
    assert remove.status_code == OK

    dmlist = requests.get(config.url + 'dm/list/v1', params={'token': reg_two_users_and_create_dm['token1']})
    assert dmlist.status_code == OK
    dmlist_data = dmlist.json()

    dmlist2 = requests.get(config.url + 'dm/list/v1', params={'token': reg_another_two_users_and_dm['token1']})
    assert dmlist2.status_code == OK
    dmlist2_data = dmlist2.json()

    dmlist3 = requests.get(config.url + 'dm/list/v1', params={'token': reg_two_users_and_create_dm['token2']})
    assert dmlist3.status_code == OK
    dmlist3_data = dmlist3.json()

    assert len(dmlist_data['dms']) == 1
    assert len(dmlist2_data['dms']) == 1
    assert len(dmlist3_data['dms']) == 1

#test error dm details

def test_details_invalid_token(reg_two_users_and_create_dm):
    resp = requests.get(config.url + 'dm/details/v1', params={'token': 'invalid_token' , 'dm_id': reg_two_users_and_create_dm['dm_id']})
    assert resp.status_code == A_ERR

def test_details_invalid_dm_id(reg_two_users_and_create_dm):
    resp = requests.get(config.url + 'dm/details/v1', params={'token': reg_two_users_and_create_dm['token2'], 'dm_id': -1})
    assert resp.status_code == I_ERR

def test_details_not_member(reg_two_users_and_create_dm, reg_another_two_users_and_dm):
    resp = requests.get(config.url + 'dm/details/v1', params={'token': reg_two_users_and_create_dm['token2'], 'dm_id': reg_another_two_users_and_dm['dm_id']})
    assert resp.status_code == A_ERR

#test working dm details
def test_dm_details_basic(reg_two_users_and_create_dm):
    resp = requests.get(config.url + 'dm/details/v1', params={'token': reg_two_users_and_create_dm['token1'], 'dm_id': reg_two_users_and_create_dm['dm_id']})
    assert resp.status_code == OK
    resp_data = resp.json()
    assert resp_data['members'][0]['u_id'] == reg_two_users_and_create_dm['u_id1']
    assert resp_data['members'][1]['u_id'] == reg_two_users_and_create_dm['u_id2']

def test_dm_leave_basic(reg_two_users_and_create_dm):
    leave = requests.post(config.url + 'dm/leave/v1', json={'token': reg_two_users_and_create_dm['token2'], 'dm_id': reg_two_users_and_create_dm['dm_id']})
    assert leave.status_code == OK

    dmlist = requests.get(config.url + 'dm/list/v1', params={'token': reg_two_users_and_create_dm['token2']})
    assert dmlist.status_code == OK
    dmlist_data = dmlist.json()
   
    assert len(dmlist_data['dms']) == 0


#messages errors
def test_dm_messages_invalid_token(reg_two_users_and_create_dm):
    resp = requests.get(config.url + 'dm/messages/v1', params={'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c', 'channel_id': reg_two_users_and_create_dm['dm_id'], 'start': 0})
    assert resp.status_code == A_ERR

def test_dm_messages_expired_token(reg_two_users_and_create_dm):
    resp1 = requests.post(config.url + 'auth/logout/v1', json={'token': reg_two_users_and_create_dm['token1']})
    assert resp1.status_code == OK
    resp2 = requests.get(config.url + 'dm/messages/v1', params={'token': reg_two_users_and_create_dm['token1'], 'dm_id': reg_two_users_and_create_dm['dm_id'], 'start': 0})
    assert resp2.status_code == A_ERR

def test_dm_messages_unauthorised(reg_two_users_and_create_dm, reg_another_two_users_and_dm):
    resp = requests.get(config.url + 'dm/messages/v1', params={'token': reg_another_two_users_and_dm['token2'], 'dm_id': reg_two_users_and_create_dm['dm_id'], 'start': 0})
    assert resp.status_code == A_ERR

def test_dm_messages_invalid_channel(reg_two_users_and_create_dm):
    resp = requests.get(config.url + 'dm/messages/v1', params={'token': reg_two_users_and_create_dm['token1'], 'dm_id': -1, 'start': 0})
    assert resp.status_code == I_ERR

def test_dm_messages_big_start(reg_two_users_and_create_dm):
    resp = requests.get(config.url + 'dm/messages/v1', params={'token': reg_two_users_and_create_dm['token1'], 'dm_id': reg_two_users_and_create_dm['dm_id'], 'start': 1})
    assert resp.status_code == I_ERR

#messages working
def test_dm_messages_empty(reg_two_users_and_create_dm):
    resp = requests.get(config.url + 'dm/messages/v1', params={'token': reg_two_users_and_create_dm['token1'], 'dm_id': reg_two_users_and_create_dm['dm_id'], 'start': 0})
    assert resp.status_code == OK
    resp_data = resp.json()
    assert resp_data['start'] == 0
    assert resp_data['end'] == -1
    assert resp_data['messages'] == []

def test_dm_small_messages(reg_two_users_and_create_dm):
    for i in range(2):
        resp = requests.post(config.url + 'message/senddm/v1', json={
                             'token': reg_two_users_and_create_dm['token1'], 'dm_id': reg_two_users_and_create_dm['dm_id'], 'message': str(i)})
        assert resp.status_code == OK
    resp = requests.get(config.url + 'dm/messages/v1', params={
                        'token': reg_two_users_and_create_dm['token1'], 'dm_id': reg_two_users_and_create_dm['dm_id'], 'start': 0})
    assert resp.status_code == OK
    resp_data = resp.json()
    assert resp_data['start'] == 0
    assert resp_data['end'] == -1
    for i in range(2):
        assert resp_data['messages'][i]['message'] == str(1 - i)


def test_dm_big_messages(reg_two_users_and_create_dm):
    for i in range(150):
        resp = requests.post(config.url + 'message/senddm/v1', json={
                             'token': reg_two_users_and_create_dm['token1'], 'dm_id': reg_two_users_and_create_dm['dm_id'], 'message': str(i)})
        assert resp.status_code == OK
    resp = requests.get(config.url + 'dm/messages/v1', params={
                        'token': reg_two_users_and_create_dm['token1'], 'dm_id': reg_two_users_and_create_dm['dm_id'], 'start': 0})
    assert resp.status_code == OK
    resp_data = resp.json()
    assert resp_data['start'] == 0
    assert resp_data['end'] == 50
    for i in range(50):
        assert resp_data['messages'][i]['message'] == str(149 - i)
    resp = requests.get(config.url + 'dm/messages/v1', params={
                        'token': reg_two_users_and_create_dm['token1'], 'dm_id': reg_two_users_and_create_dm['dm_id'], 'start': 100})
    assert resp.status_code == OK
    resp_data = resp.json()
    assert resp_data['start'] == 100
    assert resp_data['end'] == -1
    for i in range(50):
        assert resp_data['messages'][i]['message'] == str(49 - i)
