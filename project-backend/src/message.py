from src.helper import get_user_id, valid_token, generate_message_id, \
    user_in_channel, valid_channel_id, user_in_dm, update_stats_messages
from src.data_store import data_store
from src.error import AccessError, InputError
from src.notifications import react_notification, tag_notification
import time
import threading

react_list = [1]

# Check if the dm_id exists inside of data_store.
def valid_dm_id(dm_id, store):
    for dms in store['dms']:
        if dm_id == dms['dm_id']:
            return True
    return False

# Check if the message is in between 1 and 1000, inclusively
def valid_message(message):
    if len(message) in range(1,1001):
        return True
    return False

# Returns a dictionary containing message details
def generate_message_dict(message_id, token, message):
    user_id = get_user_id(token)
    time_created =  int(time.time())
    message_dict = {
        "message_id": message_id,
        "u_id":user_id,
        "message": message,
        "time_created": time_created,
        "reacts": [],
        "is_pinned": False
    }
    return message_dict

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

# Looks through the user's channels to find the message
# If user does not have permission, raise an AccessError
# If message is found, edit the message
def edit_message_in_dm(dm, message_id, user_id, message):
    # Looks for the message_id in messages of dms
    for message_dict in dm["messages"]:
        if message_dict["message_id"] == message_id:
            # Checks if user has permissions to edit
            if message_dict["u_id"] == user_id or user_id in \
                dm["owner"]:
                edit_or_remove_message(message, message_dict, 
                dm["messages"])
                update_stats_messages(user_id)
                return True
            else:
                raise AccessError("Only owners can edit another \
                    member's message")
    return False

# Looks through the user's dms to find the message
# If user does not have permission, raise an AccessError
# If message is found, edit the message
def edit_message_in_channel(channel, message_id, user_id, message):
    # Looks for the message_id in messages of channels
    for message_dict in channel["messages"]:
        if message_dict["message_id"] == message_id:
            # Checks if user has permissions to edit
            if message_dict["u_id"] == user_id or user_id in \
                channel["owner_permissions"]:
                edit_or_remove_message(message, message_dict, 
                channel["messages"])
                update_stats_messages(user_id)
                return True
            else:
                raise AccessError("Only owners can edit another \
                    member's message")
    return False

# Edits or removes the message depending on whether the message is empty or not
def edit_or_remove_message(message, message_dict, messages):
    # Checks if edit is empty
    if message == "":
        messages.remove(message_dict)
    else:
        message_dict["message"] = message

# Looks through the user's dms to find the message
# If user does not have permission, raise an AccessError
# If message is found, delete the message
def delete_message_in_dm(dm, message_id, user_id):
    for message_dict in dm["messages"]:
        if message_dict["message_id"] == message_id:
            if message_dict["u_id"] == user_id or user_id in \
                dm["owner"]:
                dm["messages"].remove(message_dict)
                return True
            else:
                raise AccessError("Only owners can edit another \
                    member's message")
    return False

# Looks through the user's channels to find the message
# If user does not have permission, raise an AccessError
# If message is found, delete the message
def delete_message_in_channel(channel, message_id, user_id):
    # Looks for message to edit in messages of channel
    for message_dict in channel["messages"]:
        if message_dict["message_id"] == message_id:
            # Checks if user has permissions to remove
            if message_dict["u_id"] == user_id or user_id in \
                channel["owner_permissions"]:
                channel["messages"].remove(message_dict)
                return True
            else:
                raise AccessError("Only owners can edit another \
                    member's message")
    return False

# Adds the react to the message
# Gives InputError is user already reacted
def add_react(message_dict, react_id, user_id):
    # Adds to an existing react
    for react in message_dict['reacts']:
        # Causes coverage error only cause 1 react_id exists so far
        if react['react_id'] == react_id:
            # Checks if user already reacted
            if user_id in react['u_ids']:
                raise InputError("Already contains this react")
            else:
                react['u_ids'].append(user_id)
                return True

    # Adds a new react
    new_react = {
        'react_id': react_id,
        'u_ids': [user_id],
        'is_this_user_reacted': False
    }
    message_dict['reacts'].append(new_react)
    return True

