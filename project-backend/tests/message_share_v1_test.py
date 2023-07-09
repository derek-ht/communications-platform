import pytest
import json
import requests
from src.error import AccessError, InputError
from src.helper import Success_code
from src.config import url
import time

def dm_messages_v1(token, dm_id, start):
    pload = {
        "token": token,
        "dm_id": dm_id,
        "start": start
    }
    response = requests.get(url + "dm/messages/v1", params = pload)
    return response.json()

def message_share_v1(token, og_message_id, message, channel_id, dm_id):
    pload = {
        "token": token,
        "og_message_id": og_message_id,
        "message": message,
        "channel_id": channel_id,
        "dm_id": dm_id
    }
    response = requests.post(url + "message/share/v1", json = pload)
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

def message_send_v1(token, channel_id, message):
    pload = {
        "token": token,
        "channel_id": channel_id,
        "message": message
    }
    response = requests.post(url + "message/send/v1", json = pload)
    return response.json()

def dm_create_v1(token, u_ids):
    pload = {
        "token": token, 
        "u_ids": u_ids
    }
    response = requests.post(url + "dm/create/v1", json = pload)
    return response.json()

def message_senddm_v1(token, dm_id, message):
    pload = {
        "token": token,
        "dm_id": dm_id,
        "message": message
    }
    response = requests.post(url + "message/senddm/v1", json = pload)
    return response.json()

# Set up channel with one member
@pytest.fixture
def set_up_channel():
    requests.delete(f'{url}/clear/v1')
    details = auth_register_v2("1@email.com", "password", "name1", "surname1")
    token = details["token"]

    channel_id = channels_create_v2(token, "channel_name", True)["channel_id"]
    message = "message"
    message_id = message_send_v1(token, channel_id, message)["message_id"]

    return token, channel_id, message, message_id

# Set up dm with two members
@pytest.fixture
def set_up_dm():
    requests.delete(f'{url}/clear/v1')
    
    details = auth_register_v2("1@email.com", "password", "name1", "surname1")
    token = details["token"]

    details = auth_register_v2("2@email.com", "password", "name2", "surname2")
    user_id2 = details["auth_user_id"]

    dm_id = dm_create_v1(token, [user_id2])["dm_id"]
    message = "message"
    message_id = message_senddm_v1(token, dm_id, message)["message_id"]

    return token, dm_id, message, message_id

def check_message(given_message, message_id, message, correct_timestamp, user_id):
    recieved_msg_id = given_message["message_id"]
    recieved_msg = given_message["message"]
    time_created = given_message["time_created"]
    received_user_id = given_message["u_id"]

    assert recieved_msg_id == message_id
    assert recieved_msg == message
    assert received_user_id == user_id
    assert correct_timestamp - time_created < 2

# Tests sharing mesage from channel to channel
def test_share_channel_to_channel(set_up_channel):
    token = set_up_channel[0] 
    message, og_message_id = set_up_channel[2:]
    
    share_chnl_id = channels_create_v2(token, "channel_name2", True)["channel_id"]

    response = message_share_v1(token, og_message_id, "", share_chnl_id, -1)
    assert response.status_code == Success_code

    check_messages = channel_messages_v2(token, share_chnl_id, 0)["messages"]
    assert message in check_messages[0]["message"]

# Tests sharing channel to channel with multiple messages
def test_share_channel_to_channel_multipls_messages(set_up_channel):
    token = set_up_channel[0] 
    
    og_message = "hello"
    message_id = message_send_v1(token, 1, og_message)["message_id"]
    share_chnl_id = channels_create_v2(token, "channel_name2", True)["channel_id"]

    response = message_share_v1(token, message_id, "", share_chnl_id, -1)
    assert response.status_code == Success_code

    check_messages = channel_messages_v2(token, share_chnl_id, 0)["messages"]
    assert og_message in check_messages[0]["message"]

# Tests sharing message from channel to dm
def test_share_channel_to_dm(set_up_channel):
    token = set_up_channel[0] 
    message, og_message_id = set_up_channel[2:]
    
    details = auth_register_v2("2@email.com", "password", "name2", "surname2")
    user_id2 = details["auth_user_id"]

    share_dm_id = dm_create_v1(token, [user_id2])["dm_id"]

    response = message_share_v1(token, og_message_id, "", -1, share_dm_id)
    assert response.status_code == Success_code

    check_messages = dm_messages_v1(token, share_dm_id, 0)["messages"]
    assert message in check_messages[0]["message"]

# Tests sharing message from dm to channel
def test_share_dm_to_channel(set_up_dm):
    token = set_up_dm[0] 
    message, og_message_id = set_up_dm[2:]
    
    share_chnl_id = channels_create_v2(token, "channel_name2", True)["channel_id"]

    response = message_share_v1(token, og_message_id, "", share_chnl_id, -1)
    assert response.status_code == Success_code

    check_messages = channel_messages_v2(token, share_chnl_id, 0)["messages"]
    assert message in check_messages[0]["message"]

# Tests sharing message from dm to dm
def test_share_dm_to_dm(set_up_dm):
    token = set_up_dm[0] 
    message, og_message_id = set_up_dm[2:]
    
    details = auth_register_v2("3@email.com", "password", "name3", "surname3")
    user_id3 = details["auth_user_id"]

    share_dm_id = dm_create_v1(token, [user_id3])["dm_id"]

    response = message_share_v1(token, og_message_id, "", -1, share_dm_id)
    assert response.status_code == Success_code

    check_messages = dm_messages_v1(token, share_dm_id, 0)["messages"]
    assert message in check_messages[0]["message"]

