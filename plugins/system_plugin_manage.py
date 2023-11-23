import asyncio

from API.api_iirose import APIIirose
from API.decorator.command import on_command, MessageType
from API.api_message import send_markdown_code
from API.api_get_config import get_master_id
from plugin_system.plugin_init import plugin_manage_data
from plugin_system.plugin_manage import *

API = APIIirose()


@on_command('.插件', substring=False, command_type=[MessageType.room_chat, MessageType.private_chat])
async def plugin_help(Message):
    await API.send_msg(Message, '')


@on_command('.插件 ', substring=[True, 4], command_type=[MessageType.room_chat, MessageType.private_chat])
async def plugin_manage(Message, text):
    if Message.user_id == get_master_id():
        if text[:2] == '列表':
            msg = ''
            for i in plugin_manage_data:
                msg += f'{"启用" if plugin_manage_data[i]["status"] else "禁用"}-{i}\n'
            await API.send_msg(Message, send_markdown_code(msg[:-2]))
        elif text[:2] == '禁用':
            data = await off_plugin(text[3:])
            if data['code'] == 200:
                await API.send_msg(Message, '禁用成功！')
            else:
                await API.send_msg(Message, '禁用失败，请检查插件名是否正确')
        elif text[:2] == '启用':
            data = await on_plugin(text[3:])
            if data['code'] == 200:
                await API.send_msg(Message, '启用成功！')
            else:
                await API.send_msg(Message, '启用失败，请检查插件名是否正确')
        elif text[:2] == '重载':
            data = await reload_plugin(text[3:])
            if data['code'] == 200:
                await API.send_msg(Message, '重载成功！')
            else:
                await API.send_msg(Message, '重载失败，请检查插件名是否正确')
        else:
            await API.send_msg(Message, '未知参数')
    else:
        await API.send_msg(Message, '无权执行')
