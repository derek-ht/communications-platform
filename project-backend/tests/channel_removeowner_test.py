import re
import pytest
import requests
from src.config import url
from src.error import AccessError, InputError
from src.helper import Success_code

# This fixture clears the data and registers 2 users, returning the token of
# the first user and the user_id of the second user
@pytest.fixture
def set_up():
    requests.delete(f'{url}clear/v1')

    user1_token = requests.post(f'{url}auth/register/v2', json = {
    'email': 'history@gmail.com',
    'password': '123456',
    'name_first': 'Adam',
    'name_last': 'Chen'}).json()['token']

    user2 = requests.post(f'{url}auth/register/v2', json = {
    'email': 'kydares@gmail.com',
    'password': 'ilovemyself',
    'name_first': 'Kyle',
    'name_last': 'Wu'}).json()

    user2_id = user2['auth_user_id']
    user2_token = user2['token']

    new_channel_id = requests.post(f'{url}channels/create/v2', json = {
    'token': user1_token,
    'name': 'new_channel',
    'is_public': True}).json()['channel_id']

    requests.post(f'{url}channel/join/v2', json = {
    'token': user2_token,
    'channel_id': new_channel_id})

    return user2_id, user1_token, new_channel_id

# Tests a successful case of adding a member as a channel owner
def test_channel_removeowner_successful(set_up):
    member_id, owner_token, new_channel_id = set_up

    requests.post(f'{url}channel/addowner/v1', json = {
    'token': owner_token,
    'channel_id': new_channel_id,
    'u_id': member_id})

    response = requests.post(f'{url}channel/removeowner/v1', json = {
    'token': owner_token,
    'channel_id': new_channel_id,
    'u_id': member_id})

    assert response.status_code == Success_code
    assert response.json() == {}
    
    channel_owners = requests.get(f'{url}channel/details/v2', params = {
    'token': owner_token,
    'channel_id': new_channel_id}).json()['owner_members']

    is_owner = False
    for member in channel_owners:
        if member['email'] == 'kydares@gmail.com':
            is_owner = True
    assert is_owner == False

# Tests a successful case of removing the creator of the channel as owner
def test_channel_removeowner_original_owner_successful():
    requests.delete(f'{url}clear/v1')

    owner = requests.post(f'{url}auth/register/v2', json = {
    'email': 'history@gmail.com',
    'password': '123456',
    'name_first': 'Adam',
    'name_last': 'Chen'}).json()

    owner_id = owner['auth_user_id']
    owner_token = owner['token']

    member = requests.post(f'{url}auth/register/v2', json = {
    'email': 'kydares@gmail.com',
    'password': 'ilovemyself',
    'name_first': 'Kyle',
    'name_last': 'Wu'}).json()

    member_id = member['auth_user_id']
    member_token = member['token']

    new_channel_id = requests.post(f'{url}channels/create/v2', json = {
    'token': owner_token,
    'name': 'new_channel',
    'is_public': True}).json()['channel_id']

    requests.post(f'{url}channel/join/v2', json = {
    'token': member_token,
    'channel_id': new_channel_id})

    requests.post(f'{url}channel/addowner/v1', json = {
    'token': owner_token,
    'channel_id': new_channel_id,
    'u_id': member_id})

    response = requests.post(f'{url}channel/removeowner/v1', json = {
        'token': member_token,
        'channel_id': new_channel_id,
        'u_id': owner_id})

    assert response.json() == {}
    assert response.status_code == Success_code

    channel_owners = requests.get(f'{url}channel/details/v2', params = {
    'token': owner_token,
    'channel_id': new_channel_id}).json()['owner_members']

    is_owner = False
    for member in channel_owners:
        if member['email'] == 'history1932@gmail.com':
            is_owner = True
    assert is_owner == False

def test_channel_removeowner_removing_global_owner(set_up):
    member_id, owner_token, new_channel_id = set_up

    requests.post(f'{url}channel/addowner/v1', json = {
    'token': owner_token,
    'channel_id': new_channel_id,
    'u_id': member_id})

    member_token = requests.post(f'{url}auth/login/v2', json = {
    'email': 'kydares@gmail.com',
    'password': 'ilovemyself'
    }).json()['token']

    owner_id = requests.post(f'{url}auth/login/v2', json = {
        'email': 'history@gmail.com',
        'password': '123456'
    }).json()['auth_user_id']

    response = requests.post(f'{url}channel/removeowner/v1', json = {
    'token': member_token,
    'channel_id': new_channel_id,
    'u_id': owner_id})

    assert response.status_code == Success_code
    assert response.json() == {}

    # Checking that the global owner has channel_permissions
    response = requests.post(f'{url}channel/addowner/v1', json = {
    'token': owner_token,
    'channel_id': new_channel_id,
    'u_id': owner_id})

    assert response.status_code == Success_code