# Finds the message in the dm to add a react to
def add_react_in_dm(dm, message_id, user_id, react_id):
    # Looks for the message_id in messages of dms
    for message_dict in dm["messages"]:
        if message_dict["message_id"] == message_id:
            # Adds the react proper
            add_react(message_dict, react_id, user_id)
            return True
    return False

# Finds the message in the ch to add a react to
def add_react_in_channel(channel, message_id, user_id, react_id):
    # Looks for the message_id in messages of channels
    for message_dict in channel["messages"]:
        if message_dict["message_id"] == message_id:
            # Adds the react proper
            add_react(message_dict, react_id, user_id)
            return True
    return False

# Removes the react from the message and removes react dict if no reacts left
def unreact_msg(message_dict, react, react_id, user_id):
    # Checks if user has reacted
    if user_id in react['u_ids']:
        react['u_ids'].remove(user_id)
        # Removes react if no users left
        if react['u_ids'] == []:
            message_dict['reacts'].remove(react)
        return True
    return False

# Finds msg to unreact
def unreact_find_msg(message_dict, react_id, user_id):
    for react in message_dict['reacts']:
        # Causes coverage error only cause 1 react_id exists so far
        if react['react_id'] == react_id:
            # Adds the react proper
            if unreact_msg(message_dict, react, react_id, user_id):
                return True

    # If unable to find the message in the ch/dm            
    raise InputError("Message does not contain a react with ID react_id \
        from the user")

# Finds the message in the dm to add a react to
def unreact_in_dm(dm, message_id, user_id, react_id):
    # Looks for the message_id in messages of dms
    for message_dict in dm["messages"]:
        if message_dict["message_id"] == message_id:
            # Adds the react proper
            unreact_find_msg(message_dict, react_id, user_id)
            return True
    return False

# Finds the message in the ch to add a react to
def unreact_in_channel(channel, message_id, user_id, react_id):
    # Looks for the message_id in messages of channels
    for message_dict in channel["messages"]:
        if message_dict["message_id"] == message_id:
            # Adds the react proper
            unreact_find_msg(message_dict, react_id, user_id)
            return True
    return False

# Does a permissions check and either pins or unpins a message in a channel
def pin_do_dm(dm, message_dict, user_id, do_pin):
    # Path if function is to pin
    if do_pin is True:
        # Checks for user permissions
        if user_id in dm["owner"]:
            # Checks if message is already pinned
            if message_dict["is_pinned"]:
                raise InputError("Message already pinned")
            else:
                message_dict["is_pinned"] = True
                return True
        else:
            raise AccessError("Only owners can pin messages")
    
    else:
        # Checks for user permissions
        if user_id in dm["owner"]:
            # Checks if message is already pinned
            if message_dict["is_pinned"]:
                message_dict["is_pinned"] = False
                return True
            
            else:
                raise InputError("Message is not pinned")
        
        else:
            raise AccessError("Only owners can unpin messages")

# Does a permissions check and either pins or unpins a message in a dm
def pin_do_ch(channel, message_dict, user_id, do_pin):
    # Path if function is to pin
    if do_pin is True:
        # Checks for user permissions
        if user_id in channel["owner_permissions"]:
            # Checks if message is already pinned
            if message_dict["is_pinned"]:
                raise InputError("Message already pinned")
            else:
                message_dict["is_pinned"] = True
                return True
        else:
            raise AccessError("Only owners can pin messages")
    
    else:
        # Checks for user permissions
        if user_id in channel["owner_permissions"]:
            # Checks if message is already pinned
            if message_dict["is_pinned"]:
                message_dict["is_pinned"] = False
                return True
            else:
                raise InputError("Message is not pinned")
        
        else:
            raise AccessError("Only owners can unpin messages")



# Finds the message in the dm and pins if perms permit
def pin_in_dm(dm, message_id, user_id):
    # Looks for the message_id in messages of dms
    for message_dict in dm["messages"]:
        if message_dict["message_id"] == message_id:
            if pin_do_dm(dm, message_dict, user_id, True):
                return True
    return False

