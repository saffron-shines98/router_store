import decimal

from config import Config
from datetime import datetime
import json
from app.common_utils import get_current_datetime, clean_string, authenticate_user
from app.exceptions import AuthMissing, InvalidDateFormat, AlreadyExists, BadRequest
from app.retail.v1.order.order_coordinator import OrderCoordinator

class OrderService:

    def __init__(self, params, headers):
        self.params = params
        self.headers = headers
        self.coordinator =OrderCoordinator()

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
            return self.coordinator.save_data_in_db_pool_nodeapp(log_params, 'plotch_noderetailapi_request_logs')
        except:
            return self.coordinator.save_data_in_db_pool_nodeapp(log_params, 'plotch_noderetailapi_request_logs')

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
        authenticate_user_from_through_sso = authenticate_user(self.headers.get('Auth-Token'), self.headers.get('Nodesso-Id'))
        log_params = {
            'request': json.dumps(self.params),
            'created_at': get_current_datetime(),
            'identifier_id': self.params.get('order_id'),
            'status': 0,
            'identifier_instance_id': self.params.get('noderetail_storefront_id')
        }
        try:
            entity = self.coordinator.save_data_in_db_pool(log_params, 'plotch_noderetailapi_status_request_logs')
        except:
            entity = self.coordinator.save_data_in_db_pool(log_params, 'plotch_noderetailapi_status_request_logs')
        return 'success'

    def customer_status_create(self):
        try:
            account_id = self.coordinator.get_account_id(self.params.get('noderetail_customer_instance_id'))
        except:
            account_id = self.coordinator.get_account_id(self.params.get('noderetail_customer_instance_id'))
        identifier_id = self.params.get('customer_id')
        identifier_instance_id = self.params.get('noderetail_customer_instance_id')
        try:
            check_duplicacy = self.coordinator.customer_check_duplicacy(identifier_instance_id, identifier_id)
        except:
            check_duplicacy = self.coordinator.customer_check_duplicacy(identifier_instance_id, identifier_id)
        log_params = {
            'request': json.dumps(self.params),
            'headers': json.dumps(self.headers),
            'created_at': get_current_datetime(),
            'custom_data': json.dumps({'customer_instance_id': self.params.get('noderetail_customer_instance_id')}),
            'created_by' : self.params.get('noderetail_account_user_id'),
            'account_id' : account_id.get('account_id'),
            'type': 'customer',
            'identifier_id': identifier_id,
            'identifier_instance_id':identifier_instance_id
        }
        try:
            entity= self.coordinator.save_data_in_db_pool_nodeapp(log_params, 'plotch_noderetailapi_request_logs')
        except:
            entity = self.coordinator.save_data_in_db_pool_nodeapp(log_params, 'plotch_noderetailapi_request_logs')
        if check_duplicacy:
            raise AlreadyExists('Customer Already Exist')
        jwt_token = self.headers.get('Auth-Token')
        if not jwt_token:
            raise AuthMissing('Auth token is missing')
        authenticate_user_from_through_sso = authenticate_user(self.headers.get('Auth-Token'), self.headers.get('Nodesso-Id'))
        customer_contact_info_phone = self.params.get('customer_contact_info').get('contact').get('phone')
        customer_user_id_phone = self.params.get('customer_contact_info').get('customer_user_id').get('phone')
        if not customer_contact_info_phone and customer_user_id_phone:
            customer_contact_info_phone= customer_user_id_phone
            self.params.get('customer_contact_info', {}).get('contact').update({'phone': customer_user_id_phone})
        if not customer_user_id_phone and customer_contact_info_phone:
            customer_user_id_phone=customer_contact_info_phone
            self.params.get('customer_contact_info', {}).get('customer_user_id').update({'phone': customer_contact_info_phone})
        location_payload= self.params.get('locations')
        for location in location_payload:
            gps=location.get('gps')
            city = clean_string(location.get('city', ''))
            country= location.get('country')
            area_code= location.get('area_code')
            building = clean_string(location.get('building', ''))
            is_default= location.get('is_default')
            label = clean_string(location.get('label', ''))
            locality = clean_string(location.get('locality', ''))
            state = clean_string(location.get('state', ''))
            street_name = clean_string(location.get('street_name', ''))
            type = location.get('type')
            break
        customer_status_payload = {
            'firstname': self.params.get('customer_contact_info').get('firstname'),
            'lastname': self.params.get('customer_contact_info').get('lastname'),
            'birthdate': self.params.get('customer_contact_info').get('birthdate'),
            'source': self.params.get('customer_contact_info').get('source'),
            'contact_phone': customer_contact_info_phone,
            'email': self.params.get('customer_contact_info').get('contact').get('email'),
            'otp_verified': self.params.get('customer_contact_info').get('customer_user_id').get('otp_verified'),
            'phone': customer_user_id_phone,
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
            'status': 0,
            'created_at': get_current_datetime(),
            'account_id': account_id.get('account_id'),
            'created_by': self.params.get('noderetail_account_user_id'),
            'parent_id' : entity,
            'is_api': 1,
            'customer_instance_id': self.params.get('noderetail_customer_instance_id')
        }
        try:
            self.coordinator.save_data_in_db_pool(customer_status_payload, 'plotch_customer_importer_data')
        except:
            self.coordinator.save_data_in_db_pool(customer_status_payload, 'plotch_customer_importer_data')
        return 'success'

    
    def order_create(self):
        identifier_id = self.params.get('order_id')
        identifier_instance_id = self.params.get('noderetail_order_instance_id')
        try:
            check_duplicacy = self.coordinator.check_order_duplicacy(identifier_id, identifier_instance_id)
        except:
            check_duplicacy = self.coordinator.check_order_duplicacy(identifier_id, identifier_instance_id)
        log_id = self.generate_api_logs('order', identifier_id, identifier_instance_id)
        if check_duplicacy:
            return 'success'
        authenticate_user_from_through_sso = authenticate_user(self.headers.get('Auth-Token'), self.headers.get('Nodesso-Id'))
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
            'billing_building': clean_string(billing_location.get('building', '')),          
            'billing_street': clean_string(billing_location.get('street_name', '')),            
            'billing_city': billing_location.get('city'),              
            'billing_locality': clean_string(billing_location.get('locality', '')),          
            'billing_area_code': billing_location.get('area_code'),         
            'billing_state': billing_location.get('state'),             
            'billing_country': billing_location.get('country'), 
            'billing_label': billing_location.get('label'),            
            'shipping_contact_number': shipping_info.get('contact', {}).get('phone'),   
            'shipping_email': shipping_info.get('contact', {}).get('email'),            
            'shipping_gps': shipping_location.get('gps'),              
            'shipping_building': clean_string(shipping_location.get('building', '')),       
            'shipping_street': clean_string(shipping_location.get('street_name', '')),         
            'shipping_city': shipping_location.get('city'),           
            'shipping_locality': clean_string(shipping_location.get('locality', '')),       
            'shipping_area_code': shipping_location.get('area_code'),      
            'shipping_state': shipping_location.get('state'),          
            'shipping_country': shipping_location.get('country'), 
            'shipping_label': shipping_location.get('label'),                      
            'item_id': order_items.get('id'),                 
            'qty': order_items.get('qty'),                     
            'price': order_items.get('price'),                   
            'discount': abs(int(order_items.get('discount'))),
            'taxes': order_items.get('taxes'),                   
            'order_discount': abs(int(order_info.get('discount'))),
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
        try:
            self.coordinator.save_data_in_db_pool(request_params, 'plotch_order_importer_data')
        except:
            self.coordinator.save_data_in_db_pool(request_params, 'plotch_order_importer_data')
        params = {
            'payment_mode': payment_info.get('payment_mode'),
            'payment_transaction_id': payment_info.get('payment_transaction_id'),
            'payment_status': 1 if payment_info.get('payment_status') == 'paid' else 0,
            'created_at': get_current_datetime()
        }

        try:
            self.coordinator.save_data_in_db_pool(params, 'plotch_imported_order_transaction')
        except:
            self.coordinator.save_data_in_db_pool(params, 'plotch_imported_order_transaction')
        return 'success'

    def order_update(self):
        identifier_id = self.params.get('order_id')
        identifier_instance_id = self.params.get('noderetail_order_instance_id')

        check_status = self.coordinator.check_order_status(identifier_id, identifier_instance_id)
        if check_status:
            raise AlreadyExists('Order already processed. Cannot update.')

        log_id = self.generate_api_logs('order_update', identifier_id, identifier_instance_id)
        authenticate_user_from_through_sso = authenticate_user(self.headers.get('Auth-Token'), self.headers.get('Nodesso-Id'))
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
            'billing_building': clean_string(billing_location.get('building', '')),
            'billing_street': clean_string(billing_location.get('street_name', '')),
            'billing_city': billing_location.get('city'),
            'billing_locality': clean_string(billing_location.get('locality', '')),
            'billing_area_code': billing_location.get('area_code'),
            'billing_state': billing_location.get('state'),
            'billing_country': billing_location.get('country'),
            'billing_label': billing_location.get('label'),
            'shipping_contact_number': shipping_info.get('contact', {}).get('phone'),
            'shipping_email': shipping_info.get('contact', {}).get('email'),
            'shipping_gps': shipping_location.get('gps'),
            'shipping_building': clean_string(shipping_location.get('building', '')),
            'shipping_street': clean_string(shipping_location.get('street_name', '')),
            'shipping_city': shipping_location.get('city'),
            'shipping_locality': clean_string(shipping_location.get('locality', '')),
            'shipping_area_code': shipping_location.get('area_code'),
            'shipping_state': shipping_location.get('state'),
            'shipping_country': shipping_location.get('country'),
            'shipping_label': shipping_location.get('label'),
            'item_id': order_items.get('id'),
            'qty': order_items.get('qty'),
            'price': order_items.get('price'),
            'discount': abs(int(order_items.get('discount') or 0)),
            'taxes': order_items.get('taxes'),
            'order_discount': abs(int((order_info.get('discount') or 0))),
            'packaging_charges': order_info.get('packaging_charges',0),
            'delivery_charges': order_info.get('delivery_charges',0),
            'other_charges': order_info.get('other_charges',0),
            'order_total': order_info.get('order_total',0),
            'payment_mode': payment_info.get('payment_mode'),
            'payment_transaction_id': payment_info.get('payment_transaction_id'),
            'payment_status': payment_info.get('payment_status'),
            'parent_id': log_id,
            'storefront_id': self.params.get('noderetail_order_instance_id')
        }
        for key, value in dict(request_params).items():
            if not value:
                request_params.pop(key)
        try:
            self.coordinator.update_data_in_db_pool(request_params, 'plotch_order_importer_data', [{'col': 'order_id', 'val': identifier_id},
                    {'col': 'storefront_id', 'val': identifier_instance_id}])
        except:
            self.coordinator.update_data_in_db_pool(request_params, 'plotch_order_importer_data', [{'col': 'order_id', 'val': identifier_id},
                    {'col': 'storefront_id', 'val': identifier_instance_id}])

        payment_transaction_id = payment_info.get('payment_transaction_id')
        params = {
            'payment_mode': payment_info.get('payment_mode'),
            'payment_transaction_id': payment_info.get('payment_transaction_id'),
            'payment_status': 1 if payment_info.get('payment_status') == 'paid' else 0
        }
        try:
            self.coordinator.update_data_in_db_pool(params, 'plotch_imported_order_transaction', [{'col': 'payment_transaction_id', 'val': payment_transaction_id}])
        except:
            self.coordinator.update_data_in_db_pool(params, 'plotch_imported_order_transaction', [{'col': 'payment_transaction_id', 'val': payment_transaction_id}])
        return 'success'

    def order_fetch(self):
        identifier_id = self.params.get('order_id')  # posr.order_id
        identifier_instance_id = self.params.get('noderetail_storefront_id')  # posr.storefront_id
        noderetail_account_user_id = self.params.get('noderetail_account_user_id')
        noderetail_order_instance_id = self.params.get('noderetail_order_instance_id')
        order_status = self.params.get('order_status', '')
        created_at_start = self.params.get('order_created_at_date_start', '')
        created_at_end = self.params.get('order_created_at_date_end', '')
        updated_at_start = self.params.get('order_updated_at_date_start', '')
        updated_at_end = self.params.get('order_updated_at_date_end', '')
        page_number = max(int(self.params.get('page_number', 1)), 1)
        page_size = int(self.params.get('page_size', 10))

        log_id = self.generate_api_logs('order_fetch', identifier_id, identifier_instance_id)
        authenticate_user_from_through_sso = authenticate_user(self.headers.get('Auth-Token'),self.headers.get('Nodesso-Id'))

        if page_size or page_number:
            pagination_condition = 'LIMIT {} OFFSET {}'.format(page_size, (page_number - 1) * page_size)
        date_created = ''
        if created_at_start and created_at_end:
            date_created = '''AND poid.created_at BETWEEN '{}' AND '{}' '''.format(created_at_start, created_at_end)
        date_updated = ''
        if updated_at_start and updated_at_end:
            date_updated = '''AND poid.updated_at BETWEEN '{}' AND '{}' '''.format(updated_at_start, updated_at_end)
        get_orders_data = self.coordinator.fetch_order_details(identifier_id, identifier_instance_id, order_status, date_created, date_updated, pagination_condition)

        response_payload = {
            "api_action_status": "success",
            "order_fetch_request_id": None,
            "noderetail_account_user_id": noderetail_account_user_id,
            "noderetail_order_instance_id": noderetail_order_instance_id,
            "orders": []
        }
        if get_orders_data:
            response_payload["order_fetch_request_id"] = get_orders_data[0].get("entity_id")

        for order_data in get_orders_data:
                payload = {
                    "noderetail_order_id": order_data.get("noderetail_order_id"),
                    "network_order_id": order_data.get("ondc_network_order_id"),
                    "client_order_id": identifier_id,
                    "customer_info": {
                        "customer_id": order_data.get("alternate_customer_id"),
                        "noderetail_customer_id": order_data.get("noderetail_customer_id"),
                        "contact": {
                            "phone": order_data.get("phone"),
                            "email": order_data.get("email")
                        }
                    },
                    "billing_info": {
                        "contact": {
                            "phone": order_data.get("billing_contact_number"),
                            "email": order_data.get("billing_email")
                        },
                        "location": {
                            "gps": order_data.get("billing_gps"),
                            "building": order_data.get("billing_building"),
                            "street_name": order_data.get("billing_street"),
                            "locality": order_data.get("billing_locality"),
                            "city": order_data.get("billing_city"),
                            "area_code": order_data.get("billing_area_code"),
                            "state": order_data.get("billing_state"),
                            "country": order_data.get("billing_country"),
                            "label": order_data.get("billing_label")
                        }
                    },
                    "shipping_info": {
                        "contact": {
                            "phone": order_data.get("shipping_contact_number"),
                            "email": order_data.get("shipping_email")
                        },
                        "location": {
                            "gps": order_data.get("shipping_gps"),
                            "building": order_data.get("shipping_building"),
                            "street_name": order_data.get("shipping_street"),
                            "locality": order_data.get("shipping_locality"),
                            "city": order_data.get("shipping_city"),
                            "area_code": order_data.get("shipping_area_code"),
                            "state": order_data.get("shipping_state"),
                            "country": order_data.get("shipping_country"),
                            "label": order_data.get("shipping_label")
                        }
                    },
                    "order_info": {
                        "order_items": [
                            {
                                "id": order_data.get("item_id"),
                                "qty": order_data.get("qty"),
                                "price": str(order_data.get("price")),
                                "discount": str(order_data.get("discount")),
                                "taxes": str(order_data.get("taxes"))
                            }
                        ],
                        "discount": str(order_data.get("order_discount")),
                        "packaging_charges": str(order_data.get("packaging_charges")),
                        "delivery_charges": str(order_data.get("delivery_charges")),
                        "other_charges": str(order_data.get("other_charges")),
                        "order_total": str(order_data.get("order_total"))
                    },
                    "payment_info": {
                        "payment_mode": order_data.get("payment_mode"),
                        "payment_transaction_id": order_data.get("payment_transaction_id"),
                        "payment_status": order_data.get("payment_status")
                    },
                    "fulfillments": [
                        {
                            "fulfillment_id": order_data.get("fulfillment_id"),
                            "fulfillment_mode": order_data.get("fulfillment_mode"),
                            "fulfillment_status": order_data.get("fulfillment_status"),
                            "fulfillment_courier": order_data.get("fulfillment_courier"),
                            "fulfillment_tracking": order_data.get("fulfillment_tracking"),
                            "fulfillment_update_time": order_data.get("fulfillment_update_time")
                       }
                    ]
                }
                response_payload["orders"].append(payload)
        return response_payload

    def order_status(self):
        rs_order_number_list = []
        rs_order_id_list = []
        orders = self.params.get('orders')
        for order in orders:
            order_number = order.get('order_id')  # rs.order_number
            order_id = order.get('noderetail_order_id')  # rs.order_id
            noderetail_account_user_id = order.get('noderetail_account_user_id')  # poid.user_instance_id
            noderetail_order_instance_id = order.get('noderetail_order_instance_id')  # storefront_id
            storefront_id = order.get('noderetail_storefront_id')

            if not (order_number and order_id and storefront_id):
                raise BadRequest('order_id, noderetail_order_id, noderetail_storefront_id Are Mandatory')

            if order_number:
                rs_order_number_list.append(order_number)
            if order_id:
                rs_order_id_list.append(order_id)

            log_id = self.generate_api_logs('order_status', order_number, storefront_id)
            authenticate_user_from_through_sso = authenticate_user(self.headers.get('Auth-Token'), self.headers.get('Nodesso-Id'))

            order_status_data = self.coordinator.get_order_status(rs_order_number_list, storefront_id, rs_order_id_list)
            status_details = self.coordinator.get_status(rs_order_number_list, storefront_id)

            response_payload = []
            if order_status_data:
                for response in order_status_data:
                    status_detail = next(
                        (detail for detail in status_details if detail['order_id'] == response.get('order_number')),
                        None)
                    payload = {
                        "order_id": response.get('order_number'),
                        "noderetail_order_id": response.get('rs_order_id'),
                        "is_order_created": True if response.get('is_order_created') == 1 else False,
                        "noderetail_account_user_id": '',
                        "noderetail_order_instance_id": noderetail_order_instance_id,
                        "is_order_active": True,
                        "order_status": status_detail['order_status'],
                        "order_created_time": response.get('order_created_time'),
                        "order_update_time": response.get('order_update_time'),
                        "order_items_info": []
                    }
                    for details in status_details:
                        item_payload = {
                            "item_order_id": response.get('item_order_id'),
                            "item_id": int(response.get('item_id')),
                            "noderetail_item_id": response.get('noderetail_item_id'),
                            "fulfillments": [{
                                "fulfillment_id": details.get('fulfillment_id'),
                                "fulfillment_mode": details.get('fulfillment_mode'),
                                "fulfillment_status": details.get('fulfillment_status'),
                                "fulfillment_courier": details.get('fulfillment_courier'),
                                "fulfillment_tracking": details.get('fulfillment_tracking'),
                                "fulfillment_update_time": details.get('fulfillment_update_time')
                            }],
                            "refund_status": details.get('refund_status')
                        }
                        payload["order_items_info"].append(item_payload)
                    response_payload.append(payload)
        return {"api_action_status": "success", "orders_status": response_payload}

