from loguru import logger
from API.api_iirose import APIIirose  # 大部分接口都在这里
from globals.globals import GlobalVal  # 一些全局变量 now_room_id 是机器人当前所在的房间标识，websocket是ws链接，请勿更改其他参数防止出bug，也不要去监听ws，websockets库只允许一个监听流
from API.api_get_config import get_master_id  # 用于获取配置文件中主人的唯一标识
from API.decorator.command import on_command, MessageType  # 注册指令装饰器和消息类型Enmu

API = APIIirose()  # 吧class定义到变量就不会要求输入self了（虽然我都带了装饰器没有要self的 直接用APIIirose也不是不可以 习惯了


@on_command('测试', False, command_type=[MessageType.room_chat, MessageType.private_chat])  # command_type 参数可让本指令在哪些地方生效，发送弹幕需验证手机号，每天20条。本参数需要输入列表，默认不输入的情况下只对房间消息做出反应，单个类型也需要是列表
async def test_0(Message):  # 请保证同一个插件内不要有两个相同的指令函数名进行注册，否则只会保留最后一个注册的
    await API.send_msg(Message, 'Hello World!')  # send_msg API会自己通过第一个参数自动选择发送到的地方，目前有房间，私聊，弹幕


@on_command('TEST-', True, command_type=[MessageType.room_chat, MessageType.private_chat])  # substring可输入布朗类型也可以是列表，布朗的情况下框架自动获取长度判断，用于取左侧的消息，第二个参数为数字类，框架会取这个数字的左侧，如果发送的消息=左侧这几个数字的消息就会执行此函数，函数需要有两个参数，第二个参数会返回去除指令的消息
async def test_1(Message, text):
    await API.send_msg(Message, text)


async def user_move_room(Message):
    # 当房间内用户移动到其他房间时触发本函数
    pass


async def user_join_room(Message):
    # 当有用户(包括机器人)加入到当前房间时触发本函数
    # 框架默认消息均不排除自身，请通过Message中的is_bot进行判断，该参数为布朗类，为True时说明该消息为自身
    await API.like(Message.user_id)  # 触发进入房间后机器人会给触发的用户点赞


async def user_leave_room(Message):
    # 当有用户(包括机器人)离开到当前房间时触发本函数
    # 接口内还有其他参数可根据注释自行使用，如有疑问请加入README中的房间询问
    pass


async def revoke_message(Message):
    # 有撤回消息时会触发这个函数（不排除自身
    # Message里面只有user_id和message_id
    pass


async def room_message(Message):
    # 接受到房间消息会触发该函数，排除自身
    pass


"""
未完待续，其余事件请自行查看 ws_iirose>transfer_plugin.py 中的所有 plugin_transfer 函数
"""


async def on_init():
    logger.info('框架会在登陆成功后执行这个函数，只会执行一次')  # 本框架使用logger日志管理器
