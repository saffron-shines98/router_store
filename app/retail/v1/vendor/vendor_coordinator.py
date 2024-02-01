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

    def get_user_instance_id(self, noderetail_storefront_id):
        query = '''SELECT user_instance_id from retail_user_instance WHERE storefront_id = '{}' '''.format(noderetail_storefront_id)
        return self.mysql_conn.query_db(query)

    def fetch_provider_details(self, identifier_id, user_instance_ids, status_f, storename, email_f, phone_f, city_f, state_f):
        user_instance_ids_str = ', '.join(map(str, user_instance_ids))
        query = '''select rui.seller_id, rui.is_active, rui.company_name, rui.email, rui.mobile, rui.pan_no, rui.gstin,
        rui.gps_coordinates, rui.shipping_city, rui.shipping_state, rui.shipping_address, rui.shipping_pincode, rui.account_id,
        rhi.marketplace_logo, rhi.store_detail_description, rhi.store_description, 
        rhi.store_open_days, rhi.store_timing, rhi.name, rhi.email, rhi.mobile, rhi.store_description,
        rhi.image, rhi.fssai, rhi.pan_no, rhi.gstin, rhi.categories, rhi.serviceability_mode, rhi.pickup_radius, rhi.other_params, rhi.account_id,
        psp.account_name, psp.account_no, psp.ifsc_code from retail_user_instance as rui
        JOIN retail_hub_instance as rhi on rui.seller_id = rhi.seller_id
        JOIN plotch_seller_profile as psp on rui.user_instance_id = psp.user_instance_id
        where rui.seller_id = '{}' AND rui.user_instance_id IN({}) {} {} {} {} {} {} '''.format(identifier_id, user_instance_ids_str, status_f, storename, email_f,
        phone_f, city_f, state_f)
        return self.mysql_conn.query_db(query)

