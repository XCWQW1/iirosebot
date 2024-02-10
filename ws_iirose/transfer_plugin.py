import gzip
import html
import os
import re
import signal
import sys
import traceback

from loguru import logger

from API.decorator.command import function_records, MessageType
from globals.globals import GlobalVal
from plugin_system.plugin_transfer import plugin_transfer
from plugin_system.plugin_init import plugin_manage_data
from API.api_iirose import APIIirose


API = APIIirose()
gold = 0


def check_start_symbols(text):
    pattern = r'^(\W+)'  # 匹配一个或多个非单词字符（符号）开头
    matches = re.match(pattern, text)

    if matches:
        start_symbols = matches.group(1)  # 获取匹配到的开头符号
        return True, start_symbols
    else:
        return False, None


def replay_to_json(text):
    try:
        text = text.split(" (hr_) ")
        reply_list = []
        num = 0
        for i in text:
            data = i.split(" (_hr) ")

            if len(data) == 1:
                reply_list[len(reply_list) - 1]['reply'] = data[0]
                break

            user_data = data[1].split("_")
            if num == 0:
                reply_list.append({"message": data[0], "user_name": user_data[0], "timestamp": user_data[1]})
            else:
                reply_list[len(reply_list) - 1]['reply'] = data[0]
                reply_list.append({"message": data[0], "user_name": user_data[0], "timestamp": user_data[1]})
            num += 1
        return reply_list
    except:
        return []


