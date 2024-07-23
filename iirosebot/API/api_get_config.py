import json
import re
import yaml
from loguru import logger

from iirosebot.utools.generate_token import generate_token

config_path = "config/config.yml"


def get_master_id() -> str:
    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)

        master_id = str(config["other"]["master_id"])
    except:
        master_id = None

    return master_id


def get_bot_id() -> str:
    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)

        master_id = str(config["bot"]["uid"])
    except:
        master_id = None

    return master_id


def get_user_color() -> str:
    with open(config_path, 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)

    color = str(config["bot"]["color"])
    pattern = r'^([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$'
    if re.match(pattern, color):
        return color
    else:
        logger.warning('[警告|配置] 配置文件中的颜色不符合16进制')
        return 'DC143C'


def get_log_level() -> str:
    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
        level = str(config["log"]["level"])
    except:
        level = 'INFO'

    return level


def get_log_color() -> bool:
    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
        color_status = config["log"]["color"]
    except:
        color_status = True

    return color_status


def get_introduction() -> str:
    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
        introduction = str(config["bot"]["introduction"])
    except:
        introduction = ''

    return introduction


def get_serve() -> json:
    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
        serve_status = config["serve"]
    except:
        serve_status = {
            'token': generate_token(40),
            'http_api': {
                'enabled': False,
                'verify': False,
                'host': 'localhost',
                'port': 9000,
            },
            'webhook': {
                'enabled': False,
                'url': 'http://your_webhook.server/',
                'verify': False,
                'time_out': 3000,
            },
            'websocket_server': {
                'enabled': False,
                'verify': False,
                'host': 'localhost',
                'port': 9002,
            },
            'websocket_reverse': {
                'enabled': False,
                'verify': False,
                'url': 'ws://your_websocket_universal.server',
                'api': 'ws://your_websocket_api.server',
                'event': 'ws://your_websocket_event.server',
                'reconnect_interval': 3000,
            },
        }

    return serve_status


def get_heartbeat() -> json:
    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
        heartbeat_status = config["heartbeat"]
    except:
        heartbeat_status = {
            'enabled': True,
            'interval': 15000
        }

    return heartbeat_status


def get_token() -> str:
    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
        serve_status = config["serve"]["token"]
    except:
        serve_status = generate_token(40)

    return serve_status
