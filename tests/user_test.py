import pytest
import requests
import json
import datetime
from datetime import timezone
import time as t
from src import config

A_ERR = 403
I_ERR = 400
OK = 200

@pytest.fixture
def reg_user():
    clear_resp = requests.delete(config.url + "clear/v1")
    assert clear_resp.status_code == OK
    resp = requests.post(config.url + "auth/register/v2", json={"email": "1@test.test", "password": "1testtest", "name_first": "first_test", "name_last": "first_test"})
    assert resp.status_code == OK
    resp_data = resp.json()
    return {
        "token": resp_data["token"], 
        "u_id": resp_data["auth_user_id"],
    }

@pytest.fixture
def reg_two_users():
    clear_resp = requests.delete(config.url + 'clear/v1')
    assert clear_resp.status_code == OK
    resp1 = requests.post(config.url + 'auth/register/v2', json={'email': '1@test.test', 'password': '1testtest', 'name_first': 'first_test', 'name_last': 'first_test'})
    assert resp1.status_code == OK
    resp2 = requests.post(config.url + 'auth/register/v2', json={'email': '2@lol.lol', 'password': '2abcabc', 'name_first': 'Second_Jane', 'name_last': 'Second_Austen'})
    assert resp2.status_code == OK
    resp1_data = resp1.json()
    resp2_data = resp2.json()
    return {'token1': resp1_data['token'], 'token2': resp2_data['token'], 
    'u_id1': resp1_data['auth_user_id'], 'u_id2': resp2_data['auth_user_id']}

# Tests for users/all/v1
def test_users_two_users(reg_two_users):
    resp1 = requests.get(config.url + 'users/all/v1', params={'token': reg_two_users['token1']})
    assert resp1.status_code == OK
    resp1_data = resp1.json()
    assert resp1_data["users"][0]["u_id"] == reg_two_users["u_id1"]
    assert resp1_data["users"][1]["u_id"] == reg_two_users["u_id2"]
def test_users_invalid_token(reg_two_users):
    resp = requests.get(config.url + 'users/all/v1', params={'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c'})
    assert resp.status_code == A_ERR

# Tests for user/profile/v1
def test_user_profile_valid(reg_user):
    resp = requests.get(config.url + "user/profile/v1", params={"token": reg_user["token"], "u_id": reg_user["u_id"]})
    assert resp.status_code == OK
    resp_data = resp.json()
    assert resp_data["user"]["u_id"] == reg_user["u_id"]
def test_user_profile_invalid_token(reg_user):
    resp = requests.get(config.url + "user/profile/v1", params={"token": "invalid", "u_id": reg_user["u_id"]})
    assert resp.status_code == A_ERR
def test_user_profile_invalid_id(reg_user):
    resp = requests.get(config.url + "user/profile/v1", params={"token": reg_user["token"], "u_id": "-1"})
    assert resp.status_code == I_ERR

# Tests for user/profile/setname/v1
def test_setname_valid(reg_two_users):
    resp = requests.put(config.url + "user/profile/setname/v1", json={"token": reg_two_users["token1"], "name_first": "new_first", "name_last": "new_last"})
    assert resp.status_code == OK
    resp = requests.get(config.url + "user/profile/v1", params={"token": reg_two_users["token1"], "u_id": reg_two_users["u_id1"]})
    assert resp.status_code == OK
    resp_data = resp.json()
    assert resp_data["user"]["name_first"] == "new_first"
    assert resp_data["user"]["name_last"] == "new_last"
def test_setname_invalid_token(reg_user):
    resp = requests.put(config.url + "user/profile/setname/v1", json={"token": "invalid", "name_first": "new_first", "name_last": "new_last"})
    assert resp.status_code == A_ERR
def test_setname_invalid_name_first(reg_user):
    resp = requests.put(config.url + "user/profile/setname/v1", json={"token": reg_user["token"], "name_first": "A" * 100, "name_last": "new_last"})
    assert resp.status_code == I_ERR
