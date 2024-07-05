import asyncio
import time
import traceback
import websockets

from enum import Enum
from loguru import logger
from iirosebot.globals.globals import GlobalVal
from iirosebot.ws_iirose.ping import ping_iirose
from iirosebot.ws_iirose.login_bot import login_to_server
from iirosebot.ws_iirose.transfer_plugin import process_message


class Status(Enum):
    ONLINE = 0
    OFFLINE = 1
    RECONNECT = 2


bot_status = Status.OFFLINE
re_loop = False


async def connect_to_iirose_server():
    global bot_status
    global re_loop
    logger.info('正在连接')
    wss_host = 1
    while True:
        try:
            async with websockets.connect(f'ws://m{wss_host if wss_host else ""}.iirose.com:8777') as websocket:
                re_loop = False
                GlobalVal.websocket = websocket
                bot_status = Status.ONLINE
                loop = asyncio.get_event_loop()
                loop.create_task(login_to_server(websocket)), loop.create_task(ping_iirose(websocket))
                async for message in websocket:
                    await process_message(message, websocket)
        except:
            bot_status = Status.RECONNECT
            if GlobalVal.move_room:
                logger.info(f'正在移动到 {GlobalVal.room_id}')
                GlobalVal.move_room = False
            else:
                logger.error(f'Error，ws连接断开：{traceback.format_exc()}，五秒后重连')
                if wss_host == 2:
                    wss_host = None
                elif wss_host is None:
                    wss_host = 1
                wss_host = 2
                time.sleep(5)
