from PySide2.QtWidgets import QDialogButtonBox, QVBoxLayout, QWidget


class Window(QWidget):

    def __init__(self, window_title):
        QWidget.__init__(self)
        self.db = None
        self.layout = QVBoxLayout()
        self.window_title = window_title
        self.button = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.show_screen = None
        self.resize(400, 600)

    def start(self):
        self.load_window()
        self.connect_widgets()

    def load_window(self):
        self.setWindowTitle(self.window_title)

    def connect_widgets(self):
        self.setLayout(self.layout)
