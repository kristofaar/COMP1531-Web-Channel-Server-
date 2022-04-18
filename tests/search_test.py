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
def send_message():
    # Register a user
    clear_resp = requests.delete(config.url + "clear/v1")
    assert clear_resp.status_code == OK
    resp = requests.post(config.url + "auth/register/v2", json={"email": "1@test.test", "password": "1testtest", "name_first": "first_test", "name_last": "first_test"})
    assert resp.status_code == OK
    reg_user = resp.json()

    # Create a channel
    resp = requests.post(config.url + 'channels/create/v2', json={"token": reg_user["token"], "name": "first_channel", "is_public": True})
    assert resp.status_code == OK
    create_channel = resp.json()

    # Send a message
    resp = requests.post(config.url + "message/send/v1", json={"token": reg_user["token"], "channel_id": create_channel["channel_id"], "message": "The quick brown fox jumped over the lazy dog."})
    assert resp.status_code == OK
    send_msg = resp.json()

    return {
        "token": reg_user["token"], 
        "u_id": reg_user["auth_user_id"],
        "channel_id": create_channel["channel_id"],
        "message_id": send_msg["message_id"],
    }

# Tests for search/v1
def test_search_invalid_token(send_message):
    resp = requests.get(config.url + "search/v1", params={"token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c", "query_str": "Fox"})
    assert resp.status_code == A_ERR

def test_search_invalid_query_str(send_message):
    resp = requests.get(config.url + "search/v1", params={"token": send_message["token"], "query_str": "c" * 1001})
    assert resp.status_code == I_ERR

def test_search_valid(send_message):
    resp = requests.get(config.url + "search/v1", params={"token": send_message["token"], "query_str": "Fox"})
    assert resp.status_code == OK
    resp_data = resp.json()
    assert resp_data["messages"][0]["message"] == "The quick brown fox jumped over the lazy dog."
