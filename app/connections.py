# import MySQLdb
import redis
import pika
from elasticsearch import Elasticsearch, RequestsHttpConnection
import pymysql
from datetime import datetime

class SqlConnection(object):
    def __init__(self, db_config):
        self.db_config = db_config

    @staticmethod
    def parsed_db_result(db_data) -> dict:
        if not db_data:
            return {}
        parsed_db_data = {}
        for key, val in enumerate(db_data):
            if isinstance(val, datetime):
                parsed_db_data[key] = val.strftime('%Y-%m-%d %H:%M:%S')
            elif isinstance(val, str) and val == 'NULL':
                parsed_db_data[key] = None
            else:
                parsed_db_data[key] = val
        return parsed_db_data

    def get_connection(self):
        return pymysql.connect(**self.db_config)

    def query_db(self, query, params=None) -> list:
        connection = self.get_connection()
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            try:
                cursor.execute(query, params)
            except pymysql.Error as e:
                raise e
            result = cursor.fetchall()
            return [self.parsed_db_result(row) for row in result] if result else []

    def query_db_one(self, query, params=None, parsed=True) -> dict:
        connection = self.get_connection()
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            try:
                cursor.execute(query, params)
            except pymysql.Error as e:
                raise e
            result = cursor.fetchone()
            return result

    def write_db(self, query, params=None) -> int:
        connection = self.get_connection()
        with connection.cursor() as cursor:
            try:
                cursor.execute(query, params)
                connection.commit()
                return cursor.lastrowid
            except pymysql.Error as e:
                connection.rollback()
                raise e
            finally:
                connection.close()

    def reconnect_db(self):
        self.connection = pymysql.connect(**self.db_config)
        self.cursor = self.connection.cursor(dictionary=True, buffered=True)


class RedisConnection(object):
    @staticmethod
    def get_redis_connections(redis_config):
        redis_host = redis_config.get('host')
        redis_port = redis_config.get('port')
        password = redis_config.get('password')
        if redis_host and redis_port:
            redis_connection = redis.Redis(
                host=redis_host, port=redis_port, password=password)
            return redis_connection

class RabbitMQConnection(object):
    def __init__(self, url):
        self.url = url
        self.rabbit_conn = self.get_rabbitmq_connection()

    def get_rabbitmq_connection(self):
        connection = pika.BlockingConnection(pika.URLParameters(self.url))
        channel = connection.channel()
        return channel

    def push_message_to_queue(self, exchange='', routing_key='', body=''):
        try:
            try:
                self.rabbit_conn.basic_publish(exchange=exchange, routing_key=routing_key, body=body)
            except Exception as e:
                self.rabbit_conn = self.get_rabbitmq_connection()
                self.rabbit_conn.basic_publish(exchange=exchange, routing_key=routing_key, body=body)
        except Exception as e:
            return str(e)

class SqlConnectionNodeSso(object):

    def __init__(self, db_config):
        self.db_config_node_sso = db_config

    def get_connection_node_sso(self):
        return pymysql.connect(**self.db_config_node_sso)

    @staticmethod
    def parsed_db_result_node_sso(db_data) -> dict:
        parsed_db_data = dict()
        for key, val in db_data.items():
            if isinstance(val, datetime):
                parsed_db_data.update({key: val.strftime('%Y-%m-%d %H:%M:%S')})
            elif isinstance(val, str) and val == 'NULL':
                parsed_db_data.update({key: None})
            else:
                parsed_db_data.update({key: val})
        return parsed_db_data

    def query_db_node_sso(self, query, params=None) -> list:
        connection = self.get_connection_node_sso()
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            try:
                cursor.execute(query, params)
            except pymysql.Error as e:
                raise e
            result = cursor.fetchall()
            return [self.parsed_db_result_node_sso(row) for row in result] if result else []

    def query_db_one_node_sso(self, query, params=None, parsed=True) -> dict:
        connection = self.get_connection_node_sso()
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            try:
                cursor.execute(query, params)
            except pymysql.Error as e:
                raise e
            result = cursor.fetchone()
            return self.parsed_db_result_node_sso(result) if result else {}

    def write_db_node_sso(self, query, params=None) -> int:
        connection = self.get_connection_node_sso()
        with connection.cursor() as cursor:
            try:
                cursor.execute(query, params)
                connection.commit()
                return cursor.lastrowid
            except pymysql.Error as e:
                connection.rollback()
                raise e
            finally:
                connection.close()

    def __del__(self):
        pass


class ModifiedESConnection:
    def __init__(self, es_host, es_port):
        self.es_host = es_host
        self.es_port = es_port

    def get_es_handle(self):
        es_client = Elasticsearch(
            hosts=[{'host': self.es_host, 'port': self.es_port}],
            timeout=30,
            connection_class=RequestsHttpConnection)
        return es_client

class ESUtility:
    def __init__(self, es_handle, index, doctype):
        self.es_handle = es_handle
        self.es_index = index
        self.es_doctype = '_doc' if index in ['plotch_products_p4p76erzw4', 'plotch_products_j1uksul7pz',
                                              'plotch_products_zfykjvf9j0', 'plotch_products_qpygsziwtp'] else doctype

    @staticmethod
    def _get_parsed_es_data(es_data) -> list:
        return [data.get('_source', {}) for data in es_data.get('hits', {}).get('hits', [])]

    def get_total_rows_count(self, es_query):
        es_count = self.es_handle.count(index=self.es_index, doc_type=self.es_doctype, body=es_query)
        return self.es_handle.count(index=self.es_index, doc_type=self.es_doctype, body=es_query)

    def _get_parsed_query_data(self, query) -> list:
        es_data = self.es_handle.search(index=self.es_index, doc_type=self.es_doctype, body=query)
        return self._get_parsed_es_data(es_data)

    def _get_data_by_scrolling(self, query) -> list:
        response_data = []
        es_data = self.es_handle.search(index=self.es_index, doc_type=self.es_doctype, scroll='2m', size=1000,
                                        body=query)
        sid = es_data['_scroll_id']
        scroll_size = es_data['hits']['total']
        response_data.extend(self._get_parsed_es_data(es_data))
        while scroll_size > 0:
            page = self.es_handle.scroll(scroll_id=sid, scroll='2m')
            sid = page['_scroll_id']
            scroll_size = len(page['hits']['hits'])
            parsed_es_data = self._get_parsed_es_data(page)
            response_data.extend(parsed_es_data)
        return response_data

    def get_parsed_es_result_set(self, es_query, fields=None) -> list:
        if fields:
            es_query.update({'_source': fields})
        return self._get_parsed_query_data(es_query)

    def get_document_from_es(self, query) -> dict:
        response_data = self._get_parsed_query_data(query)
        return response_data[0] if response_data else {}

    def get_complete_es_result_set(self, query, fields=None) -> dict:
        if fields:
            query.update({'_source': fields})
        return self.es_handle.search(index=self.es_index, doc_type=self.es_doctype, body=query)

