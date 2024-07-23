import hashlib


def md5_encrypt(string):
    md5 = hashlib.md5()
    md5.update(string.encode('utf-8'))
    encrypted_string = md5.hexdigest()

    return encrypted_string
