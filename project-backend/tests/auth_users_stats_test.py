import pytest
import requests
import datetime
from time import sleep
from src.config import url
from src.helper import Success_code

def clear_v1():
    requests.delete(f'{url}clear/v1')
    return {}

def auth_register_v2(email, password, name_first, name_last):
    pload = {
        'email': email,
        'password': password,
        'name_first': name_first,
        'name_last': name_last
    }
    return requests.post(f'{url}auth/register/v2', json = pload).json()

def auth_login_v2(email, password):
    pload = {
        'email': email,
        'password': password,
    }
    return requests.post(f'{url}auth/login/v2', json = pload).json()

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
    return {}

def channel_leave_v1(token, channel_id):
    pload = {
        'token': token,
        'channel_id': channel_id
    }
    requests.post(f'{url}channel/leave/v1', json = pload)
    return {}

def channel_invite_v2(token, channel_id, u_id):
    pload = {
        'token': token,
        'channel_id': channel_id,
        'u_id': u_id
    }
    requests.post(f'{url}channel/invite/v2', json = pload)
    return {}

def user_stats_v1(token):
    pload = {
        'token': token
    }
    return requests.get(f'{url}user/stats/v1', params = pload)

def users_stats_v1(token):
    pload = {
        'token': token
    }
    return requests.get(f'{url}users/stats/v1', params = pload)

def dm_create_v1(token, id1, id2):
    pload = {
        'token': token,
        'u_ids': [id1, id2]
    }
    return requests.post(f'{url}dm/create/v1', json = pload).json()

def dm_remove_v1(token, dm_id):
    pload = {
        'token': token,
        'dm_id': dm_id
    }
    requests.delete(f'{url}dm/remove/v1', json = pload)
    return {}

def dm_leave_v1(token, dm_id):
    pload = {
        'token': token,
        'dm_id': dm_id
    }
    requests.post(f'{url}dm/leave/v1', json = pload)
    return {}

def message_send_v1(token, channel_id, message):
    pload = {
        "token": token,
        "channel_id": channel_id,
        "message": message
    }
    return requests.post(f'{url}message/send/v1', json = pload).json()

def message_sendlater_v1(token, channel_id, message, time_sent):
    pload = {
        'token': token,
        'channel_id': channel_id,
        'message': message,
        'time_sent': time_sent
    }
    return requests.post(f'{url}message/sendlater/v1', json = pload).json()

def message_sendlaterdm_v1(token, dm_id, message, time_sent):
    pload = {
        'token': token,
        'dm_id': dm_id,
        'message': message,
        'time_sent': time_sent
    }
    return requests.post(f'{url}message/sendlaterdm/v1', json = pload).json()

def standup_start_v1(token, channel_id, length):
    pload = {
        'token': token,
        'channel_id': channel_id,
        'length': length
    }
    return requests.post(f'{url}standup/start/v1', json = pload).json()

def standup_send_v1(token, channel_id, message):
    pload = {
        'token': token,
        'channel_id': channel_id,
        'message': message
    }
    return requests.post(f'{url}standup/start/v1', json = pload).json()

def message_remove_v1(token, message_id):
    pload = {
        'token': token,
        'message_id': message_id
    }
    requests.delete(f'{url}message/remove/v1', json = pload)
    return {}

def message_edit_v1(token, message_id, message):
    pload = {
        'token': token,
        'message_id': message_id,
        'message': message
    }
    requests.put(f'{url}message/edit/v1', json = pload)
    return {}

def message_share_v1(token, og_message_id, message, channel_id, dm_id):
    pload = {
        'token': token,
        'og_message_id': og_message_id,
        'message': message,
        'channel_id': channel_id,
        'dm_id': dm_id
    }
    return requests.post(f'{url}message/share/v1', json = pload).json()

def message_senddm_v1(token, dm_id, message):
    pload = {
        "token": token,
        "dm_id": dm_id,
        "message": message
    }
    return requests.post(f'{url}message/senddm/v1', json = pload).json()

def admin_user_remove_v1(token, u_id):
    pload = {
        "token": token,
        "u_id": u_id
    }
    requests.delete(f'{url}admin/user/remove/v1', json = pload)
    return {}

@pytest.fixture
def reg_multi_users():
    clear_v1()
    users = {}
    for i in range(1,4):
        email = f'{i}a@gmail.com'
        password = "password"
        name_first = f"{i}"
        name_last = f"{i}"
        users[f'{i}'] = auth_register_v2(email, password, name_first, name_last)
    return users

