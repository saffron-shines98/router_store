import json
from app.common_utils import get_current_datetime, authenticate_user
from app.exceptions import AuthMissing, AlreadyExists
from app.retail.v1.vendor.vendor_coordinator import VendorCoordinator

class VendorService:

    def __init__(self, params, headers):
        self.params = params
        self.headers = headers
        self.coordinator = VendorCoordinator()

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

    def create_vendor(self):
        noderetail_storefront_id = self.params.get('noderetail_storefront_id')
        for provider_details in self.params.get('providers'):
            provider_id = provider_details.get('provider_id')
            log_id = self.generate_api_logs(type='vendor', identifier_id=provider_id, identifier_instance_id=noderetail_storefront_id)
            try:
                self.coordinator.push_data_in_queue({'entity_id': log_id}, 'noderetail_provider_create_q')
            except:
                self.coordinator.push_data_in_queue({'entity_id': log_id}, 'noderetail_provider_create_q')
        return 'success'
        

        