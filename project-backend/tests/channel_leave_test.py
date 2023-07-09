import pytest
import requests
from src.config import url
from src.error import AccessError, InputError
from src.helper import Success_code

@pytest.fixture
def set_up():
    requests.delete(f'{url}clear/v1')

    member_token = requests.post(f'{url}auth/register/v2', json = {
    'email': 'history@gmail.com',
    'password': '123456',
    'name_first': 'Adam',
    'name_last': 'Chen'}).json()['token']

    user_token = requests.post(f'{url}auth/register/v2', json = {
    'email': 'kydares@gmail.com',
    'password': 'ilovemyself',
    'name_first': 'Kyle',
    'name_last': 'Wu'}).json()['token']

    new_channel_id = requests.post(f'{url}channels/create/v2', json = {
    'token': member_token,
    'name': 'new_channel',
    'is_public': True}).json()['channel_id']

    return member_token, new_channel_id, user_token

@pytest.fixture
def set_up_no_member_token():
    requests.delete(f'{url}clear/v1')

    member_token = requests.post(f'{url}auth/register/v2', json = {
    'email': 'history@gmail.com',
    'password': '123456',
    'name_first': 'Adam',
    'name_last': 'Chen'}).json()['token']

    user_token = requests.post(f'{url}auth/register/v2', json = {
    'email': 'kydares@gmail.com',
    'password': 'ilovemyself',
    'name_first': 'Kyle',
    'name_last': 'Wu'}).json()['token']

    new_channel_id = requests.post(f'{url}channels/create/v2', json = {
    'token': member_token,
    'name': 'new_channel',
    'is_public': True}).json()['channel_id']

    return new_channel_id, user_token

# This tests for when a non_owner member leaves the channel
def test_channel_leave_non_owner_successful(set_up):
    member_token, new_channel_id, user_token = set_up

    new_channel_id = requests.post(f'{url}channels/create/v2', json = {
    'token': member_token,
    'name': 'another_new_channel',
    'is_public': True}).json()['channel_id']

    requests.post(f'{url}channel/join/v2', json = {
    'token': user_token,
    'channel_id': new_channel_id})

    response = requests.post(f'{url}channel/leave/v1', json = {
        'token': user_token,
        'channel_id': new_channel_id
    })

    assert response.json() == {}
    assert response.status_code == Success_code

    response = requests.get(f'{url}channels/list/v2', params = {
    'token': user_token})
    assert response.json()['channels'] == []

    # Checking that member is not in channel

    channel_members = requests.get(f'{url}/channel/details/v2', params = {
        'token': member_token,
        'channel_id': new_channel_id
    }).json()['all_members']

    is_member = False
    for members in channel_members:
        if members['email'] == 'kydares@gmail.com':
            is_member = True
    assert is_member == False

# This tests for when an owner of the channel leaves their channel
def test_channel_leave_owner_successful(set_up):
    member_token, new_channel_id, user_token = set_up

    requests.post(f'{url}channel/join/v2', json = {
    'token': user_token,
    'channel_id': new_channel_id})

    response = requests.post(f'{url}channel/leave/v1', json = {
        'token': member_token,
        'channel_id': new_channel_id
    })

    assert response.json() == {}
    assert response.status_code == Success_code

    response = requests.get(f'{url}channels/list/v2', params = {
    'token': member_token})
    assert response.json()['channels'] == []

    # Checking that member is not in channel

    channel_members = requests.get(f'{url}/channel/details/v2', params = {
        'token': user_token,
        'channel_id': new_channel_id
    }).json()['all_members']

    is_member = False
    for members in channel_members:
        if members['email'] == 'history1932@gmail.com':
            is_member = True
    assert is_member == False

    # Checking that member is not owner

    owner_members = requests.get(f'{url}/channel/details/v2', params = {
        'token': user_token,
        'channel_id': new_channel_id
    }).json()['owner_members']
    is_owner = False
    for members in owner_members:
        if members['email'] == 'history1932@gmail.com':
            is_owner = True
    assert is_owner == False
    
# The following tests for errors

# This tests for when an invalid channel_id is passed
def test_channel_leave_invalid_channel_id(set_up_no_member_token):
    new_channel_id, user_token = set_up_no_member_token
    
    requests.post(f'{url}channel/join/v2', json = {
    'token': user_token,
    'channel_id': new_channel_id})

    response = requests.post(f'{url}channel/leave/v1', json = {
        'token': user_token,
        'channel_id': new_channel_id + 3
    })

    assert response.status_code == InputError.code

# This tests for when a non-member attempts to leave a channel
def test_channel_leave_non_member(set_up_no_member_token):
    new_channel_id, user_token = set_up_no_member_token

    response = requests.post(f'{url}channel/leave/v1', json = {
        'token': user_token,
        'channel_id': new_channel_id
    })

    assert response.status_code == AccessError.code

# This tests for when an invalid token is passed
def test_channel_leave_invalid_token(set_up_no_member_token):
    new_channel_id, user_token = set_up_no_member_token

    requests.post(f'{url}channel/join/v2', json = {
    'token': user_token,
    'channel_id': new_channel_id})

    response = requests.post(f'{url}channel/leave/v1', json = {
    'token': 'invalid_token',
    'channel_id': new_channel_id})

    assert response.status_code == AccessError.code

# The following tests for when input and access errors are implied

# Tests for when an invalid token and an invalid channel_id are passed
def test_channel_leave_invalid_token_and_invalid_channel_id(set_up_no_member_token):
    new_channel_id, user_token = set_up_no_member_token

    requests.post(f'{url}channel/join/v2', json = {
    'token': user_token,
    'channel_id': new_channel_id})

    response = requests.post(f'{url}channel/leave/v1', json = {
    'token': 'invalid_token',
    'channel_id': new_channel_id + 3})

    assert response.status_code == AccessError.code
