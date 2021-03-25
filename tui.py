from functools import partial
import threading

from time import sleep
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
from prompt_toolkit.styles import Style
from prompt_toolkit.widgets import Box, Button, Frame, Label, TextArea
from prompt_toolkit.enums import EditingMode
from prompt_toolkit.filters import Condition
from prompt_toolkit.completion import WordCompleter

from vk import get_list_conversations, get_conversation_text, send_message, vk_longpoll, vk_api

selected_conversation = None


def monitoring_vk_longpoll(text_area):
    for event in vk_longpoll.listen():
        if not get_app().is_running:
            break

        if event.type == VkEventType.MESSAGE_NEW and event.peer_id == selected_conversation:
            user = vk_api.users.get(user_ids=event.user_id)[0]
            text_area.text = f'From: {user["first_name"]} {user["last_name"]}\n\n {event.text}\n\n' + text_area.text


def command_handler(input_field, buff):
    if selected_conversation is not None:
        if input_field.text.startswith("/msg"):
            send_message(selected_conversation, input_field.text.replace('/msg ', ''))

    else:
        return


def conversations_handler(id):
    global selected_conversation
    text_area.text = "\n".join(get_conversation_text(id))

    selected_conversation = id


def next_conversations(buttons_list, offset):
    new_conversations = get_list_conversations(count=len(buttons_list), offset=offset)
    for iter in range(0, len(buttons_list) - 1):
        conversation = new_conversations[iter]
        button = buttons_list[iter]

        button.text = conversation[0][:25]
        button.handler = partial(conversations_handler, conversation[1])

    buttons_list[-1].handler = partial(next_conversations, buttons_list, offset + len(buttons_list))
    get_app().layout.focus(buttons_list[0])


def get_buttons_list(count=10, offset=0):
    buttons_list = []
    for conversation in get_list_conversations(count=10, offset=0):
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
text_area = TextArea(focusable=False)

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

root_container = HSplit(
    [Label(text="VK messanger (type 'q' for exit)", width=1), VSplit(
        [Frame(title="Conversations", body=ScrollablePane(HSplit(buttons_list, padding=1, padding_char='-'))),
         HSplit([Frame(title='Conversation', body=text_area), input_field])]
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
    # vk_mon.()
    get_app().exit()
    exit()


# Build a main application object.
application = Application(layout=layout, key_bindings=kb, full_screen=True)


def start_tui():
    application.run()
    vk_monitoring_thread.join()
