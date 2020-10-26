from threading import Timer, Thread
from datetime import datetime
import numpy
import RPi.GPIO as GPIO
import time


def write_value(key, value):
    # function takes two variables. key indicates the designated PIN # and value indicates the requested value change
    GPIO.output(int(key), int(value))
    time.sleep(.01)


class Commands:
    def __init__(self, data, mosquitto, additional_data=None):
        self.data = data
        self.timers = dict()
        self.targets = dict()
        self.mosquitto = mosquitto
        self.additional_data = additional_data

    def get_command(self, command):
        for cmd in self.data:
            if command == cmd['command_name']:
                return cmd

    def create_thread(self, thread_type, command_data):
        if thread_type == 'timer':
            if command_data['rule_name'] in list(self.timers.keys()):
                print('Timer exists... Resetting timer')
                self.timers[command_data['rule_name']].update({command_data['rule_name']: datetime.now()})
                return
            else:
                print('Creating new timer for {}'.format(command_data['rule_name']))
                Thread(target=self.create_timer, args=(command_data,))
                return

    def create_timer(self, command_data):
        new_data = {
                'rule_name': command_data['rule_name'],
                'result': command_data['rule_function'],
                'rule_timer': 0,
                'rule_function': None}

        self.timers.update({command_data['rule_name']: datetime.now()})
        time_since = datetime.now() - self.timers[command_data['rule_name']]

        while time_since < command_data['rule_timer']:
            print('Time since last recorded movement... {}'.format(time_since))
            time_since = datetime.now() - self.timers[command_data['rule_name']]
            time.sleep(1)

        print('Finished timer for {}'.format(command_data['rule_name']))
        self.timers.pop(command_data['rule_name'])
        self.command(new_data)

    def command(self, command_data):
        if command_data['result'] is None:
            return

        if command_data['rule_timer'] > 0:
            self.create_thread('timer', command_data)

        print('Action: {}. Activated'.format(command_data['result']))

        command = self.get_command(command_data['result'])
        command_type = command['command_type']
        command_sensor = command['command_sensor']
        command_value = command['command_value']

        if command_type == 'hue':
            print('Sending Hue Group Command')
            group_command = {}
            command_value = command_value.split(';')

            for cmd in command_value:
                cmd = cmd.split(':')
                group_command.update({cmd[0]: eval(cmd[1])})
            response = self.additional_data['hue'].set_group(command['info_id'], group_command)
            print(response)

        elif command_type == 'write':
            print('Writing to pin...')
            for pin in self.additional_data['sensor_org'][command_sensor]:
                write_value(pin, command_value)

        elif 'broadcast_' in command_type:
            print('Broadcasting...')
            channel = command_type.replace('broadcast_', '')
            self.mosquitto.broadcast(channel, command_value)

        elif command_type == 'read_thing':
            print('Reading data...')
            if command_sensor == 'all':
                result = self.additional_data['status']()
                self.mosquitto.broadcast('thing_info', str(result))
            else:
                for pin in self.additional_data['sensor_org'][command_sensor]:
                    message = str(self.additional_data['sensors'][pin].state())
                    self.mosquitto.broadcast('sensor_value', message, pin)

        elif command_type == 'HVAC':
            print('Regulating Temperature...')
            target = eval(command_value.split(';')[0])
            math = eval(command_value.split(';')[2])

            op = {'average': numpy.mean(self.additional_data['status']['temperature']),
                  'sum': numpy.sum(self.additional_data['status']['temperature']),
                  'min': numpy.min(self.additional_data['status']['temperature']),
                  'max': numpy.max(self.additional_data['status']['temperature']),
                  'median': numpy.median(self.additional_data['status']['temperature'])
                  }

            print(op[math])
            print(target)

            if target > op[math]:
                start_commands = ['heat_on', 'fan_on']
                stop_commands = ['heat_off', 'fan_off']

            elif target < op[math]:
                start_commands = ['AC_on', 'fan_on']
                stop_commands = ['AC_off', 'fan_off']

            self.create_target(command_data, start_commands, stop_commands)

        elif command_type == 'data':
            self.data['reload']

