from modules.database_manager import Database
from modules.home_control import Room


def load_data():
    credentials = {
        'username': 'self',
        'password': 'password',
        'database': 'smart_home',
        'host': '192.168.50.90'
    }
    db = Database(credentials)

    room_id = 1

    room_data = db.query('select * from home_rooms where room_id = %s', [room_id])[0]
    thing_data = db.query(
        'select * from home_things where '
        'thing_id = (select thing_id from rooms_things where rooms_room_id = %s)', [room_id])

    sensor_data = db.query(
                    'select * from pins_configurations where thing_id = '
                    '(select thing_id from rooms_things where rooms_room_id = %s);', [room_id]
                )
    mqtt_data = {
        'type': 'room',
        'channels': db.query('select * from mosquitto_channels'),
        'configuration': db.query('select * from mosquitto_configuration')[0],
        'listen': ['room_interrupts', 'room_commands']
    }
    commands_data = db.query('select * from commands where info_type = %s and info_id = %s', ['room', room_id])

    rules = db.query('select * from rules where info_type = %s and info_id = %s', ['room', room_id])

    for rule in rules:
        rule.update(
            {'conditions': db.query('select * from conditions where condition_rule_id = %s', [rule['rule_id']])}
        )

    data = {
        'room_data': room_data,
        'thing_data': thing_data,
        'sensor_data': sensor_data,
        'commands_data': commands_data,
        'rules_data': rules,
        'mqtt_data': mqtt_data
    }

    return {'data': data, 'query': db.query}


if __name__ == '__main__':
    info = load_data()
    room = Room(info['data'], info['query'])
