import pytest
import requests
from src.config import url
from src.error import AccessError, InputError
import time
from src.helper import Success_code

LENGTH = 1

def clear_v1():
    requests.delete(f'{url}clear/v1')

def auth_register_v2(email, password, name_first, name_last):
    pload = {
        'email': email,
        'password': password,
        'name_first': name_first,
        'name_last': name_last
    }
    return requests.post(f'{url}auth/register/v2', json = pload).json()

def channels_create_v2(token, name, is_public):
    pload = {
        'token': token,
        'name': name,
        'is_public': is_public
    }
    return requests.post(f'{url}channels/create/v2', json = pload).json()
    
def channel_join_v2(token, channel_id):
    pload = {
        'token': token,
        'channel_id': channel_id
    }
    requests.post(f'{url}channel/join/v2', json = pload)

def channel_messages_v2(token, channel_id, start):
    pload = {
        'token': token,
        'channel_id': channel_id,
        'start': start
    }
    return requests.get(f'{url}channel/messages/v2', params = pload).json()

def standup_start_v1(token, channel_id, length):
    pload = {
        'token': token,
        'channel_id': channel_id,
        'length': length
    }
    requests.post(f'{url}standup/start/v1', json = pload)

def standup_send_v1(token, channel_id, message):
    pload = {
        'token': token,
        'channel_id': channel_id,
        'message': message
    }
    return requests.post(f'{url}standup/send/v1', json = pload)

@pytest.fixture
def set_up():
    clear_v1()
    owner_token = auth_register_v2(
        'history1932@gmail.com', 'password', 'Adam', 'Chen')['token']
    member_token = auth_register_v2(
        'kydares@gmail.com', 'password', 'Kyle', 'Wu')['token']
    channel_id = channels_create_v2(owner_token, 'name', True)['channel_id']
    channel_join_v2(member_token, channel_id)
    return owner_token, member_token, channel_id

# Testing a successful case of sending a message in a standup
def test_standup_send_successful(set_up):
    owner_token, member_token, channel_id = set_up
    standup_start_v1(owner_token, channel_id, LENGTH)
    response = standup_send_v1(member_token, channel_id, "Hello")
    assert response.status_code == Success_code
    assert response.json() == {}
    response = standup_send_v1(owner_token, channel_id, "Hi")
    assert response.status_code == Success_code
    assert response.json() == {}
    time.sleep(LENGTH)
    messages = channel_messages_v2(owner_token, channel_id, 0)['messages']
    assert messages[0]['message'] == "kylewu: Hello\nadamchen: Hi"

# Testing a successful case of sending a message in a standup where @ is used
# in a message
def test_standup_send_successful_with_tag(set_up):
    owner_token, member_token, channel_id = set_up
    standup_start_v1(owner_token, channel_id, LENGTH)
    response = standup_send_v1(member_token, channel_id, "Hello")
    assert response.status_code == Success_code
    assert response.json() == {}
    response = standup_send_v1(owner_token, channel_id, "@Hi")
    assert response.status_code == Success_code
    assert response.json() == {}
    time.sleep(LENGTH)
    messages = channel_messages_v2(owner_token, channel_id, 0)['messages']
    assert messages[0]['message'] == "kylewu: Hello\nadamchen: @Hi"

# The following test for exceptions

# Tests for when an invalid channel_id is passed
def test_standup_send_invalid_channel_id(set_up):
    owner_token, member_token, channel_id = set_up
    standup_start_v1(owner_token, channel_id, LENGTH)
    response = standup_send_v1(member_token, channel_id + 5, "Hello")
    assert response.status_code == InputError.code

# Tests for when the message is over 1000 characters
def test_standup_send_message_too_long(set_up):
    owner_token, member_token, channel_id = set_up
    long_message = "a" * 1001
    standup_start_v1(owner_token, channel_id, LENGTH)
    response = standup_send_v1(member_token, channel_id, long_message)
    assert response.status_code == InputError.code

# Tests for when a message is sent when there is no active standup
def test_standup_send_no_active_standup(set_up):
    owner_token, member_token, channel_id = set_up
    response = standup_send_v1(owner_token, channel_id, "Hello")
    assert response.status_code == InputError.code
    response = standup_send_v1(member_token, channel_id, "Hello")
    assert response.status_code == InputError.code

# Tests for when the user sending the message is not a member of the channel
def test_standup_send_not_member_of_channel(set_up):
    owner_token, member_token, channel_id = set_up
    standup_start_v1(owner_token, channel_id, LENGTH)
    standup_send_v1(member_token, channel_id, "Hello")
    standup_send_v1(owner_token, channel_id, "Hi")
    non_member = auth_register_v2("dt@gmail.com", "password", "Derek", "Tran")
    response = standup_send_v1(non_member['token'], channel_id, "Hello")
    assert response.status_code == AccessError.code

# Tests for when an invalid token is passed
def test_standup_send_invalid_token(set_up):
    owner_token, member_token, channel_id = set_up
    standup_start_v1(owner_token, channel_id, LENGTH)
    response = standup_send_v1(member_token + 'abcdefg', channel_id, "Hello")
    assert response.status_code == AccessError.code
    
    

    