@pytest.fixture
def channel_set_up(reg_multi_users):
    users = reg_multi_users
    owner_token = users['1']['token']
    member_token = users['2']['token']
    channel_id = channels_create_v2(owner_token, 'name', True)['channel_id']
    channel_join_v2(member_token, channel_id)
    return channel_id, users

@pytest.fixture
def dm_set_up(reg_multi_users):
    users = reg_multi_users
    dm = dm_create_v1(\
        users['1']['token'], users['2']['auth_user_id'], users['3']['auth_user_id'])
    return dm['dm_id'], users

'''
==============================================================================
'''

# STREAM
# create channel and asserts the workspace_stats updates
def test_users_stats_channel_create_owner(channel_set_up):
    users = channel_set_up[1]
    response = users_stats_v1(users['1']['token'])
    assert response.status_code == Success_code
    assert len(response.json()['workspace_stats']['channels_exist']) == 2

# join channel and asserts the workspace_stats updates
def test_users_stats_channel_join_member(channel_set_up):
    users = channel_set_up[1]
    response = users_stats_v1(users['2']['token'])
    assert response.status_code == Success_code
    assert len(response.json()['workspace_stats']['channels_exist']) == 2
    assert response.json()['workspace_stats']['channels_exist'][-1]['num_channels_exist'] == 1

# invite channel and asserts the workspace_stats updates
def test_users_stats_channel_invite_member(channel_set_up):
    cid, users = channel_set_up
    channel_invite_v2(users['2']['token'], cid, users['3']['auth_user_id'])
    response = users_stats_v1(users['3']['token'])
    assert response.status_code == Success_code
    assert len(response.json()['workspace_stats']['channels_exist']) == 2
    assert response.json()['workspace_stats']['channels_exist'][-1]['num_channels_exist'] == 1

# leave channel and asserts the workspace_stats updates
def test_users_stats_channel_leave_member(channel_set_up):
    cid, users = channel_set_up
    channel_leave_v1(users['1']['token'], cid)
    response = users_stats_v1(users['1']['token'])
    assert response.status_code == Success_code
    assert len(response.json()['workspace_stats']['channels_exist']) == 2
    assert response.json()['workspace_stats']['channels_exist'][-1]['num_channels_exist'] == 1

'''
==============================================================================
'''

# STREAM
# creates dm and ensures workspace stats updates
def test_users_stats_dm_create(dm_set_up):
    users = dm_set_up[1]
    response = users_stats_v1(users['1']['token'])
    assert response.status_code == Success_code
    assert len(response.json()['workspace_stats']['dms_exist']) == 2
    assert response.json()['workspace_stats']['dms_exist'][-1]['num_dms_exist'] == 1

# removes dm and ensures all messages are removed and the users in the dm are
# also removed
def test_users_stats_dm_remove(dm_set_up):
    dm_id, users = dm_set_up    
    for i in range(1,6):
        message_senddm_v1(users['1']['token'], dm_id, f"{i}pls")
        message_senddm_v1(users['2']['token'], dm_id, f"{i}work")
        message_senddm_v1(users['3']['token'], dm_id, f"{i}beg")
        
    response = users_stats_v1(users['1']['token'])
    assert response.status_code == Success_code
    assert len(response.json()['workspace_stats']['messages_exist']) == 16
    assert response.json()['workspace_stats']['messages_exist'][-1]['num_messages_exist'] == 15

    dm_remove_v1(users['1']['token'], dm_id)
    response = users_stats_v1(users['1']['token'])
    assert response.status_code == Success_code
    assert len(response.json()['workspace_stats']['messages_exist']) == 31
    assert len(response.json()['workspace_stats']['dms_exist']) == 3
    assert response.json()['workspace_stats']['dms_exist'][-1]['num_dms_exist'] == 0

# Checks that workspace_stats updates after a dm is removed after all users
# in that dm leave
def test_users_stats_dm_leave(dm_set_up):
    dm_id, users = dm_set_up
    dm_leave_v1(users['1']['token'], dm_id)
    dm_leave_v1(users['2']['token'], dm_id)
    dm_leave_v1(users['3']['token'], dm_id)
    response = users_stats_v1(users['1']['token'])
    assert len(response.json()['workspace_stats']['dms_exist']) == 3
    assert response.json()['workspace_stats']['dms_exist'][-1]['num_dms_exist'] == 0

'''
==============================================================================
'''

