import pytest

# Importing from
import requests
from src.config import url
from src.error import AccessError
from src.helper import Success_code

@pytest.fixture
def set_up():
    requests.delete(url + "clear/v1")
    tokens = []
    user_ids = []

    # Registers 10 users and store their tokens and user ids
    for i in range(1, 11):
    
        pload = {
        "email": f"name{i}@gmail.com",
        "password": "password",
        "name_first": f"person{i}",
        "name_last": f"surname{i}"
        }
        response = requests.post(url + "auth/register/v2", json = pload)
        
        user_details = response.json()
        tokens.append(user_details["token"])
        user_ids.append(user_details["auth_user_id"])

    return tokens, user_ids

# Testing when user is in one channel in a datastore of one channel
def test_channels_list_one_channel(set_up):
    tokens, user_ids = set_up
    auth_token = tokens[0]
    member_u_id = user_ids[1]

    # creates channel and populates it with one other member
    pload = {
        "token": auth_token,
        "name": "poop",
        "is_public": True
    }
    response = requests.post(url + "channels/create/v2", json = pload)
    channel_id = response.json()["channel_id"]

    pload = {
        "token": auth_token,
        "channel_id": channel_id,
        "u_id": member_u_id
    }
    requests.post(url + "channel/invite/v2", json = pload)

    response = requests.get(url + "channels/list/v2", params = {"token": auth_token})
    assert response.status_code == Success_code

    assert(response.json() == {
        "channels": [
        {
            "channel_id": 1,
            "name": "poop"
        }
        ]}
    )

# Testing when user is in one channel in a datastore of three channels
def test_channel_list_one_of_several_channels(set_up):
    tokens, user_ids = set_up
    auth_token = tokens[0]
    member_token = tokens[1]
    member_u_id = user_ids[1]

    pload = {
        "token": auth_token,
        "name": "channel1",
        "is_public": True
    }
    response = requests.post(url + "channels/create/v2", json = pload)
    channel_id = response.json()["channel_id"]

    pload = {
        "token": auth_token,
        "name": "channel2",
        "is_public": True
    }
    requests.post(url + "channels/create/v2", json = pload)

    pload = {
        "token": auth_token,
        "name": "channel3",
        "is_public": True
    }
    requests.post(url + "channels/create/v2", json = pload)

    pload = {
        "token": auth_token,
        "channel_id": channel_id,
        "u_id": member_u_id
    }
    requests.post(url + "channel/invite/v2", json = pload)

    response = requests.get(url + "channels/list/v2", params = {"token": member_token})
    assert response.status_code == Success_code
    assert(response.json() == {
        "channels": [
        {
            "channel_id": 1,
            "name": "channel1"
        }
        ]}
    )

# Testing when user is member of private channel
def test_channel_list_is_member_private_channels(set_up):
    tokens, user_ids = set_up
    auth_token = tokens[0]
    member_token = tokens[1]
    member_u_id = user_ids[1]

    pload = {
        "token": auth_token,
        "name": "channel1",
        "is_public": False
    }
    response = requests.post(url + "channels/create/v2", json = pload)
    channel_id = response.json()["channel_id"]

    pload = {
        "token": auth_token,
        "name": "channel2",
        "is_public": False
    }
    requests.post(url + "channels/create/v2", json = pload)

    pload = {
        "token": auth_token,
        "name": "channel3",
        "is_public": False
    }
    requests.post(url + "channels/create/v2", json = pload)

    pload = {
        "token": auth_token,
        "channel_id": channel_id,
        "u_id": member_u_id
    }
    requests.post(url + "channel/invite/v2", json = pload)

    response = requests.get(url + "channels/list/v2", params = {"token": member_token})
    assert response.status_code == Success_code
    assert(response.json() == {
        "channels": [
        {
            "channel_id": 1,
            "name": "channel1"
        }
        ]}
    )

