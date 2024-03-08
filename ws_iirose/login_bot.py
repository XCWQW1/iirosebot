import asyncio
import json

from API.api_get_config import get_introduction
from globals.globals import GlobalVal

from loguru import logger
from API.api_load_config import load_config
from utools.md5_encrypt import md5_encrypt
from plugin_system.plugin_transfer import plugin_transfer

on_init = False


async def login_to_server(websocket):
    bot_name, room_id, bot_password = load_config()
    logger.info('开始登陆')
    # 登陆
    if GlobalVal.room_id is not None:
        room_id = GlobalVal.room_id
        GlobalVal.now_room_id = GlobalVal.room_id
    if GlobalVal.now_room_id is None:
        GlobalVal.now_room_id = room_id

    with open("config/room.json", 'r', encoding='utf-8') as file:
        room_config = json.load(file)

    login_json = {
        "r": room_id,
        "n": bot_name,
        "p": md5_encrypt(bot_password),
        "st": 'n',
        "mo": str(get_introduction()),
        "mb": '',
        "mu": '01',
        'fp': f'@{md5_encrypt(bot_name)}'
    }

    if GlobalVal.move_room:
        login_json['lr'] = GlobalVal.old_room_id
        if GlobalVal.room_password is not None:
            login_json['rp'] = GlobalVal.room_password
            room_config[room_id] = GlobalVal.room_password
            with open("config/room.json", 'w', encoding='utf-8') as file:
                json.dump(room_config, file, indent=4, ensure_ascii=False)
        GlobalVal.move_room = False

    if room_id in room_config:
        login_json['rp'] = room_config[room_id]

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
