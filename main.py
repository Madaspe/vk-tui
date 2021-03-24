import vk_api
import vk_api.longpoll

from settings import TOKEN, save_token

if TOKEN is None:
    TOKEN = input("Token: ")
    save_token(TOKEN)

