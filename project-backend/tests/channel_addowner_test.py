import pytest
import requests
from src.config import url
from src.error import AccessError, InputError
from src.helper import Success_code

@pytest.fixture
def set_up():
    requests.delete(f'{url}clear/v1')

    owner_token = requests.post(f'{url}auth/register/v2', json = {
    'email': 'history@gmail.com',
    'password': '123456',
    'name_first': 'Adam',
    'name_last': 'Chen'}).json()['token']

    user_id = requests.post(f'{url}auth/register/v2', json = {
    'email': 'kydares@gmail.com',
    'password': 'ilovemyself',
    'name_first': 'Kyle',
    'name_last': 'Wu'}).json()['auth_user_id']

    new_channel_id = requests.post(f'{url}channels/create/v2', json = {
    'token': owner_token,
    'name': 'new_channel',
    'is_public': True}).json()['channel_id']

    return user_id, owner_token, new_channel_id

# Tests a successful case of adding a member as a channel owner
def test_channel_addowner_successful(set_up):
    member_id, owner_token, new_channel_id = set_up

    user_token = requests.post(f'{url}auth/login/v2', json = {
        'email': 'kydares@gmail.com',
        'password': 'ilovemyself'
    }).json()['token']

    requests.post(f'{url}channel/join/v2', json = {
    'token': user_token,
    'channel_id': new_channel_id})

    response = requests.post(f'{url}channel/addowner/v1', json = {
    'token': owner_token,
    'channel_id': new_channel_id,
    'u_id': member_id})

    assert response.json() == {}
    assert response.status_code == Success_code

    channel_owners = requests.get(f'{url}channel/details/v2', params = {
    'token': owner_token,
    'channel_id': new_channel_id}).json()['owner_members']

    is_owner = False
    for member in channel_owners:
        if member['email'] == 'kydares@gmail.com':
            is_owner = True
    assert is_owner == True

# A global owner adding themselves as an owner
def test_channel_addowner_global_owner_adding_themself_as_owner(set_up):
    member_id, owner_token, new_channel_id = set_up

    owner_id = requests.post(f'{url}auth/login/v2', json = {
        'email': 'history@gmail.com',
        'password': '123456'
    }).json()['auth_user_id']

    requests.post(f'{url}channel/invite/v2', json = {
    'token': owner_token,
    'channel_id': new_channel_id,
    'u_id': member_id})

    requests.post(f'{url}channel/leave/v1', json = {
    'token': owner_token,
    'channel_id': new_channel_id
    })

    requests.post(f'{url}channel/join/v2', json = {
    'token': owner_token,
    'channel_id': new_channel_id})

    response = requests.post(f'{url}channel/addowner/v1', json = {
    'token': owner_token,
    'channel_id': new_channel_id,
    'u_id': owner_id})

    assert response.json() == {}
    assert response.status_code == Success_code

    channel_owners = requests.get(f'{url}channel/details/v2', params = {
    'token': owner_token,
    'channel_id': new_channel_id}).json()['owner_members']

    is_owner = False
    for member in channel_owners:
        if member['email'] == 'history@gmail.com':
            is_owner = True
    assert is_owner == True

# The following test for errors

# Tests when an invalid channel_id is passed
def test_channel_addowner_invalid_channel_id(set_up):
    member_id, owner_token, new_channel_id = set_up

    user_token = requests.post(f'{url}auth/login/v2', json = {
        'email': 'kydares@gmail.com',
        'password': 'ilovemyself'
    }).json()['token']
    
    requests.post(f'{url}channel/join/v2', json = {
    'token': user_token,
    'channel_id': new_channel_id})

    response = requests.post(f'{url}channel/addowner/v1', json = {
    'token': owner_token,
    'channel_id': new_channel_id + 3,
    'u_id': member_id})

    assert response.status_code == InputError.code

# Tests when an invalid u_id is passed
def test_channel_addowner_invalid_u_id(set_up):
    member_id, owner_token, new_channel_id = set_up

    user_token = requests.post(f'{url}auth/login/v2', json = {
    'email': 'kydares@gmail.com',
    'password': 'ilovemyself'
    }).json()['token']
    
    requests.post(f'{url}channel/join/v2', json = {
    'token': user_token,
    'channel_id': new_channel_id})

    response = requests.post(f'{url}channel/addowner/v1', json = {
    'token': owner_token,
    'channel_id': new_channel_id,
    'u_id': member_id + 3})

    assert response.status_code == InputError.code
    
