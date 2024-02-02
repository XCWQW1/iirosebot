import yaml


def load_config() -> [str, str, str]:
    config_path = "config/config.yml"

    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)

    room_id = str(config['bot']['room_id'])
    bot_name = str(config['bot']['username'])
    bot_password = str(config['bot']['password'])

    return bot_name, room_id, bot_password
