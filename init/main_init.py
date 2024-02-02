import os
import sys
import yaml
import signal
import asyncio
import configparser

from loguru import logger


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
            'color': '040b02'
        },
        'other': {
            'master_id': ''
        }
    }
    with open(config_path, "w", encoding='utf-8') as f:
        yaml.dump(config_data, f, allow_unicode=True)
    logger.error(f'配置文件 {config_path} 不存在，已自动创建')
    logger.info("已关闭程序，请配置后重载")
    logger.info('框架已关闭')
    pid = os.getpid()
    if sys.platform == 'win32':
        os.kill(pid, signal.CTRL_C_EVENT)
    else:
        os.kill(pid, signal.SIGKILL)
    sys.exit(0)


async def main_init():
    folders = ['plugins', 'logs', 'config']

    logger.info("正在监测配置文件夹是否存在")

    tasks = []
    for folder in folders:
        tasks.append(asyncio.create_task(initialize_folder(folder)))

    await asyncio.gather(*tasks)

    # 配置文件路径
    config_path = "config/config.yml"

    # 如果配置文件不存在，则创建一个新的配置文件
    if not os.path.exists(config_path):
        await create_config_file(config_path)
    else:
        logger.info(f'配置文件 {config_path} 已经存在')
