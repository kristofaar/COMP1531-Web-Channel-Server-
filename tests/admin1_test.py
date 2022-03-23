from email import message
import pytest
import requests
import json
from src import config

A_ERR = 403
I_ERR = 400
OK = 200


@pytest.fixture
# first user (global) makes first channel, second user makes second channel
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

# test admin_user_remove_v1 errors


def test_admin_user_remove_v1_invalid_token(reg_two_users_and_create_two_channels):
    resp = requests.delete(config.url + 'admin/user/remove/v1', json={
                           'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c', 'u_id': reg_two_users_and_create_two_channels['u_id2']})
    resp.status_code = A_ERR


def test_admin_user_remove_v1_expired_token(reg_two_users_and_create_two_channels):
    resp = requests.get(config.url + 'auth/logout/v1',
                        json={'token': reg_two_users_and_create_two_channels['token1']})
    resp.status_code = OK
    resp1 = requests.delete(config.url + 'admin/user/remove/v1', json={
        'token': reg_two_users_and_create_two_channels['token1'], 'u_id': reg_two_users_and_create_two_channels['u_id2']})
    resp1.status_code = A_ERR


def test_admin_user_remove_v1_invalid_uid(reg_two_users_and_create_two_channels):
    resp = requests.delete(config.url + 'admin/user/remove/v1', json={
                           'token': reg_two_users_and_create_two_channels['token1'], 'u_id': -1})
    resp.status_code = I_ERR


def test_admin_user_remove_v1_uid_only_global_user(reg_two_users_and_create_two_channels):
    resp = requests.delete(config.url + 'admin/user/remove/v1', json={
                           'token': reg_two_users_and_create_two_channels['token1'], 'u_id': reg_two_users_and_create_two_channels['u_id1']})
    resp.status_code = I_ERR


def test_admin_user_remove_v1_user_not_global(reg_two_users_and_create_two_channels):
    resp = requests.delete(config.url + 'admin/user/remove/v1', json={
                           'token': reg_two_users_and_create_two_channels['token2'], 'u_id': reg_two_users_and_create_two_channels['u_id2']})
    resp.status_code = A_ERR

# test admin_user_remove_v1 working


def test_admin_user_remove_v1_first_remove_second_check_users_list(reg_two_users_and_create_two_channels):
    resp = requests.delete(config.url + 'admin/user/remove/v1', json={
                           'token': reg_two_users_and_create_two_channels['token1'], 'u_id': reg_two_users_and_create_two_channels['u_id2']})
    resp.status_code = OK

    # check 2nd user doesn't exist in users
    token1 = reg_two_users_and_create_two_channels['token1']
    resp = requests.get(config.url + f'users/all/v1?token={token1}')
    resp.status_code = OK

    all_users = resp.json()
    for user in all_users['users']:
        assert reg_two_users_and_create_two_channels['u_id2'] != user['u_id']


def test_admin_user_remove_v1_first_remove_second_check_channels(reg_two_users_and_create_two_channels):
    resp = requests.delete(config.url + 'admin/user/remove/v1', json={
                           'token': reg_two_users_and_create_two_channels['token1'], 'u_id': reg_two_users_and_create_two_channels['u_id2']})
    resp.status_code = OK

    # 2nd user sends a message in 2nd channel
    resp1 = requests.post(config.url + 'message/send/v1', json={
                          'token': reg_two_users_and_create_two_channels['token2'], 'channel_id': reg_two_users_and_create_two_channels['channel_id2'], 'message': 'a random msg'})
    resp1.status_code = OK
    message_id = resp1['message_id']

    # check 2nd user doesn't exist in 2nd channel members list
    token1 = reg_two_users_and_create_two_channels['token1']
    ch_id2 = reg_two_users_and_create_two_channels['ch_id2']
    resp1 = requests.get(config.url + 'channel/details/v2' +
                         f'?token={token1}&channel_id={ch_id2}')
    resp1.status_code = OK

    ch2_details = resp1.json()
    assert reg_two_users_and_create_two_channels['u_id2'] not in ch2_details[
        'all_members'] and reg_two_users_and_create_two_channels['u_id2'] not in ch2_details['owner']

    # check 2nd user's channel messages in 2nd channel is replaced by 'Removed user'
    # first user (global) joins second channel so msgs can be seen
    resp2 = requests.post(config.url + 'channel/join/v2', json={
                          'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id2']})
    resp2.status_code = OK

    # check msg in second channel
    resp3 = requests.get(config.url + 'channel/messages/v2', params={
                         'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id2'], 'start': 0})
    resp3.status_code = OK
    channel_msgs = resp3.json()['messages']
    assert channel_msgs[0]['message'] == 'Removed user'

    '''
    # loop though msgs 
    start_ind = end_ind = 0
    while end_ind != -1:
        resp3 = requests.get(config.url + 'channel/messages/v2', params={'token': reg_two_users_and_create_two_channels['token1'], 'channel_id': reg_two_users_and_create_two_channels['ch_id2'], 'start': {start_ind}})
        resp3.status_code = OK
        end_ind = resp3.json()['end']
        channel_msgs = resp3.json()['messages']
        for msg in channel_msgs:
            if msg['u_id'] == reg_two_users_and_create_two_channels['u_id2']:
               assert msg['message'] is 'Removed user'
    '''

# still working on it


def test_admin_user_remove_v1_first_remove_second_check_dm(reg_two_users_and_create_two_channels):
    # second user makes dm msg to first user
    resp = requests.post(config.url + 'dm/create/v1', json={
                         'token': reg_two_users_and_create_two_channels['token2'], 'u_ids': [reg_two_users_and_create_two_channels['u_id1']]})
    resp.status_code = OK
    dm_id = resp['dm_id']

    resp = requests.post(config.url + 'message/senddm/v1', params={
                         'token': reg_two_users_and_create_two_channels['token2'], 'dm_id': dm_id, 'message': 'What a joke this is'})
    resp.status_code = OK

    # delete second user
    resp1 = requests.delete(config.url + 'admin/user/remove/v1', json={
        'token': reg_two_users_and_create_two_channels['token1'], 'u_id': reg_two_users_and_create_two_channels['u_id2']})
    resp1.status_code = OK

    # first user check dm messages by second user are 'Removed users'
    resp2 = requests.get(config.url + 'dm/list/v1',
                         params={'token': reg_two_users_and_create_two_channels['token1']})
    resp2.status_code = OK
    dms_list = resp2.json()['dms']
    dm_id = dms_list['dm_id']

    resp3 = requests.get(config.url + 'dm/messages/v1', params={
                         'token': reg_two_users_and_create_two_channels['token1'], 'dm_id': dm_id, 'start': 0})
    msg_list = resp3.json()['messages']
    assert msg_list[0]['message'] == 'Removed user'


def test_admin_user_remove_v1_removing_global_user(reg_two_users_and_create_two_channels):
    # test for 2 global owners, one removing the other, need userpermission change to work
    # make second user a global user
    resp = requests.post(config.url + 'admin/userpermission/change/v1', json={
                         'token': reg_two_users_and_create_two_channels['token1'], 'u_id': reg_two_users_and_create_two_channels['u_id2'], 'permission_id': 1})
    resp.status_code = OK

    # second user now removes first user their global owner role
    resp1 = requests.delete(config.url + 'admin/user/remove/v1', json={
        'token': reg_two_users_and_create_two_channels['token2'], 'u_id': reg_two_users_and_create_two_channels['u_id1']})
    resp1.status_code = OK
