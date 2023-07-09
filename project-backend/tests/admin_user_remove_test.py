import pytest
import requests
from src.config import url
from src.error import AccessError, InputError
from src.helper import Success_code

# Fixture sets up 2 registered users
@pytest.fixture()
def set_up_owner():
    requests.delete(f'{url}clear/v1')
    pload = {
        'email': 'history1932@gmail.com', 
        'password': '123456', 
        'name_first': 'Adam', 
        'name_last': 'Chen'
    }
    response = requests.post(f'{url}auth/register/v2', json = pload)
    owner_token = response.json()['token']
    pload = {
        'email': 'kydares@gmail.com', 
        'password': 'ilovemyself', 
        'name_first': 'Kyle', 
        'name_last': 'Wu'
    }
    response = requests.post(f'{url}auth/register/v2', json = pload)
    user_id = response.json()['auth_user_id']
    return user_id, owner_token

# Tests for a standard case of removing a user
def test_admin_user_remove_successfully_removed_no_session():
    requests.delete(f'{url}clear/v1')
    pload = {
        'email': 'history1932@gmail.com', 
        'password': '123456', 
        'name_first': 'Adam', 
        'name_last': 'Chen'
    }
    response = requests.post(f'{url}auth/register/v2', json = pload)
    owner_token = response.json()['token']
    pload = {
        'email': 'kydares@gmail.com', 
        'password': 'ilovemyself', 
        'name_first': 'Kyle', 
        'name_last': 'Wu'
    }
    response = requests.post(f'{url}auth/register/v2', json = pload)
    user = response.json()
    user_id = user['auth_user_id']
    user_token = user['token']
    requests.post(f'{url}auth/logout/v1', json = {'token': user_token})
    pload = {
        'token': owner_token,
        'u_id': user_id
    }
    response = requests.delete(f'{url}admin/user/remove/v1', json = pload)
    assert response.status_code == Success_code
    assert response.json() == {}
    assert response.json() == {}
    # Checking that the user is removed from streams
    is_user = False
    pload = {
        'token': owner_token
    }
    response = requests.get(f'{url}users/all/v1', params = pload)
    all_users = response.json()['users']
    for user in all_users:
        if user['email'] == 'kydares@gmail.com':
            is_user = True
    assert is_user == False

# Tests for when a user is removed while in a session
def test_admin_user_remove_successfully_removed_user_in_sessions(set_up_owner):
    pload = {
        'email': 'kydares@gmail.com',
        'password': 'ilovemyself'
    }
    requests.post(f'{url}auth/login/v2', json = pload)
    user_id, owner_token = set_up_owner
    pload = {
        'token': owner_token,
        'u_id': user_id
    }
    response = requests.delete(f'{url}admin/user/remove/v1', json = pload)
    assert response.status_code == Success_code
    assert response.json() == {}
    # Checking that the user is removed from streams
    is_user = False
    pload = {
        'token': owner_token
    }
    response = requests.get(f'{url}users/all/v1', params = pload)
    all_users = response.json()['users']
    for user in all_users:
        if user['email'] == 'kydares@gmail.com':
            is_user = True
    assert is_user == False 

