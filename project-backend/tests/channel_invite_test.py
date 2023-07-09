import pytest
import requests
from src.config import url
from src.error import AccessError, InputError
from src.helper import Success_code

# Set_up creates the required users and channel and also clears the
# data_store
@pytest.fixture
def set_up():
    requests.delete(f'{url}/clear/v1')

    member_token = requests.post(f'{url}/auth/register/v2', json = {
    'email': 'history1932@gmail.com',
    'password': '123456',
    'name_first': 'Adam',
    'name_last': 'Chen'}).json()['token']

    user_id = requests.post(f'{url}/auth/register/v2', json = {
    'email': 'kydares@gmail.com',
    'password': 'ilovemyself',
    'name_first': 'Kyle',
    'name_last': 'Wu'}).json()['auth_user_id']

    new_channel_id = requests.post(f'{url}/channels/create/v2', json = {
    'token': member_token,
    'name': 'new_channel',
    'is_public': True}).json()['channel_id']

    return user_id, new_channel_id, member_token

@pytest.fixture
def set_up_adding_owner():
    requests.delete(f'{url}/clear/v1')

    member = requests.post(f'{url}/auth/register/v2', json = {
    'email': 'history1932@gmail.com',
    'password': '123456',
    'name_first': 'Adam',
    'name_last': 'Chen'}).json()

    user_token = requests.post(f'{url}/auth/register/v2', json = {
    'email': 'kydares@gmail.com',
    'password': 'ilovemyself',
    'name_first': 'Kyle',
    'name_last': 'Wu'}).json()['token']
    
    return member, user_token

@pytest.fixture
def set_up_non_member_invite():
    requests.delete(f'{url}/clear/v1')

    member_token = requests.post(f'{url}/auth/register/v2', json = {
    'email': 'history1932@gmail.com',
    'password': '123456',
    'name_first': 'Adam',
    'name_last': 'Chen'}).json()['token']

    user_id = requests.post(f'{url}/auth/register/v2', json = {
    'email': 'kydares@gmail.com',
    'password': 'ilovemyself',
    'name_first': 'Kyle',
    'name_last': 'Wu'}).json()['auth_user_id']

    non_member_token = requests.post(f'{url}/auth/register/v2', json = {
    'email': 'DerekTran@gmail.com',
    'password': '12345678',
    'name_first': 'Derek',
    'name_last': 'Tran'}).json()['token']
    
    new_channel_id = requests.post(f'{url}/channels/create/v2', json = {
    'token': member_token,
    'name': 'new_channel',
    'is_public': True}).json()['channel_id']

    return non_member_token, user_id, new_channel_id

# Testing a successful inviting process with a single user
def test_channel_invite_successful_single(set_up):
    user_id, new_channel_id, member_token = set_up
    
    response = requests.post(f'{url}/channel/invite/v2', json = {
    'token': member_token,
    'channel_id': new_channel_id,
    'u_id': user_id})

    assert response.json() == {}
    assert response.status_code == Success_code
    
    user = requests.post(f'{url}/auth/register/v2', json = {
    'email': 'DerekTran@gmail.com',
    'password': '12345678',
    'name_first': 'Derek',
    'name_last': 'Tran'})

    response = requests.post(f'{url}/channel/invite/v2', json = {
    'token': member_token,
    'channel_id': new_channel_id,
    'u_id': user.json()['auth_user_id']})

    assert response.json() == {}
    assert response.status_code == Success_code

    response = requests.get(f'{url}/channels/list/v2', params = {
    'token': user.json()['token']})
    assert response.json()['channels'][0]['channel_id'] == new_channel_id

