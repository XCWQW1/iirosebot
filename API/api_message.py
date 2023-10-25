def at_user(user_id: str) -> str:
    """
    艾特用户
    :param user_id:  用户的唯一标识
    :return:
    """
    return f" [*{user_id}*] "


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
