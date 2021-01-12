# -*- coding: UTF8 -*-

import os
import time
import logging

import wx  # pip install wxPython
import wx.xrc

from .node import Node
from .encryption import Encryption
from .message import Message, OwnMessage
from .utils import get_date_from_timestamp
from .wxdisplay import MainMenu, Conversation, CreateNewKeyPair, ReceivedMessages
from .validation import is_valid_node


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
    self.newChat_sbSizer

    And

    chat_container_bSizer
    by
    self.chatContainer_bSizer

    And

    recipient_bSizer
    by
    self.recipient_bSizer

    And

    chat_container_main_bSizer
    by
    self.chatContainerMain_bSizer

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
            known_nodes = self.master_node.databases.nodes.get_all_node_ids()

            # If we do not know any node.
            if len(known_nodes) > 0:
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

        def __init__(self, parent, master_node, network):
            ReceivedMessages.__init__(self, parent)
            self.parent = parent
            self.master_node = master_node
            self.network = network

            # Get the known peers' IDs.
            self.recipient_choices_indexes = self.network.nodes.get_all_node_ids()

            self.scroll_index = 0
            self.user_filter = ""
            # Selected node of the "new message" box.
            self.new_message_selected_node = None

            self.display_conversations(self.scroll_index, self.user_filter)

            self.show_new_message_box()

            # Add events
            self.recipient_choice.Bind(wx.EVT_CHOICE, self.update_new_message_recipient)
            self.new_chat_message_textCtrl.Bind(wx.EVT_TEXT, self.update_message)
            self.send_new_chat_button.Bind(wx.EVT_BUTTON, self.send_message_to_new_node)

        def __del__(self):
            self.parent.Show()

        def display_conversations(self, scroll_index: int, user_filter: str) -> None:
            """
            :param int scroll_index:
            :param str user_filter:
            """
            all_conv_ids = self.master_node.databases.conversations.get_all_conversations_ids()

            displayed_conversations = 0

            for index, node_id in enumerate(all_conv_ids):

                if not self.master_node.databases.conversations.does_conversation_exist_with_node(node_id):
                    continue

                # Apply filter (searchbar) and index (scrollbar)
                if user_filter not in node_id or index < scroll_index:
                    continue

                node_name = Node.derive_name(node_id)
                last_message = self.master_node.databases.conversations.get_last_conversation_message(
                    node_id,
                    self.master_node.rsa_private_key
                )
                last_message_date = get_date_from_timestamp(last_message.get_time_received())

                # Creates a new sizer to contain a conversation.
                node_sb_sizer = wx.StaticBoxSizer(wx.StaticBox(self, id=wx.ID_ANY, label=node_name), wx.HORIZONTAL)

                # Displays the last message of the conversation.
                self.conv_snippet_staticText = wx.StaticText(node_sb_sizer.GetStaticBox(), wx.ID_ANY,
                                                             last_message, wx.DefaultPosition, wx.DefaultSize,
                                                             wx.ST_ELLIPSIZE_END)
                self.conv_snippet_staticText.Wrap(-1)
                node_sb_sizer.Add(self.conv_snippet_staticText, 1, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

                self.conv_last_date_staticText = wx.StaticText(node_sb_sizer.GetStaticBox(), wx.ID_ANY,
                                                               last_message_date, wx.DefaultPosition,
                                                               wx.DefaultSize, 0)
                self.conv_last_date_staticText.Wrap(-1)
                node_sb_sizer.Add(self.conv_last_date_staticText, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL |
                                  wx.ALIGN_CENTER_HORIZONTAL, 5)

                # Adds an "open" button on the conversation sizer.
                self.conv_open_button = wx.Button(node_sb_sizer.GetStaticBox(), wx.ID_ANY, u"Open", wx.DefaultPosition,
                                                  wx.DefaultSize, wx.BU_EXACTFIT)
                node_sb_sizer.Add(self.conv_open_button, 0, wx.ALL, 5)
                self.messages_bSizer.Add(node_sb_sizer, 0, wx.ALL | wx.EXPAND, 5)

                # We're passing custom data using a lambda function
                self.conv_open_button.Bind(wx.EVT_BUTTON, lambda event: self.open_chat_id(event, node_id))

                displayed_conversations += 1

            # If one or more conversation are displayed
            if displayed_conversations > 0:
                # Adds a scrollbar
                self.conversations_scrollBar = wx.ScrollBar(self, wx.ID_ANY, pos=wx.Point(displayed_conversations,
                                                                                          displayed_conversations),
                                                            size=wx.DefaultSize, style=wx.SB_VERTICAL)
                self.messages_main_bSizer.Add(self.conversations_scrollBar, 0, wx.ALL | wx.EXPAND, 5)
                self.conversations_scrollBar.Bind(wx.EVT_SCROLL, self.scroll)

        def show_new_message_box(self):
            # Adds the choice box.
            self.recipient_choice = wx.Choice(self.new_message_sbSizer.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition,
                                              wx.DefaultSize, self.recipient_choices_names, 0)
            # Initialize the selection to 0.
            self.recipient_choice.SetSelection(0)
            # Add to the sizer (display).
            self.recipient_bSizer.Add(self.recipient_choice, 1, wx.ALL, 5)

            # Adds some text.
            message_staticText = wx.StaticText(self.new_message_sbSizer.GetStaticBox(), wx.ID_ANY, u"Message",
                                               wx.DefaultPosition, wx.DefaultSize, 0)
            # Add style
            message_staticText.Wrap(-1)
            # Add to the sizer (display).
            self.new_message_sbSizer.Add(message_staticText, 0, 0, 5)

            # Adds the textControl box, for the user to compose a message

            # Create a new message object.
            self.new_message = OwnMessage(self.master_node)
            self.new_chat_message_textCtrl = wx.TextCtrl(self.new_message_sbSizer.GetStaticBox(), wx.ID_ANY,
                                                         wx.EmptyString, wx.DefaultPosition, wx.DefaultSize,
                                                         wx.TE_AUTO_URL | wx.TE_BESTWRAP | wx.TE_CHARWRAP |
                                                         wx.TE_MULTILINE | wx.TE_NOHIDESEL | wx.TE_RICH |
                                                         wx.TE_RICH2 | wx.TE_WORDWRAP)
            self.new_chat_message_textCtrl.SetMinSize(wx.Size(-1, 50))
            self.new_message_sbSizer.Add(self.new_chat_message_textCtrl, 1, wx.ALL | wx.EXPAND, 5)

            # Add the "Send" button.
            self.send_new_chat_button = wx.Button(self.new_message_sbSizer.GetStaticBox(), wx.ID_ANY, u"Send",
                                                  wx.DefaultPosition, wx.DefaultSize, 0)
            self.new_message_sbSizer.Add(self.send_new_chat_button, 0, wx.ALL, 5)

        def scroll(self, event) -> None:
            print("scroll event type: ", type(event))
            self.scroll_index = event.GetPosition()
            self.display_conversations(self.scroll_index, self.user_filter)

        def filter_search(self, event) -> None:
            print("filter_search event type: ", type(event))
            self.user_filter = event.GetString()
            self.display_conversations(self.scroll_index, self.user_filter)

        def open_chat_id(self, event: wx.CommandEvent, node_id: str) -> None:
            print("open_chat_id event type: ", type(event))
            full_conversation = Controller.ConversationWrapper(self, self.master_node, node_id)
            full_conversation.Show()
            self.Hide()

        def update_new_message_recipient(self, event):
            self.new_message_recipient_id = self.recipient_choices_indexes[event.GetSelection()]

        def send_message_to_new_node(self, event):
            print("send_message_to_new_node event type: ", type(event))
            node_info: dict = self.network.nodes.get_contact_info(self.new_message_recipient_id)

            if not node_info:
                raise KeyError("Tried to send a message to a node we don't know ?!")
            if not is_valid_node(node_info):
                # We should delete the entry from the database.
                raise ValueError("Invalid node information from the database.")

            node = Node.from_dict(node_info)

            self.network.prepare_message_for_recipient(node, )
            self.network.send_message()
            self.master_node.databases.conversations.get_decrypted_aes(node.get_id_from_rsa_key(node.get_rsa_public_key()))
            # C'est ici qu'on va créer une clef AES pour la conversation. Note: pas de forward secrecy (pour l'instant).

        def update_message(self, event: wx.CommandEvent) -> None:
            """
            This function is called every time the new message txtCtrl is updated.
            Relatively inefficient performance-wise ; needs to be improved.
            """
            self.new_message.set_message(event.GetString())

    class ConversationWrapper(Conversation):

        def __init__(self, parent, master_node, recipient_node_id):
            Conversation.__init__(self, parent)
            self.parent = parent
            self.master_node = master_node
            self.recipient_id = recipient_node_id

        def __del__(self):
            self.parent.Show()

        def display_conversation(self):
            messages = self.master_node.databases.conversations.get_all_messages_of_conversation_raw(self.master_node.rsa_private_key,
                                                                                                     self.recipient_id)
            messages_wx_objects = {}
            for message in messages:
                msg_content = message.get_message()
                msg_received = get_date_from_timestamp(message.get_time_received())
                rcp_name = Node.derive_name(self.recipient_id)

                # Variable implementation, might need a dictionary implementation.

                message_1_sbSizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, rcp_name, wx.HORIZONTAL))

                self.message_content_1_staticText = wx.StaticText(message_1_sbSizer.GetStaticBox(), wx.ID_ANY,
                                                                  msg_content,
                                                                  wx.DefaultPosition, wx.DefaultSize, 0)
                self.message_content_1_staticText.Wrap(-1)

                message_1_sbSizer.Add(self.message_content_1_staticText, 1, wx.ALIGN_CENTER_VERTICAL, 5)

                self.message_timestamp_1_staticText = wx.StaticText(message_1_sbSizer.GetStaticBox(), wx.ID_ANY,
                                                                    msg_received, wx.DefaultPosition, wx.DefaultSize,
                                                                    0)
                self.message_timestamp_1_staticText.Wrap(-1)

                message_1_sbSizer.Add(self.message_timestamp_1_staticText, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

                self.messages_bSizer.Add(message_1_sbSizer, 0, wx.ALL | wx.EXPAND, 5)

        def send_message_to_current_node(self, event):
            event.Skip()
