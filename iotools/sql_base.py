# coding=utf-8


import sqlite3


class ColumnTypes:
    INTEGER = "INTEGER"
    TEXT = "TEXT"
    BLOB = "BLOB"
    REAL = "REAL"
    NUMERIC = "NUMERIC"


class SQLManager:
    instances = dict()

    @staticmethod
    def get_instance(database):
        if SQLManager.instances.get(database):
            return SQLManager.instances[database]
        else:
            SQLManager.instances[database] = SQLUtil(database)
            return SQLManager.instances[database]


class SQLUtil:
    def __init__(self, database):
        self.connection = sqlite3.connect(database, check_same_thread=False)  # dirty hack
        self.cursor = self.connection.cursor()

    def create_table(self, table, columns=list(), types=list()):
        if len(columns) != len(types):
            print("Columns and types have different size!")
            return

        with self.connection:
            query = "CREATE TABLE IF NOT EXISTS {0} ({1})".format(table, ",".join(["{0} '{1}'".format(pair[0], pair[1]) for pair in zip(columns, types)]))
            self.log_operation(query)
            self.cursor.execute(query)

    def delete_table(self, table):
        with self.connection:
            query = "DROP TABLE {0}".format(table)
            self.log_operation(query)
            self.cursor.execute(query)

    def select_all(self, table):
        with self.connection:
            query = 'SELECT * FROM {0}'.format(table)
            self.log_operation(query)
            return self.cursor.execute(query).fetchall()

    def select_single(self, field, query, table):
        with self.connection:
            query = 'SELECT * FROM {0} WHERE {1} = {2}'.format(table, field, query)
            self.log_operation(query)
            return self.cursor.execute(query).fetchall()[0]

    def add_record(self, table, columns=list(), values=list()):
        if len(columns) != len(values):
            print("Columns and values have different size!")
            return

        with self.connection:
            query = "INSERT INTO {0} ({1}) VALUES ({2})".format(table, ",".join(columns), ",".join("'{0}'".format(val) for val in values))
            self.log_operation(query)
            self.cursor.execute(query)
            self.connection.commit()

    def edit_record(self, query, table, columns=list(), values=list()):
        if len(columns) != len(values):
            print("Columns and values have different size!")
            return

        with self.connection:
            sql_query = "UPDATE {0} SET {1} WHERE {2}".format(table,
                                                              ",".join(["{0} = {1}".format(pair[0], pair[1]) for pair in zip(columns, values)]),
                                                              query)
            self.log_operation(sql_query)
            self.cursor.execute(query)
            self.connection.commit()

    def delete_record(self, table, query):
        with self.connection:
            sql_query = "DELETE FROM {0} WHERE {1}".format(table, query)
            self.log_operation(sql_query)
            self.cursor.execute(sql_query)
            self.connection.commit()

    @staticmethod
    def log_operation(query):
        print("Executing query ->\n{0}".format(query))

    def close_db(self):
        self.cursor.close()
        self.connection.close()
