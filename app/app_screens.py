import colorsys
import calendar
from datetime import datetime

from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import StringProperty, NumericProperty, ListProperty, BooleanProperty, ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.screenmanager import Screen
from kivymd.theming import ThemableBehavior
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRectangleFlatButton, MDRaisedButton
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.list import MDList, OneLineIconListItem
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.picker import MDDatePicker
from kivymd.uix.screen import MDScreen
from kivymd.uix.tab import MDTabs, MDTabsBase
from kivymd.uix.toolbar import MDToolbar
from kivy.uix.popup import Popup
from modules.hue_manager import HueAPI
from modules.project_manager import Projects, Project, Task, Subtask, Tasks


class Login(MDScreen):
    Builder.load_string('''
<Login>
    md_bg_color: app.theme_cls.bg_darkest
    MDGridLayout:
        cols:2
        pos_hint:{'x':.15, 'y':-.5}
        row_force_default:True
        row_default_height:35
        
        MDLabel:
            text: "Username"
            theme_text_color: "Primary"
            size_hint_x: None
            width: 150

        MDTextField:
            id : username
            text: 'python'
            size_hint_x: None
            width: 150

        MDLabel:
            text: "Password"
            size_hint_x: None
            width: 150
            theme_text_color: "Primary"

        MDTextField:
            id: password
            text: 'password'
            password:True
            size_hint_x: None
            width: 150

        MDRoundFlatButton:
            text:'Exit'
            width:150
            on_release:root.exit_app()

        MDRoundFlatButton:
            text:'Login'
            width:150
            on_release:app.get_screen(root.check_credentials({root.ids.username.text:root.ids.password.text}))       
    
''')

    username = StringProperty()
    password = StringProperty()

    def __init__(self, **kwargs):

        # make sure we aren't overriding any important functionality
        super(Login, self).__init__(**kwargs)

        self.db_credentials = {}
        self.hue_credentials = {'192.168.50.34': 'pJPb8WW2wW1P82RKu1sHBLkEQofDMofh2yNDnXzj'}
        self.user_authenticated = False

    def check_credentials(self, user_credentials):
        print('User entered', user_credentials)
        user = {'self': 'password'}
        for key in user:
            if key in user_credentials.keys():
                if user_credentials[key] == user[key]:
                    self.log_in({key: user_credentials[key]})
                else:
                    print('Incorrect Password')
            else:
                print('Incorrect Username')
        return 'main_menu'

    def log_in(self, db_credentials):
        self.user_authenticated = True
        self.db_credentials = db_credentials
        print('Successful Login')

    def exit(self):
        exit()


class MenuScreen(MDScreen):
    Builder.load_string('''
<MenuScreen>
    md_bg_color: app.theme_cls.bg_darkest
    MDToolbar:
        title: 'Main Menu'
        pos_hint:{'x':0, 'y':.90}

    RelativeLayout:           
        MDRoundFlatButton:
            text: 'Project Manager'
            on_release:app.get_screen('projects')
            background_color: 0.1, 0.5, 0.6, 1
            pos_hint: {"x":0.1, "y":.6} 
            size_hint: 0.3, 0.2

        MDRoundFlatButton:
            text: 'Smart Control'
            on_release:app.get_screen('smart_menu')
            background_color: 0.1, 0.5, 0.6, 1
            pos_hint: {"x":0.5, "y":.6} 
            size_hint: 0.3, 0.2

        MDRoundFlatButton:
            text: 'Calendar'
            on_release:app.get_screen('calendar')
            background_color: 0.1, 0.5, 0.6, 1
            pos_hint: {"x":0.1, "y":.2} 
            size_hint: 0.3, 0.2

''')

    def __init__(self, **kwargs):
        # make sure we aren't overriding any important functionality
        super(MenuScreen, self).__init__(**kwargs)

    def load(self):
        print('Main Menu Loaded')


class SmarthomeMenuScreen(MDScreen):
    Builder.load_string('''
<SmarthomeMenuScreen>
    md_bg_color: app.theme_cls.bg_darkest
    MDToolbar:
        title: 'Smart Home Menu'
        left_action_items: [["dots-horizontal", lambda x: app.get_screen('main_menu')]]
        pos_hint:{'x':0, 'y':.90}
    
    RelativeLayout:           
        MDRoundFlatButton:
            id: rooms
            text: 'Rooms'
            on_release:app.get_screen('rooms')
            background_color: 0.1, 0.5, 0.6, 1
            pos_hint: {"x":0.1, "y":.6} 
            size_hint: 0.3, 0.2

        MDRoundFlatButton:
            text: 'Hue Manager'
            on_release:app.get_screen('smart_menu')
            background_color: 0.1, 0.5, 0.6, 1
            pos_hint: {"x":0.5, "y":.6} 
            size_hint: 0.3, 0.2
         
''')

    def __init__(self, **kwargs):
        # make sure we aren't overriding any important functionality
        super(SmarthomeMenuScreen, self).__init__(**kwargs)

    def load(self):
        print('Smart Menu Loaded')


