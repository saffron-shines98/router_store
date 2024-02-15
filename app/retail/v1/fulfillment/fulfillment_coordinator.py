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

    def get_fulfillment_status(self, order_id, noderetail_storefront_id, fulfillment_id):
        query = '''SELECT nfi.fulfillment_id, nfi.fulfillment_mode, nfi.fulfillment_status, nfi.fulfillment_courier,
        nfi.fulfillment_tracking, nfi.fulfillment_update_time, nfi.created_at FROM noderetail_fulfillment_item as nfi 
        JOIN noderetail_fulfillment as nf on nf.entity_id = nfi.parent_id 
        WHERE nf.order_id = '{}' AND nf.noderetail_storefront_id = '{}' and nfi.fulfillment_id = '{}' 
        '''.format(order_id, noderetail_storefront_id, fulfillment_id)
        return self.mysql_conn.query_db(query)
