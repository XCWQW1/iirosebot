import inspect
import re
from openai import OpenAI
from loguru import logger
from API.api_iirose import APIIirose
from API.api_load_config import load_config
import json
from API.api_get_config import get_master_id
from plugins.chat.tools_desc import tools,available_functions
from datetime import datetime
from random import randint
import asyncio
from plugins.chat.tools_func import *
from time import sleep
from plugins.chat.config import *

client = OpenAI(
        api_key=api_key,
        base_url=base_url
    )

class GPT:
    def __init__(self, user_data):
        if user_data is None:
            raise
        self.id = user_data['id']
        self.name = user_data['name']
        self.chat_times = max_chat_times
        self.last_time = None
        self.messages = [
            {'role':"system", 'content':"[当前用户的名字和id分别是是{self.name},{self.id}]"+prompt},
            ]
    
    async def chat(self, Message):
        global n_Message
        n_Message = Message
        message = Message.message
        if self.chat_times == 0 and self.id != get_master_id():
            self.chat_times += calculate_time_difference(self.last_time,int(datetime.now().timestamp()))
            result = reply_list[randint(0,len(reply_list)-1)]
            yield result
        else:
            self.messages.append({'role': 'user', 'content': message})
            response = await self.run_conversation()
            for result in self.process_respon(Message, response):
                yield result
            self.chat_times -= 1
            self.last_time = int(datetime.now().timestamp())

    def process_respon(self, Message, response):
        if "您" in response or "你" in response or "我" in response:
            self.messages.append({"role":"system","content":callback_prompt})
        if response[:8] == "Markdown":
            result = r'\\\\*' + response[9:]
            yield result
        else:
            if len(sentence_endings) == 0:
                yield response
            else:
                result = f" [*{self.name}*] "
                for c in response:
                    if c is not None:
                        result += c
                        if len(sentence_endings) != 0:
                            sleep(0.1 * randint(0,3))
                        if c in sentence_endings:
                            yield result
                            result = ""
                yield result

    
    async def run_conversation(self):
        """递归执行gpt函数调用

        :return: _description_
        :rtype: _type_
        """        
        messages = self.messages
        result = None
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                tools=tools,
            )
        except:
            return error_reply
        choice_box = response.choices[0]
        finish_reason = choice_box.finish_reason
        response_message = choice_box.message
        if finish_reason == 'tool_calls':
            tool_calls = response_message.tool_calls
            if tool_calls:
                messages.append(response_message)
                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    function_to_call = available_functions[function_name]
                    function_args = json.loads(tool_call.function.arguments)
                    logger.info(f"[GPT] CALL : {function_name} by {tool_call.function.arguments}")
                    if inspect.iscoroutinefunction(function_to_call):
                        function_response = await function_to_call(**function_args)
                    else:
                        function_response = function_to_call(**function_args)
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": function_name,
                            "content": function_response,
                        }
                    )
                result = await self.run_conversation()
        elif finish_reason == 'stop':
            result = response_message.content
        return result
        
def is_reply(Message:str):
    """判断是否应该回复

    :param Message: 消息体
    :type Message: str
    """    
    message = Message.message
    bot_name, room_id, bot_password = load_config()
    if bot_name in message or alis in message:
        if '(_hr)' in message:
            reply_list = re.split(r'\(hr_\)|\(_hr\)', message)
            for i in range(1,len(reply_list),2):
                name = reply_list[i]
                if name not in (bot_name, Message.user_name):
                    #不支持多人对话
                    return None
            return reply_list[-1]
        else:
            return ""
    return None


def calculate_time_difference(timestamp1, timestamp2):
    """计算聊天次数

    :param timestamp1: _description_
    :type timestamp1: _type_
    :param timestamp2: _description_
    :type timestamp2: _type_
    :return: _description_
    :rtype: _type_
    """    
    dt1 = datetime.fromtimestamp(timestamp1)
    dt2 = datetime.fromtimestamp(timestamp2)
    time_difference = abs(dt2 - dt1)
    minutes_difference = time_difference.total_seconds() / 60
    units_difference = int(minutes_difference / 3)
    return min(units_difference, 3)