class RoomsScreen(MDScreen):
    Builder.load_string('''
<RoomsScreen>
    md_bg_color: app.theme_cls.bg_darkest
    MDToolbar:
        title: 'Rooms'
        left_action_items: [["dots-horizontal", lambda x: app.get_screen('smart_menu')]]
        pos_hint:{'x':0, 'y':.90}

    RelativeLayout:
               
        MDRoundFlatButton:
            id: rooms
            text: 'Kitchen'
            on_release:app.get_screen('room',1)
            background_color: 0.1, 0.5, 0.6, 1
            pos_hint: {"x":0.15, "y":.65} 
            size_hint: 0.3, 0.2

        MDRoundFlatButton:
            id: rooms
            text: 'Living Room'
            on_release:app.get_screen('room',2)
            background_color: 0.1, 0.5, 0.6, 1
            pos_hint: {"x":0.6, "y":.65} 
            size_hint: 0.3, 0.2

        MDRoundFlatButton:
            id: rooms
            text: 'Hallway'
            on_release:app.get_screen('room',3)
            background_color: 0.1, 0.5, 0.6, 1
            pos_hint: {"x":0.37, "y":.40} 
            size_hint: 0.3, 0.2

        MDRoundFlatButton:
            id: rooms
            text: 'Guest Bedroom'
            on_release:app.get_screen('rooms',3)
            background_color: 0.1, 0.5, 0.6, 1
            pos_hint: {"x":0.6, "y":.15} 
            size_hint: 0.3, 0.2

        MDRoundFlatButton:
            id: rooms
            text: 'Master Bedroom'
            on_release:app.get_screen('room',3)
            background_color: 0.1, 0.5, 0.6, 1
            pos_hint: {"x":0.15, "y":.15} 
            size_hint: 0.3, 0.2
''')

    def __init__(self, **kwargs):
        # make sure we aren't overriding any important functionality
        super(RoomsScreen, self).__init__(**kwargs)

    def load(self):
        print('Rooms Menu Loaded')


# v ------------------------------------------ v #
class ProjectListItem(MDBoxLayout):
    Builder.load_string('''
<ProjectListItem>:

    BoxLayout:
        orientation:'horizontal'
        padding: '5dp'

        MDLabel:
            text: root.project_name

        MDRoundFlatButton:
            text: '>'
            size_hint_x: None
            width: self.height
            on_release: app.get_screen('project',root.project_id)
''')
    project_id = NumericProperty()
    project_name = StringProperty()


class ProjectListScreen(MDScreen):
    Builder.load_string('''
<ProjectListScreen>:
    md_bg_color: app.theme_cls.bg_darkest

    MDToolbar:
        title: 'Projects'
        left_action_items: [["dots-horizontal", lambda x: app.get_screen('main_menu')]]
        pos_hint:{'x':0, 'y':.90}
    
    RelativeLayout:
        RecycleView:
            pos_hint:{'x':0, 'y':-.1}
            data: root.data
            viewclass: 'ProjectListItem'
            RecycleBoxLayout:
                default_size: None, dp(56)
                default_size_hint: 1, None
                size_hint_y: None
                height: self.minimum_height
                orientation: 'vertical'
                spacing: dp(2)

    MDBottomAppBar:
        MDToolbar:
            icon: "git"
            type: "bottom"
            on_action_button: root.add_project()

''')

    data = ListProperty()
    project_id = NumericProperty()
    project_name = StringProperty()

    def __init__(self, **kwargs):
        super(ProjectListScreen, self).__init__(**kwargs)
        self.db_credentials = {}

    def load(self):
        print('Project List Loading')
        self.projects = Projects(self.db_credentials)
        self.data = self.projects.project_list()

    def add_project(self):
        default = {
            'project_name': 'New project name',
            'project_description': 'New project objective'
        }

        self.projects.add_project(default)
        self.data = self.projects.project_list()


