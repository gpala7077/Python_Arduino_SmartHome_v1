from PySide2.QtWidgets import QDialogButtonBox, QVBoxLayout, QWidget, QToolBar


class Window(QWidget):

    def __init__(self, window_title):
        QWidget.__init__(self)
        self.db = None
        self.nav_bar = ('Previous', 'Main Menu', 'Database Management', 'Smart Home')
        self.navigation = QToolBar()
        self.layout = QVBoxLayout()
        self.window_title = window_title
        self.button = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.show_screen = None
        self.resize(405, 600)
        self.previous_screen = None

    def start(self):
        self.load_window()
        self.connect_widgets()

    def load_window(self):
        self.setWindowTitle(self.window_title)
        if self.__class__.__name__ != 'Login':
            for action in self.nav_bar:
                self.navigation.addAction(action)
                self.navigation.addSeparator()

            self.layout.setMenuBar(self.navigation)

    def connect_widgets(self):
        self.setLayout(self.layout)
        self.navigation.actionTriggered.connect(self.navigate)

    def navigate(self, action):
        if action.text() == 'Previous':
            open_screen = self.previous_screen
        else:
            open_screen = action.text()

        close_screen = self.__class__.__name__
        if open_screen is not None:
            self.show_screen(open_screen, close_screen)
