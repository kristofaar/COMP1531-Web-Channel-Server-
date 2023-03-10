import pytest
import requests
import json
from src import config
from datetime import timedelta, timezone
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


# send errors
def test_message_send_invalid_token(reg_two_users_and_create_two_channels):
    resp = requests.post(config.url + 'message/send/v1', json={'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c',
                         'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'message': 'hi'})
    assert resp.status_code == A_ERR


def test_message_send_expired_token(reg_two_users_and_create_two_channels):
    resp1 = requests.post(config.url + 'auth/logout/v1',
                          json={'token': reg_two_users_and_create_two_channels['token1']})
    assert resp1.status_code == OK
    resp = requests.post(config.url + 'message/send/v1', json={
                         'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'message': 'hi'})
    assert resp.status_code == A_ERR


def test_message_send_unauthorised(reg_two_users_and_create_two_channels):
    resp = requests.post(config.url + 'message/send/v1', json={
                         'token': reg_two_users_and_create_two_channels['token2'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'message': 'hi'})
    assert resp.status_code == A_ERR


def test_message_send_invalid_channel(reg_two_users_and_create_two_channels):
    resp = requests.post(config.url + 'message/send/v1', json={
                         'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': 123312321345, 'message': 'hi'})
    assert resp.status_code == I_ERR


def test_message_send_bad_length(reg_two_users_and_create_two_channels):
    resp1 = requests.post(config.url + 'message/send/v1', json={
                          'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'message': ''})
    assert resp1.status_code == I_ERR
    msg = 'a'
    for _ in range(1000):
        msg += 'a'
    resp2 = requests.post(config.url + 'message/send/v1', json={
                          'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'message': msg})
    assert resp2.status_code == I_ERR

# send working


def test_one_user_two_messages(reg_two_users_and_create_two_channels):
    resp1 = requests.post(config.url + 'message/send/v1', json={
                          'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'message': 'hi'})
    assert resp1.status_code == OK
    resp1_data = resp1.json()
    resp2 = requests.post(config.url + 'message/send/v1', json={
                          'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'message': 'cool'})
    assert resp2.status_code == OK
    resp2_data = resp2.json()
    resp3 = requests.get(config.url + 'channel/messages/v2', params={
                         'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'start': 0})
    assert resp3.status_code == OK
    resp3_data = resp3.json()
    assert resp3_data['start'] == 0
    assert resp3_data['end'] == -1
    # hi
    assert resp1_data['message_id'] == resp3_data['messages'][1]['message_id']
    # cool
    assert resp2_data['message_id'] == resp3_data['messages'][0]['message_id']
    assert resp3_data['messages'][0]['message_id'] != resp3_data['messages'][1]['message_id']
    assert resp3_data['messages'][0]['u_id'] == reg_two_users_and_create_two_channels['u_id1']
    assert resp3_data['messages'][1]['u_id'] == reg_two_users_and_create_two_channels['u_id1']
    assert resp3_data['messages'][0]['message'] == 'cool'
    assert resp3_data['messages'][1]['message'] == 'hi'
    assert resp3_data['messages'][0]['time_sent'] >= resp3_data['messages'][1]['time_sent']


def test_two_users_one_message(reg_two_users_and_create_two_channels):
    resp1 = requests.post(config.url + 'message/send/v1', json={
                          'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'message': 'hi'})
    assert resp1.status_code == OK
    resp2 = requests.post(config.url + 'message/send/v1', json={
                          'token': reg_two_users_and_create_two_channels['token2'], 'channel_id': reg_two_users_and_create_two_channels['ch_id2'], 'message': 'cool'})
    assert resp2.status_code == OK
    resp3 = requests.get(config.url + 'channel/messages/v2', params={
                         'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'start': 0})
    assert resp3.status_code == OK
    resp3_data = resp3.json()
    resp4 = requests.get(config.url + 'channel/messages/v2', params={
                         'token': reg_two_users_and_create_two_channels['token2'], 'channel_id': reg_two_users_and_create_two_channels['ch_id2'], 'start': 0})
    assert resp4.status_code == OK
    resp4_data = resp4.json()
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

# edit errors


def test_message_edit_invalid_token(reg_two_users_and_create_two_channels):
    resp = requests.put(config.url + 'message/edit/v1', json={
                        'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c', 'message_id': 0, 'message': 'hi'})
    assert resp.status_code == A_ERR


def test_message_edit_expired_token(reg_two_users_and_create_two_channels):
    resp1 = requests.post(config.url + 'auth/logout/v1',
                          json={'token': reg_two_users_and_create_two_channels['token1']})
    assert resp1.status_code == OK
    resp = requests.put(config.url + 'message/edit/v1', json={
                        'token': reg_two_users_and_create_two_channels['token1'], 'message_id': 0, 'message': 'hi'})
    assert resp.status_code == A_ERR


def test_message_edit_unauthorised(reg_two_users_and_create_two_channels):
    resp1 = requests.post(config.url + 'message/send/v1', json={
                          'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'message': 'hi'})
    assert resp1.status_code == OK
    resp1_data = resp1.json()
    resp2 = requests.post(config.url + 'channel/join/v2', json={
                          'token': reg_two_users_and_create_two_channels['token2'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1']})
    assert resp2.status_code == OK
    resp3 = requests.put(config.url + 'message/edit/v1', json={
                         'token': reg_two_users_and_create_two_channels['token2'], 'message_id': resp1_data['message_id'], 'message': 'hi1'})
    assert resp3.status_code == A_ERR


def test_message_edit_invalid_id(reg_two_users_and_create_two_channels):
    resp = requests.put(config.url + 'message/edit/v1', json={
                        'token': reg_two_users_and_create_two_channels['token1'], 'message_id': 123312321345, 'message': 'hi'})
    assert resp.status_code == I_ERR


def test_message_edit_not_in_channel(reg_two_users_and_create_two_channels):
    resp1 = requests.post(config.url + 'message/send/v1', json={
                          'token': reg_two_users_and_create_two_channels['token2'], 'channel_id': reg_two_users_and_create_two_channels['ch_id2'], 'message': 'hi'})
    assert resp1.status_code == OK
    resp1_data = resp1.json()
    resp2 = requests.put(config.url + 'message/edit/v1', json={
                         'token': reg_two_users_and_create_two_channels['token1'], 'message_id': resp1_data['message_id'], 'message': 'hi1'})
    assert resp2.status_code == I_ERR


def test_message_edit_bad_length(reg_two_users_and_create_two_channels):
    resp1 = requests.post(config.url + 'message/send/v1', json={
                          'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'message': 'hi'})
    assert resp1.status_code == OK
    resp1_data = resp1.json()
    msg = 'a'
    for _ in range(1000):
        msg += 'a'
    resp2 = requests.put(config.url + 'message/edit/v1', json={
                         'token': reg_two_users_and_create_two_channels['token1'], 'message_id': resp1_data['message_id'], 'message': msg})
    assert resp2.status_code == I_ERR

# edit working


def test_message_edit_basic(reg_two_users_and_create_two_channels):
    resp1 = requests.post(config.url + 'message/send/v1', json={
                          'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'message': 'hi'})
    assert resp1.status_code == OK
    resp1_data = resp1.json()
    resp2 = requests.put(config.url + 'message/edit/v1', json={
                         'token': reg_two_users_and_create_two_channels['token1'], 'message_id': resp1_data['message_id'], 'message': 'lol'})
    assert resp2.status_code == OK
    resp3 = requests.get(config.url + 'channel/messages/v2', params={
                         'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'start': 0})
    assert resp3.status_code == OK
    resp_data = resp3.json()
    assert resp_data['messages'][0]['message'] == 'lol'


def test_message_edit_owner(reg_two_users_and_create_two_channels):
    resp0 = requests.post(config.url + 'channel/join/v2', json={
                          'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id2']})
    assert resp0.status_code == OK
    resp1 = requests.post(config.url + 'message/send/v1', json={
                          'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id2'], 'message': 'hi'})
    assert resp1.status_code == OK
    resp1_data = resp1.json()
    resp2 = requests.put(config.url + 'message/edit/v1', json={
                         'token': reg_two_users_and_create_two_channels['token2'], 'message_id': resp1_data['message_id'], 'message': 'lol'})
    assert resp2.status_code == OK
    resp3 = requests.get(config.url + 'channel/messages/v2', params={
                         'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id2'], 'start': 0})
    assert resp3.status_code == OK
    resp_data = resp3.json()
    assert resp_data['messages'][0]['message'] == 'lol'


def test_message_edit_global_owner(reg_two_users_and_create_two_channels):
    resp0 = requests.post(config.url + 'channel/join/v2', json={
                          'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id2']})
    assert resp0.status_code == OK
    resp1 = requests.post(config.url + 'message/send/v1', json={
                          'token': reg_two_users_and_create_two_channels['token2'], 'channel_id': reg_two_users_and_create_two_channels['ch_id2'], 'message': 'hi'})
    assert resp1.status_code == OK
    resp1_data = resp1.json()
    resp2 = requests.put(config.url + 'message/edit/v1', json={
                         'token': reg_two_users_and_create_two_channels['token1'], 'message_id': resp1_data['message_id'], 'message': 'lol'})
    assert resp2.status_code == OK
    resp3 = requests.get(config.url + 'channel/messages/v2', params={
                         'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id2'], 'start': 0})
    assert resp3.status_code == OK
    resp_data = resp3.json()
    assert resp_data['messages'][0]['message'] == 'lol'

# remove errors


def test_message_remove_invalid_token(reg_two_users_and_create_two_channels):
    resp = requests.delete(config.url + 'message/remove/v1', json={
                           'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c', 'message_id': 0})
    assert resp.status_code == A_ERR


def test_message_remove_expired_token(reg_two_users_and_create_two_channels):
    resp1 = requests.post(config.url + 'auth/logout/v1',
                          json={'token': reg_two_users_and_create_two_channels['token1']})
    assert resp1.status_code == OK
    resp = requests.delete(config.url + 'message/remove/v1', json={
                           'token': reg_two_users_and_create_two_channels['token1'], 'message_id': 0})
    assert resp.status_code == A_ERR


def test_message_remove_unauthorised(reg_two_users_and_create_two_channels):
    resp1 = requests.post(config.url + 'message/send/v1', json={
                          'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'message': 'hello'})
    assert resp1.status_code == OK
    resp1_data = resp1.json()
    resp2 = requests.post(config.url + 'channel/join/v2', json={
                          'token': reg_two_users_and_create_two_channels['token2'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1']})
    assert resp2.status_code == OK
    resp3 = requests.delete(config.url + 'message/remove/v1', json={
                            'token': reg_two_users_and_create_two_channels['token2'], 'message_id': resp1_data['message_id']})
    assert resp3.status_code == A_ERR


def test_message_remove_not_in_channel(reg_two_users_and_create_two_channels):
    resp1 = requests.post(config.url + 'message/send/v1', json={
                          'token': reg_two_users_and_create_two_channels['token2'], 'channel_id': reg_two_users_and_create_two_channels['ch_id2'], 'message': 'hi'})
    assert resp1.status_code == OK
    resp1_data = resp1.json()
    resp2 = requests.delete(config.url + 'message/remove/v1', json={
                            'token': reg_two_users_and_create_two_channels['token1'], 'message_id': resp1_data['message_id']})
    assert resp2.status_code == I_ERR


def test_message_remove_invalid_id(reg_two_users_and_create_two_channels):
    resp = requests.delete(config.url + 'message/remove/v1', json={
                           'token': reg_two_users_and_create_two_channels['token1'], 'message_id': 123312321345})
    assert resp.status_code == I_ERR


# remove working
def test_message_remove_basic(reg_two_users_and_create_two_channels):
    resp1 = requests.post(config.url + 'message/send/v1', json={
                          'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'message': 'hi'})
    assert resp1.status_code == OK
    resp1_data = resp1.json()
    resp2 = requests.delete(config.url + 'message/remove/v1', json={
                            'token': reg_two_users_and_create_two_channels['token1'], 'message_id': resp1_data['message_id']})
    assert resp2.status_code == OK
    resp3 = requests.get(config.url + 'channel/messages/v2', params={
                         'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'start': 0})
    assert resp3.status_code == OK
    resp_data = resp3.json()
    assert len(resp_data['messages']) == 0


def test_message_remove_owner(reg_two_users_and_create_two_channels):
    resp0 = requests.post(config.url + 'channel/join/v2', json={
                          'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id2']})
    assert resp0.status_code == OK
    resp1 = requests.post(config.url + 'message/send/v1', json={
                          'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id2'], 'message': 'hi'})
    assert resp1.status_code == OK
    resp1_data = resp1.json()
    resp2 = requests.delete(config.url + 'message/remove/v1', json={
                            'token': reg_two_users_and_create_two_channels['token2'], 'message_id': resp1_data['message_id']})
    assert resp2.status_code == OK
    resp3 = requests.get(config.url + 'channel/messages/v2', params={
                         'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id2'], 'start': 0})
    assert resp3.status_code == OK
    resp_data = resp3.json()
    assert len(resp_data['messages']) == 0


def test_message_remove_global_owner(reg_two_users_and_create_two_channels):
    resp0 = requests.post(config.url + 'channel/join/v2', json={
                          'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id2']})
    assert resp0.status_code == OK
    resp1 = requests.post(config.url + 'message/send/v1', json={
                          'token': reg_two_users_and_create_two_channels['token2'], 'channel_id': reg_two_users_and_create_two_channels['ch_id2'], 'message': 'hi'})
    assert resp1.status_code == OK
    resp1_data = resp1.json()
    resp2 = requests.delete(config.url + 'message/remove/v1', json={
                            'token': reg_two_users_and_create_two_channels['token1'], 'message_id': resp1_data['message_id']})
    assert resp2.status_code == OK
    resp3 = requests.get(config.url + 'channel/messages/v2', params={
                         'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id2'], 'start': 0})
    assert resp3.status_code == OK
    resp_data = resp3.json()
    assert len(resp_data['messages']) == 0

# dms


@pytest.fixture
def reg_two_users_and_create_dm():
    clear_resp = requests.delete(config.url + 'clear/v1')
    assert clear_resp.status_code == OK
    requests.post(config.url + 'auth/register/v2', json={
                  'email': '1@test.test', 'password': '1testtest', 'name_first': 'first_test', 'name_last': 'first_test'})
    resp1 = requests.post(config.url + 'auth/login/v2',
                          json={'email': '1@test.test', 'password': '1testtest'})
    assert resp1.status_code == OK
    resp2 = requests.post(config.url + 'auth/register/v2', json={
                          'email': '2@lol.lol', 'password': '2abcabc', 'name_first': 'Second_Jane', 'name_last': 'Second_Austen'})
    assert resp2.status_code == OK
    resp1_data = resp1.json()
    resp2_data = resp2.json()
    resp3 = requests.post(config.url + 'dm/create/v1', json={
                          'token': resp1_data['token'], 'u_ids': [resp2_data['auth_user_id']]})
    assert resp3.status_code == OK
    resp3_data = resp3.json()
    return {'token1': resp1_data['token'], 'token2': resp2_data['token'],
            'u_id1': resp1_data['auth_user_id'], 'u_id2': resp2_data['auth_user_id'],
            'dm_id': resp3_data['dm_id']}


@pytest.fixture
def reg_another_two_users_and_dm():
    reg1 = requests.post(config.url + 'auth/register/v2', json={
                         'email': '3@test.test', 'password': '3testtest', 'name_first': 'third_name', 'name_last': 'third_last_name'})
    assert reg1.status_code == OK
    reg2 = requests.post(config.url + 'auth/register/v2', json={
                         'email': '4@lol.lol', 'password': '4abcabc', 'name_first': 'Fourth_boi', 'name_last': 'Fourth_last'})
    assert reg2.status_code == OK
    reg1_data = reg1.json()
    reg2_data = reg2.json()
    dmcreate = requests.post(config.url + 'dm/create/v1', json={
                             'token': reg1_data['token'], 'u_ids': [reg2_data['auth_user_id']]})
    assert dmcreate.status_code == OK
    dmcreate_data = dmcreate.json()
    dmdet = requests.get(config.url + 'dm/details/v1',
                         params={'token': reg1_data['token'], 'dm_id': dmcreate_data['dm_id']})
    dmdet_data = dmdet.json()
    return {'token1': reg1_data['token'], 'token2': reg2_data['token'],
            'u_id1': reg1_data['auth_user_id'], 'u_id2': reg2_data['auth_user_id'],
            'dm_id': dmcreate_data['dm_id'], 'dm_name': dmdet_data['name']}


# send errors
def test_message_senddm_invalid_token(reg_two_users_and_create_dm):
    resp = requests.post(config.url + 'message/senddm/v1', json={
                         'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c', 'dm_id': reg_two_users_and_create_dm['dm_id'], 'message': 'hi'})
    assert resp.status_code == A_ERR


def test_message_senddm_expired_token(reg_two_users_and_create_dm):
    resp1 = requests.post(config.url + 'auth/logout/v1',
                          json={'token': reg_two_users_and_create_dm['token1']})
    assert resp1.status_code == OK
    resp = requests.post(config.url + 'message/senddm/v1', json={
                         'token': reg_two_users_and_create_dm['token1'], 'dm_id': reg_two_users_and_create_dm['dm_id'], 'message': 'hi'})
    assert resp.status_code == A_ERR


def test_message_senddm_unauthorised(reg_two_users_and_create_dm, reg_another_two_users_and_dm):
    resp = requests.post(config.url + 'message/senddm/v1', json={
                         'token': reg_two_users_and_create_dm['token2'], 'dm_id': reg_another_two_users_and_dm['dm_id'], 'message': 'hi'})
    assert resp.status_code == A_ERR


def test_message_senddm_invalid_channel(reg_two_users_and_create_dm):
    resp = requests.post(config.url + 'message/senddm/v1', json={
                         'token': reg_two_users_and_create_dm['token1'], 'dm_id': 123312321345, 'message': 'hi'})
    assert resp.status_code == I_ERR


def test_message_senddm_bad_length(reg_two_users_and_create_dm):
    resp1 = requests.post(config.url + 'message/senddm/v1', json={
                          'token': reg_two_users_and_create_dm['token1'], 'dm_id': reg_two_users_and_create_dm['dm_id'], 'message': ''})
    assert resp1.status_code == I_ERR
    msg = 'a'
    for _ in range(1000):
        msg += 'a'
    resp2 = requests.post(config.url + 'message/senddm/v1', json={
                          'token': reg_two_users_and_create_dm['token1'], 'dm_id': reg_two_users_and_create_dm['dm_id'], 'message': msg})
    assert resp2.status_code == I_ERR


# sendlater errors


def test_sendlater_invalid_token(reg_two_users_and_create_two_channels):
    datet = datetime.datetime.now(timezone.utc)
    datet += timedelta(seconds=5)
    time = datet.replace(tzinfo=timezone.utc)
    time_later = time.timestamp()
    resp = requests.post(config.url + 'message/sendlater/v1', json={'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c',
                         'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'message': 'hi', 'time_sent': time_later})
    assert resp.status_code == A_ERR


def test_sendlater_expired_token(reg_two_users_and_create_two_channels):
    resp1 = requests.post(config.url + 'auth/logout/v1',
                          json={'token': reg_two_users_and_create_two_channels['token1']})
    assert resp1.status_code == OK
    datet = datetime.datetime.now(timezone.utc)
    datet += timedelta(seconds=5)
    time = datet.replace(tzinfo=timezone.utc)
    time_later = time.timestamp()
    resp = requests.post(config.url + 'message/sendlater/v1', json={
                         'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'message': 'hi', 'time_sent': time_later})
    assert resp.status_code == A_ERR


def test_sendlater_unauthorised(reg_two_users_and_create_two_channels):
    datet = datetime.datetime.now(timezone.utc)
    datet += timedelta(seconds=5)
    time = datet.replace(tzinfo=timezone.utc)
    time_later = time.timestamp()
    resp = requests.post(config.url + 'message/sendlater/v1', json={
                         'token': reg_two_users_and_create_two_channels['token2'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'message': 'hi', 'time_sent': time_later})
    assert resp.status_code == A_ERR


def test_sendlater_msg_length(reg_two_users_and_create_two_channels):
    datet = datetime.datetime.now(timezone.utc)
    datet += timedelta(seconds=5)
    time = datet.replace(tzinfo=timezone.utc)
    time_later = time.timestamp()

    resp1 = requests.post(config.url + 'message/sendlater/v1', json={
                          'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'message': '', 'time_sent': time_later})
    assert resp1.status_code == I_ERR
    msg = 'a'
    for _ in range(1000):
        msg += 'a'
    resp2 = requests.post(config.url + 'message/sendlater/v1', json={
                          'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'message': msg, 'time_sent': time_later})
    assert resp2.status_code == I_ERR


def test_sendlater_invalid_channel(reg_two_users_and_create_two_channels):
    datet = datetime.datetime.now(timezone.utc)
    datet += timedelta(seconds=5)
    time = datet.replace(tzinfo=timezone.utc)
    time_later = time.timestamp()

    resp = requests.post(config.url + 'message/sendlater/v1', json={
                         'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': 123423, 'message': 'hi', 'time_sent': time_later})
    assert resp.status_code == I_ERR


def test_sendlater_timepast(reg_two_users_and_create_two_channels):
    datet = datetime.datetime.now(timezone.utc)
    datet -= timedelta(seconds=5)
    time1 = datet.replace(tzinfo=timezone.utc)
    time_before = time1.timestamp()

    resp = requests.post(config.url + 'message/sendlater/v1', json={
                         'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'message': 'hi', 'time_sent': time_before})
    assert resp.status_code == I_ERR

# test sendlater working


def test_sendlater_timefuture(reg_two_users_and_create_two_channels):
    time_future = int(time.time() + 2)

    resp = requests.post(config.url + 'message/sendlater/v1', json={
                         'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'message': 'hi', 'time_sent': time_future})
    assert resp.status_code == OK
    message_id = resp.json()['message_id']

    resp = requests.get(config.url + 'channel/messages/v2', params={
                        'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'start': 0})
    assert resp.status_code == OK
    messages = resp.json()['messages']
    assert messages == []

    time.sleep(2)
    resp = requests.get(config.url + 'channel/messages/v2', params={
                        'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'start': 0})
    assert resp.status_code == OK
    messages = resp.json()['messages']
    assert messages[0]['message_id'] == message_id


def test_sendlater_multiple(reg_two_users_and_create_two_channels):
    time_before = int(time.time() + 2)

    resp = requests.post(config.url + 'message/sendlater/v1', json={
                         'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'message': 'hi', 'time_sent': time_before})
    assert resp.status_code == OK
    message_id1 = resp.json()['message_id']

    time_before = int(time.time() + 1)
    resp = requests.post(config.url + 'message/sendlater/v1', json={
                         'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'message': 'hi', 'time_sent': time_before})
    assert resp.status_code == OK
    message_id2 = resp.json()['message_id']

    resp = requests.get(config.url + 'channel/messages/v2', params={
                        'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'start': 0})
    assert resp.status_code == OK
    messages = resp.json()['messages']
    assert messages == []

    time.sleep(1)
    resp = requests.get(config.url + 'channel/messages/v2', params={
                        'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'start': 0})
    assert resp.status_code == OK
    messages = resp.json()['messages']
    assert messages[0]['message_id'] == message_id2

    time.sleep(1)
    resp = requests.get(config.url + 'channel/messages/v2', params={
                        'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'start': 0})
    assert resp.status_code == OK
    messages = resp.json()['messages']
    assert messages[0]['message_id'] == message_id1
    assert messages[1]['message_id'] == message_id2


def test_sendlater_edit(reg_two_users_and_create_two_channels):
    time_before = int(time.time() + 1)

    resp = requests.post(config.url + 'message/sendlater/v1', json={
                         'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'message': 'hi', 'time_sent': time_before})
    assert resp.status_code == OK
    message_id1 = resp.json()['message_id']

    resp3 = requests.put(config.url + 'message/edit/v1', json={
                         'token': reg_two_users_and_create_two_channels['token1'], 'message_id': message_id1, 'message': 'hi1'})
    assert resp3.status_code == I_ERR

    time.sleep(2)
    resp3 = requests.put(config.url + 'message/edit/v1', json={
                         'token': reg_two_users_and_create_two_channels['token1'], 'message_id': message_id1, 'message': 'hii'})
    assert resp3.status_code == OK
    resp = requests.get(config.url + 'channel/messages/v2', params={
                        'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'start': 0})
    assert resp.status_code == OK
    messages = resp.json()['messages']
    assert messages[0]['message'] == 'hii'


def test_sendlater_delete(reg_two_users_and_create_two_channels):
    time_before = int(time.time() + 1)

    resp = requests.post(config.url + 'message/sendlater/v1', json={
                         'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'message': 'hi', 'time_sent': time_before})
    assert resp.status_code == OK
    message_id1 = resp.json()['message_id']
    resp3 = requests.put(config.url + 'message/edit/v1', json={
                         'token': reg_two_users_and_create_two_channels['token1'], 'message_id': message_id1, 'message': ''})
    assert resp3.status_code == I_ERR

    time.sleep(2)
    resp3 = requests.put(config.url + 'message/edit/v1', json={
                         'token': reg_two_users_and_create_two_channels['token1'], 'message_id': message_id1, 'message': ''})
    assert resp3.status_code == OK
    resp = requests.get(config.url + 'channel/messages/v2', params={
                        'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'start': 0})
    assert resp.status_code == OK
    messages = resp.json()['messages']
    assert messages == []

    # add request for message/react, should return I_ERR
    pass


"""
def test_sendlater_react(reg_two_users_and_create_two_channels):
    time_before = int(time.time() + 1)

    resp = requests.post(config.url + 'message/sendlater/v1', json={
                         'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'message': 'hi', 'time_sent': time_before})
    assert resp.status_code == OK
    message_id1 = resp.json()['message_id']
    # msg react request error

    time.sleep(2)
    # msg react request OK
    resp = requests.get(config.url + 'channel/messages/v2', params={
                        'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'start': 0})
    assert resp.status_code == OK
    messages = resp.json()['messages']
    # assert messages[0]['reacts']['react_id'] ==
"""

# sendlaterdm errors


def test_sendlaterdm_invalid_token(reg_two_users_and_create_dm):
    time_before = int(time.time() + 1)
    resp = requests.post(config.url + 'message/sendlaterdm/v1', json={'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c',
                         'dm_id': reg_two_users_and_create_dm['dm_id'], 'message': 'hi', 'time_sent': time_before})
    assert resp.status_code == A_ERR


def test_sendlaterdm_expired_token(reg_two_users_and_create_dm):
    resp1 = requests.post(config.url + 'auth/logout/v1',
                          json={'token': reg_two_users_and_create_dm['token1']})
    assert resp1.status_code == OK
    time_later = int(time.time() + 1)
    resp = requests.post(config.url + 'message/sendlaterdm/v1', json={
                         'token': reg_two_users_and_create_dm['token1'], 'dm_id': reg_two_users_and_create_dm['dm_id'], 'message': 'hi', 'time_sent': time_later})
    assert resp.status_code == A_ERR


def test_sendlaterdm_unauthorised(reg_two_users_and_create_dm, reg_another_two_users_and_dm):
    time_later = int(time.time() + 1)
    resp = requests.post(config.url + 'message/sendlaterdm/v1', json={
                         'token': reg_another_two_users_and_dm['token1'], 'dm_id': reg_two_users_and_create_dm['dm_id'], 'message': 'hi', 'time_sent': time_later})
    assert resp.status_code == A_ERR


def test_sendlaterdm_msg_length(reg_two_users_and_create_dm):
    time_later = int(time.time() + 1)
    time.sleep(2)
    msg = 'a'
    for _ in range(1000):
        msg += 'a'
    resp2 = requests.post(config.url + 'message/sendlaterdm/v1', json={
                          'token': reg_two_users_and_create_dm['token1'], 'dm_id': reg_two_users_and_create_dm['dm_id'], 'message': msg, 'time_sent': time_later})
    assert resp2.status_code == I_ERR


def test_sendlaterdm_invalid_channel(reg_two_users_and_create_dm):
    time_later = int(time.time() + 1)
    time.sleep(2)
    resp = requests.post(config.url + 'message/sendlaterdm/v1', json={
                         'token': reg_two_users_and_create_dm['token1'], 'dm_id': 123423, 'message': 'hi', 'time_sent': time_later})
    assert resp.status_code == I_ERR


def test_sendlaterdm_timepast(reg_two_users_and_create_dm):
    time_later = int(time.time() - 1)
    time.sleep(1)

    resp = requests.post(config.url + 'message/sendlaterdm/v1', json={
                         'token': reg_two_users_and_create_dm['token1'], 'dm_id': reg_two_users_and_create_dm['dm_id'], 'message': 'hi', 'time_sent': time_later})
    assert resp.status_code == I_ERR

# test sendlaterdm working


def test_sendlaterdm_timefuture(reg_two_users_and_create_dm):
    time_later = int(time.time() + 2)
    resp = requests.post(config.url + 'message/sendlaterdm/v1', json={
                         'token': reg_two_users_and_create_dm['token1'], 'dm_id': reg_two_users_and_create_dm['dm_id'], 'message': 'hi', 'time_sent': time_later})
    assert resp.status_code == OK
    message_id = resp.json()['message_id']
    time.sleep(1)
    resp = requests.get(config.url + 'dm/messages/v1', params={
        'token': reg_two_users_and_create_dm['token1'], 'dm_id': reg_two_users_and_create_dm['dm_id'], 'start': 0})
    assert resp.status_code == OK
    messages = resp.json()['messages']
    assert messages == []

    time.sleep(1)
    resp = requests.get(config.url + 'dm/messages/v1', params={
        'token': reg_two_users_and_create_dm['token1'], 'dm_id': reg_two_users_and_create_dm['dm_id'], 'start': 0})
    assert resp.status_code == OK
    messages = resp.json()['messages']
    assert messages[0]['message_id'] == message_id


def test_sendlaterdm_multiple(reg_two_users_and_create_dm):
    time_before = int(time.time() + 2)

    resp = requests.post(config.url + 'message/sendlaterdm/v1', json={
                         'token': reg_two_users_and_create_dm['token1'], 'dm_id': reg_two_users_and_create_dm['dm_id'], 'message': 'hi', 'time_sent': time_before})
    assert resp.status_code == OK
    message_id1 = resp.json()['message_id']

    time_before = int(time.time() + 1)

    resp = requests.post(config.url + 'message/sendlaterdm/v1', json={
                         'token': reg_two_users_and_create_dm['token2'], 'dm_id': reg_two_users_and_create_dm['dm_id'], 'message': 'hie', 'time_sent': time_before})
    assert resp.status_code == OK
    message_id2 = resp.json()['message_id']

    resp = requests.get(config.url + 'dm/messages/v1', params={
                        'token': reg_two_users_and_create_dm['token1'], 'dm_id': reg_two_users_and_create_dm['dm_id'], 'start': 0})
    assert resp.status_code == OK
    messages = resp.json()['messages']
    assert messages == []

    time.sleep(1)
    resp = requests.get(config.url + 'dm/messages/v1', params={
                        'token': reg_two_users_and_create_dm['token1'], 'dm_id': reg_two_users_and_create_dm['dm_id'], 'start': 0})
    assert resp.status_code == OK
    messages = resp.json()['messages']
    assert messages[0]['message_id'] == message_id2

    time.sleep(1)
    resp = requests.get(config.url + 'dm/messages/v1', params={
                        'token': reg_two_users_and_create_dm['token1'], 'dm_id': reg_two_users_and_create_dm['dm_id'], 'start': 0})
    assert resp.status_code == OK
    messages = resp.json()['messages']
    assert messages[0]['message_id'] == message_id1
    assert messages[1]['message_id'] == message_id2


def test_sendlaterdm_edit(reg_two_users_and_create_dm):
    time_before = int(time.time() + 1)

    resp = requests.post(config.url + 'message/sendlaterdm/v1', json={
                         'token': reg_two_users_and_create_dm['token1'], 'dm_id': reg_two_users_and_create_dm['dm_id'], 'message': 'hi', 'time_sent': time_before})
    assert resp.status_code == OK
    message_id1 = resp.json()['message_id']

    resp3 = requests.put(config.url + 'message/edit/v1', json={
                         'token': reg_two_users_and_create_dm['token1'], 'message_id': message_id1, 'message': 'hii'})
    assert resp3.status_code == I_ERR
    time.sleep(1)
    resp3 = requests.put(config.url + 'message/edit/v1', json={
                         'token': reg_two_users_and_create_dm['token1'], 'message_id': message_id1, 'message': 'hii'})
    assert resp3.status_code == OK
    resp = requests.get(config.url + 'dm/messages/v1', params={
                        'token': reg_two_users_and_create_dm['token1'], 'dm_id': reg_two_users_and_create_dm['dm_id'], 'start': 0})
    assert resp.status_code == OK
    messages = resp.json()['messages']
    assert messages[0]['message'] == 'hii'


def test_sendlaterdm_delete(reg_two_users_and_create_dm):
    time_before = int(time.time() + 1)

    resp = requests.post(config.url + 'message/sendlaterdm/v1', json={
                         'token': reg_two_users_and_create_dm['token1'], 'dm_id': reg_two_users_and_create_dm['dm_id'], 'message': 'hi', 'time_sent': time_before})
    assert resp.status_code == OK
    message_id1 = resp.json()['message_id']

    resp3 = requests.put(config.url + 'message/edit/v1', json={
                         'token': reg_two_users_and_create_dm['token1'], 'message_id': message_id1, 'message': ''})
    assert resp3.status_code == I_ERR
    time.sleep(1)
    resp3 = requests.put(config.url + 'message/edit/v1', json={
                         'token': reg_two_users_and_create_dm['token1'], 'message_id': message_id1, 'message': ''})
    assert resp3.status_code == OK
    resp = requests.get(config.url + 'dm/messages/v1', params={
                        'token': reg_two_users_and_create_dm['token1'], 'dm_id': reg_two_users_and_create_dm['dm_id'], 'start': 0})
    assert resp.status_code == OK
    messages = resp.json()['messages']
    assert messages == []


"""
def test_sendlaterdm_react(reg_two_users_and_create_dm):
    time_before = int(time.time() + 1)

    resp = requests.post(config.url + 'message/sendlaterdm/v1', json={
                         'token': reg_two_users_and_create_dm['token1'], 'dm_id': reg_two_users_and_create_dm['dm_id'], 'message': 'hi', 'time_sent': time_before})
    assert resp.status_code == OK
    message_id1 = resp.json()['message_id']
    # msg react request error

    time.sleep(2)
    # msg react request OK
    resp = requests.get(config.url + 'dm/messages/v1', params={
                        'token': reg_two_users_and_create_dm['token1'], 'dm_id': reg_two_users_and_create_dm['dm_id'], 'start': 0})
    assert resp.status_code == OK
    messages = resp.json()['messages']
    # assert messages[0]['reacts']['react_id'] ==
"""

# message share errors


def test_messageshare_invalid_token(reg_two_users_and_create_dm):
    resp1 = requests.post(config.url + 'message/senddm/v1', json={
                          'token': reg_two_users_and_create_dm['token1'], 'dm_id': reg_two_users_and_create_dm['dm_id'], 'message': 'hi'})
    assert resp1.status_code == OK
    og_message_id = resp1.json()['message_id']
    resp = requests.post(config.url + 'message/share/v1', json={'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c',
                                                                'og_message_id': og_message_id, 'message': 'buddy', 'channel_id': -1, 'dm_id': reg_two_users_and_create_dm['dm_id']})
    assert resp.status_code == A_ERR


def test_messageshare_expired_token_dm(reg_two_users_and_create_dm):
    resp1 = requests.post(config.url + 'message/senddm/v1', json={
                          'token': reg_two_users_and_create_dm['token1'], 'dm_id': reg_two_users_and_create_dm['dm_id'], 'message': 'hi'})
    assert resp1.status_code == OK
    og_message_id = resp1.json()['message_id']
    resp1 = requests.post(config.url + 'auth/logout/v1',
                          json={'token': reg_two_users_and_create_dm['token1']})
    assert resp1.status_code == OK
    resp = requests.post(config.url + 'message/share/v1', json={'token': reg_two_users_and_create_dm['token1'],
                                                                'og_message_id': og_message_id, 'message': 'buddy', 'channel_id': -1, 'dm_id': reg_two_users_and_create_dm['dm_id']})
    assert resp.status_code == A_ERR


def test_messageshare_unauthorised_dm(reg_two_users_and_create_dm, reg_another_two_users_and_dm):
    resp1 = requests.post(config.url + 'message/senddm/v1', json={
                          'token': reg_two_users_and_create_dm['token1'], 'dm_id': reg_two_users_and_create_dm['dm_id'], 'message': 'hi'})
    assert resp1.status_code == OK
    og_message_id = resp1.json()['message_id']
    resp = requests.post(config.url + 'message/share/v1', json={'token': reg_another_two_users_and_dm['token1'],
                                                                'og_message_id': og_message_id, 'message': 'buddy', 'channel_id': -1, 'dm_id': reg_two_users_and_create_dm['dm_id']})
    assert resp.status_code == A_ERR


def test_messageshare_unauthorised_channel(reg_two_users_and_create_two_channels):
    resp1 = requests.post(config.url + 'message/send/v1', json={
                          'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'message': 'hi'})
    assert resp1.status_code == OK
    og_message_id = resp1.json()['message_id']
    resp = requests.post(config.url + 'message/share/v1', json={'token': reg_two_users_and_create_two_channels['token2'],
                                                                'og_message_id': og_message_id, 'message': 'buddy', 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'dm_id': -1})
    assert resp.status_code == A_ERR


def test_messageshare_msg_length_dm(reg_two_users_and_create_dm):
    resp1 = requests.post(config.url + 'message/senddm/v1', json={
                          'token': reg_two_users_and_create_dm['token1'], 'dm_id': reg_two_users_and_create_dm['dm_id'], 'message': 'hi'})
    assert resp1.status_code == OK
    og_message_id = resp1.json()['message_id']
    msg = 'a'
    for _ in range(1000):
        msg += 'a'
    resp = requests.post(config.url + 'message/share/v1', json={'token': reg_two_users_and_create_dm['token1'],
                                                                'og_message_id': og_message_id, 'message': msg, 'channel_id': -1, 'dm_id': reg_two_users_and_create_dm['dm_id']})
    assert resp.status_code == I_ERR


def test_messageshare_invalid_dm(reg_two_users_and_create_dm):
    resp1 = requests.post(config.url + 'message/senddm/v1', json={
                          'token': reg_two_users_and_create_dm['token1'], 'dm_id': reg_two_users_and_create_dm['dm_id'], 'message': 'hi'})
    assert resp1.status_code == OK
    og_message_id = resp1.json()['message_id']
    resp = requests.post(config.url + 'message/share/v1', json={'token': reg_two_users_and_create_dm['token1'],
                                                                'og_message_id': og_message_id, 'message': 'buddy', 'channel_id': -1, 'dm_id': 123423})
    assert resp.status_code == I_ERR


def test_messageshare_both_negative_one(reg_two_users_and_create_dm):
    resp1 = requests.post(config.url + 'message/senddm/v1', json={
                          'token': reg_two_users_and_create_dm['token1'], 'dm_id': reg_two_users_and_create_dm['dm_id'], 'message': 'hi'})
    assert resp1.status_code == OK
    og_message_id = resp1.json()['message_id']
    resp = requests.post(config.url + 'message/share/v1', json={'token': reg_two_users_and_create_dm['token1'],
                                                                'og_message_id': og_message_id, 'message': 'buddy', 'channel_id': -1, 'dm_id': -1})
    assert resp.status_code == I_ERR


def test_messageshare_neither_negative_one(reg_two_users_and_create_dm):
    resp1 = requests.post(config.url + 'message/senddm/v1', json={
                          'token': reg_two_users_and_create_dm['token1'], 'dm_id': reg_two_users_and_create_dm['dm_id'], 'message': 'hi'})
    assert resp1.status_code == OK
    og_message_id = resp1.json()['message_id']
    resp = requests.post(config.url + 'message/share/v1', json={'token': reg_two_users_and_create_dm['token1'],
                                                                'og_message_id': og_message_id, 'message': 'buddy', 'channel_id': -3, 'dm_id': -4})
    assert resp.status_code == I_ERR


def test_messageshare_invalid_msg_id(reg_two_users_and_create_dm):
    resp = requests.post(config.url + 'message/share/v1', json={'token': reg_two_users_and_create_dm['token1'],
                                                                'og_message_id': 4293095, 'message': 'buddy', 'channel_id': -1, 'dm_id': reg_two_users_and_create_dm['dm_id']})
    assert resp.status_code == I_ERR


def test_messageshare_invalid_channel(reg_two_users_and_create_dm):
    resp1 = requests.post(config.url + 'message/senddm/v1', json={
                          'token': reg_two_users_and_create_dm['token1'], 'dm_id': reg_two_users_and_create_dm['dm_id'], 'message': 'hi'})
    assert resp1.status_code == OK
    og_message_id = resp1.json()['message_id']
    resp = requests.post(config.url + 'message/share/v1', json={'token': reg_two_users_and_create_dm['token1'],
                                                                'og_message_id': og_message_id, 'message': 'buddy', 'channel_id': 4293095, 'dm_id': -1})
    assert resp.status_code == I_ERR

# message share working


def test_messageshare_working_channel(reg_two_users_and_create_two_channels):
    resp3 = requests.post(config.url + 'channels/create/v2', json={
                          'token': reg_two_users_and_create_two_channels['token1'], 'name': 'Newone', 'is_public': True})
    assert resp3.status_code == OK
    channel_id = resp3.json()['channel_id']
    resp1 = requests.post(config.url + 'message/send/v1', json={
                          'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': channel_id, 'message': 'hi'})
    assert resp1.status_code == OK
    og_message_id = resp1.json()['message_id']
    resp = requests.post(config.url + 'message/share/v1', json={'token': reg_two_users_and_create_two_channels['token1'],
                                                                'og_message_id': og_message_id, 'message': 'buddy', 'channel_id': channel_id, 'dm_id': -1})
    assert resp.status_code == OK
    shared_message_id = resp.json()['shared_message_id']
    resp3 = requests.get(config.url + 'channel/messages/v2', params={
                         'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': channel_id, 'start': 0})
    assert resp3.status_code == OK
    messages = resp3.json()['messages']
    assert messages[0]['message'] == 'hibuddy'
    assert messages[0]['message_id'] == shared_message_id


def test_messageshare_working_channel_empty(reg_two_users_and_create_two_channels):
    resp1 = requests.post(config.url + 'message/send/v1', json={
                          'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'message': 'hi'})
    assert resp1.status_code == OK
    og_message_id = resp1.json()['message_id']
    resp = requests.post(config.url + 'message/share/v1', json={'token': reg_two_users_and_create_two_channels['token1'],
                                                                'og_message_id': og_message_id, 'message': '', 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'dm_id': -1})
    assert resp.status_code == OK
    shared_message_id = resp.json()['shared_message_id']
    resp3 = requests.get(config.url + 'channel/messages/v2', params={
                         'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'start': 0})
    assert resp3.status_code == OK
    messages = resp3.json()['messages']
    assert messages[0]['message'] == 'hi'
    assert messages[0]['message_id'] == shared_message_id


def test_messageshare_working_dm(reg_two_users_and_create_dm, reg_another_two_users_and_dm):
    resp3 = requests.post(config.url + 'dm/create/v1', json={
                          'token': reg_two_users_and_create_dm['token1'], 'u_ids': [reg_another_two_users_and_dm['u_id2']]})
    assert resp3.status_code == OK
    dm_id = resp3.json()['dm_id']
    resp1 = requests.post(config.url + 'message/senddm/v1', json={
                          'token': reg_two_users_and_create_dm['token1'], 'dm_id': dm_id, 'message': 'hi'})
    assert resp1.status_code == OK
    og_message_id = resp1.json()['message_id']
    resp = requests.post(config.url + 'message/share/v1', json={'token': reg_two_users_and_create_dm['token1'],
                                                                'og_message_id': og_message_id, 'message': 'buddy', 'channel_id': -1, 'dm_id': dm_id})
    assert resp.status_code == OK
    shared_message_id = resp.json()['shared_message_id']
    resp3 = requests.get(config.url + 'dm/messages/v1', params={
                         'token': reg_two_users_and_create_dm['token1'], 'dm_id': dm_id, 'start': 0})
    assert resp3.status_code == OK
    messages = resp3.json()['messages']
    assert messages[0]['message'] == 'hibuddy'
    assert messages[0]['message_id'] == shared_message_id


# send working
def test_one_user_two_dms(reg_two_users_and_create_dm, ):
    resp1 = requests.post(config.url + 'message/senddm/v1', json={
                          'token': reg_two_users_and_create_dm['token1'], 'dm_id': reg_two_users_and_create_dm['dm_id'], 'message': 'hi'})
    assert resp1.status_code == OK
    resp1_data = resp1.json()
    resp2 = requests.post(config.url + 'message/senddm/v1', json={
                          'token': reg_two_users_and_create_dm['token1'], 'dm_id': reg_two_users_and_create_dm['dm_id'], 'message': 'cool'})
    assert resp2.status_code == OK
    resp2_data = resp2.json()
    resp3 = requests.get(config.url + 'dm/messages/v1', params={
                         'token': reg_two_users_and_create_dm['token1'], 'dm_id': reg_two_users_and_create_dm['dm_id'], 'start': 0})
    assert resp3.status_code == OK
    resp3_data = resp3.json()
    assert resp3_data['start'] == 0
    assert resp3_data['end'] == -1
    # hi
    assert resp1_data['message_id'] == resp3_data['messages'][1]['message_id']
    # cool
    assert resp2_data['message_id'] == resp3_data['messages'][0]['message_id']
    assert resp3_data['messages'][0]['message_id'] != resp3_data['messages'][1]['message_id']
    assert resp3_data['messages'][0]['u_id'] == reg_two_users_and_create_dm['u_id1']
    assert resp3_data['messages'][1]['u_id'] == reg_two_users_and_create_dm['u_id1']
    assert resp3_data['messages'][0]['message'] == 'cool'
    assert resp3_data['messages'][1]['message'] == 'hi'
    assert resp3_data['messages'][0]['time_sent'] >= resp3_data['messages'][1]['time_sent']


def test_two_users_one_dm(reg_two_users_and_create_dm):
    resp1 = requests.post(config.url + 'message/senddm/v1', json={
                          'token': reg_two_users_and_create_dm['token1'], 'dm_id': reg_two_users_and_create_dm['dm_id'], 'message': 'hi'})
    assert resp1.status_code == OK
    resp2 = requests.post(config.url + 'message/senddm/v1', json={
                          'token': reg_two_users_and_create_dm['token2'], 'dm_id': reg_two_users_and_create_dm['dm_id'], 'message': 'cool'})
    assert resp2.status_code == OK
    resp3 = requests.get(config.url + 'dm/messages/v1', params={
                         'token': reg_two_users_and_create_dm['token1'], 'dm_id': reg_two_users_and_create_dm['dm_id'], 'start': 0})
    assert resp3.status_code == OK
    resp3_data = resp3.json()
    resp4 = requests.get(config.url + 'dm/messages/v1', params={
                         'token': reg_two_users_and_create_dm['token2'], 'dm_id': reg_two_users_and_create_dm['dm_id'], 'start': 0})
    assert resp4.status_code == OK
    assert resp3_data['start'] == 0
    assert resp3_data['end'] == -1
    assert resp3_data['messages'][0]['message_id'] != resp3_data['messages'][1]['message_id']
    assert resp3_data['messages'][0]['u_id'] == reg_two_users_and_create_dm['u_id2']
    assert resp3_data['messages'][1]['u_id'] == reg_two_users_and_create_dm['u_id1']
    assert resp3_data['messages'][0]['message'] == 'cool'
    assert resp3_data['messages'][1]['message'] == 'hi'
    assert resp3_data['messages'][0]['time_sent'] >= resp3_data['messages'][1]['time_sent']

# edit and remove for dms errors


def test_message_edit_dm_invalid_id(reg_two_users_and_create_dm):
    resp = requests.put(config.url + 'message/edit/v1', json={
                        'token': reg_two_users_and_create_dm['token1'], 'message_id': 123312321345, 'message': 'hi'})
    assert resp.status_code == I_ERR


def test_message_remove_dm_invalid_id(reg_two_users_and_create_dm):
    resp = requests.delete(config.url + 'message/remove/v1', json={
                           'token': reg_two_users_and_create_dm['token1'], 'message_id': 123312321345})
    assert resp.status_code == I_ERR

# edit and remove for dms working


def test_one_user_two_dms_edit(reg_two_users_and_create_dm, reg_another_two_users_and_dm):
    resp1 = requests.post(config.url + 'message/senddm/v1', json={
                          'token': reg_two_users_and_create_dm['token1'], 'dm_id': reg_two_users_and_create_dm['dm_id'], 'message': 'hi'})
    assert resp1.status_code == OK
    resp1_data = resp1.json()
    resp2 = requests.post(config.url + 'message/senddm/v1', json={
                          'token': reg_two_users_and_create_dm['token2'], 'dm_id': reg_two_users_and_create_dm['dm_id'], 'message': 'cool'})
    assert resp2.status_code == OK
    resp2_data = resp2.json()
    resp2 = requests.put(config.url + 'message/edit/v1', json={
                         'token': reg_two_users_and_create_dm['token1'], 'message_id': resp2_data['message_id'], 'message': 'lol'})
    assert resp2.status_code == OK
    resp2 = requests.put(config.url + 'message/edit/v1', json={
                         'token': reg_two_users_and_create_dm['token2'], 'message_id': resp1_data['message_id'], 'message': 'xxx'})
    assert resp2.status_code == A_ERR
    resp2 = requests.put(config.url + 'message/edit/v1', json={
                         'token': reg_two_users_and_create_dm['token1'], 'message_id': resp1_data['message_id'], 'message': 'x'})
    assert resp2.status_code == OK
    resp3 = requests.get(config.url + 'dm/messages/v1', params={
                         'token': reg_two_users_and_create_dm['token1'], 'dm_id': reg_two_users_and_create_dm['dm_id'], 'start': 0})
    assert resp3.status_code == OK
    resp3_data = resp3.json()
    assert resp3_data['start'] == 0
    assert resp3_data['end'] == -1
    assert resp3_data['messages'][0]['message'] == 'lol'
    assert resp3_data['messages'][1]['message'] == 'x'
    resp2 = requests.put(config.url + 'message/edit/v1', json={
                         'token': reg_two_users_and_create_dm['token2'], 'message_id': resp2_data['message_id'], 'message': 'aaa'})
    assert resp2.status_code == OK
    resp3 = requests.get(config.url + 'dm/messages/v1', params={
                         'token': reg_two_users_and_create_dm['token1'], 'dm_id': reg_two_users_and_create_dm['dm_id'], 'start': 0})
    assert resp3.status_code == OK
    resp3_data = resp3.json()
    assert resp3_data['start'] == 0
    assert resp3_data['end'] == -1
    assert resp3_data['messages'][0]['message'] == 'aaa'
    assert resp3_data['messages'][1]['message'] == 'x'
    resp2 = requests.put(config.url + 'message/edit/v1', json={
                         'token': reg_two_users_and_create_dm['token2'], 'message_id': resp2_data['message_id'], 'message': ''})
    assert resp2.status_code == OK
    resp3 = requests.get(config.url + 'dm/messages/v1', params={
                         'token': reg_two_users_and_create_dm['token1'], 'dm_id': reg_two_users_and_create_dm['dm_id'], 'start': 0})
    assert resp3.status_code == OK
    resp3_data = resp3.json()
    assert resp3_data['start'] == 0
    assert resp3_data['end'] == -1
    assert resp3_data['messages'][0]['message'] == 'x'


def test_one_user_two_dms_remove(reg_two_users_and_create_dm, reg_another_two_users_and_dm):
    resp1 = requests.post(config.url + 'message/senddm/v1', json={
                          'token': reg_two_users_and_create_dm['token1'], 'dm_id': reg_two_users_and_create_dm['dm_id'], 'message': 'hi'})
    assert resp1.status_code == OK
    resp1_data = resp1.json()
    resp2 = requests.post(config.url + 'message/senddm/v1', json={
                          'token': reg_two_users_and_create_dm['token2'], 'dm_id': reg_two_users_and_create_dm['dm_id'], 'message': 'cool'})
    assert resp2.status_code == OK
    resp2_data = resp2.json()
    resp2 = requests.delete(config.url + 'message/remove/v1', json={
                            'token': reg_two_users_and_create_dm['token1'], 'message_id': resp2_data['message_id']})
    assert resp2.status_code == OK
    resp2 = requests.delete(config.url + 'message/remove/v1', json={
                            'token': reg_two_users_and_create_dm['token2'], 'message_id': resp1_data['message_id']})
    assert resp2.status_code == A_ERR
    resp2 = requests.delete(config.url + 'message/remove/v1', json={
                            'token': reg_two_users_and_create_dm['token1'], 'message_id': resp1_data['message_id']})
    assert resp2.status_code == OK
    resp3 = requests.get(config.url + 'dm/messages/v1', params={
                         'token': reg_two_users_and_create_dm['token1'], 'dm_id': reg_two_users_and_create_dm['dm_id'], 'start': 0})
    assert resp3.status_code == OK
    resp3_data = resp3.json()
    assert resp3_data['messages'] == []
    resp2 = requests.post(config.url + 'message/senddm/v1', json={
                          'token': reg_two_users_and_create_dm['token2'], 'dm_id': reg_two_users_and_create_dm['dm_id'], 'message': 'cool'})
    assert resp2.status_code == OK
    resp2_data = resp2.json()
    resp2 = requests.delete(config.url + 'message/remove/v1', json={
                            'token': reg_two_users_and_create_dm['token2'], 'message_id': resp2_data['message_id']})
    assert resp2.status_code == OK
    resp3 = requests.get(config.url + 'dm/messages/v1', params={
                         'token': reg_two_users_and_create_dm['token1'], 'dm_id': reg_two_users_and_create_dm['dm_id'], 'start': 0})
    assert resp3.status_code == OK
    resp3_data = resp3.json()
    assert resp3_data['messages'] == []

#React/Unreact errors
def test_react_invalid_token(reg_two_users_and_create_two_channels):
    message1 = requests.post(config.url + 'message/send/v1', json={'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'message': 'hi'})
    assert message1.status_code == OK
    message1_data = message1.json()

    react = requests.post(config.url + 'message/react/v1', json={'token':'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c',
                                                                  'message_id': message1_data['message_id'], 'react_id': 1})
    assert react.status_code == A_ERR

def test_react_invalid_message(reg_two_users_and_create_two_channels):
    message1 = requests.post(config.url + 'message/send/v1', json={'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'message': 'hi'})
    assert message1.status_code == OK
    
    react = requests.post(config.url + 'message/react/v1', json={'token': reg_two_users_and_create_two_channels['token1'], 'message_id': 993129, 'react_id': 1})
    assert react.status_code == I_ERR

def test_react_invalid_react(reg_two_users_and_create_two_channels):
    message1 = requests.post(config.url + 'message/send/v1', json={'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'message': 'hi'})
    assert message1.status_code == OK
    message1_data = message1.json()

    react = requests.post(config.url + 'message/react/v1', json={'token': reg_two_users_and_create_two_channels['token1'], 'message_id': message1_data['message_id'], 'react_id': -9123})
    assert react.status_code == I_ERR

def test_duplicate_react(reg_two_users_and_create_two_channels):    
    message1 = requests.post(config.url + 'message/send/v1', json={'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'message': 'hi'})
    assert message1.status_code == OK
    message1_data = message1.json()

    react = requests.post(config.url + 'message/react/v1', json={'token': reg_two_users_and_create_two_channels['token1'], 'message_id': message1_data['message_id'], 'react_id': 1})
    assert react.status_code == OK

    react = requests.post(config.url + 'message/react/v1', json={'token': reg_two_users_and_create_two_channels['token1'], 'message_id': message1_data['message_id'], 'react_id': 1})
    assert react.status_code == I_ERR

def test_unreact_invalid_token(reg_two_users_and_create_two_channels):
    message1 = requests.post(config.url + 'message/send/v1', json={'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'message': 'hi'})
    assert message1.status_code == OK
    message1_data = message1.json()

    react = requests.post(config.url + 'message/unreact/v1', json={'token':'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c',
                                                                  'message_id': message1_data['message_id'], 'react_id': 1})
    assert react.status_code == A_ERR

def test_unreact_invalid_message(reg_two_users_and_create_two_channels):
    message1 = requests.post(config.url + 'message/send/v1', json={'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'message': 'hi'})
    assert message1.status_code == OK

    unreact = requests.post(config.url + 'message/unreact/v1', json={'token': reg_two_users_and_create_two_channels['token1'], 'message_id': 993129, 'react_id': 1})
    assert unreact.status_code == I_ERR

def test_unreact_invalid_react(reg_two_users_and_create_two_channels):
    message1 = requests.post(config.url + 'message/send/v1', json={'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'message': 'hi'})
    assert message1.status_code == OK
    message1_data = message1.json()

    unreact = requests.post(config.url + 'message/unreact/v1', json={'token': reg_two_users_and_create_two_channels['token1'], 'message_id': message1_data['message_id'], 'react_id': -9123})
    assert unreact.status_code == I_ERR

def test_unreact_no_react_on_message(reg_two_users_and_create_two_channels):
    message1 = requests.post(config.url + 'message/send/v1', json={'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'message': 'hi'})
    assert message1.status_code == OK
    message1_data = message1.json()

    unreact = requests.post(config.url + 'message/unreact/v1', json={'token': reg_two_users_and_create_two_channels['token1'], 'message_id': message1_data['message_id'], 'react_id': 1})
    assert unreact.status_code == I_ERR

#React/Unreact Tests Working
def test_react_message_channel(reg_two_users_and_create_two_channels):
    message1 = requests.post(config.url + 'message/send/v1', json={'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'message': 'hi'})
    assert message1.status_code == OK
    message1_data = message1.json()

    react = requests.post(config.url + 'message/react/v1', json={'token': reg_two_users_and_create_two_channels['token1'], 'message_id': message1_data['message_id'], 'react_id': 1})
    assert react.status_code == OK

def test_react_message_dm(reg_two_users_and_create_dm):
    message = requests.post(config.url + 'message/senddm/v1', json={
                          'token': reg_two_users_and_create_dm['token1'], 'dm_id': reg_two_users_and_create_dm['dm_id'], 'message': 'hi'})
    assert message.status_code == OK
    message1_data = message.json()

    react = requests.post(config.url + 'message/react/v1', json={'token': reg_two_users_and_create_dm['token1'], 'message_id': message1_data['message_id'], 'react_id': 1})
    assert react.status_code == OK

def test_unreact_message_channel(reg_two_users_and_create_two_channels):
    message1 = requests.post(config.url + 'message/send/v1', json={'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'message': 'hi'})
    assert message1.status_code == OK
    message1_data = message1.json()

    react = requests.post(config.url + 'message/react/v1', json={'token': reg_two_users_and_create_two_channels['token1'], 'message_id': message1_data['message_id'], 'react_id': 1})
    assert react.status_code == OK

    unreact = requests.post(config.url + 'message/unreact/v1', json={'token': reg_two_users_and_create_two_channels['token1'], 'message_id': message1_data['message_id'], 'react_id': 1})
    assert unreact.status_code == OK

def test_unreact_message_dm(reg_two_users_and_create_dm):
    message = requests.post(config.url + 'message/senddm/v1', json={
                          'token': reg_two_users_and_create_dm['token1'], 'dm_id': reg_two_users_and_create_dm['dm_id'], 'message': 'hi'})
    assert message.status_code == OK
    message1_data = message.json()

    react = requests.post(config.url + 'message/react/v1', json={'token': reg_two_users_and_create_dm['token1'], 'message_id': message1_data['message_id'], 'react_id': 1})
    assert react.status_code == OK

    unreact = requests.post(config.url + 'message/unreact/v1', json={'token': reg_two_users_and_create_dm['token1'], 'message_id': message1_data['message_id'], 'react_id': 1})
    assert unreact.status_code == OK

#Pin/Unpin errors
def test_pin_invalid_token(reg_two_users_and_create_two_channels):
    message1 = requests.post(config.url + 'message/send/v1', json={'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'message': 'hi'})
    assert message1.status_code == OK
    message1_data = message1.json()

    react = requests.post(config.url + 'message/pin/v1', json={'token':'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c',
                                                                  'message_id': message1_data['message_id']})
    assert react.status_code == A_ERR

def test_pin_invalid_message(reg_two_users_and_create_two_channels):
    message1 = requests.post(config.url + 'message/send/v1', json={'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'message': 'hi'})
    assert message1.status_code == OK

    pin = requests.post(config.url + 'message/pin/v1', json={'token': reg_two_users_and_create_two_channels['token1'], 'message_id': 993129})
    assert pin.status_code == I_ERR

def test_double_pin(reg_two_users_and_create_two_channels):
    message1 = requests.post(config.url + 'message/send/v1', json={'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'message': 'hi'})
    assert message1.status_code == OK
    message1_data = message1.json()

    pin = requests.post(config.url + 'message/pin/v1', json={'token': reg_two_users_and_create_two_channels['token1'], 'message_id': message1_data["message_id"]})
    assert pin.status_code == OK

    pin1 = requests.post(config.url + 'message/pin/v1', json={'token': reg_two_users_and_create_two_channels['token1'], 'message_id': message1_data["message_id"]})
    assert pin1.status_code == I_ERR

def test_pin_no_permissions_channel(reg_two_users_and_create_two_channels):
    message1 = requests.post(config.url + 'message/send/v1', json={'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'message': 'hi'})
    assert message1.status_code == OK
    message1_data = message1.json()

    join = requests.post(config.url + 'channel/join/v2', json={
                          'token': reg_two_users_and_create_two_channels['token2'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1']})
    assert join.status_code == OK

    pin = requests.post(config.url + 'message/pin/v1', json={'token': reg_two_users_and_create_two_channels['token2'], 'message_id': message1_data["message_id"]})
    assert pin.status_code == A_ERR

def test_pin_no_permissions_dm(reg_two_users_and_create_dm):
    message = requests.post(config.url + 'message/senddm/v1', json={
                          'token': reg_two_users_and_create_dm['token1'], 'dm_id': reg_two_users_and_create_dm['dm_id'], 'message': 'hi'})
    assert message.status_code == OK
    message1_data = message.json()

    pin = requests.post(config.url + 'message/pin/v1', json={'token': reg_two_users_and_create_dm['token2'], 'message_id': message1_data['message_id'], 'react_id': 1})
    assert pin.status_code == A_ERR

def test_unpin_invalid_token(reg_two_users_and_create_two_channels):
    message1 = requests.post(config.url + 'message/send/v1', json={'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'message': 'hi'})
    assert message1.status_code == OK
    message1_data = message1.json()
    
    react = requests.post(config.url + 'message/unpin/v1', json={'token':'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c',
                                                                  'message_id': message1_data['message_id']})
    assert react.status_code == A_ERR

def test_unpin_invalid_message_channel(reg_two_users_and_create_two_channels):
    message1 = requests.post(config.url + 'message/send/v1', json={'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'message': 'hi'})
    assert message1.status_code == OK

    pin = requests.post(config.url + 'message/unpin/v1', json={'token': reg_two_users_and_create_two_channels['token1'], 'message_id': 993129})
    assert pin.status_code == I_ERR

def test_unpin_not_pinned_message_channel(reg_two_users_and_create_two_channels):
    message1 = requests.post(config.url + 'message/send/v1', json={'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'message': 'hi'})
    assert message1.status_code == OK
    message1_data = message1.json()

    pin = requests.post(config.url + 'message/unpin/v1', json={'token': reg_two_users_and_create_two_channels['token1'], 'message_id': message1_data["message_id"]})
    assert pin.status_code == I_ERR

def test_unpin_no_permissions_channel(reg_two_users_and_create_two_channels):
    message1 = requests.post(config.url + 'message/send/v1', json={'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'message': 'hi'})
    assert message1.status_code == OK
    message1_data = message1.json()

    join = requests.post(config.url + 'channel/join/v2', json={
                          'token': reg_two_users_and_create_two_channels['token2'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1']})
    assert join.status_code == OK

    pin = requests.post(config.url + 'message/unpin/v1', json={'token': reg_two_users_and_create_two_channels['token2'], 'message_id': message1_data["message_id"]})
    assert pin.status_code == A_ERR

def test_unpin_no_permissions_dm(reg_two_users_and_create_dm):
    message = requests.post(config.url + 'message/senddm/v1', json={
                          'token': reg_two_users_and_create_dm['token1'], 'dm_id': reg_two_users_and_create_dm['dm_id'], 'message': 'hi'})
    assert message.status_code == OK
    message1_data = message.json()

    pin = requests.post(config.url + 'message/pin/v1', json={'token': reg_two_users_and_create_dm['token1'], 'message_id': message1_data['message_id'], 'react_id': 1})
    assert pin.status_code == OK

    unpin = requests.post(config.url + 'message/unpin/v1', json={'token': reg_two_users_and_create_dm['token2'], 'message_id': message1_data['message_id'], 'react_id': 1})
    assert unpin.status_code == A_ERR

#Pin/Unpin Tests Working
def test_pin_message_channel(reg_two_users_and_create_two_channels):
    message1 = requests.post(config.url + 'message/send/v1', json={'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'message': 'hi'})
    assert message1.status_code == OK
    message1_data = message1.json()
    

    pin = requests.post(config.url + 'message/pin/v1', json={'token': reg_two_users_and_create_two_channels['token1'], 'message_id': message1_data['message_id']})
    assert pin.status_code == OK

def test_pin_message_dm(reg_two_users_and_create_dm):
    message = requests.post(config.url + 'message/senddm/v1', json={
                          'token': reg_two_users_and_create_dm['token1'], 'dm_id': reg_two_users_and_create_dm['dm_id'], 'message': 'hi'})
    assert message.status_code == OK
    message1_data = message.json()

    pin = requests.post(config.url + 'message/pin/v1', json={'token': reg_two_users_and_create_dm['token1'], 'message_id': message1_data['message_id'], 'react_id': 1})
    assert pin.status_code == OK

def test_unpin_message_channel(reg_two_users_and_create_two_channels):
    message1 = requests.post(config.url + 'message/send/v1', json={'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id1'], 'message': 'hi'})
    assert message1.status_code == OK
    message1_data = message1.json()
    

    pin = requests.post(config.url + 'message/pin/v1', json={'token': reg_two_users_and_create_two_channels['token1'], 'message_id': message1_data['message_id']})
    assert pin.status_code == OK

    unpin = requests.post(config.url + 'message/unpin/v1', json={'token': reg_two_users_and_create_two_channels['token1'], 'message_id': message1_data['message_id']})
    assert unpin.status_code == OK

def test_unpin_message_dm(reg_two_users_and_create_dm):
    message = requests.post(config.url + 'message/senddm/v1', json={
                          'token': reg_two_users_and_create_dm['token1'], 'dm_id': reg_two_users_and_create_dm['dm_id'], 'message': 'hi'})
    assert message.status_code == OK
    message1_data = message.json()

    pin = requests.post(config.url + 'message/pin/v1', json={'token': reg_two_users_and_create_dm['token1'], 'message_id': message1_data['message_id'], 'react_id': 1})
    assert pin.status_code == OK

    unpin = requests.post(config.url + 'message/unpin/v1', json={'token': reg_two_users_and_create_dm['token1'], 'message_id': message1_data['message_id'], 'react_id': 1})
    assert unpin.status_code == OK