class MutableTextInput(FloatLayout):
    Builder.load_string('''
<MutableLabelTextInput@MutableTextInput>:
    MDLabel:
        id: w_label
        pos: root.pos
        text: root.text

    TextInput:
        id: w_textinput
        pos: root.pos
        text: root.text
        multiline: root.multiline
        on_focus: root.check_focus_and_view(self)

<MutableRstDocumentTextInput@MutableTextInput>:
    RstDocument:
        id: w_label
        pos: root.pos
        text: root.text

    TextInput:
        id: w_textinput
        pos: root.pos
        text: root.text
        multiline: root.multiline
        on_focus: root.check_focus_and_view(self)
''')



    text = StringProperty()
    multiline = BooleanProperty(True)

    def __init__(self, **kwargs):
        super(MutableTextInput, self).__init__(**kwargs)
        Clock.schedule_once(self.prepare, 0)

    def prepare(self, *args):
        self.w_textinput = self.ids.w_textinput.__self__
        self.w_label = self.ids.w_label.__self__
        self.view()

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos) and touch.is_double_tap:
            self.edit()
        return super(MutableTextInput, self).on_touch_down(touch)

    def edit(self):
        self.clear_widgets()
        self.add_widget(self.w_textinput)
        self.w_textinput.focus = True

    def view(self):
        self.clear_widgets()
        if not self.text:
            self.w_label.text = ''
        self.add_widget(self.w_label)

    def check_focus_and_view(self, textinput):
        if not textinput.focus:
            self.text = textinput.text
            self.view()

# ^------------------------------------------ ^ #


# v ------------------------------------------ v #

class TaskListItem(MDBoxLayout):
    Builder.load_string('''
<TaskListItem>:
    padding: '5dp'

    MDLabel:
        text: root.task_name

    MDLabel:
        text: root.task_due

    MDLabel:
        text: root.task_complete

    MDRoundFlatButton:
        text: '>'
        size_hint_x: None
        width: self.height
        on_release: app.get_screen('task',root.task_id)
''')
    project_id = NumericProperty()
    task_id = NumericProperty()
    task_name = StringProperty()
    task_description = StringProperty()
    task_due = StringProperty()
    task_complete = StringProperty()


class ProjectScreen(MDScreen):
    Builder.load_string('''
<ProjectScreen>:
    md_bg_color: app.theme_cls.bg_darkest

    MDToolbar:
        title: root.project_name
        left_action_items: [["dots-horizontal", lambda x: app.get_screen('projects')]]
        pos_hint:{'x':0, 'y':.90}
      
    RelativeLayout:
    
        MDGridLayout:
            cols:1
            pos_hint:{'x':0, 'y':-.1}
            
            MDTextField:
                hint_text: "Description"
                color_mode: 'accent'
                multiline: True
                helper_text_mode: "on_focus"
                helper_text: "Describe the project objective"

            RecycleView:
                data: root.task_list
                viewclass: 'TaskListItem'
                RecycleBoxLayout:
                    default_size: None, dp(56)
                    default_size_hint: 1, None
                    size_hint_y: None
                    height: self.minimum_height
                    orientation: 'vertical'
                    spacing: dp(2)
    
    MDBottomAppBar:
        MDToolbar:
            icon: "git"
            type: "bottom"
            on_action_button: root.add_task()


''')
    project_id = NumericProperty()
    project_name = StringProperty()
    project_description = StringProperty()
    task_list = ListProperty()

    def __init__(self, **kwargs):

        # make sure we aren't overriding any important functionality
        super(ProjectScreen, self).__init__(**kwargs)
        self.db_credentials = {}
        self.record_id = 0

    def load(self):
        self.project = Project(self.db_credentials, self.record_id)
        self.data = self.project.data
        self.task_list = self.project.task_list()
        self.prepare_attributes()

    def prepare_attributes(self):
        if self.data != {}:
            self.project_id = self.data['project_id']
            self.project_name = self.data['project_name']
            self.project_description = self.data['project_description']

        if self.task_list != []:
            for task in self.task_list:
                task.update({'task_due': task['task_due'].strftime("%Y-%m-%d")})
                if task['task_complete']:
                    task.update({'task_complete': 'Complete'})
                else:
                    task.update({'task_complete': 'Not Complete'})

    def save_project(self):
        self.project.update_project('project_name', self.project_name)
        self.project.update_project('project_description', self.project_description)
        self.project.save_project()
        self.data = self.project.data
        self.task_list = self.project.task_list()
        self.prepare_attributes()

    def add_task(self):
        print('adding',self.project_id)
        default = {
            'project_id': self.project_id,
            'task_name': 'New task name',
            'task_description': 'New task objective',
            'task_due': datetime.now(),
            'task_complete': 0
        }

        self.project.add_task(default)
        self.data = self.project.data
        self.task_list = self.project.task_list()
        self.prepare_attributes()