# STREAM
# send channel
def test_users_stats_messages_channel_sent(channel_set_up):
    cid, users = channel_set_up
    message_send_v1(users['2']['token'], cid, "work")
    response = users_stats_v1(users['2']['token'])
    assert response.status_code == Success_code
    assert len(response.json()['workspace_stats']['messages_exist']) == 2

# edit message in channel to "" (removing it)
def test_users_stats_messages_channel_edit(channel_set_up):
    cid, users = channel_set_up
    m_id = message_send_v1(users['2']['token'], cid, "work")['message_id']
    message_edit_v1(users['2']['token'], m_id, "")
    response = users_stats_v1(users['2']['token'])
    assert response.status_code == Success_code
    assert len(response.json()['workspace_stats']['messages_exist']) == 3
    assert response.json()['workspace_stats']['messages_exist'][-1]['num_messages_exist'] == 0

# remove message in channel
def test_users_stats_messages_channel_remove(channel_set_up):
    cid, users = channel_set_up
    m_id = message_send_v1(users['2']['token'], cid, "work")['message_id'] 
    message_remove_v1(users['2']['token'], m_id)
    response = users_stats_v1(users['2']['token'])
    assert response.status_code == Success_code
    assert len(response.json()['workspace_stats']['messages_exist']) == 3
    assert response.json()['workspace_stats']['messages_exist'][-1]['num_messages_exist'] == 0

# send message in dm
def test_users_stats_messages_dm_sent(dm_set_up):
    dm_id, users = dm_set_up
    message_senddm_v1(users['1']['token'], dm_id, "work")
    response = users_stats_v1(users['1']['token'])
    assert response.status_code == Success_code
    assert len(response.json()['workspace_stats']['messages_exist']) == 2

# edit message in dm to "" (removing it)
def test_users_stats_messages_dm_edit(dm_set_up):
    dm_id, users = dm_set_up
    m_id = message_senddm_v1(users['1']['token'], dm_id, "work")["message_id"]
    message_edit_v1(users['1']['token'], m_id, "")
    response = users_stats_v1(users['1']['token'])
    assert response.status_code == Success_code
    assert len(response.json()['workspace_stats']['messages_exist']) == 3
    assert response.json()['workspace_stats']['messages_exist'][-1]['num_messages_exist'] == 0

# remove message in dm
def test_users_stats_messages_dm_remove(dm_set_up):
    dm_id, users = dm_set_up
    m_id = message_senddm_v1(users['1']['token'], dm_id, "work")["message_id"]
    message_remove_v1(users['1']['token'], m_id)
    response = users_stats_v1(users['1']['token'])
    assert response.status_code == Success_code
    assert len(response.json()['workspace_stats']['messages_exist']) == 3
    assert response.json()['workspace_stats']['messages_exist'][-1]['num_messages_exist'] == 0

def test_users_stats_messages_sendlater(channel_set_up):
    cid, users = channel_set_up
    time = datetime.datetime.now().timestamp()
    message_sendlater_v1(users['1']['token'], cid, 'hi', time + 2)
    sleep(3)
    response = users_stats_v1(users['1']['token'])
    assert response.status_code == Success_code
    assert len(response.json()['workspace_stats']['messages_exist']) == 2
    assert response.json()['workspace_stats']['messages_exist'][-1]['num_messages_exist'] == 1

def test_users_stats_messages_sendlaterdm_remove(dm_set_up):
    dm_id, users = dm_set_up
    time = datetime.datetime.now().timestamp()
    message_sendlaterdm_v1(users['1']['token'], dm_id, 'hi', time + 2)
    sleep(3)
    response = users_stats_v1(users['1']['token'])
    assert response.status_code == Success_code
    assert len(response.json()['workspace_stats']['messages_exist']) == 2
    assert response.json()['workspace_stats']['messages_exist'][-1]['num_messages_exist'] == 1
    dm_remove_v1(users['1']['token'], dm_id)
    response = users_stats_v1(users['1']['token'])
    assert response.status_code == Success_code
    assert len(response.json()['workspace_stats']['messages_exist']) == 3
    assert response.json()['workspace_stats']['messages_exist'][-1]['num_messages_exist'] == 0

def test_users_stats_messages_share_channel(channel_set_up):
    cid, users = channel_set_up
    dm_id = dm_create_v1(users['1']['token'], 2, 3)['dm_id']

    m_id = message_send_v1(users['1']['token'], cid, "work")['message_id']
    message_share_v1(users['1']['token'], m_id, '222', cid, -1)
    response = users_stats_v1(users['1']['token'])
    assert response.status_code == Success_code
    assert len(response.json()['workspace_stats']['messages_exist']) == 3
    assert response.json()['workspace_stats']['messages_exist'][-1]['num_messages_exist'] == 2

    message_share_v1(users['1']['token'], m_id, '333', -1, dm_id)
    response = users_stats_v1(users['1']['token'])
    assert response.status_code == Success_code
    assert len(response.json()['workspace_stats']['messages_exist']) == 4
    assert response.json()['workspace_stats']['messages_exist'][-1]['num_messages_exist'] == 3