async def pares_big(data):
    iirose_date = GlobalVal.iirose_date
    big_r = data.split("<")
    user_data_json = {}
    room_data_json = {}
    for i in big_r:
        if i[:1] != "%":
            match = re.search(r'\b([\da-f]{13}_[\da-f]{13})\b', i)
            if i[:8] == 'cartoon/':
                user_data = i.split('>')
                if user_data[8][:1] == 'X':
                    user_data = i.split(">")
                    if len(user_data) != 14:
                        continue
                    user_data_json[user_data[8]] = {
                        "id": user_data[8],
                        "name": user_data[2],
                        "pic": 'https://static.codemao.cn/rose/v0/images/icon/' + user_data[0] if user_data[0][-4:] == '.png' else 'https://static.codemao.cn/rose/v0/images/icon/' + user_data[0] + '.jpg',
                        "sex": user_data[1],
                        "color": user_data[3],
                        "introduction": None,
                        "room_id": user_data[4],
                        "tag": None,
                        "online_time": None,
                        "private_chat_background_image": None,
                        "status": user_data[11]
                    }
                    continue
            if match:
                room_data = i.split(">")
                if len(room_data) == 8:
                    room_id = room_data[0].split('_')[1]
                    room_name = room_data[1]
                    room_type = room_data[0].split('_')[0]
                    room_color = room_data[2]
                    room_p_data = room_data[3]

                    if int(room_p_data[:1]) == 0:
                        room_properties = None
                    elif int(room_p_data[:1]) == 1:
                        room_properties = 'music_share'
                    elif int(room_p_data[:1]) == 2:
                        room_properties = 'video_share'
                    elif int(room_p_data[:1]) == 3:
                        room_properties = 'music'
                    elif int(room_p_data[:1]) == 4:
                        room_properties = 'video'

                    if int(room_p_data[1:2]) == 1:
                        room_weather_environment_sound = True
                    else:
                        room_weather_environment_sound = False

                    if int(room_p_data[2:3]) == 1:
                        room_role_play = True
                    else:
                        room_role_play = False

                    if len(room_p_data) == 4:
                        if int(room_p_data[-1:]) == 0:
                            room_language = 'ALL'
                        elif int(room_p_data[-1:]) == 1:
                            room_language = 'JA'
                        elif int(room_p_data[-1:]) == 2:
                            room_language = 'EN'
                        elif int(room_p_data[-1:]) == 3:
                            room_language = 'ZH'
                        elif int(room_p_data[-1:]) == 4:
                            room_language = 'KO'
                        elif int(room_p_data[-1:]) == 5:
                            room_language = 'FA'
                        else:
                            room_language = None
                    else:
                        room_language = None

                    room_data = room_data[5].split("&&")
                    room_pic = room_data[0].split(' ')[0] if room_data[0][:3] in ['s:/', '://'] else None
                    room_pic = 'http' + room_pic if room_pic else None

                    room_introduction = room_data[0].split(' ', maxsplit=1)[1] if not \
                    room_data[0].split(' ', maxsplit=1)[1] == '' else None
                    room_created = room_data[1]
                    room_member = room_data[4].split(' & ') if room_data[4] != '' else None
                    room_photo_album = ['http' + url_p for url_p in room_data[7].split(' ')] if room_data[
                                                                                                    7] != '' else None

                    room_data = room_data[6].split(' ', maxsplit=1)
                    if len(room_data) >= 2:
                        room_music_url = room_data[0]
                        room_music_pic = room_data[1].split('@|')[0]
                        room_music_name = room_data[1].split('@|')[1]
                        room_music_auther = room_data[1].split('@|')[2]
                    else:
                        room_music_url = None
                        room_music_pic = None
                        room_music_name = None
                        room_music_auther = None

                    room_data_json[room_id] = {
                        "id": room_id,
                        "name": room_name,
                        "type": room_type,
                        "color": room_color,
                        "pic": room_pic,
                        "introduction": room_introduction,
                        "created": room_created,
                        "member": room_member,
                        "photo_album": room_photo_album,
                        "music_url": room_music_url,
                        "music_name": room_music_name,
                        "music_auther": room_music_auther,
                        "properties": room_properties,
                        "language": room_language,
                        "weather_environment_sound": room_weather_environment_sound,
                        "role_play": room_role_play
                    }
                    continue
            else:
                if i[:4] == 'http':
                    i = i.split('>')
                    if len(i) != 14:
                        continue

                    user_pic = i[0]
                    user_sex = i[1]
                    user_name = i[2]
                    user_color = i[3]
                    user_id = i[8]
                    user_introduction = i[6] if not i[6] == '' else None
                    user_room_id = i[4]
                    user_tag = i[12] if not i[12] == '' else None
                    user_online_time = i[13].replace("'", '')
                    user_private_chat_background_image = i[10] if not i[10] == '' else None
                    user_status = i[11]

                    if user_online_time == '':
                        user_online_time = 0
                    else:
                        user_online_time = int(re.sub(r"\D", "", user_online_time))

                    if user_status == '':
                        user_status = 0
                    elif user_status == 'a':
                        user_status = 12
                    elif user_status == '*':
                        user_status = 11

                    user_data_json[user_id] = {
                        "id": user_id,
                        "name": user_name,
                        "pic": user_pic,
                        "sex": user_sex,
                        "color": user_color,
                        "introduction": user_introduction,
                        "room_id": user_room_id,
                        "tag": user_tag,
                        "online_time": user_online_time,
                        "private_chat_background_image": user_private_chat_background_image,
                        "status": user_status
                    }
                    continue

    GlobalVal.iirose_date['room'] = room_data_json
    GlobalVal.iirose_date['user'] = user_data_json


