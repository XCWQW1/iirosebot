"""
框架内所有会抛出的异常
"""


class IIRoseBotException(Exception):
    """所有异常基类"""


class APIException(IIRoseBotException):
    """接口异常"""


class DecoratorException(IIRoseBotException):
    """装饰器异常"""


class LoginException(IIRoseBotException):
    """登陆错误"""
