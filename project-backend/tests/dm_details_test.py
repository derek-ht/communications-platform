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

    pload = {
        'token': user1['token'],
        'u_ids': [2, 3],
    }
    response = requests.post(url + 'dm/create/v1', json = pload)
    dm1 = response.json()

    pload = {
        'token': user2['token'],
        'u_ids': [3],
    }
    response = requests.post(url + 'dm/create/v1', json = pload)
    dm2 = response.json()

    pload = {
        'token': user2['token'],
        'u_ids': [1],
    }
    response = requests.post(url + 'dm/create/v1', json = pload)
    dm3 = response.json()

    return user1, user2, user3, dm1, dm2, dm3

# Standard Case
def test_dm_details_standard(setup):
    user1 = setup[0]
    user2 = setup[1]

    pload = {
        'token': user1['token'],
        'dm_id': 1,
    }
    response = requests.get(url + 'dm/details/v1', params = pload)
    details1 = response.json()

    pload = {
        'token': user2['token'],
        'dm_id': 2,
    }
    response = requests.get(url + 'dm/details/v1', params = pload)
    details2 = response.json()

    pload = {
        'token': user2['token'],
        'dm_id': 3,
    }
    response = requests.get(url + 'dm/details/v1', params = pload)
    details3 = response.json()
    
    assert details1 == {
        'name': 'adamchen, kylewu, taepham',
        'members': [
            {
                'u_id': 1,
                'email': 'history@gmail.com',
                'name_first': 'Adam',
                'name_last': 'Chen',
                'handle_str': 'adamchen'
            }, 
            {
                'u_id': 2,
                'email': 'physics@gmail.com',
                'name_first': 'Kyle',
                'name_last': 'Wu',
                'handle_str': 'kylewu'
            },
            {
                'u_id': 3,
                'email': 'biology@gmail.com',
                'name_first': 'Tae',
                'name_last': 'Pham',
                'handle_str': 'taepham'
            }
        ]}

    assert details2 == {
        'name': 'kylewu, taepham',
        'members': [
            {
                'u_id': 2,
                'email': 'physics@gmail.com',
                'name_first': 'Kyle',
                'name_last': 'Wu',
                'handle_str': 'kylewu'
            },
            {
                'u_id': 3,
                'email': 'biology@gmail.com',
                'name_first': 'Tae',
                'name_last': 'Pham',
                'handle_str': 'taepham'
            }
        ]}

    assert details3 == {
        'name': 'adamchen, kylewu',
        'members': [
            {
                'u_id': 1,
                'email': 'history@gmail.com',
                'name_first': 'Adam',
                'name_last': 'Chen',
                'handle_str': 'adamchen'
            }, 
            {
                'u_id': 2,
                'email': 'physics@gmail.com',
                'name_first': 'Kyle',
                'name_last': 'Wu',
                'handle_str': 'kylewu',
            }
        ]}
    assert response.status_code == Success_code

# Invalid token
def test_dm_details_invalid_token(setup):

    pload = {
        'token': 'not_a_token',
        'dm_id': 1
    }
    response = requests.get(url + 'dm/details/v1', params = pload)
    assert response.status_code == AccessError.code

# Invalid dm_id
def test_dm_details_invalid_dm_id(setup):
    user1 = setup[0]
    dm3 = setup[5]

    pload = {
        'token': user1['token'],
        'dm_id': dm3['dm_id'] + 1
    }
    response = requests.get(url + 'dm/details/v1', params = pload)
    assert response.status_code == InputError.code

# User not part of dm
def test_dm_details_invalid_perms(setup):
    user1 = setup[0]
    dm2 = setup[4]

    pload = {
        'token': user1['token'],
        'dm_id': dm2['dm_id']
    }
    response = requests.get(url + 'dm/details/v1', params = pload)
    assert response.status_code == AccessError.code