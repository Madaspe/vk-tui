import vk_api
from vk_api.exceptions import ApiError
from vk_api.longpoll import VkLongPoll
from vk_api.utils import get_random_id
from settings import delete_token
from simple_cache import get_from_cache
from getpass import getuser


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
            self.upload = vk_api.VkUpload(self.vk)

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

    def get_conversation_text(self, id, count_messages=200):
        messages = []

        conversation_history = self.vk_api.messages.getHistory(count=count_messages, peer_id=id)['items']
        for message in conversation_history:

            type_conversation = "group" if str(message['from_id'])[0] == "-" else "user"
            from_id = message['from_id'] if type_conversation == "user" else str(message['from_id'])[1:]

            if from_id not in self.peer_names[type_conversation]:
                user = self.vk_api.users.get(user_ids=from_id)[0] if type_conversation == "user" else \
                    self.vk_api.groups.getById(group_ids=str(from_id))[0]
                self.peer_names[type_conversation][
                    from_id] = f"{user['first_name']} {user['last_name']}" if type_conversation == "user" else \
                    f"{user['name']}"

            name_user = self.peer_names[type_conversation][from_id]
            if message['text'] == '':
                messages.append(f'From: {name_user}\n\n <><><><><><><><>\n\n')
            else:
                messages.append(f'From: {name_user}\n\n {message["text"]}\n\n')

        return messages

    def send_message(self, id, msg):
        self.vk_api.messages.send(peer_id=id, message=msg, random_id=get_random_id())

    def send_photo(self, id, path, msg=""):
        photo = self.upload.photo_messages(path.replace('~', f"/home/{getuser()}"))
        owner_id = photo[0]['owner_id']
        photo_id = photo[0]['id']
        access_key = photo[0]['access_key']
        attachment = f'photo{owner_id}_{photo_id}_{access_key}'

        if msg:
            self.vk_api.messages.send(peer_id=id, random_id=get_random_id(), attachment=attachment, message=msg)
        else:
            self.vk_api.messages.send(peer_id=id, random_id=get_random_id(), attachment=attachment)

    def send_video(self, id, path, msg=""):
        video = self.upload.video(path.replace('~', f"/home/{getuser()}"))
        owner_id = video['owner_id']
        video_id = video['video_id']
        access_key = video['access_key']
        attachment = f'video{owner_id}_{video_id}_{access_key}'

        if msg:
            self.vk_api.messages.send(peer_id=id, random_id=get_random_id(), attachment=attachment, message=msg)
        else:
            self.vk_api.messages.send(peer_id=id, random_id=get_random_id(), attachment=attachment)
