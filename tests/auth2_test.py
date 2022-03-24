import pytest
import requests
import json
from src import config

A_ERR = 403
I_ERR = 400
OK = 200
"""
@pytest.fixture
def reg_two_users():
    clear_resp = requests.delete(config.url + 'clear/v1')
    assert clear_resp.status_code == OK
    resp1 = requests.post(config.url + 'auth/register/v2', json={'email': 'teast@test.test', 'password': 'testtesttest', 'name_first': 'test', 'name_last': 'test'})
    assert resp1.status_code == OK
    resp2 = requests.post(config.url + 'auth/register/v2', json={'email': 'lol@lol.lol', 'password': '123abc123abc', 'name_first': 'Jane', 'name_last': 'Austen'})
    assert resp2.status_code == OK
    resp1_data = resp1.json()
    resp2_data = resp2.json()
    return {'token1': resp1_data['token'], 'token2': resp2_data['token'], 'u_id1': resp1_data['auth_user_id'], 'u_id2': resp2_data['auth_user_id']}

#login errors
def test_login_invalid_email(reg_two_users):
    resp = requests.post(config.url + 'auth/login/v2', json={'email': 'invalid@email.lol', 'password': 'coolpass123'})
    assert resp.status_code == I_ERR

def test_login_wrong_pass(reg_two_users):
    resp = requests.post(config.url + 'auth/login/v2', json={'email': 'lol@lol.lol', 'password': 'coolpass123'})
    assert resp.status_code == I_ERR

#login working
def test_login_working(reg_two_users):
    resp1 = requests.post(config.url + 'auth/login/v2', json={'email': 'teast@test.test', 'password': 'testtesttest'})
    assert resp1.status_code == OK
    resp2 = requests.post(config.url + 'auth/login/v2', json={'email': 'lol@lol.lol', 'password': '123abc123abc'})
    assert resp2.status_code == OK

def test_login_multiple_sessions(reg_two_users):
    resp = requests.post(config.url + 'auth/login/v2', json={'email': 'lol@lol.lol', 'password': '123abc123abc'})
    resp_data = resp.json()
    assert resp_data['token'] != reg_two_users['token2']

#register errors
def test_email_invalid(reg_two_users):
    resp = requests.post(config.url + 'auth/register/v2', json={'email': 'teast', 'password': 'testtesttest', 'name_first': 'test', 'name_last': 'test'})
    assert resp.status_code == I_ERR

def test_email_duplicate(reg_two_users):
    resp = requests.post(config.url + 'auth/register/v2', json={'email': 'teast@test.test', 'password': 'testtesttest', 'name_first': 'test', 'name_last': 'test'})
    assert resp.status_code == I_ERR

def test_invalid_pass(reg_two_users):
        resp = requests.post(config.url + 'auth/register/v2', json={'email': 't@test.test', 'password': '', 'name_first': 'test', 'name_last': 'test'})
        assert resp.status_code == I_ERR

def test_invalid_name(reg_two_users):
        resp1 = requests.post(config.url + 'auth/register/v2', json={'email': '1@test.test', 'password': '2131443214das', 'name_first': '', 'name_last': 'test'})
        assert resp1.status_code == I_ERR
        resp2 = requests.post(config.url + 'auth/register/v2', json={'email': '2@test.test', 'password': '2131443214das', 'name_first': 'a6tdsf679t679fdst76tfad76st67fdst76fdst67tfds67tf76dst67fdst67afdts67tf67atsd67ftda67stf67tafd67st67dasft67fda67', 'name_last': 'test'})
        assert resp2.status_code == I_ERR
        resp3 = requests.post(config.url + 'auth/register/v2', json={'email': '3@test.test', 'password': '2131443214das', 'name_first': 'sadasdasd', 'name_last': ''})
        assert resp3.status_code == I_ERR
        resp4 = requests.post(config.url + 'auth/register/v2', json={'email': '4@test.test', 'password': '2131443214das', 'name_first': 'asd', 'name_last': 'te2317213g8y21g38g321876g3218g312687t327816t73821tg78321tg78321gt78321tg78312t78321t783t78132t78213ty87123t78123ty78123t78t32178'})
        assert resp4.status_code == I_ERR

#register working

def test_register():
    clear_resp = requests.delete(config.url + 'clear/v1')
    assert clear_resp.status_code == OK
    resp1 = requests.post(config.url + 'auth/register/v2', json={'email': 'teast@test.test', 'password': 'testtesttest', 'name_first': 'test', 'name_last': 'test'})
    assert resp1.status_code == OK

#logout error

def test_invalid_logout(reg_two_users):
    resp1 = requests.post(config.url + 'auth/logout/v1', json={'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c'})
    assert resp1.status_code == A_ERR

def test_logout_twice(reg_two_users):
    requests.post(config.url + 'auth/logout/v1', json={'token': reg_two_users['token1']})
    resp1 = requests.post(config.url + 'auth/logout/v1', json={'token': reg_two_users['token1']})
    assert resp1.status_code == A_ERR
"""
#logout working

def test_logout(reg_two_users):
    resp1 = requests.post(config.url + 'auth/logout/v1', json={'token': reg_two_users['token1']})
    assert resp1.status_code == OK
    resp2 = requests.post(config.url + 'channels/create/v2', json={'token': reg_two_users['token1'], 'name': 'okName', 'is_public': False})
    assert resp2.status_code == A_ERR