# ^------------------------------------------ ^ #


# v ------------------------------------------ v #

class SubTaskListItem(MDBoxLayout):
    Builder.load_string('''
<SubTaskListItem>:
    padding: '5dp'

    MDLabel:
        text: root.subtask_name

    MDLabel:
        text: root.subtask_due

    MDLabel:
        text: root.subtask_complete

    Button:
        text: '>'
        size_hint_x: None
        width: self.height
        on_release: app.get_screen('task',root.task_id)
        on_release: app.get_screen('subtask',root.subtask_id)
''')



    task_id = NumericProperty()
    subtask_id = NumericProperty()
    subtask_name = StringProperty()
    subtask_description = StringProperty()
    subtask_due = StringProperty()
    subtask_complete = StringProperty()


class TaskScreen(MDScreen):
    Builder.load_string('''
<TaskScreen>:
    md_bg_color: app.theme_cls.bg_darkest

    BoxLayout:

        orientation: 'vertical'

        BoxLayout:

            orientation: 'horizontal'
            size_hint_y: None
            height: '48dp'
            padding: '5dp'

            canvas:
                Color:
                    rgb: .3, .3, .3
                Rectangle:
                    pos: self.pos
                    size: self.size

            Button:
                text: 'Home'
                size_hint_x: None
                width: self.height
                on_release:app.get_screen('main_menu')

            MutableLabelTextInput:
                text: root.task_name
                font_size: '16sp'
                on_text: root.task_name = self.text

            BoxLayout:
                orientation:'vertical'
                size_hint_x: None

                Button:
                    text: 'Save'
                    width: self.height
                    on_release:root.save_task()

                Button:
                    text: 'New Subtask'
                    width: self.height
                    on_release:root.add_subtask()

        BoxLayout:
            orientation: 'vertical'
            size_hint_y: None

            Label:
                text: 'Task Due'

            Button:
                text: root.task_due
                on_release:root.show_date_picker()

            Label:
                text: 'Task Description'

            MutableRstDocumentTextInput:
                text: root.task_description
                multiline: True
                on_text:root.task_description = self.text

            Label:
                text: 'Task Complete'

            Label:
                text: root.task_complete
            Label:
                text: 'Current Subtasks'

        RecycleView:
            data: root.subtask_list
            viewclass: 'SubTaskListItem'
            RecycleBoxLayout:
                default_size: None, dp(56)
                default_size_hint: 1, None
                size_hint_y: None
                height: self.minimum_height
                orientation: 'vertical'
                spacing: dp(2)
''')
    task_id = NumericProperty()
    task_name = StringProperty()
    task_description = StringProperty()
    task_due = StringProperty()
    task_complete = StringProperty()
    subtask_list = ListProperty()

    def __init__(self, **kwargs):

        # make sure we aren't overriding any important functionality
        super(TaskScreen, self).__init__(**kwargs)

        self.db_credentials = {}
        self.record_id = 0


    def load(self):
        self.task_manager = Task(self.db_credentials, self.record_id)
        self.data = self.task_manager.data
        self.subtask_list = self.task_manager.subtask_list()
        self.prepare_attributes()

    def prepare_attributes(self):
        if self.data != {}:
            self.data.update({'task_due': self.data['task_due'].strftime("%Y-%m-%d")})

            if self.data['task_complete']:
                self.data.update({'task_complete': 'Complete'})
            else:
                self.data.update({'task_complete': 'Not Complete'})

            self.task_id = self.data['task_id']
            self.task_name = self.data['task_name']
            self.task_description = self.data['task_description']
            self.task_due = self.data['task_due']
            self.task_complete = self.data['task_complete']

        if self.subtask_list != []:
            for task in self.subtask_list:
                task.update({'subtask_due': task['subtask_due'].strftime("%Y-%m-%d'")})
                if task['subtask_complete']:
                    task.update({'subtask_complete': 'Complete'})
                else:
                    task.update({'subtask_complete': 'Not Complete'})

    def save_task(self):
        print(self.task_due)
        self.task_manager.update_task('task_name', self.task_name)
        self.task_manager.update_task('task_description', self.task_description)
        self.task_manager.update_task('task_due', self.task_due)

        if self.task_complete == 'Complete':
            self.task_manager.update_task('task_complete', 1)
        elif self.task_complete == 'Not complete':
            self.task_manager.update_task('task_complete', 0)

        self.task_manager.save_task()
        self.data = self.task_manager.data
        self.subtask_list = self.task_manager.subtask_list()
        self.prepare_attributes()

    def add_subtask(self):
        default = {
            'task_id': self.task_id,
            'subtask_name': 'New subtask name',
            'subtask_description': 'New subtask objective',
            'subtask_due': datetime.now(),
            'subtask_complete': 0
        }

        self.task_manager.add_subtask(default)
        self.data = self.task_manager.data
        self.subtask_list = self.task_manager.subtask_list()
        self.prepare_attributes()

    def get_date(self, date):
        self.task_due = str(date)

    def show_date_picker(self):
        min_date = datetime.strptime("2020-02-15", '%Y-%m-%d').date()
        max_date = datetime.strptime("2020-12-20", '%Y-%m-%d').date()
        date_dialog = MDDatePicker(
            callback=self.get_date,
            min_date=min_date,
            max_date=max_date,
        )
        date_dialog.open()


