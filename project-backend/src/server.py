import sys
import signal
import json
from json import dumps
from flask import Flask, request, send_from_directory
from flask_cors import CORS
from src import config
from src.auth import auth_register_v2, auth_login_v2, auth_logout_v1,\
    auth_passwordreset_reset_v1, auth_passwordreset_request_v1
from src.channels import channels_create_v2, channels_list_v2, \
    channels_listall_v2
from src.channel import channel_invite_v2, channel_messages_v2, \
    channel_join_v2, channel_details_v2, channel_addowner_v1, \
        channel_leave_v1, channel_removeowner_v1
from src.message import message_send_v1, message_edit_v1, message_remove_v1, \
    message_senddm_v1, message_pin_v1, message_unpin_v1, \
    message_react_v1, message_unreact_v1, message_sendlater_v1, message_sendlaterdm_v1
from src.dm import dm_create_v1, dm_details_v1, dm_leave_v1, dm_list_v1, \
    dm_messages_v1, dm_remove_v1
from src.users import users_all_v1, users_stats_v1
from src.user import user_profile_v1, user_profile_setname_v1, \
    user_profile_setemail_v1, user_profile_sethandle_v1, user_stats_v1, \
    user_profile_uploadphoto_v1
from src.admin import admin_user_remove_v1, admin_permission_change_v1
from src.standup import standup_start_v1, standup_send_v1, standup_active_v1
from src.search import search_v1
from src.other import clear_v1
from src.data_store import data_store
from src.notifications import notifications_get_v1
from src.share import message_share_v1

def quit_gracefully(*args):
    '''For coverage'''
    exit(0)

def defaultHandler(err):
    response = err.get_response()
    print('response', err, err.get_response())
    response.data = dumps({
        "code": err.code,
        "name": "System Error",
        "message": err.get_description(),
    })
    response.content_type = 'application/json'
    return response

APP = Flask(__name__)
CORS(APP)

APP.config['TRAP_HTTP_EXCEPTIONS'] = True
APP.register_error_handler(Exception, defaultHandler)

#### NO NEED TO MODIFY ABOVE THIS POINT, EXCEPT IMPORTS

# Function to save data to 'database.json'
@APP.route("/auth/register/v2", methods = ['POST'])
def auth_register():
    data = request.get_json()
    response = auth_register_v2(data['email'], data['password'], 
    data['name_first'], data['name_last'])
    return dumps(response)

@APP.route("/auth/login/v2", methods = ['POST'])
def auth_login():
    data = request.get_json()
    response = auth_login_v2(data['email'], data['password'])
    return dumps(response)

@APP.route("/auth/logout/v1", methods = ['POST'])
def auth_logout():
    data = request.get_json()
    response = auth_logout_v1(data['token'])
    return dumps(response)

@APP.route("/channel/details/v2", methods = ['GET'])
def channel_detail():
    data = request.args
    response = channel_details_v2(data['token'], int(data['channel_id']))
    return dumps(response)

@APP.route("/channel/messages/v2", methods = ['GET'])
def channel_messages():
    data = request.args
    response = channel_messages_v2(data['token'], int(data['channel_id']), 
    int(data['start']))
    return dumps(response)

@APP.route("/channel/join/v2", methods = ['POST'])
def channel_join():
    data = request.get_json()
    response = channel_join_v2(data['token'], data['channel_id'])
    return dumps(response)

@APP.route("/channel/invite/v2", methods = ['POST'])
def channel_invite():
    data = request.get_json()
    response = channel_invite_v2(data['token'], data['channel_id'], 
    data['u_id'])
    return dumps(response)

@APP.route("/channel/leave/v1", methods = ['POST'])
def channel_leave():
    data = request.get_json()
    response = channel_leave_v1(data['token'], data['channel_id'])
    return dumps(response)

@APP.route("/channel/addowner/v1", methods = ['POST'])
def channel_addowner():
    data = request.get_json()
    response = channel_addowner_v1(data['token'], data['channel_id'], 
    data['u_id'])
    return dumps(response)