def test_setname_invalid_name_last(reg_user):
    resp = requests.put(config.url + "user/profile/setname/v1", json={"token": reg_user["token"], "name_first": "new_first", "name_last": "A" * 100})
    assert resp.status_code == I_ERR

# Tests for user/profile/setemail/v1
def test_setemail_valid(reg_two_users):
    resp = requests.put(config.url + "user/profile/setemail/v1", json={"token": reg_two_users["token1"], "email": "3@lol.lol"})
    assert resp.status_code == OK
    resp = requests.get(config.url + "user/profile/v1", params={"token": reg_two_users["token1"], "u_id": reg_two_users["u_id1"]})
    assert resp.status_code == OK
    resp_data = resp.json()
    assert resp_data["user"]["email"] == "3@lol.lol"
def test_setemail_invalid_token(reg_user):
    resp = requests.put(config.url + "user/profile/setemail/v1", json={"token": "invalid", "email": "2@lol.lol"})
    assert resp.status_code == A_ERR
def test_setemail_invalid_email(reg_user):
    resp = requests.put(config.url + "user/profile/setemail/v1", json={"token": reg_user["token"], "email": "invalid"})
    assert resp.status_code == I_ERR
def test_setemail_duplicate_email(reg_two_users):
    resp = requests.put(config.url + "user/profile/setemail/v1", json={"token": reg_two_users["token1"], "email": "2@lol.lol"})
    assert resp.status_code == I_ERR

# Tests for user/profile/sethandle/v1
def test_sethandle_valid(reg_two_users):
    resp = requests.put(config.url + "user/profile/sethandle/v1", json={"token": reg_two_users["token1"], "handle_str": "newhandle"})
    assert resp.status_code == OK
    resp = requests.get(config.url + "user/profile/v1", params={"token": reg_two_users["token1"], "u_id": reg_two_users["u_id1"]})
    assert resp.status_code == OK
    resp_data = resp.json()
    assert resp_data["user"]["handle_str"] == "newhandle"
def test_sethandle_invalid_token(reg_user):
    resp = requests.put(config.url + "user/profile/sethandle/v1", json={"token": "invalid", "handle_str": "newhandle"})
    assert resp.status_code == A_ERR
def test_setemail_invalid_handle_len(reg_user):
    resp = requests.put(config.url + "user/profile/sethandle/v1", json={"token": reg_user["token"], "handle_str": "na"})
    assert resp.status_code == I_ERR
def test_setemail_non_alnum_handle(reg_user):
    resp = requests.put(config.url + "user/profile/sethandle/v1", json={"token": reg_user["token"], "handle_str": "abcde1*"})
    assert resp.status_code == I_ERR
def test_setemail_duplicate_handle(reg_two_users):
    resp = requests.put(config.url + "user/profile/sethandle/v1", json={"token": reg_two_users["token1"], "handle_str": 'secondjanesecondaust'})
    assert resp.status_code == I_ERR

#tests for user_stats
def test_user_stats_invalid_token():
    clear_resp = requests.delete(config.url + 'clear/v1')
    assert clear_resp.status_code == OK
    resp = requests.get(config.url + "user/stats/v1", params={"token": "invalid"})
    assert resp.status_code == A_ERR

