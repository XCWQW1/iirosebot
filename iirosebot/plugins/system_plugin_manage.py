from iirosebot.API.api_iirose import APIIirose
from iirosebot.API.decorator import on_command, MessageType
from iirosebot.API.api_get_config import get_master_id
from iirosebot.API.api_message import send_markdown_code
from iirosebot.plugin_system.plugin_manage import plugin_manage_data, off_plugin, on_plugin, reload_plugin, load_plugin

API = APIIirose()


@on_command('.插件', substring=False, command_type=[MessageType.private_chat])
async def plugin_help(Message):
    if Message.user_id == get_master_id():
        text = ('.插件 - 显示当前页面\n'
                '.插件 列表 - 列出所有插件\n'
                '.插件 启用 <插件名> - 启用插件\n'
                '.插件 禁用 <插件名> - 禁用插件\n'
                '.插件 重载 <插件名> - 重新载入插件\n'
                '.插件 加载 <插件名> - 加载未载入的插件')
        await API.send_msg(Message, send_markdown_code(text))
    else:
        await API.send_msg(Message, '无权执行')


@on_command('.插件 ', substring=[True, 4], command_type=[MessageType.private_chat])
async def plugin_manage(message, text):
    if message.user_id == get_master_id():
        if text[:2] == '列表':
            msg = ''
            for i in plugin_manage_data:
                msg += f'{"启用" if plugin_manage_data[i]["status"] else "禁用"}-{i}\n'
            await API.send_msg(message, send_markdown_code(msg[:-1]))
        elif text[:2] == '禁用':
            data = await off_plugin(text[3:])
            if data['code'] == 200:
                await API.send_msg(message, '禁用成功！')
            else:
                await API.send_msg(message, '禁用失败，请检查插件名是否正确')
        elif text[:2] == '启用':
            data = await on_plugin(text[3:])
            if data['code'] == 200:
                await API.send_msg(message, '启用成功！')
            else:
                await API.send_msg(message, '启用失败，请检查插件名是否正确')
        elif text[:2] == '重载':
            data = await reload_plugin(text[3:])
            if data['code'] == 200:
                await API.send_msg(message, '重载成功！')
            else:
                await API.send_msg(message, '重载失败，请检查插件名是否正确')
        elif text[:2] == '加载':
            data = await load_plugin(text[3:])
            if data['code'] == 200:
                await API.send_msg(message, '加载成功！')
            else:
                await API.send_msg(message, '加载失败，请检查插件名是否正确')
        else:
            await API.send_msg(message, '未知参数')
    else:
        await API.send_msg(message, '无权执行')
