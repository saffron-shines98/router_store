from config import Config
from app.exceptions import InvalidAuth
from app.base_coordinator import BaseCoordinator, SSOCoordinator


class CatalogCoordinator(BaseCoordinator):
    def __init__(self):
        super(CatalogCoordinator, self).__init__()
        self.sso_coordinator = SSOCoordinator()
        self.mysql_conn = Config.MYSQL_CONN
    
    def fetch_catalog_data(self, catalog_id, condition_str, limit, current_page):
        query = """select cp.*, pisi.qty as inventory_qty from crs_products cp 
                    LEFT JOIN plotch_inventory_summary_item pisi ON cp.product_id=pisi.product_id 
                    where cp.catalog_id='{}' AND pisi.qty>0 {} 
                    order by id desc limit {} offset {}""".format(catalog_id, condition_str, limit, int(limit)*int(current_page)-1)
        return self.mysql_conn.query_db(query=query)