# Finds the message in the ch and pins if perms permit
def pin_in_channel(channel, message_id, user_id):
    # Looks for the message_id in messages of channels
    for message_dict in channel["messages"]:
        if message_dict["message_id"] == message_id:
            if pin_do_ch(channel, message_dict, user_id, True):
                return True
    return False

# Finds the message in the dm and pins if perms permit
def unpin_in_dm(dm, message_id, user_id):
    # Looks for the message_id in messages of dms
    for message_dict in dm["messages"]:
        if message_dict["message_id"] == message_id:
            if pin_do_dm(dm, message_dict, user_id, False):
                return True
    return False

# Finds the message in the ch and pins if perms permit
def unpin_in_channel(channel, message_id, user_id):
    # Looks for the message_id in messages of channels
    for message_dict in channel["messages"]:
        if message_dict["message_id"] == message_id:
            if pin_do_ch(channel, message_dict, user_id, False):
                return True
    return False


# Sends message to given channel_id
# Arguments:
#   token (str)        - token used to authorise the user
#   channel_id (int)   - id of channel where the message is to be sent
#   message (str)      - message to be sent
# Exceptions:
#   AccessError - Occurs when the token is invalid
#   InputError  - Occurs when the channel id is invalid
#   InputError  - Occurs when the length of the message is less than 1 or over
#                 1000 characters
#   AccessError - Occurs when the user is not a member of the the channel
#   
# Return value:
#   Returns {message_id : message_id}
#   when no errors are raised
def message_send_v1(token, channel_id, message):
    store = data_store.get()

    # Check invalid token
    if not valid_token(token):
        raise AccessError("Invalid token")

    # Check input errors
    if message == "":
        raise InputError("Message is too short")
    if len(message) > 1000:
        raise InputError("Message is too long")

    if not valid_channel_id(channel_id, store):
        raise InputError("Channel with given channel_id does not exist")

    user_id = get_user_id(token)
    if not user_in_channel(channel_id, user_id, store):
        raise AccessError("User is not in channel of given channel id")

    # Set up dict for message
    message_id = generate_message_id(store)
    message_dict = generate_message_dict(message_id, token, message)

    # Looks for channel id in data_store and appends message to messages
    add_message_to_channel(store, channel_id, message_dict)

    tag_notification(token, channel_id, message, True)
    data_store.set(store)

    return {
        "message_id": message_id
    }

# Return the messages of a specific dm, given a valid user id and start 
# index.
# Arguments:
#   dm_id (int)        - id code of the dm
#   token (str)        - token used to authorise the user
#   store (list)       - list of dictionaries containing user information
#   message (str)      - message to be sent
# Exceptions:
#   AccessError - Occurs when the token is invalid
#   InputError  - Occurs when the dm id is invalid
#   InputError  - Occurs when the length of the message is less than 1 or over
#                 1000 characters
#   AccessError - Occurs when the user is not a member of the the dm
#   
# Return value:
#   Returns {message_id : message_id}
#   when no errors are raised
def message_senddm_v1(token, dm_id, message):
    store = data_store.get()

    if not valid_token(token):
        raise AccessError("Invalid token")
    
    if not valid_dm_id(dm_id, store):
        raise InputError("Invalid dm ID.")

    if not valid_message(message):
        raise InputError("The length of the message must be in between 1 and \
            1000, inclusively")

    if not user_in_dm(dm_id, token):
        raise AccessError("User is not a member of this dm.")
    
    message_id = generate_message_id(store)
    dm_message = generate_message_dict(message_id, token, message)

    add_message_to_dm(store, dm_id, dm_message)

    tag_notification(token, dm_id, message, False)
    data_store.set(store)

    return {"message_id" : message_id}