def test_user_stats_initial(reg_two_users):
    resp = requests.get(config.url + "user/stats/v1", params={"token": reg_two_users['token1']})
    assert resp.status_code == OK
    resp_data = resp.json()
    assert resp_data['user_stats']['channels_joined'][0]['num_channels_joined'] == 0
    assert resp_data['user_stats']['channels_joined'][0]['time_stamp'] != 0
    assert resp_data['user_stats']['dms_joined'][0]['num_dms_joined'] == 0
    assert resp_data['user_stats']['dms_joined'][0]['time_stamp'] == resp_data['user_stats']['channels_joined'][0]['time_stamp']
    assert resp_data['user_stats']['messages_sent'][0]['num_messages_sent'] == 0
    assert resp_data['user_stats']['messages_sent'][0]['time_stamp'] == resp_data['user_stats']['channels_joined'][0]['time_stamp']
    assert resp_data['user_stats']['involvement_rate'] == 0
    resp = requests.get(config.url + "user/stats/v1", params={"token": reg_two_users['token2']})
    assert resp.status_code == OK
    resp_data = resp.json()
    assert resp_data['user_stats']['channels_joined'][0]['num_channels_joined'] == 0
    assert resp_data['user_stats']['channels_joined'][0]['time_stamp'] != 0
    assert resp_data['user_stats']['dms_joined'][0]['num_dms_joined'] == 0
    assert resp_data['user_stats']['dms_joined'][0]['time_stamp'] == resp_data['user_stats']['channels_joined'][0]['time_stamp']
    assert resp_data['user_stats']['messages_sent'][0]['num_messages_sent'] == 0
    assert resp_data['user_stats']['messages_sent'][0]['time_stamp'] == resp_data['user_stats']['channels_joined'][0]['time_stamp']
    assert resp_data['user_stats']['involvement_rate'] == 0

def test_user_stats_working(reg_two_users):
    #channels create, dm create, message send, message senddm, channel join, auth register, message remove
    resp = requests.post(config.url + "channels/create/v2", json={"token": reg_two_users['token1'], "name": "name", "is_public": True})
    assert resp.status_code == OK
    ch_id1 = resp.json()['channel_id']
    resp = requests.post(config.url + "dm/create/v1", json={"token": reg_two_users['token1'], "u_ids": [reg_two_users['u_id2']]})
    assert resp.status_code == OK
    dm_id1 = resp.json()['dm_id']
    resp = requests.post(config.url + "message/send/v1", json={"token": reg_two_users['token1'], "channel_id": ch_id1, "message": "Hello!"})
    assert resp.status_code == OK
    msg_id1 = resp.json()['message_id']
    resp = requests.post(config.url + "message/senddm/v1", json={"token": reg_two_users['token1'], "dm_id": dm_id1, "message": "Hello!x2"})
    assert resp.status_code == OK
    msg_id2 = resp.json()['message_id']
    resp = requests.get(config.url + "user/stats/v1", params={"token": reg_two_users['token1']})
    assert resp.status_code == OK
    resp_data = resp.json()
    assert resp_data['user_stats']['channels_joined'][1]['num_channels_joined'] == 1
    assert resp_data['user_stats']['dms_joined'][1]['num_dms_joined'] == 1
    assert resp_data['user_stats']['messages_sent'][1]['num_messages_sent'] == 1
    assert resp_data['user_stats']['messages_sent'][2]['num_messages_sent'] == 2
    assert resp_data['user_stats']['involvement_rate'] == 1
    resp = requests.get(config.url + "channel/messages/v2", params={"token": reg_two_users['token1'], "channel_id": ch_id1, "start": 0})
    assert resp.status_code == OK
    assert resp.json()["messages"][0]["time_sent"] == resp_data['user_stats']['messages_sent'][1]['time_stamp']
    resp = requests.get(config.url + "dm/messages/v1", params={"token": reg_two_users['token1'], "dm_id": dm_id1, "start": 0})
    assert resp.status_code == OK
    assert resp.json()["messages"][0]["time_sent"] == resp_data['user_stats']['messages_sent'][2]['time_stamp']
    resp = requests.post(config.url + "channels/create/v2", json={"token": reg_two_users['token2'], "name": "namea", "is_public": True})
    assert resp.status_code == OK
    ch_id2 = resp.json()['channel_id']
    resp = requests.post(config.url + "dm/create/v1", json={"token": reg_two_users['token2'], "u_ids": [reg_two_users['u_id1']]})
    assert resp.status_code == OK
    dm_id2 = resp.json()['dm_id']
    resp = requests.post(config.url + "channel/join/v2", json={"token": reg_two_users['token1'], "channel_id": ch_id2})
    assert resp.status_code == OK
    resp = requests.post(config.url + "message/senddm/v1", json={"token": reg_two_users['token2'], "dm_id": dm_id2, "message": "Hello!x3"})
    assert resp.status_code == OK
    resp = requests.delete(config.url + "message/remove/v1", json={"token": reg_two_users['token1'], "message_id": msg_id1})
    assert resp.status_code == OK
    resp = requests.delete(config.url + "message/remove/v1", json={"token": reg_two_users['token1'], "message_id": msg_id2})
    assert resp.status_code == OK
    resp = requests.get(config.url + "user/stats/v1", params={"token": reg_two_users['token1']})
    assert resp.status_code == OK
    resp_data = resp.json()
    assert resp_data['user_stats']['involvement_rate'] == 1
    resp = requests.get(config.url + "user/stats/v1", params={"token": reg_two_users['token2']})
    assert resp.status_code == OK
    resp_data = resp.json()
    assert resp_data['user_stats']['involvement_rate'] == 0.8

