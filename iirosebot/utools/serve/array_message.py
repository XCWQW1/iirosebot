import re
import base64
import requests
import traceback
import iirosebot.API.api_iirose

from loguru import logger

from iirosebot.globals import GlobalVal
from iirosebot.utools import hex2uid, uid2hex


async def file_pares(image_path):
    if image_path.startswith('file:///'):
        # FILE
        file_path = image_path[8:]
        img = await iirosebot.API.api_iirose.APIIirose.upload_files(file_path)
        return "[{}#e]".format(img['url'])

    elif image_path.startswith('http://') or image_path.startswith('https://'):
        # URL
        return "[{}#e]".format(image_path)

    elif image_path.startswith('base64://'):
        # Base64
        base64_data = image_path[9:]
        img_data = base64.b64decode(base64_data)
        img = await iirosebot.API.api_iirose.APIIirose.upload_files(img_data)
        return "[{}#e]".format(img['url'])


async def array2text(array: list):
    text = ""
    try:
        for i in array:
            if i['type'] == "text":
                text += i['data']['text']

            elif i['type'] == "face":
                text += "[https://xc.null.red:8043/XCimg/img/qq-face/{}.png]".format(i['data']['id'])

            elif i['type'] in ['image', 'record', 'video']:
                if 'url' in i['data']:
                    text += i['data']['url']
                else:
                    text += await file_pares(i['data']['file'])

            elif i['type'] == "at":
                text += " [*{}*] ".format(GlobalVal.iirose_date['user'][hex2uid(i['data']['qq'])]['name'])

            elif i['type'] == "share":
                text += i['data']['url']

            elif i['type'] == "contact":
                if i['data']['type'] == "qq":
                    text += " [@{}@] ".format(hex2uid(i['data']['id']))
                elif i['data']['type'] == "group":
                    text += " [_{}_] ".format(hex2uid(i['data']['id']))

            elif i['type'] == "music":
                text = "媒体已点播"
                if i['data']['type'] == "163":
                    song_data = requests.get(
                        'https://xc.null.red:8043/meting-api/?type=302&id={}'.format(i['data']['id'])).json()
                    await iirosebot.API.api_iirose.APIIirose.play_media(True, song_data['url'], True,
                                                                        iirosebot.API.api_iirose.PlatformType.netease,
                                                                        song_data['name'], song_data['author'],
                                                                        song_data['lrc_control'], song_data['pic'],
                                                                        song_data['id'], song_data['time'] / 1000 / 60)
                elif i['data']['type'] == "qq":
                    song_data = requests.get(
                        'https://xc.null.red:8043/music/qq/?id={}&type=302'.format(i['data']['id'])).json()
                    await iirosebot.API.api_iirose.APIIirose.play_media(True, song_data['url'], True,
                                                                        iirosebot.API.api_iirose.PlatformType.netease,
                                                                        song_data['name'], song_data['author'],
                                                                        song_data['lrc_control'], song_data['pic'],
                                                                        song_data['id'], song_data['time'] / 1000 / 60)
                elif i['data']['type'] == "custom":
                    if 'image' in i['data']:
                        await iirosebot.API.api_iirose.APIIirose.play_media(True, i['data']['audio'],
                                                                            media_name=i['data']['title'],
                                                                            media_auther=i['data']['title'],
                                                                            media_pic=i['data']['image'])
                    else:
                        await iirosebot.API.api_iirose.APIIirose.play_media(True, i['data']['audio'],
                                                                            media_name=i['data']['title'],
                                                                            media_auther=i['data']['title'])

            elif i['type'] == "reply":
                try:
                    reply_id = str(int(i['data']['id']))
                except:
                    reply_id = str(hex2uid(i['data']['id']))

            else:
                text += "[暂不支持:{}]".format(i['data']['type'])
    except:
        logger.error("CQ消息解析出错\n" + traceback.format_exc())
        return "消息解析出错"

    return text


async def text2array(text):
    try:
        if type(text) == list:
            return [{
                "type": "text",
                "data": {
                    "text": str(text),
                }
            }]

        result = []
        last_pos = 0

        combined_pattern = f"(\[(http[^\[\]]+)\])|( \[([@*_])([^\[\]@*_]+)[@*_]\] )"

        for match in re.finditer(combined_pattern, text):
            # 文本匹配
            if last_pos < match.start():
                result.append({"type": "text", "data": {"text": text[last_pos:match.start()]}})

            if match.group(1):  # URL 匹配
                result.append({"type": "image", "data": {"file": match.group(1)[1:-1]}})
            else:  # RI码匹配
                symbol = match.group(4)
                content = match.group(5)
                if symbol == '*':
                    if content in GlobalVal.iirose_date['user_name']:
                        result.append({"type": "at", "data": {"qq": uid2hex(GlobalVal.iirose_date['user_name'][content]['id'])}})
                elif symbol == '@':
                    result.append({"type": "contact", "data": {"type": "qq", "id": uid2hex(content)}})
                elif symbol == '_':
                    result.append({"type": "contact", "data": {"type": "qq", "group": uid2hex(content)}})

            # 更新起始位置
            last_pos = match.end()

        # 添加最后一个匹配项之后的文本
        if last_pos < len(text):
            result.append({"type": "text", "data": {"text": text[last_pos:]}})

        return result
    except:
        logger.error(f'RI转CQ出错：{traceback.format_exc()}')
        return [{
            "type": "text",
            "data": {
                "text": "消息解析出错",
            }
        }]
