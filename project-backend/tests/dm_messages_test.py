import pytest
import requests
import time
from src.config import url
from src.error import AccessError, InputError
from src.helper import Success_code

# Registers users and stores their returned dictionaries in the users 
# dictionary.
@pytest.fixture
def set_up():
    requests.delete(f'{url}clear/v1')
    users = {}
    for i in range(1, 4):
        pload = {
            'email': f"name{i}@gmail.com", 
            'password': "password", 
            'name_first': f"person{i}", 
            'name_last': f"surname{i}"
        }
        user = requests.post(f'{url}auth/register/v2', json = pload)
        users[f"{i}"] = user.json()
    return users

# Creates a dm, sends 51 messages into the dm from the given user and returns
# the dm_id.
def set_up_dm_51_messages(user):
    pload = {
        'token': user['token'],
        'u_ids': [
            user['auth_user_id']
        ]
    }
    response = requests.post(f'{url}dm/create/v1', json = pload)
    dm_id = response.json()['dm_id']
    for i in range(1,52):
        pload = {
            'token': user['token'],
            'dm_id': dm_id,
            'message': f'{i}'
        }
        requests.post(f'{url}message/senddm/v1', json = pload)
    return dm_id

# Tests that an empty dictionary is returned if no messages are sent in a dm.
def test_dm_messages_empty(set_up):
    users = set_up
    pload = {
        'token': users['2']['token'],
        'u_ids': [
            users['1']['auth_user_id'],
            users['2']['auth_user_id']
        ]
    }
    response = requests.post(f'{url}dm/create/v1', json = pload)
    dm_id = response.json()['dm_id']
    pload = {
        'token': users['2']['token'],
        'dm_id': dm_id,
        'start': 0
    }
    response = requests.get(f'{url}dm/messages/v1', params = pload)
    assert response.status_code == Success_code
    messages = response.json()
    assert messages == {
        'messages' : [],
        'start' : 0,
        'end' : -1
    }

# Tests that a dictionary of dms are displayed starting at the zero index.
def test_dm_messages_zero_start(set_up):
    users = set_up
    pload = {
        'token': users['1']['token'],
        'u_ids': [
            users['1']['auth_user_id'],
            users['2']['auth_user_id']
        ]
    }
    response = requests.post(f'{url}dm/create/v1', json = pload)
    dm_id = response.json()['dm_id']
    pload = {
            'token': users['1']['token'],
            'dm_id': dm_id,
            'message': 'Hi'
    }
    response = requests.post(f'{url}message/senddm/v1', json = pload)
    message_id_1 = response.json()
    pload['token'] = users['2']['token']
    response = requests.post(f'{url}message/senddm/v1', json = pload)
    message_id_2 = response.json()
    pload = {
        'token': users['2']['token'],
        'dm_id': dm_id,
        'start': 0
    }
    response = requests.get(f'{url}dm/messages/v1', params = pload)
    assert response.status_code == Success_code
    messages = response.json()
    assert messages['messages'][0]['message_id'] == message_id_2['message_id']
    assert messages['messages'][0]['u_id'] == users['2']['auth_user_id']
    assert messages['messages'][0]['message'] == 'Hi'
    assert time.time() - messages['messages'][0]['time_created'] < 4
    assert messages['messages'][1]['message_id'] == message_id_1['message_id']
    assert messages['messages'][1]['u_id'] == users['1']['auth_user_id']
    assert messages['messages'][1]['message'] == 'Hi'
    assert time.time() - messages['messages'][1]['time_created'] < 4
    assert messages['start'] == 0
    assert messages['end'] == -1

# Tests that a dictionary of dms are displayed starting at a non-zero index.
def test_dm_messages_non_zero_start(set_up):
    users = set_up
    pload = {
        'token': users['1']['token'],
        'u_ids': [
            users['1']['auth_user_id'],
            users['2']['auth_user_id']
        ]
    }
    response = requests.post(f'{url}dm/create/v1', json = pload)
    dm_id = response.json()['dm_id']
    pload = {
        'token': users['1']['token'],
        'dm_id': dm_id,
        'message': 'Hi'
    }
    response = requests.post(f'{url}message/senddm/v1', json = pload)
    message_id_1 = response.json()
    pload['token'] = users['2']['token']
    response = requests.post(f'{url}message/senddm/v1', json = pload)
    pload = {
        'token': users['2']['token'],
        'dm_id': dm_id,
        'start': 1
    }
    response = requests.get(f'{url}dm/messages/v1', params = pload)
    assert response.status_code == Success_code
    messages = response.json()
    assert messages['messages'][0]['message_id'] == message_id_1['message_id']
    assert messages['messages'][0]['u_id'] == users['1']['auth_user_id']
    assert messages['messages'][0]['message'] == 'Hi'
    assert time.time() - messages['messages'][0]['time_created'] < 4
    assert messages['start'] == 1
    assert messages['end'] == -1

# Tests that dictionary of messages is returned given multiple dms are 
# created.
def test_dm_messages_multiple_channels(set_up):
    users = set_up
    pload = {
        'token': users['2']['token'],
        'u_ids': [
            users['1']['auth_user_id'],
            users['2']['auth_user_id']
        ]
    }
    requests.post(f'{url}dm/create/v1', json = pload)
    pload = {
        'token': users['2']['token'],
        'u_ids': [
            users['1']['auth_user_id'],
            users['2']['auth_user_id']
        ]
    }
    response = requests.post(f'{url}dm/create/v1', json = pload)
    dm_id = response.json()['dm_id']
    pload = {
        'token': users['2']['token'],
        'dm_id': dm_id,
        'start': 0
    }
    response = requests.get(f'{url}dm/messages/v1', params = pload)
    assert response.status_code == Success_code
    messages = response.json()
    assert messages == {
        'messages' : [],
        'start' : 0,
        'end' : -1
    }

