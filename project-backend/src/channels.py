from src.data_store import data_store
from src.error import InputError, AccessError
from src.helper import valid_token, get_user_id, update_stats_channels

# Checks for valid ch_name (1 - 20 characters inclusive) and returns a bool
def channel_name_valid(ch_name):
    if len(ch_name) in range(1, 21):
        return True
    else:
        return False

# This function adds the new channel dict to data_store
def add_channel(store, name, channel_id, user_id, is_public):
    # Adds new channel to data_store
    store['channels'].append({'channel_id': channel_id, 
                                'name': name, 
                                'is_public': is_public, 
                                'owner_members': [user_id], 
                                'owner_permissions': [user_id], 
                                'all_members': [user_id],
                                'messages': [], 
                                'standup': {'started_by': None, 'messages': [],
                                'time_finish': None}
                            })

    # Adds new channel to user['channels']
    store['users'][user_id - 1]['channels'].append(channel_id)

# This function returns a list of channels which the user is involved in
def append_channels(store, user_id):
    channels_list = {
        "channels": []
    }
    # Loops through each channel in store the user is a part of
    for channel in store["channels"]:
        if user_id in channel["all_members"]:
            # Records channel's id and name and appends to the list
            channel_details = {
                'channel_id': channel['channel_id'],
                'name': channel['name']
            }
            channels_list["channels"].append(channel_details)

    return channels_list

# This function returns a list of channels in the entirety of streams
def gathering_channels(store):
    channels_list = {
        "channels": []
    }

    # Gathers channel's id and name from each channel in datastore
    for channel in store["channels"]:
        channel_details = {
            'channel_id': channel['channel_id'],
            'name': channel['name']
        }
        channels_list["channels"].append(channel_details)

    return channels_list

# Creates a channel, and adds it to data_store
# Arguments:
#       token (str)         - Token of user creating channel
#       name (str)          - Name of created channel
#       is_public (bool)    - Whether created channel to be public or private
# Exceptions:
#       InputError          - Occurs when intended channel name is invalid 
#                             (not within 1 - 20 characters inclusive)
#       AccessError         - Occurs when user tries to create a channel
#                             with an invalid user token
# Return Value:
#       Returns dict, {'channel_id': channel_id},
#           when user token is valid and channel name is valid
def channels_create_v2(token, name, is_public):
    store = data_store.get()
    
    # Check user token is valid 
    if not valid_token(token):
        raise AccessError("Invalid user token")

    # Check ch_name // 1-20 length
    if not channel_name_valid(name):
        raise InputError("Invalid channel name")

    # Gets u_id of user creating channel
    user_id = get_user_id(token)

    # Assigns new ch_id to be next int in list
    channel_id = len(store['channels']) + 1

    add_channel(store, name, channel_id, user_id, is_public)

    data_store.set(store)

    update_stats_channels(user_id)
    return {
        'channel_id': channel_id
    }

# Returns a list of all channels the authorised user is a part of 
# Arguments:
#       token (str)): Token of user
# Return Value:
#       Returns list of dictionaries in dict channels_list {
#           "channels": [{
#               "channel_id": channel_id
#               "name": "channel_name"
#           }]
#       }
def channels_list_v2(token):
    store = data_store.get()
    
    # Check user_id is valid
    if not valid_token(token):
        raise AccessError("Invalid token")
    
    user_id = get_user_id(token)

    channels_list = append_channels(store, user_id)

    return channels_list

# Returns a list of all channels in datastore
# Arguments:
#       token (str)): Token of user
# Return Value:
#       Returns list of dictionaries in dict channels_list {
#           "channels": [{
#               "channel_id": channel_id
#               "name": "channel_name"
#           }]
#       }
def channels_listall_v2(token):    
    store = data_store.get()

    # Check user_id is valid
    if not valid_token(token):
        raise AccessError("Invalid token")

    channels_list = gathering_channels(store)

    return channels_list