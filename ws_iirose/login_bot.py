import asyncio
import json
from globals.globals import GlobalVal

from loguru import logger
from API.api_load_config import load_config
from utools.md5_encrypt import md5_encrypt
from plugin_system.plugin_transfer import plugin_transfer

on_init = False


async def login_to_server(websocket, plugin_list):
    GlobalVal.plugin_list = plugin_list
    bot_name, room_id, bot_password = load_config()
    logger.info('开始登陆')
    # 登陆
    if GlobalVal.room_id is not None:
        room_id = GlobalVal.room_id
        GlobalVal.now_room_id = GlobalVal.room_id
    if GlobalVal.now_room_id is None:
        GlobalVal.now_room_id = room_id

    login_json = {
        "r": room_id,
        "n": bot_name,
        "p": md5_encrypt(bot_password),
        "st": 'n',
        "mo": '',
        "mb": '',
        "mu": '01'
    }
    if GlobalVal.move_room:
        GlobalVal.move_room = False
    await websocket.send('*' + json.dumps(login_json))
    logger.info('已发送登陆信息')
    await asyncio.sleep(2)


async def init_plugin():
    global on_init
    if not on_init:
        logger.info('执行插件初始化')
        await plugin_transfer('on_init')
        on_init = True
    logger.info('高性能ですから')
