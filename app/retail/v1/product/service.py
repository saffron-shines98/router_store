from config import Config
from datetime import datetime
import json
from decimal import Decimal
from app.common_utils import get_current_datetime, authenticate_user
from app.exceptions import AuthMissing
from app.retail.v1.product.product_coordinator import ProductCoordinator
from app.common_utils import validate_jwt



class ProductService:
    def __init__(self, params, headers):
        self.params = params
        self.headers = headers
        self.coordinator = ProductCoordinator()

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
            return self.coordinator.save_data_in_db_pool(log_params, 'plotch_noderetailapi_request_logs')
        except:
            return self.coordinator.save_data_in_db_pool(log_params, 'plotch_noderetailapi_request_logs')

    def create_product_request_log(self):
        self.headers.update({"Skip-Validation": self.headers.get('Skip-Validation') or "1",
                             "Storefront-Id": self.params.get('noderetail_storefront_id', ''),
                             "Authorization": Config.API_ACCESS_KEY})
        db_params = {'request': json.dumps(self.params), 'headers': json.dumps(self.headers),
            'status': 0, 'created_at': get_current_datetime(), 'created_by': 1, 'type': 'product',
            'identifier_id': self.params.get('item_id', '')}
        try:
            entity_id = self.coordinator.save_data_in_db_with_place_holder(db_params, 'plotch_noderetailapi_request_logs')
        except:
            entity_id = self.coordinator.save_data_in_db_with_place_holder(db_params,'plotch_noderetailapi_request_logs')
        try:
            self.coordinator.push_data_in_queue({"entity_id": entity_id}, 'product_create_request_log_q')
        except:
            self.coordinator.push_data_in_queue({"entity_id": entity_id}, 'product_create_request_log_q')
        if not self.headers.get('Auth-Token', ''):
            raise AuthMissing('Auth token is missing')
        authenticate_user_from_through_sso = authenticate_user(self.headers.get('Auth-Token'),self.headers.get('Nodesso-Id'))
        return dict()

    def product_status(self):
        for product_details in self.params.get('items'):
            ondc_item_id = product_details.get('item_id')
            email = product_details.get('noderetail_account_user_id')
            authenticate_user_from_through_sso = authenticate_user(self.headers.get('Auth-Token'), self.headers.get('Nodesso-Id'))
            account_id = self.coordinator.get_account_id(email)
            product_status_details = self.coordinator.get_product_status(ondc_item_id, account_id.get('account_id'))
            if product_status_details:
                item = product_status_details[0]
                catalog_id = item.get('catalog_id')
                storefront_id = self.coordinator.get_storefront_id(catalog_id)
                marketplace_details = self.coordinator.get_marketplace_details(storefront_id.get('storefront_id'))
                instance_details = json.loads(marketplace_details.get('instance_details', '{}'))
                marketplace_name = self.coordinator.get_marketplace_name(instance_details.get('marketplace_instance'))
                entity_id = self.generate_api_logs(type='product_status', identifier_id=ondc_item_id, identifier_instance_id=storefront_id.get('storefront_id'))

                response_payload = []
                for details in product_status_details:
                    payload = {
                        "item_id": details.get('ondc_item_id'),
                        "noderetail_item_id": details.get('ondc_item_id'),
                        "is_item_created": bool(product_status_details),
                        "noderetail_account_user_id": details.get('account_id'),
                        "noderetail_catalog_id": details.get('catalog_id'),
                        "is_item_active": True if details.get('is_active') == 1 else False,
                        "is_item_instock": True if float(details.get('qty', 0)) > 0 else False,
                        "inventory": str(details.get('qty')),
                        "agg_marketplace_info": [
                            {
                                "agg_marketplace_id": instance_details.get('marketplace_instance'),
                                "agg_marketplace_name": marketplace_name.get('marketplace_name'),
                                "is_item_active": True if details.get('is_active') == 1 else False,
                                "is_item_instock": True if float(details.get('qty', 0)) > 0 else False,
                                "inventory": str(details.get('qty')),
                                "last_catalog_sync_time": details.get('updated_at'),
                                "last_inv_sync_time": details.get('updated_at'),
                            }
                        ],
                    }
                    response_payload.append(payload)
                return {"api_action_status": "success", "items_status": response_payload}