# Tests that the user is removed from the channel and that their messages are
# changed to 'Removed user'
def test_admin_user_remove_removed_from_channel(set_up_owner):
    user_id, owner_token = set_up_owner
    pload = {
        'token': owner_token,
        'name': 'new_channel',
        'is_public': True
    }
    response = requests.post(f'{url}channels/create/v2', json = pload)
    channel_id = response.json()['channel_id']
    pload = {
        'email': 'kydares@gmail.com',
        'password': 'ilovemyself'
    }
    response = requests.post(f'{url}auth/login/v2', json = pload)
    user_token = response.json()['token']
    pload = {
        'token': user_token,
        'channel_id': channel_id
    }
    requests.post(f'{url}channel/join/v2', json = pload)
    for message_count in range(0, 76):
        if message_count % 15 == 0:
            pload = {
                'token': user_token,
                'channel_id': channel_id,
                'message': 'Hello guys'
            }
            requests.post(f'{url}message/send/v1', json = pload)
        else:
            pload = {
                'token': owner_token,
                'channel_id': channel_id,
                'message': 'LOLOLOL'
            }
            requests.post(f'{url}message/send/v1', json = pload)
    pload = {
        'token': owner_token,
        'u_id': user_id
    }
    response = requests.delete(f'{url}admin/user/remove/v1', json = pload)
    assert response.status_code == Success_code
    assert response.json() == {}
    # Checking that the content of the user's messages are replaced with
    # 'Removed user'
    pload = {
        'token': owner_token,
        'channel_id': channel_id,
        'start': 0
    }
    response = requests.get(f'{url}channel/messages/v2', params = pload)
    channel_messages = response.json()['messages']
    for i in range(0,50):
        if i % 15 == 0:
            assert channel_messages[i]['message'] == 'Removed user'
        else:
            assert channel_messages[i]['message'] == 'LOLOLOL'
    pload = {
        'token': owner_token,
        'channel_id': channel_id,
        'start': 50
    }
    response = requests.get(f'{url}channel/messages/v2', params = pload)
    channel_messages = response.json()['messages']
    assert channel_messages[10]['message'] == 'Removed user'
    assert channel_messages[25]['message'] == 'Removed user'
    # Checking that the user is removed from channel
    pload = {
        'token': owner_token,
        'channel_id': channel_id
    }
    response = requests.get(f'{url}channel/details/v2', params = pload)
    channel_members = response.json()['all_members']
    is_member = False
    for member in channel_members:
        if member['email'] == 'kydares@gmail.com':
            is_member = True
    assert is_member == False

# Tests that the user is removed from the dm and that their messages are
# changed to 'Removed user'
def test_admin_user_removed_from_dms(set_up_owner):
    user_id, owner_token = set_up_owner
    pload = {
        'token': owner_token,
        'u_ids': [user_id]
    }
    response = requests.post(f'{url}dm/create/v1', json = pload)
    dm_id = response.json()['dm_id']
    pload = {
        'email': 'kydares@gmail.com',
        'password': 'ilovemyself'
    }
    response = requests.post(f'{url}auth/login/v2', json = pload)
    user_token = response.json()['token']
    for message_count in range(0, 76):
        if message_count % 15 == 0:
            pload = {
                'token': user_token,
                'dm_id': dm_id,
                'message': 'Hello guys'
            }
            requests.post(f'{url}message/senddm/v1', json = pload)
        else:
            pload = {
                'token': owner_token,
                'dm_id': dm_id,
                'message': 'LOLOLOL'
            }
            requests.post(f'{url}message/senddm/v1', json = pload)
    pload = {
        'token': owner_token,
        'u_id': user_id
    }
    response = requests.delete(f'{url}admin/user/remove/v1', json = pload)
    assert response.status_code == Success_code
    assert response.json() == {}
    # Checking that the content of the user's messages are replaced with
    # 'Removed user'
    pload = {
        'token': owner_token,
        'dm_id': dm_id,
        'start': 0
    }
    response = requests.get(f'{url}dm/messages/v1', params = pload)
    dm_messages = response.json()['messages']

    for i in range(0,50):
        if i % 15 == 0:
            assert dm_messages[i]['message'] == 'Removed user'
        else:
            assert dm_messages[i]['message'] == 'LOLOLOL'

    pload = {
        'token': owner_token,
        'dm_id': dm_id,
        'start': 50
    }
    response = requests.get(f'{url}dm/messages/v1', params = pload)
    dm_messages = response.json()['messages']
    assert dm_messages[10]['message'] == 'Removed user'
    assert dm_messages[25]['message'] == 'Removed user'
    # Checking that the user is removed from DMs

    pload = {
        'token': owner_token,
        'dm_id': dm_id,
    }
    response = requests.get(f'{url}dm/details/v1', params = pload)
    dm_members = response.json()['members']
    is_member = False
    for member in dm_members:
        if member['email'] == 'kydares@gmail.com':
            is_member = True
    assert is_member == False
    
