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
        print(f"crs_rpr   count: {crs_products_count}")
        joined_result = self.coordinator.fetch_catalog_data(catalog_id, self.params.get('page_size', 10), self.params.get('page_number', 1))

        items = []
        for product_data in joined_result:
            response =  {
                        "item_id": product_data.get('ondc_item_id'),
                        "provider_id": f"{product_data.get('seller_id')}",
                        "noderetail_account_user_id": f"{product_data.get('account_id')}",
                        "noderetail_catalog_id": f"{product_data.get('catalog_id')}",
                        "noderetail_storefront_id": f"{self.params.get('noderetail_storefront_id')}",
                        "noderetail_item_id": "string",
                        "noderetail_provider_id": "string",
                        "noderetail_category": f"{product_data.get('category_name')}",
                        "noderetail_category_id": f"{product_data.get('category_id')}",
                        "noderetail_product_url": f"https://www.craftsvilla.com/product/{product_data.get('product_id')}",
                        "product_type": "simple",
                        "name": f"{product_data.get('product_name')}",
                        "description": f"{product_data.get('description')}",
                        "short_description": "string",
                        "category": f"{product_data.get('category_name')}",
                        "variant_group_id": f"{product_data.get('variant_group_id')}",
                        "variant": f"{product_data.get('string')}",
                        "location_id": [],
                        "inventory_info": {
                            "qty": "0",
                            "min_qty": "10",
                            "max_qty": "1",
                            "is_in_stock": "1"
                        },
                        "pricing_info": {
                            "mrp": "599.00",
                            "sale_price": "299.00",
                            "discount_start_date": "",
                            "discount_end_date": "",
                            "discounted_price": ""
                        },
                        "provider_info": {
                            "store_name": "string",
                            "brand_logo": "string",
                            "long_desc": "string",
                            "short_desc": "string",
                            "store_images": [
                            "string-image-url"
                            ],
                            "fssai_license_num": "string",
                            "serviceability": [
                            {
                                "mode": "hyperlocal/pincode/pan-india",
                                "radius": "number",
                                "unit": "km"
                            }
                            ],
                            "locations": [
                            {
                                "id": "string",
                                "gps": "string",
                                "type": "billing/shipping",
                                "address": {
                                "city": "string",
                                "state": "string",
                                "street": "string",
                                "area_code": "string",
                                "locality": "string"
                                },
                                "schedule": {
                                "open_days": "1,2,3,4,5,6,7",
                                "open_hours": [
                                    {
                                    "start_time": "string",
                                    "end_time": "string"
                                    }
                                ]
                                }
                            }
                            ]
                        },
                        "images": [
                            "string"
                        ],
                        "attributes": {
                            "brand": "string",
                            "color": "string",
                            "size": "string",
                            "gender": "string",
                            "pattern": "string",
                            "material": "string",
                            "occasion": "string",
                            "season": "string",
                            "trend": "string",
                            "features": "string",
                            "material_finish": "string",
                            "size_chart": "string",
                            "fulfillment_mode": "string",
                            "available_on_cod": False,
                            "cancellable": False,
                            "rateable": False,
                            "return_pickup": False,
                            "return_window": "P7D",
                            "returnable": True,
                            "time_to_ship": "P2D",
                            "common_or_generic_name_of_commodity": "string",
                            "imported_product_country_of_origin": "string",
                            "manufacturer_address": "string",
                            "manufacturer_name": "string",
                            "measure_of_commodity_in_pkg": "string",
                            "month_year_of_manufacture_packing_import": "string",
                            "nutritional_info": "string",
                            "additives_info": "string",
                            "brand_owner_fssai_license_no": "string",
                            "other_fssai_license_no": "string",
                            "importer_fssai_license_no": "string",
                            "is_veg": "string"
                        }
                        }
            items.append(response)
                           
        return {'items':items, "total_size":crs_products_count.get('count',0), "total_pages": int(math.ceil(float(crs_products_count.get('count', 0)) / int(self.params.get('page_size') or self.parmas.get('page_number'))))}