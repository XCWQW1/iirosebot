import asyncio
import os
import signal
import sys
import threading

import requests

from API.api_get_config import get_log_level
from log.main import log
from loguru import logger
from globals.globals import GlobalVal
from init.main_init import main_init


def signal_handler(sig, frame):
    logger.info('框架已关闭')
    pid = os.getpid()
    if sys.platform == 'win32':
        os.kill(pid, signal.CTRL_C_EVENT)
    else:
        os.kill(pid, signal.SIGKILL)
    sys.exit(0)


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    log_level = get_log_level()
    log(log_level)
    iirosebot_version = 'v1.6.2'

    def check_version():
        try:
            data = requests.get('https://api.github.com/repos/XCWQW1/iirosebot/releases', timeout=30).json()
            if iirosebot_version == data[0]['tag_name']:
                logger.info('框架版本已为最新')
            else:
                logger.warning(f"框架最新版本为：{data[0]['tag_name']}")
        except:
            logger.warning('获取版本信息失败！')

    logger.info(f'框架版本：{iirosebot_version}，日志等级：{log_level}')
    logger.info('正在检查更新中...')
    threading.Thread(target=check_version()).start()
    asyncio.run(main_init())
    from ws_iirose.ws import connect_to_iirose_server
    from plugin_system.plugin_init import find_plugins_functions
    GlobalVal.plugin_list = asyncio.run(find_plugins_functions())
    asyncio.run(connect_to_iirose_server())
