from config import Config
from app.exceptions import InvalidAuth
from app.base_coordinator import BaseCoordinator,SSOCoordinator


class OrderCoordinator(BaseCoordinator):

    def __init__(self):
        super(OrderCoordinator, self).__init__()
        self.sso_coordinator =SSOCoordinator()

    def validate_jwt(self, payload):
        response = self.sso_coordinator.post('/verifyHeader', payload=payload, headers={'Authorization':Config.Authorization})
        if response.status_code == 200:
            return response.json().get('d')
        raise InvalidAuth('Invalid auth token.')

    def get_account_id(self, customer_instance):
        query = '''select account_id from retail_customer where customer_instance = '{}' limit 1'''.format(customer_instance)
        return self.mysql_conn_pool.query_db_one_pool(query)

    def check_order_duplicacy(self, identifier, identifier_instance):
        query = '''select entity_id from plotch_order_importer_data where order_id = '{}' and storefront_id = '{}' limit 1'''.format(identifier, identifier_instance)
        return self.mysql_conn_pool.query_db_one_pool(query)

    def customer_check_duplicacy(self, identifier_instance, identifier):
        query = '''select entity_id from plotch_customer_importer_data where alternate_customer_id = '{}' and customer_instance_id = '{}' limit 1'''.format(identifier, identifier_instance)
        return self.mysql_conn_pool.query_db_one_pool(query)

    def check_order_status(self, identifier, identifier_instance):
        query = '''SELECT status FROM plotch_order_importer_data WHERE status != 0 AND order_id = '{}' and storefront_id = '{}' limit 1'''.format(identifier, identifier_instance)
        return self.mysql_conn_pool.query_db_one_pool(query)

    def fetch_order_details(self, identifier_instance_id, order_num, order_id, date_created, date_updated, pagination_condition):
        query = ''' SELECT rs.order_id as rs_order_id, rs.order_number, rs.customer_id, rc.alternate_customer_id, 
        rc.mobile as rc_mobile, rc.email as rc_email, rsi.order_item_id, rsi.ondc_order_id AS network_order_id, rsi.qty, rsi.mrp, rsi.item_discount_amount, 
        rsi.shipping_amount, rsi.shipping_amount, rs.discount_amount, rs.subtotal, rs.payment_mode, rs.checkout_id, payment_status, rsi.other_charges  
        FROM retail_sales as rs 
        JOIN retail_sales_item AS rsi ON rs.order_id = rsi.order_id 
        JOIN retail_customer as rc ON rs.customer_id = rc.customer_id 
        JOIN retail_shipments AS rsh ON rsi.shipment_id = rsh.entity_id
        where rs.storefront_id = '{}' {} {} {} {} {}
        '''.format(identifier_instance_id, order_num, order_id, date_created, date_updated, pagination_condition)
        return self.mysql_conn_pool.query_db_pool(query)

    def get_customer_address(self, address_type, identifier_instance_id, order_num, order_id, pagination_condition):
        query = '''SELECT rsa.* from retail_sales_address as rsa JOIN retail_sales AS rs ON rs.order_id = rsa.order_id 
        where rsa.address_type = '{}' and rs.storefront_id = '{}' {} {} {} '''.format(address_type, identifier_instance_id, order_num, order_id, pagination_condition)
        return self.mysql_conn_pool.query_db_one_pool(query)

    def get_fulfilment_details(self, identifier_instance_id, order_num, order_status, order_id, pagination_condition):
        query= '''SELECT rs.order_number, po.fulfilment_status AS fulfillment_status, po.created_at, 
        rsi.vendor_order_id, rsh.transaction_type, rsh.courier_partner, rsh.tracking_number  
        FROM plotch_order_status_request as po 
        JOIN retail_sales as rs on rs.order_number = po.order_id  
        JOIN retail_sales_item AS rsi ON rs.order_id = rsi.order_id 
        JOIN retail_shipments AS rsh ON rsi.shipment_id = rsh.entity_id WHERE rs.storefront_id = '{}' {} {} {} {}
        '''.format(identifier_instance_id, order_num, order_status, order_id, pagination_condition)
        return self.mysql_conn_pool.query_db_pool(query)

    def get_order_status(self, order_id_list, identifier_instance_id, rs_order_cond):
        query = '''SELECT rs.order_number, rs.order_id as rs_order_id, rs.created_by AS is_order_created,   
        rs.created_at AS order_created_time, rs.updated_at AS order_update_time, 
        rsi.order_item_id AS item_order_id, rsi.product_id AS item_id, rsi.ondc_item_id AS noderetail_item_id 
        FROM retail_sales as rs
        JOIN retail_sales_item AS rsi ON rs.order_id = rsi.order_id
        JOIN retail_shipments AS rsh ON rsi.shipment_id = rsh.entity_id 
        where rs.order_number IN ({}) AND rs.storefront_id = '{}' {} 
        '''.format(str(order_id_list)[1:-1], identifier_instance_id, rs_order_cond)
        return self.mysql_conn_pool.query_db_pool(query)

    def get_status(self, order_id_list, identifier_instance_id):
        query = '''SELECT po.order_id, po.order_status, rs.order_id as rs_order_id, po.refund_status, po.fulfilment_status AS fulfillment_status, rsi.vendor_order_id AS fulfilment_id, 
        rsh.transaction_type AS fulfillment_mode, rsh.courier_partner AS fulfilment_courier, rsh.tracking_number AS fulfillment_tracking, 
        po.created_at AS fulfillment_update_time 
        FROM plotch_order_status_request as po 
        JOIN retail_sales as rs on rs.order_number = po.order_id  
        JOIN retail_sales_item AS rsi ON rs.order_id = rsi.order_id 
        JOIN retail_shipments AS rsh ON rsi.shipment_id = rsh.entity_id WHERE rs.order_number IN ({}) 
        and rs.storefront_id = '{}' '''.format(str(order_id_list)[1:-1], identifier_instance_id)
        return self.mysql_conn_pool.query_db_pool(query)