# Removes message with given message_id
# Arguments:
#   token (str)        - token used to authorise the user
#   message_id (int)   - message id of messsage to be removed
#   message (str)      - new message to replace message at message_id
# Exceptions:
#   AccessError - Occurs when the token is invalid
#   InputError  - Occurs when the message_id does not refer to a valid message 
#   within the channel or dm the user has joined
#   InputError  - Occurs when the message is longer than 1000 characters
#   AccessError - Occurs when the user does not have permissions to remove 
#   other member's messages
# Return value:
#   Returns {}
def message_edit_v1(token, message_id, message):

    if not valid_token(token):
        raise AccessError("Invalid token")

    if len(message) > 1000:
        raise InputError("Message too long")

    store = data_store.get()
    user_id = get_user_id(token)
    user_channels = store["users"][user_id - 1]["channels"]
    user_dms = store["users"][user_id - 1]["dms"]
    
    # Looping through the user's dms
    for dm in store["dms"]:
        if dm["dm_id"] in user_dms:
            if edit_message_in_dm(dm, message_id, user_id, message):
                tag_notification(token, dm["dm_id"], message, False)
                data_store.set(store)
                return {}

    # Loops through the channels the user has joined
    for channel in store["channels"]:
        if channel["channel_id"] in user_channels:
           if edit_message_in_channel(channel, message_id, user_id, message):
               tag_notification(token, channel["channel_id"], message, True)
               data_store.set(store)
               return {}

    # Message_id wasn't found
    raise InputError("The given message_id either does not exist or is not in \
        a channel the user is in")

# Removes message with given message_id
# Arguments:
#   token (str)        - token used to authorise the user
#   message_id (int)   - message id of messsage to be removed
# Exceptions:
#   AccessError - Occurs when the token is invalid
#   InputError  - Occurs when the message_id does not refer to a valid message 
#   within the channel or dm the user has joined
#   AccessError - Occurs when the user does not have permissions to remove 
#   other member's messages
# Return value:
#   Returns {}
def message_remove_v1(token, message_id):
    if not valid_token(token):
        raise AccessError("Invalid token")

    store = data_store.get()
    user_id = get_user_id(token)
    user_channels = store["users"][user_id - 1]["channels"]
    user_dms = store["users"][user_id - 1]["dms"]

    # Looping through user's dms
    for dm in store["dms"]:
        if dm["dm_id"] in user_dms:
            if delete_message_in_dm(dm, message_id, user_id):
                update_stats_messages(user_id)
                data_store.set(store)
                return {}
    # Loops through the channels the user has joined
    for channel in store["channels"]:
        if channel["channel_id"] in user_channels:
            if delete_message_in_channel(channel, message_id, user_id):
                update_stats_messages(user_id)
                data_store.set(store)
                return {}
    # Message_id wasn't found
    raise InputError("The given message_id either does not exist or is not in \
                                                    a channel the user is in")

# Adds a react to a message given a react_id
# Arguments:
#   token (str)         - token used to authorise the user
#   message_id (int)    - message id of messsage to add react
#   react_id (int)      - react_id of which react to add
# Exceptions:
#   AccessError - Occurs when the token is invalid
#   InputError  - Occurs when the message_id does not refer to a valid message 
#                 within the channel or dm the user has joined
#   InputError  - Occurs when react_id is not a valid react Id that exists yet
#   InputError  - Occurs when a message already has a react of react_id
#                 from the user
# Return value:
#   Returns {}
def message_react_v1(token, message_id, react_id):
    store = data_store.get()
    # Check valid token
    if not valid_token(token):
        raise AccessError("Invalid token")

    # Check valid react_id
    if react_id not in react_list:
        raise InputError("Invalid react_id")

    user_id = get_user_id(token)
    user_channels = store["users"][user_id - 1]["channels"]
    user_dms = store["users"][user_id - 1]["dms"]

    # Loops through the dms the user has joined
    for dm in store["dms"]:
        if dm["dm_id"] in user_dms:
            if add_react_in_dm(dm, message_id, user_id, react_id):
                react_notification(token, dm["dm_id"], False, message_id)
                data_store.set(store)
                return {}

    # Loops through the channels the user has joined
    for channel in store["channels"]:
        if channel["channel_id"] in user_channels:
           if add_react_in_channel(channel, message_id, user_id, react_id):
               react_notification(token, channel["channel_id"], True, message_id)
               data_store.set(store)
               return {}

    # Message_id wasn't found
    raise InputError("The given message_id either does not exist or is not in \
                                                    a channel the user is in")

