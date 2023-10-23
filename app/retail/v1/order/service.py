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

    def generate_api_logs(self, type=None):
        log_params = {
            'request': json.dumps(self.params),
            'headers': json.dumps(self.headers),
            'created_at': get_current_datetime(),
            'type': type
        }
        return self.coordinator.save_data_in_db(log_params, 'plotch_order_status_request_logs')

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
        customer_status_payload = {
            'firstname': self.params.get('customer_info').get('firstname'),
            'lastname': self.params.get('customer_info').get('lastname'),
            'birthdate': self.params.get('customer_info').get('birthdate'),
            'alternate_customer_id': self.params.get('customer_info').get('alternate_customer_id'),
            'source': self.params.get('customer_info').get('source'),
            'phone': self.params.get('customer_info').get('contact').get('phone'),
            'email': self.params.get('customer_info').get('contact').get('email'),
            'gps': self.params.get('location').get('gps'),
            'building': self.params.get('location').get('building'),
            'street': self.params.get('location').get('name'),
            'city': self.params.get('location').get('city'),
            'locality': self.params.get('location').get('locality'),
            'area_code': self.params.get('location').get('area_code'),
            'state': self.params.get('location').get('state'),
            'country': self.params.get('location').get('country'),
            'label': self.params.get('location').get('label'),
            'customer_instance_id': self.params.get('customer_instance_id'),
            'status': 1,
            'created_at': get_current_datetime(),
            'account_id': account_id.get('account_id'),
            'created_by': 1
        }
        self.coordinator.save_data_in_db(customer_status_payload, 'plotch_customer_importer_data')
        return 'success'
    
    def order_create(self):
        log_id = self.generate_api_logs(type='order')
        self.authenticate_user()
        customer_info = self.params.get('customer_info', {})
        billing_info = self.params.get('billing_info', {})
        billing_location = billing_info.get('location', {})
        shipping_info = self.params.get('shipping_info', {})
        shipping_location = shipping_info.get('location', {})
        order_info = self.params.get('order_info', {})
        order_items = order_info.get('order_items', [{}])[0]
        payment_info = self.params.get('payment_info', {})
        request_params = {     
            'user_instance_id': self.params.get('noderetail_account_user_id'),              
            'order_id': self.params.get('order_id'),        
            'alternate_customer_id': customer_info.get('customer_id'),   
            'phone': customer_info.get('contact', {}).get('phone'),                     
            'email': customer_info.get('contact', {}).get('email'),                     
            'billing_contact_number': billing_info.get('contact', {}).get('phone'),    
            'billing_email': billing_info.get('contact', {}).get('email'),             
            'billing_gps': billing_location.get('gps'),               
            'billing_building': billing_location.get('building'),          
            'billing_street': billing_location.get('street_name'),            
            'billing_city': billing_location.get('city'),              
            'billing_locality': billing_location.get('locality'),          
            'billing_area_code': billing_location.get('area_code'),         
            'billing_state': billing_location.get('state'),             
            'billing_country': billing_location.get('country'), 
            'billing_label': billing_location.get('label'),            
            'shipping_contact_number': shipping_info.get('contact', {}).get('phone'),   
            'shipping_email': shipping_info.get('contact', {}).get('email'),            
            'shipping_gps': shipping_location.get('gps'),              
            'shipping_building': shipping_location.get('building'),       
            'shipping_street': shipping_location.get('street_name'),         
            'shipping_city': shipping_location.get('city'),           
            'shipping_locality': shipping_location.get('locality'),       
            'shipping_area_code': shipping_location.get('area_code'),      
            'shipping_state': shipping_location.get('state'),          
            'shipping_country': shipping_location.get('country'), 
            'shipping_label': shipping_location.get('label'),                      
            'item_id': order_items.get('id'),                 
            'qty': order_items.get('qty'),                     
            'price': order_items.get('price'),                   
            'discount': order_items.get('discount'),                
            'taxes': order_items.get('taxes'),                   
            'order_discount': order_info.get('discount'),          
            'packaging_charges': order_info.get('packaging_charges'),       
            'delivery_charges': order_info.get('delivery_charges'),        
            'other_charges': order_info.get('other_charges'),           
            'order_total': order_info.get('order_total'),           
            'payment_mode': payment_info.get('payment_mode'),            
            'payment_transaction_id': payment_info.get('payment_transaction_id'),  
            'payment_status': payment_info.get('payment_status'),          
            'parent_id': log_id,               
            'storefront_id': self.params.get('noderetail_order_instance_id'),           
            'status': 0,                  
            'created_at': get_current_datetime(),                                                   
            'is_api': 1
        }      
        self.coordinator.save_data_in_db(request_params, 'plotch_order_importer_data')
        return 'success'
          