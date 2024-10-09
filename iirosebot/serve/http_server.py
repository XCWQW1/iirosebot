import json
import asyncio
import traceback

from aiohttp import web
from loguru import logger

from iirosebot.globals import GlobalVal
from iirosebot.utools import hex2uid, uid2hex, message_id_h2i
from iirosebot.API.api_iirose import APIIirose
from iirosebot.API.api_load_config import load_config
from iirosebot.API.api_get_config import get_token, get_onebot_v11_serve
from iirosebot.utools.serve.array_message import array2text


routes = web.RouteTableDef()
API = APIIirose()
api_token = get_token()
onebot_v11_url = '/onebot/v11'
onebot_v11_api_list = {}


def onebot_v11_api():
    def decorator(func):
        onebot_v11_api_list[func.__name__] = func

    return decorator


def return_data(data: json, status: str, retcode: int, status_code: int) -> json:
    return web.json_response({
        "status": status,
        "retcode": retcode,
        "data": data
    }, status=status_code)


@onebot_v11_api()
@routes.route('*', f"{onebot_v11_url}/http")
@routes.route('*', onebot_v11_url)
async def root(request):
    return return_data({}, 'ok', 0, 200)


@onebot_v11_api()
@routes.route('*', f"{onebot_v11_url}/http/send_msg")
@routes.route('*', f'{onebot_v11_url}/send_msg')
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
        return web.json_response({"code": 405, 'error': "Method Not Allowed"}, status=405)

    if type(message) != str:
        message, reply_id, private_id, Message = await array2text(message)

    if message == "":
        return return_data({}, 'failed', 400, 200)

    if message is None:
        return return_data({}, 'failed', 400, 200)

    if reply_id is not None:
        msg_id = await API.replay_msg(Message, message, private_id=private_id)
        return return_data({"message_id": msg_id}, 'ok', 0, 200)

    if message_type == "private":
        msg_id = await API.send_msg_to_private(message, user_id)
        return return_data({"message_id": msg_id}, 'ok', 0, 200)

    elif message_type == "group":
        msg_id = await API.send_msg_to_room(message)
        return return_data({"message_id": msg_id}, 'ok', 0, 200)

    else:
        if user_id is not None:
            msg_id = await API.send_msg_to_private(message, user_id)
            return return_data({"message_id": msg_id}, 'ok', 0, 200)

        elif group_id is not None:
            msg_id = await API.send_msg_to_room(message)
            return return_data({"message_id": msg_id}, 'ok', 0, 200)

    return return_data({}, 'failed', 400, 200)


@onebot_v11_api()
@routes.route('*', f"{onebot_v11_url}/http/send_private_msg")
@routes.route('*', f'{onebot_v11_url}/send_private_msg')
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
        message, reply_id, private_id, Message = await array2text(message)

    if message == "":
        return return_data({}, 'failed', 400, 200)

    if message is not None and user_id is not None:
        if reply_id is not None:
            msg_id = await API.replay_msg(Message, message, private_id=private_id)
            return return_data({"message_id": msg_id}, 'ok', 0, 200)

        msg_id = await API.send_msg_to_private(message, user_id)
        return return_data({"message_id": msg_id}, 'ok', 0, 200)

    return return_data({}, 'failed', 400, 200)


@onebot_v11_api()
@routes.route('*', f"{onebot_v11_url}/http/send_group_msg")
@routes.route('*', f'{onebot_v11_url}/send_group_msg')
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
        message, reply_id, private_id, Message = await array2text(message)

    if message == "":
        return return_data({}, 'failed', 400, 200)

    if message is not None:
        if reply_id is not None:
            msg_id = await API.replay_msg(Message, message, private_id=private_id)
            return return_data({"message_id": msg_id}, 'ok', 0, 200)

        msg_id = await API.send_msg_to_room(message)
        return return_data({"message_id": msg_id}, 'ok', 0, 200)

    return return_data({}, 'failed', 400, 200)


