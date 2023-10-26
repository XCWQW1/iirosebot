import inspect
import os
from enum import Enum

function_records = {}


class MessageType(Enum):
    room_chat = 0
    private_chat = 1
    danmu = 2
    move_room = 3
    join_room = 4
    leave_room = 5
    revoke_message = 5


def on_command(command: str, substring: list[bool, int] or bool, command_type: list = [MessageType.room_chat]):
    """
    指令注册装饰器
    :param command:  命令
    :param substring:  [是否取左侧判断触发，取左侧几个字符] 不需要的情况下写False
    :param command_type:  指令处理那几个类型的消息 需要列表内写CommandType类，处理那几种写那几种 默认只处理房间
    :return:
    """
    def decorator(func):
        if type(substring) == bool:
            substring_bool = substring
            substring_num = 0
        else:
            substring_bool = substring[0]
            substring_num = substring[1]
        plugins_file = os.getcwd() + '/plugins/'
        file_name = inspect.getfile(func).replace(plugins_file, '').replace('.py', '')
        record = {
            'command': command,
            'func_name': func.__name__,
            'file_name': file_name,
            'substring_bool': substring_bool,
            'substring_num': substring_num,
            'command_type': command_type
        }
        if file_name in function_records:
            function_records[file_name][record['command']] = record
        else:
            function_records[file_name] = {record['command']: record}
        return func

    if callable(command or substring):
        raise Exception('你没有在装饰器内写入参数')

    return decorator
