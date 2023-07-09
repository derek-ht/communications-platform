import jwt
import hashlib
import smtplib
import string
import datetime
import random
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from src.data_store import data_store
from src.helper import SECRET, valid_password, valid_name,\
    duplicate_email, valid_email, valid_token, DEFAULT_IMG_URL

from src.error import InputError, AccessError

# Generates an auth token by encoding the user_id 
def generate_token(user_id, session_id):
    return jwt.encode({'user_id': user_id, 'session_id': session_id},
                       SECRET, algorithm = "HS256")

# Appends a new session id to the user's session_id list
def create_session(users):
    if users['session_ids']:
        users['session_ids'].append(users['session_ids'][-1] + 1 )
    else:
        users['session_ids'].append(0)

# Creates the handle_str by concatenating the first and last name and taking the 
# first 20 characters and reducing all characters to lowercase alphanumeric
def create_handle(name_first, name_last):
    fullname = name_first + name_last
    fullname = fullname.lower()
    fullname = ''.join(char for char in fullname if char.isalnum())  
    total_len = len(fullname)
    if total_len > 20:
        handle_str = fullname[0:20]
    else:
        handle_str = fullname
    return handle_str

# This function returns the encoded password using the sha256 algorithm
def encrypt_password(password):
    encoded = password.encode()
    encoded_password = hashlib.sha256(encoded)
    encrypted_password = encoded_password.hexdigest()
    return encrypted_password

# This function adds the new user dict to the data
def register_user(store, new_id, email, name_first, name_last, password, 
    handle_str, session_id, permission_id, token):
    store['users'].append({
            'user_id': new_id, 'email': email, 
            'password': password, 'name_first': name_first, 
            'name_last': name_last, 'handle_str': handle_str, 
            'profile_img_url': DEFAULT_IMG_URL,
            'channels': [], 'permission_id': permission_id, 'session_ids': [session_id],
            'is_removed': False, 'dms': [], 'message_count': 0,
            'notifications': [], 'password_reset_code': -1,
            'user_stats': {
                'channels_joined': [{
                                'num_channels_joined': 0,
                                'time_stamp': int(datetime.datetime.now().timestamp())
                                }], 
                'dms_joined': [{
                                'num_dms_joined': 0,
                                'time_stamp': int(datetime.datetime.now().timestamp())
                                }], 
                'messages_sent': [{
                                'num_messages_sent': 0,
                                'time_stamp': int(datetime.datetime.now().timestamp())
                                }], 
                'involvement_rate': float(0)
            }
            })
    data_store.set(store)
    return {
        'auth_user_id': new_id,
        'token': token,
    }

# This function counts the number of duplicate handles in streams
def dup_handle_counter(store, handle_str):
    counter = 0
    for name in store['users']:
        if not name['is_removed']:
            temp_name = name['name_first'] + name['name_last']
            temp_name = ''.join(char for char in temp_name if char.isalnum())
            temp_name = temp_name.lower()
            
            if len(temp_name) > 20:
                temp_handle = temp_name[0:20]
            else:
                temp_handle = temp_name

            if handle_str == temp_handle or handle_str == name['handle_str']:
                counter += 1

    return counter

# Generates a new handle for the user based on the number of duplicates
def generating_handle_str(store, handle_str, counter):
    stripped_handle = handle_str
    for users in store['users']: 
        if not users['is_removed']:
            handle_check = stripped_handle + str(counter - 1)
            if handle_check == users['handle_str']:
                counter += 1
            if counter > 0:
                handle_str = stripped_handle + str(counter - 1)
    return handle_str
    
# Accounts for duplicate handles by incrementing a number concatenated 
# to the end of their handle_str.
def create_dup_handle(store, handle_str):
    counter = dup_handle_counter(store, handle_str)
    handle_str = generating_handle_str(store, handle_str, counter)
    return handle_str

# Adds the new user to streams
def add_user_to_data(store, new_id, email, name_first, name_last, password, 
    handle_str, session_id, token):
    # Checking if the new user is a global owner
    if store['users'] == []:
        permission_id = 1
        store['workspace_stats']['channels_exist'].append({
                        'num_channels_exist': 0,
                        'time_stamp': int(datetime.datetime.now().timestamp())
                        })
        store['workspace_stats']['dms_exist'].append({
                        'num_dms_exist': 0,
                        'time_stamp': int(datetime.datetime.now().timestamp())
                        })
        store['workspace_stats']['messages_exist'].append({
                        'num_messages_exist': 0,
                        'time_stamp': int(datetime.datetime.now().timestamp())
                        })
        store['workspace_stats']['utilization_rate'] = float(0)
    else:
        permission_id = 2
        handle_str = create_dup_handle(store, handle_str)

    new_user = register_user(store, new_id, email, name_first, name_last, password, 
        handle_str, session_id, permission_id, token)
    
    return new_user

# This function assigns the user with the password reset code and returns a 
# True upon success
def search_for_user(store, email, reset_code):
    is_user = False
    for user in store['users']:
        if user['email'] == email:
            is_user = True
            user['session_ids'] = []
            user['password_reset_code'] = encrypt_password(reset_code)
            break
    return is_user

# This functions sets up the SMTP server for sending emails 
def set_up_server(stream_email, stream_password):
    server = smtplib.SMTP(host = 'smtp.gmail.com', port = 587)
    server.starttls()
    server.login(stream_email, stream_password)
    return server

