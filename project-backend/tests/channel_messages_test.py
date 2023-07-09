import pytest
import requests
import time
from src.config import url
from src.error import AccessError, InputError
from src.helper import Success_code

# Register users and stores their returned dictionaries in the users 
# dictionary.
@pytest.fixture
def set_up_users():
    requests.delete(f'{url}clear/v1')
    users = {}
    for i in range(1, 3):
        pload = {
            'email': f"name{i}@gmail.com", 
            'password': "password", 
            'name_first': f"person{i}", 
            'name_last': f"surname{i}"
        }
        user = requests.post(f'{url}auth/register/v2', json = pload)
        users[f"{i}"] = user.json()
    return users

# Create a channel given a user and return the new channel_id.
def set_up_channel(user):
    pload = {
        'token': user['token'],
        'name': 'new_channel_1',
        'is_public': True
    }
    response = requests.post(f'{url}channels/create/v2', json = pload)
    new_channel_id = response.json()['channel_id']
    pload = {
        'token': user['token'],
        'channel_id': new_channel_id,
        'message': "Hello"
    }
    response = requests.post(f'{url}message/send/v1', json = pload)
    message_id_1 = response.json()
    pload['message'] = 'World'
    response = requests.post(f'{url}message/send/v1', json = pload)
    message_id_2 = response.json()
    return new_channel_id, message_id_1, message_id_2

# Create a channel, send 51 messages into the channel from the given user and
# return the new channel_id.
def set_up_channel_51_messages(user):
    pload = {
        'token': user['token'],
        'name': 'new_channel_1',
        'is_public': True
    }
    response = requests.post(f'{url}channels/create/v2', json = pload)
    new_channel_id = response.json()['channel_id']
    for i in range(1,52):
        pload = {
            'token': user['token'],
            'channel_id': new_channel_id,
            'message': f"{i}"
        }
        requests.post(f'{url}message/send/v1', json = pload)
    return new_channel_id

# Test that a list of messages are returned given an owner token and
# zero start.
def test_channel_messages_owner_zero_start(set_up_users):
    users = set_up_users
    new_channel_id, message_id_1, message_id_2 = set_up_channel(users['1'])
    pload = {
        'token': users['1']['token'],
        'channel_id': new_channel_id,
        'start': 0
    }
    response = requests.get(f'{url}channel/messages/v2', params = pload)
    assert response.status_code == Success_code
    messages = response.json()
    assert messages['messages'][0]['message_id'] == message_id_2['message_id']
    assert messages['messages'][0]['u_id'] == users['1']['auth_user_id']
    assert messages['messages'][0]['message'] == 'World'
    assert time.time() - messages['messages'][0]['time_created'] < 4
    assert messages['messages'][1]['message_id'] == message_id_1['message_id']
    assert messages['messages'][1]['u_id'] == users['1']['auth_user_id']
    assert messages['messages'][1]['message'] == 'Hello'
    assert time.time() - messages['messages'][1]['time_created'] < 4
    assert messages['start'] == 0
    assert messages['end'] == -1

# Test that a list of messages are returned given an owner token and
# non-zero start.
def test_channel_messages_owner_non_zero_start(set_up_users):
    users = set_up_users
    new_channel_id, message_id_1, message_id_2 = set_up_channel(users['1'])
    assert message_id_2['message_id'] == 2
    pload = {
            'token': users['1']['token'],
            'channel_id': new_channel_id,
            'start': 1
    }
    response = requests.get(f'{url}channel/messages/v2', params = pload)
    assert response.status_code == Success_code
    messages = response.json()
    assert messages['messages'][0]['message_id'] == message_id_1['message_id']
    assert messages['messages'][0]['u_id'] == users['1']['auth_user_id']
    assert messages['messages'][0]['message'] == 'Hello'
    assert time.time() - messages['messages'][0]['time_created'] < 4
    assert messages['start'] == 1
    assert messages['end'] == -1

# Test that the returned messages are the same given two different user tokens 
# and a non-zero start.
def test_channel_messages_user_non_zero_start(set_up_users):
    users = set_up_users
    new_channel_id = set_up_channel(users['1'])[0]
    pload = {
            'token': users['2']['token'],
            'channel_id': new_channel_id,
    }
    requests.post(f'{url}channel/join/v2', json = pload)
    pload = {
            'token': users['1']['token'],
            'channel_id': new_channel_id,
            'start': 1
    }
    response = requests.get(f'{url}channel/messages/v2', params = pload)
    assert response.status_code == Success_code
    messages_1 = response.json()
    pload['token'] = users['2']['token']
    response = requests.get(f'{url}channel/messages/v2', params = pload)
    assert response.status_code == Success_code
    messages_2 = response.json()
    assert messages_1 == messages_2

