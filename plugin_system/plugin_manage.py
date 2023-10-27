import os
import json


plugin_json = {}


if os.path.exists('config/plugin_manage.json'):
    with open('data.json', 'r') as f:
        plugin_json = json.load(f)
else:
    with open('data.json', 'w') as f:
        json.dump(plugin_json, f)

