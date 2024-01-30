from config import Config
from app.exceptions import InvalidAuth
from app.base_coordinator import BaseCoordinator,SSOCoordinator


class VendorCoordinator(BaseCoordinator):

    def __init__(self):
        super(VendorCoordinator, self).__init__()
        self.sso_coordinator =SSOCoordinator()

    def validate_jwt(self, payload):
        response = self.sso_coordinator.post('/verifyHeader', payload=payload, headers={'Authorization':Config.Authorization})
        if response.status_code == 200:
            return response.json().get('d')
        raise InvalidAuth('Invalid auth token.')

    def fetch_provider_details(self, identifier_id):
        query = '''select * from plotch_vendor_importer_data where provider_id ='{}' '''.format(identifier_id)
        return self.mysql_conn.query_db_one(query)