def test_user_stats_working_invite_leave(reg_two_users):
    resp = requests.post(config.url + "channels/create/v2", json={"token": reg_two_users['token1'], "name": "name", "is_public": True})
    assert resp.status_code == OK
    ch_id1 = resp.json()['channel_id']
    resp = requests.post(config.url + "channel/invite/v2", json={"token": reg_two_users['token1'], "channel_id": ch_id1, "u_id": reg_two_users["u_id2"]})
    assert resp.status_code == OK
    resp = requests.get(config.url + "user/stats/v1", params={"token": reg_two_users['token2']})
    assert resp.status_code == OK
    resp_data = resp.json()
    assert resp_data['user_stats']['channels_joined'][1]['num_channels_joined'] == 1
    resp = requests.post(config.url + "channel/leave/v1", json={"token": reg_two_users['token2'], "channel_id": ch_id1})
    assert resp.status_code == OK
    resp = requests.get(config.url + "user/stats/v1", params={"token": reg_two_users['token2']})
    assert resp.status_code == OK
    resp_data = resp.json()
    assert resp_data['user_stats']['channels_joined'][2]['num_channels_joined'] == 0

def test_user_stats_dm_leave_remove(reg_two_users):
    resp = requests.post(config.url + "dm/create/v1", json={"token": reg_two_users['token1'], "u_ids": [reg_two_users['u_id2']]})
    assert resp.status_code == OK
    dm_id1 = resp.json()['dm_id']
    resp = requests.post(config.url + "dm/create/v1", json={"token": reg_two_users['token2'], "u_ids": [reg_two_users['u_id1']]})
    assert resp.status_code == OK
    dm_id2 = resp.json()['dm_id']
    resp = requests.get(config.url + "user/stats/v1", params={"token": reg_two_users['token2']})
    assert resp.status_code == OK
    resp_data = resp.json()
    assert resp_data['user_stats']['dms_joined'][2]['num_dms_joined'] == 2
    resp = requests.delete(config.url + "dm/remove/v1", json={"token": reg_two_users['token1'], "dm_id": dm_id1})
    assert resp.status_code == OK
    resp = requests.post(config.url + "dm/leave/v1", json={"token": reg_two_users['token1'], "dm_id": dm_id2})
    assert resp.status_code == OK
    resp = requests.get(config.url + "user/stats/v1", params={"token": reg_two_users['token1']})
    assert resp.status_code == OK
    resp_data = resp.json()
    assert resp_data['user_stats']['dms_joined'][3]['num_dms_joined'] == 1
    assert resp_data['user_stats']['dms_joined'][4]['num_dms_joined'] == 0

