from API.api_get_config import get_master_id
from API.api_iirose import APIIirose
from API.api_load_config import load_config
from API.api_message import parse_room_id, at_user
from API.decorator.command import on_command, MessageType
from globals.globals import GlobalVal

API = APIIirose()
move_to_master_bool = False


@on_command('移动到 ', [True, 4], command_type=[MessageType.room_chat, MessageType.private_chat])
async def move_to(Message, text):
    if Message.user_id == get_master_id():
        try:
            room_id = parse_room_id(text)
        except:
            await API.send_msg(Message, f'{at_user(Message.user_name)}无法解析到房间标识，请检查输入是否正确！')
            return
        await API.send_msg(Message, f'{at_user(Message.user_name)}正在尝试移动到 {text} ！')
        move_date = await API.move_room(room_id)
        if move_date['code'] == 500:
            await API.send_msg(Message, f'{at_user(Message.user_name)}不可以移动到当前房间！')
    else:
        await API.send_msg(Message, f'{at_user(Message.user_name)}错误，您没有权限执行')


@on_command('开始跟随', False, command_type=[MessageType.room_chat, MessageType.private_chat])
async def flow_me(Message):
    global move_to_master_bool
    if Message.user_id == get_master_id():
        if not move_to_master_bool:
            move_to_master_bool = True
            await API.send_msg(Message, f'{at_user(Message.user_name)}已开始跟随')
        else:
            await API.send_msg(Message, f'{at_user(Message.user_name)}错误，已经执行过一次了')
    else:
        await API.send_msg(Message, f'{at_user(Message.user_name)}错误，您没有权限执行')


@on_command('停止跟随', False, command_type=[MessageType.room_chat, MessageType.private_chat])
async def wait_here(Message):
    global move_to_master_bool
    if Message.user_id == get_master_id():
        if move_to_master_bool:
            move_to_master_bool = False
            await API.send_msg(Message, f'{at_user(Message.user_name)}已停止跟随')
        else:
            await API.send_msg(Message, f'{at_user(Message.user_name)}错误，已经执行过一次了')
    else:
        await API.send_msg(Message, f'{at_user(Message.user_name)}错误，您没有权限执行')


@on_command('回到默认房间', False, command_type=[MessageType.room_chat, MessageType.private_chat])
async def back_home(Message):
    if Message.user_id == get_master_id():
        bot_name, room_id, bot_password = load_config()
        if GlobalVal.now_room_id != room_id:
            await API.send_msg(Message, f'{at_user(Message.user_name)}已执行')
            await API.move_room(room_id)
        else:
            await API.send_msg(Message, f'{at_user(Message.user_name)}错误，当前房间已是默认房间！')
    else:
        await API.send_msg(Message, f'{at_user(Message.user_name)}错误，您没有权限执行')


async def user_move_room(Message):
    global move_to_master_bool
    if move_to_master_bool:
        if Message.user_id == get_master_id():
            await API.move_room(Message.to_room_id)
