from kivy.metrics import cm
from kivy.uix.screenmanager import Screen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRectangleFlatButton
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.selectioncontrol import MDSwitch
from kivymd.uix.slider import MDSlider

from modules.commands_manager import Commands
from modules.mosquitto_manager import Mosquitto


class Login(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)

    def cancel(self):
        exit()


class Main_Menu(Screen):
    def __init__(self, home, **kw):
        super().__init__(**kw)
        self.home = home


class Home_Control(Screen):
    def __init__(self, home, **kw):
        super().__init__(**kw)
        self.home = home
        self.status = self.home.current_status()
        self.build()

    def build(self):

        float_layout = MDFloatLayout()

        float_layout.add_widget(self.available_rooms(.7, 0))
        float_layout.add_widget(self.current_light_status(.1, .7))
        float_layout.add_widget(self.current_hue(0, .5))

        float_layout.add_widget(self.current_door_status(.7, .7))
        float_layout.add_widget(self.current_humidity_status(.1, .3))
        float_layout.add_widget(self.current_temperature_status(.7, .3))

        self.add_widget(float_layout)

    def available_rooms(self, x, y):
        rooms = list(self.home.rooms.keys())
        grid_layout = MDGridLayout(
            cols=1, adaptive_height=True, pos_hint={'x': x, 'y': y}
        )

        for room in rooms:
            button = MDRectangleFlatButton(text=room)
            button.bind(on_press=self.available_rooms_callback)
            grid_layout.add_widget(button)

        return grid_layout

    def current_light_status(self, x, y):
        grid_layout = MDGridLayout(
            cols=1, adaptive_height=True, adaptive_width=True, pos_hint={'x': x, 'y': y}
        )
        light_layout = MDBoxLayout(
            orientation='vertical', adaptive_height=True, adaptive_width=True
        )
        for sensor in self.status.query('sensor_type == "light"').to_dict(orient='records'):
            grid_layout.add_widget(MDLabel(text='All Lights'))
            box_layout = MDBoxLayout(orientation='horizontal')
            button1 = MDSwitch(active=[1, 0][int(sensor['sensor_value'])])
            button1.id = sensor['sensor_name']
            button1.bind(active=self.commands_callback)
            label1 = MDLabel(text=sensor['sensor_name'])
            box_layout.add_widget(label1)
            box_layout.add_widget(button1)
            light_layout.add_widget(box_layout)

        grid_layout.add_widget(light_layout)
        return grid_layout

    def current_door_status(self, x, y):
        grid_layout = MDGridLayout(
            cols=1, adaptive_height=True, adaptive_width=True, pos_hint={'x': x, 'y': y}
        )
        door_layout = MDBoxLayout(
            orientation='vertical', adaptive_height=True, adaptive_width=True
        )
        for sensor in self.status.query('sensor_type == "door"').to_dict(orient='records'):
            grid_layout.add_widget(MDLabel(text='All Doors'))
            box_layout = MDBoxLayout(orientation='horizontal')
            button1 = MDLabel(text=['Closed', 'Open'][int(sensor['sensor_value'])])
            button1.id = sensor['sensor_name']
            label1 = MDLabel(text=sensor['sensor_name'])
            box_layout.add_widget(label1)
            box_layout.add_widget(button1)
            door_layout.add_widget(box_layout)

        grid_layout.add_widget(door_layout)
        return grid_layout

    def current_temperature_status(self, x, y):
        grid_layout = MDGridLayout(
            cols=1, adaptive_height=True, pos_hint={'x': x, 'y': y}
        )
        grid_layout.add_widget(MDLabel(text='Current Temperature'))

        for sensor in self.status.query('sensor_type == "temperature"').to_dict(orient='records'):
            label1 = MDLabel(text='{sensor_name} {sensor_value}'.format(**sensor))

            grid_layout.add_widget(label1)

        return grid_layout

    def current_humidity_status(self, x, y):
        grid_layout = MDGridLayout(
            cols=1, adaptive_height=True, pos_hint={'x': x, 'y': y}
        )
        grid_layout.add_widget(MDLabel(text='Current Humidity'))

        for sensor in self.status.query('sensor_type == "humidity"').to_dict(orient='records'):
            label1 = MDLabel(text='{sensor_name} {sensor_value}'.format(**sensor))

            grid_layout.add_widget(label1)

        return grid_layout

    def current_hue(self, x, y):
        grid_layout = MDGridLayout(
            cols=1, adaptive_height=True, pos_hint={'x': x, 'y': y}
        )
        grid_layout.add_widget(MDLabel(text='Home Hue Brightness'))
        label1 = MDSlider(min=0, max=255)
        label1.bind(on_touch_up=self.commands_callback)
        grid_layout.add_widget(label1)

        return grid_layout

    def available_rooms_callback(self, instance):
        print(instance.text)

    def commands_callback(self, instance, value):
        if isinstance(instance, MDSlider) and instance.active:
            self.home.commands.execute('hue_lights_on',
                                       '{}"bri": {}, "on": true{}'.format("{", int(instance.value), "}"))
        elif isinstance(instance, MDSwitch):
            print(instance.active)


class Home_Management(Screen):
    def __init__(self, db, **kw):
        super().__init__(**kw)
        self.db = db