def test_user_stats_message_share(reg_two_users):
    resp = requests.post(config.url + "dm/create/v1", json={"token": reg_two_users['token1'], "u_ids": [reg_two_users['u_id2']]})
    assert resp.status_code == OK
    dm_id1 = resp.json()['dm_id']
    resp = requests.post(config.url + "dm/create/v1", json={"token": reg_two_users['token2'], "u_ids": [reg_two_users['u_id1']]})
    assert resp.status_code == OK
    dm_id2 = resp.json()['dm_id']
    resp = requests.post(config.url + "message/senddm/v1", json={"token": reg_two_users['token2'], "dm_id": dm_id2, "message": "Hello!x3"})
    assert resp.status_code == OK
    msg_id = resp.json()['message_id']
    resp = requests.post(config.url + "message/share/v1", json={"token": reg_two_users['token1'], "og_message_id": msg_id, "message": "", "channel_id": -1, "dm_id": dm_id1})
    assert resp.status_code == OK
    resp = requests.get(config.url + "user/stats/v1", params={"token": reg_two_users['token1']})
    assert resp.status_code == OK
    resp_data = resp.json()
    assert resp_data['user_stats']['messages_sent'][1]['num_messages_sent'] == 1

def test_user_stats_message_send_later(reg_two_users):
    resp = requests.post(config.url + "channels/create/v2", json={"token": reg_two_users['token1'], "name": "name", "is_public": True})
    assert resp.status_code == OK
    ch_id1 = resp.json()['channel_id']
    resp = requests.post(config.url + "dm/create/v1", json={"token": reg_two_users['token1'], "u_ids": [reg_two_users['u_id2']]})
    assert resp.status_code == OK
    dm_id1 = resp.json()['dm_id']
    # Getting the current date
    # and time
    datet = datetime.datetime.now(timezone.utc)
    time = datet.replace(tzinfo=timezone.utc)
    time_sent = time.timestamp()
    resp = requests.post(config.url + "message/sendlater/v1", json={"token": reg_two_users['token1'], "channel_id": ch_id1, "message": "hi", "time_sent": time_sent + 1})
    assert resp.status_code == OK
    resp = requests.post(config.url + "message/sendlaterdm/v1", json={"token": reg_two_users['token1'], "dm_id": dm_id1, "message": "hix2", "time_sent": time_sent + 1})
    assert resp.status_code == OK
    resp = requests.post(config.url + "standup/start/v1", json={"token": reg_two_users['token1'], "channel_id": ch_id1, "length": 1})
    assert resp.status_code == OK
    resp = requests.post(config.url + "standup/send/v1", json={"token": reg_two_users['token1'], "channel_id": ch_id1, "message": "hix3"})
    assert resp.status_code == OK
    resp = requests.get(config.url + "user/stats/v1", params={"token": reg_two_users['token1']})
    assert resp.status_code == OK
    resp_data = resp.json()
    assert len(resp_data['user_stats']['messages_sent']) == 1
    t.sleep(1)
    resp = requests.get(config.url + "user/stats/v1", params={"token": reg_two_users['token1']})
    assert resp.status_code == OK
    resp_data = resp.json()
    assert resp_data['user_stats']['messages_sent'][1]['num_messages_sent'] == 1
    assert resp_data['user_stats']['messages_sent'][2]['num_messages_sent'] == 2
    assert resp_data['user_stats']['messages_sent'][3]['num_messages_sent'] == 3


#tests for users_stats
def test_users_stats_invalid_token():
    clear_resp = requests.delete(config.url + 'clear/v1')
    assert clear_resp.status_code == OK
    resp = requests.get(config.url + "users/stats/v1", params={"token": "invalid"})
    assert resp.status_code == A_ERR

