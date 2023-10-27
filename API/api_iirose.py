import json
import subprocess

from loguru import logger
import random
from typing import Union

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
    async def send_msg_to_danmu(msg: str, color: int = 0):
        """
        发送消息到私聊~{"t":"[https://xc.null.red:8043/XCimg/img/save/E4A1F509115D8BE947EA7CAA0395E1CA-2067967008.jpg#e]","c":"236614","v":0}
        :param msg:  要发送的消息
        :param color:  要发送消息的背景色
        :return:
        """
        await GlobalVal.websocket.send('~' + json.dumps({"t": msg, "c": color}))
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
        elif data.type == MessageType.danmu:
            await APIIirose.send_msg_to_danmu(msg, color)
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
    async def play_media(data, media_type: bool, media_url: str):
        """
        播放媒体，需要依赖ffmpeg获取视频长度
        :param data:  函数的第一个输入参数
        :param media_type:  媒体类型 True 为音频 False 为视频
        :param media_url:  媒体外链
        :return:
        """
        if media_type:
            # music
            media_type = 0
        else:
            # video
            media_type = 1

        try:
            command = ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', '-show_streams', media_url]
            result = subprocess.run(command, capture_output=True, text=True)
            output = result.stdout
            media_data = json.loads(output)
            duration = float(media_data['format']['duration'])
        except:
            return {"code": 403, "error": "无法访问到媒体"}

        card_json = {
            "m": f"m__4={media_type}"
                 f">>{data.user_name}"
                 f">https://static.codemao.cn/rose/v0/images/system/demandAlbumLarge.png",
            "mc": "0",
            "i": str(random.random())[2:14]
        }

        if media_url[:5] == "https":
            media_url = media_url[4:]
        elif media_url[:5] == "http:":
            media_url = media_url[4:]

        media_json = {
            "s": media_url,
            "d": duration,
            "c": "s://static.codemao.cn/rose/v0/images/system/demandAlbumLarge.png",
            "n": "媒体",
            "r": data.user_name,
            "b": f"={media_type}"
        }

        await GlobalVal.websocket.send(json.dumps(card_json))
        await GlobalVal.websocket.send('&1' + json.dumps(media_json))

        return {"code": 200}

    @staticmethod
    async def stop_media():
        await GlobalVal.websocket.send('{0' + json.dumps({"m": "cut", "mc": "0", "i": str(random.random())[2:14]}))
        return {"code": 200}

    @staticmethod
    async def revoke_message(message_id: str):
        await GlobalVal.websocket.send(f'v0#{message_id}')
        return {"code": 200}
