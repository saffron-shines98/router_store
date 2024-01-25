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
        return self.mysql_conn.query_db_one(query)

    def check_order_duplicacy(self, identifier, identifier_instance):
        query = '''select entity_id from plotch_order_importer_data where order_id = '{}' and storefront_id = '{}' limit 1'''.format(identifier, identifier_instance)
        return self.mysql_conn.query_db_one(query)

    def customer_check_duplicacy(self, identifier_instance, identifier):
        query = '''select entity_id from plotch_customer_importer_data where alternate_customer_id = '{}' and customer_instance_id = '{}' limit 1'''.format(identifier, identifier_instance)
        return self.mysql_conn.query_db_one(query)

    def fetch_order_details(self, identifier_id, identifier_instance_id, order_status, pagination_condition):
        query = ''' SELECT poid.*, poid.order_id AS noderetail_order_id, 
        rsi.ondc_order_id AS network_order_id, poid.alternate_customer_id AS noderetail_customer_id,
        rsi.ondc_order_id AS network_order_id, posr.order_id AS client_order_id, rsi.vendor_order_id AS fulfilment_id, 
        rsh.status AS fulfillment_mode, rsh.courier_partner AS fulfilment_courier, posr.fulfilment_status AS fulfillment_status,
        rsh.tracking_number AS fulfillment_tracking, rsh.updated_at AS fulfillment_update_time
        FROM plotch_order_status_request AS posr 
        JOIN retail_sales as rs on rs.order_number = posr.order_id
        JOIN plotch_order_importer_data as poid on posr.order_id = poid.order_id
        JOIN retail_sales_item AS rsi ON rs.order_id = rsi.order_id 
        JOIN retail_shipments AS rsh ON rsi.shipment_id = rsh.entity_id 
        JOIN retail_shipment_status AS rss ON rsi.status = rss.entity_id
        where posr.order_id = '{}' and posr.storefront_id = '{}' and posr.order_status = '{}' {}
        '''.format(identifier_id, identifier_instance_id, order_status, pagination_condition)
        return self.mysql_conn.query_db(query)
