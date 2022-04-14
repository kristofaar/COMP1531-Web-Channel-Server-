import pytest
import requests
import json
from src import config
from datetime import timezone
import datetime
import time

A_ERR = 403
I_ERR = 400
OK = 200

@pytest.fixture
def reg_two_users_and_create_two_channels():
    clear_resp = requests.delete(config.url + 'clear/v1')
    assert clear_resp.status_code == OK
    resp1 = requests.post(config.url + 'auth/register/v2', json={
                          'email': 'teast@test.test', 'password': 'testtesttest', 'name_first': 'test', 'name_last': 'test'})
    assert resp1.status_code == OK
    resp2 = requests.post(config.url + 'auth/register/v2', json={
                          'email': 'lol@lol.lol', 'password': '123abc123abc', 'name_first': 'Jane', 'name_last': 'Austen'})
    assert resp2.status_code == OK
    resp1_data = resp1.json()
    resp2_data = resp2.json()
    resp3 = requests.post(config.url + 'channels/create/v2', json={
                          'token': resp1_data['token'], 'name': 'CoolChannelName', 'is_public': True})
    assert resp3.status_code == OK
    resp4 = requests.post(config.url + 'channels/create/v2', json={
                          'token': resp2_data['token'], 'name': 'NiceChannel', 'is_public': False})
    assert resp4.status_code == OK
    resp3_data = resp3.json()
    resp4_data = resp4.json()
    return {'token1': resp1_data['token'], 'token2': resp2_data['token'], 'u_id1': resp1_data['auth_user_id'], 'u_id2': resp2_data['auth_user_id'], 'ch_id1': resp3_data['channel_id'], 'ch_id2': resp4_data['channel_id']}

@pytest.fixture
def reg_2_users_2_channels_3s_standup():
    clear_resp = requests.delete(config.url + 'clear/v1')
    assert clear_resp.status_code == OK
    resp1 = requests.post(config.url + 'auth/register/v2', json={
                          'email': 'teast@test.test', 'password': 'testtesttest', 'name_first': 'test', 'name_last': 'test'})
    assert resp1.status_code == OK
    resp2 = requests.post(config.url + 'auth/register/v2', json={
                          'email': 'lol@lol.lol', 'password': '123abc123abc', 'name_first': 'Jane', 'name_last': 'Austen'})
    assert resp2.status_code == OK
    resp1_data = resp1.json()
    resp2_data = resp2.json()
    resp3 = requests.post(config.url + 'channels/create/v2', json={
                          'token': resp1_data['token'], 'name': 'CoolChannelName', 'is_public': True})
    assert resp3.status_code == OK
    resp4 = requests.post(config.url + 'channels/create/v2', json={
                          'token': resp2_data['token'], 'name': 'NiceChannel', 'is_public': False})
    assert resp4.status_code == OK
    resp3_data = resp3.json()
    resp4_data = resp4.json()
    dt = datetime.datetime.now(timezone.utc)
    utc_time = dt.replace(tzinfo=timezone.utc)
    utc_timestamp = int(utc_time.timestamp())
    utc_timestamp += 3
    resp5 = requests.post(config.url + 'standup/start/v1', json={'token': resp1_data['token'], 'channel_id': resp3_data['channel_id'], 'length': 3})
    assert resp5.status_code == OK
    resp5_data = resp5.json()
    return {'token1': resp1_data['token'], 'token2': resp2_data['token'], 'u_id1': resp1_data['auth_user_id'], 'u_id2': resp2_data['auth_user_id'], 'ch_id1': resp3_data['channel_id'], 'ch_id2': resp4_data['channel_id'], 'time_finish': resp5_data['time_finish']}

def test_standup_active(reg_2_users_2_channels_3s_standup):
    resp = requests.get(config.url + 'standup/active/v1', params={'token': reg_2_users_2_channels_3s_standup['token1'], 'channel_id': reg_2_users_2_channels_3s_standup['ch_id1']})
    assert resp.status_code == OK
    resp_data = resp.json()
    assert resp_data['is_active'] == True
    assert resp_data['time_finish'] == reg_2_users_2_channels_3s_standup['time_finish']

def test_standup_one_message(reg_2_users_2_channels_3s_standup):
    resp = requests.post(config.url + 'standup/send/v1', json={'token': reg_2_users_2_channels_3s_standup['token1'], 'channel_id': reg_2_users_2_channels_3s_standup['ch_id1'], 'message': "STANDUP_MESSAGE_1"})
    assert resp.status_code == OK
    time.sleep(3)
    resp2 = requests.get(config.url + 'channel/messages/v2', params={'token': reg_2_users_2_channels_3s_standup['token1'], 'channel_id': reg_2_users_2_channels_3s_standup['ch_id1'], 'start': 0})
    assert resp2.status_code == OK
    resp2_data = resp2.json()
    assert resp2_data['messages'][0]['message'] == "testtest: STANDUP_MESSAGE_1\n"

