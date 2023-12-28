import json
import subprocess
from enum import Enum

from loguru import logger
import random
from typing import Union

import requests

from globals.globals import GlobalVal
from API.api_load_config import load_config
from ws_iirose.transfer_plugin import MessageType


class PlatformType(Enum):
    no_platform = 0
    netease = 1
    qq = 2
    kugou = 3


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
        if data.type in [MessageType.room_chat, MessageType.join_room, MessageType.leave_room]:
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
    async def play_media(media_type: bool,
                         media_url: str,
                         send_card: bool = True,
                         platform_type: PlatformType = PlatformType.no_platform,
                         music_name: str = '未知',
                         music_auther: str = '未知',
                         music_lrc: str = '未知',
                         music_pic: str = 'https://static.codemao.cn/rose/v0/images/system/demandAlbumLarge.png',
                         music_song_id: str = '',
                         media_time: int = None,
                         music_br=128):
        """
        播放媒体，需要依赖ffmpeg获取视频长度，为网易云音乐时可以通过music开头的几个变量自定义内容，如果提供了媒体时长可不依赖ffmpeg
        :param music_br: 音乐码率
        :param media_time:  媒体时长
        :param send_card: 是否发送卡片消息
        :param platform_type: 平台类型，需导入 PlatformType Enum进行选择 输入后music开头的参数歌曲id为必填
        :param music_song_id: 歌曲id
        :param music_pic: 音乐封面
        :param music_lrc: 音乐歌词
        :param music_auther: 音乐作者
        :param music_name: 音乐名称
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
        if media_time is None:
            try:
                command = ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', '-show_streams',
                           media_url]
                result = subprocess.run(command, capture_output=True, text=True)
                output = result.stdout
                media_data = json.loads(output)
                duration = float(media_data['format']['duration'])
            except:
                return {"code": 403,
                        "error": "无法访问到媒体或无法调用ffprobe,请检查媒体是否正确以及ffmpeg是否安装并且环境变量配置正确"}
        else:
            duration = media_time
        if platform_type == PlatformType.netease:
            card_json = {
                "m": f"m__4@0"
                     f">{music_name}>{music_auther}"
                     f">{music_pic}"
                     f">0c0a15>{music_br}",
                "mc": "0",
                "i": str(random.random())[2:14]
            }
        elif platform_type == PlatformType.qq:
            card_json = {
                "m": f"m__4@2"
                     f">{music_name}>{music_auther}"
                     f">{music_pic}"
                     f">0c0a15>{music_br}",
                "mc": "0",
                "i": str(random.random())[2:14]
            }
        elif platform_type == PlatformType.kugou:
            card_json = {
                "m": f"m__4@4"
                     f">{music_name}>{music_auther}"
                     f">{music_pic}"
                     f">0c0a15>{music_br}",
                "mc": "0",
                "i": str(random.random())[2:14]
            }
        elif platform_type == PlatformType.no_platform:
            card_json = {
                "m": f"m__4={media_type}"
                     f">>{music_auther}"
                     f">https://static.codemao.cn/rose/v0/images/system/demandAlbumLarge.png",
                "mc": "0",
                "i": str(random.random())[2:14]
            }

        if media_url[:5] == "https":
            media_url = media_url[4:]
        elif media_url[:5] == "http:":
            media_url = media_url[4:]

        if music_pic[:5] == "https":
            music_pic = music_pic[4:]
        elif music_pic[:5] == "http:":
            music_pic = music_pic[4:]

        if platform_type == PlatformType.netease:
            media_json = {
                "s": media_url,
                "d": duration,
                "c": music_pic,
                "n": music_name,
                "r": music_auther,
                "b": "@0",
                "o": f's://music.163.com/#/song?id={music_song_id}',
                "l": music_lrc
            }
        if platform_type == PlatformType.qq:
            media_json = {
                "s": media_url,
                "d": duration,
                "c": music_pic,
                "n": music_name,
                "r": music_auther,
                "b": "@2",
                "o": f's://y.qq.com/n/ryqq/songDetail/{music_song_id}',
                "l": music_lrc
            }
        if platform_type == PlatformType.kugou:
            media_json = {
                "s": media_url,
                "d": duration,
                "c": music_pic,
                "n": music_name,
                "r": music_auther,
                "b": "@4",
                "o": f's://www.kugou.com/song/#hash={music_song_id}',
                "l": music_lrc
            }
        elif platform_type == PlatformType.no_platform:
            media_json = {
                "s": media_url,
                "d": duration,
                "c": music_pic,
                "n": music_name,
                "r": music_auther,
                "b": f"={media_type}"
            }

        if send_card:
            await GlobalVal.websocket.send(json.dumps(card_json))
        await GlobalVal.websocket.send('&1' + json.dumps(media_json))

        return {"code": 200, 'duration': duration}

    @staticmethod
    async def stop_media():
        await GlobalVal.websocket.send('{0' + json.dumps({"m": "cut", "mc": "0", "i": str(random.random())[2:14]}))
        return {"code": 200}

    @staticmethod
    async def revoke_message(message_id: str):
        await GlobalVal.websocket.send(f'v0#{message_id}')
        return {"code": 200}

    @staticmethod
    async def update_share():
        await GlobalVal.websocket.send(f'>#')

    @staticmethod
    async def buy_share(num: int):
        await GlobalVal.websocket.send(f'>${num}')

    @staticmethod
    async def sell_share(num: int):
        await GlobalVal.websocket.send(f'>@{num}')
