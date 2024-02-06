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

    def fetch_vendor(self):
        identifier_id = self.params.get('provider_id')
        identifier_instance_id = self.params.get('noderetail_storefront_id')
        status = self.params.get('status')
        store_name = self.params.get('store_name')
        email = self.params.get('provider_email')
        phone = self.params.get('provider_phone')
        city = self.params.get('provider_city')
        state = self.params.get('provider_state')
        authenticate_user_from_through_sso = authenticate_user(self.headers.get('Auth-Token'), self.headers.get('Nodesso-Id'))
        entity_id = self.generate_api_logs(type='fetch_vendor', identifier_id=identifier_id, identifier_instance_id=identifier_instance_id)

        status_f = "AND rui.is_active = '{}' ".format(status) if status else ''
        storename = "AND rui.company_name = '{}' ".format(store_name) if store_name else ''
        email_f = "AND rui.email = '{}' ".format(email) if email else ''
        phone_f = "AND rui.mobile = '{}' ".format(phone) if phone else ''
        city_f = "AND rui.city = '{}' ".format(city) if city else ''
        state_f = "AND rui.state = '{}' ".format(state) if state else ''

        user_instance_ids = self.coordinator.get_user_instance_id(self.params.get('noderetail_storefront_id'))
        get_providers_data = self.coordinator.fetch_provider_details(identifier_id, user_instance_ids, status_f, storename, email_f,
        phone_f, city_f, state_f)

        response_payload = []
        for provider_data in get_providers_data:
            tnc = json.loads(provider_data.get('other_params') or '{}')
            try:
                store_timing = json.loads(provider_data.get('store_timing', ''))
            except:
                store_timing = []
            open_hours = []
            if store_timing:
                for time in store_timing:
                    start_time, end_time = time.split('-')[0], time.split('-')[1]
                    open_hours.append({'start_time': start_time, 'end_time': end_time})
            if provider_data.get('rui.account_id') == provider_data.get('rhi.account_id'):
                serviceability_mode = provider_data.get('serviceability_mode', '')
                pickup_radius = str(provider_data.get('pickup_radius', ''))
            else:
                serviceability_mode = pickup_radius = ''
            provider_payload = {
                "provider_id": provider_data.get('seller_id'),
                "agg_marketplace_id": provider_data.get(self.params.get('agg_marketplace_id')),
                "status": provider_data.get('is_active'),
                "create_account": True,
                "agg_subscribe": True,
                "provider_profile": {
                    "store_name": provider_data.get('company_name'),
                    "brand_logo": provider_data.get('marketplace_logo'),
                    "long_desc": provider_data.get('store_detail_description'),
                    "short_desc": provider_data.get('store_description'),
                    "provider_contact_name": provider_data.get('name'),
                    "provider_email": provider_data.get('email'),
                    "provider_phone": provider_data.get('mobile'),
                    "customer_support_email": provider_data.get('email'),
                    "customer_support_phone": provider_data.get('mobile'),
                    "store_images": [provider_data.get('image')],
                },
                "certs": {
                    "fssai_license_num": provider_data.get('fssai'),
                    "aadhaar_num": provider_data.get('aadhaar_num'),
                    "pan_num": provider_data.get('pan_no'),
                    "gst_num": provider_data.get('gstin'),
                },
                "serviceability": [
                    {
                        "category": provider_data.get('categories'),
                        "mode": serviceability_mode,
                        "radius": pickup_radius,
                        "unit": 'km',
                    }
                ],
                "banks": [
                    {
                        "beneficiary_name": provider_data.get('contact_name'),
                        "bank_name": provider_data.get('account_name'),
                        "bank_account_num": provider_data.get('account_no'),
                        "bank_ifsc_code": provider_data.get('ifsc_code'),
                        "bank_account_type": provider_data.get('account_type'),
                    }
                ],
                "locations": [
                    {
                        "id": provider_data.get('alternate_location_id'),
                        "gps": provider_data.get('gps_coordinates'),
                        "type": "billing",
                        "address": {
                            "city": provider_data.get('shipping_city'),
                            "state": provider_data.get('shipping_state'),
                            "street": provider_data.get('shipping_address'),
                            "area_code": provider_data.get('shipping_pincode'),
                            "locality": provider_data.get('shipping_address'),
                        },
                        "schedule": {
                            "open_days": json.loads(provider_data.get('store_open_days')),
                            "open_hours": open_hours
                        }
                    }
                ],
                "tnc": {
                    "fulfillment_mode": tnc.get('fulfillment_mode'),
                    "available_on_cod": bool(tnc.get('available_on_cod')),
                    "cancellable": bool(tnc.get('cancellable')),
                    "rateable": bool(tnc.get('rateable')),
                    "return_pickup": bool(tnc.get('supports_return_pickup')),
                    "return_window": tnc.get('return_window'),
                    "returnable": bool(tnc.get('returnable')),
                    "time_to_ship": tnc.get('time_to_ship'),
                    "courier_control": tnc.get('courier_control'),
                }
            }
            response_payload.append(provider_payload)
        return {"api_action_status": "success", "providers": response_payload}