def test_standup_start_invalid_token(reg_two_users_and_create_two_channels):
    dt = datetime.datetime.now(timezone.utc)
    utc_time = dt.replace(tzinfo=timezone.utc)
    utc_timestamp = int(utc_time.timestamp())
    utc_timestamp += 3
    resp = requests.post(config.url + 'standup/start/v1', json={'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c', 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'length': 3})
    assert resp.status_code == A_ERR

def test_standup_start_invalid_channel(reg_two_users_and_create_two_channels):
    dt = datetime.datetime.now(timezone.utc)
    utc_time = dt.replace(tzinfo=timezone.utc)
    utc_timestamp = int(utc_time.timestamp())
    utc_timestamp += 3
    resp = requests.post(config.url + 'standup/start/v1', json={'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': -1, 'length': 3})
    assert resp.status_code == I_ERR

def test_standup_start_invalid_length(reg_two_users_and_create_two_channels):
    dt = datetime.datetime.now(timezone.utc)
    utc_time = dt.replace(tzinfo=timezone.utc)
    utc_timestamp = int(utc_time.timestamp())
    utc_timestamp += 3
    resp = requests.post(config.url + 'standup/start/v1', json={'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'length': -1})
    assert resp.status_code == I_ERR

def test_standup_start_already_active(reg_2_users_2_channels_3s_standup):
    dt = datetime.datetime.now(timezone.utc)
    utc_time = dt.replace(tzinfo=timezone.utc)
    utc_timestamp = int(utc_time.timestamp())
    utc_timestamp += 3
    resp = requests.post(config.url + 'standup/start/v1', json={'token': reg_2_users_2_channels_3s_standup['token1'], 'channel_id': reg_2_users_2_channels_3s_standup['ch_id1'], 'length': 3})
    assert resp.status_code == I_ERR

def test_standup_start_nonmember(reg_two_users_and_create_two_channels):
    dt = datetime.datetime.now(timezone.utc)
    utc_time = dt.replace(tzinfo=timezone.utc)
    utc_timestamp = int(utc_time.timestamp())
    utc_timestamp += 3
    resp = requests.post(config.url + 'standup/start/v1', json={'token': reg_two_users_and_create_two_channels['token2'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'length': 3})
    assert resp.status_code == A_ERR

def test_standup_active_invalid_token(reg_2_users_2_channels_3s_standup):
    resp = requests.get(config.url + 'standup/active/v1', params={'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c', 'channel_id': reg_2_users_2_channels_3s_standup['ch_id1']})
    assert resp.status_code == A_ERR

def test_standup_active_invalid_channel(reg_2_users_2_channels_3s_standup):
    resp = requests.get(config.url + 'standup/active/v1', params={'token': reg_2_users_2_channels_3s_standup['token1'], 'channel_id': -1})
    assert resp.status_code == I_ERR

def test_standup_send_invalid_token(reg_2_users_2_channels_3s_standup):
    resp = requests.post(config.url + 'standup/send/v1', json={'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c', 'channel_id': reg_2_users_2_channels_3s_standup['ch_id1'], 'message': "STANDUP_MESSAGE_1"})
    assert resp.status_code == A_ERR

def test_standup_send_invalid_channel(reg_2_users_2_channels_3s_standup):
    resp = requests.post(config.url + 'standup/send/v1', json={'token': reg_2_users_2_channels_3s_standup['token1'], 'channel_id': -1, 'message': "STANDUP_MESSAGE_1"})
    assert resp.status_code == I_ERR

def test_standup_send_invalid_message(reg_2_users_2_channels_3s_standup):
    resp = requests.post(config.url + 'standup/send/v1', json={'token': reg_2_users_2_channels_3s_standup['token1'], 'channel_id': reg_2_users_2_channels_3s_standup['ch_id1'], 'message': "a"*1001})
    assert resp.status_code == I_ERR

def test_standup_send_no_standup(reg_two_users_and_create_two_channels):
    resp = requests.post(config.url + 'standup/send/v1', json={'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'message': "STANDUP_MESSAGE_1"})
    assert resp.status_code == I_ERR

def test_standup_send_invalid_non_member(reg_2_users_2_channels_3s_standup):
    resp = requests.post(config.url + 'standup/send/v1', json={'token': reg_2_users_2_channels_3s_standup['token2'], 'channel_id': reg_2_users_2_channels_3s_standup['ch_id1'], 'message': "STANDUP_MESSAGE_1"})
    assert resp.status_code == A_ERR
