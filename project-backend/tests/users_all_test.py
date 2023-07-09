import pytest
import requests
from src.config import url
from src.error import AccessError, InputError
from src.helper import Success_code, DEFAULT_IMG_URL

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

# Tests that the details of a single user are displayed in a list.
def test_users_all_single():
    requests.delete(f'{url}clear/v1')
    pload = {
        'email': 'name1@gmail.com',
        'password': 'password',
        'name_first': 'person1',
        'name_last': 'surname1'
    }
    response = requests.post(f'{url}auth/register/v2', json = pload)
    user = response.json()
    pload = {
        'token': user['token']
    }
    response = requests.get(f'{url}users/all/v1', params = pload)
    users = response.json()
    assert users == {
        'users': [
            {
                'u_id': user['auth_user_id'],
                'email': 'name1@gmail.com',
                'name_first': 'person1',
                'name_last': 'surname1',
                'handle_str': 'person1surname1',
                'profile_img_url': DEFAULT_IMG_URL
            },
        ]}

# Tests that the details of a multiple user are displayed in a list.
def test_users_all_multiple(set_up):
    users = set_up
    pload = {
        'token': users['1']['token']
    }
    response = requests.get(f'{url}users/all/v1', params = pload)
    users_profile = response.json()
    assert users_profile == {
        'users': [
            {
                'u_id': users['1']['auth_user_id'],
                'email': 'name1@gmail.com',
                'name_first': 'person1',
                'name_last': 'surname1',
                'handle_str': 'person1surname1',
                'profile_img_url': DEFAULT_IMG_URL
            },
            {
                'u_id': users['2']['auth_user_id'],
                'email': 'name2@gmail.com',
                'name_first': 'person2',
                'name_last': 'surname2',
                'handle_str': 'person2surname2',
                'profile_img_url': DEFAULT_IMG_URL
            },
            {
                'u_id': users['3']['auth_user_id'],
                'email': 'name3@gmail.com',
                'name_first': 'person3',
                'name_last': 'surname3',
                'handle_str': 'person3surname3',
                'profile_img_url': DEFAULT_IMG_URL
            }
        ]}

# Tests that an access error is raised when the token is inactive.
def test_users_all_inactive_token(set_up):
    users = set_up
    pload = {
        'token': users['1']['token']
    }
    requests.post(f'{url}auth/logout/v1', json = pload)
    response = requests.get(f'{url}users/all/v1', params = pload)
    assert response.status_code == AccessError.code

# Tests that an access error is raised when the token is invalid
def test_users_all_invalid_token():
    pload = {
        'token': '1'
    }
    response = requests.get(f'{url}users/all/v1', params = pload)
    assert response.status_code == AccessError.code
