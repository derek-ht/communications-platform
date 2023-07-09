import pytest
import requests

# Importing from
from src.config import url
from src.error import AccessError, InputError
from src.helper import Success_code

@pytest.fixture
def setup():
    requests.delete(url + 'clear/v1')

    pload = {
        'email': 'history@gmail.com',
        'password': 'testpass',
        'name_first': 'Adam',
        'name_last': 'Chen'
    }
    response = requests.post(url + 'auth/register/v2', json = pload)
    user1 = response.json()

    pload = {
        'email': 'physics@gmail.com',
        'password': 'passtest',
        'name_first': 'Kyle',
        'name_last': 'Wu'
    }
    response = requests.post(url + 'auth/register/v2', json = pload)
    user2 = response.json()
    
    pload = {
        'email': 'biology@gmail.com',
        'password': 'testtest',
        'name_first': 'Tae',
        'name_last': 'Pham'
    }
    response = requests.post(url + 'auth/register/v2', json = pload)
    user3 = response.json()

    return user1, user2, user3

# Standard Case
def test_dm_create_standard(setup):
    user1 = setup[0]
    user2 = setup[1]
    
    pload = {
        'token': user1['token'],
        'u_ids': [2, 3]
    }
    response = requests.post(url + 'dm/create/v1', json = pload)
    dm1 = response.json()

    pload = {
        'token': user2['token'],
        'u_ids': [1]
    }
    response = requests.post(url + 'dm/create/v1', json = pload)
    dm2 = response.json()

    assert dm1 == {'dm_id': 1}
    assert dm2 == {'dm_id': 2}
    assert response.status_code == Success_code

# Dm with only owner
def test_dm_create_only_owner(setup):
    user1 = setup[0]
    user2 = setup[1]

    pload = {
        'token': user1['token'],
        'u_ids': []
    }
    response = requests.post(url + 'dm/create/v1', json = pload)
    dm1 = response.json()

    pload = {
        'token': user2['token'],
        'u_ids': [2]
    }
    response = requests.post(url + 'dm/create/v1', json = pload)
    dm2 = response.json()

    assert dm1 == {'dm_id': 1}
    assert dm2 == {'dm_id': 2}
    assert response.status_code == Success_code

# Invalid token
def test_dm_create_invalid_token(setup):

    pload = {
        'token': 'not_a_token',
        'u_ids': [2, 3]
    }
    response = requests.post(url + 'dm/create/v1', json = pload)
    assert response.status_code == AccessError.code
    
    pload = {
        'token': '',
        'u_ids': [2, 3]
    }
    response = requests.post(url + 'dm/create/v1', json = pload)
    assert response.status_code == AccessError.code

# Invalid u_ids
def test_dm_create_invalid_ids(setup):
    user1 = setup[0]

    pload = {
        'token': user1['token'],
        'u_ids': [4]
    }
    response = requests.post(url + 'dm/create/v1', json = pload)
    assert response.status_code == InputError.code

# Duplicate users for dms
def test_dm_create_dupe_users(setup):
    user1 = setup[0]

    pload = {
        'token': user1['token'],
        'u_ids': [2, 2]
    }
    response = requests.post(url + 'dm/create/v1', json = pload)
    assert response.status_code == InputError.code