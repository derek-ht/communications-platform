import pytest
import requests
from src.config import url
from src.error import AccessError, InputError
from src.helper import Success_code

# Auth Login Tests
@pytest.fixture
def reg_one_user():
    requests.delete(f'{url}clear/v1')
    response = requests.post(f'{url}auth/register/v2', json = {
        'email': 'adamchen@hotmail.com',
        'password': 'jinladen',
        'name_first': 'Adam',
        'name_last': 'Chen',
    })
    new_user = response.json()
    return new_user

@pytest.fixture
def reg_multi_users():
    requests.delete(f'{url}clear/v1')
    users = {}
    for i in range(1,4):
        email = f'{i}@gmail.com'
        password = "password"
        name_first = f"{i}"
        name_last = f"{i}"
        response = requests.post(f'{url}auth/register/v2', json = {
            'email': email,
            'password': password,
            'name_first': name_first,
            'name_last': name_last})
        users[f'{i}'] = response.json()
        assert response.status_code == Success_code
    return users

@pytest.fixture
def login_multi_users(reg_multi_users):
    users = {}
    for i in range(1, 4):
        email = f"{i}@gmail.com"
        password = "password"
        response = requests.post(f'{url}auth/login/v2', json = {
            'email': email,
            'password': password
        })
        assert response.status_code == Success_code
        users[f"{i}"] = response.json()
    return users

# Testing standard case for auth_login with single user
def test_login_works_users(reg_one_user):
    auth_user_id1 = reg_one_user

    response = requests.post(f'{url}auth/login/v2', json = {
        'email': 'adamchen@hotmail.com',
        'password': 'jinladen'
    })
    assert response.status_code == Success_code
    auth_user_id2 = response.json()

    assert auth_user_id1['auth_user_id'] == auth_user_id2['auth_user_id']

# Testing standard case for auth_login with single user
def test_login_works_multiple_users(reg_multi_users):
    users = reg_multi_users

    auth_user_id1 = users['2']

    response = requests.post(f'{url}auth/login/v2', json = {
        'email': '2@gmail.com',
        'password': 'password'
    })

    auth_user_id2 = response.json()
    
    assert response.status_code == Success_code

    assert auth_user_id1['auth_user_id'] == auth_user_id2['auth_user_id']

# Testing standard case for auth_login for a user in a session
def test_login_works_session():
    requests.delete(f'{url}clear/v1')
    response = requests.post(f'{url}auth/register/v2', json = {
        'email': 'adamchen@hotmail.com',
        'password': 'jinladen',
        'name_first': 'kyle',
        'name_last': 'jeremy'
    })
    auth_user_id1 = response.json()

    response = requests.post(f'{url}auth/login/v2', json = {
        'email': 'adamchen@hotmail.com',
        'password': 'jinladen'
    })

    assert response.status_code == Success_code
    auth_user_id2 = response.json()

    assert auth_user_id1['token'] != auth_user_id2['token']

# Testing when auth_login recieves an incorrect password
def test_login_wrong_password():
    requests.delete(f'{url}clear/v1')
    
    requests.post(f'{url}auth/register/v2', json = {
        'email': 'adamchen@hotmail.com',
        'password': 'jinladen',
        'name_first': 'kyle',
        'name_last': 'jeremy'
    })

    response = requests.post(f'{url}auth/login/v2', json = {
        'email': 'adamchen@hotmail.com',
        'password': 'wrong_password'
    })
    assert response.status_code == InputError.code

# Testing for when a non-registered email is passed to auth_login
def test_login_user_not_registered():
    requests.delete(f'{url}clear/v1')
    requests.post(f'{url}auth/register/v2', json = {
        'email':'adamchen@hotmail.com',
        'password': 'jinladen',
        'name_first': 'kyle',
        'name_last': 'jeremy'
    })
    response = requests.post(f'{url}auth/login/v2', json = {
        'email':'notregistered@hotmail.com',
        'password': 'jinladen',
        'name_first': 'kyle',
        'name_last': 'jeremy'
    })
    assert response.status_code == InputError.code

# Testing for when a non-registered email is passed to auth_login when
# there are no registered users
def test_login_user_no_registered_users():
    requests.delete(f'{url}clear/v1')
    response = requests.post(f'{url}auth/login/v2', json = {
        'email': 'notregistered@hotmail.com',
        'password': 'right_password',
        'name_first': 'kyle',
        'name_last': 'jeremy'
    })
    assert response.status_code == InputError.code