# ^------------------------------------------ ^ #


# v ------------------------------------------ v #

class SubtaskScreen(MDScreen):
    Builder.load_string('''
<SubtaskScreen>:
    md_bg_color: app.theme_cls.bg_darkest

    BoxLayout:
        orientation: 'vertical'

        Label:
            text: 'Subtask Due'

        MutableRstDocumentTextInput:
            text: root.subtask_due
            multiline: True
            on_text:root.subtask_due = self.text            

        Label:
            text: 'Subtask Description'

        MutableRstDocumentTextInput:
            text: root.subtask_description
            multiline: True
            on_text:root.subtask_description = self.text

        Label:
            text: 'Subtask Complete'

        MutableRstDocumentTextInput:
            text: root.subtask_complete
            multiline: True
            on_text:root.subtask_complete = self.text
''')
    task_id = NumericProperty()
    subtask_id = NumericProperty()
    subtask_name = StringProperty()
    subtask_description = StringProperty()
    subtask_due = StringProperty()
    subtask_complete = StringProperty()

    def __init__(self, **kwargs):

        # make sure we aren't overriding any important functionality
        super(SubtaskScreen, self).__init__(**kwargs)

        # changing the values here changes the placement of widget on screen

        self.db_credentials = {}
        self.record_id = 0

    def load(self):
        self.subtask_manager = Subtask(self.db_credentials, self.record_id)
        self.data = self.subtask_manager.data
        self.prepare_attributes()

    def prepare_attributes(self):
        if self.data != {}:

            self.data.update({'subtask_due': self.data['subtask_due'].strftime("%Y-%m-%d'")})

            if self.data['subtask_complete']:
                self.data.update({'subtask_complete': 'Complete'})
            else:
                self.data.update({'subtask_complete': 'Not Complete'})

            self.subtask_id = self.data['subtask_id']
            self.subtask_name = self.data['subtask_name']
            self.subtask_description = self.data['subtask_description']
            self.subtask_due = self.data['subtask_description']
            self.subtask_complete = self.data['subtask_description']

    def save_subtask(self):
        self.subtask_manager.update_subtask('subtask_name', self.subtask_name)
        self.subtask_manager.update_subtask('subtask_description', self.subtask_description)
        self.subtask_manager.update_subtask('subtask_due', self.subtask_due.strptime("%Y-%m-%d'"))
        self.subtask_manager.update_subtask('subtask_complete', self.subtask_complete)
        self.subtask_manager.save_subtask()
        self.data = self.subtask_manager.data
        self.prepare_attributes()

# ^------------------------------------------ ^ #


# v ------------------------------------------ v #


# ^------------------------------------------ ^ #


# v ------------------------------------------ v #
class SubgroupList(BoxLayout):
    Builder.load_string('''
<SubgroupList>
    orientation: 'horizontal'
    
    MLabel:
        text: root.subgroup_name
    
    ToggleButton:
        text: 'State'
        
''')

    subgroup_id = NumericProperty()
    subgroup_name = StringProperty()


