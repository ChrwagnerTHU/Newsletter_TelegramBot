import json
from pathlib import Path
import re
import os

CONFIG_DIR = os.path.join(os.path.dirname(__file__), "configs")


def config_pfad(user_id):
    return os.path.join(CONFIG_DIR, f"{user_id}.json")

def meta_config_pfad():
    return os.path.join(CONFIG_DIR, f"config.json")

def lade_config(user_id):
    path = config_pfad(user_id)
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)
        config = {
        "Name": "Max",
        "Location": "Ulm",
        "Calendar": ""
        }
        with open(CONFIG_DIR, 'w') as f:
            json.dump(config, f, indent=4)
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def speichere_config(user_id, config):
    path = config_pfad(user_id)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

def list_config(user_id):
    return lade_config(user_id)

def edit_config(user_id, index, neues_dict):
    daten = lade_config(user_id)
    if 0 <= index < len(daten):
        daten[index].update(neues_dict)
        speichere_config(user_id, daten)
        return True
    return False

def get_all_user_ids():
    c_dir = Path(CONFIG_DIR)
    json_ids = [
        f.stem for f in c_dir.iterdir()
        if f.is_file() and f.suffix == ".json" and re.fullmatch(r"\d+", f.stem)
    ]
    return json_ids

def get_meta_config():
    with open(meta_config_pfad(), "r") as file:
        data = json.load(file)
    return data


def get_telegram_token(prod):
    with open(meta_config_pfad(), "r") as file:
        data = json.load(file)
        if prod:
            return data["TOKEN"]
        else: 
            return data["TOKEN_DEV"]