import json

from iirosebot.globals import GlobalVal
from iirosebot.utools import hex2uid, uid2hex
from iirosebot.API.api_iirose import APIIirose
from iirosebot.API.api_load_config import load_config
from iirosebot.API.api_get_config import get_token
from iirosebot.utools.serve.array_message import array2text


API = APIIirose()
api_token = get_token()
onebot_v11_api_list = {}


def onebot_v11_api():
    def decorator(func):
        onebot_v11_api_list[func.__name__] = func

    return decorator


def message_id_h2i(message_id):
    if message_id is None:
        return None
    try:
        message_id = int(message_id)
    except ValueError:
        message_id = hex2uid(message_id)

    return int(message_id)


def return_data(data: json, status: str, retcode: int, status_code: int) -> json:
    return {
        "status": status,
        "retcode": retcode,
        "data": data
    }


@onebot_v11_api()
async def root(request):
    return return_data({}, 'ok', 0, 200)


@onebot_v11_api()
async def send_msg(request):
    if request.method == 'GET':
        message_type = request.query.get('message_type', None)
        user_id = hex2uid(request.query.get('user_id', None))
        group_id = hex2uid(request.query.get('group_id', None))
        message = request.query.get('message', None)
        auto_escape = request.query.get('auto_escape', False)

    elif request.method == 'POST':
        data = await request.json()
        message_type = data.get('message_type', None)
        user_id = hex2uid(data.get('user_id', None))
        group_id = hex2uid(data.get('group_id', None))
        message = data.get('message', None)
        auto_escape = data.get('auto_escape', False)

    else:
        return return_data({}, 'failed', 400, 200)

    if type(message) != str:
        message = await array2text(message)

    if message == "":
        return return_data({}, 'failed', 400, 200)

    if message is None:
        return return_data({}, 'failed', 400, 200)

    if message_type == "private":
        msg_id = await API.send_msg_to_private(message, user_id)
        return return_data({"message_id": msg_id}, 'ok', 0, 200)

    elif message_type == "group":
        msg_id = await API.send_msg_to_room(message, user_id)
        return return_data({"message_id": msg_id}, 'ok', 0, 200)

    else:
        if user_id is not None:
            msg_id = await API.send_msg_to_private(message, user_id)
            return return_data({"message_id": msg_id}, 'ok', 0, 200)

        elif group_id is not None:
            msg_id = await API.send_msg_to_room(message, user_id)
            return return_data({"message_id": msg_id}, 'ok', 0, 200)

    return return_data({}, 'failed', 400, 200)


@onebot_v11_api()
async def send_private_msg(request):
    if request.method == 'GET':
        user_id = hex2uid(request.query.get('user_id', None)) if request.query.get('user_id', None) is not None else None
        message = request.query.get('message', None)
        auto_escape = request.query.get('auto_escape', False)

    elif request.method == 'POST':
        data = await request.json()
        user_id = hex2uid(request.query.get('user_id', None)) if request.query.get('user_id', None) is not None else None
        message = data.get('message', None)
        auto_escape = data.get('auto_escape', False)

    else:
        return return_data({}, 'failed', 400, 200)

    if type(message) != str:
        message = await array2text(message)

    if message == "":
        return return_data({}, 'failed', 400, 200)

    if message is not None and user_id is not None:
        msg_id = await API.send_msg_to_private(message, user_id)
        return return_data({"message_id": msg_id}, 'ok', 0, 200)

    return return_data({}, 'failed', 400, 200)


@onebot_v11_api()
async def send_group_msg(request):
    if request.method == 'GET':
        group_id = hex2uid(request.query.get('group_id', None))
        message = request.query.get('message', None)
        auto_escape = request.query.get('auto_escape', False)

    elif request.method == 'POST':
        data = await request.json()
        group_id = hex2uid(data.get('group_id', None))
        message = data.get('message', None)
        auto_escape = data.get('auto_escape', False)

    else:
        return return_data({}, 'failed', 400, 200)

    if type(message) != str:
        message = await array2text(message)

    if message == "":
        return return_data({}, 'failed', 400, 200)

    if message is not None and group_id is not None:
        msg_id = await API.send_msg_to_room(message, group_id)
        return return_data({"message_id": msg_id}, 'ok', 0, 200)

    return return_data({}, 'failed', 400, 200)


