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
def test_dm_remove_standard(setup):
    user1 = setup[0]
    user2 = setup[1]
    user3 = setup[2]
    dm1 = setup[3]

    pload = {
        'token': user1['token'],
        'dm_id': dm1['dm_id']
    }
    response = requests.delete(url + 'dm/remove/v1', json = pload)    

    assert response.status_code == Success_code
    assert response.json() == {}

    pload = {
        'token': user1['token']
    }
    response = requests.get(url + 'dm/list/v1', params = pload)
    dm_list1 = response.json()

    pload = {
        'token': user2['token']
    }
    response = requests.get(url + 'dm/list/v1', params = pload)
    dm_list2 = response.json()

    pload = {
        'token': user3['token']
    }
    response = requests.get(url + 'dm/list/v1', params = pload)
    dm_list3 = response.json()

    assert dm_list1 == {'dms': [{'dm_id': 3, 
                                 'name': 'adamchen, kylewu'}
                                ]}

    assert dm_list2 == {'dms': [{'dm_id': 2,
                                 'name': 'kylewu, taepham'},
                                {'dm_id': 3, 
                                 'name': 'adamchen, kylewu'}
                                ]}

    assert dm_list3 == {'dms': [{'dm_id': 2,
                                 'name': 'kylewu, taepham'}
                                ]}

# User left with no dms
def test_dm_remove_no_dms_left(setup):
    user1 = setup[0]
    user2 = setup[1]
    dm1 = setup[3]
    dm3 = setup[5]

    pload = {
        'token': user1['token'],
        'dm_id': dm1['dm_id']
    }
    response = requests.delete(url + 'dm/remove/v1', json = pload)
    
    assert response.status_code == Success_code
    assert response.json() == {}
    
    pload = {
        'token': user2['token'],
        'dm_id': dm3['dm_id']
    }
    requests.delete(url + 'dm/remove/v1', json = pload)

    pload = {
        'token': user1['token']
    }
    response = requests.get(url + 'dm/list/v1', params = pload)
    dm_list1 = response.json()

    assert dm_list1 == {'dms': []}

# Accessing a removed dm
def test_dm_remove_removed_dm(setup):
    user1 = setup[0]
    dm1 = setup[3]

    pload = {
        'token': user1['token'],
        'dm_id': dm1['dm_id']
    }
    response = requests.delete(url + 'dm/remove/v1', json = pload)
    
    assert response.status_code == Success_code
    assert response.json() == {}

    pload = {
        'token': user1['token'],
        'dm_id': dm1['dm_id']
    }
    response = requests.delete(url + 'dm/remove/v1', json = pload)
    assert response.status_code == InputError.code

# Invalid token
def test_dm_remove_invalid_token(setup):
    dm1 = setup[3]

    pload = {
        'token': 'not_a_token',
        'dm_id': dm1['dm_id']
    }
    response = requests.delete(url + 'dm/remove/v1', json = pload)
    assert response.status_code == AccessError.code

# Invalid dm_id
def test_dm_remove_invalid_dm_id(setup):
    user1 = setup[0]
    dm3 = setup[5]

    pload = {
        'token': user1['token'],
        'dm_id': dm3['dm_id'] + 1
    }
    response = requests.delete(url + 'dm/remove/v1', json = pload)
    assert response.status_code == InputError.code

# Token not from owner
def test_dm_remove_not_owner(setup):
    user3 = setup[2] 
    dm1 = setup[3]

    pload = {
        'token': user3['token'],
        'dm_id': dm1['dm_id']
    }
    response = requests.delete(url + 'dm/remove/v1', json = pload)
    assert response.status_code == AccessError.code