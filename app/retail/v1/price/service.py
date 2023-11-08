import json
from app.common_utils import get_current_datetime
from app.retail.v1.price.price_coordinator import PriceCoordinator

class PriceService:

    def __init__(self, params, headers):
        self.params = params
        self.headers = headers
        self.coordinator = PriceCoordinator()

    def generate_api_logs(self, type, identifier_id, identifier_instance_id):
        log_params = {
            'request': json.dumps(self.params),
            'headers': json.dumps(self.headers),
            'created_at': get_current_datetime(),
            'type': type,
            'status':0,
            'identifier_id': identifier_id,
            'identifier_instance_id': identifier_instance_id
        }
        return self.coordinator.save_data_in_db(log_params, 'plotch_noderetailapi_request_logs')

    def update_price(self):
        entity_id = self.generate_api_logs('price', self.params.get('noderetail_item_id'), self.params.get('noderetail_storefront_id'))
        jwt_token= self.headers.get('Auth-Token')
        nodesso_id = self.headers.get('Nodesso-Id')
        self.coordinator.authenticate_user(jwt_token, nodesso_id)
        self.coordinator.push_data_in_queue({'entity_id':entity_id}, 'noderetail_price_update_sync_q')
        return {}