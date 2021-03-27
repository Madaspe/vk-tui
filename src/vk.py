import vk_api
from vk_api.exceptions import ApiError
from vk_api.longpoll import VkLongPoll
from vk_api.utils import get_random_id
from settings import delete_token
from simple_cache import get_from_cache


def get_peer_names():
    try:
        peer_names = get_from_cache('peer_names')
    except KeyError:
        peer_names = {"user": {}, "chat": {}, "group": {}}

    return peer_names


class Vk:
    def __init__(self, token):
        try:
            self.vk = vk_api.VkApi(token=token)
            self.vk_api = self.vk.get_api()
            self.vk_longpoll = VkLongPoll(self.vk)

            self.peer_names = get_peer_names()
        except ApiError:
            print("Token not avalible")
            delete_token()

    def get_list_conversations(self, count=10, offset=0):
        conversations_ids = []

        conversations = \
            self.vk_api.messages.getConversations(count=count, offset=offset, fields="first_name,last_name,name")[
                'items']
        for conversation in conversations:
            peer_id = str(conversation['conversation']['peer']['id'])
            type_conversation = conversation['conversation']['peer']['type']

            if peer_id not in self.peer_names[type_conversation]:
                self.save_peer_name(conversation)

            conversations_ids.append([self.peer_names[type_conversation][peer_id], peer_id])

        return conversations_ids

    def save_peer_name(self, conversation):
        peer_id = str(conversation['conversation']['peer']['id'])
        type_conversation = conversation['conversation']['peer']['type']

        if type_conversation == "user":
            self.peer_names['user'][peer_id] = \
                self.vk_api.users.get(user_ids=conversation['conversation']['peer']['id'])[0][
                    'first_name']
        elif type_conversation == "chat":
            self.peer_names['chat'][peer_id] = conversation['conversation']['chat_settings']['title']
        elif type_conversation == 'group':
            self.peer_names['group'][peer_id] = \
                self.vk_api.groups.getById(group_ids=conversation['conversation']['peer']['local_id'])[0]['name']

    def get_conversation_text(self, id, count_messages=30):
        messages = []

        conversation_history = self.vk_api.messages.getHistory(count=count_messages, peer_id=id)['items']
        for message in conversation_history:
            if message["from_id"] not in self.peer_names['user']:
                user = self.vk_api.users.get(user_ids=message['from_id'])[0]
                self.peer_names['user'][message['from_id']] = f"{user['first_name']} {user['last_name']}"

            message["from_id"] = self.peer_names['user'][message["from_id"]]
            if message['text'] == '':
                messages.append(f'From: {message["from_id"]}\n\n <><><><><><><><>\n\n')
            else:
                messages.append(f'From: {message["from_id"]}\n\n {message["text"]}\n\n')

        return messages

    def send_message(self, id, msg):
        self.vk_api.messages.send(peer_id=id, message=msg, random_id=get_random_id())

    def listen_longpoll(self):
        for event in self.vk_longpoll.listen():
            yield event
# try:
#     vk = vk_api.VkApi(token=TOKEN)
#     vk_api = vk.get_api()
#     vk_longpoll = VkLongPoll(vk)
# except ApiError:
#     result = input_dialog(
#         title="VK ", text="Please type your vk token:      (Tab to change focus)"
#     ).run()
#
#     if result:
#         TOKEN = result
#         save_token(TOKEN)
#
# try:
#     peer_names = get_from_cache('peer_names')
# except KeyError:
#     peer_names = {"user": {}, "chat": {}, "group": {}}
#
#
# def save_peer_name(conversation):
#     peer_id = str(conversation['conversation']['peer']['id'])
#     type_conversation = conversation['conversation']['peer']['type']
#
#     if type_conversation == "user":
#         peer_names['user'][peer_id] = vk_api.users.get(user_ids=conversation['conversation']['peer']['id'])[0][
#             'first_name']
#     elif type_conversation == "chat":
#         peer_names['chat'][peer_id] = conversation['conversation']['chat_settings']['title']
#     elif type_conversation == 'group':
#         peer_names['group'][peer_id] = \
#             vk_api.groups.getById(group_ids=conversation['conversation']['peer']['local_id'])[0]['name']
#
#
# def get_list_conversations(count=10, offset=0):
#     conversations_ids = []
#
#     conversations = vk_api.messages.getConversations(count=count, offset=offset, fields="first_name,last_name,name")[
#         'items']
#     for conversation in conversations:
#         peer_id = str(conversation['conversation']['peer']['id'])
#         type_conversation = conversation['conversation']['peer']['type']
#
#         if peer_id not in peer_names[type_conversation]:
#             save_peer_name(conversation)
#
#         conversations_ids.append([peer_names[type_conversation][peer_id], peer_id])
#
#     return conversations_ids
#
#
# def get_conversation_text(id, count_messages=30):
#     messages = []
#
#     conversation_history = vk_api.messages.getHistory(count=count_messages, peer_id=id)['items']
#     for message in conversation_history:
#         if message["from_id"] not in peer_names['user']:
#             user = vk_api.users.get(user_ids=message['from_id'])[0]
#             peer_names['user'][message['from_id']] = f"{user['first_name']} {user['last_name']}"
#
#         message["from_id"] = peer_names['user'][message["from_id"]]
#         if message['text'] == '':
#             messages.append(f'From: {message["from_id"]}\n\n <><><><><><><><>\n\n')
#         else:
#             messages.append(f'From: {message["from_id"]}\n\n {message["text"]}\n\n')
#
#     return messages
#
#
# def send_message(id, msg):
#     vk_api.messages.send(peer_id=id, message=msg, random_id=get_random_id())
