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

    """

    def __init__(self):
        # Save credentials
        self.credentials = None
        self.db = None
        self.cursor = None

    def initialize(self):
        """Log in and Set Cursor."""

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
            if not data.empty:
                column_names = [col_name[0] for col_name in self.cursor.description]

                data.columns = column_names
                return data
            else:
                return None

        elif 'insert' in query:  # If query is insert type. return primary key of the inserted row.
            if values is not None:
                self.cursor.execute(query, values)
            else:
                self.cursor.execute(query)
            self.db.commit()
            last_id = self.cursor.getlastrowid()
            print('last id =', last_id)
            return last_id

        elif 'replace' in query or 'delete' in query:
            if values is not None:
                self.cursor.execute(query, values)
            else:
                self.cursor.execute(query)
            self.db.commit()

    def replace_insert_data(self, query_type, table, data):
        columns = list(data.to_dict(orient='records')[0].keys())
        columns = ', '.join(columns)

        if query_type == 'replace':
            sql = 'replace into {} ({}) values '.format(table, columns)

        elif query_type == 'insert':
            sql = 'insert into {} ({}) values '.format(table, columns)

        values = []

        for row in data.to_dict(orient='records'):
            val = []
            for v in list(row.values()):
                if isinstance(v, int):
                    val.append(str(v))
                else:
                    val.append('"{}"'.format(v))

            val = ', '.join(val)
            values.append('({})'.format(val))

        sql += ', '.join(values)
        self.query(sql)
        return 'Data Updated'

    def get_thing_data(self, thing_id, role):
        """Get all necessary thing data"""

        # Get room_name
        room_data = self.query(
            'select room_name from home_rooms where room_id = '
            '(select rooms_room_id from rooms_things where rooms_thing_id = %s)',
            [thing_id]).to_dict(orient='records')[0]

        # Get All Thing data
        thing_data = self.query('select * from home_things where thing_id = %s',
                                [thing_id]).to_dict(orient='records')[0]
        # Get all sensor data
        sensor_data = self.query(
            'select * '
            'from pins_configurations '
            'where thing_id = %s;',
            [thing_id])

        group_data = self.query('select * from home_groups where group_id '
                                'IN(select group_id from groups_rooms_things where info_id = %s and info_level=%s)',
                                [thing_id, 3])

        # Get all channels and replace room and thing name
        channels = self.query('select channel_name, channel_broadcast from mosquitto_channels')
        channels = channels.replace('room_name', room_data['room_name'], regex=True)
        channels = channels.replace('thing_name', thing_data['thing_name'], regex=True)

        if role == 'emitter':
            listen = []
            for group in group_data:
                replace = channels.replace('group_name', group['group_name'], regex=True)
                listen += replace.query('channel_name == "group_commands"')['channel_broadcast'].tolist()

            listen += channels.query('channel_name == "thing_commands"')['channel_broadcast'].tolist()

        elif role == 'receiver':
            listen = channels.query('channel_name == "thing_info"')['channel_broadcast'].tolist()

        channels_dict = {}
        for channel in channels.to_dict(orient='records'):
            channels_dict.update({channel['channel_name']: [channel['channel_broadcast']]})

        mqtt_data = {
            'channels_dict': channels_dict,
            'channels': channels,
            'configuration': self.query('select * from mosquitto_configuration').to_dict(orient='records')[0],
            'listen': listen
        }

        commands_data = self.query('select * from commands where info_level = %s and info_id = %s', [3, thing_id])

        data = {
            'info_id': thing_id,
            'info_level': 3,
            'group_data': group_data,
            'room_data': room_data,
            'thing_data': thing_data,
            'sensor_data': sensor_data,
            'commands_data': commands_data,
            'mqtt_data': mqtt_data
        }
        return data

    def get_room_data(self, room_id):
        """Get all necessary room data"""
        # get room data
        room_data = self.query('select * from home_rooms where room_id = %s', [room_id]).to_dict(orient='records')[0]

        # Get all things associated with that room
        thing_data = self.query(
            'select * from home_things where '
            'thing_id = (select rooms_thing_id from rooms_things where rooms_room_id = %s)', [room_id])

        # Get all pin configurations for room
        sensor_data = self.query(
            'select * from pins_configurations where thing_id = '
            '(select rooms_thing_id from rooms_things where rooms_room_id = %s);', [room_id]
        )

        group_listen = self.query('select group_id, group_name from home_groups where group_id '
                                  'IN(select group_id from groups_rooms_things where info_id = %s and info_level=%s)',
                                  [room_id, 2]).to_dict(orient='records')

        group_data = self.query('select * from home_groups where info_id = %s and info_level=%s',
                                [room_id, 2])

        # Get all mosquitto channels
        channels = self.query('select * from mosquitto_channels')
        channels = channels.replace('room_name', room_data['room_name'], regex=True)  # prepare channels
        # Prepare listening channels
        listen = []
        for group in group_listen:
            replace = channels.replace('group_name', group['group_name'], regex=True)
            listen += replace.query('channel_name == "group_commands"')['channel_broadcast'].tolist()

        listen += channels.query('channel_name == "room_commands"')['channel_broadcast'].tolist()

        l1 = channels.query('channel_name=="thing_interrupt"')
        b1 = channels.query('channel_name=="thing_commands"')
        things = {}
        for thing in thing_data.to_dict(orient='records'):
            listen += l1.replace('thing_name', thing['thing_name'], regex=True)['channel_broadcast'].tolist()
            things.update({thing['thing_id']: b1.replace('thing_name', thing['thing_name'], regex=True)[
                'channel_broadcast'].tolist()})

        channels_dict = {}
        for channel in channels.to_dict(orient='records'):
            channels_dict.update({channel['channel_name']: [channel['channel_broadcast']]})

        mqtt_data = {
            'channels_dict': channels_dict,
            'channels': channels,
            'configuration': self.query('select * from mosquitto_configuration').to_dict(orient='records')[0],
            'listen': listen,
            'broadcast': things
        }

        commands_data = self.query('select * from commands where info_level = %s and info_id = %s', [2, room_id])

        rules = self.query('select * from rules where info_level = %s and info_id = %s', [2, room_id])

        conditions = self.query('select * from conditions where condition_rule_id '
                                'IN(select rule_id from rules where info_level = %s and info_id = %s)', [2, room_id])
        hue_groups = self.query('select group_id, name from hue_groups')

        group_id = hue_groups.query('name == "{}"'.format(room_data['room_name']))['group_id'].tolist()[0]
        hue_data = {'group_id': group_id, 'hue_groups': hue_groups, 'hue_lights': None}
        data = {
            'info_id': room_id,
            'info_level': 2,
            'hue_data': hue_data,
            'room_data': room_data,
            'group_data': group_data,
            'thing_data': thing_data,
            'sensor_data': sensor_data,
            'commands_data': commands_data,
            'rules_data': rules,
            'conditions_data': conditions,
            'mqtt_data': mqtt_data
        }

        return data

    def get_home_data(self):
        """Get all necessary home data"""

        room_data = self.query('select * from home_rooms')
        thing_data = self.query('select * from home_things')
        sensor_data = self.query('select * from pins_configurations')
        channels = self.query('select * from mosquitto_channels')
        listen = channels.query('channel_name == "home_commands"')['channel_broadcast'].tolist()
        lis1 = channels.query('channel_name == "room_info"')

        for room in room_data.to_dict(orient='records'):
            l1 = lis1.replace('room_name', room['room_name'], regex=True)
            listen += l1['channel_broadcast'].tolist()

        channels_dict = {}
        for channel in channels.to_dict(orient='records'):
            channels_dict.update({channel['channel_name']: [channel['channel_broadcast']]})

        mqtt_data = {
            'channels_dict': channels_dict,
            'channels': channels,
            'configuration': self.query('select * from mosquitto_configuration').to_dict(orient='records')[0],
            'listen': listen
        }

        commands_data = self.query('select * from commands where info_id = %s and info_level = %s', [1, 1])
        rules = self.query('select * from rules')

        group_data = self.query('select * from home_groups where group_id '
                                'IN(select group_id from groups_rooms_things where info_id = %s and info_level=%s)',
                                [1, 1])

        hue_groups = self.query('select group_id, name from hue_groups')
        group_id = hue_groups.query('name == "{}"'.format('Home'))['group_id'].tolist()[0]
        hue_data = {'group_id': group_id, 'hue_groups': hue_groups, 'hue_lights': None}

        data = {
            'info_level': 1,
            'info_id':  1,
            'hue_data': hue_data,
            'room_data': room_data,
            'thing_data': thing_data,
            'group_data': group_data,
            'sensor_data': sensor_data,
            'commands_data': commands_data,
            'rules_data': rules,
            'mqtt_data': mqtt_data
        }

        return data
