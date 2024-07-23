import asyncio
import json
import time
import traceback

import aiohttp

from aiohttp import web
from loguru import logger

from iirosebot.API.api_get_config import get_serve, get_token, get_bot_id
from iirosebot.globals import GlobalVal
from iirosebot.utools import uid2hex
from iirosebot.utools.serve.array_message import text2array

onebot_v11_url = '/onebot/v11'
event_ws_client = []
api_token = get_token()
ws_server_queue = asyncio.Queue()


async def send_data(data: json, post_type: str) -> None:
    send_data = {
        "time": int(time.time()),
        "self_id": uid2hex(get_bot_id()),
        "post_type": post_type,
    }

    for i in event_ws_client:
        try:
            await i.send_json({**send_data, **data})
        except:
            event_ws_client.remove(i)


async def api_message(message):
    print(message)


async def event_message():
    while True:
        item = await ws_server_queue.get()

        try:
            message_id = int(item[1].message_id)
        except ValueError:
            message_id = uid2hex(item[1].message_id)
        except:
            pass

        if item[0] == "room_message":
            await send_data(
                {
                    "message_type": "group",
                    "sub_type": "normal",
                    "message_id": message_id,
                    "group_id": uid2hex(GlobalVal.now_room_id),
                    "user_id": uid2hex(item[1].user_id),
                    "anonymous": None,
                    "message": await text2array(item[1].message),
                    "raw_message": str(item[1].message),
                    "font": 456,
                    "sender": {
                        "user_id": uid2hex(item[1].user_id),
                        "nickname": item[1].user_name,
                        "sex": "unknown",
                        "age": "18",
                    },
                },
                'message'
            )
        elif item[0] == "private_message":
            await send_data(
                {
                    "message_type": "private",
                    "sub_type": "friend",
                    "message_id": message_id,
                    "group_id": uid2hex(GlobalVal.now_room_id),
                    "user_id": uid2hex(item[1].user_id),
                    "message": await text2array(item[1].message),
                    "raw_message": str(item[1].message),
                    "font": 456,
                    "sender": {
                        "user_id": uid2hex(item[1].user_id),
                        "nickname": item[1].user_name,
                        "sex": "unknown",
                        "age": "18",
                    },
                },
                'message'
            )


async def websocket_api(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT:
            if msg.data == 'close':
                await ws.close()
            else:
                await api_message(msg.data)

        elif msg.type == aiohttp.WSMsgType.ERROR:
            logger.error(f"[WEBSOCKET] 被错误的关闭，原因：{ws.exception()}")

    logger.info('[WEBSOCKET] WebSocket 连接已关闭')

    return ws


async def websocket_event(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    event_ws_client.append(ws)

    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT:
            if msg.data == 'close':
                event_ws_client.remove(ws)
                await ws.close()

        elif msg.type == aiohttp.WSMsgType.ERROR:
            logger.error(f"[WEBSOCKET] 被错误的关闭，原因：{ws.exception()}")

    logger.info('[WEBSOCKET] WebSocket 连接已关闭')

    return ws


async def websocket(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    event_ws_client.append(ws)

    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT:
            if msg.data == 'close':
                event_ws_client.remove(ws)
                await ws.close()
            else:
                await api_message(msg.data)
        elif msg.type == aiohttp.WSMsgType.ERROR:
            logger.error(f"[WEBSOCKET] 被错误的关闭，原因：{ws.exception()}")

    logger.info('[WEBSOCKET] WebSocket 连接已关闭')

    return ws

@web.middleware
async def verify_token(request, handler):
    logger.info(f"[WEBSOCKET SERVER] {request.remote} {request.method} {request.path}")

    if not get_serve()['websocket_server']['verify']:
        return await handler(request)

    auth_header = request.query.get('access_token', None)
    if auth_header is not None:
        if auth_header != api_token:
            return web.json_response({'code': 403, 'error': 'access token 不符合'}, status=403)
        return await handler(request)

    auth_header = request.headers.get('Authorization')

    if not auth_header or not auth_header.startswith('Bearer '):
        return web.json_response({'code': 401, 'error': 'access token 未提供'}, status=401)

    token = auth_header.split('Bearer ')[1].strip()
    if token != api_token:
        return web.json_response({'code': 403, 'error': 'access token 不符合'}, status=403)

    return await handler(request)


app = web.Application(middlewares=[verify_token])
app.add_routes([web.get(f'{onebot_v11_url}/api', websocket_api),
                web.get(f'{onebot_v11_url}/event', websocket_event),
                web.get(f'{onebot_v11_url}/', websocket),
                web.get(f'{onebot_v11_url}', websocket)])

runner = web.AppRunner(app)


async def start_websocket_server(host: str, port: int) -> None:
    close_event = asyncio.Event()

    try:
        await runner.setup()
        site = web.TCPSite(runner, host, port)
        await site.start()
        logger.info('[WEBSOCKET SERVER] 监听 http://{}:{} 中'.format(host, port))
    except:
        logger.error('[WEBSOCKET SERVER] 启动时出错: {}'.format(traceback.format_exc()))
        return

    async def close_websocket():
        await runner.cleanup()
        logger.info('[WEBSOCKET SERVER] 已释放监听')

    async def wait_for_close():
        await close_event.wait()
        await close_websocket()

    task = asyncio.create_task(event_message())
    task = asyncio.create_task(wait_for_close())

    try:
        while True:
            await asyncio.sleep(1)

    except:
        await close_websocket()
