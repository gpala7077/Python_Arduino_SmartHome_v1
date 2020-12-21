from modules.commands_manager import Commands
from modules.database_manager import Database
from modules.mosquitto_manager import Mosquitto


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
        self.mosquitto = Mosquitto()
        self.commands = Commands()
        self.interrupts = None
        self.status = None
        self.sensors = None
        self.tasks = dict()

    def initialize(self):
        """Start up program"""
        print('Initializing {} | {}'.format(self.__class__.__name__, self.name))
        self.mosquitto.host_ip = self.data['mqtt_data']['configuration']['mqtt_value']  # Get broker ip address
        self.commands.data = self.data  # commands data
        self.commands.mosquitto = self.mosquitto  # Give command access to MQTT
        self.mosquitto.commands = self.commands  # Give MQTT access to commands
        self.mosquitto.db = self.db
        print(self.mosquitto.connect())  # Log info
        print(self.mosquitto.listen(self.data['mqtt_data']['listen']))  # Log info

    def run(self):
        """Start main loop"""
        print('Starting Main Loop for {} | {}'.format(self.__class__.__name__, self.name))
