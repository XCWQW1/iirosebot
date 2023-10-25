import configparser


def load_config() -> [str, str, str]:
    # 配置文件路径
    config_path = "config/config.ini"

    # 读取配置文件
    config = configparser.ConfigParser()
    config.read(config_path)

    # 获取相应的配置信息
    room_id = str(config.get("bot", "room_id"))
    bot_name = str(config.get("bot", "name"))
    bot_password = str(config.get("bot", "password"))

    return bot_name, room_id, bot_password

