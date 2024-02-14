from config import Config
from datetime import datetime
import json
from app.common_utils import get_current_datetime, clean_string, authenticate_user
from app.exceptions import AuthMissing, InvalidDateFormat, AlreadyExists
from app.retail.v1.fulfillment.fulfillment_coordinator import FulfillmentCoordinator

class FulfillmentService:

    def __init__(self, params, headers):
        self.params = params
        self.headers = headers
        self.coordinator =FulfillmentCoordinator()

    def generate_api_logs(self, type=None, identifier_id=None, identifier_instance_id=None):
        log_params = {
            'request': json.dumps(self.params),
            'headers': json.dumps(self.headers),
            'created_at': get_current_datetime(),
            'type': type,
            'status': 0,
            'identifier_id': identifier_id,
            'identifier_instance_id': identifier_instance_id
        }
        try:
            return self.coordinator.save_data_in_db(log_params, 'plotch_noderetailapi_request_logs')
        except:
            return self.coordinator.save_data_in_db(log_params, 'plotch_noderetailapi_request_logs')

    def fulfillment_create(self):
        order_id = self.params.get('order_id')
        noderetail_storefront_id = self.params.get('noderetail_storefront_id')
        authenticate_user_from_through_sso = authenticate_user(self.headers.get('Auth-Token'), self.headers.get('Nodesso-Id'))
        log_id = self.generate_api_logs(type='fulfillment_create', identifier_id=order_id, identifier_instance_id=noderetail_storefront_id)
        return 'success'

    def fulfillment_status(self):
        order_id = self.params.get('order_id')
        noderetail_storefront_id = self.params.get('noderetail_storefront_id')
        # authenticate_user_from_through_sso = authenticate_user(self.headers.get('Auth-Token'), self.headers.get('Nodesso-Id'))
        # log_id = self.generate_api_logs(type='fulfillment_status', identifier_id=order_id, identifier_instance_id=noderetail_storefront_id)
        status_details = self.coordinator.get_fulfillment_status(order_id, noderetail_storefront_id)
        if status_details:
            for details in status_details:
                response_payload = {
                    "api_action_status": "success",
                    "fulfillment_id": details.get('fulfillment_id'),
                    "noderetail_fulfillment_id": self.params.get('noderetail_fulfillment_id'),
                    "fulfillment_mode": details.get('fulfillment_mode'),
                    "fulfillment_status": details.get('fulfillment_status'),
                    "fulfillment_courier": details.get('fulfillment_courier'),
                    "fulfillment_tracking": details.get('fulfillment_tracking'),
                    "fulfillment_update_time": details.get('fulfillment_update_time')
                }
                return response_payload
        return {"error": "Fulfillment status not found for the provided parameters"}
