import functools
import os
import sys
import inspect
import importlib
import importlib.util
import traceback

from loguru import logger

plugin_data_list = {}
plugin_manage_data = {}


async def find_plugin():
    plugin_files = [os.path.join("plugins", plugin_file) for plugin_file in os.listdir("plugins")
                    if plugin_file.endswith('.py') and not plugin_file.startswith('__')]
    return plugin_files


async def get_functions_from_file(file_path, plugin_name):
    try:
        module_name = inspect.getmodulename(file_path)
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        functions = {}
        for name, obj in inspect.getmembers(module):
            try:
                if inspect.iscoroutinefunction(obj):  # 判断是否为协程函数
                    coro_func = functools.partial(obj)  # 使用偏函数包装协程函数
                    coro_func.__name__ = name  # 设置偏函数的名称为原始函数名称
                    functions[name] = coro_func
                elif inspect.isfunction(obj):  # 判断是否为普通函数
                    functions[name] = obj
            except:
                pass

        if hasattr(module, 'PLUGIN_DATE'):
            PLUGIN_DATE = getattr(module, 'PLUGIN_DATE')
        else:
            PLUGIN_DATE = {
                'name': plugin_name,
                "author": None,
                'version': None,
                "description": None,
                "dependencies": {}
            }
        plugin_manage_data[plugin_name] = {
            "status": True
        }
        plugin_data_list[plugin_name] = PLUGIN_DATE

    except:
        logger.error(f'记录插件 {file_path} 中的函数出错：{traceback.format_exc()}')
        functions = None

    return functions


async def find_plugins_functions():
    logger.info('开始寻找插件！')
    plugin_num = 0
    plugin_dnf_list = {}
    get_find_plugins_list = await find_plugin()
    for file_path in get_find_plugins_list:
        if sys.platform.startswith("win32"):
            name = file_path.split('plugins\\')[1].replace('.py', '')
        else:
            name = file_path.split('plugins/')[1].replace('.py', '')
        logger.info(f'找到插件：{name}')
        def_ls = await get_functions_from_file(file_path, name)
        plugin_dnf_list[plugin_num] = {'name': name, 'file_path': file_path, 'def': def_ls}
        plugin_num = plugin_num + 1
    logger.info(f'寻找完毕，共计 {plugin_num} 个插件以及 {len(plugin_data_list)} 条插件信息')
    return plugin_dnf_list
