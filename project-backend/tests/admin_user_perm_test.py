import pytest
import requests
from src.config import url
from src.error import AccessError, InputError
from src.helper import Success_code

# Fixture sets up a single registered user
@pytest.fixture
def new_user():
    requests.delete(f'{url}clear/v1')
    response = requests.post(f'{url}auth/register/v2', json = {
    'email': 'adamchen@hotmail.com',
    'password': 'jinladen',
    'name_first': 'kyle',
    'name_last': 'jeremy'})
    user = response.json()
    return user

# Fixture sets up multiple registered users
@pytest.fixture
def reg_multi_users():
    requests.delete(f'{url}clear/v1')
    users = {}
    for i in range(1, 4):
        pload = {
            'email': f"{i}@gmail.com", 
            'password': "password", 
            'name_first': f"{i}", 
            'name_last': f"{i}"
        }
        response = requests.post(f'{url}auth/register/v2', json = pload)
        users[f"{i}"] = response.json()
    return users

# Tests for when an invalid u_id is passed
def test_admin_user_permission_change_invalid_user(reg_multi_users):
    user1 = reg_multi_users['1']
    pload = {
        'token': user1['token'],
        'u_id': 100,
        'permission_id': 1
    }
    response = requests.post(f'{url}admin/userpermission/change/v1', json = pload)
    assert response.status_code == InputError.code

# Tests for when an invalid token is passed
def test_admin_user_permission_change_invalid_token(reg_multi_users):
    user1 = reg_multi_users['1']
    requests.post(f'{url}auth/logout/v1', json = {'token': user1['token']})
    pload = {
        'token': user1['token'],
        'u_id': user1['auth_user_id'],
        'permission_id': 1
    }
    response = requests.post(f'{url}admin/userpermission/change/v1', json = pload)
    assert response.status_code == AccessError.code

# Tests for when a non-owner accesses the function
def test_admin_user_permission_change_not_global(reg_multi_users):
    user2 = reg_multi_users['2']
    user3 = reg_multi_users['3']
    pload = {
        'token': user2['token'],
        'u_id': user3['auth_user_id'],
        'permission_id': 1
    }
    response = requests.post(f'{url}admin/userpermission/change/v1', json = pload)
    assert response.status_code == AccessError.code

# Tests for when there is only one global owner
def test_admin_user_permission_change_only_global_1(new_user):
    pload = {
        'token': new_user['token'],
        'u_id': new_user['auth_user_id'],
        'permission_id': 1
    }
    response = requests.post(f'{url}admin/userpermission/change/v1', json = pload)
    assert response.status_code == InputError.code

# Tests for when 
def test_admin_user_permission_change_only_global_success(reg_multi_users):
    user1 = reg_multi_users['1']
    user2 = reg_multi_users['2']
    pload = {
        'token': user1['token'],
        'u_id': user2['auth_user_id'],
        'permission_id': 1
    }
    response = requests.post(f'{url}admin/userpermission/change/v1', json = pload)
    assert response.status_code == Success_code
    assert response.json() == {}

# Tests for when an invalid permission_id is passed (3)
def test_admin_user_permission_change_invalid_perm_3(reg_multi_users):
    user1 = reg_multi_users['1']
    user2 = reg_multi_users['2']
    pload = {
        'token': user1['token'],
        'u_id': user2['auth_user_id'],
        'permission_id': 3
    }
    response = requests.post(f'{url}admin/userpermission/change/v1', json = pload)
    assert response.status_code == InputError.code

# Tests for when an invalid permission_id is passed (0)
def test_admin_user_permission_change_invalid_perm_0(reg_multi_users):
    user1 = reg_multi_users['1']
    user2 = reg_multi_users['2']
    pload = {
        'token': user1['token'],
        'u_id': user2['auth_user_id'],
        'permission_id': 0
    }
    response = requests.post(f'{url}admin/userpermission/change/v1', json = pload)
    assert response.status_code == InputError.code

# Tests for a successful case of changing user permissions
def test_admin_user_permission_change_success(reg_multi_users):
    users = reg_multi_users
    response = requests.post(f'{url}admin/userpermission/change/v1', json = {
        'token': users['1']['token'],
        'u_id': users['2']['auth_user_id'],
        'permission_id': 1
    })
    assert response.status_code == Success_code
    assert response.json() == {}
    response = requests.post(f'{url}admin/userpermission/change/v1', json = {
        'token': users['2']['token'],
        'u_id': users['3']['auth_user_id'],
        'permission_id': 1
    })
    assert response.status_code == Success_code
    assert response.json() == {}
    response = requests.post(f'{url}admin/userpermission/change/v1', json = {
        'token': users['3']['token'],
        'u_id': users['2']['auth_user_id'],
        'permission_id': 2
    })
    assert response.status_code == Success_code
    assert response.json() == {}
    response = requests.post(f'{url}admin/userpermission/change/v1', json = {
        'token': users['3']['token'],
        'u_id': users['3']['auth_user_id'],
        'permission_id': 2
    })
    assert response.status_code == Success_code
    assert response.json() == {}

