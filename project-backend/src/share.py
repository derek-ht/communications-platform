from src.helper import get_user_id, valid_token, generate_message_id, \
    user_in_channel, valid_channel_id, user_in_dm, update_stats_messages
from src.data_store import data_store
from src.error import AccessError, InputError
import time
from src.channels import channels_list_v2
from src.dm import dm_list_v1
from src.notifications import tag_notification

# Checks if dm id exists in store
def valid_dm_id(dm_id, store):
    for dm in store['dms']:
        if dm['dm_id'] == dm_id:
            return True
    return False

# Checks if message id exists in store
def valid_message(token, message_id, store):
    channels = [channel["channel_id"] for channel in \
        channels_list_v2(token)["channels"]]
    # Searches dms for message id
    dms = [dm["dm_id"] for dm in dm_list_v1(token)["dms"]]
    for dm in store['dms']:
        if dm['dm_id'] in dms:
            for message in dm["messages"]:
                if message["message_id"] == message_id:
                    return True
    # Searches channels for message_id
    for channel in store['channels']:
        if channel['channel_id'] in channels:
            for message in channel["messages"]:
                if message["message_id"] == message_id:
                    return True
    
    return False

# Gets message at message_id
def get_message(message_id, store):
    # Searches channels
    for channel in store['channels']:
        for message in channel["messages"]:
            if message["message_id"] == message_id:
                return message["message"]
    # Searches dms
    for dm in store['dms']:
        for message in dm["messages"]:
            if message["message_id"] == message_id:
                return message["message"]

# Adds the message to a given channel
def add_message_to_channel(store, channel_id, message_dict):
    for channel in store["channels"]:
        if channel["channel_id"] == channel_id:
            channel["messages"].append(message_dict)
    # Increment user's message_count
    store['users'][message_dict['u_id'] - 1]['message_count'] += 1
    update_stats_messages(message_dict['u_id'])

# Adds the message to a given dm
def add_message_to_dm(store, dm_id, dm_message):
    for dm in store['dms']:
        if dm_id == dm['dm_id']:
            dm['messages'].append(dm_message)
    # Increment user's message_count
    store['users'][dm_message['u_id'] - 1]['message_count'] += 1
    update_stats_messages(dm_message['u_id'])

#########################
# Shares given message to another channel with the option to add a message
# Arguments:
#   token (str)         - token used to authorise the user
#   og_message_id (int) - message id of messsage to be shared
#   message (str)       - optional message to be sent with the shared message
#   channel_id (int)    - Channel id of channel the original message is from (0 if in dm)
#   dm_id (int)         - Dm id of channel the original message is from (0 if in channel)
# Exceptions:
#   Input error - occurs when both channel_id and dm_id are invalid
#   Input error - occurs when neither channel_id nor dm_id are -1
#   Input error - occurs when og_message_id does not refer to a valid message 
#                 within a channel/DM that the authorised user has joined
#   Input error - occurs when length of message is more than 1000 characters
#   Access Error - Occurs when the token is invalid
#   Access Error - the pair of channel_id and dm_id are valid (i.e. one is -1, 
#                  the other is valid) and the authorised user has not joined 
#                  the channel or DM they are trying to share the message to 
# Return value:
#   Returns {"shared_message_id": message_id}
def message_share_v1(token, og_message_id, message, channel_id, dm_id):
    store = data_store.get()
    
    if not valid_token(token):
        raise AccessError("invalid token")

    message_id = -1
    # Assures either given dm id or channel id is -1
    if channel_id != -1 and dm_id == -1:
        message_id = share_channel_message(token, og_message_id, message, channel_id, store)
        tag_notification(token, channel_id, message, True)
    elif channel_id == -1 and dm_id != -1:
        message_id = share_dm_message(token, og_message_id, message, dm_id, store)
        tag_notification(token, dm_id, message, False)
    else:
        raise InputError("No minus ones")
    data_store.set(store)
    
    return {
        "shared_message_id": message_id
    }

# Shares mesage to channel
def share_channel_message(token, og_message_id, message, channel_id, store):
    if not valid_channel_id(channel_id, store):
        raise InputError("Invalid channel id")
    
    if not user_in_channel(channel_id, get_user_id(token), store):
        raise AccessError("User not in channel")

    if not valid_message(token, og_message_id, store):
        raise InputError("Message doesn't exisit")
    
    og_message = get_message(og_message_id, store)
    share_message, message_id = create_share_message(token, og_message, message, store)
    add_message_to_channel(store, channel_id, share_message)

    return message_id

# Shares message to dm
def share_dm_message(token, og_message_id, message, dm_id, store):
    if not valid_dm_id(dm_id, store):
        raise InputError("Invalid dm")
    
    if not user_in_dm(dm_id, token):
        raise AccessError("User not in dm")
    
    if not valid_message(token, og_message_id, store):
        raise InputError("Dm message doesn't exist")
    
    og_message = get_message(og_message_id, store)
    share_message, message_id = create_share_message(token, og_message, message, store)
    add_message_to_dm(store, dm_id, share_message)

    return message_id

# Creates message dict for shared message
def create_share_message(token, og_message, extra_message, store):
    if len(extra_message) > 1000:
        raise InputError("Extra message too long")
    
    message_id = generate_message_id(store)

    share_message = { 
    "message_id": message_id,
    "u_id": get_user_id(token),
    "message": f"{extra_message}\n-----\n{og_message}\n-----",
    "time_created": int(time.time()),
    "reacts": [],
    "is_pinned": False
    }

    return share_message, message_id