# Tests when a non_member tries to get added as owner
def test_channel_addowner_non_member(set_up):
    member_id, owner_token, new_channel_id = set_up

    response = requests.post(f'{url}channel/addowner/v1', json = {
    'token': owner_token,
    'channel_id': new_channel_id,
    'u_id': member_id})

    assert response.status_code == InputError.code

# Tests when an owner tries to be added as an owner
def test_channel_addowner_already_owner(set_up):
    member_id, owner_token, new_channel_id = set_up
    
    user_token = requests.post(f'{url}auth/login/v2', json = {
    'email': 'kydares@gmail.com',
    'password': 'ilovemyself'
    }).json()['token']    

    requests.post(f'{url}channel/join/v2', json = {
    'token': user_token,
    'channel_id': new_channel_id})

    requests.post(f'{url}channel/addowner/v1', json = {
    'token': owner_token,
    'channel_id': new_channel_id,
    'u_id': member_id})

    response = requests.post(f'{url}channel/addowner/v1', json = {
    'token': owner_token,
    'channel_id': new_channel_id,
    'u_id': member_id})

    assert response.status_code == InputError.code

# Tests when a non-owner tries to add another member as an owner
def test_channel_addowner_not_owner(set_up):
    member_id, non_owner_token, new_channel_id = set_up
    
    user_token = requests.post(f'{url}auth/login/v2', json = {
    'email': 'kydares@gmail.com',
    'password': 'ilovemyself'
    }).json()['token']    

    non_owner_token = requests.post(f'{url}auth/register/v2', json = {
    'email': 'DerekTran@gmail.com',
    'password': '12345678',
    'name_first': 'Derek',
    'name_last': 'Tran'}).json()['token']

    requests.post(f'{url}channel/join/v2', json = {
    'token': non_owner_token,
    'channel_id': new_channel_id})
    
    requests.post(f'{url}channel/join/v2', json = {
    'token': user_token,
    'channel_id': new_channel_id})
    
    response = requests.post(f'{url}channel/addowner/v1', json = {
    'token': non_owner_token,
    'channel_id': new_channel_id,
    'u_id': member_id})

    assert response.status_code == AccessError.code

# Tests when an invalid token is passed
def test_channel_addowner_invalid_token(set_up):
    member_id, invalid_token, new_channel_id = set_up
    
    user_token = requests.post(f'{url}auth/login/v2', json = {
    'email': 'kydares@gmail.com',
    'password': 'ilovemyself'
    }).json()['token']
    
    requests.post(f'{url}channel/join/v2', json = {
    'token': user_token,
    'channel_id': new_channel_id})

    invalid_token = 'invalid_token'

    response = requests.post(f'{url}channel/addowner/v1', json = {
    'token': invalid_token,
    'channel_id': new_channel_id,
    'u_id': member_id})

    assert response.status_code == AccessError.code

# The following test for when Input and Access Errors are implied

# Tests when a non-owner tries to add another member as an owner and when 
# an invalid u_id is passed
def test_channel_addowner_not_owner_and_invalid_u_id(set_up):
    member_id, non_owner_token, new_channel_id = set_up
    
    user_token = requests.post(f'{url}auth/login/v2', json = {
    'email': 'kydares@gmail.com',
    'password': 'ilovemyself'
    }).json()['token']
    
    requests.post(f'{url}channel/join/v2', json = {
    'token': user_token,
    'channel_id': new_channel_id})

    non_owner_token = requests.post(f'{url}auth/register/v2', json = {
    'email': 'DerekTran@gmail.com',
    'password': '12345678',
    'name_first': 'Derek',
    'name_last': 'Tran'}).json()['token']

    requests.post(f'{url}channel/join/v2', json = {
    'token': non_owner_token,
    'channel_id': new_channel_id})
    
    response = requests.post(f'{url}channel/addowner/v1', json = {
    'token': non_owner_token,
    'channel_id': new_channel_id,
    'u_id': member_id + 5})

    assert response.status_code == AccessError.code

