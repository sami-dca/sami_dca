# -*- coding: UTF8 -*-

import os
import time
import logging

from typing import List

import wx  # pip install wxPython
import wx.xrc

from .node import Node
from .encryption import Encryption
from .validation import is_valid_node
from .message import Message, OwnMessage
from .utils import get_date_from_timestamp, resettable
from .wxdisplay import MainMenu, Conversation, CreateNewKeyPair, ReceivedMessages


class Controller:

    def __init__(self, master_node, network):
        self.master_node = master_node
        self.network = network
        self.app = wx.App()
        self.main_frame = self.MainMenuWrapper(None, self.master_node, self.network)
        self.main_frame.Show()

    """

    The following classes depend on their respective equivalent in the wxdisplay.py file.

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

    class MainMenuWrapper(MainMenu):

        def __init__(self, parent, master_node, network):
            MainMenu.__init__(self, parent)
            self.parent = parent
            self.master_node = master_node
            self.network = network
            self.keys_directory_path = None

        def set_server_display(self, status: bool) -> None:
            if status:
                text = "Up"
                colour = wx.Colour(0, 255, 0)
            else:
                text = "Down"
                colour = wx.Colour(255, 0, 0)

            self.server_status_staticText.SetForegroundColour(colour)
            self.server_status_staticText.SetLabel(text)

        def load_private_key(self, event: wx.FileDirPickerEvent) -> None:

            def get_directory(path: str) -> str:
                paths = path.split(os.sep)
                paths.pop(-1)  # Remove last item (the file name)
                return os.sep.join(paths)

            private_key_path = event.GetPath()

            self.keys_directory_path = get_directory(private_key_path)

            if not os.path.isfile(private_key_path):
                return

            rsa_private_key = Encryption.import_rsa_private_key_from_file(private_key_path)
            if not rsa_private_key:
                self.private_key_filePicker.SetPath(u"Invalid private key file !")
                return

            # Disable the file picker, as the private key is loaded.
            # We do not want the user to change the private key of this instance.
            self.private_key_filePicker.Enable(False)
            self.master_node.initialize(rsa_private_key)
            self.node_name_staticText.SetLabel(self.master_node.name)
            # Enable the conversations button.
            self.show_conversations_Button.Enable(True)
            # Enable the export pubkey button
            self.export_pubkey_button.Enable(True)

        def export_pubkey(self, event: wx.CommandEvent) -> None:
            assert self.keys_directory_path is not None
            self.master_node.export_rsa_public_key_to_file(self.master_node.rsa_public_key, self.keys_directory_path)
            logging.info(f'Exported public key to {self.keys_directory_path!r}')

        def open_pair_creation_window(self, event: wx.CommandEvent) -> None:
            keygen_window = Controller.CreateNewKeyPairWrapper(self, self.master_node, self.network)
            keygen_window.Show()
            self.Hide()

        def show_conversations(self, event: wx.CommandEvent) -> None:
            possible_conversations = self.master_node.databases.conversations.get_all_available_conversations_ids()

            # If we do not know any node.
            if len(possible_conversations) > 0:
                # Display the conversations window.
                received_messages_window = Controller.ReceivedMessagesWrapper(self, self.master_node, self.network)
                received_messages_window.Show()
                self.Hide()
            else:
                # Get the current label of the button
                label = self.show_conversations_Button.GetLabel()
                # Set a new one
                self.show_conversations_Button.SetLabel("We don't know any nodes !")
                # Wait for a moment ; long enough for the user to be able to read the label.
                time.sleep(2)
                # Set the label back to its original value
                self.show_conversations_Button.SetLabel(label)

    class CreateNewKeyPairWrapper(CreateNewKeyPair):

        def __init__(self, parent, master_node, network):
            CreateNewKeyPair.__init__(self, parent)
            self.parent = parent
            self.master_node = master_node
            self.network = network
            self.key_pair_location_dirPicker.SetPath(os.path.dirname(os.path.abspath(__file__)))

        def __del__(self):
            self.parent.Show()

        def create_key_pair(self, event: wx.FileDirPickerEvent):
            rsa_private_key = Encryption.create_rsa_pair()
            location = event.GetPath()
            self.master_node.export_rsa_private_key_to_file(rsa_private_key, location)

    class ReceivedMessagesWrapper(ReceivedMessages):

        @resettable
        def __init__(self, parent, master_node, network):
            ReceivedMessages.__init__(self, parent)
            self.parent = parent
            self.master_node = master_node
            self.network = network

            # Get the known peers' IDs.
            available_nodes = self.get_available_nodes()
            # Exclude self
            own_node_id = self.master_node.get_id()
            if own_node_id in available_nodes:
                available_nodes.pop(available_nodes.index(own_node_id))
            self.recipient_choices_ids = available_nodes

            self.scroll_index = 0
            self.user_filter = ""
            # Selected node of the "new message" box.
            # By default the first one, with index 0.
            # If the list if empty however, we'll just won't set the var
            # and won't display the new message box.
            if len(self.recipient_choices_ids) > 0:
                self.new_message = None
                self.new_message_recipient_id = self.recipient_choices_ids[0]
                self.show_new_message_box()

            self.display_conversations(self.scroll_index, self.user_filter)

        def __del__(self):
            self.parent.Show()

        def get_available_nodes(self) -> List[str]:
            """
            Returns all the nodes IDs with which we have not started a conversation, but we can.
            """
            all_ids = self.master_node.databases.conversations.get_all_available_conversations_ids()
            existing_conversations = self.master_node.databases.conversations.get_all_conversations_ids()
            available_nodes = all_ids.difference(existing_conversations)
            return list(available_nodes)

        def display_conversations(self, scroll_index: int, user_filter: str) -> None:
            """
            :param int scroll_index:
            :param str user_filter:
            """
            self.reset()

            all_conv_ids = self.master_node.databases.conversations.get_all_conversations_ids()

            displayed_conversations = 0

            for index, node_id in enumerate(all_conv_ids):

                if not self.master_node.databases.conversations.does_conversation_exist_with_node(node_id):
                    continue

                # Apply filter (searchbar) and index (scrollbar)
                if user_filter not in node_id or index < scroll_index:
                    continue

                node_name = Node.derive_name(node_id)
                last_message: Message = self.master_node.databases.conversations.get_last_conversation_message(node_id)

                if not last_message:
                    continue

                last_message_date = get_date_from_timestamp(last_message.get_time_received())

                # Creates a new sizer to contain a conversation.
                node_sb_sizer = wx.StaticBoxSizer(wx.StaticBox(self, id=wx.ID_ANY, label=node_name), wx.HORIZONTAL)

                # Displays the last message of the conversation.
                conv_snippet_static_text = wx.StaticText(node_sb_sizer.GetStaticBox(), wx.ID_ANY,
                                                         last_message.get_message(), wx.DefaultPosition,
                                                         wx.DefaultSize, wx.ST_ELLIPSIZE_END)
                conv_snippet_static_text.Wrap(-1)
                node_sb_sizer.Add(conv_snippet_static_text, 1, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

                conv_last_date_static_text = wx.StaticText(node_sb_sizer.GetStaticBox(), wx.ID_ANY,
                                                           last_message_date, wx.DefaultPosition,
                                                           wx.DefaultSize, 0)
                conv_last_date_static_text.Wrap(-1)
                node_sb_sizer.Add(conv_last_date_static_text, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL |
                                  wx.ALIGN_CENTER_HORIZONTAL, 5)

                # Adds an interaction button on the conversation sizer.
                open_conversation_button_label = u"Open"
                conv_open_button = wx.Button(node_sb_sizer.GetStaticBox(), wx.ID_ANY, open_conversation_button_label,
                                             wx.DefaultPosition, wx.DefaultSize, wx.BU_EXACTFIT)
                node_sb_sizer.Add(conv_open_button, 0, wx.ALL, 5)
                self.received_messages_bSizer.Add(node_sb_sizer, 0, wx.ALL | wx.EXPAND, 5)

                # We're passing custom data using a lambda function
                conv_open_button.Bind(wx.EVT_BUTTON, lambda event: self.open_chat_id(event, node_id))

                displayed_conversations += 1

            # If one or more conversation are displayed
            if displayed_conversations > 0:
                # Adds a scrollbar
                scroll_bar = wx.ScrollBar(self, wx.ID_ANY,
                                          pos=wx.Point(displayed_conversations, displayed_conversations),
                                          size=wx.DefaultSize, style=wx.SB_VERTICAL)
                self.chat_container_main_bSizer.Add(scroll_bar, 0, wx.ALL | wx.EXPAND, 5)
                scroll_bar.Bind(wx.EVT_SCROLL, self.scroll)

        def show_new_message_box(self) -> None:
            recipient_choices_names = [Node.derive_name(i) for i in self.recipient_choices_ids]

            # Adds the choice box.
            recipient_choice = wx.Choice(self.new_chat_sbSizer.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition,
                                         wx.DefaultSize, recipient_choices_names, 0)
            # Initialize the selection to 0.
            recipient_choice.SetSelection(0)
            # Add to the sizer (display).
            self.new_chat_sbSizer.Add(recipient_choice, 1, wx.ALL, 5)

            # Adds box description
            description = u"Message"
            message_static_text = wx.StaticText(self.new_chat_sbSizer.GetStaticBox(), wx.ID_ANY,
                                                description, wx.DefaultPosition, wx.DefaultSize, 0)
            message_static_text.Wrap(-1)
            self.new_chat_sbSizer.Add(message_static_text, 0, 0, 5)

            # Adds the textControl box, for the user to compose a message

            self.new_message = OwnMessage(self.master_node)
            new_chat_message_text_ctrl = wx.TextCtrl(self.new_chat_sbSizer.GetStaticBox(), wx.ID_ANY,
                                                     wx.EmptyString, wx.DefaultPosition, wx.DefaultSize,
                                                     wx.TE_AUTO_URL | wx.TE_BESTWRAP | wx.TE_CHARWRAP |
                                                     wx.TE_MULTILINE | wx.TE_NOHIDESEL | wx.TE_RICH |
                                                     wx.TE_RICH2 | wx.TE_WORDWRAP)
            new_chat_message_text_ctrl.SetMinSize(wx.Size(-1, 50))
            self.new_chat_sbSizer.Add(new_chat_message_text_ctrl, 1, wx.ALL | wx.EXPAND, 5)

            # Add the submit button.
            button_label = u"Send"
            send_new_chat_button = wx.Button(self.new_chat_sbSizer.GetStaticBox(), wx.ID_ANY,
                                             button_label, wx.DefaultPosition, wx.DefaultSize, 0)
            self.new_chat_sbSizer.Add(send_new_chat_button, 0, wx.ALL, 5)

            # Add events
            recipient_choice.Bind(wx.EVT_CHOICE, self.update_new_message_recipient)
            new_chat_message_text_ctrl.Bind(wx.EVT_TEXT, self.update_message)
            send_new_chat_button.Bind(wx.EVT_BUTTON, self.send_message_to_new_node)

        def scroll(self, event: wx.ScrollEvent) -> None:
            self.scroll_index = event.GetPosition()
            self.display_conversations(self.scroll_index, self.user_filter)

        def filter_search(self, event) -> None:
            print("filter_search event type: ", type(event))
            self.user_filter = event.GetString()
            self.display_conversations(self.scroll_index, self.user_filter)

        def open_chat_id(self, event: wx.CommandEvent, node_id: str) -> None:
            full_conversation = Controller.ConversationWrapper(self, self.master_node, self.network, node_id)
            full_conversation.Show()
            self.Hide()
            event.Skip()

        def update_new_message_recipient(self, event: wx.CommandEvent) -> None:
            self.new_message_recipient_id = self.recipient_choices_ids[event.GetSelection()]

        def send_message_to_new_node(self, event: wx.CommandEvent) -> None:
            node_info: dict = self.master_node.databases.nodes.get_node_info(self.new_message_recipient_id)

            if not node_info:
                raise KeyError("Tried to send a message to a node we don't know ?!")
            if not is_valid_node(node_info):
                # TODO: We should delete the entry from the database.
                raise ValueError(f"Invalid node information in the database for {self.new_message_recipient_id!r}")

            node = Node.from_dict(node_info)

            if not node:
                raise InterruptedError('Could not create node object')

            # TODO: Should be sent to a MP queue ; as of now, the window freezes when clicking "Send".
            self.network.prepare_and_send_own_message(node, self.new_message)

            event.Skip()

        def update_message(self, event: wx.CommandEvent) -> None:
            self.new_message.set_message(event.GetString())

    class ConversationWrapper(Conversation):

        def __init__(self, parent, master_node, network, recipient_node_id):
            Conversation.__init__(self, parent)
            self.parent = parent
            self.network = network
            self.master_node = master_node
            self.recipient_id = recipient_node_id
            self.new_message = OwnMessage(self.master_node)
            self.display_conversation()

        def __del__(self):
            self.parent.Show()

        def display_conversation(self) -> None:
            messages = self.master_node.databases.conversations.get_all_messages_of_conversation(self.recipient_id)

            for message in messages:
                content = message.get_message()
                received_timestamp = get_date_from_timestamp(message.get_time_received())
                rcp_name = Node.derive_name(self.recipient_id)

                message_sb_sizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, rcp_name), wx.HORIZONTAL)

                message_content_static_text = wx.StaticText(message_sb_sizer.GetStaticBox(), wx.ID_ANY,
                                                            content, wx.DefaultPosition, wx.DefaultSize, 0)
                message_content_static_text.Wrap(-1)

                message_sb_sizer.Add(message_content_static_text, 1, wx.ALIGN_CENTER_VERTICAL, 5)

                message_timestamp_static_text = wx.StaticText(message_sb_sizer.GetStaticBox(), wx.ID_ANY,
                                                              received_timestamp, wx.DefaultPosition,
                                                              wx.DefaultSize, 0)
                message_timestamp_static_text.Wrap(-1)

                message_sb_sizer.Add(message_timestamp_static_text, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

                self.messages_bSizer.Add(message_sb_sizer, 0, wx.ALL | wx.EXPAND, 5)

        def update_new_message(self, event: wx.CommandEvent) -> None:
            self.new_message.set_message(event.GetString())

        def send_message_to_current_node(self, event: wx.CommandEvent) -> None:
            node_info: dict = self.master_node.databases.nodes.get_node_info(self.recipient_id)

            if not node_info:
                raise KeyError("Tried to send a message to a node we don't know ?!")
            if not is_valid_node(node_info):
                # TODO: We should delete the entry from the database.
                raise ValueError(f"Invalid node information in the database for {self.recipient_id!r}")

            node = Node.from_dict(node_info)

            if not node:
                raise InterruptedError('Could not create node object')

            # TODO: Should be sent to a MP queue ; as of now, the window freezes when clicking "Send".
            self.network.prepare_and_send_own_message(node, self.new_message)

            event.Skip()