# Tests that the user's name is changed to 'Removed user'
def test_admin_user_remove_name_change(set_up_owner):
    user_id, owner_token = set_up_owner
    pload = {
        'token': owner_token,
        'u_id': user_id
    }
    response = requests.delete(f'{url}admin/user/remove/v1', json = pload)
    assert response.status_code == Success_code
    assert response.json() == {}
    
    # Checking that the user's profile is the same except for the first
    # and last names
    pload = {
        'token': owner_token,
        'u_id': user_id
    }
    response = requests.get(f'{url}user/profile/v1', params = pload)
    user = response.json()['user']
    assert user['name_first'] == 'Removed'
    assert user['name_last'] == 'user'

# Tests that the user's handle and email are reusable
def test_admin_user_remove_reusing_handle_and_email(set_up_owner):
    user_id, owner_token = set_up_owner
    pload = {
        'token': owner_token,
        'u_id': user_id
    }
    response = requests.delete(f'{url}admin/user/remove/v1', json = pload)
    assert response.status_code == Success_code
    assert response.json() == {}
    pload = {
        'token': owner_token,
        'u_id': user_id
    }
    response = requests.get(f'{url}user/profile/v1', params = pload)    
    user = response.json()['user']
    user_handle = user['handle_str']
    # Checking that the user's email and handle are reusable
    pload = {
        'email': 'kydares@gmail.com', 
        'password': 'ilovemyself', 
        'name_first': 'Kyle', 
        'name_last': 'Wu'
    }
    response = requests.post(f'{url}auth/register/v2', json = pload)
    new_user_id = response.json()['auth_user_id']
    pload = {
        'token': owner_token,
        'u_id': new_user_id
    }
    response = requests.get(f'{url}user/profile/v1', params = pload) 
    new_user = response.json()['user']
    assert new_user['handle_str'] == user_handle
    assert new_user['email'] == 'kydares@gmail.com'

# Tests that the removed user can't log in using their email and password
def test_admin_user_remove_invalid_login(set_up_owner):
    user_id, owner_token = set_up_owner
    pload = {
        'token': owner_token,
        'u_id': user_id
    }
    response = requests.delete(f'{url}admin/user/remove/v1', json = pload)
    assert response.status_code == Success_code
    assert response.json() == {}
    pload = {
        'email': 'kydares@gmail.com',
        'password': 'ilovemyself'
    }
    # Checking that the user cannot log back in
    response = requests.post(f'{url}/auth/login/v2', json = pload)
    assert response.status_code == InputError.code

# The following test for errors

# Invalid token is passed
def test_admin_user_remove_invalid_token_after_removing(set_up_owner):
    user_id, owner_token = set_up_owner
    pload = {
        'email': 'kydares@gmail.com',
        'password': 'ilovemyself'
    }
    response = requests.post(f'{url}auth/login/v2', json = pload)
    user_token = response.json()['token']
    pload = {
        'email': 'history1932@gmail.com',
        'password': '123456'
    }
    response = requests.post(f'{url}auth/login/v2', json = pload)
    owner_id = response.json()['auth_user_id']

    pload = {
        'token': owner_token,
        'u_id': user_id
    }
    response = requests.delete(f'{url}admin/user/remove/v1', json = pload)
    assert response.status_code == Success_code
    assert response.json() == {}  
    pload = {
        'token': user_token,
        'u_ids': [user_id, owner_id]
    }
    response = requests.post(f'{url}dm/create/v1', json = pload)    
    assert response.status_code == AccessError.code

