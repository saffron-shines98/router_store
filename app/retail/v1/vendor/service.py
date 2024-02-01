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

    def generate_error_log(self, type=None, error_msg=None):
        log_params = {
            'request': json.dumps(self.params),
            'headers': json.dumps(self.headers),
            'created_at': get_current_datetime(),
            'type': type,
            'error_msg': error_msg
        }
        try:
            self.coordinator.save_data_in_db(log_params, 'noderetail_api_request_error_log')
        except:
            self.coordinator.save_data_in_db(log_params, 'noderetail_api_request_error_log')

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
        for provider_details in self.params.get('providers'):
            provider_id = provider_details.get('provider_id')
            user_instance_id = provider_details.get('noderetail_user_instance_id')
            log_common_object = [{'col': 'identifier_id', 'val': provider_id},{'col': 'identifier_instance_id', 'val': user_instance_id}]
            try:
                log_exist = self.coordinator.get_single_data_from_db('plotch_noderetailapi_request_logs',log_common_object , ['entity_id']).get('entity_id')
            except:
                log_exist = self.coordinator.get_single_data_from_db('plotch_noderetailapi_request_logs', log_common_object, ['entity_id']).get('entity_id')
            if log_exist:
                raise AlreadyExists('Provider already exists')

            try:
               authenticate_user_from_through_sso = authenticate_user(self.headers.get('Auth-Token'), self.headers.get('Nodesso-Id'))
            except Exception as e:
                self.generate_error_log(type='vendor', error_msg='Validation Error')
                raise AuthMissing('Validation Error')

            log_id = self.generate_api_logs(type='vendor', identifier_id=provider_id, identifier_instance_id=user_instance_id)
            try:
                self.coordinator.push_data_in_queue({'entity_id': log_id}, 'noderetail_provider_create_q')
            except:
                self.coordinator.push_data_in_queue({'entity_id': log_id}, 'noderetail_provider_create_q')
        return 'success'
        

        