from config import Config
from datetime import datetime
import json
from app.common_utils import get_current_datetime, clean_string, authenticate_user
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
        try:
            return self.coordinator.save_data_in_db(log_params, 'plotch_noderetailapi_request_logs')
        except:
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
        entity_id = self.generate_api_logs('inventory', self.params.get('item_id'), self.params.get('storefront_instance_id'))
        authenticate_user_from_through_sso = authenticate_user(self.headers.get('Auth-Token'), self.headers.get('Nodesso-Id'))
        self.params['log_id'] = entity_id
        try:
           inventory_entity_id = self.coordinator.save_data_in_db({'status': 0, 'parent_id': entity_id, 'item_id': self.params.get('item_id'),
        'qty': self.params.get('qty'), 'storefront_id': self.params.get('storefront_instance_id'), 'created_at': get_current_datetime()}, 'plotch_inventory_importer_data')
        except:
            inventory_entity_id = self.coordinator.save_data_in_db({'status': 0, 'parent_id': entity_id, 'item_id': self.params.get('item_id'),
            'qty': self.params.get('qty'), 'storefront_id': self.params.get('storefront_instance_id'), 'created_at': get_current_datetime()}, 'plotch_inventory_importer_data')
        self.params['inventory_entity_id'] = inventory_entity_id
        try:
           error_msg = self.coordinator.push_data_in_queue({'inventory_entity_id': inventory_entity_id}, 'noderetail_inventory_update_sync_q')
        except:
            error_msg = self.coordinator.push_data_in_queue({'inventory_entity_id': inventory_entity_id}, 'noderetail_inventory_update_sync_q')
        if error_msg:
            try:
               self.coordinator.update_data_in_db({'status': 8, 'error_log': error_msg}, 'plotch_noderetailapi_request_logs', [{'col': 'entity_id', 'val': entity_id}])
            except:
                self.coordinator.update_data_in_db({'status': 8, 'error_log': error_msg}, 'plotch_noderetailapi_request_logs', [{'col': 'entity_id', 'val': entity_id}])
            try:
                self.coordinator.update_data_in_db({'status': 8}, 'plotch_inventory_importer_data', [{'col': 'entity_id', 'val': inventory_entity_id}])
            except:
                self.coordinator.update_data_in_db({'status': 8}, 'plotch_inventory_importer_data', [{'col': 'entity_id', 'val': inventory_entity_id}])
        return {}
