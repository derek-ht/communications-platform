import pytest
import json
import requests
from src.error import AccessError, InputError
from src.helper import Success_code
from src.config import url

def auth_register_v2(email, password, fname, lname):
    pload = {
        "email": email,
        "password": password,
        "name_first": fname,
        "name_last": lname
    }
    response = requests.post(url + "auth/register/v2", json = pload)
    return response.json()

def channels_create_v2(token, name, is_public):
    pload = {
        "token": token, 
        "name": name, 
        "is_public": is_public
    }
    response = requests.post(url + "channels/create/v2", json = pload)
    return response.json()

def channel_invite_v2(token, channel_id, u_id):
    pload = {
        "token": token,
        "channel_id": channel_id,
        "u_id": u_id
    }
    response = requests.post(url + "channel/invite/v2", json = pload)
    return response.json()

def message_react_v1(token, message_id, react_id):
    pload = {
        "token": token,
        "message_id": message_id,
        "react_id": react_id
    }
    response = requests.post(url + "message/react/v1", json = pload)
    return response.json()

def message_send_v2(token, channel_id, message):
    pload = {
        "token": token,
        "channel_id": channel_id,
        "message": message
    }
    response = requests.post(url + "message/send/v1", json = pload)
    return response.json()

def dm_create_v1(token, u_ids):
    pload = {
        "token": token, 
        "u_ids": u_ids
    }
    response = requests.post(url + "dm/create/v1", json = pload)
    return response.json()

def message_senddm_v1(token, dm_id, message):
    pload = {
        "token": token,
        "dm_id": dm_id,
        "message": message
    }
    response = requests.post(url + "message/senddm/v1", json = pload)
    return response.json()

def notifications_get_v1(token):
    pload = {
        "token": token
    }
    response = requests.get(url + "notifications/get/v1", params = pload)
    return response

def dm_details_v1(token, dm_id):
    pload = {
        "token": token,
        "dm_id": dm_id
    }
    response = requests.get(url + "dm/details/v1", params = pload)
    return response.json()

def user_profile_v1(token, u_id):
    pload = {
        "token": token,
        "u_id": u_id
    }
    response = requests.get(url + "user/profile/v1", params = pload)
    return response.json()

# Sets up channels with two members
@pytest.fixture
def set_up_channel():
    requests.delete(f'{url}/clear/v1')

    details = auth_register_v2("1@email.com", "password", "name1", "surname1")
    token = details["token"]
    user_id = details["auth_user_id"]
    user_handle = user_profile_v1(token, user_id)["user"]["handle_str"]

    details = auth_register_v2("2@email.com", "password", "name2", "surname2")
    token2 = details["token"]
    user_id2 = details["auth_user_id"]
    user_handle2 = user_profile_v1(token2, user_id2)["user"]["handle_str"]

    channel_name = "channel_name1"
    response = channels_create_v2(token, channel_name, True)
    channel_id = response["channel_id"]

    channel_invite_v2(token, channel_id, user_id2)
    
    return channel_id, channel_name, token, user_handle, token2, user_handle2

# Sets up dm with two members
@pytest.fixture
def set_up_dm():
    requests.delete(f'{url}/clear/v1')

    details = auth_register_v2("1@email.com", "password", "name1", "surname1")
    token = details["token"]
    user_id = details["auth_user_id"]
    user_handle = user_profile_v1(token, user_id)["user"]["handle_str"]

    details = auth_register_v2("2@email.com", "password", "name2", "surname2")
    token2 = details["token"]
    user_id2 = details["auth_user_id"]
    user_handle2 = user_profile_v1(token2, user_id2)["user"]["handle_str"]

    response = dm_create_v1(token, [user_id2])
    dm_id = response["dm_id"]
    dm_name = dm_details_v1(token, dm_id)["name"]

    return dm_id, dm_name, token, user_handle, token2, user_handle2

# Tests notifications for adding to channel
def test_adding_to_channel(set_up_channel):
    channel_id, channel_name = set_up_channel[:2]
    user_handle, token2 = set_up_channel[3:5]
    response = notifications_get_v1(token2)
    assert response.status_code == Success_code

    notif_response = response.json()
    assert notif_response == {"notifications": [
            {
                "channel_id": channel_id, 
                "dm_id": -1, 
                "notification_message": f"{user_handle} added you to {channel_name}"
            }
        ]
    }

# Tests notifications for adding to dm
def test_adding_to_dm(set_up_dm):
    dm_id, dm_name = set_up_dm[:2]
    user_handle, token2 = set_up_dm[3:5]
    response = notifications_get_v1(token2)
    assert response.status_code == Success_code

    notif_response = response.json()

    assert notif_response == {"notifications": [
            {
                "channel_id": -1, 
                "dm_id": dm_id, 
                "notification_message": f"{user_handle} added you to {dm_name}"
            }
        ]
    }
    
    token = set_up_dm[2]
    assert notifications_get_v1(token).json() == {
        "notifications": []
    }