'''
=================================================================
'''

# Auth Register Tests

# The following tests test for Invalid email

def test_register_invalid_email_plain():
    requests.delete(f'{url}clear/v1')
    response = requests.post(f'{url}auth/register/v2', json = {
        'email':'adamchenmail',
        'password': 'jinladen',
        'name_first': 'kyle',
        'name_last': 'jeremy'

    })
    assert response.status_code == InputError.code
    
def test_register_invalid_email_no_com():
    requests.delete(f'{url}clear/v1')
    response = requests.post(f'{url}auth/register/v2', json = {
        'email':'adamchen@hotmail',
        'password': 'jinladen',
        'name_first': 'kyle',
        'name_last': 'jeremy'
    })
    assert response.status_code == InputError.code

def test_register_invalid_email_no_at():
    requests.delete(f'{url}clear/v1')
    response = requests.post(f'{url}auth/register/v2', json = {
        'email':'adamchenhotmail',
        'password': 'jinladen',
        'name_first': 'kyle',
        'name_last': 'jeremy'
    })
    assert response.status_code == InputError.code

def test_register_invalid_email_no_username():
    requests.delete(f'{url}clear/v1')
    response = requests.post(f'{url}auth/register/v2', json = {
        'email':'@hotmail',
        'password': 'jinladen',
        'name_first': 'kyle',
        'name_last': 'jeremy'
    })
    assert response.status_code == InputError.code
    
'''
=================================================================
'''

# The following tests test for when various inputs are empty

def test_register_no_inputs():
    requests.delete(f'{url}clear/v1')
    response = requests.post(f'{url}auth/register/v2', json = {
        'email':'',
        'password': '',
        'name_first': '',
        'name_last': ''
    })
    
    assert response.status_code == InputError.code
    
def test_register_no_email():
    requests.delete(f'{url}clear/v1')
    response = requests.post(f'{url}auth/register/v2', json = {
        'email':'',
        'password': 'jinladen',
        'name_first': 'kyle',
        'name_last': 'jeremy'
    })
    
    assert response.status_code == InputError.code
    
def test_register_no_password():
    requests.delete(f'{url}clear/v1')
    response = requests.post(f'{url}auth/register/v2', json = {
        'email':'adamchen@hotmail',
        'password': '',
        'name_first': 'kyle',
        'name_last': 'jeremy'
    })
    
    assert response.status_code == InputError.code
    
def test_register_no_first_name():
    requests.delete(f'{url}clear/v1')
    response = requests.post(f'{url}auth/register/v2', json = {
        'email':'adamchen@hotmail',
        'password': 'jinladen',
        'name_first': '',
        'name_last': 'jeremy'
    })
    
    assert response.status_code == InputError.code

def test_register_no_last_name():
    requests.delete(f'{url}clear/v1')
    response = requests.post(f'{url}auth/register/v2', json = {
        'email':'adamchen@hotmail',
        'password': 'jinladen',
        'name_first': 'kyle',
        'name_last': ''
    })
    assert response.status_code == InputError.code

'''
=================================================================
'''

# Creating handles from duplicate names
def test_handle_non_alphanumeric():
    requests.delete(f'{url}clear/v1')
    first_user = requests.post(f'{url}auth/register/v2', json = {
        'email':'adamchen@hotmail.com',
        'password': 'derekk',
        'name_first': '@bcdefgh!j',
        'name_last': 'klmn opqrst'
    }).json()

    new_channel_id_1 = requests.post(f'{url}channels/create/v2', json = {
        'token': first_user['token'],
        'name': 'new_channel_1',
        'is_public': True
    }).json()

    second_user = requests.post(f'{url}auth/register/v2', json = {
        'email':'adamchen1@hotmail.com',
        'password': 'derekk',
        'name_first': 'bcdefghj',
        'name_last': 'klmnopqrst'
    }).json()

    requests.post(f'{url}channel/join/v2', json = {
        'token': second_user['token'],
        'channel_id': new_channel_id_1['channel_id']
    })

    response = requests.get(f'{url}channel/details/v2', params = {
        'token': first_user['token'],
        'channel_id': new_channel_id_1['channel_id']
    })

    assert response.json()['all_members'] == [
        {
            'u_id': first_user['auth_user_id'],
            'email': 'adamchen@hotmail.com',
            'name_first': '@bcdefgh!j',
            'name_last': 'klmn opqrst',
            'handle_str': 'bcdefghjklmnopqrst',
        },
        {
            'u_id': second_user['auth_user_id'],
            'email': 'adamchen1@hotmail.com',
            'name_first': 'bcdefghj',
            'name_last': 'klmnopqrst',
            'handle_str': 'bcdefghjklmnopqrst0',
        }
    ]