# Tests sharing message from dm to dm with multiple messages
def test_share_dm_to_dm_multiple_messages(set_up_dm):
    token = set_up_dm[0] 
    
    og_message = "poop"
    message_id = message_senddm_v1(token, 1, og_message)["message_id"]

    details = auth_register_v2("3@email.com", "password", "name3", "surname3")
    user_id3 = details["auth_user_id"]

    share_dm_id = dm_create_v1(token, [user_id3])["dm_id"]

    response = message_share_v1(token, message_id, "", -1, share_dm_id)
    assert response.status_code == Success_code

    check_messages = dm_messages_v1(token, share_dm_id, 0)["messages"]
    assert og_message in check_messages[0]["message"]

# Tests sharing message with optional message
def test_share_optional_message(set_up_channel):
    token = set_up_channel[0] 
    og_message_id = set_up_channel[3]
    
    share_chnl_id = channels_create_v2(token, "channel_name2", True)["channel_id"]
    opt_message = "Doctors hate her! You won't believe this"

    response = message_share_v1(token, og_message_id, opt_message, share_chnl_id, -1)
    assert response.status_code == Success_code

    check_messages = channel_messages_v2(token, share_chnl_id, 0)["messages"]
    assert opt_message in check_messages[0]["message"]

# Tests sharing message to dm with optional message
def test_share_optional_message_dm(set_up_dm):
    token = set_up_dm[0] 
    og_message_id = set_up_dm[3]
    
    details = auth_register_v2("3@email.com", "password", "name3", "surname3")
    user_id3 = details["auth_user_id"]

    share_dm_id = dm_create_v1(token, [user_id3])["dm_id"]
    opt_message = "Doctors hate her! You won't believe this"

    response = message_share_v1(token, og_message_id, opt_message, -1, share_dm_id)
    assert response.status_code == Success_code

    check_messages = dm_messages_v1(token, share_dm_id, 0)["messages"]
    assert opt_message in check_messages[0]["message"]

# Tests sharing message where both channel id and dm id arguments are not -1
def test_no_minus_one(set_up_channel):
    token, channel_id = set_up_channel[:2] 
    og_message_id = set_up_channel[3]

    response = message_share_v1(token, og_message_id, "", channel_id, channel_id)
    assert response.status_code == InputError.code

# Tests sharing message given an invalid channel_id
def test_invalid_channel_id(set_up_channel):
    token, channel_id = set_up_channel[:2] 
    og_message_id = set_up_channel[3]
    
    invalid_channel_id = channel_id + 1

    response = message_share_v1(token, og_message_id, "", invalid_channel_id, -1)
    assert response.status_code == InputError.code

# Tests sharing message given an invalid dm_id
def test_invalid_dm_id(set_up_dm):
    token, dm_id = set_up_dm[:2] 
    og_message_id = set_up_dm[3]
    
    invalid_dm_id = dm_id + 1

    response = message_share_v1(token, og_message_id, "", -1, invalid_dm_id)
    assert response.status_code == InputError.code

# Tests when optional message is over 1000 characters
def test_too_big_message(set_up_channel):
    token, channel_id = set_up_channel[:2] 
    og_message_id = set_up_channel[3]
    new_message = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\
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
               aaaaaaaaaaaaaaaaaa"

    response = message_share_v1(token, og_message_id, new_message, channel_id, -1)
    assert response.status_code == InputError.code

# Tests when the message to share doesn't exist
def test_invalid_og_message(set_up_channel):
    token, channel_id = set_up_channel[:2] 
    og_message_id = set_up_channel[3]

    invalid_message_id = og_message_id + 1

    response = message_share_v1(token, invalid_message_id, "", channel_id, -1)
    assert response.status_code == InputError.code

# Tests when the message in dm to share doesn't exist
def test_invalid_og_message_dm(set_up_dm):
    token, dm_id = set_up_dm[:2] 
    og_message_id = set_up_dm[3]

    invalid_message_id = og_message_id + 1

    response = message_share_v1(token, invalid_message_id, "", -1, dm_id)
    assert response.status_code == InputError.code

# Tests when user is not in given channel id
def test_not_in_channel(set_up_channel):
    channel_id = set_up_channel[1] 
    og_message_id = set_up_channel[3]
    details = auth_register_v2("3@email.com", "password", "name3", "surname3")
    not_member_token = details["token"]

    response = message_share_v1(not_member_token, og_message_id, "", channel_id, -1)
    assert response.status_code == AccessError.code

# Tests when user is not in given dm id
def test_not_in_dm(set_up_dm):
    dm_id = set_up_dm[1] 
    og_message_id = set_up_dm[3]
    details = auth_register_v2("3@email.com", "password", "name3", "surname3")
    not_member_token = details["token"]

    response = message_share_v1(not_member_token, og_message_id, "", -1, dm_id)
    assert response.status_code == AccessError.code

# Tests invalid token
def test_invaid_token(set_up_channel):
    channel_id = set_up_channel[1] 
    og_message_id = set_up_channel[3]
    invalid_token = "invalid_token"
    response = message_share_v1(invalid_token, og_message_id, "", channel_id, -1)
    assert response.status_code == AccessError.code