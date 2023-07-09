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

def message_pin_v1(token, message_id):
    pload = {
        'token': token,
        'message_id': message_id
    }
    return requests.post(f'{url}message/pin/v1', json = pload)

def message_unpin_v1(token, message_id):
    pload = {
        'token': token,
        'message_id': message_id
    }
    return requests.post(f'{url}message/unpin/v1', json = pload)

@pytest.fixture
def setup():
    clear_v1()

    user1 = auth_register_v2('history@gmail.com', 'testpass', 'Adam', 'Chen')
    user2 = auth_register_v2('physics@gmail.com', 'passtest', 'Kyle', 'Wu')

    # Setup channel msgs
    ch = channels_create_v2(user1['token'], 'ch_name', True)
    channel_join_v2(user2['token'], ch['channel_id'])
    ch_msg1 = message_send_v1(user1['token'], ch['channel_id'], "1")
    ch_msg2 = message_send_v1(user2['token'], ch['channel_id'], "2")
    ch_msg3 = message_send_v1(user1['token'], ch['channel_id'], "3")

    # Setup dm msgs
    dm = dm_create_v1(user2['token'], [user1['auth_user_id']])
    dm_msg1 = message_senddm_v1(user1['token'], dm['dm_id'], "11")
    dm_msg2 = message_senddm_v1(user2['token'], dm['dm_id'], "22")
    dm_msg3 = message_senddm_v1(user2['token'], dm['dm_id'], "33")

    # Setting up pins in Ch
    message_pin_v1(user1['token'], ch_msg1)
    message_pin_v1(user1['token'], ch_msg2)

    # Setting up pins in Dm
    message_pin_v1(user2['token'], dm_msg1)
    message_pin_v1(user2['token'], dm_msg3)

    return user1, user2, ch, ch_msg1, ch_msg2, ch_msg3, \
        dm, dm_msg1, dm_msg2, dm_msg3

# Standard case - Chs
def test_message_unpin_standard_ch(setup):
    user1 = setup[0]
    user2 = setup[1]
    ch = setup[2]
    ch_msg1 = setup[3]

    response = message_unpin_v1(user1['token'], ch_msg1)
    assert response.status_code == Success_code

    messages = channel_messages_v2(user2['token'], ch['channel_id'], 0)
    assert messages[0]['is_pinned'] == False
    assert messages[1]['is_pinned'] == True
    assert messages[2]['is_pinned'] == False

# Standard case - Dms
def test_message_unpin_standard_dm(setup):
    user1 = setup[0]
    user2 = setup[1]
    dm = setup[6]
    dm_msg3 = setup[9]

    response = message_unpin_v1(user2['token'], dm_msg3)
    assert response.status_code == Success_code

    messages = dm_messages_v1(user1['token'], dm['dm_id'], 0)
    assert messages[0]['is_pinned'] == False
    assert messages[1]['is_pinned'] == False
    assert messages[2]['is_pinned'] == True

# User token invalid
def test_message_unpin_invalid_token(setup):
    ch_msg1 = setup[3]

    response = message_unpin_v1('not_a_token', ch_msg1)
    assert response.status_code == AccessError.code

# User does not have owner perms
def test_message_unpin_user_no_perms(setup):
    user1 = setup[0]
    user2 = setup[1]
    ch_msg1 = setup[3]
    dm_msg1 = setup[7]

    response = message_unpin_v1(user2['token'], ch_msg1)
    assert response.status_code == AccessError.code
    response = message_unpin_v1(user1['token'], dm_msg1)
    assert response.status_code == AccessError.code

# User not in the Ch
def test_message_unpin_user_not_in_ch(setup):
    user3 = auth_register_v2('biology@gmail.com', 'testtest', 'Tae', 'Pham')
    ch_msg1 = setup[3]

    response = message_unpin_v1(user3['token'], ch_msg1)
    assert response.status_code == InputError.code

# Invalid message Id
def test_message_unpin_invalid_message_id(setup):
    user1 = setup[0]

    not_msg_id = 20
    response = message_unpin_v1(user1['token'], not_msg_id)
    assert response.status_code == InputError.code

# Message already unpinned
def test_message_unpin_already_unpinned(setup):
    user1 = setup[0]
    user2 = setup[1]
    ch_msg1 = setup[3]
    dm_msg1 = setup[7]

    message_unpin_v1(user2['token'], dm_msg1)
    response = message_unpin_v1(user2['token'], dm_msg1)
    assert response.status_code == InputError.code
    message_unpin_v1(user1['token'], ch_msg1)
    response = message_unpin_v1(user1['token'], ch_msg1)
    assert response.status_code == InputError.code