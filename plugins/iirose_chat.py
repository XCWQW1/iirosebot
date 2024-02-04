import asyncio
from loguru import logger
from plugins.chat.api_chat import GPT
from plugins.chat.api_chat import is_reply
from API.api_iirose import APIIirose
API = APIIirose()
GPT_list = {}

async def room_message(Message):
    logger.debug("Room message")
    if Message.is_bot:
        return
    flag = is_reply(Message)
    if flag is not None:
        if flag != "":
            Message.message = flag
        user_id = Message.user_id
        user_data = await API.get_user_info(user_id)
        if user_id in GPT_list:
            user_GPT = GPT_list[user_id]
        else:
            user_GPT = GPT(user_data)
            GPT_list[user_id] = user_GPT

        async for result in user_GPT.chat(Message):
            if result == "":
                continue
            logger.info(f"[GPT] 发送: {result}")
            await API.send_msg(Message,result)

async def private_message(Message):
    if Message.is_bot:
        return
    flag = is_reply(Message)
    if flag != "" and flag is not None:
        Message.message = flag
    user_id = Message.user_id
    user_data = await API.get_user_info(user_id)
    if user_id in GPT_list:
        user_GPT = GPT_list[user_id]
    else:
        user_GPT = GPT(user_data)
        GPT_list[user_id] = user_GPT

    async for result in user_GPT.chat(Message):
        if result == "":
                continue
        logger.info(f"[GPT] 发送: {result}")
        await API.send_msg(Message,result)