@onebot_v11_api()
@routes.route('*', f"{onebot_v11_url}/http/delete_msg")
@routes.route('*', f'{onebot_v11_url}/delete_msg')
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
@routes.route('*', f"{onebot_v11_url}/http/get_msg")
@routes.route('*', f'{onebot_v11_url}/get_msg')
async def get_msg(request):
    if request.method == 'GET':
        message_id = message_id_h2i(request.query.get('message_id', None))

    elif request.method == 'POST':
        data = await request.json()
        message_id = message_id_h2i(data.get('message_id', None))

    if message_id is None:
        return return_data({}, 'failed', 400, 200)

    message_id = str(message_id)
    if message_id in GlobalVal.send_message_cache['private']:
        message_info = GlobalVal.send_message_cache['private'][message_id]
        message_info['type'] = 'private'
    elif message_id in GlobalVal.send_message_cache['group']:
        message_info = GlobalVal.send_message_cache['group'][message_id]
        message_info['type'] = 'group'
    elif message_id in GlobalVal.message_cache['private']:
        message_info = GlobalVal.message_cache['private'][message_id]
        message_info['type'] = 'private'
    elif message_id in GlobalVal.message_cache['group']:
        message_info = GlobalVal.message_cache['group'][message_id]
        message_info['type'] = 'group'

    if message_info is None:
        return return_data({}, 'failed', 400, 200)

    return return_data({
        "time": int(message_info['timestamp']),
        "message_type": message_info['type'],
        "message_id": message_info['message_id'],
        "real_id": message_info['message_id'],
        "sender": {
            "user_id": uid2hex(message_info['user_id']),
            "nickname": GlobalVal.iirose_date['user'][message_info['user_id']]['name'],
            "sex": "unknown",
            "age": "18",
        },
        "message": message_info['message']
    }, 'ok', 0, 404)


@onebot_v11_api()
@routes.route('*', f"{onebot_v11_url}/http/send_like")
@routes.route('*', f'{onebot_v11_url}/send_like')
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
@routes.route('*', f"{onebot_v11_url}/http/set_group_kick")
@routes.route('*', f'{onebot_v11_url}/set_group_kick')
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
@routes.route('*', f"{onebot_v11_url}/http/set_group_ban")
@routes.route('*', f'{onebot_v11_url}/set_group_ban')
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
@routes.route('*', f"{onebot_v11_url}/http/set_group_anonymous_ban")
@routes.route('*', f'{onebot_v11_url}/set_group_anonymous_ban')
async def set_group_anonymous_ban(request):
    return return_data({}, 'ok', 0, 200)


@onebot_v11_api()
@routes.route('*', f"{onebot_v11_url}/http/set_group_whole_ban")
@routes.route('*', f'{onebot_v11_url}/set_group_whole_ban')
async def set_group_whole_ban(request):
    if request.method == 'GET':
        enable = request.query.get('enable', False)

    elif request.method == 'POST':
        data = await request.json()
        enable = data.get('enable', False)

    await API.whole_ban(enable)

    return return_data({}, 'ok', 0, 200)


@onebot_v11_api()
@routes.route('*', f"{onebot_v11_url}/http/set_group_admin")
@routes.route('*', f'{onebot_v11_url}/set_group_admin')
async def set_group_admin(request):
    return return_data({}, 'ok', 0, 200)


@onebot_v11_api()
@routes.route('*', f"{onebot_v11_url}/http/set_group_anonymous")
@routes.route('*', f'{onebot_v11_url}/set_group_anonymous')
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
@routes.route('*', f"{onebot_v11_url}/http/set_group_name")
@routes.route('*', f'{onebot_v11_url}/set_group_name')
async def set_group_name(request):
    return return_data({}, 'ok', 0, 200)


@onebot_v11_api()
@routes.route('*', f"{onebot_v11_url}/http/get_login_info")
@routes.route('*', f'{onebot_v11_url}/get_login_info')
async def get_login_info(request):
    bot_name, _, _ = load_config()
    return return_data({'user_id': uid2hex(GlobalVal.iirose_date['user_name'][bot_name]['id']), 'nickname': bot_name}, 'ok', 0, 200)


@onebot_v11_api()
@routes.route('*', f"{onebot_v11_url}/http/get_stranger_info")
@routes.route('*', f'{onebot_v11_url}/get_stranger_info')
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
@routes.route('*', f"{onebot_v11_url}/http/get_friend_list")
@routes.route('*', f'{onebot_v11_url}/get_friend_list')
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
@routes.route('*', f"{onebot_v11_url}/http/get_group_info")
@routes.route('*', f'{onebot_v11_url}/get_group_info')
async def get_group_info(request):
    if request.method == 'GET':
        group_id = hex2uid(message_id_h2i(request.query.get('group_id', None)))

    elif request.method == 'POST':
        data = await request.json()
        group_id = hex2uid(message_id_h2i(data.get('group_id', None)))

    if group_id is None:
        return return_data({}, 'failed', 400, 200)
    room_info = GlobalVal.iirose_date['room'][group_id]
    return return_data({
        "group_id": uid2hex(group_id),
        "group_name": room_info['name'],
        "member_count": 0,
        "max_member_count": 0
    }, 'ok', 0, 200)


