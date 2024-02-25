import re


def at_user(user_name: str) -> str:
    """
    艾特用户
    :param user_name:  用户名
    :return:
    """
    return f" [*{user_name}*] "


def room_address(room_id: str) -> str:
    """
    发送房间地址
    :param room_id:  房间的唯一标识
    :return:
    """
    return f" [_{room_id}_] "


def send_markdown(markdown_text: str) -> str:
    """
    发送markdown文本
    :param markdown_text:
    :return:
    """
    return f"\\\\\\*\n{markdown_text}"


def send_markdown_code(code: str, lang: str = '') -> str:
    """
    发送markdown代码框
    :param code:  代码
    :param lang:  开发语言可不写
    :return:
    """
    return f"\\\\\\*\n```{lang}\n{code}\n```"


def parse_room_id(room_text: str) -> str:
    # 输入房间消息解析出房间表示
    return re.findall(r"_([^_]+)_", room_text)[0].replace(" ", "")
