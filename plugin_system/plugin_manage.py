from plugin_system.plugin_init import plugin_manage_data


async def on_plugin(plugin_name):
    if plugin_name in plugin_manage_data:
        plugin_manage_data[plugin_name]['status'] = True
        return {'code': 200}
    else:
        return {'code': 404, 'error': '找不到该插件'}


async def off_plugin(plugin_name):
    if plugin_name in plugin_manage_data:
        plugin_manage_data[plugin_name]['status'] = False
        return {'code': 200}
    else:
        return {'code': 404, 'error': '找不到该插件'}


async def plugin_status(plugin_name):
    if plugin_name in plugin_manage_data:
        return plugin_manage_data[plugin_name]['status']
    else:
        return False
