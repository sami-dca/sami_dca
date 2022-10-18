import logging
from pathlib import Path

from kivy.base import ExceptionHandler, ExceptionManager
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import DictProperty, ObjectProperty, StringProperty

# from kivy.logger import Logger
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import NoTransition, Screen, ScreenManager
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel

from ..config import Setting, settings
from ..database.private import (
    ConversationsDatabase,
    ConversationsMembershipsDatabase,
    MessagesDatabase,
)
from ..messages import EncryptedMessage
from ..nodes.own import is_private_key_loaded
from ..utils import format_err

Window.size = (320, 600)


def load_kv_files(directory: Path):
    """
    Recursively search for kivy (.kv) files in a directory, and load them.
    """
    for path in directory.iterdir():
        if path.is_dir():
            load_kv_files(path)
        elif path.is_file() or path.is_symlink():
            if path.suffix == ".kv":
                logging.debug(f"Loaded {path}")
                Builder.load_file(str(path))


load_kv_files(Path(__file__).parent)


class WindowManager(ScreenManager):
    pass


class ErrorPopup(Popup):
    pass


class LoadKeyScreen(Screen):
    """
    A screen prompting the user to load a key!
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
    msg = StringProperty()
    timestamp = StringProperty()
    friend_avatar = StringProperty()
    profile = DictProperty()


class ConversationsScreen(Screen):
    """
    A screen that displays all message histories.
    """

    name = StringProperty("conversations")

    def on_enter(self, *args) -> None:
        self._populate()

    def _populate(self) -> None:
        conversations = ConversationsDatabase().get_all_conversations()
        conv_members_db = ConversationsMembershipsDatabase()
        messages_db = MessagesDatabase()
        for conv in conversations:
            members = conv_members_db.get_members_of_conversation(conv.uid)
            if len(members) != 2:
                # It's not a one-on-one conversation,
                # so it should be displayed in the group conversations.
                continue
            last_message = EncryptedMessage.from_dbo(
                messages_db.get_last_message(conv.uid)
            ).to_clear()
            if last_message is None:
                continue

            chat_item = ChatListItem()
            chat_item.friend_name = "Friend"  # FIXME
            chat_item.friend_avatar = "Image"  # FIXME
            chat_item.msg = last_message.content
            chat_item.timestamp = last_message.time_received
            chat_item.sender = last_message.author
            self.ids.chat_list.add_widget(chat_item)


class GroupListItem(MDCard):
    """
    A clickable chat item for the group chat timeline.
    """

    group_name = StringProperty()
    group_avatar = StringProperty()
    friend_msg = StringProperty()
    timestamp = StringProperty()


class GroupScreen(Screen):
    """
    A screen that display message history in groups.
    """

    name = StringProperty("group")

    def on_enter(self, *args) -> None:
        self._populate()

    def _populate(self) -> None:
        conversations = ConversationsDatabase().get_all_conversations()
        conv_members_db = ConversationsMembershipsDatabase()
        messages_db = MessagesDatabase()
        for conv in conversations:
            members = conv_members_db.get_members_of_conversation(conv.uid)
            if len(members) == 2:
                # It's not a group conversation, so it should be displayed
                # in the one-to-one conversations screen.
                continue
            last_message = EncryptedMessage.from_dbo(
                messages_db.get_last_message(conv.uid)
            ).to_clear()
            if last_message is None:
                continue

            chat_item = ChatListItem()
            chat_item.friend_name = "Group"  # FIXME
            chat_item.friend_avatar = "Image"  # FIXME
            chat_item.msg = last_message.content
            chat_item.timestamp = last_message.time_received
            chat_item.sender = last_message.author
            self.ids.chat_list.add_widget(chat_item)


class ChatBubble(MDBoxLayout):
    """
    A chat bubble for the chat screen messages.
    """

    profile = DictProperty()
    msg = StringProperty()
    time = StringProperty()
    sender = StringProperty()


class ChatScreen(Screen):
    """
    A screen that display messages with a node.
    """

    name = StringProperty("active_chat")
    text = StringProperty()
    image = ObjectProperty()

    def __init__(self, conversation_uid, **kwargs):
        super().__init__(**kwargs)
        self.conversation_uid = conversation_uid

    def on_enter(self, *args):
        self._populate()

    def _populate(self) -> None:
        displayed: int = 0
        for message in MessagesDatabase().get_messages(self.conversation_uid):
            if message is None:
                continue
            chat_msg = ChatBubble()
            chat_msg.msg = message.content
            chat_msg.time = message.time_received
            chat_msg.sender = message.author
            self.ids.msg_list.add_widget(chat_msg)
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
    """
    The main App class using KivyMD's properties.
    """

    wm: ScreenManager

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
            def handle_exception(self, inst: NameError):
                print(inst)
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

    def create_chat(self, conversation_uid):
        """
        Get all messages and create a chat screen.
        """
        chat_screen = ChatScreen(conversation_uid)
        chat_screen.text = conversation_uid  # FIXME
        chat_screen.image = ""  # FIXME
        self.wm.switch_to(chat_screen)

    def open_user_settings(self):
        self.wm.switch_to(SettingsScreen())

    def send(self):
        chat_screen = self.wm.get_screen("active_chat")
        text_input = chat_screen.ids.input.ids.content
        print(text_input.text)
        # Clear input
        text_input.text = ""