# Testing an edge case for handles which involves an integer in a user's
# name
def test_handle_edge_case():
    requests.delete(f'{url}clear/v1')

    first_user = requests.post(f'{url}auth/register/v2', json = {
        'email': 'adamchen@hotmail.com',
        'password': 'derekk',
        'name_first': 'abc',
        'name_last': 'def'
    }).json()

    new_channel_id_1 = requests.post(f'{url}channels/create/v2', json = {
        'token': first_user['token'],
        'name': 'new_channel_1',
        'is_public': True
    }).json()
    
    second_user = requests.post(f'{url}auth/register/v2', json = {
        'email': 'adamchen1@hotmail.com',
        'password': 'derekk',
        'name_first': 'abc',
        'name_last': 'def0'
    }).json()

    requests.post(f'{url}channel/join/v2', json = {
        'token': second_user['token'],
        'channel_id': new_channel_id_1['channel_id']
    })

    third_user = requests.post(f'{url}auth/register/v2', json = {
        'email': 'adamchen2@hotmail.com',
        'password': 'derekk',
        'name_first': 'abc',
        'name_last': 'def'
    }).json()

    requests.post(f'{url}channel/join/v2', json = {
        'token': third_user['token'],
        'channel_id': new_channel_id_1['channel_id']
    })

    fourth_user = requests.post(f'{url}auth/register/v2', json = {
        'email': 'adamchen3@hotmail.com',
        'password': 'derekk',
        'name_first': 'abc',
        'name_last': 'def1'
    }).json()

    requests.post(f'{url}channel/join/v2', json = {
        'token': fourth_user['token'],
        'channel_id': new_channel_id_1['channel_id']
    })

    assert requests.get(f'{url}channel/details/v2', params = {
        'token': first_user['token'],
        'channel_id': new_channel_id_1['channel_id']
    }).json()['all_members'] == [
        {
            'u_id': first_user['auth_user_id'],
            'email': 'adamchen@hotmail.com',
            'name_first': 'abc',
            'name_last': 'def',    
            'handle_str': 'abcdef',
        },
        {
            'u_id': second_user['auth_user_id'],
            'email': 'adamchen1@hotmail.com',
            'name_first': 'abc',
            'name_last': 'def0',
            'handle_str': 'abcdef0',
        },
        {
            'u_id': third_user['auth_user_id'],
            'email': 'adamchen2@hotmail.com',
            'name_first': 'abc',
            'name_last': 'def',
            'handle_str': 'abcdef1',
        },
        {
            'u_id': fourth_user['auth_user_id'],
            'email': 'adamchen3@hotmail.com',
            'name_first': 'abc',
            'name_last': 'def1',
            'handle_str': 'abcdef10',
        }
    ]

# Tests for when duplicate handles are encountered

def test_register_handle_duplicates_long():
    requests.delete(f'{url}clear/v1')

    first_user = requests.post(f'{url}auth/register/v2', json = {
        'email': 'adamchen@hotmail.com',
        'password': 'derekk',
        'name_first': '12345',
        'name_last': '1234512345123451'
    }).json()

    new_channel_id_1 = requests.post(f'{url}channels/create/v2', json = {
        'token': first_user['token'],
        'name': 'new_channel_1',
        'is_public': True
    }).json()
    
    second_user = requests.post(f'{url}auth/register/v2', json = {
        'email': 'adamchen1@hotmail.com',
        'password': 'derekk',
        'name_first': '12345',
        'name_last': '123451234512345'
    }).json()

    requests.post(f'{url}channel/join/v2', json = {
        'token': second_user['token'],
        'channel_id': new_channel_id_1['channel_id']
    })


    assert requests.get(f'{url}channel/details/v2', params = {
        'token': first_user['token'],
        'channel_id': new_channel_id_1['channel_id']
    }).json()['all_members'] == [
        {
            'u_id': first_user['auth_user_id'],
            'email': 'adamchen@hotmail.com',
            'name_first': '12345',
            'name_last': '1234512345123451',
            'handle_str': '12345123451234512345',
        },
        {
            'u_id': second_user['auth_user_id'],
            'email': 'adamchen1@hotmail.com',
            'name_first': '12345',
            'name_last': '123451234512345',
            'handle_str': '123451234512345123450',
        }
    ]

