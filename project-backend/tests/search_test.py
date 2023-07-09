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

def dm_create_v1(token, u_ids):
    pload = {
        'token': token,
        'u_ids': u_ids
    }
    return requests.post(f'{url}dm/create/v1', json = pload).json()

def message_send_v1(token, channel_id, message):
    pload = {
            'token': token,
            'channel_id': channel_id,
            'message': message
        }
    return requests.post(f'{url}message/send/v1', json = pload).json()

def message_senddm_v1(token, dm_id, message):
    pload = {
            'token': token,
            'dm_id': dm_id,
            'message': message
        }
    return requests.post(f'{url}message/senddm/v1', json = pload).json()

def search_v1(token, query_str):
    pload = {
        'token': token,
        'query_str': query_str
    }
    response = requests.get(f'{url}search/v1', params = pload)
    assert response.status_code == Success_code
    return response.json()

# Register users and stores their returned dictionaries in the users 
# dictionary.
@pytest.fixture
def set_up_users():
    clear_v1()
    users = {}
    for i in range(1, 4):
        users[f"{i}"] = auth_register_v2(f"name{i}@gmail.com", "password",
            f"person{i}", f"surname{i}"
        )
    return users

# Create a channel given a user, send five messages and return the new channel_id.
def set_up_channel(user):
    new_channel_id = channels_create_v2(user['token'], 'new_channel_1',
        True
    )['channel_id']
    channel_message_ids = {}
    for i in range(1, 6):
        channel_message_ids[f"{i}"] = message_send_v1(user['token'], 
        new_channel_id, f"channel message{i}"
        )['message_id']
    return new_channel_id, channel_message_ids

# Create a dm given a user, send five messages and return the new dm_id.
def set_up_dm(user):
    dm_id = dm_create_v1(user['token'], [user['auth_user_id']])['dm_id']
    dm_message_ids = {}
    for i in range(1, 6):
        dm_message_ids[f"{i}"] = message_senddm_v1(user['token'], dm_id,
            f'dm message{i}'
        )['message_id']
    return dm_id, dm_message_ids

# Test that a list of messages containing an empty query_str is returned.
def test_search_empty_space_string(set_up_users):
    users = set_up_users
    channel_message_ids = set_up_channel(users['1'])[1]
    search_messages = search_v1(users['1']['token'], ' ')
    for i in range(1,6):
        assert channel_message_ids[f'{i}'] == search_messages['messages'] \
            [i - 1]['message_id']

# Test that a list of messages containing an alphanumeric query_str is returned.
def test_search_alphanumerical_string(set_up_users):
    users = set_up_users
    channel_message_ids = set_up_channel(users['1'])[1]
    search_messages = search_v1(users['1']['token'], 'message')
    for i in range(1,6):
        assert channel_message_ids[f'{i}'] == search_messages['messages'] \
            [i - 1]['message_id']

# Test that a list of messages is returned given multiple channels.
def test_search_multiple_channels(set_up_users):
    users = set_up_users
    channel_message_ids_1 = set_up_channel(users['2'])[1]
    channel_message_ids_2 = set_up_channel(users['2'])[1]
    search_messages = search_v1(users['2']['token'], 'message1')
    assert channel_message_ids_1['1'] == search_messages['messages'][0]\
        ['message_id']
    assert channel_message_ids_2['1'] == search_messages['messages'][1]\
        ['message_id']

# Test that a list of messages is returned given multiple dms.
def test_search_multiple_dms(set_up_users):
    users = set_up_users
    dm_message_ids_1 = set_up_dm(users['1'])[1]
    dm_message_ids_2 = set_up_dm(users['1'])[1]
    search_messages = search_v1(users['1']['token'], 'message1')
    assert dm_message_ids_1['1'] == search_messages['messages'][0]\
        ['message_id']
    assert dm_message_ids_2['1'] == search_messages['messages'][1]\
        ['message_id']

# Test that a list of messages is returned given multiple users.
def test_search_multiple_channels_and_users(set_up_users):
    users = set_up_users
    set_up_dm(users['1'])
    message_ids = set_up_dm(users['2'])[1]
    search_messages = search_v1(users['2']['token'], 'message1')
    assert message_ids['1'] == search_messages['messages'][0]\
        ['message_id']

# Test that an Access Error is raised when the token is invalid.
def test_search_invalid_token(set_up_users):
    users = set_up_users
    set_up_channel(users['1'])
    pload = {
        'token': '1',
        'query_str': 'message'
    }
    response = requests.get(f'{url}search/v1', params = pload)
    assert response.status_code == AccessError.code

# Test that an Access Error is raised when the query_str is greater
# than 1000 characters.
def test_search_input_error_greater_than_1000(set_up_users):
    users = set_up_users
    set_up_channel(users['1'])
    pload = {
        'token': users['1']['token'],
        'query_str': "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\
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
    }
    response = requests.get(f'{url}search/v1', params = pload)
    assert response.status_code == InputError.code

# Test that an Access Error is raised when the query_str is less
# than 1 characters.
def test_search_input_error_less_than_1(set_up_users):
    users = set_up_users
    set_up_channel(users['1'])
    pload = {
        'token': users['1']['token'],
        'query_str': ''
    }
    response = requests.get(f'{url}search/v1', params = pload)
    assert response.status_code == InputError.code