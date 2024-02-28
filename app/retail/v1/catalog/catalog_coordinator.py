from config import Config
from app.exceptions import InvalidAuth
from app.base_coordinator import BaseCoordinator, SSOCoordinator


class CatalogCoordinator(BaseCoordinator):
    def __init__(self):
        super(CatalogCoordinator, self).__init__()
        self.sso_coordinator = SSOCoordinator()
        self.mysql_conn = Config.MYSQL_CONN
        self.mysql_conn_pool = Config.MYSQL_CONN_POOLING
    
    def fetch_catalog_data(self, catalog_id, condition_str, limit, current_page):
        query = """select cp.*, pisi.qty as inventory_qty from crs_products cp 
                    LEFT JOIN plotch_inventory_summary_item pisi ON cp.product_id=pisi.product_id 
                    where cp.catalog_id='{}' {} 
                    order by id desc limit {} offset {}""".format(catalog_id, condition_str, limit, int(limit)*(int(current_page)-1))
        return self.mysql_conn_pool.query_db_pool(query=query)

    def get_catgory_details(self, ondc_domain, pagination_cond):
        query = '''SELECT cc.parent_id, cc.name, cc.category_id, cc.ondc_domain, cc.level from crs_category cc
        where ondc_domain = '{}' {} '''.format(ondc_domain, pagination_cond)
        return self.mysql_conn_pool.query_db_pool(query)

    def get_source_node(self, category_ids):
        query = '''SELECT source_node FROM plotch_linkage WHERE target_node IN ({}) 
        AND source_module_id = 23 AND target_module_id =15 AND status !=2;'''.format(str(category_ids)[1:-1])
        return self.mysql_conn_pool.query_db_pool(query)

    def attribute_details(self, attribute_set_values):
        query = '''SELECT distinct m.attribute_id, m.attribute_name, m.attribute_value, m.is_required FROM plotch_attribute_sets_details d 
        JOIN plotch_product_attribute_master m ON m.attribute_id = d.attribute_id AND m.status = 1 LEFT 
        JOIN plotch_product_attribute_value ppav ON m.attribute_id = ppav.attribute_id 
        WHERE d.attribute_set_id IN ({}) '''.format(str(attribute_set_values)[1:-1])
        return self.mysql_conn_pool.query_db_pool(query)

    def get_category_parent_details(self, parent_id):
        query = '''SELECT name, level FROM crs_category WHERE entity_id = {} '''.format(parent_id)
        return self.mysql_conn_pool.query_db_pool(query)