def test_register_handle_duplicates_same_short():
    requests.delete(f'{url}clear/v1')

    first_user = requests.post(f'{url}auth/register/v2', json = {
        'email': 'adamchen@hotmail.com',
        'password': 'derekk',
        'name_first': '12345',
        'name_last': '12345'
    }).json()

    new_channel_id_1 = requests.post(f'{url}channels/create/v2', json = {
        'token': first_user['token'],
        'name': 'new_channel_1',
        'is_public': True
    }).json()
    
    second_user = requests.post(f'{url}auth/register/v2', json = {
        'email': 'adamchen1@hotmail.com',
        'password': 'derekk',
        'name_first': '12345',
        'name_last': '12345'
    }).json()

    requests.post(f'{url}channel/join/v2', json = {
        'token': second_user['token'],
        'channel_id': new_channel_id_1['channel_id']
    })

    assert requests.get(f'{url}channel/details/v2', params = {
        'token': first_user['token'],
        'channel_id': new_channel_id_1['channel_id']
    }).json()['all_members'] == [
        {
            'u_id': first_user['auth_user_id'],
            'email': 'adamchen@hotmail.com',
            'name_first': '12345',
            'name_last': '12345',
            'handle_str': '1234512345',
        },
        {
            'u_id': second_user['auth_user_id'],
            'email': 'adamchen1@hotmail.com',
            'name_first': '12345',
            'name_last': '12345',
            'handle_str': '12345123450',
        }
    ]

def test_register_handle_duplicates_same_long():
    requests.delete(f'{url}clear/v1')

    first_user = requests.post(f'{url}auth/register/v2', json = {
        'email': 'adamchen@hotmail.com',
        'password': 'derekk',
        'name_first': '12345',
        'name_last': '123451234512345'
    }).json()

    new_channel_id_1 = requests.post(f'{url}channels/create/v2', json = {
        'token': first_user['token'],
        'name': 'new_channel_1',
        'is_public': True
    }).json()
    
    second_user = requests.post(f'{url}auth/register/v2', json = {
        'email': 'adamchen1@hotmail.com',
        'password': 'derekk',
        'name_first': '12345',
        'name_last': '123451234512345'
    }).json()

    requests.post(f'{url}channel/join/v2', json = {
        'token': second_user['token'],
        'channel_id': new_channel_id_1['channel_id']
    })

    assert requests.get(f'{url}channel/details/v2', params = {
        'token': first_user['token'],
        'channel_id': new_channel_id_1['channel_id']
    }).json()['all_members'] == [
        {
            'u_id': first_user['auth_user_id'],
            'email': 'adamchen@hotmail.com',
            'name_first': '12345',
            'name_last': '123451234512345',
            'handle_str': '12345123451234512345',
        },
        {
            'u_id': second_user['auth_user_id'],
            'email': 'adamchen1@hotmail.com',
            'name_first': '12345',
            'name_last': '123451234512345',
            'handle_str': '123451234512345123450',
        }
    ]

'''
=================================================================
'''
# Checking user_id creation
def test_register_user_id():
    requests.delete(f'{url}clear/v1')
    
    user_id1 = requests.post(f'{url}auth/register/v2', json = {
        'email':'adamchen@hotmail.com',
        'password': 'derekk',
        'name_first': '12345',
        'name_last': '1234512345123451'
    })

    user_id1 = user_id1.json()
    
    user_id2 = requests.post(f'{url}auth/register/v2', json = {
        'email':'adamchen1@hotmail.com',
        'password': 'derekk',
        'name_first': '12345',
        'name_last': '123451234512345'
    })

    user_id2 = user_id2.json()
    assert user_id1['auth_user_id'] == 1
    assert user_id2['auth_user_id'] == 2

