import asyncio
import traceback
import threading
import queue

from loguru import logger
from iirosebot.globals.globals import GlobalVal
from iirosebot.plugin_system.plugin_init import plugin_manage_data
from iirosebot.serve.webhook import wh_queue
from iirosebot.serve.websocket_server import ws_server_queue
from iirosebot.API.api_get_config import get_serve

serve_status = get_serve()
task_queue = queue.Queue()


async def plugin_transfer_thread(function_name, data=None, one_func=False):
    if one_func:
        if data is not None:
            try:
                len(data)
                task = asyncio.create_task(function_name(*data))
            except:
                task = asyncio.create_task(function_name(data))
        else:
            task = asyncio.create_task(function_name())
        await asyncio.gather(task)
    else:
        if GlobalVal.plugin_list is not None:
            for plugin_key, plugin_date in GlobalVal.plugin_list.items():
                plugin_name = plugin_date['name']
                plugin_def = plugin_date['def']
                plugin_file_path = plugin_date['file_path']

                if plugin_name in plugin_manage_data:
                    if plugin_manage_data[plugin_name]['status']:
                        if plugin_def is not None:
                            if function_name in plugin_def:
                                try:
                                    if data is not None:
                                        try:
                                            len(data)
                                            task = asyncio.create_task(plugin_def[function_name](*data))
                                        except:
                                            task = asyncio.create_task(plugin_def[function_name](data))
                                    else:
                                        task = asyncio.create_task(plugin_def[function_name]())
                                    await asyncio.gather(task)

                                except:
                                    logger.error(f'调用插件 {plugin_file_path} 报错：{traceback.format_exc()}')


class PluginTransferThread(threading.Thread):
    def __init__(self, queue_in):
        threading.Thread.__init__(self)
        self.queue = queue_in
        self.stop_event = threading.Event()

    def run(self):
        while not self.stop_event.is_set():
            task = self.queue.get()
            if task is not None:
                try:
                    asyncio.run(plugin_transfer_thread(*task))
                except:
                    logger.error(f'执行插件任务报错：{traceback.format_exc()}')
                self.queue.task_done()
            if task[0] == 'on_close':
                break

    def stop(self):
        self.stop_event.set()


PluginTransferThread(task_queue).start()


async def plugin_transfer(function_name, data=None, one_func=False):
    task_queue.put((function_name, data, one_func))

    if not one_func and serve_status['webhook']['enabled']:
        await wh_queue.put((function_name, data))

    if not one_func and serve_status['websocket_server']['enabled']:
        await ws_server_queue.put((function_name, data))

