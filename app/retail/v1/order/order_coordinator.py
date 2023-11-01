from config import Config
from app.exceptions import InvalidAuth
from app.base_coordinator import BaseCoordinator,SSOCoordinator


class OrderCoordinator(BaseCoordinator):

    def __init__(self):
        super(OrderCoordinator, self).__init__()
        self.sso_coordinator =SSOCoordinator()

    def validate_jwt(self, payload):
        response = self.sso_coordinator.post('/verifyHeader', payload=payload, headers={'Authorization':Config.Authorization})
        if response.status_code == 200:
            return response.json().get('d')
        raise InvalidAuth('Invalid auth token.')

    def get_account_id(self, customer_instance):
        query = 'select account_id from retail_customer where customer_instance = {} limit 1'.format(customer_instance)
        return self.mysql_conn.query_db_one(query)
    
    def check_duplicacy(self, identifier, identifier_instance):
        query = "select entity_id from plotch_noderetailapi_request_logs where identifier_id = '{}' and identifier_instance_id = {} limit 1".format(identifier, identifier_instance)
        return self.mysql_conn.query_db_one(query)


