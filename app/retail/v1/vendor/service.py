import json
from app.common_utils import get_current_datetime
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
            log_id = self.generate_api_logs(type='vendor', identifier_id=provider_id, identifier_instance_id=user_instance_id)
            self.authenticate_user()
            provider_profile = provider_details.get('provider_profile', {})
            certs = provider_details.get('certs', {})
            serviceability = provider_details.get('serviceability', [{}])[0]
            banks = provider_details.get('banks', [{}])[0]
            account_common_object= [{'col': 'user_instance_id', 'val': user_instance_id}]
            try:
                account_id = self.coordinator.get_single_data_from_db('retail_user_instance', account_common_object,['account_id']).get('account_id')
            except:
                account_id = self.coordinator.get_single_data_from_db('retail_user_instance', account_common_object,['account_id']).get('account_id')
            request_params = {
                'provider_id': provider_id,
                'agg_marketplace_id': provider_details.get('agg_marketplace_id'),
                'agg_subscribe': provider_details.get('agg_subscribe'),
                'provider_status': provider_details.get('status'),
                'create_account': provider_details.get('create_account'),
                'name': provider_profile.get('provider_contact_name'),
                'store_name': provider_profile.get('store_name'),
                'logo': provider_profile.get('brand_logo'),
                'long_desc': provider_profile.get('long_desc'),
                'short_desc': provider_profile.get('short_desc'),
                'email': provider_profile.get('provider_email'),
                'phone': provider_profile.get('provider_phone'),
                'customer_support_email': provider_profile.get('customer_support_email'),
                'customer_support_phone': provider_profile.get('customer_support_phone'),
                'store_image': ','.join(provider_profile.get('store_images')),
                'fssai_licence_number': certs.get('fssai_license_num'),
                'aadhaar_num': certs.get('aadhaar_num'),
                'pan_num': certs.get('pan_num'),
                'gst_num': certs.get('gst_num'),
                'category': serviceability.get('category'),
                'serviceability': serviceability.get('mode'),
                'radius': serviceability.get('radius'),
                'unit': serviceability.get('unit'),
                'beneficary_name': banks.get('beneficary_name'),
                'bank_name': banks.get('bank_name'),
                'bank_account_num': banks.get('bank_account_num'),
                'bank_ifsc_code': banks.get('bank_ifsc_code'),
                'bank_account_type': banks.get('bank_account_type'),
                'user_instance_id': user_instance_id,
                'status': 0,
                'parent_id': log_id, 
                'created_at': get_current_datetime(),   
                'account_id': account_id,
                'created_by': provider_details.get('noderetail_account_user_id'),
                'is_api': 1
            }
            locations = provider_details.get('locations', [])
            for details in locations:
                address = details.get('address', {})
                schedule = details.get('schedule', {})
                open_hours = schedule.get('open_hours', [{}])[0]
                if details.get('type') == 'shipping':
                    request_params.update({
                        'gps': details.get('gps'),
                        'street': address.get('street'),
                        'city': address.get('city'),
                        'state': address.get('state'),
                        'area_code': address.get('area_code'),
                        'locality': address.get('locality'),
                        'store_working_days': schedule.get('open_days'),
                        'store_start_hour': open_hours.get('start_time'),
                        'store_close_hour': open_hours.get('end_time'),
                    })
                elif details.get('type') == 'billing':
                    request_params.update({
                        'billing_gps': details.get('gps'),
                        'billing_street': address.get('street'),
                        'billing_city': address.get('city'),
                        'billing_state': address.get('state'),
                        'billing_area_code': address.get('area_code'),
                        'billing_locality': address.get('locality'),
                        'billing_store_working_days': schedule.get('open_days'),
                        'billing_store_start_hour': open_hours.get('start_time'),
                        'billing_store_close_hour': open_hours.get('end_time'),
                    })
                elif details.get('type') == 'pickup':
                    request_params.update({
                        'pickup_gps': details.get('gps'),
                        'pickup_street': address.get('street'),
                        'pickup_city': address.get('city'),
                        'pickup_state': address.get('state'),
                        'pickup_area_code': address.get('area_code'),
                        'pickup_locality': address.get('locality'),
                        'pickup_store_working_days': schedule.get('open_days'),
                        'pickup_store_start_hour': open_hours.get('start_time'),
                        'pickup_store_close_hour': open_hours.get('end_time'),
                    })
            try:
                self.coordinator.save_data_in_db(request_params, 'plotch_vendor_importer_data')
            except:
                self.coordinator.save_data_in_db(request_params, 'plotch_vendor_importer_data')
        return 'success'
        

        