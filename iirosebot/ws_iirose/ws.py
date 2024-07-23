"""
处理ws链接
"""
import asyncio
import traceback
import websockets

from enum import Enum
from loguru import logger

from iirosebot.exception import LoginException
from iirosebot.globals.globals import GlobalVal
from iirosebot.ws_iirose.ping import ping_iirose
from iirosebot.ws_iirose.login_bot import login_to_server
from iirosebot.ws_iirose.transfer_plugin import process_message
from iirosebot.main import shutdown


class Status(Enum):
    ONLINE = 0
    OFFLINE = 1
    RECONNECT = 2


bot_status = Status.OFFLINE


async def connect_to_iirose_server():
    global bot_status
    logger.info('正在链接到蔷薇服务器')
    wss_host = 1
    while True:
        try:
            async with websockets.connect(f'ws://m{wss_host if wss_host else ""}.iirose.com:8777') as websocket:
                GlobalVal.websocket = websocket
                bot_status = Status.ONLINE
                loop = asyncio.get_event_loop()
                loop.create_task(login_to_server(websocket)), loop.create_task(ping_iirose(websocket))
                async for message in websocket:
                    await process_message(message, websocket)
        except LoginException:
            shutdown()
        except:
            if GlobalVal.close_status:
                await GlobalVal.websocket.close()
                logger.info('已关闭对蔷薇服务器的链接')
                break
            bot_status = Status.RECONNECT
            if GlobalVal.move_room:
                logger.info(f'正在移动到 {GlobalVal.room_id}')
                GlobalVal.move_room = False
            else:
                logger.error(f'与蔷薇服务器的连接已断开：\n{traceback.format_exc()}\n将在五秒后重连')
                if wss_host == 2:
                    wss_host = None
                elif wss_host is None:
                    wss_host = 1
                wss_host = 2
                await asyncio.sleep(5)
