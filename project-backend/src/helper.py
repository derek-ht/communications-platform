import jwt
import re
import datetime
from src.data_store import data_store
from src.config import url

SECRET = "w+L4&J6cp*x6R4B%#9(QCw[jSpc.eu"
Success_code = 200
DEFAULT_IMG_URL = f'{url}static/default.jpg'

# Return True if the user associated with user_id
# is included in the 'users' list and False otherwise
def valid_user_id(users, user_id):
    for user in users:
        if user_id == user['user_id'] and not user['is_removed']:
            return True
    return False

# Determines whether the given session id is valid
def valid_session_id(user, session_id):
    if session_id in user['session_ids']:
        return True
    return False

# Determines whether the given token is valid
def valid_token(token):
    # Checking if token is decodable
    try:
        decoded = jwt.decode(token, SECRET, algorithms = ['HS256'])
    except:
        return False
    store = data_store.get()
    user_id = decoded['user_id']
    session_id = decoded['session_id']
    # Checking if user_id associated with token is valid
    if not valid_user_id(store['users'], user_id):
        return False
    # Checking if session_id associated with token is valid
    if not valid_session_id(store['users'][user_id - 1], session_id):
        return False
    return True

# Returns the user_id associated with the given token
def get_user_id(token):
    decoded = jwt.decode(token, SECRET, algorithms = ['HS256'])
    user_id = decoded['user_id']
    return user_id

# Checks for correct password format
def valid_password(password):
    if len(password) < 6:
        return False
    return True

# Checks for correct name format
def valid_name(name_first, name_last):
    if not len(name_first) in range(1, 51) or not len(name_last) in range(1, 51):
        return False
    return True

# Checks for duplicate emails
def duplicate_email(email, store):
    for user in store['users']:
        if user['email'] == email and not user['is_removed']:
            return True
    return False

# Checks for the correct email format
def valid_email(email):
    regex = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'

    if (re.fullmatch(regex, email)):
        return True
    else:
        return False

# Checks for valid handle length
def valid_handle_length(handle_str):
    if not len(handle_str) in range(3, 21):
        return False
    return True

# Checks that handle is alphanumeric
def valid_handle_alpha(handle_str):
    if not handle_str.isalnum():
        return False
    return True

# Checks that handle is not already in use
def duplicate_handle(handle_str, store):
    for user in store['users']:
        if user['handle_str'] == handle_str and not user['is_removed']:
            return True
    return False

# Generate and return a unique message_id 
def generate_message_id(store):
    message_id = 0

    for m_id in store["sendlaterIds"]:
        if  message_id < m_id:
            message_id = m_id

    for dm in store['dms']:
        if len(dm['messages']) != 0:
            if message_id < dm['messages'][-1]['message_id']:
                message_id = dm['messages'][-1]['message_id']
    
    for channel in store['channels']:
        if len(channel['messages']) != 0:
            if message_id < channel['messages'][-1]['message_id']:
                message_id = channel['messages'][-1]['message_id']
    message_id += 1
    return message_id

# Check if the user is a member of the given channel.
def user_in_channel(channel_id, auth_user_id, store):
    for channels in store['channels']:
        if channels['channel_id'] == channel_id:
            if auth_user_id in channels['all_members']:
                return True
    return False

# Check if the channel_id is valid
def valid_channel_id(channel_id, store):
    for channels in store['channels']:
        if channels['channel_id'] == channel_id:
            return True
    return False

# Checks if the user is a member of the given dm
def user_in_dm(dm_id, token):
    user_id = get_user_id(token)
    store = data_store.get()
    for dms in store['dms']:
        if dm_id == dms['dm_id']:
            if user_id in dms['all_members']:
                return True
    return False

# Count total number of messages in Streams
def count_messages(store):
    total_messages = 0

    # Count number of messages in all dms
    for dm in store['dms']:
        total_messages += len(dm['messages'])

    # Count number of messages in all channels
    for channel in store["channels"]:
        total_messages += len(channel['messages'])

    return total_messages

# Count the number of users who have joined at least one channel or dm
def num_users_who_have_joined_at_least_one_channel_or_dm(store):
    counter = 0
    for users in store['users']:
        if users['channels'] or users['dms'] and not users['is_removed']:
            counter += 1
    return counter

# Count number of active users in streams
def num_users(store):
    counter = 0
    for users in store['users']:
        if not users['is_removed']:
            counter += 1
    return counter

