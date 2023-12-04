from config import Config
from app.exceptions import InvalidAuth
from app.base_coordinator import BaseCoordinator, SSOCoordinator
from app.connections import ESUtility


class CatalogCoordinator(BaseCoordinator):
    def __init__(self):
        super(CatalogCoordinator, self).__init__()
        self.sso_coordinator = SSOCoordinator()
        self.mysql_conn = Config.MYSQL_CONN
    
    def fetch_catalog_data(self, catalog_id, condition_str, limit, current_page):
        query = """select cp.*, pisi.qty as inventory_qty from crs_products cp 
                    LEFT JOIN plotch_inventory_summary_item pisi ON cp.product_id=pisi.product_id 
                    where cp.catalog_id='{}' {} 
                    order by id desc limit {} offset {}""".format(catalog_id, condition_str, limit, int(limit)*(int(current_page)-1))
        print(query)
        return self.mysql_conn.query_db(query=query)
    
    def fetch_catalog_data_count(self, catalog_id, condition_str):
        query = """select count(cp.id) as product_count from crs_products cp 
                    LEFT JOIN plotch_inventory_summary_item pisi ON cp.product_id=pisi.product_id 
                    where cp.catalog_id='{}' {} 
                    order by id desc""".format(catalog_id, condition_str)
        print(query)
        return self.mysql_conn.query_db_one(query)
    
    def get_product_count_from_es(self, es_query, index):
        if not es_query.get('query'):
            return dict()
        es_utility = ESUtility(self.es_conn, index.lower(), '_search')
        print(index.lower())
        print(es_query)
        return es_utility.get_total_rows_count(es_query)

