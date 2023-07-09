import pytest
import requests
from src.config import url
from src.error import AccessError, InputError
from src.helper import Success_code

@pytest.fixture
def token():
    requests.delete(f'{url}clear/v1')
    response = requests.post(f'{url}auth/register/v2', json = {
    'email': 'adamchen@hotmail.com',
    'password': 'jinladen',
    'name_first': 'kyle',
    'name_last': 'jeremy'})
    user_token = response.json()['token']
    return user_token

@pytest.fixture
def reg_multi_users():
    requests.delete(f'{url}clear/v1')
    users = {}
    for i in range(1, 4):
        pload = {
            'email': f"{i}@gmail.com", 
            'password': "password", 
            'name_first': f"{i}", 
            'name_last': f"{i}"
        }
        response = requests.post(f'{url}auth/register/v2', json = pload)
        users[f"{i}"] = response.json()
    return users

# user setname function
def test_setname_valid_token(token):
    requests.post(f'{url}auth/logout/v1', json = {'token': token})
    pload = {
        'token': token,
        'name_first': 'derek',
        'name_last': 'derek'
    }
    response = requests.put(f'{url}user/profile/setname/v1', json = pload)
    assert response.status_code == AccessError.code

def test_setname_null_both(token):
    pload = {
        'token': token,
        'name_first': '',
        'name_last': ''
    }
    response = requests.put(f'{url}user/profile/setname/v1', json = pload)
    assert response.status_code == InputError.code

def test_setname_null_first(token):
    pload = {
        'token': token,
        'name_first': '',
        'name_last': 'derek'
    }
    response = requests.put(f'{url}user/profile/setname/v1', json = pload)
    assert response.status_code == InputError.code

def test_setname_null_last(token):
    pload = {
        'token': token,
        'name_first': 'derek',
        'name_last': ''
    }
    response = requests.put(f'{url}user/profile/setname/v1', json = pload)
    assert response.status_code == InputError.code

def test_setname_valid_first_1(token):
    pload = {
        'token': token,
        'name_first': 'd',
        'name_last': 'derek'
    }
    response = requests.put(f'{url}user/profile/setname/v1', json = pload)
    assert response.status_code == Success_code
    assert response.json() == {}

def test_setname_valid_first_50(token):
    pload = {
        'token': token,
        'name_first': 'derekderekderekderekderekderekderekderekderekderek',
        'name_last': 'derek'
    }
    response = requests.put(f'{url}user/profile/setname/v1', json = pload)
    assert response.status_code == Success_code
    assert response.json() == {}

def test_setname_valid_first_51(token):
    pload = {
        'token': token,
        'name_first': 'derekderekderekderekderekderekderekderekderekderekX',
        'name_last': 'derek'
    }
    response = requests.put(f'{url}user/profile/setname/v1', json = pload)
    assert response.status_code == InputError.code

def test_setname_valid_last_1(token):
    pload = {
        'token': token,
        'name_first': 'derek',
        'name_last': 'd'
    }
    response = requests.put(f'{url}user/profile/setname/v1', json = pload)
    assert response.status_code == Success_code
    assert response.json() == {}

def test_setname_valid_last_50(token):
    pload = {
        'token': token,
        'name_first': 'derek',
        'name_last': 'derekderekderekderekderekderekderekderekderekderek'
    }
    response = requests.put(f'{url}user/profile/setname/v1', json = pload)
    assert response.status_code == Success_code
    assert response.json() == {}

def test_setname_invalid_last_51(token):
    pload = {
        'token': token,
        'name_first': 'derek',
        'name_last': 'derekderekderekderekderekderekderekderekderekderekX'
    }
    response = requests.put(f'{url}user/profile/setname/v1', json = pload)
    assert response.status_code == InputError.code

def test_setname_success(reg_multi_users):
    users = reg_multi_users

    pload = {
        'token': users['1']['token'],
        'name': 'new_channel_1',
        'is_public': True
    }
    response = requests.post(f'{url}channels/create/v2', json = pload)
    new_channel_id_1 = response.json()

    pload = {
        'token': users['2']['token'],
        'channel_id': new_channel_id_1['channel_id']
    }
    requests.post(f'{url}channel/join/v2', json = pload)
    pload = {
        'token': users['3']['token'],
        'channel_id': new_channel_id_1['channel_id']
    }
    requests.post(f'{url}channel/join/v2', json = pload)
    pload = {
        'token': users['1']['token'],
        'name_first': '2',
        'name_last': '3'
    }
    response = requests.put(f'{url}user/profile/setname/v1', json = pload)
    assert response.status_code == Success_code
    assert response.json() == {}
    pload = {
        'token': users['2']['token'],
        'name_first': '3',
        'name_last': '4'
    }
    requests.put(f'{url}user/profile/setname/v1', json = pload)
    assert response.status_code == Success_code
    assert response.json() == {}
    pload = {
        'token': users['3']['token'],
        'name_first': '4',
        'name_last': '5'
    }
    requests.put(f'{url}user/profile/setname/v1', json = pload)
    assert response.status_code == Success_code
    assert response.json() == {}

    pload = {
        'token': users['1']['token'],
        'channel_id': new_channel_id_1['channel_id']
    }
    response = requests.get(f'{url}channel/details/v2', params = pload)
    members = response.json()['all_members']
    assert members == [
        {
            'u_id': 1,
            'email': '1@gmail.com',
            'name_first': '2',
            'name_last': '3',
            'handle_str': '11'
        },
        {
            'u_id': 2,
            'email': '2@gmail.com',
            'name_first': '3',
            'name_last': '4',
            'handle_str': '22'
        },
        {
            'u_id': 3,
            'email': '3@gmail.com',
            'name_first': '4',
            'name_last': '5',
            'handle_str': '33'
        }
    ]
