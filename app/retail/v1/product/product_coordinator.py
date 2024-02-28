from config import Config
from app.exceptions import InvalidAuth
from app.base_coordinator import BaseCoordinator, SSOCoordinator


class ProductCoordinator(BaseCoordinator):
    def __init__(self):
        super(ProductCoordinator, self).__init__()
        self.sso_coordinator = SSOCoordinator()

    def get_account_id(self, email):
        query = '''SELECT account_id from retail_user_instance where email = '{}' limit 1'''.format(email)
        return self.mysql_conn_pool.query_db_one_pool(query)

    def get_product_status(self, ondc_item_id, account_id):
        query = '''select cp.catalog_id, cp.ondc_item_id, cp.created_by, cp.is_active, 
                pisi.qty, cp.updated_at, pisi.updated_at from crs_products cp
                JOIN plotch_inventory_summary_item pisi on cp.product_id = pisi.product_id 
                where cp.ondc_item_id = '{}' and cp.account_id = '{}' '''.format(ondc_item_id, account_id)
        return self.mysql_conn_pool.query_db_pool(query)

    def get_storefront_id(self, catalog_id):
        query = '''SELECT pl.target_node as catalog_id, pl.source_node as storefront_id from plotch_linkage pl 
        join crs_catalog cc on cc.id = pl.target_node 
        where pl.source_module_id = 46 and pl.target_module_id = 3 and cc.catalog_id = '{}' '''.format(catalog_id)
        return self.mysql_conn_pool.query_db_one_pool(query)

    def get_marketplace_details(self, storefront_id):
        query = '''SELECT instance_details, instance_name from plotch_instance where instance_id = '{}' and
        status = 1 and instance_type_id = 46 '''.format(storefront_id)
        return self.mysql_conn_pool.query_db_one_pool(query)

    def get_marketplace_name(self, marketplace_instance_id):
        query = '''select marketplace_name from plotch_marketplaces where marketplace_instance_id = '{}' 
        '''.format(marketplace_instance_id)
        return self.mysql_conn_pool.query_db_one_pool(query)