# Testing a successful inviting process with multiple users
def test_channel_invite_successful_multiple(set_up):
    user_id, new_channel_id, member_token = set_up

    user1_id = requests.post(f'{url}/auth/register/v2', json = {
    'email': 'DerekTran@gmail.com',
    'password': '12345678',
    'name_first': 'Derek',
    'name_last': 'Tran'}).json()['auth_user_id']

    response = requests.post(f'{url}/channel/invite/v2', json = {
    'token': member_token,
    'channel_id': new_channel_id,
    'u_id': user_id})

    assert response.json() == {}
    assert response.status_code == Success_code
    
    response = requests.post(f'{url}/channel/invite/v2', json = {
    'token': member_token,
    'channel_id': new_channel_id,
    'u_id': user1_id})

    assert response.json() == {}
    assert response.status_code == Success_code

    user_token = requests.post(f'{url}/auth/login/v2', json = {
    'email': 'kydares@gmail.com',
    'password': 'ilovemyself'}).json()['token']

    user1_token = requests.post(f'{url}/auth/login/v2', json = {
    'email': 'DerekTran@gmail.com',
    'password': '12345678'}).json()['token']

    response = requests.get(f'{url}/channels/list/v2', params = {
    'token': user_token})
    assert response.json()['channels'][0]['channel_id'] == new_channel_id

    response = requests.get(f'{url}/channels/list/v2', params = {
    'token': user1_token})
    assert response.json()['channels'][0]['channel_id'] == new_channel_id
    
# Tests for when a global owner is added to a private channel
def test_channel_invite_adding_global_owner_private(set_up_adding_owner):
    member, user_token = set_up_adding_owner
    
    member_id = member['auth_user_id']
    member_token = member['token']
    
    new_channel_id = requests.post(f'{url}/channels/create/v2', json = {
    'token': user_token,
    'name': 'new_channel',
    'is_public': False}).json()['channel_id']

    response = requests.post(f'{url}/channel/invite/v2', json = {
    'token': user_token,
    'channel_id': new_channel_id,
    'u_id': member_id})

    assert response.json() == {}
    assert response.status_code == Success_code

    response = requests.get(f'{url}/channels/list/v2', params = {
    'token': member['token']})
    assert response.json()['channels'][0]['channel_id'] == new_channel_id

    # Checking that the global owner has channel_permissions
    response = requests.post(f'{url}channel/addowner/v1', json = {
    'token': member_token,
    'channel_id': new_channel_id,
    'u_id': member_id})

    assert response.status_code == Success_code

# Tests for when a global owner is added to a public channel
def test_channel_invite_adding_global_owner_public(set_up_adding_owner):
    member, user_token = set_up_adding_owner
    
    member_id = member['auth_user_id']
    member_token = member['token']
    
    new_channel_id = requests.post(f'{url}/channels/create/v2', json = {
    'token': user_token,
    'name': 'new_channel',
    'is_public': True}).json()['channel_id']

    response = requests.post(f'{url}/channel/invite/v2', json = {
    'token': user_token,
    'channel_id': new_channel_id,
    'u_id': member_id})
    
    assert response.json() == {}
    assert response.status_code == Success_code

    response = requests.get(f'{url}/channels/list/v2', params = {
    'token': member['token']})
    assert response.json()['channels'][0]['channel_id'] == new_channel_id

    # Checking that the global owner has channel_permissions
    response = requests.post(f'{url}channel/addowner/v1', json = {
    'token': member_token,
    'channel_id': new_channel_id,
    'u_id': member_id})

    assert response.status_code == Success_code

# The following test for errors

# Testing an invalid channel_id
def test_channel_invite_invalid_channel_id(set_up):
    user_id, new_channel_id, member_token = set_up
    
    response = requests.post(f'{url}/channel/invite/v2', json = {
    'token': member_token,
    'channel_id': new_channel_id + 3,
    'u_id': user_id})

    assert response.status_code == InputError.code

# Testing an invalid user_id
def test_channel_invite_invalid_user_id(set_up):
    user_id, new_channel_id, member_token = set_up
    
    response = requests.post(f'{url}/channel/invite/v2', json = {
    'token': member_token,
    'channel_id': new_channel_id,
    'u_id': user_id + 3})

    assert response.status_code == InputError.code

