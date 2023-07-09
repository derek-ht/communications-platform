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

# Tests that the details of a single user are displayed in a list
def test_user_profile_base(set_up):
    users = set_up
    pload = {
        'token': users['1']['token'],
        'u_id': users['1']['auth_user_id']
    }
    response = requests.get(f'{url}user/profile/v1', params = pload)
    assert response.status_code == Success_code
    profile = response.json()
    assert profile == {
        'user': {
            'u_id': users['1']['auth_user_id'],
            'email': 'name1@gmail.com',
            'name_first': 'person1',
            'name_last': 'surname1',
            'handle_str': 'person1surname1',
            'profile_img_url': DEFAULT_IMG_URL}
    }
        
# Tests that an access error is raised when the token is inactive
def test_user_profile_inactive_token(set_up):
    users = set_up
    pload = {
        'token': users['1']['token']
    }
    requests.post(f'{url}auth/logout/v1', json = pload)
    pload = {
        'token': users['1']['auth_user_id'],
        'u_id': users['1']['auth_user_id']
    }
    response = requests.get(f'{url}user/profile/v1', params = pload)
    assert response.status_code == AccessError.code

# Tests that an access error is raised when the token is invalid
def test_user_profile_invalid_token(set_up):
    users = set_up
    pload = {
        'token': '1',
        'u_id': users['1']['auth_user_id']
    }
    response = requests.get(f'{url}user/profile/v1', params = pload)
    assert response.status_code == AccessError.code

# Tests that an access error is raised when the user_id is invalid
def test_user_profile_invalid_u_id(set_up):
    users = set_up
    pload = {
        'token': users['1']['token'],
        'u_id': -1
    }
    response = requests.get(f'{url}user/profile/v1', params = pload)
    assert response.status_code == InputError.code

# Tests that an access error is raised when the token and user_id are invalid
def test_user_profile_invalid_both():
    pload = {
        'token': '1',
        'u_id': -1
    }
    response = requests.get(f'{url}user/profile/v1', params = pload)
    assert response.status_code == AccessError.code



