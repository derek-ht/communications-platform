import pytest
import requests
from src.config import url
from src.error import AccessError, InputError
from src.helper import Success_code

# Registers users and stores their returned dictionaries in the users 
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
    
# Test that a message_id is return in a dictionary. 
def test_message_senddm_base(set_up_users):
    users = set_up_users
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
            'token': users['2']['token'],
            'dm_id': dm_id,
            'message': 'Hi'
    }
    response = requests.post(f'{url}message/senddm/v1', json = pload)
    assert response.status_code == Success_code
    message_id_1 = response.json()
    assert message_id_1 == {'message_id' : 1}

# Test that a message_id is return in a dictionary.  This also tests that
# the function can find the correct channel given multiple are created.
def test_message_senddm_multiple_channel(set_up_users):
    users = set_up_users
    pload = {
        'token': users['1']['token'],
        'u_ids': [
            users['1']['auth_user_id'],
            users['2']['auth_user_id']
        ]
    }
    requests.post(f'{url}dm/create/v1', json = pload)
    response = requests.post(f'{url}dm/create/v1', json = pload)
    dm_id = response.json()['dm_id']
    pload = {
            'token': users['2']['token'],
            'dm_id': dm_id,
            'message': 'Hi'
    }
    response = requests.post(f'{url}message/senddm/v1', json = pload)
    message_id_1 = response.json()
    assert message_id_1 == {'message_id' : 1}

# Tests that an input error is raised when the dm_id is invalid.
def test_message_senddm_input_error_invalid_dm(set_up_users):
    users = set_up_users
    pload = {
            'token': users['2']['token'],
            'dm_id': 1,
            'message': 'Hi'
    }
    response = requests.post(f'{url}message/senddm/v1', json = pload)
    assert response.status_code == InputError.code

# Tests that an input error is raised when the message is empty.
def test_message_senddm_input_error_invalid_message_less_than_1(set_up_users):
    users = set_up_users
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
            'token': users['2']['token'],
            'dm_id': dm_id,
            'message': ''
    }
    response = requests.post(f'{url}message/senddm/v1', json = pload)
    assert response.status_code == InputError.code

# Tests that an input error is raised when the message length is greater 
# than 1000.
def test_message_senddm_input_error_invalid_message_greater_than_1000(
    set_up_users
):
    users = set_up_users
    pload = {
        'token': users['1']['token'],
        'u_ids': [
            users['1']['auth_user_id'],
            users['2']['auth_user_id']
        ]
    }
    response = requests.post(f'{url}dm/create/v1', json = pload)
    dm_id = response.json()['dm_id']
    message = \
        "00000000000000000000000000000000000000000000000000000000000000000000\
        000000000000000000000000000000000000000000000000000000000000000000000\
        000000000000000000000000000000000000000000000000000000000000000000000\
        000000000000000000000000000000000000000000000000000000000000000000000\
        000000000000000000000000000000000000000000000000000000000000000000000\
        000000000000000000000000000000000000000000000000000000000000000000000\
        000000000000000000000000000000000000000000000000000000000000000000000\
        000000000000000000000000000000000000000000000000000000000000000000000\
        000000000000000000000000000000000000000000000000000000000000000000000\
        000000000000000000000000000000000000000000000000000000000000000000000\
        000000000000000000000000000000000000000000000000000000000000000000000\
        000000000000000000000000000000000000000000000000000000000000000000000\
        000000000000000000000000000000000000000000000000000000000000000000000\
        000000000000000000000000000000000000000000000000000000000000000000000\
        000000000000000000000000000000000001111"
    pload = {
            'token': users['2']['token'],
            'dm_id': dm_id,
            'message': message
    }
    response = requests.post(f'{url}message/senddm/v1', json = pload)
    assert response.status_code == InputError.code

# Tests that an access error is raised when the user is not a member of the 
# channel.
def test_message_senddm_access_error_not_a_member(set_up_users):
    users = set_up_users
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
            'token': users['3']['token'],
            'dm_id': dm_id,
            'message': 'Hey Friends'
    }
    response = requests.post(f'{url}message/senddm/v1', json = pload)
    assert response.status_code == AccessError.code

# Tests that an access error is raised when the token is inactive.
def test_message_senddm_access_error_inactive_token(set_up_users):
    users = set_up_users
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
        'token': users['2']['token']
    }
    requests.post(f'{url}auth/logout/v1', json = pload)
    pload = {
            'token': users['2']['token'],
            'dm_id': dm_id,
            'message': 'Hey Friends'
    }
    response = requests.post(f'{url}message/senddm/v1', json = pload)
    assert response.status_code == AccessError.code

# Tests that an access error is raised when the token is invalid.
def test_message_senddm_access_error_invalid_token(set_up_users):
    users = set_up_users
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
            'token': '1',
            'dm_id': dm_id,
            'message': 'Hey Friends'
    }
    response = requests.post(f'{url}message/senddm/v1', json = pload)
    assert response.status_code == AccessError.code

# Coverage test which tests the generate_message_id returns a valid id.
def test_message_senddm_generate_message_id(set_up_users):
    users = set_up_users
    pload = {
        'token': users['1']['token'],
        'u_ids': [
            users['1']['auth_user_id'],
            users['2']['auth_user_id']
        ]
    }
    response = requests.post(f'{url}dm/create/v1', json = pload)
    dm_id_1 = response.json()['dm_id']
    response = requests.post(f'{url}dm/create/v1', json = pload)
    dm_id_2 = response.json()['dm_id']
    response = requests.post(f'{url}dm/create/v1', json = pload)
    dm_id_3 = response.json()['dm_id']
    pload = {
            'token': users['1']['token'],
            'dm_id': dm_id_3,
            'message': 'Hey Friends'
    }
    response = requests.post(f'{url}message/senddm/v1', json = pload)
    assert response.status_code == Success_code
    message_id_1 = response.json()
    assert message_id_1 == {'message_id' : 1}
    pload['dm_id'] = dm_id_2 
    response = requests.post(f'{url}message/senddm/v1', json = pload)
    assert response.status_code == Success_code
    message_id_2 = response.json()
    assert message_id_2 == {'message_id' : 2}
    pload['dm_id'] = dm_id_1 
    response = requests.post(f'{url}message/senddm/v1', json = pload)
    assert response.status_code == Success_code
    message_id_2 = response.json()
    assert message_id_2 == {'message_id' : 3}
