from threading import Thread
import mysql.connector as mariadb
import os


def build_dictionary(key, data):
    dictionary_result = {}
    for i in range(0, len(key)):
        dictionary_result.update({key[i]: data[i]})
    return dictionary_result


class Database:
    def __init__(self, credentials):
        Thread.__init__(self)

        # Save credentials
        self.credentials = credentials

        # Log into local database
        self.db = mariadb.connect(
            user=self.credentials['username'],
            password=self.credentials['password'],
            database=self.credentials['database'],
            host=self.credentials['host']
        )

        # create pointer
        self.cursor = self.db.cursor()

    def query(self, query, values=None):
        self.db.commit()
        if 'select' in query:
            if values is not None:
                self.cursor.execute(query, values)
            else:
                self.cursor.execute(query)

            results = []
            columns = []

            for col in self.cursor.description:
                columns.append(col[0])

            for data in self.cursor:
                results.append(build_dictionary(columns, data))
            return results

        elif 'insert' in query:
            self.cursor.execute(query, values)
            self.db.commit()
            last_id = self.cursor.getlastrowid()
            print('last id =', last_id)
            return last_id
