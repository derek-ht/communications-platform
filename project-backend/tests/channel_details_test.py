import pytest
import requests
from src.config import url
from src.error import AccessError, InputError
from src.helper import Success_code

# Register three users and store their returned dictionaries in the users 
# dictionary.
@pytest.fixture
def set_up_users():
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

# Create a channel given a user and return the channel_id.
def set_up_channel(user):
    pload = {
        'token': user['token'],
        'name': 'new_channel_1',
        'is_public': True
    }
    response = requests.post(f'{url}channels/create/v2', json = pload)
    new_channel_id = response.json()['channel_id']
    return new_channel_id

# Test whether the details of a single user are returned correctly.
def test_channel_details_base(set_up_users):
    users = set_up_users
    new_channel_id = set_up_channel(users['1'])
    pload = {
        'token': users['1']['token'],
        'channel_id': new_channel_id
    }
    response = requests.get(f'{url}channel/details/v2', params = pload) 
    assert response.status_code == Success_code
    details = response.json()
    assert details == {
        'name': 'new_channel_1',
        'is_public': True,
        'owner_members': [
            {
                'u_id': users['1']['auth_user_id'], 
                'email': 'name1@gmail.com',
                'name_first': 'person1',
                'name_last': 'surname1',
                'handle_str': 'person1surname1',
            }
        ],
        'all_members': [
            {
                'u_id': users['1']['auth_user_id'], 
                'email': 'name1@gmail.com',
                'name_first': 'person1',
                'name_last': 'surname1',
                'handle_str': 'person1surname1',
            }
        ],
    }

# Test whether the details of multiple users are returned correctly.
def test_channel_details_multiple_users(set_up_users):
    users = set_up_users
    new_channel_id = set_up_channel(users['1'])
    pload = {
        'token': users['2']['token'],
        'channel_id': new_channel_id
    }
    requests.post(f'{url}channel/join/v2', json = pload)
    response = requests.get(f'{url}channel/details/v2', params = pload) 
    assert response.status_code == Success_code
    details = response.json()
    assert details == {
        'name': 'new_channel_1',
        'is_public': True,
        'owner_members': [
            {
                'u_id': users['1']['auth_user_id'], 
                'email': 'name1@gmail.com',
                'name_first': 'person1',
                'name_last': 'surname1',
                'handle_str': 'person1surname1',
            }
        ],
        'all_members': [
            {
                'u_id': users['1']['auth_user_id'], 
                'email': 'name1@gmail.com',
                'name_first': 'person1',
                'name_last': 'surname1',
                'handle_str': 'person1surname1',
            },
            {
                'u_id': users['2']['auth_user_id'], 
                'email': 'name2@gmail.com',
                'name_first': 'person2',
                'name_last': 'surname2',
                'handle_str': 'person2surname2',
            }
        ],
    }
    
# Test that the details of a single channel is returned given multiple channels
# are created.
def test_channel_details_multiple_channels(set_up_users):
    users = set_up_users 
    set_up_channel(users['1'])
    new_channel_id = set_up_channel(users['2'])
    pload = {
        'token': users['2']['token'],
        'channel_id': new_channel_id
    }
    response = requests.get(f'{url}channel/details/v2', params = pload) 
    assert response.status_code == Success_code
    details = response.json()
    assert details == {
        'name': 'new_channel_1',
        'is_public': True,
        'owner_members': [
            {
                'u_id': users['2']['auth_user_id'], 
                'email': 'name2@gmail.com',
                'name_first': 'person2',
                'name_last': 'surname2',
                'handle_str': 'person2surname2',
            }
        ],
        'all_members': [
            {
                'u_id': users['2']['auth_user_id'], 
                'email': 'name2@gmail.com',
                'name_first': 'person2',
                'name_last': 'surname2',
                'handle_str': 'person2surname2',
            }
        ],
    }   

# Test whether an input error is raised when a non-zero invalid channel_id 
# is called.
def test_channel_details_input_error(set_up_users):
    users = set_up_users
    pload = {
        'token': users['1']['token'],
        'channel_id': 10
    }
    response = requests.get(f'{url}channel/details/v2', params = pload) 
    assert response.status_code == InputError.code

# Test whether an input error is raised when a zero invalid channel_id 
# is called.
def test_channel_details_input_error_zero(set_up_users):
    users = set_up_users
    pload = {
        'token': users['1']['token'],
        'channel_id': 0
    }
    response = requests.get(f'{url}channel/details/v2', params = pload) 
    assert response.status_code == InputError.code

# Test that an access error is raised when the user is not a member of the 
# channel.
def test_channel_details_access_error_channel_id(set_up_users):
    users = set_up_users
    new_channel_id = set_up_channel(users['1'])
    pload = {
            'token': users['2']['token'],
            'channel_id': new_channel_id
    }
    response = requests.get(f'{url}channel/details/v2', params = pload) 
    assert response.status_code == AccessError.code

# Test that an access error is raised when the token is inactive.
def test_channel_details_access_error_inactive_token(set_up_users):
    users = set_up_users
    new_channel_id = set_up_channel(users['1'])
    pload = {
        'token': users['1']['token'],
    }
    requests.post(f'{url}auth/logout/v1', json = pload) 
    pload = {
        'token': users['1']['token'],
        'channel_id': new_channel_id
    }
    response = requests.get(f'{url}channel/details/v2', params = pload) 
    assert response.status_code == AccessError.code

# Test that an access error is raised when the token is invalid.
def test_channel_details_access_error_invalid_token(set_up_users):
    users = set_up_users
    new_channel_id = set_up_channel(users['1'])
    pload = {
        'token': '1',
        'channel_id': new_channel_id
    }
    response = requests.get(f'{url}channel/details/v2', params = pload) 
    assert response.status_code == AccessError.code
