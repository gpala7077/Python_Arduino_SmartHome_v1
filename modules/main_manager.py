import json

from modules.commands_manager import Commands
from modules.database_manager import Database
from modules.mosquitto_manager import MQTT_Client
import pandas as pd


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

    def run(self):
        """Start main loop"""
        print('Starting Main Loop for {} | {}'.format(self.__class__.__name__, self.name))