def test_users_stats_initial(reg_two_users):
    resp = requests.get(config.url + "users/stats/v1", params={"token": reg_two_users['token1']})
    assert resp.status_code == OK
    resp_data = resp.json()
    assert resp_data['workspace_stats']['channels_exist'][0]['num_channels_exist'] == 0
    assert resp_data['workspace_stats']['channels_exist'][0]['time_stamp'] != 0
    assert resp_data['workspace_stats']['dms_exist'][0]['num_dms_exist'] == 0
    assert resp_data['workspace_stats']['dms_exist'][0]['time_stamp'] == resp_data['workspace_stats']['channels_exist'][0]['time_stamp']
    assert resp_data['workspace_stats']['messages_exist'][0]['num_messages_exist'] == 0
    assert resp_data['workspace_stats']['messages_exist'][0]['time_stamp'] == resp_data['workspace_stats']['channels_exist'][0]['time_stamp']
    assert resp_data['workspace_stats']['utilization_rate'] == 0
    resp = requests.get(config.url + "users/stats/v1", params={"token": reg_two_users['token2']})
    assert resp.status_code == OK
    resp_data = resp.json()
    assert resp_data['workspace_stats']['channels_exist'][0]['num_channels_exist'] == 0
    assert resp_data['workspace_stats']['channels_exist'][0]['time_stamp'] != 0
    assert resp_data['workspace_stats']['dms_exist'][0]['num_dms_exist'] == 0
    assert resp_data['workspace_stats']['dms_exist'][0]['time_stamp'] == resp_data['workspace_stats']['channels_exist'][0]['time_stamp']
    assert resp_data['workspace_stats']['messages_exist'][0]['num_messages_exist'] == 0
    assert resp_data['workspace_stats']['messages_exist'][0]['time_stamp'] == resp_data['workspace_stats']['channels_exist'][0]['time_stamp']
    assert resp_data['workspace_stats']['utilization_rate'] == 0

def test_users_stats_working(reg_two_users):
    #channels create, dm create, message send, message senddm, channel join, auth register, message remove
    resp = requests.post(config.url + "channels/create/v2", json={"token": reg_two_users['token1'], "name": "name", "is_public": True})
    assert resp.status_code == OK
    ch_id1 = resp.json()['channel_id']
    resp = requests.post(config.url + "dm/create/v1", json={"token": reg_two_users['token1'], "u_ids": [reg_two_users['u_id2']]})
    assert resp.status_code == OK
    dm_id1 = resp.json()['dm_id']
    resp = requests.post(config.url + "message/send/v1", json={"token": reg_two_users['token1'], "channel_id": ch_id1, "message": "Hello!"})
    assert resp.status_code == OK
    msg_id1 = resp.json()['message_id']
    resp = requests.post(config.url + "message/senddm/v1", json={"token": reg_two_users['token1'], "dm_id": dm_id1, "message": "Hello!x2"})
    assert resp.status_code == OK
    msg_id2 = resp.json()['message_id']
    resp = requests.get(config.url + "users/stats/v1", params={"token": reg_two_users['token1']})
    assert resp.status_code == OK
    resp_data = resp.json()
    assert resp_data['workspace_stats']['channels_exist'][1]['num_channels_exist'] == 1
    assert resp_data['workspace_stats']['dms_exist'][1]['num_dms_exist'] == 1
    assert resp_data['workspace_stats']['messages_exist'][1]['num_messages_exist'] == 1
    assert resp_data['workspace_stats']['messages_exist'][2]['num_messages_exist'] == 2
    assert resp_data['workspace_stats']['utilization_rate'] == 1
    resp = requests.get(config.url + "channel/messages/v2", params={"token": reg_two_users['token1'], "channel_id": ch_id1, "start": 0})
    assert resp.status_code == OK
    assert resp.json()["messages"][0]["time_sent"] == resp_data['workspace_stats']['messages_exist'][1]['time_stamp']
    resp = requests.get(config.url + "dm/messages/v1", params={"token": reg_two_users['token1'], "dm_id": dm_id1, "start": 0})
    assert resp.status_code == OK
    assert resp.json()["messages"][0]["time_sent"] == resp_data['workspace_stats']['messages_exist'][2]['time_stamp']
    resp = requests.post(config.url + "channels/create/v2", json={"token": reg_two_users['token2'], "name": "namea", "is_public": True})
    assert resp.status_code == OK
    resp = requests.post(config.url + "dm/create/v1", json={"token": reg_two_users['token2'], "u_ids": [reg_two_users['u_id1']]})
    assert resp.status_code == OK
    dm_id2 = resp.json()['dm_id']
    resp = requests.post(config.url + "message/senddm/v1", json={"token": reg_two_users['token2'], "dm_id": dm_id2, "message": "Hello!x3"})
    assert resp.status_code == OK
    resp = requests.delete(config.url + "message/remove/v1", json={"token": reg_two_users['token1'], "message_id": msg_id1})
    assert resp.status_code == OK
    resp = requests.put(config.url + "message/edit/v1", json={"token": reg_two_users['token1'], "message_id": msg_id2, 'message': ""})
    assert resp.status_code == OK
    resp = requests.get(config.url + "users/stats/v1", params={"token": reg_two_users['token1']})
    assert resp.status_code == OK
    resp_data = resp.json()
    assert resp_data['workspace_stats']['messages_exist'][3]['num_messages_exist'] == 3
    assert resp_data['workspace_stats']['messages_exist'][4]['num_messages_exist'] == 2
    assert resp_data['workspace_stats']['messages_exist'][5]['num_messages_exist'] == 1

