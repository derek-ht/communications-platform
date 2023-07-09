from src.error import InputError
from src.error import AccessError
from src.data_store import data_store
from src.helper import get_user_id, valid_token

# Return whether query_str is between 1 and 1000 characters inclusively.
def valid_query_string(query_str):
    if len(query_str) in range(1,1001):
        return True
    return False

# Search for through either channel or dm and append all messages with
# the query string into the search_messages list.
def search_v1_query_finder(search_messages, group, query_str, user_id):
    store = data_store.get()
    for groups in store[group]:
        if user_id in groups['all_members']:
            for message in groups['messages']:
                if query_str in message['message']:
                    search_messages['messages'].append(message)
    return search_messages

# Returns the details of all users
# Arguments:
#   token (str) - token used to authorise the user
#   query_str (str) - a the string a user searches for in messages
# Exceptions:
#   AccessError - Occurs when the token is invalid
#   InputError - Occurs when the query_str is not between 1 to 1000 
#                characters
#   
# Return value:
#   Returns {
#       'messages': [
#           {
#               'message_id': message_id,
#               'u_id': auth_user_id,
#               'message': <message>,
#               'time_created': time_created,
#           },
#           {
#               'message_id': message_id,
#               'u_id': auth_user_id,
#               'message': <message>,
#               'time_created': time_created,
#           }
#       ],
#   }
#   when no errors are raised
def search_v1(token, query_str):
    if not valid_token(token):
        raise AccessError('Invalid token')
    
    if not valid_query_string(query_str):
        raise InputError("The length of the message must be in between 1 and \
            1000 characters, inclusively")

    user_id = get_user_id(token)
    search_messages = {'messages': []}

    search_messages = search_v1_query_finder(search_messages, 'channels', 
        query_str, user_id)
    search_messages = search_v1_query_finder(search_messages, 'dms', 
        query_str, user_id)

    return search_messages