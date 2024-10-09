import json
import time
import traceback

from loguru import logger

import aiohttp
import asyncio

from iirosebot.API.api_get_config import get_bot_id, get_onebot_v11_serve, get_token
from iirosebot.globals import GlobalVal
from iirosebot.utools import uid2hex
from iirosebot.utools.websocket_utools import return_event_message, api_message

event_ws_client = []
ws_client_queue = asyncio.Queue()

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


async def event_message():
    while not GlobalVal.close_status:
        item = await ws_client_queue.get()
        data = await return_event_message(item)
        if data is None:
            continue
        await send_data(data, 'message')


async def create_ws(client_type, url):
    reconnect_delay = 5
    max_delay = 60

    while not GlobalVal.close_status:
        try:
            async with aiohttp.ClientSession() as session:
                logger.info(f"[WEBSOCKET CLIENT|{client_type}] 正在尝试连接至 {url}")
                headers = {
                    "Content-Type": "application/json",
                    "x-self-id": str(uid2hex(get_bot_id()))
                }

                if client_type == "接口":
                    headers["X-Client-Role"] = "API"
                elif client_type == "事件":
                    headers["X-Client-Role"] = "Event"
                elif client_type == "共用":
                    headers["X-Client-Role"] = "Universal"

                if get_onebot_v11_serve()['websocket_reverse']['verify']:
                    headers['X-Authorization'] = f"Bearer {get_token()}"

                async with session.ws_connect(url, headers=headers) as ws:
                    logger.info(f"[WEBSOCKET CLIENT|{client_type}] 已连接到 {url}")
                    reconnect_delay = 5

                    if client_type in ["共用", "事件"]:
                        event_ws_client.append(ws)
                        await send_data(
                            {
                                "meta_event_type": "lifecycle",
                                "sub_type": "connect"
                            },
                            'meta_event'
                        )

                    async for msg in ws:
                        if msg.data == 'close':
                            logger.error(f"[WEBSOCKET CLIENT|{client_type}] 链接被服务器关闭")
                            await ws.close()
                        elif client_type in ["共用", "接口"]:
                            await api_message(msg.data, ws)

                        if msg.type == aiohttp.WSMsgType.ERROR:
                            logger.error(f"[WEBSOCKET CLIENT|{client_type}] 链接被错误的关闭，原因：{ws.exception()}")

        except Exception as e:
            logger.error(f"[WEBSOCKET CLIENT|{client_type}] ws连接错误: {e}")
            logger.debug(f"[WEBSOCKET CLIENT|{client_type}] {traceback.format_exc()}")

        logger.info(f"[WEBSOCKET CLIENT|{client_type}] {reconnect_delay} 秒后重新尝试连接...")
        await asyncio.sleep(reconnect_delay)

        reconnect_delay = min(reconnect_delay + 1, max_delay)


async def start_websocket_client(config):
    if 'url' in config:
        logger.info(f"[WEBSOCKET CLIENT|共用] 检测到反向ws url参数存在，禁用api, event")
        clients = [
            asyncio.create_task(create_ws("共用", config['url']))
        ]
    else:
        logger.info(f"[WEBSOCKET CLIENT|共用] 检测到反向ws url参数不存在，启用api, event")
        clients = [
            asyncio.create_task(create_ws("接口", config['api'])),
            asyncio.create_task(create_ws("事件", config['event']))
        ]

    await asyncio.gather(asyncio.create_task(event_message()), *clients)

