import re


def uid2hex(user_id):
    if user_id is None:
        return None

    if user_id[:1] == "X":
        cleaned_hex_string = re.sub(r'[^0-9a-fA-F]', '', user_id[1:])
        return -int(cleaned_hex_string, 16)
    else:
        return -int(user_id, 16)


def hex2uid(user_hex: int):
    if user_hex is None:
        return None

    uid = hex(int(user_hex))[3:]
    try:
        int(uid)
        return 'X' + uid
    except:
        pass
    return uid

def message_id_h2i(message_id):
    if message_id is None:
        return None
    try:
        message_id = int(message_id)
    except ValueError:
        message_id = hex2uid(message_id)

    return int(message_id)