# Tests for when an invalid u_id is passed
def test_admin_user_remove_invalid_u_id(set_up_owner):
    user_id, owner_token = set_up_owner
    pload = {
        'token': owner_token,
        'u_id': user_id + 3
    }
    response = requests.delete(f'{url}admin/user/remove/v1', json = pload)
    assert response.status_code == InputError.code 

# Tests for when u_id refers to the only owner
# In other words, when the owner removes themself
def test_admin_user_remove_only_global_owner():
    requests.delete(f'{url}clear/v1')
    pload = {
        'email': 'history1932@gmail.com', 
        'password': '123456', 
        'name_first': 'Adam', 
        'name_last': 'Chen'
    }
    response = requests.post(f'{url}auth/register/v2', json = pload)
    owner_id = response.json()['auth_user_id']
    pload = {
        'email': 'history1932@gmail.com',
        'password': '123456'
    }
    response = requests.post(f'{url}auth/login/v2', json = pload)
    owner_token = response.json()['token']
    pload = {
        'token': owner_token,
        'u_id': owner_id
    }
    response = requests.delete(f'{url}admin/user/remove/v1', json = pload)
    assert response.status_code == InputError.code

# Tests for when the authorised user is not a global owner
def test_admin_user_remove_auth_is_not_global_owner():
    requests.delete(f'{url}clear/v1')
    pload = {
        'email': 'history1932@gmail.com', 
        'password': '123456', 
        'name_first': 'Adam', 
        'name_last': 'Chen'
    }
    response = requests.post(f'{url}auth/register/v2', json = pload)
    owner_id = response.json()['auth_user_id']
    pload = {
        'email': 'kydares@gmail.com', 
        'password': 'ilovemyself', 
        'name_first': 'Kyle', 
        'name_last': 'Wu'
    }
    response = requests.post(f'{url}auth/register/v2', json = pload)
    pload = {
        'email': 'kydares@gmail.com',
        'password': 'ilovemyself'
    }
    response = requests.post(f'{url}auth/login/v2', json = pload)
    user_token = response.json()['token']
    pload = {
        'token': user_token,
        'u_id': owner_id
    }
    response = requests.delete(f'{url}admin/user/remove/v1', json = pload)
    assert response.status_code == AccessError.code

# Tests for when an invalid token is passed  
def test_admin_user_remove_invalid_token(set_up_owner):
    user_id, owner_token = set_up_owner
    pload = {
        'token': owner_token + 'abc',
        'u_id': user_id
    }
    response = requests.delete(f'{url}admin/user/remove/v1', json = pload)
    assert response.status_code == AccessError.code

# Tests for when the authorized user is not a global owner and an invalid
# u_id is passed
def test_admin_user_remove_auth_is_not_global_owner_and_invalid_u_id():
    requests.delete(f'{url}clear/v1')

    pload = {
        "email": "history@gmail.com",
        "password": "123456",
        "name_first": "Adam",
        "name_last": "Chen"
    }
    response = requests.post(url + "auth/register/v2", json = pload)
    owner_id = response.json()['auth_user_id']

    pload = {
        "email": 'kydares@gmail.com',
        "password": 'ilovemyself',
        "name_first": "Kyle",
        "name_last": "Wu"
    }
    requests.post(url + "auth/register/v2", json = pload)

    pload = {
        "email": 'kydares@gmail.com',
        "password": 'ilovemyself'
    }
    response = requests.post(url + "auth/login/v2", json = pload)
    user_token = response.json()['token']

    pload = {
        "token": user_token,
        "u_id": owner_id + 3
    }
    response = requests.delete(url + "admin/user/remove/v1", json = pload)
    assert response.status_code == AccessError.code

# Tests for an invalid token and an invalid u_id are passed
def test_admin_user_remove_invalid_token_and_invalid_u_id(set_up_owner):
    user_id, invalid_token = set_up_owner
    invalid_token = 'invalid_token'
    pload = {
        "token": invalid_token,
        "u_id": user_id + 3
    }
    response = requests.delete(url + "admin/user/remove/v1", json = pload)
    assert response.status_code == AccessError.code