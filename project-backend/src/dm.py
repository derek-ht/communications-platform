from src.data_store import data_store
from src.error import InputError, AccessError
from src.notifications import added_notification
from src.helper import valid_user_id, valid_token, get_user_id, user_in_dm,\
                        update_stats_dms, update_stats_messages

# Handles exceptions for dm_remove
def exception_handling_for_dm_remove(token, dm_id, store):
    # Check user token is valid 
    if not valid_token(token):
        raise AccessError("Invalid user token")

    # Check dm_id is valid
    if not valid_dm_id(dm_id, store):
        raise InputError("Dm_id is invalid")

# Handles basic exceptions for dm functions
def dm_basic_exception_handling(token, dm_id, store):
    exception_handling_for_dm_remove(token, dm_id, store)

    if not user_in_dm(dm_id, token):
        raise AccessError("User is not a member of this dm.")

# Generates a dm_id
def dm_id_generation(store):
    # Assign dm_id to be next int in list
    if store['dms'] == []:
        dm_id = 1
    else:
        # Taking the latest dm_id and adding 1
        dm_id = store['dms'][-1]['dm_id'] + 1
    return dm_id

# Gets handles of u_ids and makes into dm name
def dm_name_generation(store, owner_id, u_ids):
    handles = []
    if owner_id not in u_ids:
        # Deals with case when owner invites themself for dm
        u_ids.append(owner_id)
    for users in store['users']:
        if users['user_id'] in u_ids:
            handles.append(users['handle_str'])
    handles.sort()
    dm_name = ', '.join(handles)
    return dm_name

# Adds dm to the datastore and updates the dms which the user is involed in
def adding_dm_to_data(store, dm_id, dm_name, owner_id, u_ids):
    # Add new dm to data_store
    store['dms'].append({
        'dm_id': dm_id,
        'name': dm_name,
        'owner': [owner_id],
        'all_members': u_ids,
        'messages': []
    })
    # Add dms to users['dms']
    for user_id in u_ids:
        store['users'][user_id - 1]['dms'].append(dm_id)
        update_stats_dms(user_id)

# Checks if dm_id exists in data_store and returns a bool
def valid_dm_id(dm_id, store):
    for dms in store['dms']:
        if dm_id == dms['dm_id']:
            return True
    return False

# Returns a list of all users in the dm
def dm_users_list(store, user_ids):
    # Gets details for members of dm
    user_list = []
    for user in store['users']:
        if user['user_id'] in user_ids:
            user_list.append({
                'u_id': user['user_id'],
                'email': user['email'],
                'name_first': user['name_first'],
                'name_last': user['name_last'],
                'handle_str': user['handle_str']})
    return user_list

# Check if the start value exists in the message bank and return a boolean.
def valid_start(dm_id, start, store):
    dm = store['dms'][dm_id - 1]
    if start > len(dm['messages']):
        return False
    return True

# Creates a list of messages from the given dm, beginning at the start 
# index and ending after 50 messages have been appended or the message bank 
# ends. Return end = -1 if less than 50 messages are returned.
def messages_list(store, dm_id, start, user_id):
    messages = {'messages': []}
    for dm in store['dms']:
        if dm['dm_id'] == dm_id:
            count = 0
            for message in reversed(dm['messages']):
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

    if start + 50 < len(dm['messages']):
        messages['end'] = start + 50
    else:
        messages['end'] = -1
    return messages

# Returns a list of all users and name of the dm with dm_id
def generating_user_lists(store, dm_id):
    # Retrieving details from dm
    for dms in store['dms']:
        if dms['dm_id'] == dm_id:
            dm_name = dms['name']
            user_ids = dms['all_members']

    # Gets details for members of dm
    user_list = dm_users_list(store, user_ids)
    return user_list, dm_name

def remove_dm_if_owner(store, dm_id, user_id):
    # Check if user is owner of dm_id
    for dms in store['dms']:
        if dms['dm_id'] == dm_id:
            if user_id not in dms['owner']:
                raise AccessError("User is not owner of dm")
            else:
                remove_dm_user_dm_id(store, dms)
                remove_dm_messages(store, dms, user_id)
                store['dms'].remove(dms)
                update_stats_dms(user_id)

# Removes the dm_id from the users' dms list who were in the dm                
def remove_dm_user_dm_id(store, dms):
    for user_id in dms['all_members']:
        store['users'][user_id - 1]['dms'].remove(dms['dm_id'])
        update_stats_dms(user_id)
        
# Removes all the messages from a dm
def remove_dm_messages(store, dms, user_id):
    for message_dict in reversed(dms['messages']):
        dms['messages'].remove(message_dict)
        update_stats_messages(user_id)
        
    

# Removes the user from the dm
def remove_user_from_dm(store, dm_id, user_id):
    for dms in store['dms']:
        if dms['dm_id'] == dm_id:
            dms['all_members'].remove(user_id)
            # Removes the dm_id from the user's dms list who was in that dm
            store['users'][user_id - 1]['dms'].remove(dms['dm_id'])
            if user_id in dms['owner']:
                dms['owner'].remove(user_id)
                
            if dms['all_members'] == [] and dms['owner'] == []:
                # Removes dm if no members left
                remove_dm_messages(store, dms, user_id)
                store['dms'].remove(dms)
    
