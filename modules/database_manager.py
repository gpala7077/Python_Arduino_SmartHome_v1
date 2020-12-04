import mysql.connector as db
import pandas as pd


class Database:
    """Data Handler Class.

    Attributes
    ----------
    credentials : dict
        dictionary containing the {username:un, password:pw, database:name, host: ip}

    db : object
        mysql.connector db object class.

    cursor : object
        mysql.connector db cursor class.

    Parameters
    ----------
    credentials : dict
        dictionary containing the {username:un, password:pw, database:name, host: ip}

    """

    def __init__(self, credentials):
        # Save credentials
        self.credentials = credentials

        # Log into local database
        self.db = db.connect(
            user=self.credentials['username'],
            password=self.credentials['password'],
            database=self.credentials['database'],
            host=self.credentials['host']
        )

        # create pointer
        self.cursor = self.db.cursor()

    def query(self, query, values=None):
        """Query the connecting database. Returns a pandas data frame."""
        self.db.commit()  # Ensure all changes are committed before querying.

        if 'select' in query:  # If query is select type. return pandas data frame
            if values is not None:
                self.cursor.execute(query, values)
            else:
                self.cursor.execute(query)

            data = pd.DataFrame(self.cursor.fetchall())
            column_names = [col_name[0] for col_name in self.cursor.description]

            # Add column names
            data.columns = column_names

            return data

        elif 'insert' in query:  # If query is insert type. return primary key of the inserted row.
            self.cursor.execute(query, values)
            self.db.commit()
            last_id = self.cursor.getlastrowid()
            print('last id =', last_id)
            return last_id

    def get_thing_data(self, thing_id, role):

        room_data = self.query(
            'select * from home_rooms where room_id = '
            '(select rooms_room_id from rooms_things where rooms_thing_id = %s)',
            [thing_id]).to_dict(orient='records')[0]

        thing_data = self.query('select * from home_things where thing_id = %s',
                                [thing_id]).to_dict(orient='records')[0]

        sensor_data = self.query(
            'select * '
            'from pins_configurations '
            'where thing_id = %s;',
            [thing_id])

        channels = self.query('select * from mosquitto_channels')
        channels = channels.replace('room_name', room_data['room_name'], regex=True)
        channels = channels.replace('thing_name', thing_data['thing_name'], regex=True)

        if role == 'emitter':
            listen = channels.query('channel_name == "thing_commands"')['channel_broadcast'].to_list()
            listen += channels.query('channel_name == "group_commands"')['channel_broadcast'].to_list()

        elif role == 'receiver':
            listen = channels.query('channel_name == "thing_info"')['channel_broadcast'].to_list()

        mqtt_data = {
            'channels': channels,
            'configuration': self.query('select * from mosquitto_configuration').to_dict(orient='records')[0],
            'listen': listen
        }

        commands_data = self.query('select * from commands where info_level = %s and info_id = %s', [3, thing_id])

        data = {
            'info_id': thing_id,
            'room_data': room_data,
            'thing_data': thing_data,
            'sensor_data': sensor_data,
            'commands_data': commands_data,
            'mqtt_data': mqtt_data
        }
        return data

    def get_room_data(self, room_id):

        room_data = self.query('select * from home_rooms where room_id = %s', [room_id]).to_dict(orient='records')[0]

        thing_data = self.query(
            'select * from home_things where '
            'thing_id = (select thing_id from rooms_things where rooms_room_id = %s)', [room_id])

        sensor_data = self.query(
            'select * from pins_configurations where thing_id = '
            '(select thing_id from rooms_things where rooms_room_id = %s);', [room_id]
        )

        channels = self.query('select * from mosquitto_channels')
        channels = channels.replace('room_name', room_data['room_name'], regex=True)

        listen = channels.query('channel_name == "room_commands"')['channel_broadcast'].to_list()
        listen += channels.query('channel_name == "group_commands"')['channel_broadcast'].to_list()

        l1 = channels.query('channel_name=="thing_interrupt"')
        for thing in thing_data.to_dict(orient='records'):
            listen += l1.replace('thing_name', thing['thing_name'], regex=True)['channel_broadcast'].to_list()

        mqtt_data = {
            'channels': channels,
            'configuration': self.query('select * from mosquitto_configuration').to_dict(orient='records')[0],
            'listen': listen
        }

        commands_data = self.query('select * from commands where info_level = %s and info_id = %s', [2, room_id])

        rules = self.query('select * from rules where info_level = %s and info_id = %s', [2, room_id])

        conditions = self.query('select * from conditions where condition_rule_id = '
                                '(select rule_id from rules where info_level = %s and info_id = %s)', [2, room_id])

        data = {
            'info_id': room_id,
            'room_data': room_data,
            'thing_data': thing_data,
            'sensor_data': sensor_data,
            'commands_data': commands_data,
            'rules_data': rules,
            'conditions_data': conditions,
            'mqtt_data': mqtt_data
        }

        return data

    def get_home_data(self):

        room_data = self.query('select * from home_rooms')
        thing_data = self.query('select * from home_things')
        sensor_data = self.query('select * from pins_configurations')
        channels = self.query('select * from mosquitto_channels')

        listen = channels.query('channel_name == "home_commands"')['channel_broadcast'].to_list()
        lis1 = channels.query('channel_name == "room_info"')

        for room in room_data.to_dict(orient='records'):
            l1 = lis1.replace('room_name', room['room_name'], regex=True)
            listen += l1['channel_broadcast'].to_list()

        mqtt_data = {
            'channels': channels,
            'configuration': self.query('select * from mosquitto_configuration').to_dict(orient='records')[0],
            'listen': listen
        }

        commands_data = self.query('select * from commands')
        rules = self.query('select * from rules')

        data = {
            'room_data': room_data,
            'thing_data': thing_data,
            'sensor_data': sensor_data,
            'commands_data': commands_data,
            'rules_data': rules,
            'mqtt_data': mqtt_data
        }

        return data
