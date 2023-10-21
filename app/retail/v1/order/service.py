from config import Config
from datetime import datetime
import json
from app.common_utils import get_current_datetime
from app.exceptions import AuthMissing
from app.retail.v1.order.order_coordinator import OrderCoordinator

class OrderService:

    def __init__(self, params, headers):
        self.params = params
        self.headers = headers
        self.coordinator =OrderCoordinator()

    def update_order_status(self):
        log_params = {
            'request': json.dumps(self.params),
            'headers': json.dumps(self.headers),
            'created_at': get_current_datetime()
        }
        self.coordinator.save_data_in_db(log_params, 'plotch_order_status_request_logs')
        jwt_token = self.headers.get('Auth-Token')
        nodesso_id = self.headers.get('Nodesso-Id')
        if not jwt_token:
            raise AuthMissing('Auth token is missing')
        payload = {
            'nodesso_id': nodesso_id,
            'auth_token': jwt_token
        }
        self.coordinator.validate_jwt(payload)
        created_time = self.params.get('status_created_time')
        input_format = "%d:%m:%Y %H:%M:%S"
        output_format = "%Y:%m:%d %H:%M:%S"
        parsed_date = datetime.strptime(created_time, input_format)
        converted_date_time = parsed_date.strftime(output_format)
        order_payload = {
            "order_id": self.params.get('order_id'),
            "order_status": self.params.get('order_status'),
            "fulfilment_status": self.params.get('fulfilment_status'),
            "refund_status": self.params.get('refund_status'),
            "status_created_time": converted_date_time,
            "remark": self.params.get('remark'),
            "created_at":get_current_datetime()
        }
        entity_id = self.coordinator.save_data_in_db(order_payload, 'plotch_order_status_request')
        self.coordinator.push_data_in_queue({"entity_id": entity_id}, 'plotch_order_status_request_q')
        return order_payload

    def customer_status_create(self):
        log_params = {
            'request': json.dumps(self.params),
            'headers': json.dumps(self.headers),
            'created_at': get_current_datetime()
        }
        self.coordinator.save_data_in_db(log_params, 'plotch_order_status_request_logs')
        jwt_token = self.headers.get('Auth-Token')
        nodesso_id = self.headers.get('Nodesso-Id')
        if not jwt_token:
            raise AuthMissing('Auth token is missing')
        payload = {
            'nodesso_id': nodesso_id,
            'auth_token': jwt_token
        }
        self.coordinator.validate_jwt(payload)
        account_id = self.coordinator.get_account_id(self.params.get('customer_instance_id'))
        request_data = json.dumps(self.params)
        location_payload= self.params.get('location')
        for location in location_payload:
            gps=location.get('gps')
            city = location.get('city')
            country= location.get('country')
            area_code= location.get('area_code')
            building = location.get('building')
            is_default= location.get('is_default')
            label = location.get('label')
            locality = location.get('locality')
            state = location.get('state')
            street_name = location.get('street_name')
            type = location.get('type')

        customer_status_payload = {
            'firstname': self.params.get('customer_contact_info').get('firstname'),
            'lastname': self.params.get('customer_contact_info').get('lastname'),
            'birthdate': self.params.get('customer_contact_info').get('birthdate'),
            'account_user_id': self.params.get('noderetail_account_user_id'),
            'source': self.params.get('customer_contact_info').get('source'),
            'phone': self.params.get('customer_contact_info').get('contact').get('phone'),
            'email': self.params.get('customer_contact_info').get('contact').get('email'),
            'otp_verified': self.params.get('customer_contact_info').get('customer_user_id').get('otp_verified'),
            'customer_user_id_phone': self.params.get('customer_contact_info').get('customer_user_id').get('phone'),
            'gps': gps,
            'building': building,
            'street': street_name,
            'city': city,
            'locality': locality,
            'area_code': area_code,
            'state': state,
            'country': country,
            'label': label,
            'alternate_customer_id': self.params.get('customer_id'),
            'status': 1,
            'created_at': get_current_datetime(),
            'account_id': account_id.get('account_id'),
            'created_by': 1,
            'request': request_data,
            'customer_instance_id': self.params.get('noderetail_customer_instance_id')
        }
        self.coordinator.save_data_in_db(customer_status_payload, 'plotch_customer_importer_data')
        return 'success'
