from pathlib import Path

from kivy.base import ExceptionHandler, ExceptionManager
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.properties import NumericProperty, ObjectProperty, StringProperty
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import NoTransition, Screen, ScreenManager
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel

from ..config import Identifier, Setting, settings
from ..events import global_stop_event
from ..network import Networks
from ..network.requests import MPP, Request
from ..objects import Conversation, OwnMessage, is_private_key_loaded
from ..utils import format_err


class WindowManager(ScreenManager):
    pass


class ErrorPopup(Popup):
    pass


class LoadKeyScreen(Screen):
    """
    A screen prompting the user to load a value!
    """

    name = StringProperty("load_key")


class StartScreen(Screen):
    """
    The first screen that is displayed when launching the app.
    """

    name = StringProperty("start")
    logo = ObjectProperty()

    def on_enter(self, *args):
        def _end_start_sequence(_):
            if is_private_key_loaded():
                self.manager.switch_to(ConversationsScreen())
            else:
                self.manager.switch_to(LoadKeyScreen())

        Clock.schedule_once(_end_start_sequence, 0.2)


class ChatListItem(MDCard):
    """
    A clickable chat item for the chat timeline.
    """

    friend_name = StringProperty()
    message = StringProperty()
    timestamp = StringProperty()
    friend_avatar = StringProperty()
    conversation = NumericProperty()


class ConversationsScreen(Screen):
    """
    A screen that displays all message histories.
    """

    name = StringProperty("conversations")

    def on_enter(self, *args) -> None:
        self._populate()

    def _populate(self) -> None:
        conversations = Conversation.all()
        for conv in conversations:
            if len(conv.members) != 2:
                # It's not a one-on-one conversation,
                # so it should be displayed in the group conversations.
                continue
            last_message = conv.messages.clear.get_last()
            if not last_message:
                # There are no messages in this conversation
                continue

            chat_item = ChatListItem()
            chat_item.friend_name = last_message.author.name
            chat_item.friend_avatar = last_message.author.pattern
            chat_item.message = last_message.value
            chat_item.timestamp = last_message.time_received
            chat_item.sender = last_message.author
            self.ids.chat_list.add_widget(chat_item)


class GroupListItem(MDCard):
    """
    A clickable chat item for the group chat timeline.
    """

    group_name = StringProperty()
    group_avatar = StringProperty()
    message = StringProperty()
    timestamp = StringProperty()


class GroupScreen(Screen):
    """
    A screen that display message history in groups.
    """

    name = StringProperty("group")

    def on_enter(self, *args) -> None:
        self._populate()

    def _populate(self) -> None:
        conversations = Conversation.all()
        for conv in conversations:
            if len(conv.members) == 2:
                # It's not a group conversation, so it should be displayed
                # in the one-to-one conversations screen.
                continue
            last_message = conv.messages.clear.get_last()
            if last_message is None:
                # There are no messages in this conversation
                continue

            chat_item = ChatListItem()
            chat_item.friend_name = last_message.author.name
            chat_item.friend_avatar = last_message.author.pattern
            chat_item.message = last_message.value
            chat_item.timestamp = last_message.time_received
            chat_item.sender = last_message.author
            self.ids.chat_list.add_widget(chat_item)


class ChatBubble(MDBoxLayout):
    """
    A chat bubble for the chat screen messages.
    """

    message = StringProperty()
    time = StringProperty()
    sender = StringProperty()


class ChatScreen(Screen):
    """
    A screen that display messages with a node.
    """

    name = StringProperty("active_chat")
    text = StringProperty()
    image = ObjectProperty()

    def __init__(self, conversation: Conversation, **kwargs):
        super().__init__(**kwargs)
        self.conversation = conversation

    def on_enter(self, *args):
        self._populate()

    def _populate(self) -> None:
        displayed: int = 0
        for message in self.conversation.clear_messages:
            chat_bubble = ChatBubble()
            chat_bubble.message = message.value
            chat_bubble.time = message.time_received
            chat_bubble.sender = message.author
            self.ids.message_list.add_widget(chat_bubble)
            displayed += 1

        if not displayed:
            Popup(title="Error", content=MDLabel(text="No message"))
            self.sm.switch_to(ConversationsScreen())


class SettingListItem(MDCard):
    """
    A settable setting item for the setting page.
    """

    setting_name = StringProperty()
    description = StringProperty()


class SettingsScreen(Screen):
    """
    A screen to tune Sami's settings.
    """

    name = StringProperty("settings")
    _settings = settings

    def on_enter(self, *args) -> None:
        self._populate()

    def _populate(self) -> None:
        pass


class MainApp(MDApp):
    wm: ScreenManager

    def __init__(self, **kwargs):
        Window.size = (320, 600)
        self.load_all_kv_files(str(Path(__file__).parent))
        super().__init__(**kwargs)
        self.networks = Networks()

    def __del__(self):
        global_stop_event.set()  # FIXME: remove?

    def build(self):
        """
        Initializes the application and returns the root widget.
        """
        self.theme_cls.primary_palette = "Purple"
        self.theme_cls.accent_palette = "Purple"
        self.theme_cls.accent_hue = "400"
        self.title = "Sami"
        self.wm = WindowManager(transition=NoTransition())

        # Initialize settings
        settings.application_theme = Setting(
            default_value="Light",
            description="Application color scheme to use",
        )

        self.wm.add_widget(StartScreen())

        class E(ExceptionHandler):
            """
            Handler with the responsibility of displaying all unhandled errors.
            """

            def handle_exception(self, inst: NameError):
                pop = ErrorPopup()
                pop.ids.error.text = format_err(inst)
                pop.open()
                return ExceptionManager.PASS

        ExceptionManager.add_handler(E())

        return self.wm

    def back_to_conversations(self):
        self.wm.switch_to(ConversationsScreen())

    def back_to_groups(self):
        self.wm.switch_to(GroupScreen())

    def switch_theme(self):
        """
        Switch the app's theme (light / dark).
        """
        if self.theme_cls.theme_style == "Dark":
            self.theme_cls.theme_style = "Light"
        else:
            self.theme_cls.theme_style = "Dark"
        settings.application_theme = self.theme_cls.theme_style
        settings.save()

    def create_chat(self, conv_id: int):
        """
        Get all messages and create a chat screen.
        """
        chat_screen = ChatScreen(Conversation.from_id(Identifier(conv_id)))
        chat_screen.text = conv_id  # FIXME
        chat_screen.image = ""  # FIXME
        self.wm.switch_to(chat_screen)

    def open_user_settings(self):
        self.wm.switch_to(SettingsScreen())

    def send(self):
        chat_screen = self.wm.get_screen("active_chat")
        text_input = chat_screen.ids.input.ids.value
        message = OwnMessage(content=text_input)
        conversation = Conversation.from_id()
        conversation.message.append(message)
        self.networks.broadcast(
            Request.new(
                MPP(
                    conversation_id=conversation.id,
                    message=message.encrypt(conversation.value),
                )
            )
        )
        # Clear input
        text_input.text = ""
