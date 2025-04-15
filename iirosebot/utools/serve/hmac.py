import hmac
import hashlib


def generate_signature(secret_key, message):
    """
    生成HMAC SHA1签名
    :param secret_key: 秘钥
    :param message: 消息
    :return: HMAC SHA1
    """

    signature = hmac.new(secret_key.encode(), message.encode(), hashlib.sha1).hexdigest()

    return signature