# Tests that dictionary of messages is returned given multiple channels are 
# created.
def test_channel_messages_multiple_channels(set_up_users):
    users = set_up_users
    set_up_channel(users['1'])
    new_channel_id, message_id_3, message_id_4 = set_up_channel(users['2'])
    pload = {
            'token': users['2']['token'],
            'channel_id': new_channel_id,
            'start': 0
    }
    response = requests.get(f'{url}channel/messages/v2', params = pload)
    assert response.status_code == Success_code
    messages = response.json()
    assert messages['messages'][0]['message_id'] == message_id_4['message_id']
    assert messages['messages'][0]['u_id'] == users['2']['auth_user_id']
    assert messages['messages'][0]['message'] == 'World'
    assert time.time() - messages['messages'][0]['time_created'] < 4
    assert messages['messages'][1]['message_id'] == message_id_3['message_id']
    assert messages['messages'][1]['u_id'] == users['2']['auth_user_id']
    assert messages['messages'][1]['message'] == 'Hello'
    assert time.time() - messages['messages'][1]['time_created'] < 4
    assert messages['start'] == 0
    assert messages['end'] == -1

# Tests that two dictionaries of messages are returned with the first 
# displaying the first 50 messages in the channel and the second displaying 
# the last message.
def test_channel_message_51_messages(set_up_users):
    users = set_up_users
    new_channel_id = set_up_channel_51_messages(users['1'])
    pload = {
        'token': users['1']['token'],
        'channel_id': new_channel_id,
        'start': 0
    }
    response = requests.get(f'{url}channel/messages/v2', params = pload)
    assert response.status_code == Success_code
    pload['start'] = 50
    response = requests.get(f'{url}channel/messages/v2', params = pload)
    assert response.status_code == Success_code
    messages = response.json()
    assert messages['messages'][0]['message_id'] == 1
    assert messages['messages'][0]['u_id'] == users['1']['auth_user_id']
    assert messages['messages'][0]['message'] == '1'
    assert time.time() - messages['messages'][0]['time_created'] < 4
    assert messages['start'] == 50
    assert messages['end'] == -1

# Test that an input error is raised when the channel id is invalid.
def test_channel_messages_input_error_invalid_channel(set_up_users):
    users = set_up_users
    pload = {
        'token': users['1']['token'],
        'channel_id': 1,
        'start': 0
    }
    response = requests.get(f'{url}channel/messages/v2', params = pload)
    assert response.status_code == InputError.code

# Test that an input error is raised when the start index is greater than the 
# message bank.
def test_channel_messages_input_error_start_too_big(set_up_users):
    users = set_up_users
    new_channel_id = set_up_channel(users['1'])
    pload = {
        'token': users['1']['token'],
        'channel_id': new_channel_id,
        'start': 2
    }
    response = requests.get(f'{url}channel/messages/v2', params = pload)
    assert response.status_code == InputError.code

# Test that an access error is raised when the user is not in the channel.
def test_channel_messages_access_error_user_not_in_channel(set_up_users):
    users = set_up_users
    new_channel_id = set_up_channel(users['1'])
    pload = {
        'token': users['2']['token'],
        'channel_id': new_channel_id,
        'start': 0
    }
    response = requests.get(f'{url}channel/messages/v2', params = pload)
    assert response.status_code == AccessError.code

# Test that an access error is raised when the token is inactive.
def test_channel_messages_access_error_inactive_token(set_up_users):
    users = set_up_users
    new_channel_id = set_up_channel(users['1'])
    pload = {
        'token': users['1']['token']
    }
    requests.post(f'{url}auth/logout/v1', json = pload)
    pload = {
        'token': users['1']['token'],
        'channel_id': new_channel_id,
        'start': 0
    }
    response = requests.get(f'{url}channel/messages/v2', params = pload)
    assert response.status_code == AccessError.code

# Test that an access error is raised when the token is invalid.
def test_channel_messages_access_error_invalid_token(set_up_users):
    users = set_up_users
    new_channel_id = set_up_channel(users['1'])
    pload = {
        'token': '1',
        'channel_id': new_channel_id,
        'start': 0
    }
    response = requests.get(f'{url}channel/messages/v2', params = pload)
    assert response.status_code == AccessError.code

