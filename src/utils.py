import os
import json
from datetime import datetime

def remove_from_close_friends_lists(username):
    base_path = "custom/close_friends"
    found_in = []
    for file in os.listdir(base_path):
        if file.endswith(".json"):
            path = os.path.join(base_path, file)
            with open(path, "r+", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                    original_len = len(data)
                    data = [entry for entry in data if entry.get("value") != username]
                    if len(data) != original_len:
                        found_in.append(file)
                        f.seek(0)
                        json.dump(data, f, indent=4)
                        f.truncate()
                except Exception as e:
                    print(f"⚠️ No se pudo procesar {file}: {e}")
    return found_in

def add_to_blacklist(username):
    blacklist_path = "custom/not_following/black_list.json"
    if not os.path.exists(blacklist_path):
        os.makedirs(os.path.dirname(blacklist_path), exist_ok=True)
        with open(blacklist_path, "w", encoding="utf-8") as f:
            json.dump({ "name": "black list", "users": [] }, f, indent=4)

    with open(blacklist_path, "r+", encoding="utf-8") as f:
        data = json.load(f)
        if any(u["value"] == username for u in data["users"]):
            return
        timestamp = int(datetime.now().timestamp())
        data["users"].append({
            "href": f"https://www.instagram.com/{username}",
            "value": username,
            "timestamp": timestamp
        })
        f.seek(0)
        json.dump(data, f, indent=4)
        f.truncate()
