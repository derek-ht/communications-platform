import pytest
import requests
from PIL import Image
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

def user_profile_v1(token, u_id):
    pload = {
        'token': token,
        'u_id': u_id
    }
    response = requests.get(f'{url}user/profile/v1', params = pload)
    assert response.status_code == Success_code
    return response.json()

def users_all_v1(token):
    pload = {
        'token': token
    }
    response = requests.get(f'{url}users/all/v1', params = pload)
    assert response.status_code == Success_code
    return response.json()

def user_profile_uploadphoto_v1(
    token, img_url, x_start, y_start, x_end, y_end
):
    pload = {
        'token': token, 
        'img_url': img_url, 
        'x_start': x_start, 
        'y_start': y_start, 
        'x_end': x_end, 
        'y_end': y_end
    }
    response = requests.post(f'{url}user/profile/uploadphoto/v1', 
    json = pload)
    assert response.status_code == Success_code
    return response.json()

# Registers users and stores their returned dictionaries in the users 
# dictionary. Also returns the url of a valid img_url.
@pytest.fixture
def set_up():
    clear_v1()
    users = {}
    for i in range(1, 4):
        users[f"{i}"] = auth_register_v2(f"name{i}@gmail.com", "password",
            f"person{i}", f"surname{i}"
        )
    img_url = 'http://images.neopets.com/press/zafara_1.jpg'
    return users, img_url

# Tests that the profile_img_url of a user has changed to the new cropped image
# and that the cropped image has a certain width and height
def test_user_profile_uploadphoto_base(set_up):
    users, img_url = set_up
    token = users['1']['token']
    u_id = users['1']['auth_user_id']
    user_profile_uploadphoto_v1(token, img_url, 200, 200, 800, 800)
    assert user_profile_v1(token, u_id)['user']['profile_img_url'] == f'{url}\
static/{u_id}.jpg'
    image = Image.open(f'src/static/{u_id}.jpg')
    width, height = image.size
    assert width == 600
    assert height == 600

# Tests that url has changed and the width and height are correct given multiple 
# users
def test_user_profile_uploadphoto_multiple_users(set_up):
    users, img_url = set_up
    token = users['3']['token']
    u_id = users['3']['auth_user_id']
    user_profile_uploadphoto_v1(token, img_url, 200, 200, 800, 800)
    assert user_profile_v1(token, u_id)['user']['profile_img_url'] == f'{url}\
static/{u_id}.jpg'
    image = Image.open(f'src/static/{u_id}.jpg')
    width, height = image.size
    assert width == 600
    assert height == 600

# Tests that an access error is raised when the token is invalid
def test_user_profile_uploadphoto_input_error_invalid_token(set_up):
    img_url = set_up[1]
    pload = {
        'token': '1', 
        'img_url': img_url, 
        'x_start': 0, 
        'y_start': 0, 
        'x_end': 100, 
        'y_end': 100
    }
    response = requests.post(f'{url}user/profile/uploadphoto/v1', json = pload)
    assert response.status_code == AccessError.code

# Tests that an input error is raised when the given dimensions are not in
# the range of the image dimensions.
def test_user_profile_uploadphoto_input_error_invalid_image_dimensions(set_up):
    users, img_url = set_up
    token = users['3']['token']
    pload = {
        'token': token, 
        'img_url': img_url, 
        'x_start': 0, 
        'y_start': 0, 
        'x_end': 10000, 
        'y_end': 10000
    }
    response = requests.post(f'{url}user/profile/uploadphoto/v1', json = pload)
    assert response.status_code == InputError.code

# Tests that an input error is raised when the end coordinate is less than the 
# start coordinate.
def test_user_profile_uploadphoto_input_error_invalid_dimensions(set_up):
    users, img_url = set_up
    token = users['3']['token']
    pload = {
        'token': token, 
        'img_url': img_url, 
        'x_start': 10, 
        'y_start': 10, 
        'x_end': 0, 
        'y_end': 0
    }
    response = requests.post(f'{url}user/profile/uploadphoto/v1', json = pload)
    assert response.status_code == InputError.code

# Tests that an input error is raised when the image is not a JPG
def test_user_profile_uploadphoto_input_error_invalid_format(set_up):
    users = set_up[0]
    token = users['3']['token']
    invalid_img = 'http://images.neopets.com/pets/sad/aisha_christmas_baby.gif'
    pload = {
        'token': token, 
        'img_url': invalid_img, 
        'x_start': 0, 
        'y_start': 0, 
        'x_end': 100, 
        'y_end': 100
    }
    response = requests.post(f'{url}user/profile/uploadphoto/v1', json = pload)
    assert response.status_code == InputError.code

# Tests that an Input Error is raised if the url returns a non-200 status code
def test_user_profile_uploadphoto_input_error_invalid_url(set_up):
    users = set_up[0]
    token = users['3']['token']
    invalid_img = 'Error'
    pload = {
        'token': token, 
        'img_url': invalid_img, 
        'x_start': 0, 
        'y_start': 0, 
        'x_end': 100, 
        'y_end': 100
    }
    response = requests.post(f'{url}user/profile/uploadphoto/v1', json = pload)
    assert response.status_code == InputError.code