# The following test for errors

# Tests for when an invalid channel_id is passed
def test_channel_removeowner_invalid_channel_id(set_up):
    member_id, owner_token, new_channel_id = set_up

    requests.post(f'{url}channel/addowner/v1', json = {
    'token': owner_token,
    'channel_id': new_channel_id,
    'u_id': member_id})

    response = requests.post(f'{url}channel/removeowner/v1', json = {
    'token': owner_token,
    'channel_id': new_channel_id + 3,
    'u_id': member_id})

    assert response.status_code == InputError.code

# Tests for when an invalid u_id is passed
def test_channel_removeowner_invalid_u_id(set_up):
    member_id, owner_token, new_channel_id = set_up
    
    requests.post(f'{url}channel/addowner/v1', json = {
    'token': owner_token,
    'channel_id': new_channel_id,
    'u_id': member_id})

    response = requests.post(f'{url}channel/removeowner/v1', json = {
    'token': owner_token,
    'channel_id': new_channel_id,
    'u_id': member_id + 3})

    assert response.status_code == InputError.code

# Tests for when a non-owner member is removed as owner
def test_channel_removeowner_removing_non_owner(set_up):
    member_id, owner_token, new_channel_id = set_up

    response = requests.post(f'{url}channel/removeowner/v1', json = {
    'token': owner_token,
    'channel_id': new_channel_id,
    'u_id': member_id})

    assert response.status_code == InputError.code

# Tests for when u_id is associated with the only owner of the channel
def test_channel_removeowner_u_id_only_owner(set_up):
    member_id, owner_token, new_channel_id = set_up
    
    user_token = requests.post(f'{url}auth/login/v2', json = {
    'email': 'kydares@gmail.com',
    'password': 'ilovemyself'
    }).json()['token']
    
    new_channel_id = requests.post(f'{url}channels/create/v2', json = {
    'token': user_token,
    'name': 'new_channel',
    'is_public': True}).json()['channel_id']    

    requests.post(f'{url}channel/join/v2', json = {
    'token': owner_token,
    'channel_id': new_channel_id})

    response = requests.post(f'{url}channel/removeowner/v1', json = {
    'token': owner_token,
    'channel_id': new_channel_id,
    'u_id': member_id})

    assert response.status_code == InputError.code

# Tests for when the authorized user has no owner permissions
def test_channel_removeowner_no_owner_permissions(set_up):
    member_id, owner_token, new_channel_id = set_up

    requests.post(f'{url}channel/addowner/v1', json = {
    'token': owner_token,
    'channel_id': new_channel_id,
    'u_id': member_id})
    
    non_owner_token = requests.post(f'{url}auth/register/v2', json = {
    'email': 'DerekTran@gmail.com',
    'password': '12345678',
    'name_first': 'Derek',
    'name_last': 'Tran'}).json()['token']

    requests.post(f'{url}channel/join/v2', json = {
    'token': non_owner_token,
    'channel_id': new_channel_id})

    response = requests.post(f'{url}channel/removeowner/v1', json = {
    'token': non_owner_token,
    'channel_id': new_channel_id,
    'u_id': member_id})

    assert response.status_code == AccessError.code

# Tests for when an invalid token is passed
def test_channel_removeowner_invalid_token(set_up):
    member_id, owner_token, new_channel_id = set_up

    requests.post(f'{url}channel/addowner/v1', json = {
    'token': owner_token,
    'channel_id': new_channel_id,
    'u_id': member_id})
    
    response = requests.post(f'{url}channel/removeowner/v1', json = {
    'token': 'invalid_token',
    'channel_id': new_channel_id,
    'u_id': member_id})

    assert response.status_code == AccessError.code

# The following test for when input and access errors should be thrown

# Tests for when the authorized user has no owner permissions and an invalid
# u_id is passed
def test_channel_removeowner_no_owner_permissions_and_invalid_u_id(set_up):
    member_id, owner_token, new_channel_id = set_up
    pload = {
        'token': owner_token,
        'channel_id': new_channel_id,
        'u_id': member_id
    }
    requests.post(f'{url}channel/addowner/v1', json = pload)
    pload = {
        'email': 'DerekTran@gmail.com',
        'password': '12345678',
        'name_first': 'Derek',
        'name_last': 'Tran'
    }
    response = requests.post(f'{url}auth/register/v2', json = pload)
    non_owner_token = response.json()['token']
    pload = {
        'token': non_owner_token,
        'channel_id': new_channel_id
    }
    requests.post(f'{url}channel/join/v2', json = pload)
    pload = {
        'token': non_owner_token,
        'channel_id': new_channel_id,
        'u_id': member_id + 3
    }
    response = requests.post(f'{url}channel/removeowner/v1', json = pload)
    assert response.status_code == AccessError.code
    
