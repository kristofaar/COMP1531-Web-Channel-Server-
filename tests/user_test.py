import pytest
import requests
import json
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

def test_users_two_users(reg_two_users):
    resp1 = requests.get(config.url + 'users/all/v1', params={'token': reg_two_users['token1']})
    assert resp1.status_code == OK
    resp1_data = resp1.json()
    assert resp1_data["users"][0]["u_id"] == reg_two_users["u_id1"]
    assert resp1_data["users"][1]["u_id"] == reg_two_users["u_id2"]

def test_user_profile(reg_user):
    resp = requests.get(config.url + "user/profile/v1", params={"token": reg_user["token"], "u_id": reg_user["u_id"]})
    assert resp.status_code == OK
    assert resp.json() == [{
        "u_id": reg_user["u_id"]
    }]

# Tests for user/profile/setname/v1
def test_setname_valid(reg_user):
    resp = requests.put(config.url + "user/profile/setname/v1", json={"token": reg_user["token"], "new_first", "new_last"})
    assert resp.status_code == OK
    assert resp.json() == [{
        "name_first" == "new_first",
        "name_last" == "new_last",
    }]
def test_invalid_name_first(reg_user):
    resp = requests.put(config.url + "user/profile/setname/v1", json={"token": reg_user["token"], "A" * 100, "new_last"})
    assert resp.status_code == I_ERR
def test_invalid_name_last(reg_user):
    resp = requests.put(config.url + "user/profile/setname/v1", json={"token": reg_user["token"], "new_first", "A" * 100})
    assert resp.status_code == I_ERR

# Tests for user/profile/setemail/v1
def test_setemail_valid(reg_user):
def test_invalid_email(reg_user):
def test_duplicate_email(reg_user):

# Tests for user/profile/sethandle/v1
def test_sethandle_valid(reg_user):
def test_invalid_handle_len(reg_user):
def test_non_alnum_handle(reg_user):
def test_duplicate_handle(reg_user):
