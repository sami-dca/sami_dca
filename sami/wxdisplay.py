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
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"Sami DCA", pos = wx.DefaultPosition, size = wx.Size( 405,375 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

		self.SetSizeHints( wx.Size( 350,375 ), wx.DefaultSize )

		main_menu_bSizer = wx.BoxSizer( wx.VERTICAL )

		info_sbSizer = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Info" ), wx.VERTICAL )

		server_status_bSizer = wx.BoxSizer( wx.HORIZONTAL )

		self.server_status_info_staticText = wx.StaticText( info_sbSizer.GetStaticBox(), wx.ID_ANY, u"Listening status: ", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.server_status_info_staticText.Wrap( -1 )

		self.server_status_info_staticText.SetForegroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOWTEXT ) )
		self.server_status_info_staticText.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_APPWORKSPACE ) )

		server_status_bSizer.Add( self.server_status_info_staticText, 0, wx.ALL, 5 )

		self.server_status_staticText = wx.StaticText( info_sbSizer.GetStaticBox(), wx.ID_ANY, u"Down", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.server_status_staticText.Wrap( -1 )

		self.server_status_staticText.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, wx.EmptyString ) )
		self.server_status_staticText.SetForegroundColour( wx.Colour( 255, 0, 0 ) )

		server_status_bSizer.Add( self.server_status_staticText, 0, wx.ALL, 5 )


		info_sbSizer.Add( server_status_bSizer, 1, wx.EXPAND, 5 )

		node_name_bSizer = wx.BoxSizer( wx.HORIZONTAL )

		self.node_name_info_staticText = wx.StaticText( info_sbSizer.GetStaticBox(), wx.ID_ANY, u"Your name : ", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.node_name_info_staticText.Wrap( -1 )

		node_name_bSizer.Add( self.node_name_info_staticText, 0, wx.ALL|wx.EXPAND, 5 )

		self.node_name_staticText = wx.StaticText( info_sbSizer.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.node_name_staticText.Wrap( -1 )

		self.node_name_staticText.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, wx.EmptyString ) )

		node_name_bSizer.Add( self.node_name_staticText, 0, wx.ALL|wx.EXPAND, 5 )


		info_sbSizer.Add( node_name_bSizer, 1, wx.EXPAND, 5 )


		main_menu_bSizer.Add( info_sbSizer, 0, wx.EXPAND, 5 )

		rsa_keys_sbSizer = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"RSA keys" ), wx.VERTICAL )

		self.rsa_private_key_status_staticText = wx.StaticText( rsa_keys_sbSizer.GetStaticBox(), wx.ID_ANY, u"RSA private key: ", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.rsa_private_key_status_staticText.Wrap( -1 )

		rsa_keys_sbSizer.Add( self.rsa_private_key_status_staticText, 0, wx.ALL, 5 )

		rsa_bSizer = wx.BoxSizer( wx.HORIZONTAL )

		self.private_key_filePicker = wx.FilePickerCtrl( rsa_keys_sbSizer.GetStaticBox(), wx.ID_ANY, wx.EmptyString, u"Select an RSA PrivateKey file", u"*.pem", wx.DefaultPosition, wx.DefaultSize, wx.FLP_DEFAULT_STYLE )
		self.private_key_filePicker.SetToolTip( u"Select an RSA private key file" )

		rsa_bSizer.Add( self.private_key_filePicker, 1, wx.ALL|wx.EXPAND, 5 )

		self.export_pubkey_button = wx.Button( rsa_keys_sbSizer.GetStaticBox(), wx.ID_ANY, u"Export pubkey", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.export_pubkey_button.Enable( False )

		rsa_bSizer.Add( self.export_pubkey_button, 0, wx.ALL, 5 )


		rsa_keys_sbSizer.Add( rsa_bSizer, 1, wx.EXPAND, 5 )

		self.create_new_key_pair_button = wx.Button( rsa_keys_sbSizer.GetStaticBox(), wx.ID_ANY, u"Create a new key pair", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.create_new_key_pair_button.SetToolTip( u"Create a new pair of RSA keys" )

		rsa_keys_sbSizer.Add( self.create_new_key_pair_button, 0, wx.ALL|wx.EXPAND, 5 )


		main_menu_bSizer.Add( rsa_keys_sbSizer, 0, wx.EXPAND, 5 )

		chat_sbSizer = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Chat" ), wx.VERTICAL )

		self.show_conversations_Button = wx.Button( chat_sbSizer.GetStaticBox(), wx.ID_ANY, u"Chat with other nodes", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.show_conversations_Button.Enable( False )

		chat_sbSizer.Add( self.show_conversations_Button, 0, wx.ALL|wx.EXPAND, 5 )


		main_menu_bSizer.Add( chat_sbSizer, 0, wx.EXPAND, 5 )


		self.SetSizer( main_menu_bSizer )
		self.Layout()

		self.Centre( wx.BOTH )

		# Connect Events
		self.private_key_filePicker.Bind( wx.EVT_FILEPICKER_CHANGED, self.load_private_key )
		self.export_pubkey_button.Bind( wx.EVT_BUTTON, self.export_pubkey )
		self.create_new_key_pair_button.Bind( wx.EVT_BUTTON, self.open_pair_creation_window )
		self.show_conversations_Button.Bind( wx.EVT_BUTTON, self.show_conversations )

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
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"Create a new key", pos = wx.DefaultPosition, size = wx.Size( 525,200 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

		self.SetSizeHints( wx.Size( 525,200 ), wx.DefaultSize )

		create_new_key_pair_bSizer = wx.BoxSizer( wx.VERTICAL )

		pair_location_sbSizer = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Location" ), wx.VERTICAL )

		self.pair_creation_info_1_staticText = wx.StaticText( pair_location_sbSizer.GetStaticBox(), wx.ID_ANY, u"Note: as soon as you select a directory, the creation will launch.", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.pair_creation_info_1_staticText.Wrap( -1 )

		pair_location_sbSizer.Add( self.pair_creation_info_1_staticText, 0, wx.ALL, 5 )

		self.key_pair_location_dirPicker = wx.DirPickerCtrl( pair_location_sbSizer.GetStaticBox(), wx.ID_ANY, wx.EmptyString, u"Select a folder where the keys will be stored", wx.DefaultPosition, wx.DefaultSize, wx.DIRP_DEFAULT_STYLE )
		pair_location_sbSizer.Add( self.key_pair_location_dirPicker, 0, wx.ALL|wx.EXPAND, 5 )

		self.pair_creation_info_2_staticText = wx.StaticText( pair_location_sbSizer.GetStaticBox(), wx.ID_ANY, u"File will be named \"private_[ID].pem\".", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.pair_creation_info_2_staticText.Wrap( -1 )

		pair_location_sbSizer.Add( self.pair_creation_info_2_staticText, 0, wx.ALL, 5 )


		create_new_key_pair_bSizer.Add( pair_location_sbSizer, 0, wx.ALL|wx.EXPAND, 5 )


		self.SetSizer( create_new_key_pair_bSizer )
		self.Layout()

		self.Centre( wx.BOTH )

		# Connect Events
		self.key_pair_location_dirPicker.Bind( wx.EVT_DIRPICKER_CHANGED, self.create_key_pair )

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

		self.received_messages_bSizer = wx.BoxSizer( wx.VERTICAL )

		self.filter_nodes_search_ctrl = wx.SearchCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.filter_nodes_search_ctrl.ShowSearchButton( True )
		self.filter_nodes_search_ctrl.ShowCancelButton( True )
		self.filter_nodes_search_ctrl.SetToolTip( u"Search for a node" )

		self.received_messages_bSizer.Add( self.filter_nodes_search_ctrl, 0, wx.ALL|wx.EXPAND, 5 )

		self.chat_container_main_bSizer = wx.BoxSizer( wx.HORIZONTAL )

		chat_container_bSizer = wx.BoxSizer( wx.VERTICAL )


		self.chat_container_main_bSizer.Add( chat_container_bSizer, 1, wx.EXPAND, 5 )


		self.received_messages_bSizer.Add( self.chat_container_main_bSizer, 1, wx.EXPAND, 5 )

		self.SetSizer( self.received_messages_bSizer )
		self.Layout()

		self.Centre( wx.BOTH )

		# Connect Events
		self.filter_nodes_search_ctrl.Bind( wx.EVT_TEXT_ENTER, self.filter_search )

	def __del__( self ):
		pass


	# Virtual event handlers, overide them in your derived class
	def filter_search( self, event ):
		event.Skip()


###########################################################################
## Class Conversation
###########################################################################

class Conversations (wx.Frame):

	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"Conversation - node1", pos = wx.DefaultPosition, size = wx.Size( 624,320 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

		conversation_bSizer = wx.BoxSizer( wx.HORIZONTAL )

		messages_main_bSizer = wx.BoxSizer( wx.VERTICAL )

		self.messages_bSizer = wx.BoxSizer( wx.VERTICAL )


		messages_main_bSizer.Add( self.messages_bSizer, 1, wx.EXPAND, 5 )

		new_message_bSizer = wx.BoxSizer( wx.HORIZONTAL )

		self.new_message_textCtrl = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_AUTO_URL )
		new_message_bSizer.Add( self.new_message_textCtrl, 1, wx.ALL|wx.EXPAND, 5 )

		self.send_message_button = wx.Button( self, wx.ID_ANY, u"Send", wx.DefaultPosition, wx.DefaultSize, wx.BU_EXACTFIT )
		new_message_bSizer.Add( self.send_message_button, 0, wx.ALL, 5 )


		messages_main_bSizer.Add( new_message_bSizer, 0, wx.EXPAND, 5 )


		conversation_bSizer.Add( messages_main_bSizer, 1, wx.EXPAND, 5 )

		# self.messages_scrollBar = wx.ScrollBar( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.SB_VERTICAL )
		# conversation_bSizer.Add( self.messages_scrollBar, 0, wx.EXPAND, 5 )


		self.SetSizer( conversation_bSizer )
		self.Layout()

		self.Centre( wx.BOTH )

		# Connect Events
		self.new_message_textCtrl.Bind( wx.EVT_TEXT, self.update_new_message )
		self.send_message_button.Bind(wx.EVT_BUTTON, self.send_message)

	def __del__( self ):
		pass


	# Virtual event handlers, overide them in your derived class
	def update_new_message( self, event ):
		event.Skip()

	def send_message(self, event):
		event.Skip()


