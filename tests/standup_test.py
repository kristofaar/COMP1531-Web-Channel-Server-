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

def test_standup_active(reg_two_users_and_create_two_channels):
    dt = datetime.datetime.now(timezone.utc)
    utc_time = dt.replace(tzinfo=timezone.utc)
    utc_timestamp = utc_time.timestamp()
    utc_timestamp += 3
    resp = requests.post(config.url + 'standup/start/v1', json={'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'length': 3})
    assert resp.status_code == OK
    resp2 = requests.get(config.url + 'standup/active/v1', json={'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1']})
    assert resp2.status_code == OK
    resp2_data = resp2.json()
    assert resp2_data['is_active'] == True
    assert round(resp2_data['time_finish']) == round(utc_timestamp)