# Testing when user is in several channels in a datastore of several channels
def test_channel_list_user_in_several_channels(set_up):
    tokens, user_ids = set_up
    auth_token = tokens[0]
    member_token = tokens[1]
    member_u_id = user_ids[1]
    
    # Creates 6 channels and add member to every second channel
    pload = {
        "token": auth_token,
        "name": "channel1",
        "is_public": True
    }
    requests.post(url + "channels/create/v2", json = pload)

    pload = {
        "token": auth_token,
        "name": "channel2",
        "is_public": True
    }
    response = requests.post(url + "channels/create/v2", json = pload)
    channel_id = response.json()["channel_id"]
    pload = {
        "token": auth_token,
        "channel_id": channel_id,
        "u_id": member_u_id
    }
    requests.post(url + "channel/invite/v2", json = pload)

    pload = {
        "token": auth_token,
        "name": "channel3",
        "is_public": True
    }
    requests.post(url + "channels/create/v2", json = pload)

    pload = {
        "token": auth_token,
        "name": "channel4",
        "is_public": True
    }
    response = requests.post(url + "channels/create/v2", json = pload)
    channel_id = response.json()["channel_id"]
    pload = {
        "token": auth_token,
        "channel_id": channel_id,
        "u_id": member_u_id
    }
    requests.post(url + "channel/invite/v2", json = pload)

    pload = {
        "token": auth_token,
        "name": "channel5",
        "is_public": True
    }
    requests.post(url + "channels/create/v2", json = pload)

    pload = {
        "token": auth_token,
        "name": "channel6",
        "is_public": True
    }
    response = requests.post(url + "channels/create/v2", json = pload)
    channel_id = response.json()["channel_id"]
    pload = {
        "token": auth_token,
        "channel_id": channel_id,
        "u_id": member_u_id
    }
    requests.post(url + "channel/invite/v2", json = pload)

    response = requests.get(url + "channels/list/v2", params = {"token": member_token})
    assert response.status_code == Success_code
    assert(response.json() == {
        "channels": [
            {
                "channel_id": 2,
                "name": "channel2"
            },
            {
                "channel_id": 4,
                "name": "channel4"
            },
            {
                "channel_id": 6,
                "name": "channel6"
            }
        ]
        }
    )

# Testing when there are multiple members in channels
def test_channel_list_multiple_members_in_channels(set_up):
    tokens, user_ids = set_up
    auth_token = tokens[0]
    member_token = tokens[1]

    # Creates 6 channels and populates them and only adds member_u_id to every second channel
    pload = {
        "token": auth_token,
        "name": "channel1",
        "is_public": True
    }
    response = requests.post(url + "channels/create/v2", json = pload)
    channel_id = response.json()["channel_id"]
    for user_id in user_ids[2:-1]:
        pload = {
            "token": auth_token,
            "channel_id": channel_id,
            "u_id": user_id
        }
        requests.post(url + "channel/invite/v2", json = pload)

    pload = {
        "token": auth_token,
        "name": "channel2",
        "is_public": True
    }
    response = requests.post(url + "channels/create/v2", json = pload)
    channel_id = response.json()["channel_id"]
    for user_id in user_ids[1:-1]:
        pload = {
            "token": auth_token,
            "channel_id": channel_id,
            "u_id": user_id
        }
        requests.post(url + "channel/invite/v2", json = pload)

    pload = {
        "token": auth_token,
        "name": "channel3",
        "is_public": True
    }
    response = requests.post(url + "channels/create/v2", json = pload)
    channel_id = response.json()["channel_id"]
    for user_id in user_ids[2:-1]:
        pload = {
            "token": auth_token,
            "channel_id": channel_id,
            "u_id": user_id
        }
        requests.post(url + "channel/invite/v2", json = pload)

    pload = {
        "token": auth_token,
        "name": "channel4",
        "is_public": True
    }
    response = requests.post(url + "channels/create/v2", json = pload)
    channel_id = response.json()["channel_id"]
    for user_id in user_ids[1:-1]:
        pload = {
            "token": auth_token,
            "channel_id": channel_id,
            "u_id": user_id
        }
        requests.post(url + "channel/invite/v2", json = pload)

    pload = {
        "token": auth_token,
        "name": "channel5",
        "is_public": True
    }
    response = requests.post(url + "channels/create/v2", json = pload)
    channel_id = response.json()["channel_id"]
    for user_id in user_ids[2:-1]:
        pload = {
            "token": auth_token,
            "channel_id": channel_id,
            "u_id": user_id
        }
        requests.post(url + "channel/invite/v2", json = pload)

    pload = {
        "token": auth_token,
        "name": "channel6",
        "is_public": True
    }
    response = requests.post(url + "channels/create/v2", json = pload)
    channel_id = response.json()["channel_id"]    
    for user_id in user_ids[1:-1]:
        pload = {
            "token": auth_token,
            "channel_id": channel_id,
            "u_id": user_id
        }
        requests.post(url + "channel/invite/v2", json = pload)
    
    response = requests.get(url + "channels/list/v2", params = {"token": member_token})
    assert response.status_code == Success_code
    assert(response.json() == {
        "channels": [
            {
                "channel_id": 2,
                "name": "channel2"
            },
            {
                "channel_id": 4,
                "name": "channel4"
            },
            {
                "channel_id": 6,
                "name": "channel6"
            }
        ]
        })

