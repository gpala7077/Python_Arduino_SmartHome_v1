import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from threading import Timer

import pandas as pd


class Condition:
    """Represents a single condition to a rule.

    Attributes
    -----------
    condition_rule_id : int
        Primary record ID in Database for condition

    condition_type : str
        Type of condition i.e average, sum, max, min

    condition_check: str
        Type of sensors or specific sensor. i.e. LDR, LDR1, lights, motion, motion2

    condition_logic : str
        Type of logic to apply condition. i.e. <, <=, >, >=, etc...

    condition_value : int
        Condition threshold to test live values.
        

    Parameters
    ----------
    data : dict
        Dictionary defined as {condition_name: condition_value}

    """

    def __init__(self, data):
        self.condition_rule_id = data['condition_rule_id']  # Set attributes
        self.condition_type = data['condition_type']
        self.condition_check = data['condition_check']
        self.condition_logic = data['condition_logic']
        self.condition_value = data['condition_value']

    def condition_met(self, data):
        """Checks if condition is met. Returns True if met, False if not.

        Parameters
        ----------
        data : DataFrame
            Pandas data frame containing the filtered data for condition.
        """

        if self.condition_type == 'sum':  # Check sum
            return eval('{}{}{}'.format(data['sensor_value'].sum(), self.condition_logic, self.condition_value))

        elif self.condition_type == 'average':  # Check mean
            return eval('{}{}{}'.format(data['sensor_value'].mean(), self.condition_logic, self.condition_value))

        elif self.condition_type == 'time':  # Check time constraints
            now = datetime.now()  # initialize datetime now variable
            current_time = now.strftime("%H:%M")  # reformat current time

            if self.condition_logic == '>':  # Check constraints
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
    """Represents a smart home rule.

    Attributes
    ----------
    rule_id : int
        Primary key for rule

    info_id : int
        Primary key for room/thing

    info_level: int
        Level of control. (i.e. 1 = home, 2 = room, 3 = thing)

    rule_name : str
        Name of rule

    commands : tuple
        A tuple containing 1 or 2 commands of class type Command. (cmd1, cmd2) or (cmd1)

    rule_timer : int
        Number of seconds before executing cmd2

    rule_sensor : str
        name of sensor or types of sensors that trigger the rule.

    conditions : list
        List of class type Condition

    Parameters
    ----------
    data : dict
        Dictionary containing all rule information

    commands : tuple
        A tuple containing 1 or 2 objects of class type Command. (cmd1, cmd2) or (cmd1)

    conditions : list of dict
        List of dictionaries defined as {condition_name: condition_value}

    """

    def __init__(self, data, commands, conditions):
        self.rule_id = data['rule_id']  # Set attributes
        self.info_id = data['info_id']
        self.info_level = data['info_level']
        self.rule_name = data['rule_name']
        self.commands = commands
        self.rule_timer = data['rule_timer']
        self.rule_sensor = data['rule_sensor']
        self.conditions = [Condition(condition) for condition in conditions]

    def check_conditions(self, status):
        """Simultaneously check all conditions in rule.

        Parameters
        ----------
        status : DataFrame
            Pandas data frame of all current sensors in room

        """

        conditions_check = []  # Initialize empty condition list
        results = []  # Initialize empty result list
        with ThreadPoolExecutor() as executor:  # Begin sub-threads
            for condition in self.conditions:  # iterate through each condition

                if any(char.isdigit() for char in condition.condition_check):
                    data = status.query('sensor_name == "{}"'.format(condition.condition_check))  # filter status data

                else:
                    data = status.query('sensor_type == "{}"'.format(condition.condition_check))  # filter status data

                conditions_check.append(executor.submit(condition.condition_met, data=data))  # submit to thread pool

            for result in as_completed(conditions_check):  # Wait until all conditions have finished
                results.append(result.result())  # Append result to result list

            if [True] * len(results) == results:  # If all conditions are met, return True
                return True
            else:
                return False

    def __repr__(self):
        """Canonical string representation of rule."""

        return self.rule_name


class Command:
    """Represents a single command.

    Attributes
    ----------
    info_id : int
        Primary key for room/thing

    info_level: int
        Level of control. (i.e. 1 = home, 2 = room, 3 = thing)

    command_name : str
        Name of command

    command_type : str
        Type of command

    command_sensor : str
        Type of sensor or group to send command to

    command_value : str
        Command value can be evaluated as a string, dictionary or int. Depends on type of command.

     Parameters
    ----------
    data : dict
        Dictionary containing all command information

    """

    def __init__(self, data):
        if isinstance(data, pd.DataFrame):
            data = data.to_dict(orient='records')[0]

        self.info_id = data['info_id']  # Set attributes
        self.info_level = data['info_level']
        self.command_name = data['command_name']
        self.command_type = data['command_type']
        self.command_sensor = data['command_sensor']
        self.command_value = data['command_value']

    def get_query(self):
        """Build query to call data"""

        if any(char.isdigit() for char in self.command_sensor):
            command = 'pin_name == "{}"'.format(self.command_sensor)

        else:
            command = 'pin_sensor == "{}"'.format(self.command_sensor)

        return command

    def __repr__(self):
        """Canonical string representation of command."""

        return '{} | {} | {} | {}'.format(self.command_name, self.command_type, self.command_sensor, self.command_value)