# Removes a react to a message given a react_id
# Arguments:
#   token (str)         - token used to authorise the user
#   message_id (int)    - message id of messsage to add react
#   react_id (int)      - react_id of which react to add
# Exceptions:
#   AccessError - Occurs when the token is invalid
#   InputError  - Occurs when the message_id does not refer to a valid message 
#                 within the channel or dm the user has joined
#   InputError  - Occurs when react_id is not a valid react Id that exists yet
#   InputError  - Occurs when a message doesn't have a react of react_id
#                 from the user
# Return value:
#   Returns {}
def message_unreact_v1(token, message_id, react_id):
    store = data_store.get()
    # Check valid token
    if not valid_token(token):
        raise AccessError("Invalid token")

    # Check valid react_id
    if react_id not in react_list:
        raise InputError("Invalid react_id")

    user_id = get_user_id(token)
    user_channels = store["users"][user_id - 1]["channels"]
    user_dms = store["users"][user_id - 1]["dms"]

    # Loops through the dms the user has joined
    for dm in store["dms"]:
        if dm["dm_id"] in user_dms:
            if unreact_in_dm(dm, message_id, user_id, react_id):
                data_store.set(store)
                return {}

    # Loops through the channels the user has joined
    for channel in store["channels"]:
        if channel["channel_id"] in user_channels:
           if unreact_in_channel(channel, message_id, user_id, react_id):
               data_store.set(store)
               return {}

    # Message_id wasn't found
    raise InputError("The given message_id either does not exist or is not in \
                                                    a channel the user is in")
                                                    
# Pins a message given a message_id
# Arguments:
#   token (str)         - token used to authorise the user
#   message_id (int)    - message id of messsage to be pinned
# Exceptions:
#   AccessError - Occurs when the token is invalid
#   InputError  - Occurs when the message_id does not refer to a valid message 
#                 within the channel or dm the user has joined
#   InputError  - Occurs when the message is already pinned
#   AccessError - Occurs when the user does not have permissions
#                 to pin a message
# Return value:
#   Returns {}
def message_pin_v1(token, message_id):
    store = data_store.get()
    # Check valid token
    if not valid_token(token):
        raise AccessError("Invalid token")

    user_id = get_user_id(token)
    user_channels = store["users"][user_id - 1]["channels"]
    user_dms = store["users"][user_id - 1]["dms"]

    # Loops through the dms the user has joined
    for dm in store["dms"]:
        if dm["dm_id"] in user_dms:
            if pin_in_dm(dm, message_id, user_id):
                data_store.set(store)
                return {}

    # Loops through the channels the user has joined
    for channel in store["channels"]:
        if channel["channel_id"] in user_channels:
           if pin_in_channel(channel, message_id, user_id):
                data_store.set(store)
                return {}

    # Message_id wasn't found
    raise InputError("The given message_id either does not exist or is not in \
                                                    a channel the user is in")

# Unpins a message given a message_id
# Arguments:
#   token (str)         - token used to authorise the user
#   message_id (int)    - message id of messsage to be unpinned
# Exceptions:
#   AccessError - Occurs when the token is invalid
#   InputError  - Occurs when the message_id does not refer to a valid message 
#                 within the channel or dm the user has joined
#   InputError  - Occurs when the message has not been pinned
#   AccessError - Occurs when the user does not have permissions
#                 to unpin a message
# Return value:
#   Returns {}
def message_unpin_v1(token, message_id):
    store = data_store.get()
    # Check valid token
    if not valid_token(token):
        raise AccessError("Invalid token")

    user_id = get_user_id(token)
    user_channels = store["users"][user_id - 1]["channels"]
    user_dms = store["users"][user_id - 1]["dms"]

    # Loops through the dms the user has joined
    for dm in store["dms"]:
        if dm["dm_id"] in user_dms:
            if unpin_in_dm(dm, message_id, user_id):
                data_store.set(store)
                return {}

    # Loops through the channels the user has joined
    for channel in store["channels"]:
        if channel["channel_id"] in user_channels:
           if unpin_in_channel(channel, message_id, user_id):
                data_store.set(store)
                return {}

    # Message_id wasn't found
    raise InputError("The given message_id either does not exist or is not in \
                                                    a channel the user is in")

