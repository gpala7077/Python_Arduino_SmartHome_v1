class Command:
    def __init__(self, data):
        self.info_id = data['info_id']
        self.info_type = data['info_type']
        self.command_name = data['command_name']
        self.command_type = data['command_type']
        self.command_sensor = data['command_sensor']
        self.command_value = data['command_value']

    def get_query(self):

        if any(char.isdigit() for char in self.command_sensor):
            command = 'pin_name == "{}"'.format(self.command_sensor)

        else:
            command = 'pin_sensor == "{}"'.format(self.command_sensor)

        return command


class Commands:
    def __init__(self, data):
        self.data = data
        self.r_pi_read_write = None
        self.mosquitto = None

    def execute(self, command):

        command = Command(self.data['commands_data'].query(
            'command_name == "{}"'.format(command)).to_dict(orient='records')[0])

        # Raspberry Pi MCU commands
        if command.command_type == 'write':
            self.r_pi_read_write(command.get_query(), 'write', command.command_value)

        elif command.command_type == 'read' and command.command_sensor == 'all':
            result = self.r_pi_read_write()
            self.mosquitto.broadcast(self.data['mqtt_data']['channels'].
                                     query('channel_name=="thing_info"')['channel_broadcast'].to_list(), result)

        elif command.command_type == 'read':
            result = self.r_pi_read_write(command.get_query())
            self.mosquitto.broadcast(self.data['mqtt_data']['channels'].
                                     query('channel_name=="thing_info"')['channel_broadcast'].to_list(), result)

        return 'Command executed successfully'
