import asyncio
import traceback
import threading
import queue

from loguru import logger
from globals.globals import GlobalVal

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
    else:
        if GlobalVal.plugin_list is not None:
            for plugin_key, plugin_date in GlobalVal.plugin_list.items():
                plugin_name = plugin_date['name']
                plugin_def = plugin_date['def']
                plugin_file_path = plugin_date['file_path']
                if plugin_def is not None:
                    if function_name in plugin_def:
                        try:
                            if data is not None:
                                task = asyncio.create_task(plugin_def[function_name](data))
                            else:
                                task = asyncio.create_task(plugin_def[function_name]())

                        except Exception as e:
                            logger.error(f'调用插件 {plugin_file_path} 报错：{traceback.format_exc()}')


class PluginTransferThread(threading.Thread):
    def __init__(self, queue_in):
        threading.Thread.__init__(self)
        self.queue = queue_in

    def run(self):
        while True:
            # 从队列中获取任务并执行
            task = self.queue.get()
            if task is None:
                pass
            else:
                try:
                    asyncio.run(plugin_transfer_thread(*task))
                except Exception as e:
                    logger.error(f'执行插件任务报错：{traceback.format_exc()}')
                self.queue.task_done()


PluginTransferThread(task_queue).start()


async def plugin_transfer(function_name, data=None, one_func=False):
    task_queue.put((function_name, data, one_func))
