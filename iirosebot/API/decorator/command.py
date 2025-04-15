import os
import inspect

from enum import Enum
from iirosebot.exception import DecoratorException

function_records = {}


class MessageType(Enum):
    room_chat = 0
    private_chat = 1
    danmu = 2
    move_room = 3
    join_room = 4
    leave_room = 5
    revoke_message = 6
    media_video = 7
    media_music = 8


def on_command(command: str, substring: list[bool, int] or bool, command_type: list = [MessageType.room_chat]):
    """
    指令注册装饰器
    :param command:  命令
    :param substring:  [是否取左侧判断触发，取左侧几个字符] 不需要的情况下写False，True的情况下如果不提供list框架会直接len取命令长度进行判断
    :param command_type:  指令处理那几个类型的消息 需要列表内写CommandType类，处理那几种写那几种 默认只处理房间
    :return:
    """
    def decorator(func):
        try:
            if type(substring) is bool:
                if substring:
                    substring_bool = substring
                    substring_num = len(command)
                else:
                    substring_bool = substring
                    substring_num = 0
            else:
                substring_bool = substring[0]
                substring_num = substring[1]
        except:
            raise DecoratorException('substring 参数不正确')
        plugins_file = os.getcwd() + '/plugins/'
        file_name = inspect.getfile(func).replace(plugins_file, '').replace('.py', '')

        if '\\' in file_name:
            file_name = file_name.split('\\')[-1]

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
        raise DecoratorException('装饰器参数缺失')

    return decorator