class LightTab(FloatLayout, MDTabsBase):
    Builder.load_string('''
<LightTab>
    ColorWheel:
        id: colorpicker
        pos_hint:{'x':-.2, 'y':.0}
        on_touch_up:root.on_color(colorpicker)
    
    MDSlider:
        id:dimmer
        orientation:'vertical'
        pos_hint:{'x':.40, 'y':0}
        min: 0
        max: 255
        value: 255
        hint: False
        on_active: root.dim(dimmer)
        
    BoxLayout:
        orientation:'horizontal'
        pos_hint:{'x':0, 'y':0}

        MDRoundFlatButton:
            text:'On'
            on_release: root.switch(True)

        MDRoundFlatButton:
            text:'Off'
            on_release: root.switch(False)
            
                
''')
    members = ListProperty()
    subgroups = ListProperty()

    def __init__(self, hue_credentials,room_id,**kwargs):
        # make sure we aren't overriding any important functionality
        super(LightTab, self).__init__(**kwargs)

        # changing the values here changes the placement of widget on screen
        self.hue_credentials = hue_credentials
        self.room_id = room_id
        self.hues = {}
        self.build()

    def build(self):
        self.group_id = self.room_id
        self.HueAPI = HueAPI(self.hue_credentials)

    def on_color(self, wheel):
        if wheel.color != [0,0,0,0]:
            self.values = colorsys.rgb_to_hsv(wheel.color[0], wheel.color[1], wheel.color[2])

            group_command ={
                'hue':int(self.values[0] * 65000),
                'sat':int(self.values[1] * 255),
                'bri':int(self.values[2] * 255)
            }
            self.HueAPI.set_group(self.group_id ,group_command)

    def dim(self, instance):
            print(instance.active)
            group_command ={
                'bri':int(instance.value)
            }
            self.HueAPI.set_group(self.group_id ,group_command)

    def switch(self,command):
        group_command = {
            'on': command
        }

        self.HueAPI.set_group(self.group_id, group_command)


class Room(MDScreen):
    Builder.load_string('''
<Room>
    md_bg_color: app.theme_cls.bg_darkest
    MDToolbar:
        title: 'Room name'
        left_action_items: [["dots-horizontal", lambda x: app.get_screen('rooms')]]
        pos_hint:{'x':0, 'y':.90}

''')

    def __init__(self, **kwargs):
        # make sure we aren't overriding any important functionality
        super(Room, self).__init__(**kwargs)

        # changing the values here changes the placement of widget on screen
        self.db_credentials = {}
        self.hue_credentials = {}
        self.record_id = ''


    def load(self):

        tab = LightTab(id='lights',text='lights',hue_credentials=self.hue_credentials,room_id= self.record_id)
        tabs = MDTabs(pos_hint={'x':0, 'y':0},on_tab_switch=self.on_tab_switch,size_hint=[1, .90])
        tabs.add_widget(tab)
        self.add_widget(tabs)

        print('Room Loaded')

    def on_tab_switch(
        self, instance_tabs, instance_tab, instance_tab_label, tab_text
    ):
        '''Called when switching tabs.

        :type instance_tabs: <kivymd.uix.tab.MDTabs object>;
        :param instance_tab: <__main__.Tab object>;
        :param instance_tab_label: <kivymd.uix.tab.MDTabsLabel object>;
        :param tab_text: text or name icon of tab;
        '''

        # instance_tab.ids.label.text = tab_text


class GroupListItem(MDBoxLayout):
    Builder.load_string('''
<GroupListItem>:
    padding: '5dp'

    MDLabel:
        text: root.group_name

    Button:
        text: '>'
        size_hint_x: None
        width: self.height
        on_release: app.get_screen('group',root.group_id)

''')



    group_id = NumericProperty()
    group_name=StringProperty()


class GroupListScreen(Screen):
    Builder.load_string('''
<GroupListScreen>:
    md_bg_color: app.theme_cls.bg_darkest

    RecycleView:
        data: root.data
        viewclass: 'GroupListItem'
        RecycleBoxLayout:
            default_size: None, dp(56)
            default_size_hint: 1, None
            size_hint_y: None
            height: self.minimum_height
            orientation: 'vertical'
            spacing: dp(2)
''')

    data = ListProperty()
    group_id = NumericProperty()
    group_name = StringProperty()

    def __init__(self,**kwargs):

        # make sure we aren't overriding any important functionality
        super(GroupListScreen, self).__init__(**kwargs)

        # changing the values here changes the placement of widget on screen
        self.db_credentials = {}
        self.hue_credentials = {}

    def load(self):
        self.hue_manager = HueManager(self.db_credentials, self.hue_credentials)
        self.data = self.hue_manager.data_list()['groups']

    def add_group(self):

        default = {
            'group_name': 'New group name',
            'group_description': 'New group description'
        }

        self.hue_manager.add_group(default)
        self.data = self.hue_manager.data_list()['groups']

# ^------------------------------------------ ^ #



# v ------------------------------------------ v #