@APP.route("/channel/removeowner/v1", methods = ['POST'])
def channel_removeowner():
    data = request.get_json()
    response = channel_removeowner_v1(data['token'], data['channel_id'], 
    data['u_id'])
    return dumps(response)

@APP.route("/channels/create/v2", methods = ['POST'])
def channels_create():
    data = request.get_json()
    response = channels_create_v2(data['token'], data['name'], 
    data['is_public'])
    return dumps(response)

@APP.route("/message/edit/v1", methods = ['PUT'])
def message_edit():
    data = request.get_json()
    response = message_edit_v1(data['token'], data['message_id'], 
    data['message'])
    return dumps(response)

@APP.route("/message/remove/v1", methods = ['DELETE'])
def message_remove():
    data = request.get_json()
    response = message_remove_v1(data['token'], data['message_id'])
    return dumps(response)

@APP.route("/message/senddm/v1", methods = ['POST'])
def message_senddm():
    data = request.get_json()
    response = message_senddm_v1(data['token'], data['dm_id'], data['message'])
    return dumps(response)

@APP.route("/message/react/v1", methods = ['POST'])
def message_react():
    data = request.get_json()
    response = message_react_v1(data['token'], data['message_id'], data['react_id'])
    return dumps(response)

@APP.route("/message/unreact/v1", methods = ['POST'])
def message_unreact():
    data = request.get_json()
    response = message_unreact_v1(data['token'], data['message_id'], data['react_id'])
    return dumps(response)

@APP.route("/message/pin/v1", methods = ['POST'])
def message_pin():
    data = request.get_json()
    response = message_pin_v1(data['token'], data['message_id'])
    return dumps(response)

@APP.route("/message/unpin/v1", methods = ['POST'])
def message_unpin():
    data = request.get_json()
    response = message_unpin_v1(data['token'], data['message_id'])
    return dumps(response)

@APP.route("/user/profile/setname/v1", methods = ['PUT'])
def user_profile_setname():
    data = request.get_json()
    response = user_profile_setname_v1(data['token'], data['name_first'], 
    data['name_last'])
    return dumps(response)

@APP.route("/user/profile/setemail/v1", methods = ['PUT'])
def user_profile_setemail():
    data = request.get_json()
    response = user_profile_setemail_v1(data['token'], data['email'])
    return dumps(response)

@APP.route("/user/profile/sethandle/v1", methods = ['PUT'])
def user_profile_sethandle():
    data = request.get_json()
    response = user_profile_sethandle_v1(data['token'], data['handle_str'])
    return dumps(response)

@APP.route("/admin/userpermission/change/v1", methods = ['POST'])
def admin_userpermission_change():
    data = request.get_json()
    response = admin_permission_change_v1(data['token'], data['u_id'], 
    data['permission_id'])
    return dumps(response)

@APP.route("/admin/user/remove/v1", methods = ['DELETE'])
def admin_user_remove():
    data = request.get_json()
    response = admin_user_remove_v1(data['token'], data['u_id'])
    return dumps(response)

@APP.route("/users/all/v1", methods = ['GET'])
def users_all():
    data = request.args
    response = users_all_v1(data['token'])
    return dumps(response)

@APP.route("/message/send/v1", methods = ['POST'])
def message_send():
    data = request.get_json()
    response = message_send_v1(data['token'], data['channel_id'], 
    data['message'])
    return dumps(response)

@APP.route("/user/profile/v1", methods = ['GET'])
def user_profile():
    data = request.args
    response = user_profile_v1(data['token'], int(data['u_id']))
    return dumps(response)

@APP.route("/user/profile/uploadphoto/v1", methods = ['POST'])
def user_profile_uploadphoto():
    data = request.get_json()
    response = user_profile_uploadphoto_v1(data['token'],
    data['img_url'], int(data['x_start']), int(data['y_start']),
    int(data['x_end']), int(data['y_end']))
    return dumps(response)

@APP.route("/dm/create/v1", methods = ['POST'])
def dm_create():
    data = request.get_json()
    response = dm_create_v1(data['token'], data['u_ids'])
    return dumps(response)

@APP.route("/dm/list/v1", methods = ['GET'])
def dm_list():
    data = request.args
    response = dm_list_v1(data['token'])
    return dumps(response)

