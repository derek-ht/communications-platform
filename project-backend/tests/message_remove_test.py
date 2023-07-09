import pytest
from src.config import url
import requests
from src.error import AccessError, InputError
from src.helper import Success_code

# Sets up channel with the owners message in it and return owner's token
@pytest.fixture
def set_up_owner():
    requests.delete(url + "clear/v1")

    pload = {
        "email": "1@email.com",
        "password": "password",
        "name_first": "name1",
        "name_last": "surname1"
    }

    response = requests.post(url + "auth/register/v2", json = pload)
    token = response.json()["token"]

    pload = {
        "token": token,
        "name": "channel_1",
        "is_public": False
    }
    response = requests.post(url + "channels/create/v2", json = pload)
    channel_id = response.json()["channel_id"]

    message = "message_example"
    pload = {
        "token": token,
        "channel_id": channel_id,
        "message": message
    }
    response = requests.post(url + "message/send/v1", json = pload)
    message_id = response.json()["message_id"]

    return token, message_id, channel_id

# Sets up channel with a members message in it and return the member's token and owners token
@pytest.fixture
def set_up_member():
    requests.delete(url + "clear/v1")

    pload = {
        "email": "1@email.com",
        "password": "password",
        "name_first": "name1",
        "name_last": "surname1"
    }
    response = requests.post(url + "auth/register/v2", json = pload)
    auth_token = response.json()["token"]

    pload = {
        "email": "2@email.com",
        "password": "password",
        "name_first": "name2",
        "name_last": "surname2"
    }
    response = requests.post(url + "auth/register/v2", json = pload)
    member_token = response.json()["token"]
    member_u_id = response.json()['auth_user_id']

    pload = {
        "token": auth_token,
        "name": "channel_1",
        "is_public": False
    }
    response = requests.post(url + "channels/create/v2", json = pload)
    channel_id = response.json()["channel_id"]

    pload = {
        "token": auth_token,
        "channel_id": channel_id,
        "u_id": member_u_id
    }
    requests.post(url + "channel/invite/v2", json = pload)

    message = "message_example"
    pload = {
        "token": member_token,
        "channel_id": channel_id,
        "message": message
    }
    response = requests.post(url + "message/send/v1", json = pload)
    message_id = response.json()["message_id"]

    return member_token, message_id, channel_id, auth_token

# Sets up dm with a members message in it and return the member's token
@pytest.fixture
def set_up_member_dm():
    requests.delete(url + "clear/v1")
    
    pload = {
        "email": "1@email.com",
        "password": "password",
        "name_first": "name1",
        "name_last": "surname1"
    }
    response = requests.post(url + "auth/register/v2", json = pload)
    auth_token = response.json()["token"]
    
    pload = {
        "email": "2@email.com",
        "password": "password",
        "name_first": "name2",
        "name_last": "surname2"
    }
    response = requests.post(url + "auth/register/v2", json = pload)
    member_token = response.json()["token"]
    member_u_id = response.json()["auth_user_id"]

    pload = {
        "token": auth_token,
        "u_ids": [member_u_id]
    }
    response = requests.post(url + "dm/create/v1", json = pload)
    dm_id = response.json()["dm_id"]

    message = "message_example"
    pload = {
        "token": member_token,
        "dm_id": dm_id,
        "message": message
    }
    response = requests.post(url + "message/senddm/v1", json = pload)
    message_id = response.json()["message_id"]

    return member_token, message_id, dm_id


# Sets up dm with the owner's message in it and return the member's token
@pytest.fixture
def set_up_member_dm_with_owner_message():
    requests.delete(url + "clear/v1")

    pload = {
        "email": "1@email.com",
        "password": "password",
        "name_first": "name1",
        "name_last": "surname1"
    }
    response = requests.post(url + "auth/register/v2", json = pload)
    auth_token = response.json()["token"]
    
    pload = {
        "email": "2@email.com",
        "password": "password",
        "name_first": "name2",
        "name_last": "surname2"
    }
    response = requests.post(url + "auth/register/v2", json = pload)
    member_token = response.json()["token"]
    member_u_id = response.json()["auth_user_id"]

    pload = {
        "token": auth_token,
        "u_ids": [member_u_id]
    }
    response = requests.post(url + "dm/create/v1", json = pload)
    dm_id = response.json()["dm_id"]

    message = "message_example"
    pload = {
        "token": auth_token,
        "dm_id": dm_id,
        "message": message
    }
    response = requests.post(url + "message/senddm/v1", json = pload)
    print(response.json())
    message_id = response.json()["message_id"]

    return member_token, message_id, dm_id, auth_token