# Tests when a non-owner tries to add another non-owner member as an owner
def test_channel_addowner_not_owner_and_non_member(set_up):
    non_member_id, non_owner_token, new_channel_id = set_up

    non_owner_token = requests.post(f'{url}auth/register/v2', json = {
    'email': 'DerekTran@gmail.com',
    'password': '12345678',
    'name_first': 'Derek',
    'name_last': 'Tran'}).json()['token']
    
    requests.post(f'{url}channel/join/v2', json = {
    'token': non_owner_token,
    'channel_id': new_channel_id})
    
    response = requests.post(f'{url}channel/addowner/v1', json = {
    'token': non_owner_token,
    'channel_id': new_channel_id,
    'u_id': non_member_id})

    assert response.status_code == AccessError.code

# Tests when a non-owner tries to add an owner as an owner
def test_channel_addowner_not_owner_and_already_owner(set_up):
    member_id, owner_token, new_channel_id = set_up

    member_token = requests.post(f'{url}auth/login/v2', json = {
    'email': 'kydares@gmail.com',
    'password': 'ilovemyself'
    }).json()['token']

    non_owner_token = requests.post(f'{url}auth/register/v2', json = {
    'email': 'DerekTran@gmail.com',
    'password': '12345678',
    'name_first': 'Derek',
    'name_last': 'Tran'}).json()['token']

    requests.post(f'{url}channel/join/v2', json = {
    'token': non_owner_token,
    'channel_id': new_channel_id})
    
    requests.post(f'{url}channel/join/v2', json = {
    'token': member_token,
    'channel_id': new_channel_id})
    
    requests.post(f'{url}channel/addowner/v1', json = {
    'token': owner_token,
    'channel_id': new_channel_id,
    'u_id': member_id})

    response = requests.post(f'{url}channel/addowner/v1', json = {
    'token': non_owner_token,
    'channel_id': new_channel_id,
    'u_id': member_id})

    assert response.status_code == AccessError.code

# Tests when an invalid token and an invalid channel_id are passed
def test_channel_addowner_invalid_token_and_invalid_channel_id(set_up):
    member_id, invalid_token, new_channel_id = set_up

    user_token = requests.post(f'{url}auth/login/v2', json = {
    'email': 'kydares@gmail.com',
    'password': 'ilovemyself'
    }).json()['token']

    requests.post(f'{url}channel/join/v2', json = {
    'token': user_token,
    'channel_id': new_channel_id})

    invalid_token = 'invalid_token'

    response = requests.post(f'{url}channel/addowner/v1', json = {
    'token': invalid_token,
    'channel_id': new_channel_id + 3,
    'u_id': member_id})

    assert response.status_code == AccessError.code

# Tests when an invalid token and an invalid u_id are passed
def test_channel_addowner_invalid_token_and_invalid_u_id(set_up):
    member_id, invalid_token, new_channel_id = set_up

    user_token = requests.post(f'{url}auth/login/v2', json = {
    'email': 'kydares@gmail.com',
    'password': 'ilovemyself'
    }).json()['token']

    invalid_token = 'invalid_token'

    requests.post(f'{url}channel/join/v2', json = {
    'token': user_token,
    'channel_id': new_channel_id})

    response = requests.post(f'{url}channel/addowner/v1', json = {
    'token': invalid_token,
    'channel_id': new_channel_id,
    'u_id': member_id + 3})

    assert response.status_code == AccessError.code

# Tests when an invalid token is passed and when a non-member is added as an 
# owner
def test_channel_addowner_invalid_token_and_non_member(set_up):
    non_member_id, invalid_token, new_channel_id = set_up

    invalid_token = 'invalid_token'

    response = requests.post(f'{url}channel/addowner/v1', json = {
    'token': invalid_token,
    'channel_id': new_channel_id,
    'u_id': non_member_id})

    assert response.status_code == AccessError.code

# Tests when an invalid token is passed and when an owner is added as an owner
def test_channel_addowner_invalid_token_and_already_owner(set_up):
    member_id, owner_token, new_channel_id = set_up

    user_token = requests.post(f'{url}auth/login/v2', json = {
    'email': 'kydares@gmail.com',
    'password': 'ilovemyself'
    }).json()['token']

    requests.post(f'{url}channel/join/v2', json = {
    'token': user_token,
    'channel_id': new_channel_id})
    
    requests.post(f'{url}channel/addowner/v1', json = {
    'token': owner_token,
    'channel_id': new_channel_id,
    'u_id': member_id})

    response = requests.post(f'{url}channel/addowner/v1', json = {
    'token': 'invalid_token',
    'channel_id': new_channel_id,
    'u_id': member_id})

    assert response.status_code == AccessError.code