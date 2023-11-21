import ssl
import asyncio
import time
import traceback
import websockets

from enum import Enum
from loguru import logger
from globals.globals import GlobalVal
from ws_iirose.ping import ping_iirose
from ws_iirose.login_bot import login_to_server
from ws_iirose.transfer_plugin import process_message


class Status(Enum):
    ONLINE = 0
    OFFLINE = 1
    RECONNECT = 2


bot_status = Status.OFFLINE


async def connect_to_iirose_server(plugin_list):
    global bot_status
    logger.info('正在连接')
    wss_host = 2
    while True:
        try:
            async with websockets.connect(f'wss://m{wss_host if wss_host else ""}.iirose.com:8778', ssl=ssl.create_default_context()) as websocket:
                GlobalVal.websocket = websocket
                bot_status = Status.ONLINE
                loop = asyncio.get_event_loop()
                task = loop.create_task(login_to_server(websocket, plugin_list)), loop.create_task(ping_iirose(websocket))
                async for message in websocket:
                    await process_message(message, websocket, plugin_list)
        except Exception as e:
            bot_status = Status.RECONNECT
            if GlobalVal.move_room:
                logger.info(f'正在移动到 {GlobalVal.room_id}')
                GlobalVal.move_room = False
            else:
                logger.error(f'Error，ws连接断开：{e}，五秒后重连')
                if wss_host != 9 and type(wss_host) == int:
                    wss_host += 1
                elif wss_host is None:
                    wss_host = 1
                else:
                    wss_host = None
                time.sleep(5)