# Testing when user is not member of any channels
def test_channel_list_not_member(set_up):
    tokens, user_ids = set_up
    auth_token = tokens[0]
    member_token = tokens[1]

    # Creates 6 channels and invites users that aren't member_u_id
    pload = {
        "token": auth_token,
        "name": "channel1",
        "is_public": True
    }
    response = requests.post(url + "channels/create/v2", json = pload)
    channel_id = response.json()["channel_id"]
    for user_id in user_ids[2:-1]:
        pload = {
            "token": auth_token,
            "channel_id": channel_id,
            "u_id": user_id
        }
        requests.post(url + "channel/invite/v2", json = pload)

    pload = {
        "token": auth_token,
        "name": "channel2",
        "is_public": True
    }
    response = requests.post(url + "channels/create/v2", json = pload)
    channel_id = response.json()["channel_id"]
    for user_id in user_ids[2:-1]:
        pload = {
            "token": auth_token,
            "channel_id": channel_id,
            "u_id": user_id
        }
        requests.post(url + "channel/invite/v2", json = pload)

    pload = {
        "token": auth_token,
        "name": "channel3",
        "is_public": True
    }
    response = requests.post(url + "channels/create/v2", json = pload)
    channel_id = response.json()["channel_id"]
    for user_id in user_ids[2:-1]:
        pload = {
            "token": auth_token,
            "channel_id": channel_id,
            "u_id": user_id
        }
        requests.post(url + "channel/invite/v2", json = pload)

    pload = {
        "token": auth_token,
        "name": "channel4",
        "is_public": True
    }
    response = requests.post(url + "channels/create/v2", json = pload)
    channel_id = response.json()["channel_id"]
    for user_id in user_ids[2:-1]:
        pload = {
            "token": auth_token,
            "channel_id": channel_id,
            "u_id": user_id
        }
        requests.post(url + "channel/invite/v2", json = pload)

    pload = {
        "token": auth_token,
        "name": "channel5",
        "is_public": True
    }
    response = requests.post(url + "channels/create/v2", json = pload)
    channel_id = response.json()["channel_id"]
    for user_id in user_ids[2:-1]:
        pload = {
            "token": auth_token,
            "channel_id": channel_id,
            "u_id": user_id
        }
        requests.post(url + "channel/invite/v2", json = pload)
    
    pload = {
        "token": auth_token,
        "name": "channel6",
        "is_public": True
    }
    response = requests.post(url + "channels/create/v2", json = pload)
    channel_id = response.json()["channel_id"]
    for user_id in user_ids[2:-1]:
        pload = {
            "token": auth_token,
            "channel_id": channel_id,
            "u_id": user_id
        }
        requests.post(url + "channel/invite/v2", json = pload)

    response = requests.get(url + "channels/list/v2", params = {"token": member_token})
    assert response.status_code == Success_code
    assert(response.json() == {
        "channels": []
        })

# No channels in datastor
def test_empty_channels(set_up):
    tokens= set_up[0]
    auth_token = tokens[0]

    response = requests.get(url + "channels/list/v2", params = {"token": auth_token})
    assert response.status_code == Success_code
    assert(response.json() == {
        "channels": []
        }
    )

# Testing invalid auth user id
def test_invalid_user_id_access_error():
    invalid_token = "invalid_token"
    
    response = requests.get(url + "channels/list/v2", params = {"token": invalid_token})
    assert response.status_code == AccessError.code
