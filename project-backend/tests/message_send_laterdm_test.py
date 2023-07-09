import pytest
import json
import requests
from src.error import AccessError, InputError
from src.helper import Success_code
from src.config import url
import time


def channels_create_v2(token, name, is_public):
    pload = {
        "token": token, 
        "name": name, 
        "is_public": is_public
    }
    response = requests.post(url + "channels/create/v2", json = pload)
    return response.json()

def message_send_laterdm(token, dm_id, message, time_sent ):
    pload = {
        "token": token,
        "dm_id": dm_id,
        "message": message,
        "time_sent": time_sent
    }
    response = requests.post(url + "message/sendlaterdm/v1", json = pload)
    return response

def auth_register_v2(email, password, fname, lname):
    pload = {
        "email": email,
        "password": password,
        "name_first": fname,
        "name_last": lname
    }
    response = requests.post(url + "auth/register/v2", json = pload)
    return response.json()

def dm_create_v1(token, u_ids):
    pload = {
        "token": token, 
        "u_ids": u_ids
    }
    response = requests.post(url + "dm/create/v1", json = pload)
    return response.json()

def dm_messages_v1(token, dm_id, start):
    pload = {
        "token": token,
        "dm_id": dm_id,
        "start": start
    }
    response = requests.get(url + "dm/messages/v1", params = pload)
    return response.json()

@pytest.fixture
def set_up():
    requests.delete(f'{url}/clear/v1')
    details = auth_register_v2("1@email.com", "password", "name1", "surname1")
    token = details["token"]
    user_id = details["auth_user_id"]

    details = auth_register_v2("2@email.com", "password", "name2", "surname2")
    user_id2 = details["auth_user_id"]

    dm_id = dm_create_v1(token, [user_id, user_id2])["dm_id"]

    return token, user_id, dm_id

def check_message(given_message, message_id, message, correct_timestamp, user_id):
    recieved_msg_id = given_message["message_id"]
    recieved_msg = given_message["message"]
    time_created = given_message["time_created"]
    received_user_id = given_message["u_id"]

    assert recieved_msg_id == message_id
    assert recieved_msg == message
    assert received_user_id == user_id
    assert correct_timestamp - time_created < 2

# Test whether valid message to a channel is sent
def test_valid_message_3_seconds(set_up):
    token, user_id, dm_id = set_up

    message = "Hello"
    curr_timestamp = time.time()
    delay = 1
    response = message_send_laterdm(token, dm_id, message, curr_timestamp + delay)
    assert response.status_code == Success_code
    message_id = response.json()["message_id"]
    
    response = dm_messages_v1(token, dm_id, 0)
    messages = response["messages"]
    assert len(messages) == 0
    
    time.sleep(delay + 1)

    response = dm_messages_v1(token, dm_id, 0)
    messages = response["messages"]
    assert len(messages) == 1
    check_message(messages[0], message_id, message, curr_timestamp + delay, user_id)

# test valid message and during wait time allow other functions to operate
def test_valid_message_3_seconds_allow_other_functions_to_operate(set_up):
    token, user_id, dm_id = set_up

    message = "Hello"
    curr_timestamp = time.time()
    delay = 1
    response = message_send_laterdm(token, dm_id, message, curr_timestamp + delay)
    assert response.status_code == Success_code
    message_id = response.json()["message_id"]
    
    response = dm_messages_v1(token, dm_id, 0)
    messages = response["messages"]
    assert len(messages) == 0
    
    #ADD OTHER FUNCIOTNS
    channels_create_v2(token, "pooploopy", True)
    time.sleep(delay + 1)

    response = dm_messages_v1(token, dm_id, 0)
    messages = response["messages"]
    assert len(messages) == 1
    check_message(messages[0], message_id, message, curr_timestamp + delay, user_id)

