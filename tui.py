from functools import partial

from prompt_toolkit.application import Application
from prompt_toolkit.application.current import get_app
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.key_binding.bindings.focus import focus_next, focus_previous
from prompt_toolkit.layout import HSplit, Layout, VSplit, ScrollablePane
from prompt_toolkit.styles import Style
from prompt_toolkit.widgets import Box, Button, Frame, Label, TextArea

from vk import get_list_conversations, get_conversation_text

buttons_list = []


def exit_clicked():
    get_app().exit()


def conversations_handler(id):
    text_area.text = "\n".join(get_conversation_text(id))


for conversation in get_list_conversations(count=200, offset=0):
    buttons_list.append(Button(conversation, handler=partial(conversations_handler, conversation), width=30))
buttons_list.append(Button("Exit", handler=exit_clicked, width=30))

text_area = TextArea(focusable=True)

root_container = VSplit(
    [ScrollablePane(HSplit(buttons_list, padding=1, padding_char='-')),
     Frame(body=text_area)]
)

layout = Layout(container=root_container, focused_element=buttons_list[0])

# Key bindings.
kb = KeyBindings()
kb.add("tab")(focus_next)
kb.add("s-tab")(focus_previous)


@kb.add('c-c')
def exit():
    get_app().exit()


# Build a main application object.
application = Application(layout=layout, key_bindings=kb, full_screen=True)


def main():
    application.run()


if __name__ == "__main__":
    main()
