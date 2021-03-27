from os import mkdir, remove

from getpass import getuser

try:
    mkdir(f'/home/{getuser()}/.config/vk-tui')
except FileExistsError as e:
    pass


def save_token(token):
    try:
        with open(f"/home/{getuser()}/.config/vk-tui/token", 'w') as file:
            file.write(token)
    except Exception as e:
        pass


def delete_token():
    try:
        remove(f"/home/{getuser()}/.config/vk-tui/token")
    except:
        pass


TOKEN = None

try:
    with open(f'/home/{getuser()}/.config/vk-tui/token') as file:
        TOKEN = file.read().replace("\n", "")
except Exception as e:
    pass
