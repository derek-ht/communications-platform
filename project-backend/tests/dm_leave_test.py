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
def test_dm_leave_standard(setup):
    user1 = setup[0]
    user2 = setup[1]
    dm1 = setup[3]

    pload = {
        'token': user2['token'],
        'dm_id': dm1['dm_id']
    }
    response = requests.post(url + 'dm/leave/v1', json = pload)
    assert response.status_code == Success_code
    assert response.json() == {}

    pload = {
        'token': user1['token'],
        'dm_id': 1,
    }
    response = requests.get(url + 'dm/details/v1', params = pload)
    details1 = response.json()

    assert details1 =={
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
                'u_id': 3,
                'email': 'biology@gmail.com',
                'name_first': 'Tae',
                'name_last': 'Pham',
                'handle_str': 'taepham',
            }
        ]}

# Dm Owner leaves dm
def test_dm_leave_owner(setup):
    user1 = setup[0]
    user2 = setup[1]
    dm3 = setup[5]

    pload = {
        'token': user2['token'],
        'dm_id': dm3['dm_id']
    }
    response = requests.post(url + 'dm/leave/v1', json = pload)
    assert response.status_code == Success_code
    assert response.json() == {}

    pload = {
        'token': user1['token'],
        'dm_id': dm3['dm_id'],
    }
    response = requests.get(url + 'dm/details/v1', params = pload)
    details3 = response.json()

    assert details3 == {
        'name': 'adamchen, kylewu',
        'members': [
            {
                'u_id': 1,
                'email': 'history@gmail.com',
                'name_first': 'Adam',
                'name_last': 'Chen',
                'handle_str': 'adamchen'
            }
        ]
        }

# Case where dm left with no users
# Should be treated as if dm was removed
def test_dm_leave_empty_dm(setup):
    user1 = setup[0]
    user2 = setup[1]
    dm3 = setup[5]

    pload = {
        'token': user2['token'],
        'dm_id': dm3['dm_id']
    }
    response = requests.post(url + 'dm/leave/v1', json = pload)
    assert response.status_code == Success_code
    assert response.json() == {}

    pload = {
        'token': user1['token'],
        'dm_id': dm3['dm_id']
    }
    response = requests.post(url + 'dm/leave/v1', json = pload)
    assert response.status_code == Success_code
    assert response.json() == {}

    pload = {
        'token': user1['token'],
        'dm_id': dm3['dm_id']
    }
    response = requests.post(url + 'dm/leave/v1', json = pload)
    assert response.status_code == InputError.code

# Invalid token
def test_dm_leave_invalid_token(setup):
    dm1 = setup[3]

    pload = {
        'token': 'not_a_token',
        'dm_id': dm1['dm_id']
    }
    response = requests.post(url + 'dm/leave/v1', json = pload)
    assert response.status_code == AccessError.code

# Invalid dm_id
def test_dm_leave_invalid_dm_id(setup):
    user1 = setup[0]
    dm3 = setup[5]

    pload = {
        'token': user1['token'],
        'dm_id': dm3['dm_id'] + 1
    }
    response = requests.post(url + 'dm/leave/v1', json = pload)
    assert response.status_code == InputError.code

# User not part of dm
def test_dm_leave_not_member(setup):
    user1 = setup[0]
    dm2 = setup[4]

    pload = {
        'token': user1['token'],
        'dm_id': dm2['dm_id']
    }
    response = requests.post(url + 'dm/leave/v1', json = pload)
    assert response.status_code == AccessError.code