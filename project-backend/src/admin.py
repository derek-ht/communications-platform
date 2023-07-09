# Importing from other files.
from src.error import InputError, AccessError
from src.data_store import data_store
from src.auth import generate_token
from src.channel import channel_messages_v2, channel_leave_v1
from src.dm import dm_leave_v1, dm_messages_v1
from src.message import message_edit_v1
from src.user import user_profile_setname_v1
from src.helper import get_user_id, valid_user_id, valid_token,\
update_stats_utilization, update_stats_channels, update_stats_dms


PERMISSION_IDS = (1,2)

# Tests for exceptions
def admin_exception_handling(token, store, u_id):
    if not valid_token(token):
        raise AccessError('Invalid token')
    
    user_id = get_user_id(token)

    if not is_global_owner(store, user_id):
        raise AccessError('the authorised user is not a global owner')
    
    if not valid_user_id(store['users'], u_id):
        raise InputError('u_id does not refer to a valid user')
    
    if is_only_global_owner(store['users'], u_id):
        raise InputError('u_id refers to a user who is the only global owner')

# Checks if the given user is a global owner of streams
def is_global_owner(store, user_id):
    if store['users'][user_id - 1]['permission_id'] == 1:
        return True
    return False

# This function determines if the user associated with user_id is the only
# global owner of streams
def is_only_global_owner(users, user_id):
    count = 0
    user_is_owner = False
    for user in users:
        if user['permission_id'] == 1:
            if user['user_id'] == user_id:
                user_is_owner = True
            count += 1
    if count == 1 and user_is_owner:
        return True

# This function edits the given messages to 'Removed user'
def editing_messages(u_token, messages, u_id):
    for message in messages:
        # Changing contents of messages to be 'Removed user'
        if message['u_id'] == u_id:
            message_edit_v1(u_token, message['message_id'], 'Removed user')

# This functions edits all messages sent by the user associated with u_id in 
# channels to be 'Removed user'
def updating_channel_messages(u_token, channel, u_id):
    # Editing user's messages in channels
    start = 0
    messages = channel_messages_v2(u_token, channel, start)['messages']
    message_end = channel_messages_v2(u_token, channel, start)['end']

    while (message_end != -1):
        editing_messages(u_token, messages, u_id)
        start += 50
        messages = channel_messages_v2(u_token, channel, start)['messages']
        message_end = channel_messages_v2(u_token, channel, start)['end']
        
    # Editing remaining messages
    editing_messages(u_token, messages, u_id)
    
# This functions edits all messages sent by the user associated with u_id in 
# dms to be 'Removed user'
def updating_dm_messages(u_token, dm, u_id):
    # Editing user's messages in DMs
    start = 0
    messages = dm_messages_v1(u_token, dm, start)['messages']
    message_end = dm_messages_v1(u_token, dm, start)['end']

    while (message_end != -1):
        editing_messages(u_token, messages, u_id)
        start += 50
        messages = dm_messages_v1(u_token, dm, start)['messages']
        message_end = dm_messages_v1(u_token, dm, start)['end']

    # Editing remaining messages
    editing_messages(u_token, messages, u_id)
    
# This function appends the user session_ids with a negative session_id
# and returns the generated token
def creating_negative_session(user, u_id):
    if (user['session_ids']):
        user['session_ids'].append(-1)
    else:
        user['session_ids'] = [-1]
    u_token = generate_token(u_id, -1)
    return u_token

# Loops through all the channels the user is in and removes them from having 
# owner permissions
def remove_owner_permissions(u_id, store):
    channels = store['users'][u_id - 1]['channels']
    for channel in channels:
        if not u_id in store['channels'][channel - 1]['owner_members']:
            store['channels'][channel - 1]['owner_permissions'].remove(u_id)

# Loops through all the channels the user is in and gives the channel
# owner_permissions
def add_owner_permissions(u_id, store):
    channels = store['users'][u_id - 1]['channels']
    for channel in channels:
        if not u_id in store['channels'][channel - 1]['owner_permissions']:
            store['channels'][channel - 1]['owner_permissions'].append(u_id)
    
# Given a user by their user ID, set their permissions to new permissions
# described by permission_id.
# Arguments:
#     token (str) - token of the user
#     u_id (int) - user id of the user to be removed
# Exceptions:
#     AccessError - Occurs if the token is invalid
#     AccessError - Occurs if the authorised user is not a global owner
#     InputError - Occurs if the u_id does not refer to a valid user.
#     InputError - Occurs if the u_id refers to a user who is the only global 
#                  owner.
# Return Value:
#     Returns an empty dictionary on success
def admin_user_remove_v1(token, u_id):
    store = data_store.get()
    admin_exception_handling(token, store, u_id)
    user = store['users'][u_id - 1]

    # Starting a session with a negative session_id which is inaccessible by
    # the user. This enables us to begin removing them from channels and dms
    u_token = creating_negative_session(user, u_id)

    # Profile should have first name being Removed and last name user
    user_profile_setname_v1(u_token, 'Removed', 'user')

    for channel in user['channels']:
        updating_channel_messages(u_token, channel, u_id)
        # Removing user from channel
        channel_leave_v1(u_token, channel)
        update_stats_channels(u_id)
        
    for dm in user['dms']:
        updating_dm_messages(u_token, dm, u_id)
        # Removing user from dm
        dm_leave_v1(u_token, dm)
        update_stats_dms(u_id)

    #Removing from streams
    user['is_removed'] = True
    update_stats_utilization()
    data_store.set(store)

    return {}

# Given a user by their user ID, set their permission-id to a new id
# described by permission_id.
# Arguments:
#     token (str) - auth token of the user
#     u_id (int) - user id of the user to be updated
#     permission_id (int) - permission status to be updated to
# Exceptions:
#     AccessError - Occurs if the token is invalid
#     AccessError - Occurs if the authorised user is not a global owner
#     InputError - Occurs if the u_id does not refer to a valid user.
#     InputError - Occurs if the u_id refers to a user who is the only global 
#                  owner.
#     InputError - Occurs if the permission to be changed to is not valid.
# Return Value:
#     Returns an empty dictionary on success
def admin_permission_change_v1(token, u_id, permission_id):
    store = data_store.get()
    admin_exception_handling(token, store, u_id)

    if not permission_id in PERMISSION_IDS:
        raise InputError('permission_id is invalid')
    
    # Changing user channel permissions
    if permission_id == 2 and store['users'][u_id - 1]['permission_id'] == 1:
        remove_owner_permissions(u_id, store)
    
    if permission_id == 1 and store['users'][u_id - 1]['permission_id'] == 2:
        add_owner_permissions(u_id, store)

    store['users'][u_id - 1]['permission_id'] = permission_id
    data_store.set(store)
    
    return {}