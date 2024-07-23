import hmac
import json
import time
import asyncio

import requests

from loguru import logger
from iirosebot.utools import uid2hex
from requests import RequestException
from iirosebot.globals import GlobalVal
from iirosebot.utools.serve import generate_signature
from iirosebot.utools.serve.array_message import text2array
from iirosebot.API.api_get_config import get_token, get_serve, get_bot_id, get_heartbeat

wh_queue = asyncio.Queue()


def send_data(data: json, post_type: str) -> None:
    send_data = {
        "time": int(time.time()),
        "self_id": uid2hex(get_bot_id()),
        "post_type": post_type,
    }

    send_data = json.dumps({**send_data, **data}, separators=(',', ':'), ensure_ascii=False)

    headers = {
        "Content-Type": "application/json",
        "x-self-id": str(uid2hex(get_bot_id()))
    }

    if get_serve()['webhook']['verify']:
        generated_hmac = generate_signature(get_token(), send_data)

        headers['x-signature'] = f"sha1={generated_hmac}"

    try:
        logger.debug('[WEBHOOK] POST 请求 {} 请求头 {} 内容 {}'.format(get_serve()['webhook']['url'], headers, send_data))
        data = requests.post(get_serve()['webhook']['url'], data=send_data, headers=headers, timeout=get_serve()['webhook']['time_out'])
        if str(data.status_code)[:1] != '2' and str(data.status_code) != "404":
            logger.error('[WEBHOOK] 访问 {} 出错，状态为 {} 返回 {}'.format(get_serve()['webhook']['url'], data.status_code, data.text))
    except RequestException as e:
        logger.error('[WEBHOOK] 访问 {} 出错 {}'.format(get_serve()['webhook']['url'], e))


async def start_webhook(url: str, timeout: int) -> None:
    logger.info('WEBHOOK 已启用')

    send_data(
        {
            "meta_event_type": "lifecycle",
            "sub_type": "enable"
        },
        'meta_event'
    )

    while True:
        item = await wh_queue.get()

        try:
            message_id = int(item[1].message_id)
        except ValueError:
            message_id = uid2hex(item[1].message_id)
        except:
            pass

        if item[0] == "room_message":
            send_data(
                {
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
                },
                'message'
            )
        elif item[0] == "private_message":
            send_data(
                {
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
                },
                'message'
            )


async def start_heartbeat():
    if get_heartbeat()['enabled']:
        while True:
            send_data(
                {
                    "meta_event_type": "heartbeat",
                    "sub_type": "enable",
                    "status": {"online": True, "good": True},
                    "interval": get_heartbeat()['interval'],
                },
                'meta_event'
            )
            await asyncio.sleep(get_heartbeat()['interval'] / 1000.0)
