# -*- coding: UTF8 -*-

import os
import time

import wx
import wx.xrc

from .node import Node
from .utils import Utils
from .message import Message
from .encryption import Encryption
from .wxdisplay import MainMenu, Conversation, CreateNewKeyPair, ReceivedMessages


class Controller:

    def __init__(self, master_node, network):
        self.master_node = master_node
        self.network = network
        self.app = wx.App()
        self.mainFrame = self.MainMenuWrapper(None, self.master_node, self.network)
        self.mainFrame.Show()

    """

    The following classes depend on their respective equivalent in the wxdisplay.py file.

    When generating a new display from wxFormBuilder, replace every instance of

    you will also need to change all the instances of

    newChat_sbSizer
    by
    self.newChat_sbSizer

    And

    chatContainer_bSizer
    by
    self.chatContainer_bSizer

    And

    recipient_bSizer
    by
    self.recipient_bSizer

    And

    chatContainerMain_bSizer
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
            self.keys_directory = None

        def set_server_display(self, status: bool) -> None:
            if status:
                text = "Up"
                colour = wx.Colour(0, 255, 0)
            else:
                text = "Down"
                colour = wx.Colour(255, 0, 0)

            self.serverStatus_staticText.SetForegroundColour(colour)
            self.serverStatus_staticText.SetLabel(text)

        def load_private_key(self, event) -> None:
            print("load_private_key event type: ", type(event))
            self.keys_directory = event.GetPath()

            if not os.path.isfile(self.keys_directory):
                return

            rsa_private_key = Encryption.import_rsa_private_key_from_file(self.keys_directory)
            if not rsa_private_key:
                self.privateKey_filePicker.SetPath(u"Invalid private key file !")
                return

            # Disable the file picker, as the private key is loaded.
            # We do not want the user to change the private key of this instance.
            self.privateKey_filePicker.Enable(False)
            self.master_node.set_rsa_private_key(rsa_private_key)
            self.master_node.__initialize()
            self.nodeName_staticText.SetLabel(self.master_node.name)
            # Enable the conversations button.
            self.showConversations_Button.Enable(True)
            # Enable the export pubkey button
            self.exportPubkey_button.Enable(True)

        def export_pubkey(self, event) -> None:
            print("export_pubkey event type: ", type(event))
            assert self.keys_directory is not None
            Encryption.export_rsa_public_key_to_file(self.master_node.rsa_private_key, self.keys_directory)

        def open_pair_creation_window(self, event: wx.CommandEvent) -> None:
            print("open_pair_creation_window event type: ", type(event))
            keygen_window = Controller.CreateNewKeyPairWrapper(self, self.master_node, self.network)
            keygen_window.Show()
            self.Hide()

        def show_conversations(self, event: wx.CommandEvent) -> None:
            print("show_conversations event type: ", type(event))
            known_nodes = self.master_node.contacts.list_peers()
            print("Try to discover new nodes on the network.")

            # If we do not know any node.
            if len(known_nodes) == 0:
                # Get the current label of the button
                label = self.showConversations_Button.GetLabel()
                # Set a new one
                self.showConversations_Button.SetLabel("We don't know any nodes !")
                # Wait for a moment ; long enough for the user to be able to read the label.
                time.sleep(2)
                # Set the label back to its original value
                self.showConversations_Button.SetLabel(label)
                return

            # Display the conversations window.
            received_messages_window = Controller.ReceivedMessagesWrapper(self, self.master_node, self.network)
            received_messages_window.Show()
            self.Hide()

    class CreateNewKeyPairWrapper(CreateNewKeyPair):

        def __init__(self, parent, master_node, network):
            CreateNewKeyPair.__init__(self, parent)
            self.parent = parent
            self.master_node = master_node
            self.network = network
            self.keyPairLocation_dirPicker.SetPath(os.path.dirname(os.path.abspath(__file__)))

        def __del__(self):
            self.parent.Show()

        def create_key_pair(self, event):
            print("create_key_pair event type: ", type(event))
            rsa_private_key = Encryption.create_rsa_pair()
            location = event.GetPath()
            Encryption.export_rsa_private_key_to_file(rsa_private_key, location)

    class ReceivedMessagesWrapper(ReceivedMessages):

        def __init__(self, parent, master_node, network):
            ReceivedMessages.__init__(self, parent)
            self.parent = parent
            self.master_node = master_node
            self.network = network

            # Get a list of the known peers.
            # A list of IDs
            self.recipient_choices_indexes = self.master_node.contacts.list_peers()
            # A list of names, derived from the IDs.
            self.recipient_choices = [Node.get_name_from_node(identifier) for identifier in self.recipient_choices_indexes]

            self.scroll_index = 0
            self.user_filter = ""
            # Selected node of the "new message" box.
            self.new_message_selected_node = None

            self.display_conversations(self.scroll_index, self.user_filter)

            self.show_new_message_box()

            # Add events
            self.recipient_choice.Bind(wx.EVT_CHOICE, self.update_new_message_recipient)
            self.newChatMessage_textCtrl.Bind(wx.EVT_TEXT, self.update_message)
            self.sendNewChat_button.Bind(wx.EVT_BUTTON, self.send_message_to_new_node)

        def __del__(self):
            self.parent.Show()

        def display_conversations(self, index: int, user_filter: str) -> None:
            all_conversations_identifiers = self.master_node.conversations.get_all_conversations_ids()

            displayed_conversations = 0

            for i, node_id in enumerate(all_conversations_identifiers):

                # If a conversation does not exists with the node, we skip to the next iteration.
                if not self.master_node.conversations.does_conversation_exist_with_node(node_id):
                    continue

                # Apply filter and index (scrollbar)
                if user_filter not in node_id or i < index:
                    continue

                displayed_conversations += 1
                node_name = Node.get_name_from_node(node_id)
                last_message = self.master_node.conversations.get_last_conversation_message(
                    self.master_node.rsa_private_key,
                    node_id
                )

                # Creates a new sizer to contain a conversation.
                node_sbSizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, node_name), wx.HORIZONTAL)

                # Displays the last message of the conversation.
                self.node_lastConvSnippet_staticText = wx.StaticText(node_sbSizer.GetStaticBox(), wx.ID_ANY,
                                                                     lastMessage, wx.DefaultPosition, wx.DefaultSize,
                                                                     wx.ST_ELLIPSIZE_END)
                self.node_lastConvSnippet_staticText.Wrap(-1)
                node_sbSizer.Add(self.node_lastConvSnippet_staticText, 1, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

                self.node_lastConvDate_staticText = wx.StaticText(node_sbSizer.GetStaticBox(), wx.ID_ANY,
                                                                  lastMessageTimestamp, wx.DefaultPosition,
                                                                  wx.DefaultSize, 0)
                self.node_lastConvDate_staticText.Wrap(-1)
                node_sbSizer.Add(self.node_lastConvDate_staticText, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL |
                                 wx.ALIGN_CENTER_HORIZONTAL, 5)

                # Adds an "open" button on the conversation sizer.
                self.node_button = wx.Button(node_sbSizer.GetStaticBox(), wx.ID_ANY, u"Open", wx.DefaultPosition,
                                             wx.DefaultSize, wx.BU_EXACTFIT)
                node_sbSizer.Add(self.node_button, 0, wx.ALL, 5)
                self.chatContainer_bSizer.Add(node_sbSizer, 0, wx.ALL | wx.EXPAND, 5)

                # We're passing custom data using a lambda function
                self.node_button.Bind(wx.EVT_BUTTON, lambda event: self.open_chat_id(event, node_id))

            # If one or more conversation are displayed
            if displayed_conversations > 0:
                # Adds a scrollbar
                self.conversations_scrollBar = wx.ScrollBar(self, wx.ID_ANY, pos=wx.Point(displayed_conversations, displayed_conversations),
                                                            size=wx.DefaultSize, style=wx.SB_VERTICAL)
                self.chatContainerMain_bSizer.Add(self.conversations_scrollBar, 0, wx.ALL | wx.EXPAND, 5)
                self.conversations_scrollBar.Bind(wx.EVT_SCROLL, self.scroll)

        def show_new_message_box(self):
            # Adds the choice box.
            self.recipient_choice = wx.Choice(self.newChat_sbSizer.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition,
                                              wx.DefaultSize, self.recipient_choices, 0)
            # Initialize the selection to 0.
            self.recipient_choice.SetSelection(0)
            # Add to the sizer (display).
            self.recipient_bSizer.Add(self.recipient_choice, 1, wx.ALL, 5)

            # Adds some text.
            message_staticText = wx.StaticText(self.newChat_sbSizer.GetStaticBox(), wx.ID_ANY, u"Message",
                                                    wx.DefaultPosition, wx.DefaultSize, 0)
            # Add style
            message_staticText.Wrap(-1)
            # Add to the sizer (display).
            self.newChat_sbSizer.Add(message_staticText, 0, 0, 5)

            # Adds the textControl box, for the user to compose a message

            # Create a new message object.
            self.newMessage = Message()
            self.newChatMessage_textCtrl = wx.TextCtrl(self.newChat_sbSizer.GetStaticBox(), wx.ID_ANY, wx.EmptyString,
                                                       wx.DefaultPosition, wx.DefaultSize, wx.TE_AUTO_URL |
                                                       wx.TE_BESTWRAP | wx.TE_CHARWRAP | wx.TE_MULTILINE |
                                                       wx.TE_NOHIDESEL | wx.TE_RICH | wx.TE_RICH2 | wx.TE_WORDWRAP)
            self.newChatMessage_textCtrl.SetMinSize(wx.Size(-1, 50))
            self.newChat_sbSizer.Add(self.newChatMessage_textCtrl, 1, wx.ALL | wx.EXPAND, 5)

            # Add the "Send" button.
            self.sendNewChat_button = wx.Button(self.newChat_sbSizer.GetStaticBox(), wx.ID_ANY, u"Send",
                                                wx.DefaultPosition, wx.DefaultSize, 0)
            self.newChat_sbSizer.Add(self.sendNewChat_button, 0, wx.ALL, 5)

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
            full_conversation = Controller.ConversationWrapper(self, self.master_node, self.network, node_id)
            full_conversation.Show()
            self.Hide()

        def update_new_message_recipient(self, event):
            # Gets the ID of the selected node.
            self.new_message_recipient_id = self.recipient_choices_indexes[event.GetSelection()]

        def send_message_to_new_node(self, event):
            node_info: dict = self.master_node.contacts.get_contact_info(self.new_message_recipient_id)
            node_object = Node.from_dict(node_info)
            self.network.prepare_message_for_recipient()
            self.network.send_message()
            self.master_node.conversations.get_decrypted_aes(node_object.get_id_from_rsa_key(node_object.get_rsa_public_key()))
            # C'est ici qu'on va créer une clef AES pour la conversation. Note: pas de forward secrecy (pour l'instant).

        def update_message(self, event: wx.CommandEvent) -> None:
            """
            This function is called every time the new message txtCtrl is updated.
            Inefficient performance-wise ; needs to be improved.
            """
            self.newMessage.set_message(event.GetString())

    class ConversationWrapper(Conversation):

        def __init__(self, parent, master_node, network, recipient_node_id):
            Conversation.__init__(self, parent)
            self.parent = parent
            self.master_node = master_node
            self.network = network
            self.rcp_id = recipient_node_id

        def __del__(self):
            self.parent.Show()

        def display_conversation(self):
            conversation_message = self.master_node.conversations.get_all_messages_of_conversation_raw(self.master_node.rsa_private_key,
                                                                                                       self.rcp_id)
            messages_wx_objects = {}
            for message in conversation_message:
                msg_content = message.get_message()
                msg_received = Utils.get_date_from_timestamp(message.get_time_received())
                rcp_name = Node.get_name_from_node(self.rcp_id)

                # Variable implementation, might need a dictionary implementation.

                message_1_sbSizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, rcp_name, wx.HORIZONTAL))

                self.messageContent_1_staticText = wx.StaticText(message_1_sbSizer.GetStaticBox(), wx.ID_ANY,
                                                                 msg_content,
                                                                 wx.DefaultPosition, wx.DefaultSize, 0)
                self.messageContent_1_staticText.Wrap(-1)

                message_1_sbSizer.Add(self.messageContent_1_staticText, 1, wx.ALIGN_CENTER_VERTICAL, 5)

                self.messageTimestamp_1_staticText = wx.StaticText(message_1_sbSizer.GetStaticBox(), wx.ID_ANY,
                                                                   msg_received, wx.DefaultPosition, wx.DefaultSize,
                                                                   0)
                self.messageTimestamp_1_staticText.Wrap(-1)

                message_1_sbSizer.Add(self.messageTimestamp_1_staticText, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

                self.messages_bSizer.Add(message_1_sbSizer, 0, wx.ALL | wx.EXPAND, 5)

        def send_message_to_current_node(self, event):
            event.Skip()
