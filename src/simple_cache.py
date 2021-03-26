import os
import json
import getpass

cache = {}

try:
    os.mkdir(f"/home/{getpass.getuser()}/.config/vk-tui/")
except:
    pass

try:
    with open(f"/home/{getpass.getuser()}/.config/vk-tui/cache", 'r') as file:
        file_text = file.read()
        if file_text:
            cache = json.loads(file_text)
except FileNotFoundError:
    open(f"/home/{getpass.getuser()}/.config/vk-tui/cache", 'w').close()


def add_to_cache(key, value):
    cache[key] = value


def get_from_cache(key):
    return cache[key]


def save_cache_to_file():
    with open(f"/home/{getpass.getuser()}/.config/vk-tui/cache", 'w') as file:
        file.write(json.dumps(cache))


def remove_all_cache_file():
    with open(f"/home/{getpass.getuser()}/.config/vk-tui/cache", 'w') as file:
        file.write("")