class LightListItem(MDBoxLayout):
    Builder.load_string('''
<LightListItem>:
    padding: '5dp'

    Label:
        text: root.hue_name
    
    BoxLayout:
        orientation:'horizontal'
    
        ToggleButton:
            id: member
            text: str(root.hue_id)
            width: self.height
            on_release: root.parent.parent.parent.parent.parent.member(root.hue_id,self.state)
            
        Button:
            text: 'effect'
            width: self.height
            on_release: root.parent.parent.parent.parent.parent.effect(root.hue_id)
                

''')


    hue_id = NumericProperty()
    hue_name = StringProperty()


class SubgroupListItem(MDBoxLayout):
    Builder.load_string('''
<SubgroupListItem>:

    padding: '5dp'

    Label:
        text: root.subgroup_name

    Button:
        text: '>'
        size_hint_x: None
        width: self.height
        on_release: app.get_screen('subgroup',root.subgroup_id)

''')



    group_id = NumericProperty()
    group_name=StringProperty()


class GroupScreen(MDScreen):
    Builder.load_string('''
<GroupScreen>:
    md_bg_color: app.theme_cls.bg_darkest

    BoxLayout:
        orientation: 'vertical'
        size_hint_y: None
    
        Label:
            text: 'Available Lights'
    BoxLayout:
        orientation:'horizontal'
        
        RecycleView:
            data: root.lights
            viewclass: 'LightListItem'
            RecycleBoxLayout:
                default_size: None, dp(56)
                default_size_hint: 1, None
                size_hint_y: None
                height: self.minimum_height
                orientation: 'vertical'
                spacing: dp(2)
        
        RecycleView:
            data: root.subgroups
            viewclass: 'SubgroupListItem'
            RecycleBoxLayout:
                default_size: None, dp(56)
                default_size_hint: 1, None
                size_hint_y: None
                height: self.minimum_height
                orientation: 'vertical'
                spacing: dp(2)

''')
    group_id = NumericProperty()
    group_name = StringProperty()
    lights = ListProperty()
    subgroups = ListProperty()


    def __init__(self, **kwargs):

        # make sure we aren't overriding any important functionality
        super(GroupScreen, self).__init__(**kwargs)

        # changing the values here changes the placement of widget on screen
        self.db_credentials = {}
        self.hue_credentials = {}
        self.record_id = 0

    def load(self):
        self.hue_manager = HueManager(self.db_credentials,self.hue_credentials)
        self.group_manager = Group(self.db_credentials, self.hue_credentials,self.record_id)
        self.data = self.group_manager.query[self.record_id]
        self.subgroups = self.group_manager.data_list()['subgroups']
        self.members = self.group_manager.data_list()['members']
        self.lights = self.hue_manager.data_list()['lights']
        member_check = []
        for member in self.members:
            member_check.append(member['hue_id'])


        self.prepare_attributes()

    def prepare_attributes(self):
        if self.data != {}:
            self.group_id = self.data['group_id']
            self.group_name = self.data['group_name']

    def save_group(self):
        print('save group')

    def member(self,hue_id,state):
        if state == 'down':
            self.group_manager.add_member(hue_id)

        if state == 'up':
            self.group_manager.del_member(hue_id)



    def effect(self,hue_id):
        self.hue = Hue(self.db_credentials,self.hue_credentials,hue_id)
        self.hue.update_light('on', False)
        self.hue.set()
        self.hue.update_light('on',True)
        self.hue.set()


class SubgroupScreen(Screen):
    Builder.load_string('''
<SubgroupScreen>:
    md_bg_color: app.theme_cls.bg_darkest
    BoxLayout:
        orientation: 'vertical'
        size_hint_y: None

        Label:
            text: 'Project Description'

        MutableRstDocumentTextInput:
            text: root.group_description
            multiline: True
            on_text:root.group_description = self.text

        Label:
            text: 'Available Lights'

    RecycleView:
        data: root.data
        viewclass: 'LightListItem'
        RecycleBoxLayout:
            default_size: None, dp(56)
            default_size_hint: 1, None
            size_hint_y: None
            height: self.minimum_height
            orientation: 'vertical'
            spacing: dp(2)
''')
    group_id = NumericProperty()
    group_name = StringProperty()
    group_description = StringProperty()
    data = ListProperty()

    def __init__(self, **kwargs):

        # make sure we aren't overriding any important functionality
        super(SubgroupScreen, self).__init__(**kwargs)

        # changing the values here changes the placement of widget on screen
        self.db_credentials = {}
        self.hue_credentials = {}
        self.record_id = 0

    def load(self):
        self.subgroup_manager = SubgroupScreen(self.db_credentials, self.hue_credentials,self.record_id)
        self.group_manager = Group(self.db_credentials, self.hue_credentials,self.group_manager['group_id'])
        self.data = self.group_manager.data_list()
        self.prepare_attributes()

    def prepare_attributes(self):
        if self.data != {}:
            self.subgroup_id = self.data['subgroup_id']
            self.subgroup_name = self.data['subgroup_name']
            self.subgroup_description = self.data['subgroup_description']

    def save_group(self):
        print('save subgroup')

    def add_member(self,hue_id):
        self.subgroup_manager.add_member(hue_id)
        self.load()

