import json

from loguru import logger

from iirosebot.globals import GlobalVal
from iirosebot.serve.http_server import onebot_v11_api_list
from iirosebot.utools import uid2hex
from iirosebot.utools.serve.array_message import text2array


def return_data(data, status: str, retcode: int, echo_id) -> json:
    return {
        "status": str(status),
        "retcode": retcode,
        "data": data,
        'echo': str(echo_id)
    }


class QueryParams:
    method = 'GET'

    def __init__(self, query_string):
        self.query_params = query_string

    @property
    def query(self):
        return self.query_params

    def get(self, key, default=None):
        print(key, self.query_params.get(key, default))
        return self.query_params.get(key, default)


async def api_message(message, ws):
    message = json.loads(message)
    if message['action'] in onebot_v11_api_list:
        data = await onebot_v11_api_list[message['action']](QueryParams(message['params']))
        try:
            data = json.loads(data.text)
        except:
            logger.error(f"[onebot|v11|API] 调用 {message['action']} 产生错误 携带参数：{message['params']}")
            return
        logger.info(f"[onebot|v11|API] {message['action']} 被调用")
        if str(data['retcode'])[:1] == "4":
            data['retcode'] = int('1' + str(data['retcode']))
        await ws.send_json(return_data(data['data'], data['status'], data['retcode'], message['echo']))
    else:
        await ws.send_json(return_data(None, 'failed', 1404, message['echo']))

async def return_event_message(item):
    try:
        message_id = int(item[1].message_id)
    except ValueError:
        message_id = uid2hex(item[1].message_id)
    except:
        pass

    if item[0] == "room_message":
        return {
                "message_type": "group",
                "sub_type": "normal",
                "message_id": message_id,
                "group_id": uid2hex(GlobalVal.now_room_id),
                "user_id": uid2hex(item[1].user_id),
                "anonymous": None,
                "message": await text2array(item[1].message),
                "raw_message": str(item[1].message),
                "font": 456,
                "sender": {
                    "user_id": uid2hex(item[1].user_id),
                    "nickname": item[1].user_name,
                    "sex": "unknown",
                    "age": "18",
                },
            }
    elif item[0] == "private_message":
        return {
                "message_type": "private",
                "sub_type": "friend",
                "message_id": message_id,
                "group_id": uid2hex(GlobalVal.now_room_id),
                "user_id": uid2hex(item[1].user_id),
                "message": await text2array(item[1].message),
                "raw_message": str(item[1].message),
                "font": 456,
                "sender": {
                    "user_id": uid2hex(item[1].user_id),
                    "nickname": item[1].user_name,
                    "sex": "unknown",
                    "age": "18",
                },
            }