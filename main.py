from prompt_toolkit.shortcuts import input_dialog
from settings import TOKEN, save_token

if TOKEN is None:
    result = input_dialog(
        title="VK ", text="Please type your vk token:      (Tab to change focus)"
    ).run()

    if result:
        TOKEN = result
        save_token(TOKEN)

