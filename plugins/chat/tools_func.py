from openai import OpenAI
from loguru import logger
from API.api_iirose import APIIirose
from API.api_load_config import load_config
import json
from plugins.chat.tools_desc import tool
from datetime import datetime
from random import randint
from globals.globals import GlobalVal
import asyncio

API = APIIirose()

class Message_Init:
    type = None
    timestamp = int(datetime.now().timestamp())
    user_id = ""
    user_name = ""
    user_pic = ""
    message = ""
    message_id = ""
    message_color = ""
    message_background_color = ""
    is_bot = True

n_Message = Message_Init()

@tool
def get_user_id(user_name:str):
    """获得用户id

    :param user_name: 用户名
    :type user_name: str
    """
    for id in GlobalVal.iirose_date['user']:
        if GlobalVal.iirose_date['user'][id]['name'] == user_name:
            result = id
            return result
    return "未查询到该用户id，可能名字错误"

@tool
async def get_user_info(user_id:str):
    """获取用户信息
    返回用户所在房间的id

    :param user_id: 用户id
    :type user_id: str
    :return: _description_
    :rtype: _type_
    """    
    user_data = await API.get_user_info(user_id)
    result = {
        'user_name' : user_data['name'],
        'room_id' : user_data['room_id'],
    }
    return result

@tool
async def get_room_info(room_id:str):
    """获取房间信息

    :param room_id: 房间id
    :type room_id: str
    :return: _description_
    :rtype: _type_
    """    
    result = {}
    response = await API.get_room_info(room_id)
    if response == None:
        return "获取失败，可能房间id错误"
    result['name'] = response['name']
    return result

@tool
async def like(user_id:str, message:str = ""):
    """为用户点赞

    :param user_id: 用户id
    :type user_id: str
    :param message: 点赞留言,默认为""
    :type message: str, optional
    """    
    response = await API.like(user_id,message)
    if response['code'] == 200:
        return "点赞成功"
    else:
        return "点赞失败"

@tool
async def send_msg(message:str):
    """发送消息

    :param message: 消息
    :type message: str
    """    
    response = await API.send_msg(n_Message, message)
    if response['code'] == 200:
        return "发送成功"
    else:
        return "发送失败"

@tool
async def move_room(room_id:str,password:str=""):
    """
    移动到指定的房间
    :param room_id:  目标房间id
    :type room_id: str
    :param password: 目标房间密码,默认为空
    :type password: str
    :return:
    """
    response = await API.move_room(room_id,password=password)
    if response['code'] == 200:
        return "success"
    else:
        return response['error']
    