from modules.sql_database import Database


class Projects:
    def __init__(self, user_credentials):
        self.Projects_Db = Database(user_credentials, 'projects')
        self.data = {}
        self.load_data()

    def load_data(self):
        select = {'table': 'projects'}
        self.data = self.Projects_Db.sql_select(select)

        if self.data == select:
            print('Projects Database: Empty Database')
            return
        else:
            print('Projects Database: Data has been loaded')
            return

    def add_project(self, data_dict):
        if self.check_name(data_dict['project_name']):
            columns = list(data_dict.keys())
            values = list(data_dict.values())
            insert = {
                'table': 'projects',
                'columns': columns,
                'values': values
            }

            new_key = self.Projects_Db.sql_insert(insert)
            self.load_data()
            print('New project has been added')
            return new_key
        else:
            print('Project name exists')
            return False

    def del_project(self, project_id):
        project = Project(project_id)
        if project.tasks is None:
            skeleton_data = {
                'table': 'projects',
                'condition': 'project_id',
                'value': project_id
            }

            self.Projects_Db.sql_delete(skeleton_data)
            self.load_data()
            print('Project deleted')
            return
        else:
            print('Cannot delete project with active tasks')
            return

    def project_list(self):
        project_list = []
        if self.data != {'table': 'projects'}:
            for project in self.data:
                project_list.append(self.data[project])
        return project_list

    def check_name(self,project_name):
        project_data = {
            'table': 'projects',
            'condition': 'project_name',
            'value': project_name
        }

        name_check = self.Projects_Db.sql_where(project_data,exists=True)

        if name_check == 1:
             return False
        elif name_check == 0:
            return True


class Tasks:
    def __init__(self, user_credentials):
        self.Projects_Db = Database(user_credentials, 'projects')
        self.data = {}
        self.load_data()

    def load_data(self):
        select = {'table': 'tasks'}
        self.data = self.Projects_Db.sql_select(select)

        if self.data == select:
            print('Projects Database: Empty Database')
            return
        else:
            print('Projects Database: Data has been loaded')
            return

    def get_tasks_year_month_day(self, year, month, day):
        task_data = {
            'table': 'tasks',
            'condition1': 'YEAR(task_due)',
            'value1': year,
            'condition2': 'MONTH(task_due)',
            'value2': month,
            'condition3':'DAY(task_due)',
            'value3': day
        }

        result = self.Projects_Db.sql_where(task_data)
        print(result)
        return result


class Project:
    def __init__(self, user_credentials, project_id):

        self.Projects_Db = Database(user_credentials, 'projects')
        self.data = {}
        self.tasks = {}
        self.load_project(project_id)

    def load_project(self, project_id):

        project_data = {
            'table': 'projects',
            'condition': 'project_id',
            'value': project_id
        }

        task_data = {
            'table': 'tasks',
            'condition': 'project_id',
            'value': project_id
        }
        data = self.Projects_Db.sql_where(project_data)
        if data is not None:
            self.data = data[project_id]
            self.tasks = self.Projects_Db.sql_where(task_data)
            print('Project loaded')
        else:
            print('No data')
        return

    def save_project(self):

        save = {
            'table': 'projects',
            'columns': list(self.data.keys()),
            'values': list(self.data.values()),
            'condition': 'project_id',
            'key': self.data['project_id']
        }
        self.Projects_Db.sql_update(save)
        self.load_project(self.data['project_id'])

        return 'Project saved'

    def update_project(self, attribute, new_val):
        self.data.update({attribute: new_val})

    def add_task(self, data_dict):
        name = data_dict['task_name']
        if self.check_name(name):
            columns = list(data_dict.keys())
            values = list(data_dict.values())
            insert = {
                'table': 'tasks',
                'columns': columns,
                'values': values
            }

            key = self.Projects_Db.sql_insert(insert)
            self.load_project(self.data['project_id'])
            print('Task added')
            return key
        else:
            print('Name exists')

    def del_task(self, task_id):
        skeleton_data = {
            'table': 'tasks',
            'condition': 'task_id',
            'value': task_id
        }
        self.Projects_Db.sql_delete(skeleton_data)
        self.load_project(self.data['project_id'])
        print('Task Deleted')
        return

    def check_name(self,task_name):

        task_data = {
            'table': 'tasks',
            'condition': 'task_name',
            'value': task_name
        }

        name_check = self.Projects_Db.sql_where(task_data)
        print(name_check)
        if name_check == 1:
             return False
        elif name_check == 0:
            return True
        elif name_check == {}:
            return True

    def task_list(self):
        task_list = []
        if self.tasks is not None:
            for task in self.tasks:
                task_list.append(self.tasks[task])
        return task_list


class Task:
    def __init__(self, user_credentials, task_id):

        self.Projects_Db = Database(user_credentials, 'projects')
        self.data = {}
        self.subtasks = {}
        self.load_task(task_id)

    def load_task(self, id):

        task_data = {
            'table': 'tasks',
            'condition': 'task_id',
            'value': id
        }

        subtask_data = {
            'table': 'subtasks',
            'condition': 'task_id',
            'value': id
        }
        data = self.Projects_Db.sql_where(task_data)
        if data is not None:

            self.data = data[id]
            self.subtasks = self.Projects_Db.sql_where(subtask_data)
            print('Task loaded')
        else:
            print('No data')

        return

    def save_task(self):
        data = self.data
        columns = list(data.keys())
        values = list(data.values())

        save = {
            'table': 'tasks',
            'columns': columns,
            'values': values,
            'condition': 'task_id',
            'key': self.data['task_id']
        }
        self.Projects_Db.sql_update(save)
        self.load_task(self.data['task_id'])

    def update_task(self, attribute, new_val):
        self.data.update({attribute: new_val})

    def add_subtask(self, data_dict):
        name = data_dict['subtask_name']
        if self.check_name(name):
            columns = list(data_dict.keys())
            values = list(data_dict.values())
            insert = {
                'table': 'subtasks',
                'columns': columns,
                'values': values
            }

            key = self.Projects_Db.sql_insert(insert)
            self.load_task(self.data['task_id'])
            print('Subtask added')
            return key

    def subtask_list(self):
        subtask_list = []
        if self.subtasks is not None:
            for subtask in self.subtasks:
                subtask_list.append(self.subtasks[subtask])
        return subtask_list

    def check_name(self,subtask_name):
        subtask_data = {
            'table': 'subtasks',
            'condition': 'subtask_name',
            'value': subtask_name
        }

        name_check = self.Projects_Db.sql_where(subtask_data)

        if name_check == 1:
            return False
        elif name_check == 0:
            return True


class Subtask:
    def __init__(self, user_credentials, subtask_id):

        self.Projects_Db = Database(user_credentials, 'projects')
        self.data = {}
        self.load_task(subtask_id)

    def load_subtask(self, subtask_id):

        subtask_data = {
            'table': 'subtasks',
            'condition': 'subtask_id',
            'value': subtask_id
        }
        data = self.Projects_Db.sql_where(subtask_data)
        if data is not None:

            self.data = data[subtask_id]
            print('Subtask loaded')
        else:
            print('No data')

        return

    def save_subtask(self):
        data = self.data
        columns = list(data.keys())
        values = list(data.values())

        save = {
            'table': 'subtasks',
            'columns': columns,
            'values': values,
            'condition': 'subtask_id',
            'key': self.data['subtask_id']
        }
        self.Projects_Db.sql_update(save)
        self.load_task(self.data['subtask_id'])

    def update_subtask(self, attribute, new_val):
        self.data.update({attribute: new_val})