async def process_message(data, websocket):
    global gold
    msg_list = []

    if data[0] == 1:
        data = gzip.decompress(data[1:]).decode('utf-8')
    else:
        data = data.decode("utf-8")

    split_list = data.split("<")

    async def login_error(data):
        if data[:3] == '%*"':
            try:
                error_code = int(data[3:])
                if error_code == 0:
                    logger.error('登陆失败：名字被占用')
                elif error_code == 1:
                    logger.error('登陆失败：用户不存在')
                elif error_code == 2:
                    logger.error('登陆失败：密码错误')
                elif error_code == 5:
                    logger.error('登陆失败：房间密码错误')
                    GlobalVal.now_room_id = GlobalVal.old_room_id
                    GlobalVal.room_id = GlobalVal.old_room_id
                    await GlobalVal.websocket.close()
                    return
                elif type(error_code) == int:
                    logger.error(f'登陆失败：未知错误代码：{error_code}，可能今日登陆次数到达上限')
                logger.error("已关闭程序，请检查配置文件")
                logger.info('框架已关闭')
                pid = os.getpid()
                if sys.platform == 'win32':
                    os.kill(pid, signal.CTRL_C_EVENT)
                else:
                    os.kill(pid, signal.SIGKILL)
                sys.exit(0)
            except:
                pass

    if len(split_list) <= 1:
        for i in split_list:
            if not i[:1] == "%":
                msg_list.append(i)
            else:
                await websocket.send(">#")
                await login_error(data)
                from ws_iirose.login_bot import init_plugin
                await init_plugin()
                await pares_big(data)
                await plugin_transfer('date_update')
    else:
        start_symbol_text = None
        if not data[:1] == "%":
            for s_list in split_list:
                symbols_bool, symbols_string = check_start_symbols(s_list)
                if symbols_bool:
                    start_symbol_text = symbols_string
                    msg_list.append(s_list)
                else:
                    try:
                        msg_list.append(start_symbol_text + s_list)
                    except:
                        msg_list.append(s_list)
        else:
            await websocket.send(">#")
            await login_error(data)
            from ws_iirose.login_bot import init_plugin
            await init_plugin()
            await pares_big(data)
            await plugin_transfer('date_update')

    for data in reversed(msg_list):
        if data == 'm':
            logger.info(f'[事件|移动] 切换房间')
            await websocket.close()
            return
        else:
            if data[:2] == '-*':
                # 其他端移动房间 需同时移动
                logger.info(f'[事件|移动] 收到移动事件，正在前往 {data[2:]}')
                await API.move_room(data[2:])
                await websocket.close()
                return
            if data == ',':
                # 切媒体
                logger.info(f'[事件|媒体] 切媒体')
                await plugin_transfer('media_cut')
                return

            if data[:1] == ">":
                msg = data[1:].split('"')
                if len(msg) != 5:
                    return

                class Data:
                    price_share = float(msg[2])
                    old_price_share = float(gold)
                    total_share = int(msg[0])
                    total_money = float(msg[1])
                    hold_share = float(msg[3]) if msg[3] != '' else 0
                    hold_money = float(msg[4])

                if Data.price_share == 1.0:
                    logger.info(f'[事件|股票] 股票崩盘')
                    await plugin_transfer('share_jump', Data)
                if Data.price_share != gold:
                    gold = Data.price_share
                    logger.info(f'[事件|股票] 股价：{Data.price_share} 钞/股，总股: {Data.total_share}，总金: {Data.total_money}，持股: {Data.hold_share}，余额: {Data.hold_money}')
                    await plugin_transfer('share_message', Data)
                return

            if data[:1] == '"':
                msg_type = data.count('"', 0, len(data))
                msg = data.split(">")

                if msg_type == 1:
                    # 房间消息
                    if len(msg) == 11:
                        # 纯文本类
                        class Message:
                            type = MessageType.room_chat
                            timestamp = msg[0][1:]
                            user_pic = msg[1]
                            user_name = html.unescape(msg[2])
                            user_id = msg[8]
                            message = html.unescape(msg[3])
                            message_id = msg[10]
                            message_color = msg[4]
                            message_background_color = msg[5]
                            is_bot = True if msg[9][:2] == "4'" else False
                            is_replay = False

                        if Message.message[:4] == 'm__4':
                            msg = Message.message.split('>')

                            class Media:
                                media_name = msg[1]
                                media_auther = msg[2]
                                media_pic = msg[3]

                            logger.info(f'[事件|媒体|点播] {Message.user_name} 点播来自 {Media.media_auther} 的 {Media.media_name}')
                            await plugin_transfer('play_media', (Message, Media))
                            return

                        replay_data = replay_to_json(Message.message)
                        if replay_data:
                            Message.message = replay_data
                            Message.is_replay = True

                        logger.info(f'[消息|房间] {Message.user_name}({Message.user_id}): {Message.message} ({Message.message_id})')
                        await plugin_transfer('room_message', Message)

                    elif len(msg) == 12:
                        # 事件类
                        # 移动到其他房间
                        if msg[3][:2] == "'2":
                            class Message:
                                type = MessageType.move_room
                                timestamp = msg[0][1:]
                                user_pic = msg[1]
                                user_name = msg[2]
                                user_id = msg[8]
                                color = msg[5]
                                to_room_id = msg[11][1:]
                                is_bot = True if msg[9][:2] == "4'" else False

                            logger.info(f'[事件|移动到其他房间] {Message.user_name}({Message.user_id}) => {Message.to_room_id}')
                            await plugin_transfer('user_move_room', Message)
                            continue

                        elif msg[3] == "'1":
                            # 用户加入房间
                            class Message:
                                type = MessageType.join_room
                                timestamp = msg[0][1:]
                                user_pic = msg[1]
                                user_name = msg[2]
                                user_id = msg[8]
                                color = msg[5]
                                is_bot = True if msg[9][:2] == "4'" else False

                            logger.info(f'[事件|用户加入房间] {Message.user_name}({Message.user_id})')
                            await plugin_transfer('user_join_room', Message)
                            continue

                        elif msg[3] == "'3":
                            # 用户离开房间
                            class Message:
                                type = MessageType.leave_room
                                timestamp = msg[0][1:]
                                user_pic = msg[1]
                                user_name = msg[2]
                                user_id = msg[8]
                                color = msg[5]
                                is_bot = True if msg[9][:2] == "4'" else False

                            logger.info(f'[事件|用户离开房间] {Message.user_name}({Message.user_id})')
                            await plugin_transfer('user_leave_room', Message)
                            continue

                elif msg_type == 2:
                    # 私聊消息
                    class Message:
                        type = MessageType.private_chat
                        timestamp = msg[0][1:]
                        user_id = msg[1]
                        user_name = html.unescape(msg[2])
                        user_pic = msg[3]
                        message = html.unescape(msg[4])
                        message_id = msg[10]
                        message_color = msg[5]
                        message_background_color = msg[6]
                        is_bot = True if msg[9][:2] == "4'" else False
                        is_replay = False

                    replay_data = replay_to_json(Message.message)
                    if replay_data:
                        Message.message = replay_data
                        Message.is_replay = True

                    logger.info(f'[消息|私聊] {Message.user_name}({Message.user_id}): {Message.message} ({Message.message_id})')
                    await plugin_transfer('private_message', Message)

            elif data[:1] == '=':
                msg_type = data.count('=', 0, len(data))
                msg = data.split(">")

                # 弹幕消息
                class Message:
                    type = MessageType.danmu
                    user_id = msg[6]
                    user_name = html.unescape(msg[0][1:])
                    user_title = html.unescape(msg[8])
                    user_pic = msg[5]
                    message = html.unescape(msg[1])
                    message_color = msg[2]
                    message_background_color = msg[3]
                    is_bot = True if msg[9][:2] == "4'" else False

                logger.info(f'[消息|弹幕] {Message.user_name}({Message.user_id}): {Message.message}')
                await plugin_transfer('danmu_message', Message)

            elif data[:3] == 'v0#':
                # 撤回消息
                msg = data.split("#")[1].split("_")

                class Message:
                    type = MessageType.revoke_message
                    user_id = msg[0]
                    message_id = msg[1]

                logger.info(f'[事件|撤回] 用户 {Message.user_id} 撤回了 {Message.message_id}')
                await plugin_transfer('revoke_message', Message)
                continue

            elif data[:2] == '&1':
                msg = data.split(">")

                def iirose_url_parse(iirose_url):
                    if iirose_url[2:6] == 's://':
                        iirose_media_url = 'http' + iirose_url[2:]
                    elif iirose_url[2:5] == '://':
                        iirose_media_url = 'http' + iirose_url[2:]
                    else:
                        iirose_media_url = iirose_url[2:]
                    return iirose_media_url

                if msg[5] == '2':
                    # video
                    class Message:
                        type = MessageType.media_video
                        play_user = msg[4]
                        media_name = msg[2][:-2]
                        media_auther = msg[3]
                        media_url = iirose_url_parse(msg[0])
                        media_pic_url = iirose_url_parse(msg[6])
                        media_time = msg[1]

                    logger.info(f'[事件|媒体|视频] 由 {Message.play_user} 播放来自 {Message.media_auther} 的 {Message.media_name}，地址是{Message.media_url}')
                    await plugin_transfer('media_video_message', Message)
                    await plugin_transfer('media_message', Message)
                    continue

                if msg[5] == '1':
                    # music
                    class Message:
                        type = MessageType.media_music
                        play_user = msg[4]
                        media_name = msg[2]
                        media_auther = msg[3][2:]
                        media_url = iirose_url_parse(msg[0])
                        media_pic_url = iirose_url_parse(msg[6])
                        media_time = msg[1]

                    logger.info(f'[事件|媒体|音频] 由 {Message.play_user} 播放来自 {Message.media_auther} 的 {Message.media_name}，地址是 {Message.media_url}')
                    await plugin_transfer('media_music_message', Message)
                    await plugin_transfer('media_message', Message)
                    continue
            elif data[:2] == '`~':
                try:
                    data = int(data[2:])
                    if data == 1:
                        logger.info(f'[事件|房间|移动] 密码正确')
                    else:
                        GlobalVal.now_room_id = GlobalVal.old_room_id
                        GlobalVal.room_id = GlobalVal.old_room_id
                        logger.error(f'[事件|房间|移动] 密码错误')
                    continue
                except:
                    pass
            elif data == 'm!5':
                GlobalVal.now_room_id = GlobalVal.old_room_id
                GlobalVal.room_id = GlobalVal.old_room_id
                logger.error(f'[事件|房间|移动] 未提供密码')
                continue

            try:
                if Message:
                    pass
            except:
                Message = None

            if Message is not None and hasattr(Message, 'message'):
                # 调用注册过的命令
                plugin_list_remake = {}
                for plugin_list_r in GlobalVal.plugin_list:
                    plugin_list_remake[GlobalVal.plugin_list[plugin_list_r]['name']] = GlobalVal.plugin_list[plugin_list_r]

                for func in function_records:
                    if func in plugin_manage_data:
                        if not plugin_manage_data[func]['status']:
                            continue
                    for com_list in function_records[func]:
                        if com_list in Message.message:
                            if not function_records[func][com_list]['func_name'] in plugin_list_remake[func]['def']:
                                del function_records[func][com_list]['func_name']
                                return
                            if function_records[func][com_list]['substring_bool']:
                                if len(Message.message) > function_records[func][com_list][
                                    'substring_num'] and Message.message[
                                                         :function_records[func][com_list]['substring_num']] == str(function_records[func][com_list]['command']):
                                    try:
                                        if Message.type in function_records[func][com_list]['command_type']:
                                            await plugin_transfer(
                                                plugin_list_remake[func]['def'][function_records[func][com_list]['func_name']], (Message, Message.message.split(function_records[func][com_list]['command'])[1]),
                                                True
                                            )
                                    except:
                                        logger.error(
                                            f'调用已注册 {function_records[func][com_list]["command"]} 指令报错：{traceback.format_exc()}')
                            else:
                                if Message.message == str(function_records[func][com_list]['command']):
                                    try:
                                        if Message.type in function_records[func][com_list]['command_type']:
                                            await plugin_transfer(plugin_list_remake[func]['def'][function_records[func][com_list]['func_name']], Message, True)
                                    except:
                                        logger.error(
                                            f'调用已注册 {function_records[func][com_list]["command"]} 指令报错：{traceback.format_exc()}')
                continue

        logger.info(f'[未知] {data}')
