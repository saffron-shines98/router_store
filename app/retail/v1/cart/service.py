import json
from app.common_utils import get_current_datetime, clean_string, authenticate_user
from app.exceptions import AuthMissing, InvalidDateFormat, AlreadyExists
from app.retail.v1.cart.cart_coordinator import CartCoordinator

class CartService:

    def __init__(self, params, headers):
        self.params = params
        self.headers = headers
        self.coordinator = CartCoordinator()

    def generate_api_logs(self, type=None, identifier_id=None, identifier_instance_id=None):
        log_params = {
            'request': json.dumps(self.params),
            'headers': json.dumps(self.headers),
            'created_at': get_current_datetime(),
            'type': type,
            'identifier_id': identifier_id,
            'identifier_instance_id': identifier_instance_id
        }
        try:
            return self.coordinator.save_data_in_db_pool_nodeapp(log_params, 'plotch_noderetailapi_request_logs')
        except:
            return self.coordinator.save_data_in_db_pool_nodeapp(log_params, 'plotch_noderetailapi_request_logs')

    def authenticate_user(self):
        jwt_token = self.headers.get('Auth-Token')
        nodesso_id = self.headers.get('Nodesso-Id')
        if not jwt_token:
            raise AuthMissing('Auth token is missing')
        payload = {
            'nodesso_id': nodesso_id,
            'auth_token': jwt_token
        }
        self.coordinator.validate_jwt(payload)

    def cart_create(self):
        # authenticate_user_from_through_sso = authenticate_user(self.headers.get('Auth-Token'), self.headers.get('Nodesso-Id'))
        client_cart_id = self.params.get('client_cart_id')
        noderetail_storefront_id = self.params.get('noderetail_storefront_id')
        log_id = self.generate_api_logs(type='cart_create', identifier_id=client_cart_id, identifier_instance_id=noderetail_storefront_id)
        try:
            self.coordinator.push_data_in_queue({'entity_id': log_id}, 'noderetail_cart_create_q')
        except:
            self.coordinator.push_data_in_queue({'entity_id': log_id}, 'noderetail_cart_create_q')

        response_data = {
            'api_action_status': 'success',
            'client_cart_id': client_cart_id,
            'noderetail_storefront_id': noderetail_storefront_id
        }
        return response_data

    def cart_update(self):
        authenticate_user_from_through_sso = authenticate_user(self.headers.get('Auth-Token'), self.headers.get('Nodesso-Id'))
        client_cart_id = self.params.get('client_cart_id')
        noderetail_storefront_id = self.params.get('noderetail_storefront_id')
        noderetail_cart_id = self.params.get('noderetail_cart_id')
        log_id = self.generate_api_logs(type='cart_update', identifier_id=client_cart_id, identifier_instance_id=noderetail_storefront_id)
        try:
            self.coordinator.push_data_in_queue({'entity_id': log_id}, 'noderetail_cart_update_q')
        except:
            self.coordinator.push_data_in_queue({'entity_id': log_id}, 'noderetail_cart_update_q')

        response_data = {
            'api_action_status': 'success',
            'client_cart_id': client_cart_id,
            'noderetail_cart_id': noderetail_cart_id
        }
        return response_data