import asyncio
from loguru import logger
import os
import signal
import sys

from log.main import log
from init.main_init import main_init
from plugin_system.plugin_transfer import plugin_transfer
from ws_iirose.ws import connect_to_iirose_server
from plugin_system.plugin_init import find_plugins_functions


def signal_handler(sig, frame):
    asyncio.run(plugin_transfer('on_stop'))
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
    plugin_list = asyncio.run(find_plugins_functions())
    asyncio.run(connect_to_iirose_server(plugin_list))