class Commands:
    """Represents all available commands.

    Attributes
    ----------
    data : dictionary
        Dictionary defined as {type of data : data}

    r_pi_read_write : function
        Function passed by Raspberry pi.

    current_status : DataFrame
        Pandas data frame representing the current status.

    mosquitto : object of Class Mosquitto
        Mosquitto class used to communicate with base

    third_party : dict of objects
        Dictionary of Third-party API objects

    timers : dict of Timers
        Dictionary of active rules and Timers.

    """

    def __init__(self):
        # Define empty attributes
        self.data = None
        self.r_pi_read_write = None
        self.current_status = None
        self.mosquitto = None
        self.third_party = None
        self.timers = {}

    def check_command(self, command):
        """Checks for the type of command, returns command or rule object."""

        if isinstance(command, dict):
            # If passed command is a dict then return a Command object
            command = Command(command)

        elif isinstance(command, str):
            # If passed command is a string
            if command.isdigit() and self.data['info_level'] < 3:  # If command is a number and less than info level 3
                command = Command(self.data['commands_data'].query(  # Get exact command record ID
                    'command_record_id == "{}"'.format(command)).to_dict(orient='records')[0])
            else:
                data = self.data['commands_data'].query(
                    'command_name == "{}" and '
                    'info_id == "{}" and '
                    'info_level == "{}"'.format(command, self.data['info_id'], self.data['info_level']))
                if data.empty:
                    print(data)
                    print(command, self.data['info_id'], self.data['info_level'])
                command = Command(data)

        elif isinstance(command, pd.DataFrame):
            # If passed command is a data frame. return a Rule object

            sensor_type = command['sensor_type'].tolist()[0]  # Get sensor type
            data = self.data['rules_data'].query('rule_sensor == "{}"'.format(sensor_type)).to_dict(
                orient='records')  # get rules data
            command = []

            for rule in data:
                if rule['rule_function'] != 'none':
                    cmd = (  # Build command tuple
                        Command(self.data['commands_data'].query('command_name == "{}"'.format(rule['rule_command'])).
                                to_dict(orient='records')[0]),

                        Command(self.data['commands_data'].query('command_name == "{}"'.format(rule['rule_function'])).
                                to_dict(orient='records')[0])
                    )
                else:
                    cmd = (  # Build command tuple
                        Command(self.data['commands_data'].query('command_name == "{}"'.format(rule['rule_command'])).
                                to_dict(orient='records')[0]), None)

                conditions = self.data['conditions_data'].query(  # Get all condition data
                    'condition_rule_id == {}'.format(rule['rule_id'])).to_dict(orient='records')

                command.append(Rule(rule, cmd, conditions))  # initialize new Rule object

        return command

    def execute(self, command, command_value=None, args=None):
        """Execute command."""

        command = self.check_command(command)  # Check type of command
        if command_value is not None:  # Force replace command value if requested
            command.command_value = command_value

        print(command)  # Print the canonical string representation

        if isinstance(command, Command):  # If object is of type Command
            # ***************** Raspberry Pi MCU commands *****************

            if command.command_type == 'write':
                self.r_pi_read_write(command.get_query(), 'write', command.command_value)

            elif command.command_type == 'read' and command.command_sensor == 'all':
                result = self.r_pi_read_write()
                self.mosquitto.broadcast(self.data['mqtt_data']['channels_dict']['thing_info'], result)

            elif command.command_type == 'read':
                result = self.r_pi_read_write(command.get_query())
                self.mosquitto.broadcast(self.data['mqtt_data']['channels_dict']['thing_info'], result)

            # ***************** HVAC Commands *****************
            elif command.command_type == 'HVAC' and (command.command_sensor == 'heat' or
                                                     command.command_sensor == 'cool' or
                                                     command.command_sensor == 'off'):
                command_sequence = {
                    'heat': ('AC_off', 'fan_off', 'heat_on', 'fan_on'),
                    'cool': ('heat_off', 'fan_off', 'AC_on', 'fan_on'),
                    'off': ('AC_off', 'heat_off', 'fan_off')
                }
                i = 0
                started = datetime.now()
                wait_interval = 10
                while i < len(command_sequence[command.command_sensor]):
                    if (datetime.now() - started).total_seconds() >= wait_interval:
                        print(self.execute('room_command', command_sequence[command.command_sensor][i]))
                        started = datetime.now()
                        i += 1

                args = ['check_temperature', command.command_value,
                        command.command_sensor]  # override command_value, additional argument
                self.timers.update(
                    {command.command_type: Timer(interval=60 * 5, function=self.execute, args=args)})
                self.timers[command.command_type].start()

            elif command.command_type == 'HVAC' and command.command_sensor == 'check':
                current_temperature = self.current_status().query('sensor_type=="temperature"')  # Get all temp readings
                current_temperature = current_temperature['sensor_value'].mean()  # Calculate average
                current_temperature = (current_temperature * 1.8) + 32  # Convert to F, comment out for Celcius
                print('Currently {}ing home to {}.'.format(args, command.command_value))
                if \
                        (args == 'cool' and current_temperature <= int(command.command_value)) or \
                        (args == 'heat' and current_temperature >= int(command.command_value)):

                    print('Requested temperature reached!')
                    print(self.execute('turn_off_HVAC'))

                else:
                    self.timers.pop(command.command_type)
                    args = ['check_temperature', command.command_value, args]  # override command_value,
                    self.timers.update(
                        {command.command_type: Timer(interval=60 * 5, function=self.execute, args=args)})
                    self.timers[command.command_type].start()

            # ***************** Phillips Hue - Third Party Commands *****************
            elif command.command_type == 'hue':

                command.command_value = command.command_value.replace("'", "\"")
                if command.command_sensor == 'group':
                    num = self.data['hue_data']['group_id']
                    print(self.third_party['hue'].set_group(num, command.command_value))

                else:
                    num = self.data['hue_data']['hue_groups'].query('name == "{}"'.format(
                        command.command_sensor))['group_id'].tolist()[0]
                    print(self.third_party['hue'].set_group(num, command.command_value))

            # ***************** PushBullet - Third Party Commands *****************
            elif command.command_type == 'push':
                if command.command_sensor == 'push_message':
                    data = command.command_value.replace("'", "\"")  # Replace single for double quotes
                    data = json.loads(data)
                    title = data['title']
                    body = data['body']
                    self.third_party['push'].push.push_note(title=title, body=body)

            # ***************** Sonos - Third Party Commands *****************
            elif command.command_type == 'sonos':
                if command.command_sensor == 'listen' and command.command_value == 'random':
                    self.third_party['sonos'].listen()

                elif command.command_sensor == 'listen':
                    self.third_party['sonos'].listen(command.command_value)

                elif command.command_sensor == 'speak':
                    current = self.third_party['sonos'].player.volume
                    self.third_party['sonos'].player.volume += 25
                    self.third_party['sonos'].speak(command.command_value)
                    self.third_party['sonos'].player.volume = current

            # ***************** Broadcast commands *****************
            elif command.command_type == 'broadcast':
                if command.command_sensor == 'group':
                    channel = self.data['mqtt_data']['channels'].query('channel_name == "group_commands"')
                    group_name = self.data['group_data'].query('info_id == {} and info_level == {}'.format(
                        self.data['info_id'], self.data['info_level']))['group_name'].tolist()[0]

                    channel = channel.replace('group_name', group_name, regex=True)
                    channel = channel['channel_broadcast'].tolist()

                    self.mosquitto.broadcast(channel, command.command_value)

                elif 'thing' in command.command_sensor:
                    num = int(list(filter(lambda x: x.isdigit(), command.command_sensor))[0])
                    channel = self.data['mqtt_data']['broadcast'][num]

                    self.mosquitto.broadcast(channel, command.command_value)

                elif command.command_sensor == 'room':
                    channel = self.data['mqtt_data']['channels_dict']['room_info']
                    self.mosquitto.broadcast(channel, str(self.current_status(current=True).to_dict(orient='list')))

            # ***************** App commands *****************
            elif command.command_type == 'app':
                channel = self.data['mqtt_data']['channels_dict']['room_commands']
                payload = command.command_value
                self.mosquitto.broadcast(channel, str(payload))

            return '{} | Command executed successfully'.format(command)

        elif len(command) > 0 and (command, list) and isinstance(command[0], Rule):
            status = self.current_status(current=False)  # True for current status, False for last known status.
            check_rules = []  # Initialize empty condition list
            results = []  # Initialize empty result list

            with ThreadPoolExecutor() as executor:  # Begin sub-threads
                for cmd in command:  # iterate through each command
                    check_rules.append(
                        executor.submit(self.process_rule, rule=cmd, status=status))  # submit to thread pool

                for result in as_completed(check_rules):  # Wait until all conditions have finished
                    results.append(result.result())  # Append result to result list
            print(results)

    def process_rule(self, rule, status):
        if rule.check_conditions(status):  # If Rule passes all conditions
            if rule.rule_sensor in self.timers:  # If timer exists, cancel and replace
                self.timers[rule.rule_sensor].cancel()

            if rule.rule_timer > 0:  # Create new timer
                self.timers.update(
                    {rule.rule_sensor: Timer(interval=rule.rule_timer, function=self.execute, args=[rule.commands[1]])})
                self.timers[rule.rule_sensor].start()
            return self.execute(rule.commands[0])
