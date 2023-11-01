from config import Config
from app.exceptions import InvalidAuth
from app.base_coordinator import BaseCoordinator, SSOCoordinator


class CatalogCoordinator(BaseCoordinator):
    def __init__(self):
        super(CatalogCoordinator, self).__init__()
        self.sso_coordinator = SSOCoordinator()
        self.mysql_conn = Config.MYSQL_CONN

    def validate_jwt(self, payload):
        response = self.sso_coordinator.post('/verifyHeader', payload=payload, headers={'Authorization':Config.Authorization})
        if response.status_code == 200:
            return response.json().get('d')
        raise InvalidAuth('Invalid auth token.')
    
    def fetch_catalog_data(self, catalog_id, condition_str, limit, current_page):
        query = f"""select cp.*, pisi.qty as inventory_qty from crs_products cp 
                    LEFT JOIN plotch_inventory_summary_item pisi 
                    ON cp.product_id=pisi.product_id 
                    where cp.catalog_id='{catalog_id}' AND pisi.qty>0 {condition_str} limit {limit} offset {int(limit)*int(current_page)-1};"""
        return self.mysql_conn.query_db(query=query)

