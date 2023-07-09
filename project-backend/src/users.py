from src.helper import valid_token
from src.data_store import data_store
from src.error import AccessError

# Returns the details of all users
# Arguments:
#   token (str) - token used to authorise the user
# Exceptions:
#   AccessError - Occurs when the token is invalid
#   
# Return value:
#   Returns [{
#       'u_id': auth_user_id,
#       'email': email,
#       'name_first': name_first,
#       'name_last': name_last,
#       'handle_str': handle_str,
#       'profile_img_url': profile_img_url
#     },
#     {
#       'u_id': auth_user_id,
#       'email': email,
#       'name_first': name_first,
#       'name_last': name_last,
#       'handle_str': handle_str,
#       'profile_img_url': profile_img_url
#     }
#   when no errors are raised
def users_all_v1(token):
    store = data_store.get()
    user = []

    if not valid_token(token):
        raise AccessError("Invalid Token")

    for users in store['users']:
        if not users['is_removed']:
            user.append({
                'u_id': users['user_id'],
                'email': users['email'],
                'name_first': users['name_first'],
                'name_last': users['name_last'],
                'handle_str': users['handle_str'],
                'profile_img_url': users['profile_img_url']
            })
    return {
        'users': user
    }

# Fetches the required statistics about the use of UNSW Streams.
# Arguments:
#     token (str) - auth token of the user
# Exceptions:
#     AccessError - Occurs if the token is invalid
# Return Value:
#     Returns a dictionary shape
#     {
#      channels_exist: [{num_channels_exist, time_stamp}], 
#      dms_exist: [{num_dms_exist, time_stamp}], 
#      messages_exist: [{num_messages_exist, time_stamp}], 
#      utilization_rate 
#     }
def users_stats_v1(token):
    if not valid_token(token):
        raise AccessError("Invalid Token")
    
    store = data_store.get()

    return {'workspace_stats': store['workspace_stats']}