@onebot_v11_api()
async def delete_msg(request):
    if request.method == 'GET':
        message_id = message_id_h2i(request.query.get('message_id', None))

    elif request.method == 'POST':
        data = await request.json()
        message_id = message_id_h2i(data.get('message_id', None))

    if message_id is None:
        return return_data({}, 'failed', 400, 200)

    if str(message_id) in GlobalVal.send_message_cache['private']:
        await API.revoke_message(str(message_id), GlobalVal.send_message_cache['private'][str(message_id)]['user_id'])
    else:
        await API.revoke_message(str(message_id))

    return return_data({}, 'ok', 0, 200)


@onebot_v11_api()
async def get_msg(request):
    if request.method == 'GET':
        user_id = hex2uid(message_id_h2i(request.query.get('user_id', None)))

    elif request.method == 'POST':
        data = await request.json()
        user_id = hex2uid(message_id_h2i(data.get('user_id', None)))

    if user_id is None:
        return return_data({}, 'failed', 400, 200)

    return return_data({}, 'ok', 0, 404)


@onebot_v11_api()
async def send_like(request):
    if request.method == 'GET':
        user_id = hex2uid(message_id_h2i(request.query.get('user_id', None)))

    elif request.method == 'POST':
        data = await request.json()
        user_id = hex2uid(message_id_h2i(data.get('user_id', None)))

    if user_id is None:
        return return_data({}, 'failed', 400, 200)

    await API.like(user_id)

    return return_data({}, 'ok', 0, 200)


@onebot_v11_api()
async def set_group_kick(request):
    if request.method == 'GET':
        user_id = hex2uid(message_id_h2i(request.query.get('user_id', None)))
        reject_add_request = request.query.get('reject_add_request', False)

    elif request.method == 'POST':
        data = await request.json()
        user_id = hex2uid(message_id_h2i(data.get('user_id', None)))
        reject_add_request = data.get('reject_add_request', False)

    if user_id is None:
        return return_data({}, 'failed', 400, 200)

    try:
        await API.send_kick(await API.get_user_info(user_id)['name'])
    except:
        pass

    return return_data({}, 'ok', 0, 200)


@onebot_v11_api()
async def set_group_ban(request):
    if request.method == 'GET':
        user_id = hex2uid(message_id_h2i(request.query.get('user_id', None)))
        duration = request.query.get('duration', 0)

    elif request.method == 'POST':
        data = await request.json()
        user_id = hex2uid(message_id_h2i(data.get('user_id', None)))
        duration = data.get('duration', 0)

    if user_id is None:
        return return_data({}, 'failed', 400, 200)

    try:
        await API.send_ban(await API.get_user_info(user_id)['name'], duration)
    except:
        pass

    return return_data({}, 'ok', 0, 200)


@onebot_v11_api()
async def set_group_anonymous_ban(request):
    return return_data({}, 'ok', 0, 200)


@onebot_v11_api()
async def set_group_whole_ban(request):
    if request.method == 'GET':
        enable = request.query.get('enable', False)

    elif request.method == 'POST':
        data = await request.json()
        enable = data.get('enable', False)

    await API.whole_ban(enable)

    return return_data({}, 'ok', 0, 200)


@onebot_v11_api()
async def set_group_admin(request):
    return return_data({}, 'ok', 0, 200)


@onebot_v11_api()
async def set_group_anonymous(request):
    if request.method == 'GET':
        enable = request.query.get('enable', False)

    elif request.method == 'POST':
        data = await request.json()
        enable = data.get('enable', False)

    if enable is None:
        return return_data({}, 'failed', 400, 200)

    await API.room_anonymous(enable)

    return return_data({}, 'ok', 0, 200)


@onebot_v11_api()
async def set_group_name(request):
    return return_data({}, 'ok', 0, 200)


@onebot_v11_api()
async def get_login_info(request):
    bot_name, _, _, bot_id = load_config()
    return return_data({'user_id': uid2hex(bot_id), 'nickname': bot_name}, 'ok', 0, 200)


