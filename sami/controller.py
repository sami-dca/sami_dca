import time

from . import wxdisplay

from pathlib import Path
from typing import List, Optional

import wx  # pip install wxPython
import wx.xrc

from .network import Networks
from .nodes.own import MasterNode
from .network.requests import MPP
from .utils import get_date_from_timestamp
from .messages import OwnMessage, Conversation
from .cryptography.asymmetric import PrivateKey
from .database.private import ConversationsDatabase

import logging as _logging
logger = _logging.getLogger('ui')


def get_valid_conversations() -> List[Conversation]:
    existing_conversations_dbo = ConversationsDatabase().get_all_conversations()
    existing_conversations = [
        Conversation.from_dbo(dbo)
        for dbo in existing_conversations_dbo
    ]
    return [
        conversation for conversation in existing_conversations
        if conversation.key_dbo is not None
    ]


def get_available_conversations() -> List[Conversation]:
    """
    Returns all the nodes IDs with which we have
    not started a conversation yet.
    """
    return [
        conversation for conversation in get_valid_conversations()
        if len(conversation.messages) > 0
    ]


class Controller:

    def __init__(self):
        self.app = wx.App()
        self.main_frame = self.MainMenu(None)
        self.main_frame.Show()

    """

    The following classes depend on their respective equivalent 
    in the wxdisplay.py file.

    When generating a new display from wxFormBuilder, replace every instance of

    you will also need to change all the instances of

    new_chat_sbSizer
    by
    self.new_chat_sbSizer

    And

    chat_container_main_bSizer
    by
    self.chat_container_main_bSizer

    And
    
    received_messages_bSizer
    by
    self.received_messages_bSizer
    
    And
    
    messages_bSizer
    by
    self.messages_bSizer

    """

    class MainMenu(wxdisplay.MainMenu):

        def __init__(self, parent):
            wxdisplay.MainMenu.__init__(self, parent)
            self.master_node: Optional[MasterNode] = None
            self.keys_directory_path: Optional[Path] = None

        def set_server_display(self, status: bool) -> None:
            if status:
                text = "Up"
                colour = wx.Colour(0, 127, 0)
            else:
                text = "Down"
                colour = wx.Colour(127, 0, 0)

            self.server_status_staticText.SetForegroundColour(colour)
            self.server_status_staticText.SetLabel(text)

        def load_private_key(self, event: wx.FileDirPickerEvent) -> None:
            private_key_path: Path = Path(event.GetPath())
            self.keys_directory_path: Path = private_key_path.parent

            if not private_key_path.is_file():
                # File does not exist
                self.private_key_filePicker.SetPath(
                    "Specified file does not exist !"
                )
                return

            rsa_private_key = PrivateKey.from_file(private_key_path)
            if rsa_private_key is None:
                # Invalid private key information in the file
                self.private_key_filePicker.SetPath(
                    "Invalid private key file !"
                )
                return

            # Now that the private key is loaded, we disable the file picker.
            # We forbid changing the private key of this client instance.
            self.private_key_filePicker.Enable(False)
            self.master_node: MasterNode = MasterNode(rsa_private_key)
            self.node_name_staticText.SetLabel(self.master_node.name)
            # Enable the buttons:
            # - Conversations
            self.show_conversations_Button.Enable(True)
            # - Pubkey export
            self.export_pubkey_button.Enable(True)

        def export_pubkey(self, event: wx.CommandEvent) -> None:
            assert self.master_node is not None
            self.master_node.export_public_key(self.keys_directory_path)
            logger.info(f'Exported public key '
                        f'to {str(self.keys_directory_path)!r}')

        def open_pair_creation_window(self, event: wx.CommandEvent) -> None:
            Controller.CreateNewKeyPair(self).Show()
            self.Hide()

        def show_conversations(self, event: wx.CommandEvent) -> None:
            possible_conversations = get_available_conversations()

            if len(possible_conversations) > 0:
                Controller.ReceivedMessages(parent=self).Show()
                self.Hide()
            else:
                temp_label = "We don't know any nodes !"
                original_label = self.show_conversations_Button.GetLabel()
                self.show_conversations_Button.SetLabel(temp_label)
                time.sleep(2)
                self.show_conversations_Button.SetLabel(original_label)

    class CreateNewKeyPair(wxdisplay.CreateNewKeyPair):

        def __init__(self, parent):
            wxdisplay.CreateNewKeyPair.__init__(self, parent)
            self.parent = parent

        def __del__(self):
            self.parent.Show()

        def create_key_pair(self, event: wx.FileDirPickerEvent):
            dst_dir = Path(event.GetPath())
            rsa_private_key = PrivateKey.new()
            master_node = MasterNode(rsa_private_key)
            master_node.export_private_key(dst_dir)

    class ReceivedMessages(wxdisplay.ReceivedMessages):

        def __init__(self, parent):
            wxdisplay.ReceivedMessages.__init__(self, parent)
            self.parent = parent
            self.networks: Networks = Networks()
            self.conversation_choices: Optional[List[Conversation]] = None
            self.scroll_index = 0
            self.user_filter = ""
            self.new_message_text: Optional[str] = None
            self.new_msg_conv: Optional[Conversation] = None

        def __del__(self):
            self.parent.Show()

        def display(self) -> None:
            self.conversation_choices = get_available_conversations()

            if len(self.conversation_choices) > 0:
                self.new_msg_conv = self.conversation_choices[0]
                self.show_new_message_box()

            self.display_conversations(self.scroll_index, self.user_filter)

        def display_conversations(self, scroll_index: int,
                                  user_filter: str) -> None:
            conversations_dbo = ConversationsDatabase().get_all_conversations()
            conversations = [
                Conversation.from_dbo(conv_dbo)
                for conv_dbo in conversations_dbo
            ]

            displayed_conversations = 0

            for index, conv in enumerate(conversations):
                members_names = [node.name for node in conv.members]
                conv_name = ', '.join(members_names)

                # TODO: Apply filter (searchbar) and index (scrollbar)
                if user_filter not in conv.id or index < scroll_index:
                    continue

                last_message = conv.messages[-1]
                if last_message is None:
                    continue

                last_message_date = get_date_from_timestamp(
                    last_message.time_received)

                node_sb_sizer = wx.StaticBoxSizer(
                    wx.StaticBox(self, id=wx.ID_ANY, label=conv_name),
                    wx.HORIZONTAL
                )

                # Displays the last message of the conversation.
                conv_snippet_static_text = wx.StaticText(
                    node_sb_sizer.GetStaticBox(), wx.ID_ANY,
                    last_message.content, wx.DefaultPosition,
                    wx.DefaultSize, wx.ST_ELLIPSIZE_END
                )
                conv_snippet_static_text.Wrap(-1)
                node_sb_sizer.Add(conv_snippet_static_text, 1,
                                  wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

                conv_last_date_static_text = wx.StaticText(
                    node_sb_sizer.GetStaticBox(), wx.ID_ANY, last_message_date,
                    wx.DefaultPosition, wx.DefaultSize, 0
                )
                conv_last_date_static_text.Wrap(-1)
                node_sb_sizer.Add(conv_last_date_static_text, 0,
                                  wx.ALL | wx.ALIGN_CENTER_VERTICAL |
                                  wx.ALIGN_CENTER_HORIZONTAL, 5)

                # Adds an interaction button on the conversation sizer.
                open_conversation_button_label = u"Open"
                conv_open_button = wx.Button(
                    node_sb_sizer.GetStaticBox(), wx.ID_ANY,
                    open_conversation_button_label, wx.DefaultPosition,
                    wx.DefaultSize, wx.BU_EXACTFIT
                )
                node_sb_sizer.Add(conv_open_button, 0, wx.ALL, 5)
                self.received_messages_bSizer.Add(node_sb_sizer, 0,
                                                  wx.ALL | wx.EXPAND, 5)

                # We're passing custom data using a lambda function
                conv_open_button.Bind(
                    wx.EVT_BUTTON,
                    lambda event: self.open_chat_id(event, conv)
                )

                displayed_conversations += 1

            # If one or more conversation are displayed
            if displayed_conversations > 0 and False:  # Disabled
                # Adds a scrollbar
                scroll_bar = wx.ScrollBar(
                    self, wx.ID_ANY, pos=wx.Point(displayed_conversations,
                                                  displayed_conversations),
                    size=wx.DefaultSize, style=wx.SB_VERTICAL
                )
                self.chat_container_main_bSizer.Add(scroll_bar, 0,
                                                    wx.ALL | wx.EXPAND, 5)
                scroll_bar.Bind(wx.EVT_SCROLL, self.scroll)

        def show_new_message_box(self) -> None:

            new_chat_sb_sizer = wx.StaticBoxSizer(
                wx.StaticBox(self, wx.ID_ANY, u"New conversation"),
                wx.VERTICAL
            )

            self.recipient_bSizer = wx.BoxSizer(wx.HORIZONTAL)

            recipient_static_text = wx.StaticText(
                new_chat_sb_sizer.GetStaticBox(), wx.ID_ANY, u"Send to:",
                wx.DefaultPosition, wx.DefaultSize, 0
            )
            recipient_static_text.Wrap(-1)

            self.recipient_bSizer.Add(recipient_static_text, 0,
                                      wx.ALIGN_CENTER_VERTICAL, 5)

            new_chat_sb_sizer.Add(self.recipient_bSizer, 0, wx.EXPAND, 5)

            self.received_messages_bSizer.Add(new_chat_sb_sizer, 0,
                                              wx.EXPAND, 5)

            recipient_choices_names = [
                ', '.join([member.name for member in conv.members])
                for conv in self.conversation_choices
            ]

            recipient_choice = wx.Choice(
                new_chat_sb_sizer.GetStaticBox(), wx.ID_ANY,
                wx.DefaultPosition, wx.DefaultSize, recipient_choices_names, 0
            )
            recipient_choice.SetSelection(0)
            new_chat_sb_sizer.Add(recipient_choice, 1, wx.ALL, 5)

            description = u"Message"
            message_static_text = wx.StaticText(
                new_chat_sb_sizer.GetStaticBox(), wx.ID_ANY, description,
                wx.DefaultPosition, wx.DefaultSize, 0
            )
            message_static_text.Wrap(-1)
            new_chat_sb_sizer.Add(message_static_text, 0, 0, 5)

            # Adds the textControl box, for the user to compose a message

            self.new_message_text = ''
            new_chat_message_text_ctrl = wx.TextCtrl(
                new_chat_sb_sizer.GetStaticBox(), wx.ID_ANY,
                wx.EmptyString, wx.DefaultPosition, wx.DefaultSize,
                wx.TE_AUTO_URL | wx.TE_BESTWRAP | wx.TE_CHARWRAP |
                wx.TE_MULTILINE | wx.TE_NOHIDESEL | wx.TE_RICH |
                wx.TE_RICH2 | wx.TE_WORDWRAP
            )
            new_chat_message_text_ctrl.SetMinSize(wx.Size(-1, 50))
            new_chat_sb_sizer.Add(new_chat_message_text_ctrl, 1,
                                  wx.ALL | wx.EXPAND, 5)

            # Add the submit button.
            button_label = u"Send"
            send_new_chat_button = wx.Button(
                new_chat_sb_sizer.GetStaticBox(), wx.ID_ANY, button_label,
                wx.DefaultPosition, wx.DefaultSize, 0
            )
            new_chat_sb_sizer.Add(send_new_chat_button, 0, wx.ALL, 5)

            # Add events
            recipient_choice.Bind(wx.EVT_CHOICE, self.update_new_msg_recipient)
            new_chat_message_text_ctrl.Bind(wx.EVT_TEXT, self.update_message)
            send_new_chat_button.Bind(wx.EVT_BUTTON, self.send_msg_to_new_conv)

        def scroll(self, event: wx.ScrollEvent) -> None:
            self.scroll_index = event.GetPosition()
            self.display_conversations(self.scroll_index, self.user_filter)

        def filter_search(self, event) -> None:
            print("filter_search event type: ", type(event))
            self.user_filter = event.GetString()
            self.display_conversations(self.scroll_index, self.user_filter)

        def open_chat_id(self, event: wx.CommandEvent,
                         conversation: Conversation) -> None:
            Controller.Conversations(self, conversation).Show()
            self.Hide()
            event.Skip()

        def update_new_msg_recipient(self, event: wx.CommandEvent) -> None:
            selected = event.GetSelection()
            self.new_msg_conv = self.conversation_choices[selected]

        def send_msg_to_new_conv(self, event: wx.CommandEvent) -> None:
            new_message = OwnMessage(conversation=self.new_msg_conv)
            new_message.content = self.new_message_text
            req = MPP.new(new_message.to_encrypted())
            self.networks.map(lambda net: net.broadcast(req))
            event.Skip()

        def update_message(self, event: wx.CommandEvent) -> None:
            self.new_message_text = event.GetString()

    class Conversations(wxdisplay.Conversations):

        def __init__(self, parent, conversation: Conversation):
            wxdisplay.Conversations.__init__(self, parent)
            self.parent = parent
            self.networks: Networks = Networks()
            self.master_node: MasterNode = MasterNode()
            self.conversation = conversation
            self.new_message = OwnMessage(conversation=conversation)
            self.display_conversation()

        def __del__(self):
            self.parent.Show()

        def display_conversation(self) -> None:
            for message in self.conversation.messages:
                received_time = get_date_from_timestamp(message.time_received)

                message_sb_sizer = wx.StaticBoxSizer(
                    wx.StaticBox(self, wx.ID_ANY, message.author.name),
                    wx.HORIZONTAL
                )

                message_content_static_text = wx.StaticText(
                    message_sb_sizer.GetStaticBox(), wx.ID_ANY,
                    message.content, wx.DefaultPosition, wx.DefaultSize, 0
                )
                message_content_static_text.Wrap(-1)

                message_sb_sizer.Add(message_content_static_text, 1,
                                     wx.ALIGN_CENTER_VERTICAL, 5)

                message_timestamp_static_text = wx.StaticText(
                    message_sb_sizer.GetStaticBox(), wx.ID_ANY,
                    received_time, wx.DefaultPosition, wx.DefaultSize, 0
                )
                message_timestamp_static_text.Wrap(-1)

                message_sb_sizer.Add(message_timestamp_static_text, 0,
                                     wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

                self.messages_bSizer.Add(message_sb_sizer, 0,
                                         wx.ALL | wx.EXPAND, 5)

        def update_new_message(self, event: wx.CommandEvent) -> None:
            self.new_message.content = event.GetString()

        def send_message(self, event: wx.CommandEvent) -> None:
            req = MPP.new(encrypted_message=self.new_message.to_encrypted())
            self.new_message = OwnMessage(conversation=self.conversation)
            self.networks.map(lambda net: net.broadcast(req))
            event.Skip()
