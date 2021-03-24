import vk_api
from vk_api.longpoll import VkLongPoll
from vk_api.utils import get_random_id

from settings import TOKEN

vk = vk_api.VkApi(token=TOKEN)
vk_api = vk.get_api()
vk_longpoll = VkLongPoll(vk)

def get_list_conversations(count=30, offset=0):
    conversations_ids = []

    conversations = vk_api.messages.getConversations(count=count, offset=offset, fields="first_name,last_name,name")[
        'items']
    for conversation in conversations:
        conversations_ids.append(conversation['conversation']['peer']['id'])

    return conversations_ids


def get_conversation_text(id, count_messages=30):
    messages = []

    conversation_history = vk_api.messages.getHistory(count=count_messages, peer_id=id)['items']
    for message in conversation_history:
        if message['text'] == '':
            messages.append(f'From: {message["from_id"]}\n\n <><><><><><><><>\n\n')
        else:
            messages.append(f'From: {message["from_id"]}\n\n {message["text"]}\n\n')

    return messages


def send_message(id, msg):
    vk_api.messages.send(peer_id=id, message=msg, random_id=get_random_id())
