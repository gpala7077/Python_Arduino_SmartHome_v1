from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager
from mysql.connector import Error
from app.kivySmartHome.modules.screens import *
from home.main import Home
from kivymd.app import MDApp


class MyMainApp(MDApp):
    Builder.load_file("kv/login.kv")
    Builder.load_file("kv/menus.kv")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.screen_manager = ScreenManager()
        self.theme_cls.theme_style = "Dark"
        self.home = None
        self.credentials = {'username': None,
                            'password': None,
                            'database': 'smart_home',
                            'host': '192.168.50.173'}

    def build(self):
        self.screen_manager.switch_to(Login(name='login'))
        return self.screen_manager

    def transition_screen(self, screen, direction):

        if screen == 'main_menu':
            screen = Main_Menu(self.home, name=screen)

        elif screen == 'home_control':
            screen = Home_Control(self.home, name=screen)

        elif screen == 'home_management':
            screen = Home_Management(self.home, name=screen)

        self.screen_manager.switch_to(screen, direction=direction)
        self.screen_manager.remove_widget(self.screen_manager.screens[0])

    def check_credentials(self, username, password):
        self.credentials.update({'username': username})
        self.credentials.update({'password': password})
        try:
            self.home = Home('viewer', self.credentials)
            print(self.home.initialize())
            print(self.home.start_rooms())
            self.transition_screen('main_menu', 'left')

        except Error:
            print('Incorrect Credentials!!!')
            self.screen_manager.current = 'login'

    def toolbar_callback(self, instance):
        print(instance)


if __name__ == "__main__":
    MyMainApp().run()
