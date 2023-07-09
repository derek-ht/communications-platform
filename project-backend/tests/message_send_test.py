import pytest
import time
import requests
from src.config import url
from src.error import AccessError, InputError
from src.helper import Success_code

@pytest.fixture
def set_up():
    requests.delete(f'{url}/clear/v1')
    pload = {
        "email": "1@email.com",
        "password": "password",
        "name_first": "name1",
        "name_last": "surname1"
    }
    response = requests.post(url + "auth/register/v2", json = pload)
    details = response.json()
    print(details)
    token = details["token"]
    user_id = details["auth_user_id"]

    return token, user_id

# Checks if the given message matches the given message details
def check_message(given_message, message_id, message, curr_timestamp, user_id):
    recieved_msg_id = given_message["message_id"]
    recieved_msg = given_message["message"]
    time_created = given_message["time_created"]
    received_user_id = given_message["u_id"]

    assert recieved_msg_id == message_id
    assert recieved_msg == message
    assert received_user_id == user_id
    assert curr_timestamp - time_created < 2

# Test whether valid message to a private channel is sent
def test_valid_private_channel(set_up):
    token, user_id = set_up

    pload = {
        "token": token, 
        "name": "channel_1", 
        "is_public": False
    }
    response = requests.post(url + "channels/create/v2", json = pload)
    print(response)
    details = response.json()
    channel_id = details["channel_id"]

    message = "Hello"
    pload = {
        "token": token,
        "channel_id": channel_id,
        "message": message
    }
    response = requests.post(url + "message/send/v1", json = pload)
    assert response.status_code == Success_code
    message_id = response.json()["message_id"]
    curr_timestamp = time.time()
    
    pload = {
        "token": token,
        "channel_id": channel_id,
        "start": 0
    }
    response = requests.get(url + "channel/messages/v2", params = pload)
    messages = response.json()["messages"]
    
    check_message(messages[0], message_id, message, curr_timestamp, user_id)

# Test whether valid message to a public channel is sent
def test_valid_public_channel(set_up):
    token, user_id = set_up
    
    pload = {
        "token": token,
        "name": "channel_1",
        "is_public": True
    }
    response = requests.post(url + "channels/create/v2", json = pload)
    channel_id = response.json()["channel_id"]

    message = "Hello"
    pload = {
        "token": token,
        "channel_id": channel_id,
        "message": message
    }
    response = requests.post(url + "message/send/v1", json = pload)
    assert response.status_code == Success_code
    message_id = response.json()["message_id"]
    curr_timestamp = time.time()
    
    pload = {
        "token": token,
        "channel_id": channel_id,
        "start": 0
    }
    response = requests.get(url + "channel/messages/v2", params = pload)
    messages = response.json()["messages"]

    check_message(messages[0], message_id, message, curr_timestamp, user_id)

# Test whether message of 1 character is sent
def test_1_char(set_up):
    token, user_id = set_up
    
    pload = {
        "token": token,
        "name": "channel_1",
        "is_public": True
    }
    response = requests.post(url + "channels/create/v2", json = pload)
    channel_id = response.json()["channel_id"]

    message = "a"
    pload = {
        "token": token,
        "channel_id": channel_id,
        "message": message
    }
    response = requests.post(url + "message/send/v1", json = pload)
    assert response.status_code == Success_code
    message_id = response.json()["message_id"]
    curr_timestamp = time.time()
    
    pload = {
        "token": token,
        "channel_id": channel_id,
        "start": 0
    }
    response = requests.get(url + "channel/messages/v2", params = pload)
    messages = response.json()["messages"]

    check_message(messages[0], message_id, message, curr_timestamp, user_id)

# Test whether message of 1000 characters is sent
def test_1000_char(set_up):
    token, user_id = set_up
    pload = {
        "token": token,
        "name": "channel_1",
        "is_public": True
    }
    response = requests.post(url + "channels/create/v2", json = pload)
    channel_id = response.json()["channel_id"]

    long_msg = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\
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

    pload = {
        "token": token,
        "channel_id": channel_id,
        "message": long_msg
    }
    response = requests.post(url + "message/send/v1", json = pload)
    assert response.status_code == Success_code
    message_id = response.json()["message_id"]
    curr_timestamp = time.time()
    
    pload = {
        "token": token,
        "channel_id": channel_id,
        "start": 0
    }
    response = requests.get(url + "channel/messages/v2", params = pload)
    messages = response.json()["messages"]

    check_message(messages[0], message_id, long_msg, curr_timestamp, user_id)