def test_users_stats_working_invite_leave_join(reg_two_users):
    resp = requests.post(config.url + "channels/create/v2", json={"token": reg_two_users['token1'], "name": "name", "is_public": True})
    assert resp.status_code == OK
    ch_id1 = resp.json()['channel_id']
    resp = requests.get(config.url + "users/stats/v1", params={"token": reg_two_users['token1']})
    assert resp.status_code == OK
    resp_data = resp.json()
    assert resp_data['workspace_stats']['utilization_rate'] == 0.5
    resp = requests.post(config.url + "channel/invite/v2", json={"token": reg_two_users['token1'], "channel_id": ch_id1, "u_id": reg_two_users["u_id2"]})
    assert resp.status_code == OK
    resp = requests.get(config.url + "users/stats/v1", params={"token": reg_two_users['token2']})
    assert resp.status_code == OK
    resp_data = resp.json()
    assert resp_data['workspace_stats']['utilization_rate'] == 1
    resp = requests.post(config.url + "channel/leave/v1", json={"token": reg_two_users['token2'], "channel_id": ch_id1})
    assert resp.status_code == OK
    resp = requests.get(config.url + "users/stats/v1", params={"token": reg_two_users['token2']})
    assert resp.status_code == OK
    resp_data = resp.json()
    assert resp_data['workspace_stats']['utilization_rate'] == 0.5
    resp = requests.post(config.url + "channel/join/v2", json={"token": reg_two_users['token2'], "channel_id": ch_id1})
    assert resp.status_code == OK
    resp = requests.get(config.url + "users/stats/v1", params={"token": reg_two_users['token2']})
    assert resp.status_code == OK
    resp_data = resp.json()
    assert resp_data['workspace_stats']['utilization_rate'] == 1

def test_users_stats_dm_leave_remove(reg_two_users):
    resp = requests.post(config.url + "dm/create/v1", json={"token": reg_two_users['token1'], "u_ids": [reg_two_users['u_id2']]})
    assert resp.status_code == OK
    dm_id1 = resp.json()['dm_id']
    resp = requests.post(config.url + "dm/create/v1", json={"token": reg_two_users['token2'], "u_ids": [reg_two_users['u_id1']]})
    assert resp.status_code == OK
    dm_id2 = resp.json()['dm_id']
    resp = requests.get(config.url + "users/stats/v1", params={"token": reg_two_users['token2']})
    assert resp.status_code == OK
    resp_data = resp.json()
    assert resp_data['workspace_stats']['utilization_rate'] == 1
    resp = requests.delete(config.url + "dm/remove/v1", json={"token": reg_two_users['token1'], "dm_id": dm_id1})
    assert resp.status_code == OK
    resp = requests.post(config.url + "dm/leave/v1", json={"token": reg_two_users['token1'], "dm_id": dm_id2})
    assert resp.status_code == OK
    resp = requests.get(config.url + "users/stats/v1", params={"token": reg_two_users['token2']})
    assert resp.status_code == OK
    resp_data = resp.json()
    assert resp_data['workspace_stats']['utilization_rate'] == 0.5
    assert resp_data['workspace_stats']['dms_exist'][3]['num_dms_exist'] == 1

