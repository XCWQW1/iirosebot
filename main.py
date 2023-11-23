import asyncio
import os
import signal
import sys

from log.main import log
from loguru import logger
from globals.globals import GlobalVal
from init.main_init import main_init
from ws_iirose.ws import connect_to_iirose_server
from plugin_system.plugin_init import find_plugins_functions


def signal_handler(sig, frame):
    logger.info('框架已关闭')
    pid = os.getpid()
    if sys.platform == 'win32':
        os.kill(pid, signal.CTRL_C_EVENT)
    else:
        os.kill(pid, signal.SIGKILL)
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)

if __name__ == '__main__':
    log('INFO')
    asyncio.run(main_init())
    GlobalVal.plugin_list = asyncio.run(find_plugins_functions())
    asyncio.run(connect_to_iirose_server())
