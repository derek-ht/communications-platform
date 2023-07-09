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

    return user1, user2

# Standard case
def test_channels_create_valid(setup):
    user1, user2 = setup
    
    pload = {
        'token': user1['token'],
        'name': 'test_ch1',
        'is_public': True       
    }
    response = requests.post(url + 'channels/create/v2', json = pload)
    ch1 = response.json()

    pload = {
        'token': user2['token'],
        'name': 'test_ch2',
        'is_public': False       
    }
    response = requests.post(url + 'channels/create/v2', json = pload)
    ch2 = response.json()

    assert ch1 == {'channel_id': 1}
    assert ch2 == {'channel_id': 2}
    assert response.status_code == Success_code

# Duplicate ch_names
def test_channels_create_dupe_ch_name(setup):
    user1, user2 = setup

    pload = {
        'token': user1['token'],
        'name': 'test_same',
        'is_public': True       
    }
    response = requests.post(url + 'channels/create/v2', json = pload)
    ch1 = response.json()

    pload = {
        'token': user2['token'],
        'name': 'test_same',
        'is_public': True       
    }
    response = requests.post(url + 'channels/create/v2', json = pload)
    ch2 = response.json()

    assert(ch1 != ch2)
    assert response.status_code == Success_code

# Invalid user token
def test_channels_create_invalid_token(setup):

    pload = {
        'token': 'invalid_token',
        'name': 'test_ch1',
        'is_public': True       
    }
    response = requests.post(url + 'channels/create/v2', json = pload)
    assert response.status_code == AccessError.code

# Valid ch_name, edge length cases
def test_channels_create_valid_ch_name_edge(setup):
    user1, user2 = setup

    pload = {
        'token': user1['token'],
        'name': 't',
        'is_public': True       
    }
    response = requests.post(url + 'channels/create/v2', json = pload)
    ch1 = response.json()

    pload = {
        'token': user2['token'],
        'name': 'testlimit20_12345678',
        'is_public': False     
    }
    response = requests.post(url + 'channels/create/v2', json = pload)
    ch2 = response.json()
    
    assert ch1 == {'channel_id': 1}
    assert ch2 == {'channel_id': 2}
    assert response.status_code == Success_code

# Invalid ch_name
def test_channels_create_invalid_ch_name(setup):
    user1, user2 = setup

    pload = {
        'token': user1['token'],
        'name': '',
        'is_public': False     
    }
    response = requests.post(url + 'channels/create/v2', json = pload)
    assert response.status_code == InputError.code
    
    pload = {
        'token': user2['token'],
        'name': '',
        'is_public': False     
    }
    response = requests.post(url + 'channels/create/v2', json = pload)
    assert response.status_code == InputError.code