# Test sending message to nonexistent channel id
def test_invalid_channel_id(set_up):
    token = set_up[0]
    
    pload = {
        "token": token,
        "name": "channel_1",
        "is_public": True
    }
    response = requests.post(url + "channels/create/v2", json = pload)
    channel_id = response.json()["channel_id"]

    invalid_channel_id = channel_id + 1

    message = "Hello"
    pload = {
        "token": token,
        "channel_id": invalid_channel_id,
        "message": message
    }
    response = requests.post(url + "message/send/v1", json = pload)

    assert response.status_code == InputError.code

#channel_id is valid and the authorised user is not a member of the channel:
#user not part of channel
def test_not_part_of_channel(set_up):
    token = set_up[0]
    
    pload = {
            "token": token,
            "name": "channel_1",
            "is_public": True
        }
    response = requests.post(url + "channels/create/v2", json = pload)
    channel_id = response.json()["channel_id"] 

    pload = {
        "email": "2@email.com",
        "password": "password",
        "name_first": "name",
        "name_last": "lastname"
    }
    response = requests.post(url + "auth/register/v2", json = pload)
    not_member_token = response.json()["token"]

    message = "Hello"
    pload = {
        "token": not_member_token,
        "channel_id": channel_id,
        "message": message
    }
    response = requests.post(url + "message/send/v1", json = pload)
    assert response.status_code == AccessError.code

# test empty message
def test_empty_message(set_up):
    token = set_up[0]
    
    pload = {
            "token": token,
            "name": "channel_1",
            "is_public": True
        }
    response = requests.post(url + "channels/create/v2", json = pload)
    channel_id = response.json()["channel_id"]

    message = ""
    pload = {
        "token": token,
        "channel_id": channel_id,
        "message": message
    }
    response = requests.post(url + "message/send/v1", json = pload)
    assert response.status_code == InputError.code

# test message greater than 1000 characters
def test_too_big_message(set_up):
    token = set_up[0]
    
    pload = {
            "token": token,
            "name": "channel_1",
            "is_public": True
        }
    response = requests.post(url + "channels/create/v2", json = pload)
    channel_id = response.json()["channel_id"]

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
    pload = {
        "token": token,
        "channel_id": channel_id,
        "message": message
    }
    response = requests.post(url + "message/send/v1", json = pload)
    assert response.status_code == InputError.code

# Tests invalid token
def test_invalid_token(set_up):
    token = set_up[0]
    pload = {
            "token": token,
            "name": "channel_1",
            "is_public": True
        }
    response = requests.post(url + "channels/create/v2", json = pload)
    channel_id = response.json()["channel_id"]

    invalid_token = "invalid_token_string"
    
    pload = {
        "token": invalid_token,
        "channel_id": channel_id,
        "message": "message"
    }
    response = requests.post(url + "message/send/v1", json = pload)
    assert response.status_code == AccessError.code

# Coverage test which tests the generate_message_id returns a valid id.
def test_message_send_generate_message_id(set_up):
    token = set_up[0]
    pload = {
        'token': token,
        'name': "channel",
        'is_public': True
    }
    response = requests.post(f'{url}channels/create/v2', json = pload)
    channel_id_1 = response.json()['channel_id']
    response = requests.post(f'{url}channels/create/v2', json = pload)
    channel_id_2 = response.json()['channel_id']
    response = requests.post(f'{url}channels/create/v2', json = pload)
    channel_id_3 = response.json()['channel_id']
    pload = {
            'token': token,
            'channel_id': channel_id_3,
            'message': 'Hey Friends'
    }
    response = requests.post(f'{url}message/send/v1', json = pload)
    assert response.status_code == Success_code
    message_id_1 = response.json()
    assert message_id_1 == {'message_id' : 1}
    pload['channel_id'] = channel_id_2 
    response = requests.post(f'{url}message/send/v1', json = pload)
    assert response.status_code == Success_code
    message_id_2 = response.json()
    assert message_id_2 == {'message_id' : 2}
    pload['channel_id'] = channel_id_1 
    response = requests.post(f'{url}message/send/v1', json = pload)
    assert response.status_code == Success_code
    message_id_2 = response.json()
    assert message_id_2 == {'message_id' : 3}