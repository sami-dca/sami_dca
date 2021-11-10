from kivy.lang import Builder

from kivymd.app import MDApp


class SamiApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = 'Purple'
        return Builder.load_file('main.kv')


SamiApp().run()