# Testing when an existing member is invited to the channel
def test_channel_invite_existing_member(set_up):
    user_id, new_channel_id, member_token = set_up
    
    requests.post(f'{url}/channel/invite/v2', json = {
    'token': member_token,
    'channel_id': new_channel_id,
    'u_id': user_id})
    
    response = requests.post(f'{url}/channel/invite/v2', json = {
    'token': member_token,
    'channel_id': new_channel_id,
    'u_id': user_id})

    assert response.status_code == InputError.code

# Testing when the invite is sent by a user who is not a member of the channel
def test_channel_invite_not_member_of_channel(set_up_non_member_invite):
    non_member_token, user_id, new_channel_id = set_up_non_member_invite

    response = requests.post(f'{url}/channel/invite/v2', json = {
    'token': non_member_token,
    'channel_id': new_channel_id,
    'u_id': user_id})

    assert response.status_code == AccessError.code

# Testing when an invalid token is passed
def test_channel_invite_invalid_token(set_up) :
    user_id, new_channel_id, member_token = set_up

    response = requests.post(f'{url}/channel/invite/v2', json = {
    'token': member_token + 'invalid_token',
    'channel_id': new_channel_id,
    'u_id': user_id})

    assert response.status_code == AccessError.code

# The following test for when input and access errors should be thrown

# Testing situations where there is an invalid u_id and the invitation is sent
# by a non-member of the channel
def test_channel_invite_auth_not_member_and_invalid_u_id(set_up_non_member_invite):
    non_member_token, user_id, new_channel_id = set_up_non_member_invite

    response = requests.post(f'{url}/channel/invite/v2', json = {
    'token': non_member_token,
    'channel_id': new_channel_id,
    'u_id': user_id + 10})

    assert response.status_code == AccessError.code

# Testing situations where the invitation is sent by a non-member and the
# recipient of the invitation is already a member
def test_channel_invite_auth_not_member_and_user_already_in_channel(set_up_non_member_invite):
    non_member_token, user_id, new_channel_id = set_up_non_member_invite
    
    member_token = requests.post(f'{url}/auth/login/v2', json = {
        'email': 'history1932@gmail.com',
        'password': '123456'
    }).json()['token']

    requests.post(f'{url}/channel/invite/v2', json = {
    'token': member_token,
    'channel_id': new_channel_id,
    'u_id': user_id})
    
    response = requests.post(f'{url}/channel/invite/v2', json = {
    'token': non_member_token,
    'channel_id': new_channel_id,
    'u_id': user_id})

    assert response.status_code == AccessError.code

# Testing when an invalid token and an invalid u_id are passed
def tets_channel_invite_invalid_token_and_invalid_u_id(set_up):
    user_id, new_channel_id, member_token = set_up

    response = requests.post(f'{url}/channel/invite/v2', json = {
    'token': member_token + 'invalid_token',
    'channel_id': new_channel_id,
    'u_id': user_id + 10})

    assert response.status_code == AccessError.code

# Testing when an invalid token is passed and the user associated with
# u_id is already a member
def test_channel_invite_invalid_token_and_user_already_in_channel(set_up):
    user_id, new_channel_id, member_token = set_up

    requests.post(f'{url}/channel/invite/v2', json = {
    'token': member_token,
    'channel_id': new_channel_id,
    'u_id': user_id})

    response = requests.post(f'{url}/channel/invite/v2', json = {
    'token': member_token + 'invalid_token',
    'channel_id': new_channel_id,
    'u_id': user_id})

    assert response.status_code == AccessError.code

# Testing when an invalid token and invalid channel_id are passed
def test_channel_invite_invalid_token_and_invalid_channel_id(set_up):
    user_id, new_channel_id, member_token = set_up

    response = requests.post(f'{url}/channel/invite/v2', json = {
    'token': member_token + 'invalid_token',
    'channel_id': new_channel_id + 10,
    'u_id': user_id})

    assert response.status_code == AccessError.code