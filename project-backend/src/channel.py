# Importing from other files.
from src.error import InputError
from src.error import AccessError
from src.data_store import data_store
from src.notifications import added_notification
from src.helper import get_user_id, valid_user_id, valid_token, \
    user_in_channel, valid_channel_id, update_stats_channels
    
# Handles basic exceptions
def channel_basic_exception_handling(token, channel_id, store):
    if not valid_token(token):
        raise AccessError('Invalid token')

    if not valid_channel_id(channel_id, store):
        raise InputError('channel_id does not refer to a valid channel')
        
# Handles exceptions for channel_addowner and channel_removeowner
def channel_owner_exceptions(channel_id, store, token, u_id):
    channel_basic_exception_handling(token, channel_id, store)
    user_id = get_user_id(token)
    if not has_owner_perms(channel_id, store['channels'], user_id):
        raise AccessError('channel_id is valid and the authorised user does \
        not have owner permissions in the channel')

    if not valid_user_id(store['users'], u_id):
        raise InputError('u_id does not refer to a valid user')

# Check if the start value exists in the message bank.
def valid_start(channel_id, start, store):
    channel = store['channels'][channel_id - 1]
    if len(channel['messages']) == 0 and start == 0:
        return True
    if start >= len(channel['messages']):
        return False
    return True

# Checks if the user associated with 'user_id' has owner permissions of the 
# given channel 
def has_owner_perms(channel_id, channels, user_id):
    if user_id in channels[channel_id - 1]['owner_permissions']:
        return True
    return False

# Checks if the user associated with 'user_id' is an owner of the given channel
def is_owner_of_channel(channel_id, channels, user_id):
    if user_id in channels[channel_id - 1]['owner_members']:
        return True
    return False

# This function returns a list containing details about every owner
def owner_members_list(channel, store):
    owner_members = []
    for owners in channel['owner_members']:
        owner_info = {}
        for users in store['users']:
            if users['user_id'] == owners:
                owner_info['u_id'] = users['user_id']
                owner_info['email'] = users['email']
                owner_info['name_first'] = users['name_first']
                owner_info['name_last'] = users['name_last']
                owner_info['handle_str'] = users['handle_str']
                owner_members.append(owner_info)
    return owner_members
    
# This function returns a list containing details about every member
def all_members_list(channel, store):
    all_members = []
    for members in channel['all_members']:
        all_members_info = {}
        for users in store['users']:
            if users['user_id'] == members:
                all_members_info['u_id'] = users['user_id']
                all_members_info['email'] = users['email']
                all_members_info['name_first'] = users['name_first']
                all_members_info['name_last'] = users['name_last']
                all_members_info['handle_str'] = users['handle_str']
                all_members.append(all_members_info)
    return all_members

# This function creates a list of messages from the given channel, beginning 
# at the start index and ending after 50 messages have been appended or the 
# message bank ends.
def messages_list(store, channel_id, start, user_id):
    messages = {'messages': []}
    channel = store['channels'][channel_id - 1]
    count = 0
    for message in reversed(channel['messages']):
        if count - start >= 50:
            break
        if start <= count:
            add_msg = message.copy()
            for reacts in add_msg['reacts']:
                # Causes coverage error only 
                # cause 1 react_id exists so far
                if user_id in reacts['u_ids']:
                    reacts['is_this_user_reacted'] = True
            messages['messages'].append(add_msg)
        count += 1
    
    messages['start'] = start

    if start + 50 < len(channel['messages']):
        messages['end'] = start + 50
    else:
        messages['end'] = -1
    return messages
  
# This function adds the user associated with u_id to the given channel
def add_member(store, u_id, channel_id):
    channel = store['channels'][channel_id - 1]
    channel['all_members'].append(u_id)

    if store['users'][u_id - 1]['permission_id'] == 1:
        channel['owner_permissions'].append(u_id)

    store['users'][u_id - 1]['channels'].append(channel_id)

# This function removes the member associated with user_id from the given 
# channel
def remove_member(store, user_id, channel_id):
    store['users'][user_id - 1]['channels'].remove(channel_id)
    store['channels'][channel_id - 1]['all_members'].remove(user_id)

    if user_id in store['channels'][channel_id - 1]['owner_members']:
        store['channels'][channel_id - 1]['owner_members'].remove(user_id)
    
    if user_id in store['channels'][channel_id - 1]['owner_permissions']:
        store['channels'][channel_id - 1]['owner_permissions'].remove(user_id)


# This function lets another user join a channel through an invitation
# Arguments:
#   token (str) - The token of the user sending the invitation
#   channel_id (int) - The id of the channel being joined
#   u_id (int) - The id of the user who joins the channel

