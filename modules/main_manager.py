import json
from datetime import datetime

import pandas as pd

from modules.commands_manager import Commands
from modules.database_manager import Database
from modules.mosquitto_manager import MQTT_Client
from modules.project_manager import Projects


class Main:
    """Base framework for smart home main loops

    Attributes
    ----------
    db : object
        Object of type Database()

    third_party : dict
        Dictionary of third_party objects

    data : dict
        Dictionary containing all necessary data defined as {data_name : data}

    mosquitto : object
        Object of type Mosquitto

    commands : object
        Object of type Commands

    status : DataFrame
        Pandas data frame containing current sensor data

    Parameters
    ----------

    credentials : dict
        Database credentials defined as {'username': 'un', 'password': 'pwd', 'database': 'name', 'host': 'IP'}

    """

    def __init__(self, credentials):
        self.db = Database(credentials)  # Set credentials
        self.name = None
        self.third_party = dict()
        self.data = None
        self.mosquitto = MQTT_Client()
        self.commands = Commands()
        self.projects = Projects()
        self.interrupts = None
        self.status = pd.DataFrame()
        self.tasks = dict()
        self.role = None
        self.new_status_flag = False

    def initialize(self):
        """Start up program"""
        print('Initializing {} | {}'.format(self.__class__.__name__, self.name))
        self.mosquitto.host_ip = self.data['mqtt_data']['configuration']['mqtt_value']  # Get broker ip address
        self.mosquitto.process_message = self.process_message               # Define callback

        self.commands.data = self.data  # commands data
        self.commands.mosquitto = self.mosquitto  # Give command access to MQTT

        print(self.mosquitto.connect())  # Log info
        print(self.mosquitto.listen(self.data['mqtt_data']['listen']))  # Log info

    def process_message(self):
        topic, msg = self.mosquitto.messages.get()

        if self.role == 'executor':
            if 'interrupt' in topic:  # If interrupt
                msg = msg.replace("'", "\"")  # Replace single for double quotes
                msg = json.loads(msg)  # convert string to dictionary
                msg = pd.DataFrame.from_dict(msg)  # Convert dictionary to data frame
                print(self.commands.execute(msg))  # Execute command based on the latest interrupt

            elif 'commands' in topic:  # If command
                print(self.commands.execute(msg))

        elif 'info' in topic:  # If info
            self.new_status_flag = True
            msg = msg.replace("'", "\"")  # Replace single for double quotes
            msg = json.loads(msg)  # convert to dictionary
            self.status = pd.DataFrame.from_dict(msg)  # Convert to data frame and replace sensors

    def on_push(self, data):

        print("Received data:\n{}".format(data))
        latest_push = self.third_party['push'].push.get_pushes()[0]
        if 'title' not in latest_push:
            if 'send command' in latest_push['body']:
                command = latest_push['body'].split('send command ')[1]

                self.third_party['push'].push.push_note('Commands', self.commands.execute(command))

            elif 'task tracker' in latest_push['body']:

                task_id = list(filter(lambda x: x.isdigit(), latest_push['body']))
                task_id = int(''.join(task_id))

                notes = latest_push['body'].split(' notes ')[1]
                not_completed = 'not completed' in latest_push['body']
                completed = 'completed' in latest_push['body']

                task = self.db.query(
                    'select * from tasks_tracker where task_id = %s and task_timestamp = DATE(NOW())', [task_id])

                if task is not None:
                    if not_completed:
                        self.third_party['push'].push.push_note('Tasks', 'Replaced Task log. Try again tomorrow...')
                        task['task_completed'] = False

                    elif completed:
                        self.third_party['push'].push.push_note('Tasks', 'Replaced Task log. Great comeback!')
                        task['task_completed'] = True

                    task['task_notes'] = notes
                    task['task_timestamp'] = datetime.now()
                    task['task_id'] = task_id
                    self.db.replace_insert_data('replace', 'tasks_tracker', task)

                else:

                    task = pd.DataFrame(columns=['task_id', 'task_timestamp', 'task_completed', 'task_notes'])
                    new_row = {'task_id': task_id, 'task_timestamp': datetime.now(), 'task_notes': notes}

                    if not_completed:
                        self.third_party['push'].push.push_note('Tasks', 'Added new task log. Try again tomorrow...')
                        new_row.update({'task_completed': False})

                    elif completed:
                        self.third_party['push'].push.push_note('Tasks', 'Added new task log. Great job!')
                        new_row.update({'task_completed': True})
                    task = task.append(new_row, ignore_index=True)
                    self.db.replace_insert_data('insert', 'tasks_tracker', task)

            elif 'journal entry' in latest_push['body']:
                entry = self.db.query(
                    'select * from reflections where reflection_timestamp = DATE(NOW())')

                new_entry = latest_push['body'].split('entry ')[1]

                if entry is not None:
                    entry['reflection_entry'] = new_entry
                    self.db.replace_insert_data('replace', 'reflections', entry)
                    self.third_party['push'].push.push_note('Reflections', 'Replaced reflection entry. Till tomorrow...')

                else:
                    entry = pd.DataFrame(columns=['reflection_timestamp', 'reflection_entry'])
                    entry = entry.append({'reflection_timestamp': datetime.now(), 'reflection_entry': new_entry},
                                         ignore_index=True)
                    self.db.replace_insert_data('insert', 'reflections', entry)
                    self.third_party['push'].push.push_note('Reflections', 'Added reflection entry. Till tomorrow...')

            elif 'vitals' in latest_push['body']:
                reading = pd.DataFrame(columns=['vitals_human_id', 'vitals_timestamp', 'vitals_reading', 'vitals_value'])

                if 'blood pressure' in latest_push['body']:
                    human_id = latest_push['body'].split('human ID=')[1]
                    human_id = human_id.split(',')[0]
                    vitals_value = latest_push['body'].split('reading=')[1]
                    vitals_value = vitals_value.split(',')[0]
                    vitals_value = vitals_value.split('/')
                    vitals_timestamp = datetime.now()
                    print(vitals_value)

                    systolic = {
                     'vitals_human_id': human_id,
                     'vitals_timestamp': vitals_timestamp,
                     'vitals_reading': 'Blood Pressure Systolic',
                     'vitals_value': vitals_value[0]}

                    dystolic = {
                     'vitals_human_id': human_id,
                     'vitals_timestamp': vitals_timestamp,
                     'vitals_reading': 'Blood Pressure Dystolic',
                     'vitals_value': vitals_value[1]}

                    reading = reading.append(systolic, ignore_index=True)
                    reading = reading.append(dystolic, ignore_index=True)

                    self.db.replace_insert_data('insert', 'vitals', reading)
                    self.third_party['push'].push.push_note('Human Vitals', 'Added blood pressure entries.')

                elif 'heart rate' in latest_push['body']:
                    human_id = latest_push['body'].split('human ID=')[1]
                    human_id = human_id.split(',')[0]
                    vitals_value = latest_push['body'].split('reading=')[1]
                    vitals_value = vitals_value.split(',')[0]
                    print(vitals_value)

                    heart_rate = {
                     'vitals_human_id': human_id,
                     'vitals_timestamp': datetime.now(),
                     'vitals_reading': 'Heart Rate',
                     'vitals_value': vitals_value}

                    reading = reading.append(heart_rate, ignore_index=True)

                    self.db.replace_insert_data('insert', 'vitals', reading)
                    self.third_party['push'].push.push_note('Human Vitals', 'Added Heart Rate entry.')

                elif 'oxygen' in latest_push['body']:
                    human_id = latest_push['body'].split('human ID=')[1]
                    human_id = human_id.split(',')[0]
                    vitals_value = latest_push['body'].split('reading=')[1]
                    vitals_value = vitals_value.split(',')[0]
                    print(vitals_value)

                    heart_rate = {
                     'vitals_human_id': human_id,
                     'vitals_timestamp': datetime.now(),
                     'vitals_reading': 'Oxygen %',
                     'vitals_value': vitals_value}

                    reading = reading.append(heart_rate, ignore_index=True)

                    self.db.replace_insert_data('insert', 'vitals', reading)
                    self.third_party['push'].push.push_note('Human Vitals', 'Added Oxygen % entry.')

            elif 'moods' in latest_push['body']:
                reading = pd.DataFrame(columns=['mood_timestamp', 'mood_value', 'mood_reason'])
                mood = latest_push['body'].split('mood=')[1]
                mood = mood.split(',')[0]
                reason = latest_push['body'].split('reason=')[1]
                reason = reason.split(',')[0]
                print(reason)

                new_row = {
                 'mood_timestamp': datetime.now(),
                 'mood_value': mood,
                 'mood_reason': reason
                }
                reading = reading.append(new_row, ignore_index=True)

                self.db.replace_insert_data('insert', 'moods', reading)
                self.third_party['push'].push.push_note('Moods', 'Added Mood entry.')

            elif 'current task status' == latest_push['body']:
                time_block = self.projects.get_current_time_block()
                time_block = time_block['time_block_id'].tolist()[0]
                task = self.projects.get_current_task(time_block).to_dict(orient='records')[0]

                time_diff = self.projects.get_time_block(task['task_block_end'])['time_block_end'].tolist()[0]
                time_diff = time_diff - datetime.now()

                title, body = self.projects.format_task(task, time_diff)

                self.third_party['push'].push.push_note(title, body)

            elif 'current goal status' == latest_push['body']:
                title = 'Goals'
                goals = self.projects.get_goals().to_dict(orient='records')
                body = self.projects.format_goals(goals)
                self.third_party['push'].push.push_note(title, body)

            elif 'goal tracker' in latest_push['body']:

                goal_id = list(filter(lambda x: x.isdigit(), latest_push['body']))
                goal_id = int(''.join(goal_id))

                notes = latest_push['body'].split('notes ')[1]
                not_completed = 'not completed' in latest_push['body']
                completed = 'completed' in latest_push['body']

                goal = self.db.query(
                    'select * from goals_tracker where goal_id = %s and goal_timestamp = DATE(NOW())', [goal_id])

                if goal is not None:
                    if not_completed:
                        self.third_party['push'].push.push_note('Tasks', 'Replaced Task log. Try again tomorrow...')
                        goal['goal_completed'] = False

                    elif completed:
                        self.third_party['push'].push.push_note('Tasks', 'Replaced Task log. Great comeback!')
                        goal['goal_completed'] = True

                    goal['goal_notes'] = notes
                    goal['goal_timestamp'] = datetime.now()
                    goal['goal_id'] = goal_id
                    self.db.replace_insert_data('replace', 'goals_tracker', goal)

                else:

                    goal = pd.DataFrame(columns=['goal_id', 'goal_timestamp', 'goal_completed', 'goal_notes'])
                    new_row = {'goal_id': goal_id, 'goal_timestamp': datetime.now(), 'goal_notes': notes}

                    if not_completed:
                        self.third_party['push'].push.push_note('Goals', 'Added new goal log. Try again tomorrow...')
                        new_row.update({'goal_completed': False})

                    elif completed:
                        self.third_party['push'].push.push_note('Goals', 'Added new goal log. Great job!')
                        new_row.update({'goal_completed': True})
                    goal = goal.append(new_row, ignore_index=True)
                    self.db.replace_insert_data('insert', 'goals_tracker', goal)

    def run(self):
        """Start main loop"""
        print('Starting Main Loop for {} | {}'.format(self.__class__.__name__, self.name))
