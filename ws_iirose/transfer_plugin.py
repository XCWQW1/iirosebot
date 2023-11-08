import gzip
import html
import re
import traceback

from loguru import logger
from API.decorator.command import function_records, MessageType
from plugin_system.plugin_transfer import plugin_transfer


def check_start_symbols(text):
    pattern = r'^(\W+)'  # 匹配一个或多个非单词字符（符号）开头
    matches = re.match(pattern, text)

    if matches:
        start_symbols = matches.group(1)  # 获取匹配到的开头符号
        return True, start_symbols
    else:
        return False, None


async def process_message(data, websocket, plugin_list):
    msg_list = []

    if data[0] == 1:
        data = gzip.decompress(data[1:]).decode('utf-8')
    else:
        data = data.decode("utf-8")

    split_list = data.split("<")

    async def login_error(data):
        if data[:1] == '%*"':
            error_code = data[:-3]
            if error_code == 1:
                logger.error('[登陆|错误] 用户不存在')
            elif error_code == 2:
                logger.error('[登陆|错误] 密码错误')
            elif error_code == 0:
                logger.error('[登陆|错误] 名字被占用')
            elif error_code == 2:
                logger.error('[登陆|错误] 用户不存在')
        else:
            from ws_iirose.login_bot import init_plugin
            await init_plugin()

    if len(split_list) <= 1:
        for i in split_list:
            if not i[:1] == "%":
                msg_list.append(i)
            else:
                await login_error(data)
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
            await login_error(data)

    for data in reversed(msg_list):
        if data == 'm':
            logger.info(f'[WS] 切换房间')
            await websocket.close()
            return
        else:
            if data == ',':
                # 切媒体
                logger.info(f'[事件|媒体] 切媒体')
                await plugin_transfer('media_cut')
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

                        if Message.message[:4] == 'm__4':
                            msg = Message.message.split('>')

                            class Media:
                                media_name = msg[1]
                                media_auther = msg[2]
                                media_pic = msg[3]

                            logger.info(f'[事件|媒体|点播] {Message.user_name} 点播来自 {Media.media_auther} 的 {Media.media_name}')
                            await plugin_transfer('play_media', (Message, Media))
                            return

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

            try:
                if Message:
                    pass
            except:
                Message = None

            if Message is not None and hasattr(Message, 'message'):
                # 调用注册过的命令
                plugin_list_remake = {}
                for plugin_list_r in plugin_list:
                    plugin_list_remake[plugin_list[plugin_list_r]['name']] = plugin_list[plugin_list_r]

                for func in function_records:
                    for com_list in function_records[func]:
                        if com_list in Message.message:
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
