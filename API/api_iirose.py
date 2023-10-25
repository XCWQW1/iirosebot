import json
from loguru import logger
import random
import traceback
from typing import Union

import aiohttp
import requests

from globals.globals import GlobalVal
from API.api_load_config import load_config
from ws_iirose.transfer_plugin import MessageType


class APIIirose:
    def __int__(self):
        pass

    @staticmethod
    async def send_msg_to_room(msg: str, color: int = 0):
        """
        发送消息到房间
        :param msg:  要发送的消息
        :param color:  要发送消息的背景色
        :return:
        """
        await GlobalVal.websocket.send(json.dumps({"m": msg, "mc": color, "i": str(random.random())[2:14]}))
        return {"code": 200}

    @staticmethod
    async def send_msg_to_private(msg: str, user_id: str, color: int = 0):
        """
        发送消息到私聊
        :param user_id: 要发送私聊消息到的用户唯一标识
        :param msg:  要发送的消息
        :param color:  要发送消息的背景色
        :return:
        """
        await GlobalVal.websocket.send(
            json.dumps({"g": user_id, "m": msg, "mc": color, "i": str(random.random())[2:14]}))
        return {"code": 200}

    @staticmethod
    async def send_msg(data, msg: str, color: int = 0):
        """
        自动选择发送到的位置
        :param data:  输入函数中第一个参数
        :param msg:  要发送的消息
        :param color:  要发送消息的背景色
        :return:
        """
        if data.type == MessageType.room_chat or MessageType.join_room or MessageType.leave_room:
            await APIIirose.send_msg_to_room(msg, color)
        elif data.type == MessageType.private_chat:
            await APIIirose.send_msg_to_private(msg, data.user_id, color)
        else:
            return {"code": 404, "error": "未知的类型"}
        return {"code": 200}

    @staticmethod
    async def move_room(room_id: str):
        """
        移动到指定的房间
        :param room_id:  目标房间id
        :return:
        """
        if GlobalVal.room_id is None:
            bot_name, c_room_id, bot_password = load_config()
        else:
            c_room_id = GlobalVal.room_id
        if room_id == c_room_id:
            logger.error('移动房间失败，原因：目标访问为当前所在房间')
            return {"code": 500, "error": "移动房间失败，原因：目标访问为当前所在房间"}
        GlobalVal.room_id = room_id
        GlobalVal.move_room = True
        await GlobalVal.websocket.send(f'm{room_id}')
        return {"code": 200}

    @staticmethod
    async def upload_files(file_name: Union[str, bytes]):
        """
        上传文件
        :param file_name:  # 输入str类 则文件精准路径会自动转换为二进制，输入bytes会直接发送，方便图片渲染等直接发送二进制
        :return:  # 成功后返回文件直连在json的url键下
        """

        try:
            if type(file_name) == str:
                files = {'f[]': open(file_name, 'rb')}
            else:
                files = {'f[]': (file_name, 'image/png')}

            response = requests.post('https://xc.null.red:8043/XCimg/upload_cache', files=files)
        except AttributeError:
            return {"code": 404, "error": "错误，获取不到文件", "url": None}
        except:
            return {"code": 404, "error": "错误，访问接口失败", "url": None}
        if response.status_code == 200:
            return {"code": 200, "url": f'https://xc.null.red:8043/XCimg/img/{response.text}'}

    @staticmethod
    async def like(user_id: str, message: str = ''):
        """
        给某人点赞
        :param message:  点赞的备注 可不写
        :param user_id:  目标人物唯一标识
        :return:
        """
        await GlobalVal.websocket.send(f'+*{user_id} {message}')
        return {"code": 200}

    @staticmethod
    async def play_media(media_type: bool):
        if media_type:
            # music
            media_type = 0
        else:
            # video
            media_type = 1
        card_json = {
            "m": f"m__4={media_type}"
                 f">>XCWQW233"
                 f">https://static.codemao.cn/rose/v0/images/system/demandAlbumLarge.png",
            "mc": "0",
            "i": str(random.random())[2:14]
        }

        media_json = {
            "s": "",
            "d": 1420.16,
            "c": "s://static.codemao.cn/rose/v0/images/system/demandAlbumLarge.png",
            "n": "",
            "r": "XCWQW233",
            "b": "=1"
        }
        return {"code": 200}

    @staticmethod
    async def stop_media():
        await GlobalVal.websocket.send('{0' + json.dumps({"m": "cut", "mc": "0", "i": str(random.random())[2:14]}))
        return {"code": 200}
