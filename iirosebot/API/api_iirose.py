"""
常用接口
"""
import io
import json
import html
import random
import traceback

import requests
import subprocess

from enum import Enum
from typing import Union
from loguru import logger

from iirosebot.exception import APIException
from iirosebot.globals.globals import GlobalVal
from iirosebot.API.decorator import MessageType
from iirosebot.API.api_load_config import load_config
from iirosebot.API.api_get_config import get_user_color


bot_name, _, _ = load_config()


class PlatformType(Enum):
    no_platform = 0
    netease = 1
    qq = 2
    kugou = 3
    bilibili_video = 4
    bilibili_live = 5


class APIIirose:
    def __int__(self):
        pass

    @staticmethod
    async def send_msg_to_room(msg: str, color: str = None):
        """
        发送消息到房间
        :param msg:  要发送的消息
        :param color:  要发送消息的背景色
        :return:
        """
        if color is None:
            color = get_user_color()
        msg_id = str(random.random())[2:14]
        await GlobalVal.websocket.send(json.dumps({"m": msg, "mc": str(color), "i": msg_id}))
        logger.info(f'[消息|房间|发送] {bot_name}：{msg} ({msg_id})')
        GlobalVal.send_message_cache['group'][msg_id] = {"message": msg}
        return msg_id

    @staticmethod
    async def send_msg_to_private(msg: str, user_id: str, color: str = None):
        """
        发送消息到私聊
        :param user_id: 要发送私聊消息到的用户唯一标识
        :param msg:  要发送的消息
        :param color:  要发送消息的背景色
        :return:
        """
        if color is None:
            color = get_user_color()
        msg_id = str(random.random())[2:14]
        await GlobalVal.websocket.send(json.dumps({"g": user_id, "m": msg, "mc": str(color), "i": msg_id}))
        logger.info(f'[消息|私聊|发送] {bot_name}：{msg} ({msg_id}) => {user_id}')
        GlobalVal.send_message_cache['private'][msg_id] = {"message": msg, "user_id": user_id}
        return msg_id

    @staticmethod
    async def send_msg_to_danmu(msg: str, color: str = None):
        """
        发送消息到弹幕
        :param msg:  要发送的消息
        :param color:  要发送消息的背景色
        :return:
        """
        if color is None:
            color = get_user_color()
        await GlobalVal.websocket.send('~' + json.dumps({"t": msg, "c": str(color)}))
        logger.info(f'[消息|弹幕|发送] {bot_name}：{msg}')
        return None

    @staticmethod
    async def send_msg_to_forum(msg: str, color: str = None, replyId: str = None):
        """
        发送消息到论坛  非认证用户无法发送
        :param msg:  要发送的消息
        :param color:  消息的颜色十六进至
        :param replyId:  回复消息的id
        """
        if color is None:
            color = get_user_color()
        await GlobalVal.websocket.send(':-' + json.dumps({"t": f"{color}{'[@' + str(replyId) + ']' if replyId else ''}{msg}", "r": str(random.random())[2:15]}))
        logger.info(f'[消息|论坛|发送] {bot_name}：{msg}')

    @staticmethod
    async def send_msg(data, msg: str, color: str = None):
        """
        自动选择发送到的位置
        :param data:  输入函数中第一个参数
        :param msg:  要发送的消息
        :param color:  要发送消息的背景色
        :return:
        """
        if color is None:
            color = get_user_color()
        if data.type in [MessageType.room_chat, MessageType.join_room, MessageType.leave_room]:
            msg_id = await APIIirose.send_msg_to_room(msg, str(color))
        elif data.type == MessageType.private_chat:
            msg_id = await APIIirose.send_msg_to_private(msg, data.user_id, str(color))
        elif data.type == MessageType.danmu:
            msg_id = await APIIirose.send_msg_to_danmu(msg, str(color))
        else:
            raise APIException("未知的类型")
        return msg_id

    @staticmethod
    async def replay_msg(data, msg: str, color: str = None):
        """
        引用消息
        :param data: 输入函数的第一个参数
        :param msg: 消息内容
        :param color: 引用消息颜色
        :return:
        """
        if color is None:
            color = get_user_color()

        await GlobalVal.websocket.send(json.dumps({"m": f"{data.message} (_hr) {data.user_name}_{data.timestamp} (hr_) {msg}", "mc": str(color), "i": str(random.random())[2:14]}))

    @staticmethod
    async def move_room(room_id: str, password: str = None):
        """
        移动到指定的房间
        :param room_id:  目标房间id
        :param password: 目标房间密码，目标房间有密码的情况下需带此参数
        :return:
        """
        if password is not None:
            password = html.escape(password)
            GlobalVal.room_password = password
            await GlobalVal.websocket.send(f'=^~{room_id}>{password}')
        else:
            with open("config/room.json", 'r', encoding='utf-8') as file:
                room_config = json.load(file)
            if room_id in room_config:
                password = room_config[room_id]
        GlobalVal.old_room_id = GlobalVal.now_room_id
        if GlobalVal.room_id is None:
            _, c_room_id, _ = load_config()
        else:
            c_room_id = GlobalVal.room_id
        if room_id == c_room_id:
            logger.error('移动房间失败，原因：目标访问为当前所在房间')
            raise APIException("移动房间失败，原因：目标访问为当前所在房间")
        GlobalVal.room_id = room_id
        GlobalVal.move_room = True
        if password is not None:
            await GlobalVal.websocket.send(f'm{room_id}>{password}')
        else:
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
            if type(file_name) is str:
                files = {'f[]': open(file_name, 'rb')}
            else:
                files = {'f[]': ('bytes.png', file_name, 'image/png')}

            response = requests.post('https://xc.null.red:8043/XCimg/upload', files=files)
        except AttributeError:
            raise APIException("错误，获取不到文件")
        except:
            raise APIException("错误，访问接口失败\n" + traceback.format_exc())
        if response.status_code == 200:
            return {"url": f'https://xc.null.red:8043/XCimg/img/{response.text}'}

    @staticmethod
    async def like(user_id: str, message: str = None):
        """
        给某人点赞
        :param message:  点赞的备注 可不写
        :param user_id:  目标人物唯一标识
        :return:
        """
        await GlobalVal.websocket.send(f'+*{user_id}{"" if message is None else " " + message}')
        logger.info(f'[事件|点赞] 目标用户：{user_id} {"" if message is None else "留言：" + message}')
        return {"code": 200}

    @staticmethod
    async def subscription(user_id: str):
        """
        关注某人
        :param user_id:  目标人物唯一标识
        :return:
        """
        await GlobalVal.websocket.send(f'+#0{user_id}')
        logger.info(f'[事件|关注] 目标用户：{user_id}')
        return {"code": 200}

    @staticmethod
    async def unsubscription(user_id: str):
        """
        取消关注某人
        :param user_id:  目标人物唯一标识
        :return:
        """
        await GlobalVal.websocket.send(f'+#1{user_id}')
        logger.info(f'[事件|取关] 目标用户：{user_id}')
        return {"code": 200}

    @staticmethod
    async def play_media(
            media_type: bool,
            media_url: str,
            send_card: bool = True,
            platform_type: PlatformType = PlatformType.no_platform,
            media_name: str = '未知',
            media_auther: str = '未知',
            media_lrc: str = '未知',
            media_pic: str = 'https://static.codemao.cn/rose/v0/images/system/demandAlbumLarge.png',
            music_song_id: str = '',
            media_time: int = None,
            media_audio: str = None,
            media_br=128,
            color: str = None
    ):
        """
        播放媒体，需要依赖ffmpeg获取视频长度，为网易云音乐时可以通过music开头的几个变量自定义内容，如果提供了媒体时长可不依赖ffmpeg
        :param color: 媒体卡片的颜色
        :param media_br: 音乐码率
        :param media_time:  媒体时长
        :param send_card: 是否发送卡片消息
        :param platform_type: 平台类型，需导入 PlatformType Enum进行选择 输入后music开头的参数歌曲id为必填
        :param music_song_id: 歌曲id
        :param media_pic: 音乐封面
        :param media_lrc: 音乐歌词
        :param media_auther: 音乐作者
        :param media_name: 音乐名称
        :param media_type:  媒体类型 True 为音频 False 为视频
        :param media_url:  媒体外链
        :param media_audio:  媒体音频地址，仅在bilibili平台起作用，视频地址填入media_url
        :return:
        """
        message_id = str(random.random())[2:14]

        if color is None:
            if media_pic:
                try:
                    from PIL import Image
                    import numpy as np
                    response = requests.get(media_pic, timeout=5)
                    image = Image.open(io.BytesIO(response.content))
                    image = image.convert("RGB")
                    pixels = np.array(image)
                    avg_color = tuple(map(int, np.mean(pixels, axis=(0, 1))))
                    color = '{:02x}{:02x}{:02x}'.format(*avg_color)
                except ModuleNotFoundError:
                    logger.warning('媒体卡片颜色获取失败，依赖库缺失')
                    color = get_user_color()
                except:
                    color = get_user_color()
            else:
                color = get_user_color()

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
                raise APIException("无法访问到媒体或无法调用ffprobe,请检查媒体是否正确以及ffmpeg是否安装并且环境变量配置正确")
        else:
            duration = media_time

        if not media_audio is None and platform_type == PlatformType.bilibili_video:
            if media_url.startswith("http"):
                media_url = media_url[4:] + "#audio=" + str(media_audio)
        else:
            if media_url.startswith("http"):
                media_url = media_url[4:]

        if media_pic.startswith("http"):
            media_pic = media_pic[4:]

        if platform_type == PlatformType.netease:
            media_json = {
                "s": media_url,
                "d": duration,
                "c": media_pic,
                "n": media_name,
                "r": media_auther,
                "b": "@0",
                "o": f's://music.163.com/#/song?id={music_song_id}',
                "l": media_lrc
            }
        if platform_type == PlatformType.qq:
            media_json = {
                "s": media_url,
                "d": duration,
                "c": media_pic,
                "n": media_name,
                "r": media_auther,
                "b": "@2",
                "o": f's://y.qq.com/n/ryqq/songDetail/{music_song_id}',
                "l": media_lrc
            }
        if platform_type == PlatformType.kugou:
            media_json = {
                "s": media_url,
                "d": duration,
                "c": media_pic,
                "n": media_name,
                "r": media_auther,
                "b": "@4",
                "o": f's://www.kugou.com/song/#hash={music_song_id}',
                "l": media_lrc
            }
        elif platform_type == PlatformType.bilibili_video:
            media_json = {
                "s": media_url,
                "d": duration,
                "c": media_pic,
                "n": media_name,
                "r": media_auther,
                "b": f"!3"
            }
        elif platform_type == PlatformType.bilibili_live:
            media_json = {
                "s": media_url,
                "d": duration,
                "c": media_pic,
                "n": media_name,
                "r": media_auther,
                "b": f"!8"
            }
        elif platform_type == PlatformType.no_platform:
            media_json = {
                "s": media_url,
                "d": duration,
                "c": media_pic,
                "n": media_name,
                "r": media_auther,
                "b": f"={media_type}"
            }

        media_name = html.escape(media_name)
        media_auther = html.escape(media_auther)
        media_url = html.escape(media_url)
        color = html.escape(color)
        media_pic = 'http' + media_pic

        if platform_type == PlatformType.netease:
            card_json = {
                "m": f"m__4@0"
                     f">{media_name}>{media_auther}"
                     f">{media_pic}"
                     f">{color}>{media_br}",
                "mc": color,
                "i": message_id
            }
        elif platform_type == PlatformType.qq:
            card_json = {
                "m": f"m__4@2"
                     f">{media_name}>{media_auther}"
                     f">{media_pic}"
                     f">{color}>{media_br}",
                "mc": color,
                "i": message_id
            }
        elif platform_type == PlatformType.kugou:
            card_json = {
                "m": f"m__4@4"
                     f">{media_name}>{media_auther}"
                     f">{media_pic}"
                     f">{color}>{media_br}",
                "mc": color,
                "i": message_id
            }
        elif platform_type == PlatformType.bilibili_video:
            minutes = int(media_time) // 60
            seconds = int(media_time) % 60
            time_format = f"{minutes}:{seconds:02d}"
            card_json = {
                "m": f"m__4*3"
                     f">{media_name}>{media_auther}"
                     f">{media_pic}>{color}>>{media_br}>>{time_format}",
                "mc": color,
                "i": message_id
            }
        elif platform_type == PlatformType.bilibili_live:
            minutes = int(media_time) // 60
            seconds = int(media_time) % 60
            time_format = f"{minutes}:{seconds:02d}"
            if media_br >= 10000:
                media_br = str(media_br)[:1] + 'e4'
            card_json = {
                "m": f"m__4*8"
                     f">{media_name}>{media_auther}"
                     f">{media_pic}>{color}>>{media_br}>>{time_format}",
                "mc": color,
                "i": message_id
            }
        elif platform_type == PlatformType.no_platform:
            card_json = {
                "m": f"m__4={media_type}"
                     f">{media_name}>{media_auther}"
                     f">{media_pic}",
                "mc": color,
                "i": message_id
            }
        else:
            raise APIException('不支持的平台')

        if send_card:
            await GlobalVal.websocket.send(json.dumps(card_json))
        else:
            message_id = None
        room_info = await APIIirose.get_room_info(GlobalVal.now_room_id)

        try:
            room_info = room_info['properties']
        except:
            room_info = None

        if room_info is None or room_info == 'video_share':
            media_type = '&1'
        else:
            media_type = '&0'

        await GlobalVal.websocket.send(media_type + json.dumps(media_json, ensure_ascii=False))

        return {'duration': float(duration), 'message_id': message_id}

    @staticmethod
    async def stop_media(text: str = 'cut', color: str = None):
        """
        投票切歌
        :param text:  消息内容
        :param color:  消息颜色
        :return:
        """
        if color is None:
            color = get_user_color()
        await GlobalVal.websocket.send('{0' + json.dumps({"m": text, "mc": color, "i": str(random.random())[2:14]}))

    @staticmethod
    async def revoke_message(message_id: str, user_id: str = None):
        """
        撤回消息
        :param message_id:  消息id
        :param user_id:  私聊用户的id，不提供按房间消息走
        :return:
        """
        if user_id is None:
            await GlobalVal.websocket.send(f'v0#{message_id}')
        else:
            await GlobalVal.websocket.send(f'v0*{user_id}#{message_id}')
            print(f'v0*{user_id}#{message_id}')

    @staticmethod
    async def update_share():
        """
        重新获取当前股价
        :return:
        """
        await GlobalVal.websocket.send('>#')

    @staticmethod
    async def buy_share(num: int):
        """
        购买股票
        :return:
        """
        await GlobalVal.websocket.send(f'>${num}')

    @staticmethod
    async def sell_share(num: int):
        """
        卖出股票
        :return:
        """
        await GlobalVal.websocket.send(f'>@{num}')

    @staticmethod
    async def get_room_info(room_id: str = None, room_name: str = None) -> json:
        try:
            data = GlobalVal.iirose_date['room'][room_id]
            return data
        except:
            return {}

    @staticmethod
    async def get_user_info(user_id: str = None, user_name: str = None) -> json:
        try:
            data = GlobalVal.iirose_date['user'][user_id]
            return data
        except:
            return {}

    @staticmethod
    async def get_playlist():
        await GlobalVal.websocket.send("%")
        raise APIException("获取歌单失败，原因：超时")

    @staticmethod
    async def send_notice(message: str):
        await GlobalVal.websocket.send(f'!!["{message}"]')

    @staticmethod
    async def send_kick(user_name: str):
        await GlobalVal.websocket.send(f'!#["{html.escape(user_name.lower())}"]')

    @staticmethod
    async def send_ban(user_name: str, duration: int, message: str = ""):
        await GlobalVal.websocket.send(f'!h3["41","{html.escape(user_name.lower())}","{duration}s","{message}"]')

    @staticmethod
    async def whole_ban(enable: bool):
        if enable:
            await GlobalVal.websocket.send("_~!4")
        else:
            await GlobalVal.websocket.send("_~!0")

    @staticmethod
    async def room_anonymous(enable: bool):
        if enable:
            await GlobalVal.websocket.send('!h7["10"]')
        else:
            await GlobalVal.websocket.send('!h7["1"]')


class BaseStation:
    def __int__(self):
        pass

    @staticmethod
    async def send(packageName: str, user_id: dict or list or str, msg: str):
        """
        由基站向用户发送消息
        :param packageName: 包名
        :param user_id: 用户唯一标识，可输入数组或列表用于群发，也可以只输入字符串单独发送
        :param msg: 要发送的内容
        """
        if type(user_id) is str:
            logger.info(f'[基站|发送] 包名：{packageName}, 内容：{msg}，目标：{user_id}')
            await GlobalVal.websocket.send("/<{}>{}:{}".format(packageName, user_id, msg))
        else:
            user_list = ""
            for i in user_id:
                user_list += i + ","
            logger.info(f'[基站|发送] 包名：{packageName}, 内容：{msg}，目标：{user_list}')
            await GlobalVal.websocket.send("/<{}>{}:{}".format(packageName, user_list[:-1], msg))

