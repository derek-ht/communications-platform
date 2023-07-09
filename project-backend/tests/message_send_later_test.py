import pytest
import json
import requests
from src.error import AccessError, InputError
from src.helper import Success_code
from src.config import url
import time

def message_send_later(token, channel_id, message, time_sent ):
    pload = {
        "token": token,
        "channel_id": channel_id,
        "message": message,
        "time_sent": time_sent
    }
    response = requests.post(url + "/message/sendlater/v1", json = pload)
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

def channels_create_v2(token, name, is_public):
    pload = {
        "token": token, 
        "name": name, 
        "is_public": is_public
    }
    response = requests.post(url + "channels/create/v2", json = pload)
    return response.json()

def channel_messages_v2(token, channel_id, start):
    pload = {
        "token": token,
        "channel_id": channel_id,
        "start": start
    }
    response = requests.get(url + "channel/messages/v2", params = pload)
    return response.json()

@pytest.fixture
def set_up():
    requests.delete(f'{url}/clear/v1')
    details = auth_register_v2("1@email.com", "password", "name1", "surname1")
    token = details["token"]
    user_id = details["auth_user_id"]

    return token, user_id

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
    token, user_id = set_up

    details = channels_create_v2(token, "channel_1", True)
    channel_id = details["channel_id"]

    message = "Hello"
    curr_timestamp = time.time()
    delay = 1
    response = message_send_later(token, channel_id, message, curr_timestamp + delay)
    assert response.status_code == Success_code
    message_id = response.json()["message_id"]
    
    response = channel_messages_v2(token, channel_id, 0)
    messages = response["messages"]
    assert len(messages) == 0
    
    time.sleep(delay + 1)

    response = channel_messages_v2(token, channel_id, 0)
    messages = response["messages"]
    assert len(messages) == 1
    check_message(messages[0], message_id, message, curr_timestamp + delay, user_id)

# test valid message and during wait time allow other functions to operate
def test_valid_message_3_seconds_allow_other_functions_to_operate(set_up):
    token, user_id = set_up

    details = channels_create_v2(token, "channel_1", True)
    channel_id = details["channel_id"]

    message = "Hello"
    curr_timestamp = time.time()
    delay = 1
    response = message_send_later(token, channel_id, message, curr_timestamp + delay)
    assert response.status_code == Success_code
    message_id = response.json()["message_id"]
    
    response = channel_messages_v2(token, channel_id, 0)
    messages = response["messages"]
    assert len(messages) == 0
    
    #OTHER FUNCIOTNS
    channels_create_v2(token, "poopychannel", True)

    time.sleep(delay + 1)

    response = channel_messages_v2(token, channel_id, 0)
    messages = response["messages"]
    assert len(messages) == 1
    check_message(messages[0], message_id, message, curr_timestamp + delay, user_id)

# Sending message to the past
def test_send_to_past(set_up):
    token = set_up[0]

    details = channels_create_v2(token, "channel_1", True)
    channel_id = details["channel_id"]

    message = "Hello"
    curr_timestamp = time.time()
    delay = -60
    response = message_send_later(token, channel_id, message, curr_timestamp + delay)
    assert response.status_code == InputError.code

# Test whether message of 1 character is sent one minute later
def test_1_char_3_seconds(set_up):
    token, user_id = set_up

    details = channels_create_v2(token, "channel_1", True)
    channel_id = details["channel_id"]

    message = "a"
    curr_timestamp = time.time()
    delay = 1
    response = message_send_later(token, channel_id, message, curr_timestamp + delay)
    assert response.status_code == Success_code
    message_id = response.json()["message_id"]
    
    response = channel_messages_v2(token, channel_id, 0)
    messages = response["messages"]
    assert len(messages) == 0
    
    time.sleep(delay + 1)

    response = channel_messages_v2(token, channel_id, 0)
    messages = response["messages"]
    assert len(messages) == 1
    check_message(messages[0], message_id, message, curr_timestamp + delay, user_id)

# Test whether message of 1000 characters is sent
def test_1000_char(set_up):
    token, user_id = set_up

    details = channels_create_v2(token, "channel_1", True)
    channel_id = details["channel_id"]

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
    response = message_send_later(token, channel_id, message, curr_timestamp + delay)
    assert response.status_code == Success_code
    message_id = response.json()["message_id"]
    
    response = channel_messages_v2(token, channel_id, 0)
    messages = response["messages"]
    assert len(messages) == 0
    
    time.sleep(delay + 1)

    response = channel_messages_v2(token, channel_id, 0)
    messages = response["messages"]
    assert len(messages) == 1
    check_message(messages[0], message_id, message, curr_timestamp + delay, user_id)

# Test sending message to nonexistent channel id
def test_invalid_channel_id(set_up):
    token = set_up[0]

    details = channels_create_v2(token, "channel_1", True)
    channel_id = details["channel_id"]
    
    invalid_channel_id = channel_id + 1

    message = "a"
    curr_timestamp = time.time()
    delay = 1
    response = message_send_later(token, invalid_channel_id, message, curr_timestamp + delay)
    assert response.status_code == InputError.code

#channel_id is valid and the authorised user is not a member of the channel:
#user not part of channel
def test_not_part_of_channel(set_up):
    token = set_up[0]
    
    response = channels_create_v2(token, "channel_1", True)
    channel_id = response["channel_id"] 

    response = auth_register_v2("2@email.com", "password", "name", "lastname")
    not_member_token = response["token"]

    message = "Hello"
    curr_timestamp = time.time()
    delay = 1
    response = message_send_later(not_member_token, channel_id, message, curr_timestamp + delay)

    assert response.status_code == AccessError.code

# test empty message
def test_empty_message(set_up):
    token = set_up[0]

    details = channels_create_v2(token, "channel_1", True)
    channel_id = details["channel_id"]

    message = ""
    curr_timestamp = time.time()
    delay = 1
    response = message_send_later(token, channel_id, message, curr_timestamp + delay)

    assert response.status_code == InputError.code

# test message greater than 1000 characters
def test_too_big_message(set_up):
    token = set_up[0]

    details = channels_create_v2(token, "channel_1", True)
    channel_id = details["channel_id"]

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
    response = message_send_later(token, channel_id, message, curr_timestamp + delay)

    assert response.status_code == InputError.code

# Tests invalid token
def test_invalid_token(set_up):
    token = set_up[0]
    details = channels_create_v2(token, "channel_1", True)
    channel_id = details["channel_id"]

    invalid_token = "invalid_token"

    message = "hello"
    curr_timestamp = time.time()
    delay = 1
    response = message_send_later(invalid_token, channel_id, message, curr_timestamp + delay)
    assert response.status_code == AccessError.code