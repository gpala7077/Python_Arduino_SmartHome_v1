from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from threading import Timer

import pandas as pd


class Action(Timer):
    def __init__(self, command, interval, fn):
        super().__init__(interval, fn, args=[command])
        self.start()


class Condition:
    def __init__(self, data):
        self.condition_rule_id = data['condition_rule_id']
        self.condition_type = data['condition_type']
        self.condition_check = data['condition_check']
        self.condition_logic = data['condition_logic']
        self.condition_value = data['condition_value']

    def condition_met(self, data):

        if self.condition_type == 'sum':
            return eval('{}{}{}'.format(data['sensor_value'].sum(), self.condition_logic, self.condition_value))

        elif self.condition_type == 'average':
            return eval('{}{}{}'.format(data['sensor_value'].mean(), self.condition_logic, self.condition_value))

        elif self.condition_type == 'time':
            now = datetime.now()
            current_time = now.strftime("%H:%M")

            if self.condition_logic == '>':
                return current_time > self.condition_value

            elif self.condition_logic == '>=':
                return current_time >= self.condition_value

            elif self.condition_logic == '<':
                return current_time < self.condition_value

            elif self.condition_logic == '<=':
                return current_time <= self.condition_value

            elif self.condition_logic == '==':
                return current_time == self.condition_value

            elif self.condition_logic == '!=':
                return current_time != self.condition_value


class Rule:
    def __init__(self, data, commands, conditions):
        self.rule_id = data['rule_id']
        self.info_id = data['info_id']
        self.info_level = data['info_level']
        self.rule_name = data['rule_name']
        self.commands = commands
        self.rule_timer = data['rule_timer']
        self.rule_sensor = data['rule_sensor']
        self.conditions = [Condition(condition) for condition in conditions]

    def check_conditions(self, status):
        conditions_check = []
        results = []
        with ThreadPoolExecutor(max_workers=10) as executor:
            for condition in self.conditions:
                data = status.query('sensor_type == "{}"'.format(condition.condition_check))
                conditions_check.append(
                    executor.submit(condition.condition_met, data=data)
                )

            for result in as_completed(conditions_check):
                results.append(result.result())

            if [True] * len(results) == results:
                return True
            else:
                return False

    def __repr__(self):
        return self.rule_name


class Command:
    def __init__(self, data):
        self.info_id = data['info_id']
        self.info_level = data['info_level']
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

    def __repr__(self):
        return self.command_name


class Commands:
    def __init__(self):
        self.data = None
        self.r_pi_read_write = None
        self.current_status = None
        self.mosquitto = None
        self.third_party = None
        self.timers = {}

    def check_command(self, command):
        if isinstance(command, str):
            command = Command(self.data['commands_data'].query(
                'command_name == "{}"'.format(command)).to_dict(orient='records')[0])

        elif isinstance(command, pd.DataFrame):
            sensor_type = command['sensor_type'].to_list()[0]
            data = self.data['rules_data'].query('rule_sensor == "{}"'.format(sensor_type)).to_dict(
                orient='records')[0]

            cmd = (
                Command(self.data['commands_data'].query('command_name == "{}"'.format(data['rule_command'])).
                        to_dict(orient='records')[0]),
                Command(self.data['commands_data'].query('command_name == "{}"'.format(data['rule_function'])).
                        to_dict(orient='records')[0])
            )
            conditions = self.data['conditions_data'].query(
                'condition_rule_id == {}'.format(data['rule_id'])).to_dict(orient='records')

            command = Rule(data, cmd, conditions)

        return command

    def execute(self, command):
        command = self.check_command(command)
        print(command)

        if isinstance(command, Command):
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

            # Phillips Hue - Third Party Commands
            elif command.command_type == 'hue':

                command.command_value = command.command_value.replace("'", "\"")
                if command.command_sensor == 'group':
                    print(self.third_party['hue'].set_group(self.data['info_id'], command.command_value))

                elif 'light' in command.command_sensor:
                    num = list(filter(lambda x: x.isdigit(), command.command_sensor))[0]
                    print(self.third_party['hue'].set_light(num, command.command_value))

            # Broadcasting to Thing commands
            elif command.command_type == 'broadcast':

                if command.command_sensor == 'group':
                    channel = self.data['mqtt_data']['channels'].query('channel_name == "group_commands"')[
                        'channel_broadcast'].to_list()
                    self.mosquitto.broadcast(channel, command.command_value)

                elif 'thing' in command.command_sensor:
                    num = list(filter(lambda x: x.isdigit(), command.command_sensor))[0]
                    channel = self.data['mqtt_data']['broadcast'][num]
                    self.mosquitto.broadcast(channel, command.command_value)

            return 'Command executed successfully'

        elif isinstance(command, Rule) and command.check_conditions(self.current_status()):
            if command.rule_timer > 0 and command.rule_id in self.timers:
                self.timers[command.rule_id].cancel()
                self.timers.update({command.rule_id: Action(command.commands[1], command.rule_timer, self.execute)})
                return self.execute(command.commands[0])

            elif command.rule_timer > 0:
                self.timers.update({command.rule_id: Action(command.commands[1], command.rule_timer, self.execute)})
                return self.execute(command.commands[0])

            else:
                return self.execute(command.commands[0])