@APP.route("/dm/remove/v1", methods = ['DELETE'])
def dm_remove():
    data = request.get_json()
    response = dm_remove_v1(data['token'], data['dm_id'])
    return dumps(response)

@APP.route("/dm/details/v1", methods = ['GET'])
def dm_details():
    data = request.args
    response = dm_details_v1(data['token'], int(data['dm_id']))
    return dumps(response)

@APP.route("/dm/leave/v1", methods = ['POST'])
def dm_leave():
    data = request.get_json()
    response = dm_leave_v1(data['token'], data['dm_id'])
    return dumps(response)

@APP.route("/dm/messages/v1", methods = ['GET'])
def dm_messages():
    data = request.args
    response = dm_messages_v1(data['token'], int(data['dm_id']), 
    int(data['start']))
    return dumps(response)

@APP.route("/channels/listall/v2", methods = ['GET'])
def channels_listall():
    data = request.args
    response = channels_listall_v2(data['token'])
    return dumps(response)

@APP.route("/channels/list/v2", methods = ['GET'])
def channels_list():
    data = request.args
    response = channels_list_v2(data['token'])
    return dumps(response)

@APP.route("/standup/start/v1", methods = ['POST'])
def standup_start():
    data = request.get_json()
    response = standup_start_v1(data['token'], data['channel_id'], 
    data['length'])
    return dumps(response)

@APP.route("/standup/send/v1", methods = ['POST'])
def standup_send():
    data = request.get_json()
    response = standup_send_v1(data['token'], data['channel_id'], 
    data['message'])
    return dumps(response)

@APP.route("/standup/active/v1", methods = ['GET'])
def standup_active():
    data = request.args
    response = standup_active_v1(data['token'], int(data['channel_id']))
    return dumps(response)

@APP.route("/search/v1", methods = ['GET'])
def search():
    data = request.args
    response = search_v1(data['token'], data['query_str'])
    return dumps(response)

@APP.route("/clear/v1", methods = ['DELETE'])
def clear():
    clear_v1()
    return {}

@APP.route("/user/stats/v1", methods = ['GET'])
def user_stats():
    data = request.args
    response = user_stats_v1(data['token'])
    return dumps(response)

@APP.route("/users/stats/v1", methods = ['GET'])
def users_stats():
    data = request.args
    response = users_stats_v1(data['token'])
    return dumps(response)

@APP.route("/notifications/get/v1", methods = ['GET'])
def notifications_get():
    data = request.args
    response = notifications_get_v1(data['token'])
    return dumps(response)

@APP.route("/message/share/v1", methods = ['POST'])
def message_share():
    data = request.get_json()
    response = message_share_v1(data["token"], data["og_message_id"], data["message"], data["channel_id"], data["dm_id"])
    return response

@APP.route("/message/sendlater/v1", methods = ['POST'])
def message_sendlater():
    data = request.get_json()
    response = message_sendlater_v1(data['token'], data['channel_id'], 
    data['message'], data["time_sent"])
    return dumps(response)

@APP.route("/message/sendlaterdm/v1", methods = ['POST'])
def message_sendlaterdm():
    data = request.get_json()
    response = message_sendlaterdm_v1(data['token'], data['dm_id'], 
    data['message'], data["time_sent"])
    return dumps(response)
    
@APP.route("/static/<path:path>")
def serve_image(path):
	return send_from_directory('/static/', path)

@APP.route("/auth/passwordreset/request/v1", methods = ['POST'])
def auth_passwordreset_request():
    data = request.get_json()
    response = auth_passwordreset_request_v1(data['email'])
    return dumps(response)

@APP.route("/auth/passwordreset/reset/v1", methods = ['POST'])
def auth_passwordreset_reset():
    data = request.get_json()
    response = auth_passwordreset_reset_v1(data['reset_code'], data['new_password'])
    return dumps(response)

#### NO NEED TO MODIFY BELOW THIS POINT

if __name__ == "__main__":
    signal.signal(signal.SIGINT, quit_gracefully) # For coverage
    APP.run(port=config.port) # Do not edit this port
