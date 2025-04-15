import os
import sys

from iirosebot.globals.globals import GlobalVal
from iirosebot.plugin_system.plugin_init import plugin_manage_data, get_functions_from_file

no_plugin_error = '找不到该插件'


async def on_plugin(plugin_name):
    if plugin_name in plugin_manage_data:
        plugin_manage_data[plugin_name]['status'] = True
        return {'code': 200}
    else:
        return {'code': 404, 'error': no_plugin_error}


async def off_plugin(plugin_name):
    if plugin_name in plugin_manage_data:
        plugin_manage_data[plugin_name]['status'] = False
        return {'code': 200}
    else:
        return {'code': 404, 'error': no_plugin_error}


async def reload_plugin(plugin_name):
    if plugin_name in plugin_manage_data:
        plugin_list = {}
        for num, plugin_info in GlobalVal.plugin_list.items():
            plugin_info['num'] = num
            plugin_list[plugin_info['name']] = plugin_info

        def_ls = await get_functions_from_file(plugin_list[plugin_name]['file_path'], plugin_list[plugin_name]['name'])
        GlobalVal.plugin_list[plugin_list[plugin_name]['num']] = {'name': plugin_list[plugin_name]['name'], 'file_path': plugin_list[plugin_name]['file_path'], 'def': def_ls}
        return {'code': 200}
    else:
        return {'code': 404, 'error': no_plugin_error}


async def load_plugin(plugin_name):
    file_path = f"plugins/{plugin_name}.py"
    if os.path.exists(file_path):
        if sys.platform.startswith("win32"):
            name = file_path.split('plugins\\')[1].replace('.py', '')
        else:
            name = file_path.split('plugins/')[1].replace('.py', '')
        def_ls = await get_functions_from_file(file_path, name)
        GlobalVal.plugin_list[len(GlobalVal.plugin_list)] = {'name': name, 'file_path': file_path, 'def': def_ls}
        return {'code': 200}
    else:
        return {'code': 404, 'error': no_plugin_error}


async def plugin_status(plugin_name):
    if plugin_name in plugin_manage_data:
        return plugin_manage_data[plugin_name]['status']
    else:
        return False
