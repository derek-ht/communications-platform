import pytest
import requests
from src.config import url
from src.error import AccessError, InputError
from src.helper import Success_code

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
    return requests.post(f'{url}standup/start/v1', json = pload).json()

def standup_active_v1(token, channel_id):
    pload = {
        'token': token,
        'channel_id': channel_id
    }
    return requests.get(f'{url}standup/active/v1', params = pload)

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

# Tests a successful case when there is an active standup
def test_standup_active_successful_active_standup(set_up):
    owner_token, channel_id = set_up
    print(channel_id)
    time_finish = standup_start_v1(owner_token, channel_id, 10)['time_finish']
    response = standup_active_v1(owner_token, channel_id)
    assert response.status_code == Success_code
    assert response.json()['is_active'] == True
    assert response.json()['time_finish'] == time_finish

# Tests a successful case when there is no active standup
def test_standup_active_successful_no_active_standup(set_up):
    owner_token, channel_id = set_up
    response = standup_active_v1(owner_token, channel_id)
    assert response.status_code == Success_code
    assert response.json()['is_active'] == False
    assert response.json()['time_finish'] == None

# The following test for exceptions

# Tests for when an invalid channel_id is passed
def test_standup_active_invalid_channel_id(set_up):
    owner_token, channel_id = set_up
    standup_start_v1(owner_token, channel_id, 10)['time_finish']
    response = standup_active_v1(owner_token, channel_id + 10)
    assert response.status_code == InputError.code

# Tests for when the given token does not belong to a member of the channel
def test_standup_active_not_member_of_channel(set_up):
    owner_token, channel_id = set_up
    standup_start_v1(owner_token, channel_id, 5)['time_finish']
    non_member_token = auth_register_v2(
        'derek@gmail.com', 'password', 'Derek', 'Tran')['token']
    response = standup_active_v1(non_member_token, channel_id)
    assert response.status_code == AccessError.code

# Tests for when an invalid token is passed
def test_standup_active_invalid_token(set_up):
    owner_token, channel_id = set_up
    standup_start_v1(owner_token, channel_id, 5)['time_finish']
    response = standup_active_v1(owner_token + 'abcdefg', channel_id)
    assert response.status_code == AccessError.code