import pytest
import requests
from src.config import url
from src.error import AccessError, InputError
from src.helper import Success_code

# Set_up clears the data_store and registers two users
@pytest.fixture
def set_up():
    requests.delete(f'{url}clear/v1')

    user1_token = requests.post(f'{url}auth/register/v2', json = {
    'email': 'history@gmail.com',
    'password': '123456',
    'name_first': 'Adam',
    'name_last': 'Chen'}).json()['token']

    requests.post(f'{url}auth/register/v2', json = {
    'email': 'kydares@gmail.com',
    'password': 'ilovemyself',
    'name_first': 'Kyle',
    'name_last': 'Wu'})

    return user1_token

# Testing a single user joining a public channel
def test_channel_join_public_single(set_up):
    token = set_up
    new_channel_id = requests.post(f'{url}channels/create/v2', json = {
    'token': token,
    'name': 'new_channel',
    'is_public': True}).json()['channel_id']
    
    token2 = requests.post(f'{url}auth/login/v2', json = {
        'email': 'kydares@gmail.com',
        'password': 'ilovemyself'
    }).json()['token']

    response = requests.post(f'{url}channel/join/v2', json = {
    'token': token2,
    'channel_id': new_channel_id})

    assert response.json() == {}
    assert response.status_code == Success_code
    response = requests.get(f'{url}channels/list/v2', params = {
    'token': token})
    assert response.json()['channels'][0]['channel_id'] == new_channel_id

# Testing multiple users joinig a public channel
def test_channel_join_public_multiple(set_up):
    token = set_up

    new_channel_id = requests.post(f'{url}channels/create/v2', json = {
    'token': token,
    'name': 'new_channel',
    'is_public': True}).json()['channel_id']

    token2 = requests.post(f'{url}auth/register/v2', json = {
    'email': 'DerekTran@gmail.com',
    'password': '12345678',
    'name_first': 'Derek',
    'name_last': 'Tran'}).json()['token']

    token3 = requests.post(f'{url}auth/login/v2', json = {
    'email': 'kydares@gmail.com',
    'password': 'ilovemyself'}).json()['token']

    response = requests.post(f'{url}channel/join/v2', json = {
    'token': token3,
    'channel_id': new_channel_id})
    assert response.json() == {}
    assert response.status_code == Success_code

    response = requests.post(f'{url}channel/join/v2', json = {
    'token': token2,
    'channel_id': new_channel_id})
    assert response.json() == {}
    assert response.status_code == Success_code
    
    response = requests.get(f'{url}channels/list/v2', params = {
    'token': token})
    assert response.json()['channels'][0]['channel_id'] == new_channel_id

    response = requests.get(f'{url}channels/list/v2', params = {
    'token': token2})
    assert response.json()['channels'][0]['channel_id'] == new_channel_id

# Testing a global owner joining a private channel
def test_channel_join_private_is_global_owner(set_up):
    token = set_up

    user1_id = requests.post(f'{url}auth/login/v2', json = {
    'email': 'history@gmail.com',
    'password': '123456'}).json()['auth_user_id']

    token2 = requests.post(f'{url}auth/login/v2', json = {
    'email': 'kydares@gmail.com',
    'password': 'ilovemyself'}).json()['token']
    
    new_channel_id = requests.post(f'{url}channels/create/v2', json = {
    'token': token2,
    'name': 'new_channel',
    'is_public': False}).json()['channel_id']

    response = requests.post(f'{url}channel/join/v2', json = {
    'token': token,
    'channel_id': new_channel_id})
    assert response.json() == {}
    assert response.status_code == Success_code
    
    response = requests.get(f'{url}channels/list/v2', params = {
    'token': token})
    assert response.json()['channels'][0]['channel_id'] == new_channel_id

    # Checking that the global owner has channel_permissions
    response = requests.post(f'{url}channel/addowner/v1', json = {
    'token': token,
    'channel_id': new_channel_id,
    'u_id': user1_id})

    assert response.status_code == Success_code

# The following test for errors

# Testing a non-owner joining a private channel
def test_channel_join_private_not_global_owner(set_up):
    token = set_up

    new_channel_id = requests.post(f'{url}channels/create/v2', json = {
    'token': token,
    'name': 'new_channel',
    'is_public': False}).json()['channel_id']

    user_token = requests.post(f'{url}auth/login/v2', json = {
    'email': 'kydares@gmail.com',
    'password': 'ilovemyself'}).json()['token']
    
    response = requests.post(f'{url}channel/join/v2', json = {
    'token': user_token, 
    'channel_id': new_channel_id})
    assert response.status_code == AccessError.code

# Testing an invalid channel_id
def test_channel_join_invalid_channel_id(set_up):
    token = set_up
    
    new_channel_id = requests.post(f'{url}channels/create/v2', json = {
    'token': token,
    'name': 'new_channel',
    'is_public': True}).json()['channel_id']

    user_token = requests.post(f'{url}auth/login/v2', json = {
    'email': 'kydares@gmail.com',
    'password': 'ilovemyself'}).json()['token']

    response = requests.post(f'{url}channel/join/v2', json = {
    'token': user_token, 
    'channel_id': new_channel_id + 3})
    assert response.status_code == InputError.code

# Testing an existing user joining a channel
def test_channel_join_existing_member(set_up):
    token = set_up

    new_channel_id = requests.post(f'{url}channels/create/v2', json = {
    'token': token,
    'name': 'new_channel',
    'is_public': True}).json()['channel_id']

    user_token = requests.post(f'{url}auth/login/v2', json = {
    'email': 'kydares@gmail.com',
    'password': 'ilovemyself'}).json()['token']

    requests.post(f'{url}channel/join/v2', json = {
    'token': user_token, 
    'channel_id': new_channel_id})

    response = requests.post(f'{url}channel/join/v2', json = {
    'token': user_token, 
    'channel_id': new_channel_id})
    assert response.status_code == InputError.code
    
# Testing an invalid token
def test_channel_join_invalid_token(set_up):
    token = set_up

    new_channel_id = requests.post(f'{url}channels/create/v2', json = {
    'token': token,
    'name': 'new_channel',
    'is_public': True}).json()['channel_id']

    response = requests.post(f'{url}channel/join/v2', json = {
    'token': 'invalid_token', 
    'channel_id': new_channel_id})
    assert response.status_code == AccessError.code

# The following test for when input and access errors should be thrown

# Testing an invalid token and an invalid channel_id
def test_channel_join_invalid_token_and_invalid_channel_id(set_up):
    token = set_up

    new_channel_id = requests.post(f'{url}channels/create/v2', json = {
    'token': token,
    'name': 'new_channel',
    'is_public': True}).json()['channel_id']

    response = requests.post(f'{url}channel/join/v2', json = {
    'token': 'invalid_token', 
    'channel_id': new_channel_id + 3})
    assert response.status_code == AccessError.code
