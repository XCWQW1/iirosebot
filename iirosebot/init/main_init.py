import os
import yaml
import aiohttp
import asyncio

from loguru import logger
from iirosebot.globals.globals import GlobalVal
from iirosebot.utools.generate_token import generate_token


async def initialize_folder(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)
        logger.info(f'文件夹 {folder} 不存在，已自动创建')
    else:
        logger.info(f'文件夹 {folder} 已经存在')


async def create_config_file(config_path):
    config_data = {
        'bot': {
            'room_id': '5ce6a4b520a90',
            'username': '',
            'password': '',
            'color': '040b02',
            'introduction': ''
        },
        'serve': {
            'token': generate_token(40),
            'http_api': {
                'enabled': False,
                'verify': False,
                'host': 'localhost',
                'port': 9000,
            },
            'webhook': {
                'enabled': False,
                'url': 'http://your_webhook.server/',
                'verify': False,
                'time_out': 3000,
            },
            'websocket_server': {
                'enabled': False,
                'verify': False,
                'host': 'localhost',
                'port': 9002,
            },
            'websocket_reverse': {
                'enabled': False,
                'verify': False,
                'url': 'ws://your_websocket_universal.server',
                'api': 'ws://your_websocket_api.server',
                'event': 'ws://your_websocket_event.server',
                'reconnect_interval': 3000,
            },
        },
        'heartbeat': {
            'enabled': False,
            'interval': 15000,
        },
        'other': {
            'master_id': '',
        },
        'log': {
            'level': 'INFO',
            'color': True,
        }
    }
    with open(config_path, "w", encoding='utf-8') as f:
        yaml.dump(config_data, f, allow_unicode=True)
    logger.warning(f'配置文件 {config_path} 不存在，已自动创建')


async def create_room_config_file(config_path):
    with open(config_path, "w", encoding='utf-8') as f:
        f.write('{}')
    logger.warning(f'配置文件 {config_path} 不存在，已自动创建')


async def check_folders():
    folders = ['plugins', 'logs', 'config']

    logger.info("正在检测配置文件夹是否存在")

    tasks = []
    for folder in folders:
        tasks.append(asyncio.create_task(initialize_folder(folder)))

    await asyncio.gather(*tasks)

    logger.info("正在检测配置文件是否存在")
    config_path = "config/config.yml"

    if not os.path.exists(config_path):
        await create_config_file(config_path)
    else:
        logger.info(f'配置文件 {config_path} 已经存在')

    config_path = "config/room.json"

    if not os.path.exists(config_path):
        await create_room_config_file(config_path)
    else:
        logger.info(f'配置文件 {config_path} 已经存在')


async def check_version():
    logger.info('正在检查更新中...')
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('https://api.github.com/repos/XCWQW1/iirosebot/releases', timeout=30) as response:
                data = await response.json()
                if GlobalVal.iirosebot_version == data[0]['tag_name']:
                    logger.info('框架版本已为最新')
                else:
                    logger.warning(f"框架最新版本为：{data[0]['tag_name']}")
    except Exception as e:
        logger.warning(f'获取版本信息失败！错误信息：{str(e)}')


async def main_init():
    task = asyncio.create_task(check_version())
    await check_folders()
