# -*- coding: UTF8 -*-

import threading
import wx

from sami.node import MasterNode
from sami.network import Network
from sami.controller import Controller


class Main:
    def __init__(self):
        self.master_node = MasterNode()
        self.network = Network(self.master_node, "192.168.0.48", 62489)  # !!! DEV ONLY !!!
        self.controller = Controller(self.master_node, self.network)

        self.start_server()
        self.controller.app.MainLoop()

    def start_server(self) -> None:
        """
        Instantiate server as a new thread.
        """
        t_net = threading.Thread(target=self.network.listen, name="net_thread", daemon=True)
        t_net.start()

        self.controller.mainFrame.serverStatus_staticText.SetForegroundColour(wx.Colour(0, 255, 0))
        self.controller.mainFrame.serverStatus_staticText.SetLabel("Up")


def main():
    dca = Main()
    dca.start_server()


if __name__ == "__main__":
    main()
