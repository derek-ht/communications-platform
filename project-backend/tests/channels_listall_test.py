import pytest

# Importing from
import requests
from src.config import url
from src.error import AccessError
from src.helper import Success_code

@pytest.fixture
def set_up():
    requests.delete(url + "clear/v1")

    pload = {
        "email": "name1@gmail.com",
        "password": "password",
        "name_first": "person1",
        "name_last": "surname1"
    }
    response = requests.post(url + "auth/register/v2", json = pload)
    token = response.json()["token"]
    return token
    

# Testing when there is only one public channel
def test_channels_listall_one_public_channel(set_up):
    token = set_up
    pload = {
        "token": token,
        "name": "poop",
        "is_public": True
    }
    requests.post(url + "channels/create/v2", json = pload)

    response = requests.get(url + "channels/listall/v2", params = {"token": token})
    assert response.status_code == Success_code
    assert response.json() == {
            "channels": [
                {
                    "channel_id": 1,
                    "name": "poop"
                }
            ]
        }

# Testing when there are 3 public channels
def test_channel_listall_few_public_channels(set_up):
    token = set_up
    
    pload = {
        "token": token,
        "name": "channel1",
        "is_public": True
    }
    requests.post(url + "channels/create/v2", json = pload)

    pload = {
        "token": token,
        "name": "channel2",
        "is_public": True
    }
    requests.post(url + "channels/create/v2", json = pload)

    pload = {
        "token": token,
        "name": "channel3",
        "is_public": True
    }
    requests.post(url + "channels/create/v2", json = pload)

    response = requests.get(url + "channels/listall/v2", params = {"token": token})
    assert response.status_code == Success_code

    assert(response.json() == {
        "channels": [
        {
            "channel_id": 1,
            "name": "channel1"
        },
        {
            "channel_id": 2,
            "name": "channel2"
        },
        {
            'channel_id': 3,
            'name': "channel3"
        }
        ]}
    )

# Testing when there is only one private channel
def test_channels_listall_one_private_channel(set_up):
    token = set_up

    pload = {
        "token": token,
        "name": "poop",
        "is_public": False
    }
    requests.post(url + "channels/create/v2", json = pload)

    response = requests.get(url + "channels/listall/v2", params = {"token": token})
    assert response.status_code == Success_code

    assert(response.json() == {
        "channels": [
        {
            "channel_id": 1,
            "name": "poop"
        }
        ]}
    )

# Testing when there are 3 private channels
def test_channel_listall_few_private_channels(set_up):
    token = set_up

    pload = {
        "token": token,
        "name": "channel1",
        "is_public": False
    }
    requests.post(url + "channels/create/v2", json = pload)

    pload = {
        "token": token,
        "name": "channel2",
        "is_public": False
    }
    requests.post(url + "channels/create/v2", json = pload)

    pload = {
        "token": token,
        "name": "channel3",
        "is_public": False
    }
    requests.post(url + "channels/create/v2", json = pload)

    response = requests.get(url + "channels/listall/v2", params = {"token": token})
    assert response.status_code == Success_code

    assert(response.json() == {
        "channels": [
        {
            "channel_id": 1,
            "name": "channel1"
        },
        {
            "channel_id": 2,
            "name": "channel2"
        },
        {
            'channel_id': 3,
            'name': "channel3"
        }
        ]}
    )

# Testing when there are 6 created channels with mix of publice and private
def test_channel_listall_many_mixed_channels(set_up):
    token = set_up

    pload = {
        "token": token,
        "name": "channel1",
        "is_public": False
    }
    requests.post(url + "channels/create/v2", json = pload)

    pload = {
        "token": token,
        "name": "channel2",
        "is_public": True
    }
    requests.post(url + "channels/create/v2", json = pload)

    pload = {
        "token": token,
        "name": "channel3",
        "is_public": False
    }
    requests.post(url + "channels/create/v2", json = pload)

    pload = {
        "token": token,
        "name": "channel4",
        "is_public": True
    }
    requests.post(url + "channels/create/v2", json = pload)

    pload = {
        "token": token,
        "name": "channel5",
        "is_public": False
    }
    requests.post(url + "channels/create/v2", json = pload)

    pload = {
        "token": token,
        "name": "channel6",
        "is_public": True
    }
    requests.post(url + "channels/create/v2", json = pload)

    response = requests.get(url + "channels/listall/v2", params = {"token": token})
    assert response.status_code == Success_code

    assert(response.json() == {
        "channels": [
            {
                "channel_id": 1,
                "name": "channel1"
            },
            {
            "channel_id": 2,
            "name": "channel2"
            },
            {
                'channel_id': 3,
                'name': "channel3"
            },
            {
                "channel_id": 4,
                "name": "channel4"
            },
            {
                "channel_id": 5,
                "name": "channel5"
            },
            {
                "channel_id": 6,
                "name": "channel6"               
            }
        ]
        }
    )

# No channels in datastore
def test_empty_channels(set_up):
    token = set_up

    response = requests.get(url + "channels/listall/v2", params = {"token": token})
    assert response.status_code == Success_code

    assert(response.json() == {
        "channels": []
        }
    )

# Testing invalid auth user id
def test_invalid_token_access_error(set_up):
    invalid_token = "invalid_token_string"

    response = requests.get(url + "channels/listall/v2", params = {"token": invalid_token})
    assert response.status_code == AccessError.code
