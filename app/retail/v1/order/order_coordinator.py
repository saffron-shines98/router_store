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

    def fetch_order_details(self, identifier_id, identifier_instance_id, rs_order_id, date_created, date_updated, pagination_condition):
        query = ''' SELECT poid.*, rs.order_id as rs_order_id, 
        rsi.ondc_order_id AS network_order_id, poid.alternate_customer_id AS noderetail_customer_id,
        rsi.vendor_order_id AS fulfilment_id, 
        rsh.status AS fulfillment_mode, rsh.courier_partner AS fulfilment_courier, 
        rsh.tracking_number AS fulfillment_tracking, rsh.updated_at AS fulfillment_update_time
        FROM plotch_order_importer_data as poid
        JOIN retail_sales as rs on rs.order_number = poid.order_id
        JOIN retail_sales_item AS rsi ON rs.order_id = rsi.order_id 
        JOIN retail_shipments AS rsh ON rsi.shipment_id = rsh.entity_id 
        JOIN retail_shipment_status AS rss ON rsi.status = rss.entity_id
        where poid.order_id = '{}' and poid.storefront_id = '{}' and rs.order_id='{}' {} {} {}
        '''.format(identifier_id, identifier_instance_id, rs_order_id, date_created, date_updated, pagination_condition)
        return self.mysql_conn_pool.query_db_pool(query)

    def get_fetch_details(self, identifier_id, identifier_instance_id, order_status):
        query= '''SELECT posr.order_id, posr.fulfilment_status AS fulfillment_status FROM plotch_order_status_request as posr 
        JOIN retail_sales as rs on rs.order_number = posr.order_id id WHERE posr.storefront_id = '267986' AND 
        posr.order_status = '{}' and rs.order_id = '{}' order by 1 desc limit 1 '''
        query ='''SELECT order_id, fulfilment_status FROM plotch_order_status_request 
         WHERE order_id = '{}' AND storefront_id = '{}' AND order_status = '{}' order by 1 desc limit 1 
         '''.format(identifier_id, identifier_instance_id, order_status)
        return self.mysql_conn_pool.query_db_one_pool(query)

    def get_order_status(self, order_id_list, identifier_instance_id, rs_order_id_list):
        query = '''SELECT rs.order_number, rs.order_id as rs_order_id, poid.user_instance_id AS noderetail_account_user_id, 
        rs.created_by AS is_order_created,   
        rs.created_at AS order_created_time, rs.updated_at AS order_update_time 
        FROM plotch_order_importer_data AS poid
        JOIN retail_sales as rs on rs.order_number = poid.order_id
        JOIN retail_sales_item AS rsi ON rs.order_id = rsi.order_id
        JOIN retail_shipments AS rsh ON rsi.shipment_id = rsh.entity_id 
        JOIN retail_shipment_status AS rss ON rsi.status = rss.entity_id 
        where poid.order_id IN ({}) AND poid.storefront_id = '{}' and rs.order_id IN ({})
        '''.format(str(order_id_list)[1:-1], identifier_instance_id, str(rs_order_id_list)[1:-1])
        return self.mysql_conn_pool.query_db_pool(query)

    def get_status(self, order_id_list, identifier_instance_id):
        query = '''SELECT po.order_id, po.order_status, rs.order_id as rs_order_id, po.refund_status, po.fulfilment_status AS fulfillment_status, rsi.vendor_order_id AS fulfilment_id, 
        rsh.transaction_type AS fulfillment_mode, rsh.courier_partner AS fulfilment_courier, rsh.tracking_number AS fulfillment_tracking, 
        po.created_at AS fulfillment_update_time,
        rsi.order_item_id AS item_order_id, rsi.product_id AS item_id, rsi.ondc_item_id AS noderetail_item_id 
        FROM plotch_order_status_request as po 
        JOIN retail_sales as rs on rs.order_number = po.order_id  
        JOIN retail_sales_item AS rsi ON rs.order_id = rsi.order_id 
        JOIN retail_shipments AS rsh ON rsi.shipment_id = rsh.entity_id WHERE po.order_id IN ({}) 
        and po.storefront_id = '{}' '''.format(str(order_id_list)[1:-1], identifier_instance_id)
        return self.mysql_conn_pool.query_db_pool(query)
