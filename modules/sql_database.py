import mysql.connector as mariadb

# Necessary Data structures for SQL statements
skeleton_structures = dict(
    data1={
        'table': 'projects',
    },
    data2={
        'table': 'projects',
        'condition': 'project_id',
        'value': 32
    },
    data3={
        'table': 'projects',
        'columns': ['project_name', 'project_description'],
        'values': ['Test Name', 'Test Value']
    },

    data4={
        'table': 'projects',
        'columns': ['project_name', 'project_description'],
        'values': ['Harry Potter', 'You are a wizard'],
        'condition': 'project_id',
        'key': 29
    }
)


def condition_builder(dict_data):
    condition_id = []
    value_id = []

    for condition in dict_data:
        if 'condition' in condition:
            condition_id.append(dict_data[condition] + ' = %s')

        if 'value' in condition:
            value_id.append(dict_data[condition])

    sep = ' AND '
    return_data = [sep.join(condition_id), value_id]

    return return_data


def build_dictionary(key, data):
    dictionary_result = {}
    for i in range(0, len(key)):
        dictionary_result.update({key[i]: data[i]})
    return dictionary_result


class Database:

    def __init__(self, user_credentials, database):
        user = list(user_credentials.keys())[0]
        password = list(user_credentials.values())[0]
        # Log into database
        self.db = mariadb.connect(
            user=user,
            password=password,
            database=database)

        # create pointer
        self.cursor = self.db.cursor()

    def sql_select(self, dict_data):
        select_results = {}
        columns = []
        sql = 'SELECT * FROM ' + dict_data['table']
        self.cursor.execute(sql)

        for col in self.cursor.description:
            columns.append(col[0])

        for data in self.cursor:
            select_data = build_dictionary(columns, data)
            select_results.update({data[0]: select_data})

        return select_results


    def sql_where(self, dict_data,exists=None):
        select_results = {}
        columns = []
        return_data = condition_builder(dict_data)
        if exists:
            sql = 'SELECT exists(SELECT * FROM ' + dict_data['table'] + ' WHERE ' + return_data[0] + ')'
        else:
            sql = 'SELECT * FROM ' + dict_data['table'] + ' WHERE ' + return_data[0]

        if isinstance(return_data[1], list) and len(return_data[1]) > 1:
            self.cursor.execute(sql, return_data[1])

        else:
            if isinstance(return_data[1], list):
                return_data = return_data[1][0]
            self.cursor.execute(sql, (return_data,))

        for col in self.cursor.description:
            columns.append(col[0])

        for data in self.cursor:
            select_data = build_dictionary(columns, data)
            select_results.update({data[0]: select_data})

        if exists:
            return list(select_results.keys())[0]

        return select_results

    def sql_insert(self, dict_data):
        skeleton_data = skeleton_structures['data3']
        dict_data = dict(dict_data)
        sep = ', '
        sql_columns = sep.join(dict_data['columns'])
        sql_values = ['%s'] * len(dict_data['columns'])
        sql_values = sep.join(sql_values)
        sql = "INSERT INTO " + dict_data['table'] + " (" + sql_columns + ") VALUES (" + sql_values + ")"

        self.cursor.execute(sql, dict_data['values'])
        self.db.commit()

        return self.cursor.lastrowid

    def sql_update(self, dict_data):
        set_char = ' = %s, '
        sql_columns = set_char.join(dict_data['columns']) + ' = %s'

        sql = "UPDATE " + dict_data['table'] + " SET " + sql_columns + " WHERE " + dict_data['condition'] + " = %s"
        dict_data['values'].append(dict_data['key'])
        self.cursor.execute(sql, dict_data['values'])
        self.db.commit()
        return_update = {
            'table': dict_data['table'],
            'condition': dict_data['condition'],
            'value': dict_data['key']
        }
        return self.sql_where(return_update)

    def sql_delete(self, dict_data):
        return_data = condition_builder(dict_data)

        sql = 'DELETE FROM ' + dict_data['table'] + ' WHERE ' + return_data[0]

        if isinstance(return_data[1], list) and len(return_data[1]) > 1:
            self.cursor.execute(sql, return_data[1])
        else:
            if isinstance(return_data[1], list):
                return_data = return_data[1][0]
                self.cursor.execute(sql, (return_data,))

        self.db.commit()
        return 'Row deleted'
