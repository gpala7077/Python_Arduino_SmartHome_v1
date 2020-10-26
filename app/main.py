from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, SlideTransition
from app.app_screens import Login


class Root(ScreenManager):
    def __init__(self, **kwargs):
        super(Root, self).__init__(**kwargs)
        self.transition = SlideTransition()


class MainApp(MDApp):

    def build(self):
        # Declare root widget attributes
        self.theme_cls.theme_style = "Light"  # "Light"
        self.theme_cls.primary_palette = "BlueGray"  # "Purple", "Red"
        self.theme_cls.primary_hue = "500"

        self.root = Root()
        self.load_screens()
        self.root.current = 'login'
        return self.root

    def load_screens(self):
        self.screens = {
            'login': Login(name='login'),

            # 'main_menu': MenuScreen(name='main_menu'),
            # 'smart_menu': SmarthomeMenuScreen(name='smart_menu'),

            # 'projects': ProjectListScreen(name='projects'),
            # 'project': ProjectScreen(name='project'),
            # 'task': TaskScreen(name='task'),
            # 'subtask': SubtaskScreen(name='subtask'),
            #
            # 'groups': GroupListScreen(name='groups'),
            # 'group': GroupScreen(name='group'),
            # 'subgroup': SubgroupScreen(name='subgroup'),
            #
            # 'calendar': CalendarScreen(name='calendar'),
            # 'rooms': RoomsScreen(name='rooms'),
            # 'room': Room(name='room')
        }

        for screen in self.screens:
            self.root.add_widget(self.screens[screen])

    def get_screen(self, name, record_id=None):
        if self.screens['login'].user_authenticated:
            self.screens[name].db_credentials = self.screens['login'].db_credentials
            self.screens[name].hue_credentials = self.screens['login'].hue_credentials

            if record_id is not None:
                self.screens[name].record_id = record_id

            self.screens[name].load()
            self.root.current = name


if __name__ == '__main__':
    App = MainApp()
    App.run()