'''
=================================================================
'''

# user setemail function
def test_setemail_invalid_token(token):
    requests.post(f'{url}auth/logout/v1', json = {'token': token})
    pload = {
        'token': token,
        'email': 'adamchen33@hotmail.com'
    }
    response = requests.put(f'{url}user/profile/setemail/v1', json = pload)
    assert response.status_code == AccessError.code
    

def test_setemail_invalid_email(token):
    pload = {
        'token': token,
        'email': 'adam😋chen@hotmail.com'
    }
    response = requests.put(f'{url}user/profile/setemail/v1', json = pload)
    assert response.status_code == InputError.code

def test_setemail_duplicate_email(token):
    requests.post(f'{url}auth/register/v2', json = {
        'email': 'adamchen2@hotmail.com',
        'password': 'jinladen',
        'name_first': 'kyle',
        'name_last': 'jeremy'
    })
    requests.post(f'{url}auth/register/v2', json = {
        'email': 'adamchen3@hotmail.com',
        'password': 'jinladen',
        'name_first': 'kyle',
        'name_last': 'jeremy'
    })
    pload = {
        'token': token,
        'email': 'adamchen3@hotmail.com'
    }
    response = requests.put(f'{url}user/profile/setemail/v1', json = pload)
    assert response.status_code == InputError.code

def test_setemail_success(reg_multi_users):
    users = reg_multi_users
    pload = {
        'token': users['1']['token'],
        'name': 'new_channel_1',
        'is_public': True
    }
    response = requests.post(f'{url}channels/create/v2', json = pload)
    new_channel_id_1 = response.json()
    pload = {
        'token': users['2']['token'],
        'channel_id': new_channel_id_1['channel_id']
    }
    requests.post(f'{url}channel/join/v2', json = pload)
    pload = {
        'token': users['3']['token'],
        'channel_id': new_channel_id_1['channel_id']
    }
    requests.post(f'{url}channel/join/v2', json = pload)
    pload = {
        'token': users['1']['token'],
        'email': '10@gmail.com'
    }
    response = requests.put(f'{url}user/profile/setemail/v1', json = pload)
    assert response.status_code == Success_code
    assert response.json() == {}
    pload = {
        'token': users['2']['token'],
        'email': '20@gmail.com'
    }
    requests.put(f'{url}user/profile/setemail/v1', json = pload)
    assert response.status_code == Success_code
    assert response.json() == {}
    pload = {
        'token': users['3']['token'],
        'email': '30@gmail.com'
    }
    requests.put(f'{url}user/profile/setemail/v1', json = pload)
    assert response.status_code == Success_code
    assert response.json() == {}

    pload = {
        'token': users['1']['token'],
        'channel_id': new_channel_id_1['channel_id']
    }
    response = requests.get(f'{url}channel/details/v2', params = pload)
    members = response.json()['all_members']
    assert members == [
        {
            'u_id': 1,
            'email': '10@gmail.com',
            'name_first': '1',
            'name_last': '1',
            'handle_str': '11'
        },
        {
            'u_id': 2,
            'email': '20@gmail.com',
            'name_first': '2',
            'name_last': '2',
            'handle_str': '22'
        },
        {
            'u_id': 3,
            'email': '30@gmail.com',
            'name_first': '3',
            'name_last': '3',
            'handle_str': '33'
        }
    ]

'''
=================================================================
'''

# user sethandle function
def test_sethandle_invalid_token(token):
    requests.post(f'{url}auth/logout/v1', json = {'token': token})
    pload = {
        'token': token,
        'handle_str': 'derek'
    }
    response = requests.put(f'{url}user/profile/sethandle/v1', json = pload)
    assert response.status_code == AccessError.code

def test_sethandle_invalid_handle_3(token):
    pload = {
        'token': token,
        'handle_str': 'derek'
    }
    response = requests.put(f'{url}user/profile/sethandle/v1', json = pload)
    assert response.status_code == Success_code
    assert response.json() == {}

def test_sethandle_invalid_handle_20(token):
    pload = {
        'token': token,
        'handle_str': 'abcabcabcabcabcabcab'
    }
    response = requests.put(f'{url}user/profile/sethandle/v1', json = pload)
    assert response.status_code == Success_code
    assert response.json() == {}

def test_sethandle_invalid_handle_21(token):
    pload = {
        'token': token,
        'handle_str': 'abcabcabcabcabcabcabc'
    }
    response = requests.put(f'{url}user/profile/sethandle/v1', json = pload)
    assert response.status_code == InputError.code