# Waits given time and then sends message to channel
def waitAndsend(token, channel_id, message_id, message, wait_time, store):
    time.sleep(wait_time)
    # Set up dict for message
    message_dict = generate_message_dict(message_id, token, message)

    # Looks for channel id in data_store and appends message to messages
    add_message_to_channel(store, channel_id, message_dict)
    
    tag_notification(token, channel_id, message, True)
    store["sendlaterIds"].remove(message_id)
    data_store.set(store)

# Waits given time and then sends message to dm
def waitAndsenddm(token, dm_id, message_id, message, wait_time, store):
    time.sleep(wait_time)
    # Set up dict for message
    message_dict = generate_message_dict(message_id, token, message)

    # Looks for channel id in data_store and appends message to messages
    add_message_to_dm(store, dm_id, message_dict)
    
    tag_notification(token, dm_id, message, False)
    store["sendlaterIds"].remove(message_id)
    data_store.set(store)

# Sends message at time given
# Arguments:
#   token (str)         - token used to authorise the user
#   channel_id (int)    - id of channel the message is being sent to
#   message (str)       - Message to be sent
#   time_sent (int)     - Unix time of when the message is to be sent
# Exceptions:
#   Input error - channel_id does not refer to a valid channel
#   Input error - length of message is over 1000 characters
#   Input error - time_sent is a time in the past
#   Access Error - Occurs when the token is invalid
#   Access Error - channel_id is valid and the authorised user is not a member 
#                  of the channel they are trying to post to
# Return value:
#   Returns {"message_id": message_id}
def message_sendlater_v1(token, channel_id, message, time_sent):
    store = data_store.get()

    # Check invalid token
    if not valid_token(token):
        raise AccessError("Invalid token")

    # Check input errors
    if message == "":
        raise InputError("Message is too short")

    if len(message) > 1000:
        raise InputError("Message is too long")

    if not valid_channel_id(channel_id, store):
        raise InputError("Channel with given channel_id does not exist")

    user_id = get_user_id(token)
    if not user_in_channel(channel_id, user_id, store):
        raise AccessError("User is not in channel of given channel id")
    
    # Checks time_sent is not in the past
    wait_time = time_sent - int(time.time())
    if wait_time <= 0:
        raise InputError
    
    # Set up dict for message
    message_id = generate_message_id(store)
    store["sendlaterIds"].append(message_id)
    
    threading.Thread(target = waitAndsend, args = (token, channel_id, \
        message_id, message, wait_time, store)).start()

    return {
        "message_id": message_id
    }

# Sends message at time given to dm
# Arguments:
#   token (str)         - token used to authorise the user
#   dm_id (int)         - id of dm the message is being sent to
#   message (str)       - Message to be sent
#   time_sent (int)     - Unix time of when the message is to be sent
# Exceptions:
#   Input error - channel_id does not refer to a valid channel
#   Input error - length of message is over 1000 characters
#   Input error - time_sent is a time in the past
#   Access Error - Occurs when the token is invalid
#   Access Error - channel_id is valid and the authorised user is not a member 
#                  of the channel they are trying to post to
# Return value:
#   Returns {"message_id": message_id}
def message_sendlaterdm_v1(token, dm_id, message, time_sent):
    store = data_store.get()

    # Check input errors
    if not valid_token(token):
        raise AccessError("Invalid token")
    
    if not valid_dm_id(dm_id, store):
        raise InputError("Invalid dm ID.")

    if not valid_message(message):
        raise InputError("The length of the message must be in between 1 and \
            1000, inclusively")

    if not user_in_dm(dm_id, token):
        raise AccessError("User is not a member of this dm.")
    
    # Checks time_sent is not in the past
    wait_time = time_sent - int(time.time())
    if wait_time <= 0:
        raise InputError
    
    # Set up dict for message
    message_id = generate_message_id(store)
    store["sendlaterIds"].append(message_id)

    threading.Thread(target = waitAndsenddm, args = (token, dm_id, \
        message_id, message, wait_time, store)).start()

    return {"message_id" : message_id}