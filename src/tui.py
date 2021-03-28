from functools import partial
import threading

from vk_api.longpoll import VkEventType

from prompt_toolkit.application import Application
from prompt_toolkit.application.current import get_app
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.key_binding.bindings.focus import focus_next, focus_previous
from prompt_toolkit.layout import (
    CompletionsMenu,
    Float,
    FloatContainer,
    HSplit,
    Layout,
    ScrollablePane,
    VSplit,
)
from prompt_toolkit.widgets import Button, Frame, Label, TextArea
from prompt_toolkit.filters import Condition
from prompt_toolkit.completion import WordCompleter

from vk import Vk
from settings import TOKEN

from simple_cache import save_cache_to_file, add_to_cache

selected_conversation = None
vk = Vk(token=TOKEN)


def monitoring_vk_longpoll(text_area):
    for event in vk.vk_longpoll.listen():
        if not get_app().is_running:
            break
        if event.type == VkEventType.MESSAGE_NEW and str(event.peer_id) == str(selected_conversation):
            user = vk.vk_api.users.get(user_ids=event.user_id)[0]
            text_area.text = f'From: {user["first_name"]} {user["last_name"]}\n\n {event.text}\n\n' + text_area.text


def command_handler(input_field, buff):
    old_input_text = input_field.text
    input_field.text = "Command excluding"

    if selected_conversation is not None:
        if old_input_text.startswith("/msg"):
            vk.send_message(selected_conversation, old_input_text.replace('/msg ', ''))
        elif old_input_text.startswith('/photo'):
            text = old_input_text.replace('/photo ', '')
            text = text.split()

            vk.send_photo(selected_conversation, text[0], msg=" ".join(text[1:]))
        elif old_input_text.startswith('/video'):
            text = old_input_text.replace('/video ', '')
            text = text.split()

            vk.send_video(selected_conversation, text[0], msg=" ".join(text[1:]))

    input_field.text = ""
    return


def conversations_handler(id):
    global selected_conversation
    text_area.text = "\n".join(vk.get_conversation_text(id))

    selected_conversation = id


def next_conversations(buttons_list, offset):
    new_conversations = vk.get_list_conversations(count=len(buttons_list), offset=offset)
    for iter in range(0, len(buttons_list) - 1):
        conversation = new_conversations[iter]
        button = buttons_list[iter]

        button.text = conversation[0][:25]
        button.handler = partial(conversations_handler, conversation[1])

    buttons_list[-1].handler = partial(next_conversations, buttons_list, offset + len(buttons_list))
    get_app().layout.focus(buttons_list[0])


def get_buttons_list(count=10, offset=0):
    buttons_list = []
    for conversation in vk.get_list_conversations(count=10, offset=0):
        buttons_list.append(
            Button(conversation[0][:25], handler=partial(conversations_handler, conversation[1]), width=30))
    buttons_list.append(Button("Next", handler=partial(next_conversations, buttons_list, len(buttons_list)), width=30))

    return buttons_list


command_completer = WordCompleter(
    [
        "/msg",
        "/photo",
        "/stiker",
        "/file",
        "/video"
    ],

)
buttons_list = get_buttons_list()
text_area = TextArea(focusable=True)

vk_monitoring_thread = threading.Thread(target=monitoring_vk_longpoll, args=(text_area,), daemon=True)
vk_monitoring_thread.start()

input_field = TextArea(
    height=1,
    prompt="(click 't' to focus)  >>> ",
    multiline=False,
    wrap_lines=False,
    focusable=True,
    completer=command_completer
)

input_field.accept_handler = partial(command_handler, input_field)
conversation_frame = Frame(title="Conversation (type 'c' for focus)", body=text_area)

root_container = HSplit(
    [Label(text="VK messanger (type 'q' for exit)", width=1), VSplit(
        [Frame(title="Conversations", body=ScrollablePane(HSplit(buttons_list, padding=1, padding_char='-'))),
         HSplit([conversation_frame, input_field])]
    )]
)

root_container = FloatContainer(
    root_container,
    floats=[
        Float(
            xcursor=True,
            ycursor=True,
            content=CompletionsMenu(max_height=32, scroll_offset=2),
        ),
    ],
)

layout = Layout(container=root_container, focused_element=buttons_list[0])


@Condition
def is_active():
    if get_app().layout.has_focus(input_field):
        return False
    else:
        return True


# Key bindings.
kb = KeyBindings()
kb.add("tab")(focus_next)
kb.add("s-tab")(focus_previous)


@kb.add("t", filter=is_active)
def _(event):
    get_app().layout.focus(input_field)


@kb.add('q', filter=is_active)
def _(event):
    add_to_cache('peer_names', vk.peer_names)
    save_cache_to_file()
    get_app().exit()
    exit()


@kb.add('c', filter=is_active)
def _(event):
    get_app().layout.focus(text_area)


# Build a main application object.
application = Application(layout=layout, key_bindings=kb, full_screen=True)


def start_tui():
    application.run()
    vk_monitoring_thread.join()
