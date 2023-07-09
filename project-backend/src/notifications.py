from src.data_store import data_store
from src.helper import get_user_id, valid_token
from src.error import AccessError

# Creates notificaiton dict with given items
def generate_notification_dict(channel_id, dm_id, notif_message):
    notif = {
        "channel_id": channel_id,
        "dm_id": dm_id,
        "notification_message": notif_message
    }
    return notif

# Adds notification to user
def add_notif_to_user(user_id, notification):
    store = data_store.get()
    for user in store["users"]:
        if user["user_id"] == user_id:
            user["notifications"].append(notification)

# Gets handle of user
def get_user_handle(token):
    store = data_store.get()
    user_id = get_user_id(token)
    for user in store["users"]:
        if user["user_id"] == user_id:
            return user["handle_str"]

# Gets name of channel at channel id
def get_channel_name(channel_id):
    store = data_store.get()
    for channel in store["channels"]:
        if channel["channel_id"] == channel_id:
            return channel["name"]

# Gets name of dm at dm id
def get_dm_name(dm_id):
    store = data_store.get()
    for dm in store["dms"]:
        if dm["dm_id"] == dm_id:
            return dm["name"]

# Gets notifications of user
# Arguments:
#   token (str) - token of authorized user
# Exceptions:
#   N/A
# Return value:
#   Returns {"notification": [{ "channel_id": channel_id, "dm_id": dm_id, 
#                                "notification_message": notif_message } ... ]}
def notifications_get_v1(token):
    store = data_store.get()
    
    if not valid_token(token):
        raise AccessError
    
    notifications = []

    user_id = get_user_id(token)
    # Searches for user with given user id and retrieves first 20 notificaitons
    for user in store["users"]:
        if user["user_id"] == user_id:
            notifications = user["notifications"][-20:]
    
    return {
        "notifications": notifications
    }

# Adds a notification to tagged user
def tag_notification(token, group_id, message, is_channel):
    user_handle = get_user_handle(token)
    store = data_store.get()
    reciever_id = -1

    # Looks for user handle in message
    words = message.split()
    for word in words:
        if word[0] == '@':
            # Gets user id of user with user handle
            for user in store['users']:
                if word[1:] == user['handle_str']:
                    reciever_id = user["user_id"]
    
    # If no user id is found with given user handle, or message has no tag, quits
    if reciever_id == -1:
        return

    # Looks for channel or dm name of where the message was sent
    group_name = "Not Initialized"
    if is_channel:
        dm_id = -1
        channel_id = group_id
        group_name = get_channel_name(group_id)
    else:
        dm_id = group_id
        channel_id = -1
        group_name = get_dm_name(group_id)
    
    notif_message = f"{user_handle} tagged you in {group_name}: {message[:20]}"
    notif = generate_notification_dict(channel_id, dm_id, notif_message)
    add_notif_to_user(reciever_id, notif)

# Gets the user id of the user who sent the message at the message_id
def get_user_id_from_message(message_id):
    store = data_store.get()
    # Looks for message id in dms
    for dm in store['dms']:
        if len(dm['messages']) != 0:
            for message in dm["messages"]:
                if message["message_id"] == message_id:
                    return message["u_id"]
    # Looks for message id in dms
    for channel in store['channels']:
        if len(channel['messages']) != 0:
            for message in channel["messages"]:
                if message["message_id"] == message_id:
                    return message["u_id"]

# Adds notification to user whose message got reacted
def react_notification(token, group_id, is_channel, message_id):
    user_handle = get_user_handle(token)
    reciever_id = get_user_id_from_message(message_id)
    
    # Gets channel or dm name of the reacted message
    group_name = "Not Initialized"
    if is_channel:
        dm_id = -1
        channel_id = group_id
        group_name = get_channel_name(group_id)
    else:
        dm_id = group_id
        channel_id = -1
        group_name = get_dm_name(group_id)
    
    notif_message = f"{user_handle} reacted to your message in {group_name}"

    notif = generate_notification_dict(channel_id, dm_id, notif_message)
    add_notif_to_user(reciever_id, notif)

# Adds notification to users who are added to a dm or channel
def added_notification(token, group_id, is_channel, reciever_id):
    user_handle = get_user_handle(token)
    
    # Gets channel or dm name of the group the user was added to
    group_name = "Not Initialized"
    if is_channel:
        dm_id = -1
        channel_id = group_id
        group_name = get_channel_name(group_id)
    else:
        dm_id = group_id
        channel_id = -1
        group_name = get_dm_name(group_id)

    notif_message = f"{user_handle} added you to {group_name}"
    
    notif = generate_notification_dict(channel_id, dm_id, notif_message)
    add_notif_to_user(reciever_id, notif)

