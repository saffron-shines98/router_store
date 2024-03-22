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
        query = '''SELECT user_instance_id from retail_user_instance WHERE storefront_id = '{}' '''.format(
            noderetail_storefront_id)
        return self.mysql_conn_pool.query_db_pool(query)

    def fetch_provider_details(self, identifier_id, user_instance_ids, status_f, storename, email_f, phone_f, city_f, state_f):
        query = '''select rui.seller_id, rui.is_active, rui.company_name, rui.email, rui.mobile, rui.pan_no, rui.gstin,
        rui.gps_coordinates, rui.city, rui.state, rui.address, rui.pincode, rui.account_id,
        rhi.marketplace_logo, rhi.store_detail_description, rhi.store_description, 
        rhi.store_open_days, rhi.store_timing, rhi.name, rhi.email, rhi.mobile, rhi.store_description,
        rhi.image, rhi.fssai, rhi.pan_no, rhi.gstin, rhi.categories, rhi.serviceability_mode, rhi.pickup_radius, rhi.other_params, rhi.account_id,
        psp.contact_name, psp.account_name, psp.account_no, psp.ifsc_code, ca.account_type, 
        pms.entity_id as pms_entity_id, pms.hub_instance_id as marketplace_id,pms.status as marketplace_approved,
        ca.account_id as ca_account_id
        from retail_user_instance as rui
        JOIN retail_hub_instance as rhi on rui.account_id = rhi.account_id
        JOIN plotch_seller_profile as psp on rui.user_instance_id = psp.user_instance_id
        JOIN crs_accounts as ca on rui.account_id = ca.account_id
        LEFT JOIN  plotch_marketplace_subscription as pms on pms.user_instance_id= rui.user_instance_id
        where rui.seller_id = '{}' AND rui.user_instance_id IN({}) {} {} {} {} {} {} '''.format(identifier_id, str(user_instance_ids)[1:-1], status_f, storename, email_f,
        phone_f, city_f, state_f)
        return self.mysql_conn_pool.query_db_pool(query)

    def count_crs_products(self):
        query = '''SELECT COUNT(*) AS num_items_live FROM crs_products as cp 
        JOIN retail_user_instance AS rui on cp.seller_id = rui.seller_id'''
        return self.mysql_conn_pool.query_db_pool(query)

    def fetch_vender_status(self, provider_id, user_instance_ids):
        query = '''SELECT seller_id, is_active from retail_user_instance AS rui WHERE seller_id = '{}' AND 
        user_instance_id IN({}) '''.format(provider_id, str(user_instance_ids)[1:-1])
        return self.mysql_conn_pool.query_db_pool(query)

    def check_provider_status(self, provider_id, noderetail_storefront_id):
        query = '''SELECT status FROM plotch_vendor_importer_data WHERE status != 0 AND provider_id = '{}' 
        and noderetail_storefront_id = '{}' '''.format(provider_id, noderetail_storefront_id)
        return self.mysql_conn_pool.query_db_one_pool(query)
