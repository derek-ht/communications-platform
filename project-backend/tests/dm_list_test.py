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
def test_dm_list_standard(setup):
    user1 = setup[0]
    user2 = setup[1]
    user3 = setup[2]

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

    # dm_list2 shows case of user in all dms
    assert dm_list1 == {'dms': [{'dm_id': 1, 
                                 'name': 'adamchen, kylewu, taepham'},
                                {'dm_id': 3,
                                 'name': 'adamchen, kylewu'}
                                ]}
    assert dm_list2 == {'dms': [{'dm_id': 1,
                                 'name': 'adamchen, kylewu, taepham'},
                                {'dm_id': 2,
                                 'name': 'kylewu, taepham'},
                                {'dm_id': 3,
                                 'name': 'adamchen, kylewu'}
                                ]}
    assert dm_list3 == {'dms': [{'dm_id': 1,
                                 'name': 'adamchen, kylewu, taepham'},
                                {'dm_id': 2,
                                 'name': 'kylewu, taepham'}
                                ]}
    assert response.status_code == Success_code

# User not in any dms
def test_dm_list_no_dms(setup):
    
    pload = {
        'email': 'english@gmail.com',
        'password': 'failpass',
        'name_first': 'Koe',
        'name_last': 'Tai'
    }
    response = requests.post(url + 'auth/register/v2', json = pload)
    user4 = response.json()
    
    pload = {
        'token': user4['token']
    }
    response = requests.get(url + 'dm/list/v1', params = pload)
    dm_list = response.json()

    assert dm_list == {'dms': []}
    assert response.status_code == Success_code

# Invalid token
def test_dm_list_invalid_token(setup):

    pload = {
        'token': 'not_a_token'
    }
    response = requests.get(url + 'dm/list/v1', params = pload)
    assert response.status_code == AccessError.code
