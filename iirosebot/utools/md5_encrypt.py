import re
import hashlib


def md5_encrypt(string):
    if bool(re.fullmatch(r"[a-fA-F0-9]{32}", string)):  # 已经是md5就不加密了
        return string

    md5 = hashlib.md5()
    md5.update(string.encode('utf-8'))
    encrypted_string = md5.hexdigest()

    return encrypted_string
