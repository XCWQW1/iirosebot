"""
入口文件
"""
import sys
import signal
import asyncio

from loguru import logger
from iirosebot.log.main import log
from iirosebot.init.main_init import main_init
from iirosebot.globals.globals import GlobalVal
from iirosebot.API.api_get_config import get_log_level, get_serve


def shutdown():
    from iirosebot.plugin_system.plugin_transfer import task_queue, PluginTransferThread
    logger.info('正在关闭框架')
    GlobalVal.close_status = True

    if get_serve()['webhook']['enabled']:
        """ 有缘再修
        from iirosebot.serve.webhook import send_data
        send_data(
            {
                "meta_event_type": "lifecycle",
                "sub_type": "disable"
            },
            'meta_event'
        )
        """
        logger.info('WEBHOOK 已关闭')

    # 释放掉调用插件函数的进程
    task_queue.put(('on_close', None, False))

    PluginTransferThread(task_queue).stop()

    sys.exit(0)


def signal_handler(sig, frame):
    shutdown()


async def main():
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    log_level = get_log_level()
    log(log_level)
    logger.info(f'框架版本：{GlobalVal.iirosebot_version}，日志等级：{log_level}')

    await main_init()

    from iirosebot.ws_iirose.ws import connect_to_iirose_server
    from iirosebot.plugin_system.plugin_init import find_plugins_functions
    GlobalVal.plugin_list = await find_plugins_functions()
    await connect_to_iirose_server()


if __name__ == '__main__':
    asyncio.run(main())


'''
                    _ooOoo_
                   o8888888o
                   88" . "88
                   (| -_- |)
                    O\ = /O
                ____/`---'\____
              .   ' \\| |// `.
               / \\||| : |||// \
             / _||||| -:- |||||- \
               | | \\\ - /// | |
             | \_| ''\---/'' | |
              \ .-\__ `-` ___/-. /
           ___`. .' /--.--\ `. . __
        ."" '< `.___\_<|>_/___.' >'"".
        | | : `- \`.;`\ _ /`;.`/ - ` : | |
         \ \ `-. \_ __\ /__ _/ .-` / /
 ======`-.____`-.___\_____/___.-`____.-'======
                    `=---='

 .............................................
          佛祖保佑             永无BUG
'''