# Exceptions:
#   InputError  - Occurs when u_id is invalid
#   InputError  - Occurs when channel_id is invalid
#   InputError  - Occurs if the user associated with u_id is already a 
#                 member of the channel
#   AccessError - Occurs when the user associated with token is not a 
#                 member of the channel
#   AccessError - Occurs if the token is invalid

# Return Value:
#     Returns {} if no exceptions occur during runtime
def channel_invite_v2(token, channel_id, u_id):
    store = data_store.get()
    channel_basic_exception_handling(token, channel_id, store)
    auth_user_id = get_user_id(token)

    if not user_in_channel(channel_id, auth_user_id, store):
        raise AccessError('Invitation sent by user who is not a \
            member of channel.')

    if user_in_channel(channel_id, u_id, store):
        raise InputError('Invited user is already a member of \
            channel.')

    if not valid_user_id(store['users'], u_id):
        raise InputError('Invalid u_id')

    # Add the member to the channel
    add_member(store, u_id, channel_id)

    update_stats_channels(u_id)

    added_notification(token, channel_id, True, u_id)

    data_store.set(store)

    return {}

# Return the details of the given channel, including the details of each 
# owner/member.
# Arguments:
#   token (str)      - token used to authorise the user
#   channel_id (int) - id code of the channel
# Exceptions:
#   AccessError - Occurs when the token is invalid
#   InputError  - Occurs when the channel id is invalid
#   AccessError - Occurs when the user is not a member of the the channel
# Return value:
#   Returns {
#       'name': 'Hayden',
#       'is_public': is_public
#       'owner_members': [
#           {
#               'u_id': auth_user_id,
#               'email': email,
#               'name_first': name_first,
#               'name_last': name_last,
#               'handle_str': handle_str,
#           }
#       ],
#       'all_members': [
#           {
#               'u_id': auth_user_id,
#               'email': email,
#               'name_first': name_first,
#               'name_last': name_last,
#               'handle_str': handle_str,
#           }
#       ],
#   }
#   when errors are not raised
def channel_details_v2(token, channel_id):
    store = data_store.get()
    channel_basic_exception_handling(token, channel_id, store)
    auth_user_id = get_user_id(token)

    if not user_in_channel(channel_id, auth_user_id, store):
        raise AccessError('User is not a member of this channel.')

    channel = store['channels'][channel_id - 1]
    details = {
        'name': channel['name'],
        'is_public': channel['is_public'],
    }
    # Create a list of details for each owner and adds it to the 
    # details dictionary.
    details['owner_members'] = owner_members_list(channel, store)

    # Create a list of details for each member and adds it to the 
    # details dictionary.
    details['all_members'] = all_members_list(channel, store)

    return details

# Return the messages of a specific channel, given an valid user id and start 
# index.
# Arguments:
#   channel_id (int)   - id code of the channel
#   token (str)        - token used to authorise the user
#   start (int)        - the starting index of the returned messages
# Exceptions:
#   AccessError - Occurs when the token is invalid
#   InputError  - Occurs when the channel id is invalid
#   AccessError - Occurs when the user is not a member of the the channel
#   Input Error - Occurs when the start value is greater than the length of 
#                 the message bank
# Return value:
#   Returns {
#       'messages': [
#           {
#               'message_id': message_id,
#               'u_id': auth_user_id,
#               'message': <message>,
#               'time_created': time_created,
#           }
#       ],
#       'start': start,
#       'end': start + 50,
#   }
#   when no errors are raised
def channel_messages_v2(token, channel_id, start):
    store = data_store.get()
    channel_basic_exception_handling(token, channel_id, store)
    user_id = get_user_id(token)

    if not user_in_channel(channel_id, user_id, store):
        raise AccessError("User is not a member of this channel.")

    if not valid_start(channel_id, start, store):
        raise InputError(
            "Start value is greater than the total number of messages in \
            the channel")
    
    messages = messages_list(store, channel_id, start, user_id)
    
    return messages