@onebot_v11_api()
async def get_stranger_info(request):
    if request.method == 'GET':
        user_id = hex2uid(message_id_h2i(request.query.get('user_id', None)))

    elif request.method == 'POST':
        data = await request.json()
        user_id = hex2uid(message_id_h2i(data.get('user_id', None)))

    if user_id is None:
        return return_data({}, 'failed', 400, 200)
    try:
        data = await API.get_user_info(user_id)
        if data == {}:
            return return_data({}, 'failed', 400, 200)
    except:
        return return_data({}, 'failed', 400, 200)

    return return_data(
        {
            "user_id": uid2hex(data['id']),
            "nickname": data['name'],
            "sex": data['sex'],
            "age": 18
        },
        'ok', 0, 200)


@onebot_v11_api()
async def get_friend_list(request):
    if request.method == 'GET':
        user_id = hex2uid(message_id_h2i(request.query.get('user_id', None)))

    elif request.method == 'POST':
        data = await request.json()
        user_id = hex2uid(message_id_h2i(data.get('user_id', None)))

    if user_id is None:
        return return_data({}, 'failed', 400, 200)

    return return_data({}, 'ok', 0, 200)


@onebot_v11_api()
async def get_group_info(request):
    if request.method == 'GET':
        user_id = hex2uid(message_id_h2i(request.query.get('user_id', None)))

    elif request.method == 'POST':
        data = await request.json()
        user_id = hex2uid(message_id_h2i(data.get('user_id', None)))

    if user_id is None:
        return return_data({}, 'failed', 400, 200)

    return return_data({}, 'ok', 0, 200)


@onebot_v11_api()
async def get_group_list(request):
    if request.method == 'GET':
        user_id = hex2uid(message_id_h2i(request.query.get('user_id', None)))

    elif request.method == 'POST':
        data = await request.json()
        user_id = hex2uid(message_id_h2i(data.get('user_id', None)))

    if user_id is None:
        return return_data({}, 'failed', 400, 200)

    return return_data({}, 'ok', 0, 200)


@onebot_v11_api()
async def get_group_member_info(request):
    if request.method == 'GET':
        user_id = hex2uid(message_id_h2i(request.query.get('user_id', None)))

    elif request.method == 'POST':
        data = await request.json()
        user_id = hex2uid(message_id_h2i(data.get('user_id', None)))

    if user_id is None:
        return return_data({}, 'failed', 400, 200)

    try:
        data = await API.get_user_info(user_id)
        if data == {}:
            return return_data({}, 'failed', 400, 200)

    except:
        return return_data({}, 'failed', 400, 200)

    return return_data(
        {
            "group_id": uid2hex(data['room_id']),
            "user_id": uid2hex(data['id']),
            "nickname": data['name'],
            "card": data['name'],
            "sex": "unknown",
            "age": 18,
            "area": "",
            "join_time": 0,
            "last_sent_time": 0,
            "level": "",
            "role": "member",
            "unfriendly": False,
            "title": "",
            "title_expire_time": 0,
            "card_changeable": True,
        },
        'ok', 0, 200)


@onebot_v11_api()
async def get_group_member_list(request):
    if request.method == 'GET':
        user_id = hex2uid(message_id_h2i(request.query.get('user_id', None)))

    elif request.method == 'POST':
        data = await request.json()
        user_id = hex2uid(message_id_h2i(data.get('user_id', None)))

    if user_id is None:
        return return_data({}, 'failed', 400, 200)

    return return_data({}, 'ok', 0, 200)


@onebot_v11_api()
async def can_send(request):
    if request.method == 'GET':
        user_id = hex2uid(message_id_h2i(request.query.get('user_id', None)))

    elif request.method == 'POST':
        data = await request.json()
        user_id = hex2uid(message_id_h2i(data.get('user_id', None)))

    if user_id is None:
        return return_data({}, 'failed', 400, 200)

    return return_data({}, 'ok', 0, 200)


@onebot_v11_api()
async def get_status(request):
    return return_data({"online": True, "good": True}, 'ok', 0, 200)


@onebot_v11_api()
async def get_version_info(request):
    return return_data({"app_name": "iirose-iirosebot", "app_version": GlobalVal.iirosebot_version[1:], "protocol_version": "v11"}, 'ok', 0, 200)


@onebot_v11_api()
async def set_restart(request):
    return return_data({}, 'ok', 0, 200)


@onebot_v11_api()
async def clean_cache(request):
    GlobalVal.message_cache = {"private": {}, "group": {}}
    GlobalVal.send_message_cache = {"private": {}, "group": {}}
    return return_data({}, 'ok', 0, 200)