@onebot_v11_api()
@routes.route('*', f"{onebot_v11_url}/http/get_group_list")
@routes.route('*', f'{onebot_v11_url}/get_group_list')
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
@routes.route('*', f"{onebot_v11_url}/http/get_group_member_info")
@routes.route('*', f'{onebot_v11_url}/get_group_member_info')
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
@routes.route('*', f"{onebot_v11_url}/http/get_group_member_list")
@routes.route('*', f'{onebot_v11_url}/get_group_member_list')
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
@routes.route('*', f"{onebot_v11_url}/http/can_send_image")
@routes.route('*', f'{onebot_v11_url}/can_send_image')
@routes.route('*', f"{onebot_v11_url}/http/can_send_record")
@routes.route('*', f'{onebot_v11_url}/can_send_record')
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
@routes.route('*', f"{onebot_v11_url}/http/get_status")
@routes.route('*', f'{onebot_v11_url}/get_status')
async def get_status(request):
    return return_data({"online": True, "good": True}, 'ok', 0, 200)


@onebot_v11_api()
@routes.route('*', f"{onebot_v11_url}/http/get_version_info")
@routes.route('*', f'{onebot_v11_url}/get_version_info')
async def get_version_info(request):
    return return_data({"app_name": "iirose-iirosebot", "app_version": GlobalVal.iirosebot_version[1:], "protocol_version": "v11"}, 'ok', 0, 200)


@onebot_v11_api()
@routes.route('*', f"{onebot_v11_url}/http/set_restart")
@routes.route('*', f'{onebot_v11_url}/set_restart')
async def set_restart(request):
    return return_data({}, 'ok', 0, 200)


@onebot_v11_api()
@routes.route('*', f"{onebot_v11_url}/http/clean_cache")
@routes.route('*', f'{onebot_v11_url}/clean_cache')
async def clean_cache(request):
    GlobalVal.message_cache = {"private": {}, "group": {}}
    GlobalVal.send_message_cache = {"private": {}, "group": {}}
    return return_data({}, 'ok', 0, 200)


# 鉴权
@web.middleware
async def verify_token(request, handler):
    logger.info(f"[HTTP API] {request.remote} {request.method} {request.path}")
    if request.method == "POST":
        logger.debug(f"[HTTP API] {request.method} 请求 {request.path} 请求头 {dict(request.headers.items())} 内容 {await request.json()}")
    elif request.method == "GET":
        logger.debug(f"[HTTP API] {request.method} 请求 {request.path} 请求头 {dict(request.headers.items())} 内容 {dict(request.query.items())}")

    if not get_onebot_v11_serve()['http_api']['verify']:
        return await handler(request)

    auth_header = request.query.get('access_token', None)
    if auth_header is not None:
        if auth_header != api_token:
            return web.json_response({'code': 403, 'error': 'access token 不符合'}, status=403)
        return await handler(request)

    auth_header = request.headers.get('Authorization')
    token = auth_header.split(' ')

    if not auth_header or len(token) != 2:
        return web.json_response({'code': 401, 'error': 'access token 未提供'}, status=401)

    if token[1].strip() != api_token:
        return web.json_response({'code': 403, 'error': 'access token 不符合'}, status=403)

    return await handler(request)


app = web.Application(middlewares=[verify_token])
app.add_routes(routes)
runner = web.AppRunner(app)


async def start_http_api(host: str, port: int) -> None:
    close_event = asyncio.Event()

    try:
        await runner.setup()
        site = web.TCPSite(runner, host, port)
        await site.start()
        logger.info('[HTTP API] 监听 http://{}:{} 中'.format(host, port))
    except:
        logger.error('[HTTP API] 启动时出错: {}'.format(traceback.format_exc()))
        return

    async def close_http_api():
        await runner.cleanup()
        logger.info('[HTTP API] 已释放监听')

    async def wait_for_close():
        await close_event.wait()
        await close_http_api()

    task = asyncio.create_task(wait_for_close())

    try:
        while not GlobalVal.close_status:
            await asyncio.sleep(1)

    except:
        await close_http_api()
