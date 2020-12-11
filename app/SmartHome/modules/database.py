from datetime import datetime
from functools import partial
import pandas as pd
from PySide2.QtCore import QAbstractTableModel, Qt, QAbstractItemModel
from app.SmartHome.modules.base import Window
from PySide2.QtWidgets import QGridLayout, QLabel, QPushButton, QComboBox, QLineEdit, QTableView, QVBoxLayout


class Pandas(QAbstractTableModel):

    def __init__(self, df):
        super(Pandas, self).__init__()
        self.df = df

    def rowCount(self, parent):
        return self.df.shape[0]

    def columnCount(self, parent):
        return self.df.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        value = self.df.iloc[index.row(), index.column()]

        if role == Qt.DisplayRole:

            if isinstance(value, datetime):
                return value.strftime("%Y-%m-%d")

            if isinstance(value, float):
                return "%.2f" % value

            if isinstance(value, str):
                return '%s' % value

            return '{}'.format(value)

        if role == Qt.TextAlignmentRole:
            return Qt.AlignCenter

    def setData(self, index, value, role):
        if role == Qt.EditRole:
            self.df.iloc[index.row(), index.column()] = value
            return True

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self.df.columns[section])

            if orientation == Qt.Vertical:
                return str(self.df.index[section])

    def flags(self, index):
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable


class Db_Management(Window):
    def __init__(self, window_title):
        super(Db_Management, self).__init__(window_title)
        self.menu = {task: QPushButton(task) for task in ('Manage Rooms',)}

    def load_window(self):
        super(Db_Management, self).load_window()

        for task in self.menu:
            self.layout.addWidget(self.menu[task])

    def connect_widgets(self):
        super(Db_Management, self).connect_widgets()
        close_screen = self.__class__.__name__
        for task in self.menu:
            self.menu[task].clicked.connect(partial(self.show_screen, task, close_screen))


class Manage_Rooms(Window):
    def __init__(self, window_title, db):
        super(Manage_Rooms, self).__init__(window_title)
        self.db = db
        self.rooms = Pandas(self.db.query('select * from home_rooms'))
        self.table = QTableView()
        self.combobox = QComboBox()
        self.delete = self.combobox.currentText()
        self.buttons = {button: QPushButton(button) for button in ('New Room', 'Save Changes', 'Delete Room')}

    def load_window(self):
        super(Manage_Rooms, self).load_window()
        for selection in self.rooms.df['room_name'].tolist():
            self.combobox.addItem(selection)

        for button in self.buttons:
            if button != 'Delete Room':
                self.layout.addWidget(self.buttons[button])

        self.layout.addWidget(self.table)
        self.layout.addWidget(self.buttons['Delete Room'])
        self.layout.addWidget(self.combobox)

    def connect_widgets(self):
        super(Manage_Rooms, self).connect_widgets()
        self.table.setModel(self.rooms)

        for button in self.buttons:
            if button == 'New Room':
                self.buttons[button].clicked.connect(self.new_room)
            elif button == 'Save Changes':
                self.buttons[button].clicked.connect(self.save_new_data)
            elif button == 'Delete Room':
                self.buttons[button].clicked.connect(self.delete_data)
        self.combobox.currentTextChanged.connect(self.delete_row)

    def delete_row(self):
        self.delete = self.combobox.currentText()

    def delete_data(self):
        room_id = self.rooms.df.query('room_name =="{}"'.format(self.delete))['room_id'].tolist()[0]
        self.db.query('delete from home_rooms where room_id = %s', [room_id])
        self.delete_combo_box()
        self.rooms = Pandas(self.db.query('select * from home_rooms'))
        self.table.setModel(self.rooms)
        self.reload_combo_box()

    def save_new_data(self):
        print(self.db.replace_data('home_rooms', self.rooms.df))

    def new_room(self):
        data = self.rooms.df.to_dict(orient='records')
        new_row = self.rooms.df.to_dict(orient='records')[-1]
        new_row.update({'room_id': int(new_row['room_id'])+1})
        new_row.update({'room_name': 'New Room'})
        new_row.update({'room_description': 'New Description'})
        data.append(new_row)

        self.delete_combo_box()
        self.rooms = Pandas(pd.DataFrame(data))
        self.table.setModel(self.rooms)
        self.reload_combo_box()

    def delete_combo_box(self):
        for i in range(len(self.rooms.df['room_name'].tolist())):
            self.combobox.removeItem(i)

    def reload_combo_box(self):

        for selection in self.rooms.df['room_name'].tolist():
            self.combobox.addItem(selection)