# Tests that two dictionaries of messages are returned with the first 
# displaying the first 50 messages in the dm and the second displaying the last
# message.
def test_dm_message_51_messages(set_up):
    users = set_up
    new_dm_id = set_up_dm_51_messages(users['1'])
    pload = {
        'token': users['1']['token'],
        'dm_id': new_dm_id,
        'start': 0
    }
    response = requests.get(f'{url}dm/messages/v1', params = pload)
    assert response.status_code == Success_code
    pload['start'] = 50
    response = requests.get(f'{url}dm/messages/v1', params = pload)
    assert response.status_code == Success_code
    messages = response.json()
    assert messages['messages'][0]['message_id'] == 1
    assert messages['messages'][0]['u_id'] == users['1']['auth_user_id']
    assert messages['messages'][0]['message'] == '1'
    assert time.time() - messages['messages'][0]['time_created'] < 4
    assert messages['start'] == 50
    assert messages['end'] == -1

# Tests that an input error is raised when the dm_id is invalid.
def test_dm_messages_input_error_invalid_dm(set_up):
    users = set_up
    pload = {
        'token': users['2']['token'],
        'dm_id': 1,
        'start': 0
    }
    response = requests.get(f'{url}dm/messages/v1', params = pload)
    assert response.status_code == InputError.code

# Tests that an input error is raised when the start index is greater than
# the length of the dms message bank.
def test_dm_messages_input_error_start_too_big(set_up):
    users = set_up
    pload = {
        'token': users['2']['token'],
        'u_ids': [
            users['1']['auth_user_id'],
            users['2']['auth_user_id']
        ]
    }
    response = requests.post(f'{url}dm/create/v1', json = pload)
    dm_id = response.json()['dm_id']
    pload = {
            'token': users['1']['token'],
            'dm_id': dm_id,
            'message': 'Hi'
    }
    response = requests.post(f'{url}message/senddm/v1', json = pload)
    message_id_1 = response.json()
    pload = {
            'token': users['2']['token'],
            'dm_id': dm_id,
            'start': message_id_1['message_id'] + 1
    }
    response = requests.get(f'{url}dm/messages/v1', params = pload)
    assert response.status_code == InputError.code

#  Tests that an access error is raised when a user not in the channel calls 
#  the dm_messages function.
def test_dm_messages_access_error_user_not_in_dm(set_up):
    users = set_up
    pload = {
        'token': users['2']['token'],
        'u_ids': [
            users['1']['auth_user_id'],
            users['2']['auth_user_id']
        ]
    }
    response = requests.post(f'{url}dm/create/v1', json = pload)
    dm_id = response.json()['dm_id']
    pload = {
            'token': users['1']['token'],
            'dm_id': dm_id,
            'message': 'Hi'
    }
    response = requests.post(f'{url}message/senddm/v1', json = pload)
    message_id_1 = response.json()
    pload = {
            'token': users['3']['token'],
            'dm_id': dm_id,
            'start': message_id_1['message_id'] + 1
    }
    response = requests.get(f'{url}dm/messages/v1', params = pload)
    assert response.status_code == AccessError.code

#  Tests that an access error is raised when the token is inactive.
def test_dm_messages_access_error_inactive_token(set_up):
    users = set_up
    pload = {
        'token': users['2']['token'],
        'u_ids': [
            users['1']['auth_user_id'],
            users['2']['auth_user_id']
        ]
    }
    response = requests.post(f'{url}dm/create/v1', json = pload)
    dm_id = response.json()['dm_id']
    pload = {
            'token': users['1']['token'],
            'dm_id': dm_id,
            'message': 'Hi'
    }
    requests.post(f'{url}message/senddm/v1', json = pload)
    pload = {
        'token': users['2']['token']
    }
    requests.post(f'{url}auth/logout/v1', json = pload)
    pload = {
            'token': users['2']['token'],
            'dm_id': dm_id,
            'start': 0
    }
    response = requests.get(f'{url}dm/messages/v1', params = pload)
    assert response.status_code == AccessError.code

#  Tests that an access error is raised when the token is invalid.
def test_dm_messages_access_error_invalid_token(set_up):
    users = set_up
    pload = {
        'token': users['2']['token'],
        'u_ids': [
            users['1']['auth_user_id'],
            users['2']['auth_user_id']
        ]
    }
    response = requests.post(f'{url}dm/create/v1', json = pload)
    dm_id = response.json()['dm_id']
    pload = {
            'token': users['1']['token'],
            'dm_id': dm_id,
            'message': 'Hi'
    }
    requests.post(f'{url}message/senddm/v1', json = pload)
    pload = {
            'token': users['1']['token'],
            'dm_id': dm_id,
            'message': 'Hi'
    }
    pload = {
            'token': '1',
            'dm_id': dm_id,
            'start': 0
    }
    response = requests.get(f'{url}dm/messages/v1', params = pload)
    assert response.status_code == AccessError.code
