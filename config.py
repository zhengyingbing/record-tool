from pathlib import Path
import json

CONFIG_FILE = "config.json"

def save_config(path):
    config = {"last_path": path}
    Path(CONFIG_FILE).write_text(json.dumps(config))

def load_config():
    try:
        return json.loads(Path(CONFIG_FILE).read_text()).get("last_path", "")
    except:
        return ""
