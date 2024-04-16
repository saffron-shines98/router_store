# import MySQLdb
from datetime import datetime
import mysql.connector as MySQLdb



class SqlConnection(object):
    active_connections = 0
    total_write_connections = 0

    def __init__(self, db_config):
        self.db_config = db_config
        try:
            self.connection = MySQLdb.connect(**self.db_config)
            self.cursor = self.connection.cursor(dictionary=True, buffered=True)
        except Exception as e:
            self.connection.close()

    @staticmethod
    def parsed_db_result(db_data) -> dict:
        parsed_db_data = dict()
        for key, val in db_data.items():
            if isinstance(val, datetime):
                parsed_db_data.update({key: val.strftime('%Y-%m-%d %H:%M:%S')})
            elif isinstance(val, str) and val == 'NULL':
                parsed_db_data.update({key: None})
            else:
                parsed_db_data.update({key: val})
        return parsed_db_data

    def reconnect_db(self):
        self.connection = MySQLdb.connect(**self.db_config)
        self.cursor = self.connection.cursor(dictionary=True, buffered=True)

    def query_db(self, query, params=None) -> list:
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
        except Exception as e:
            self.reconnect_db()
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
        self.connection.commit()
        result = self.cursor.fetchall()
        return list(map(lambda row: self.parsed_db_result(row), result)) if result else list()

    def query_db_one(self, query, params=None, parsed=True) -> dict:
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
        except Exception as e:
            self.reconnect_db()
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
        self.connection.commit()
        result = self.cursor.fetchone()
        if not result:
            return dict()
        return self.parsed_db_result(result) if parsed else result

    def write_db(self, query, params=None) -> int:
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            self.connection.commit()
        except Exception as e:
            self.reconnect_db()
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            self.connection.commit()
        return self.cursor.lastrowid

    def __del__(self):
        self.cursor.close()
        self.connection.close()
