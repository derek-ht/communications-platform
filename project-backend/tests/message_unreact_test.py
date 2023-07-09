import pytest
import requests

# Importing from
from src.config import url
from src.error import AccessError, InputError
from src.helper import Success_code

def clear_v1():
    requests.delete(f'{url}clear/v1')

def auth_register_v2(email, password, name_first, name_last):
    pload = {
        'email': email,
        'password': password,
        'name_first': name_first,
        'name_last': name_last
    }
    return requests.post(f'{url}auth/register/v2', json = pload).json()

def channels_create_v2(token, name, is_public):
    pload = {
        'token': token,
        'name': name,
        'is_public': is_public
    }
    return requests.post(f'{url}channels/create/v2', json = pload).json()
    
def channel_join_v2(token, channel_id):
    pload = {
        'token': token,
        'channel_id': channel_id
    }
    requests.post(f'{url}channel/join/v2', json = pload)

def dm_create_v1(token, u_ids):
    pload = {
        'token': token,
        'u_ids': u_ids
    }
    return requests.post(f'{url}dm/create/v1', json = pload).json()

def message_send_v1(token, channel_id, message):
    pload = {
        'token': token,
        'channel_id': channel_id,
        'message': message
    }
    return requests.post(
        f'{url}message/send/v1', json = pload).json()['message_id']

def message_senddm_v1(token, dm_id, message):
    pload = {
        'token': token,
        'dm_id': dm_id,
        'message': message
    }
    return requests.post(
        f'{url}message/senddm/v1', json = pload).json()['message_id']

def channel_messages_v2(token, channel_id, start):
    pload = {
        'token': token,
        'channel_id': channel_id,
        'start': start
    }
    return requests.get(
        f'{url}channel/messages/v2', params = pload).json()['messages']

def dm_messages_v1(token, dm_id, start):
    pload = {
        'token': token,
        'dm_id': dm_id,
        'start': start
    }
    return requests.get(
        f'{url}dm/messages/v1', params = pload).json()['messages']

def message_react_v1(token, message_id, react_id):
    pload = {
        'token': token,
        'message_id': message_id,
        'react_id': react_id
    }
    return requests.post(f'{url}message/react/v1', json = pload).json()

def message_unreact_v1(token, message_id, react_id):
    pload = {
        'token': token,
        'message_id': message_id,
        'react_id': react_id
    }
    return requests.post(f'{url}message/unreact/v1', json = pload)

@pytest.fixture
def setup():
    clear_v1()

    user1 = auth_register_v2('history@gmail.com', 'testpass', 'Adam', 'Chen')
    user2 = auth_register_v2('physics@gmail.com', 'passtest', 'Kyle', 'Wu')

    # Setup channel
    ch = channels_create_v2(user1['token'], 'ch_name', True)
    channel_join_v2(user2['token'], ch['channel_id'])
    ch_msg1 = message_send_v1(user1['token'], ch['channel_id'], "1")
    ch_msg2 = message_send_v1(user2['token'], ch['channel_id'], "2")

    # Setup dm
    dm = dm_create_v1(user2['token'], [user1['auth_user_id']])
    dm_msg1 = message_senddm_v1(user1['token'], dm['dm_id'], "11")
    dm_msg2 = message_senddm_v1(user2['token'], dm['dm_id'], "22")

    # Adding reacts to msgs in ch
    message_react_v1(user1['token'], ch_msg1, 1)
    message_react_v1(user1['token'], ch_msg2, 1)
    message_react_v1(user2['token'], ch_msg1, 1)

    # Adding reacts to msgs in dm
    message_react_v1(user1['token'], dm_msg1, 1)
    message_react_v1(user1['token'], dm_msg2, 1)
    message_react_v1(user2['token'], dm_msg1, 1)

    return user1, user2, ch, ch_msg1, ch_msg2, dm, dm_msg1, dm_msg2

# Standard case - Ch
def test_messages_unreact_standard_ch(setup):
    user1 = setup[0]
    user2 = setup[1]
    ch = setup[2]
    ch_msg1 = setup[3]
    ch_msg2 = setup[4]

    response = message_unreact_v1(user1['token'], ch_msg2, 1)
    assert response.status_code == Success_code
    response = message_unreact_v1(user2['token'], ch_msg1, 1)
    assert response.status_code == Success_code

    messages = channel_messages_v2(user2['token'], ch['channel_id'], 0)
    assert messages[1]['reacts'] == [
        {
            'react_id': 1,
            'u_ids': [user1['auth_user_id']],
            'is_this_user_reacted': False
        }
    ]
    assert messages[0]['reacts'] == []

# Standard case - Dm
def test_messages_unreact_standard_dm(setup):
    user1 = setup[0]
    user2 = setup[1]
    dm = setup[5]
    dm_msg1 = setup[6]
    dm_msg2 = setup[7]

    response = message_unreact_v1(user1['token'], dm_msg1, 1)
    assert response.status_code == Success_code
    response = message_unreact_v1(user1['token'], dm_msg2, 1)
    assert response.status_code == Success_code

    messages = dm_messages_v1(user2['token'], dm['dm_id'], 0)
    assert messages[1]['reacts'] == [
        {
            'react_id': 1,
            'u_ids': [user2['auth_user_id']],
            'is_this_user_reacted': True
        }
    ]
    assert messages[0]['reacts'] == []

# User token invalid
def test_messages_unreact_invalid_token(setup):
    ch_msg1 = setup[3]

    response = message_unreact_v1('not_a_token', ch_msg1, 1)
    assert response.status_code == AccessError.code

# User tries to unreact when they aren't in the channel
def test_messages_unreact_user_not_in_ch(setup):
    user3 = auth_register_v2('biology@gmail.com', 'testtest', 'Tae', 'Pham')
    ch_msg1 = setup[3]

    response = message_unreact_v1(user3['token'], ch_msg1, 1)
    assert response.status_code == InputError.code

# User tries to unreact to an invalid msg_id
def test_messages_unreact_invalid_msg_id(setup):
    user1 = setup[0]

    not_msg_id = 20
    response = message_unreact_v1(user1['token'], not_msg_id, 1)
    assert response.status_code == InputError.code

# User not reacted to the message currently
def test_messages_unreact_not_reacted(setup):
    user1 = setup[0]
    dm_msg1 = setup[6]

    message_unreact_v1(user1['token'], dm_msg1, 1)
    response = message_unreact_v1(user1['token'], dm_msg1, 1)
    assert response.status_code == InputError.code

# React Id invalid
def test_messages_unreact_invalid_react_id(setup):
    user1 = setup[0]
    ch_msg1 = setup[3]

    invalid_react_id = -11
    response = message_unreact_v1(user1['token'], ch_msg1, invalid_react_id)
    assert response.status_code == InputError.code