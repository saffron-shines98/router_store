from config import Config
from datetime import datetime
import json
from app.common_utils import get_current_datetime
from app.exceptions import AuthMissing
from app.retail.v1.product.product_coordinator import ProductCoordinator
from app.common_utils import validate_jwt



class ProductService:
    def __init__(self, params, headers):
        self.params = params
        self.headers = headers
        self.coordinator = ProductCoordinator()
    
    def create_product_request_log(self):
        self.headers.update({"Skip-Validation": self.headers.get('Skip-Validation') or "1",
                             "Storefront-Id": self.params.get('noderetail_storefront_id', ''),
                             "Authorization": Config.API_ACCESS_KEY})
        db_params = {'request': json.dumps(self.params), 'headers': json.dumps(self.headers),
            'status': 0, 'created_at': get_current_datetime(), 'created_by': 1, 'type': 'product'}
        entity_id = self.coordinator.save_data_in_db_with_place_holder(db_params, 'plotch_noderetailapi_request_logs')
        self.coordinator.push_data_in_queue({"entity_id": entity_id}, 'product_create_request_log_q')
        if not self.headers.get('Auth-Token', ''):
            raise AuthMissing('Auth token is missing')
        payload = {'nodesso_id': self.headers.get('Nodesso-Id', ''),'auth_token': self.headers.get('Auth-Token', '')}
        validate_jwt(payload)
        return dict()