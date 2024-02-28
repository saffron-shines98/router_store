import json
from app.common_utils import get_current_datetime,authenticate_user
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
        try:
            return self.coordinator.save_data_in_db_pool(log_params, 'plotch_noderetailapi_request_logs')
        except:
            return self.coordinator.save_data_in_db_pool(log_params, 'plotch_noderetailapi_request_logs')


    def update_price(self):
        entity_id = self.generate_api_logs('price', self.params.get('noderetail_item_id'), self.params.get('noderetail_storefront_id'))
        jwt_token= self.headers.get('Auth-Token')
        nodesso_id = self.headers.get('Nodesso-Id')
        authenticate_user_from_through_sso = authenticate_user(jwt_token, nodesso_id)
        pricing_info = self.params.get('pricing_info', {})
        mrp = pricing_info.get('mrp')
        sale_price = pricing_info.get('sale_price')
        discounted_price = pricing_info.get('discounted_price')
        try:
           price_entity_id = self.coordinator.save_data_in_db_pool({'status': 0, 'parent_id': entity_id, 'item_id': self.params.get('item_id'),
           'storefront_id': self.params.get('noderetail_storefront_id'), 'mrp': mrp, 'sale_price': sale_price,
           'discounted_price': discounted_price, 'created_at': get_current_datetime()}, 'plotch_price_importer_data')
        except:
            price_entity_id = self.coordinator.save_data_in_db_pool({'status': 0, 'parent_id': entity_id, 'item_id': self.params.get('item_id'),
            'storefront_id': self.params.get('noderetail_storefront_id'), 'mrp': mrp, 'sale_price': sale_price,
            'discounted_price': discounted_price, 'created_at': get_current_datetime()}, 'plotch_price_importer_data')
        try:
            error_msg = self.coordinator.push_data_in_queue({'entity_id':entity_id, 'price_entity_id': price_entity_id}, 'noderetail_price_update_sync_q')
        except:
            error_msg = self.coordinator.push_data_in_queue({'entity_id': entity_id, 'price_entity_id': price_entity_id}, 'noderetail_price_update_sync_q')
        if error_msg:
            try:
                self.coordinator.update_data_in_db_pool({'status': 8, 'error_log': error_msg}, 'plotch_noderetailapi_request_logs', [{'col': 'entity_id', 'val': entity_id}])
            except:
                self.coordinator.update_data_in_db_pool({'status': 8, 'error_log': error_msg},'plotch_noderetailapi_request_logs',[{'col': 'entity_id', 'val': entity_id}])
            try:
                self.coordinator.update_data_in_db_pool({'status': 8}, 'plotch_price_importer_data', [{'col': 'entity_id', 'val': price_entity_id}])
            except:
                self.coordinator.update_data_in_db_pool({'status': 8}, 'plotch_price_importer_data', [{'col': 'entity_id', 'val': price_entity_id}])
        return {}

    def bulk_update_price(self):
        entity_id = self.generate_api_logs('bulk_price','',self.params.get('noderetail_storefront_id'))
        jwt_token = self.headers.get('Auth-Token')
        nodesso_id = self.headers.get('Nodesso-Id')
        authenticate_user_from_through_sso = authenticate_user(jwt_token, nodesso_id)
        try:
            self.coordinator.push_data_in_queue({'entity_id': entity_id}, 'noderetail_bulk_price_update_sync_q')
        except:
            self.coordinator.push_data_in_queue({'entity_id': entity_id}, 'noderetail_bulk_price_update_sync_q')
        return {}