# Tests notification for tagging user in a channel
def test_tagging_user_in_messages(set_up_channel):
    channel_id, channel_name, token, user_handle, token2, user_handle2 = set_up_channel
    message = f"@{user_handle2} 123456789ABCDEFG"
    message_send_v2(token, channel_id, message)

    response = notifications_get_v1(token2)
    assert response.status_code == Success_code

    notif_response = response.json()
    assert notif_response == {"notifications": [
            {
                "channel_id": channel_id, 
                "dm_id": -1, 
                "notification_message": f"{user_handle} added you to {channel_name}"
            },
            {
                "channel_id": channel_id, 
                "dm_id": -1, 
                "notification_message": f"{user_handle} tagged you in {channel_name}: {message[:20]}"
            }
        ]
    }

# Tests notification for tagging user in a dm
def test_tagging_user_in_dms(set_up_dm):
    dm_id, dm_name, token, user_handle, token2, user_handle2 = set_up_dm
    message = f"@{user_handle2} 123456789ABCDEFG"
    message_senddm_v1(token, dm_id, message)

    response = notifications_get_v1(token2)
    assert response.status_code == Success_code

    notif_response = response.json()
    assert notif_response == {"notifications": [
            {
                "channel_id": -1, 
                "dm_id": dm_id, 
                "notification_message": f"{user_handle} added you to {dm_name}"
            },
            {
                "channel_id": -1, 
                "dm_id": dm_id, 
                "notification_message": f"{user_handle} tagged you in {dm_name}: {message[:20]}"
            }
        ]
    }

# Tests notifications when reacting to channel message
def test_react_in_channel(set_up_channel):
    channel_id, channel_name, token, user_handle, token2 = set_up_channel[:5]
    message = f"funny joke"
    message_id = message_send_v2(token2, channel_id, message)["message_id"]

    message_react_v1(token, message_id, 1)

    response = notifications_get_v1(token2)
    assert response.status_code == Success_code

    notif_response = response.json()
    assert notif_response == {"notifications": [
            {
                "channel_id": channel_id, 
                "dm_id": -1, 
                "notification_message": f"{user_handle} added you to {channel_name}"
            },
            {
                "channel_id": channel_id, 
                "dm_id": -1, 
                "notification_message": f"{user_handle} reacted to your message in {channel_name}"
            }
        ]
    }

# Tests notifications when reacting to dm message
def test_react_in_dm(set_up_dm):
    dm_id, dm_name, token, user_handle, token2 = set_up_dm[:5]
    message = f"funny joke"
    message_id = message_senddm_v1(token2, dm_id, message)["message_id"]

    message_react_v1(token, message_id, 1)

    response = notifications_get_v1(token2)
    assert response.status_code == Success_code

    notif_response = response.json()
    assert notif_response == {"notifications": [
            {
                "channel_id": -1, 
                "dm_id": dm_id, 
                "notification_message": f"{user_handle} added you to {dm_name}"
            },
            {
                "channel_id": -1, 
                "dm_id": dm_id, 
                "notification_message": f"{user_handle} reacted to your message in {dm_name}"
            }
        ]
    }

# Tests when there are 20 notifications
def test_20_notificaitons(set_up_channel):
    channel_id, channel_name, token, user_handle, token2, user_handle2 = set_up_channel
    
    correct_notifs = [{
        "channel_id": channel_id, 
        "dm_id": -1, 
        "notification_message": f"{user_handle} added you to {channel_name}"
    }]

    i = 0
    for i in range(19):
        message = f"@{user_handle2} message{i}"
        message_send_v2(token, channel_id, message)
        new_notif = {
            "channel_id": channel_id, 
            "dm_id": -1, 
            "notification_message": f"{user_handle} tagged you in {channel_name}: {message[:20]}"
        }
        correct_notifs.append(new_notif)

    response = notifications_get_v1(token2)
    assert response.status_code == Success_code

    notif_response = response.json()
    assert notif_response == {"notifications": correct_notifs}

# Tests when there are 21 notifications
def test_more_than_20_notificaiotns(set_up_channel):
    channel_id, channel_name, token, user_handle, token2, user_handle2 = set_up_channel
    
    correct_notifs = [{
        "channel_id": channel_id, 
        "dm_id": -1, 
        "notification_message": f"{user_handle} added you to {channel_name}"
    }]

    i = 0
    for i in range(21):
        message = f"@{user_handle2} {i}"
        message_send_v2(token, channel_id, message)
        new_notif = {
            "channel_id": channel_id, 
            "dm_id": -1, 
            "notification_message": f"{user_handle} tagged you in {channel_name}: {message[:20]}"
        }
        correct_notifs.append(new_notif)

    response = notifications_get_v1(token2)
    assert response.status_code == Success_code

    notif_response = response.json()
    assert notif_response == {"notifications": correct_notifs[-20:]}

# Tests invalid token
def test_invalid_token(set_up_channel):
    invalid_token = "invalid_token"
    response = notifications_get_v1(invalid_token)
    assert response.status_code == AccessError.code