# This function generates the email message
def generate_message(reset_code, stream_email, email):
    msg = MIMEMultipart()
    message = f'''
    Hello user,
    Your code to reset your password is:
    {reset_code}
    '''
    msg['From'] = stream_email
    msg['To'] = email
    msg['Subject'] = 'Streams password reset'
    msg.attach(MIMEText(message, 'plain'))
    return msg

# Checks if the email matches the correctly registered password and returns
# the user_id assigned to the entered email and password.
# Arguments:
#     email (str) - email of the user
#     password (str) - password of the user
# Exceptions:
#     InputError - Occurs when email is not registered, 
#                  i.e. does not exist in data_store.
#     InputError - Occurs when password entered in login is not assigned 
#                  to registered the email.
# Return Value:
#     Returns the 'auth_user_id' (dict) if the password entered is 
#     assigned to the email entered in data_store.
def auth_login_v2(email, password):
    store = data_store.get()
    for user in store['users']:
        if user['email'] == email and not user['is_removed']:
            # Password encryption
            password = encrypt_password(password)

            if user['password'] == password:
                create_session(user)
                token = generate_token(user['user_id'], user['session_ids'][-1])
                return {
                    'auth_user_id': user['user_id'],
                    'token': token,
                }
            else:
                raise InputError("Wrong password")
    raise InputError("Email not registered")

# Creates a new user in data_store, including their created handle_str (str), 
# auth_user_id (int), channels (list) and permission_id (int) in their 
# respective key in data_store as well.
# Arguments:
#     email (str) - email of the user
#     password (str) - password of the user
#     name_first (str) - first name of the user
#     name_last (str) - last name of the user
# Exceptions:
#     InputError - Occurs if email is not in the correct format
#     InputError - Occurs if email already exists in data_store
#     InputError - Occurs if either first or last name is not between 
#                  1-50 characters inclusively
#     InputError - Occurs when password entered is less than 6 characters
# Return Value:
#     Returns the 'auth_user_id' (dict) of the new user if all 
#     arguments are valid.
def auth_register_v2(email, password, name_first, name_last):
    store = data_store.get()

    # Error checking
    if not valid_email(email):
        raise InputError("Invalid email format")

    if duplicate_email(email, store):
        raise InputError("Email has been used before.")
    
    if not valid_name(name_first, name_last):
        raise InputError("First name and last name must be between\
        1-50 characeters inclusively.")

    if not valid_password(password):
        raise InputError("Password must be greater than 5 characters.")

    # Create user id, by assigning the current number of users registed plus one.
    new_id = len(store['users']) + 1
    
    handle_str = create_handle(name_first, name_last)

    password = encrypt_password(password)

    session_id = 0
    token = generate_token(new_id, session_id)
    
    # Adding new user to empty list
    new_user = add_user_to_data(store, new_id, email, name_first, name_last, password, 
        handle_str, session_id, token)
    data_store.set(store)

    return new_user

# Given an active token, invalidates the token to log the user out by removing
# the token's corresponding session_id from the user's session_id list.
# Arguments:
#     token (str) - auth token of the user
# Exceptions:
#     AccessError - Occurs if the token is invalid
# Return Value:
#     Returns an empty dictionary on success
def auth_logout_v1(token):
    if not valid_token(token):
        raise AccessError("Invalid token")

    decoded = jwt.decode(token, SECRET, algorithms = 'HS256')
    session_id = decoded['session_id']
    user_id = decoded['user_id']
    store = data_store.get()
    # Find user from the token, in the users list and remove the session_id
    # found from the token.
    store['users'][user_id - 1]['session_ids'].remove(session_id)
    data_store.set(store)
    return {}

# Given an email address, if the user is a registered user, sends them an email
# containing a specific secret code, that when entered in auth/passwordreset/reset,
# shows that the user trying to reset the password is the one who got sent this
# email. When a user requests a password reset, they should be logged out of all 
# current sessions.
# Arguments:
#     email (str) - email of the user
# Exceptions:
#     N/A
# Return Value:
#     Returns an empty dictionary on success
def auth_passwordreset_request_v1(email):
    store = data_store.get()
    is_user = False
    reset_code = ''.join(random.choices(string.ascii_uppercase + \
        string.digits, k = 10))
    is_user = search_for_user(store, email, reset_code)
    if not is_user:
        return {}
    
    stream_email = 'F13ACamel.reset@gmail.com'
    stream_password = 'F13ACamelreset123'
    server = set_up_server(stream_email, stream_password)
    msg = generate_message(reset_code, stream_email, email)
    server.send_message(msg)
    del msg
    return {}

# Given a reset code for a user, set that user's new password to the password provided.
# Arguments:
#     reset_code (str) - reset_code generated by request
#     new_password (str) - password to be changed to
# Exceptions:
#     InputError - reset_code is not a valid reset code
#     InputError - password entered is less than 6 characters long
# Return Value:
#     Returns an empty dictionary on success
def auth_passwordreset_reset_v1(reset_code, new_password):
    store = data_store.get()
    for user in store['users']:
        if user['password_reset_code'] == encrypt_password(reset_code):
            if not valid_password(new_password):
                raise InputError('password entered is less than 6 characters')
            user['password'] = encrypt_password(new_password)
            user['password_reset_code'] = -1
            return {}
    raise InputError('reset_code is not a valid reset code')
