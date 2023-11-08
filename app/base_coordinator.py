import json
import requests
from config import Config
from flask import Response
from app.exceptions import InvalidAuth, AuthMissing


class BaseCoordinator:

    def __init__(self, base_url=''):
        self.base_url = base_url
        self.mysql_conn = Config.MYSQL_CONN
        self.rabbitmq_conn = Config.RABBITMQ_CONNECTION

    def get_single_data_from_db(self, table_name: str, condition_params: list, column_list='*', order_by_column=1, order_by='ASC') -> dict:
        column_sub_query = ','.join(column_list)
        where_sub_query = ' and '.join(['{} {} %s'.format(data.get('col'), data.get('operator') or '=')
                for data in condition_params])
        order_by_query = ' order by {} {} '.format(order_by_column, order_by)
        query = '''select {} from {} where {} {} limit 1'''.format(column_sub_query, table_name, where_sub_query, order_by_query,)
        return self.mysql_conn.query_db_one(query, tuple([data.get('val') for data in condition_params]))

    def get_multiple_data_from_db(self, table_name: str, condition_params: list, column_list='*',  order_by_column=1, order_by='ASC') -> list:
        column_sub_query = ','.join(column_list)
        where_sub_query = ' and '.join(['{} {} %s'.format(data.get('col'), data.get('operator') or '=') for data in condition_params])
        order_by_query = ' order by {} {} '.format(order_by_column, order_by)
        query = '''select {} from {} where {} {}'''.format(column_sub_query, table_name, where_sub_query, order_by_query)
        return self.mysql_conn.query_db(query, tuple([data.get('val') for data in condition_params]))

    def save_data_in_db(self, db_params: dict, table_name: str, commit=True) -> int:
        query = "insert into " + table_name + " (" + ",".join(db_params.keys()) + ") VALUES (" + ",".join(
            ['%s' for x in db_params.values()]) + ")"
        if commit:
            return self.mysql_conn.write_db(query, tuple(db_params.values()))
        else:
            return self.mysql_conn.cursor.execute(query, tuple(db_params.values()))
        
    def update_data_in_db(self, db_params: dict, table_name: str, condition_params: list, commit=True) -> int:
        update_values = [str(key) + " = '" + str(val) + "'" for key, val in db_params.items()]
        query = 'update ' + table_name + '  set ' + ','.join(
            update_values) + ' where {}'.format(' AND '.join(['{} {} %s'.format(data.get('col'), data.get('operator') or '=')
                for data in condition_params]))
        if commit:
            return self.mysql_conn.write_db(query, tuple([data.get('val') for data in condition_params]))
        else:
            return self.mysql_conn.cursor.execute(query, tuple([data.get('val') for data in condition_params]))
    
    def save_data_in_db_with_place_holder(self, db_params, table_name, commit=True):
        query = "insert into " + table_name + " (" + ",".join(db_params.keys()) + ") VALUES (" + ', '.join('%s' for v in db_params.values()) + ")"
        if commit:
            return self.mysql_conn.write_db(query, tuple([v for v in db_params.values()]))
        else:
            return self.mysql_conn.cursor.execute(query, tuple([v for v in db_params.values()]))

    @staticmethod
    def path_with_slash(path: str) -> str:
        return path if path.startswith('/') else '/' + path

    def action(self, path: str) -> str:
        return self.base_url.strip('/') + self.path_with_slash(path)

    def post(self, path, payload=None, headers=dict(), params=None, data=None, timeout=90) -> Response:
        headers.update({'Content-type': 'application/json', 'Accept': 'application/json'})
        response = requests.post(self.action(path), params=params, json=payload, headers=headers, data=data, timeout=timeout)
        return response

    def get(self, path, payload=None, headers=None, timeout=90):
        response = requests.get(
            self.action(path), params=payload, headers=headers, timeout=timeout)
        return response
    
    def push_data_in_queue(self, params, routing_key='', exchange=''):
        self.rabbitmq_conn.push_message_to_queue(exchange, routing_key, json.dumps(params))

    def validate_jwt(self, payload):
        response = SSOCoordinator().post('/verifyHeader', payload=payload,headers={'Authorization': Config.Authorization})
        if response.status_code == 200:
            return response.json().get('d')
        raise InvalidAuth('Invalid auth token.')

    def authenticate_user(self, jwt, nodesso):
        jwt_token = jwt
        nodesso_id = nodesso
        if not jwt_token:
            raise AuthMissing('Auth token is missing')
        payload = {
            'nodesso_id': nodesso_id,
            'auth_token': jwt_token
        }
        self.validate_jwt(payload)

class SSOCoordinator(BaseCoordinator):

    def __init__(self):
        base_url = Config.SSO_COORDINATOR_URI
        super(SSOCoordinator, self).__init__(base_url)
