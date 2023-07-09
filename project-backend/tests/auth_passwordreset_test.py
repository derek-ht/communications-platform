import pytest
import requests
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

def auth_login_v2(email, password):
    pload = {
        'email': email,
        'password': password,
    }
    return requests.post(f'{url}auth/login/v2', json = pload).json()

def auth_reset_request_v1(email):
    pload = {
        'email': email
    }
    return requests.post(f'{url}auth/passwordreset/request/v1', json = pload)

def auth_reset_reset_v1(reset_code, new_password):
    pload = {
        'reset_code': reset_code,
        'new_password': new_password
    }
    return requests.post(f'{url}auth/passwordreset/reset/v1', json = pload)

def auth_logout_v1(token):
    pload = {
        'token': token
    }
    requests.post(f'{url}auth/logout/v1', json = pload)
    return {}

@pytest.fixture
def reg_one_user():
    clear_v1()
    user = auth_register_v2(
        'adamchen@hotmail.com', 'jinladen', 'Adam', 'Chen')
    return user

@pytest.fixture
def reg_multi_users():
    clear_v1()
    users = {}
    for i in range(1,4):
        email = f'{i}@gmail.com'
        password = "password"
        name_first = f"{i}"
        name_last = f"{i}"
        users[f'{i}'] = auth_register_v2(email, password, name_first, name_last)
    return users

# Password reset request a registered user
def test_request_success(reg_one_user):
    response = auth_reset_request_v1("adamchen@hotmail.com")
    assert response.status_code == Success_code

# Password reset request a non registered user
def test_request_not_user(reg_multi_users):
    response = auth_reset_request_v1("asdf@hotmail.com")
    assert response.status_code == Success_code

# Invalid reset code
def test_reset_code_invalid_reset_code():
    response = auth_reset_reset_v1("12345678910", "password")
    assert response.status_code == InputError.code

# Invalid password
def test_reset_code_invalid_password():
    response = auth_reset_reset_v1("12345678910", "abc")
    assert response.status_code == InputError.code