# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version Oct 26 2018)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc

###########################################################################
## Class MainMenu
###########################################################################

class MainMenu ( wx.Frame ):

	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"Secure chat app", pos = wx.DefaultPosition, size = wx.Size( 405,375 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

		self.SetSizeHints( wx.Size( 350,375 ), wx.DefaultSize )

		mainMenu_bSizer = wx.BoxSizer( wx.VERTICAL )

		info_sbSizer = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Info" ), wx.VERTICAL )

		serverStatus_bSizer = wx.BoxSizer( wx.HORIZONTAL )

		self.serverStatusInfo_staticText = wx.StaticText( info_sbSizer.GetStaticBox(), wx.ID_ANY, u"Listening status: ", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.serverStatusInfo_staticText.Wrap( -1 )

		self.serverStatusInfo_staticText.SetForegroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOWTEXT ) )
		self.serverStatusInfo_staticText.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_APPWORKSPACE ) )

		serverStatus_bSizer.Add( self.serverStatusInfo_staticText, 0, wx.ALL, 5 )

		self.serverStatus_staticText = wx.StaticText( info_sbSizer.GetStaticBox(), wx.ID_ANY, u"Down", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.serverStatus_staticText.Wrap( -1 )

		self.serverStatus_staticText.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, wx.EmptyString ) )
		self.serverStatus_staticText.SetForegroundColour( wx.Colour( 255, 0, 0 ) )

		serverStatus_bSizer.Add( self.serverStatus_staticText, 0, wx.ALL, 5 )


		info_sbSizer.Add( serverStatus_bSizer, 1, wx.EXPAND, 5 )

		nodeName_bSizer = wx.BoxSizer( wx.HORIZONTAL )

		self.nodeNameInfo_staticText = wx.StaticText( info_sbSizer.GetStaticBox(), wx.ID_ANY, u"Your name : ", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.nodeNameInfo_staticText.Wrap( -1 )

		nodeName_bSizer.Add( self.nodeNameInfo_staticText, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.EXPAND, 5 )

		self.nodeName_staticText = wx.StaticText( info_sbSizer.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.nodeName_staticText.Wrap( -1 )

		self.nodeName_staticText.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, wx.EmptyString ) )

		nodeName_bSizer.Add( self.nodeName_staticText, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5 )


		info_sbSizer.Add( nodeName_bSizer, 1, wx.EXPAND, 5 )


		mainMenu_bSizer.Add( info_sbSizer, 0, wx.EXPAND, 5 )

		rsaKeys_sbSizer = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"RSA Keys" ), wx.VERTICAL )

		self.rsaPrivateKeyStatus_staticText = wx.StaticText( rsaKeys_sbSizer.GetStaticBox(), wx.ID_ANY, u"RSA private key: ", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.rsaPrivateKeyStatus_staticText.Wrap( -1 )

		rsaKeys_sbSizer.Add( self.rsaPrivateKeyStatus_staticText, 0, wx.ALL, 5 )

		bSizer14 = wx.BoxSizer( wx.HORIZONTAL )

		self.privateKey_filePicker = wx.FilePickerCtrl( rsaKeys_sbSizer.GetStaticBox(), wx.ID_ANY, wx.EmptyString, u"Select an RSA PrivateKey file", u"*.pem", wx.DefaultPosition, wx.DefaultSize, wx.FLP_DEFAULT_STYLE )
		self.privateKey_filePicker.SetToolTip( u"Select an RSA private key file" )

		bSizer14.Add( self.privateKey_filePicker, 1, wx.ALL|wx.EXPAND, 5 )

		self.exportPubkey_button = wx.Button( rsaKeys_sbSizer.GetStaticBox(), wx.ID_ANY, u"Export pubkey", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.exportPubkey_button.Enable( False )

		bSizer14.Add( self.exportPubkey_button, 0, wx.ALL, 5 )


		rsaKeys_sbSizer.Add( bSizer14, 1, wx.EXPAND, 5 )

		self.createNewKeyPair_button = wx.Button( rsaKeys_sbSizer.GetStaticBox(), wx.ID_ANY, u"Create a new key pair", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.createNewKeyPair_button.SetToolTip( u"Create a new pair of RSA keys" )

		rsaKeys_sbSizer.Add( self.createNewKeyPair_button, 0, wx.ALL|wx.EXPAND, 5 )


		mainMenu_bSizer.Add( rsaKeys_sbSizer, 0, wx.EXPAND, 5 )

		chat_sbSizer = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Chat" ), wx.VERTICAL )

		self.showConversations_Button = wx.Button( chat_sbSizer.GetStaticBox(), wx.ID_ANY, u"Chat with other nodes", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.showConversations_Button.Enable( False )

		chat_sbSizer.Add( self.showConversations_Button, 0, wx.ALL|wx.EXPAND, 5 )


		mainMenu_bSizer.Add( chat_sbSizer, 0, wx.EXPAND, 5 )


		self.SetSizer( mainMenu_bSizer )
		self.Layout()

		self.Centre( wx.BOTH )

		# Connect Events
		self.privateKey_filePicker.Bind( wx.EVT_FILEPICKER_CHANGED, self.load_private_key )
		self.exportPubkey_button.Bind( wx.EVT_BUTTON, self.export_pubkey )
		self.createNewKeyPair_button.Bind( wx.EVT_BUTTON, self.open_pair_creation_window )
		self.showConversations_Button.Bind( wx.EVT_BUTTON, self.show_conversations )

	def __del__( self ):
		pass


	# Virtual event handlers, overide them in your derived class
	def load_private_key( self, event ):
		event.Skip()

	def export_pubkey( self, event ):
		event.Skip()

	def open_pair_creation_window( self, event ):
		event.Skip()

	def show_conversations( self, event ):
		event.Skip()


###########################################################################
## Class CreateNewKeyPair
###########################################################################

class CreateNewKeyPair ( wx.Frame ):

	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"Create a new key pair", pos = wx.DefaultPosition, size = wx.Size( 525,200 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

		self.SetSizeHints( wx.Size( 525,200 ), wx.DefaultSize )

		createNewKeyPair_bSizer = wx.BoxSizer( wx.VERTICAL )

		pairLocation_sbSizer = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Location" ), wx.VERTICAL )

		self.pairCreationInfo1_staticText = wx.StaticText( pairLocation_sbSizer.GetStaticBox(), wx.ID_ANY, u"Note: as soon as you select a directory, the creation will launch.", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.pairCreationInfo1_staticText.Wrap( -1 )

		pairLocation_sbSizer.Add( self.pairCreationInfo1_staticText, 0, wx.ALL, 5 )

		self.keyPairLocation_dirPicker = wx.DirPickerCtrl( pairLocation_sbSizer.GetStaticBox(), wx.ID_ANY, wx.EmptyString, u"Select a folder where the keys will be stored", wx.DefaultPosition, wx.DefaultSize, wx.DIRP_DEFAULT_STYLE )
		pairLocation_sbSizer.Add( self.keyPairLocation_dirPicker, 0, wx.ALL|wx.EXPAND, 5 )

		self.pairCreationInfo2_staticText = wx.StaticText( pairLocation_sbSizer.GetStaticBox(), wx.ID_ANY, u"Files will be named \"private_[ID].pem\" and \"public_[ID].pem\".", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.pairCreationInfo2_staticText.Wrap( -1 )

		pairLocation_sbSizer.Add( self.pairCreationInfo2_staticText, 0, wx.ALL, 5 )


		createNewKeyPair_bSizer.Add( pairLocation_sbSizer, 0, wx.ALL|wx.EXPAND, 5 )


		self.SetSizer( createNewKeyPair_bSizer )
		self.Layout()

		self.Centre( wx.BOTH )

		# Connect Events
		self.keyPairLocation_dirPicker.Bind( wx.EVT_DIRPICKER_CHANGED, self.create_key_pair )

	def __del__( self ):
		pass


	# Virtual event handlers, overide them in your derived class
	def create_key_pair( self, event ):
		event.Skip()


###########################################################################
## Class ReceivedMessages
###########################################################################

class ReceivedMessages ( wx.Frame ):

	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"See all conversations", pos = wx.DefaultPosition, size = wx.Size( 548,562 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

		self.SetSizeHints( wx.Size( 300,300 ), wx.DefaultSize )

		receivedself.messages_bSizer = wx.BoxSizer( wx.VERTICAL )

		self.filterNodes_searchCtrl = wx.SearchCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.filterNodes_searchCtrl.ShowSearchButton( True )
		self.filterNodes_searchCtrl.ShowCancelButton( True )
		self.filterNodes_searchCtrl.SetToolTip( u"Search for a node" )

		receivedself.messages_bSizer.Add( self.filterNodes_searchCtrl, 0, wx.ALL|wx.EXPAND, 5 )

		self.chatContainerMain_bSizer = wx.BoxSizer( wx.HORIZONTAL )

		self.chatContainer_bSizer = wx.BoxSizer( wx.VERTICAL )


		self.chatContainerMain_bSizer.Add( self.chatContainer_bSizer, 1, wx.EXPAND, 5 )


		receivedself.messages_bSizer.Add( self.chatContainerMain_bSizer, 1, wx.EXPAND, 5 )

		self.newChat_sbSizer = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"New conversation" ), wx.VERTICAL )

		self.recipient_bSizer = wx.BoxSizer( wx.HORIZONTAL )

		self.recipient_staticText = wx.StaticText( self.newChat_sbSizer.GetStaticBox(), wx.ID_ANY, u"Send to:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.recipient_staticText.Wrap( -1 )

		self.recipient_bSizer.Add( self.recipient_staticText, 0, wx.ALIGN_CENTER_VERTICAL, 5 )


		self.newChat_sbSizer.Add( self.recipient_bSizer, 0, wx.EXPAND, 5 )


		receivedself.messages_bSizer.Add( self.newChat_sbSizer, 0, wx.EXPAND, 5 )


		self.SetSizer( receivedself.messages_bSizer )
		self.Layout()

		self.Centre( wx.BOTH )

		# Connect Events
		self.filterNodes_searchCtrl.Bind( wx.EVT_TEXT_ENTER, self.filter_search )

	def __del__( self ):
		pass


	# Virtual event handlers, overide them in your derived class
	def filter_search( self, event ):
		event.Skip()


###########################################################################
## Class Conversation
###########################################################################

class Conversation ( wx.Frame ):

	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"Conversation - node1", pos = wx.DefaultPosition, size = wx.Size( 624,320 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

		conversation_bSizer = wx.BoxSizer( wx.HORIZONTAL )

		messagesMain_bSizer8 = wx.BoxSizer( wx.VERTICAL )

		self.messages_bSizer = wx.BoxSizer( wx.VERTICAL )

		messagesMain_bSizer8.Add( self.messages_bSizer, 1, wx.EXPAND, 5 )

		newMessage_bSizer = wx.BoxSizer( wx.HORIZONTAL )

		self.newMessage_textCtrl = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		newMessage_bSizer.Add( self.newMessage_textCtrl, 1, wx.ALL|wx.EXPAND, 5 )

		self.sendMessage_button = wx.Button( self, wx.ID_ANY, u"Send", wx.DefaultPosition, wx.DefaultSize, wx.BU_EXACTFIT )
		newMessage_bSizer.Add( self.sendMessage_button, 0, wx.ALL, 5 )


		messagesMain_bSizer8.Add( newMessage_bSizer, 0, wx.EXPAND, 5 )


		conversation_bSizer.Add( messagesMain_bSizer8, 1, wx.EXPAND, 5 )

		self.messages_scrollBar = wx.ScrollBar( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.SB_VERTICAL )
		conversation_bSizer.Add( self.messages_scrollBar, 0, wx.EXPAND, 5 )


		self.SetSizer( conversation_bSizer )
		self.Layout()

		self.Centre( wx.BOTH )

		# Connect Events
		self.sendMessage_button.Bind( wx.EVT_BUTTON, self.send_message_to_current_node )

	def __del__( self ):
		pass


	# Virtual event handlers, overide them in your derived class
	def send_message_to_current_node( self, event ):
		event.Skip()