# This function enables a user join a channel
# Arguments:
#   token (str) - The token of the user joining the channel
#   channel_id (int) - The id of the channel being joined
# Exceptions:
#   InputError  - Occurs when the channel_id is invalid
#   InputError  - Occurs if the user associated with token is already a member 
#                 of the channel
#   AccessError - Occurs when the channel is private and the user associated 
#                 with token is not a global owner
#   AccessError - Occurs when the token is invalid
# Return Value:
#     Returns {} if no exceptions occur during runtime
def channel_join_v2(token, channel_id):
    store = data_store.get()
    channel_basic_exception_handling(token, channel_id, store)
    auth_user_id = get_user_id(token)
    channel = store['channels'][channel_id - 1]

    if not channel['is_public'] and \
        store['users'][auth_user_id - 1]['permission_id'] == 2:
        raise AccessError('The channel is private and the \
            authorised user is not a global owner.')

    if user_in_channel(channel_id, auth_user_id, store):
        raise InputError('The authorised user is already member \
            of channel.')

    # Add the member to the channel
    add_member(store, auth_user_id, channel_id)
    update_stats_channels(auth_user_id)
    data_store.set(store)
    return {}

# This function lets a user leave a channel
# Arguments:
#   token (str) - The token of the user leaving the channel
#   channel_id (int) - The id of the channel being left
# Exceptions:
#   InputError  - Occurs when the channel_id does not refer to a valid 
#                 channel
#   AccessError - Occurs when the channel_id is valid and the authorised 
#                 user is not a member of the channel
#   AccessError - Occurs if the token is invalid
# Return Value:
#   Returns {} if no exceptions occur during runtime
def channel_leave_v1(token, channel_id):
    store = data_store.get()
    channel_basic_exception_handling(token, channel_id, store)
    user_id = get_user_id(token)

    if user_id in store['channels'][channel_id - 1]['all_members']:
        remove_member(store, user_id, channel_id)
        update_stats_channels(user_id)
    else:
        raise AccessError('channel_id is valid and the authorised user is not\
             a member of the channel')
    return {}

# This function lets a user with owner permissions to remove a user as an 
# owner of the channel
# Arguments:
#   token (str) - The token of the user removing the owner
#   channel_id (int) - The id of the channel
#   u_id (int)  - The id of the user being removed as owner
# Exceptions:
#   InputError  - Occurs when the channel_id does not refer to a valid 
#                 channel
#   InputError  - Occurs when the u_id does not refer to a valid user
#   InputError  - Occurs when the u_id refers to a user who is not an owner 
#                 of the channel
#   InputError  - u_id refers to a user who is currently the only owner of 
#                 the channel
#   AccessError - Occurs when the channel_id is valid and the authorised 
#                 user does not have owner permissions in the channel
#   AccessError - Occurs if the token is invalid
# Return Value:
#     Returns {} if no exceptions occur during runtime
def channel_removeowner_v1(token, channel_id, u_id):
    store = data_store.get()
    channel_owner_exceptions(channel_id, store, token, u_id)  

    if store['channels'][channel_id - 1]['owner_members'] == [u_id]:
        raise InputError('u_id refers to a user who is currently the only \
            owner of the channel')

    if u_id in store['channels'][channel_id - 1]['owner_members']:
        # Removing from owner list
        store['channels'][channel_id - 1]['owner_members'].remove(u_id)
        # If the user is not a global owner
        if store['users'][u_id - 1]['permission_id'] == 2:
            store['channels'][channel_id - 1]['owner_permissions'].remove(u_id)
    else:
        raise InputError('u_id refers to a user who is not an owner of the \
            channel')
    data_store.set(store)
    return {}

# This function lets a user with owner permissions to add a member as an 
# owner of the channel
# Arguments:
#   token (str) - The token of the user adding the member as owner
#   channel_id (int) - The id of the channel
#   u_id (int)  - The id of the member being added as owner
# Exceptions:
#   InputError  - Occurs when the channel_id does not refer to a valid 
#                 channel
#   InputError  - Occurs when the u_id does not refer to a valid user
#   InputError  - Occurs when the u_id refers to a user who is not a member 
#                 of the channel
#   InputError  - u_id refers to a user who is already an owner of the channel
#   AccessError - Occurs when the channel_id is valid and the authorised 
#                 user does not have owner permissions in the channel
#   AccessError - Occurs if the token is invalid
# Return Value:
#     Returns {} if no exceptions occur during runtime
def channel_addowner_v1(token, channel_id, u_id):
    store = data_store.get()
    channel_owner_exceptions(channel_id, store, token, u_id)  

    if not user_in_channel(channel_id, u_id, store):
        raise InputError('u_id refers to a user who is not a member of the \
        channel')

    if is_owner_of_channel(channel_id, store['channels'], u_id):
        raise InputError('u_id refers to a user who is already an owner of \
        the channel')
    
    channel = store['channels'][channel_id - 1]

    # If all exceptions are bypassed, add user as owner
    channel['owner_members'].append(u_id)
    channel['owner_permissions'].append(u_id)
    data_store.set(store)
    return {}