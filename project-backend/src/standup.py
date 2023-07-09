# Importing from other files.
from src.error import InputError
from src.error import AccessError
from src.data_store import data_store
from src.helper import get_user_id, valid_token, user_in_channel, \
    valid_channel_id
from src.message import generate_message_dict, generate_message_id, \
    add_message_to_channel
import time
import threading

# This function handles basic exceptions for standup functions
def standup_exception_handling(token, channel_id, store):
    if not valid_token(token):
        raise AccessError('Invalid token')
    
    if not valid_channel_id(channel_id, store):
        raise InputError('channel_id does not refer to a valid channel')

    if not user_in_channel(channel_id, get_user_id(token), store):
        raise AccessError('channel_id is valid and the authorised user is not \
        a member of the channel')

# This function gathers all messages and sends it into the channel as a single
# message in the following format:
'''
[message_sender1_handle]: [message1]
[message_sender2_handle]: [message2]
[message_sender3_handle]: [message3]
[message_sender4_handle]: [message4]
'''
def send_message(standup, store, token, channel_id):
    standup_messages = ""
    for message in standup['messages']:
        standup_messages += \
            f"{str(message['handle_str'])}: {str(message['message'])}"
        if message != standup['messages'][-1]:
            standup_messages += '\n'

    message_id = generate_message_id(store)
    message_dict = generate_message_dict(message_id, token, standup_messages)
    add_message_to_channel(store, channel_id, message_dict)

# This function makes the standup inactive
def set_standup_to_inactive(standup):
    standup['started_by'] = None
    standup['messages'] = []
    standup['time_finish'] = None

# This function ends the standup by collating all messages in the bank and
# adding it to the channel messages as one singular message and resetting all
# values in the standup dictionary
def end_standup(length, standup, store, token, channel_id):
    time.sleep(length)
    send_message(standup, store, token, channel_id)
    set_standup_to_inactive(standup)
    data_store.set(store)

# This function enables a user to initiate a standup in a channel
# Arguments:
#   token (str) - The token of the user initiating the standup
#   channel_id (int) - The id of the channel where the standup is occurring
#   length (int) - The length of the standup in seconds

# Exceptions:
#   InputError  - Occurs when channel_id is invalid
#   InputError  - Occurs when length is a negative integer
#   InputError  - Occurs when there is an active standup running in the channel
#   AccessError - Occurs when the user associated with the token is not a 
#                 member of the channel
#   AccessError - Occurs when the token is invalid

# Return Value:
#   Returns {time_finish} if no exceptions occur during runtime
def standup_start_v1(token, channel_id, length):
    time_start = time.time()
    time_finish = int(time_start + length)
    store = data_store.get()
    standup_exception_handling(token, channel_id, store)

    if length < 0:
        raise InputError('length is a negative integer')

    user_id = get_user_id(token)
    standup = store['channels'][channel_id - 1]['standup']

    if standup['started_by'] != None:
        raise InputError('an active standup is currently running in the \
            channel')

    standup['time_finish'] = time_finish
    standup['started_by'] = user_id
    threading.Thread(target = end_standup, args = (length, standup, store, \
        token, channel_id)).start()
    
    return {
        'time_finish': time_finish
    }

# This function enables a user to send a message in a standup
# Arguments:
#   token (str) - The token of the user initiating the standup
#   channel_id (int) - The id of the channel where the standup is occurring
#   message (str) - The message being sent

# Exceptions:
#   InputError  - Occurs when channel_id is invalid
#   InputError  - Occurs when the length of the message is over 1000 characters
#   InputError  - Occurs when there is no active standup running in the channel
#   AccessError - Occurs when the user associated with the token is not a 
#                 member of the channel
#   AccessError - Occurs when the token is invalid

# Return Value:
#   Returns {} if no exceptions occur during runtime
def standup_send_v1(token, channel_id, message):
    store = data_store.get()
    standup_exception_handling(token, channel_id, store)

    if len(message) > 1000:
        raise InputError('length of message is over 1000 characters')

    user_id = get_user_id(token)
    standup = store['channels'][channel_id - 1]['standup']

    if standup['started_by'] == None:
        raise InputError('an active standup is not currently running in the \
            channel')

    # Adding message to messages bank for current standup
    standup['messages'].append({
        'message': message,
        'handle_str': store['users'][user_id - 1]['handle_str']
    })
    data_store.set(store)
    
    return {}

# This function enables a user to check whether there is an active standup in
# the channel
# Arguments:
#   token (str) - The token of the user initiating the standup
#   channel_id (int) - The id of the channel where the standup is occurring

# Exceptions:
#   InputError  - Occurs when channel_id is invalid
#   AccessError - Occurs when the user associated with the token is not a 
#                 member of the channel
#   AccessError - Occurs when the token is invalid

# Return Value:
#   Returns {is_active, time_finish} if no exceptions occur during runtime
def standup_active_v1(token, channel_id):
    store = data_store.get()
    standup_exception_handling(token, channel_id, store)
    
    standup = store['channels'][channel_id - 1]['standup']
    is_active = False
    time_finish = None

    # If there is an active standup, update 'is_active' and 'time_finish'
    if standup['started_by'] != None:
        is_active = True
        time_finish = standup['time_finish']
    
    return {
        'is_active': is_active,
        'time_finish': time_finish
    }
        
    

    

    



    
    