def test_channel_removeowner_no_owner_permissions_and_non_owner_u_id(set_up):
    member_id, non_owner_token, new_channel_id = set_up
    pload = {
        'email': 'DerekTran@gmail.com',
        'password': '12345678',
        'name_first': 'Derek',
        'name_last': 'Tran'
    }
    response = requests.post(f'{url}auth/register/v2', json = pload)
    non_owner_token = response.json()['token']
    pload = {
        'token': non_owner_token,
        'channel_id': new_channel_id
    }
    requests.post(f'{url}channel/join/v2', json = pload)
    pload = {
        'token': non_owner_token,
        'channel_id': new_channel_id,
        'u_id': member_id
    }
    response = requests.post(f'{url}channel/removeowner/v1', json = pload)
    assert response.status_code == AccessError.code

# Tests for when the user without owner permissions tries to remove the only
# owner 
def test_channel_removeowner_no_owner_permissions_and_u_id_is_only_owner(set_up):
    owner_id, non_owner_token, new_channel_id = set_up
    pload = {
        'email': 'DerekTran@gmail.com',
        'password': '12345678',
        'name_first': 'Derek',
        'name_last': 'Tran'
    }
    response = requests.post(f'{url}auth/register/v2', json = pload)
    non_owner_token = response.json()['token']
    pload = {
        'email': 'history@gmail.com',
        'password': '123456'
    }
    response = requests.post(f'{url}auth/login/v2', json = pload)
    owner_id = response.json()['auth_user_id']
    requests.post(f'{url}channel/join/v2', json = pload)
    pload = {
        'token': non_owner_token,
        'channel_id': new_channel_id,
        'u_id': owner_id
    }
    response = requests.post(f'{url}channel/removeowner/v1', json = pload)
    assert response.status_code == AccessError.code

# Tests for when an invalid token and an invalid channel_id are passed
def test_channel_removeowner_invalid_token_and_invalid_channel_id(set_up):
    member_id, owner_token, new_channel_id = set_up
    pload = {
        'token': owner_token,
        'channel_id': new_channel_id,
        'u_id': member_id
    }
    requests.post(f'{url}channel/addowner/v1', json = pload)
    pload['token'] = '1'
    pload['channel_id'] = new_channel_id + 3
    response = requests.post(f'{url}channel/removeowner/v1', json = pload)
    assert response.status_code == AccessError.code

# Tests for when an invalid token and an invalid u_id are passed
def test_channel_removeowner_invalid_token_and_invalid_u_id(set_up):
    member_id, owner_token, new_channel_id = set_up
    pload = {
        'token': owner_token,
        'channel_id': new_channel_id,
        'u_id': member_id
    }
    response = requests.post(f'{url}channel/addowner/v1', json = pload)
    pload['token'] = '1'
    pload['u_id'] = member_id + 3
    response = requests.post(f'{url}channel/removeowner/v1', json = pload)
    assert response.status_code == AccessError.code

# Tests for when an invalid token is passed and a non-owner member is removed 
# as owner
def test_channel_removeowner_invalid_token_and_removing_non_owner(set_up):
    member_id, invalid_token, new_channel_id = set_up
    invalid_token = 'invalid_token'
    
    response = requests.post(f'{url}channel/removeowner/v1', json = {
    'token': invalid_token,
    'channel_id': new_channel_id,
    'u_id': member_id})

    assert response.status_code == AccessError.code

# Tests for when an invalid token is passed and the u_id is associated with 
# the only owner of the channel
def test_channel_removeowner_invalid_token_and_u_id_only_owner(set_up):
    member_id, invalid_token, new_channel_id = set_up
    
    member_token = requests.post(f'{url}auth/login/v2', json = {
    'email': 'kydares@gmail.com',
    'password': 'ilovemyself'
    }).json()['token']

    new_channel_id = requests.post(f'{url}channels/create/v2', json = {
    'token': member_token,
    'name': 'new_channel',
    'is_public': True}).json()['channel_id']

    invalid_token = 'invalid_token'

    response = requests.post(f'{url}channel/removeowner/v1', json = {
    'token': invalid_token,
    'channel_id': new_channel_id,
    'u_id': member_id})

    assert response.status_code == AccessError.code