def test_users_stats_messages_share_dm(channel_set_up):
    cid, users = channel_set_up
    dm_id = dm_create_v1(users['1']['token'], 2, 3)['dm_id']
    m_id = message_senddm_v1(users['1']['token'], dm_id, "work")["message_id"]

    message_share_v1(users['1']['token'], m_id, '222', cid, -1)
    response = users_stats_v1(users['1']['token'])
    assert response.status_code == Success_code
    assert len(response.json()['workspace_stats']['messages_exist']) == 3
    assert response.json()['workspace_stats']['messages_exist'][-1]['num_messages_exist'] == 2

    message_share_v1(users['1']['token'], m_id, '222', cid, -1)
    response = users_stats_v1(users['1']['token'])
    assert response.status_code == Success_code
    assert len(response.json()['workspace_stats']['messages_exist']) == 4
    assert response.json()['workspace_stats']['messages_exist'][-1]['num_messages_exist'] == 3

def test_users_stats_messages_standup(channel_set_up):
    cid, users = channel_set_up
    standup_start_v1(users['1']['token'], cid, 2)
    standup_send_v1(users['1']['token'], cid, '1')
    standup_send_v1(users['1']['token'], cid, '2')
    sleep(3)
    response = users_stats_v1(users['1']['token'])
    assert response.status_code == Success_code
    assert len(response.json()['workspace_stats']['messages_exist']) == 2
    assert response.json()['workspace_stats']['messages_exist'][-1]['num_messages_exist'] == 1

'''
==============================================================================
'''

# Update stats utilization rate
def test_users_stats_utilization_rate_channel(channel_set_up):
    cid, users = channel_set_up
    response = users_stats_v1(users['2']['token'])
    assert response.status_code == Success_code
    assert response.json()['workspace_stats']['utilization_rate'] == (2/3)

    channel_leave_v1(users['2']['token'], cid)
    response = users_stats_v1(users['2']['token'])
    assert response.status_code == Success_code
    assert response.json()['workspace_stats']['utilization_rate'] == (1/3)    

def test_users_stats_utilization_rate_admin_remove(channel_set_up):
    users = channel_set_up[1]
    admin_user_remove_v1(users['1']['token'], users['2']['auth_user_id'])
    response = users_stats_v1(users['3']['token'])
    assert response.status_code == Success_code
    assert response.json()['workspace_stats']['utilization_rate'] == (1/2)

def test_users_stats_utilization_rate_dm(dm_set_up):
    dm_id, users = dm_set_up
    response = users_stats_v1(users['2']['token'])
    assert response.status_code == Success_code
    assert response.json()['workspace_stats']['utilization_rate'] == (3/3)

    dm_leave_v1(users['3']['token'], dm_id)
    response = users_stats_v1(users['2']['token'])
    assert response.status_code == Success_code
    assert response.json()['workspace_stats']['utilization_rate'] == (2/3)


def test_users_stats_utilization_rate_dm_channel(dm_set_up):
    dm_id, users = dm_set_up
    dm_leave_v1(users['3']['token'], dm_id)
    cid = channels_create_v2(users['3']['token'], 'name', True)['channel_id']
    response = users_stats_v1(users['2']['token'])
    assert response.status_code == Success_code
    assert response.json()['workspace_stats']['utilization_rate'] == (3/3)

    channel_leave_v1(users['3']['token'], cid)
    response = users_stats_v1(users['2']['token'])
    assert response.status_code == Success_code
    assert response.json()['workspace_stats']['utilization_rate'] == (2/3)

    admin_user_remove_v1(users['1']['token'], users['2']['auth_user_id'])
    response = users_stats_v1(users['3']['token'])
    assert response.status_code == Success_code
    assert response.json()['workspace_stats']['utilization_rate'] == (1/2)

'''
==============================================================================
'''

def test_users_stats_access_error(reg_multi_users):
    users = reg_multi_users
    admin_user_remove_v1(users['1']['token'], users['2']['auth_user_id'])
    response = users_stats_v1(users['2']['token'])
    assert response.status_code == 403