# Sending message to the past
def test_send_to_past(set_up):
    token, dm_id = set_up[0], set_up[2]

    message = "Hello"
    curr_timestamp = time.time()
    delay = -60
    response = message_send_laterdm(token, dm_id, message, curr_timestamp + delay)
    assert response.status_code == InputError.code

# Test whether message of 1 character is sent one minute later
def test_1_char_3_seconds(set_up):
    token, user_id, dm_id = set_up

    message = "a"
    curr_timestamp = time.time()
    delay = 1
    response = message_send_laterdm(token, dm_id, message, curr_timestamp + delay)
    assert response.status_code == Success_code
    message_id = response.json()["message_id"]
    
    response = dm_messages_v1(token, dm_id, 0)
    messages = response["messages"]
    assert len(messages) == 0
    
    time.sleep(delay + 1)

    response = dm_messages_v1(token, dm_id, 0)
    messages = response["messages"]
    assert len(messages) == 1
    check_message(messages[0], message_id, message, curr_timestamp + delay, user_id)

# Test whether message of 1000 characters is sent
def test_1000_char(set_up):
    token, user_id, dm_id = set_up

    message = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\
aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\
aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\
aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\
aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\
aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\
aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\
aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\
aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\
aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\
aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\
aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\
aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\
aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\
aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\
aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\
aaaaaaaa"
    curr_timestamp = time.time()
    delay = 1
    response = message_send_laterdm(token, dm_id, message, curr_timestamp + delay)
    assert response.status_code == Success_code
    message_id = response.json()["message_id"]
    
    response = dm_messages_v1(token, dm_id, 0)
    messages = response["messages"]
    assert len(messages) == 0
    
    time.sleep(delay + 1)

    response = dm_messages_v1(token, dm_id, 0)
    messages = response["messages"]
    assert len(messages) == 1
    check_message(messages[0], message_id, message, curr_timestamp + delay, user_id)

# Test sending message to nonexistent channel id
def test_invalid_channel_id(set_up):
    token, dm_id = set_up[0], set_up[2]
    
    invalid_channel_id = dm_id + 1

    message = "a"
    curr_timestamp = time.time()
    delay = 1
    response = message_send_laterdm(token, invalid_channel_id, message, curr_timestamp + delay)
    assert response.status_code == InputError.code

#dm_id is valid and the authorised user is not a member of the channel:
#user not part of channel
def test_not_part_of_channel(set_up):
    dm_id = set_up[2]

    response = auth_register_v2("3@email.com", "password", "name3", "lastname3")
    not_member_token = response["token"]

    message = "Hello"
    curr_timestamp = time.time()
    delay = 1
    response = message_send_laterdm(not_member_token, dm_id, message, curr_timestamp + delay)

    assert response.status_code == AccessError.code

# test empty message
def test_empty_message(set_up):
    token, dm_id = set_up[0], set_up[2]

    message = ""
    curr_timestamp = time.time()
    delay = 1
    response = message_send_laterdm(token, dm_id, message, curr_timestamp + delay)

    assert response.status_code == InputError.code

# test message greater than 1000 characters
def test_too_big_message(set_up):
    token, dm_id = set_up[0], set_up[2]

    message = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\
               aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\
               aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\
               aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\
               aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\
               aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\
               aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\
               aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\
               aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\
               aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\
               aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\
               aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\
               aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\
               aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\
               aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\
               aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\
               aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\
               aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\
               aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\
               aaaaaaaaaaaaaa"
    curr_timestamp = time.time()
    delay = 1
    response = message_send_laterdm(token, dm_id, message, curr_timestamp + delay)

    assert response.status_code == InputError.code

# Tests invalid token
def test_invalid_token(set_up):
    dm_id = set_up[2]

    invalid_token = "invalid_token"

    message = "hello"
    curr_timestamp = time.time()
    delay = 1
    response = message_send_laterdm(invalid_token, dm_id, message, curr_timestamp + delay)
    assert response.status_code == AccessError.code