import configparser


def get_master_id() -> [str, str, str]:
    # 配置文件路径
    config_path = "config/config.ini"

    # 读取配置文件
    config = configparser.ConfigParser()
    config.read(config_path)

    # 获取相应的配置信息
    master_id = str(config.get("other", "master_id"))

    return master_id
