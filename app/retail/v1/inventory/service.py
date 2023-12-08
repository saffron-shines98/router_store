from config import Config
from datetime import datetime
import json
from app.common_utils import get_current_datetime, clean_string
from app.exceptions import AuthMissing, InvalidDateFormat, AlreadyExists
from app.retail.v1.inventory.inventory_coordinator import InventoryCoordinator


class InventoryService:

    def __init__(self, params, headers):
        self.params = params
        self.headers = headers
        self.coordinator = InventoryCoordinator()

    def generate_api_logs(self, type, identifier_id, identifier_instance_id):
        log_params = {
            'request': json.dumps(self.params),
            'headers': json.dumps(self.headers),
            'created_at': get_current_datetime(),
            'type': type,
            'identifier_id': identifier_id,
            'identifier_instance_id': identifier_instance_id
        }
        return self.coordinator.save_data_in_db(log_params, 'plotch_noderetailapi_request_logs')

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

    def update_inventory(self):
        self.generate_api_logs('inventory', self.params.get('item_id'), self.params.get('storefront_instance_id'))
        self.authenticate_user()
        self.coordinator.push_data_in_queue(self.params, 'noderetail_inventory_update_sync_q')
        return {}
