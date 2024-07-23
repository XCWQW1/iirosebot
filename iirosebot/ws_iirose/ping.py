import asyncio
import traceback

from iirosebot.globals import GlobalVal


max_len = 50


def del_json_half(json_data):
    keys_to_delete = list(json_data.keys())[len(json_data) // 2:]
    for key in keys_to_delete:
        del json_data[key]


async def ping_iirose(websocket):
    try:
        while True:
            if len(GlobalVal.message_cache['private']) >= max_len:
                del_json_half(GlobalVal.message_cache['private'])
            if len(GlobalVal.message_cache['group']) >= max_len:
                del_json_half(GlobalVal.message_cache['group'])
            if len(GlobalVal.send_message_cache['private']) >= max_len:
                del_json_half(GlobalVal.send_message_cache['private'])
            if len(GlobalVal.send_message_cache['group']) >= max_len:
                del_json_half(GlobalVal.send_message_cache['group'])

            await websocket.send('')
            await asyncio.sleep(60)
    except:
        traceback.print_exc()
        pass