'''
=================================================================
'''
# Length of password less than 6 characters

def test_register_less_password_1():
    requests.delete(f'{url}clear/v1')
    
    response = requests.post(f'{url}auth/register/v2', json = {
        'email':'adamchen@hotmail.com',
        'password': 'd',
        'name_first': 'kyle',
        'name_last': 'jeremy'
    })

    assert response.status_code == InputError.code

def test_register_less_password_5():
    requests.delete(f'{url}clear/v1')
    
    response = requests.post(f'{url}auth/register/v2', json = {
        'email':'adamchen@hotmail.com',
        'password': 'derek',
        'name_first': '12345',
        'name_last': '1234512345123451'
    })

    assert response.status_code == InputError.code

# Tests for when password length is exactly 6
def test_register_less_password_6():
    requests.delete(f'{url}clear/v1')
    
    response = requests.post(f'{url}auth/register/v2', json = {
        'email':'adamchen@hotmail.com',
        'password': 'derekk',
        'name_first': '12345',
        'name_last': '1234512345123451'
    })

    assert response.json()['auth_user_id'] == 1

# Length of first name between 1 and 50 inclusive

def test_register_name_first_1():

    requests.delete(f'{url}clear/v1')
    
    response = requests.post(f'{url}auth/register/v2', json = {
        'email':'adamchen@hotmail.com',
        'password': 'jinladen',
        'name_first': 'k',
        'name_last': '1234512345123451'
    })

    assert response.status_code == Success_code
    assert response.json()['auth_user_id'] == 1

def test_register_name_first_50():
    requests.delete(f'{url}clear/v1')
    
    response = requests.post(f'{url}auth/register/v2', json = {
        'email':'adamchen@hotmail.com',
        'password': 'jinladen',
        'name_first': 'derekderekderekderekderekderekderekderekderekderek',
        'name_last': 'jeremy'
    })

    assert response.status_code == Success_code
    assert response.json()['auth_user_id'] == 1

# Length of name is 51
def test_register_name_first_51():
    requests.delete(f'{url}clear/v1')
    
    response = requests.post(f'{url}auth/register/v2', json = {
        'email':'adamchen@hotmail.com',
        'password': 'jinladen',
        'name_first': 'derekderekderekderekderekderekderekderekderekderekd',
        'name_last': 'jeremy'
    })

    assert response.status_code == InputError.code

# Length of last name between 1 and 50 inclusive
def test_register_name_last_1():
    requests.delete(f'{url}clear/v1')
    
    response = requests.post(f'{url}auth/register/v2', json = {
        'email':'adamchen@hotmail.com',
        'password': 'jinladen',
        'name_first': 'derek',
        'name_last': 'd'
    })

    assert response.json()['auth_user_id'] == 1

# Length of name is exactly 50
def test_register_name_last_50():
    requests.delete(f'{url}clear/v1')
    
    response = requests.post(f'{url}auth/register/v2', json = {
        'email':'adamchen@hotmail.com',
        'password': 'jinladen',
        'name_first': 'derek',
        'name_last': 'derekderekderekderekderekderekderekderekderekderek'
    })

    assert response.json()['auth_user_id'] == 1

# Length of name is 51
def test_register_name_last_51():
    requests.delete(f'{url}clear/v1')
    
    response = requests.post(f'{url}auth/register/v2', json = {
        'email':'adamchen@hotmail.com',
        'password': 'jinladen',
        'name_first': 'derek',
        'name_last': 'derekderekderekderekderekderekderekderekderekderekd'
    })

    assert response.status_code == InputError.code

'''
=================================================================
'''

# Contains non-ascii character
def test_register_no_ascii_email():
    requests.delete(f'{url}clear/v1')
    
    response = requests.post(f'{url}auth/register/v2', json = {
        'email':'adam😋chen@hotmail.com',
        'password': 'jinladen',
        'name_first': 'derek',
        'name_last': 'derekde'
    })

    assert response.status_code == InputError.code

'''
=================================================================
'''

# Duplicate email
def test_register_same_user():
    requests.delete(f'{url}clear/v1')
    
    requests.post(f'{url}auth/register/v2', json = {
        'email':'adamchen@hotmail.com',
        'password': 'jinladen',
        'name_first': 'derek',
        'name_last': 'derekde'
    })

    response = requests.post(f'{url}auth/register/v2', json = {
        'email':'adamchen@hotmail.com',
        'password': 'jinladen',
        'name_first': 'derek',
        'name_last': 'derekde'
    })

    assert response.status_code == InputError.code

