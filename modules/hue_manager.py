import json

import requests


# from modules.sql_database import Database


class HueAPI:
    def __init__(self, hue_credentials):
        self.hue_credentials = hue_credentials
        self.ip_address = ''
        self.user = ''
        self.data = ''
        self.load()

    def load(self):
        self.ip_address = list(self.hue_credentials.keys())[0]
        self.user = list(self.hue_credentials.values())[0]
        url = 'http://{}/api/{}'.format(self.ip_address, self.user)
        get_data = requests.get(url=url)
        self.data = get_data.json()
        return

    def set_light(self, hue_id, light_command):
        # light_command = json.dumps(light_command)
        url = 'http://{}/api/{}/lights/{}/state'.format(self.ip_address, self.user, hue_id)
        response = requests.put(url=url, data=light_command).json()
        return response

    def set_group(self, group_id, group_command):
        # group_command = json.dumps(group_command)
        url = 'http://{}/api/{}/groups/{}/action'.format(self.ip_address, self.user, group_id)
        response = requests.put(url=url, data=group_command).json()
        return response

    def get_group(self, group_id):
        url = 'http://{}/api/{}/groups/{}'.format(self.ip_address, self.user, group_id)
        response = requests.get(url=url).json()
        return response

    def add_group(self, group_name, hue_lights):
        group_command = {
            'name': group_name,
            'lights': hue_lights
        }

        group_command = json.dumps(group_command)
        url = 'http://{}/api/{}/groups/'.format(self.ip_address, self.user)
        response = requests.post(url=url, data=group_command).json()
        return response

