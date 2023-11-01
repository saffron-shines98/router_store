from config import Config
from datetime import datetime
import json
from app.common_utils import get_current_datetime
from app.exceptions import AuthMissing
from app.retail.v1.catalog.catalog_coordinator import CatalogCoordinator
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
        self.coordinator.validate_jwt(payload)

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
        crs_products_count = self.coordinator.get_single_data_from_db('crs_products', [{'col':'catalog_id', 'val': catalog_id}], ['count(1) as count'])
        condition_str = ''
        if self.params.get('noderetail_provider_id'):
            condition_str += ''' and cp.vendor_id = "{}" '''.format(self.params.get('noderetail_provider_id'))
        if self.params.get('noderetail_category'):
            condition_str += ''' and cp.category_name = "{}" '''.format(self.params.get('noderetail_category'))
        if self.params.get('noderetail_category_id'):
            condition_str += ''' and cp.category_id = {} '''.format(self.params.get('noderetail_category_id'))
        joined_result = self.coordinator.fetch_catalog_data(catalog_id, condition_str, self.params.get('page_size', 10), self.params.get('page_number', 1))

        items = []
        for product_data in joined_result:
            try:
                other_params = json.loads(product_data.get('other_params'), strict=False)
            except:
                other_params = dict()
            response =  {
                        "item_id": product_data.get('ondc_item_id', ''),
                        "provider_id": product_data.get('seller_id', ''),
                        "noderetail_account_user_id": product_data.get('account_id', ''),
                        "noderetail_catalog_id": product_data.get('catalog_id', ''),
                        "noderetail_storefront_id": self.params.get('noderetail_storefront_id', ''),
                        "noderetail_item_id": "",
                        "noderetail_provider_id": "",
                        "noderetail_category": product_data.get('category_name'),
                        "noderetail_category_id": product_data.get('category_id'),
                        "noderetail_product_url": "https://www.craftsvilla.com/product/" + str(product_data.get('product_id', '')),
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
                            "min_qty": "10",
                            "max_qty": "1",
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
                            "store_name": "",
                            "brand_logo": "",
                            "long_desc": "",
                            "short_desc": "",
                            "store_images": [
                            "string-image-url"
                            ],
                            "fssai_license_num": "",
                            "serviceability": [
                            {
                                "mode": "hyperlocal/pincode/pan-india",
                                "radius": "number",
                                "unit": "km"
                            }
                            ],
                            "locations": [
                            {
                                "id": "",
                                "gps": "",
                                "type": "billing/shipping",
                                "address": {
                                "city": "",
                                "state": "",
                                "street": "",
                                "area_code": "",
                                "locality": ""},
                                "schedule": {
                                "open_days": "1,2,3,4,5,6,7",
                                "open_hours": [
                                    {
                                    "start_time": "",
                                    "end_time": ""
                                    }]}}]
                        },
                        "images": [
                        ],
                        "attributes": {
                            "brand": "","color": "","size": "","gender": "","pattern": "","material": "",
                            "occasion": "","season": "","trend": "","features": "","material_finish": "",
                            "size_chart": "","fulfillment_mode": "","available_on_cod": False,"cancellable": False,
                            "rateable": False,"return_pickup": False,"return_window": "P7D","returnable": True,
                            "time_to_ship": "P2D","common_or_generic_name_of_commodity": "","imported_product_country_of_origin": "",
                            "manufacturer_address": "","manufacturer_name": "","measure_of_commodity_in_pkg": "",
                            "month_year_of_manufacture_packing_import": "","nutritional_info": "",
                            "additives_info": "","brand_owner_fssai_license_no": "",
                            "other_fssai_license_no": "","importer_fssai_license_no": "",
                            "is_veg": ""}
                        }
            response.update(other_params)
            items.append(response)
                           
        return {'items':items, "total_size":crs_products_count.get('count',0), "total_pages": int(math.ceil(float(crs_products_count.get('count', 0)) / int(self.params.get('page_size') or self.parmas.get('page_number'))))}