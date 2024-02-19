import re
import yaml

import log.main

config_path = "config/config.yml"


def get_master_id() -> str:
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)

    master_id = str(config["other"]["master_id"])

    return master_id


def get_user_color() -> str:
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)

    color = str(config["bot"]["color"])
    pattern = r'^([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$'
    if re.match(pattern, color):
        return color
    else:
        log.main.logger.warning('[警告|配置] 配置文件中的颜色不符合16进制')
        return 'DC143C'


def get_log_level() -> str:
    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        level = str(config["log"]["level"])
    except:
        level = 'INFO'

    return level