# Tests that a global owner who owns the channel does not lose their channel 
# permissions when demoted
def test_admin_user_permission_channel_permissions_demoted_is_owner\
    (reg_multi_users):
    users = reg_multi_users

    response = requests.post(f'{url}admin/userpermission/change/v1', json = {
    'token': users['1']['token'],
    'u_id': users['3']['auth_user_id'],
    'permission_id': 1})
    
    assert response.status_code == Success_code
    assert response.json() == {}

    new_channel_id = requests.post(f'{url}channels/create/v2', json = {
    'token': users['1']['token'],
    'name': 'new_channel',
    'is_public': True}).json()['channel_id']

    requests.post(f'{url}channel/join/v2', json = {
    'token': users['2']['token'],
    'channel_id': new_channel_id})

    response = requests.post(f'{url}admin/userpermission/change/v1', json = {
        'token': users['3']['token'],
        'u_id': users['1']['auth_user_id'],
        'permission_id': 2
    })
    
    assert response.status_code == Success_code
    assert response.json() == {}
    
    # Checking that user1 (global owner) still has owner permissions
    response = requests.post(f'{url}channel/addowner/v1', json = {
    'token': users['1']['token'],
    'channel_id': new_channel_id,
    'u_id': users['2']['auth_user_id']})

    assert response.status_code == Success_code

# Tests that a global owner who doesn't own the channel loses their channel 
# permissions when demoted
def test_admin_user_permission_channel_permissions_demoted_not_owner\
    (reg_multi_users):
    users = reg_multi_users

    response = requests.post(f'{url}admin/userpermission/change/v1', json = {
    'token': users['1']['token'],
    'u_id': users['3']['auth_user_id'],
    'permission_id': 1})
    
    assert response.status_code == Success_code
    assert response.json() == {}
    new_channel_id = requests.post(f'{url}channels/create/v2', json = {
    'token': users['2']['token'],
    'name': 'new_channel',
    'is_public': True}).json()['channel_id']

    requests.post(f'{url}channel/join/v2', json = {
    'token': users['1']['token'],
    'channel_id': new_channel_id})

    response = requests.post(f'{url}admin/userpermission/change/v1', json = {
        'token': users['3']['token'],
        'u_id': users['1']['auth_user_id'],
        'permission_id': 2
    })
    
    assert response.status_code == Success_code
    assert response.json() == {}
    
    # Checking that user1 (global owner) does not have owner permissions
    response = requests.post(f'{url}channel/addowner/v1', json = {
    'token': users['1']['token'],
    'channel_id': new_channel_id,
    'u_id': users['1']['auth_user_id']})

    assert response.status_code == AccessError.code

# Tests that a user gains channel permissions when added as owner
def test_admin_user_permission_channel_permissions_promoted(reg_multi_users):
    users = reg_multi_users

    # In the first channel, member is already an owner
    new_channel_id = requests.post(f'{url}channels/create/v2', json = {
    'token': users['1']['token'],
    'name': 'new_channel',
    'is_public': True}).json()['channel_id']

    requests.post(f'{url}channel/join/v2', json = {
    'token': users['2']['token'],
    'channel_id': new_channel_id})

    requests.post(f'{url}channel/addowner/v1', json = {
    'token': users['1']['token'],
    'channel_id': new_channel_id,
    'u_id': users['2']['auth_user_id']})

    # In second channel, member does not have owner permissions
    even_newer_channel_id = requests.post(f'{url}channels/create/v2', json = {
    'token': users['1']['token'],
    'name': 'new_channel',
    'is_public': True}).json()['channel_id']

    requests.post(f'{url}channel/join/v2', json = {
    'token': users['2']['token'],
    'channel_id': even_newer_channel_id})

    response = requests.post(f'{url}admin/userpermission/change/v1', json = {
        'token': users['1']['token'],
        'u_id': users['2']['auth_user_id'],
        'permission_id': 1
    })
    
    assert response.status_code == Success_code
    assert response.json() == {}
    
    # Checking that user1 (global owner) has owner permissions in both channels

    response = requests.post(f'{url}channel/removeowner/v1', json = {
    'token': users['2']['token'],
    'channel_id': new_channel_id,
    'u_id': users['1']['auth_user_id']})

    assert response.status_code == Success_code
    
    response = requests.post(f'{url}channel/addowner/v1', json = {
    'token': users['2']['token'],
    'channel_id': even_newer_channel_id,
    'u_id': users['2']['auth_user_id']})

    assert response.status_code == Success_code





    




    
    