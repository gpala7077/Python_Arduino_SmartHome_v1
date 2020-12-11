from datetime import datetime
from functools import partial

import pandas as pd
from PySide2.QtCore import QAbstractTableModel, Qt
from PySide2.QtWidgets import QPushButton, QComboBox, QTableView

from app.SmartHome.modules.base import Window


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


class Database_Management(Window):
    def __init__(self, window_title):
        super(Database_Management, self).__init__(window_title)
        self.menu = {task: QPushButton(task) for task in ('Manage Rooms', 'Manage Things', 'Manage Commands')}

    def load_window(self):
        super(Database_Management, self).load_window()

        for task in self.menu:
            self.layout.addWidget(self.menu[task])

    def connect_widgets(self):
        super(Database_Management, self).connect_widgets()
        close_screen = self.__class__.__name__
        for task in self.menu:
            self.menu[task].clicked.connect(partial(self.show_screen, task, close_screen))


class Manage_Table(Window):
    def __init__(self, window_title, db):
        super(Manage_Table, self).__init__(window_title)
        self.db = db
        self.table = QTableView()
        self.combobox = QComboBox()
        self.delete = self.combobox.currentText()
        self.buttons = {button: QPushButton(button) for button in ('New', 'Save', 'Delete')}
        self.data = None

    def load_window(self):
        super(Manage_Table, self).load_window()
        self.load_combo_box()

        for button in self.buttons:
            if button != 'Delete':
                self.layout.addWidget(self.buttons[button])

        self.layout.addWidget(self.table)
        self.layout.addWidget(self.buttons['Delete'])
        self.layout.addWidget(self.combobox)

    def connect_widgets(self):
        super(Manage_Table, self).connect_widgets()
        self.table.setModel(self.data)

        for button in self.buttons:
            if button == 'New':
                self.buttons[button].clicked.connect(self.new_data)
            elif button == 'Save':
                self.buttons[button].clicked.connect(self.save_new_data)
            elif button == 'Delete':
                self.buttons[button].clicked.connect(self.delete_data)
        self.combobox.currentTextChanged.connect(self.delete_row)

    def delete_row(self):
        self.delete = self.combobox.currentText()

    def delete_combo_box(self):
        pass

    def load_combo_box(self):
        pass

    def save_new_data(self):
        pass

    def delete_data(self):
        pass

    def new_data(self):
        pass


class Manage_Rooms(Manage_Table):
    def __init__(self, window_title, db):
        super(Manage_Rooms, self).__init__(window_title, db)
        self.data = Pandas(self.db.query('select * from home_rooms'))

    def delete_combo_box(self):
        for i in range(len(self.data.df['room_name'].tolist())):
            self.combobox.removeItem(i)

    def load_combo_box(self):
        for selection in self.data.df['room_name'].tolist():
            self.combobox.addItem(selection)

    def save_new_data(self):
        print(self.db.replace_data('home_rooms', self.data.df))

    def delete_data(self):
        room_id = self.data.df.query('room_name =="{}"'.format(self.delete))['room_id'].tolist()[0]
        self.db.query('delete from home_rooms where room_id = %s', [room_id])
        self.delete_combo_box()
        self.data = Pandas(self.db.query('select * from home_rooms'))
        self.table.setModel(self.data)
        self.load_combo_box()

    def new_data(self):
        data = self.data.df.to_dict(orient='records')
        new_row = self.data.df.to_dict(orient='records')[-1]
        new_row.update({'room_id': int(new_row['room_id']) + 1})
        new_row.update({'room_name': 'New Room'})
        new_row.update({'room_description': 'New Description'})
        data.append(new_row)

        self.delete_combo_box()
        self.data = Pandas(pd.DataFrame(data))
        self.table.setModel(self.data)
        self.load_combo_box()


class Manage_Things(Manage_Table):
    def __init__(self, window_title, db):
        super(Manage_Things, self).__init__(window_title, db)
        self.data = Pandas(self.db.query('select * from home_things'))

    def delete_combo_box(self):
        for i in range(len(self.data.df['thing_name'].tolist())):
            self.combobox.removeItem(i)

    def load_combo_box(self):
        for selection in self.data.df['thing_name'].tolist():
            self.combobox.addItem(selection)

    def save_new_data(self):
        print(self.db.replace_data('home_things', self.data.df))

    def delete_data(self):
        room_id = self.data.df.query('thing_name =="{}"'.format(self.delete))['thing_id'].tolist()[0]
        self.db.query('delete from home_things where thing_id = %s', [room_id])
        self.delete_combo_box()
        self.data = Pandas(self.db.query('select * from home_things'))
        self.table.setModel(self.data)
        self.load_combo_box()

    def new_data(self):
        data = self.data.df.to_dict(orient='records')
        new_row = self.data.df.to_dict(orient='records')[-1]
        new_row.update({'thing_id': int(new_row['thing_id']) + 1})
        new_row.update({'thing_name': 'New Thing'})
        new_row.update({'thing_description': 'New Description'})
        data.append(new_row)

        self.delete_combo_box()
        self.data = Pandas(pd.DataFrame(data))
        self.table.setModel(self.data)
        self.load_combo_box()


class Manage_Commands(Manage_Table):
    def __init__(self, window_title, db):
        super(Manage_Commands, self).__init__(window_title, db)
        self.data = Pandas(self.db.query('select * from commands'))

    def delete_combo_box(self):
        for i in range(len(self.data.df['command_record_id'].tolist())):
            self.combobox.removeItem(i)

    def load_combo_box(self):
        for selection in self.data.df['command_record_id'].tolist():
            self.combobox.addItem(str(selection))

    def save_new_data(self):
        print(self.db.replace_data('commands', self.data.df))

    def delete_data(self):
        room_id = self.data.df.query('command_record_id =="{}"'.format(self.delete))['command_record_id'].tolist()[0]
        self.db.query('delete from home_things where thing_id = %s', [room_id])
        self.delete_combo_box()
        self.data = Pandas(self.db.query('select * from home_things'))
        self.table.setModel(self.data)
        self.load_combo_box()

    def new_data(self):
        data = self.data.df.to_dict(orient='records')
        new_row = self.data.df.to_dict(orient='records')[-1]
        new_row.update({'command_record_id': int(new_row['command_record_id']) + 1})
        new_row.update({'info_level': 'New Command'})
        new_row.update({'info_id': 'New Command'})
        new_row.update({'command_type': 'New Command'})
        new_row.update({'command_sensor': 'New Command'})
        new_row.update({'command_name': 'New Command'})
        new_row.update({'command_value': 'New Value'})
        data.append(new_row)

        self.delete_combo_box()
        self.data = Pandas(pd.DataFrame(data))
        self.table.setModel(self.data)
        self.load_combo_box()