def test_register_same_email():
    requests.delete(f'{url}clear/v1')
    
    requests.post(f'{url}auth/register/v2', json = {
        'email':'adamchen@hotmail.com',
        'password': 'jinladen',
        'name_first': 'derek',
        'name_last': 'derekde'
    })

    response = requests.post(f'{url}auth/register/v2', json = {
        'email':'adamchen@hotmail.com',
        'password': 'jinladends',
        'name_first': 'derekdwd',
        'name_last': 'derekdeadwd'
    })

    assert response.status_code == InputError.code

'''
=================================================================
'''
# Token generation
def test_token_gen_login_login(reg_one_user):
    token1 = requests.post(f'{url}auth/login/v2', json = {
        'email':'adamchen@hotmail.com',
        'password': 'jinladen'
    }).json()

    token2 = requests.post(f'{url}auth/login/v2', json = {
        'email':'adamchen@hotmail.com',
        'password': 'jinladen'
    }).json()

    assert token1['token'] != token2['token']

def test_token_gen_register_login():
    requests.delete(f'{url}clear/v1')

    response = requests.post(f'{url}auth/register/v2', json = {
        'email':'adamchen@hotmail.com',
        'password': 'jinladen',
        'name_first': 'kyle',
        'name_last': 'jeremy'
    })

    assert response.status_code == Success_code

    token1 = response.json()

    response = requests.post(f'{url}auth/login/v2', json = {
        'email':'adamchen@hotmail.com',
        'password': 'jinladen'
    })

    assert response.status_code == Success_code

    token2 = response.json()
    
    assert token1['token'] != token2['token']

'''
=================================================================
'''
# Testing for Auth logout function

# Testing standard case for auth_logout
def test_auth_logout(reg_one_user):
    token = requests.post(f'{url}auth/login/v2', json = {
        'email': 'adamchen@hotmail.com', 
        'password': 'jinladen'
    }).json()

    response = requests.post(f'{url}auth/logout/v1', json = {
        'token': token['token']
    })

    assert response.status_code == Success_code
    assert response.json() == {}

    response = requests.post(f'{url}auth/logout/v1', json = {
        'token': token['token']
    })

    assert response.status_code == AccessError.code

def test_auth_login_logout_login_logout(reg_one_user):
    token = requests.post(f'{url}auth/login/v2', json = {
        'email': 'adamchen@hotmail.com',
        'password': 'jinladen'
    }).json()['token']
    token2 = requests.post(f'{url}auth/login/v2', json = {
        'email': 'adamchen@hotmail.com',
        'password': 'jinladen'
    }).json()['token']
    token3 = requests.post(f'{url}auth/login/v2', json = {
        'email': 'adamchen@hotmail.com',
        'password': 'jinladen'
    }).json()['token']

    assert requests.post(f'{url}auth/logout/v1', json = {
        'token': token
    }).json() == {}
    assert requests.post(f'{url}auth/logout/v1', json = {
        'token' : token2
    }).json() == {}
    assert requests.post(f'{url}auth/logout/v1', json = {
        'token' : token3
    }).json() == {}
    assert requests.post(f'{url}auth/logout/v1', json = {
        'token' : reg_one_user['token']
    }).json() == {}

    token = requests.post(f'{url}auth/login/v2', json = {
        'email': 'adamchen@hotmail.com',
        'password': 'jinladen'
    }).json()['token']
    token2 = requests.post(f'{url}auth/login/v2', json = {
        'email': 'adamchen@hotmail.com',
        'password': 'jinladen'
    }).json()['token']
    token3 = requests.post(f'{url}auth/login/v2', json = {
        'email': 'adamchen@hotmail.com',
        'password': 'jinladen'
    }).json()['token']

    assert requests.post(f'{url}auth/logout/v1', json = {
        'token': token
    }).json() == {}
    assert requests.post(f'{url}auth/logout/v1', json = {
        'token' : token2
    }).json() == {}
    assert requests.post(f'{url}auth/logout/v1', json = {
        'token' : token3
    }).json() == {}