# ^------------------------------------------ ^ #
class CalendarScreen(MDScreen):
    Builder.load_string('''
<CalendarScreen>
    md_bg_color: app.theme_cls.bg_darkest
    MDToolbar:
        title: 'Calendar'
        left_action_items: [["dots-horizontal", lambda x: app.get_screen('main_menu')]]
        pos_hint:{'x':0, 'y':.90}
'''
    )
    def __init__(self, **kwargs):
        super(CalendarScreen, self).__init__(**kwargs)
        self.year = datetime.now().year
        self.month = datetime.now().month
        self.build()

    def build(self,year=None,month = None):
        self.tasks = Tasks({'python': 'password'})


        if year == None and month == None:
            self.c = calendar.monthcalendar(self.year, self.month)

        else:
            self.c = calendar.monthcalendar(year,month)

        days = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
        months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
        self.calendar = MDGridLayout(cols=7)
        self.calendar.id = 'calendar'
        self.months = MDGridLayout(cols=12)
        self.months.size_hint = [1, .03]
        self.months.pos_hint  = {'x':0,'y':.90}
        self.calendar.size_hint= [1,.87]

        size = [0.03,0.03]
        align = 'center'
        color = 'Primary'

        for day in days:
            self.calendar.add_widget(MDLabel(text=day,size_hint = size,halign= align,theme_text_color = color))

        for month in months:
            self.months.add_widget(
                Button(
                    on_release=self.on_month,
                    text='{}'.format(month),
                    background_color = [115 / 255, 161 / 255, 221 / 255, .35]
                )
            )

        size2 = [1,1]
        for i in self.c:
            for j in i:
                if j == 0:
                    tasks_due = ''
                    box_layout = BoxLayout(orientation='vertical')
                    box_layout.add_widget(MDLabel(text='',size_hint=[.3,.3],theme_text_color = color))
                    box_layout.add_widget(
                        MDRectangleFlatButton(
                            on_release=self.on_release,
                            text='',
                            size_hint = size2
                        ))
                    self.calendar.add_widget(box_layout)

                else:
                    tasks_due = ''
                    s = self.tasks.get_tasks_year_month_day(self.year, self.month, j)

                    for key in s:
                        msg  = s[key]['task_name'] + '\n'
                        tasks_due += msg

                    box_layout = BoxLayout(orientation='vertical')
                    box_layout.add_widget(MDLabel(text=str(j),size_hint=[.3,.3],theme_text_color = color))
                    box_layout.add_widget(
                        MDRectangleFlatButton(
                            id=str(j),
                            on_release=self.on_release,
                            text=tasks_due,
                            size_hint = size2
                        ))
                    self.calendar.add_widget(box_layout)

        self.add_widget(self.months)
        self.add_widget(self.calendar)


    def load(self):
        self.remove_widget(self.children[0])
        self.build(self.year,self.month)

    def on_release(self, event):
        print(event.id)
        data = self.tasks.get_tasks_year_month_day(self.year, self.month, eval(event.id))
        return taskListPopUp(data)

    def on_month(self, event):
        months = {
            'Jan':1,
            'Feb':2,
            'Mar':3,
            'Apr':4,
            'May':5,
            'Jun':6,
            'Jul':7,
            'Aug':8,
            'Sep':9,
            'Oct':10,
            'Nov':11,
            'Dec':12
        }
        self.month = months[event.text]
        self.remove_widget(self.children[0])
        self.build(self.year,self.month)

        print("date clicked :" + event.text)


class taskListPopUp(Popup):
    def __init__(self, data, **kwargs):
      # make sure we aren't overriding any important functionality
        super(taskListPopUp, self).__init__(**kwargs)
        msg = ''
        for key in data:
            if data[key]['task_complete']:
                com = 'Complete'
            else:
                com = 'Not Complete'

            msg += '{task} is {com}'.format(task=data[key]['task_name'],com=com) + '\n\n'

        button = Button(text='Close',on_release=self.dismiss)
        box = BoxLayout(orientation='vertical')
        box.add_widget(Label(text=msg))
        box.add_widget(button)
        self.content = box
        self.open()

