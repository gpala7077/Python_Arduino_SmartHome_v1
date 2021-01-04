import time
from datetime import datetime


class Projects:

    def __init__(self):
        self.db = None

    def get_time_block(self, time_block):
        return self.db.query('select * from time_blocks where time_block_id = {}'.format(time_block))

    def get_current_time_block(self):
        current_time_block = self.db.query('select * from time_blocks '
                                           'where '
                                           'TIME(NOW()) between TIME(time_block_start) and '
                                           'TIME(time_block_end)')
        return current_time_block

    def get_current_task(self, time_block):
        current_task = self.db.query('select * from tasks where {} between task_block_start and task_block_end '.format(
            time_block))

        return current_task

    def get_goals(self):
        goals = self.db.query('select * from goals')
        return goals

    def format_task(self, task, time_diff):
        title = 'Tasks'
        body = 'Task Name:\n{task_name}\n\n' \
               'Task ID:\n{task_id}\n\n' \
               'Time Allotted:\n{} hours, {} minutes, and {} seconds\n\n' \
               'Task Deadline:\n{task_start} to {task_end}\n\n' \
               'Task Description:\n{task_description}\n\n' \
               'Task Materials:\n{task_materials}\n\n' \
               'Success is:\n{task_success}'.format(
            time_diff.seconds // 3600,
            (time_diff.seconds // 60) % 60,
            time_diff.seconds % 60,
            **task)
        return title, body

    def format_goals(self, goals):
        body_msg = 'ID      |       Goal Name\n'
        for goal in goals:
            print(goal)
            body_msg += '{goal_id:3}      |       {goal_name}\n'.format(
                **goal)

        return body_msg