# class HueManager:
#     def __init__(self, db_credentials, hue_credentials):
#         self.Projects_Db = Database(db_credentials, 'smart_home')
#         self.hue_credentials = hue_credentials
#         self.db_credentials = db_credentials
#         self.lights_get = {}
#         self.select_lights = {}
#         self.select_groups = {}
#         self.select_members = {}
#         self.select_users = {}
#         self.load_data()
#         self.update_lights_to_sql()
#
#     def load_data(self):
#         self.Projects_Db = Database(self.db_credentials,'smart_home')
#         select_lights = { 'table': 'hue_lights' }
#         select_groups = {'table':'hue_groups'}
#         select_members = {'table':'hue_members'}
#         select_users = {'table':'hue_users'}
#
#         self.select_lights = self.Projects_Db.sql_select(select_lights)
#         self.select_groups = self.Projects_Db.sql_select(select_groups)
#         self.select_members = self.Projects_Db.sql_select(select_members)
#         self.select_users = self.Projects_Db.sql_select(select_users)
#
#     def get_lights(self):
#         user_credentials = self.hue_credentials
#         ipaddress = list(user_credentials.keys())[0]
#         user = list(user_credentials.values())[0]
#         url = 'http://{}/api/{}/lights'.format(ipaddress,user)
#         get_lights = requests.get(url=url)
#         self.lights_get = get_lights.json()
#
#     def add_light(self, data_dict):
#         columns = list(data_dict.keys())
#         values = list(data_dict.values())
#         insert = {
#             'table': 'hue_lights',
#             'columns': columns,
#             'values': values
#         }
#
#         new_key = self.Projects_Db.sql_insert(insert)
#         self.load_data()
#         return new_key
#
#     def update_lights_to_sql(self):
#         self.get_lights()
#         lights = list(self.select_lights.keys())
#         for hue_id in self.lights_get:
#             if int(hue_id) not in lights:
#                 # data_dict should be structured as
#                 data_dict = {
#                     'hue_id': hue_id,
#                     'hue_name':self.lights_get[hue_id]['name']
#                 }
#                 print('New light bulb found! - Adding a/an {} with ID # {}'.format(data_dict['hue_name'],data_dict['hue_id']))
#                 self.add_light(data_dict)
#             self.load_data()
#
#     def add_group(self, data_dict):
#         columns = list(data_dict.keys())
#         values = list(data_dict.values())
#         insert = {
#             'table': 'hue_groups',
#             'columns': columns,
#             'values': values
#         }
#
#         new_key = self.Projects_Db.sql_insert(insert)
#         self.load_data()
#         return new_key
#
#     def del_group(self, group_id):
#         group = Group(group_id)
#         if group.members != {}:
#             skeleton_data = {
#                 'table': 'hue_groups',
#                 'condition': 'group_id',
#                 'value': group_id
#             }
#             self.Projects_Db.sql_delete(skeleton_data)
#             self.load_data()
#             print('Group deleted')
#         else:
#             print('Cannot delete group with active members')
#         return
#
#     def del_light(self, light_id):
#         light = Hue(light_id)
#         if light.groups is None:
#             skeleton_data = {
#                 'table': 'hue_lights',
#                 'condition': 'hue_id',
#                 'value': light_id
#             }
#             self.Projects_Db.sql_delete(skeleton_data)
#             self.load_data()
#             print('Project deleted')
#             return
#         else:
#             print('Cannot delete light bulb in active groups')
#             return
#
#     def data_list(self):
#         lights_list = []
#         groups_list = []
#         members_list = []
#         users_list = []
#
#         data_dict = {
#             'lights':lights_list,
#             'groups':groups_list,
#             'members':members_list,
#             'users':users_list
#         }
#
#         if self.select_lights != {'table':'smart_home'}:
#             for light in self.select_lights:
#                 lights_list.append(self.select_lights[light])
#
#         if self.select_groups != {'table': 'smart_home'}:
#             for group in self.select_groups:
#                 groups_list.append(self.select_groups[group])
#
#         if self.select_members != {'table': 'smart_home'}:
#             for member in self.select_members:
#                 members_list.append(self.select_members[member])
#
#         if self.select_users != {'table': 'smart_home'}:
#             for user in self.select_users:
#                 users_list.append(self.select_users[user])
#
#         return data_dict
#
#     def hue(self,hue_id):
#         return Hue(self.username, self.password, self.hue_credentials, hue_id)
#
#     def group(self,group_id):
#         return Group(self.username,self.password,group_id)
#
#
# class Hue:
#     def __init__(self, db_credentials,hue_credentials,hue_id):
#         self.Projects_Db = Database(db_credentials,'smart_home')
#         self.hue_id = hue_id
#         self.ipaddress = list(hue_credentials.keys())[0]
#         self.user = list(hue_credentials.values())[0]
#         self.data = {}
#         self.get_status()
#
#     def update_light(self, attribute, new_val):
#         self.data.update({attribute: new_val})
#
#     def set(self):
#         mykeys = ['on','hue','sat','bri','effect']
#         light_command = {}
#         for key in mykeys:
#             light_command.update({key:self.data[key]})
#         light_command = json.dumps(light_command)
#         url = 'http://{}/api/{}/lights/{}/state'.format(self.ipaddress, self.user, self.hue_id)
#         response = requests.put(url=url, data=light_command).json()
#
#         return response
#
#     def get_status(self):
#         url = 'http://{}/api/{}/lights/{}'.format(self.ipaddress,self.user,self.hue_id)
#         get_lights = requests.get(url=url)
#         get_lights = get_lights.json()
#
#         for state in get_lights['state']:
#             if state not in ['xy','mode','reachable']:
#                 self.data.update({state:get_lights['state'][state]})
#         print(self.data)
#
#     def save_history(self):
#         # data_dict should be structured as
#         data_dict = {
#             'hue_id': self.hue_id,
#             'on_bin': self.data['on'],
#             'bri':self.data['bri'],
#             'hue':self.data['hue'],
#             'sat':self.data['sat'],
#             'effect':self.data['effect'],
#             'ct':self.data['ct'],
#             'alert':self.data['alert'],
#             'colormode':self.data['colormode']
#         }
#
#         columns = list(data_dict.keys())
#         values = list(data_dict.values())
#         insert = {
#             'table': 'hue_history',
#             'columns': columns,
#             'values': values
#         }
#         print(insert)
#         new_key = self.Projects_Db.sql_insert(insert)
#         return new_key
#
#
# class Group:
#     def __init__(self, db_credentials,hue_credentials,group_id):
#         self.SmartHome_Db = Database(db_credentials, 'smart_home')
#         self.ipaddress = list(hue_credentials.keys())[0]
#         self.user = list(hue_credentials.values())[0]
#         self.group_id = group_id
#         self.data = {}
#         self.members = {}
#         self.subgroups = {}
#         self.load_data()
#
#     def load_data(self):
#         select_data = {
#             'table':'hue_groups',
#             'condition':'group_id',
#             'value':self.group_id
#         }
#         select_subgroups = {
#             'table':'hue_subgroups',
#             'condition':'group_id',
#             'value':self.group_id
#         }
#         select_members = {
#             'table':'hue_members',
#             'condition':'group_id',
#             'value':self.group_id
#         }
#
#         self.data = self.SmartHome_Db.sql_where(select_data)
#         self.members = self.SmartHome_Db.sql_where(select_members)
#         self.subgroups = self.SmartHome_Db.sql_where(select_subgroups)
#
#     def update_group(self, attribute, new_val):
#         self.data.update({attribute: new_val})
#
#     def add_member(self, hue_id):
#         # data_dict should be structured as
#         data_dict = {
#             'group_id': self.group_id,
#             'hue_id': hue_id
#         }
#
#         columns = list(data_dict.keys())
#         values = list(data_dict.values())
#         insert = {
#             'table': 'hue_members',
#             'columns': columns,
#             'values': values
#         }
#
#         new_key = self.SmartHome_Db.sql_insert(insert)
#         self.load_data()
#         return new_key
#
#     def del_member(self, hue_id):
#         # data_dict should be structured as
#         data_dict = {
#             'table': 'hue_members',
#             'condition1': 'group_id',
#             'value1': self.group_id,
#             'condition2':'hue_id',
#             'value2': hue_id
#         }
#         self.SmartHome_Db.sql_delete(data_dict)
#         self.load_data()
#         return
#
#     def data_list(self):
#         subgroups_list = []
#         members_list = []
#
#         data_dict = {
#             'subgroups':subgroups_list,
#             'members':members_list,
#         }
#
#         if self.subgroups is not None:
#             for subgroup in self.subgroups:
#                 subgroups_list.append(self.subgroups[subgroup])
#
#         if self.members != {'table': 'smart_home'} and self.members != {'table': 'projects'}:
#             for member in self.members:
#                 members_list.append(self.members[member])
#
#         return data_dict
#
#
# class Subgroup:
#     def __init__(self, db_credentials,hue_credentials,subgroup_id):
#         self.Projects_Db = Database(db_credentials,'smart_home')
#         self.ipaddress = list(hue_credentials.keys())[0]
#         self.user = list(hue_credentials.values())[0]
#         self.subgroup_id = subgroup_id
#         self.data = {}
#         self.members = {}
#
#     def load_data(self):
#         select_data = {
#             'table':'hue_subgroups',
#             'condition':'subgroup_id',
#             'value':self.subgroup_id
#         }
#
#
#         select_members = {
#             'table':'hue_submembers',
#             'condition':'subgroup_id',
#             'value':self.subgroup_id
#         }
#
#         self.data = self.Projects_Db.sql_where(select_data)
#         self.members = self.Projects_Db.sql_select(select_members)
#
#     def update_subgroup(self, attribute, new_val):
#         self.data.update({attribute: new_val})
#
#     def add_submember(self, hue_id):
#         # data_dict should be structured as
#         data_dict = {
#             'group_id':self.data['group_id'],
#             'subgroup_id': self.subgroup_id,
#             'hue_id': hue_id
#         }
#
#         columns = list(data_dict.keys())
#         values = list(data_dict.values())
#         insert = {
#             'table': 'hue_members',
#             'columns': columns,
#             'values': values
#         }
#
#         new_key = self.Projects_Db.sql_insert(insert)
#         self.load_data()
#         return new_key
#
#     def del_member(self, hue_id):
#         # data_dict should be structured as
#         data_dict = {
#             'table': 'hue_submembers',
#             'condition1': 'group_id',
#             'value1': self.data['group_id'],
#             'condition2':'subgroup_id',
#             'value2': self.subgroup_id,
#             'condition3': 'hue_id',
#             'value3': hue_id
#         }
#         self.Projects_Db.sql_delete(data_dict)
#         self.load_data()
#         return
#
