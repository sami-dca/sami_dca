from .network import Networks
from .ui import MainApp


class Controller:
    def __init__(self, has_ui: bool):
        self.has_ui = has_ui
        if self.has_ui:
            self.ui = MainApp()
        self.networks = Networks()

    def run(self):
        if self.has_ui:
            self.ui.run()
