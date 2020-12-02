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
        self.db.commit()                    # Ensure all changes are committed before querying.

        if 'select' in query:               # If query is select type. return pandas data frame
            if values is not None:
                self.cursor.execute(query, values)
            else:
                self.cursor.execute(query)

            data = pd.DataFrame(self.cursor.fetchall())
            column_names = [col_name[0] for col_name in self.cursor.description]

            # Add column names
            data.columns = column_names

            return data

        elif 'insert' in query:             # If query is insert type. return primary key of the inserted row.
            self.cursor.execute(query, values)
            self.db.commit()
            last_id = self.cursor.getlastrowid()
            print('last id =', last_id)
            return last_id

    def get_thing_data(self, primary_key):

        room_data = self.query(
            'select * from home_rooms where room_id = '
            '(select rooms_room_id from rooms_things where rooms_thing_id = %s)',
            [primary_key]).to_dict(orient='records')[0]

        thing_data = self.query('select * from home_things where thing_id = %s',
                                [primary_key]).to_dict(orient='records')[0]

        sensor_data = self.query(
            'select * '
            'from pins_configurations '
            'where thing_id = %s;',
            [primary_key])

        channels = self.query('select * from mosquitto_channels')
        channels = channels.replace('room_name', room_data['room_name'], regex=True)
        channels = channels.replace('thing_name', thing_data['thing_name'], regex=True)

        listen = channels.query('channel_name == "thing_commands"')['channel_broadcast'].to_list()
        listen += channels.query('channel_name == "group_commands"')['channel_broadcast'].to_list()

        mqtt_data = {
            'channels': channels,
            'configuration': self.query('select * from mosquitto_configuration').to_dict(orient='records')[0],
            'listen': listen
        }

        commands_data = self.query('select * from commands where info_type = %s and info_id = %s', ['thing', primary_key])

        data = {
            'room_data': room_data,
            'thing_data': thing_data,
            'sensor_data': sensor_data,
            'commands_data': commands_data,
            'mqtt_data': mqtt_data
        }
        return data
