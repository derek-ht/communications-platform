import urllib.request
from PIL import Image

from src.data_store import data_store
from src.config import url
from src.helper import get_user_id, valid_token, valid_name, duplicate_email,\
                       valid_email, valid_handle_length, valid_handle_alpha,\
                       duplicate_handle, valid_token, DEFAULT_IMG_URL
from src.error import InputError, AccessError
import time

def valid_jpg(image):
    img_type = image.format
    correct_types = ['JPG', 'JPEG']
    if img_type in correct_types:
        return True
    raise InputError("Image uploaded must be a JPG")

def valid_dimensions(image, x_start, y_start, x_end, y_end):
    width, height = image.size

    if x_start > x_end or y_start > y_end:
        raise InputError("x_end must be greater than or equal to x_start \
        and y end must be greater than or equal to y_start.")

    if x_end > width or y_end > height:
        raise InputError("x_start, y_start, x_end and y_end must be within \
        the dimensions of the image at the URL.")


# Update the authorised user's first and last name
# Arguments:
#     token (str) - auth token of the user
#     name_first (str) - first name to be changed to
#     name_last (str) - last name to be changed to
# Exceptions:
#     AccessError - Occurs if the token is invalid
#     InputError - Occurs if either first or last name is not between 
#                  1-50 characters inclusively
# Return Value:
#     Returns an empty dictionary on success
def user_profile_setname_v1(token, name_first, name_last):
    if not valid_token(token):
        raise AccessError("Invalid token")
 
    if not valid_name(name_first, name_last):
        raise InputError("First name and last name must be between\
        1-50 characeters inclusively.")

    user_id = get_user_id(token)
    store = data_store.get()
    # Find user from the token, in the users list and update their
    # first and last name to the given new names.
    store['users'][user_id - 1]['name_first'] = name_first
    store['users'][user_id - 1]['name_last'] = name_last
    data_store.set(store)
    
    return {}

# Update the authorised user's email address
# Arguments:
#     token (str) - auth token of the user
#     email (str) - email of the user
# Exceptions:
#     AccessError - Occurs if the token is invalid
#     InputError - Occurs if the email is in an invalid email format
#     InputError - Occurs if the user wants to change to an email that already
#                  exists.
# Return Value:
#     Returns an empty dictionary on success
def user_profile_setemail_v1(token, email):
    if not valid_token(token):
        raise AccessError("Invalid token")
        
    if not valid_email(email):
        raise InputError("Invalid email format")

    store = data_store.get()

    if duplicate_email(email, store):
        raise InputError("Email has been used before.")

    user_id = get_user_id(token)
    # Find user from the token, in the users list and update their
    # email to the given new email.
    store['users'][user_id - 1]['email'] = email
    data_store.set(store)

    return {}

# Update the authorised user's handle (i.e. display name)
# Arguments:
#     token (str) - auth token of the user
#     handle_str (str) - handle of the user
# Exceptions:
#     AccessError - Occurs if the token is invalid
#     InputError - Occurs if the handle is not between 3-20 characters 
#                  inclusively
#     InputError - Occurs if the handle contains non-alphanumeric characters.
#     InputError - Occurs if the new handle is already used by another user.
# Return Value:
#     Returns an empty dictionary on success
def user_profile_sethandle_v1(token, handle_str):
    if not valid_token(token):
        raise AccessError("Invalid token")

    if not valid_handle_length(handle_str):
        raise InputError("Length of handle_str is not between \
                        3 and 20 characters inclusive")

    if not valid_handle_alpha(handle_str):
        raise InputError("Handle_str contains characters\
                         that are not alphanumeric")
    
    store = data_store.get()

    if duplicate_handle(handle_str, store):
        raise InputError("The handle is already used by another user")
    user_id = get_user_id(token)
    # Find user from the token, in the users list and update their
    # handle to the given new handle.
    store['users'][user_id - 1]['handle_str'] = handle_str
    data_store.set(store)

    return {}

# Returns the details of a single user
# Arguments:
#   token (str) - token used to authorise the user
#   u_id (int)  - The user ID of the person who joins the channel
# Exceptions:
#   AccessError - Occurs when the token is invalid
#   
# Return value:
#   Returns {
#       'u_id': auth_user_id,
#       'email': email,
#       'name_first': name_first,
#       'name_last': name_last,
#       'handle_str': handle_str,
#       'profile_img_url': profile_img_url
#     }
#   when no errors are raised
def user_profile_v1(token, u_id):
    if not valid_token(token):
        raise AccessError("Invalid Token")

    store = data_store.get()

    for users in store['users']:
        if u_id == users['user_id']:
            return {
                'user': {
                    'u_id': users['user_id'],
                    'email': users['email'],
                    'name_first': users['name_first'],
                    'name_last': users['name_last'],
                    'handle_str': users['handle_str'],
                    'profile_img_url': users['profile_img_url']}
            }
    raise InputError("Invalid auth_user_id")

# Fetches the required statistics about this user's use of UNSW Streams.
# Arguments:
#     token (str) - auth token of the user
# Exceptions:
#     AccessError - Occurs if the token is invalid
# Return Value:
#     Returns a dictionary of shape 
#    {
#     channels_joined: [{num_channels_joined, time_stamp}],
#     dms_joined: [{num_dms_joined, time_stamp}], 
#     messages_sent: [{num_messages_sent, time_stamp}], 
#     involvement_rate 
#    }
def user_stats_v1(token):
    if not valid_token(token):
        raise AccessError("Invalid Token")

    user_id = get_user_id(token)

    store = data_store.get()

    return {'user_stats': store['users'][user_id - 1]['user_stats']}

# Store an image url to the user and the respective image into an image
# folder. 
# Arguments:
#   token (str)   - token used to authorise the user
#   img_url (str) - url of the route which returns an image
#   x_start (int) - x starting point of crop
#	y_start (int) - y starting point of crop
#	x_end (int) - x end point of crop
#	y_end (int) - y end point of crop
# Exceptions:
#   AccessError - Occurs when the token is invalid
#   InputError  - Occurs when the image is not a jpg
#   InputError  - Occurs when the dimensions are beyond the image 
#                 dimensions
#   InputError  - Occurs when the end point is less than the start
#                 point.
#   
# Return value:
#   Returns {}
#   when no errors are raised
def user_profile_uploadphoto_v1(token, img_url, x_start, y_start, x_end, y_end):
    store = data_store.get()

    if not valid_token(token):
        raise AccessError("Invalid Token")

    u_id = get_user_id(token)
    
    try:
        urllib.request.urlretrieve(img_url, f'src/static/temp.jpg')
    except ValueError as invalid_url:
        raise InputError("Invalid URL") from invalid_url

    image = Image.open(f'src/static/temp.jpg')
    valid_jpg(image)
    valid_dimensions(image, x_start, y_start, x_end, y_end)
    
    cropped = image.crop((x_start, y_start, x_end, y_end))
    cropped.save(f'src/static/{u_id}.jpg')

    profile_img_url = f'{url}static/{u_id}.jpg'
    for users in store['users']:
        if u_id == users['user_id']:
            users['profile_img_url'] = profile_img_url

    return {}
