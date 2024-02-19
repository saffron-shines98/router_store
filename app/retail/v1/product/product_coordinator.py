from config import Config
from app.exceptions import InvalidAuth
from app.base_coordinator import BaseCoordinator, SSOCoordinator


class ProductCoordinator(BaseCoordinator):
    def __init__(self):
        super(ProductCoordinator, self).__init__()
        self.sso_coordinator = SSOCoordinator()

    def get_product_status(self, ondc_item_id, email):
        query = '''select cp.ondc_item_id, cp.created_by, cp.account_id, cp.catalog_id, cp.is_active, cp.is_in_stock, 
        pisi.qty, cp.last_es_sync_time, cp.updated_at, pisi.updated_at, rui.email, rui.storefront_id from crs_products cp 
        JOIN plotch_inventory_summary_item pisi on cp.account_id = pisi.account_id 
        JOIN retail_user_instance rui ON rui.account_id = cp.account_id where cp.ondc_item_id = '{}' 
        and rui.email = '{}' limit 1 '''.format(ondc_item_id, email)
        print(query)
        return self.mysql_conn.query_db(query)

    def get_marketplace_details(self, storefront_id):
        query = '''SELECT instance_details, instance_name from plotch_instance where instance_id = '{}' 
        '''.format(storefront_id)
        return self.mysql_conn.query_db_one(query)
