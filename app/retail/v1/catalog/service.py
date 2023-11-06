from config import Config
from datetime import datetime
import json
from app.common_utils import get_current_datetime
from app.exceptions import AuthMissing
from app.retail.v1.catalog.catalog_coordinator import CatalogCoordinator
from app.common_utils import validate_jwt
import math

class CatalogService:
    def __init__(self, params, headers):
        self.params = params
        self.headers = headers
        self.coordinator = CatalogCoordinator()
    
    def authenticate_user(self):
        jwt_token = self.headers.get('Auth-Token')
        nodesso_id = self.headers.get('Nodesso-Id')
        if not jwt_token:
            raise AuthMissing('Auth token is missing')
        payload = {
            'nodesso_id': nodesso_id,
            'auth_token': jwt_token
        }
        validate_jwt(payload)
    
    def extract_image_url(self, image_params):
        if 'http' in image_params:
            return image_params
        else:
            return Config.IMAGE_BASE_URL_FOR_CDN_AZ + image_params

    def extract_image_from_params(self, product_data, other_params):
        image_list = list()
        if product_data.get('main_image') or other_params.get('main_image'):
            main_image = product_data.get('main_image') or other_params.get('main_image')
            image_list.append(self.extract_image_url(main_image))
        if product_data.get('image1') or other_params.get('image1'):
            main_image = product_data.get('image1') or other_params.get('image1')
            image_list.append(self.extract_image_url(main_image))
        if product_data.get('image2') or other_params.get('image2'):
            main_image = product_data.get('image2') or other_params.get('image2')
            image_list.append(self.extract_image_url(main_image))
        if product_data.get('image3') or other_params.get('image3'):
            main_image = product_data.get('image3') or other_params.get('image3')
            image_list.append(self.extract_image_url(main_image))
        if product_data.get('image4') or other_params.get('image4'):
            main_image = product_data.get('image4') or other_params.get('image4')
            image_list.append(self.extract_image_url(main_image))
        return image_list

    def fetch_catalog(self):
        self.authenticate_user()
        plotch_instance = self.coordinator.get_single_data_from_db('plotch_instance', 
                                                                   [{'col':'instance_id', 'val': self.params.get('noderetail_storefront_id')}, {'col':'instance_type_id', 'val': 46}])
        instance_details = plotch_instance.get('instance_details')
        try: 
            catalog = json.loads(instance_details).get('catalog')
        except :
            catalog = ""
        crs_catalog = self.coordinator.get_single_data_from_db('crs_catalog', [{'col':'id', 'val': catalog}])
        catalog_id = crs_catalog.get('catalog_id')
        condition_str = ''
        if self.params.get('noderetail_provider_id'):
            condition_str += ''' and cp.seller_id = "{}" '''.format(self.params.get('noderetail_provider_id'))
        if self.params.get('noderetail_category'):
            condition_str += ''' and cp.category_name = "{}" '''.format(self.params.get('noderetail_category'))
        if self.params.get('noderetail_category_id'):
            condition_str += ''' and cp.category_id = {} '''.format(self.params.get('noderetail_category_id'))
        if self.params.get('noderetail_agg_id'):
            retail_user_instance_data = self.coordinator.get_single_data_from_db('retail_user_instance', [{'col':'user_name', 'val': self.params.get('noderetail_agg_id','')}], ['vendor_id'])
            if retail_user_instance_data:
                condition_str += ''' and cp.vendor_id = "{}" '''.format(retail_user_instance_data.get('vendor_id', ''))
        noderetail_catalog_id = ''
        if catalog_id and self.params.get('noderetail_catalog_id'):
            noderetail_catalog_id = catalog_id
        joined_result = self.coordinator.fetch_catalog_data(catalog_id, condition_str, self.params.get('page_size'), self.params.get('page_number'))
        items = []
        domain_details = self.coordinator.get_single_data_from_db('plotch_domains', [{'col':'instance_id', 'val': self.params.get('noderetail_storefront_id','')}], ['primary_domain'])
        for product_data in joined_result:
            try:
                other_params = json.loads(product_data.get('other_params'), strict=False)
            except:
                other_params = dict()
            images = self.extract_image_from_params(product_data, other_params)
            response =  {
                        "item_id": product_data.get('alternate_product_id', '') or product_data.get('ondc_item_id', ''),
                        "provider_id": product_data.get('seller_id', '') or product_data.get('vendor_id'),
                        "noderetail_account_user_id": self.params.get('noderetail_account_user_id', ''),
                        "noderetail_catalog_id": noderetail_catalog_id,
                        "noderetail_storefront_id": self.params.get('noderetail_storefront_id', ''),
                        "noderetail_item_id": str(int(product_data.get('product_id', ''))) if product_data.get('product_id', '') else '',
                        "noderetail_provider_id":  product_data.get('seller_id', '') or product_data.get('vendor_id'),
                        "noderetail_category": product_data.get('category_name'),
                        "noderetail_category_id": product_data.get('category_id'),
                        "noderetail_product_url": "https://"+ domain_details.get('primary_domain', '')+ "/product/s/" + str(int(product_data.get('product_id', ''))) if product_data.get('product_id', '') else '',
                        "product_type": "simple",
                        "name": product_data.get('product_name', ''),
                        "description": product_data.get('description', ''),
                        "short_description": "",
                        "category": product_data.get('category_name', ''),
                        "variant_group_id": product_data.get('variant_group_id', ''),
                        "variant": product_data.get('variant',''),
                        "location_id": [],
                        "inventory_info": {
                            "qty": str(product_data.get('inventory_qty')),
                            "min_qty": "",
                            "max_qty": "",
                            "is_in_stock": "1"
                        },
                        "pricing_info": {
                            "mrp":  str(product_data.get('mrp', '')),
                            "sale_price":  str(product_data.get('sales_price', '')),
                            "discount_start_date": str(product_data.get('discount_start_date', '')),
                            "discount_end_date":  str(product_data.get('discount_end_date', '')),
                            "discounted_price":  str(product_data.get('discounted_price', '')),
                        },
                        "provider_info": {
                            "store_name": product_data.get('vendor_name') or other_params.get('vendor_name', ''),
                            "brand_logo": "",
                            "long_desc": other_params.get('long_desc', ''),
                            "short_desc": other_params.get('short_desc', ''),
                            "store_images": [],
                            "fssai_license_num": product_data.get('fssai_number', ''),
                            "serviceability": [],
                            "locations": []
                            },
                        "images": images,
                        "attributes": {}}
            keys_to_be_removed = ["provider_id", "circle_radius", "bpp_uri", "locations", "long_desc", "storefront_timing", 
                                  "short_desc", "city_code", "product_hash", "ntags", "days", "bpp_id"]
            other_params = {key: value for key, value in other_params.items() if key not in keys_to_be_removed}
            response.get('attributes').update(other_params)
            items.append(response)
        return {'items':items}