# Update channel stats
def update_stats_channels(user_id):
    store = data_store.get()
    
    user_stats = store['users'][user_id - 1]['user_stats']

    user_channels = store['users'][user_id - 1]['channels']
    num_user_channels = len(user_channels)

    workspace_stats = store['workspace_stats']
    num_channels = len(store['channels'])

    time_stamp = int(datetime.datetime.now().timestamp())

    # Only append if num_channels_joined changes from the last data point
    if user_stats['channels_joined'][-1]['num_channels_joined'] != num_user_channels:
        user_stats['channels_joined'].append({
                                        'num_channels_joined': num_user_channels,
                                        'time_stamp': time_stamp
                                        })

    # Only append if num_channels_exist changes from the last data point
    if workspace_stats['channels_exist'][-1]['num_channels_exist'] != num_channels:
        workspace_stats['channels_exist'].append({
                                        'num_channels_exist': num_channels,
                                        'time_stamp': time_stamp
                                        })
    update_stats_involvement()
    update_stats_utilization()
    data_store.set(store)

# Update dm stats
def update_stats_dms(user_id):
    store = data_store.get()

    user_stats = store['users'][user_id - 1]['user_stats']
    user_dms = store['users'][user_id - 1]['dms']
    num_user_dms = len(user_dms)

    workspace_stats = store['workspace_stats']
    num_dms = len(store['dms'])

    time_stamp = int(datetime.datetime.now().timestamp())

    # Only append if num_dms_joined changes from the last data point
    if user_stats['dms_joined'][-1]['num_dms_joined'] != num_user_dms:
        user_stats['dms_joined'].append({
                                        'num_dms_joined': num_user_dms,
                                        'time_stamp': time_stamp
                                        })
    # Only append if num_dms_exist changes from the last data point
    if workspace_stats['dms_exist'][-1]['num_dms_exist'] != num_dms:
        workspace_stats['dms_exist'].append({
                                        'num_dms_exist': num_dms,
                                        'time_stamp': time_stamp
                                        })
    update_stats_involvement()
    update_stats_utilization()
    data_store.set(store)

# Update message stats
def update_stats_messages(user_id):
    store = data_store.get()

    user_stats = store['users'][user_id - 1]['user_stats']
    num_user_messages = store['users'][user_id - 1]['message_count']

    workspace_stats = store['workspace_stats']
    num_messages = count_messages(store)

    time_stamp = int(datetime.datetime.now().timestamp())

    # Only append if num_messages_sent changes from the last data point                                
    if user_stats['messages_sent'][-1]['num_messages_sent'] != num_user_messages:
        user_stats['messages_sent'].append({
                                        'num_messages_sent': num_user_messages,
                                        'time_stamp': time_stamp
                                        })
    # Only append if num_messages_exist changes from the last data point                              
    if workspace_stats['messages_exist'][-1]['num_messages_exist'] != num_messages:
        workspace_stats['messages_exist'].append({
                                        'num_messages_exist': num_messages,
                                        'time_stamp': time_stamp
                                        })
    update_stats_involvement()
    update_stats_utilization()
    data_store.set(store)

# Update involvement stats
def update_stats_involvement():
    store = data_store.get()
    for user in store['users']:
        user_id = user['user_id']
        user_stats = store['users'][user_id - 1]['user_stats']
        user_channels = store['users'][user_id - 1]['channels']
        user_dms = store['users'][user_id - 1]['dms']

        # User variables
        num_user_channels = len(user_channels)
        num_user_dms = len(user_dms)
        num_user_messages = store['users'][user_id - 1]['message_count']

        # Stream variables
        num_channels = len(store['channels'])
        num_dms = len(store['dms'])
        num_messages = count_messages(store)

        # Calculate involvement_rate
        numerator_user = num_user_channels + num_user_dms + num_user_messages
        denominator_user = num_channels + num_dms + num_messages
        
        # Prevent division by 0
        if denominator_user == 0:
            involvement_rate = 0
        else:
            # Cap involvement rate at 1
            involvement_rate = (numerator_user / denominator_user)
            if involvement_rate > 1:
                involvement_rate = 1
        user_stats['involvement_rate'] = float(involvement_rate)
    data_store.set(store)

# Update utilization stats
def update_stats_utilization():
    store = data_store.get()
    
    workspace_stats = store['workspace_stats']
    # Calculate utilization_rate
    numerator_stream = num_users_who_have_joined_at_least_one_channel_or_dm(store)
    denominator_stream = num_users(store)

    utilization_rate = (numerator_stream / denominator_stream)
    
    workspace_stats['utilization_rate'] = float(utilization_rate)
    data_store.set(store)
