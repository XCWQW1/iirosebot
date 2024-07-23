import asyncio


class GlobalVal:
    websocket = None
    old_room_id = None
    room_id = None
    move_room = False
    now_room_id = None
    room_password = None
    plugin_list = None
    plugin_status = None
    iirose_date = {"user": {}, "room": {}, "user_name": {}, "room_name": {}, "room_tree": {}}
    queue_list = {"playlist": asyncio.Queue()}
    iirosebot_version = 'v1.7.1'
    close_status = False
    message_cache = {"private": {}, "group": {}}
    send_message_cache = {"private": {}, "group": {}}