def test_users_stats_message_share(reg_two_users):
    resp = requests.post(config.url + "dm/create/v1", json={"token": reg_two_users['token1'], "u_ids": [reg_two_users['u_id2']]})
    assert resp.status_code == OK
    dm_id1 = resp.json()['dm_id']
    resp = requests.post(config.url + "dm/create/v1", json={"token": reg_two_users['token2'], "u_ids": [reg_two_users['u_id1']]})
    assert resp.status_code == OK
    dm_id2 = resp.json()['dm_id']
    resp = requests.post(config.url + "message/senddm/v1", json={"token": reg_two_users['token2'], "dm_id": dm_id2, "message": "Hello!x3"})
    assert resp.status_code == OK
    msg_id = resp.json()['message_id']
    resp = requests.post(config.url + "message/share/v1", json={"token": reg_two_users['token1'], "og_message_id": msg_id, "message": "", "channel_id": -1, "dm_id": dm_id1})
    assert resp.status_code == OK
    resp = requests.get(config.url + "users/stats/v1", params={"token": reg_two_users['token1']})
    assert resp.status_code == OK
    resp_data = resp.json()
    assert resp_data['workspace_stats']['messages_exist'][2]['num_messages_exist'] == 2

def test_users_stats_message_send_later(reg_two_users):
    resp = requests.post(config.url + "channels/create/v2", json={"token": reg_two_users['token1'], "name": "name", "is_public": True})
    assert resp.status_code == OK
    ch_id1 = resp.json()['channel_id']
    resp = requests.post(config.url + "dm/create/v1", json={"token": reg_two_users['token1'], "u_ids": [reg_two_users['u_id2']]})
    assert resp.status_code == OK
    dm_id1 = resp.json()['dm_id']
    # Getting the current date
    # and time
    datet = datetime.datetime.now(timezone.utc)
    time = datet.replace(tzinfo=timezone.utc)
    time_sent = time.timestamp()
    resp = requests.post(config.url + "message/sendlater/v1", json={"token": reg_two_users['token1'], "channel_id": ch_id1, "message": "hi", "time_sent": time_sent + 1})
    assert resp.status_code == OK
    resp = requests.post(config.url + "message/sendlaterdm/v1", json={"token": reg_two_users['token1'], "dm_id": dm_id1, "message": "hix2", "time_sent": time_sent + 1})
    assert resp.status_code == OK
    resp = requests.post(config.url + "standup/start/v1", json={"token": reg_two_users['token1'], "channel_id": ch_id1, "length": 1})
    assert resp.status_code == OK
    resp = requests.post(config.url + "standup/send/v1", json={"token": reg_two_users['token1'], "channel_id": ch_id1, "message": "hix3"})
    assert resp.status_code == OK
    resp = requests.get(config.url + "users/stats/v1", params={"token": reg_two_users['token1']})
    assert resp.status_code == OK
    resp_data = resp.json()
    assert len(resp_data['workspace_stats']['messages_exist']) == 1
    t.sleep(1)
    resp = requests.get(config.url + "users/stats/v1", params={"token": reg_two_users['token1']})
    assert resp.status_code == OK
    resp_data = resp.json()
    assert len(resp_data['workspace_stats']['messages_exist']) == 4