def test_sethandle_invalid_handle_uni(token):
    pload = {
        'token': token,
        'handle_str': 'abcabc😋'
    }
    response = requests.put(f'{url}user/profile/sethandle/v1', json = pload)
    assert response.status_code == InputError.code

def test_sethandle_invalid_handle_duplicate(token):
    requests.post(f'{url}auth/register/v2', json = {
        'email': 'adamchen2@hotmail.com',
        'password': 'jinladen',
        'name_first': 'kyle',
        'name_last': 'jeremy'
    })
    requests.post(f'{url}auth/register/v2', json = {
        'email': 'adamchen3@hotmail.com',
        'password': 'jinladen',
        'name_first': 'kyle',
        'name_last': 'jeremy'
    })
    pload = {
        'token': token,
        'handle_str': 'kylejeremy1'
    }
    response = requests.put(f'{url}user/profile/sethandle/v1', json = pload)
    assert response.status_code == InputError.code

def test_sethandle_success(reg_multi_users):
    users = reg_multi_users
    pload = {
        'token': users['1']['token'],
        'name': 'new_channel_1',
        'is_public': True
    }
    response = requests.post(f'{url}channels/create/v2', json = pload)
    new_channel_id_1 = response.json()
    pload = {
        'token': users['2']['token'],
        'channel_id': new_channel_id_1['channel_id']
    }
    requests.post(f'{url}channel/join/v2', json = pload)
    pload = {
        'token': users['3']['token'],
        'channel_id': new_channel_id_1['channel_id']
    }
    response = requests.post(f'{url}channel/join/v2', json = pload)
    pload = {
        'token': users['1']['token'],
        'handle_str': '123'
    }
    response = requests.put(f'{url}user/profile/sethandle/v1', json = pload)
    assert response.status_code == Success_code
    assert response.json() == {}
    pload = {
        'token': users['2']['token'],
        'handle_str': '1234'
    }
    response = requests.put(f'{url}user/profile/sethandle/v1', json = pload)
    assert response.status_code == Success_code
    assert response.json() == {}
    pload = {
        'token': users['3']['token'],
        'handle_str': '12345'
    }
    response = requests.put(f'{url}user/profile/sethandle/v1', json = pload)
    assert response.status_code == Success_code
    assert response.json() == {}

    pload = {
        'token': users['1']['token'],
        'channel_id': new_channel_id_1['channel_id']
    }
    response = requests.get(f'{url}channel/details/v2', params = pload)
    members = response.json()['all_members']
    assert members == [
        {
            'u_id': 1,
            'email': '1@gmail.com',
            'name_first': '1',
            'name_last': '1',
            'handle_str': '123'
        },
        {
            'u_id': 2,
            'email': '2@gmail.com',
            'name_first': '2',
            'name_last': '2',
            'handle_str': '1234'
        },
        {
            'u_id': 3,
            'email': '3@gmail.com',
            'name_first': '3',
            'name_last': '3',
            'handle_str': '12345'
        }
    ]

'''
=================================================================
'''
# testing all 3 functions together
def test_set_name_handle_email(reg_multi_users):
    users = reg_multi_users
    pload = {
        'token': users['1']['token'],
        'name': 'new_channel_1',
        'is_public': True
    }
    response = requests.post(f'{url}channels/create/v2', json = pload)
    new_channel_id_1 = response.json()
    pload = {
        'token': users['2']['token'],
        'channel_id': new_channel_id_1['channel_id']
    }
    requests.post(f'{url}channel/join/v2', json = pload)
    pload = {
        'token': users['3']['token'],
        'channel_id': new_channel_id_1['channel_id']
    }
    requests.post(f'{url}channel/join/v2', json = pload)
    pload = {
        'token': users['2']['token'],
        'name_first': 'baaa',
        'name_last': 'haaa'
    }
    response = requests.put(f'{url}user/profile/setname/v1', json = pload)
    assert response.status_code == Success_code
    assert response.json() == {}
    pload = {
        'token': users['2']['token'],
        'email': 'banana@gmail.com'
    }
    response = requests.put(f'{url}user/profile/setemail/v1', json = pload)
    assert response.status_code == Success_code
    assert response.json() == {}
    pload = {
        'token': users['2']['token'],
        'handle_str': '12345'
    }
    response = requests.put(f'{url}user/profile/sethandle/v1', json = pload)
    assert response.status_code == Success_code
    assert response.json() == {}

    pload = {
        'token': users['1']['token'],
        'channel_id': new_channel_id_1['channel_id']
    }
    response = requests.get(f'{url}channel/details/v2', params = pload)
    members = response.json()['all_members']
    assert members == [
        {
            'u_id': 1,
            'email': '1@gmail.com',
            'name_first': '1',
            'name_last': '1',
            'handle_str': '11'
        },
        {
            'u_id': 2,
            'email': 'banana@gmail.com',
            'name_first': 'baaa',
            'name_last': 'haaa',
            'handle_str': '12345'
        },
        {
            'u_id': 3,
            'email': '3@gmail.com',
            'name_first': '3',
            'name_last': '3',
            'handle_str': '33'
        }
    ]