from config import Config
from app.exceptions import InvalidAuth
from app.base_coordinator import BaseCoordinator,SSOCoordinator


class FulfillmentCoordinator(BaseCoordinator):

    def __init__(self):
        super(FulfillmentCoordinator, self).__init__()
        self.sso_coordinator =SSOCoordinator()

    def validate_jwt(self, payload):
        response = self.sso_coordinator.post('/verifyHeader', payload=payload, headers={'Authorization':Config.Authorization})
        if response.status_code == 200:
            return response.json().get('d')
        raise InvalidAuth('Invalid auth token.')

    def get_account_id(self, noderetail_storefront_id, noderetail_account_user_id):
        query = '''SELECT account_id from retail_user_instance where storefront_id = {} 
        and email = '{}' '''.format(noderetail_storefront_id, noderetail_account_user_id)
        return self.mysql_conn_pool.query_db_one_pool(query)

    def get_fulfillment_status(self, order_id, account_id, noderetail_storefront_id):
        query = '''SELECT rss.status_label, rsh.logistic_order_id, rsh.transaction_type,
        rsh.courier_partner, rsh.tracking_number, rsh.updated_at 
        FROM retail_shipments rsh 
        JOIN retail_sales_item as rsi on rsh.entity_id = rsi.shipment_id
        JOIN retail_sales as rs on rs.order_id = rsi.order_id
        LEFT JOIN retail_shipment_status AS rss ON rss.entity_id = rsh.status 
        WHERE rs.order_number = '{}' AND rsh.account_id = '{}' and rs.storefront_id = {} 
        '''.format(order_id, account_id, noderetail_storefront_id)
        return self.mysql_conn.query_db(query)