# Tests when message id is from a dm the auth user has not joined
def test_message_id_of_different_dm(set_up_member_dm_with_owner_message):
    member_token = set_up_member_dm_with_owner_message[0]
    owner_token = set_up_member_dm_with_owner_message[3]

    pload = {
        "email": "3@email.com",
        "password": "password",
        "name_first": "name3",
        "name_last": "surname3"
    }
    response = requests.post(url + "auth/register/v2", json = pload)
    other_user_id = response.json()["auth_user_id"]
    
    pload = {
        "token": owner_token,
        "u_ids": [other_user_id]
    }
    response = requests.post(url + "dm/create/v1", json = pload)
    other_dm_id = response.json()["dm_id"]

    pload = {
        "token": owner_token,
        "dm_id": other_dm_id,
        "message": "message"
    }
    response = requests.post(url + "message/senddm/v1", json = pload)
    other_message_id = response.json()["message_id"]

    pload = {
        "token": member_token,
        "message_id": other_message_id,
    }
    response = requests.delete(url + "message/remove/v1", json = pload)
    assert response.status_code == InputError.code

# Tests a member removing other member's dm
def test_remove_others_dm_as_member(set_up_member_dm_with_owner_message):
    token, message_id, dm_id = set_up_member_dm_with_owner_message[0:3]
    
    pload = {
        "token": token,
        "dm_id": dm_id,
        "start": 0
    }
    response = requests.get(url + "dm/messages/v1", params = pload)
    messages = response.json()["messages"]
    assert messages[0]["message"] == "message_example"

    pload = {
        "token": token,
        "message_id": message_id,
    }
    response = requests.delete(url + "message/remove/v1", json = pload)
    assert response.status_code == AccessError.code

# Tests a member removing their own dm
def test_remove_own_dm_as_member(set_up_member_dm):
    token, message_id, dm_id = set_up_member_dm
    
    pload = {
        "token": token,
        "dm_id": dm_id,
        "start": 0
    }
    response = requests.get(url + "dm/messages/v1", params = pload)
    messages = response.json()["messages"]
    assert messages[0]["message"] == "message_example"
    
    pload = {
        "token": token,
        "message_id": message_id,
    }
    response = requests.delete(url + "message/remove/v1", json = pload)
    assert response.status_code == Success_code
    assert response.json() == {}

    pload = {
        "token": token,
        "dm_id": dm_id,
        "start": 0
    }
    response = requests.get(url + "dm/messages/v1", params = pload)
    messages = response.json()["messages"]
    assert messages == []

# Tests removing dm with a dm id that doesn't exist
def test_nonexistent_dm_id(set_up_member_dm):
    token, message_id, dm_id = set_up_member_dm
    invalid_message_id = message_id + 1

    pload = {
        "token": token,
        "dm_id": dm_id,
        "start": 0
    }
    response = requests.get(url + "dm/messages/v1", params = pload)
    messages = response.json()["messages"]
    assert messages[0]["message"] == "message_example"

    pload = {
        "token": token,
        "message_id": invalid_message_id,
    }
    response = requests.delete(url + "message/remove/v1", json = pload)
    assert response.status_code == InputError.code

# Tests a member removing their own message
def test_remove_own_message_as_member(set_up_member):
    token, message_id, channel_id = set_up_member[0:3]
    
    pload = {
        "token": token,
        "channel_id": channel_id,
        "start": 0
    }
    response = requests.get(url + "channel/messages/v2", params = pload)
    message = response.json()["messages"][0]
    assert message["message"] == "message_example"
    
    pload = {
        "token": token,
        "message_id": message_id,
    }
    response = requests.delete(url + "message/remove/v1", json = pload)
    assert response.status_code == Success_code
    assert response.json() == {}

    pload = {
        "token": token,
        "channel_id": channel_id,
        "start": 0
    }
    response = requests.get(url + "channel/messages/v2", params = pload)
    messages = response.json()["messages"]
    assert messages == []

