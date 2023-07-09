import pytest
import requests
from src.config import url
from src.error import AccessError, InputError
from src.helper import Success_code
import time

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

def standup_start_v1(token, channel_id, length):
    pload = {
        'token': token,
        'channel_id': channel_id,
        'length': length
    }
    return requests.post(f'{url}standup/start/v1', json = pload)

@pytest.fixture
def set_up():
    clear_v1()
    owner_token = auth_register_v2(
        'history1932@gmail.com', 'password', 'Adam', 'Chen')['token']
    member_token = auth_register_v2(
        'kydares@gmail.com', 'password', 'Kyle', 'Wu')['token']
    channel_id = channels_create_v2(owner_token, 'name', True)['channel_id']
    channel_join_v2(member_token, channel_id)
    return owner_token, channel_id

# Tests a successful case
def test_standup_start_successful(set_up):
    owner_token, channel_id = set_up
    time_start = int(time.time())
    response = standup_start_v1(owner_token, channel_id, 5)
    assert response.status_code == Success_code
    # Checking that the return value is correct
    assert (int(response.json()['time_finish']) - time_start) - 5 == 0

# Tests for when an invalid channel_id is passed
def test_standup_start_invalid_channel_id(set_up):
    owner_token, channel_id = set_up
    response = standup_start_v1(owner_token, channel_id + 10, 1)
    assert response.status_code == InputError.code

# Tests for when an invalid length is passed
def test_standup_start_invalid_length(set_up):
    owner_token, channel_id = set_up
    response = standup_start_v1(owner_token, channel_id, -1)
    assert response.status_code == InputError.code

# Tests for when another standup is currently occurring
def test_standup_start_channel_already_has_standup(set_up):
    owner_token, channel_id = set_up
    standup_start_v1(owner_token, channel_id, 5)
    response = standup_start_v1(owner_token, channel_id, 1)
    assert response.status_code == InputError.code

# Tests for when the user who starts the standup is not in the channel
def test_standup_start_user_not_in_channel(set_up):
    non_member_token, channel_id = set_up
    non_member_token = auth_register_v2(
        'derek@gmail.com', 'password', 'Derek', 'Tran')['token']
    response = standup_start_v1(non_member_token, channel_id, 1)
    assert response.status_code == AccessError.code

# Tests for when an invalid token is passed
def test_standup_start_invalid_token(set_up):
    owner_token, channel_id = set_up
    response = standup_start_v1(owner_token + 'abc', channel_id, 1)
    assert response.status_code == AccessError.code




    