# Creates a dm, and adds it to data_store.
# Arguments:
#       token (str)         - Token of user creating dm
#       u_ids (list)        - List of user_ids of users to be added to dm
#       
# Exceptions:
#       InputError          - Occurs when any of users in u_ids is not
#                             a valid user_id
#       InputError          - Occurs when u_id has duplicate users
#                             or is an empty list
#       AccessError         - Occurs when user tries to create a channel
#                             with an invalid user token
#
# Return Value:
#       Returns dict, {'dm_id': dm_id},
#           when user token is valid and u_ids is of valid users
def dm_create_v1(token, u_ids):
    store = data_store.get()

    # Check user token is valid 
    if not valid_token(token):
        raise AccessError("Invalid user token")

    # Check u_ids are all valid
    for user in u_ids:
        if not valid_user_id(store['users'], user):
            raise InputError("u_ids does not refer to a valid user")

    # Checks u_id does not contain duplicates
    if len(u_ids) != len(set(u_ids)):
        raise InputError("u_ids contains duplicate users")

    # Gets u_id of user creating channel
    owner_id = get_user_id(token)
    dm_id = dm_id_generation(store)
    dm_name = dm_name_generation(store, owner_id, u_ids)
    adding_dm_to_data(store, dm_id, dm_name, owner_id, u_ids)
    data_store.set(store)
    # Adds notifications for users added to dm
    for u_id in u_ids:
        if u_id != owner_id:
            added_notification(token, dm_id, False, u_id)
    data_store.set(store)
    
    return {'dm_id': dm_id}

# Gets a list of dms the user if part of
#
# Arguments:
#       token (str)         - Token of user
#       
# Exceptions:
#       AccessError         - Occurs when user tries to access
#                             with an invalid user token
#
# Return Value:
#       Returns dict, {'dms': dm_list},
#           when user token is valid
def dm_list_v1(token):
    store = data_store.get()

    # Check user token is valid 
    if not valid_token(token):
        raise AccessError("Invalid user token")

    # Gets u_id of user
    user_id = get_user_id(token)

    # Checks if dms are valid and adds to return list
    dm_list = []
    for dms in store['dms']:
        if user_id in dms['all_members']:
            dm_list.append({
                'dm_id': dms['dm_id'],
                'name': dms['name']
            })

    return {"dms": dm_list}

# Removes an existing dm that user is owner of
#
# Arguments:
#       token (str)         - Token of user
#       dm_id (int)         - Id of dm due to be removed
#       
# Exceptions:
#       InputError          - Occurs when dm_id does not refer to any
#                             existing dm
#       AccessError         - Occurs when user tries to access
#                             with an invalid user token
#       AccessError         - Occurs when user is not owner of dm
#
# Return Value:
#       Returns dict, {},
#           when user token is valid, dm_id is valid,
#           and user is owner of dm
def dm_remove_v1(token, dm_id):
    store = data_store.get()
    dm_basic_exception_handling(token, dm_id, store)

    # Gets u_id of user removing channel
    user_id = get_user_id(token)
    remove_dm_if_owner(store, dm_id, user_id)
    data_store.set(store)

    return {}

# Gets a dict of details about the dm
#
# Arguments:
#       token (str)         - Token of user
#       dm_id (int)         - Id of dm to get details from
#       
# Exceptions:
#       InputError          - Occurs when dm_id does not refer to any
#                             existing dm
#       AccessError         - Occurs when user tries to access
#                             with an invalid user token
#       AccessError         - Occurs when user is not member of dm
#
# Return Value:
#       Returns dict, {'name': dm_name, 'members': user_list},
#           when user token is valid, dm_id is valid,
#           and user is member or owner of dm
def dm_details_v1(token, dm_id):
    store = data_store.get()
    dm_basic_exception_handling(token, dm_id, store)

    user_list, dm_name = generating_user_lists(store, dm_id)

    return {'name': dm_name, 'members': user_list}

# Leaves a dm the user is part of
#
# Arguments:
#       token (str)         - Token of user
#       dm_id (int)         - Id of dm due to leave from
#       
# Exceptions:
#       InputError          - Occurs when dm_id does not refer to any
#                             existing dm
#       AccessError         - Occurs when user tries to access
#                             with an invalid user token
#       AccessError         - Occurs when user is not member of dm
#
# Return Value:
#       Returns dict, {'name': dm_name, 'members': user_list},
#           when user token is valid, dm_id is valid,
#           and user is member or owner of dm
def dm_leave_v1(token, dm_id):
    store = data_store.get()
    dm_basic_exception_handling(token, dm_id, store)

    user_id = get_user_id(token)
    remove_user_from_dm(store, dm_id, user_id)
    data_store.set(store)
    update_stats_dms(user_id)
    return {}
    
# Return the messages of a specific dm, given a valid token, dm_id and start 
# index.
# Arguments:
#   dm_id (int)        - id code of the dm
#   token (str)        - token used to authorise the user
#   start (int)        - the starting index of the returned messages
# Exceptions:
#   AccessError - Occurs when the token is invalid
#   InputError  - Occurs when the dm id is invalid
#   AccessError - Occurs when the user is not a member of the the dm
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
#   when no errors are raised and at least 50 messages are appended
def dm_messages_v1(token, dm_id, start):
    store = data_store.get()
    dm_basic_exception_handling(token, dm_id, store)

    if not valid_start(dm_id, start, store):
        raise InputError(
            "Start value is greater than the total number of messages in \
            the dm")
    
    user_id = get_user_id(token)
    messages = messages_list(store, dm_id, start, user_id)

    return messages