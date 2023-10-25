import asyncio
import importlib
import traceback
import threading
import queue

from loguru import logger

plugin_data_list = {}
task_queue = queue.Queue()


async def plugin_transfer_thread(function_name, plugin_dict, data=None):
    if plugin_dict:
        for plugin_key, plugin_date in plugin_dict.items():
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


async def plugin_transfer(function_name, plugin_dict, data=None):
    task_queue.put((function_name, plugin_dict, data))


async def plugins_date(plugin_dict):
    logger.info('正在获取插件元数据')
    for plugin_key, plugin_date in plugin_dict.items():
        plugin_name = plugin_date['name']
        plugin_file_path = plugin_date['file_path']
        try:
            spec = importlib.util.spec_from_file_location('', plugin_file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        except:
            logger.error(f'获取插件 {plugin_file_path} 元数据报错：{traceback.format_exc()}')
            continue

        if hasattr(module, 'PLUGIN_DATE'):
            PLUGIN_DATE = getattr(module, 'PLUGIN_DATE')
        else:
            PLUGIN_DATE = {
                'name': plugin_name,
                "author": "[未知]",
                'version': '[未知]',
                "description": "[未知]",
                "dependencies": {}
            }
        plugin_data_list[plugin_name] = PLUGIN_DATE
    logger.info(f'共成功获取到 {len(plugin_data_list)} 个插件的元数据')
    return plugin_data_list