# Tests owner removing their own message
def test_remove_own_message_as_owner(set_up_owner):
    token, message_id, channel_id = set_up_owner
    
    pload = {
        "token": token,
        "channel_id": channel_id,
        "start": 0
    }
    response = requests.get(url + "channel/messages/v2", params = pload)
    message = response.json()["messages"][0]
    print(message)
    assert message["message"] == "message_example"
    
    pload = {
        "token": token,
        "message_id": message_id,
    }
    response = requests.delete(url + "message/remove/v1", json = pload)
    assert response.status_code == Success_code
    assert response.json() == {}

    pload = {
        "token": token,
        "channel_id": channel_id,
        "start": 0
    }
    response = requests.get(url + "channel/messages/v2", params = pload)
    print(response.json())
    messages = response.json()["messages"]
    assert messages == []

# Tests the owner removing another members message
def test_owner_remove_others_message(set_up_member):
    message_id, channel_id, owner_token = set_up_member[1:4]

    pload = {
        "token": owner_token,
        "channel_id": channel_id,
        "start": 0
    }
    response = requests.get(url + "channel/messages/v2", params = pload)
    messages = response.json()["messages"]
    assert messages[0]["message"] == "message_example"

    pload = {
        "token": owner_token,
        "message_id": message_id
    }
    response = requests.delete(url + "message/remove/v1", json = pload)
    assert response.status_code == Success_code
    assert response.json() == {}

    pload = {
        "token": owner_token,
        "channel_id": channel_id,
        "start": 0
    }
    response = requests.get(url + "channel/messages/v2", params = pload)
    messages = response.json()["messages"]
    assert messages == []

# Tests trying to remove message with nonexistent message id
def test_nonexistent_message_id(set_up_member):
    token, message_id = set_up_member[0:2]
    
    invalid_message_id = message_id + 1

    pload = {
        "token": token,
        "message_id": invalid_message_id
    }
    response = requests.delete(url + "message/remove/v1", json = pload)
    assert response.status_code == InputError.code

# Tests when message id is from a channel the auth user has not joined
def test_message_id_of_different_channel(set_up_member):
    token = set_up_member[0]

    pload = {
        "email": "3@email.com",
        "password": "password",
        "name_first": "name3",
        "name_last": "surname3"
    }
    response = requests.post(url + "auth/register/v2", json = pload)
    other_user_token = response.json()["token"]
    
    pload = {
        "token": other_user_token,
        "name": "channel_2",
        "is_public": False
    }
    response = requests.post(url + "channels/create/v2", json = pload)
    other_channel_id = response.json()["channel_id"]

    pload = {
        "token": other_user_token,
        "channel_id": other_channel_id,
        "message": "message"
    }
    response = requests.post(url + "message/send/v1", json = pload)
    other_message_id = response.json()["message_id"]

    pload = {
        "token": token,
        "message_id": other_message_id
    }
    response = requests.delete(url + "message/remove/v1", json = pload)
    assert response.status_code == InputError.code

# Tests member of channel removing another person's message
def test_remove_others_message_as_member(set_up_owner):
    owner_token, message_id, channel_id = set_up_owner

    # Registers member and adds to the channel
    pload = {
        "email": "2@email.com",
        "password": "password",
        "name_first": "name2",
        "name_last": "surname2"
    }
    response = requests.post(url + "auth/register/v2", json = pload)
    member_token = response.json()["token"]
    member_u_id = response.json()["auth_user_id"]

    pload = {
        "token": owner_token,
        "channel_id": channel_id,
        "u_id": member_u_id
    }
    requests.post(url + "channel/invite/v2", json = pload)

    pload = {
        "token": member_token,
        "message_id": message_id
    }
    response = requests.delete(url + "message/remove/v1", json = pload)
    assert response.status_code == AccessError.code

# Tests invalid token
def test_invalid_token(set_up_owner):
    message_id = set_up_owner[1]

    invalid_token = "invalid_token_string"
    
    pload = {
        "token": invalid_token,
        "message_id": message_id
    }
    response = requests.delete(url + "message/remove/v1", json = pload)
    assert response.status_code == AccessError.code

